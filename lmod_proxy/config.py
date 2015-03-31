# -*- coding: utf-8 -*-
"""Configuration of flask application via environment, or file"""
import logging
import os

import yaml

log = logging.getLogger('gitreload')  # pylint: disable=C0103


CONFIG_PATHS = [
    os.environ.get('LMODP_CONFIG', ''),
    os.path.join(os.getcwd(), 'lmod_proxy.yml'),
    os.path.join(os.path.expanduser('~'), 'lmod_proxy.yml'),
    '/etc/lmod_proxy.yml',
]

CONFIG_KEYS = {
    # Path to base64 encoded, un-passphrased, key and certificate
    # combined file
    'LMODP_CERT': 'ocw.app.mit.edu-key-and-cert.pem',

    # The base64 encoded string of the certificate as opposed to the
    # path. This will trigger the app to write out the certificate on
    # startup for environments that are best configured via variables
    # only like Heroku.
    'LMODP_CERT_STRING': '',

    # Base URL for which the gradebook API lives and accepts
    # certificate authentication
    'LMODP_URLBASE': 'https://learning-modules.mit.edu:8443/',

    # Direct path to apache htpasswd file to use for basic auth
    'LMODP_HTPASSWD_PATH': '.htpasswd',

    # Setting that actually contains the strings of the htpasswd file
    # for situations like heroku.  If set it will write out the string
    # to a file for reading on startup.
    'LMODP_HTPASSWD': None,
}


def _configure():
    """Configure the application by trying config file and overriding with
    environment variables.
    """
    config_file_path = None
    fallback_config = {}
    for config_path in CONFIG_PATHS:
        if os.path.isfile(config_path):
            config_file_path = config_path
            break
    if config_file_path:
        with open(config_file_path) as config_file:
            fallback_config = yaml.load(config_file)

    configuration = {}
    for key, default_value in CONFIG_KEYS.items():
        configuration[key] = os.environ.get(
            key, fallback_config.get(key, default_value)
        )

    if configuration['LMODP_HTPASSWD']:
        configuration['LMODP_HTPASSWD_PATH'] = os.path.abspath('.htpasswd')
        with open(configuration['LMODP_HTPASSWD_PATH'], 'w') as wfile:
            wfile.write(configuration['LMODP_HTPASSWD'])

    if configuration['LMODP_CERT_STRING']:
        configuration['LMODP_CERT'] = os.path.abspath('.cert.pem')
        with open(configuration['LMODP_CERT'], 'w') as wfile:
            wfile.write(configuration['LMODP_CERT_STRING'])

    return configuration

globals().update(_configure())
