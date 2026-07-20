import sqlite3
from datetime import datetime
from app.core.security import pwd_context 

DB_PATH = "gestivoryx.db" 

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Generamos el hash en tiempo real con tu librería nativa
hash_nativo = pwd_context.hash("123456")
# Capturamos la fecha y hora actual para las columnas de auditoría
ahora_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

try:
    # 1. Inspeccionamos qué columnas existen realmente en tu tabla de usuarios
    cursor.execute("PRAGMA table_info(usuarios);")
    columnas_reales = [row[1] for row in cursor.fetchall()]
    
    # 2. Limpiamos intentos previos de forma segura según tus columnas
    if "username" in columnas_reales:
        cursor.execute("DELETE FROM usuarios WHERE username='alex'")
    if "email" in columnas_reales:
        cursor.execute("DELETE FROM usuarios WHERE email='alex@correo.com'")
    
    # 3. Diccionario con los campos de usuario y campos de auditoría de tiempo
    posibles_datos = {
        "username": "alex",
        "nombre": "Alex Sinisterra",
        "nombre_completo": "Alex Sinisterra",
        "full_name": "Alex Sinisterra",
        "rol": "Administrador",
        "role": "Administrador",
        "rol": "admin",
        "role": "admin",
        "password": hash_nativo,
        "contrasena": hash_nativo,
        "hashed_password": hash_nativo,
        "password_hash": hash_nativo,
        "email": "alex@correo.com",
        "activo": 1,
        "is_active": 1,
        "status": "activo",
        # Inyección de tiempos para cumplir restricciones NOT NULL
        "creado_en": ahora_str,
        "created_at": ahora_str,
        "actualizado_en": ahora_str,
        "updated_at": ahora_str
    }
    
    # 4. Filtramos: Solo conservamos los campos que tu base de datos sí tenga
    datos_finales = {k: v for k, v in posibles_datos.items() if k in columnas_reales}
    
    # 5. Insertamos dinámicamente sin riesgo de nombres de columna erróneos
    if datos_finales:
        columnas = datos_finales.keys()
        valores = list(datos_finales.values())
        placeholders = ", ".join(["?"] * len(columnas))
        
        sql = f"INSERT INTO usuarios ({', '.join(columnas)}) VALUES ({placeholders})"
        cursor.execute(sql, valores)
        conn.commit()
        
        print("\n=======================================================")
        print("🚀 ¡Usuario 'alex' inyectado con ÉXITO ABSOLUTO!")
        print(f"Columnas mapeadas en tu BD: {list(columnas)}")
        print("=======================================================\n")
    else:
        print("❌ No se encontraron columnas compatibles en la tabla 'usuarios'.")

except Exception as e:
    print(f"❌ Error crítico al insertar: {e}")
finally:
    conn.close()