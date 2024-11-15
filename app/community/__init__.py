# app/login/__init__.py
from flask import Blueprint

community_bp = Blueprint('community', __name__, template_folder='templates')

from app.community import routes
