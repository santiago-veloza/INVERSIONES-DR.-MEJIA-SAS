# 🏥 Sistema de Gestión de Órdenes de Trabajo - Inversiones Dr. Mejía SAS

## 📋 Descripción General

Sistema web integral desarrollado para **Inversiones Dr. Mejía SAS**, empresa del sector óptico con cobertura nacional en Colombia. La plataforma optimiza la gestión completa de órdenes de trabajo ópticas, control de proveedores, seguimiento de pagos y comunicación centralizada entre 21 sedes distribuidas en el país.

## 🎯 Objetivos del Sistema

- **Centralización Operativa**: Unificación de la gestión de todas las sedes en una plataforma única
- **Optimización de Procesos**: Automatización del flujo de trabajo entre sedes, administración central y proveedores
- **Control Financiero**: Seguimiento detallado de ventas, costos y utilidades por sede
- **Trazabilidad Completa**: Registro exhaustivo de operaciones con auditoría integrada
- **Gestión de Utilidades**: Análisis en tiempo real de ganancias y márgenes de rentabilidad

## 🚀 Características Principales

### 📊 **Gestión Multi-Sede**
- Administración de 21 sedes en Colombia con control independiente
- Dashboard centralizado con estadísticas en tiempo real
- Sistema de mensajería integrado para comunicación eficiente

### 👥 **Sistema de Roles Avanzado**
- **Admin Central**: Control total del sistema, gestión de usuarios y análisis de utilidades
- **Admin de Sede**: Gestión específica de su sede con acceso a órdenes y pagos
- **Asistente**: Operaciones administrativas y creación de órdenes
- **Proveedor**: Gestión de órdenes asignadas y actualización de estados

### 💰 **Control Financiero y Utilidades**
- **Análisis de Rentabilidad**: Cálculo automático de utilidades (Vr Venta - Vr Costo)
- **Dashboard Financiero**: Ganancias totales y mensuales con márgenes de utilidad
- **Top Sedes**: Ranking de sedes por ventas y órdenes (actualización automática cada 5 minutos)
- **Exportación**: Reportes en Excel y CSV con datos financieros completos

### 🔄 **Flujo de Órdenes Optimizado**
- Creación de órdenes con fórmulas ópticas y especificaciones de lentes
- Workflow automatizado: Creación → Revisión Admin → Envío Proveedor → Proceso → Entrega
- Sistema de notificaciones automáticas en cada cambio de estado
- Estados codificados por colores para visualización rápida

### 📈 **Dashboard Interactivo**
- **KPIs en Tiempo Real**: Órdenes, ventas, utilidades actualizadas automáticamente
- **Gráficos de Lentes**: Distribución de Progresivos, Bifocales y Monofocales
- **Top 5 Sedes**: Rankings por ventas y órdenes del mes con actualización en tiempo real
- **Estadísticas Detalladas**: Tabla completa con métricas por sede

## 🏗️ Arquitectura Técnica

### 🖥️ **Backend**
- **Framework**: Flask 2.2.5 con extensiones especializadas
- **Base de Datos**: PostgreSQL (Supabase) en producción
- **ORM**: SQLAlchemy para modelado de datos
- **Autenticación**: Flask-Login con roles granulares
- **API RESTful**: Endpoints para actualización en tiempo real

### 🎨 **Frontend**
- **Framework CSS**: Bootstrap 5.3 con diseño responsive
- **Template Engine**: Jinja2 con herencia de plantillas
- **JavaScript**: Vanilla JS con fetch API para actualizaciones asíncronas
- **Iconografía**: Font Awesome 6
- **Formateo Dinámico**: Separadores de miles en tiempo real para valores monetarios

### 🔒 **Seguridad**
- Control de acceso basado en roles (RBAC)
- Protección CSRF en todos los formularios
- Hash seguro de contraseñas con Werkzeug
- Validación de datos en cliente y servidor
- Auditoría completa de operaciones

## 📁 Estructura del Proyecto

```
INVERSIONES-DR.-MEJIA-SAS/
├── 🖥️ backend/
│   ├── app/
│   │   ├── models.py          # Modelos: User, WorkOrder, Payment, Sede, etc.
│   │   ├── routes.py          # Rutas y endpoints API
│   │   ├── forms.py           # Formularios WTForms
│   │   ├── security.py        # Decoradores de seguridad
│   │   └── __init__.py        # Inicialización y filtros personalizados
│   └── config.py              # Configuración del sistema
├── 🎨 frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css     # Estilos personalizados
│   │   └── uploads/           # Archivos subidos (soportes)
│   └── templates/
│       ├── admin/             # Dashboards y gestión administrativa
│       ├── auth/              # Login y autenticación
│       ├── ordenes/           # Gestión de órdenes
│       ├── pagos/             # Control de pagos
│       ├── proveedores/       # Panel de proveedores
│       └── sedes/             # Administración de sedes
├── 🚀 app.py                  # Punto de entrada
├── 📋 create_admin.py         # Script creación admin
└── 📚 README.md               # Documentación
```

## 🏢 Sedes en Colombia

**21 sedes** distribuidas estratégicamente:

| Región | Sedes |
|--------|-------|
| **Bogotá D.C.** | Usaquén, Suba, Kennedy |
| **Antioquia** | Medellín, Bello |
| **Valle del Cauca** | Cali, Palmira |
| **Atlántico** | Barranquilla |
| **Santander** | Bucaramanga |
| **Norte de Santander** | Cúcuta |
| **Otras ciudades** | Cartagena, Soacha, Ibagué, Pereira, Armenia, Manizales, Villavicencio, Neiva, Montería, Sincelejo, Pasto |

