from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.models import Producto, Usuario
from app.schemas.schemas import ProductoCreate, ProductoOut, ProductoUpdate

router = APIRouter(prefix="/api/productos", tags=["Productos"])


@router.get("/", response_model=list[ProductoOut])
def listar_productos(
    solo_activos: bool = True,
    bajo_stock: bool = False,
    q: str = Query(default=None, description="Búsqueda por nombre o código"),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    query = db.query(Producto)
    if solo_activos:
        query = query.filter(Producto.activo == True)
    if bajo_stock:
        query = query.filter(Producto.stock <= Producto.stock_minimo)
    if q:
        search = f"%{q}%"
        query = query.filter(
            Producto.nombre.ilike(search) | Producto.codigo.ilike(search)
        )
    return query.order_by(Producto.nombre).all()


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod


@router.post("/", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto(
    data: ProductoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    if db.query(Producto).filter(Producto.codigo == data.codigo).first():
        raise HTTPException(status_code=400, detail="Ya existe un producto con ese código")
    prod = Producto(**data.model_dump())
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return prod


@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(
    producto_id: int,
    data: ProductoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if data.codigo and data.codigo != prod.codigo:
        if db.query(Producto).filter(Producto.codigo == data.codigo).first():
            raise HTTPException(status_code=400, detail="Ya existe un producto con ese código")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(prod, field, value)
    db.commit()
    db.refresh(prod)
    return prod


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    prod.activo = False
    db.commit()
