"""Carga datos de ejemplo: sedes, proveedores y 20 órdenes que recorren cada estado del flujo.

Uso:  python seed_demo.py            (agrega los datos si no existen)
      python seed_demo.py --reset    (borra primero las órdenes 100001-100020 y las vuelve a crear)
Las órdenes de ejemplo usan consecutivos numéricos 100001-100020 en order_number.
"""
import sys
from datetime import datetime, timedelta

from app import app
from backend.app.models import (db, User, Sede, Provider, WorkOrder, Payment,
                                Notification, SedeMessage)

SEDES = [
    dict(name='Óptica Dr. Mejía Villavicencio', department='Meta', city='Villavicencio',
         address='Cra 31 # 38-20 Centro', phone='3101112233', email='villavicencio@opticasdrmejia.com', manager='Laura Gómez'),
    dict(name='Óptica Dr. Mejía Yopal', department='Casanare', city='Yopal',
         address='Calle 9 # 20-15', phone='3102223344', email='yopal@opticasdrmejia.com', manager='Carlos Rincón'),
    dict(name='Óptica Dr. Mejía San José', department='Guaviare', city='San José del Guaviare',
         address='Av. Panamericana # 5-40', phone='3103334455', email='sanjose@opticasdrmejia.com', manager='Marta Ruiz'),
]

CLIENTES = [
    ('María Fernanda Torres', '40123456'), ('Juan Pablo Cárdenas', '86054321'), ('Luz Marina Pardo', '21345678'),
    ('Andrés Felipe Rojas', '1121850432'), ('Carolina Suárez', '1010234567'), ('Pedro Antonio Silva', '17312456'),
    ('Diana Marcela León', '40987654'), ('Hernán Darío Vega', '79456123'), ('Sandra Milena Cruz', '52345987'),
    ('Jorge Eliécer Mora', '11223344'), ('Paola Andrea Ibáñez', '1121900345'), ('Luis Carlos Beltrán', '86123456'),
    ('Ana Lucía Peña', '40765432'), ('Camilo Ernesto Díaz', '1121877654'), ('Rosa Elena Quintero', '21987345'),
    ('Mauricio Salazar', '80234567'), ('Gloria Patricia Nieto', '40345678'), ('Iván Darío Castro', '86987123'),
    ('Yaneth Patricia Ortiz', '40567890'), ('Fabián Alberto Gil', '1121823456'),
]

LENTES = [
    ('Progresivo', 'Progresivo digital Blue Cut'), ('Monofocal', 'Monofocal antirreflejo'),
    ('Bifocal', 'Bifocal flat-top fotocromático'), ('Progresivo', 'Progresivo fotocromático'),
    ('Monofocal', 'Monofocal policarbonato filtro azul'),
]
MONTURAS = ['Acetato negro', 'Metálica dorada', 'Al aire (rimless)', 'Acetato carey', 'Metálica plateada']
EMPRESAS = ['Particular', 'Sanitas EPS', 'Convenio Ecopetrol', 'Particular', 'Coomeva']

FIRST_NUMBER = 100001
DEMO_NUMBERS = [str(FIRST_NUMBER + i) for i in range(20)]

now = datetime.utcnow()


def ago(days, hours=0):
    return now - timedelta(days=days, hours=hours)


