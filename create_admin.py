

import sys
import os
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import create_app, db
from backend.app.models import User
from backend.config import Config
from werkzeug.security import generate_password_hash

parser = argparse.ArgumentParser()
parser.add_argument('--reset-password', action='store_true',
                        help='Sobrescribe la contraseña del admin con ADMIN_PASSWORD del .env')
args = parser.parse_args()

app = create_app()

with app.app_context():
    admin = User.query.filter_by(role='admin').first()

    if admin:
        print(f"✅ Ya existe un usuario admin: {admin.username}")
        if args.reset_password:
            admin.password_hash = generate_password_hash(Config.ADMIN_PASSWORD)
            db.session.commit()
            print(f"🔑 Contraseña del admin actualizada al valor actual de ADMIN_PASSWORD en .env.")
    else:
        print("👤 Creando usuario administrador...")

        # Crear usuario admin con credenciales tomadas del .env
        admin = User(
            username=Config.ADMIN_USERNAME,
            email=Config.ADMIN_EMAIL,
            password_hash=generate_password_hash(Config.ADMIN_PASSWORD),
            role='admin',
            is_active=True,
            sede_id=None,
            provider_id=None
        )

        db.session.add(admin)
        db.session.commit()

        print("✅ Usuario admin creado exitosamente!")
        print("\n📋 Credenciales:")
        print(f"   Usuario: {Config.ADMIN_USERNAME}")
        print(f"   Contraseña: {Config.ADMIN_PASSWORD}")
        print("\n⚠️  IMPORTANTE: Cambia esta contraseña después del primer login!")
