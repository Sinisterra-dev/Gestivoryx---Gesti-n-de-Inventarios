# Importa Depends y HTTPException de FastAPI para inyección de dependencias y manejo de errores HTTP
# Importa status para códigos de estado HTTP predefinidos
from fastapi import Depends, HTTPException, status
# Importa OAuth2PasswordBearer para manejar esquema de autenticación OAuth2 con password
# Este esquema extrae automáticamente el token Bearer del header Authorization
from fastapi.security import OAuth2PasswordBearer
# Importa Session de SQLAlchemy ORM para manejar sesiones de base de datos
from sqlalchemy.orm import Session

# Importa decode_access_token del módulo security para validar tokens JWT
# Esta función decodifica y verifica la firma del token
from app.core.security import decode_access_token
# Importa get_db del módulo database para inyectar sesión de base de datos
# Esta función es una dependencia que proporciona una sesión SQLAlchemy
from app.database import get_db
# Importa el modelo Usuario para consultas de autenticación en base de datos
from app.models.models import Usuario

# Instancia de OAuth2PasswordBearer configurada para obtener token desde endpoint /api/auth/login
# Este esquema es utilizado por get_current_user para extraer el token del header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Dependencia de FastAPI que valida el token JWT y retorna el usuario autenticado
# Esta función es utilizada por todos los routers para proteger endpoints que requieren autenticación
# El token se extrae automáticamente del header Authorization: Bearer <token>
def get_current_user(
    # token: token JWT extraído del header Authorization por oauth2_scheme
    # db: sesión de base de datos inyectada por get_db para consultar usuario
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    # Define excepción HTTP 401 que se lanza cuando no se pueden validar las credenciales
    # Incluye header WWW-Authenticate: Bearer para indicar que se requiere autenticación
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Decodifica el token JWT usando decode_access_token de security.py
    # Si el token es inválido o expiró, retorna None
    payload = decode_access_token(token)
    # Si payload es None, el token no pudo ser decodificado, lanza excepción 401
    if payload is None:
        raise credentials_exception
    # Extrae el username del payload del token (campo "sub" = subject)
    username: str = payload.get("sub")
    # Si no hay username en el payload, el token es inválido, lanza excepción 401
    if username is None:
        raise credentials_exception
    # Consulta la base de datos para obtener el usuario con ese username
    # Usa la sesión db inyectada para query al modelo Usuario
    user = db.query(Usuario).filter(Usuario.username == username).first()
    # Si el usuario no existe o está desactivo (activo=False), lanza excepción 401
    # Esto previene acceso con tokens de usuarios eliminados o deshabilitados
    if user is None or not user.activo:
        raise credentials_exception
    # Retorna el usuario autenticado para ser usado por los endpoints
    return user


# Dependencia que verifica que el usuario tenga rol de administrador
# Esta función depende de get_current_user, por lo que primero valida el token
# Es utilizada por endpoints que requieren permisos de administrador (ej: CRUD usuarios)
def get_admin_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    # Verifica si el rol del usuario no es "admin"
    # Si no es admin, lanza excepción HTTP 403 Forbidden
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos de administrador",
        )
    # Si es admin, retorna el usuario para que el endpoint pueda proceder
    return current_user
