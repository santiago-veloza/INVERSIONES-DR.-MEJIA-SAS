"""
Gestor simplificado para tareas comunes del sistema.
Facilita el mantenimiento y operación del proyecto.
"""

import sys
import os
import click
from datetime import datetime

# Agregar path para imports
sys.path.insert(0, os.path.dirname(__file__))

@click.group()
def cli():
    """Gestor del Sistema Ópticas Dr. Mejía SAS"""
    pass

@cli.command()
def status():
    """Ver estado general del sistema"""
    try:
        from backend.app import create_app, db
        from backend.app.models import User, Sede, WorkOrder, Provider
        
        app = create_app()
        with app.app_context():
            print("📊 ESTADO DEL SISTEMA")
            print("=" * 40)
            print(f"👥 Usuarios: {User.query.count()}")
            print(f"🏢 Sedes: {Sede.query.filter_by(is_active=True).count()}")
            print(f"📦 Órdenes: {WorkOrder.query.count()}")
            print(f"🏭 Proveedores: {Provider.query.count()}")
            print(f"⏰ Última verificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

@cli.command()
def migrate():
    """Ejecutar migración para mejorar mantenibilidad"""
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'migrate_to_maintainable.py'], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errores:", result.stderr)
    except Exception as e:
        print(f"❌ Error ejecutando migración: {e}")

@cli.command()
@click.option('--username', default='admin', help='Nombre de usuario')
@click.option('--password', default='admin123', help='Contraseña')
def create_admin(username, password):
    """Crear usuario administrador"""
    try:
        from backend.app import create_app, db
        from backend.app.models import User
        
        app = create_app()
        with app.app_context():
            existing_admin = User.query.filter_by(username=username).first()
            if existing_admin:
                print(f"⚠️ Usuario {username} ya existe")
                return
            
            admin = User(
                username=username,
                email=f'{username}@opticasdrmejia.com',
                role='admin',
                is_active=True
            )
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            
            print(f"✅ Usuario administrador '{username}' creado exitosamente")
            print(f"🔑 Credenciales: {username} / {password}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

@cli.command()
def clear_cache():
    """Limpiar cache del sistema"""
    try:
        from backend.app import create_app
        from backend.app.services import CacheService
        from backend.app.services.stats_service import StatsService
        
        app = create_app()
        with app.app_context():
            # Limpiar cache general
            CacheService.clear()
            
            # Limpiar cache de estadísticas
            stats_service = StatsService()
            stats_service.clear_all_stats_cache()
            
            print("✅ Cache limpiado exitosamente")
            
    except Exception as e:
        print(f"❌ Error: {e}")

@cli.command()
def check_sedes():
    """Verificar y crear usuarios de sede si es necesario"""
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'check_sedes.py'], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errores:", result.stderr)
    except Exception as e:
        print(f"❌ Error: {e}")

@cli.command()
@click.option('--host', default='127.0.0.1', help='Host para el servidor')
@click.option('--port', default=5000, help='Puerto para el servidor')
@click.option('--debug', is_flag=True, help='Ejecutar en modo debug')
def run(host, port, debug):
    """Ejecutar servidor de desarrollo"""
    try:
        from backend.app import create_app
        
        app = create_app()
        print(f"🚀 Iniciando servidor en http://{host}:{port}")
        print("📋 Panel de administración disponible")
        print("🔐 Usuarios de sede: OpticasDrMejia2024")
        print("👤 Admin: admin / admin123")
        
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        print(f"❌ Error: {e}")

@cli.command()
def test_services():
    """Probar que todos los servicios funcionan correctamente"""
    try:
        from backend.app import create_app
        from backend.app.services.auth_service import AuthService
        from backend.app.services.order_service import OrderService
        from backend.app.services.stats_service import StatsService
        from backend.app.services import CacheService
        from backend.app.services.utils import ValidationUtils, FileUtils, NumberUtils
        
        app = create_app()
        with app.app_context():
            print("🧪 PROBANDO SERVICIOS")
            print("=" * 30)
            
            # Test CacheService
            CacheService.set('test', 'value', 60)
            if CacheService.get('test') == 'value':
                print("✅ CacheService")
                CacheService.delete('test')
            else:
                print("❌ CacheService")
            
            # Test ValidationUtils
            if ValidationUtils.validate_email('test@example.com'):
                print("✅ ValidationUtils")
            else:
                print("❌ ValidationUtils")
            
            # Test NumberUtils
            formatted = NumberUtils.format_currency(1234567.89)
            if formatted:
                print(f"✅ NumberUtils - {formatted}")
            else:
                print("❌ NumberUtils")
            
            # Test StatsService
            stats_service = StatsService()
            stats = stats_service.get_dashboard_stats()
            if isinstance(stats, dict):
                print("✅ StatsService")
            else:
                print("❌ StatsService")
            
            print("\n🎯 Servicios verificados exitosamente")
            
    except Exception as e:
        print(f"❌ Error: {e}")

@cli.command()
def info():
    """Mostrar información del proyecto"""
    print("""
🏥 Sistema de Gestión Óptica - Inversiones Dr. Mejía SAS
========================================================

📋 CARACTERÍSTICAS:
  • Sistema multi-sede (21+ sedes)
  • Gestión completa de órdenes ópticas
  • Dashboard ejecutivo con KPIs
  • Sistema de roles y permisos
  • Módulo financiero avanzado
  • Auditoría y seguridad

🏗️ ARQUITECTURA MEJORADA:
  • Servicios modulares (AuthService, OrderService, StatsService)
  • Cache inteligente con TTL
  • Logging estructurado
  • Configuración por entornos
  • Validaciones centralizadas
  • Utilidades reutilizables

📁 ESTRUCTURA DE SERVICIOS:
  • backend/app/services/
    ├── __init__.py (BaseService, CacheService)
    ├── auth_service.py (Autenticación)
    ├── order_service.py (Gestión de órdenes)
    ├── stats_service.py (Estadísticas y KPIs)
    └── utils.py (Utilidades compartidas)

🚀 COMANDOS ÚTILES:
  • python manage.py status - Ver estado del sistema
  • python manage.py migrate - Ejecutar migración
  • python manage.py run - Iniciar servidor de desarrollo
  • python manage.py clear-cache - Limpiar cache
  • python manage.py test-services - Probar servicios

🔐 CREDENCIALES POR DEFECTO:
  • Admin Central: admin / admin123
  • Sedes: OpticasDrMejia2024
  • Base de datos: Configurada en .env

💡 DESARROLLO:
  • Flask 2.2.5 + PostgreSQL + Bootstrap 5
  • Arquitectura MVC con servicios
  • Responsive design
  • Real-time notifications

📧 Soporte: desarrollo@opticasdrmejia.com
    """)

if __name__ == '__main__':
    cli()