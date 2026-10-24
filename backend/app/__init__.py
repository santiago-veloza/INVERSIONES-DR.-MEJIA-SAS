from flask import Blueprint, Flask
from backend.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
import os
import logging
from logging.handlers import RotatingFileHandler

# Extensiones
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = 'Por favor, inicie sesión para acceder a esta página.'
login_manager.login_message_category = 'info'
csrf = CSRFProtect()
cache = Cache()

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
    
    # Inicializar configuración específica
    config_class.init_app(app)
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    
    # Habilitar CSRF en producción, deshabilitar en desarrollo
    if not app.config.get('DEBUG', False):
        csrf.init_app(app)
    
    # Configurar cache
    cache.init_app(app, config={
        'CACHE_TYPE': app.config.get('CACHE_TYPE', 'simple'),
        'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
    })
    
    # Crear carpeta de uploads si no existe
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Configurar logging para desarrollo
    if app.config.get('DEBUG', False):
        logging.basicConfig(
            level=getattr(logging, app.config.get('LOG_LEVEL', 'INFO')),
            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )

    # Importo módulos que dependen de db/login_manager
    from backend.app import models
    from backend.app import routes, forms

    app.register_blueprint(bp)

    # Filtro personalizado para formatear números con separador de miles
    @app.template_filter('format_currency')
    def format_currency(value):
        """Formatea un número como moneda con separador de miles (puntos) y decimales con coma"""
        try:
            # Convertir a float si es string
            if isinstance(value, str):
                value = float(value)
            
            # Verificar si el número tiene decimales significativos
            if value % 1 == 0:
                # Si no tiene decimales, formatear sin decimales
                formatted = "{:,.0f}".format(value)
            else:
                # Si tiene decimales, formatear con 2 decimales
                formatted = "{:,.2f}".format(value)
            
            # Reemplazar coma por punto para miles y punto por coma para decimales (formato colombiano)
            formatted = formatted.replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')
            return formatted
        except (ValueError, TypeError):
            return value

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

    # Headers de seguridad HTTP
    @app.after_request
    def security_headers(response):
        from flask import request
        # Content Security Policy - permisivo con Bootstrap/Chart.js/Popper vía CDN
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://fonts.gstatic.com; "
            "img-src 'self' data: https://res.cloudinary.com; "
            "connect-src 'self'"
        )
        # Otros headers de seguridad
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    # Manejo de errores CSRF deshabilitado
    # @app.errorhandler(400)
    # def handle_csrf_error(e):
    #     from flask import flash, redirect, url_for
    #     if 'CSRF' in str(e):
    #         flash('Error de seguridad CSRF. Por favor, actualice la página e intente de nuevo.', 'error')
    #         return redirect(url_for('main.login'))
    #     return e

    # Crear índices de rendimiento para optimizar consultas del dashboard
    with app.app_context():
        try:
            # Crear índices si no existen (mejora rendimiento del dashboard)
            db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_workorder_sede_id ON work_order(sede_id)"))
            db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_workorder_status ON work_order(status)"))
            db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_workorder_payment_status ON work_order(payment_status)"))
            db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_workorder_created_at ON work_order(created_at)"))
            db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_workorder_sede_created ON work_order(sede_id, created_at)"))
            db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_workorder_sede_payment ON work_order(sede_id, payment_status)"))
            db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_workorder_lens_class ON work_order(lens_class)"))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Info: Índices ya existentes o no se pudieron crear: {e}")

    # Limpieza automática del registro de auditoría: borra entradas de más de
    # 140 horas para que la tabla no crezca indefinidamente. Se revisa cada
    # hora. El chequeo de WERKZEUG_RUN_MAIN evita que el reloader de Flask
    # (modo debug) arranque el programador dos veces.
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        from apscheduler.schedulers.background import BackgroundScheduler

        def cleanup_old_audit_logs():
            with app.app_context():
                from datetime import datetime, timedelta
                from backend.app.models import AuditLog
                cutoff = datetime.utcnow() - timedelta(hours=140)
                deleted = AuditLog.query.filter(AuditLog.timestamp < cutoff).delete()
                db.session.commit()
                if deleted:
                    app.logger.info(f'Limpieza automática: {deleted} registro(s) de auditoría de más de 140 horas eliminados.')

        scheduler = BackgroundScheduler(daemon=True)
        scheduler.add_job(cleanup_old_audit_logs, 'interval', hours=1, id='cleanup_audit_logs', replace_existing=True)
        scheduler.start()

    return app


# Importar rutas, modelos y formularios para que sean accesibles desde el blueprint
from backend.app import routes, models, forms