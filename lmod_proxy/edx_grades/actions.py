# -*- coding: utf-8 -*-
"""Actions to perform based on API request.
"""
from cStringIO import StringIO

from flask import render_template
from requests.exceptions import RequestException

from pylmod.exceptions import PyLmodException


def post_grades(gradebook, form):
    """post grades to LMod using :py:class::`pylmod.GradeBook`

    Args:
        gradebook (pylmod.GradeBook): Instantiated grade book class.
        form (lmod_proxy.edx_grades.forms.EdXGradesForm): validated form.
    Returns:
        tuple: message(str), data(list), success(bool)
    """
    error_message = ''

    fake_csv = StringIO(form.datafile.data)
    results = None
    try:
        results, time_taken = gradebook.spreadsheet2gradebook(fake_csv)
    except PyLmodException, ex:
        error_message = unicode(ex)

    number_failed = 0
    if results and results.get('data'):
        number_failed = int(results['data'].get('numFailures', 0))
    if number_failed > 0:
        error_message = render_template(
            'grade_transfer_failed.html',
            number_failed=number_failed,
            failed_grades=results['data']['results']
        )
    return (
        error_message or 'Successfully posted grades',
        [],
        not bool(error_message)
    )


def get_membership(gradebook, form):
    """Return students in gradebook specified

    Args:
        gradebook (pylmod.GradeBook): Instantiated grade book class.
        form (lmod_proxy.edx_grades.forms.EdXGradesForm): validated form.
    Returns:
        tuple: message(str), data(list), success(bool)
    """
    error_message = ''
    try:
        data = gradebook.get_students(
            simple=True,
            section_name=form.section.data
        )
    except (PyLmodException, RequestException), ex:
        data = [{}]
        error_message = unicode(ex)
    return (
        error_message or 'Successfully retrieved students',
        data,
        not bool(error_message)
    )


def get_assignments(gradebook, form):
    """Return the assignments available in LMod for the gradebook

    Args:
        gradebook (pylmod.GradeBook): Instantiated grade book class.
        form (lmod_proxy.edx_grades.forms.EdXGradesForm): validated form.
    Returns:
        tuple: message(str), data(list), success(bool)
    """
    error_message = ''
    try:
        data = gradebook.get_assignments(simple=True)
    except (PyLmodException, RequestException), ex:
        data = [{}]
        error_message = unicode(ex)
    return (
        error_message or 'Successfully retrieved assignments',
        data,
        not bool(error_message)
    )


def get_sections(gradebook, form):
    """Return the sections available in LMod for the gradebook

    Args:
        gradebook (pylmod.GradeBook): Instantiated grade book class.
        form (lmod_proxy.edx_grades.forms.EdXGradesForm): validated form.
    Returns:
        tuple: message(str), data(list), success(bool)
    """
    error_message = ''
    try:
        data = gradebook.get_sections(simple=True)
    except (PyLmodException, RequestException), ex:
        data = [{}]
        error_message = unicode(ex)
    return (
        error_message or 'Successfully retrieved sections',
        data,
        not bool(error_message)
    )
