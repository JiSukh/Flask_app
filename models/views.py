from flask import abort
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView


class UserView(ModelView):
    column_display_pk = True  # optional, but I like to see the IDs in the list
    column_hide_backrefs = False
    column_list = ('id', 'email', 'password', 'firstname', 'lastname', 'phone', 'posts', 'mfa_enable', 'mfa_key', 'salt')
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'db_admin'
    
    def inaccessible_callback(self, name, **kwargs):
        abort(403)

class LogView(ModelView):
    column_display_pk = True  # optional, but I like to see the IDs in the list
    column_hide_backrefs = False

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'db_admin'
    
    def inaccessible_callback(self, name, **kwargs):
        abort(403)

class PostView(ModelView):
    column_display_pk = True  
    column_hide_backrefs = False
    column_list = ('id', 'userid', 'created', 'title', 'body', 'user')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'db_admin'
    
    def inaccessible_callback(self, name, **kwargs):
        abort(403)