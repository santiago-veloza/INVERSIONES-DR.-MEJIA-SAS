# 🎨 Frontend - Sistema de Gestión Óptica

## 📁 Estructura del Frontend

```
frontend/
├── static/                # Archivos estáticos
│   ├── css/
│   │   └── styles.css     # Estilos personalizados
│   ├── js/                # JavaScript personalizado
│   ├── img/               # Imágenes del sistema
│   └── uploads/           # Archivos subidos por usuarios
└── templates/             # Plantillas HTML (Jinja2)
    ├── base.html          # Plantilla base
    ├── index.html         # Página principal
    ├── admin/             # Templates de administración
    ├── auth/              # Templates de autenticación
    ├── notifications/     # Templates de notificaciones
    ├── ordenes/           # Templates de órdenes
    ├── pagos/             # Templates de pagos
    ├── proveedores/       # Templates de proveedores
    └── reports/           # Templates de reportes
```

## 🎨 Tecnologías Utilizadas

- **Framework CSS**: Bootstrap 5.3
- **Template Engine**: Jinja2
- **JavaScript**: Vanilla JS + Bootstrap JS
- **Iconos**: Font Awesome 6
- **Formularios**: HTML5 + validación JavaScript

## 🖼️ Características del Frontend

### Diseño Responsivo
- Compatible con dispositivos móviles, tablets y escritorio
- Grid system de Bootstrap para layouts adaptativos
- Menús de navegación colapsables

### Interfaz por Roles
- **Admin Central**: Acceso completo a todas las funcionalidades
- **Admin de Sede**: Panel específico para gestión de su sede
- **Asistente**: Interfaz operativa simplificada
- **Proveedor**: Panel especializado para gestión de órdenes

### Componentes Interactivos
- **Dashboard** con estadísticas y gráficos
- **Formularios dinámicos** con validación en tiempo real
- **Modales** para confirmaciones y detalles
- **Notificaciones** toast y alertas
- **Tablas** con filtrado y ordenamiento
- **Carga de archivos** con previsualización

### Temas y Estilos
- Tema profesional con colores corporativos
- Consistencia visual en todos los módulos
- Animaciones sutiles para mejor UX
- Indicadores de estado con colores semánticos

## 🔧 Personalización

Los estilos se pueden personalizar editando:
- `static/css/styles.css` - Estilos personalizados
- `templates/base.html` - Estructura base y navegación
- Variables CSS de Bootstrap para temas globales

## 📱 Compatibilidad

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Dispositivos móviles iOS/Android




# 📊 Dashboard Administrativo Central - Documentación

## 🎯 Funcionalidades Implementadas

### 📈 **Estadísticas por Sede**
Cada sede muestra:
- **Órdenes Totales**: Todas las órdenes registradas
- **Órdenes del Mes**: Órdenes del mes actual
- **Órdenes Completadas**: Órdenes finalizadas (recibidas + finalizadas)
- **Órdenes en Progreso**: Enviadas, aceptadas, en proceso
- **Órdenes Listas**: Devueltas por proveedor, listas para recoger
- **Ventas del Mes**: Suma de costos de órdenes pagadas en el mes
- **Ventas Totales**: Suma total de ventas de la sede
- **Pagos Pendientes**: Dinero pendiente de pago por órdenes completadas
- **% de Completadas**: Tasa de finalización de órdenes
- **Días Promedio**: Tiempo promedio para completar órdenes

### 🏆 **Rankings y Top Performers**
- **Top 5 Sedes por Ventas del Mes**
- **Top 5 Sedes por Número de Órdenes del Mes**
- Ordenamiento visual con posiciones

### 📊 **Estadísticas del Sistema**
- Total de sedes activas
- Órdenes totales del sistema
- Órdenes del mes actual
- Ventas totales acumuladas
- Ventas del mes actual
- Total de pagos pendientes

### 🛠️ **Funcionalidades Interactivas**

