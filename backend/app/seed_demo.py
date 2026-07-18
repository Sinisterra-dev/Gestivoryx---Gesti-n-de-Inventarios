import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "gestivoryx.db"

def conectar_db():
    return sqlite3.connect(DB_NAME)

def poblar_datos():
    conn = conectar_db()
    cursor = conn.cursor()
    
    print("⏳ Limpiando datos antiguos para evitar duplicados...")
    cursor.execute("DELETE FROM detalle_ventas")
    cursor.execute("DELETE FROM ventas")
    cursor.execute("DELETE FROM productos")
    cursor.execute("DELETE FROM clientes")
    cursor.execute("DELETE FROM proveedores")
    
    # 1. Insertar Proveedores Realistas
    print("📦 Insertando proveedores...")
    proveedores = [
        ("Tech Distribution S.A.S.", "Carlos Mendoza", "3157894512"),
        ("Logística y Suministros Global", "Ana María Silva", "3104561234"),
        ("Importaciones del Pacífico", "Jorge Eliecer", "3189876543"),
        ("Mayorista de Oficina Express", "Elena Gómez", "3001234567")
    ]
    cursor.executemany(
        "INSERT INTO proveedores (nombre, contacto, telefono) VALUES (?, ?, ?)", 
        proveedores
    )
    
    # Obtener IDs de proveedores generados
    cursor.execute("SELECT id FROM proveedores")
    proveedor_ids = [row[0] for row in cursor.fetchall()]

    # 2. Insertar Productos con Margen de Ganancia Lógico
    print("💻 Insertando catálogo de productos...")
    # Formato: (Nombre, Categoría, Stock Inicial, Precio Compra, Precio Venta, Proveedor_ID)
    productos_plantilla = [
        ("Mouse Ergonómico Inalámbrico", "Accesorios", 45, 15.00, 29.99),
        ("Teclado Mecánico RGB", "Accesorios", 20, 45.00, 79.90),
        ("Monitor 24 Pulgadas FHD", "Electrónica", 12, 95.00, 149.00),
        ("Disco Duro Externo 1TB", "Almacenamiento", 30, 35.00, 59.99),
        ("Memoria USB 64GB Tipo C", "Almacenamiento", 100, 5.50, 12.50),
        ("Silla de Oficina Ergonómica", "Oficina", 8, 80.00, 135.00),
        ("Hub USB-C 7 en 1", "Accesorios", 25, 18.00, 34.99),
        ("Cargador Carga Rápida 65W", "Electrónica", 50, 12.00, 24.50),
        ("Audífonos Noise Cancelling", "Electrónica", 15, 65.00, 110.00),
        ("Escritorio Elevable Manual", "Oficina", 5, 120.00, 199.99)
    ]
    
    productos = []
    for p in productos_plantilla:
        # Asigna un proveedor aleatorio de los que acabamos de insertar
        prov_id = random.choice(proveedor_ids)
        productos.append((p[0], p[1], p[2], p[3], p[4], prov_id))
        
    cursor.executemany(
        "INSERT INTO productos (nombre, categoria, stock, precio_compra, precio_venta, proveedor_id) VALUES (?, ?, ?, ?, ?, ?)",
        productos
    )

    # 3. Insertar Clientes
    print("👥 Insertando clientes de prueba...")
    clientes = [
        ("Alejandro Sinisterra", "alex@correo.com", "3120001122"),
        ("Claudia Restrepo", "claudia.r@outlook.com", "3165554433"),
        ("Sistemas Luro Legal", "contacto@lurolegal.com", "3017778899"),
        ("Estudio Digital Pixel", "info@pixel.co", "3114445566"),
        ("Andrés Caicedo", "andres99@gmail.com", "3153332211")
    ]
    cursor.executemany(
        "INSERT INTO clientes (nombre, email, telefono) VALUES (?, ?, ?)", 
        clientes
    )
    
    # Obtener IDs de clientes y productos para armar las ventas
    cursor.execute("SELECT id FROM clientes")
    cliente_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id, precio_venta, stock FROM productos")
    productos_db = cursor.fetchall() # Lista de tuplas (id, precio_venta, stock)

    # 4. Generar Ventas Históricas Dinámicas (Últimos 30 días)
    print("📈 Generando historial de ventas dinámico...")
    hoy = datetime.now()
    
    # Vamos a generar entre 20 y 30 transacciones distribuidas en el tiempo
    num_ventas = random.randint(20, 30)
    
    for _ in range(num_ventas):
        cliente_id = random.choice(cliente_ids)
        # Genera una fecha aleatoria en los últimos 30 días para simular actividad real
        dias_atras = random.randint(0, 30)
        horas_atras = random.randint(8, 18) # Horario laboral simulado
        fecha_venta = (hoy - timedelta(days=dias_atras)).replace(hour=horas_atras, minute=random.randint(0, 59))
        fecha_str = fecha_venta.strftime("%Y-%m-%d %H:%M:%S")
        
        # Insertar la cabecera de la venta temporalmente con total 0
        cursor.execute(
            "INSERT INTO ventas (cliente_id, fecha, total) VALUES (?, ?, ?)",
            (cliente_id, fecha_str, 0)
        )
        venta_id = cursor.lastrowid
        
        # Determinar cuántos productos diferentes lleva este cliente en esta compra (1 a 3)
        items_en_venta = random.randint(1, 3)
        productos_seleccionados = random.sample(productos_db, items_en_venta)
        
        total_venta = 0
        for prod_id, precio_venta, stock in productos_seleccionados:
            cantidad = random.randint(1, 2) # Compras al por menor normales
            subtotal = cantidad * precio_venta
            total_venta += subtotal
            
            # Registrar el detalle
            cursor.execute(
                "INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario) VALUES (?, ?, ?, ?)",
                (venta_id, prod_id, cantidad, precio_venta)
            )
            
            # Descontar del stock físico para simular consistencia en el inventario
            cursor.execute(
                "UPDATE productos SET stock = stock - ? WHERE id = ?",
                (cantidad, prod_id)
            )
            
        # Actualizar el total real de la cabecera de la venta
        cursor.execute(
            "UPDATE ventas SET total = ? WHERE id = ?",
            (total_venta, venta_id)
        )

    conn.commit()
    conn.close()
    print("✅ ¡Base de datos poblada con éxito para la demo!")

if __name__ == "__main__":
    poblar_datos()