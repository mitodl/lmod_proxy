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

    # Base URL for which the gradebook API lives and accepts
    # certificate authentication
    'LMODP_URLBASE': 'https://learning-modules.mit.edu:8443/'
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
    return configuration

globals().update(_configure())
