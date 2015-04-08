lmod_proxy
==========
.. image:: https://img.shields.io/travis/mitodl/lmod_proxy.svg
    :target: https://travis-ci.org/mitodl/lmod_proxy
.. image:: https://img.shields.io/coveralls/mitodl/lmod_proxy.svg
    :target: https://coveralls.io/r/mitodl/lmod_proxy
.. image:: https://img.shields.io/github/issues/mitodl/lmod_proxy.svg
    :target: https://github.com/mitodl/lmod_proxy/issues
.. image:: https://img.shields.io/badge/license-AGPLv3-blue.svg
    :target: https://github.com/mitodl/lmod_proxy/blob/master/license

Flask application for proxying requests to the MIT Learning Modules
API from edx-platform.


Quick Start
===========

- Download the latest tar ball or clone from github.
- Run ``pip install -r requirements.txt``
- Make sure you have ``htpasswd`` available/installed
- Run ``htpasswd -c ~/.htpasswd <your username>``
- Create environment variable with path to password file: ``export LMODP_HTPASSWD_PATH=~/.htpasswd``
- Run ``lmod_proxy``
- Go to https://localhost:5000/ and use the form there to try things out

You will also likely need to customize your settings to be able to do
authentication to LMod via a proper certificate.  To do that,
determine the path to your certificate and export that path for the
configuration with a configuration environment variable: ``export
LMODP_CERT=/path/to/mycert.pem``.  The certificate needs to be a plain
(no passphrase) base64 encoded file with both your certificate and
private key from MIT.


Running on Heroku
=================

There is an included Procfile to run the application in heroku, to do
so just create a heroku app, configure the appropriate environment
variables in heroku via ``heroku config:set LMODP_...=...``. The one
catch being that your certificate file and HTPASSWD files probably
shouldn't be checked in with the repository on heroku, so you can
actually copy your entire HTPASSWD file into the ``LMODP_HTPASSWD``
variable and your certificate into ``LMODP_CERT_STRING`` variable.


Configuring edX Platform
========================

To configure your edX platform to use this as your remote gradebook
endpoint, you need to configure a few things, first you need to enable
the feature and point it at the URL of your lmod_proxy server.  Adding
something like: ``FEATURES['REMOTE_GRADEBOOK_URL'] =
'https://<htpasswd_user>:<htpasswd_password>@myapp.herokuapp.com/edx_grades'``
to your config will enable the feature, and then in your course, you
will just need to specify the GradeBook UUID to point at in your
advanced settings with something like:

.. code-block:: json

  "remote_gradebook": {
    "name": "STELLAR:/project/mitxdemosite",
    "section": "devops01"
  }

