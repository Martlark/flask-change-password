Flask-change-password: Feature rich change password page
========================================================

|PyPI Version|

Flask-change-password is a Flask extension that implements create and change
password pages that can easily be integrated with a Flask application.

Features
--------


Installation & Basic Usage
--------------------------

Install via `pip <https://pypi.python.org/pypi/pip>`_:

::

    pip install flask-change-password

After installing, wrap your Flask app with an ``ChangePassword``, or call init_app(app).

Example:

.. code:: python

    from flask import Flask
    from flask_change_password import ChangePassword, ChangePasswordForm, SetPasswordForm

    app = Flask(__name__)

    app.secret_key = os.urandom(20)
    flask_change_password = ChangePassword(min_password_length=10, rules=dict(long_password_override=2))
    flask_change_password.init_app(app)


The GitHub repository includes a small example application which shows how to use in an application.

NOTES
-----

This extension uses KnockoutJS for the page view controller and will call the JS from a CDN.

        <script src="https://unpkg.com/tko/dist/tko.es6.min.js"></script>

The source will need to be allowed in your CSP, if you have one.

Options
-------

-  ``app``,  Flask application.  Use init_app(app) to initialise later on.

Rules
-----

A rules dictionary controls how the password is checked and certain aspects of the page operation.

The rules are:

    rules = {'punctuation': 1, 'uppercase': 1, 'lowercase': 1, 'number_sequence': True,
                      'username': True, 'numbers': 1, 'username_length': 0, 'username_requires_separators': False,
                      'passwords': True, 'keyboard_sequence': False, 'alphabet_sequence': False, 'flash': True
                      'long_password_override': 0, 'pwned': True, 'show_hide_passwords': True, 'min_password_length': 20}

* punctuation            - required punctuation in the password (string.punctuation is used).
* uppercase              - required upper case letters.
* lowercase              - required lower case letters.
* number_sequence        - forbid 3 or more numbers in sequence. ie: 123,234,456 etc.
* username               - forbid the password from containing the user name (if supplied as user).
* numbers                - required numbers.
* passwords              - forbid using a password similar to the top 10000 used passwords.
* keyboard_sequence      - forbid a sequence of 4 or more keyboard letters, ie: qwerty.
* alphabet_sequence      - forbid a sequence of 4 or more alphabetic ordered letters, ie: abcd.
* long_password_override - number - when a password is this number times the min length, rules are not enforced.  Set to 0 to disable.  Default is 2
* pwned                  - dynamically query HIBP list of hacked and released passwords and forbid any hacked password found. see: https://haveibeenpwned.com/API/v2#PwnedPasswords
* show_hide_passwords    - allow the client to click to show the password on the page
* min_password_length    - minimum length of the password
* flash                  - produce Flask flash messages on errors

Use the `update_rules` method to change the rules.

Username creation not yet discussed.

* username_length - minimum length for a username
* username_requires_separators - username must use . or - inside


Methods
-------

-  ``ChangePassword(app=None, min_password_length=20, rules=None)`` - Create object.
-  ``init_app(app)`` - Initialise and start with the given Flask application.
-  ``change_password_template(form, submit_text=None)`` - Format and return a
     fragment of HTML that implements the change/set password form.  form is the
     required password operation form. submit_text is the text to show on the submit
     button.  Default is 'submit'
-  ``update_rules(rules=None)`` - Modify the current rules by supplying a dictionary of new rules

Adding the form to a page
-------------------------

Call as follows in your Flask application route:

.. code:: python

    return render_template('change_password.html', password_template=password_template, title=title, form=form,
                               user=dict(username='test.user'),
                               )

And include the template using the jinja2 `safe` pipe.

.. code:: html

    {% extends "base.html" %}

    {% block app_content %}
        <h1>Test Change Password</h1>
        {{ password_template|safe }}
    {% endblock %}


Change Password
---------------

Example of calling the change password form.

.. code:: python

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

Create Password
---------------

Example of calling the create password form.  Use the SetPasswordForm class.

.. code:: python

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




Licensing
---------

- Apache 2.0

.. |PyPI Version| image:: https://img.shields.io/pypi/v/flask-change-password.svg
   :target: https://pypi.python.org/pypi/flask-change-password

