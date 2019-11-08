# -*- coding: utf-8 -*-
"""Module for Common test classes and functions that help with common
problems like basic authentication.
"""
import base64
import importlib
import os
import unittest
import unittest.mock as mock


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

        importlib.reload(lmod_proxy.config)
        self.app = app_factory()

    def get_basic_auth_headers(self, invalid=False):
        """Return a header dictionary with the appropriate basic
        authentication header for the test user.

        Args:
            invalid (bool): if set to True, returns bad authentication
        """
        user = self.NOT_USER if invalid else self.TEST_USER
        user_pass = '{0}:{1}'.format(user, self.TEST_PASS)
        b64_bytes = base64.b64encode(bytes(user_pass, encoding='utf-8'))
        b64_user_pass_str = str(b64_bytes, encoding='utf-8')
        return {'Authorization': 'Basic {0}'.format(b64_user_pass_str)}
