# Importa APIRouter para crear el router de movimientos con sus endpoints
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
# Importa los modelos Movimiento, Producto y Usuario para consultas en base de datos
from app.models.models import Movimiento, Producto, Usuario
# Importa los esquemas de movimientos para validación y respuesta
from app.schemas.schemas import MovimientoCreate, MovimientoOut

# Crea el router de movimientos con prefijo /api/movimientos y tag "Movimientos de Inventario"
router = APIRouter(prefix="/api/movimientos", tags=["Movimientos de Inventario"])


# Endpoint GET /api/movimientos para listar todos los movimientos de inventario
# response_model=list[MovimientoOut] indica que la respuesta es una lista de movimientos
# Soporta filtro opcional por producto_id
@router.get("/", response_model=list[MovimientoOut])
def listar_movimientos(
    # producto_id: parámetro query opcional para filtrar movimientos de un producto específico
    producto_id: int = None,
    # db: sesión de base de datos inyectada para consultar movimientos
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Crea la query base para consultar movimientos
    # options() con joinedload carga las relaciones producto y usuario en una sola consulta
    # Esto evita el problema N+1 de consultas múltiples
    q = db.query(Movimiento).options(
        joinedload(Movimiento.producto),  # Carga la relación producto (producto_id -> Producto)
        joinedload(Movimiento.usuario),  # Carga la relación usuario (usuario_id -> Usuario)
    )
    # Si se proporciona producto_id, filtra movimientos de ese producto específico
    if producto_id:
        q = q.filter(Movimiento.producto_id == producto_id)
    # Ordena los movimientos por fecha de creación descendente (más recientes primero)
    # Retorna todos los movimientos con sus relaciones cargadas
    return q.order_by(Movimiento.creado_en.desc()).all()


# Endpoint POST /api/movimientos para registrar un movimiento manual de inventario
# status_code=201 indica que se creó un recurso exitosamente
# Este endpoint permite registrar entradas, salidas o ajustes de stock manualmente
@router.post("/", response_model=MovimientoOut, status_code=status.HTTP_201_CREATED)
def registrar_movimiento(
    # data: datos del movimiento a registrar, validados por el esquema MovimientoCreate
    data: MovimientoCreate,
    # db: sesión de base de datos inyectada para registrar el movimiento
    db: Session = Depends(get_db),
    # current_user: usuario autenticado que está registrando el movimiento
    current_user: Usuario = Depends(get_current_user),
):
    # Valida que el tipo de movimiento sea uno de los permitidos
    # Los tipos válidos son: entrada (aumenta stock), salida (disminuye stock), ajuste (establece stock)
    if data.tipo not in ("entrada", "salida", "ajuste"):
        # Si el tipo no es válido, lanza excepción 400 Bad Request
        raise HTTPException(
            status_code=400,
            detail="Tipo inválido. Usa: entrada, salida, ajuste",
        )

    # Consulta la base de datos para buscar el producto asociado al movimiento
    prod = db.query(Producto).filter(Producto.id == data.producto_id).first()
    # Si el producto no existe, lanza excepción 404 Not Found
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Guarda el stock actual del producto antes de modificarlo
    # Este valor se usará para registrar el stock_anterior en el movimiento
    stock_anterior = prod.stock

    # Según el tipo de movimiento, ajusta el stock del producto
    if data.tipo == "entrada":
        # ENTRADA: aumenta el stock con la cantidad especificada
        prod.stock += data.cantidad
    elif data.tipo == "salida":
        # SALIDA: disminuye el stock con la cantidad especificada
        # Verifica que haya stock suficiente antes de descontar
        if prod.stock < data.cantidad:
            # Si no hay stock suficiente, lanza excepción 400 Bad Request
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente. Disponible: {prod.stock}",
            )
        # Descuenta la cantidad del stock
        prod.stock -= data.cantidad
    else:  # ajuste
        # AJUSTE: establece el stock exactamente al valor especificado
        # Esto es útil para correcciones manuales de inventario
        prod.stock = data.cantidad

    # Crea el registro del movimiento con toda la información de trazabilidad
    mov = Movimiento(
        producto_id=prod.id,            # ID del producto cuyo stock se modificó
        usuario_id=current_user.id,    # ID del usuario que registró el movimiento
        tipo=data.tipo,                # Tipo de movimiento (entrada/salida/ajuste)
        cantidad=data.cantidad,         # Cantidad del movimiento
        stock_anterior=stock_anterior, # Stock antes del movimiento
        stock_nuevo=prod.stock,        # Stock después del movimiento
        motivo=data.motivo,            # Motivo o descripción del movimiento
    )
    # Agrega el movimiento a la sesión de base de datos
    db.add(mov)
    # Confirma la transacción para persistir el movimiento y el cambio de stock
    db.commit()
    # Refresca la instancia para obtener los valores generados (id, creado_en)
    db.refresh(mov)

    # Retorna el movimiento creado con sus relaciones cargadas
    # Se hace una query adicional para cargar las relaciones producto y usuario
    return (
        db.query(Movimiento)
        .options(joinedload(Movimiento.producto), joinedload(Movimiento.usuario))
        .filter(Movimiento.id == mov.id)
        .first()
    )
