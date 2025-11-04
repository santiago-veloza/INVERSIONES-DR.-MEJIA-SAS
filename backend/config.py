import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv() # Carga las variables del archivo .env

class Config:
    # Genero una clave secreta segura si no existe en el entorno
    _secret_key = os.environ.get('SECRET_KEY')
    if not _secret_key:
        # Solo en desarrollo - genero clave temporal
        # En producción esto que implementé debe ser una variable de entorno
        print("WARNING: SECRET_KEY no encontrada en variables de entorno. Generando clave temporal.")
        print("Para producción, configure SECRET_KEY como variable de entorno.")
        _secret_key = secrets.token_hex(32)
    
    SECRET_KEY = _secret_key
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'frontend', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB max upload size
    
    # Configuraciones de seguridad para sesiones que implementé (simplificado para debug)
    SESSION_COOKIE_SECURE = False  # Deshabilitado temporalmente para desarrollo
    SESSION_COOKIE_HTTPONLY = True  
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protección CSRF básica
    
    # Configuración de timeout de sesión que implementé (TIEMPOS REDUCIDOS PARA PRUEBAS)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=12)  # 12 minutos para pruebas
    SESSION_TIMEOUT_WARNING = timedelta(minutes=11)     # Advertencia a 11 minutos
    SESSION_REFRESH_EACH_REQUEST = True  # Renovar sesión en cada request