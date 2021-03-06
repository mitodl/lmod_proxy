# -*- coding: utf-8 -*-
"""Forms needed for the edx_grade blueprint."""
from flask_wtf import Form
from flask_wtf.file import FileField
from wtforms import SelectField, StringField, validators

from lmod_proxy.edx_grades.actions import (
    post_grades,
    get_membership,
    get_assignments,
    get_sections,
)

ACTIONS = {
    'post-grades': post_grades,
    'get-membership': get_membership,
    'get-assignments': get_assignments,
    'get-sections': get_sections,
}


class StrippedField(StringField):
    """Simple override of String field where values are stripped"""
    def process_data(self, data):
        """Take value list and strip it"""
        if data:
            self.data = data.strip()
        else:
            self.data = None


class EdXGradesForm(Form):
    """Form given to us by edx-platform."""
    gradebook = StrippedField(validators=[validators.required()])
    user = StrippedField(id='user', validators=[validators.Email()])
    datafile = FileField(
        id='datafile',
        validators=[validators.Optional()]
    )
    section = StrippedField(id=u'section', validators=[validators.Optional()])
    submit = SelectField(
        choices=[(x, x) for x in ACTIONS.keys()]
    )
