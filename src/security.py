__author__ = 'Tsintsir'

from db import DatabaseWrapper
from functools import wraps
from flask import request, Response
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
        token = request.token
        # TODO: Better secret handling.
        try:
            jwt.decode(token, 'gitsubmitsecret')
        except jwt.ExpiredSignatureError as e:
            return token_expiration_error()
        except jwt.DecodeError as e:
            return token_decode_error()
        return f(*args, **kwargs)
    return decorated