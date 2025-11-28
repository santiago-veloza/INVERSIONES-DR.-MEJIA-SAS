"""
Script para crear el usuario administrador inicial
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Verificar si ya existe un admin
    admin = User.query.filter_by(role='admin').first()
    
    if admin:
        print(f"✅ Ya existe un usuario admin: {admin.username}")
    else:
        print("👤 Creando usuario administrador...")
        
        # Crear usuario admin
        admin = User(
            username='admin',
            email='admin@opticas.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            is_active=True,
            sede_id=None,
            provider_id=None
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Usuario admin creado exitosamente!")
        print("\n📋 Credenciales:")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
        print("\n⚠️  IMPORTANTE: Cambia esta contraseña después del primer login!")
