# Gestivoryx – Gestión de Inventarios

**Gestivoryx** es un sistema de gestión de inventario para PYMEs construido con **Python + FastAPI + SQLite**.  
Incluye una API REST completa con autenticación JWT, control de roles y un frontend HTML/CSS/JS listo para usar.

---

## 🔖 Estado

- **Estado:** WIP (en evolución activa hacia producción)
- **Propósito:** MVP para PYMEs → evolución a producto comercial
- **Propietario:** Alexander Sinisterra

---

## 📌 Módulos del sistema

| Módulo        | Descripción                                       |
|---------------|---------------------------------------------------|
| Auth          | Login con JWT, información del usuario autenticado |
| Productos     | CRUD, búsqueda y filtro de bajo stock             |
| Categorías    | CRUD de categorías de productos                   |
| Proveedores   | CRUD de proveedores                               |
| Clientes      | CRUD de clientes                                  |
| Ventas        | Crear venta (descuenta stock automáticamente), anular |
| Movimientos   | Entradas, salidas y ajustes de inventario         |
| Usuarios      | CRUD de usuarios (solo admin)                     |
| Dashboard     | Estadísticas generales del negocio                |

---

## 🧭 Stack tecnológico

### Backend
- **Python 3.10+**
- **FastAPI** – framework web async
- **SQLAlchemy 2.x** – ORM
- **SQLite** – base de datos (sin dependencias externas)
- **Pydantic v2** – validación de datos
- **python-jose** – generación y verificación de JWT
- **passlib + bcrypt** – hashing de contraseñas
- **Uvicorn** – servidor ASGI

### Frontend
- **HTML / CSS / JavaScript** (vanilla)
- Páginas: login, admin, productos, categorías, proveedores, clientes, ventas, usuarios, ajustes

---

## 📁 Estructura del proyecto

```
Gestivoryx/
├── backend/
│   ├── app/
│   │   ├── main.py              # Punto de entrada, monta todos los routers
│   │   ├── database.py          # Conexión SQLAlchemy + SQLite
│   │   ├── core/
│   │   │   ├── config.py        # Variables de entorno
│   │   │   ├── security.py      # Hashing y JWT
│   │   │   └── deps.py          # Dependencias FastAPI (auth, roles)
│   │   ├── models/
│   │   │   └── models.py        # Modelos SQLAlchemy (ORM)
│   │   ├── schemas/
│   │   │   └── schemas.py       # Esquemas Pydantic (validación)
│   │   └── routers/
│   │       ├── auth.py
│   │       ├── productos.py
│   │       ├── categorias.py
│   │       ├── proveedores.py
│   │       ├── clientes.py
│   │       ├── ventas.py
│   │       ├── movimientos.py
│   │       ├── usuarios.py
│   │       └── dashboard.py
│   ├── tests/
│   │   └── test_api.py          # Tests de integración
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── login.html
    ├── admin.html
    ├── lista_productos.html
    ├── categorias.html
    ├── proveedores.html
    ├── clientes.html
    ├── ventas.html
    ├── usuarios.html
    ├── ajustes.html
    └── assets/
```

---

## 🚀 Instalación y ejecución local

### Requisitos
- Python 3.10 o superior
- No se necesita instalar ninguna base de datos (SQLite se crea automáticamente)

### Instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd Gestivoryx

# 2. Crear y activar el entorno virtual
cd backend
python -m venv venv
source venv/bin/activate        # Linux / Mac
# .\venv\Scripts\Activate.ps1   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
```

### Variables de entorno (`.env`)

```env
SECRET_KEY=cambia-esto-en-produccion-usa-una-clave-segura-de-64-caracteres
DATABASE_URL=sqlite:///./gestivoryx.db
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256
APP_PORT=3000
ALLOWED_ORIGINS=*
```

### Ejecutar el servidor

```bash
uvicorn app.main:app --reload --port 3000
```

La API estará disponible en: **http://localhost:3000**  
Documentación interactiva (Swagger): **http://localhost:3000/docs**

### Usuario administrador por defecto

| Campo    | Valor      |
|----------|------------|
| Username | `admin`    |
| Password | `admin123` |
| Rol      | admin      |

> ⚠️ Cambiar la contraseña del admin en producción.

---

## 🔌 Endpoints principales

**Base URL:** `http://localhost:3000`

| Módulo      | Método | Ruta                          | Descripción                        |
|-------------|--------|-------------------------------|------------------------------------|
| Auth        | POST   | `/api/auth/login`             | Obtener token JWT                  |
| Auth        | GET    | `/api/auth/me`                | Datos del usuario autenticado      |
| Productos   | GET    | `/api/productos`              | Listar productos                   |
| Productos   | POST   | `/api/productos`              | Crear producto                     |
| Productos   | PUT    | `/api/productos/{id}`         | Actualizar producto                |
| Productos   | DELETE | `/api/productos/{id}`         | Eliminar producto                  |
| Categorías  | GET    | `/api/categorias`             | Listar categorías                  |
| Proveedores | GET    | `/api/proveedores`            | Listar proveedores                 |
| Clientes    | GET    | `/api/clientes`               | Listar clientes                    |
| Ventas      | POST   | `/api/ventas`                 | Registrar venta (descuenta stock)  |
| Movimientos | GET    | `/api/movimientos`            | Ver historial de movimientos       |
| Usuarios    | GET    | `/api/usuarios`               | Listar usuarios (solo admin)       |
| Dashboard   | GET    | `/api/dashboard/stats`        | Estadísticas del negocio           |

La documentación completa de todos los endpoints está disponible en **http://localhost:3000/docs**.

---

## 🔒 Seguridad

- Autenticación con **JWT** (Bearer token)
- Contraseñas hasheadas con **bcrypt**
- Control de roles: `admin` y `usuario`
- CORS configurable mediante variable de entorno `ALLOWED_ORIGINS`

---

## 🧪 Tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## 🧠 Principios de diseño

- Separación clara de responsabilidades (routers / schemas / models)
- Validaciones centralizadas con Pydantic v2
- Arquitectura preparada para escalar (fácil migración a PostgreSQL)
- API documentada automáticamente con Swagger y ReDoc
- Base sólida para autenticación y control de roles

---

## 🛡️ Consideraciones para producción

- Cambiar `SECRET_KEY` por una clave segura de 64+ caracteres
- Reemplazar SQLite por PostgreSQL para mayor concurrencia
- Configurar `ALLOWED_ORIGINS` con los dominios reales
- Agregar rate limiting y logs estructurados
- Desplegar con Docker y/o un reverse proxy (Nginx)
- Habilitar HTTPS obligatorio

---

## 🛣️ Roadmap

- [x] CRUD completo de los módulos principales
- [x] Autenticación JWT con control de roles
- [x] Tests de integración
- [ ] Migración opcional a PostgreSQL
- [ ] Despliegue en entorno productivo (Docker / cloud)
- [ ] Optimización y mejoras del frontend
- [ ] Observabilidad y métricas

---

## 🤝 Contribuciones

Este proyecto es propiedad privada.  
Las contribuciones externas requieren autorización expresa del propietario.

---

## 📜 Licencia

**Proprietary – Todos los derechos reservados**

Este software es propiedad exclusiva de Alexander Sinisterra.  
No está permitido copiar, redistribuir, sublicenciar ni usar este código con fines comerciales sin autorización expresa por escrito del autor.

---

## 👤 Autor

**Alexander Sinisterra**  
Estudiante de Ingeniería en Sistemas  
Desarrollador backend en Python  
Proyecto personal con proyección comercial
