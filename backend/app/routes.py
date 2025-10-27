from flask import render_template, flash, redirect, url_for, request, current_app, send_from_directory, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from app import db, login_manager, csrf
from app import bp
from app.models import User, Provider, WorkOrder, Payment, Notification, Sede, SedeMessage
from app.forms import (
    LoginForm, RegistrationForm, ProviderForm, ProviderEditForm, WorkOrderForm,
    WorkOrderStatusForm, PaymentForm, PendingPaymentsFilterForm, UserForm, SedeAdminForm, SedeMessageForm,
    ChangePasswordForm, SedeUserEditForm
)
from werkzeug.utils import secure_filename
from functools import wraps
from urllib.parse import urlparse
import os
import uuid # Genero IDs únicos para las órdenes de trabajo
import bleach
import html
import re
import mimetypes  # Uso mimetypes en lugar de python-magic para simplicidad
from datetime import datetime

# Configuración de sanitización que implementé para seguridad
ALLOWED_TAGS = ['b', 'i', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li']
ALLOWED_ATTRIBUTES = {}

# Configuración de tipos de archivos que permito subir
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'txt'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/png', 'image/jpeg', 'image/gif',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain'
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # Límite de 5MB por archivo que establecí

def validate_file_upload(file):
    """Función que desarrollé para validar archivos subidos de forma exhaustiva"""
    errors = []
    
    if not file or not file.filename:
        return ["No se ha seleccionado ningún archivo"], None
    
    # Sanitizar nombre de archivo
    original_filename = file.filename
    secure_name = secure_filename(original_filename)
    
    if not secure_name:
        errors.append("Nombre de archivo inválido")
        return errors, None
    
    # Valido que el archivo tenga extensión
    if '.' not in secure_name:
        errors.append("El archivo debe tener una extensión")
        return errors, None
        
    extension = secure_name.rsplit('.', 1)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        errors.append(f"Extensión de archivo no permitida. Permitidas: {', '.join(ALLOWED_EXTENSIONS)}")
    
    # Leo el contenido del archivo para hacer validaciones adicionales
    file_content = file.read()
    file.seek(0)  # Reseteo el puntero del archivo para uso posterior
    
    # Verifico el tamaño del archivo
    if len(file_content) > MAX_FILE_SIZE:
        errors.append(f"El archivo es demasiado grande. Máximo permitido: {MAX_FILE_SIZE / (1024*1024):.1f}MB")
    
    # Valido el tipo MIME usando mimetypes (implementé esta solución por compatibilidad)
    try:
        detected_mime, _ = mimetypes.guess_type(secure_name)
        if detected_mime and detected_mime not in ALLOWED_MIME_TYPES:
            errors.append(f"Tipo de archivo no permitido: {detected_mime}")
    except Exception as e:
        errors.append("Error al verificar el tipo de archivo")
    
    # Implementé validación de contenido para evitar archivos ejecutables maliciosos
    dangerous_signatures = [
        b'\x4d\x5a',  # MZ header (ejecutables Windows)
        b'\x7f\x45\x4c\x46',  # ELF header (ejecutables Linux)
        b'\xfe\xed\xfa',  # Mach-O header (ejecutables macOS)
        b'<script',  # Scripts en archivos de texto
        b'<?php',  # Código PHP
    ]
    
    file_start = file_content[:100].lower()
    for signature in dangerous_signatures:
        if signature in file_start:
            errors.append("El archivo contiene contenido potencialmente peligroso")
            break
    
    if errors:
        return errors, None
        
    # Genero un nombre único y seguro para el archivo
    unique_filename = f"{uuid.uuid4().hex}_{secure_name}"
    
    return [], unique_filename

def sanitize_input(input_string):
    """Función que desarrollé para sanitizar entrada de usuario y prevenir XSS"""
    if not input_string:
        return input_string
    
    # Elimino caracteres peligrosos usando bleach
    cleaned = bleach.clean(str(input_string), tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    # Aplico escape adicional para HTML por seguridad
    cleaned = html.escape(cleaned, quote=True)
    return cleaned.strip()

def validate_and_sanitize_form_data(form_data, required_fields=None):
    """Función que creé para validar y sanitizar datos de formulario"""
    sanitized_data = {}
    errors = []
    
    if required_fields is None:
        required_fields = []
    
    for key, value in form_data.items():
        if value is not None:
            sanitized_value = sanitize_input(value)
            
            # Implementé validaciones específicas para diferentes tipos de campos
            if key in ['email'] and sanitized_value:
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', sanitized_value):
                    errors.append(f'El formato del email {key} no es válido')
            
            if key in ['phone'] and sanitized_value:
                if not re.match(r'^[\d\s\-\+\(\)]+$', sanitized_value):
                    errors.append(f'El formato del teléfono {key} no es válido')
            
            sanitized_data[key] = sanitized_value
        
        # Verifico campos obligatorios
        if key in required_fields and (not value or not sanitized_data.get(key)):
            errors.append(f'El campo {key} es obligatorio')
    
    return sanitized_data, errors

# --- Decoradores que implementé para control de roles ---
def role_required(*roles):
    """Decorador que creé para proteger rutas según el rol del usuario"""
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.role not in roles:
                flash('No tienes permiso para acceder a esta página.', 'danger')
                return redirect(url_for('main.index'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# --- Rutas de Autenticación que desarrollé ---
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Obtengo datos del formulario directamente
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user_type = request.form.get('user_type', '')
        sede_id = request.form.get('sede_id', type=int)
        remember_me = 'remember_me' in request.form
        
        # Validaciones básicas
        if not username or not password or not user_type:
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('main.login'))
        
        # Buscar usuario en la base de datos
        user = User.query.filter_by(username=username).first()
        
        # Valido que el usuario existe, password es correcto y está activo
        if user is None or not user.check_password(password) or not user.is_active:
            flash('Usuario o contraseña inválidos o cuenta inactiva.', 'danger')
            return redirect(url_for('main.login'))
        
        # Valido que el tipo de usuario seleccionado coincida con el rol del usuario
        if user_type == 'central' and user.role not in ['admin', 'asistente']:
            flash('Este usuario no tiene acceso a Administración Central.', 'danger')
            return redirect(url_for('main.login'))
        elif user_type == 'sede' and user.role != 'admin_sede':
            flash('Este usuario no es administrador de sede.', 'danger')
            return redirect(url_for('main.login'))
        elif user_type == 'proveedor' and user.role != 'proveedor':
            flash('Este usuario no es proveedor.', 'danger')
            return redirect(url_for('main.login'))
        
        # Para administradores de sede, validar que se seleccionó una sede válida
        if user_type == 'sede':
            if not sede_id or sede_id == 0:
                flash('Debe seleccionar una sede.', 'danger')
                return redirect(url_for('main.login'))
            
            # Verifico que el usuario puede acceder a esta sede
            if user.sede_id and user.sede_id != sede_id:
                flash('No tiene permisos para acceder a esta sede.', 'danger')
                return redirect(url_for('main.login'))
            
            # Almacenar la sede seleccionada en la sesión
            from flask import session
            session['sede_seleccionada'] = sede_id
        
        # Login exitoso
        login_user(user, remember=remember_me)
        
        # Inicializar timeout de sesión
        from flask import session
        from datetime import datetime
        session['last_activity'] = datetime.now().isoformat()
        session.permanent = True
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        
        # Implementé mensajes personalizados según el tipo de usuario
        if user.role == 'admin':
            flash(f'Bienvenido Administrador Central, {user.username}!', 'success')
        elif user.role == 'asistente':
            flash(f'Bienvenido Asistente, {user.username}!', 'success')
        elif user.role == 'admin_sede':
            sede = Sede.query.get(session.get('sede_seleccionada'))
            flash(f'Bienvenido Administrador de {sede.name}, {user.username}!', 'success')
        elif user.role == 'proveedor':
            flash(f'Bienvenido Proveedor, {user.username}!', 'success')
        
        return redirect(next_page)
    
    # GET request - mostrar el formulario de login
    # Obtengo sedes para el select
    sedes = Sede.query.filter_by(is_active=True).order_by(Sede.city, Sede.name).all()
    return render_template('auth/login.html', title='Iniciar Sesión', sedes=sedes)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
@role_required('admin')
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        if form.role.data == 'proveedor' and form.provider_name.data:
            user.provider_id = form.provider_name.data # Asigna el ID del proveedor
        db.session.add(user)
        db.session.commit()
        flash(f'Usuario {user.username} registrado exitosamente con el rol {user.role}.', 'success')
        return redirect(url_for('main.login'))
    return render_template('auth/register.html', title='Registrar Usuario', form=form)

# --- Rutas del Panel de Control que implementé ---
@bp.route('/')
@bp.route('/index')
@login_required
def index():
    if current_user.role in ['admin', 'asistente', 'admin_sede']:
        from sqlalchemy import func
        
        total_orders = WorkOrder.query.count()
        
        # Órdenes en progreso (enviadas, aceptadas, en proceso)
        orders_in_progress = WorkOrder.query.filter(WorkOrder.status.in_(['enviada', 'aceptada', 'en_proceso'])).count()
        
        # Órdenes listas para recoger
        orders_ready = WorkOrder.query.filter_by(status='devuelta_proveedor').count()
        
        # Órdenes completas (recibidas en óptica + finalizadas)
        orders_finished = WorkOrder.query.filter(WorkOrder.status.in_(['recibida_optica', 'finalizada'])).count()
        
        # Órdenes rechazadas
        orders_rejected = WorkOrder.query.filter_by(status='rechazada').count()

        # Gráficos: estado general de órdenes
        chart_data = {
            'labels': ['En Progreso', 'Listas para Recoger', 'Completadas', 'Rechazadas'],
            'data': [orders_in_progress, orders_ready, orders_finished, orders_rejected]
        }
        
        return render_template('index.html', title='Panel de Control',
                               total_orders=total_orders,
                               orders_in_progress=orders_in_progress,
                               orders_ready=orders_ready,
                               orders_finished=orders_finished,
                               orders_rejected=orders_rejected,
                               chart_data=chart_data)

    elif current_user.role == 'proveedor' and current_user.provider:
        provider_id = current_user.provider.id
        orders_pending_response = WorkOrder.query.filter_by(provider_id=provider_id, status='enviada').count()  # Pendientes de aceptar/rechazar
        orders_accepted = WorkOrder.query.filter_by(provider_id=provider_id, status='aceptada').count()  # Aceptadas pero no iniciadas
        orders_in_process = WorkOrder.query.filter_by(provider_id=provider_id, status='en_proceso').count()  # En proceso
        orders_completed = WorkOrder.query.filter_by(provider_id=provider_id, status='devuelta_proveedor').count()  # Terminadas
        orders_paid = WorkOrder.query.filter_by(provider_id=provider_id, payment_status='pagada').count()
        orders_pending_payment = WorkOrder.query.filter_by(provider_id=provider_id, payment_status='pendiente').count()

        chart_data = {
            'labels': ['Pendientes Respuesta', 'Aceptadas', 'En Proceso', 'Terminadas'],
            'data': [orders_pending_response, orders_accepted, orders_in_process, orders_completed]
        }
        payment_chart_data = {
            'labels': ['Pagadas', 'Pendientes de Pago'],
            'data': [orders_paid, orders_pending_payment]
        }
        return render_template('index.html', title='Panel de Proveedor',
                                    orders_pending_response=orders_pending_response,
                                    orders_accepted=orders_accepted,
                                    orders_in_process=orders_in_process,
                                    orders_completed=orders_completed,
                                    orders_paid=orders_paid,
                                    orders_pending_payment=orders_pending_payment,
                                    chart_data=chart_data,
                                    payment_chart_data=payment_chart_data)
    else:
        # Si un usuario proveedor no tiene provider_id asociado, o algún otro caso no manejado.
        flash('Tu cuenta no está completamente configurada. Contacta al administrador.', 'warning')
        return render_template('index.html', title='Inicio')


# --- Dashboard Administrativo que desarrollé ---
@bp.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    """Dashboard completo para administrador central con estadísticas por sede"""
    from sqlalchemy import func, and_, extract
    from datetime import datetime, timedelta
    
    # Obtengo mes actual
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Obtengo todas las sedes
    sedes = Sede.query.filter_by(is_active=True).order_by(Sede.name).all()
    
    sede_stats = []
    
    for sede in sedes:
        # Estadísticas por sede
        
        # Órdenes totales de la sede
        total_orders = WorkOrder.query.filter_by(sede_id=sede.id).count()
        
        # Órdenes del mes actual
        orders_this_month = WorkOrder.query.filter(
            and_(
                WorkOrder.sede_id == sede.id,
                extract('month', WorkOrder.created_at) == current_month,
                extract('year', WorkOrder.created_at) == current_year
            )
        ).count()
        
        # Órdenes finalizadas (completas)
        orders_completed = WorkOrder.query.filter(
            and_(
                WorkOrder.sede_id == sede.id,
                WorkOrder.status.in_(['recibida_optica', 'finalizada'])
            )
        ).count()
        
        # Órdenes finalizadas este mes
        orders_completed_this_month = WorkOrder.query.filter(
            and_(
                WorkOrder.sede_id == sede.id,
                WorkOrder.status.in_(['recibida_optica', 'finalizada']),
                extract('month', WorkOrder.created_at) == current_month,
                extract('year', WorkOrder.created_at) == current_year
            )
        ).count()
        
        # Órdenes en progreso
        orders_in_progress = WorkOrder.query.filter(
            and_(
                WorkOrder.sede_id == sede.id,
                WorkOrder.status.in_(['enviada', 'aceptada', 'en_proceso'])
            )
        ).count()
        
        # Órdenes listas para recoger
        orders_ready = WorkOrder.query.filter(
            and_(
                WorkOrder.sede_id == sede.id,
                WorkOrder.status == 'devuelta_proveedor'
            )
        ).count()
        
        # Ventas del mes (suma de costos de órdenes pagadas)
        sales_this_month = db.session.query(func.sum(WorkOrder.total_amount)).filter(
            and_(
                WorkOrder.sede_id == sede.id,
                WorkOrder.payment_status == 'pagada',
                extract('month', WorkOrder.created_at) == current_month,
                extract('year', WorkOrder.created_at) == current_year
            )
        ).scalar() or 0
        
        # Ventas totales
        total_sales = db.session.query(func.sum(WorkOrder.total_amount)).filter(
            and_(
                WorkOrder.sede_id == sede.id,
                WorkOrder.payment_status == 'pagada'
            )
        ).scalar() or 0
        
        # Pagos pendientes
        pending_payments = db.session.query(func.sum(WorkOrder.total_amount)).filter(
            and_(
                WorkOrder.sede_id == sede.id,
                WorkOrder.payment_status == 'pendiente',
                WorkOrder.status.in_(['recibida_optica', 'finalizada'])
            )
        ).scalar() or 0
        
        # Tasa de finalización (% de órdenes completadas vs total)
        completion_rate = round((orders_completed / total_orders * 100) if total_orders > 0 else 0, 1)
        
        # Promedio de días para completar órdenes (simplificado - basado en created_at)
        # Nota: Esto es una estimación. Para mayor precisión, el modelo necesita un campo updated_at
        avg_completion_days = 7  # Valor fijo por ahora, se puede calcular cuando se agregue updated_at
        
        sede_stats.append({
            'sede': sede,
            'total_orders': total_orders,
            'orders_this_month': orders_this_month,
            'orders_completed': orders_completed,
            'orders_completed_this_month': orders_completed_this_month,
            'orders_in_progress': orders_in_progress,
            'orders_ready': orders_ready,
            'sales_this_month': sales_this_month,
            'total_sales': total_sales,
            'pending_payments': pending_payments,
            'completion_rate': completion_rate,
            'avg_completion_days': avg_completion_days
        })
    
    # Estadísticas generales del sistema
    system_stats = {
        'total_sedes': len(sedes),
        'total_orders_system': sum([s['total_orders'] for s in sede_stats]),
        'total_sales_system': sum([s['total_sales'] for s in sede_stats]),
        'total_pending_payments': sum([s['pending_payments'] for s in sede_stats]),
        'orders_this_month_system': sum([s['orders_this_month'] for s in sede_stats]),
        'sales_this_month_system': sum([s['sales_this_month'] for s in sede_stats])
    }
    
    # Top 5 sedes por ventas del mes
    top_sedes_month = sorted(sede_stats, key=lambda x: x['sales_this_month'], reverse=True)[:5]
    
    # Top 5 sedes por órdenes del mes
    top_sedes_orders = sorted(sede_stats, key=lambda x: x['orders_this_month'], reverse=True)[:5]
    
    return render_template('admin/dashboard.html', 
                         title='Dashboard Administrativo',
                         sede_stats=sede_stats,
                         system_stats=system_stats,
                         top_sedes_month=top_sedes_month,
                         top_sedes_orders=top_sedes_orders,
                         current_month=current_month,
                         current_year=current_year)


# --- API Endpoints que creé para el Dashboard ---
@bp.route('/api/admin/stats')
@login_required
@role_required('admin')
def api_admin_stats():
    """API endpoint para obtener estadísticas en tiempo real"""
    from sqlalchemy import func, and_, extract
    from datetime import datetime
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Estadísticas rápidas del sistema
    total_orders = WorkOrder.query.count()
    orders_this_month = WorkOrder.query.filter(
        and_(
            extract('month', WorkOrder.created_at) == current_month,
            extract('year', WorkOrder.created_at) == current_year
        )
    ).count()
    
    pending_orders = WorkOrder.query.filter(
        WorkOrder.status.in_(['enviada', 'aceptada', 'en_proceso'])
    ).count()
    
    return jsonify({
        'total_orders': total_orders,
        'orders_this_month': orders_this_month,
        'pending_orders': pending_orders,
        'timestamp': datetime.now().isoformat()
    })


@bp.route('/api/admin/sede/<int:sede_id>')
@login_required
@role_required('admin')
def api_sede_details(sede_id):
    """API endpoint para obtener detalles específicos de una sede"""
    from sqlalchemy import func, and_, extract
    from datetime import datetime, timedelta
    
    sede = Sede.query.get_or_404(sede_id)
    
    # Estadísticas de los últimos 6 meses
    months_data = []
    for i in range(6):
        date = datetime.now() - timedelta(days=30*i)
        month = date.month
        year = date.year
        
        orders_count = WorkOrder.query.filter(
            and_(
                WorkOrder.sede_id == sede_id,
                extract('month', WorkOrder.created_at) == month,
                extract('year', WorkOrder.created_at) == year
            )
        ).count()
        
        sales = db.session.query(func.sum(WorkOrder.total_amount)).filter(
            and_(
                WorkOrder.sede_id == sede_id,
                WorkOrder.payment_status == 'pagada',
                extract('month', WorkOrder.created_at) == month,
                extract('year', WorkOrder.created_at) == year
            )
        ).scalar() or 0
        
        months_data.append({
            'month': f"{month}/{year}",
            'orders': orders_count,
            'sales': float(sales)
        })
    
    return jsonify({
        'sede': {
            'id': sede.id,
            'name': sede.name,
            'city': sede.city,
            'manager': sede.manager
        },
        'months_data': list(reversed(months_data))  # Más reciente al final
    })


# --- Gestión de Proveedores que desarrollé ---
@bp.route('/providers')
@login_required
@role_required('admin', 'asistente')
def list_providers():
    providers = Provider.query.order_by(Provider.name).all()
    return render_template('proveedores/list.html', title='Lista de Proveedores', providers=providers)

@bp.route('/provider/new', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'asistente')
def create_provider():
    form = ProviderForm()
    if form.validate_on_submit():
        try:
            # Creo el proveedor
            provider = Provider(
                nit=form.nit.data,
                razon_social=form.razon_social.data,
                name=form.name.data or form.razon_social.data,  # Usar razón social si no hay nombre comercial
                contact_person=form.contact_person.data,
                phone=form.phone.data,
                email=form.email.data,
                address=form.address.data
            )
            db.session.add(provider)
            db.session.flush()  # Para obtener el ID del proveedor
            
            # Creo el usuario para el proveedor
            user = User(
                username=form.username.data,
                email=form.user_email.data,
                role='proveedor',
                provider_id=provider.id
            )
            user.set_password(form.password.data)
            db.session.add(user)
            
            db.session.commit()
            
            flash(f'Proveedor "{provider.razon_social}" y usuario "{user.username}" registrados exitosamente!', 'success')
            return redirect(url_for('main.list_providers'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el proveedor: {str(e)}', 'error')
            return render_template('proveedores/create_edit.html', title='Registrar Nuevo Proveedor', form=form)
    return render_template('proveedores/create_edit.html', title='Registrar Nuevo Proveedor', form=form)

@bp.route('/provider/edit/<int:provider_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'asistente')
def edit_provider(provider_id):
    provider = Provider.query.get_or_404(provider_id)
    form = ProviderEditForm(obj=provider) # Pre-pobla el formulario con los datos del proveedor
    form._original_obj = provider  # Para validaciones
    if form.validate_on_submit():
        form.populate_obj(provider) # Actualiza el objeto proveedor con los datos del formulario
        db.session.commit()
        flash(f'Proveedor "{provider.razon_social}" actualizado exitosamente!', 'success')
        return redirect(url_for('main.list_providers'))
    return render_template('proveedores/create_edit.html', title='Editar Proveedor', form=form, provider_id=provider_id)

@bp.route('/provider/change_password/<int:provider_id>', methods=['POST'])
@login_required
@role_required('admin', 'asistente')
def change_provider_password(provider_id):
    provider = Provider.query.get_or_404(provider_id)
    
    # Buscar el usuario asociado al proveedor
    user = User.query.filter_by(provider_id=provider_id, role='proveedor').first()
    
    if not user:
        flash('Este proveedor no tiene un usuario asociado.', 'error')
        return redirect(url_for('main.list_providers'))
    
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Validaciones básicas (sin sanitizar las contraseñas)
    if not new_password or not confirm_password:
        flash('Todos los campos son obligatorios.', 'error')
        return redirect(url_for('main.list_providers'))
    
    if len(new_password) < 6:
        flash('La contraseña debe tener al menos 6 caracteres.', 'error')
        return redirect(url_for('main.list_providers'))
    
    if new_password != confirm_password:
        flash('Las contraseñas no coinciden.', 'error')
        return redirect(url_for('main.list_providers'))
    
    # Actualizar la contraseña
    try:
        user.set_password(new_password)
        db.session.commit()
        flash(f'Contraseña actualizada exitosamente para el usuario "{user.username}" del proveedor "{provider.razon_social}".', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar la contraseña: {str(e)}', 'error')
    
    return redirect(url_for('main.list_providers'))

# --- Gestión de Sedes que implementé ---
@bp.route('/sedes')
@login_required
@role_required('admin', 'asistente')
def list_sedes():
    sedes = Sede.query.order_by(Sede.city, Sede.name).all()
    return render_template('sedes/list.html', title='Gestión de Sedes', sedes=sedes)

@bp.route('/sede/add', methods=['POST'])
@login_required
@role_required('admin', 'asistente')
def add_sede():
    name = request.form.get('name')
    city = request.form.get('city')
    address = request.form.get('address')
    phone = request.form.get('phone')
    manager = request.form.get('manager')
    
    # Datos del administrador
    admin_username = request.form.get('admin_username')
    admin_email = request.form.get('admin_email')
    admin_password = request.form.get('admin_password')
    admin_password2 = request.form.get('admin_password2')
    
    # Valido datos básicos de la sede
    if not name or not city:
        flash('Nombre y ciudad son campos obligatorios.', 'error')
        return redirect(url_for('main.list_sedes'))
    
    # Valido datos del administrador
    if not admin_username or not admin_email or not admin_password:
        flash('Usuario, email y contraseña del administrador son obligatorios.', 'error')
        return redirect(url_for('main.list_sedes'))
    
    if admin_password != admin_password2:
        flash('Las contraseñas del administrador no coinciden.', 'error')
        return redirect(url_for('main.list_sedes'))
    
    if len(admin_password) < 6:
        flash('La contraseña del administrador debe tener al menos 6 caracteres.', 'error')
        return redirect(url_for('main.list_sedes'))
    
    # Verifico si ya existe una sede con el mismo nombre
    existing_sede = Sede.query.filter_by(name=name).first()
    if existing_sede:
        flash(f'Ya existe una sede con el nombre "{name}".', 'error')
        return redirect(url_for('main.list_sedes'))
    
    # Verifico si ya existe un usuario con el mismo username o email
    existing_user_username = User.query.filter_by(username=admin_username).first()
    if existing_user_username:
        flash(f'Ya existe un usuario con el nombre "{admin_username}".', 'error')
        return redirect(url_for('main.list_sedes'))
    
    existing_user_email = User.query.filter_by(email=admin_email).first()
    if existing_user_email:
        flash(f'Ya existe un usuario con el email "{admin_email}".', 'error')
        return redirect(url_for('main.list_sedes'))
    
    try:
        # Creo la sede primero
        new_sede = Sede(
            name=name,
            city=city,
            address=address,
            phone=phone,
            manager=manager,
            is_active=True
        )
        db.session.add(new_sede)
        db.session.flush()  # Para obtener el ID de la sede
        
        # Creo el usuario administrador de la sede
        admin_user = User(
            username=admin_username,
            email=admin_email,
            role='admin_sede',
            sede_id=new_sede.id,
            is_active=True
        )
        admin_user.set_password(admin_password)
        db.session.add(admin_user)
        
        # Confirmar ambas transacciones
        db.session.commit()
        
        flash(f'Sede "{name}" creada exitosamente con su administrador "{admin_username}".', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear la sede: {str(e)}', 'error')
    
    return redirect(url_for('main.list_sedes'))

@bp.route('/sede/toggle_status/<int:sede_id>', methods=['POST'])
@login_required
@role_required('admin', 'asistente')
def toggle_sede_status(sede_id):
    sede = Sede.query.get_or_404(sede_id)
    
    try:
        sede.is_active = not sede.is_active
        db.session.commit()
        return jsonify({'success': True, 'message': f'Sede {"activada" if sede.is_active else "desactivada"} exitosamente.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@bp.route('/sede/edit/<int:sede_id>', methods=['POST'])
@login_required
@role_required('admin', 'asistente')
def edit_sede(sede_id):
    sede = Sede.query.get_or_404(sede_id)
    
    name = request.form.get('name')
    city = request.form.get('city')
    address = request.form.get('address')
    phone = request.form.get('phone')
    manager = request.form.get('manager')
    
    if not name or not city:
        flash('Nombre y ciudad son campos obligatorios.', 'error')
        return redirect(url_for('main.list_sedes'))
    
    # Verifico si ya existe otra sede con el mismo nombre (excluyendo la actual)
    existing_sede = Sede.query.filter(Sede.name == name, Sede.id != sede_id).first()
    if existing_sede:
        flash(f'Ya existe otra sede con el nombre "{name}".', 'error')
        return redirect(url_for('main.list_sedes'))
    
    try:
        sede.name = name
        sede.city = city
        sede.address = address
        sede.phone = phone
        sede.manager = manager
        db.session.commit()
        flash(f'Sede "{name}" actualizada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar la sede: {str(e)}', 'error')
    
    return redirect(url_for('main.list_sedes'))

@bp.route('/sede/change_admin_password/<int:sede_id>', methods=['POST'])
@login_required
@role_required('admin', 'asistente')
def change_sede_admin_password(sede_id):
    sede = Sede.query.get_or_404(sede_id)
    
    # Buscar el administrador de la sede
    admin_user = User.query.filter_by(sede_id=sede_id, role='admin_sede', is_active=True).first()
    if not admin_user:
        flash('No se encontró un administrador activo para esta sede.', 'error')
        return redirect(url_for('main.list_sedes'))
    
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')
    
    # Validaciones
    if not new_password or not confirm_new_password:
        flash('Todos los campos de contraseña son obligatorios.', 'error')
        return redirect(url_for('main.list_sedes'))
    
    if new_password != confirm_new_password:
        flash('Las contraseñas no coinciden.', 'error')
        return redirect(url_for('main.list_sedes'))
    
    if len(new_password) < 6:
        flash('La contraseña debe tener al menos 6 caracteres.', 'error')
        return redirect(url_for('main.list_sedes'))
    
    try:
        admin_user.set_password(new_password)
        db.session.commit()
        flash(f'Contraseña del administrador de sede "{admin_user.username}" cambiada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar la contraseña: {str(e)}', 'error')
    
    return redirect(url_for('main.list_sedes'))

@bp.route('/create_sede_admin', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_sede_admin():
    form = SedeAdminForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data,
                email=form.email.data,
                role='admin_sede',
                sede_id=form.sede_id.data,
                is_active=True
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            
            sede = Sede.query.get(form.sede_id.data)
            flash(f'Administrador de sede "{user.username}" creado exitosamente para {sede.name}.', 'success')
            return redirect(url_for('main.admin_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el administrador de sede: {str(e)}', 'error')
    
    return render_template('admin/create_sede_admin.html', title='Crear Administrador de Sede', form=form)

@bp.route('/sede_payments')
@login_required
@role_required('admin_sede')
def sede_payments():
    from flask import session
    
    # Primero verificar si el usuario tiene sede asignada
    if not current_user.sede_id:
        flash('Usuario no tiene sede asignada.', 'danger')
        return redirect(url_for('main.index'))
    
    # Usar la sede del usuario si no hay sede en sesión
    sede_id = session.get('sede_seleccionada', current_user.sede_id)
    
    # Verifico que la sede de la sesión coincida con la del usuario
    if sede_id != current_user.sede_id:
        sede_id = current_user.sede_id
        session['sede_seleccionada'] = sede_id
    
    # Obtengo órdenes de la sede con información de pagos
    orders = WorkOrder.query.filter_by(sede_id=sede_id).order_by(WorkOrder.created_at.desc()).all()
    
    # Separar órdenes por estado de pago
    pending_payments = [order for order in orders if order.payment_status in ['pendiente', 'parcialmente_pagada']]
    paid_orders = [order for order in orders if order.payment_status == 'pagada']
    
    # Obtengo proveedores únicos que tienen órdenes en esta sede
    provider_ids = {order.provider_id for order in orders if order.provider_id}
    providers = Provider.query.filter(Provider.id.in_(provider_ids)).all() if provider_ids else []
    
    sede = Sede.query.get(sede_id)
    
    if not sede:
        flash('Sede no encontrada.', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('pagos/sede_payments.html', 
                         title=f'Gestión de Pagos - {sede.name}', 
                         orders=orders, 
                         pending_payments=pending_payments,
                         paid_orders=paid_orders,
                         providers=providers,
                         sede=sede)

# --- Sistema de Órdenes de Trabajo que desarrollé ---
@bp.route('/orders')
@login_required
def list_orders():
    if current_user.role == 'proveedor' and current_user.provider:
        orders = WorkOrder.query.filter_by(provider_id=current_user.provider.id).order_by(WorkOrder.created_at.desc()).all()
    elif current_user.role == 'admin_sede' and current_user.sede_id:
        # Admin de sede solo ve órdenes de su sede
        orders = WorkOrder.query.filter_by(sede_id=current_user.sede_id).order_by(WorkOrder.created_at.desc()).all()
    else: # admin, asistente, o proveedor sin asignación (que no debería pasar en la práctica)
        orders = WorkOrder.query.order_by(WorkOrder.created_at.desc()).all()
    return render_template('ordenes/list.html', title='Lista de Órdenes de Trabajo', orders=orders)

@bp.route('/order/new', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'asistente', 'admin_sede')
def create_order():
    form = WorkOrderForm(current_user=current_user)
    
    if form.validate_on_submit():
        # Validación adicional para admin_sede: solo puede crear órdenes para su sede
        if current_user.role == 'admin_sede':
            if form.sede_id.data != current_user.sede_id:
                flash('Solo puedes crear órdenes para tu sede asignada.', 'danger')
                return render_template('ordenes/create_edit.html', title='Crear Nueva Orden de Trabajo', form=form)
        
        order_number = str(uuid.uuid4()).split('-')[0].upper() # Genera un número de orden simple
        order = WorkOrder(
            order_number=order_number,
            client_name=form.client_name.data,
            client_cc=form.client_cc.data,
            receipt_number=form.receipt_number.data,
            lens_type=form.lens_type.data,
            sede_id=form.sede_id.data,
            provider_id=form.provider_id.data,
            # Fórmula Ojo Derecho
            formula_od_esfera=form.formula_od_esfera.data,
            formula_od_cilindro=form.formula_od_cilindro.data,
            formula_od_eje=form.formula_od_eje.data,
            formula_od_adicion=form.formula_od_adicion.data,
            # Fórmula Ojo Izquierdo
            formula_oi_esfera=form.formula_oi_esfera.data,
            formula_oi_cilindro=form.formula_oi_cilindro.data,
            formula_oi_eje=form.formula_oi_eje.data,
            formula_oi_adicion=form.formula_oi_adicion.data,
            # Información adicional
            formula_details=form.formula_details.data,
            due_date=form.due_date.data,
            comments=form.comments.data,
            created_by_user_id=current_user.id,
            total_amount=form.total_amount.data if form.total_amount.data else 0.0,
            status='enviada'  # Enviar automáticamente al proveedor
        )
        db.session.add(order)
        # Flush para asegurar que order.id esté disponible antes de crear notificaciones
        db.session.flush()
        # Notificar al proveedor inmediatamente
        provider_user = User.query.filter_by(provider_id=order.provider_id, role='proveedor').first()
        if provider_user:
            notification = Notification(
                user_id=provider_user.id,
                message=f'🆕 Nueva orden recibida! N°: {order.order_number} para {order.client_name}. Por favor acepta o rechaza esta orden.',
                work_order_id=order.id
            )
            db.session.add(notification)
            
        # Notificar a la sede que creó la orden (si es admin_sede)
        if current_user.role == 'admin_sede':
            notification = Notification(
                user_id=current_user.id,
                message=f'✅ Orden creada exitosamente. La orden N° {order.order_number} para {order.client_name} ha sido enviada al proveedor {order.provider.name}.',
                work_order_id=order.id
            )
            db.session.add(notification)
        db.session.commit()
        # Obtengo nombre del proveedor de forma segura (por si la relación no está cargada)
        provider_name = None
        if order.provider_id:
            p = Provider.query.get(order.provider_id)
            provider_name = p.name if p else None

        flash(f'Orden de Trabajo N° {order.order_number} creada' + (f' y asignada a {provider_name}.' if provider_name else '.'), 'success')
        return redirect(url_for('main.list_orders'))
    return render_template('ordenes/create_edit.html', title='Crear Nueva Orden de Trabajo', form=form)


@bp.route('/order/<int:order_id>')
@login_required
def view_order(order_id):
    order = WorkOrder.query.get_or_404(order_id)
    # Asegúrate de que el proveedor solo vea sus propias órdenes
    if current_user.role == 'proveedor' and current_user.provider and order.provider_id != current_user.provider.id:
        flash('No tienes permiso para ver esta orden.', 'danger')
        return redirect(url_for('main.list_orders'))

    payments = Payment.query.filter_by(work_order_id=order.id).order_by(Payment.payment_date.desc()).all()

    return render_template('ordenes/detail.html', title=f'Detalle de Orden {order.order_number}', order=order, payments=payments)

@bp.route('/order/edit/<int:order_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'asistente', 'admin_sede')
def edit_order(order_id):
    order = WorkOrder.query.get_or_404(order_id)
    
    # Verifico permisos para admin_sede: solo puede editar órdenes de su sede
    if current_user.role == 'admin_sede':
        if order.sede_id != current_user.sede_id:
            flash('No tienes permisos para editar órdenes de otras sedes.', 'danger')
            return redirect(url_for('main.list_orders'))
    
    form = WorkOrderForm(current_user=current_user, obj=order)
    if form.validate_on_submit():
        # Validación adicional para admin_sede: no puede cambiar la sede
        if current_user.role == 'admin_sede':
            if form.sede_id.data != current_user.sede_id:
                flash('No puedes cambiar la sede de origen de la orden.', 'danger')
                return render_template('ordenes/create_edit.html', title=f'Editar Orden {order.order_number}', form=form, order=order)
        
        form.populate_obj(order)
        order.created_by_user_id = current_user.id # Quien edita también se registra
        db.session.commit()
        flash(f'Orden de Trabajo N° {order.order_number} actualizada exitosamente.', 'success')
        return redirect(url_for('main.view_order', order_id=order.id))
    return render_template('ordenes/create_edit.html', title=f'Editar Orden {order.order_number}', form=form, order=order)

@bp.route('/order/update_status/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_order_status(order_id):
    order = WorkOrder.query.get_or_404(order_id)

    # Restricciones por rol para cambiar estados
    if current_user.role == 'proveedor' and (order.provider_id != current_user.provider.id if current_user.provider else True):
        flash('No tienes permiso para actualizar el estado de esta orden.', 'danger')
        return redirect(url_for('main.view_order', order_id=order_id))
    
    if current_user.role == 'asistente' or current_user.role == 'admin':
        # Asistente/Admin puede cambiar casi todos los estados
        allowed_statuses = [
            'pendiente_envio', 'enviada', 'recibida_optica', 'finalizada', 'cancelada'
        ]
    elif current_user.role == 'proveedor':
        # Proveedor puede aceptar, rechazar, iniciar trabajo y marcar como terminado
        if order.status == 'enviada':
            # Si la orden está enviada, puede aceptar o rechazar
            allowed_statuses = ['aceptada', 'rechazada']
        elif order.status == 'aceptada':
            # Si ya aceptó, puede iniciar el trabajo
            allowed_statuses = ['en_proceso']
        elif order.status == 'en_proceso':
            # Si está en proceso, puede marcar como terminada
            allowed_statuses = ['devuelta_proveedor']
        else:
            # No puede cambiar otros estados
            allowed_statuses = []
    else:
        flash('Rol no autorizado para actualizar estados.', 'danger')
        return redirect(url_for('main.view_order', order_id=order_id))

    form = WorkOrderStatusForm(obj=order)
    # Filtrar las opciones de estado según el rol
    form.status.choices = [(s, label) for s, label in form.status.choices if s in allowed_statuses]


    if form.validate_on_submit():
        old_status = order.status
        order.status = form.status.data
        
        # Manejar rechazo: almacenar razón y incrementar contador
        if order.status == 'rechazada' and old_status != 'rechazada':
            order.rejection_reason = form.rejection_reason.data
            order.rejection_count = (order.rejection_count or 0) + 1
        
        # Asegurar que comments sea string antes de concatenar
        if order.comments is None:
            order.comments = ''
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        if form.comments.data:
            order.comments += f"\n[{timestamp}] {current_user.username} cambió el estado a '{order.status}'. Comentarios: {form.comments.data}"
        else:
            order.comments += f"\n[{timestamp}] {current_user.username} cambió el estado a '{order.status}'."
        
        # Agregar razón de rechazo a los comentarios si aplica
        if order.status == 'rechazada' and form.rejection_reason.data:
            order.comments += f"\n[{timestamp}] Razón del rechazo: {form.rejection_reason.data}"
        
        db.session.commit()

        # Notificaciones automáticas según el flujo
        if order.status == 'enviada':
            # Notificar al proveedor cuando se le asigna
            provider_user = User.query.filter_by(provider_id=order.provider_id, role='proveedor').first()
            if provider_user:
                notification = Notification(user_id=provider_user.id, message=f'Nueva orden N° {order.order_number} enviada para {order.client_name}. Por favor revisa y acepta/rechaza.', work_order_id=order.id)
                db.session.add(notification)
                
            # También confirmar a la sede que envió la orden
            if old_status != 'enviada':  # Solo si es un cambio nuevo a enviada
                sede_admins = User.query.filter_by(role='admin_sede', sede_id=order.sede_id, is_active=True).all()
                for admin_user in sede_admins:
                    notification = Notification(
                        user_id=admin_user.id, 
                        message=f'📧 Orden enviada exitosamente. La orden N° {order.order_number} para {order.client_name} ha sido enviada al proveedor {order.provider.name}.', 
                        work_order_id=order.id
                    )
                    db.session.add(notification)
        elif order.status == 'aceptada' and old_status != 'aceptada':
            # Proveedor aceptó la orden - notificar PRINCIPALMENTE a la sede que la envió
            sede_admins = User.query.filter_by(role='admin_sede', sede_id=order.sede_id, is_active=True).all()
            for admin_user in sede_admins:
                notification = Notification(
                    user_id=admin_user.id, 
                    message=f'✅ ¡Orden aceptada! El proveedor {order.provider.name} ha aceptado la orden N° {order.order_number} para {order.client_name}.', 
                    work_order_id=order.id
                )
                db.session.add(notification)
            
            # También notificar a administradores centrales (para monitoreo general)
            optica_users = User.query.filter(User.role.in_(['admin', 'asistente'])).all()
            for u in optica_users:
                notification = Notification(user_id=u.id, message=f'¡Orden aceptada! El proveedor {order.provider.name} ha aceptado la orden N° {order.order_number} para {order.client_name}.', work_order_id=order.id)
                db.session.add(notification)
        elif order.status == 'rechazada' and old_status != 'rechazada':
            # Proveedor rechazó la orden - notificar a la sede que la envió
            sede_admins = User.query.filter_by(role='admin_sede', sede_id=order.sede_id, is_active=True).all()
            for admin_user in sede_admins:
                notification = Notification(
                    user_id=admin_user.id, 
                    message=f'⚠️ Orden rechazada N° {order.order_number} para {order.client_name}. Razón: {order.rejection_reason}. Puede hacer ajustes y reenviar la orden.', 
                    work_order_id=order.id
                )
                db.session.add(notification)
            
            # También notificar a administradores centrales
            optica_users = User.query.filter(User.role.in_(['admin', 'asistente'])).all()
            for u in optica_users:
                notification = Notification(user_id=u.id, message=f'⚠️ Orden rechazada. El proveedor {order.provider.name} ha rechazado la orden N° {order.order_number} para {order.client_name}. Razón: {order.rejection_reason}', work_order_id=order.id)
                db.session.add(notification)
        elif order.status == 'en_proceso' and old_status != 'en_proceso':
            # Proveedor inició el trabajo - notificar PRINCIPALMENTE a la sede que la envió
            sede_admins = User.query.filter_by(role='admin_sede', sede_id=order.sede_id, is_active=True).all()
            for admin_user in sede_admins:
                notification = Notification(
                    user_id=admin_user.id, 
                    message=f'🔧 Trabajo iniciado. El proveedor {order.provider.name} ha iniciado el trabajo en la orden N° {order.order_number} para {order.client_name}.', 
                    work_order_id=order.id
                )
                db.session.add(notification)
            
            # También notificar a administradores centrales
            optica_users = User.query.filter(User.role.in_(['admin', 'asistente'])).all()
            for u in optica_users:
                notification = Notification(user_id=u.id, message=f'🔧 Trabajo iniciado. El proveedor {order.provider.name} ha iniciado el trabajo en la orden N° {order.order_number} para {order.client_name}.', work_order_id=order.id)
                db.session.add(notification)
        elif order.status == 'devuelta_proveedor' and old_status != 'devuelta_proveedor':
            # Proveedor terminó el trabajo - notificar PRINCIPALMENTE a la sede que la envió
            sede_admins = User.query.filter_by(role='admin_sede', sede_id=order.sede_id, is_active=True).all()
            for admin_user in sede_admins:
                notification = Notification(
                    user_id=admin_user.id, 
                    message=f'✅ ¡Trabajo terminado! El proveedor {order.provider.name} ha terminado la orden N° {order.order_number} para {order.client_name}. Lista para recoger.', 
                    work_order_id=order.id
                )
                db.session.add(notification)
            
            # También notificar a administradores centrales
            optica_users = User.query.filter(User.role.in_(['admin', 'asistente'])).all()
            for u in optica_users:
                notification = Notification(user_id=u.id, message=f'✅ ¡Trabajo terminado! El proveedor {order.provider.name} ha terminado la orden N° {order.order_number} para {order.client_name}. Lista para recoger.', work_order_id=order.id)
                db.session.add(notification)
        elif order.status == 'recibida_optica' and old_status != 'recibida_optica':
            # Óptica recibió el trabajo - notificar al proveedor
            provider_user = User.query.filter_by(provider_id=order.provider_id, role='proveedor').first()
            if provider_user:
                notification = Notification(user_id=provider_user.id, message=f'La óptica ha recibido la orden N° {order.order_number} de {order.client_name}.', work_order_id=order.id)
                db.session.add(notification)
        elif order.status == 'finalizada' and old_status != 'finalizada':
            # Notificar al proveedor (si es relevante, depende del flujo)
            pass

        db.session.commit()
        flash(f'Estado de la orden N° {order.order_number} actualizado a "{order.status}".', 'success')
        return redirect(url_for('main.view_order', order_id=order.id))

    return render_template('ordenes/update_status.html', title=f'Actualizar Estado de Orden {order.order_number}', form=form, order=order)

# --- Sistema de Gestión de Pagos que implementé ---
@bp.route('/order/<int:order_id>/payment/new', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'asistente', 'admin_sede')
def add_payment(order_id):
    order = WorkOrder.query.get_or_404(order_id)
    
    # Verifico permisos para admin_sede: solo puede agregar pagos a órdenes de su sede
    if current_user.role == 'admin_sede':
        if order.sede_id != current_user.sede_id:
            flash('No tienes permisos para registrar pagos de órdenes de otras sedes.', 'danger')
            return redirect(url_for('main.list_orders'))
    
    form = PaymentForm()
    if form.validate_on_submit():
        support_filename = None
        if form.support_file.data:
            # Valido archivo de forma segura
            validation_errors, validated_filename = validate_file_upload(form.support_file.data)
            
            if validation_errors:
                for error in validation_errors:
                    flash(error, 'error')
                return render_template('pagos/add_payment.html', form=form, order=order, title='Registrar Pago')
            
            # Guardar archivo validado
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], validated_filename)
            try:
                form.support_file.data.save(filepath)
                support_filename = validated_filename
            except Exception as e:
                flash(f'Error al guardar el archivo: {str(e)}', 'error')
                return render_template('pagos/add_payment.html', form=form, order=order, title='Registrar Pago')

        payment = Payment(
            amount=form.amount.data,
            description=form.description.data,
            support_file=support_filename,
            work_order_id=order.id,
            provider_id=order.provider_id,
            registered_by_user_id=current_user.id
        )
        db.session.add(payment)

        # Actualizar el estado de pago de la orden
        # Incluimos el pago recién creado en el cálculo (sumar existente + nuevo)
        existing_paid = db.session.query(db.func.sum(Payment.amount)).filter_by(work_order_id=order.id).scalar() or 0
        total_paid_for_order = existing_paid + (payment.amount or 0)
        if total_paid_for_order >= (order.total_amount or 0):
            order.payment_status = 'pagada'
        elif total_paid_for_order > 0:
            order.payment_status = 'parcialmente_pagada'
        else:
            order.payment_status = 'pendiente'

        # Notificar al proveedor sobre el pago
        provider_user = User.query.filter_by(provider_id=order.provider_id, role='proveedor').first()
        if provider_user:
            notification = Notification(
                user_id=provider_user.id,
                message=f'¡Se ha registrado un pago de ${payment.amount} para la orden N° {order.order_number}!',
                work_order_id=order.id
            )
            db.session.add(notification)

        db.session.commit()
        flash(f'Pago de ${payment.amount} registrado para la orden N° {order.order_number}.', 'success')
        return redirect(url_for('main.view_order', order_id=order.id))
    return render_template('pagos/add_payment.html', title=f'Registrar Pago para Orden {order.order_number}', form=form, order=order)

@bp.route('/payments/pending', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'asistente', 'admin_sede')
def list_pending_payments():
    # Query base: órdenes que no están completamente pagadas
    query = WorkOrder.query.filter(WorkOrder.payment_status.in_(['pendiente', 'parcialmente_pagada']))
    
    # Filtrar por sede si es admin_sede
    if current_user.role == 'admin_sede':
        query = query.filter_by(sede_id=current_user.sede_id)
    
    # Obtengo proveedores únicos que tienen órdenes pendientes
    orders_with_providers = query.filter(WorkOrder.provider_id.isnot(None)).all()
    provider_ids = {order.provider_id for order in orders_with_providers}
    providers = Provider.query.filter(Provider.id.in_(provider_ids)).order_by(Provider.name).all() if provider_ids else []
    
    # Creo formulario con proveedores filtrados
    form = PendingPaymentsFilterForm(providers=providers)
    
    # Variables para el template
    filtered_provider = None
    
    if request.method == 'POST' and form.validate_on_submit():
        if form.provider_id.data and form.provider_id.data != 0: # 0 representa "Todos los Proveedores"
            query = query.filter_by(provider_id=form.provider_id.data)
            # Obtengo el nombre del proveedor para mostrar en el template
            filtered_provider = Provider.query.get(form.provider_id.data)
        
    pending_orders = query.order_by(WorkOrder.created_at.desc()).all()
    
    return render_template('pagos/pending_payments.html', 
                         title='Órdenes Pendientes de Pago', 
                         orders=pending_orders, 
                         form=form,
                         filtered_provider=filtered_provider)

# Ruta para ver el archivo de soporte de pago
@bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    # Asegurarse de que el usuario tenga permiso para ver el archivo
    # Por ahora, cualquier usuario logeado puede verlo. Podrías añadir más lógica.
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


# --- Administración de Usuarios que desarrollé ---
@bp.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    users = User.query.order_by(User.username).all()
    return render_template('admin/users_list.html', title='Administrar Usuarios', users=users)

@bp.route('/admin/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(original_user=user, obj=user) # obj pre-pobla el formulario
    if form.validate_on_submit():
        form.populate_obj(user)
        # La asignación de provider_id solo si el rol es proveedor
        if user.role == 'proveedor' and form.provider_id.data:
            user.provider_id = form.provider_id.data
        elif user.role != 'proveedor':
            user.provider_id = None # Si cambia de rol, desasociar proveedor
        db.session.commit()
        flash(f'Usuario {user.username} actualizado exitosamente.', 'success')
        return redirect(url_for('main.admin_users'))
    return render_template('admin/edit_user.html', title=f'Editar Usuario: {user.username}', form=form, user=user)

@bp.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # No permitir que el admin se elimine a sí mismo
    if user.id == current_user.id:
        flash('No puedes eliminar tu propia cuenta.', 'danger')
        return redirect(url_for('main.admin_users'))
    
    # Verifico si el usuario tiene órdenes asociadas
    orders_count = WorkOrder.query.filter_by(created_by_user_id=user.id).count()
    if orders_count > 0:
        flash(f'No se puede eliminar el usuario {user.username} porque tiene {orders_count} órdenes asociadas.', 'warning')
        return redirect(url_for('main.admin_users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuario {username} eliminado exitosamente.', 'success')
    return redirect(url_for('main.admin_users'))

# --- Sistema de Reportes que implementé ---
@bp.route('/reports')
@login_required
@role_required('admin', 'asistente')
def reports():
    """Página de reportes - Muestra dashboard administrativo directamente para admin"""
    if current_user.role == 'admin':
        # Para administradores, mostrar el dashboard completo directamente
        return redirect(url_for('main.admin_dashboard'))
    else:
        # Para asistentes, mostrar página básica de reportes
        return render_template('reports/reports.html', title='Reportes')

# --- Sistema de Notificaciones que desarrollé ---
@bp.route('/notifications')
@login_required
def view_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(20).all()
    # Marcar todas las notificaciones no leídas como leídas al verlas
    for notif in notifications:
        if not notif.is_read:
            notif.is_read = True
    db.session.commit()
    return render_template('notifications/list.html', title='Mis Notificaciones', notifications=notifications)

@bp.route('/notification/mark_read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        flash('No tienes permiso para marcar esta notificación.', 'danger')
        return redirect(url_for('main.view_notifications'))
    
    notification.is_read = True
    db.session.commit()
    flash('Notificación marcada como leída.', 'success')
    return redirect(request.referrer or url_for('main.view_notifications')) # Redirige a la página anterior o a la lista de notificaciones

# --- Sistema de Mensajería Interna que implementé ---
@bp.route('/messages/send', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'asistente')
def send_sede_message():
    from app.forms import SedeMessageForm
    from app.models import SedeMessage
    
    form = SedeMessageForm()
    if form.validate_on_submit():
        try:
            # Determinar si es mensaje global o específico
            is_global = form.sede_id.data == 0
            sede_id = None if is_global else form.sede_id.data
            
            message = SedeMessage(
                title=form.title.data,
                message=form.message.data,
                sender_id=current_user.id,
                sede_id=sede_id,
                is_global=is_global,
                priority=form.priority.data,
                expires_at=form.expires_at.data
            )
            
            db.session.add(message)
            db.session.commit()
            
            # Obtengo nombre de destino para el mensaje de confirmación
            if is_global:
                destination = "todas las sedes"
            else:
                sede = Sede.query.get(sede_id)
                destination = f"sede {sede.name} - {sede.city}" if sede else "sede seleccionada"
            
            flash(f'Mensaje "{form.title.data}" enviado exitosamente a {destination}.', 'success')
            return redirect(url_for('main.list_sede_messages'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al enviar el mensaje: {str(e)}', 'error')
    else:
        # Si el formulario no es válido, mostrar los errores
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Error en {field}: {error}', 'error')
    
    return render_template('messages/send.html', title='Enviar Mensaje a Sedes', form=form)

@bp.route('/messages/list')
@login_required
@role_required('admin', 'asistente')
def list_sede_messages():
    from app.models import SedeMessage
    from datetime import datetime
    
    messages = SedeMessage.query.filter_by(is_active=True).order_by(SedeMessage.created_at.desc()).all()
    current_date = datetime.now().date()
    
    # Convertir mensajes a diccionarios para JSON
    messages_dict = []
    for msg in messages:
        msg_dict = {
            'id': msg.id,
            'title': msg.title,
            'message': msg.message,
            'priority': msg.priority,
            'is_global': msg.is_global,
            'created_at': msg.created_at.isoformat(),
            'expires_at': msg.expires_at.isoformat() if msg.expires_at else None,
            'sender': {
                'id': msg.sender.id,
                'username': msg.sender.username
            },
            'sede': {
                'id': msg.sede.id if msg.sede else None,
                'name': msg.sede.name if msg.sede else None,
                'city': msg.sede.city if msg.sede else None
            } if msg.sede else None
        }
        messages_dict.append(msg_dict)
    
    return render_template('messages/list.html', 
                         title='Mensajes Enviados', 
                         messages=messages, 
                         messages_json=messages_dict,
                         current_date=current_date)

@bp.route('/messages/my')
@login_required
def my_sede_messages():
    from app.models import SedeMessage
    from datetime import datetime
    
    # Mensajes para mi sede específica o mensajes globales
    if current_user.role == 'admin_sede' and current_user.sede_id:
        messages = SedeMessage.query.filter(
            db.or_(
                SedeMessage.sede_id == current_user.sede_id,
                SedeMessage.is_global == True
            ),
            SedeMessage.is_active == True
        ).order_by(SedeMessage.created_at.desc()).all()
    else:
        # Para admin/asistente mostrar todos los mensajes
        messages = SedeMessage.query.filter_by(is_active=True).order_by(SedeMessage.created_at.desc()).all()
    
    current_date = datetime.now().date()
    
    # Convertir mensajes a diccionarios para JSON
    messages_dict = []
    for msg in messages:
        msg_dict = {
            'id': msg.id,
            'title': msg.title,
            'message': msg.message,
            'priority': msg.priority,
            'is_global': msg.is_global,
            'created_at': msg.created_at.isoformat(),
            'expires_at': msg.expires_at.isoformat() if msg.expires_at else None,
            'sender': {
                'id': msg.sender.id,
                'username': msg.sender.username
            },
            'sede': {
                'id': msg.sede.id if msg.sede else None,
                'name': msg.sede.name if msg.sede else None,
                'city': msg.sede.city if msg.sede else None
            } if msg.sede else None
        }
        messages_dict.append(msg_dict)
    
    return render_template('messages/my_messages.html', 
                         title='Mis Mensajes', 
                         messages=messages, 
                         messages_json=messages_dict,
                         current_date=current_date)

@bp.route('/messages/archive/<int:message_id>')
@login_required
@role_required('admin', 'asistente')
def archive_sede_message(message_id):
    from app.models import SedeMessage
    
    message = SedeMessage.query.get_or_404(message_id)
    
    try:
        message.is_active = False
        db.session.commit()
        flash(f'Mensaje "{message.title}" archivado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al archivar el mensaje: {str(e)}', 'error')
    
    return redirect(url_for('main.list_sede_messages'))

@bp.route('/change-my-password', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def change_my_password():
    """Cambiar mi propia contraseña - Solo para admin"""
    form = ChangePasswordForm(current_user)
    if form.validate_on_submit():
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Tu contraseña ha sido cambiada exitosamente.', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/change_my_password.html', 
                         title='Cambiar Mi Contraseña', 
                         form=form)

@bp.context_processor
def inject_notifications():
    # Función para inyectar notificaciones no leídas en todas las plantillas
    if current_user.is_authenticated:
        unread_notifications_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        latest_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()
        
        # Agregar mensajes de sede no leídos
        sede_messages_count = 0
        if current_user.role == 'admin_sede' and current_user.sede_id:
            from app.models import SedeMessage
            sede_messages_count = SedeMessage.query.filter(
                db.or_(
                    SedeMessage.sede_id == current_user.sede_id,
                    SedeMessage.is_global == True
                ),
                SedeMessage.is_active == True
            ).count()
        
        return dict(
            unread_notifications_count=unread_notifications_count, 
            latest_notifications=latest_notifications,
            sede_messages_count=sede_messages_count
        )
    return dict(unread_notifications_count=0, latest_notifications=[])

@bp.route('/order/resubmit/<int:order_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'asistente', 'admin_sede')
def resubmit_order(order_id):
    order = WorkOrder.query.get_or_404(order_id)
    
    # Verifico que la orden esté en estado rechazada
    if order.status != 'rechazada':
        flash('Solo se pueden reenviar órdenes que han sido rechazadas.', 'danger')
        return redirect(url_for('main.view_order', order_id=order_id))
    
    # Verifico permisos para admin_sede: solo puede reenviar órdenes de su sede
    if current_user.role == 'admin_sede':
        if order.sede_id != current_user.sede_id:
            flash('No tienes permisos para reenviar órdenes de otras sedes.', 'danger')
            return redirect(url_for('main.list_orders'))
    
    form = WorkOrderForm(current_user=current_user, obj=order)
    if form.validate_on_submit():
        # Validación adicional para admin_sede: no puede cambiar la sede
        if current_user.role == 'admin_sede':
            if form.sede_id.data != current_user.sede_id:
                flash('No puedes cambiar la sede de origen de la orden.', 'danger')
                return render_template('ordenes/resubmit.html', title=f'Reenviar Orden {order.order_number}', form=form, order=order)
        
        # Actualizar los datos de la orden
        form.populate_obj(order)
        
        # Cambiar estado a enviada y registrar el reenvío
        order.status = 'enviada'
        order.resubmitted_at = datetime.utcnow()
        order.resubmitted_by_user_id = current_user.id
        
        # Agregar comentario sobre el reenvío
        if order.comments is None:
            order.comments = ''
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        order.comments += f"\n[{timestamp}] {current_user.username} reenvió la orden después del rechazo. Ajustes realizados."
        
        db.session.flush()  # Para asegurar que order.id esté disponible
        
        # Notificar al proveedor sobre el reenvío
        provider_user = User.query.filter_by(provider_id=order.provider_id, role='proveedor').first()
        if provider_user:
            notification = Notification(
                user_id=provider_user.id,
                message=f'🔄 Orden reenviada N° {order.order_number} para {order.client_name}. Se han realizado ajustes según su solicitud. Por favor revise nuevamente.',
                work_order_id=order.id
            )
            db.session.add(notification)
        
        db.session.commit()
        flash(f'Orden N° {order.order_number} reenviada exitosamente al proveedor con los ajustes realizados.', 'success')
        return redirect(url_for('main.view_order', order_id=order.id))
    
    return render_template('ordenes/resubmit.html', title=f'Reenviar Orden {order.order_number}', form=form, order=order)

# Ruta de prueba para verificar notificaciones
@bp.route('/debug/notifications')
@login_required
def debug_notifications():
    if current_user.role not in ['admin', 'admin_sede']:
        flash('Sin permisos para esta vista de debug.', 'danger')
        return redirect(url_for('main.index'))
    
    # Obtengo notificaciones del usuario actual
    user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(10).all()
    
    debug_info = {
        'user_id': current_user.id,
        'username': current_user.username,
        'role': current_user.role,
        'sede_id': current_user.sede_id,
        'total_notifications': len(user_notifications),
        'unread_count': Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    }
    
    return f"""
    <h2>DEBUG: Notificaciones para {current_user.username}</h2>
    <p><strong>ID Usuario:</strong> {debug_info['user_id']}</p>
    <p><strong>Rol:</strong> {debug_info['role']}</p>
    <p><strong>Sede ID:</strong> {debug_info['sede_id']}</p>
    <p><strong>Total notificaciones:</strong> {debug_info['total_notifications']}</p>
    <p><strong>No leídas:</strong> {debug_info['unread_count']}</p>
    
    <h3>Últimas 10 notificaciones:</h3>
    <ul>
    {''.join([f"<li>ID: {n.id} | Leída: {n.is_read} | Fecha: {n.created_at} | Orden: {n.work_order_id}<br>Mensaje: {n.message[:100]}...</li>" for n in user_notifications])}
    </ul>
    
    <a href="/index">Volver al inicio</a>
    """

# --- API para manejo de sesiones que desarrollé ---

@bp.route('/api/session/status')
@login_required
@csrf.exempt
def session_status():
    """API para verificar el estado de la sesión"""
    from flask import session, jsonify, current_app
    from datetime import datetime
    
    last_activity = session.get('last_activity')
    if last_activity:
        last_activity_dt = datetime.fromisoformat(last_activity)
        time_since_activity = (datetime.now() - last_activity_dt).total_seconds()
        session_timeout = current_app.config['PERMANENT_SESSION_LIFETIME'].total_seconds()
        warning_time = current_app.config['SESSION_TIMEOUT_WARNING'].total_seconds()
        
        return jsonify({
            'authenticated': True,
            'time_since_activity': time_since_activity,
            'session_timeout': session_timeout,
            'warning_time': warning_time,
            'time_remaining': session_timeout - time_since_activity,
            'should_warn': time_since_activity >= warning_time
        })
    
    return jsonify({'authenticated': False})

@bp.route('/api/session/extend', methods=['POST'])
@login_required
@csrf.exempt
def extend_session():
    """API para extender la sesión del usuario"""
    from flask import session, jsonify
    from datetime import datetime
    
    session['last_activity'] = datetime.now().isoformat()
    session.permanent = True
    
    return jsonify({
        'success': True,
        'message': 'Sesión extendida exitosamente',
        'extended_at': session['last_activity']
    })