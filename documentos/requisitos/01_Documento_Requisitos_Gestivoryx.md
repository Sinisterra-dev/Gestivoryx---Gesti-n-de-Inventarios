# Documento de Requisitos de Software — Gestivoryx

**Proyecto:** Gestivoryx – Sistema de Gestión de Inventarios  
**Versión:** 1.0  
**Estado:** Documento de definición de requisitos  
**Responsable:** Alexander Sinisterra  - Claudia Rojas
**Tipo de proyecto:** Desarrollo grupal / proyecto académico con proyección comercial  
**Fecha de elaboración:** Fecha entrega 1 bitácora

---

## 1. Introducción

Gestivoryx es un sistema de gestión de inventarios orientado a pequeñas y medianas empresas (PYMEs). El proyecto surge de la necesidad de contar con una herramienta que permita centralizar y facilitar la administración de productos, existencias, categorías, proveedores, clientes, ventas y movimientos de inventario.

El presente documento establece los requisitos identificados para el desarrollo de Gestivoryx. Estos requisitos representan la definición funcional y técnica considerada como base para la construcción del sistema.

---

## 2. Descripción general del proyecto

Gestivoryx busca proporcionar una aplicación web que permita a una PYME administrar sus operaciones básicas relacionadas con el inventario desde un único sistema.

El sistema contempla autenticación de usuarios, control de acceso mediante roles, administración de información comercial, registro de ventas, actualización de existencias y consulta de estadísticas generales.

---

## 3. Problema identificado

Las pequeñas y medianas empresas pueden presentar dificultades para controlar de manera organizada sus productos y movimientos de inventario cuando utilizan procesos manuales, archivos independientes o herramientas que no integran la información.

Entre las necesidades identificadas se encuentran:

- Mantener información organizada de los productos.
- Controlar las cantidades disponibles.
- Registrar entradas, salidas y ajustes de inventario.
- Gestionar proveedores y clientes.
- Registrar ventas y actualizar existencias.
- Controlar el acceso de los usuarios al sistema.
- Disponer de información general para consultar el estado del negocio.

---

## 4. Objetivo general

Desarrollar un sistema de gestión de inventarios que permita a una PYME administrar de manera centralizada sus productos, categorías, proveedores, clientes, ventas, movimientos de inventario y usuarios.

---

## 5. Objetivos específicos

- Permitir la autenticación segura de los usuarios.
- Gestionar productos y sus cantidades disponibles.
- Organizar productos mediante categorías.
- Registrar y administrar proveedores.
- Registrar y administrar clientes.
- Registrar ventas y actualizar automáticamente el inventario.
- Registrar entradas, salidas y ajustes de inventario.
- Administrar usuarios de acuerdo con sus roles.
- Proporcionar estadísticas generales mediante un dashboard.
- Facilitar la consulta y búsqueda de productos.

---

## 6. Alcance

### 6.1 Incluido en el alcance

El sistema contempla los siguientes módulos:

- Autenticación.
- Productos.
- Categorías.
- Proveedores.
- Clientes.
- Ventas.
- Movimientos de inventario.
- Usuarios.
- Dashboard.

El sistema incluye una API REST, persistencia de información en base de datos, autenticación mediante JWT, control de roles y una interfaz web para interactuar con las funcionalidades principales.

### 6.2 Fuera del alcance inicial

No forman parte del alcance inicial:

- Facturación electrónica.
- Integración con sistemas contables externos.
- Aplicaciones móviles nativas.
- Integración con dispositivos físicos de punto de venta.
- Procesamiento de pagos en línea.
- Inteligencia artificial para predicción de inventario.

Estas funcionalidades podrían considerarse en futuras versiones.

---

## 7. Actores del sistema

### Administrador

Usuario con permisos de administración. Puede gestionar usuarios y acceder a las funcionalidades administrativas del sistema.

### Usuario

Usuario operativo que puede utilizar las funcionalidades permitidas por su rol para consultar y gestionar información del inventario y las operaciones comerciales.

---

# 8. Requisitos funcionales

| ID | Requisito | Prioridad |
|---|---|---|
| RF-01 | El sistema debe permitir iniciar sesión mediante nombre de usuario y contraseña. | Alta |
| RF-02 | El sistema debe permitir consultar la información del usuario autenticado. | Media |
| RF-03 | El sistema debe permitir crear productos. | Alta |
| RF-04 | El sistema debe permitir consultar productos. | Alta |
| RF-05 | El sistema debe permitir actualizar productos. | Alta |
| RF-06 | El sistema debe permitir eliminar productos. | Media |
| RF-07 | El sistema debe permitir buscar y filtrar productos, incluyendo productos con bajo stock. | Alta |
| RF-08 | El sistema debe permitir crear, consultar, actualizar y eliminar categorías. | Alta |
| RF-09 | El sistema debe permitir crear, consultar, actualizar y eliminar proveedores. | Alta |
| RF-10 | El sistema debe permitir crear, consultar, actualizar y eliminar clientes. | Alta |
| RF-11 | El sistema debe permitir registrar ventas. | Alta |
| RF-12 | El sistema debe descontar automáticamente las existencias correspondientes al registrar una venta. | Alta |
| RF-13 | El sistema debe permitir anular ventas. | Media |
| RF-14 | El sistema debe registrar movimientos de inventario. | Alta |
| RF-15 | El sistema debe permitir consultar el historial de movimientos de inventario. | Alta |
| RF-16 | El sistema debe permitir administrar usuarios. | Alta |
| RF-17 | El sistema debe restringir determinadas operaciones de administración a usuarios con rol administrador. | Alta |
| RF-18 | El sistema debe mostrar estadísticas generales del negocio mediante un dashboard. | Media |

