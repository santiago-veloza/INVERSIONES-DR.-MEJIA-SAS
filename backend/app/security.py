from functools import wraps
from flask import request, session, current_app, g
from flask_login import current_user
from datetime import datetime, timedelta
import json
import re
import hashlib
from collections import defaultdict
from app.models import AuditLog, db

# Cache para detectar patrones anómalos
suspicious_activities = defaultdict(list)
failed_attempts = defaultdict(list)
rate_limits = defaultdict(list)

def audit_action(action_type, description=None, resource_type=None, resource_id=None, 
                severity='INFO', category='USER_ACTION', requires_attention=False):
    """
    Decorador para revisar automáticamente acciones en rutas
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Información del usuario - verificar si está autenticado
            user = None
            if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                user = current_user
            
            # Generar descripción automática si no se proporciona
            auto_description = description or f"Ejecutó {f.__name__} en {request.endpoint}"
            
            # Información adicional de la request
            metadata = {
                'endpoint': request.endpoint,
                'method': request.method,
                'args': str(args) if args else None,
                'kwargs': str(kwargs) if kwargs else None,
                'referer': request.referrer,
                'form_data': dict(request.form) if request.form else None
            }
            
            # Ejecutar la función original
            try:
                result = f(*args, **kwargs)
                
                # Log exitoso
                AuditLog.log_action(
                    action_type=action_type,
                    description=auto_description,
                    user=user,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    severity=severity,
                    category=category,
                    metadata=metadata,
                    requires_attention=requires_attention
                )
                
                return result
                
            except Exception as e:
                # Log de error
                error_metadata = metadata.copy()
                error_metadata['error'] = str(e)
                error_metadata['error_type'] = type(e).__name__
                
                AuditLog.log_action(
                    action_type=f"{action_type}_ERROR",
                    description=f"Error en {auto_description}: {str(e)}",
                    user=user,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    severity='ERROR',
                    category='SYSTEM',
                    metadata=error_metadata,
                    requires_attention=True
                )
                
                raise  # Re-raise la excepción original
                
        return decorated_function
    return decorator


def detect_suspicious_activity():
    """
    para detectar actividades sospechosas
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
            user_agent = request.headers.get('User-Agent', '')
            endpoint = request.endpoint or 'unknown'
            
            # Detectar patrones sospechosos
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
                r'python-requests', r'wget', r'curl', r'bot', r'crawler',
                r'scanner', r'exploit', r'hack'
            ]
            
            for pattern in suspicious_ua_patterns:
                if re.search(pattern, user_agent, re.IGNORECASE):
                    suspicious_flags.append(f'SUSPICIOUS_USER_AGENT:{pattern}')
            
            # 3. Detectar intentos de acceso a rutas no existentes
            if endpoint == 'static' and any(x in request.path.lower() for x in ['.php', '.asp', '.jsp', 'admin', 'wp-', 'config']):
                suspicious_flags.append('SUSPICIOUS_PATH_ACCESS')
            
            # 4. Detectar parámetros sospechosos
            for param_name, param_value in request.args.items():
                if any(x in str(param_value).lower() for x in ['<script', 'javascript:', 'union select', 'drop table', '../']):
                    suspicious_flags.append(f'SUSPICIOUS_PARAMETER:{param_name}')
            
            # 5. Detectar múltiples fallos de autenticación desde la misma IP
            if endpoint in ['main.login'] and request.method == 'POST':
                failed_attempts[ip] = [t for t in failed_attempts[ip] if current_time - t < timedelta(minutes=15)]
                # Se agregará después si falla el login
            
            # Registrar actividad sospechosa
            if suspicious_flags:
                metadata = {
                    'flags': suspicious_flags,
                    'endpoint': endpoint,
                    'path': request.path,
                    'method': request.method,
                    'args': dict(request.args),
                    'rate_limit_count': len(rate_limits[ip])
                }
                
                AuditLog.log_action(
                    action_type='SUSPICIOUS_ACTIVITY',
                    description=f"Actividad sospechosa detectada: {', '.join(suspicious_flags)}",
                    user=current_user if current_user.is_authenticated else None,
                    severity='WARNING' if len(suspicious_flags) < 3 else 'CRITICAL',
                    category='SECURITY',
                    metadata=metadata,
                    requires_attention=len(suspicious_flags) >= 2
                )
            
            # Ejecutar función original
            return f(*args, **kwargs)
            
        return decorated_function
    return decorator


def log_security_event(event_type, description, severity='WARNING', user=None, metadata=None):
    """
    para registrar eventos de seguridad específicos
    """
    # Verificar usuario autenticado
    if user is None:
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            user = current_user
        else:
            user = None
    
    AuditLog.log_action(
        action_type=event_type,
        description=description,
        user=user,
        severity=severity,
        category='SECURITY',
        metadata=metadata,
        requires_attention=severity in ['CRITICAL', 'ERROR']
    )


