from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .routes import main_bp
from .models import db, User  # Import db from models
from .auth import auth_bp  # Ensure this import is correct if you have an 'auth' blueprint

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '57b2316a3e3e3e3e3e3e3e3e3e3e3e3e'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    
    db.init_app(app)
    
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'  # Update this to 'auth.login' if the login route is under 'auth' blueprint
    login_manager.login_message_category = 'info'
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')  # Register with a prefix if needed
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
