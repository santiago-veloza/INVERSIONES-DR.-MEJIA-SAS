from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from backend.app.models import WorkOrder, User, Sede, Provider, Notification, db
from backend.app.services import BaseService, ValidationMixin, CacheService
from backend.app.security import AuditLog
import logging

logger = logging.getLogger(__name__)

class OrderService(BaseService, ValidationMixin):
    """Servicio para gestión de órdenes de trabajo"""
    
    def get_orders_by_sede(self, sede_id: int, status: str = None) -> List[WorkOrder]:
        """Obtener órdenes de una sede específica"""
        cache_key = f"orders_sede_{sede_id}_{status or 'all'}"
        cached_orders = CacheService.get(cache_key)
        
        if cached_orders is not None:
            return cached_orders
        
        query = WorkOrder.query.filter_by(sede_id=sede_id)
        if status:
            query = query.filter_by(status=status)
        
        orders = query.order_by(WorkOrder.created_at.desc()).all()
        CacheService.set(cache_key, orders, ttl=300)  # 5 minutes cache
        
        return orders
    
    def get_orders_by_provider(self, provider_id: int, status: str = None) -> List[WorkOrder]:
        """Obtener órdenes de un proveedor específico"""
        query = WorkOrder.query.filter_by(provider_id=provider_id)
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(WorkOrder.created_at.desc()).all()
    
    def create_order(self, form_data: Dict, user: User) -> Tuple[bool, str, Optional[WorkOrder]]:
        """Crear una nueva orden de trabajo"""
        
        # Validar campos requeridos
        required_fields = ['client_name', 'client_cc', 'receipt_number', 'sede_id']
        is_valid, error_message = self.validate_required_fields(form_data, required_fields)
        
        if not is_valid:
            return False, error_message, None
        
        try:
            # Generar número de orden único
            order_number = self._generate_order_number()
            
            # Crear orden
            order = WorkOrder(
                order_number=order_number,
                client_name=self.sanitize_string(form_data['client_name'], 128),
                client_cc=self.sanitize_string(form_data['client_cc'], 20),
                client_phone=self.sanitize_string(form_data.get('client_phone', ''), 20),
                receipt_number=self.sanitize_string(form_data['receipt_number'], 64),
                orden_laboratorio=self.sanitize_string(form_data.get('orden_laboratorio', ''), 64),
                empresa_convenio=self.sanitize_string(form_data.get('empresa_convenio', ''), 200),
                ciudad_municipio=self.sanitize_string(form_data.get('ciudad_municipio', ''), 100),
                sede_id=form_data['sede_id'],
                created_by_user_id=user.id,
                status='pendiente_envio'
            )
            
            # Campos opcionales de lentes
            if form_data.get('lens_class'):
                order.lens_class = form_data['lens_class']
            if form_data.get('lens_type_asesor'):
                order.lens_type_asesor = self.sanitize_string(form_data['lens_type_asesor'], 128)
            if form_data.get('frame_type'):
                order.frame_type = self.sanitize_string(form_data['frame_type'], 128)
            
            # Fórmulas ópticas
            order.formula_od = form_data.get('formula_od', '')
            order.formula_oi = form_data.get('formula_oi', '')
            order.formula_add = form_data.get('formula_add', '')
            order.formula_dp_alt = form_data.get('formula_dp_alt', '')
            order.formula_details = form_data.get('formula_details', '')
            order.observations = form_data.get('observations', '')
            order.comments = form_data.get('comments', '')
            
            # Precio de venta
            if form_data.get('sale_price'):
                try:
                    order.sale_price = float(form_data['sale_price'])
                except (ValueError, TypeError):
                    order.sale_price = 0.0
            
            # Determinar si necesita revisión admin
            if user.role in ['admin_sede', 'asistente']:
                order.pending_admin_review = True
            
            db.session.add(order)
            
            if self.commit_changes():
                # Limpiar cache relacionado
                self._clear_order_cache(order.sede_id)
                
                # Log de auditoría
                AuditLog.log_action(
                    action_type='CREATE_ORDER',
                    description=f'Orden {order.order_number} creada para {order.client_name}',
                    user=user,
                    resource_type='ORDER',
                    resource_id=str(order.id),
                    category='USER_ACTION'
                )
                
                return True, f'Orden {order.order_number} creada exitosamente', order
            else:
                return False, 'Error al guardar la orden en la base de datos', None
                
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return False, f'Error interno: {str(e)}', None
    
    def update_order_status(self, order_id: int, new_status: str, user: User, 
                          comments: str = None, provider_id: int = None) -> Tuple[bool, str]:
        """Actualizar estado de una orden"""
        
        order = self.safe_get_or_404(WorkOrder, order_id)
        if not order:
            return False, 'Orden no encontrada'
        
        old_status = order.status
        
        try:
            order.status = new_status
            
            if comments:
                order.comments = comments
            
            if provider_id:
                order.provider_id = provider_id
            
            # Lógica específica por estado
            if new_status == 'aceptada' and old_status != 'aceptada':
                order.accepted_at = datetime.utcnow()
                order.delivery_deadline = order.calculate_delivery_deadline()
            
            if self.commit_changes():
                # Limpiar cache
                self._clear_order_cache(order.sede_id)
                if order.provider_id:
                    CacheService.delete(f"orders_provider_{order.provider_id}")
                
                # Crear notificación
                self._create_status_notification(order, old_status, new_status, user)
                
                # Log de auditoría
                AuditLog.log_action(
                    action_type='UPDATE_ORDER_STATUS',
                    description=f'Orden {order.order_number} cambió de {old_status} a {new_status}',
                    user=user,
                    resource_type='ORDER',
                    resource_id=str(order.id),
                    category='USER_ACTION'
                )
                
                return True, f'Estado actualizado a {new_status}'
            else:
                return False, 'Error al actualizar el estado'
                
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            return False, f'Error interno: {str(e)}'
    
    def get_overdue_orders(self) -> List[WorkOrder]:
        """Obtener órdenes vencidas"""
        now = datetime.utcnow()
        
        return WorkOrder.query.filter(
            WorkOrder.accepted_at.isnot(None),
            WorkOrder.status.in_(['aceptada', 'en_proceso']),
            WorkOrder.delivery_deadline < now
        ).all()
    
    def _generate_order_number(self) -> str:
        """Generar número único de orden"""
        import uuid
        timestamp = datetime.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"ORD-{timestamp}-{unique_id}"
    
    def _clear_order_cache(self, sede_id: int):
        """Limpiar cache relacionado con órdenes de una sede"""
        # Limpiar todos los posibles cache keys para esta sede
        for status in ['all', 'pendiente_envio', 'enviada', 'aceptada', 'en_proceso', 'completado', 'finalizada']:
            CacheService.delete(f"orders_sede_{sede_id}_{status}")
    
    def _create_status_notification(self, order: WorkOrder, old_status: str, new_status: str, user: User):
        """Crear notificación de cambio de estado"""
        try:
            # Determinar destinatarios basado en el tipo de cambio
            notification_targets = []
            
            if new_status == 'aceptada':
                # Notificar a la sede que creó la orden
                sede_users = User.query.filter_by(sede_id=order.sede_id, is_active=True).all()
                notification_targets.extend(sede_users)
                message = f"Orden {order.order_number} ha sido aceptada por el proveedor"
                
            elif new_status == 'completado':
                # Notificar a la sede
                sede_users = User.query.filter_by(sede_id=order.sede_id, is_active=True).all()
                notification_targets.extend(sede_users)
                message = f"Orden {order.order_number} para {order.client_name} está lista para recoger"
                
            elif new_status == 'rechazada':
                # Notificar a admin y sede
                sede_users = User.query.filter_by(sede_id=order.sede_id, is_active=True).all()
                admin_users = User.query.filter_by(role='admin', is_active=True).all()
                notification_targets.extend(sede_users + admin_users)
                message = f"Orden {order.order_number} fue rechazada por el proveedor"
            
            else:
                # Notificación general de cambio de estado
                sede_users = User.query.filter_by(sede_id=order.sede_id, is_active=True).all()
                notification_targets.extend(sede_users)
                message = f"Orden {order.order_number} cambió de estado: {new_status}"
            
            # Crear notificaciones
            for target_user in notification_targets:
                if target_user.id != user.id:  # No notificar al usuario que hizo el cambio
                    notification = Notification(
                        user_id=target_user.id,
                        message=message,
                        work_order_id=order.id
                    )
                    db.session.add(notification)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error creating status notification: {e}")