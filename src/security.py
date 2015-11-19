from datetime import timedelta

__author__ = 'Tsintsir'

from db import DatabaseWrapper
from flask import g
from functools import wraps, update_wrapper
from flask import request, Response, make_response
import jwt

# Pretty much copied from http://flask.pocoo.org/snippets/8/


def basic_not_authenticated():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="GitSubmit"'})


def token_expiration_error():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'Your session has expired.', 401,
    {'WWW-Authenticate': 'Basic realm="GitSubmit"'})


def token_decode_error():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'Token could not be decoded.', 401,
    {'WWW-Authenticate': 'Basic realm="GitSubmit"'})


# This just checks to see if the user has a valid session.
def basic_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers['token']
        # TODO: Better secret handling.
        try:
            result = jwt.decode(token, 'gitsubmitsecret')
            g.token = result
        except jwt.ExpiredSignatureError as e:
            return token_expiration_error()
        except jwt.DecodeError as e:
            return token_decode_error()
        return f(*args, **kwargs)
    return decorated


# needed since api.gitsubmit is a different domain than gitsubmit
def crossdomain(app=None, origin=None, methods=None, headers='Origin, X-Requested-With, Content-Type',
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator