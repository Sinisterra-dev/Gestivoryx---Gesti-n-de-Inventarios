# Gestión de inventario (Gestivoryx)
# Autores: Alexander Sinisterra
# Tecnologías: Python, FastAPI, SQLAlchemy, SQLite

# Importa FastAPI para crear la aplicación web y la API REST
# FastAPI es el framework principal que maneja rutas, middleware y dependencias
from fastapi import FastAPI
# Importa CORSMiddleware para habilitar CORS (Cross-Origin Resource Sharing)
# Esto permite que el frontend (en otro dominio) pueda consumir la API
from fastapi.middleware.cors import CORSMiddleware

# Importa settings de config.py para obtener configuración (puerto, orígenes CORS, etc.)
from app.core.config import settings
# Importa hash_password de security.py para hashear la contraseña del admin por defecto
from app.core.security import hash_password
# Importa Base, SessionLocal y engine de database.py para operaciones de base de datos
# Base se usa para crear tablas, SessionLocal para sesiones, engine para conexión
from app.database import Base, SessionLocal, engine
# Importa todos los modelos ORM (models.py)
# El comentario noqa: F401 indica que la importación es intencional aunque no se use directamente
# Al importar models, todos los modelos se registran con SQLAlchemy, lo que permite crear las tablas
from app.models import models  # noqa: F401 – registers all ORM models
# Importa todos los routers que contienen los endpoints de la API
# Cada router maneja un módulo específico (auth, productos, ventas, etc.)
from app.routers import auth, categorias, clientes, dashboard, movimientos, productos, proveedores, usuarios, ventas

# ── Create all tables ──────────────────────────────────────────────────────────
# Crea todas las tablas en la base de datos si no existen
# Base.metadata contiene la metadata de todos los modelos importados
# bind=engine especifica el motor de conexión a usar
# Esto se ejecuta al iniciar la aplicación para asegurar que el esquema esté actualizado
Base.metadata.create_all(bind=engine)


# Función que crea un usuario administrador por defecto si no existe ningún usuario
# Esta función se ejecuta al iniciar la aplicación para asegurar que siempre haya un admin
# Es útil para el primer acceso al sistema cuando la base de datos está vacía
def _seed_admin():
    """Create a default admin user if no users exist."""
    # Importa el modelo Usuario dentro de la función para evitar importación circular
    from app.models.models import Usuario

    # Crea una sesión de base de datos para consultar y crear el usuario admin
    db = SessionLocal()
    try:
        # Verifica si no existe ningún usuario en la base de datos
        # count() retorna el número total de registros en la tabla usuarios
        if db.query(Usuario).count() == 0:
            # Crea un usuario administrador con credenciales por defecto
            # username: admin, password: admin123 (hasheado con bcrypt)
            admin = Usuario(
                username="admin",
                email="admin@gestivoryx.com",
                nombre="Administrador",
                rol="admin",
                hashed_password=hash_password("admin123"),
            )
            # Agrega el usuario a la sesión de base de datos
            db.add(admin)
            # Confirma la transacción para persistir el usuario en la base de datos
            db.commit()
    finally:
        # Cierra la sesión de base de datos siempre, incluso si hay una excepción
        db.close()


# Ejecuta la función _seed_admin() para crear el usuario admin por defecto
# Esto se ejecuta al iniciar la aplicación antes de que se acepten requests
_seed_admin()

# ── App ────────────────────────────────────────────────────────────────────────
# Crea la instancia de la aplicación FastAPI
# title: nombre de la API que aparece en la documentación Swagger
# description: descripción de la API que aparece en la documentación
# version: versión de la API para control de cambios
app = FastAPI(
    title="Gestivoryx – Gestión de Inventario",
    description="API REST para gestión de inventario, ventas, clientes y más.",
    version="1.0.0",
)

# Agrega middleware CORS para permitir solicitudes desde otros dominios
# Esto es necesario para que el frontend (que puede estar en otro dominio) pueda consumir la API
# allow_origins=["*"] permite solicitudes desde cualquier origen (configurar apropiadamente en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
# Incluye todos los routers en la aplicación principal
# Cada router contiene los endpoints de un módulo específico
# FastAPI genera automáticamente la documentación Swagger basándose en estos routers
app.include_router(auth.router)          # Endpoints de autenticación (login, me)
app.include_router(usuarios.router)      # Endpoints de gestión de usuarios
app.include_router(categorias.router)   # Endpoints de gestión de categorías
app.include_router(proveedores.router)   # Endpoints de gestión de proveedores
app.include_router(productos.router)    # Endpoints de gestión de productos
app.include_router(clientes.router)      # Endpoints de gestión de clientes
app.include_router(ventas.router)       # Endpoints de gestión de ventas
app.include_router(movimientos.router)  # Endpoints de historial de movimientos
app.include_router(dashboard.router)    # Endpoints de estadísticas del dashboard


# Endpoint raíz GET / que retorna información básica de la API
# Este endpoint es útil para verificar que la API está funcionando correctamente
# Retorna un JSON con estado, mensaje, enlace a documentación y versión
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "API Gestivoryx – Gestión de Inventario",
        "docs": "/docs",
        "version": "1.0.0",
    }