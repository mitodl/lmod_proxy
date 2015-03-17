# -*- coding: utf-8 -*-
"""Blueprint for handling the ``POST`` from the edx-platform
REMOTE_GRADEBOOK feature.
"""
from flask import (
    Blueprint,
)

edx_grades = Blueprint(
    'lmod_proxy_edx_grades',
    __name__,
    template_folder='templates/edx_grades',
    static_folder='static/edx_grades',
)


@edx_grades.route('/', methods=['GET'])
def index():
    """Handle ``POST`` from edx-platform or print available actions, and
    provide an interactive test of the available actions on ``GET``.

    Returns:
        flask.response

    """
    return '<h1>LMod Proxy edX Grades "API"</h1>'