# (estado, dict de variaciones) — 20 órdenes, cada estado del flujo representado
FLUJO = [
    # --- pendiente_envio ---
    ('pendiente_envio', dict(creada=0, admin_review=True, nota='Esperando que el admin complete tipo de lente')),
    ('pendiente_envio', dict(creada=1, nota='Orden lista para enviar al proveedor')),
    # --- enviada ---
    ('enviada', dict(creada=2, prov=1, nota='Enviada, el proveedor aún no responde')),
    ('enviada', dict(creada=3, prov=2, nota='Enviada al proveedor 2')),
    # --- rechazada y reenviada ---
    ('rechazada', dict(creada=5, prov=1, rech=1, motivo='Fórmula ilegible, falta el eje del ojo izquierdo')),
    ('enviada', dict(creada=6, prov=1, rech=1, motivo='Falta altura de montaje', reenviada=1, nota='Reenviada tras corregir datos')),
    # --- aceptada ---
    ('aceptada', dict(creada=4, prov=1, aceptada=2, nota='Aceptada dentro del plazo')),
    ('aceptada', dict(creada=14, prov=2, aceptada=10, nota='Aceptada hace 10 días: VENCIDA')),
    # --- en_proceso ---
    ('en_proceso', dict(creada=8, prov=1, aceptada=5, nota='En laboratorio, tallado en curso')),
    ('en_proceso', dict(creada=9, prov=2, aceptada=6, nota='En montaje; vence mañana')),
    ('en_proceso', dict(creada=18, prov=1, aceptada=12, nota='En proceso con 5 días de retraso: VENCIDA')),
    # --- devuelta_proveedor ---
    ('devuelta_proveedor', dict(creada=12, prov=1, aceptada=9, nota='Devuelta: lente con rayón, requiere repetición')),
    ('devuelta_proveedor', dict(creada=13, prov=2, aceptada=9, nota='Devuelta: error de eje en la fórmula')),
    # --- recibida_optica ---
    ('recibida_optica', dict(creada=11, prov=1, aceptada=9, pago='parcial', nota='Llegó a la óptica, falta entregar al paciente')),
    ('recibida_optica', dict(creada=10, prov=2, aceptada=8, pago='pendiente', nota='Recibida en sede, pago pendiente')),
    # --- finalizada ---
    ('finalizada', dict(creada=25, prov=1, aceptada=22, pago='pagada', nota='Entregada al paciente')),
    ('finalizada', dict(creada=22, prov=2, aceptada=19, pago='parcial', nota='Entregada; resta saldo por pagar al proveedor')),
    ('finalizada', dict(creada=20, prov=1, aceptada=17, pago='pendiente', nota='Entregada; pago aún no registrado')),
    # --- cancelada ---
    ('cancelada', dict(creada=15, prov=1, nota='Cancelada: el paciente desistió de la compra')),
    ('cancelada', dict(creada=7, nota='Cancelada antes de enviar: orden duplicada')),
]


def get_or_create_sedes():
    sedes = []
    for i, data in enumerate(SEDES, start=1):
        sede = Sede.query.filter_by(name=data['name']).first()
        if not sede:
            sede = Sede(is_active=True, display_order=i, **data)
            db.session.add(sede)
            db.session.flush()
        user = User.query.filter_by(username=f'sede_{sede.id}').first()
        if not user:
            user = User(username=f'sede_{sede.id}', email=f'sede{sede.id}@opticasdrmejia.com',
                        role='admin_sede', sede_id=sede.id, is_active=True)
            user.set_password(app.config['SEDE_SHARED_PASSWORD'])
            db.session.add(user)
            db.session.flush()
        sedes.append((sede, user))
    return sedes


def get_or_create_providers():
    p1 = Provider.query.first()
    if not p1:
        p1 = Provider(nit='900111222-1', razon_social='Ópticas del Valle S.A.S.', name='Ópticas del Valle',
                      contact_person='Camila Reyes', phone='3201110000', email='contacto@opticasdelvalle.com',
                      address='Cali, Valle del Cauca')
        db.session.add(p1)
        db.session.flush()
    p2 = Provider.query.filter_by(nit='900333444-5').first()
    if not p2:
        p2 = Provider(nit='900333444-5', razon_social='Laboratorio Visión Andina Ltda.', name='Visión Andina',
                      contact_person='Ricardo Pineda', phone='3209998888', email='ventas@visionandina.com',
                      address='Bogotá D.C.')
        db.session.add(p2)
        db.session.flush()
    if not User.query.filter_by(username='proveedor2').first():
        u = User(username='proveedor2', email='proveedor2@visionandina.com', role='proveedor',
                 provider_id=p2.id, is_active=True)
        u.set_password('Proveedor2024')
        db.session.add(u)
    return p1, p2


