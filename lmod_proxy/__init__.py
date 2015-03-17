# -*- coding: utf-8 -*-
"""lmod_proxy

Flask application for proxying requests to the MIT Learning Modules
API from edx-platform
"""
import os.path
from pkg_resources import get_distribution, DistributionNotFound

from flask import Flask

from lmod_proxy.edx_grades import edx_grades


def _get_version():
    """Grab version from pkg_resources"""
    # pylint: disable=no-member
    try:
        dist = get_distribution(__project__)
        # Normalize case for Windows systems
        dist_loc = os.path.normcase(dist.location)
        here = os.path.normcase(os.path.abspath(__file__))
        if not here.startswith(
                os.path.join(dist_loc, __project__)
        ):
            # not installed, but there is another version that *is*
            raise DistributionNotFound
    except DistributionNotFound:
        return 'Please install this project with setup.py'
    else:
        return dist.version

__project__ = 'lmod_proxy'
__version__ = _get_version()


app = Flask(__project__)
app.config.from_object('{0}.config'.format(__project__))

app.register_blueprint(edx_grades, url_prefix='/edx_grades')


@app.route('/', methods=['GET'])
def index():
    """Welcome them to our amazing LMod Proxy

    Return:
        Flask.response
    """
    return '<h1>Welcome to LMod-Proxy'
