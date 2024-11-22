from flask import abort
from flask_login import current_user
from functools import wraps


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