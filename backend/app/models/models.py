# Importa datetime y timezone para manejo de fechas y horas con zona horaria UTC
from datetime import datetime, timezone
# Importa Optional para typing de valores que pueden ser None
from typing import Optional

# Importa tipos de datos SQLAlchemy para definir columnas de las tablas
# Boolean: valores verdadero/falso
# DateTime: fechas y horas
# Float: números decimales (para precios)
# ForeignKey: claves foráneas para relaciones entre tablas
# Integer: números enteros (para IDs, cantidades, stock)
# String: cadenas de texto con longitud máxima
# Text: texto largo sin límite de longitud
# func: funciones de SQL (como NOW(), SUM(), etc.)
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
# Importa Mapped, mapped_column y relationship de SQLAlchemy ORM
# Mapped: anotación de tipo para campos del modelo
# mapped_column: define una columna de la tabla con sus propiedades
# relationship: define relaciones entre modelos (uno a muchos, muchos a uno)
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Importa Base de database.py
# Base es la clase base de la que heredan todos los modelos ORM
# Al heredar de Base, SQLAlchemy puede mapear las clases a tablas de base de datos
from app.database import Base


# Función auxiliar que retorna la fecha y hora actual en UTC
# Se usa como valor por defecto para campos de timestamp (creado_en, actualizado_en)
# Usar UTC asegura consistencia global y evita problemas con zonas horarias
def utcnow():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Usuario
# ---------------------------------------------------------------------------
# Modelo ORM que representa la tabla "usuarios" en la base de datos
# Almacena información de usuarios del sistema con autenticación y roles
# Relacionado con: Venta (un usuario puede tener muchas ventas), Movimiento (un usuario puede tener muchos movimientos)
class Usuario(Base):
    # Nombre de la tabla en la base de datos
    __tablename__ = "usuarios"

    # Columna id: clave primaria entera con índice para búsquedas rápidas
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Columna username: nombre de usuario único con índice para búsquedas
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    # Columna email: correo electrónico único con índice para búsquedas
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    # Columna nombre: nombre completo del usuario
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    # Columna hashed_password: contraseña hasheada con bcrypt (almacenada de forma segura)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)
    # Columna rol: rol del usuario ("admin" o "usuario") con valor por defecto "usuario"
    rol: Mapped[str] = mapped_column(String(20), default="usuario")  # admin | usuario
    # Columna activo: indica si el usuario está activo (True) o desactivado (False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    # Columna creado_en: fecha y hora de creación del registro en UTC
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    # Columna actualizado_en: fecha y hora de última actualización
    # onupdate=utcnow actualiza automáticamente este campo cuando se modifica el registro
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    # Relación uno a muchos: un usuario puede tener muchas ventas
    # back_populates="usuario" indica que el modelo Venta tiene una relación inversa llamada "usuario"
    ventas: Mapped[list["Venta"]] = relationship("Venta", back_populates="usuario")
    # Relación uno a muchos: un usuario puede tener muchos movimientos de inventario
    # back_populates="usuario" indica que el modelo Movimiento tiene una relación inversa llamada "usuario"
    movimientos: Mapped[list["Movimiento"]] = relationship("Movimiento", back_populates="usuario")


# ---------------------------------------------------------------------------
# Categoria
# ---------------------------------------------------------------------------
# Modelo ORM que representa la tabla "categorias" en la base de datos
# Almacena categorías para organizar productos
# Relacionado con: Producto (una categoría puede tener muchos productos)
class Categoria(Base):
    # Nombre de la tabla en la base de datos
    __tablename__ = "categorias"

    # Columna id: clave primaria entera con índice
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Columna nombre: nombre de la categoría único (no puede haber dos categorías con el mismo nombre)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    # Columna descripcion: descripción opcional de la categoría (puede ser None)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Columna activo: indica si la categoría está activa (True) o desactivada (False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    # Columna creado_en: fecha y hora de creación del registro en UTC
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Relación uno a muchos: una categoría puede tener muchos productos
    # back_populates="categoria" indica que el modelo Producto tiene una relación inversa llamada "categoria"
    productos: Mapped[list["Producto"]] = relationship("Producto", back_populates="categoria")


