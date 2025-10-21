#!/usr/bin/env python3
"""
🏢 Script de inicialización de sedes
Crea las 21 sedes de Inversiones Dr. Mejía en Colombia
"""

import os
import sys

# Agregar el directorio backend al path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

if __name__ == '__main__':
    try:
        print("🏢 Inicializando sedes en Colombia...")
        print("=" * 50)
        
        # Importar los modelos y la aplicación
        from app import create_app, db
        from app import Sede
        
        # Crear la aplicación
        app = create_app()
        
        with app.app_context():
            # Verificar si ya existen sedes
            if Sede.query.first():
                print("⚠️  Las sedes ya existen en la base de datos")
                sys.exit(0)
            
            # Lista de las 21 sedes principales en Colombia
            sedes_data = [
                {'name': 'Sede Bogotá Centro', 'city': 'Bogotá', 'address': 'Carrera 7 # 32-46', 'phone': '601-234-5678', 'manager': 'María García'},
                {'name': 'Sede Medellín Poblado', 'city': 'Medellín', 'address': 'Carrera 43A # 14-15', 'phone': '604-987-6543', 'manager': 'Carlos Rodríguez'},
                {'name': 'Sede Cali Norte', 'city': 'Cali', 'address': 'Avenida 6N # 28-55', 'phone': '602-456-7890', 'manager': 'Ana López'},
                {'name': 'Sede Barranquilla Centro', 'city': 'Barranquilla', 'address': 'Carrera 44 # 76-32', 'phone': '605-321-9876', 'manager': 'Luis Torres'},
                {'name': 'Sede Cartagena Histórico', 'city': 'Cartagena', 'address': 'Calle 33 # 9-58', 'phone': '605-654-3210', 'manager': 'Elena Martínez'},
                {'name': 'Sede Bucaramanga Cabecera', 'city': 'Bucaramanga', 'address': 'Carrera 35 # 54-78', 'phone': '607-789-1234', 'manager': 'Roberto Silva'},
                {'name': 'Sede Pereira Centro', 'city': 'Pereira', 'address': 'Carrera 8 # 18-43', 'phone': '606-147-2580', 'manager': 'Patricia Vargas'},
                {'name': 'Sede Manizales Universidad', 'city': 'Manizales', 'address': 'Avenida Santander # 65-23', 'phone': '606-369-1470', 'manager': 'Andrés Moreno'},
                {'name': 'Sede Santa Marta Rodadero', 'city': 'Santa Marta', 'address': 'Carrera 3 # 18-45', 'phone': '605-258-7410', 'manager': 'Carmen Díaz'},
                {'name': 'Sede Ibagué Centro', 'city': 'Ibagué', 'address': 'Carrera 3 # 12-67', 'phone': '608-741-9630', 'manager': 'Miguel Herrera'},
                {'name': 'Sede Villavicencio Llano', 'city': 'Villavicencio', 'address': 'Carrera 40 # 37-29', 'phone': '608-852-7410', 'manager': 'Sandra Gómez'},
                {'name': 'Sede Pasto Centro', 'city': 'Pasto', 'address': 'Carrera 25 # 18-56', 'phone': '602-963-8520', 'manager': 'Fernando Castillo'},
                {'name': 'Sede Cúcuta Norte', 'city': 'Cúcuta', 'address': 'Avenida 1 # 15-78', 'phone': '607-741-9630', 'manager': 'Gloria Ramírez'},
                {'name': 'Sede Neiva Centro', 'city': 'Neiva', 'address': 'Carrera 5 # 21-43', 'phone': '608-159-7530', 'manager': 'Héctor Jiménez'},
                {'name': 'Sede Armenia Quindío', 'city': 'Armenia', 'address': 'Carrera 14 # 18-92', 'phone': '606-357-1590', 'manager': 'Lucía Fernández'},
                {'name': 'Sede Montería Córdoba', 'city': 'Montería', 'address': 'Carrera 3 # 27-45', 'phone': '604-753-9510', 'manager': 'Eduardo Ruiz'},
                {'name': 'Sede Sincelejo Sucre', 'city': 'Sincelejo', 'address': 'Carrera 20 # 25-18', 'phone': '605-951-7530', 'manager': 'Isabel Castro'},
                {'name': 'Sede Valledupar Centro', 'city': 'Valledupar', 'address': 'Carrera 9 # 16-47', 'phone': '605-357-9510', 'manager': 'Jaime Mendoza'},
                {'name': 'Sede Popayán Cauca', 'city': 'Popayán', 'address': 'Carrera 6 # 4-83', 'phone': '602-159-7530', 'manager': 'Mónica Aguilar'},
                {'name': 'Sede Tunja Boyacá', 'city': 'Tunja', 'address': 'Carrera 10 # 19-56', 'phone': '608-753-9510', 'manager': 'Ricardo Peña'},
                {'name': 'Sede Florencia Caquetá', 'city': 'Florencia', 'address': 'Carrera 11 # 15-38', 'phone': '608-357-9510', 'manager': 'Beatriz Ortega'}
            ]
            
            # Crear las sedes
            for sede_data in sedes_data:
                sede = Sede(
                    name=sede_data['name'],
                    city=sede_data['city'],
                    address=sede_data['address'],
                    phone=sede_data['phone'],
                    manager=sede_data['manager']
                )
                db.session.add(sede)
            
            # Guardar todos los cambios
            db.session.commit()
            print(f"✅ {len(sedes_data)} sedes creadas correctamente:")
            
            for sede_data in sedes_data:
                print(f"   🏢 {sede_data['name']} - {sede_data['city']}")
            
        print("\n🎯 ¡Sistema listo! Ejecuta: python app.py")
        
    except Exception as e:
        print(f"❌ Error al inicializar sedes: {e}")
        sys.exit(1)