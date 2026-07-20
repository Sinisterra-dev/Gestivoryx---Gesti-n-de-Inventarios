import sqlite3

# Abrimos tu base de datos real
conn = sqlite3.connect("gestivoryx.db")
cursor = conn.cursor()

# Le pedimos a SQLite que nos diga qué tablas existen
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablas = cursor.fetchall()

print("\n==========================================")
print("📋 TUS TABLAS REALES SON:")
print("==========================================")
if not tablas:
    print("❌ La base de datos está totalmente vacía.")
for t in tablas:
    print(f"   -> {t[0]}")
print("==========================================\n")

conn.close()