from flask import render_template, request, abort
from flask_login import current_user
from config import *



@app.route('/')
def index():
    return render_template("home/index.html")

@app.route("/favicon.ico")
def favicon():
    return "", 200

@app.errorhandler(Exception)
def handle_error(e):
    error_code = getattr(e, 'code', 500)

    if error_code == 403:
        logger.warning(f'[User:{current_user.email}, Role:{current_user.role}, IP:{request.remote_addr}, URL requested: {request.url}] Unauthorised access request.')
    return render_template(f'errors/{error_code}.html', error=e), error_code    

@app.before_request
def check_for_admin(*args, **kw):
    if request.path.startswith('/admin/'):
        if not hasattr(current_user, 'role'):
            abort(401)
        elif not current_user.role == 'db_admin':
            abort(403)


if __name__ == '__main__':
    app.run()