# -*- coding: utf-8 -*-
"""Root flask application for lmod_proxy"""
import json
import logging
import OpenSSL.crypto

from config import LMODP_CERT
from datetime import datetime
from flask import Flask, redirect, url_for
from flask.ext.log import Logging
from passlib.apache import HtpasswdFile

from lmod_proxy import __project__
from lmod_proxy.auth import requires_auth
from lmod_proxy.edx_grades import edx_grades

log = logging.getLogger('lmod_proxy')  # pylint: disable=invalid-name


def app_factory():
    """Startup and application factory"""
    new_app = Flask(__project__)
    new_app.config.from_object('lmod_proxy.config'.format(__project__))
    Logging(new_app)

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


@app.route('/status', methods=['GET'])
def status():
    """Route to get app cert expiration date

    Return: json object containing app_cert_expiration date and status
    """
    app_cert_content = open(LMODP_CERT, 'rt').read()
    app_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
                                               app_cert_content)
    app_cert_expiration = datetime.strptime(app_cert.get_notAfter(),
                                            '%Y%m%d%H%M%SZ')
    date_delta = app_cert_expiration - datetime.now()
    retval = {
        'app_cert_expires': app_cert_expiration.strftime('%Y-%m-%dT%H:%M:%S'),
        'status': 'ok' if date_delta.days > 30 else 'warn'
    }
    return json.dumps(retval)
