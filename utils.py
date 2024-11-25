from flask import abort
from flask_login import current_user
from functools import wraps
import os

def roles_required(*roles):
    def inner_decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not hasattr(current_user, 'role'):
                abort(401)
            elif current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return inner_decorator

def get_last_n_lines(file_path, n=10):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            return lines[-n:]  
    else:
        return []
