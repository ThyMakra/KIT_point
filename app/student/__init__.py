from flask import Blueprint

blueprint = Blueprint(
    'student_blueprint',
    __name__,
    url_prefix='/student',
    template_folder='templates',
    static_folder='static'
)