#### 📋 **Tabla Ordenable**
- Click en cualquier columna para ordenar
- Ordenamiento automático por números (descendente)
- Ordenamiento alfabético para texto

#### 🔄 **Actualización en Tiempo Real**
- Botón "Actualizar" para refrescar estadísticas
- Auto-refresh cada 5 minutos
- API endpoint: `/api/admin/stats`

#### 📤 **Exportación de Datos**
- **Excel**: Descarga completa en formato .xlsx
- **CSV**: Fallback si Excel no está disponible
- **Imprimir**: Formato optimizado para impresión

#### 👁️ **Detalles por Sede**
- Botón "Ver detalles" en cada fila
- API endpoint: `/api/admin/sede/<id>`
- Datos históricos de 6 meses

### 🎨 **Indicadores Visuales**

#### 🎯 **Barras de Progreso**
- **Verde (≥80%)**: Excelente tasa de completadas
- **Amarillo (60-79%)**: Tasa moderada
- **Rojo (<60%)**: Necesita atención

#### 🏷️ **Badges de Estado**
- **Días Promedio**:
  - Verde: ≤3 días (excelente)
  - Amarillo: 4-7 días (bueno)
  - Rojo: >7 días (lento)

#### 💰 **Formato de Moneda**
- Formato con separadores de miles: $1,234,567
- Colores diferenciados por tipo de valor

### 🔗 **Navegación**

#### 📱 **Menú Principal**
- Admin Central → Dashboard Detallado

#### 🏠 **Panel Principal**
- Banner especial para administradores
- Acceso directo con botón destacado

#### 🔗 **Enlaces Directos**
- Ver órdenes específicas de cada sede
- Acceso rápido a gestión de usuarios

### 🌐 **API Endpoints**

#### `/api/admin/stats`
```json
{
  "total_orders": 150,
  "orders_this_month": 25,
  "pending_orders": 10,
  "timestamp": "2025-10-21T..."
}
```

#### `/api/admin/sede/<id>`
```json
{
  "sede": {
    "id": 1,
    "name": "Sede Bogotá Centro",
    "city": "Bogotá",
    "manager": "María García"
  },
  "months_data": [
    {
      "month": "5/2025",
      "orders": 12,
      "sales": 2500000
    }
  ]
}
```

### 📱 **Responsive Design**
- Optimizado para desktop, tablet y móvil
- Tabla con scroll horizontal en pantallas pequeñas
- Cards reorganizables según el tamaño de pantalla

### 🎯 **Casos de Uso Principales**

#### 📊 **Análisis de Rendimiento**
1. Identificar sedes con mejor rendimiento
2. Detectar sedes que necesitan atención
3. Comparar ventas entre sedes
4. Monitorear tiempos de entrega

#### 💼 **Toma de Decisiones**
1. Reasignación de recursos
2. Identificación de mejores prácticas
3. Planificación de capacitación
4. Gestión de inventarios

#### 📈 **Reportes Ejecutivos**
1. Exportación de datos para presentaciones
2. Impresión de reportes mensuales
3. Tracking de KPIs principales
4. Análisis de tendencias

### 🔐 **Seguridad**
- Acceso restringido solo a rol 'admin'
- Decorador `@role_required('admin')`
- Validación de permisos en todas las rutas

### 🚀 **Próximas Mejoras Sugeridas**
- Gráficos interactivos con Chart.js
- Filtros por rango de fechas
- Comparación entre períodos
- Alertas automáticas por bajo rendimiento
- Dashboard móvil dedicado
- Notificaciones push para administradores

---

## 🎮 **Cómo Usar**

1. **Acceso**: Login como admin → Menu "Admin Central" → "Dashboard Detallado"
2. **Navegación**: Click en columnas para ordenar
3. **Actualización**: Botón "Actualizar" para datos en tiempo real
4. **Exportación**: Botones Excel/CSV para descargar datos
5. **Detalles**: Botón "👁️" en cada sede para ver más información

¡El dashboard está completamente funcional y listo para usar! 🎉