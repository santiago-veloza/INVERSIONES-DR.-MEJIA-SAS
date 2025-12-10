#!/usr/bin/env python
from backend.app import create_app, db
from backend.app.models import Sede, User

app = create_app()

with app.app_context():
    print("=== VERIFICANDO SEDES EN LA BASE DE DATOS ===")
    
    # Listar todas las sedes
    sedes = Sede.query.all()
    print(f"Total de sedes encontradas: {len(sedes)}")
    
    for sede in sedes:
        print(f"- ID: {sede.id}, Nombre: {sede.name}, Ciudad: {sede.city}, Activa: {sede.is_active}")
    
    # Si no hay sedes, crear algunas de prueba
    if len(sedes) == 0:
        print("\n=== CREANDO SEDES DE PRUEBA ===")
        
        sedes_prueba = [
            {
                'name': 'Sede Principal Villavicencio',
                'department': 'Meta',
                'city': 'Villavicencio',
                'address': 'Calle Principal #123',
                'phone': '608-123-4567',
                'email': 'villavicencio@opticasdrmejia.com',
                'manager': 'Juan Pérez'
            },
            {
                'name': 'Sede Yopal',
                'department': 'Casanare',
                'city': 'Yopal',
                'address': 'Carrera 15 #45-67',
                'phone': '608-234-5678',
                'email': 'yopal@opticasdrmejia.com',
                'manager': 'María González'
            },
            {
                'name': 'Sede San José del Guaviare',
                'department': 'Meta',
                'city': 'San José del Guaviare',
                'address': 'Avenida Principal #89',
                'phone': '608-345-6789',
                'email': 'guaviare@opticasdrmejia.com',
                'manager': 'Carlos Rodríguez'
            }
        ]
        
        for sede_data in sedes_prueba:
            sede = Sede(**sede_data)
            db.session.add(sede)
            print(f"Creada sede: {sede_data['name']} - {sede_data['city']}")
        
        db.session.commit()
        print("Sedes de prueba creadas exitosamente!")
        
        # Verificar las sedes creadas
        sedes = Sede.query.all()
        print(f"\nTotal de sedes después de crear: {len(sedes)}")
        for sede in sedes:
            print(f"- ID: {sede.id}, Nombre: {sede.name}, Ciudad: {sede.city}")
    
    print("\n=== VERIFICANDO USUARIOS DE SEDE ===")
    usuarios_sede = User.query.filter_by(role='admin_sede').all()
    print(f"Total de usuarios admin_sede: {len(usuarios_sede)}")
    
    for user in usuarios_sede:
        print(f"- Usuario: {user.username}, Sede ID: {user.sede_id}, Activo: {user.is_active}")
    
    print("\n=== VERIFICACIÓN COMPLETA ===")