## 💻 Instalación

### Requisitos
- Python 3.8+
- PostgreSQL (o SQLite para desarrollo)
- Navegador moderno (Chrome, Firefox, Edge)

### Instalación Local

```bash
# 1. Clonar repositorio
git clone https://github.com/santiago-veloza/INVERSIONES-DR.-MEJIA-SAS.git
cd INVERSIONES-DR.-MEJIA-SAS

# 2. Crear entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear admin inicial
python create_admin.py

# 5. Ejecutar aplicación
python app.py
```

La aplicación estará disponible en `http://127.0.0.1:5000`

## 🔑 Credenciales por Defecto

### Admin Central
```
Usuario: admin
Contraseña: admin123
```

### Crear Usuarios Adicionales
Usar el script `create_admin.py` para crear:
- Administradores de sede
- Asistentes
- Proveedores

## 📊 Funcionalidades Clave

### 🔄 **Flujo de Trabajo Completo**

1. **Creación de Orden** (Sede/Asistente)
   - Datos del cliente (nombre, CC, teléfono)
   - Fórmula óptica (OD, OI, ADD, DP Y ALT)
   - Tipo de montura y observaciones
   - Precio de venta al cliente

2. **Revisión Admin** (Solo Admin Central)
   - Completar especificaciones de lentes
   - Definir clase (Progresivo/Bifocal/Monofocal)
   - Especificar tipo de lente (Transitions, Blue Light, etc.)
   - Sistema valida antes de enviar a proveedor

3. **Procesamiento Proveedor**
   - Aceptar/Rechazar orden
   - Actualizar estado: En Proceso → Devuelta Proveedor
   - Registrar costo total
   - Sistema calcula utilidad automáticamente

4. **Recepción en Sede**
   - Marcar como "Recibida Óptica"
   - Estado final: Finalizada

### 💵 **Sistema de Pagos**

- **Registro Detallado**: Fecha, monto, soporte documental
- **Estados de Pago**: Pendiente, Parcialmente Pagada, Pagada
- **Vista por Sede**: Órdenes pendientes con totales
- **Filtros Avanzados**: Por estado, fecha, sede

### 📈 **Dashboard Administrativo**

- **Tarjetas de Resumen**: Sedes activas, órdenes totales/mes, ventas totales/mes
- **Análisis de Lentes**: Totales y mensuales de Progresivos, Bifocales, Monofocales
- **Ganancias**: Ventas totales vs Costos con cálculo de utilidad y margen
- **Top 5 Sedes**: Por ventas y por órdenes del mes (actualización automática cada 5 minutos)
- **Tabla Detallada**: Estadísticas completas por sede con exportación

### 🎨 **Interfaz de Usuario**

- **Diseño Responsive**: Optimizado para desktop, tablet y móvil
- **Estados con Colores**: 
  - 🔴 Rojo: Pendiente Admin
  - 🟡 Amarillo: En Proceso
  - 🟢 Verde: Recibida Óptica
  - 🟠 Naranja: Devuelta Proveedor
- **Formato de Moneda**: Separadores de miles en tiempo real ($230.000)
- **Texto en Negrita**: Todos los valores de tabla en negrita para mejor lectura
- **Texto Negro**: Texto negro en todas las filas con colores de fondo

### 🔔 **Sistema de Notificaciones**

- **Alertas Automáticas**: Notificaciones en cada cambio de estado de orden
- **Panel de Notificaciones**: Campana con contador de notificaciones no leídas
- **Marcar como Leídas**: Función automática al hacer clic en la campana

### 📤 **Exportación de Datos**

- **Formatos**: Excel (.xlsx) y CSV
- **Datos Incluidos**: Todas las órdenes con datos completos
- **Datos Financieros**: Precio de venta, costo y utilidad (solo para admins)

## 🎨 Mejoras de UI/UX Recientes

### ✨ **Formateo de Valores Monetarios**
- Separadores de miles automáticos en tiempo real
- Formato inteligente: Integers sin decimales, Floats con 2 decimales
- Aplicado en toda la plataforma (listados, formularios, dashboard)

### 🎯 **Mejoras de Visualización**
- Todas las tablas con texto en **negrita** (font-weight: 700)
- Texto **negro** en todas las filas con colores de fondo
- Valores de dashboard en negrita para mejor legibilidad
- Fondo azul claro en valores de formularios para mejor contraste

### 🔄 **Mejoras de Workflow**
- Todas las órdenes de sede requieren revisión de admin antes de enviarse a proveedor
- Estado "Recibida Óptica" en **verde** para todos los usuarios
- Reorganización de formularios con secciones lógicas

## 🔧 Configuración Avanzada

### Variables de Entorno
```env
FLASK_APP=app.py
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@host/database
SECRET_KEY=your-secret-key-here
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

### Base de Datos
El sistema soporta PostgreSQL (recomendado para producción) y SQLite (desarrollo).

## 📞 Soporte

### Mantenimiento
- Backup automático de base de datos
- Actualizaciones de seguridad periódicas
- Monitoreo de rendimiento
- Optimización de consultas

### Contacto
**Desarrollador**: Santiago Veloza  
📧 santiagoveloza91@gmail.com  
🔗 [LinkedIn](https://linkedin.com/in/santiago-veloza)  
💻 [GitHub](https://github.com/santiago-veloza)

---

## 📄 Licencia

© 2025 Inversiones Dr. Mejía SAS. Todos los derechos reservados.

---

*Sistema desarrollado para optimizar las operaciones de gestión óptica a nivel nacional con enfoque en control financiero y trazabilidad completa.*
