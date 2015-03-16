# -*- coding: utf-8 -*-
"""Command line debug start of flask application"""
import logging
import os

import lmod_proxy


def run_server():
    logging.basicConfig(level=logging.DEBUG)
    port = int(os.environ.get('PROXYLMOD_PORT', 5000))
    host = os.environ.get('PROXYLMOD_HOST', 'localhost')
    lmod_proxy.app.run(debug=True, host=host, port=port)
