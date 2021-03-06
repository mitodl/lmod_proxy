# -*- coding: utf-8 -*-
"""
Test the root Web application
"""
import importlib
import unittest.mock as mock
from passlib.apache import HtpasswdFile

from lmod_proxy.tests.common import CommonTest


class TestWeb(CommonTest):
    """Verify the root Web app.  Currently it just redirects to edx_grades"""

    def setUp(self):
        """Setup commonly needed objects like the flask test client"""
        super(TestWeb, self).setUp()
        import lmod_proxy.web
        importlib.reload(lmod_proxy.web)
        self.client = lmod_proxy.web.app.test_client()

    def test_redirect(self):
        """Do a get and verify we are redirected"""
        response = self.client.get('/', headers=self.get_basic_auth_headers())
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            'http://localhost/edx_grades',
            response.headers['location']
        )

    def test_pages_protected(self):
        """Verify pages that should be protected actually are."""
        for page in ['/edx_grades', '/']:
            response = self.client.get(page)
            self.assertEqual(401, response.status_code)

    @mock.patch.dict(
        'os.environ',
        {'LMODP_HTPASSWD_PATH': '^^^/^^^'},
        clear=True
    )
    def test_htpasswd_file(self):
        """Verify we still create an app, even without an htpasswd file"""
        import logging
        import lmod_proxy.config
        importlib.reload(lmod_proxy.config)
        import lmod_proxy.web

        logging.Logger.critical = mock.MagicMock(return_value=None)

        local_app = lmod_proxy.web.app_factory()
        self.assertTrue(logging.Logger.critical.called)
        self.assertEqual(
            local_app.config['users'].users(),
            HtpasswdFile().users()
        )