---

# 9. Requisitos no funcionales

| ID | Requisito | Prioridad |
|---|---|---|
| RNF-01 | El sistema debe utilizar autenticación basada en tokens JWT. | Alta |
| RNF-02 | Las contraseñas deben almacenarse utilizando un mecanismo de hashing seguro. | Alta |
| RNF-03 | El sistema debe implementar control de acceso basado en roles. | Alta |
| RNF-04 | La API debe utilizar una arquitectura basada en servicios REST. | Alta |
| RNF-05 | Los datos recibidos por la API deben ser validados antes de ser procesados. | Alta |
| RNF-06 | El sistema debe mantener una separación entre modelos, esquemas y rutas de la aplicación. | Media |
| RNF-07 | El sistema debe poder ejecutarse en un entorno local sin requerir un servidor de base de datos externo en su configuración inicial. | Media |
| RNF-08 | La aplicación debe contar con una interfaz web que permita utilizar las funcionalidades principales. | Alta |
| RNF-09 | La API debe contar con documentación interactiva para facilitar su consulta y pruebas. | Media |

---

# 10. Reglas de negocio

| ID | Regla |
|---|---|
| RN-01 | Un usuario debe autenticarse antes de acceder a las funcionalidades protegidas del sistema. |
| RN-02 | Las operaciones administrativas de usuarios deben estar restringidas al rol administrador. |
| RN-03 | Una venta registrada debe afectar las existencias de los productos vendidos. |
| RN-04 | Los movimientos de inventario deben permitir identificar entradas, salidas o ajustes. |
| RN-05 | Los productos deben estar asociados a la información necesaria para su identificación y control de existencias. |
| RN-06 | El sistema debe impedir que usuarios sin los permisos correspondientes ejecuten operaciones restringidas. |

---

# 11. Restricciones

- El backend será desarrollado utilizando Python y FastAPI.
- La persistencia inicial utilizará SQLite.
- La comunicación del backend se realizará mediante una API REST.
- La autenticación utilizará JWT.
- El frontend inicial utilizará HTML, CSS y JavaScript sin frameworks obligatorios.
- El sistema debe poder ejecutarse en un entorno local.
- Las tecnologías y componentes podrán evolucionar en futuras versiones del proyecto.

---

# 12. Criterios generales de aceptación

El sistema se considerará funcionalmente aceptable cuando:

1. Un usuario pueda autenticarse correctamente.
2. Los usuarios puedan realizar las operaciones permitidas según su rol.
3. Se puedan gestionar productos y categorías.
4. Se puedan gestionar proveedores y clientes.
5. Se puedan registrar ventas.
6. Las ventas actualicen correctamente el stock.
7. Se puedan registrar y consultar movimientos de inventario.
8. El administrador pueda gestionar usuarios.
9. Las operaciones protegidas no estén disponibles para usuarios sin autorización.
10. El dashboard muestre información general del inventario y las operaciones.
11. Los datos enviados al sistema sean validados.
12. La API pueda ser consultada y probada mediante su documentación interactiva.

---

# 13. Tecnologías previstas

- **Lenguaje:** Python 3.10+
- **Framework backend:** FastAPI
- **ORM:** SQLAlchemy 2.x
- **Base de datos:** SQLite
- **Validación:** Pydantic v2
- **Autenticación:** JWT
- **Hashing de contraseñas:** bcrypt
- **Servidor ASGI:** Uvicorn
- **Frontend:** HTML, CSS y JavaScript

---

# 14. Control de versiones del documento

| Versión | Fecha | Descripción | Responsable |
|---|---|---|---|
| 1.0 | 11/08/2026 | Elaboración inicial del documento de requisitos. | Alexander Sinisterra |

---

## 15. Aprobación

**Responsable de la definición de requisitos:**  
Alexander Sinisterra

**Rol:**  
Desarrollador / responsable del proyecto

**Proyecto:**  
Gestivoryx – Sistema de Gestión de Inventarios

> Este documento representa la reconstrucción de la definición de requisitos utilizada como base conceptual para el desarrollo de Gestivoryx.
