import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv() # Carga las variables del archivo .env

class Config:
    # Generar una clave secreta segura si no existe en el entorno
    _secret_key = os.environ.get('SECRET_KEY')
    if not _secret_key:
        # Solo en desarrollo - generar clave temporal
        # En producción esto debe ser una variable de entorno
        print("WARNING: SECRET_KEY no encontrada en variables de entorno. Generando clave temporal.")
        print("Para producción, configure SECRET_KEY como variable de entorno.")
        _secret_key = secrets.token_hex(32)
    
    SECRET_KEY = _secret_key
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'frontend', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB max upload size
    
    # Configuraciones de seguridad para sesiones
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'  # Solo HTTPS en producción
    SESSION_COOKIE_HTTPONLY = True  # Prevenir acceso vía JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protección CSRF básica
    
    # Configuración de timeout de sesión (TIEMPOS REDUCIDOS PARA PRUEBAS)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=2)  # 2 minutos para pruebas
    SESSION_TIMEOUT_WARNING = timedelta(minutes=1)     # Advertencia a 1 minuto
    SESSION_REFRESH_EACH_REQUEST = True  # Renovar sesión en cada request