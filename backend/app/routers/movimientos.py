from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user
from app.database import get_db
from app.models.models import Movimiento, Producto, Usuario
from app.schemas.schemas import MovimientoCreate, MovimientoOut

router = APIRouter(prefix="/api/movimientos", tags=["Movimientos de Inventario"])


@router.get("/", response_model=list[MovimientoOut])
def listar_movimientos(
    producto_id: int = None,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    q = db.query(Movimiento).options(
        joinedload(Movimiento.producto),
        joinedload(Movimiento.usuario),
    )
    if producto_id:
        q = q.filter(Movimiento.producto_id == producto_id)
    return q.order_by(Movimiento.creado_en.desc()).all()


@router.post("/", response_model=MovimientoOut, status_code=status.HTTP_201_CREATED)
def registrar_movimiento(
    data: MovimientoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if data.tipo not in ("entrada", "salida", "ajuste"):
        raise HTTPException(
            status_code=400,
            detail="Tipo inválido. Usa: entrada, salida, ajuste",
        )

    prod = db.query(Producto).filter(Producto.id == data.producto_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    stock_anterior = prod.stock

    if data.tipo == "entrada":
        prod.stock += data.cantidad
    elif data.tipo == "salida":
        if prod.stock < data.cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente. Disponible: {prod.stock}",
            )
        prod.stock -= data.cantidad
    else:  # ajuste
        prod.stock = data.cantidad

    mov = Movimiento(
        producto_id=prod.id,
        usuario_id=current_user.id,
        tipo=data.tipo,
        cantidad=data.cantidad,
        stock_anterior=stock_anterior,
        stock_nuevo=prod.stock,
        motivo=data.motivo,
    )
    db.add(mov)
    db.commit()
    db.refresh(mov)

    return (
        db.query(Movimiento)
        .options(joinedload(Movimiento.producto), joinedload(Movimiento.usuario))
        .filter(Movimiento.id == mov.id)
        .first()
    )
