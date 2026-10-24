
import os
from werkzeug.security import generate_password_hash  # noqa: F401  (set_password usa argon2)

from backend.app import create_app, db
from backend.app.models import User, Provider
from backend.config import Config

PROVIDER_PASSWORD = os.environ.get('PROVIDER_TEST_PASSWORD', 'Proveedor2024')


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Tablas creadas (o ya existentes).")

        if not User.query.filter_by(role='admin').first():
            admin = User(
                username=Config.ADMIN_USERNAME,
                email=Config.ADMIN_EMAIL,
                role='admin',
                is_active=True,
            )
            admin.set_password(Config.ADMIN_PASSWORD)
            db.session.add(admin)
            print(f"Admin creado: {Config.ADMIN_USERNAME}")
        else:
            print("Ya existe un admin, no se crea otro.")

        if not Provider.query.first():
            provider = Provider(
                nit='900123456-1',
                razon_social='Ópticas del Valle S.A.S.',
                name='Ópticas del Valle',
                contact_person='Carlos López',
                email='contacto@opticasvalle.com',
                phone='3000000000',
            )
            db.session.add(provider)
            db.session.flush()

            prov_user = User(
                username='proveedor1',
                email='proveedor1@opticasdrmejia.com',
                role='proveedor',
                is_active=True,
                provider_id=provider.id,
            )
            prov_user.set_password(PROVIDER_PASSWORD)
            db.session.add(prov_user)
            print("Proveedor de prueba creado: proveedor1")
        else:
            print("Ya existe un proveedor, no se crea otro.")

        db.session.commit()
        print("Listo.")


if __name__ == '__main__':
    main()
