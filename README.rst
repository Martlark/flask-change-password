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


The repository includes a small example application.

NOTE: This extension uses KnockoutJS for the page view controller and will call the JS from a CDN.

Options
-------

-  ``app``,  Flask application.  Use init_app(app) to intialise later on.

Methods
-------

-  ``init_app(app)`` - Initialise and start with the given Flask application.
-  ``change_password_template(form, submit_text=None)`` - Format and return a
     fragment of HTML that implements the change/set password form.  form is the
     required password operation form. submit_text is the text to show on the submit
     button.  Default is 'submit'

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

