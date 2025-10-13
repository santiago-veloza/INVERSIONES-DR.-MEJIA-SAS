🧾 Sistema de Gestión de Órdenes de Trabajo - Óptica
📘 Descripción General

El Sistema de Gestión de Órdenes de Trabajo es una aplicación desarrollada para optimizar los procesos administrativos de una óptica, facilitando la comunicación entre esta y sus proveedores.
El sistema permite registrar proveedores, gestionar órdenes con fórmulas ópticas, realizar pagos, generar reportes y visualizar estadísticas a través de un panel de control.

Con esta solución se busca mejorar la trazabilidad de las órdenes, automatizar las notificaciones sobre los cambios de estado (asignación, devolución, finalización y pago), y ofrecer una interfaz adaptada a los distintos roles de usuario.

🚀 Resumen Ejecutivo del Reto

El proyecto tiene como propósito centralizar la gestión completa de las órdenes de trabajo en una óptica, desde su creación hasta su cierre y pago.
Entre sus principales características se destacan:

Registro y administración de proveedores.

Creación de órdenes con fórmulas ópticas adjuntas.

Registro y control de pagos y soportes.

Listado de órdenes pendientes de pago.

Panel de control con estadísticas y gráficos informativos.

Gestión de usuarios con roles diferenciados.

Generación de reportes detallados.

Notificaciones automáticas sobre los diferentes estados de las órdenes.

⚙️ Requisitos Funcionales
Nº	Requisito Funcional	Descripción
1	Registrar proveedores	El sistema permite registrar, actualizar y consultar la información de los proveedores.
2	Registrar órdenes de trabajo	Permite crear órdenes de trabajo dirigidas a proveedores, adjuntando las fórmulas ópticas correspondientes.
3	Registrar pago de órdenes	Permite registrar los pagos realizados a proveedores sobre las órdenes enviadas.
4	Listar órdenes pendientes de pago	Muestra un listado de todas las órdenes que aún no han sido pagadas.
5	Adjuntar soporte de pago	Al registrar un pago, se puede adjuntar el comprobante o soporte del mismo.
6	Panel de control con gráficos	Ofrece un panel con estadísticas y gráficos sobre trabajos enviados y pendientes por devolución.
7	Rol Administrador	Permite ajustar las configuraciones del sistema y gestionar usuarios (crear, editar o desactivar).
8	Rol Asistente (Óptica)	Permite crear órdenes de trabajo, enviarlas al proveedor, registrar la recepción y los pagos correspondientes.
9	Rol Proveedor	Permite consultar las órdenes recibidas, registrar devoluciones y acceder a un panel con estadísticas sobre órdenes recibidas, en proceso, devueltas y su estado de pago.
10	Generar reportes	Permite generar reportes detallados sobre las órdenes y los pagos asociados.
11	Notificaciones sobre estados de órdenes	El sistema cuenta con notificaciones automáticas para:
• Proveedores: cuando se les asignan nuevas órdenes y cuando estas son pagadas.
• Óptica (Asistente): cuando las órdenes son devueltas o finalizadas por el proveedor.
👥 Roles del Sistema

Administrador: Gestiona la configuración general del sistema y la administración de usuarios.

Asistente (Óptica): Se encarga de crear, enviar y gestionar las órdenes de trabajo, además de registrar pagos y recepciones.

Proveedor: Recibe, procesa y devuelve las órdenes, verificando su estado de pago mediante su propio panel de control.

📊 Funcionalidades Destacadas

Panel de control interactivo: Incluye indicadores visuales sobre productividad y estado de las órdenes.

Gestión documental: Permite adjuntar comprobantes de pago y soportes ópticos.

Reportes descargables: Ofrece reportes detallados en formatos como PDF o Excel.

Notificaciones automáticas: Informa en tiempo real los cambios de estado en las órdenes.

Control de acceso por roles: Garantiza la seguridad y trazabilidad de todas las operaciones realizadas.

🧩 Tecnologías Sugeridas

(Esta sección puede ajustarse según la implementación real del proyecto.)

Backend: Python (Flask / Django)

Base de Datos: PostgreSQL / MySQL

Frontend: HTML5, CSS3, JavaScript / React

Autenticación: JWT / Login con roles

Gráficos: Chart.js o Recharts

Notificaciones: Sistema interno o integración con correo electrónico