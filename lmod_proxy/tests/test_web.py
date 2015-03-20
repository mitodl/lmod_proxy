# -*- coding: utf-8 -*-
"""
Test the root Web application
"""
import unittest

import lmod_proxy.web


class TestWeb(unittest.TestCase):
    """Verify the root Web app.  Currently it just redirects to edx_grades"""

    def setUp(self):
        """Setup commonly needed objects like the flask test client"""
        super(TestWeb, self).setUp()
        self.client = lmod_proxy.web.app.test_client()

    def test_redirect(self):
        """Do a get and verify we are redirected"""
        response = self.client.get('/')
        self.assertEqual(302, response.status_code)
        self.assertEqual(
            'http://localhost/edx_grades',
            response.headers['location']
        )
