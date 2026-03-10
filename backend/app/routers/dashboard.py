from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.models import Cliente, Producto, Proveedor, Venta, Usuario
from app.schemas.schemas import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def obtener_stats(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    hoy_inicio = datetime.combine(date.today(), datetime.min.time()).replace(
        tzinfo=timezone.utc
    )
    mes_inicio = datetime.combine(date.today().replace(day=1), datetime.min.time()).replace(
        tzinfo=timezone.utc
    )

    total_productos = db.query(Producto).filter(Producto.activo == True).count()
    total_clientes = db.query(Cliente).filter(Cliente.activo == True).count()
    total_proveedores = db.query(Proveedor).filter(Proveedor.activo == True).count()

    ventas_hoy = (
        db.query(Venta)
        .filter(Venta.estado == "completada", Venta.creado_en >= hoy_inicio)
        .count()
    )

    ingresos_hoy = (
        db.query(func.sum(Venta.total))
        .filter(Venta.estado == "completada", Venta.creado_en >= hoy_inicio)
        .scalar()
        or 0.0
    )

    ingresos_mes = (
        db.query(func.sum(Venta.total))
        .filter(Venta.estado == "completada", Venta.creado_en >= mes_inicio)
        .scalar()
        or 0.0
    )

    total_ventas_mes = (
        db.query(Venta)
        .filter(Venta.estado == "completada", Venta.creado_en >= mes_inicio)
        .count()
    )

    productos_bajo_stock = (
        db.query(Producto)
        .filter(Producto.activo == True, Producto.stock <= Producto.stock_minimo)
        .count()
    )

    return DashboardStats(
        total_productos=total_productos,
        total_clientes=total_clientes,
        total_proveedores=total_proveedores,
        ventas_hoy=ventas_hoy,
        ingresos_hoy=ingresos_hoy,
        ingresos_mes=ingresos_mes,
        productos_bajo_stock=productos_bajo_stock,
        total_ventas_mes=total_ventas_mes,
    )
