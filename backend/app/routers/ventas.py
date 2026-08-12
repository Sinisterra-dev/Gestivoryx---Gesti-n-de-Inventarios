# Importa date, datetime y timezone para manejo de fechas y generación de números de venta
from datetime import date, datetime, timezone

# Importa APIRouter para crear el router de ventas con sus endpoints
# Importa Depends para inyección de dependencias (get_db, get_current_user)
# Importa HTTPException y status para manejo de errores HTTP
from fastapi import APIRouter, Depends, HTTPException, status
# Importa Session y joinedload de SQLAlchemy ORM
# Session para sesiones de base de datos, joinedload para cargar relaciones eficientemente
from sqlalchemy.orm import Session, joinedload

# Importa get_current_user de deps.py para obtener el usuario autenticado
from app.core.deps import get_current_user
# Importa get_db de database.py para inyectar sesión de base de datos
from app.database import get_db
# Importa los modelos DetalleVenta, Movimiento, Producto, Venta y Usuario para consultas
from app.models.models import DetalleVenta, Movimiento, Producto, Venta, Usuario
# Importa los esquemas de ventas para validación y respuesta
from app.schemas.schemas import VentaCreate, VentaOut

# Crea el router de ventas con prefijo /api/ventas y tag "Ventas"
router = APIRouter(prefix="/api/ventas", tags=["Ventas"])


# Función auxiliar que genera un número de venta único basado en la fecha
# El formato es VTA-YYYYMMDD-#### donde #### es un consecutivo de 4 dígitos
# Esto permite tener múltiples ventas por día con números secuenciales
def _generar_numero_venta(db: Session) -> str:
    # Obtiene la fecha actual en formato YYYYMMDD (ej: 20240811)
    today = date.today().strftime("%Y%m%d")
    # Cuenta cuántas ventas existen hoy con el prefijo VTA-YYYYMMDD-
    # Esto determina el siguiente número consecutivo a usar
    count = db.query(Venta).filter(Venta.numero.like(f"VTA-{today}-%")).count()
    # Retorna el número de venta formateado con 4 dígitos para el consecutivo
    # Ejemplo: VTA-20240811-0001, VTA-20240811-0002, etc.
    return f"VTA-{today}-{count + 1:04d}"


