import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "gestivoryx.db"

def conectar_db():
    return sqlite3.connect(DB_NAME)

def poblar_datos():
    conn = conectar_db()
    cursor = conn.cursor()
    
    print("⏳ Limpiando las 8 tablas para evitar duplicados...")
    cursor.execute("DELETE FROM detalles_venta")
    cursor.execute("DELETE FROM movimientos")
    cursor.execute("DELETE FROM ventas")
    cursor.execute("DELETE FROM productos")
    cursor.execute("DELETE FROM clientes")
    cursor.execute("DELETE FROM proveedores")
    cursor.execute("DELETE FROM categorias")
    cursor.execute("DELETE FROM usuarios")
    
    # 1. Insertar Usuario Administrador para la sesión de la Demo
    print("👤 Insertando usuarios...")
    # Nota: Si tus columnas se llaman diferente (ej. contrasena, email), se ajustan aquí
    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre, rol) VALUES (?, ?)", 
            ("ALEX", "Administrador")
        )
    except sqlite3.OperationalError:
        # Por si tu tabla tiene campos obligatorios como email/password
        cursor.execute(
            "INSERT INTO usuarios (nombre, rol, email, password) VALUES (?, ?, ?, ?)", 
            ("ALEX", "Administrador", "alex@gestivoryx.com", "123456")
        )
    
    # 2. Insertar Categorías Independientes
    print("🗂️ Insertando categorías...")
    categorias = [("Accesorios",), ("Electrónica",), ("Almacenamiento",), ("Oficina",)]
    cursor.executemany("INSERT INTO categorias (nombre) VALUES (?)", categorias)

    # 3. Insertar Proveedores
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
    
    cursor.execute("SELECT id FROM proveedores")
    proveedor_ids = [row[0] for row in cursor.fetchall()]

    # 4. Insertar Catálogo de Productos e Historial de Movimientos (Entradas Iniciales)
    print("💻 Insertando productos y registrando entradas de inventario...")
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
    
    fecha_inicial = (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d %H:%M:%S")
    
    for p in productos_plantilla:
        prov_id = random.choice(proveedor_ids)
        # Insertar producto
        cursor.execute(
            "INSERT INTO productos (nombre, categoria, stock, precio_compra, precio_venta, proveedor_id) VALUES (?, ?, ?, ?, ?, ?)",
            (p[0], p[1], p[2], p[3], p[4], prov_id)
        )
        prod_id = cursor.lastrowid
        
        # REGISTRO DE MOVIMIENTO: Entrada Inicial de Stock
        try:
            cursor.execute(
                "INSERT INTO movimientos (producto_id, tipo, cantidad, fecha, motivo) VALUES (?, ?, ?, ?, ?)",
                (prod_id, "Entrada", p[2], fecha_inicial, "Carga inicial de inventario")
            )
        except sqlite3.OperationalError:
            # Por si tus columnas se llaman tipo_movimiento o descripcion
            cursor.execute(
                "INSERT INTO movimientos (producto_id, tipo_movimiento, cantidad, fecha, descripcion) VALUES (?, ?, ?, ?, ?)",
                (prod_id, "Entrada", p[2], fecha_inicial, "Carga inicial de inventario")
            )

    # 5. Insertar Clientes
    print("👥 Insertando clientes...")
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
    
    cursor.execute("SELECT id FROM clientes")
    cliente_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id, precio_venta, nombre FROM productos")
    productos_db = cursor.fetchall()

    # 6. Generar Ventas e Historial de Movimientos (Salidas por Ventas)
    print("📈 Generando historial dinámico de ventas y salidas de stock...")
    hoy = datetime.now()
    num_ventas = random.randint(25, 35)
    
    for _ in range(num_ventas):
        cliente_id = random.choice(cliente_ids)
        dias_atras = random.randint(0, 30)
        horas_atras = random.randint(8, 18)
        fecha_venta = (hoy - timedelta(days=dias_atras)).replace(hour=horas_atras, minute=random.randint(0, 59))
        fecha_str = fecha_venta.strftime("%Y-%m-%d %H:%M:%S")
        
        # Insertar cabecera de venta
        cursor.execute(
            "INSERT INTO ventas (cliente_id, fecha, total) VALUES (?, ?, ?)",
            (cliente_id, fecha_str, 0)
        )
        venta_id = cursor.lastrowid
        
        items_en_venta = random.randint(1, 3)
        productos_seleccionados = random.sample(productos_db, items_en_venta)
        
        total_venta = 0
        for prod_id, precio_venta, nombre_prod in productos_seleccionados:
            cantidad = random.randint(1, 2)
            subtotal = cantidad * precio_venta
            total_venta += subtotal
            
            # Insertar detalle de venta
            cursor.execute(
                "INSERT INTO detalles_venta (venta_id, producto_id, cantidad, precio_unitario) VALUES (?, ?, ?, ?)",
                (venta_id, prod_id, cantidad, precio_venta)
            )
            
            # Descontar del stock del producto
            cursor.execute(
                "UPDATE productos SET stock = stock - ? WHERE id = ?",
                (cantidad, prod_id)
            )
            
            # REGISTRO DE MOVIMIENTO: Salida por Venta
            try:
                cursor.execute(
                    "INSERT INTO movimientos (producto_id, tipo, cantidad, fecha, motivo) VALUES (?, ?, ?, ?, ?)",
                    (prod_id, "Salida", cantidad, fecha_str, f"Venta registrada ##{venta_id}")
                )
            except sqlite3.OperationalError:
                cursor.execute(
                    "INSERT INTO movimientos (producto_id, tipo_movimiento, cantidad, fecha, descripcion) VALUES (?, ?, ?, ?, ?)",
                    (prod_id, "Salida", cantidad, fecha_str, f"Venta registrada ##{venta_id}")
                )
            
        # Actualizar total de la venta
        cursor.execute(
            "UPDATE ventas SET total = ? WHERE id = ?",
            (total_venta, venta_id)
        )

    conn.commit()
    conn.close()
    print("\n=======================================================")
    print("✅ ¡Las 8 tablas han sido pobladas con éxito absoluto!")
    print("=======================================================\n")

if __name__ == "__main__":
    poblar_datos()