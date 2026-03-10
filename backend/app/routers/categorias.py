from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.models import Categoria, Usuario
from app.schemas.schemas import CategoriaCreate, CategoriaOut, CategoriaUpdate

router = APIRouter(prefix="/api/categorias", tags=["Categorías"])


@router.get("/", response_model=list[CategoriaOut])
def listar_categorias(
    solo_activas: bool = True,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    q = db.query(Categoria)
    if solo_activas:
        q = q.filter(Categoria.activo == True)
    return q.order_by(Categoria.nombre).all()


@router.get("/{categoria_id}", response_model=CategoriaOut)
def obtener_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    cat = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return cat


@router.post("/", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED)
def crear_categoria(
    data: CategoriaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    if db.query(Categoria).filter(Categoria.nombre == data.nombre).first():
        raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")
    cat = Categoria(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/{categoria_id}", response_model=CategoriaOut)
def actualizar_categoria(
    categoria_id: int,
    data: CategoriaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    cat = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    cat = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    cat.activo = False
    db.commit()
