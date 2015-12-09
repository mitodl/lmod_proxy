# -*- coding: utf-8 -*-
"""Actions to perform based on API request.
"""
import logging

from flask import render_template, current_app
from requests.exceptions import RequestException

from pylmod.exceptions import PyLmodException

log = logging.getLogger(__name__)


def post_grades(gradebook, form):
    """post grades to LMod using :py:class::`pylmod.GradeBook`

    Args:
        gradebook (pylmod.GradeBook): Instantiated grade book class.
        form (lmod_proxy.edx_grades.forms.EdXGradesForm): validated form.
    Returns:
        tuple: message(str), data(list), success(bool)
    """
    error_message = ''
    approve_grades = False
    if current_app.config['LMODP_APPROVE_GRADES']:
        approve_grades = True
    csv_file = form.datafile.data.stream
    log.debug('Received grade CSV: %s', csv_file.read())
    # Seek back to 0 for future reading
    csv_file.seek(0)
    results = None
    try:
        # Create assignment to explicitly set max points.
        assignment, max_points = _get_assignment_name_max_points(form)
        gradebook.create_assignment(
            assignment[0:3] + assignment[-2:],
            assignment,
            1.0,
            max_points,
            '12-15-2013',
            gradebook.gradebook_id
        )
        results, time_taken = gradebook.spreadsheet2gradebook(
            csv_file=csv_file, approve_grades=approve_grades
        )
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


def _get_assignment_name_max_points(form):
    try:
        csv_data = form.datafile.data.stream.read()
        short_name = csv_data[0][1]
        max_points = csv_data[1][2]
        return short_name, max_points
    except IOError:
        raise
