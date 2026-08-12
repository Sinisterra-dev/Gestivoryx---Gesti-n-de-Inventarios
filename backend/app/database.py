# Importa create_engine de SQLAlchemy para crear el motor de conexión a base de datos
# Este motor maneja el pool de conexiones y la comunicación con la base de datos
from sqlalchemy import create_engine
# Importa DeclarativeBase y sessionmaker para definir modelos y crear sesiones
# DeclarativeBase es la clase base para todos los modelos ORM
# sessionmaker es una fábrica para crear sesiones de base de datos
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Importa settings de config.py para obtener la URL de conexión a la base de datos
# Esta URL se define en el archivo .env (ej: sqlite:///./gestivoryx.db)
from app.core.config import settings

# Diccionario de argumentos de conexión específicos para SQLite
# SQLite requiere check_same_thread=False para permitir acceso desde múltiples hilos
connect_args = {}
# Verifica si la URL de la base de datos es SQLite
# Si es SQLite, configura el argumento check_same_thread=False
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Crea el motor de conexión a la base de datos usando la URL de configuración
# Este motor es utilizado por todos los modelos para realizar operaciones en la base de datos
# Los connect_args aseguran que SQLite funcione correctamente en entorno multi-hilo
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# Crea una fábrica de sesiones de base de datos
# autocommit=False: las transacciones no se confirman automáticamente
# autoflush=False: los cambios no se envían a la base de datos hasta hacer flush() o commit()
# bind=engine: vincula la sesión al motor de conexión creado anteriormente
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Clase base de la que heredarán todos los modelos ORM
# Hereda de DeclarativeBase de SQLAlchemy 2.0
# Todos los modelos en models.py heredarán de esta clase
class Base(DeclarativeBase):
    pass


# Función de dependencia de FastAPI que proporciona una sesión de base de datos
# Esta función es utilizada por todos los routers para obtener una sesión de base de datos
# Es una dependency de FastAPI, por lo que se llama automáticamente en cada request
def get_db():
    # Crea una nueva sesión de base de datos usando la fábrica SessionLocal
    # Esta sesión permite realizar consultas y transacciones en la base de datos
    db = SessionLocal()
    try:
        # Yield la sesión para que el endpoint la use
        # La sesión permanece abierta mientras se ejecuta el endpoint
        yield db
    finally:
        # Cierra la sesión después de que el endpoint termina
        # Esto asegura que los recursos de la base de datos se liberen correctamente
        # Se ejecuta tanto si el endpoint tiene éxito como si lanza una excepción
        db.close()
