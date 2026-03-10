# Gestión de inventario (Gestivoryx)
# Autores: Alexander Sinisterra
# Tecnologías: Python, FastAPI, SQLAlchemy, SQLite

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models import models  # noqa: F401 – registers all ORM models
from app.routers import auth, categorias, clientes, dashboard, movimientos, productos, proveedores, usuarios, ventas

# ── Create all tables ──────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)


def _seed_admin():
    """Create a default admin user if no users exist."""
    from app.models.models import Usuario

    db = SessionLocal()
    try:
        if db.query(Usuario).count() == 0:
            admin = Usuario(
                username="admin",
                email="admin@gestivoryx.com",
                nombre="Administrador",
                rol="admin",
                hashed_password=hash_password("admin123"),
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


_seed_admin()

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Gestivoryx – Gestión de Inventario",
    description="API REST para gestión de inventario, ventas, clientes y más.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(categorias.router)
app.include_router(proveedores.router)
app.include_router(productos.router)
app.include_router(clientes.router)
app.include_router(ventas.router)
app.include_router(movimientos.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "API Gestivoryx – Gestión de Inventario",
        "docs": "/docs",
        "version": "1.0.0",
    }