# ---------------------------------------------------------------------------
# Proveedor
# ---------------------------------------------------------------------------
# Modelo ORM que representa la tabla "proveedores" en la base de datos
# Almacena información de proveedores de productos
# Relacionado con: Producto (un proveedor puede proveer muchos productos)
class Proveedor(Base):
    # Nombre de la tabla en la base de datos
    __tablename__ = "proveedores"

    # Columna id: clave primaria entera con índice
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Columna nombre: nombre del proveedor
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    # Columna contacto: nombre de la persona de contacto (opcional)
    contacto: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # Columna telefono: número de teléfono (opcional)
    telefono: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    # Columna email: correo electrónico (opcional)
    email: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    # Columna direccion: dirección física (opcional)
    direccion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Columna activo: indica si el proveedor está activo (True) o desactivado (False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    # Columna creado_en: fecha y hora de creación del registro en UTC
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Relación uno a muchos: un proveedor puede proveer muchos productos
    # back_populates="proveedor" indica que el modelo Producto tiene una relación inversa llamada "proveedor"
    productos: Mapped[list["Producto"]] = relationship("Producto", back_populates="proveedor")


# ---------------------------------------------------------------------------
# Producto
# ---------------------------------------------------------------------------
# Modelo ORM que representa la tabla "productos" en la base de datos
# Almacena información de productos del inventario con precios y stock
# Relacionado con: Categoria (muchos productos pueden pertenecer a una categoría), Proveedor (muchos productos pueden provenir de un proveedor)
# Relacionado con: DetalleVenta (un producto puede estar en muchos detalles de venta), Movimiento (un producto puede tener muchos movimientos)
class Producto(Base):
    # Nombre de la tabla en la base de datos
    __tablename__ = "productos"

    # Columna id: clave primaria entera con índice
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Columna codigo: código único del producto (para identificación interna)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    # Columna nombre: nombre del producto
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    # Columna descripcion: descripción detallada del producto (opcional)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Columna precio_compra: precio al que se compró el producto al proveedor
    precio_compra: Mapped[float] = mapped_column(Float, default=0.0)
    # Columna precio_venta: precio al que se vende el producto a los clientes
    precio_venta: Mapped[float] = mapped_column(Float, nullable=False)
    # Columna stock: cantidad actual en inventario
    stock: Mapped[int] = mapped_column(Integer, default=0)
    # Columna stock_minimo: cantidad mínima antes de alertar de bajo stock
    stock_minimo: Mapped[int] = mapped_column(Integer, default=5)
    # Columna unidad: unidad de medida (ej: "unidad", "kg", "litro") - opcional
    unidad: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    # Columna activo: indica si el producto está activo (True) o desactivado (False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    # Columna creado_en: fecha y hora de creación del registro en UTC
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    # Columna actualizado_en: fecha y hora de última actualización
    # onupdate=utcnow actualiza automáticamente este campo cuando se modifica el registro
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    # Columna categoria_id: clave foránea que referencia a la tabla categorias
    # Nullable=True permite productos sin categoría
    categoria_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("categorias.id"), nullable=True
    )
    # Columna proveedor_id: clave foránea que referencia a la tabla proveedores
    # Nullable=True permite productos sin proveedor
    proveedor_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("proveedores.id"), nullable=True
    )

    # Relación muchos a uno: muchos productos pueden pertenecer a una categoría
    # back_populates="productos" indica que el modelo Categoria tiene una relación inversa llamada "productos"
    categoria: Mapped[Optional[Categoria]] = relationship("Categoria", back_populates="productos")
    # Relación muchos a uno: muchos productos pueden provenir de un proveedor
    # back_populates="productos" indica que el modelo Proveedor tiene una relación inversa llamada "productos"
    proveedor: Mapped[Optional[Proveedor]] = relationship("Proveedor", back_populates="productos")
    # Relación uno a muchos: un producto puede estar en muchos detalles de venta
    # back_populates="producto" indica que el modelo DetalleVenta tiene una relación inversa llamada "producto"
    detalles_venta: Mapped[list["DetalleVenta"]] = relationship(
        "DetalleVenta", back_populates="producto"
    )
    # Relación uno a muchos: un producto puede tener muchos movimientos de inventario
    # back_populates="producto" indica que el modelo Movimiento tiene una relación inversa llamada "producto"
    movimientos: Mapped[list["Movimiento"]] = relationship(
        "Movimiento", back_populates="producto"
    )