# Endpoint GET /api/ventas para listar todas las ventas
# response_model=list[VentaOut] indica que la respuesta es una lista de ventas
# Carga las relaciones cliente, usuario y detalles con productos para cada venta
@router.get("/", response_model=list[VentaOut])
def listar_ventas(
    # db: sesión de base de datos inyectada para consultar ventas
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Consulta todas las ventas con sus relaciones cargadas
    # joinedload carga las relaciones en una sola consulta para evitar el problema N+1
    return (
        db.query(Venta)
        .options(
            joinedload(Venta.cliente),  # Carga la relación cliente (cliente_id -> Cliente)
            joinedload(Venta.usuario),  # Carga la relación usuario (usuario_id -> Usuario)
            # Carga la relación detalles y anida carga de productos de cada detalle
            joinedload(Venta.detalles).joinedload(DetalleVenta.producto),
        )
        # Ordena las ventas por fecha de creación descendente (más recientes primero)
        .order_by(Venta.creado_en.desc())
        .all()
    )


# Endpoint GET /api/ventas/{venta_id} para obtener una venta específica
# Retorna la venta completa con todos sus detalles y relaciones
@router.get("/{venta_id}", response_model=VentaOut)
def obtener_venta(
    # venta_id: ID de la venta a obtener (parámetro de ruta)
    venta_id: int,
    # db: sesión de base de datos inyectada para consultar la venta
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Consulta la venta específica con todas sus relaciones cargadas
    venta = (
        db.query(Venta)
        .options(
            joinedload(Venta.cliente),
            joinedload(Venta.usuario),
            joinedload(Venta.detalles).joinedload(DetalleVenta.producto),
        )
        .filter(Venta.id == venta_id)
        .first()
    )
    # Si la venta no existe, lanza excepción 404 Not Found
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    # Retorna la venta encontrada con todos sus detalles
    return venta


# Endpoint POST /api/ventas para crear una nueva venta
# status_code=201 indica que se creó un recurso exitosamente
# Este endpoint descuenta automáticamente el stock de los productos vendidos
# y registra movimientos de inventario para trazabilidad
@router.post("/", response_model=VentaOut, status_code=status.HTTP_201_CREATED)
def crear_venta(
    # data: datos de la venta a crear, validados por el esquema VentaCreate
    # Incluye cliente_id, descuento, notas y lista de detalles (productos vendidos)
    data: VentaCreate,
    # db: sesión de base de datos inyectada para crear la venta
    db: Session = Depends(get_db),
    # current_user: usuario autenticado que está registrando la venta
    current_user: Usuario = Depends(get_current_user),
):
    # Valida que la venta tenga al menos un producto (detalle)
    if not data.detalles:
        # Si no hay detalles, lanza excepción 400 Bad Request
        raise HTTPException(status_code=400, detail="La venta debe tener al menos un producto")

    # Crea la cabecera de la venta con los datos generales
    venta = Venta(
        numero=_generar_numero_venta(db),  # Genera número único de venta
        cliente_id=data.cliente_id,         # Cliente asociado (opcional)
        usuario_id=current_user.id,        # Usuario que registra la venta
        descuento=data.descuento,           # Descuento general de la venta
        notas=data.notas,                   # Notas adicionales (opcional)
        estado="completada",                # Estado inicial de la venta
    )
    # Agrega la venta a la sesión de base de datos
    db.add(venta)
    # flush() envía la venta a la base de datos sin hacer commit
    # Esto genera el ID de la venta para poder usarlo en los detalles
    db.flush()

    # Variable para acumular el total de la venta
    total = 0.0
    # Procesa cada detalle (producto) de la venta
    for item in data.detalles:
        # Consulta el producto para verificar existencia, estado y stock
        prod = db.query(Producto).filter(Producto.id == item.producto_id).first()
        # Si el producto no existe, lanza excepción 404 Not Found
        if not prod:
            raise HTTPException(
                status_code=404, detail=f"Producto {item.producto_id} no encontrado"
            )
        # Si el producto no está activo, lanza excepción 400 Bad Request
        if not prod.activo:
            raise HTTPException(
                status_code=400, detail=f"Producto {prod.nombre} no está activo"
            )
        # Si no hay stock suficiente, lanza excepción 400 Bad Request
        if prod.stock < item.cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para {prod.nombre}. Disponible: {prod.stock}",
            )

        # Determina el precio unitario a usar
        # Si se especifica en el detalle, usa ese valor; de lo contrario usa el precio_venta del producto
        precio = item.precio_unitario if item.precio_unitario is not None else prod.precio_venta
        # Calcula el subtotal del detalle (precio × cantidad)
        subtotal = precio * item.cantidad

        # Crea el detalle de venta con la información del producto vendido
        detalle = DetalleVenta(
            venta_id=venta.id,            # ID de la venta cabecera
            producto_id=prod.id,          # ID del producto vendido
            cantidad=item.cantidad,       # Cantidad vendida
            precio_unitario=precio,       # Precio unitario usado
            subtotal=subtotal,            # Subtotal calculado
        )
        # Agrega el detalle a la sesión de base de datos
        db.add(detalle)

        # Guarda el stock anterior antes de modificarlo
        stock_anterior = prod.stock
        # Descuenta la cantidad vendida del stock del producto
        prod.stock -= item.cantidad

        # Registra un movimiento de inventario tipo "salida" para trazabilidad
        # Este movimiento permite ver el historial de cambios de stock
        mov = Movimiento(
            producto_id=prod.id,            # Producto cuyo stock se modificó
            usuario_id=current_user.id,    # Usuario que realizó la venta
            tipo="salida",                 # Tipo de movimiento (salida de stock)
            cantidad=item.cantidad,         # Cantidad descontada
            stock_anterior=stock_anterior, # Stock antes de la venta
            stock_nuevo=prod.stock,        # Stock después de la venta
            motivo=f"Venta #{venta.numero}",# Motivo del movimiento
        )
        # Agrega el movimiento a la sesión de base de datos
        db.add(mov)
        # Acumula el subtotal al total de la venta
        total += subtotal

    # Calcula el total final de la venta restando el descuento general
    venta.total = total - data.descuento
    # Confirma la transacción para persistir la venta, detalles, cambios de stock y movimientos
    db.commit()
    # Refresca la instancia para obtener los valores generados
    db.refresh(venta)

    # Retorna la venta creada con todas sus relaciones cargadas
    # Se hace una query adicional para cargar las relaciones cliente, usuario y detalles con productos
    return (
        db.query(Venta)
        .options(
            joinedload(Venta.cliente),
            joinedload(Venta.usuario),
            joinedload(Venta.detalles).joinedload(DetalleVenta.producto),
        )
        .filter(Venta.id == venta.id)
        .first()
    )


# Endpoint DELETE /api/ventas/{venta_id} para anular una venta
# status_code=204 indica que la operación fue exitosa sin contenido en la respuesta
# Anular una venta restaura el stock de los productos y registra movimientos de entrada
@router.delete("/{venta_id}", status_code=status.HTTP_204_NO_CONTENT)
def anular_venta(
    # venta_id: ID de la venta a anular (parámetro de ruta)
    venta_id: int,
    # db: sesión de base de datos inyectada para anular la venta
    db: Session = Depends(get_db),
    # current_user: usuario autenticado que está anulando la venta
    current_user: Usuario = Depends(get_current_user),
):
    # Consulta la venta a anular (sin cargar relaciones para eficiencia)
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    # Si la venta no existe, lanza excepción 404 Not Found
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    # Si la venta ya está anulada, lanza excepción 400 Bad Request
    # Esto previene anulaciones múltiples de la misma venta
    if venta.estado == "anulada":
        raise HTTPException(status_code=400, detail="La venta ya está anulada")

    # Procesa cada detalle de la venta para restaurar el stock
    for detalle in venta.detalles:
        # Consulta el producto del detalle
        prod = db.query(Producto).filter(Producto.id == detalle.producto_id).first()
        # Si el producto existe (puede haber sido eliminado), restaura el stock
        if prod:
            # Guarda el stock anterior antes de modificarlo
            stock_anterior = prod.stock
            # Restaura la cantidad vendida al stock del producto
            prod.stock += detalle.cantidad
            # Registra un movimiento de inventario tipo "entrada" para trazabilidad
            # Este movimiento registra la reversión del stock por anulación de venta
            mov = Movimiento(
                producto_id=prod.id,            # Producto cuyo stock se restauró
                usuario_id=current_user.id,    # Usuario que anuló la venta
                tipo="entrada",                # Tipo de movimiento (entrada de stock)
                cantidad=detalle.cantidad,     # Cantidad restaurada
                stock_anterior=stock_anterior, # Stock antes de la restauración
                stock_nuevo=prod.stock,        # Stock después de la restauración
                motivo=f"Anulación venta #{venta.numero}",# Motivo del movimiento
            )
            # Agrega el movimiento a la sesión de base de datos
            db.add(mov)

    # Cambia el estado de la venta a "anulada"
    venta.estado = "anulada"
    # Confirma la transacción para persistir el cambio de estado y los movimientos de entrada
    db.commit()
