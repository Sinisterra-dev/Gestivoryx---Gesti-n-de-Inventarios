from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user
from app.database import get_db
from app.models.models import DetalleVenta, Movimiento, Producto, Venta, Usuario
from app.schemas.schemas import VentaCreate, VentaOut

router = APIRouter(prefix="/api/ventas", tags=["Ventas"])


def _generar_numero_venta(db: Session) -> str:
    today = date.today().strftime("%Y%m%d")
    count = db.query(Venta).filter(Venta.numero.like(f"VTA-{today}-%")).count()
    return f"VTA-{today}-{count + 1:04d}"


@router.get("/", response_model=list[VentaOut])
def listar_ventas(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return (
        db.query(Venta)
        .options(
            joinedload(Venta.cliente),
            joinedload(Venta.usuario),
            joinedload(Venta.detalles).joinedload(DetalleVenta.producto),
        )
        .order_by(Venta.creado_en.desc())
        .all()
    )


@router.get("/{venta_id}", response_model=VentaOut)
def obtener_venta(
    venta_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
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
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta


@router.post("/", response_model=VentaOut, status_code=status.HTTP_201_CREATED)
def crear_venta(
    data: VentaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if not data.detalles:
        raise HTTPException(status_code=400, detail="La venta debe tener al menos un producto")

    venta = Venta(
        numero=_generar_numero_venta(db),
        cliente_id=data.cliente_id,
        usuario_id=current_user.id,
        descuento=data.descuento,
        notas=data.notas,
        estado="completada",
    )
    db.add(venta)
    db.flush()

    total = 0.0
    for item in data.detalles:
        prod = db.query(Producto).filter(Producto.id == item.producto_id).first()
        if not prod:
            raise HTTPException(
                status_code=404, detail=f"Producto {item.producto_id} no encontrado"
            )
        if not prod.activo:
            raise HTTPException(
                status_code=400, detail=f"Producto {prod.nombre} no está activo"
            )
        if prod.stock < item.cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para {prod.nombre}. Disponible: {prod.stock}",
            )

        precio = item.precio_unitario if item.precio_unitario is not None else prod.precio_venta
        subtotal = precio * item.cantidad

        detalle = DetalleVenta(
            venta_id=venta.id,
            producto_id=prod.id,
            cantidad=item.cantidad,
            precio_unitario=precio,
            subtotal=subtotal,
        )
        db.add(detalle)

        stock_anterior = prod.stock
        prod.stock -= item.cantidad

        mov = Movimiento(
            producto_id=prod.id,
            usuario_id=current_user.id,
            tipo="salida",
            cantidad=item.cantidad,
            stock_anterior=stock_anterior,
            stock_nuevo=prod.stock,
            motivo=f"Venta #{venta.numero}",
        )
        db.add(mov)
        total += subtotal

    venta.total = total - data.descuento
    db.commit()
    db.refresh(venta)

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


@router.delete("/{venta_id}", status_code=status.HTTP_204_NO_CONTENT)
def anular_venta(
    venta_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    if venta.estado == "anulada":
        raise HTTPException(status_code=400, detail="La venta ya está anulada")

    for detalle in venta.detalles:
        prod = db.query(Producto).filter(Producto.id == detalle.producto_id).first()
        if prod:
            stock_anterior = prod.stock
            prod.stock += detalle.cantidad
            mov = Movimiento(
                producto_id=prod.id,
                usuario_id=current_user.id,
                tipo="entrada",
                cantidad=detalle.cantidad,
                stock_anterior=stock_anterior,
                stock_nuevo=prod.stock,
                motivo=f"Anulación venta #{venta.numero}",
            )
            db.add(mov)

    venta.estado = "anulada"
    db.commit()
