# 🏥 Sistema de Gestión de Órdenes de Trabajo - Inversiones Dr. Mejía SAS

## 📋 Descripción General

El Sistema de Gestión de Órdenes de Trabajo es una aplicación web desarrollada específicamente para **Inversiones Dr. Mejía SAS**, una empresa del sector óptico con presencia nacional en Colombia. El sistema optimiza los procesos administrativos entre la empresa y sus proveedores, facilitando la gestión integral de órdenes de trabajo, control de pagos, y comunicación entre sedes.

La solución permite administrar múltiples sedes a nivel nacional, gestionar proveedores especializados, procesar órdenes con fórmulas ópticas, realizar seguimiento de pagos, y generar reportes detallados a través de un panel de control moderno e intuitivo.

## 🎯 Objetivos del Sistema

El proyecto centraliza la gestión completa de las operaciones de Inversiones Dr. Mejía SAS, desde la creación de órdenes hasta su cierre y liquidación. Los objetivos principales incluyen:

- **Centralización de Operaciones**: Unificar la gestión de todas las sedes en una plataforma única
- **Optimización de Procesos**: Automatizar flujos de trabajo entre sedes, administración central y proveedores
- **Control Financiero**: Seguimiento detallado de pagos y estados financieros por sede
- **Trazabilidad Completa**: Registro exhaustivo de todas las operaciones y cambios de estado
- **Comunicación Eficiente**: Sistema de mensajería integrado entre administración central y sedes

## 🚀 Características Principales

### 📊 **Gestión Multi-Sede**
- Administración de 21 sedes distribuidas en Colombia
- Control independiente de operaciones por sede
- Comunicación centralizada con sistema de mensajería

### 👥 **Sistema de Roles Avanzado**
- **Administrador Central**: Control total del sistema y gestión de usuarios
- **Admin de Sede**: Gestión específica de su sede asignada
- **Asistente General**: Operaciones administrativas generales
- **Proveedor**: Acceso a órdenes asignadas y gestión de trabajos

### 🔄 **Flujo de Órdenes Automatizado**
- Creación de órdenes con fórmulas ópticas adjuntas
- Asignación automática a proveedores especializados
- Seguimiento de estados en tiempo real
- Notificaciones automáticas de cambios de estado

### 💰 **Control Financiero Integral**
- Registro detallado de pagos con soportes
- Estados de pago por orden (pendiente, parcial, pagada)
- Reportes financieros por sede y proveedor
- Gestión de pagos pendientes

### 📈 **Analítica y Reportes**
- Dashboard interactivo con KPIs en tiempo real
- Gráficos de productividad y rendimiento
- Reportes exportables en múltiples formatos
- Estadísticas por sede, proveedor y período

## 🏗️ Arquitectura Técnica

### 🖥️ **Backend (Python Flask)**
- **Framework Principal**: Flask 2.3+ con extensiones especializadas
- **ORM**: SQLAlchemy para modelado de datos avanzado
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Autenticación**: Flask-Login con gestión de sesiones seguras
- **API**: RESTful endpoints con validación de datos
- **Seguridad**: Roles granulares y control de acceso por recursos

### 🎨 **Frontend (Responsive Design)**
- **Framework CSS**: Bootstrap 5.3 con componentes personalizados
- **Template Engine**: Jinja2 con herencia de plantillas
- **JavaScript**: Vanilla JS + bibliotecas especializadas
- **Iconografía**: Font Awesome 6 Professional
- **UX/UI**: Diseño adaptativo para dispositivos móviles y escritorio

### 📊 **Características Técnicas Avanzadas**
- **Notificaciones en Tiempo Real**: Sistema de alertas automáticas
- **Carga de Archivos**: Gestión segura de documentos y soportes
- **Validación de Formularios**: Validación del lado cliente y servidor
- **Gestión de Sesiones**: Seguridad avanzada con timeout automático
- **Logging Completo**: Auditoría detallada de todas las operaciones

## 📁 Estructura del Proyecto

