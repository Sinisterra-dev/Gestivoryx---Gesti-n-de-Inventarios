from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


# ============================================================
# Token
# ============================================================
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: "UsuarioOut"


class TokenData(BaseModel):
    username: Optional[str] = None


# ============================================================
# Usuario
# ============================================================
class UsuarioBase(BaseModel):
    username: str
    email: EmailStr
    nombre: str
    rol: str = "usuario"


class UsuarioCreate(UsuarioBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v


class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nombre: Optional[str] = None
    rol: Optional[str] = None
    activo: Optional[bool] = None
    password: Optional[str] = None


class UsuarioOut(BaseModel):
    id: int
    username: str
    email: str
    nombre: str
    rol: str
    activo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}


# ============================================================
# Categoria
# ============================================================
class CategoriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


class CategoriaOut(CategoriaBase):
    id: int
    activo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}


# ============================================================
# Proveedor
# ============================================================
class ProveedorBase(BaseModel):
    nombre: str
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None


class ProveedorOut(ProveedorBase):
    id: int
    activo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}


# ============================================================
# Producto
# ============================================================
class ProductoBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    precio_compra: float = 0.0
    precio_venta: float
    stock: int = 0
    stock_minimo: int = 5
    unidad: Optional[str] = None
    categoria_id: Optional[int] = None
    proveedor_id: Optional[int] = None


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_compra: Optional[float] = None
    precio_venta: Optional[float] = None
    stock: Optional[int] = None
    stock_minimo: Optional[int] = None
    unidad: Optional[str] = None
    categoria_id: Optional[int] = None
    proveedor_id: Optional[int] = None
    activo: Optional[bool] = None


class ProductoOut(ProductoBase):
    id: int
    activo: bool
    creado_en: datetime
    actualizado_en: datetime
    categoria: Optional[CategoriaOut] = None
    proveedor: Optional[ProveedorOut] = None

    model_config = {"from_attributes": True}


# ============================================================
# Cliente
# ============================================================
class ClienteBase(BaseModel):
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    documento: Optional[str] = None
    direccion: Optional[str] = None


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    documento: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None


class ClienteOut(ClienteBase):
    id: int
    activo: bool
    creado_en: datetime

    model_config = {"from_attributes": True}


# ============================================================
# Venta
# ============================================================
class DetalleVentaCreate(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: Optional[float] = None  # si no se envía, usa precio_venta del producto


class DetalleVentaOut(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float
    producto: Optional[ProductoOut] = None

    model_config = {"from_attributes": True}


class VentaCreate(BaseModel):
    cliente_id: Optional[int] = None
    descuento: float = 0.0
    notas: Optional[str] = None
    detalles: list[DetalleVentaCreate]


class VentaOut(BaseModel):
    id: int
    numero: str
    total: float
    descuento: float
    estado: str
    notas: Optional[str]
    creado_en: datetime
    cliente: Optional[ClienteOut] = None
    usuario: Optional[UsuarioOut] = None
    detalles: list[DetalleVentaOut] = []

    model_config = {"from_attributes": True}


# ============================================================
# Movimiento de Inventario
# ============================================================
class MovimientoCreate(BaseModel):
    producto_id: int
    tipo: str  # entrada | salida | ajuste
    cantidad: int
    motivo: Optional[str] = None


class MovimientoOut(BaseModel):
    id: int
    tipo: str
    cantidad: int
    stock_anterior: int
    stock_nuevo: int
    motivo: Optional[str]
    creado_en: datetime
    producto: Optional[ProductoOut] = None
    usuario: Optional[UsuarioOut] = None

    model_config = {"from_attributes": True}


# ============================================================
# Dashboard
# ============================================================
class DashboardStats(BaseModel):
    total_productos: int
    total_clientes: int
    total_proveedores: int
    ventas_hoy: int
    ingresos_hoy: float
    ingresos_mes: float
    productos_bajo_stock: int
    total_ventas_mes: int
