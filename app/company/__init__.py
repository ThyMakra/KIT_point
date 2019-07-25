from flask import Blueprint

blueprint = Blueprint(
    'company_blueprint',
    __name__,
    url_prefix='/company',
    template_folder='templates',
    static_folder='static'
)
