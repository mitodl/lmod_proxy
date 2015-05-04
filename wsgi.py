# -*- coding: utf-8 -*-
"""
WSGI script needed to run on dotcloud
"""
from __future__ import print_function
import json
import os


def dotcloud_startup():
    """
    Get configuration from dotcloud environment before import application
    """
    with open('/home/dotcloud/environment.json') as env_file:
        env = json.load(env_file)
        print('Loading dotcloud environment from file.')
        for key, value in env.items():
            print('{0}: {1}'.format(key, value))
            os.environ[key] = value

    from lmod_proxy.web import app
    return app