def log_failed_login(username, reason='Invalid credentials'):
    """
    intentos fallidos de login
    """
    ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
    
    # Agregar a la lista de intentos fallidos
    current_time = datetime.utcnow()
    failed_attempts[ip].append(current_time)
    
    # Limpiar intentos antiguos
    failed_attempts[ip] = [t for t in failed_attempts[ip] if current_time - t < timedelta(minutes=15)]
    
    # Determinar severidad basada en número de intentos
    attempt_count = len(failed_attempts[ip])
    if attempt_count >= 10:
        severity = 'CRITICAL'
        requires_attention = True
    elif attempt_count >= 5:
        severity = 'ERROR'
        requires_attention = True
    else:
        severity = 'WARNING'
        requires_attention = False
    
    metadata = {
        'username_attempted': username,
        'reason': reason,
        'attempt_count': attempt_count,
        'previous_attempts': [t.isoformat() for t in failed_attempts[ip][-5:]]  # Últimos 5 intentos
    }
    
    AuditLog.log_action(
        action_type='FAILED_LOGIN',
        description=f"Intento fallido de login para '{username}' - {reason}. Intento #{attempt_count} desde esta IP.",
        severity=severity,
        category='SECURITY',
        metadata=metadata,
        requires_attention=requires_attention
    )


def log_unauthorized_access(resource_type, resource_id, action_attempted):
    """
    intentos de acceso no autorizado
    """
    user = None
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        user = current_user
    
    metadata = {
        'resource_type': resource_type,
        'resource_id': resource_id,
        'action_attempted': action_attempted,
        'user_role': user.role if user else 'unauthenticated',
        'endpoint': request.endpoint,
        'referer': request.referrer
    }
    
    AuditLog.log_action(
        action_type='UNAUTHORIZED_ACCESS',
        description=f"Intento de acceso no autorizado a {resource_type} {resource_id} - Acción: {action_attempted}",
        user=user,
        resource_type=resource_type,
        resource_id=resource_id,
        severity='ERROR',
        category='SECURITY',
        metadata=metadata,
        requires_attention=True
    )


def log_data_change(resource_type, resource_id, old_data, new_data, action='UPDATE'):
    """
    Registra cambios en datos críticos
    """
    # Verificar usuario autenticado
    user = None
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        user = current_user
    
    metadata = {
        'old_data': old_data,
        'new_data': new_data,
        'changes': get_data_diff(old_data, new_data)
    }
    
    AuditLog.log_action(
        action_type=f'DATA_{action}',
        description=f"{action} en {resource_type} {resource_id}",
        user=user,
        resource_type=resource_type,
        resource_id=resource_id,
        severity='INFO',
        category='USER_ACTION',
        metadata=metadata
    )


def get_data_diff(old_data, new_data):
    """
    Obtener diferencias entre datos antiguos y nuevos
    """
    if not isinstance(old_data, dict) or not isinstance(new_data, dict):
        return {'old': old_data, 'new': new_data}
    
    changes = {}
    all_keys = set(old_data.keys()) | set(new_data.keys())
    
    for key in all_keys:
        old_value = old_data.get(key)
        new_value = new_data.get(key)
        
        if old_value != new_value:
            changes[key] = {'old': old_value, 'new': new_value}
    
    return changes


def is_admin_required():
    """
    Verificar si el usuario actual es admin
    """
    return current_user.is_authenticated and current_user.role == 'admin'


def check_permissions(required_roles, resource_type=None, resource_id=None):
    """
    Decorador para verificar permisos y registrar intentos no autorizados
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(current_user, 'is_authenticated') or not current_user.is_authenticated:
                log_unauthorized_access(
                    resource_type or 'ENDPOINT',
                    resource_id or request.endpoint,
                    f.__name__
                )
                return {'error': 'Authentication required'}, 401
            
            if not hasattr(current_user, 'role') or current_user.role not in required_roles:
                log_unauthorized_access(
                    resource_type or 'ENDPOINT',
                    resource_id or request.endpoint,
                    f.__name__
                )
                return {'error': 'Insufficient permissions'}, 403
            
            return f(*args, **kwargs)
            
        return decorated_function
    return decorator


# Constantes para tipos de eventos
class EventTypes:
    # Autenticación
    LOGIN_SUCCESS = 'LOGIN_SUCCESS'
    LOGIN_FAILED = 'LOGIN_FAILED'
    LOGOUT = 'LOGOUT'
    SESSION_EXPIRED = 'SESSION_EXPIRED'
    
    # Acciones de usuario
    CREATE_ORDER = 'CREATE_ORDER'
    UPDATE_ORDER = 'UPDATE_ORDER'
    DELETE_ORDER = 'DELETE_ORDER'
    APPROVE_ORDER = 'APPROVE_ORDER'
    REJECT_ORDER = 'REJECT_ORDER'
    
    # Gestión de usuarios
    CREATE_USER = 'CREATE_USER'
    UPDATE_USER = 'UPDATE_USER'
    DEACTIVATE_USER = 'DEACTIVATE_USER'
    CHANGE_PASSWORD = 'CHANGE_PASSWORD'
    
    # Seguridad
    SUSPICIOUS_ACTIVITY = 'SUSPICIOUS_ACTIVITY'
    UNAUTHORIZED_ACCESS = 'UNAUTHORIZED_ACCESS'
    RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED'
    ATTACK_DETECTED = 'ATTACK_DETECTED'
    
    # Sistema
    SYSTEM_ERROR = 'SYSTEM_ERROR'
    DATABASE_ERROR = 'DATABASE_ERROR'
    CONFIGURATION_CHANGE = 'CONFIGURATION_CHANGE'


class Severity:
    INFO = 'INFO'
    WARNING = 'WARNING' 
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'
    SECURITY = 'SECURITY'


class Category:
    USER_ACTION = 'USER_ACTION'
    SECURITY = 'SECURITY'
    SYSTEM = 'SYSTEM'
    ANOMALY = 'ANOMALY'
    ATTACK = 'ATTACK'