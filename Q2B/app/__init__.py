from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
import os

def create_app():
    # Get the absolute path to the app directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Initialize Flask with explicit template folder
    app = Flask(__name__, 
                template_folder=os.path.join(app_dir, 'templates'),
                static_folder=os.path.join(app_dir, 'assets'))
    
    # MongoDB Configuration
    app.config['MONGODB_SETTINGS'] = {
        'db':'q2b_library',  # ← Q2B database
        'host':'localhost'
    }
    
    # Secret key
    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    
    # AGGRESSIVE CACHE DISABLING
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['DEBUG'] = True
    app.config['EXPLAIN_TEMPLATE_LOADING'] = True
    
    # Initialize MongoDB
    db = MongoEngine(app)
    
    # Disable ALL Jinja2 caching
    app.jinja_env.auto_reload = True
    app.jinja_env.cache = {}
    app.jinja_env.bytecode_cache = None
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please login or register first to get an account."
    
    # Debug: Print template folder location
    print(f"📁 Template folder: {app.template_folder}")
    print(f"📁 Static folder: {app.static_folder}")
    
    return app, db, login_manager

app, db, login_manager = create_app()