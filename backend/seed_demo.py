import sqlite3
import random
from datetime import datetime, timedelta

# Intentamos importar Passlib para generar el hash idéntico al del backend
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except ImportError:
    pwd_context = None

# ==============================================================================
# CONFIGURACIÓN GENERAL DEL MOTOR DE DATOS SIMULADOS
# ==============================================================================
DB_NAME = "gestivoryx.db"

def conectar_db():
    """Establece una conexión directa con la base de datos SQLite."""
    return sqlite3.connect(DB_NAME)

def poblar_datos():
    """
    Función principal encargada de limpiar el esquema actual y repoblar las 
    8 tablas del sistema con registros comerciales realistas en pesos colombianos (COP),
    con estricto control de integridad referencial y prevención de stock negativo.
    """
    conn = conectar_db()
    # Desactivamos llaves foráneas temporalmente para evitar fallos de restricción al vaciar
    conn.execute("PRAGMA foreign_keys = OFF;")
    cursor = conn.cursor()
    
    print("⏳ Limpiando las tablas del sistema para prevenir duplicación de registros...")
    
    # Listado exhaustivo que contempla variaciones de nombres en plural y singular
    tablas_limpieza = [
        "detalles_venta", 
        "detalle_ventas", 
        "movimientos", 
        "ventas", 
        "productos", 
        "clientes", 
        "proveedores", 
        "categorias", 
        "usuarios"
    ]
    
    for tabla in tablas_limpieza:
        try:
            cursor.execute(f"DELETE FROM {tabla}")
        except sqlite3.OperationalError:
            # Si la tabla no existe con ese nombre exacto, continúa sin romper el script
            pass
            
    conn.commit()
    
    # Captura de marca de tiempo unificada para auditoría interna
    ahora_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ==============================================================================
    # ⚡ MOTOR DE INSERCIÓN DINÁMICA CON AUDITORÍA E INTEGRIDAD TOTAL (V8)
    # ==============================================================================
    def insertar_dinamico(nombre_tabla, datos_origen):
        """
        Inspecciona el esquema real de la tabla en ejecución para mapear, calcular
        y blindar de forma automática cualquier restricción NOT NULL o campo faltante.
        """
        try:
            cursor.execute(f"PRAGMA table_info({nombre_tabla});")
            columnas_reales = [row[1] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            return None # Si la tabla no existe en el esquema actual, se omite de forma segura
            
        if not columnas_reales:
            return None
            
        datos_finales = {}
        
        # 1. Filtrado de campos: Solo conserva llaves existentes en la base de datos
        for llave, valor in datos_origen.items():
            if llave in columnas_reales:
                datos_finales[llave] = valor
                
        # 2. Inyección automática de Timestamps y Auditoría
        for campo_tiempo in ['creado_en', 'created_at', 'actualizado_en', 'updated_at']:
            if campo_tiempo in columnas_reales and campo_tiempo not in datos_finales:
                datos_finales[campo_tiempo] = ahora_str
                
        if 'activo' in columnas_reales and 'activo' not in datos_finales:
            datos_finales['activo'] = 1
            
        if 'status' in columnas_reales and 'status' not in datos_finales:
            datos_finales['status'] = "completada"

        # 3. Generación y Blindaje de Códigos Operacionales Obligatorios
        if 'codigo' in columnas_reales and 'codigo' not in datos_finales:
            datos_finales['codigo'] = f"COD-{random.randint(10000, 99999)}"
        if 'sku' in columnas_reales and 'sku' not in datos_finales:
            datos_finales['sku'] = f"SKU-{random.randint(10000, 99999)}"
        if 'referencia' in columnas_reales and 'referencia' not in datos_finales:
            datos_finales['referencia'] = f"REF-{random.randint(10000, 99999)}"
        if 'numero_factura' in columnas_reales and 'numero_factura' not in datos_finales:
            datos_finales['numero_factura'] = f"FAC-{random.randint(1000, 9999)}"
        if 'numero' in columnas_reales and 'numero' not in datos_finales:
            datos_finales['numero'] = f"VTA-{random.randint(10000, 99999)}"
        if 'num_venta' in columnas_reales and 'num_venta' not in datos_finales:
            datos_finales['num_venta'] = f"VTA-{random.randint(10000, 99999)}"
        if 'comprobante' in columnas_reales and 'comprobante' not in datos_finales:
            datos_finales['comprobante'] = f"CMP-{random.randint(10000, 99999)}"

        # 4. Blindaje y Precálculo Crítico de Campos Financieros (NOT NULL Constraints)
        if 'cantidad' in columnas_reales and 'cantidad' not in datos_finales:
            datos_finales['cantidad'] = 1
            
        if 'precio_unitario' in columnas_reales and 'precio_unitario' not in datos_finales:
            datos_finales['precio_unitario'] = datos_finales.get('precio', 0)
        if 'precio' in columnas_reales and 'precio' not in datos_finales:
            datos_finales['precio'] = datos_finales.get('precio_unitario', 0)

        # 🛑 CAPA DE RESPALDO INTERNA PARA EL SUBTOTAL
        if 'subtotal' in columnas_reales and 'subtotal' not in datos_finales:
            cant = datos_finales.get('cantidad', datos_origen.get('cantidad', 1))
            prec = datos_finales.get('precio_unitario', datos_finales.get('precio', datos_origen.get('precio_unitario', 0)))
            datos_finales['subtotal'] = cant * prec

        if 'descuento' in columnas_reales and 'descuento' not in datos_finales:
            datos_finales['descuento'] = 0.0
        if 'impuesto' in columnas_reales and 'impuesto' not in datos_finales:
            datos_finales['impuesto'] = 0.0
        if 'iva' in columnas_reales and 'iva' not in datos_finales:
            datos_finales['iva'] = 0.0
            
        if 'total' in columnas_reales and 'total' not in datos_finales:
            datos_finales['total'] = datos_finales.get('subtotal', 0.0)

        if 'metodo_pago' in columnas_reales and 'metodo_pago' not in datos_finales:
            datos_finales['metodo_pago'] = "Efectivo"
        if 'estado' in columnas_reales and 'estado' not in datos_finales:
            datos_finales['estado'] = "completada"

        # 5. Blindaje de Parámetros de Stock y Almacenamiento
        if 'stock_minimo' in columnas_reales and 'stock_minimo' not in datos_finales:
            datos_finales['stock_minimo'] = 3
        if 'stock_maximo' in columnas_reales and 'stock_maximo' not in datos_finales:
            datos_finales['stock_maximo'] = 150
        if 'stock_anterior' in columnas_reales and 'stock_anterior' not in datos_finales:
            datos_finales['stock_anterior'] = 0
        if 'stock_nuevo' in columnas_reales and 'stock_nuevo' not in datos_finales:
            datos_finales['stock_nuevo'] = datos_finales.get('cantidad', 0)
        if 'stock_final' in columnas_reales and 'stock_final' not in datos_finales:
            datos_finales['stock_final'] = datos_finales.get('cantidad', 0)
        if 'stock_posterior' in columnas_reales and 'stock_posterior' not in datos_finales:
            datos_finales['stock_posterior'] = datos_finales.get('cantidad', 0)

        # 6. Fallbacks de Texto Obligatorio
        if 'descripcion' in columnas_reales and 'descripcion' not in datos_finales:
            nombre_item = datos_origen.get('nombre', datos_origen.get('username', 'Registro Automático'))
            datos_finales['descripcion'] = f"Descripción del sistema para {nombre_item}"
        if 'direccion' in columnas_reales and 'direccion' not in datos_finales:
            datos_finales['direccion'] = "Zona Industrial Central"

        # 7. Relación Forzada de Auditoría de Usuario (Admin)
        if 'usuario_id' in columnas_reales and 'usuario_id' not in datos_finales:
            cursor.execute("SELECT id FROM usuarios LIMIT 1")
            u_row = cursor.fetchone()
            if u_row: datos_finales['usuario_id'] = u_row[0]
        if 'user_id' in columnas_reales and 'user_id' not in datos_finales:
            cursor.execute("SELECT id FROM usuarios LIMIT 1")
            u_row = cursor.fetchone()
            if u_row: datos_finales['user_id'] = u_row[0]

        # Ejecución y Retorno del Identificador Único Generado
        if datos_finales:
            keys = datos_finales.keys()
            placeholders = ', '.join(['?'] * len(keys))
            sql = f"INSERT INTO {nombre_tabla} ({', '.join(keys)}) VALUES ({placeholders})"
            cursor.execute(sql, list(datos_finales.values()))
            return cursor.lastrowid
        return None

    # ==============================================================================
    # PASO 1: INSERCIÓN DEL USUARIO ADMINISTRADOR DE CONTROL
    # ==============================================================================
    print("👤 Generando e insertando hash dinámico nativo de Passlib...")
    
    contrasena_plana = "123456"
    
    # Si detecta passlib en el entorno, cifra de forma nativa. Si no, usa el fallback estándar.
    if pwd_context:
        hash_seguro = pwd_context.hash(contrasena_plana)
        print("🔒 Hash generado exitosamente usando la configuración nativa de tu entorno.")
    else:
        hash_seguro = "$2b$12$R9h/cIPz0gi.UR36hoKZaOaV6g9l3G9p66j5bT/p3UwgM18n9Jny2"
        print("⚠️ Advertencia: Passlib no detectado en este entorno de ejecución. Usando fallback.")

    insertar_dinamico("usuarios", {
        "username": "alex",  # En minúsculas para cumplir con estándares comunes de login
        "nombre": "Alex Sinisterra",
        "rol": "Administrador",
        "password": hash_seguro,
        "contrasena": hash_seguro,
        "hashed_password": hash_seguro,
        "email": "alex@correo.com"
    })
    
    # ==============================================================================
    # PASO 2: ESTRUCTURACIÓN DE CATEGORÍAS COMERCIALES
    # ==============================================================================
    print("🗂️ Insertando categorías base...")
    for cat in ["Accesorios", "Electrónica", "Almacenamiento", "Oficina"]:
        insertar_dinamico("categorias", {"nombre": cat})

    # ==============================================================================
    # PASO 3: REGISTRO DE PROVEEDORES LOGÍSTICOS
    # ==============================================================================
    print("📦 Insertando directorio de proveedores...")
    proveedores_datos = [
        {"nombre": "Tech Distribution S.A.S.", "contacto": "Carlos Mendoza", "telefono": "3157894512"},
        {"nombre": "Logística y Suministros Global", "contacto": "Ana María Silva", "telefono": "3104561234"},
        {"nombre": "Importaciones del Pacífico", "contacto": "Jorge Eliecer", "telefono": "3189876543"},
        {"nombre": "Mayorista de Oficina Express", "contacto": "Elena Gómez", "telefono": "3001234567"}
    ]
    proveedor_ids = []
    for prov in proveedores_datos:
        pid = insertar_dinamico("proveedores", prov)
        if pid:
            proveedor_ids.append(pid)
            
    if not proveedor_ids:
        cursor.execute("SELECT id FROM proveedores")
        proveedor_ids = [row[0] for row in cursor.fetchall()]

    # ==============================================================================
    # PASO 4: CATÁLOGO DE PRODUCTOS EN PESOS COLOMBIANOS (COP) Y ENTRADAS INICIALES
    # ==============================================================================
    print("💻 Insertando catálogo de productos optimizado en COP y registros de entradas...")
    productos_config = [
        ("Mouse Ergonómico Inalámbrico", "Accesorios", 45, 45000, 95000),
        ("Teclado Mecánico RGB", "Accesorios", 20, 120000, 250000),
        ("Monitor 24 Pulgadas FHD", "Electrónica", 15, 450000, 690000),
        ("Disco Duro Externo 1TB", "Almacenamiento", 30, 150000, 280000),
        ("Memoria USB 64GB Tipo C", "Almacenamiento", 100, 20000, 45000),
        ("Silla de Oficina Ergonómica", "Oficina", 12, 300000, 550000),
        ("Hub USB-C 7 en 1", "Accesorios", 25, 60000, 120000),
        ("Cargador Carga Rápida 65W", "Electrónica", 50, 40000, 85000),
        ("Audífonos Noise Cancelling", "Electrónica", 18, 250000, 490000),
        ("Escritorio Elevable Manual", "Oficina", 8, 400000, 790000)
    ]
    
    fecha_apertura_inventario = (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d %H:%M:%S")
    
    for prod in productos_config:
        p_prov = random.choice(proveedor_ids) if proveedor_ids else 1
        prod_id = insertar_dinamico("productos", {
            "nombre": prod[0],
            "categoria": prod[1],
            "stock": prod[2],
            "precio_compra": prod[3],
            "precio_venta": prod[4],
            "proveedor_id": p_prov
        })
        
        if not prod_id:
            cursor.execute("SELECT id FROM productos WHERE nombre = ?", (prod[0],))
            prod_id = cursor.fetchone()[0]
            
        insertar_dinamico("movimientos", {
            "producto_id": prod_id,
            "tipo": "Entrada",
            "tipo_movimiento": "Entrada",
            "cantidad": prod[2],
            "stock_anterior": 0,
            "stock_nuevo": prod[2],
            "stock_final": prod[2],
            "stock_posterior": prod[2],
            "fecha": fecha_apertura_inventario,
            "motivo": "Carga inicial de inventario",
            "descripcion": "Carga inicial de inventario",
            "concepto": "Carga inicial de inventario"
        })

    # ==============================================================================
    # PASO 5: REGISTRO DE BASE DE CLIENTES ASOCIADOS
    # ==============================================================================
    print("👥 Insertando clientes de prueba del sistema...")
    clientes_datos = [
        {"nombre": "Alejandro Sinisterra", "email": "alex@correo.com", "telefono": "3120001122"},
        {"nombre": "Claudia Restrepo", "email": "claudia.r@outlook.com", "telefono": "3165554433"},
        {"nombre": "Sistemas Luro Legal", "email": "contacto@lurolegal.com", "telefono": "3017778899"},
        {"nombre": "Estudio Digital Pixel", "email": "info@pixel.co", "telefono": "3114445566"},
        {"nombre": "Andrés Caicedo", "email": "andres99@gmail.com", "telefono": "3153332211"}
    ]
    cliente_ids = []
    for cl in clientes_datos:
        cid = insertar_dinamico("clientes", cl)
        if cid:
            cliente_ids.append(cid)
            
    if not cliente_ids:
        cursor.execute("SELECT id FROM clientes")
        cliente_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT id, precio_venta FROM productos")
    productos_db = cursor.fetchall()

    # ==============================================================================
    # PASO 6: SIMULACIÓN DE HISTORIAL DE VENTAS TRANSACCIONALES COMPLETADAS
    # ==============================================================================
    print("📈 Generando historial transaccional dinámico en COP (Mapeo estricto)...")
    hoy = datetime.now()
    rango_ventas = random.randint(25, 35)
    
    for _ in range(rango_ventas):
        cliente_elegido = random.choice(cliente_ids) if cliente_ids else 1
        dias_desplazamiento = random.randint(1, 30)
        hora_desplazamiento = random.randint(8, 18)
        
        fecha_transaccion = (hoy - timedelta(days=dias_desplazamiento)).replace(
            hour=hora_desplazamiento, 
            minute=random.randint(0, 59)
        )
        fecha_transaccion_str = fecha_transaccion.strftime("%Y-%m-%d %H:%M:%S")
        
        articulos_en_venta = random.randint(1, 3)
        productos_simulados = random.sample(productos_db, min(articulos_en_venta, len(productos_db)))
        
        monto_acumulado_venta = 0
        detalles_preparados = []
        
        for p_id, p_venta in productos_simulados:
            cursor.execute("SELECT stock FROM productos WHERE id = ?", (p_id,))
            stock_en_bodega = cursor.fetchone()[0]
            
            # 🛑 CONTROL ABSOLUTO CONTRA STOCK NEGATIVO
            if stock_en_bodega <= 2:
                continue
                
            cantidad_solicitada = random.randint(1, min(2, stock_en_bodega))
            subtotal_calculado = cantidad_solicitada * p_venta
            monto_acumulado_venta += subtotal_calculado
            
            detalles_preparados.append((p_id, cantidad_solicitada, p_venta, subtotal_calculado, stock_en_bodega))
            
        if not detalles_preparados:
            continue
            
        # Creación de la venta principal con montos y estados unificados
        venta_id = insertar_dinamico("ventas", {
            "cliente_id": cliente_elegido,
            "fecha": fecha_transaccion_str,
            "fecha_venta": fecha_transaccion_str,
            "subtotal": monto_acumulado_venta,
            "descuento": 0.0,
            "impuesto": 0.0,
            "iva": 0.0,
            "total": monto_acumulado_venta,
            "estado": "completada",
            "status": "completada"
        })
        
        if not venta_id:
            cursor.execute("SELECT max(id) FROM ventas")
            venta_id = cursor.fetchone()[0]
            
        # Inserción explícita de registros hijos con clave 'subtotal' mandatoria
        for prod_id, cant, p_unitario, sub_item, stock_previo in detalles_preparados:
            
            payload_detalle = {
                "venta_id": venta_id,
                "producto_id": prod_id,
                "cantidad": cant,
                "precio_unitario": p_unitario,
                "precio": p_unitario,
                "subtotal": sub_item,
                "total": sub_item
            }
            
            insertar_dinamico("detalles_venta", payload_detalle)
            insertar_dinamico("detalle_ventas", payload_detalle)
            
            insertar_dinamico("movimientos", {
                "producto_id": prod_id,
                "tipo": "Salida",
                "tipo_movimiento": "Salida",
                "cantidad": cant,
                "stock_anterior": stock_previo,
                "stock_nuevo": stock_previo - cant,
                "stock_final": stock_previo - cant,
                "stock_posterior": stock_previo - cant,
                "fecha": fecha_transaccion_str,
                "motivo": f"Venta registrada #{venta_id}"
            })
            
            cursor.execute(
                "UPDATE productos SET stock = stock - ? WHERE id = ?",
                (cant, prod_id)
            )
            
        try:
            cursor.execute(
                "UPDATE ventas SET total = ?, subtotal = ? WHERE id = ?",
                (monto_acumulado_venta, monto_acumulado_venta, venta_id)
            )
        except sqlite3.OperationalError:
            try:
                cursor.execute("UPDATE ventas SET total = ? WHERE id = ?", (monto_acumulado_venta, venta_id))
            except sqlite3.OperationalError:
                pass

    conn.commit()
    conn.close()
    
    print("\n=======================================================")
    print("✅ ¡Ecosistema poblado con ÉXITO ABSOLUTO en COP y 'completada'!")
    print("=======================================================\n")

if __name__ == "__main__":
    poblar_datos()