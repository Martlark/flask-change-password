import os
import hashlib
import string
import re
import requests

from flask import request, flash, send_from_directory, render_template_string, jsonify
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, EqualTo

PWNED_URL = 'https://api.pwnedpasswords.com/'


class ChangePassword:
    def __init__(self, app=None, min_password_length=20, rules=None):
        self.base_dir = os.path.dirname(__file__)
        self.min_password_length = min_password_length
        self.app = None
        self.rules = {'punctuation': True, 'uppercase': True, 'lowercase': True, 'number_sequence': True,
                      'username': True, 'numbers': True, 'username_length': 0, 'username_requires_separators': False,
                      'passwords': True, 'keyboard_sequence': False, 'alphabet_sequence': False,
                      'long_password_override': 0, 'pwned': True}
        self.update_rules(dict(min_password_length=min_password_length))
        self.update_rules(rules or {})

        self.messages = dict(too_short='User name too short.  {} required',
                             invalid_username='Invalid user name',
                             not_start_end_with_dot='Cannot start or end with .',
                             not_start_end_with_hyphen='Cannot start or end with -',
                             dot_or_hyphen_required='. or - required')

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.app.route('/flask_change_password/check_password', methods=['POST'])(self.route_check_password)
        self.app.route('/flask_change_password/static/<filename>', methods=['GET'])(self.route_change_password_static)
        self.app.route('/flask_change_password/get_rules', methods=['GET'])(self.route_get_rules)

    def route_get_rules(self):
        return jsonify(self.rules)

    def update_rules(self, rules=None):
        self.rules.update(rules or {})
        self.min_password_length = self.rules['min_password_length']

    def change_password_template(self, form):
        with open(os.path.join(self.base_dir, 'change_password_template.html')) as f:
            text = f.read()
        return render_template_string(text, form=form, rules_text=self.get_rules_text())

    def route_change_password_static(self, filename):
        return send_from_directory(self.base_dir, filename)

    def valid_password(self, password='', username=''):
        score = 0
        try:
            score = self.password_good_enough(password=password, username=username)
        except Exception as e:
            return str(e)

        return score

    def valid_username(self, username):
        try:
            self.check_username(username=username)
        except Exception as e:
            return str(e)

        return ''

    def check_username(self, username):
        """
        raise exception if user name is not valid
        :param username:
        """
        if len(username) < self.rules['username_length']:
            raise Exception(self.messages['too_short'].format(self.rules['username_length']))

        if not re.search('^[A-Za-z0-9]+(?:[ .-][A-Za-z0-9]+)*$', username):
            raise Exception(self.messages['invalid_username'])

        if username.startswith('.') or username.endswith('.'):
            raise Exception(self.messages['not_start_end_with_dot'])

        if username.startswith('-') or username.endswith('-'):
            raise Exception(self.messages['not_start_end_with_hyphen'])

        if self.rules['username_requires_separators']:
            if '.' not in username and '-' not in username:
                raise Exception(self.messages['dot_or_hyphen_required'])

    def route_check_password(self):
        password = request.json.get('password', '')
        username = request.json.get('username', '')
        try:
            score = self.password_good_enough(password=password, username=username)
        except Exception as e:
            return str(e)

        return str(score)

    def get_rules_text(self):
        rules_text = '''Must be at least {min_password_length} characters long.'''.format(
            min_password_length=self.rules['min_password_length'])

        if self.rules['uppercase']:
            rules_text += ''' Must include at least one uppercase.'''
        if self.rules['numbers']:
            rules_text += ''' Must include at least one number.'''
        if self.rules['lowercase']:
            rules_text += ''' Must include at least one lowercase.'''
        if self.rules['punctuation']:
            rules_text += ''' Must include at least one punctuation character.'''
        if self.rules['username']:
            rules_text += ''' Cannot include your user name.'''
        if self.rules['number_sequence']:
            rules_text += ''' Cannot include number sequences.'''
        if self.rules['keyboard_sequence']:
            rules_text += ''' Cannot include keyboard letter sequences.'''
        if self.rules['alphabet_sequence']:
            rules_text += ''' Cannot include alphabetic sequences.'''
        if self.rules['pwnd']:
            rules_text += ''' Cannot be a pwned password.'''
        if self.rules['passwords']:
            rules_text += ''' Cannot be like a common password.'''
        if self.rules['long_password_override'] > 1:
            rules_text += ' Rules do not apply if password is greater than {} characters.'.format(
                self.rules['long_password_override'] * self.min_password_length)

        return rules_text

    def password_good_enough(self, password, username=''):
        """
        valid_password if the password is sufficiently secure
        raise exception if there are faults
        :param password:
        :param username: username to valid_password if used in password
        :return: strength score out of 5
        """
        score = 0
        if len(password) < self.rules['min_password_length']:
            raise Exception('length.  Required {}'.format(self.rules['min_password_length']))

        if self.rules['long_password_override'] > 1 and len(password) > self.rules['long_password_override'] * \
                self.rules['min_password_length']:
            return 5

        # only apply these tests if password is of 'middling length'
        if self.rules['uppercase'] and not re.search(r'[A-Z]', password):
            raise Exception('uppercase')
        score += 1

        if self.rules['lowercase'] and not re.search(r'[a-z]', password):
            raise Exception('lowercase')
        score += 1

        if self.rules['numbers'] and not re.search(r'[0-9]', password):
            raise Exception('numbers')
        score += 1

        if self.rules['punctuation']:
            punctuation = 0
            for p in password:
                if p in string.punctuation:
                    punctuation += 1

            if punctuation == 0:
                raise Exception('punctuation')
        score += 1

        if self.rules['username'] and len(username) > 0 and username.lower() in password.lower():
            raise Exception('difference from username')

        if self.rules['number_sequence']:
            sequence_length = 3
            for x in range(11 - sequence_length):
                consecutive_sequence = ''.join([str(y) for y in range(x, x + sequence_length)])
                if consecutive_sequence in password:
                    raise Exception('number complexity, {} disallowed'.format(consecutive_sequence))

        if self.rules['alphabet_sequence']:
            sequence_length = 4
            for x in range(len(string.ascii_letters) - sequence_length):
                consecutive_sequence = ''.join([string.ascii_letters[y] for y in range(x, x + sequence_length)])
                if consecutive_sequence in password.lower():
                    raise Exception('complexity, {} disallowed'.format(consecutive_sequence))

        if self.rules['keyboard_sequence']:
            keyboard = 'qwertyuiopasdfghjklzxcvbnm'
            sequence_length = 4
            for x in range(len(keyboard) - sequence_length):
                consecutive_sequence = ''.join([keyboard[y] for y in range(x, x + sequence_length)])
                if consecutive_sequence in password.lower():
                    raise Exception('complexity, {} disallowed'.format(consecutive_sequence))

        if self.rules['passwords']:
            with open(os.path.join(self.base_dir, '10_million_password_list_top_10000.txt')) as f:
                for line in f:
                    known_password = line.strip()
                    if password.startswith(known_password) or len(known_password) * 2 > len(
                            password) and known_password in password:
                        raise Exception('difference from known simple password: {}'.format(known_password))
        score += 1

        if self.rules['pwned']:
            self.check_pwned(password)
        return score

    @staticmethod
    def check_pwned(password):
        """
        raise exception if password hashed using sha1 is in the pwned passwords
        database.

        see: https://haveibeenpwned.com/API/v2#PwnedPasswords
        :param password:
        :return:
        """
        hash_object = hashlib.sha1(password.encode())
        full_hash = hash_object.hexdigest().upper()
        hex_dig_first5 = full_hash[:5]
        hash_search_string = full_hash[5:] + ':'
        response = requests.get(PWNED_URL + 'range/' + hex_dig_first5)
        if response.status_code == 200:
            search_space = response.content.decode('utf-8')
            if hash_search_string in search_space:
                raise Exception('difference from known passwords')

    def verify_password_change_form(self, form):
        try:
            self.password_good_enough(form.password.data, form.username.data)
        except Exception as e:
            flash('Insufficient' + str(e))
            return False

        if form.password.data != form.password2.data:
            flash('Password and repeat password not the same')
            return False

        if hasattr(form, 'old_password'):
            if len(form.old_password.data) < self.rules['min_password_length']:
                flash('Current password too short')
                return False

            if form.old_password.data == form.password2.data:
                flash('Current password and new password must be different')
                return False

        return True

    def verify_password_set_form(self, form):
        valid = True
        if form.password.data != form.password2.data:
            flash('Password and repeat password not the same')
            valid = False
        elif len(form.password.data) < self.rules['min_password_length']:
            flash('Password too short')
            valid = False
        return valid


