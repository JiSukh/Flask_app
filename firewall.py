from flask import request, render_template

import re
import logging


logger = logging.getLogger('logger')

conditions = {
    "sql_injection": r"(union|select|insert|drop|;|'|--)",
    "xss": r"(<script|<iframe|%3Cscript|%3Ciframe)",
    "path_traversal": r"(\.\.\/|\.\.\\|%2e%2e%2f|%2e%2e%5c|%2e%2e\/|%2e%2e\\)"
}

def check_for_attack():
    print(request.query_string.decode())
    for attack_type, attack_pattern in conditions.items():
        #Check if the attack pattern matches the request path or query string
        if re.search(attack_pattern, request.path, re.IGNORECASE) or re.search(attack_pattern, request.query_string.decode(), re.IGNORECASE ):
            return render_template('attacks/attack.html', label = attack_type)  
    