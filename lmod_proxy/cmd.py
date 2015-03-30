# -*- coding: utf-8 -*-
"""Command line debug start of flask application"""
import os

from lmod_proxy import config


def run_server():

    port = int(os.environ.get('LMODP_PORT', 5000))
    host = os.environ.get('LMODP_HOST', 'localhost')

    # Debug configuration settings
    config.LMODP_LOG_LEVEL = 'DEBUG'

    from lmod_proxy.web import app
    app.run(debug=True, host=host, port=port)
