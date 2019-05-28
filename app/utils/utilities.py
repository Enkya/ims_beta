from re import search
from flask import g, request
from flask_httpauth import HTTPTokenAuth
from app.models.user import User
import os
import json

auth = HTTPTokenAuth(scheme='Token')


def validate_email(email):
    ''' Method to check that a valid email is provided '''
    email_re = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return True if search(email_re, email) else False

@auth.verify_token
def verify_token(token=None):
    ''' Method to verify token '''
    token = request.headers.get('x-access-token') or ''
    user_id = User.verify_authentication_token(token)
    if user_id:
        g.user = User.query.filter_by(id=user_id).first()
        return True
    return False

def load_json_data(file_path, file_name):
    """
        this function loads JSON blobs from files on the path
    """
    # TODO create a read-safe method
    with open(os.path.join(file_path, "%s.json" % file_name), "r") as data:
        json_data = json.load(data)
    return json_data

def updateObject(obj, args):
    ''' update object with given args '''
    for k, v in args.items():
        v = (v.strip() if isinstance(v, str) else v) or None
        setattr(obj, k, v)
    return obj
