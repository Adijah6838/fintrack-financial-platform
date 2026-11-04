import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from .config import DevelopmentConfig

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=DevelopmentConfig):
    # Dynamically get the root directory (fintrack/)
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Tell Flask where to find templates and static files
    app = Flask(__name__, 
                template_folder=os.path.join(root_dir, 'templates'),
                static_folder=os.path.join(root_dir, 'static'))
                
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app import models

    # Register API Blueprints
    from app.routes.health import health_bp
    from app.routes.auth import auth_bp
    from app.routes.accounts import accounts_bp
    from app.routes.transactions import transactions_bp
    from app.routes.fraud import fraud_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(accounts_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(fraud_bp)
    app.register_blueprint(admin_bp)

    # Register Frontend Views Blueprint
    from app.routes.views import views_bp
    app.register_blueprint(views_bp)

    return app