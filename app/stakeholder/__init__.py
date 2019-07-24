from flask import Blueprint

blueprint = Blueprint(
    'stakeholder_blueprint',
    __name__,
    url_prefix='/stakeholder',
    template_folder='templates',
    static_folder='static'
)
