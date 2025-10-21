from flask import render_template, flash, redirect, url_for, request, current_app, send_from_directory, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from app import db, login_manager
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
import uuid # Para generar IDs únicos para órdenes
from datetime import datetime

# --- Decoradores para roles ---
def role_required(*roles):
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

# --- Rutas de Autenticación ---
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        # Validar que el usuario existe, password es correcto y está activo
        if user is None or not user.check_password(form.password.data) or not user.is_active:
            flash('Usuario o contraseña inválidos o cuenta inactiva.', 'danger')
            return redirect(url_for('main.login'))
        
        # Validar que el tipo de usuario seleccionado coincida con el rol del usuario
        user_type_selected = form.user_type.data
        
        if user_type_selected == 'central' and user.role not in ['admin', 'asistente']:
            flash('Este usuario no tiene acceso a Administración Central.', 'danger')
            return redirect(url_for('main.login'))
        elif user_type_selected == 'sede' and user.role != 'admin_sede':
            flash('Este usuario no es administrador de sede.', 'danger')
            return redirect(url_for('main.login'))
        elif user_type_selected == 'proveedor' and user.role != 'proveedor':
            flash('Este usuario no es proveedor.', 'danger')
            return redirect(url_for('main.login'))
        
        # Para administradores de sede, validar que se seleccionó una sede válida
        if user_type_selected == 'sede':
            sede_id = form.sede_id.data
            if not sede_id or sede_id == 0:
                flash('Debe seleccionar una sede.', 'danger')
                return redirect(url_for('main.login'))
            
            # Verificar que el usuario puede acceder a esta sede
            if user.sede_id and user.sede_id != sede_id:
                flash('No tiene permisos para acceder a esta sede.', 'danger')
                return redirect(url_for('main.login'))
            
            # Almacenar la sede seleccionada en la sesión
            from flask import session
            session['sede_seleccionada'] = sede_id
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        
        # Mensaje personalizado según el tipo de usuario
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
    return render_template('auth/login.html', title='Iniciar Sesión', form=form)

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

# --- Rutas del Panel de Control (Index) ---
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


# --- Dashboard Administrativo Detallado ---
@bp.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    """Dashboard completo para administrador central con estadísticas por sede"""
    from sqlalchemy import func, and_, extract
    from datetime import datetime, timedelta
    
    # Obtener mes actual
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Obtener todas las sedes
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


# --- API Endpoints para Dashboard ---
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


# --- Rutas de Proveedores (Admin y Asistente) ---
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
            # Crear el proveedor
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
            
            # Crear el usuario para el proveedor
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
    
    # Validaciones
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

