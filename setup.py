"""
Install lmod_proxy via setuptools
"""
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as testcommand

with open('test_requirements.txt') as test_reqs:
    tests_require = test_reqs.readlines(),


class PyTest(testcommand):
    user_options = testcommand.user_options[:]
    user_options += [
        ('coverage', 'C', 'Produce a coverage report for proxy_lmod'),
        ('pep8', 'P', 'Produce a pep8 report for proxy_lmod'),
        ('flakes', 'F', 'Produce a flakes report for proxy_lmod'),
    ]
    coverage = None
    pep8 = None
    flakes = None
    test_suite = False
    test_args = []

    def initialize_options(self):
        testcommand.initialize_options(self)

    def finalize_options(self):
        testcommand.finalize_options(self)
        self.test_suite = True
        self.test_args = []
        if self.coverage:
            self.test_args.append('--cov')
            self.test_args.append('lmod_proxy')
        if self.pep8:
            self.test_args.append('--pep8')
        if self.flakes:
            self.test_args.append('--flakes')

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        # Needed in order for pytest_cache to load properly
        # Alternate fix: import pytest_cache and pass to pytest.main
        import _pytest.config

        pm = _pytest.config.get_plugin_manager()
        pm.consider_setuptools_entrypoints()
        errno = pytest.main(self.test_args)
        sys.exit(errno)


README = open('README.rst').read()

setup(
    name='lmod_proxy',
    version='0.1.0',
    license='AGPLv3',
    author='MIT ODL Engineering',
    author_email='odl-engineering@mit.edu',
    url='http://github.com/mitodl/lmod_proxy',
    description=('Flask application for proxying requests to the'
                 'MIT Learning Modules API from edx-platform'),
    long_description=README,
    packages=find_packages(),
    install_requires=[
        'flask',
        'passlib',
        'pylmod',
        'PyYAML',
        'WTForms',

    ],
    entry_points={'console_scripts': [
        'lmod_proxy = lmod_proxy.cmd:run_server',
    ]},
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Programming Language :: Python',
    ],
    test_suite="lmod_proxy.tests",
    tests_require=tests_require,
    cmdclass={"test": PyTest},
    include_package_data=True,
    zip_safe=False,
)
