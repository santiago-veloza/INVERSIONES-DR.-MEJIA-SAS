🧾 Sistema de Gestión de Órdenes de Trabajo - Óptica
📘 Descripción General

El Sistema de Gestión de Órdenes de Trabajo es una solución desarrollada para optimizar la administración de procesos en una óptica, facilitando la comunicación entre la óptica y sus proveedores.
Permite registrar proveedores, gestionar órdenes con fórmulas ópticas, realizar pagos, generar reportes y visualizar estadísticas en un panel de control.

Este sistema mejora la trazabilidad de las órdenes, automatiza notificaciones sobre los cambios de estado (asignación, devolución, finalización y pago), y ofrece una interfaz diferenciada según el rol del usuario.

🚀 Resumen Ejecutivo del Reto

El sistema está diseñado para centralizar la gestión completa de órdenes de trabajo en una óptica, desde la creación hasta la finalización y pago.
Entre sus principales características se incluyen:

Registro y gestión de proveedores.

Creación de órdenes con fórmulas ópticas adjuntas.

Control de pagos y soportes.

Listado de órdenes pendientes.

Panel de control con estadísticas y gráficos.

Gestión de usuarios y roles diferenciados.

Generación de reportes detallados.

Envío automático de notificaciones sobre cambios de estado en las órdenes.

⚙️ Requisitos Funcionales
Nº	Requisito Funcional	Descripción
1	Registrar proveedores	Permite registrar, actualizar y consultar la información de los proveedores.
2	Registrar órdenes de trabajo	Posibilidad de crear órdenes dirigidas a proveedores, adjuntando las fórmulas ópticas correspondientes.
3	Registrar pago de órdenes	Permite registrar pagos realizados a proveedores sobre las órdenes enviadas.
4	Listar órdenes pendientes de pago	Muestra un listado de todas las órdenes que aún no han sido pagadas.
5	Adjuntar soporte de pago	Al registrar un pago, el usuario puede adjuntar el comprobante o soporte del mismo.
6	Panel de control con gráficos	Panel que muestra estadísticas y gráficos de trabajos enviados a proveedores y trabajos pendientes por devolución.
7	Rol Administrador	Permite ajustar paramétricas del sistema y gestionar usuarios (crear, editar, desactivar).
8	Rol Asistente (Óptica)	Puede crear órdenes, enviarlas al proveedor, registrar la recepción y registrar pagos.
9	Rol Proveedor	Puede ver órdenes recibidas, devolverlas a la óptica y acceder a un panel con estadísticas de sus órdenes (recibidas, en proceso, devueltas, pagadas o pendientes).
10	Generar reportes	Permite generar reportes detallados sobre las órdenes y los pagos asociados.
11	Notificaciones sobre estados de órdenes	El sistema envía notificaciones automáticas a:
• Proveedor: al recibir nuevas órdenes y al ser pagadas.
• Óptica (Asistente): al recibir órdenes devueltas o finalizadas por el proveedor.
👥 Roles del Sistema

Administrador: gestiona la configuración del sistema, usuarios y parámetros generales.

Asistente (Óptica): crea, envía y gestiona las órdenes de trabajo, incluyendo pagos y recepciones.

Proveedor: recibe y procesa las órdenes, registrando su devolución y verificando su estado de pago.

📊 Funcionalidades Destacadas

Dashboard interactivo: con indicadores visuales de productividad y cumplimiento.

Gestión documental: permite adjuntar comprobantes de pago o soportes ópticos.

Reportes descargables: en formatos como PDF o Excel.

Notificaciones en tiempo real: sobre cambios de estado en las órdenes.

Control de acceso por roles: seguridad y trazabilidad en las operaciones.

🧩 Tecnologías Sugeridas

(Esta sección puedes personalizarla según tu stack actual)

Backend: Python (Flask / Django)

Base de Datos: PostgreSQL / MySQL

Frontend: HTML5, CSS3, JavaScript / React

Autenticación: JWT / Login con roles

Gráficos: Chart.js o Recharts

Notificaciones: Sistema interno o integración con correo electrónico 