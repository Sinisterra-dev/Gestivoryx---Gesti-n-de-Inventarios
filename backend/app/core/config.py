# Importa BaseSettings y SettingsConfigDict de pydantic_settings para manejar configuración desde variables de entorno
# Este módulo permite cargar configuraciones desde archivo .env y validar tipos automáticamente
from pydantic_settings import BaseSettings, SettingsConfigDict


# Clase Settings que define todas las variables de configuración del sistema
# Hereda de BaseSettings para cargar automáticamente valores desde archivo .env
# Esta configuración es utilizada por main.py, security.py y otros módulos del sistema
class Settings(BaseSettings):
    # Configura que pydantic lea configuración desde archivo .env en el directorio actual
    # extra="ignore" permite que haya variables adicionales en .env sin causar error
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Clave secreta utilizada para firmar tokens JWT - debe cambiarse en producción
    # Usada por security.py para crear y validar tokens de autenticación
    SECRET_KEY: str = "cambia-esto-en-produccion-usa-una-clave-segura-de-64-caracteres"
    # URL de conexión a la base de datos SQLite - utilizada por database.py
    DATABASE_URL: str = "sqlite:///./gestivoryx.db"
    # Tiempo de expiración en minutos para tokens JWT - usado por security.py
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # Algoritmo de cifrado para tokens JWT (HS256) - usado por security.py
    ALGORITHM: str = "HS256"
    # Puerto donde correrá el servidor FastAPI - usado por main.py
    APP_PORT: int = 3000
    # Orígenes permitidos para CORS - usado por main.py para configurar middleware CORS
    # Puede ser "*" para permitir todos o una lista separada por comas de dominios específicos
    ALLOWED_ORIGINS: str = "*"

    # Propiedad que convierte la cadena ALLOWED_ORIGINS en una lista de strings
    # Si es "*", retorna ["*"], de lo contrario divide por comas y elimina espacios
    # Esta lista es utilizada por main.py para configurar el middleware CORS
    @property
    def cors_origins(self) -> list[str]:
        # Si el origen es "*", permite todos los orígenes retornando lista con asterisco
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        # Si no, divide la cadena por comas, elimina espacios de cada origen y retorna lista
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


# Instancia única de Settings que será importada por otros módulos
# Esta instancia carga automáticamente las variables desde .env al iniciar la aplicación
# Es importada por main.py, security.py y otros módulos que necesitan configuración
settings = Settings()

# Valor por defecto inseguro de la clave secreta para detectar si no se cambió
_DEFAULT_KEY = "cambia-esto-en-produccion-usa-una-clave-segura-de-64-caracteres"
# Verifica si la clave secreta sigue siendo el valor por defecto inseguro
# Si es así, emite un warning advirtiendo que debe cambiarse antes de producción
if settings.SECRET_KEY == _DEFAULT_KEY:
    import warnings
    warnings.warn(
        "⚠️  SECRET_KEY uses the default insecure value. "
        "Set a strong random key in your .env file before deploying to production.",
        stacklevel=1,
    )
