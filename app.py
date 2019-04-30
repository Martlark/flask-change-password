import os
from flask import Flask, redirect, url_for, render_template_string

from .flask_change_password import ChangePassword, ChangePasswordForm

app = Flask(__name__)
app.secret_key = os.urandom(20)
flask_change_password = ChangePassword(min_password_length=10, rules=dict(long_password_override=2))
flask_change_password.init_app(app)


@app.route('/')
def hello_world():

    return '<h1>Change password test application</h1><a href="/change_password">Change Password</a>'


@app.route('/changed')
def changed():
    return 'password changed'


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    title = 'Change Password'
    form = ChangePasswordForm(username='test.user', changing=True, title=title)
    if form.validate_on_submit():
        valid = flask_change_password.verify_password_change_form(form)
        if valid:
            return redirect(url_for('changed'))

        return redirect(url_for('change_password'))
    password_template = flask_change_password.change_password_template(form)
    page_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
.form {
  margin: 1em;
}

.alert-danger {
  color: red;
}

.alert-success {
  color: greenyellow;
  font-weight: bold; 
}

.form input {
  width: 40%;
  margin-bottom: 1em;
}


.form input[type=submit] {
  width: 10em;
}


.control-label {
  display: block;
}
    </style>
    <title>Test Change Password</title>
</head>
<body>
    <h1>Test Change Password</h1>
{{password_template|safe}}
</body>
</html>"""
    return render_template_string(page_html, password_template=password_template, title=title, form=form,
                                  user=dict(username='test.user'),
                                  )


if __name__ == '__main__':
    app.run()
