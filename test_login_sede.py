#!/usr/bin/env python
from backend.app import create_app, db
from backend.app.models import Sede, User

app = create_app()

with app.app_context():
    print("=== PRUEBA DE LOGIN POR SEDE ===")
    
    # Verificar sedes activas
    sedes = Sede.query.filter_by(is_active=True).order_by(Sede.department, Sede.city, Sede.name).all()
    print(f"Sedes activas disponibles: {len(sedes)}")
    
    for i, sede in enumerate(sedes[:5], 1):  # Mostrar solo las primeras 5
        print(f"{i}. ID: {sede.id} | {sede.name} - {sede.city} ({sede.department})")
        
        # Verificar si existe usuario para esta sede
        user = User.query.filter_by(username=f'sede_{sede.id}', role='admin_sede', sede_id=sede.id).first()
        
        if user:
            print(f"   ✓ Usuario existente: {user.username}")
            # Verificar contraseña
            if user.check_password('OpticasDrMejia2024'):
                print(f"   ✓ Contraseña válida")
            else:
                print(f"   ✗ Contraseña incorrecta - Rehashing...")
                user.set_password('OpticasDrMejia2024')
                db.session.commit()
                print(f"   ✓ Contraseña actualizada")
        else:
            print(f"   ⚠ Usuario no existe - Creando...")
            user = User(
                username=f'sede_{sede.id}',
                email=f'sede{sede.id}@opticasdrmejia.com',
                role='admin_sede',
                sede_id=sede.id,
                is_active=True
            )
            user.set_password('OpticasDrMejia2024')
            db.session.add(user)
            db.session.commit()
            print(f"   ✓ Usuario creado: {user.username}")
        print()
    
    print("=== INSTRUCCIONES PARA PROBAR ===")
    print("1. Ve a http://127.0.0.1:5000/login")
    print("2. Selecciona 'Sede' como tipo de usuario")
    print("3. Elige cualquier sede del dropdown")
    print("4. Usa la contraseña: OpticasDrMejia2024")
    print("5. Haz clic en 'Iniciar Sesión'")
    print()
    print("Si no funciona, verifica:")
    print("- Que JavaScript esté habilitado")
    print("- Que el selector de sede no esté oculto")
    print("- Que se esté enviando el sede_id correctamente")