def seed():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        sys.exit('No hay usuario admin. Ejecuta create_admin.py primero.')

    if '--reset' in sys.argv:
        ids = [o.id for o in WorkOrder.query.filter(WorkOrder.order_number.in_(DEMO_NUMBERS)).all()]
        if ids:
            Payment.query.filter(Payment.work_order_id.in_(ids)).delete(synchronize_session=False)
            Notification.query.filter(Notification.work_order_id.in_(ids)).delete(synchronize_session=False)
            WorkOrder.query.filter(WorkOrder.id.in_(ids)).delete(synchronize_session=False)
            db.session.commit()
            print(f'Borradas {len(ids)} órdenes de ejemplo previas')
    elif WorkOrder.query.filter(WorkOrder.order_number.in_(DEMO_NUMBERS)).count():
        sys.exit('Ya existen órdenes 100001-100020. Usa --reset para recrearlas.')

    sedes = get_or_create_sedes()
    providers = {1: None, 2: None}
    providers[1], providers[2] = get_or_create_providers()
    admin_user = admin

    for n, (estado, v) in enumerate(FLUJO):
        sede, sede_user = sedes[n % len(sedes)]
        cliente, cc = CLIENTES[n]
        clase, tipo = LENTES[n % len(LENTES)]
        prov = providers[v['prov']] if v.get('prov') else None
        creada = ago(v['creada'])
        total = float(60000 + (n % 5) * 25000)
        venta = total * 2.4
        review = v.get('admin_review', False)

        o = WorkOrder(
            order_number=DEMO_NUMBERS[n],
            receipt_number=f'RC-{1000 + n}',
            orden_laboratorio=f'LAB-{5000 + n}' if prov else None,
            ciudad_municipio=sede.city,
            client_name=cliente, client_cc=cc, client_phone=f'31{20000000 + n * 137:08d}'[:10],
            empresa_convenio=EMPRESAS[n % len(EMPRESAS)],
            lens_class=clase, lens_type=None if review else tipo, lens_type_asesor=tipo,
            frame_type=MONTURAS[n % len(MONTURAS)],
            pending_admin_review=review,
            admin_completed_at=None if review else creada + timedelta(hours=3),
            admin_completed_by_user_id=None if review else admin_user.id,
            formula_od=f'-{1 + (n % 4)}.25 -0.50 x {10 + n * 5 % 170}',
            formula_oi=f'-{1 + (n % 3)}.00 -0.75 x {20 + n * 7 % 160}',
            formula_add='+1.50' if clase != 'Monofocal' else None,
            formula_dp_alt=f'DP 62/{30 + n % 4}  ALT {18 + n % 5}',
            observations=v.get('nota'),
            created_at=creada, status=estado, comments=v.get('nota'),
            provider_id=prov.id if prov else None,
            sede_id=sede.id, created_by_user_id=sede_user.id,
            total_amount=total, sale_price=venta, payment_status='pendiente',
        )
        if v.get('aceptada') is not None:
            o.accepted_at = ago(v['aceptada'])
            o.delivery_deadline = o.calculate_delivery_deadline()
            o.check_if_overdue()
        if v.get('rech'):
            o.rejection_count = v['rech']
            o.rejection_reason = v['motivo']
        if v.get('reenviada'):
            o.resubmitted_at = ago(v['reenviada'])
            o.resubmitted_by_user_id = sede_user.id
        db.session.add(o)
        db.session.flush()

        # Pagos según el estado de pago de la orden
        pago = v.get('pago')
        if pago == 'pagada':
            monto = [total]
        elif pago == 'parcial':
            monto = [round(total * 0.4)]
        else:
            monto = []
        for m in monto:
            db.session.add(Payment(amount=m, payment_date=ago(max(v['creada'] - 5, 0)),
                                   description='Pago registrado desde datos de ejemplo',
                                   work_order_id=o.id, provider_id=prov.id, registered_by_user_id=admin_user.id))
        if pago:
            o.payment_status = {'pagada': 'pagada', 'parcial': 'parcialmente_pagada', 'pendiente': 'pendiente'}[pago]

        # Notificación para el actor al que le toca el siguiente paso
        destino = {'pendiente_envio': admin_user, 'enviada': None, 'rechazada': sede_user,
                   'devuelta_proveedor': sede_user, 'recibida_optica': sede_user, 'finalizada': sede_user,
                   'aceptada': sede_user, 'en_proceso': sede_user, 'cancelada': sede_user}[estado]
        if destino:
            db.session.add(Notification(user_id=destino.id, work_order_id=o.id, is_read=n % 3 == 0,
                                        message=f'Orden {o.order_number} ({cliente}): estado {estado}',
                                        created_at=creada + timedelta(hours=6)))

    db.session.add(SedeMessage(title='Bienvenidos al nuevo sistema',
                               message='Recuerden registrar cada orden con la fórmula completa.',
                               sender_id=admin_user.id, is_global=True, priority='normal'))
    db.session.add(SedeMessage(title='Órdenes vencidas',
                               message='Hay órdenes con retraso de entrega; contacten al proveedor.',
                               sender_id=admin_user.id, sede_id=sedes[0][0].id, priority='urgente'))
    db.session.commit()
    print('Listo: 20 órdenes de ejemplo creadas')


if __name__ == '__main__':
    with app.app_context():
        seed()
        from sqlalchemy import func
        for est, c in db.session.query(WorkOrder.status, func.count()).group_by(WorkOrder.status).order_by(func.count().desc()):
            print(f'  {est:20s} {c}')
