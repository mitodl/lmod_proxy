# -*- coding: utf-8 -*-
"""Module for Common test classes and functions that help with common
problems like basic authentication.
"""
import base64
import imp
import os
import unittest

import mock


def get_htpasswd_path():
    """Get path to test htpasswd file"""
    dir_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir_path, 'config', 'test_htpasswd')


class CommonTest(unittest.TestCase):
    """
    Basic test class that reloads the configuration and has helpers
    for handling basic authentication.
    """

    TEST_USER = 'foo'
    TEST_PASS = 'bar'
    NOT_USER = 'notuser'

    @mock.patch.dict(
        'os.environ',
        {'LMODP_HTPASSWD_PATH': get_htpasswd_path()},
        clear=True
    )
    def setUp(self):
        """
        Create the ElasticData Object and make it available to tests.
        """
        import lmod_proxy.config
        from lmod_proxy.web import app_factory

        imp.reload(lmod_proxy.config)
        self.app = app_factory()

    def get_basic_auth_headers(self, invalid=False):
        """Return a header dictionary with the appropriate basic
        authentication header for the test user.

        Args:
            invalid (bool): if set to True, returns bad authentication
        """
        user = self.NOT_USER if invalid else self.TEST_USER
        return dict(Authorization='Basic {0}'.format(base64.b64encode(
            '{0}:{1}'.format(user, self.TEST_PASS)
        )))
