from flask import Blueprint

error = Blueprint('errors', __name__, template_folder='templates')
