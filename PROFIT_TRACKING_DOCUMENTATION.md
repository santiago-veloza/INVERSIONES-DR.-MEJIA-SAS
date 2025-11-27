# Sistema de Seguimiento de Ganancias - Documentación

## Resumen de Cambios

Se ha implementado un sistema completo para rastrear el precio de venta al cliente y calcular las ganancias del negocio.

## Cambios Realizados

### 1. Base de Datos (models.py)
- **Nueva columna:** `sale_price` - Almacena el precio de venta al cliente final
- Ubicación: `backend/app/models.py` línea ~154
- Tipo: `db.Column(db.Float, nullable=True)`
- La columna se agregó exitosamente a la base de datos `site.db`

### 2. Formulario (forms.py)
- **Nuevo campo:** `sale_price` - Campo de entrada para el precio de venta
- Ubicación: `backend/app/forms.py` línea ~168
- Tipo: `FloatField` con validadores:
  - `Optional()` - El campo es opcional
  - `NumberRange(min=0)` - Solo acepta valores positivos
- Etiqueta: "Precio de Venta al Cliente"

### 3. Interfaz de Usuario (create_edit.html)
- **Nueva sección:** Campo de precio de venta en el formulario de órdenes
- Ubicación: `frontend/templates/ordenes/create_edit.html` líneas ~289-297
- Estilo: Card con fondo blanco, input centrado tipo number con decimales
- Ubicación en el formulario: Después de "Teléfono Paciente" y antes de los botones de acción

### 4. Backend - Rutas (routes.py)

#### Creación de Órdenes (línea ~1148)
```python
sale_price=form.sale_price.data,
```
Ahora guarda el precio de venta cuando se crea una nueva orden.

#### Edición de Órdenes (línea ~1264)
```python
order.sale_price = form.sale_price.data
```
Actualiza el precio de venta al editar una orden existente.

#### Dashboard - Cálculos de Ganancias (líneas ~539-602)
Se agregaron los siguientes cálculos:

**Totales del Sistema:**
- `total_revenue`: Suma de todos los precios de venta (órdenes pagadas)
- `total_costs`: Suma de todos los costos del proveedor (órdenes pagadas)
- `total_profit`: Ganancia total (revenue - costs)
- `profit_margin`: Margen de ganancia en porcentaje

**Este Mes:**
- `revenue_this_month`: Ventas del mes actual
- `costs_this_month`: Costos del mes actual
- `profit_this_month`: Ganancia del mes
- `profit_margin_month`: Margen del mes en porcentaje

### 5. Dashboard - Vista (dashboard.html)

Nueva sección "Análisis de Ganancias" ubicada después de "Estadísticas de Tipos de Lentes" (líneas ~196-263):

**Columna Izquierda - Totales del Sistema:**
- Ventas al Cliente (verde)
- Costo Proveedor (rojo)
- Ganancia Total (gradiente púrpura) con margen %

**Columna Derecha - Este Mes:**
- Ventas al Cliente (verde)
- Costo Proveedor (rojo)
- Ganancia del Mes (gradiente rosa) con margen %

**Diseño Visual:**
- Gradientes atractivos para las ganancias
- Separador vertical azul entre totales y mes actual
- Badges para mostrar el margen de ganancia
- Formato de moneda con separadores de miles

## Cómo Usar el Sistema

### Para Crear/Editar Órdenes:
1. En el formulario de orden, encontrarás el nuevo campo "PRECIO DE VENTA AL CLIENTE"
2. Ingresa el precio que se le cobró al cliente final
3. Este campo es opcional - puedes dejarlo vacío si no conoces el precio de venta aún
4. Acepta valores decimales (ej: 150000.50)

### Para Ver Ganancias en el Dashboard:
1. Accede al Dashboard Administrativo
2. Desplázate hasta la sección "Análisis de Ganancias"
3. Verás:
   - **Izquierda:** Estadísticas totales del sistema
   - **Derecha:** Estadísticas del mes actual
4. Las ganancias se calculan automáticamente como: **Precio de Venta - Costo del Proveedor**

## Notas Importantes

### Cálculo de Ganancias:
- Solo se incluyen órdenes con `payment_status = 'pagada'`
- Solo se incluyen órdenes que tienen `sale_price` definido (no NULL)
- La fórmula es: `Ganancia = sale_price - total_amount`

### Margen de Ganancia:
- Se calcula como: `(Ganancia / Ventas) × 100`
- Muestra el porcentaje de ganancia sobre las ventas totales
- Se redondea a 1 decimal

### Consideraciones:
- El campo `sale_price` es opcional para no afectar órdenes existentes
- Las órdenes antiguas sin precio de venta no afectarán los cálculos
- Puedes editar órdenes existentes para agregar el precio de venta

## Migración de Base de Datos

La columna `sale_price` fue agregada exitosamente a la tabla `work_order` en la base de datos `site.db`.

**Verificado:**
✅ Columna creada como FLOAT
✅ Permite valores NULL (opcional)
✅ Compatible con órdenes existentes

## Archivos Modificados

1. `backend/app/models.py` - Modelo de datos
2. `backend/app/forms.py` - Formulario de órdenes
3. `backend/app/routes.py` - Rutas (create_order, edit_order, admin_dashboard)
4. `frontend/templates/ordenes/create_edit.html` - Formulario de UI
5. `frontend/templates/admin/dashboard.html` - Dashboard con análisis de ganancias
6. `backend/instance/site.db` - Base de datos (nueva columna)

## Pruebas Sugeridas

1. ✅ Crear una nueva orden con precio de venta
2. ✅ Editar una orden existente para agregar precio de venta
3. ✅ Verificar que el dashboard muestra correctamente las ganancias
4. ✅ Confirmar que órdenes sin precio de venta no causan errores
5. ✅ Verificar que los cálculos son correctos comparando manualmente

## Mantenimiento Futuro

- Considera agregar validación para asegurar que `sale_price >= total_amount` (ganancia positiva)
- Podrías agregar alertas si el margen de ganancia es muy bajo
- Considera agregar gráficos de tendencia de ganancias por mes
- Podrías agregar análisis de ganancia por sede individual
