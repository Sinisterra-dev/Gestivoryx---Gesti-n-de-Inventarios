# Importa datetime para campos de fecha en los esquemas
from datetime import datetime
# Importa Optional para typing de valores que pueden ser None
from typing import Optional

# Importa BaseModel, EmailStr y field_validator de Pydantic
# BaseModel: clase base para definir esquemas de validación de datos
# EmailStr: tipo especial que valida que el string sea un email válido
# field_validator: decorador para validadores personalizados de campos
from pydantic import BaseModel, EmailStr, field_validator


# ============================================================
# Token
# ============================================================
# Esquema para la respuesta del endpoint de login
# Contiene el token JWT y la información del usuario autenticado
class Token(BaseModel):
    # Token JWT de acceso generado tras login exitoso
    access_token: str
    # Tipo de token (siempre "bearer" para autenticación HTTP Bearer)
    token_type: str = "bearer"
    # Información del usuario autenticado (sigue el esquema UsuarioOut)
    usuario: "UsuarioOut"


# Esquema para los datos decodificados de un token JWT
# Usado internamente para validar el payload del token
class TokenData(BaseModel):
    # Username extraído del subject ("sub") del token
    username: Optional[str] = None


# ============================================================
# Usuario
# ============================================================
# Esquema base con campos comunes de usuario
# Usado como base para otros esquemas de usuario
class UsuarioBase(BaseModel):
    # Nombre de usuario único para login
    username: str
    # Correo electrónico validado como email válido
    email: EmailStr
    # Nombre completo del usuario
    nombre: str
    # Rol del usuario ("admin" o "usuario") con valor por defecto "usuario"
    rol: str = "usuario"


# Esquema para crear un nuevo usuario
# Hereda de UsuarioBase y agrega el campo password
class UsuarioCreate(UsuarioBase):
    # Contraseña en texto plano (será hasheada antes de almacenarse)
    password: str

    # Validador personalizado para la contraseña
    # Se ejecuta automáticamente cuando se valida este esquema
    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        # Verifica que la contraseña tenga al menos 6 caracteres
        if len(v) < 6:
            # Si no cumple el mínimo, lanza un error de validación
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        # Si la validación pasa, retorna el valor
        return v


# Esquema para actualizar un usuario existente
# Todos los campos son opcionales para permitir actualizaciones parciales
class UsuarioUpdate(BaseModel):
    # Email opcional a actualizar
    email: Optional[EmailStr] = None
    # Nombre opcional a actualizar
    nombre: Optional[str] = None
    # Rol opcional a actualizar
    rol: Optional[str] = None
    # Estado activo/inactivo opcional a actualizar
    activo: Optional[bool] = None
    # Contraseña opcional a actualizar (si se proporciona, se hashea)
    password: Optional[str] = None


# Esquema para la respuesta de datos de usuario
# Contiene los campos que se retornan al cliente (sin contraseña)
class UsuarioOut(BaseModel):
    # ID del usuario en la base de datos
    id: int
    # Nombre de usuario
    username: str
    # Correo electrónico
    email: str
    # Nombre completo
    nombre: str
    # Rol del usuario
    rol: str
    # Estado activo/inactivo
    activo: bool
    # Fecha y hora de creación del usuario
    creado_en: datetime

    # Configuración que permite crear instancias desde objetos ORM
    # from_attributes=True permite que Pydantic lea atributos de modelos SQLAlchemy
    model_config = {"from_attributes": True}


# ============================================================
# Categoria
# ============================================================
# Esquema base con campos comunes de categoría
class CategoriaBase(BaseModel):
    # Nombre de la categoría
    nombre: str
    # Descripción opcional de la categoría
    descripcion: Optional[str] = None


# Esquema para crear una nueva categoría
# Hereda todos los campos de CategoriaBase
class CategoriaCreate(CategoriaBase):
    pass


# Esquema para actualizar una categoría existente
# Todos los campos son opcionales para permitir actualizaciones parciales
class CategoriaUpdate(BaseModel):
    # Nombre opcional a actualizar
    nombre: Optional[str] = None
    # Descripción opcional a actualizar
    descripcion: Optional[str] = None
    # Estado activo/inactivo opcional a actualizar
    activo: Optional[bool] = None


# Esquema para la respuesta de datos de categoría
class CategoriaOut(CategoriaBase):
    # ID de la categoría
    id: int
    # Estado activo/inactivo
    activo: bool
    # Fecha y hora de creación
    creado_en: datetime

    # Configuración para crear instancias desde objetos ORM
    model_config = {"from_attributes": True}


# ============================================================
# Proveedor
# ============================================================
# Esquema base con campos comunes de proveedor
class ProveedorBase(BaseModel):
    # Nombre del proveedor
    nombre: str
    # Nombre de la persona de contacto (opcional)
    contacto: Optional[str] = None
    # Número de teléfono (opcional)
    telefono: Optional[str] = None
    # Correo electrónico (opcional)
    email: Optional[str] = None
    # Dirección física (opcional)
    direccion: Optional[str] = None


