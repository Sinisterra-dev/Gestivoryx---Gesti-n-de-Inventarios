"""
Tests de integración para la API Gestivoryx.
Usa una base de datos SQLite en memoria para no afectar datos reales.
"""
# Importa pytest para escribir tests y definir fixtures
import pytest
# Importa TestClient de FastAPI para simular requests HTTP a la API
from fastapi.testclient import TestClient
# Importa create_engine de SQLAlchemy para crear motor de base de datos para tests
from sqlalchemy import create_engine
# Importa sessionmaker para crear fábrica de sesiones de base de datos
from sqlalchemy.orm import sessionmaker
# Importa StaticPool para pool de conexiones estático (necesario para SQLite en memoria)
from sqlalchemy.pool import StaticPool

# Importa Base y get_db del módulo database
# Base: clase base de modelos ORM para crear tablas
# get_db: dependencia de FastAPI que inyecta sesión de base de datos
from app.database import Base, get_db
# Importa app de main.py para crear el cliente de tests
from app.main import app

# ── Test database (in-memory) ──────────────────────────────────────────────────
# URL de base de datos SQLite en memoria
# La base de datos en memoria existe solo mientras el proceso está activo
# Esto asegura que los tests no afecten la base de datos de desarrollo
TEST_DATABASE_URL = "sqlite://"

# Crea el motor de base de datos para tests
# connect_args={"check_same_thread": False}: permite acceso desde múltiples hilos
# poolclass=StaticPool: usa un pool estático (necesario para SQLite en memoria)
engine_test = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
# Crea fábrica de sesiones para tests
# autocommit=False: las transacciones no se confirman automáticamente
# autoflush=False: los cambios no se envían a la BD hasta hacer flush() o commit()
# bind=engine_test: vincula la sesión al motor de tests
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


# Función que sobrescribe la dependencia get_db para usar la base de datos de tests
# Esto permite que los endpoints usen la base de datos en memoria en lugar de la real
def override_get_db():
    # Crea una sesión de base de datos de tests
    db = TestingSessionLocal()
    try:
        # Yield la sesión para que el endpoint la use
        yield db
    finally:
        # Cierra la sesión después de que el endpoint termine
        # Se ejecuta tanto si el test tiene éxito como si falla
        db.close()


# Fixture de pytest que crea un cliente de tests con base de datos en memoria
# scope="module" significa que se ejecuta una vez por módulo (no por cada test)
@pytest.fixture(scope="module")
def client():
    # Crea todas las tablas en la base de datos de tests
    # Base.metadata contiene la metadata de todos los modelos importados
    Base.metadata.create_all(bind=engine_test)
    # Sobrescribe la dependencia get_db para usar override_get_db
    # Esto hace que todos los endpoints usen la BD en memoria
    app.dependency_overrides[get_db] = override_get_db
    # Crea usuario admin para tests (seed inicial)
    # Importa funciones necesarias dentro del fixture para evitar importaciones circulares
    from app.core.security import hash_password
    from app.models.models import Usuario

    # Crea sesión de base de datos de tests
    db = TestingSessionLocal()
    # Crea usuario admin con credenciales de test
    admin = Usuario(
        username="admin",
        email="admin@test.com",
        nombre="Admin",
        rol="admin",
        hashed_password=hash_password("admin123"),
    )
    # Agrega el usuario a la sesión y confirma
    db.add(admin)
    db.commit()
    # Cierra la sesión
    db.close()

    # Crea cliente de tests con la aplicación FastAPI
    # with statement asegura que el cliente se cierre después de los tests
    with TestClient(app) as c:
        # Yield el cliente para que los tests lo usen
        yield c

    # Limpieza después de todos los tests del módulo
    # Elimina todas las tablas de la base de datos de tests
    Base.metadata.drop_all(bind=engine_test)
    # Limpia las sobrescrituras de dependencias
    app.dependency_overrides.clear()


# Fixture de pytest que obtiene headers de autenticación para tests
# scope="module" se ejecuta una vez por módulo
@pytest.fixture(scope="module")
def auth_headers(client):
    # Usa el cliente de tests para hacer login
    resp = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    # Verifica que el login fue exitoso
    assert resp.status_code == 200
    # Extrae el token JWT de la respuesta
    token = resp.json()["access_token"]
    # Retorna headers con el token Bearer para usar en tests autenticados
    return {"Authorization": f"Bearer {token}"}


# ── Auth tests ─────────────────────────────────────────────────────────────────
class TestAuth:
    def test_login_correcto(self, client):
        resp = client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "admin123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["usuario"]["username"] == "admin"

    def test_login_incorrecto(self, client):
        resp = client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "wrong"},
        )
        assert resp.status_code == 401

    def test_me(self, client, auth_headers):
        resp = client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["username"] == "admin"

    def test_sin_token_401(self, client):
        resp = client.get("/api/productos/")
        assert resp.status_code == 401


