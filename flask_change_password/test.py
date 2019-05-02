import unittest

from flask import Flask, render_template_string, request

from flask_change_password.flask_change_password import ChangePassword, ChangePasswordForm


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.change_password = ChangePassword(min_password_length=8)

    def test_length(self):
        result = self.change_password.valid_password('tiny')
        assert 'insufficient length' in result, result

    def test_uppercase(self):
        result = self.change_password.valid_password('alllowercase')
        assert '1 uppercase required' in result, result
        rules = self.change_password.rules
        self.change_password.update_rules(dict(uppercase=22))
        result = self.change_password.valid_password('alllowercase')
        assert '22 uppercase required' in result, result
        self.change_password.update_rules(rules)

    def test_lowercase(self):
        result = self.change_password.valid_password('ALLUPPERCASE')
        assert '1 lowercase required' in result, result
        rules = self.change_password.rules
        self.change_password.update_rules(dict(lowercase=20))
        result = self.change_password.valid_password('ALLUPPERCASE')
        assert '20 lowercase required' in result, result
        self.change_password.update_rules(rules)

    def test_nonumbers(self):
        result = self.change_password.valid_password('NoNumbers')
        assert '1 number required' in result, result
        rules = self.change_password.rules
        self.change_password.update_rules(dict(numbers=2))
        result = self.change_password.valid_password('NoNumbers')
        assert '2 numbers required' in result, result
        self.change_password.update_rules(rules)

    def test_punctuation(self):
        result = self.change_password.valid_password('NoNumbers2')
        assert '1 punctuation required' in result, result
        rules = self.change_password.rules
        self.change_password.update_rules(dict(punctuation=2))
        result = self.change_password.valid_password('NoNumbers2')
        assert '2 punctuations required' in result, result
        self.change_password.update_rules(rules)

    def test_diff_username(self):
        result = self.change_password.valid_password('NoNumbers2!', username='Numbers')
        assert 'insufficient difference from username' in result, result

    def test_simple_passwords(self):
        # has inside
        result = self.change_password.valid_password('jjrudeboyAy2!', username='Numbers')
        assert 'too similar to common password: rudeboy' in result, result
        # has inside but password longer than 2 x known bad password
        result = self.change_password.valid_password('jj--iuerudeboyAy2!', username='Numbers')
        assert 5 == result, result
        # starts with
        result = self.change_password.valid_password('monkey9054343hyAy2!', username='Numbers')
        assert 'too similar to common password: monkey' in result, result

    def test_123(self):
        result = self.change_password.valid_password('ru%d*eboyAy123!', username='Numbers')
        assert 'not enough number complexity, 123 disallowed' in result
        result = self.change_password.valid_password('ru!d%eboyAy789!', username='Numbers')
        assert 'not enough number complexity, 789 disallowed' in result

    def test_wxyz(self):
        test_password = 'ru@de%boyAy432wxyz'
        result = self.change_password.valid_password(test_password, username='Numbers')
        assert 5 == result, result

        self.change_password.update_rules(dict(alphabet_sequence=True))

        result = self.change_password.valid_password(test_password, username='Numbers')
        assert 'insufficient letter complexity, wxyz disallowed' in result, result

        result = self.change_password.valid_password('ru%d$eboyAy432WXYZ!', username='Numbers')
        assert 'insufficient letter complexity, wxyz disallowed' in result, result

    def test_pwned(self):
        rules = self.change_password.rules
        self.change_password.update_rules(
            {'punctuation': 0, 'uppercase': 0, 'lowercase': 0, 'number_sequence': False,
             'username': False, 'numbers': 0, 'username_length': 0, 'username_requires_separators': False,
             'passwords': False, 'keyboard_sequence': False, 'alphabet_sequence': False,
             'long_password_override': 0, 'pwned': True, 'min_password_length': 0})
        # known pwned password
        test_password = 'monkey'
        result = self.change_password.valid_password(test_password, username='Numbers')
        assert 'is a known hacked password' in result, result
        # this should not be pwned
        test_password = '1F6A4068DC0A7ADA930C555C3CE5B35445C:1; 1F7AD9E67E4437D507D2E8E50951889E605:2; 1FA5A0CA12BE10:1'
        result = self.change_password.valid_password(test_password, username='Numbers')
        assert 5 == result, result
        self.change_password.update_rules(rules)

    def test_qwerty(self):
        result = self.change_password.valid_password('ru@deboyAy432qwerty!', username='Numbers')
        assert 5 == result, result

        self.change_password.update_rules(dict(keyboard_sequence=True))

        result = self.change_password.valid_password('rud$e^boyAy432qwerty!', username='Numbers')
        assert 'keyboard sequence found, qwer disallowed' in result, result
        result = self.change_password.valid_password('r!judeboyAy432QWERTY!', username='Numbers')
        assert 'keyboard sequence found, qwer disallowed' in result, result

    def test_long_enough_to_pass_with_bad_stuff(self):
        result = self.change_password.valid_password('monkeyNumbers.rudeboyAy2123!', username='Numbers')
        assert result == 'insufficient difference from username', result
        self.change_password.update_rules(dict(min_password_length=10, long_password_override=2))
        result = self.change_password.valid_password('monkeyNumbers.rudeboyAy2123!', username='Numbers')
        assert result == 5, result

    def test_check_username(self):
        self.change_password.update_rules({'username_length': 4})
        result = self.change_password.valid_username(username='bad')
        assert result == 'User name too short.  4 required', result

    def test_baduser(self):
        result = self.change_password.valid_username(username='baduser.')
        assert result == 'Invalid user name', result

        result = self.change_password.valid_username(username='-baduser')
        assert result == 'Invalid user name', result

        result = self.change_password.valid_username(username='baduser')
        assert result == '', result

        self.change_password.update_rules({'username_requires_separators': 4})
        result = self.change_password.valid_username(username='baduser')
        assert result == '. or - required', result

        result = self.change_password.valid_username(username='good.user')
        assert result == '', result

        result = self.change_password.valid_username(username='good-user')
        assert result == '', result


