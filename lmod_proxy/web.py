# -*- coding: utf-8 -*-
"""Root flask application for lmod_proxy"""
import logging

from flask import Flask, redirect, url_for
from passlib.apache import HtpasswdFile

from lmod_proxy import __project__
from lmod_proxy.auth import requires_auth
from lmod_proxy.edx_grades import edx_grades
from lmod_proxy.log import configure_logging

log = logging.getLogger('lmod_proxy')  # pylint: disable=invalid-name


def app_factory():
    """Startup and application factory"""
    new_app = Flask(__project__)
    new_app.config.from_object('lmod_proxy.config'.format(__project__))
    new_app.register_blueprint(edx_grades, url_prefix='/edx_grades')
    # Load up user database
    try:
        new_app.config['users'] = HtpasswdFile(
            new_app.config['LMODP_HTPASSWD_PATH']
        )
    except IOError:
        log.critical(
            'No htpasswd file loaded, please set `LMODP_HTPASSWD`'
            'environment variable to a valid apache htpasswd file.'
        )
        new_app.config['users'] = HtpasswdFile()
    configure_logging(new_app)
    log.debug(
        'Starting with configuration:\n %s',
        '\n'.join([
            '{0}: {1}'.format(x, y)
            for x, y in sorted(dict(new_app.config).items())
        ])
    )
    return new_app


app = app_factory()


@app.route('/', methods=['GET'])
@requires_auth
def index(user):
    """Welcome them to our amazing LMod Proxy

    Return:
        Flask.response
    """
    return redirect(url_for('edx_grades.index'))