class ChangePasswordForm(FlaskForm):
    password_length = HiddenField('password_length')
    title = HiddenField('title')
    username = HiddenField('username')
    changing = HiddenField('changing', default=True)
    old_password = PasswordField('Current Password', validators=[DataRequired()],
                                 render_kw={'data-bind': 'textInput: old_password'})
    password = PasswordField('New Password', validators=[DataRequired()],
                             render_kw={'data-bind': 'textInput: password1', 'required': 'required'})
    password2 = PasswordField(
        'Repeat New Password', validators=[DataRequired(), EqualTo('password')],
        render_kw={'data-bind': 'textInput: password2', 'required': 'required'})
    submit = SubmitField('Change Password', render_kw={'data-bind': 'visible: verified()'})


class SetPasswordForm(FlaskForm):
    password_length = HiddenField('password_length')
    title = HiddenField('title')
    username = HiddenField('username')
    changing = HiddenField('changing', default=False)
    password = PasswordField('New Password', validators=[DataRequired()],
                             render_kw={'data-bind': 'textInput: password1', 'required': 'required'})
    password2 = PasswordField(
        'Repeat New Password', validators=[DataRequired(), EqualTo('password')],
        render_kw={'data-bind': 'textInput: password2', 'required': 'required'})
    submit = SubmitField('Change Password', render_kw={'data-bind': 'visible: verified()'})