# Esquema para crear un nuevo proveedor
# Hereda todos los campos de ProveedorBase
class ProveedorCreate(ProveedorBase):
    pass


# Esquema para actualizar un proveedor existente
# Todos los campos son opcionales para permitir actualizaciones parciales
class ProveedorUpdate(BaseModel):
    # Nombre opcional a actualizar
    nombre: Optional[str] = None
    # Contacto opcional a actualizar
    contacto: Optional[str] = None
    # Teléfono opcional a actualizar
    telefono: Optional[str] = None
    # Email opcional a actualizar
    email: Optional[str] = None
    # Dirección opcional a actualizar
    direccion: Optional[str] = None
    # Estado activo/inactivo opcional a actualizar
    activo: Optional[bool] = None


# Esquema para la respuesta de datos de proveedor
class ProveedorOut(ProveedorBase):
    # ID del proveedor
    id: int
    # Estado activo/inactivo
    activo: bool
    # Fecha y hora de creación
    creado_en: datetime

    # Configuración para crear instancias desde objetos ORM
    model_config = {"from_attributes": True}


# ============================================================
# Producto
# ============================================================
# Esquema base con campos comunes de producto
class ProductoBase(BaseModel):
    # Código único del producto
    codigo: str
    # Nombre del producto
    nombre: str
    # Descripción del producto (opcional)
    descripcion: Optional[str] = None
    # Precio de compra al proveedor (por defecto 0.0)
    precio_compra: float = 0.0
    # Precio de venta a clientes (obligatorio)
    precio_venta: float
    # Stock actual (por defecto 0)
    stock: int = 0
    # Stock mínimo para alertas (por defecto 5)
    stock_minimo: int = 5
    # Unidad de medida (opcional)
    unidad: Optional[str] = None
    # ID de la categoría asociada (opcional)
    categoria_id: Optional[int] = None
    # ID del proveedor asociado (opcional)
    proveedor_id: Optional[int] = None


# Esquema para crear un nuevo producto
# Hereda todos los campos de ProductoBase
class ProductoCreate(ProductoBase):
    pass


# Esquema para actualizar un producto existente
# Todos los campos son opcionales para permitir actualizaciones parciales
class ProductoUpdate(BaseModel):
    # Código opcional a actualizar
    codigo: Optional[str] = None
    # Nombre opcional a actualizar
    nombre: Optional[str] = None
    # Descripción opcional a actualizar
    descripcion: Optional[str] = None
    # Precio de compra opcional a actualizar
    precio_compra: Optional[float] = None
    # Precio de venta opcional a actualizar
    precio_venta: Optional[float] = None
    # Stock opcional a actualizar
    stock: Optional[int] = None
    # Stock mínimo opcional a actualizar
    stock_minimo: Optional[int] = None
    # Unidad opcional a actualizar
    unidad: Optional[str] = None
    # Categoría opcional a actualizar
    categoria_id: Optional[int] = None
    # Proveedor opcional a actualizar
    proveedor_id: Optional[int] = None
    # Estado activo/inactivo opcional a actualizar
    activo: Optional[bool] = None


# Esquema para la respuesta de datos de producto
# Incluye relaciones anidadas de categoría y proveedor
class ProductoOut(ProductoBase):
    # ID del producto
    id: int
    # Estado activo/inactivo
    activo: bool
    # Fecha y hora de creación
    creado_en: datetime
    # Fecha y hora de última actualización
    actualizado_en: datetime
    # Categoría asociada (si existe)
    categoria: Optional[CategoriaOut] = None
    # Proveedor asociado (si existe)
    proveedor: Optional[ProveedorOut] = None

    # Configuración para crear instancias desde objetos ORM
    model_config = {"from_attributes": True}


# ============================================================
# Cliente
# ============================================================
# Esquema base con campos comunes de cliente
class ClienteBase(BaseModel):
    # Nombre del cliente
    nombre: str
    # Correo electrónico (opcional)
    email: Optional[str] = None
    # Número de teléfono (opcional)
    telefono: Optional[str] = None
    # Número de documento (opcional)
    documento: Optional[str] = None
    # Dirección física (opcional)
    direccion: Optional[str] = None


# Esquema para crear un nuevo cliente
# Hereda todos los campos de ClienteBase
class ClienteCreate(ClienteBase):
    pass


# Esquema para actualizar un cliente existente
# Todos los campos son opcionales para permitir actualizaciones parciales
class ClienteUpdate(BaseModel):
    # Nombre opcional a actualizar
    nombre: Optional[str] = None
    # Email opcional a actualizar
    email: Optional[str] = None
    # Teléfono opcional a actualizar
    telefono: Optional[str] = None
    # Documento opcional a actualizar
    documento: Optional[str] = None
    # Dirección opcional a actualizar
    direccion: Optional[str] = None
    # Estado activo/inactivo opcional a actualizar
    activo: Optional[bool] = None


