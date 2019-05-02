# Copyright 2019 Andrew Rowe Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import os
from flask import Flask, render_template, redirect, url_for, jsonify

from flask_change_password import ChangePassword, ChangePasswordForm, SetPasswordForm

app = Flask(__name__)

app.secret_key = os.urandom(20)
flask_change_password = ChangePassword(min_password_length=10, rules=dict(long_password_override=2))
flask_change_password.init_app(app)


@app.route('/')
def page_index():
    return render_template('index.html')


@app.route('/changed/<title>/<new_password>')
def page_changed(title, new_password=''):
    return render_template('changed.html', title=title, new_password=new_password)


@app.route('/rules')
def page_rules():
    return render_template('rules.html', rules=json.dumps(flask_change_password.rules))


@app.route('/get_rules')
def get_rules():
    return jsonify(flask_change_password.rules)


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


@app.route('/set_rule/<name>/<value>')
def set_rules(name, value):
    rules = flask_change_password.rules
    if value in ['true', 'false']:
        value = value == 'true'
    elif is_number(value):
        value = int(value)
    rules[name] = value
    rules = flask_change_password.update_rules(rules)
    return jsonify(rules)


@app.route('/change_password', methods=['GET', 'POST'])
def page_change_password():
    title = 'Change Password'
    form = ChangePasswordForm(username='test.user', changing=True, title=title)
    if form.validate_on_submit():
        valid = flask_change_password.verify_password_change_form(form)
        if valid:
            return redirect(url_for('page_changed', title='changed', new_password=form.password.data))

        return redirect(url_for('page_change_password'))
    password_template = flask_change_password.change_password_template(form, submit_text='Change')
    return render_template('change_password.html', password_template=password_template, title=title, form=form,
                           user=dict(username='test.user'),
                           )


@app.route('/create_password', methods=['GET', 'POST'])
def page_create_password():
    title = 'Create Password'
    form = SetPasswordForm(username='test.user', title=title)
    if form.validate_on_submit():
        valid = flask_change_password.verify_password_change_form(form)
        if valid:
            return redirect(url_for('page_changed', title='created', new_password=form.password.data))

        return redirect(url_for('page_create_password'))
    password_template = flask_change_password.change_password_template(form, submit_text='Submit')
    return render_template('create_password.html', password_template=password_template, title=title, form=form,
                           user=dict(username='test.user'),
                           )


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8886, debug=True)
