from flask import Blueprint

blueprint = Blueprint(
    'project_blueprint',
    __name__,
    url_prefix='/project',
    template_folder='templates',
    static_folder='static'
)
