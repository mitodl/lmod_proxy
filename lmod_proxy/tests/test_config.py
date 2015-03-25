# -*- coding: utf-8 -*-
"""Verify configuration capabilities of the app"""
import imp
import os
import tempfile
import unittest

import mock
import yaml


class TestConfiguration(unittest.TestCase):
    """Test out configuration defaults, loading yaml/environ config,
    etc.
    """
    def test_defaults(self):
        """Test that default values are right given no config as well as
        asserting flask configuration is happening properly.

        By patching environment variables and returning an empty config file
        this should enforce that we are getting the default configuration.
        """
        _, temp_config_path = tempfile.mkstemp()
        self.addCleanup(os.remove, temp_config_path)
        with open(temp_config_path, 'w') as temp_config:
            temp_config.write(yaml.dump({}))

        with mock.patch.dict(
                'os.environ', {'LMODP_CONFIG': temp_config_path}, clear=True
        ):
            import lmod_proxy.config
            # Reload to reinitialize CONFIG_KEYS with patched environ
            imp.reload(lmod_proxy.config)
            import lmod_proxy.web
            imp.reload(lmod_proxy.web)

            self.assertDictContainsSubset(
                lmod_proxy.config.CONFIG_KEYS,
                dict(lmod_proxy.web.app.config)
            )

    def test_file_config_precedence_(self):
        """Verify we load config files, that they beat defaults, and that
        environment variables win.
        """
        test_cert = 'testing'
        env_test_cert = 'env_testing'

        _, temp_config_path = tempfile.mkstemp()
        self.addCleanup(os.remove, temp_config_path)

        with open(temp_config_path, 'w') as temp_config:
            temp_config.write(yaml.dump({'LMODP_CERT': test_cert}))
        with mock.patch.dict(
            'os.environ', {'LMODP_CONFIG': temp_config_path}, clear=True
        ):
            import lmod_proxy.config
            # Reload to reinitialize CONFIG_KEYS with patched environ
            imp.reload(lmod_proxy.config)
            self.assertEqual(
                lmod_proxy.config._configure()['LMODP_CERT'],
                test_cert
            )
        with mock.patch.dict(
            'os.environ', {
                'LMODP_CONFIG': temp_config_path,
                'LMODP_CERT': env_test_cert,
            },
            clear=True
        ):
            import lmod_proxy.config
            # Reload to reinitialize CONFIG_KEYS with patched environ
            imp.reload(lmod_proxy.config)
            self.assertEqual(
                lmod_proxy.config._configure()['LMODP_CERT'],
                env_test_cert
            )
