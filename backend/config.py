import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del archivo .env

class Config:
    # Clave secreta desde variable de entorno o generada
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Base de datos - se define en la variable de entorno SQLALCHEMY_DATABASE_URI (.env)
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración optimizada del pool de conexiones
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,          # Verifica conexiones antes de usarlas
        'pool_recycle': 300,            # Recicla conexiones cada 5 minutos
        'pool_size': 10,                # Máximo de conexiones en el pool
        'max_overflow': 20,             # Conexiones adicionales permitidas
        'pool_timeout': 30,             # Timeout para obtener conexión del pool
    }
    
    # Configuración de archivos
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'frontend', 'static', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB default
    
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True  
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuración de timeout de sesión: cierre por inactividad y aviso previo
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=int(os.environ.get('PERMANENT_SESSION_LIFETIME', 17)))  # 17 minutos default
    SESSION_TIMEOUT_WARNING = timedelta(minutes=int(os.environ.get('SESSION_TIMEOUT_WARNING', 15)))     # Aviso 2 minutos antes
    SESSION_REFRESH_EACH_REQUEST = True  # Renovar sesión en cada request
    
    # Configuración de cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))  # 5 minutos default
    
    # Configuración de desarrollo/producción
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')

    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@opticas.com')
    SEDE_SHARED_PASSWORD = os.environ.get('SEDE_SHARED_PASSWORD', 'OpticasDrMejia2024')
    
    @staticmethod
    def init_app(app):
        """Inicialización específica de la aplicación"""
        # Configurar logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            # Crear directorio de logs si no existe
            log_dir = os.path.dirname(Config.LOG_FILE)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Configurar handler de archivo con rotación
            file_handler = RotatingFileHandler(
                Config.LOG_FILE, 
                maxBytes=10240000,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
            app.logger.addHandler(file_handler)
            app.logger.setLevel(getattr(logging, Config.LOG_LEVEL))
            app.logger.info('Inversiones Dr. Mejia SAS startup')


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Permitir HTTP en desarrollo
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)  # Sesiones más cortas en desarrollo


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Forzar HTTPS en producción
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log de errores críticos vía email (opcional)
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER or 'localhost', cls.MAIL_PORT or 587),
            fromaddr=cls.MAIL_USERNAME or 'noreply@opticasdrmejia.com',
            toaddrs=[cls.ADMIN_EMAIL or 'admin@opticasdrmejia.com'],
            subject='Inversiones Dr. Mejia SAS - Error',
            credentials=credentials,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}