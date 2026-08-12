# Importa datetime, timedelta y timezone para manejo de fechas y expiración de tokens
from datetime import datetime, timedelta, timezone
# Importa Optional para typing de valores que pueden ser None
from typing import Optional

# Importa JWTError y jwt de la librería jose para manejo de tokens JWT
# jwt.encode() crea tokens, jwt.decode() los valida
from jose import JWTError, jwt
# Importa CryptContext de passlib para hashing de contraseñas
# Proporciona funciones seguras para hashear y verificar contraseñas
from passlib.context import CryptContext

# Importa settings de config.py para obtener SECRET_KEY y configuración de JWT
# Esta configuración es necesaria para firmar y validar tokens correctamente
from app.core.config import settings

# Contexto de criptografía configurado para usar bcrypt como esquema de hashing
# bcrypt es un algoritmo lento y seguro diseñado específicamente para contraseñas
# deprecated="auto" indica que usa la versión más reciente de bcrypt disponible
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Función que hashea una contraseña en texto plano usando bcrypt
# Esta función es utilizada al crear usuarios para almacenar contraseñas de forma segura
# El hash resultante se almacena en el campo hashed_password del modelo Usuario
def hash_password(password: str) -> str:
    # Utiliza el contexto de criptografía para hashear la contraseña
    # Retorna el hash bcrypt que se almacenará en la base de datos
    return pwd_context.hash(password)


# Función que verifica si una contraseña en texto plano coincide con un hash almacenado
# Esta función es utilizada por auth.py durante el login para validar credenciales
# Compara la contraseña ingresada con el hash almacenado en la base de datos
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Utiliza el contexto de criptografía para verificar la contraseña
    # Retorna True si coinciden, False si no coinciden
    return pwd_context.verify(plain_password, hashed_password)


# Función que crea un token JWT con los datos proporcionados
# Esta función es utilizada por auth.py al generar un token tras un login exitoso
# El token contiene los datos del usuario (username) y fecha de expiración
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    # Crea una copia de los datos para no modificar el diccionario original
    to_encode = data.copy()
    # Calcula la fecha de expiración del token
    # Si se proporciona expires_delta, lo usa; de lo contrario usa el valor de configuración (60 minutos)
    # La fecha está en UTC para consistencia global
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    # Agrega la fecha de expiración al payload del token
    to_encode.update({"exp": expire})
    # Codifica el token JWT usando la clave secreta y algoritmo de la configuración
    # El token resultante es un string que se envía al cliente
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# Función que decodifica y valida un token JWT
# Esta función es utilizada por deps.py en get_current_user para extraer el usuario del token
# Verifica la firma del token usando la clave secreta y el algoritmo configurado
def decode_access_token(token: str) -> Optional[dict]:
    try:
        # Decodifica el token usando la clave secreta y algoritmo de configuración
        # Si el token es inválido, expirado o la firma no coincide, lanza JWTError
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        # Si hay cualquier error al decodificar (token inválido, expirado, etc.), retorna None
        return None
