# -*- coding: utf-8 -*-
"""Blueprint for handling the ``POST`` from the edx-platform
REMOTE_GRADEBOOK feature.
"""
import logging

from flask import (
    Blueprint,
    current_app,
    jsonify,
    request,
    render_template,
)
from pylmod import GradeBook

from lmod_proxy.auth import requires_auth
from lmod_proxy.edx_grades.forms import ACTIONS, EdXGradesForm

log = logging.getLogger('lmod_proxy.edx_grades')
edx_grades = Blueprint(
    'edx_grades',
    __name__,
    template_folder='templates/edx_grades',
    static_folder='static/edx_grades',
)


@edx_grades.route('', methods=['GET', 'POST'])
@requires_auth
def index(user):
    """Handle ``POST`` from edx-platform or print available actions, and
    provide an interactive test of the available actions on ``GET``.

    Returns:
        flask.response: JSON on POST, HTML on GET
    """
    requestor = request.remote_addr
    if request.headers.getlist("X-Forwarded-For"):
        requestor = request.headers.getlist("X-Forwarded-For")[0]

    if request.method == 'POST':
        form = EdXGradesForm()
        log.info('edX remote gradebook POST request from %s', requestor)
        log.debug('Headers: %r', request.headers)
        log.debug('POST data: %r', request.form)
        log.debug('Form values: %r', form.data)
        if form.validate():
            message, data, success = ACTIONS[form.submit.data](
                GradeBook(
                    current_app.config['LMODP_CERT'],
                    current_app.config['LMODP_URLBASE'],
                    gbuuid=form.gradebook.data
                ),
                form
            )
            return jsonify(
                dict(
                    msg=render_template(
                        'api_message.html',
                        message=message,
                        success=success
                    ),
                    data=data
                )
            )
        else:
            response = jsonify(
                dict(
                    msg="Malformed API Call: {0}".format(form.errors), data=[]
                )
            )
            response.status_code = 422
            return response

    elif request.method == 'GET':
        log.info('edX remote gradebook GET request from %s', requestor)
        return render_template(
            'index.html',
            form=EdXGradesForm(),
            cert=current_app.config['LMODP_CERT'],
            urlbase=current_app.config['LMODP_URLBASE'],
            approve_grades=bool(current_app.config['LMODP_APPROVE_GRADES'])
        )
