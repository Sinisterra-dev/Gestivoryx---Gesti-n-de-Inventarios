# Importa APIRouter para crear el router de clientes con sus endpoints
# Importa Depends para inyección de dependencias (get_db, get_current_user)
# Importa HTTPException y status para manejo de errores HTTP
from fastapi import APIRouter, Depends, HTTPException, status
# Importa Session de SQLAlchemy ORM para sesiones de base de datos
from sqlalchemy.orm import Session

# Importa get_current_user de deps.py para obtener el usuario autenticado
from app.core.deps import get_current_user
# Importa get_db de database.py para inyectar sesión de base de datos
from app.database import get_db
# Importa los modelos Cliente y Usuario para consultas en base de datos
from app.models.models import Cliente, Usuario
# Importa los esquemas de clientes para validación y respuesta
from app.schemas.schemas import ClienteCreate, ClienteOut, ClienteUpdate

# Crea el router de clientes con prefijo /api/clientes y tag "Clientes"
router = APIRouter(prefix="/api/clientes", tags=["Clientes"])


# Endpoint GET /api/clientes para listar todos los clientes
# response_model=list[ClienteOut] indica que la respuesta es una lista de clientes
@router.get("/", response_model=list[ClienteOut])
def listar_clientes(
    # solo_activos: parámetro query opcional para filtrar solo clientes activos
    solo_activos: bool = True,
    # db: sesión de base de datos inyectada para consultar clientes
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Crea la query base para consultar todos los clientes
    q = db.query(Cliente)
    # Si solo_activos es True, filtra para retornar solo clientes activos
    if solo_activos:
        q = q.filter(Cliente.activo == True)
    # Ordena los clientes por nombre alfabéticamente y retorna todos
    return q.order_by(Cliente.nombre).all()


# Endpoint GET /api/clientes/{cliente_id} para obtener un cliente específico
@router.get("/{cliente_id}", response_model=ClienteOut)
def obtener_cliente(
    # cliente_id: ID del cliente a obtener (parámetro de ruta)
    cliente_id: int,
    # db: sesión de base de datos inyectada para consultar el cliente
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Consulta la base de datos para buscar el cliente por ID
    cli = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    # Si el cliente no existe, lanza excepción 404 Not Found
    if not cli:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    # Retorna el cliente encontrado
    return cli


# Endpoint POST /api/clientes para crear un nuevo cliente
# status_code=201 indica que se creó un recurso exitosamente
@router.post("/", response_model=ClienteOut, status_code=status.HTTP_201_CREATED)
def crear_cliente(
    # data: datos del cliente a crear, validados por el esquema ClienteCreate
    data: ClienteCreate,
    # db: sesión de base de datos inyectada para crear el cliente
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Crea una nueva instancia de Cliente con los datos validados
    cli = Cliente(**data.model_dump())
    # Agrega el cliente a la sesión de base de datos
    db.add(cli)
    # Confirma la transacción para persistir el cliente en la base de datos
    db.commit()
    # Refresca la instancia para obtener los valores generados (id, creado_en)
    db.refresh(cli)
    # Retorna el cliente creado
    return cli


# Endpoint PUT /api/clientes/{cliente_id} para actualizar un cliente
@router.put("/{cliente_id}", response_model=ClienteOut)
def actualizar_cliente(
    # cliente_id: ID del cliente a actualizar (parámetro de ruta)
    cliente_id: int,
    # data: datos a actualizar, validados por el esquema ClienteUpdate
    data: ClienteUpdate,
    # db: sesión de base de datos inyectada para actualizar el cliente
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Consulta la base de datos para buscar el cliente por ID
    cli = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    # Si el cliente no existe, lanza excepción 404 Not Found
    if not cli:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    # Actualiza solo los campos que fueron enviados en el request
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cli, field, value)
    # Confirma la transacción para persistir los cambios en la base de datos
    db.commit()
    # Refresca la instancia para obtener los valores actualizados
    db.refresh(cli)
    # Retorna el cliente actualizado
    return cli


# Endpoint DELETE /api/clientes/{cliente_id} para eliminar un cliente
# status_code=204 indica que la operación fue exitosa sin contenido en la respuesta
# Realiza un soft delete (desactiva el cliente en lugar de eliminarlo físicamente)
@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(
    # cliente_id: ID del cliente a eliminar (parámetro de ruta)
    cliente_id: int,
    # db: sesión de base de datos inyectada para actualizar el cliente
    db: Session = Depends(get_db),
    # _: usuario autenticado para validar el request
    _: Usuario = Depends(get_current_user),
):
    # Consulta la base de datos para buscar el cliente por ID
    cli = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    # Si el cliente no existe, lanza excepción 404 Not Found
    if not cli:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    # Realiza soft delete estableciendo activo=False
    cli.activo = False
    # Confirma la transacción para persistir el cambio en la base de datos
    db.commit()