# ── Categorías tests ───────────────────────────────────────────────────────────
class TestCategorias:
    def test_crear_categoria(self, client, auth_headers):
        resp = client.post(
            "/api/categorias/",
            json={"nombre": "Electrónica", "descripcion": "Productos electrónicos"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["nombre"] == "Electrónica"

    def test_listar_categorias(self, client, auth_headers):
        resp = client.get("/api/categorias/", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_duplicado_categoria(self, client, auth_headers):
        resp = client.post(
            "/api/categorias/",
            json={"nombre": "Electrónica"},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_actualizar_categoria(self, client, auth_headers):
        resp = client.put(
            "/api/categorias/1",
            json={"descripcion": "Actualizado"},
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_eliminar_categoria(self, client, auth_headers):
        # Create one to delete
        cat = client.post(
            "/api/categorias/",
            json={"nombre": "Temporal"},
            headers=auth_headers,
        )
        cat_id = cat.json()["id"]
        resp = client.delete(f"/api/categorias/{cat_id}", headers=auth_headers)
        assert resp.status_code == 204


# ── Proveedores tests ──────────────────────────────────────────────────────────
class TestProveedores:
    def test_crear_proveedor(self, client, auth_headers):
        resp = client.post(
            "/api/proveedores/",
            json={"nombre": "TechSupply", "telefono": "555-1234", "email": "tech@supply.com"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["nombre"] == "TechSupply"

    def test_listar_proveedores(self, client, auth_headers):
        resp = client.get("/api/proveedores/", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1


# ── Productos tests ────────────────────────────────────────────────────────────
class TestProductos:
    def test_crear_producto(self, client, auth_headers):
        resp = client.post(
            "/api/productos/",
            json={
                "codigo": "PROD001",
                "nombre": "Laptop HP",
                "precio_compra": 500.0,
                "precio_venta": 750.0,
                "stock": 10,
                "stock_minimo": 2,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["codigo"] == "PROD001"

    def test_codigo_duplicado(self, client, auth_headers):
        resp = client.post(
            "/api/productos/",
            json={
                "codigo": "PROD001",
                "nombre": "Otro",
                "precio_venta": 100.0,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_listar_productos(self, client, auth_headers):
        resp = client.get("/api/productos/", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_buscar_producto(self, client, auth_headers):
        resp = client.get("/api/productos/?q=Laptop", headers=auth_headers)
        assert resp.status_code == 200
        assert any("Laptop" in p["nombre"] for p in resp.json())

    def test_actualizar_producto(self, client, auth_headers):
        resp = client.put(
            "/api/productos/1",
            json={"precio_venta": 800.0},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["precio_venta"] == 800.0


# ── Clientes tests ─────────────────────────────────────────────────────────────
class TestClientes:
    def test_crear_cliente(self, client, auth_headers):
        resp = client.post(
            "/api/clientes/",
            json={"nombre": "Juan Pérez", "email": "juan@email.com", "telefono": "555-9999"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["nombre"] == "Juan Pérez"

    def test_listar_clientes(self, client, auth_headers):
        resp = client.get("/api/clientes/", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1


# ── Ventas tests ───────────────────────────────────────────────────────────────
class TestVentas:
    def test_crear_venta(self, client, auth_headers):
        resp = client.post(
            "/api/ventas/",
            json={
                "detalles": [{"producto_id": 1, "cantidad": 2}],
                "descuento": 0.0,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["total"] == 1600.0  # 2 * 800.0
        assert data["estado"] == "completada"
        assert len(data["detalles"]) == 1

    def test_stock_descuenta(self, client, auth_headers):
        prod = client.get("/api/productos/1", headers=auth_headers).json()
        assert prod["stock"] == 8  # 10 - 2

    def test_venta_sin_stock(self, client, auth_headers):
        resp = client.post(
            "/api/ventas/",
            json={"detalles": [{"producto_id": 1, "cantidad": 9999}]},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_listar_ventas(self, client, auth_headers):
        resp = client.get("/api/ventas/", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_anular_venta(self, client, auth_headers):
        # Create a sale to anull
        sale = client.post(
            "/api/ventas/",
            json={"detalles": [{"producto_id": 1, "cantidad": 1}]},
            headers=auth_headers,
        ).json()
        venta_id = sale["id"]
        resp = client.delete(f"/api/ventas/{venta_id}", headers=auth_headers)
        assert resp.status_code == 204
        # Verify stock was restored
        prod = client.get("/api/productos/1", headers=auth_headers).json()
        assert prod["stock"] == 8  # 8 - 1 (sale) + 1 (anulación) = 8


# ── Movimientos tests ──────────────────────────────────────────────────────────
class TestMovimientos:
    def test_entrada(self, client, auth_headers):
        resp = client.post(
            "/api/movimientos/",
            json={"producto_id": 1, "tipo": "entrada", "cantidad": 5, "motivo": "Reposición"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["tipo"] == "entrada"

    def test_ajuste(self, client, auth_headers):
        resp = client.post(
            "/api/movimientos/",
            json={"producto_id": 1, "tipo": "ajuste", "cantidad": 20, "motivo": "Conteo físico"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        prod = client.get("/api/productos/1", headers=auth_headers).json()
        assert prod["stock"] == 20

    def test_tipo_invalido(self, client, auth_headers):
        resp = client.post(
            "/api/movimientos/",
            json={"producto_id": 1, "tipo": "invalido", "cantidad": 1},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_listar_movimientos(self, client, auth_headers):
        resp = client.get("/api/movimientos/", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1


# ── Dashboard tests ────────────────────────────────────────────────────────────
class TestDashboard:
    def test_stats(self, client, auth_headers):
        resp = client.get("/api/dashboard/stats", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_productos" in data
        assert "ingresos_hoy" in data
        assert data["total_productos"] >= 1
