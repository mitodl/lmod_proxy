# -*- coding: utf-8 -*-
"""Basic authentication decorator for views"""
from functools import wraps
from flask import current_app, request, Response


def check_basic_auth(username, password):
    """
    This function is called to check if a username /
    password combination is valid via the htpasswd file.
    """
    valid = current_app.config['users'].check_password(username, password)
    if not valid:
        current_app.logger.warning('Invalid login from %s', username)
        valid = False
    return (
        valid,
        username
    )


def auth_failed():
    """
    Sends a 401 response that enables basic auth
    """
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )


def requires_auth(func):
    """
    Decorator function with basic and token authentication handler
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        """
        Actual wrapper to run the auth checks.
        """
        basic_auth = request.authorization
        is_valid = False
        if basic_auth:
            is_valid, user = check_basic_auth(
                basic_auth.username, basic_auth.password
            )
        if not is_valid:
            return auth_failed()
        kwargs['user'] = user
        return func(*args, **kwargs)
    return decorated
