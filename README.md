# Gestivoryx – Gestión de Clientes

**Gestivoryx** — API backend en Python para gestión básica de clientes (CRUD).  
Proyecto pensado para aprendizaje acelerado con enfoque real de producción: arquitectura modular, buenas prácticas y preparación para vender/operar en entornos reales.

---

## 🔖 Estado
- **Estado:** WIP (producción-ready en evolución)
- **Propósito:** MVP para PYMEs → evolución a producto comercial
- **Propietario:** Alexander Sinisterra

---

## 📌 Funcionalidad principal
Gestión de clientes mediante una API REST:

- Crear cliente
- Listar clientes
- Obtener cliente por ID
- Actualizar cliente
- Eliminar cliente

**Modelo de cliente**
- Nombre
- Email
- Teléfono
- Empresa

---

## 🧭 Tecnologías

### Backend
- Python 3.10+
- FastAPI
- MongoDB
- Motor (driver async)
- Pydantic
- Uvicorn

### Frontend
- HTML / CSS / JavaScript
- Frontend existente con integración progresiva
- Posible migración futura a Angular / SPA

---

## 📁 Estructura del repositorio
gestion-clientes/
├─ backend/
│ ├─ app/
│ │ ├─ routers/
│ │ ├─ models/
│ │ ├─ crud/
│ │ ├─ core/
│ │ └─ main.py
│ ├─ requirements.txt
│ ├─ .env.example
│ └─ README-backend.md
└─ frontend/
├─ assets/
├─ css/
├─ js/
├─ *.html
└─ README-frontend.md


---

## 🚀 Ejecución local (desarrollo)

### Requisitos
- Python 3.10 o superior
- MongoDB (local o en la nube)

### Instalación
```bash
cd gestion-clientes/backend
python -m venv venv
source venv/bin/activate      # Linux / Mac
# .\venv\Scripts\Activate.ps1 # Windows
pip install -r requirements.txt
cp .env.example .env
Variables de entorno mínimas
MONGO_URI=mongodb://localhost:27017/gestivoryx
DATABASE_NAME=gestivoryx
APP_PORT=3000
Ejecutar API
uvicorn app.main:app --reload --port 3000
Documentación automática
Swagger UI:
http://localhost:3000/docs

🔌 Endpoints principales
Base URL:

http://localhost:3000/api/clientes
Crear cliente
POST /api/clientes
Listar clientes
GET /api/clientes
Obtener cliente por ID
GET /api/clientes/{id}
Actualizar cliente
PUT /api/clientes/{id}
Eliminar cliente
DELETE /api/clientes/{id}
🧠 Principios de diseño
Separación clara de responsabilidades

Validaciones centralizadas con Pydantic

Arquitectura preparada para escalar

API documentada automáticamente

Enfoque asincrónico end-to-end

Base sólida para autenticación y roles

🛡️ Consideraciones para producción
Autenticación JWT

Control de roles (admin / usuario)

CORS y rate limiting

Manejo centralizado de errores

Logs estructurados

Backups de base de datos

HTTPS obligatorio

Despliegue con Docker y/o reverse proxy

🧪 Testing y calidad
Tests unitarios con pytest

Tests de integración para la API

Preparado para CI/CD

Linting y formateo automático

🛣️ Roadmap
Validaciones avanzadas

Autenticación y autorización

Manejo robusto de errores

Tests automatizados

Despliegue en entorno productivo

Optimización del frontend

Observabilidad y métricas

🤝 Contribuciones
Este proyecto es propiedad privada.
Las contribuciones externas requieren autorización expresa del propietario.

📜 Licencia
Proprietary – Todos los derechos reservados

Este software es propiedad exclusiva de Alexander Sinisterra.
No está permitido copiar, redistribuir, sublicenciar ni usar este código con fines comerciales sin autorización expresa por escrito del autor.

👤 Autor
Alexander Sinisterra
Estudiante de Ingeniería en Sistemas
Desarrollador backend en Python
Proyecto personal con proyección comercial
