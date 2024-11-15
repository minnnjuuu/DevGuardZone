# app/__init__.py
from flask import Flask
from config import Config
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 데이터베이스 연결 및 종료 설정
    from app.db_connection import get_db, close_db
    app.teardown_appcontext(close_db)

    # 블루프린트 등록
    from app.community import community_bp
    from app.learn import learn_bp
    from app.etc import about_bp

    jwt = JWTManager(app)
    
    app.register_blueprint(community_bp)
    app.register_blueprint(learn_bp)
    app.register_blueprint(about_bp)

    return app
