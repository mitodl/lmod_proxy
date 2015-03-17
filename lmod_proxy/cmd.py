# -*- coding: utf-8 -*-
"""Command line debug start of flask application"""
import logging
import os

from lmod_proxy import web

log = logging.getLogger('lmod_proxy')


def run_server():
    logging.basicConfig(level=logging.DEBUG)
    port = int(os.environ.get('LMODP_PORT', 5000))
    host = os.environ.get('LMODP_HOST', 'localhost')
    log.info(
        'Starting with configuration:\n %s',
        '\n'.join([
            '{0}: {1}'.format(x, y)
            for x, y in sorted(dict(web.app.config).items())
        ])
    )
    web.app.run(debug=True, host=host, port=port)