# --- Rutas de Sedes ---
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
    
    if not name or not city:
        flash('Nombre y ciudad son campos obligatorios.', 'error')
        return redirect(url_for('main.list_sedes'))
    
    # Verificar si ya existe
    existing_sede = Sede.query.filter_by(name=name).first()
    if existing_sede:
        flash(f'Ya existe una sede con el nombre "{name}".', 'error')
        return redirect(url_for('main.list_sedes'))
    
    try:
        sede = Sede(
            name=name,
            city=city,
            address=address,
            phone=phone,
            manager=manager,
            is_active=True
        )
        db.session.add(sede)
        db.session.commit()
        flash(f'Sede "{name}" agregada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al agregar la sede: {str(e)}', 'error')
    
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
    
    # Verificar si ya existe otra sede con el mismo nombre (excluyendo la actual)
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
    
    # Verificar que la sede de la sesión coincida con la del usuario
    if sede_id != current_user.sede_id:
        sede_id = current_user.sede_id
        session['sede_seleccionada'] = sede_id
    
    # Obtener órdenes de la sede
    orders = WorkOrder.query.filter_by(sede_id=sede_id).all()
    sede = Sede.query.get(sede_id)
    
    if not sede:
        flash('Sede no encontrada.', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('pagos/sede_payments.html', title=f'Pagos - {sede.name}', orders=orders, sede=sede)

# --- Rutas de Órdenes de Trabajo ---
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
            sede_id=form.sede_id.data,
            provider_id=form.provider_id.data,
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
        db.session.commit()
        # Obtener nombre del proveedor de forma segura (por si la relación no está cargada)
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
    
    # Verificar permisos para admin_sede: solo puede editar órdenes de su sede
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
        # Asegurar que comments sea string antes de concatenar
        if order.comments is None:
            order.comments = ''
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        if form.comments.data:
            order.comments += f"\n[{timestamp}] {current_user.username} cambió el estado a '{order.status}'. Comentarios: {form.comments.data}"
        else:
            order.comments += f"\n[{timestamp}] {current_user.username} cambió el estado a '{order.status}'."
        db.session.commit()

        # Notificaciones automáticas según el flujo
        if order.status == 'enviada':
            # Notificar al proveedor cuando se le asigna
            provider_user = User.query.filter_by(provider_id=order.provider_id, role='proveedor').first()
            if provider_user:
                notification = Notification(user_id=provider_user.id, message=f'Nueva orden N° {order.order_number} enviada para {order.client_name}. Por favor revisa y acepta/rechaza.', work_order_id=order.id)
                db.session.add(notification)
        elif order.status == 'aceptada' and old_status != 'aceptada':
            # Proveedor aceptó la orden - notificar a la óptica
            optica_users = User.query.filter(User.role.in_(['admin', 'asistente'])).all()
            for u in optica_users:
                notification = Notification(user_id=u.id, message=f'¡Orden aceptada! El proveedor {order.provider.name} ha aceptado la orden N° {order.order_number} para {order.client_name}.', work_order_id=order.id)
                db.session.add(notification)
        elif order.status == 'rechazada' and old_status != 'rechazada':
            # Proveedor rechazó la orden - notificar a la óptica
            optica_users = User.query.filter(User.role.in_(['admin', 'asistente'])).all()
            for u in optica_users:
                notification = Notification(user_id=u.id, message=f'⚠️ Orden rechazada. El proveedor {order.provider.name} ha rechazado la orden N° {order.order_number} para {order.client_name}.', work_order_id=order.id)
                db.session.add(notification)
        elif order.status == 'en_proceso' and old_status != 'en_proceso':
            # Proveedor inició el trabajo - notificar a la óptica
            optica_users = User.query.filter(User.role.in_(['admin', 'asistente'])).all()
            for u in optica_users:
                notification = Notification(user_id=u.id, message=f'🔧 Trabajo iniciado. El proveedor {order.provider.name} ha iniciado el trabajo en la orden N° {order.order_number} para {order.client_name}.', work_order_id=order.id)
                db.session.add(notification)
        elif order.status == 'devuelta_proveedor' and old_status != 'devuelta_proveedor':
            # Proveedor terminó el trabajo - notificar a la óptica
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

# --- Rutas de Pagos ---
@bp.route('/order/<int:order_id>/payment/new', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'asistente')
def add_payment(order_id):
    order = WorkOrder.query.get_or_404(order_id)
    form = PaymentForm()
    if form.validate_on_submit():
        support_filename = None
        if form.support_file.data:
            filename = secure_filename(form.support_file.data.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            form.support_file.data.save(filepath)
            support_filename = unique_filename

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
@role_required('admin', 'asistente')
def list_pending_payments():
    form = PendingPaymentsFilterForm()
    
    # Query base: órdenes que no están completamente pagadas
    query = WorkOrder.query.filter(WorkOrder.payment_status.in_(['pendiente', 'parcialmente_pagada']))
    
    # Variables para el template
    filtered_provider = None
    
    if request.method == 'POST' and form.validate_on_submit():
        if form.provider_id.data and form.provider_id.data != 0: # 0 representa "Todos los Proveedores"
            query = query.filter_by(provider_id=form.provider_id.data)
            # Obtener el nombre del proveedor para mostrar en el template
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


# --- Rutas de Administración de Usuarios (Solo Admin) ---
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
    
    # Verificar si el usuario tiene órdenes asociadas
    orders_count = WorkOrder.query.filter_by(created_by_user_id=user.id).count()
    if orders_count > 0:
        flash(f'No se puede eliminar el usuario {user.username} porque tiene {orders_count} órdenes asociadas.', 'warning')
        return redirect(url_for('main.admin_users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuario {username} eliminado exitosamente.', 'success')
    return redirect(url_for('main.admin_users'))

# --- Rutas de Reportes ---
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

# --- Rutas de Notificaciones ---
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

# --- Rutas de Mensajes a Sedes ---
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
            
            # Obtener nombre de destino para el mensaje de confirmación
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