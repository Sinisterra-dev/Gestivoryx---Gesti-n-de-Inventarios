# Importa APIRouter para crear el router de usuarios con sus endpoints
# Importa Depends para inyección de dependencias (get_db, get_current_user, get_admin_user)
# Importa HTTPException y status para manejo de errores HTTP
from fastapi import APIRouter, Depends, HTTPException, status
# Importa Session de SQLAlchemy ORM para sesiones de base de datos
from sqlalchemy.orm import Session

# Importa get_admin_user y get_current_user de deps.py para autenticación y autorización
# get_admin_user verifica que el usuario tenga rol de administrador
# get_current_user valida el token JWT y retorna el usuario autenticado
from app.core.deps import get_admin_user, get_current_user
# Importa hash_password de security.py para hashear contraseñas al crear usuarios
from app.core.security import hash_password
# Importa get_db de database.py para inyectar sesión de base de datos
from app.database import get_db
# Importa el modelo Usuario para consultas en base de datos
from app.models.models import Usuario
# Importa los esquemas de usuarios para validación y respuesta
from app.schemas.schemas import UsuarioCreate, UsuarioOut, UsuarioUpdate

# Crea el router de usuarios con prefijo /api/usuarios y tag "Usuarios"
router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])


# Endpoint GET /api/usuarios para listar todos los usuarios
# response_model=list[UsuarioOut] indica que la respuesta es una lista de usuarios
# Este endpoint requiere rol de administrador (usa get_admin_user como dependencia)
@router.get("/", response_model=list[UsuarioOut])
def listar_usuarios(
    # db: sesión de base de datos inyectada para consultar usuarios
    db: Session = Depends(get_db),
    # _: usuario administrador autenticado (get_admin_user valida rol admin)
    _: Usuario = Depends(get_admin_user),
):
    # Retorna todos los usuarios de la base de datos
    # Solo los administradores pueden ver la lista completa de usuarios
    return db.query(Usuario).all()


# Endpoint GET /api/usuarios/{usuario_id} para obtener un usuario específico
# Un admin puede ver cualquier usuario, un usuario normal solo puede verse a sí mismo
@router.get("/{usuario_id}", response_model=UsuarioOut)
def obtener_usuario(
    # usuario_id: ID del usuario a obtener (parámetro de ruta)
    usuario_id: int,
    # db: sesión de base de datos inyectada para consultar el usuario
    db: Session = Depends(get_db),
    # current_user: usuario autenticado (puede ser admin o usuario normal)
    current_user: Usuario = Depends(get_current_user),
):
    # Verifica permisos: solo admin puede ver otros usuarios
    # Un usuario normal solo puede ver su propio perfil
    if current_user.rol != "admin" and current_user.id != usuario_id:
        # Si no tiene permisos, lanza excepción 403 Forbidden
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos")
    # Consulta la base de datos para buscar el usuario por ID
    user = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    # Si el usuario no existe, lanza excepción 404 Not Found
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # Retorna el usuario encontrado
    return user


# Endpoint POST /api/usuarios para crear un nuevo usuario
# status_code=201 indica que se creó un recurso exitosamente
# Este endpoint requiere rol de administrador (usa get_admin_user como dependencia)
@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    # data: datos del usuario a crear, validados por el esquema UsuarioCreate
    data: UsuarioCreate,
    # db: sesión de base de datos inyectada para crear el usuario
    db: Session = Depends(get_db),
    # _: usuario administrador autenticado (get_admin_user valida rol admin)
    _: Usuario = Depends(get_admin_user),
):
    # Verifica si ya existe un usuario con el mismo username
    # Esto previene duplicados de usernames
    if db.query(Usuario).filter(Usuario.username == data.username).first():
        # Si existe, lanza excepción 400 Bad Request
        raise HTTPException(status_code=400, detail="El username ya existe")
    # Verifica si ya existe un usuario con el mismo email
    # Esto previene duplicados de emails
    if db.query(Usuario).filter(Usuario.email == data.email).first():
        # Si existe, lanza excepción 400 Bad Request
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    # Crea una nueva instancia de Usuario con los datos validados
    # La contraseña se hashea usando hash_password() antes de almacenarla
    user = Usuario(
        username=data.username,
        email=data.email,
        nombre=data.nombre,
        rol=data.rol,
        hashed_password=hash_password(data.password),
    )
    # Agrega el usuario a la sesión de base de datos
    db.add(user)
    # Confirma la transacción para persistir el usuario en la base de datos
    db.commit()
    # Refresca la instancia para obtener los valores generados (id, creado_en)
    db.refresh(user)
    # Retorna el usuario creado (sin la contraseña hasheada)
    return user


# Endpoint PUT /api/usuarios/{usuario_id} para actualizar un usuario
# Un admin puede actualizar cualquier usuario, un usuario normal solo puede actualizarse a sí mismo
@router.put("/{usuario_id}", response_model=UsuarioOut)
def actualizar_usuario(
    # usuario_id: ID del usuario a actualizar (parámetro de ruta)
    usuario_id: int,
    # data: datos a actualizar, validados por el esquema UsuarioUpdate
    data: UsuarioUpdate,
    # db: sesión de base de datos inyectada para actualizar el usuario
    db: Session = Depends(get_db),
    # current_user: usuario autenticado (puede ser admin o usuario normal)
    current_user: Usuario = Depends(get_current_user),
):
    # Verifica permisos: solo admin puede actualizar otros usuarios
    # Un usuario normal solo puede actualizarse a sí mismo
    if current_user.rol != "admin" and current_user.id != usuario_id:
        # Si no tiene permisos, lanza excepción 403 Forbidden
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sin permisos")
    # Consulta la base de datos para buscar el usuario por ID
    user = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    # Si el usuario no existe, lanza excepción 404 Not Found
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # Convierte los datos a diccionario, excluyendo campos no enviados
    update_data = data.model_dump(exclude_unset=True)
    # Si se está actualizando la contraseña, la hashea antes de guardar
    if "password" in update_data:
        # Hashea la nueva contraseña y la asigna al campo hashed_password
        user.hashed_password = hash_password(update_data.pop("password"))
    # Actualiza los campos restantes que fueron enviados en el request
    for field, value in update_data.items():
        setattr(user, field, value)
    # Confirma la transacción para persistir los cambios en la base de datos
    db.commit()
    # Refresca la instancia para obtener los valores actualizados
    db.refresh(user)
    # Retorna el usuario actualizado
    return user


# Endpoint DELETE /api/usuarios/{usuario_id} para eliminar un usuario
# status_code=204 indica que la operación fue exitosa sin contenido en la respuesta
# Este endpoint requiere rol de administrador (usa get_admin_user como dependencia)
# Realiza un hard delete (elimina físicamente el registro, no soft delete)
@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    # usuario_id: ID del usuario a eliminar (parámetro de ruta)
    usuario_id: int,
    # db: sesión de base de datos inyectada para eliminar el usuario
    db: Session = Depends(get_db),
    # current_user: usuario administrador autenticado (get_admin_user valida rol admin)
    current_user: Usuario = Depends(get_admin_user),
):
    # Previene que un usuario se elimine a sí mismo
    if current_user.id == usuario_id:
        # Si intenta eliminarse a sí mismo, lanza excepción 400 Bad Request
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")
    # Consulta la base de datos para buscar el usuario por ID
    user = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    # Si el usuario no existe, lanza excepción 404 Not Found
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # Elimina físicamente el usuario de la base de datos
    db.delete(user)
    # Confirma la transacción para persistir la eliminación
    db.commit()
