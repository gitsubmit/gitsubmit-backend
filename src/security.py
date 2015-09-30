__author__ = 'Tsintsir'

from db import login
from functools import wraps
from flask import request, Response

# Pretty much copied from http://flask.pocoo.org/snippets/8/

def basic_not_authenticated():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def basic_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not login(auth.username, auth.password):
            return basic_not_authenticated()
        return f(*args, **kwargs)
    return decorated