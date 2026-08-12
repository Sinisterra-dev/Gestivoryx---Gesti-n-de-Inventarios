# Importa sqlite3 para conexión directa a la base de datos SQLite
import sqlite3
# Importa datetime para generar timestamps de auditoría
from datetime import datetime
# Importa pwd_context del módulo security para hashear contraseñas
# Usa la misma configuración bcrypt que el resto de la aplicación
from app.core.security import pwd_context 

# Ruta del archivo de base de datos SQLite
DB_PATH = "gestivoryx.db" 

# Conecta a la base de datos SQLite
conn = sqlite3.connect(DB_PATH)
# Crea un cursor para ejecutar consultas SQL
cursor = conn.cursor()

# Genera el hash de la contraseña "123456" usando la configuración bcrypt de la aplicación
# Esto asegura que el hash sea compatible con el sistema de autenticación
hash_nativo = pwd_context.hash("123456")
# Captura la fecha y hora actual en formato string para las columnas de auditoría
# Formato: YYYY-MM-DD HH:MM:SS
ahora_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

try:
    # 1. Inspecciona qué columnas existen realmente en la tabla usuarios
    # PRAGMA table_info retorna información sobre la estructura de la tabla
    # Esto permite que el script sea adaptable a diferentes esquemas de base de datos
    cursor.execute("PRAGMA table_info(usuarios);")
    # Extrae solo los nombres de las columnas (índice 1 de cada fila)
    columnas_reales = [row[1] for row in cursor.fetchall()]
    
    # 2. Limpia intentos previos del usuario 'alex' para evitar duplicados
    # Verifica si existe la columna username antes de eliminar por ese campo
    if "username" in columnas_reales:
        cursor.execute("DELETE FROM usuarios WHERE username='alex'")
    # Verifica si existe la columna email antes de eliminar por ese campo
    if "email" in columnas_reales:
        cursor.execute("DELETE FROM usuarios WHERE email='alex@correo.com'")
    
    # 3. Diccionario con todos los posibles campos de usuario
    # Incluye variaciones de nombres comunes para hacerlo compatible con diferentes esquemas
    posibles_datos = {
        # Variaciones de nombre de usuario
        "username": "alex",
        # Variaciones de nombre completo
        "nombre": "Alex Sinisterra",
        "nombre_completo": "Alex Sinisterra",
        "full_name": "Alex Sinisterra",
        # Variaciones de rol (en español e inglés, con diferentes formatos)
        "rol": "Administrador",
        "role": "Administrador",
        "rol": "admin",
        "role": "admin",
        # Variaciones de campo de contraseña (todas con el hash generado)
        "password": hash_nativo,
        "contrasena": hash_nativo,
        "hashed_password": hash_nativo,
        "password_hash": hash_nativo,
        # Email del usuario
        "email": "alex@correo.com",
        # Variaciones de campo de estado activo
        "activo": 1,
        "is_active": 1,
        "status": "activo",
        # Campos de auditoría de tiempo (timestamps)
        # Inyección de tiempos para cumplir restricciones NOT NULL
        "creado_en": ahora_str,
        "created_at": ahora_str,
        "actualizado_en": ahora_str,
        "updated_at": ahora_str
    }
    
    # 4. Filtra los datos para conservar solo los campos que existen en la base de datos
    # Esto evita errores al intentar insertar en columnas que no existen
    datos_finales = {k: v for k, v in posibles_datos.items() if k in columnas_reales}
    
    # 5. Inserta dinámicamente el usuario sin riesgo de nombres de columna erróneos
    if datos_finales:
        # Extrae los nombres de las columnas a insertar
        columnas = datos_finales.keys()
        # Extrae los valores correspondientes
        valores = list(datos_finales.values())
        # Genera los placeholders para los valores (uno ? por cada columna)
        placeholders = ", ".join(["?"] * len(columnas))
        
        # Construye la SQL dinámicamente con las columnas reales
        sql = f"INSERT INTO usuarios ({', '.join(columnas)}) VALUES ({placeholders})"
        # Ejecuta la inserción con los valores
        cursor.execute(sql, valores)
        # Confirma la transacción para persistir el usuario en la base de datos
        conn.commit()
        
        # Muestra mensaje de éxito con las columnas que se usaron
        print("\n=======================================================")
        print("🚀 ¡Usuario 'alex' inyectado con ÉXITO ABSOLUTO!")
        print(f"Columnas mapeadas en tu BD: {list(columnas)}")
        print("=======================================================\n")
    else:
        # Si no hay columnas compatibles, muestra mensaje de error
        print("❌ No se encontraron columnas compatibles en la tabla 'usuarios'.")

# Manejo de excepciones para capturar cualquier error durante la inserción
except Exception as e:
    print(f"❌ Error crítico al insertar: {e}")
# Finally siempre se ejecuta, haya o no excepción
finally:
    # Cierra la conexión a la base de datos
    conn.close()