```
INVERSIONES-DR.-MEJIA-SAS/
├── 🖥️ backend/                    # Backend Principal
│   ├── app/                       # Aplicación Flask
│   │   ├── models.py             # 📊 Modelos de datos (User, WorkOrder, Payment, etc.)
│   │   ├── routes.py             # 🛣️ Rutas y endpoints API
│   │   ├── forms.py              # 📝 Formularios con validación WTF
│   │   └── __init__.py           # ⚙️ Configuración Flask
│   ├── instance/                 # 💾 Base de datos SQLite
│   ├── config.py                 # 🔧 Configuración del sistema
│   ├── init_db.py               # 🛠️ Inicialización base de datos
│   ├── init_sedes.py            # 🏢 Configuración de sedes
│   └── requirements.txt          # 📦 Dependencias Python
├── 🎨 frontend/                   # Frontend Interface
│   ├── static/                   # 🎯 Recursos estáticos
│   │   ├── css/                  # 🎨 Estilos personalizados
│   │   ├── js/                   # ⚡ Scripts JavaScript
│   │   ├── img/                  # 🖼️ Imágenes y recursos
│   │   └── uploads/              # 📁 Archivos subidos
│   └── templates/                # 📄 Plantillas HTML Jinja2
│       ├── admin/                # 👑 Interfaz administrativa
│       ├── auth/                 # 🔐 Autenticación
│       ├── messages/             # 💬 Sistema de mensajería
│       ├── ordenes/              # 📋 Gestión de órdenes
│       ├── pagos/                # 💳 Control de pagos
│       ├── proveedores/          # 🏭 Gestión de proveedores
│       ├── reports/              # 📊 Reportes y analítica
│       └── sedes/                # 🏢 Administración de sedes
├── 🐍 venv/                      # Entorno virtual Python
├── 🚀 app.py                     # Punto de entrada principal
├── 🛠️ setup_db.py               # Script configuración DB
├── 🌍 setup_sedes.py            # Script configuración sedes
└── 📚 README.md                  # Documentación principal
```

## 🏢 Gestión de Sedes

El sistema gestiona **21 sedes** distribuidas estratégicamente en Colombia:

### 📍 **Distribución Geográfica**
- **Bogotá D.C.**: 3 sedes (Norte, Sur, Centro)
- **Antioquia**: 2 sedes (Medellín, Bello)
- **Valle del Cauca**: 2 sedes (Cali, Palmira)
- **Atlántico**: 1 sede (Barranquilla)
- **Bolívar**: 1 sede (Cartagena)
- **Santander**: 1 sede (Bucaramanga)
- **Cundinamarca**: 1 sede (Soacha)
- **Tolima**: 1 sede (Ibagué)
- **Norte de Santander**: 1 sede (Cúcuta)
- **Risaralda**: 1 sede (Pereira)
- **Quindío**: 1 sede (Armenia)
- **Caldas**: 1 sede (Manizales)
- **Meta**: 1 sede (Villavicencio)
- **Huila**: 1 sede (Neiva)
- **Córdoba**: 1 sede (Montería)
- **Sucre**: 1 sede (Sincelejo)
- **Nariño**: 1 sede (Pasto)

## 👥 Sistema de Usuarios y Roles

### 🔐 **Roles y Permisos**

#### 👑 **Administrador Central**
- **Alcance**: Control total del sistema
- **Permisos**:
  - Gestión completa de usuarios y roles
  - Administración de todas las sedes
  - Acceso a reportes globales
  - Configuración del sistema
  - Gestión de proveedores a nivel nacional

#### 🏢 **Admin de Sede**
- **Alcance**: Gestión específica de sede asignada
- **Permisos**:
  - Visualización de mensajes de administración central
  - Consulta de órdenes de su sede
  - Acceso a pagos de su sede
  - Dashboard personalizado de sede

#### 🤝 **Asistente General**
- **Alcance**: Operaciones administrativas generales
- **Permisos**:
  - Creación y gestión de órdenes
  - Registro de pagos
  - Comunicación con proveedores
  - Acceso a reportes operativos

#### 🏭 **Proveedor**
- **Alcance**: Gestión de órdenes asignadas
- **Permisos**:
  - Consulta de órdenes recibidas
  - Actualización de estados de trabajo
  - Dashboard de productividad
  - Comunicación con administración

## 💻 Instalación y Configuración

### 📋 **Requisitos del Sistema**
- **Python**: 3.8+ (recomendado 3.11+)
- **Sistema Operativo**: Windows 10/11, Linux, macOS
- **RAM**: Mínimo 4GB (recomendado 8GB+)
- **Espacio en Disco**: 500MB libres
- **Navegador**: Chrome, Firefox, Edge (versiones recientes)

### 🛠️ **Proceso de Instalación**

#### 1️⃣ **Preparación del Entorno**
```bash
# Clonar repositorio
git clone https://github.com/santiago-veloza/INVERSIONES-DR.-MEJIA-SAS.git
cd INVERSIONES-DR.-MEJIA-SAS

# Crear y activar entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

#### 2️⃣ **Instalación de Dependencias**
```bash
# Instalar dependencias del backend
pip install -r backend/requirements.txt

# Verificar instalación
pip list
```

#### 3️⃣ **Configuración de Base de Datos**
```bash
# Inicializar base de datos con usuarios por defecto
python setup_db.py

# Configurar las 21 sedes en Colombia
python setup_sedes.py

