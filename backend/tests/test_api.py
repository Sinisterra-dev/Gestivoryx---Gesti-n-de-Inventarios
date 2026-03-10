"""
Tests de integración para la API Gestivoryx.
Usa una base de datos SQLite en memoria para no afectar datos reales.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# ── Test database (in-memory) ──────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite://"

engine_test = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine_test)
    app.dependency_overrides[get_db] = override_get_db
    # Seed admin user for tests
    from app.core.security import hash_password
    from app.models.models import Usuario

    db = TestingSessionLocal()
    admin = Usuario(
        username="admin",
        email="admin@test.com",
        nombre="Admin",
        rol="admin",
        hashed_password=hash_password("admin123"),
    )
    db.add(admin)
    db.commit()
    db.close()

    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=engine_test)
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def auth_headers(client):
    resp = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
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
