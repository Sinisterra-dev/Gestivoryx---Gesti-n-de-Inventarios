# Importa APIRouter para crear el router de proveedores con sus endpoints
# Importa Depends para inyección de dependencias (get_db, get_current_user)
# Importa HTTPException y status para manejo de errores HTTP
from fastapi import APIRouter, Depends, HTTPException, status
# Importa Session de SQLAlchemy ORM para sesiones de base de datos
from sqlalchemy.orm import Session

# Importa get_current_user de deps.py para obtener el usuario autenticado
from app.core.deps import get_current_user
# Importa get_db de database.py para inyectar sesión de base de datos
from app.database import get_db
# Importa los modelos Proveedor y Usuario para consultas en base de datos
from app.models.models import Proveedor, Usuario
# Importa los esquemas de proveedores para validación y respuesta
from app.schemas.schemas import ProveedorCreate, ProveedorOut, ProveedorUpdate

# Crea el router de proveedores con prefijo /api/proveedores y tag "Proveedores"
router = APIRouter(prefix="/api/proveedores", tags=["Proveedores"])


# Endpoint GET /api/proveedores para listar todos los proveedores
# response_model=list[ProveedorOut] indica que la respuesta es una lista de proveedores
@router.get("/", response_model=list[ProveedorOut])
def listar_proveedores(
    # solo_activos: parámetro query opcional para filtrar solo proveedores activos
    solo_activos: bool = True,
    # db: sesión de base de datos inyectada para consultar proveedores
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Crea la query base para consultar todos los proveedores
    q = db.query(Proveedor)
    # Si solo_activos es True, filtra para retornar solo proveedores activos
    if solo_activos:
        q = q.filter(Proveedor.activo == True)
    # Ordena los proveedores por nombre alfabéticamente y retorna todos
    return q.order_by(Proveedor.nombre).all()


# Endpoint GET /api/proveedores/{proveedor_id} para obtener un proveedor específico
@router.get("/{proveedor_id}", response_model=ProveedorOut)
def obtener_proveedor(
    # proveedor_id: ID del proveedor a obtener (parámetro de ruta)
    proveedor_id: int,
    # db: sesión de base de datos inyectada para consultar el proveedor
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Consulta la base de datos para buscar el proveedor por ID
    prov = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    # Si el proveedor no existe, lanza excepción 404 Not Found
    if not prov:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    # Retorna el proveedor encontrado
    return prov


# Endpoint POST /api/proveedores para crear un nuevo proveedor
# status_code=201 indica que se creó un recurso exitosamente
@router.post("/", response_model=ProveedorOut, status_code=status.HTTP_201_CREATED)
def crear_proveedor(
    # data: datos del proveedor a crear, validados por el esquema ProveedorCreate
    data: ProveedorCreate,
    # db: sesión de base de datos inyectada para crear el proveedor
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Crea una nueva instancia de Proveedor con los datos validados
    prov = Proveedor(**data.model_dump())
    # Agrega el proveedor a la sesión de base de datos
    db.add(prov)
    # Confirma la transacción para persistir el proveedor en la base de datos
    db.commit()
    # Refresca la instancia para obtener los valores generados (id, creado_en)
    db.refresh(prov)
    # Retorna el proveedor creado
    return prov


# Endpoint PUT /api/proveedores/{proveedor_id} para actualizar un proveedor
@router.put("/{proveedor_id}", response_model=ProveedorOut)
def actualizar_proveedor(
    # proveedor_id: ID del proveedor a actualizar (parámetro de ruta)
    proveedor_id: int,
    # data: datos a actualizar, validados por el esquema ProveedorUpdate
    data: ProveedorUpdate,
    # db: sesión de base de datos inyectada para actualizar el proveedor
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Consulta la base de datos para buscar el proveedor por ID
    prov = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    # Si el proveedor no existe, lanza excepción 404 Not Found
    if not prov:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    # Actualiza solo los campos que fueron enviados en el request
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(prov, field, value)
    # Confirma la transacción para persistir los cambios en la base de datos
    db.commit()
    # Refresca la instancia para obtener los valores actualizados
    db.refresh(prov)
    # Retorna el proveedor actualizado
    return prov


# Endpoint DELETE /api/proveedores/{proveedor_id} para eliminar un proveedor
# status_code=204 indica que la operación fue exitosa sin contenido en la respuesta
# Realiza un soft delete (desactiva el proveedor en lugar de eliminarlo físicamente)
@router.delete("/{proveedor_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_proveedor(
    # proveedor_id: ID del proveedor a eliminar (parámetro de ruta)
    proveedor_id: int,
    # db: sesión de base de datos inyectada para actualizar el proveedor
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Consulta la base de datos para buscar el proveedor por ID
    prov = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    # Si el proveedor no existe, lanza excepción 404 Not Found
    if not prov:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    # Realiza soft delete estableciendo activo=False
    prov.activo = False
    # Confirma la transacción para persistir el cambio en la base de datos
    db.commit()
