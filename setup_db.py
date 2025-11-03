#!/usr/bin/env python3
"""
🗄️ Script de inicialización de base de datos
Crea la base de datos y usuarios iniciales del sistema
"""

import os
import sys

# Agregar el directorio backend al path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

if __name__ == '__main__':
    try:
        print("🗄️ Inicializando base de datos...")
        print("=" * 50)
        
        # Importar los modelos y la aplicación
        from app import create_app, db
        from app.models import User, Provider
        
        # Crear la aplicación
        app = create_app()
        
        with app.app_context():
            # Crear todas las tablas
            db.create_all()
            print("✅ Tablas de base de datos creadas")
            
            # Verificar si ya existen usuarios
            if User.query.first():
                print("⚠️  Los usuarios ya existen en la base de datos")
                sys.exit(0)
            
            # Crear usuario administrador
            admin = User(
                username='admin',
                email='admin@inversiones.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Crear proveedores de prueba
            proveedores_data = [
                {'nit': '900123456-1', 'razon_social': 'Ópticas del Valle S.A.S.', 'name': 'Ópticas del Valle', 'contact': 'Carlos López', 'email': 'contacto@opticasvalle.com', 'phone': '555-0101'},
                {'nit': '900234567-2', 'razon_social': 'Lentes Premium Ltda.', 'name': 'Lentes Premium', 'contact': 'Ana García', 'email': 'ventas@lentespremium.com', 'phone': '555-0102'},
                {'nit': '900345678-3', 'razon_social': 'Visión Total S.A.S.', 'name': 'Visión Total', 'contact': 'Miguel Torres', 'email': 'info@visiontotal.com', 'phone': '555-0103'}
            ]
            
            for i, prov_data in enumerate(proveedores_data, 1):
                # Crear proveedor
                provider = Provider(
                    nit=prov_data['nit'],
                    razon_social=prov_data['razon_social'],
                    name=prov_data['name'],
                    contact_person=prov_data['contact'],
                    email=prov_data['email'],
                    phone=prov_data['phone'],
                    address=f'Dirección del proveedor {i}'
                )
                db.session.add(provider)
                db.session.flush()  # Para obtener el ID
                
                # Crear usuario para el proveedor
                user_provider = User(
                    username=f'proveedor{i}',
                    email=prov_data['email'],
                    role='proveedor',
                    provider_id=provider.id
                )
                user_provider.set_password(f'proveedor{i}123')
                db.session.add(user_provider)
            
            # Guardar todos los cambios
            db.session.commit()
            print("✅ Usuarios creados correctamente:")
            print("   🔐 admin / admin123 (Administrador)")
            print("   👤 proveedor1 / proveedor1123 (Proveedor)")
            print("   👤 proveedor2 / proveedor2123 (Proveedor)")
            print("   👤 proveedor3 / proveedor3123 (Proveedor)")
            
        print("\n🎯 Siguiente paso: python setup_sedes.py")
        
    except Exception as e:
        print(f"❌ Error al inicializar base de datos: {e}")
        sys.exit(1)