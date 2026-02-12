from backend.app import create_app

app = create_app()

def print_startup_info():
    """Mostrar información de inicio del sistema"""
    print("\n🏥 Sistema de Gestión Óptica - Inversiones Dr. Mejía SAS")
    print("=" * 55)
    print("🚀 Servidor iniciando...")
    print("🔐 Credenciales por defecto:")
    print("   • Admin Central: admin / admin123")
    print("   • Sedes: OpticasDrMejia2024")
    print("📋 Panel disponible en: http://127.0.0.1:5000")
    print("🛠️  Para gestión avanzada: python manage.py --help")
    print("=" * 55)

if __name__ == '__main__':
    print_startup_info()
    app.run(debug=False, host='0.0.0.0', port=5000)
