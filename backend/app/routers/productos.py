# Importa APIRouter para crear el router de productos con sus endpoints
# Importa Depends para inyección de dependencias (get_db, get_current_user)
# Importa HTTPException y status para manejo de errores HTTP
# Importa Query para definir parámetros de consulta con metadata
from fastapi import APIRouter, Depends, HTTPException, Query, status
# Importa Session de SQLAlchemy ORM para sesiones de base de datos
from sqlalchemy.orm import Session

# Importa get_current_user de deps.py para obtener el usuario autenticado
from app.core.deps import get_current_user
# Importa get_db de database.py para inyectar sesión de base de datos
from app.database import get_db
# Importa los modelos Producto y Usuario para consultas en base de datos
from app.models.models import Producto, Usuario
# Importa los esquemas de productos para validación y respuesta
from app.schemas.schemas import ProductoCreate, ProductoOut, ProductoUpdate

# Crea el router de productos con prefijo /api/productos y tag "Productos"
router = APIRouter(prefix="/api/productos", tags=["Productos"])


# Endpoint GET /api/productos para listar todos los productos
# response_model=list[ProductoOut] indica que la respuesta es una lista de productos
# Soporta filtros opcionales para activos, bajo stock y búsqueda por texto
@router.get("/", response_model=list[ProductoOut])
def listar_productos(
    # solo_activos: parámetro query opcional para filtrar solo productos activos
    solo_activos: bool = True,
    # bajo_stock: parámetro query opcional para filtrar solo productos con stock bajo
    bajo_stock: bool = False,
    # q: parámetro query opcional para búsqueda por nombre o código (case-insensitive)
    q: str = Query(default=None, description="Búsqueda por nombre o código"),
    # db: sesión de base de datos inyectada para consultar productos
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Crea la query base para consultar todos los productos
    query = db.query(Producto)
    # Si solo_activos es True, filtra para retornar solo productos activos
    if solo_activos:
        query = query.filter(Producto.activo == True)
    # Si bajo_stock es True, filtra productos con stock <= stock_minimo
    if bajo_stock:
        query = query.filter(Producto.stock <= Producto.stock_minimo)
    # Si se proporciona un término de búsqueda q, filtra por nombre o código
    if q:
        # Crea el patrón de búsqueda con comodines % para coincidencia parcial
        search = f"%{q}%"
        # Filtra productos donde nombre o código contengan el término de búsqueda
        # ilike() es case-insensitive LIKE
        # El operador | (OR) permite buscar en ambos campos
        query = query.filter(
            Producto.nombre.ilike(search) | Producto.codigo.ilike(search)
        )
    # Ordena los productos por nombre alfabéticamente y retorna todos
    return query.order_by(Producto.nombre).all()


# Endpoint GET /api/productos/{producto_id} para obtener un producto específico
@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(
    # producto_id: ID del producto a obtener (parámetro de ruta)
    producto_id: int,
    # db: sesión de base de datos inyectada para consultar el producto
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Consulta la base de datos para buscar el producto por ID
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    # Si el producto no existe, lanza excepción 404 Not Found
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    # Retorna el producto encontrado (con sus relaciones cargadas)
    return prod


# Endpoint POST /api/productos para crear un nuevo producto
# status_code=201 indica que se creó un recurso exitosamente
@router.post("/", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto(
    # data: datos del producto a crear, validados por el esquema ProductoCreate
    data: ProductoCreate,
    # db: sesión de base de datos inyectada para crear el producto
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Verifica si ya existe un producto con el mismo código
    # Esto previene duplicados de códigos de productos
    if db.query(Producto).filter(Producto.codigo == data.codigo).first():
        # Si existe, lanza excepción 400 Bad Request
        raise HTTPException(status_code=400, detail="Ya existe un producto con ese código")
    # Crea una nueva instancia de Producto con los datos validados
    prod = Producto(**data.model_dump())
    # Agrega el producto a la sesión de base de datos
    db.add(prod)
    # Confirma la transacción para persistir el producto en la base de datos
    db.commit()
    # Refresca la instancia para obtener los valores generados (id, creado_en)
    db.refresh(prod)
    # Retorna el producto creado
    return prod


# Endpoint PUT /api/productos/{producto_id} para actualizar un producto
@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(
    # producto_id: ID del producto a actualizar (parámetro de ruta)
    producto_id: int,
    # data: datos a actualizar, validados por el esquema ProductoUpdate
    data: ProductoUpdate,
    # db: sesión de base de datos inyectada para actualizar el producto
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Consulta la base de datos para buscar el producto por ID
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    # Si el producto no existe, lanza excepción 404 Not Found
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    # Si se está actualizando el código y es diferente al actual, verifica duplicados
    if data.codigo and data.codigo != prod.codigo:
        if db.query(Producto).filter(Producto.codigo == data.codigo).first():
            # Si el nuevo código ya existe en otro producto, lanza excepción 400
            raise HTTPException(status_code=400, detail="Ya existe un producto con ese código")
    # Actualiza solo los campos que fueron enviados en el request
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(prod, field, value)
    # Confirma la transacción para persistir los cambios en la base de datos
    db.commit()
    # Refresca la instancia para obtener los valores actualizados
    db.refresh(prod)
    # Retorna el producto actualizado
    return prod


# Endpoint DELETE /api/productos/{producto_id} para eliminar un producto
# status_code=204 indica que la operación fue exitosa sin contenido en la respuesta
# Realiza un soft delete (desactiva el producto en lugar de eliminarlo físicamente)
@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    # producto_id: ID del producto a eliminar (parámetro de ruta)
    producto_id: int,
    # db: sesión de base de datos inyectada para actualizar el producto
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Consulta la base de datos para buscar el producto por ID
    prod = db.query(Producto).filter(Producto.id == producto_id).first()
    # Si el producto no existe, lanza excepción 404 Not Found
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    # Realiza soft delete estableciendo activo=False
    prod.activo = False
    # Confirma la transacción para persistir el cambio en la base de datos
    db.commit()
