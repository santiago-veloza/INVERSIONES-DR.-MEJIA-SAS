from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DateField, FloatField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange
from app.models import User, Provider, WorkOrder

class LoginForm(FlaskForm):
    user_type = SelectField('Tipo de Usuario', choices=[
        ('sede', '🏢 Sede (Administrador de Sede)'),
        ('central', '🏛️ Administración Central'),
        ('proveedor', '🏭 Proveedor')
    ], validators=[DataRequired()])
    sede_id = SelectField('Sede', coerce=int, validators=[Optional()])
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        from app.models import Sede
        sedes_list = []
        for s in Sede.query.filter_by(is_active=True).order_by(Sede.name).all():
            if s.city and s.city not in ['Selecciona tu ciudad', 'selecciona tu ciudad', '']:
                sedes_list.append((s.id, f"{s.name} - {s.city}"))
            else:
                sedes_list.append((s.id, s.name))
        self.sede_id.choices = [(0, '--- Seleccionar Sede ---')] + sedes_list

class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        'Repetir Contraseña', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Rol', choices=[('asistente', 'Asistente (Óptica)'), ('proveedor', 'Proveedor'), ('admin', 'Administrador')], validators=[DataRequired()])
    provider_name = SelectField('Asignar a Proveedor (si es rol Proveedor)', choices=[('', '--- Seleccionar Proveedor ---')], validators=[Optional()]) # Se llenará dinámicamente
    submit = SubmitField('Registrar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Por favor, usa un nombre de usuario diferente.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Por favor, usa una dirección de correo diferente.')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # Cargo los proveedores existentes para la asignación
        self.provider_name.choices = [('', '--- Seleccionar Proveedor ---')] + [(p.id, f"{p.razon_social} ({p.nit})") for p in Provider.query.all()]


class ProviderForm(FlaskForm):
    # Implementé datos del proveedor
    nit = StringField('NIT', validators=[DataRequired(), Length(max=20)])
    razon_social = StringField('Razón Social', validators=[DataRequired(), Length(max=255)])
    name = StringField('Nombre Comercial', validators=[Optional(), Length(max=128)])
    contact_person = StringField('Persona de Contacto', validators=[Optional(), Length(max=128)])
    phone = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    email = StringField('Correo Electrónico', validators=[Optional(), Email(), Length(max=120)])
    address = TextAreaField('Dirección', validators=[Optional(), Length(max=500)])
    
    # Implementé datos de acceso del usuario
    username = StringField('Usuario para Acceso', validators=[DataRequired(), Length(min=4, max=20)])
    user_email = StringField('Email del Usuario', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar Contraseña', 
                             validators=[DataRequired(), EqualTo('password', message='Las contraseñas deben coincidir')])
    
    submit = SubmitField('Guardar Proveedor')

    def validate_nit(self, nit):
        provider = Provider.query.filter_by(nit=nit.data).first()
        if provider and provider.id != (getattr(self, '_original_obj', None) and self._original_obj.id):
            raise ValidationError('Ya existe un proveedor con este NIT.')

    def validate_razon_social(self, razon_social):
        provider = Provider.query.filter_by(razon_social=razon_social.data).first()
        if provider and provider.id != (getattr(self, '_original_obj', None) and self._original_obj.id):
            raise ValidationError('Ya existe un proveedor con esta razón social.')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and user.id != (getattr(self, '_original_user', None) and self._original_user.id):
            raise ValidationError('Este nombre de usuario ya está en uso.')

    def validate_user_email(self, user_email):
        user = User.query.filter_by(email=user_email.data).first()
        if user and user.id != (getattr(self, '_original_user', None) and self._original_user.id):
            raise ValidationError('Este email ya está registrado.')

    def validate_email(self, email):
        if email.data:
            provider = Provider.query.filter_by(email=email.data).first()
            if provider and provider.id != (getattr(self, '_original_obj', None) and self._original_obj.id):
                raise ValidationError('Ya existe un proveedor con este email.')


