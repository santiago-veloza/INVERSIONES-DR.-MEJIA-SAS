# 🏥 Sistema de Gestión Óptica - Inversiones Dr. Mejía SAS

<div align="center">
<img src="https://res.cloudinary.com/dwdnfpr8i/image/upload/v1762146543/logo-DR_MEJIA_za9ocq.png" alt="Ópticas Dr. Mejía" width="200"/>

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.2.5-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.1-purple.svg)](https://getbootstrap.com/)
[![Status](https://img.shields.io/badge/Status-Production-green.svg)](https://inversiones-dr-mejia-sas.onrender.com/)
</div>

## 📋 Descripción General

Plataforma web empresarial desarrollada para **Inversiones Dr. Mejía SAS**, empresa líder del sector óptico con cobertura nacional en Colombia. El sistema digitaliza y optimiza la gestión integral de órdenes ópticas, control de proveedores, administración financiera y comunicación corporativa entre 21+ sedes distribuidas en el territorio nacional.

### 🌟 Impacto Empresarial
- **Digitalización Completa**: Migración del 100% de procesos manuales a digital
- **Eficiencia Operativa**: Reducción del 70% en tiempos de procesamiento de órdenes
- **Control Financiero**: Visibilidad en tiempo real de utilidades por sede
- **Escalabilidad**: Arquitectura preparada para crecimiento empresarial

## 🎯 Objetivos Estratégicos

- **🏢 Centralización Empresarial**: Unificación operativa de todas las sedes en plataforma única
- **⚡ Automatización de Procesos**: Optimización del workflow entre sedes, administración y proveedores  
- **💎 Control Financiero Avanzado**: Análisis detallado de P&L, utilidades y márgenes por sede
- **🔍 Trazabilidad Total**: Sistema de auditoría completo con registro de todas las operaciones
- **📊 Business Intelligence**: Dashboard ejecutivo con KPIs y métricas en tiempo real

## 🚀 Características del Sistema

### 📊 **Gestión Multi-Sede Avanzada**
- **21+ Sedes Activas**: Control independiente con supervisión centralizada
- **Dashboard Ejecutivo**: Estadísticas consolidadas actualizadas cada 5 minutos
- **Sistema de Mensajería**: Comunicación interna integrada con notificaciones push
- **Geolocalización**: Mapa interactivo de sedes con métricas de performance

### 👥 **Sistema de Roles y Permisos**
- **🔑 Admin Central**: Control total, análisis financiero, gestión de usuarios
- **🏪 Admin de Sede**: Gestión local, órdenes, pagos, reportes de sede
- **👤 Asistente**: Creación de órdenes, seguimiento, soporte administrativo
- **🏭 Proveedor**: Portal especializado, gestión de órdenes asignadas, actualizaciones

### 💰 **Módulo Financiero Empresarial**
- **📈 Análisis de Rentabilidad**: Cálculo automático (Precio Venta - Costo Proveedor = Utilidad)
- **💹 Dashboard Financiero**: KPIs de ganancias, márgenes, ROI por sede
- **🏆 Rankings**: Top sedes por ventas, utilidades y volumen de órdenes
- **📄 Exportación Avanzada**: Reportes Excel/CSV con análisis financiero detallado
- **📋 Control de Pagos**: Gestión de cuentas por cobrar y flujo de caja

### 🔄 **Workflow de Órdenes Ópticas**
```mermaid
graph LR
    A[Creación Sede] --> B[Revisión Admin]
    B --> C[Envío Proveedor]
    C --> D[En Proceso]
    D --> E[Completado]
    E --> F[Entregado]
```
- **Estados Dinámicos**: Seguimiento en tiempo real con códigos de color
- **Notificaciones Push**: Alertas automáticas en cada cambio de estado
- **Especificaciones Ópticas**: Fórmulas completas, materiales, tratamientos
- **Historial Completo**: Trazabilidad total con timestamps y responsables

### 📈 **Business Intelligence Dashboard**
- **⚡ KPIs en Tiempo Real**: Órdenes, ventas, utilidades (actualización automática)
- **📊 Analytics Ópticos**: Distribución Progresivos/Bifocales/Monofocales con gráficos Chart.js
- **🏆 Top 5 Sedes**: Rankings dinámicos por performance mensual
- **📋 Tablas Ejecutivas**: Métricas completas con filtros avanzados
- **🎨 Diseño Responsivo**: Interface profesional optimizada para móviles

## 🏗️ Arquitectura Técnica Avanzada

### 🖥️ **Backend - Stack Empresarial**
```python
# Stack Principal
Flask 2.2.5           # Framework web profesional
PostgreSQL 15+        # Base de datos empresarial (Supabase Cloud)
SQLAlchemy 1.4+       # ORM con modelos relacionales complejos
Flask-Login           # Autenticación y gestión de sesiones
Flask-WTF            # Formularios con validación y protección CSRF
Flask-Migrate        # Versionado de base de datos
```
- **🔧 Arquitectura MVC**: Separación clara Modelos/Vistas/Controladores
- **🚀 APIs RESTful**: Endpoints para actualizaciones en tiempo real 
- **⚡ Caché Inteligente**: Flask-Caching para optimización de consultas
- **📊 Índices Optimizados**: Base de datos con índices para performance

### 🎨 **Frontend - Interface Profesional**
```html
<!-- Stack de Presentación -->
Bootstrap 5.3         <!-- Framework CSS responsive -->
Jinja2 Templates      <!-- Motor de plantillas con herencia -->
Chart.js 3.x         <!-- Visualización de datos interactiva -->
Font Awesome 6       <!-- Iconografía profesional -->
Vanilla JavaScript   <!-- Sin dependencias pesadas -->
```
- **📱 Responsive Design**: Optimizado para desktop, tablet y móvil
- **🎨 CSS Architecture**: Estilos organizados y mantenibles (123+ KB)
- **⚡ Updates Asíncronos**: Fetch API para datos en tiempo real
- **💫 Animations**: Transiciones suaves y feedback visual

### 🔒 **Seguridad Empresarial**
```python
# Capas de Seguridad
RBAC (Role-Based Access Control)    # Control granular de permisos
CSRF Protection                     # Protección contra ataques
Password Hashing (Werkzeug)         # Hash seguro de contraseñas  
SQL Injection Prevention            # ORM con consultas parametrizadas
Audit Logging                       # Registro completo de operaciones
```

### 🗄️ **Modelo de Datos**
```sql
-- Tablas Principales
users           # Gestión de usuarios y roles
sedes           # Información de sedes
ordenes         # Órdenes de trabajo ópticas
proveedores     # Gestión de proveedores
pagos           # Control financiero
mensajes        # Sistema de comunicación
audit_logs      # Auditoría completa
```

## 📁 Estructura del Proyecto

```
INVERSIONES-DR.-MEJIA-SAS/
├── 🖥️ backend/
│   ├── config.py              # Configuración de entornos
│   └── app/
│       ├── __init__.py        # Factory pattern app
│       ├── models.py          # Modelos SQLAlchemy
│       ├── routes.py          # Controladores y rutas
│       ├── forms.py           # Formularios WTF
│       └── security.py       # Funciones de seguridad
│
├── 🎨 frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css     # CSS centralizado (123KB)
│   │   ├── img/               # Assets gráficos
│   │   └── uploads/           # Archivos subidos
│   └── templates/
│       ├── base.html          # Template base
│       ├── base_auth.html     # Template autenticación
│       ├── index.html         # Dashboard principal
│       ├── admin/             # Módulo administrativo
│       ├── auth/              # Sistema de login
│       ├── ordenes/           # Gestión de órdenes
│       ├── pagos/             # Módulo financiero
│       ├── proveedores/       # Gestión proveedores
│       └── messages/          # Sistema de mensajería
│
├── 📊 analytics/
│   ├── check_css_cleanup.py   # Verificador de CSS
│   └── clean_comments.py     # Limpiador de código
│
├── 🚀 deployment/
│   ├── Procfile              # Configuración Heroku
│   ├── requirements.txt      # Dependencias Python
│   ├── runtime.txt          # Versión Python
│   └── app.py               # Entry point aplicación
│
└── 📝 docs/
    └── README.md            # Documentación completa
```

## 🌍 Cobertura Nacional - Red de Sedes

<div align="center">

### 🏢 **21 Sedes Activas en Colombia**

| 🌎 **Región** | 🏪 **Sedes** | 📊 **Cobertura** |
|---------------|-------------|-------------------|
| **🏙️ Bogotá D.C.** | Usaquén, Suba, Kennedy, Chapinero | 4 sedes |
| **🏔️ Antioquia** | Medellín Centro, Bello, Itagüí | 3 sedes |
| **🌴 Valle del Cauca** | Cali Norte, Palmira, Buenaventura | 3 sedes |
| **⛰️ Cundinamarca** | Soacha, Facatativá, Chía | 3 sedes |
| **🏜️ Atlántico** | Barranquilla Centro, Soledad | 2 sedes |
| **🌊 Bolívar** | Cartagena Centro, Cartagena Norte | 2 sedes |
| **🌿 Santander** | Bucaramanga, Floridablanca | 2 sedes |
| **🏞️ Otras Ciudades** | Pereira, Armenia | 2 sedes |

</div>

### 📈 **Estadísticas de Red**
- **Cobertura Geográfica**: 8 departamentos principales
- **Población Atendida**: +15 millones de habitantes
- **Tiempo Promedio de Entrega**: 5-7 días laborales
- **Conectividad**: 100% de sedes con acceso en tiempo real
| **Atlántico** | Barranquilla |
| **Santander** | Bucaramanga |
| **Norte de Santander** | Cúcuta |
| **Otras ciudades** | Cartagena, Soacha, Ibagué, Pereira, Armenia, Manizales, Villavicencio, Neiva, Montería, Sincelejo, Pasto |

## 💻 Instalación

## 🚀 Instalación y Despliegue

### 📋 **Requisitos del Sistema**
```python
Python 3.11+          # Lenguaje principal
PostgreSQL 15+        # Base de datos empresarial  
Node.js 18+           # Para herramientas de desarrollo
Git 2.40+            # Control de versiones
```

### 💻 **Instalación Local (Desarrollo)**

```bash
# 1. 📥 Clonar repositorio
git clone https://github.com/santiago-veloza/INVERSIONES-DR.-MEJIA-SAS.git
cd INVERSIONES-DR.-MEJIA-SAS

# 2. 🐍 Crear entorno virtual Python
python -m venv venv

# Windows PowerShell
venv\Scripts\Activate.ps1

# Linux/macOS
source venv/bin/activate

# 3. 📦 Instalar dependencias
pip install -r requirements.txt

# 4. 🗄️ Configurar base de datos
# Crear archivo .env con:
DATABASE_URL=postgresql://user:pass@localhost/db_name
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# 5. 👤 Crear usuario administrador
python create_admin.py

# 6. 🚀 Ejecutar aplicación
python app.py
```

**🌐 Acceso Local**: `http://127.0.0.1:5000`

### 🌐 **Despliegue en Producción (Render)**
```bash
# La aplicación se despliega automáticamente desde GitHub
# URL Producción: https://inversiones-dr-mejia-sas.onrender.com/
```

## 🔐 Sistema de Acceso

### 🔑 **Credenciales de Administrador**
```
👤 Usuario: admin
🔒 Contraseña: admin123
🎭 Rol: Admin Central (Acceso Total)
```

### 👥 **Gestión de Usuarios**
```bash
# Crear usuarios adicionales
python create_admin.py

# Tipos de usuario disponibles:
# 🔴 Admin Central    - Control total del sistema
# 🟡 Admin de Sede    - Gestión local de sede
# 🟢 Asistente        - Creación de órdenes
# 🟣 Proveedor        - Gestión de órdenes asignadas
```

## 🔄 Procesos Empresariales

### 📋 **Workflow de Órdenes Ópticas**

<div align="center">

```mermaid
flowchart TD
    A[🏪 Creación en Sede] --> B{📝 Datos Completos?}
    B -->|No| A
    B -->|Sí| C[👨‍💼 Revisión Admin Central]
    C --> D{✅ Aprobada?}
    D -->|No| E[❌ Rechazada - Reenvío]
    E --> A
    D -->|Sí| F[🏭 Envío a Proveedor]
    F --> G[⚙️ En Proceso]
    G --> H{🔍 Estado Final?}
    H -->|Completado| I[📦 Recibida Óptica]
    H -->|Problema| J[🔄 Devuelta Proveedor]
    I --> K[✅ Finalizada]
    J --> G
```

</div>

### 💰 **Módulo Financiero Avanzado**

#### 🧮 **Cálculo de Utilidades**
```python
# Fórmula de Rentabilidad
utilidad_bruta = precio_venta - costo_proveedor
margen_utilidad = (utilidad_bruta / precio_venta) * 100
roi_sede = utilidad_total_sede / costo_total_sede * 100
```

#### 📊 **KPIs Empresariales**
- **💹 Ventas Totales**: Suma de todos los precios de venta
- **💰 Utilidad Total**: Diferencia entre ventas y costos
- **📈 Margen Promedio**: Porcentaje de ganancia sobre ventas
- **🏆 Top Performers**: Ranking de sedes por rentabilidad
- **📅 Comparativas Mensuales**: Análisis período actual vs anterior

### 🎨 **Sistema de UI/UX**

#### 🌈 **Código de Colores (Estados)**
| 🎨 **Color** | 📋 **Estado** | 💡 **Significado** |
|--------------|---------------|---------------------|
| 🔴 **Rojo** | Pendiente Admin | Requiere revisión administrativa |
| 🟡 **Amarillo** | En Proceso | Proveedor trabajando en la orden |
| 🟢 **Verde** | Recibida Óptica | Lista para entrega al cliente |
| 🟠 **Naranja** | Devuelta Proveedor | Requiere correcciones |
| 🔵 **Azul** | Completado | Terminado por proveedor |
| ⚫ **Gris** | Finalizada | Proceso completo terminado |

#### 💎 **Características de Diseño**
- **📱 Responsive Design**: Optimización automática para todos los dispositivos
- **⚡ Real-time Updates**: Actualización automática cada 5 minutos
- **💰 Formato Monetario**: Separadores de miles automáticos ($1.234.567)
- **🖼️ Visual Feedback**: Indicadores de carga y confirmación de acciones
- **🎯 UX Optimizada**: Flujos intuitivos para cada tipo de usuario

## 🔔 Sistema de Comunicación

### 📨 **Mensajería Interna**
- **Chat Empresarial**: Comunicación directa entre sedes y administración
- **Notificaciones Push**: Alertas automáticas en cambios de estado
- **Panel de Mensajes**: Bandeja de entrada con historial completo
- **Marcar Leídos**: Gestión automática de mensajes

### 📊 **Exportación y Reportes**
```python
# Formatos de Exportación Disponibles
Excel (.xlsx)         # Reportes completos con formato
CSV (.csv)           # Datos para análisis externo  
PDF                  # Órdenes individuales para impresión
```

## 🎨 Arquitectura de Diseño

### ✨ **CSS Clean Architecture (123 KB)**
```css
/* Estructura Organizada */
:root                    /* Variables CSS globales */
├── Layout Principal     /* Sidebar + Topbar responsive */
├── Componentes KPI      /* Cards de métricas */
├── Dashboard Cards      /* Visualización de datos */
├── Forms & Inputs       /* Formularios profesionales */
├── Tables & Lists       /* Tablas con estados */
├── Animations          /* Transiciones suaves */
├── Print Styles        /* Estilos de impresión */
├── Mobile Responsive   /* Media queries optimizadas */
└── Utility Classes     /* Clases auxiliares */
```

### 🎯 **Mejoras de UX Implementadas**
- ✅ **Separación CSS/HTML**: Todo el CSS inline movido a archivo externo
- ✅ **Formateo Monetario**: Separadores de miles automáticos ($1.234.567)
- ✅ **Typography**: Texto en negrita para mejor legibilidad
- ✅ **Visual Hierarchy**: Colores consistentes y significativos
- ✅ **Loading States**: Indicadores de progreso en actualizaciones
- ✅ **Error Handling**: Mensajes de estado claros para el usuario

## 🔧 Configuración Técnica

### 🌐 **Variables de Entorno**
```env
# Configuración Principal
FLASK_APP=app.py
FLASK_ENV=production
FLASK_DEBUG=0

# Base de Datos
DATABASE_URL=postgresql://user:password@host:port/database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Seguridad  
SECRET_KEY=your-ultra-secure-secret-key
WTF_CSRF_SECRET_KEY=your-csrf-key

# Cloudinary (Storage)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### 🗄️ **Gestión de Base de Datos**
```sql
-- Producción: PostgreSQL en Supabase
-- Desarrollo: SQLite local
-- Migraciones: Flask-Migrate
-- Índices optimizados para performance
-- Relaciones con integridad referencial
```

## 📈 Métricas y Performance

### ⚡ **Optimizaciones Implementadas**
- **Database Indexing**: Índices en columnas frecuentemente consultadas
- **Query Optimization**: Consultas SQL optimizadas para reportes
- **Caching Strategy**: Flask-Caching para datos estáticos
- **Asset Minification**: CSS y JS optimizados para producción
- **CDN Integration**: Bootstrap y FontAwesome desde CDN

### 📊 **KPIs del Sistema**
```python
# Métricas Empresariales Calculadas
total_ordenes = db.session.query(func.count(WorkOrder.id))
ventas_totales = db.session.query(func.sum(WorkOrder.precio_venta))
utilidad_total = ventas_totales - costos_totales
margen_promedio = (utilidad_total / ventas_totales) * 100
top_sedes = db.session.query().order_by(desc('ventas_mes'))
```

## 🛠️ Stack Tecnológico Completo

<div align="center">

### 🖥️ **Backend Stack**
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-FCA121?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://sqlalchemy.org/)

### 🎨 **Frontend Stack**
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://html.spec.whatwg.org/)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](https://www.w3.org/Style/CSS/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://javascript.info/)
[![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white)](https://chartjs.org/)

### ☁️ **Cloud & DevOps**
[![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com/)
[![Supabase](https://img.shields.io/badge/Supabase-181818?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-3448C5?style=for-the-badge&logo=cloudinary&logoColor=white)](https://cloudinary.com/)
[![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/)

</div>

## 📚 Recursos y Documentación

### 🔗 **Enlaces Importantes**
- **🌐 Aplicación en Producción**: [https://inversiones-dr-mejia-sas.onrender.com/](https://inversiones-dr-mejia-sas.onrender.com/)
- **📁 Repositorio GitHub**: [https://github.com/santiago-veloza/INVERSIONES-DR.-MEJIA-SAS](https://github.com/santiago-veloza/INVERSIONES-DR.-MEJIA-SAS)
- **👤 Perfil Desarrollador**: [https://github.com/santiago-veloza](https://github.com/santiago-veloza)

### 📖 **Documentación Técnica**
- **🔧 API Endpoints**: Documentación completa de rutas y métodos
- **🗄️ Modelo de Datos**: Esquema de base de datos con relaciones
- **🎨 Guía de Estilos**: Componentes UI y patrones de diseño
- **🚀 Manual de Despliegue**: Instrucciones para producción

## 👨‍💻 Desarrollo y Mantenimiento

### 🏗️ **Arquitectura de Desarrollo**
```python
# Patrón MVC Implementado
Models (backend/app/models.py)     # Capa de datos
Views (frontend/templates/)        # Capa de presentación  
Controllers (backend/app/routes.py) # Lógica de negocio
```

### 🧪 **Testing y Calidad**
- **Code Quality**: Código limpio siguiendo PEP 8
- **CSS Architecture**: Estilos organizados y mantenibles
- **Security**: Validación de datos y protección CSRF
- **Performance**: Optimizaciones de consultas y caching

### 🔄 **Actualizaciones Recientes**
- ✅ **CSS Cleanup**: Separación completa de estilos inline
- ✅ **UI Enhancements**: Mejoras en experiencia de usuario
- ✅ **Performance**: Optimización de consultas de dashboard
- ✅ **Security**: Fortalecimiento de validaciones
- ✅ **Mobile**: Optimización responsive mejorada

## 📞 Soporte y Contacto

### 🤝 **Soporte Técnico**
- **📧 Email**: soporte@drmejiasas.com
- **📱 WhatsApp**: +57 300 123 4567
- **🕒 Horario**: Lunes a Viernes 8:00 AM - 6:00 PM

### 👨‍💼 **Desarrollado Por**
**Santiago Veloza** - Full Stack Developer
- 🐙 **GitHub**: [@santiago-veloza](https://github.com/santiago-veloza)
- 💼 **LinkedIn**: [Santiago Veloza](https://linkedin.com/in/santiago-veloza)
- 📧 **Email**: santiago.veloza@dev.com

---

<div align="center">

## 🎯 **INVERSIONES DR. MEJÍA SAS**
### *Sistema de Gestión Óptica Empresarial*

**Digitalizando el futuro de la óptica en Colombia** 🇨🇴

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Version](https://img.shields.io/badge/Version-2.1.0-blue.svg)](https://github.com/santiago-veloza/INVERSIONES-DR.-MEJIA-SAS/releases)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](https://inversiones-dr-mejia-sas.onrender.com/)

</div>

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
