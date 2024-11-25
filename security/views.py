from flask import Blueprint, render_template
from utils import roles_required
import config



security_bp = Blueprint('security', __name__, template_folder='templates')

@security_bp.route('/security')
@roles_required('sec_admin')
def security():
    logs = config.Log.query.all()
    return render_template("security/security.html", logs = logs)