class ProviderEditForm(FlaskForm):
    # Implementé solo datos del proveedor para edición (sin usuario)
    nit = StringField('NIT', validators=[DataRequired(), Length(max=20)])
    razon_social = StringField('Razón Social', validators=[DataRequired(), Length(max=255)])
    name = StringField('Nombre Comercial', validators=[Optional(), Length(max=128)])
    contact_person = StringField('Persona de Contacto', validators=[Optional(), Length(max=128)])
    phone = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    email = StringField('Correo Electrónico', validators=[Optional(), Email(), Length(max=120)])
    address = TextAreaField('Dirección', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Actualizar Proveedor')

    def validate_nit(self, nit):
        provider = Provider.query.filter_by(nit=nit.data).first()
        if provider and provider.id != (getattr(self, '_original_obj', None) and self._original_obj.id):
            raise ValidationError('Ya existe un proveedor con este NIT.')

    def validate_razon_social(self, razon_social):
        provider = Provider.query.filter_by(razon_social=razon_social.data).first()
        if provider and provider.id != (getattr(self, '_original_obj', None) and self._original_obj.id):
            raise ValidationError('Ya existe un proveedor con esta razón social.')

    def validate_email(self, email):
        if email.data:
            provider = Provider.query.filter_by(email=email.data).first()
            if provider and provider.id != (getattr(self, '_original_obj', None) and self._original_obj.id):
                raise ValidationError('Ya existe un proveedor con este email.')


class WorkOrderForm(FlaskForm):
    # Implementé información básica de la orden
    client_name = StringField('Nombre del Paciente', validators=[DataRequired(), Length(max=128)])
    client_cc = StringField('Cédula del Paciente', validators=[DataRequired(), Length(max=20)])
    client_phone = StringField('Teléfono del Paciente', validators=[Optional(), Length(max=20)])
    receipt_number = StringField('Número del Recibo de Venta', validators=[DataRequired(), Length(max=64)])
    orden_laboratorio = StringField('Número de Orden de Laboratorio', validators=[Optional(), Length(max=64)])
    empresa_convenio = StringField('Empresa/Convenio/Seguro', validators=[Optional(), Length(max=200)])
    ciudad_municipio = StringField('Ciudad/Municipio', validators=[Optional(), Length(max=100)])
    
    # Implementé sede y proveedor
    sede_id = SelectField('Sede Solicitante', coerce=int, validators=[DataRequired()])
    provider_id = SelectField('Proveedor', coerce=int, validators=[DataRequired()])
    

    
    # Implementé clasificación y tipo de lentes (opcionales para sedes)
    lens_class = SelectField('Clase de Lentes', choices=[
        ('', 'Seleccionar...'),
        ('Progresivo', 'Progresivo'),
        ('Bifocal', 'Bifocal'), 
        ('Monofocal', 'Monofocal')
    ], validators=[Optional()])
    lens_type = StringField('Tipo de Lente y Filtros', validators=[Optional(), Length(max=128)])
    frame_type = StringField('Tipo de Montura', validators=[Optional(), Length(max=128)])
    
    # Implementé fórmula con campos de texto libre
    formula_od = TextAreaField('OD (Ojo Derecho)', validators=[Optional(), Length(max=200)])
    formula_oi = TextAreaField('OI (Ojo Izquierdo)', validators=[Optional(), Length(max=200)])
    formula_add = TextAreaField('ADD (Adición)', validators=[Optional(), Length(max=200)])
    formula_dp_alt = TextAreaField('DP y ALT (Distancia Pupilar y Altura)', validators=[Optional(), Length(max=200)])
    
    # Implementé información adicional
    formula_details = TextAreaField('Detalles Adicionales de la Fórmula', validators=[Optional()])
    observations = TextAreaField('Observaciones', validators=[Optional()])
    comments = TextAreaField('Comentarios Adicionales', validators=[Optional()])
    # Nota: total_amount es establecido por el proveedor al aceptar la orden
    submit = SubmitField('Crear Orden de Trabajo')

    def __init__(self, current_user=None, *args, **kwargs):
        super(WorkOrderForm, self).__init__(*args, **kwargs)
        from app.models import Sede
        
        # Si es admin_sede, solo muestro su sede asignada
        if current_user and current_user.role == 'admin_sede' and current_user.sede_id:
            sede = Sede.query.get(current_user.sede_id)
            # Solo muestro la ciudad si no es un placeholder
            if sede.city and sede.city not in ['Selecciona tu ciudad', 'selecciona tu ciudad', '']:
                self.sede_id.choices = [(sede.id, f"{sede.name} - {sede.city}")]
            else:
                self.sede_id.choices = [(sede.id, sede.name)]
            # Pre-selecciono la sede del usuario
            self.sede_id.data = sede.id
        else:
            # Para admin y asistente, muestro todas las sedes
            sedes_list = []
            for s in Sede.query.filter_by(is_active=True).order_by(Sede.name).all():
                # Solo muestro la ciudad si no es un placeholder
                if s.city and s.city not in ['Selecciona tu ciudad', 'selecciona tu ciudad', '']:
                    sedes_list.append((s.id, f"{s.name} - {s.city}"))
                else:
                    sedes_list.append((s.id, s.name))
            self.sede_id.choices = [(0, '--- Seleccionar Sede Solicitante ---')] + sedes_list
        
        # Todos los usuarios pueden ver todos los proveedores que implementé
        self.provider_id.choices = [(p.id, f"{p.razon_social} ({p.nit})") for p in Provider.query.order_by(Provider.razon_social).all()]
        # Agrego una opción vacía si es necesario
        self.provider_id.choices.insert(0, (0, 'Seleccionar Proveedor'))


class WorkOrderStatusForm(FlaskForm):
    status = SelectField('Estado de la Orden', choices=[
        ('pendiente_envio', 'Pendiente de Envío'),
        ('enviada', 'Enviada al Proveedor'),
        ('aceptada', 'Aceptada por Proveedor'),
        ('rechazada', 'Rechazada por Proveedor'),
        ('en_proceso', 'En Proceso (Proveedor)'),
        ('devuelta_proveedor', 'Terminada - Lista para Recoger'),
        ('recibida_optica', 'Recibida en Óptica'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada')
    ], validators=[DataRequired()])
    rejection_reason = TextAreaField('Razón del Rechazo', validators=[Optional()], 
                                   description='Requerido si el estado es "Rechazada por Proveedor"')
    comments = TextAreaField('Comentarios sobre el estado', validators=[Optional()])
    submit = SubmitField('Actualizar Estado')

    def validate_rejection_reason(self, rejection_reason):
        if self.status.data == 'rechazada' and not rejection_reason.data.strip():
            raise ValidationError('Debe proporcionar una razón del rechazo cuando rechaza una orden.')


class AdminCompleteLensForm(FlaskForm):
    """Formulario para que el admin complete los campos de lentes que la sede no puede llenar"""
    lens_class = SelectField('Clase de Lentes', choices=[
        ('', 'Seleccionar...'),
        ('Progresivo', 'Progresivo'),
        ('Bifocal', 'Bifocal'), 
        ('Monofocal', 'Monofocal')
    ], validators=[DataRequired(message='Debe seleccionar la clase de lentes')])
    lens_type = StringField('Tipo de Lente y Filtros', 
                           validators=[DataRequired(message='Debe especificar el tipo de lente y filtros'), 
                                     Length(max=128)])
    submit = SubmitField('Completar y Enviar al Proveedor')


class WorkOrderStatusForm(FlaskForm):
    status = SelectField('Estado de la Orden', choices=[
        ('pendiente_envio', 'Pendiente de Envío'),
        ('enviada', 'Enviada al Proveedor'),
        ('aceptada', 'Aceptada por Proveedor'),
        ('rechazada', 'Rechazada por Proveedor'),
        ('en_proceso', 'En Proceso (Proveedor)'),
        ('devuelta_proveedor', 'Terminada - Lista para Recoger'),
        ('recibida_optica', 'Recibida en Óptica'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada')
    ], validators=[DataRequired()])
    rejection_reason = TextAreaField('Razón del Rechazo', validators=[Optional()], 
                                   description='Requerido si el estado es "Rechazada por Proveedor"')
    comments = TextAreaField('Comentarios sobre el estado', validators=[Optional()])
    submit = SubmitField('Actualizar Estado')

    def validate_rejection_reason(self, rejection_reason):
        if self.status.data == 'rechazada' and not rejection_reason.data.strip():
            raise ValidationError('Debe proporcionar una razón del rechazo cuando rechaza una orden.')

class PaymentForm(FlaskForm):
    amount = FloatField('Monto del Pago', validators=[DataRequired()])
    description = TextAreaField('Descripción del Pago', validators=[Optional()])
    support_file = FileField('Comprobante de Pago', validators=[
        FileAllowed(['jpg', 'png', 'pdf'], 'Solo se permiten imágenes (JPG, PNG) o PDF.')
    ])
    submit = SubmitField('Registrar Pago')

# Implementé formulario para filtrar órdenes pendientes de pago
class PendingPaymentsFilterForm(FlaskForm):
    provider_id = SelectField('Filtrar por Proveedor', coerce=int, validators=[Optional()])
    submit = SubmitField('Filtrar')

    def __init__(self, providers=None, *args, **kwargs):
        super(PendingPaymentsFilterForm, self).__init__(*args, **kwargs)
        if providers is not None:
            # Uso la lista de proveedores proporcionada
            self.provider_id.choices = [(0, 'Todos los Proveedores')] + [(p.id, p.razon_social or p.name) for p in providers]
        else:
            # Comportamiento por defecto que implementé (todos los proveedores)
            self.provider_id.choices = [(0, 'Todos los Proveedores')] + [(p.id, p.razon_social or p.name) for p in Provider.query.order_by(Provider.name).all()]

class UserForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Rol', choices=[('asistente', 'Asistente (Óptica)'), ('proveedor', 'Proveedor'), ('admin', 'Administrador')], validators=[DataRequired()])
    is_active = BooleanField('Usuario Activo')
    provider_id = SelectField('Asignar a Proveedor (si es rol Proveedor)', coerce=int, validators=[Optional()])
    submit = SubmitField('Guardar Usuario')

    def __init__(self, original_user=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.original_user = original_user
        self.provider_id.choices = [('', '--- Seleccionar Proveedor ---')] + [(p.id, p.name) for p in Provider.query.all()]


    def validate_username(self, username):
        if username.data != self.original_user.username:
            user = User.query.filter_by(username=self.username.data).first()
            if user:
                raise ValidationError('Por favor, usa un nombre de usuario diferente.')

    def validate_email(self, email):
        if email.data != self.original_user.email:
            user = User.query.filter_by(email=self.email.data).first()
            if user:
                raise ValidationError('Por favor, usa una dirección de correo diferente.')


class SedeAdminForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirmar Contraseña', 
                             validators=[DataRequired(), EqualTo('password', message='Las contraseñas deben coincidir')])
    sede_id = SelectField('Sede Asignada', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Crear Administrador de Sede')

    def __init__(self, *args, **kwargs):
        super(SedeAdminForm, self).__init__(*args, **kwargs)
        from app.models import Sede
        sedes_list = []
        for s in Sede.query.filter_by(is_active=True).order_by(Sede.name).all():
            if s.city and s.city not in ['Selecciona tu ciudad', 'selecciona tu ciudad', '']:
                sedes_list.append((s.id, f"{s.name} - {s.city}"))
            else:
                sedes_list.append((s.id, s.name))
        self.sede_id.choices = sedes_list

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nombre de usuario ya está en uso.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Esta dirección de email ya está registrada.')


class SedeMessageForm(FlaskForm):
    title = StringField('Título del Mensaje', validators=[DataRequired(), Length(min=5, max=200)])
    message = TextAreaField('Mensaje', validators=[DataRequired(), Length(min=10, max=1000)])
    sede_id = SelectField('Destino', coerce=int)  # Removido DataRequired() para permitir 0
    priority = SelectField('Prioridad', choices=[
        ('normal', '📢 Normal'),
        ('alta', '⚠️ Alta'),
        ('urgente', '🚨 Urgente')
    ], validators=[DataRequired()])
    expires_at = DateField('Fecha de Expiración (Opcional)', validators=[Optional()])
    submit = SubmitField('Enviar Mensaje')

    def __init__(self, *args, **kwargs):
        super(SedeMessageForm, self).__init__(*args, **kwargs)
        from app.models import Sede
        sedes_list = []
        for s in Sede.query.filter_by(is_active=True).order_by(Sede.name).all():
            if s.city and s.city not in ['Selecciona tu ciudad', 'selecciona tu ciudad', '']:
                sedes_list.append((s.id, f"🏢 {s.name} - {s.city}"))
            else:
                sedes_list.append((s.id, f"🏢 {s.name}"))
        self.sede_id.choices = [(0, '📢 Todas las Sedes')] + sedes_list
        
        # Establezco valor por defecto si no se ha enviado el formulario
        if not self.sede_id.data:
            self.sede_id.data = 0
    
    def validate_sede_id(self, sede_id):
        # Validación personalizada: permitir 0 (todas las sedes) o un ID válido de sede
        if sede_id.data is None:
            raise ValidationError('Debe seleccionar un destino.')
        
        if sede_id.data != 0:  # Si no es "todas las sedes", verificar que la sede existe
            from app.models import Sede
            sede = Sede.query.filter_by(id=sede_id.data, is_active=True).first()
            if not sede:
                raise ValidationError('La sede seleccionada no es válida.')
    
    def validate_message(self, message):
        # Validación adicional para el mensaje
        if len(message.data.strip()) < 10:
            raise ValidationError('El mensaje debe tener al menos 10 caracteres.')
        
        if len(message.data.strip()) > 1000:
            raise ValidationError('El mensaje no puede exceder 1000 caracteres.')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Contraseña Actual', validators=[DataRequired()])
    new_password = PasswordField('Nueva Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Nueva Contraseña', 
                                   validators=[DataRequired(), EqualTo('new_password', message='Las contraseñas deben coincidir')])
    submit = SubmitField('Cambiar Contraseña')

    def __init__(self, user, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate_current_password(self, current_password):
        if not self.user.check_password(current_password.data):
            raise ValidationError('La contraseña actual es incorrecta.')


class ProviderAcceptOrderForm(FlaskForm):
    """Formulario para que el proveedor acepte una orden con plazo fijo de 7 días"""
    total_amount = FloatField('Monto a Cobrar a la Sede', 
                             validators=[DataRequired(), NumberRange(min=0.01, message='El monto debe ser mayor a cero')],
                             description='Indique el monto total que cobrará por esta orden de trabajo')
    provider_comments = TextAreaField('Comentarios del Proveedor', 
                                    validators=[Optional()],
                                    description='Información adicional sobre el trabajo a realizar (opcional)')
    submit = SubmitField('Aceptar Orden - Plazo Máximo 7 Días')

    def __init__(self, *args, **kwargs):
        super(ProviderAcceptOrderForm, self).__init__(*args, **kwargs)
        # Información sobre el plazo fijo
        self.delivery_info = "Al aceptar esta orden, se establecerá automáticamente un plazo máximo de 7 días calendario para la entrega."


class SedeUserEditForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('Nombre', validators=[DataRequired(), Length(max=128)])
    last_name = StringField('Apellido', validators=[DataRequired(), Length(max=128)])
    is_active = BooleanField('Usuario Activo')
    submit = SubmitField('Actualizar Usuario')

    def __init__(self, original_user=None, *args, **kwargs):
        super(SedeUserEditForm, self).__init__(*args, **kwargs)
        self.original_user = original_user

    def validate_username(self, username):
        if self.original_user and username.data != self.original_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Este nombre de usuario ya está en uso.')

    def validate_email(self, email):
        if self.original_user and email.data != self.original_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Este email ya está en uso.')