# ---------------------------------------------------------------------------
# Cliente
# ---------------------------------------------------------------------------
# Modelo ORM que representa la tabla "clientes" en la base de datos
# Almacena información de clientes del negocio
# Relacionado con: Venta (un cliente puede tener muchas ventas)
class Cliente(Base):
    # Nombre de la tabla en la base de datos
    __tablename__ = "clientes"

    # Columna id: clave primaria entera con índice
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Columna nombre: nombre del cliente
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    # Columna email: correo electrónico del cliente (opcional)
    email: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    # Columna telefono: número de teléfono (opcional)
    telefono: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    # Columna documento: número de documento de identidad (opcional)
    documento: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    # Columna direccion: dirección física (opcional)
    direccion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Columna activo: indica si el cliente está activo (True) o desactivado (False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    # Columna creado_en: fecha y hora de creación del registro en UTC
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Relación uno a muchos: un cliente puede tener muchas ventas
    # back_populates="cliente" indica que el modelo Venta tiene una relación inversa llamada "cliente"
    ventas: Mapped[list["Venta"]] = relationship("Venta", back_populates="cliente")


# ---------------------------------------------------------------------------
# Venta
# ---------------------------------------------------------------------------
# Modelo ORM que representa la tabla "ventas" en la base de datos
# Almacena cabeceras de ventas (información general de la transacción)
# Relacionado con: Cliente (muchas ventas pueden pertenecer a un cliente), Usuario (muchas ventas pueden ser registradas por un usuario)
# Relacionado con: DetalleVenta (una venta puede tener muchos detalles de venta)
class Venta(Base):
    # Nombre de la tabla en la base de datos
    __tablename__ = "ventas"

    # Columna id: clave primaria entera con índice
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Columna numero: número único de venta (formato VTA-YYYYMMDD-####)
    numero: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    # Columna total: total de la venta después de descuentos
    total: Mapped[float] = mapped_column(Float, default=0.0)
    # Columna descuento: monto de descuento aplicado a la venta
    descuento: Mapped[float] = mapped_column(Float, default=0.0)
    # Columna estado: estado de la venta ("completada" o "anulada")
    estado: Mapped[str] = mapped_column(String(20), default="completada")
    # Columna notas: notas adicionales de la venta (opcional)
    notas: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Columna creado_en: fecha y hora de creación del registro en UTC
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Columna cliente_id: clave foránea que referencia a la tabla clientes
    # Nullable=True permite ventas sin cliente (ventas al público general)
    cliente_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("clientes.id"), nullable=True
    )
    # Columna usuario_id: clave foránea que referencia a la tabla usuarios
    # Nullable=True permite ventas sin usuario asignado (aunque normalmente siempre hay uno)
    usuario_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=True
    )

    # Relación muchos a uno: muchas ventas pueden pertenecer a un cliente
    # back_populates="ventas" indica que el modelo Cliente tiene una relación inversa llamada "ventas"
    cliente: Mapped[Optional[Cliente]] = relationship("Cliente", back_populates="ventas")
    # Relación muchos a uno: muchas ventas pueden ser registradas por un usuario
    # back_populates="ventas" indica que el modelo Usuario tiene una relación inversa llamada "ventas"
    usuario: Mapped[Optional[Usuario]] = relationship("Usuario", back_populates="ventas")
    # Relación uno a muchos: una venta puede tener muchos detalles de venta
    # cascade="all, delete-orphan" significa que al eliminar una venta, se eliminan automáticamente sus detalles
    # back_populates="venta" indica que el modelo DetalleVenta tiene una relación inversa llamada "venta"
    detalles: Mapped[list["DetalleVenta"]] = relationship(
        "DetalleVenta", back_populates="venta", cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# Detalle de Venta
# ---------------------------------------------------------------------------
# Modelo ORM que representa la tabla "detalles_venta" en la base de datos
# Almacena líneas individuales de venta (productos vendidos en una venta)
# Relacionado con: Venta (muchos detalles pueden pertenecer a una venta), Producto (muchos detalles pueden referenciar un producto)
class DetalleVenta(Base):
    # Nombre de la tabla en la base de datos
    __tablename__ = "detalles_venta"

    # Columna id: clave primaria entera con índice
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Columna cantidad: cantidad del producto vendido en este detalle
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    # Columna precio_unitario: precio unitario al que se vendió el producto
    precio_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    # Columna subtotal: subtotal del detalle (cantidad × precio_unitario)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)

    # Columna venta_id: clave foránea que referencia a la tabla ventas (obligatoria)
    venta_id: Mapped[int] = mapped_column(Integer, ForeignKey("ventas.id"), nullable=False)
    # Columna producto_id: clave foránea que referencia a la tabla productos (obligatoria)
    producto_id: Mapped[int] = mapped_column(Integer, ForeignKey("productos.id"), nullable=False)

    # Relación muchos a uno: muchos detalles pueden pertenecer a una venta
    # back_populates="detalles" indica que el modelo Venta tiene una relación inversa llamada "detalles"
    venta: Mapped[Venta] = relationship("Venta", back_populates="detalles")
    # Relación muchos a uno: muchos detalles pueden referenciar un producto
    # back_populates="detalles_venta" indica que el modelo Producto tiene una relación inversa llamada "detalles_venta"
    producto: Mapped[Producto] = relationship("Producto", back_populates="detalles_venta")


# ---------------------------------------------------------------------------
# Movimiento de Inventario
# ---------------------------------------------------------------------------
# Modelo ORM que representa la tabla "movimientos" en la base de datos
# Almacena historial de cambios de stock (entradas, salidas, ajustes)
# Relacionado con: Producto (muchos movimientos pueden referenciar un producto), Usuario (muchos movimientos pueden ser registrados por un usuario)
class Movimiento(Base):
    # Nombre de la tabla en la base de datos
    __tablename__ = "movimientos"

    # Columna id: clave primaria entera con índice
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Columna tipo: tipo de movimiento ("entrada", "salida" o "ajuste")
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)  # entrada | salida | ajuste
    # Columna cantidad: cantidad del movimiento
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    # Columna stock_anterior: stock del producto antes del movimiento
    stock_anterior: Mapped[int] = mapped_column(Integer, nullable=False)
    # Columna stock_nuevo: stock del producto después del movimiento
    stock_nuevo: Mapped[int] = mapped_column(Integer, nullable=False)
    # Columna motivo: motivo o descripción del movimiento (opcional)
    motivo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Columna creado_en: fecha y hora de creación del registro en UTC
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Columna producto_id: clave foránea que referencia a la tabla productos (obligatoria)
    producto_id: Mapped[int] = mapped_column(Integer, ForeignKey("productos.id"), nullable=False)
    # Columna usuario_id: clave foránea que referencia a la tabla usuarios (opcional)
    usuario_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=True
    )

    # Relación muchos a uno: muchos movimientos pueden referenciar un producto
    # back_populates="movimientos" indica que el modelo Producto tiene una relación inversa llamada "movimientos"
    producto: Mapped[Producto] = relationship("Producto", back_populates="movimientos")
    # Relación muchos a uno: muchos movimientos pueden ser registrados por un usuario
    # back_populates="movimientos" indica que el modelo Usuario tiene una relación inversa llamada "movimientos"
    usuario: Mapped[Optional[Usuario]] = relationship("Usuario", back_populates="movimientos")
