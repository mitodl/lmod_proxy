# -*- coding: utf-8 -*-
"""
Testing of the module level stuff itself
"""
import unittest

import unittest.mock as mock
import semantic_version


class TestModule(unittest.TestCase):
    """
    Test core module features, like asserting the version
    and making sure we are exposing our classes
    """

    @staticmethod
    def test_version():
        """
        Verify we have a valid semantic version
        """
        import lmod_proxy
        semantic_version.Version(lmod_proxy.__version__)

    def test_bad_version(self):
        """Verify bad version handling"""
        from pkg_resources import DistributionNotFound
        from lmod_proxy import _get_version

        error_string = 'Please install this project with setup.py'

        with mock.patch(
                'lmod_proxy.get_distribution',
                autospec=True
        ) as mock_distribution:
            # Test with distribution not found:
            mock_distribution.side_effect = DistributionNotFound()
            self.assertEqual(_get_version(), error_string)

        # Test with loc path not matching
        with mock.patch('os.path.abspath', autospec=True) as mock_path:
            mock_path.return_value = 'not/where/we/are'
            self.assertEqual(_get_version(), error_string)
            # Bonus regression test to make sure we are calling
            # abspath.
            self.assertTrue(mock_path.called)
