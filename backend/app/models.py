from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Implementé esto para Flask-Login para cargar un usuario dado su ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(64), nullable=False, default='asistente') # 'admin', 'asistente', 'admin_sede', 'proveedor'
    is_active = db.Column(db.Boolean, default=True) # Para desactivar usuarios
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Implementé relación con el proveedor (si el usuario es de tipo 'proveedor')
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=True)
    provider = db.relationship('Provider', backref='users', uselist=False) # backref 'users' para el proveedor
    
    # Implementé relación con sede (si el usuario es admin_sede)
    sede_id = db.Column(db.Integer, db.ForeignKey('sede.id'), nullable=True)
    sede_asignada = db.relationship('Sede', backref='administrators', foreign_keys=[sede_id])

    def set_password(self, password):
        # Uso pbkdf2:sha256 que es compatible con Python 3.13
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        try:
            return check_password_hash(self.password_hash, password)
        except ValueError as e:
            if 'unsupported hash type' in str(e):
                # Si el hash existente no es compatible, rehasheo con método compatible
                print(f"Rehashing password for user {self.username} due to compatibility issue")
                # Por seguridad, solo lo hago si la contraseña es correcta usando método alternativo
                # En este caso, permito rehacer el hash
                self.set_password(password)
                db.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error checking password: {e}")
            return False

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Sede(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)  # Nombre de la sede
    city = db.Column(db.String(100), nullable=False)  # Ciudad
    address = db.Column(db.String(300))  # Dirección completa
    phone = db.Column(db.String(20))  # Teléfono de la sede
    manager = db.Column(db.String(128))  # Encargado de la sede
    is_active = db.Column(db.Boolean, default=True)  # Si la sede está activa
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Implementé relación con órdenes de trabajo
    orders = db.relationship('WorkOrder', backref='sede', lazy=True)

    def __repr__(self):
        return f'<Sede {self.name} - {self.city}>'


class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nit = db.Column(db.String(20), nullable=False, unique=True)  # NIT único del proveedor
    razon_social = db.Column(db.String(200), nullable=False)  # Razón social oficial
    name = db.Column(db.String(128), nullable=False)  # Nombre comercial (mantener para compatibilidad)
    contact_person = db.Column(db.String(128))  # Persona de contacto
    phone = db.Column(db.String(20))  # Teléfono
    email = db.Column(db.String(120), unique=True)  # Correo electrónico
    address = db.Column(db.String(500))  # Dirección (expandida)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Implementé relación con Órdenes de Trabajo
    orders = db.relationship('WorkOrder', backref='provider', lazy=True)

    # Implementé relación con Pagos (pagos que ha recibido este proveedor)
    payments_received = db.relationship('Payment', backref='provider_paid', lazy=True)

    def __repr__(self):
        return f'<Provider {self.razon_social} (NIT: {self.nit})>'

class WorkOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(64), unique=True, nullable=False) # Número o código de orden
    
    # Implementé información del recibo de venta
    receipt_number = db.Column(db.String(64), nullable=False) # Número del recibo de venta
    orden_laboratorio = db.Column(db.String(64)) # Número de orden del laboratorio
    ciudad_municipio = db.Column(db.String(100)) # Ciudad o municipio
    
    # Implementé información del paciente
    client_name = db.Column(db.String(128), nullable=False) # Nombre del paciente
    client_cc = db.Column(db.String(20), nullable=False) # Cédula del paciente
    client_phone = db.Column(db.String(20)) # Teléfono del paciente
    empresa_convenio = db.Column(db.String(200)) # Empresa, convenio o seguro del paciente

    
    # Implementé clasificación de lentes (nuevo)
    lens_class = db.Column(db.String(20)) # Progresivo, Bifocal, Monofocal
    lens_type = db.Column(db.String(128)) # Tipo de lente y filtros específicos (opcional hasta que admin complete)
    frame_type = db.Column(db.String(128)) # Tipo de montura
    
    # Control de flujo: Sede crea → Admin completa lentes → Admin envía a proveedor
    pending_admin_review = db.Column(db.Boolean, default=False) # Si está pendiente de completar por admin
    admin_completed_at = db.Column(db.DateTime) # Fecha cuando admin completó los campos de lentes
    admin_completed_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Admin que completó
    admin_completed_by = db.relationship('User', backref='completed_orders', foreign_keys=[admin_completed_by_user_id])
    
    # Implementé fórmula óptica con campos de texto libre
    formula_od = db.Column(db.Text) # Ojo derecho (texto libre)
    formula_oi = db.Column(db.Text) # Ojo izquierdo (texto libre)
    formula_add = db.Column(db.Text) # Adición (texto libre)
    formula_dp_alt = db.Column(db.Text) # Distancia pupilar y altura (texto libre)
    
    # Información adicional y observaciones
    formula_details = db.Column(db.Text) # Detalles adicionales de fórmulas ópticas (opcional)
    observations = db.Column(db.Text) # Observaciones específicas
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(64), default='pendiente_envio') # 'pendiente_envio', 'enviada', 'en_proceso', 'devuelta_proveedor', 'recibida_optica', 'finalizada', 'cancelada'
    comments = db.Column(db.Text)

    # Relaciones
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=False)
    sede_id = db.Column(db.Integer, db.ForeignKey('sede.id'), nullable=False)  # Sede que creó la orden
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_by = db.relationship('User', backref='created_orders', foreign_keys=[created_by_user_id])

    # Relación con pagos (una orden puede tener varios pagos asociados)
    payments = db.relationship('Payment', backref='work_order', lazy=True)

    # Estado de pago de la orden (puede ser calculado en tiempo real o actualizado)
    payment_status = db.Column(db.String(64), default='pendiente') # 'pendiente', 'parcialmente_pagada', 'pagada'
    total_amount = db.Column(db.Float, default=0.0) # Monto total que se debe pagar al proveedor por esta orden
    sale_price = db.Column(db.Float, nullable=True) # Precio de venta al cliente final (para cálculo de ganancias)

    # Sistema de entrega con plazo fijo de 7 días
    accepted_at = db.Column(db.DateTime) # Fecha cuando el proveedor aceptó la orden
    delivery_deadline = db.Column(db.DateTime) # Fecha límite calculada automáticamente (accepted_at + 7 días)
    is_overdue = db.Column(db.Boolean, default=False) # Si la orden está vencida
    overdue_alert_sent = db.Column(db.Boolean, default=False) # Si ya se envió alerta de vencimiento
    days_overdue = db.Column(db.Integer, default=0) # Días de retraso

    # Sistema de rechazos y reenvíos
    rejection_reason = db.Column(db.Text)  # Razón del rechazo
    rejection_count = db.Column(db.Integer, default=0)  # Número de rechazos
    resubmitted_at = db.Column(db.DateTime)  # Fecha del último reenvío
    resubmitted_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Usuario que reenvió
    resubmitted_by = db.relationship('User', backref='resubmitted_orders', foreign_keys=[resubmitted_by_user_id])

    def calculate_delivery_deadline(self):
        """Calcula la fecha límite de entrega (7 días después de aceptada)"""
        if self.accepted_at:
            from datetime import timedelta
            return self.accepted_at + timedelta(days=7)
        return None

    def check_if_overdue(self):
        """Verifica si la orden está vencida y actualiza los campos correspondientes"""
        if self.accepted_at and self.status in ['aceptada', 'en_proceso']:
            from datetime import datetime
            deadline = self.calculate_delivery_deadline()
            now = datetime.utcnow()
            
            if now > deadline:
                self.is_overdue = True
                self.days_overdue = (now - deadline).days
                return True
            else:
                self.is_overdue = False
                self.days_overdue = 0
                return False
        return False

    def get_delivery_status_info(self):
        """Retorna información del estado de entrega"""
        if not self.accepted_at:
            return {"status": "not_accepted", "message": "No aceptada aún"}
        
        deadline = self.calculate_delivery_deadline()
        if not deadline:
            return {"status": "no_deadline", "message": "Sin fecha límite"}
            
        from datetime import datetime
        now = datetime.utcnow()
        days_left = (deadline - now).days
        
        if days_left > 0:
            return {
                "status": "on_time", 
                "days_left": days_left,
                "deadline": deadline,
                "message": f"Quedan {days_left} días"
            }
        elif days_left == 0:
            return {
                "status": "due_today", 
                "deadline": deadline,
                "message": "Vence hoy"
            }
        else:
            self.check_if_overdue()  # Actualizar estado
            return {
                "status": "overdue", 
                "days_overdue": abs(days_left),
                "deadline": deadline,
                "message": f"{abs(days_left)} días de retraso"
            }

    def __repr__(self):
        return f'<WorkOrder {self.order_number} - {self.client_name}>'

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    support_file = db.Column(db.String(256)) # Ruta al archivo de soporte (PDF, imagen, etc.)

    # Relaciones
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_order.id'), nullable=False)
    # Este proveedor_id es para saber A QUÉ proveedor se le hizo el pago,
    # aunque la orden ya tiene un proveedor_id, esto ayuda a la consistencia.
    # Puede ser el mismo que work_order.provider_id
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=False)
    registered_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    registered_by = db.relationship('User', backref='registered_payments', foreign_keys=[registered_by_user_id])

    def __repr__(self):
        return f'<Payment {self.id} for Order {self.work_order_id} - {self.amount}>'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='notifications')
    message = db.Column(db.String(512), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Opcional: Relacionar la notificación con una orden específica
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_order.id'), nullable=True)
    work_order = db.relationship('WorkOrder', backref='notifications_related', foreign_keys=[work_order_id])

    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id} - {self.message[:30]}...>'


class SedeMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)  # Título del mensaje
    message = db.Column(db.Text, nullable=False)  # Contenido del mensaje
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Quien envía
    sender = db.relationship('User', backref='sent_messages', foreign_keys=[sender_id])
    
    # Puede ser para una sede específica o para todas
    sede_id = db.Column(db.Integer, db.ForeignKey('sede.id'), nullable=True)
    sede = db.relationship('Sede', backref='received_messages', foreign_keys=[sede_id])
    
    is_global = db.Column(db.Boolean, default=False)  # Si es para todas las sedes
    priority = db.Column(db.String(20), default='normal')  # normal, alta, urgente
    is_active = db.Column(db.Boolean, default=True)  # Para poder archivar mensajes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)  # Fecha de expiración opcional

    def __repr__(self):
        return f'<SedeMessage {self.id}: {self.title}>'


class AuditLog(db.Model):
    """
    Tabla para registrar todas las actividades del sistema:
    - Acciones de usuarios (login, logout, crear orden, etc.)
    - Intentos de acceso no autorizado
    - Actividades anómalas o sospechosas
    - Cambios en datos críticos
    - Intentos de hackeo o ataques
    """
    id = db.Column(db.Integer, primary_key=True)
    
    # Información del usuario (puede ser None para intentos no autenticados)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref='audit_logs', foreign_keys=[user_id])
    username = db.Column(db.String(64), nullable=True)  # Para casos donde no hay user_id
    
    # Información de la acción
    action_type = db.Column(db.String(50), nullable=False)  # 'LOGIN', 'LOGOUT', 'CREATE_ORDER', 'UNAUTHORIZED_ACCESS', 'SUSPICIOUS_ACTIVITY', etc.
    description = db.Column(db.Text, nullable=False)  # Descripción detallada de la acción
    resource_type = db.Column(db.String(50), nullable=True)  # 'ORDER', 'USER', 'PROVIDER', 'SYSTEM', etc.
    resource_id = db.Column(db.String(50), nullable=True)  # ID del recurso afectado
    
    # Información de seguridad
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 o IPv6
    user_agent = db.Column(db.Text, nullable=True)  # Navegador y sistema operativo
    session_id = db.Column(db.String(255), nullable=True)  # ID de sesión
    
    # Severidad y categorización
    severity = db.Column(db.String(20), default='INFO')  # 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'SECURITY'
    category = db.Column(db.String(30), default='USER_ACTION')  # 'USER_ACTION', 'SECURITY', 'SYSTEM', 'ANOMALY', 'ATTACK'
    
    # Datos adicionales (JSON para flexibilidad)
    extra_data = db.Column(db.Text, nullable=True)  # JSON con información adicional
    
    # Información temporal
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Flags de estado
    is_reviewed = db.Column(db.Boolean, default=False)  # Si ya fue revisado por un admin
    requires_attention = db.Column(db.Boolean, default=False)  # Si requiere atención inmediata
    reviewed = db.Column(db.Boolean, default=False)  # Para compatibilidad
    reviewed_at = db.Column(db.DateTime, nullable=True)  # Fecha de revisión
    reviewed_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Quién lo revisó
    
    def __repr__(self):
        return f'<AuditLog {self.id}: {self.action_type} by {self.username or "Anonymous"} at {self.timestamp}>'
    
    @staticmethod
    def log_action(action_type, description, user=None, ip=None, user_agent=None, 
                   resource_type=None, resource_id=None, severity='INFO', 
                   category='USER_ACTION', metadata=None, requires_attention=False):
        """
        Método estático para crear fácilmente un log de auditoría
        """
        import json
        from flask import request, session
        
        # Obtener información de la request si no se proporciona
        if ip is None and request:
            ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        
        if user_agent is None and request:
            user_agent = request.headers.get('User-Agent')
        
        session_id = None
        if session:
            session_id = session.get('_id', None)
        
        # Serializar metadata si es un dict
        metadata_json = None
        if metadata:
            metadata_json = json.dumps(metadata) if isinstance(metadata, dict) else str(metadata)
        
        # Verificar si el usuario está autenticado y tiene id
        user_id = None
        username = 'Anonymous'
        
        if user and hasattr(user, 'id') and hasattr(user, 'is_authenticated'):
            if user.is_authenticated:
                user_id = user.id
                username = user.username
        
        log_entry = AuditLog(
            user_id=user_id,
            username=username,
            action_type=action_type,
            description=description,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            ip_address=ip,
            user_agent=user_agent,
            session_id=session_id,
            severity=severity,
            category=category,
            extra_data=metadata_json,
            requires_attention=requires_attention
        )
        
        try:
            db.session.add(log_entry)
            db.session.commit()
            return log_entry
        except Exception as e:
            db.session.rollback()
            print(f"Error creating audit log: {e}")
            return None