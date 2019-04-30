Flask-change-password: Feature rich change password page
=========================================

|PyPI Version|

Flask-change-password is a Flask extension implements a create and change password pages that can
easily be integrate with a Flask application.

Features
--------


Installation & Basic Usage
--------------------------

Install via `pip <https://pypi.python.org/pypi/pip>`_:

::

    pip install flask-change-password

After installing, wrap your Flask app with an ``IpBan``, or call ip_ban.init_app(app):

.. code:: python

    from flask import Flask
    from flask_ipban import IpBan

    app = Flask(__name__)
    ip_ban = IpBan(ban_seconds=200)
    ip_ban.init_app(app)


The repository includes a small example application.

Options
-------

-  ``app``,  Flask application to monitor.  Use ip_ban.init_app(app) to intialise later on.

Methods
-------

-  ``init_app(app)`` - Initialise and start ip_ban with the given Flask application.

Example for add:

.. code:: python

    from flask import Flask
    from flask_ipban import IpBan

    app = Flask(__name__)
    ip_ban = IpBan(app)

    @route('/login', methods=['GET','POST']
    def login:
        # ....
        # increment block if wrong passwords to prevent password stuffing
        # ....
        if request.method == 'POST':
            if request.arg.get('password') != 'secret':
                ip_ban.add(reason='bad password')

-  ``remove(ip_address)`` - remove the given ip address from the ban list.  Returns true if ban removed.
-  ``url_pattern_add('reg-ex-pattern', match_type='regex')`` - exclude any url matching the pattern from checking


Example of url_pattern_add:

.. code:: python

    from flask import Flask
    from flask_ipban import IpBan

    app = Flask(__name__)
    ip_ban = IpBan(app)
    ip_ban.url_pattern_add('^/whitelist$', match_type='regex')
    ip_ban.url_pattern_add('/flash/dance', match_type='string')


-  ``url_pattern_remove('reg-ex-pattern')`` - remove pattern from the url whitelist
-  ``url_block_pattern_add('reg-ex-pattern', match_type='regex')`` - add any url matching the pattern to the block list. match_type can be 'string' or 'regex'.  String is direct match.  Regex is a regex pattern.
-  ``url_block_pattern_remove('reg-ex-pattern')`` - remove pattern from the url block list
-  ``ip_whitelist_add('ip-address')`` - exclude the given ip from checking
-  ``ip_whitelist_remove('ip-address')`` - remove the given ip from the ip whitelist


Example of ip_whitelist_add

.. code:: python

    from flask import Flask
    from flask_ipban import IpBan

    app = Flask(__name__)
    ip_ban = IpBan(app)
    ip_ban.whitelist_add('127.0.0.1')


-  ``load_nuisances(file_name=None)`` - add a list of nuisances to url pattern block list from a file.  See below for more information.

Example:

.. code:: python

    ip_ban = IpBan()
    app = Flask(__name__)
    ip_ban.init_app(app)
    ip_ban.load_nuisances()

Licensing
---------

- Apache 2.0

.. |PyPI Version| image:: https://img.shields.io/pypi/v/flask-change-password.svg
   :target: https://pypi.python.org/pypi/flask-change-password

