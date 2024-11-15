# app/learn/__init__.py
from flask import Blueprint

learn_bp = Blueprint('learn', __name__, template_folder='templates')

from app.learn import routes
