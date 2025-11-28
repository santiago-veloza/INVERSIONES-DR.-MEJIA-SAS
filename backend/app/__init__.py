from flask import Blueprint, Flask
from backend.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os

# Extensiones que implementé
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = 'Por favor, inicie sesión para acceder a esta página.'
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
    from backend.app import models
    from backend.app import routes, forms

    app.register_blueprint(bp)

    # Middleware de seguridad y timeout de sesión que implementé
    @app.before_request
    def security_middleware():
        # Primero ejecutar detección de actividades sospechosas
        from backend.app.security import (
            suspicious_activities, failed_attempts, rate_limits,
            log_security_event, EventTypes, Severity
        )
        from flask import request
        from flask_login import current_user
        from datetime import datetime, timedelta
        import re
        
        ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        user_agent = request.headers.get('User-Agent', '')
        endpoint = request.endpoint or 'unknown'
        
        # Detectar patrones sospechosos globalmente
        suspicious_flags = []
        
        # 1. Rate limiting básico por IP
        current_time = datetime.utcnow()
        rate_limits[ip] = [t for t in rate_limits[ip] if current_time - t < timedelta(minutes=1)]
        rate_limits[ip].append(current_time)
        
        if len(rate_limits[ip]) > 30:  # Más de 30 requests por minuto
            suspicious_flags.append('RATE_LIMIT_EXCEEDED')
        
        # 2. Detectar patrones de ataque en User-Agent
        suspicious_ua_patterns = [
            r'sqlmap', r'nikto', r'burp', r'nmap', r'masscan',
            r'python-requests', r'wget', r'curl.*bot', r'scanner',
            r'exploit', r'hack', r'injection'
        ]
        
        for pattern in suspicious_ua_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                suspicious_flags.append(f'SUSPICIOUS_USER_AGENT:{pattern}')
        
        # 3. Detectar intentos de acceso a rutas no existentes sospechosas
        if endpoint == 'static' and any(x in request.path.lower() for x in ['.php', '.asp', '.jsp', 'admin', 'wp-', 'config', '.env']):
            suspicious_flags.append('SUSPICIOUS_PATH_ACCESS')
        
        # 4. Detectar parámetros sospechosos
        for param_name, param_value in request.args.items():
            if any(x in str(param_value).lower() for x in ['<script', 'javascript:', 'union select', 'drop table', '../', '..\\', 'eval(']):
                suspicious_flags.append(f'SUSPICIOUS_PARAMETER:{param_name}')
        
        # 5. Detectar contenido POST sospechoso
        if request.method == 'POST' and request.form:
            for field_name, field_value in request.form.items():
                if isinstance(field_value, str) and any(x in field_value.lower() for x in ['<script', 'javascript:', 'union select', 'drop table']):
                    suspicious_flags.append(f'SUSPICIOUS_POST_DATA:{field_name}')
        
        # Registrar actividad sospechosa si se detectó algo
        if suspicious_flags:
            severity = Severity.CRITICAL if len(suspicious_flags) >= 3 else Severity.WARNING
            
            metadata = {
                'flags': suspicious_flags,
                'endpoint': endpoint,
                'path': request.path,
                'method': request.method,
                'args': dict(request.args),
                'rate_limit_count': len(rate_limits[ip]),
                'user_agent': user_agent[:200]  # Limitar longitud
            }
            
            log_security_event(
                event_type=EventTypes.SUSPICIOUS_ACTIVITY,
                description=f"Actividad sospechosa detectada: {', '.join(suspicious_flags)}",
                severity=severity,
                user=current_user if current_user.is_authenticated else None,
                metadata=metadata
            )
    
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

    # Las tablas ya están creadas en Supabase
    # with app.app_context():
    #     db.create_all()

    return app


# Importar rutas, modelos y formularios para que sean accesibles desde el blueprint
from backend.app import routes, models, forms