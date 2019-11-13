# -*- coding: utf-8 -*-
"""
Test out the basic authentication module.
"""
import unittest.mock as mock

from lmod_proxy.auth import check_basic_auth, requires_auth
from lmod_proxy.tests.common import CommonTest


class TestAuth(CommonTest):
    """
    Verify that basic auth works as expected.
    """

    @classmethod
    def _get_requires_auth_decorator(cls):
        """
        Returns decorated mock function from
        :py:function:`archelond.auth.requires_auth`
        """
        wrapped = mock.Mock()
        wrapped.__name__ = 'foo'
        decorated = requires_auth(wrapped)
        return wrapped, decorated

    def test_check_basic_auth(self):
        """
        Validate a test user works with the correct password
        and doesn't with a bad one
        """
        with self.app.app_context():
            self.assertTrue(self.TEST_USER in self.app.config['users'].users())
            # Verify positive case
            valid, username = check_basic_auth(self.TEST_USER, self.TEST_PASS)
            self.assertTrue(valid)
            self.assertEqual(username, self.TEST_USER)

            # Verify negative password case
            valid, username = check_basic_auth(self.TEST_USER, 'blah')
            self.assertFalse(valid)
            self.assertEqual(self.TEST_USER, username)

            # Verify negative user case
            not_user = self.NOT_USER
            self.assertTrue(not_user not in self.app.config['users'].users())
            valid, username = check_basic_auth(not_user, 'blah')
            self.assertFalse(valid)
            self.assertEqual(not_user, username)

    def test_requires_auth(self):
        """
        Verify full auth with both token and basic auth.
        """

        # Test successful basic auth
        with self.app.test_request_context(
                headers=self.get_basic_auth_headers()
        ):
            wrapped, decorated = TestAuth._get_requires_auth_decorator()
            decorated()
            wrapped.assert_called_with(user=self.TEST_USER)

        # Test unsuccessful auth
        with self.app.test_request_context(
                headers=self.get_basic_auth_headers(invalid=True)
        ):
            wrapped, decorated = TestAuth._get_requires_auth_decorator()
            response = decorated()
            self.assertEqual(401, response.status_code)
