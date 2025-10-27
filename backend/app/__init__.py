from flask import Blueprint, Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os

# Extensiones que implementé
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
csrf = CSRFProtect()

bp = Blueprint('main', __name__)


def create_app(config_class=Config):
    # Defino rutas para frontend
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'frontend')
    template_folder = os.path.join(frontend_path, 'templates')
    static_folder = os.path.join(frontend_path, 'static')
    
    app = Flask(__name__, 
                template_folder=template_folder,
                static_folder=static_folder)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    # Deshabilito CSRF temporalmente para evitar problemas de tokens
    # csrf.init_app(app)

    # Creo la carpeta de uploads si no existe
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Importo módulos que dependen de db/login_manager
    from app import models
    from app import routes, forms

    app.register_blueprint(bp)

    # Middleware de timeout de sesión que implementé
    @app.before_request
    def check_session_timeout():
        from flask import session, request
        from flask_login import current_user, logout_user
        from datetime import datetime, timedelta
        
        # Excluyo rutas que no requieren autenticación o son estáticas
        excluded_routes = ['main.login', 'main.logout', 'static']
        excluded_paths = ['/static/', '/api/session/']
        
        # Verifico si la ruta debe ser excluida
        if request.endpoint in excluded_routes:
            return
            
        # Verifico si es una ruta estática o de API de sesión
        for path in excluded_paths:
            if request.path.startswith(path):
                return
                
        if current_user.is_authenticated:
            # Verifico última actividad
            last_activity = session.get('last_activity')
            
            if last_activity:
                try:
                    last_activity = datetime.fromisoformat(last_activity)
                    if datetime.now() - last_activity > app.config['PERMANENT_SESSION_LIFETIME']:
                        logout_user()
                        session.clear()
                        from flask import flash, redirect, url_for
                        flash('Su sesión ha expirado por inactividad. Por favor, inicie sesión nuevamente.', 'warning')
                        return redirect(url_for('main.login'))
                except (ValueError, TypeError):
                    # Si hay error al parsear la fecha, creo nueva marca de tiempo
                    session['last_activity'] = datetime.now().isoformat()
            else:
                # Si no hay marca de tiempo, creo una nueva
                session['last_activity'] = datetime.now().isoformat()
            
            # Actualizo última actividad solo si no es una llamada de API de sesión
            if not request.path.startswith('/api/session/status'):
                session['last_activity'] = datetime.now().isoformat()
                session.permanent = True

    # Configuro headers de seguridad (temporalmente deshabilitado para debug)
    # @app.after_request
    # def security_headers(response):
    #     # Content Security Policy - Más permisivo para Bootstrap
    #     response.headers['Content-Security-Policy'] = (
    #         "default-src 'self'; "
    #         "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
    #         "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
    #         "font-src 'self' https://cdnjs.cloudflare.com; "
    #         "img-src 'self' data:; "
    #         "connect-src 'self'"
    #     )
    #     # Otros headers de seguridad
    #     response.headers['X-Content-Type-Options'] = 'nosniff'
    #     response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    #     response.headers['X-XSS-Protection'] = '1; mode=block'
    #     response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    #     return response

    # Manejo de errores CSRF deshabilitado
    # @app.errorhandler(400)
    # def handle_csrf_error(e):
    #     from flask import flash, redirect, url_for
    #     if 'CSRF' in str(e):
    #         flash('Error de seguridad CSRF. Por favor, actualice la página e intente de nuevo.', 'error')
    #         return redirect(url_for('main.login'))
    #     return e

    with app.app_context():
        db.create_all()

    return app


# Importar rutas, modelos y formularios para que sean accesibles desde el blueprint
from app import routes, models, forms