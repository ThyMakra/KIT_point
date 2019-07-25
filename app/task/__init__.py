from flask import Blueprint

blueprint = Blueprint(
    'task_blueprint',
    __name__,
    url_prefix='/task',
    template_folder='templates',
    static_folder='static'
)