class ClientAppTestCase(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__, static_url_path='/static')
        app.testing = True
        app.secret_key = 'testing'
        app.config['WTF_CSRF_ENABLED'] = False
        app.route('/change_password', methods=['GET', 'POST'])(self.route_change_password)
        self.change_password = ChangePassword(app=app, min_password_length=8)
        self.app = app.test_client()

    def test_check_password(self):
        result = self.app.post('/flask_change_password/check_password', data=dict(password='tiny'),
                               follow_redirects=True)
        result_text = result.data.decode('utf-8')
        assert 'length' in result_text, result_text

    def test_get_password_page(self):
        result = self.app.get('/change_password')
        assert result.status_code == 200
        result_text = result.data.decode('utf-8')
        assert 'Current Password' in result_text, result_text

    def test_update_password(self):
        new_password = 'Atiny98437fdsjkl---387'
        result = self.app.post('/change_password',
                               data=dict(username='max', old_password='hello', password=new_password,
                                         password2=new_password),
                               follow_redirects=True)

        assert 'ok' == result.data.decode('utf-8'), result.data.decode('utf-8')

    def route_change_password(self):
        title = 'Change Password'
        form = ChangePasswordForm(username='max', changing=True, title=title)
        if request.method == 'POST':
            if form.validate_on_submit():
                valid = self.change_password.verify_password_change_form(form)
                return 'ok'
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        print(u"Error in the {} field - {}".format(
                            getattr(form, field).label.text,
                            error
                        ))
                return 'failed', 201

        password_template = self.change_password.change_password_template(form)
        return render_template_string('''<h1>{{ title }}</h1> {{ password_template | safe }} ''', title=title,
                                      form=form, password_template=password_template)
