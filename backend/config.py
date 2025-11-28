import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv() # Carga las variables del archivo .env

class Config:
    # Genero una clave secreta segura
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # PostgreSQL en Supabase - Connection Pooler para producción
    # Usar el pooler en lugar de la conexión directa para mejor compatibilidad
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres.pqefwwfkjssjkddvgvha:sP9a$AVsfJ48GYt@aws-0-us-west-2.pooler.supabase.com:6543/postgres'
    
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