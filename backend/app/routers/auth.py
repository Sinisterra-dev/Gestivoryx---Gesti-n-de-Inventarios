# Importa APIRouter para crear el router de autenticación con sus endpoints
# Importa Depends para inyección de dependencias (get_db, get_current_user)
# Importa HTTPException y status para manejo de errores HTTP
from fastapi import APIRouter, Depends, HTTPException, status
# Importa OAuth2PasswordRequestForm para manejar el formulario de login OAuth2
# Este formulario espera username y password en el cuerpo del request
from fastapi.security import OAuth2PasswordRequestForm
# Importa Session de SQLAlchemy ORM para sesiones de base de datos
from sqlalchemy.orm import Session

# Importa get_current_user de deps.py para obtener el usuario autenticado
# Esta dependencia valida el token JWT y retorna el usuario
from app.core.deps import get_current_user
# Importa create_access_token y verify_password de security.py
# create_access_token genera el JWT tras login exitoso
# verify_password valida la contraseña ingresada contra el hash almacenado
from app.core.security import create_access_token, verify_password
# Importa get_db de database.py para inyectar sesión de base de datos
from app.database import get_db
# Importa el modelo Usuario para consultar usuarios en la base de datos
from app.models.models import Usuario
# Importa los esquemas Token y UsuarioOut para validación y respuesta
# Token define la estructura de respuesta del login (access_token, usuario)
# UsuarioOut define la estructura de datos del usuario a retornar
from app.schemas.schemas import Token, UsuarioOut

# Crea el router de autenticación con prefijo /api/auth y tag "Autenticación"
# El prefijo se añade a todas las rutas de este router
# El tag organiza los endpoints en la documentación Swagger
router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


# Endpoint POST /api/auth/login para autenticar usuarios
# response_model=Token indica que la respuesta seguirá el esquema Token
# Este endpoint recibe username y password via OAuth2PasswordRequestForm
@router.post("/login", response_model=Token)
def login(
    # form_data: formulario OAuth2 con username y password del request
    # db: sesión de base de datos inyectada para consultar el usuario
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # Consulta la base de datos para buscar el usuario por username
    # filter(Usuario.username == form_data.username) filtra por el username ingresado
    # first() retorna el primer resultado o None si no existe
    user = db.query(Usuario).filter(Usuario.username == form_data.username).first()
    # Verifica si el usuario no existe O si la contraseña es incorrecta
    # verify_password compara la contraseña ingresada con el hash almacenado
    if not user or not verify_password(form_data.password, user.hashed_password):
        # Si las credenciales son inválidas, lanza excepción 401 Unauthorized
        # El header WWW-Authenticate indica que se requiere autenticación Bearer
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Verifica si el usuario está desactivado (activo=False)
    # Esto previene que usuarios deshabilitados puedan iniciar sesión
    if not user.activo:
        # Si el usuario está desactivado, lanza excepción 403 Forbidden
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado",
        )
    # Crea un token JWT con el username como subject ("sub")
    # Este token será usado por el cliente para autenticar requests subsiguientes
    access_token = create_access_token(data={"sub": user.username})
    # Retorna el token JWT junto con el usuario validado
    # token_type: "bearer" indica el tipo de token
    # usuario: datos del usuario siguiendo el esquema UsuarioOut
    return Token(
        access_token=access_token,
        token_type="bearer",
        usuario=UsuarioOut.model_validate(user),
    )


# Endpoint GET /api/auth/me para obtener información del usuario autenticado
# response_model=UsuarioOut indica que la respuesta seguirá el esquema UsuarioOut
# Este endpoint requiere autenticación (usa get_current_user como dependencia)
@router.get("/me", response_model=UsuarioOut)
def me(current_user: Usuario = Depends(get_current_user)):
    # current_user: usuario autenticado inyectado por get_current_user
    # get_current_user valida el token JWT y retorna el usuario correspondiente
    # Retorna la información del usuario autenticado
    return current_user
