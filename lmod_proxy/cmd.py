# -*- coding: utf-8 -*-
"""Command line debug start of flask application"""
import os

from lmod_proxy import config


def run_server():
    """Debug running of the application via flask's app reloader.

    Do not use this command to run in production.  A WSGI container like
    uwsgi or gunicorn should be used.
    """
    port = int(os.environ.get('LMODP_PORT', 5000))
    host = os.environ.get('LMODP_HOST', 'localhost')

    # Debug configuration settings
    config.FLASK_LOG_LEVEL = 'DEBUG'

    from lmod_proxy.web import app
    app.run(debug=True, host=host, port=port)
