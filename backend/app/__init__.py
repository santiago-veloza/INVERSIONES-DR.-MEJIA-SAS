from flask import Blueprint, Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Extensiones
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

bp = Blueprint('main', __name__)


def create_app(config_class=Config):
    # Definir rutas para frontend
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'frontend')
    template_folder = os.path.join(frontend_path, 'templates')
    static_folder = os.path.join(frontend_path, 'static')
    
    app = Flask(__name__, 
                template_folder=template_folder,
                static_folder=static_folder)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    # Crea la carpeta de uploads si no existe
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Importar módulos que dependen de db/login_manager
    from app import models
    from app import routes, forms

    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    return app


# Importar rutas, modelos y formularios para que sean accesibles desde el blueprint
from app import routes, models, forms