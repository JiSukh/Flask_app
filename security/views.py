from flask import Blueprint, render_template
from utils import roles_required, get_last_n_lines


from config import Config

from models import Log




security_bp = Blueprint('security', __name__, template_folder='templates')

@security_bp.route('/security')
@roles_required('sec_admin')
def security():

    log_file = get_last_n_lines(Config.LOG_FILE_PATH, n=10)
    logs = Log.query.limit(20).all()


    return render_template("security/security.html", logs = logs, logs_from_file = log_file)