# Esquema para la respuesta de datos de cliente
class ClienteOut(ClienteBase):
    # ID del cliente
    id: int
    # Estado activo/inactivo
    activo: bool
    # Fecha y hora de creación
    creado_en: datetime

    # Configuración para crear instancias desde objetos ORM
    model_config = {"from_attributes": True}


# ============================================================
# Venta
# ============================================================
# Esquema para crear un detalle de venta (producto en una venta)
# Usado dentro del esquema VentaCreate
class DetalleVentaCreate(BaseModel):
    # ID del producto a vender
    producto_id: int
    # Cantidad del producto a vender
    cantidad: int
    # Precio unitario opcional (si no se envía, usa precio_venta del producto)
    precio_unitario: Optional[float] = None  # si no se envía, usa precio_venta del producto


# Esquema para la respuesta de datos de detalle de venta
# Incluye la información del producto asociado
class DetalleVentaOut(BaseModel):
    # ID del detalle
    id: int
    # ID del producto
    producto_id: int
    # Cantidad vendida
    cantidad: int
    # Precio unitario usado
    precio_unitario: float
    # Subtotal calculado (cantidad × precio_unitario)
    subtotal: float
    # Producto asociado con todos sus datos
    producto: Optional[ProductoOut] = None

    # Configuración para crear instancias desde objetos ORM
    model_config = {"from_attributes": True}


# Esquema para crear una nueva venta
# Incluye la cabecera de la venta y la lista de detalles
class VentaCreate(BaseModel):
    # ID del cliente asociado (opcional, permite ventas al público general)
    cliente_id: Optional[int] = None
    # Descuento general de la venta (por defecto 0.0)
    descuento: float = 0.0
    # Notas adicionales (opcional)
    notas: Optional[str] = None
    # Lista de detalles (productos) de la venta
    detalles: list[DetalleVentaCreate]


# Esquema para la respuesta de datos de venta
# Incluye relaciones anidadas de cliente, usuario y detalles con productos
class VentaOut(BaseModel):
    # ID de la venta
    id: int
    # Número único de venta
    numero: str
    # Total de la venta después de descuentos
    total: float
    # Monto de descuento aplicado
    descuento: float
    # Estado de la venta ("completada" o "anulada")
    estado: str
    # Notas adicionales
    notas: Optional[str]
    # Fecha y hora de creación
    creado_en: datetime
    # Cliente asociado (si existe)
    cliente: Optional[ClienteOut] = None
    # Usuario que registró la venta
    usuario: Optional[UsuarioOut] = None
    # Lista de detalles de la venta con productos
    detalles: list[DetalleVentaOut] = []

    # Configuración para crear instancias desde objetos ORM
    model_config = {"from_attributes": True}


# ============================================================
# Movimiento de Inventario
# ============================================================
# Esquema para crear un movimiento de inventario manual
class MovimientoCreate(BaseModel):
    # ID del producto cuyo stock se modificará
    producto_id: int
    # Tipo de movimiento ("entrada", "salida" o "ajuste")
    tipo: str  # entrada | salida | ajuste
    # Cantidad del movimiento
    cantidad: int
    # Motivo o descripción del movimiento (opcional)
    motivo: Optional[str] = None


# Esquema para la respuesta de datos de movimiento
# Incluye relaciones anidadas de producto y usuario
class MovimientoOut(BaseModel):
    # ID del movimiento
    id: int
    # Tipo de movimiento
    tipo: str
    # Cantidad del movimiento
    cantidad: int
    # Stock antes del movimiento
    stock_anterior: int
    # Stock después del movimiento
    stock_nuevo: int
    # Motivo del movimiento
    motivo: Optional[str]
    # Fecha y hora de creación
    creado_en: datetime
    # Producto asociado
    producto: Optional[ProductoOut] = None
    # Usuario que registró el movimiento
    usuario: Optional[UsuarioOut] = None

    # Configuración para crear instancias desde objetos ORM
    model_config = {"from_attributes": True}


# ============================================================
# Dashboard
# ============================================================
# Esquema para las estadísticas del dashboard
# Contiene múltiples métricas del negocio en un solo objeto
class DashboardStats(BaseModel):
    # Total de productos activos en inventario
    total_productos: int
    # Total de clientes activos registrados
    total_clientes: int
    # Total de proveedores activos registrados
    total_proveedores: int
    # Número de ventas completadas hoy
    ventas_hoy: int
    # Total de ingresos (suma de ventas) de hoy
    ingresos_hoy: float
    # Total de ingresos del mes actual
    ingresos_mes: float
    # Número de productos con stock bajo (stock <= stock_minimo)
    productos_bajo_stock: int
    # Número total de ventas completadas este mes
    total_ventas_mes: int