# Verificar configuración
python -c "from backend.app.models import User, Sede; print(f'Usuarios: {User.query.count()}, Sedes: {Sede.query.count()}')"
```

#### 4️⃣ **Ejecución del Sistema**
```bash
# Iniciar servidor de desarrollo
python app.py

# El sistema estará disponible en:
# http://127.0.0.1:5000
```

## 🔑 Credenciales de Acceso por Defecto

### 👑 **Administrador Central**
```
Usuario: admin
Email: admin@inversiones.com
Contraseña: admin123
Rol: Administrador
```

### 🤝 **Asistente General**
```
Usuario: asistente1
Email: asistente@inversiones.com
Contraseña: asistente123
Rol: Asistente
```

### 🏭 **Proveedores de Prueba**
```
Usuario: proveedor1 | Contraseña: proveedor1123
Usuario: proveedor2 | Contraseña: proveedor2123
Usuario: proveedor3 | Contraseña: proveedor3123
```

### 🏢 **Administradores de Sede**
Los usuarios admin_sede se crean automáticamente para cada una de las 21 sedes:
```
Formato: admin_sede_[nombre_sede]
Contraseña: sede123
```

## 📊 Funcionalidades Avanzadas

### 🔄 **Flujo de Trabajo Automatizado**
1. **Creación de Orden**: Sede o asistente crea orden con especificaciones ópticas
2. **Asignación**: Sistema asigna automáticamente a proveedor especializado
3. **Notificación**: Proveedor recibe notificación automática
4. **Procesamiento**: Proveedor actualiza estado durante el trabajo
5. **Devolución**: Notificación automática de trabajo completado
6. **Pago**: Registro de pago con soporte documental
7. **Cierre**: Finalización automática del flujo

### 💬 **Sistema de Mensajería**
- **Comunicación Centralizada**: Mensajes desde administración central a sedes
- **Notificaciones Automáticas**: Alertas por cambios de estado
- **Priorización**: Mensajes normales, altos y urgentes
- **Archivado**: Gestión de mensajes históricos

### 📈 **Dashboard y Analítica**
- **KPIs en Tiempo Real**: Métricas de productividad actualizadas
- **Gráficos Interactivos**: Visualización de datos con Chart.js
- **Filtros Avanzados**: Análisis por fecha, sede, proveedor
- **Exportación**: Reportes en PDF, Excel y CSV

## 🔒 Seguridad y Auditoría

### 🛡️ **Características de Seguridad**
- **Autenticación Robusta**: Hash seguro de contraseñas con Werkzeug
- **Control de Sesiones**: Timeout automático y gestión segura
- **Validación de Datos**: Sanitización en cliente y servidor
- **Control de Acceso**: Decoradores de autorización granulares
- **Auditoría Completa**: Logging detallado de todas las operaciones

### 📝 **Registro de Auditoría**
- **Operaciones de Usuario**: Login, logout, cambios de datos
- **Transacciones**: Creación, modificación, eliminación de registros
- **Accesos**: Intentos de acceso y permisos denegados
- **Sistema**: Errores, excepciones y eventos críticos

## 🚀 Despliegue en Producción

### ☁️ **Opciones de Despliegue**
- **Servidor Dedicado**: Instalación en servidor físico o VPS
- **Cloud Hosting**: AWS, Google Cloud, Azure
- **Contenedores**: Docker con Docker Compose
- **PaaS**: Heroku, PythonAnywhere, Railway

### 🔧 **Configuración de Producción**
```python
# Configuración para producción en config.py
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    SSL_REDIRECT = True
```

## 📞 Soporte y Mantenimiento

### 🔧 **Mantenimiento Regular**
- **Backup Automático**: Respaldo diario de base de datos
- **Actualizaciones**: Parches de seguridad y nuevas funcionalidades
- **Monitoreo**: Supervisión continua del rendimiento
- **Optimización**: Mejoras periódicas de consultas y procesos

### 📋 **Documentación Técnica**
- **API Documentation**: Endpoints documentados con Swagger
- **Manual de Usuario**: Guías detalladas por rol
- **Manual Técnico**: Documentación para desarrolladores
- **Troubleshooting**: Guía de resolución de problemas

---

## 📄 Licencia

Este proyecto es propiedad de **Inversiones Dr. Mejía SAS**. Todos los derechos reservados.

## 👨‍💻 Desarrollado por

**Santiago Veloza**  
Desarrollador Full Stack  
📧 santiago.veloza@example.com  
🔗 LinkedIn: [santiago-veloza](https://linkedin.com/in/santiago-veloza)

---

*Sistema desarrollado específicamente para optimizar las operaciones de Inversiones Dr. Mejía SAS y mejorar la eficiencia en la gestión de órdenes de trabajo a nivel nacional.*
