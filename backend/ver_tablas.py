# Importa sqlite3 para conexión directa a la base de datos SQLite
import sqlite3

# Conecta a la base de datos SQLite existente
# "gestivoryx.db" es el archivo de base de datos del proyecto
conn = sqlite3.connect("gestivoryx.db")
# Crea un cursor para ejecutar consultas SQL
cursor = conn.cursor()

# Consulta la tabla sqlite_master para obtener todas las tablas de la base de datos
# sqlite_master es la tabla del sistema de SQLite que contiene metadata
# WHERE type='table' filtra solo tablas (excluye índices y otros objetos)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# fetchall() retorna todas las filas como una lista de tuplas
tablas = cursor.fetchall()

# Muestra encabezado y lista de tablas encontradas
print("\n==========================================")
print("📋 TUS TABLAS REALES SON:")
print("==========================================")
# Verifica si no hay tablas (base de datos vacía)
if not tablas:
    print("❌ La base de datos está totalmente vacía.")
# Itera sobre las tablas encontradas y muestra sus nombres
# t[0] es el nombre de la tabla (primera columna de cada tupla)
for t in tablas:
    print(f"   -> {t[0]}")
print("==========================================\n")

# Cierra la conexión a la base de datos
conn.close()