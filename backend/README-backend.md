# Gestivoryx – Backend API

API REST completa para el sistema de gestión de inventario Gestivoryx, construida con **Python + FastAPI + SQLite**.

---

## 🚀 Inicio rápido

### Requisitos
- Python 3.10+

### Instalación

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Linux / Mac
# .\venv\Scripts\Activate.ps1   # Windows

pip install -r requirements.txt
cp .env.example .env            # Ajustar variables si se desea
```

### Ejecutar el servidor

```bash
uvicorn app.main:app --reload --port 3000
```

La API estará disponible en: http://localhost:3000  
Documentación interactiva (Swagger): http://localhost:3000/docs  

### Usuario por defecto
| Campo     | Valor       |
|-----------|-------------|
| Username  | `admin`     |
| Password  | `admin123`  |
| Rol       | admin       |

---

## 📋 Módulos del sistema

| Módulo        | Endpoint base           | Descripción                              |
|---------------|-------------------------|------------------------------------------|
| Auth          | `/api/auth`             | Login JWT, información del usuario       |
| Productos     | `/api/productos`        | CRUD + búsqueda + filtro bajo stock      |
| Categorías    | `/api/categorias`       | CRUD de categorías de productos          |
| Proveedores   | `/api/proveedores`      | CRUD de proveedores                      |
| Clientes      | `/api/clientes`         | CRUD de clientes                         |
| Ventas        | `/api/ventas`           | Crear venta (descuenta stock), anular    |
| Movimientos   | `/api/movimientos`      | Entradas, salidas y ajustes de inventario|
| Usuarios      | `/api/usuarios`         | CRUD de usuarios (solo admin)            |
| Dashboard     | `/api/dashboard/stats`  | Estadísticas del negocio                 |

---

## 🧪 Tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## 🔧 Variables de entorno (`.env`)

```env
SECRET_KEY=cambia-esto-en-produccion
DATABASE_URL=sqlite:///./gestivoryx.db
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256
APP_PORT=3000
```

---

## 🏗️ Estructura del proyecto

```
backend/
├── app/
│   ├── main.py              # Punto de entrada, monta todos los routers
│   ├── database.py          # Conexión SQLAlchemy + SQLite
│   ├── core/
│   │   ├── config.py        # Variables de entorno
│   │   ├── security.py      # Hashing, JWT
│   │   └── deps.py          # Dependencias FastAPI (auth, roles)
│   ├── models/
│   │   └── models.py        # Modelos SQLAlchemy (ORM)
│   ├── schemas/
│   │   └── schemas.py       # Esquemas Pydantic (validación)
│   └── routers/
│       ├── auth.py
│       ├── productos.py
│       ├── categorias.py
│       ├── proveedores.py
│       ├── clientes.py
│       ├── ventas.py
│       ├── movimientos.py
│       ├── usuarios.py
│       └── dashboard.py
├── tests/
│   └── test_api.py          # 28 tests de integración
├── requirements.txt
└── .env.example
```

---

## 🔒 Seguridad

- Autenticación con JWT (Bearer token)
- Contraseñas hasheadas con bcrypt
- Control de roles: `admin` y `usuario`
- CORS habilitado (configurable para producción)

---

## 👤 Autor

**Alexander Sinisterra**  
Estudiante de Ingeniería en Sistemas  
Proyecto educativo con proyección comercial  

---

## 📜 Licencia

Proprietary — Todos los derechos reservados.  
© 2025 Alexander Sinisterra
