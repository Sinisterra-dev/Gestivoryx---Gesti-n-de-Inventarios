# Importa date, datetime, timedelta y timezone para manejo de fechas y cálculos de tiempo
# Se usa para calcular el inicio del día y del mes para filtros de estadísticas
from datetime import date, datetime, timedelta, timezone

# Importa APIRouter para crear el router de dashboard con sus endpoints
# Importa Depends para inyección de dependencias (get_db, get_current_user)
from fastapi import APIRouter, Depends
# Importa func de SQLAlchemy para funciones de agregación (SUM, COUNT, etc.)
from sqlalchemy import func
# Importa Session de SQLAlchemy ORM para sesiones de base de datos
from sqlalchemy.orm import Session

# Importa get_current_user de deps.py para obtener el usuario autenticado
from app.core.deps import get_current_user
# Importa get_db de database.py para inyectar sesión de base de datos
from app.database import get_db
# Importa los modelos Cliente, Producto, Proveedor, Venta y Usuario para consultas
from app.models.models import Cliente, Producto, Proveedor, Venta, Usuario
# Importa el esquema DashboardStats para la respuesta de estadísticas
from app.schemas.schemas import DashboardStats

# Crea el router de dashboard con prefijo /api/dashboard y tag "Dashboard"
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


# Endpoint GET /api/dashboard/stats para obtener estadísticas del negocio
# response_model=DashboardStats indica que la respuesta sigue el esquema DashboardStats
# Este endpoint calcula múltiples métricas en una sola llamada para el dashboard
@router.get("/stats", response_model=DashboardStats)
def obtener_stats(
    # db: sesión de base de datos inyectada para realizar consultas de agregación
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Calcula el inicio del día actual (00:00:00) en UTC para filtros de ventas de hoy
    # datetime.combine combina la fecha actual con la hora mínima
    # replace(tzinfo=timezone.utc) establece la zona horaria UTC
    hoy_inicio = datetime.combine(date.today(), datetime.min.time()).replace(
        tzinfo=timezone.utc
    )
    # Calcula el inicio del mes actual (día 1 a las 00:00:00) en UTC para filtros de ventas del mes
    # date.today().replace(day=1) establece el día en 1 (primer día del mes)
    mes_inicio = datetime.combine(date.today().replace(day=1), datetime.min.time()).replace(
        tzinfo=timezone.utc
    )

    # Cuenta el total de productos activos en el inventario
    # filter(Producto.activo == True) filtra solo productos activos
    # count() retorna el número de registros
    total_productos = db.query(Producto).filter(Producto.activo == True).count()
    # Cuenta el total de clientes activos registrados
    total_clientes = db.query(Cliente).filter(Cliente.activo == True).count()
    # Cuenta el total de proveedores activos registrados
    total_proveedores = db.query(Proveedor).filter(Proveedor.activo == True).count()

    # Cuenta el número de ventas completadas hoy
    # filter(Venta.estado == "completada") filtra solo ventas completadas
    # filter(Venta.creado_en >= hoy_inicio) filtra ventas creadas desde el inicio de hoy
    ventas_hoy = (
        db.query(Venta)
        .filter(Venta.estado == "completada", Venta.creado_en >= hoy_inicio)
        .count()
    )

    # Calcula el total de ingresos (suma de totales) de ventas completadas hoy
    # func.sum(Venta.total) calcula la suma del campo total de las ventas
    # scalar() retorna el valor escalar (un solo valor) de la agregación
    # or 0.0 retorna 0.0 si no hay ventas (scalar retorna None en ese caso)
    ingresos_hoy = (
        db.query(func.sum(Venta.total))
        .filter(Venta.estado == "completada", Venta.creado_en >= hoy_inicio)
        .scalar()
        or 0.0
    )

    # Calcula el total de ingresos (suma de totales) de ventas completadas este mes
    # Usa mes_inicio en lugar de hoy_inicio para filtrar ventas del mes actual
    ingresos_mes = (
        db.query(func.sum(Venta.total))
        .filter(Venta.estado == "completada", Venta.creado_en >= mes_inicio)
        .scalar()
        or 0.0
    )

    # Cuenta el número total de ventas completadas este mes
    total_ventas_mes = (
        db.query(Venta)
        .filter(Venta.estado == "completada", Venta.creado_en >= mes_inicio)
        .count()
    )

    # Cuenta el número de productos con stock bajo (stock <= stock_minimo)
    # filter(Producto.stock <= Producto.stock_minimo) filtra productos bajo su mínimo
    # Esto alerta sobre productos que necesitan reabastecimiento
    productos_bajo_stock = (
        db.query(Producto)
        .filter(Producto.activo == True, Producto.stock <= Producto.stock_minimo)
        .count()
    )

    # Retorna todas las estadísticas calculadas en un objeto DashboardStats
    # Este objeto sigue el esquema definido en schemas.py y se usa en el frontend
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
