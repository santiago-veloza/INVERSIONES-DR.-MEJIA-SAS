from backend.app import create_app
from backend.config import Config

app = create_app()

def print_startup_info():
    print("=" * 55)
    print(" Credenciales por defecto:")
    print(f"   • Admin Central: {Config.ADMIN_USERNAME} / {Config.ADMIN_PASSWORD}")
    print(f"   • Sedes: {Config.SEDE_SHARED_PASSWORD}")
    print("   • Panel disponible en: http://127.0.0.1:5000")
    print("=" * 55)

if __name__ == '__main__':
    if Config.DEBUG:
        print_startup_info()
    app.run(debug=False, host='0.0.0.0', port=5000)
