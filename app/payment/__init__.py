from flask import Blueprint

payment_blueprint = Blueprint('payment', __name__, template_folder='templates')

from . import views