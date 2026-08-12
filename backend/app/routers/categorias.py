# Importa APIRouter para crear el router de categorías con sus endpoints
# Importa Depends para inyección de dependencias (get_db, get_current_user)
# Importa HTTPException y status para manejo de errores HTTP
from fastapi import APIRouter, Depends, HTTPException, status
# Importa Session de SQLAlchemy ORM para sesiones de base de datos
from sqlalchemy.orm import Session

# Importa get_current_user de deps.py para obtener el usuario autenticado
# Esta dependencia valida el token JWT y retorna el usuario
from app.core.deps import get_current_user
# Importa get_db de database.py para inyectar sesión de base de datos
from app.database import get_db
# Importa los modelos Categoria y Usuario para consultas en base de datos
from app.models.models import Categoria, Usuario
# Importa los esquemas de categorías para validación y respuesta
# CategoriaCreate: esquema para crear categorías
# CategoriaOut: esquema para respuestas de categorías
# CategoriaUpdate: esquema para actualizar categorías
from app.schemas.schemas import CategoriaCreate, CategoriaOut, CategoriaUpdate

# Crea el router de categorías con prefijo /api/categorias y tag "Categorías"
# El prefijo se añade a todas las rutas de este router
# El tag organiza los endpoints en la documentación Swagger
router = APIRouter(prefix="/api/categorias", tags=["Categorías"])


# Endpoint GET /api/categorias para listar todas las categorías
# response_model=list[CategoriaOut] indica que la respuesta es una lista de categorías
# Este endpoint requiere autenticación (usa get_current_user como dependencia)
@router.get("/", response_model=list[CategoriaOut])
def listar_categorias(
    # solo_activas: parámetro query opcional para filtrar solo categorías activas
    # Por defecto es True, retorna solo categorías con activo=True
    solo_activas: bool = True,
    # db: sesión de base de datos inyectada para consultar categorías
    db: Session = Depends(get_db),
    # _: usuario autenticado (el underscore indica que no se usa el valor)
    # Se requiere para validar que el request esté autenticado
    _: Usuario = Depends(get_current_user),
):
    # Crea la query base para consultar todas las categorías
    q = db.query(Categoria)
    # Si solo_activas es True, filtra para retornar solo categorías activas
    if solo_activas:
        q = q.filter(Categoria.activo == True)
    # Ordena las categorías por nombre alfabéticamente y retorna todas
    return q.order_by(Categoria.nombre).all()


# Endpoint GET /api/categorias/{categoria_id} para obtener una categoría específica
# response_model=CategoriaOut indica que la respuesta sigue el esquema CategoriaOut
# categoria_id es un parámetro de ruta que especifica el ID de la categoría
@router.get("/{categoria_id}", response_model=CategoriaOut)
def obtener_categoria(
    # categoria_id: ID de la categoría a obtener (parámetro de ruta)
    categoria_id: int,
    # db: sesión de base de datos inyectada para consultar la categoría
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Consulta la base de datos para buscar la categoría por ID
    cat = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    # Si la categoría no existe, lanza excepción 404 Not Found
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    # Retorna la categoría encontrada
    return cat


# Endpoint POST /api/categorias para crear una nueva categoría
# response_model=CategoriaOut indica que la respuesta sigue el esquema CategoriaOut
# status_code=201 indica que se creó un recurso exitosamente
@router.post("/", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED)
def crear_categoria(
    # data: datos de la categoría a crear, validados por el esquema CategoriaCreate
    data: CategoriaCreate,
    # db: sesión de base de datos inyectada para crear la categoría
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Verifica si ya existe una categoría con el mismo nombre
    # Esto previene duplicados de nombres de categorías
    if db.query(Categoria).filter(Categoria.nombre == data.nombre).first():
        # Si existe, lanza excepción 400 Bad Request
        raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")
    # Crea una nueva instancia de Categoria con los datos validados
    # model_dump() convierte el esquema Pydantic a diccionario
    cat = Categoria(**data.model_dump())
    # Agrega la categoría a la sesión de base de datos
    db.add(cat)
    # Confirma la transacción para persistir la categoría en la base de datos
    db.commit()
    # Refresca la instancia para obtener los valores generados (id, creado_en)
    db.refresh(cat)
    # Retorna la categoría creada
    return cat


# Endpoint PUT /api/categorias/{categoria_id} para actualizar una categoría
# response_model=CategoriaOut indica que la respuesta sigue el esquema CategoriaOut
@router.put("/{categoria_id}", response_model=CategoriaOut)
def actualizar_categoria(
    # categoria_id: ID de la categoría a actualizar (parámetro de ruta)
    categoria_id: int,
    # data: datos a actualizar, validados por el esquema CategoriaUpdate
    data: CategoriaUpdate,
    # db: sesión de base de datos inyectada para actualizar la categoría
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Consulta la base de datos para buscar la categoría por ID
    cat = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    # Si la categoría no existe, lanza excepción 404 Not Found
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    # Actualiza solo los campos que fueron enviados en el request
    # exclude_unset=True excluye campos que no fueron enviados (mantienen valor actual)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)
    # Confirma la transacción para persistir los cambios en la base de datos
    db.commit()
    # Refresca la instancia para obtener los valores actualizados
    db.refresh(cat)
    # Retorna la categoría actualizada
    return cat


# Endpoint DELETE /api/categorias/{categoria_id} para eliminar una categoría
# status_code=204 indica que la operación fue exitosa sin contenido en la respuesta
# Realiza un soft delete (desactiva la categoría en lugar de eliminarla físicamente)
@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(
    # categoria_id: ID de la categoría a eliminar (parámetro de ruta)
    categoria_id: int,
    # db: sesión de base de datos inyectada para actualizar la categoría
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Consulta la base de datos para buscar la categoría por ID
    cat = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    # Si la categoría no existe, lanza excepción 404 Not Found
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    # Realiza soft delete estableciendo activo=False
    # Esto mantiene el registro en la base de datos pero lo marca como inactivo
    cat.activo = False
    # Confirma la transacción para persistir el cambio en la base de datos
    db.commit()
