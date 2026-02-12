"""
Servicio para gestión de autenticación y usuarios.
Centraliza la lógica de login, logout y gestión de sesiones.
"""

from typing import Dict, List, Optional, Tuple
from flask import session, request
from flask_login import login_user, logout_user
from backend.app.models import User, Sede, Provider, db
from backend.app.services import BaseService, ValidationMixin
from backend.app.services.utils import ValidationUtils
from backend.app.security import AuditLog, EventTypes, Severity, Category, log_failed_login
import logging

logger = logging.getLogger(__name__)

class AuthService(BaseService, ValidationMixin):
    """Servicio para autenticación y gestión de usuarios"""
    
    def login_sede(self, sede_id: int, password: str, remember_me: bool = False) -> Tuple[bool, str, Optional[User]]:
        """Login por sede con usuario genérico"""
        
        try:
            # Validar sede
            if not sede_id or sede_id == 0:
                return False, 'Debe seleccionar una sede válida de la lista.', None
            
            sede = Sede.query.get(sede_id)
            if not sede or not sede.is_active:
                return False, f'La sede seleccionada (ID: {sede_id}) no es válida o está inactiva.', None
            
            # Buscar o crear usuario genérico de la sede
            sede_username = f'sede_{sede_id}'
            user = User.query.filter_by(
                username=sede_username, 
                role='admin_sede', 
                sede_id=sede_id
            ).first()
            
            # Crear usuario si no existe
            if not user:
                user = self._create_sede_user(sede_id, sede_username)
                if not user:
                    return False, 'Error al crear usuario de sede', None
            
            # Validar contraseña
            if not user.check_password(password):
                log_failed_login(sede_username, 'Invalid password')
                return False, 'Contraseña incorrecta. Contacta al administrador.', None
            
            # Login exitoso
            login_user(user, remember=remember_me)
            session['sede_seleccionada'] = sede_id
            
            # Log de auditoría
            AuditLog.log_action(
                action_type=EventTypes.LOGIN_SUCCESS,
                description=f"Login exitoso - Sede: {sede.name}",
                user=user,
                severity=Severity.INFO,
                category=Category.USER_ACTION,
                metadata={'sede_id': sede_id, 'sede_name': sede.name}
            )
            
            success_message = f'✅ Bienvenido a {sede.name}'
            if sede.city:
                success_message += f' - {sede.city}'
            success_message += '!'
            
            return True, success_message, user
            
        except Exception as e:
            logger.error(f"Error in sede login: {e}")
            return False, 'Error interno en el sistema de login', None
    
    def login_user_traditional(self, username: str, password: str, user_type: str, 
                             remember_me: bool = False) -> Tuple[bool, str, Optional[User]]:
        """Login tradicional para admin central y proveedores"""
        
        try:
            if not username:
                return False, 'Debe ingresar un nombre de usuario.', None
            
            # Buscar usuario
            user = User.query.filter_by(username=username).first()
            
            # Validar usuario
            if not user:
                log_failed_login(username, 'User not found')
                return False, 'Usuario no encontrado.', None
            
            if not user.is_active:
                log_failed_login(username, 'Account inactive')
                return False, 'Cuenta inactiva.', None
            
            if not user.check_password(password):
                log_failed_login(username, 'Invalid password')
                return False, 'Contraseña incorrecta.', None
            
            # Validar tipo de usuario
            if user_type == 'central' and user.role not in ['admin', 'asistente']:
                return False, 'Este usuario no tiene acceso a Administración Central.', None
            elif user_type == 'proveedor' and user.role != 'proveedor':
                return False, 'Este usuario no es proveedor.', None
            
            # Login exitoso
            login_user(user, remember=remember_me)
            
            # Log de auditoría
            AuditLog.log_action(
                action_type=EventTypes.LOGIN_SUCCESS,
                description=f"Login exitoso - Tipo: {user_type}",
                user=user,
                severity=Severity.INFO,
                category=Category.USER_ACTION,
                metadata={'user_type': user_type, 'role': user.role}
            )
            
            # Mensaje de bienvenida
            welcome_messages = {
                'admin': '¡Bienvenido Administrador!',
                'asistente': '¡Bienvenido Asistente!',
                'proveedor': f'¡Bienvenido {user.provider.razon_social}!' if user.provider else '¡Bienvenido Proveedor!'
            }
            
            message = welcome_messages.get(user.role, '¡Bienvenido!')
            return True, message, user
            
        except Exception as e:
            logger.error(f"Error in traditional login: {e}")
            return False, 'Error interno en el sistema de login', None
    
    def logout_user_with_audit(self, user: User = None):
        """Logout con auditoría"""
        try:
            if user:
                AuditLog.log_action(
                    action_type=EventTypes.LOGOUT,
                    description="Logout exitoso",
                    user=user,
                    severity=Severity.INFO,
                    category=Category.USER_ACTION
                )
            
            logout_user()
            session.clear()
            
        except Exception as e:
            logger.error(f"Error in logout: {e}")
    
    def create_user(self, form_data: Dict) -> Tuple[bool, str, Optional[User]]:
        """Crear nuevo usuario"""
        
        required_fields = ['username', 'email', 'password', 'role']
        is_valid, error_message = self.validate_required_fields(form_data, required_fields)
        
        if not is_valid:
            return False, error_message, None
        
        try:
            # Validar email
            if not ValidationUtils.validate_email(form_data['email']):
                return False, 'Email inválido', None
            
            # Verificar si username ya existe
            existing_user = User.query.filter_by(username=form_data['username']).first()
            if existing_user:
                return False, 'El nombre de usuario ya existe', None
            
            # Verificar si email ya existe
            existing_email = User.query.filter_by(email=form_data['email']).first()
            if existing_email:
                return False, 'El email ya está registrado', None
            
            # Crear usuario
            user = User(
                username=self.sanitize_string(form_data['username'], 64),
                email=self.sanitize_string(form_data['email'], 120),
                role=form_data['role'],
                is_active=True
            )
            
            user.set_password(form_data['password'])
            
            # Asignaciones específicas por rol
            if form_data['role'] == 'proveedor' and form_data.get('provider_id'):
                user.provider_id = form_data['provider_id']
            elif form_data['role'] == 'admin_sede' and form_data.get('sede_id'):
                user.sede_id = form_data['sede_id']
            
            db.session.add(user)
            
            if self.commit_changes():
                return True, f'Usuario {user.username} creado exitosamente', user
            else:
                return False, 'Error al guardar el usuario', None
                
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False, f'Error interno: {str(e)}', None
    
    def update_user(self, user_id: int, form_data: Dict) -> Tuple[bool, str]:
        """Actualizar usuario existente"""
        
        user = User.query.get(user_id)
        if not user:
            return False, 'Usuario no encontrado'
        
        try:
            # Campos que se pueden actualizar
            if form_data.get('email'):
                if not ValidationUtils.validate_email(form_data['email']):
                    return False, 'Email inválido'
                
                # Verificar que email no esté en uso por otro usuario
                existing_email = User.query.filter(
                    User.email == form_data['email'],
                    User.id != user_id
                ).first()
                
                if existing_email:
                    return False, 'El email ya está registrado por otro usuario'
                
                user.email = self.sanitize_string(form_data['email'], 120)
            
            if 'is_active' in form_data:
                user.is_active = bool(form_data['is_active'])
            
            if form_data.get('role'):
                user.role = form_data['role']
            
            # Actualizar contraseña si se proporciona
            if form_data.get('password'):
                user.set_password(form_data['password'])
            
            if self.commit_changes():
                return True, f'Usuario {user.username} actualizado exitosamente'
            else:
                return False, 'Error al actualizar el usuario'
                
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False, f'Error interno: {str(e)}'
    
    def get_users_by_role(self, role: str = None, include_inactive: bool = False) -> List[User]:
        """Obtener usuarios por rol"""
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        
        if not include_inactive:
            query = query.filter_by(is_active=True)
        
        return query.order_by(User.username).all()
    
    def _create_sede_user(self, sede_id: int, username: str) -> Optional[User]:
        """Crear usuario genérico para sede"""
        try:
            user = User(
                username=username,
                email=f'sede{sede_id}@opticasdrmejia.com',
                role='admin_sede',
                sede_id=sede_id,
                is_active=True
            )
            
            # Contraseña por defecto para sedes
            user.set_password('OpticasDrMejia2024')
            
            db.session.add(user)
            
            if self.commit_changes():
                logger.info(f"Created sede user: {username}")
                return user
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error creating sede user: {e}")
            return None