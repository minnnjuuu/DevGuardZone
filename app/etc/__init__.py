# app/etc/__init__.py
from flask import Blueprint

about_bp = Blueprint('etc', __name__, template_folder='templates')

from app.etc import routes
