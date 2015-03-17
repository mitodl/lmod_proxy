# -*- coding: utf-8 -*-
"""Blueprint for handling the ``POST`` from the edx-platform
REMOTE_GRADEBOOK feature.
"""
from flask import (
    Blueprint,
)
from wtforms import Form, SelectField, StringField


ACTIONS = {
    'post-grades': None,
    'get-membership': None,
    'get-assignments': None,
    'get-sections': None,
}


class EdXGradesForm(Form):
    """Form given to us by edx-platform."""
    gbuuid = StringField(u'gbuuid')
    user = StringField(u'user')
    action = SelectField(
        u'submit',
        choices=[(x, x) for x in ACTIONS.keys()]
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
