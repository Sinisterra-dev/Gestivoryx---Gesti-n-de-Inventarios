# Auditoría de Consistencia de IDs - Gestivoryx Frontend
**Fecha:** 11 de julio de 2026
**Objetivo:** Identificar inconsistencias entre IDs HTML y selectores JavaScript

## Resumen de Inconsistencias Encontradas

### 1. Módulo Categorías (categorias.js vs categorias.html)

**Formulario Agregar:**
- ❌ JS busca: `catNombre`, `catDesc`
- ✅ HTML tiene: `categoryName`, `categoryDesc`

**Formulario Editar:**
- ❌ JS busca: `editCatNombre`, `editCatDesc`
- ✅ HTML tiene: `editCategoryName`, `editCategoryDesc`

**Estado:** CRÍTICO - Los IDs no coinciden en absoluto

---

### 2. Módulo Clientes (clientes.js vs clientes.html)

**Formulario Agregar:**
- ❌ JS busca: `cliNombre`, `cliDocumento`, `cliTelefono`, `cliEmail`, `cliDireccion`
- ⚠️ HTML: Necesita verificación completa (modalAgregarCliente)

**Formulario Editar:**
- ❌ JS busca: `editCliNombre`, `editCliDocumento`, `editCliTelefono`, `editCliEmail`, `editCliDireccion`
- ⚠️ HTML: Necesita verificación completa (modalEditarCliente)

**Estado:** PROBABLE INCONSISTENCIA - Patrón diferente de nombres

---

### 3. Módulo Productos (productos.js vs lista_productos.html)

**Formulario Agregar:**
- ✅ HTML tiene: `productCode`, `productName`, `productPriceCompra`, `productPrice`, `productStock`, `productStockMin`, `productUnidad`, `productCategory`
- ❌ JS también busca: `productDesc`, `productProveedor` (no verificados en HTML)

**Formulario Editar:**
- ❌ JS busca: `editProductName`, `editProductCode`, `editProductDesc`, `editProductPriceCompra`, `editProductPrice`, `editProductStock`, `editProductStockMin`, `editProductUnidad`, `editProductCategory`, `editProductProveedor`
- ⚠️ HTML: Modal editar no visible en lectura parcial

**Estado:** PARCIALMENTE VERIFICADO - Probables inconsistencias en modal editar

---

### 4. Módulo Proveedores (proveedores.js vs proveedores.html)

**Formulario Agregar:**
- ✅ HTML tiene: `provNombre`, `provContacto`, `provTelefono`, `provEmail`, `provDireccion`
- ✅ JS busca: mismos IDs

**Formulario Editar:**
- ❌ JS busca: `editProvNombre`, `editProvContacto`, `editProvTelefono`, `editProvEmail`, `editProvDireccion`
- ⚠️ HTML: Modal editar no visible en lectura parcial

**Estado:** AGREGAR OK - EDITAR SIN VERIFICAR

---

### 5. Módulo Usuarios (usuarios.js vs usuarios.html)

**Formulario Agregar:**
- ❌ JS busca: `usrUsername`, `usrNombre`, `usrEmail`, `usrPassword`, `usrRol`
- ✅ HTML tiene: `userUsername`, `userNombre`, `userEmail`, `userPassword`, `userRol`

**Estado:** INCONSISTENCIA - `usr` vs `user` como prefijo

---

### 6. Módulo Ventas (ventas.js vs ventas.html)

**Formulario Nueva Venta:**
- ❌ JS busca: `ventaProducto`, `ventaTotal`, `btnAgregarCarrito`, `tablaCarrito`, `ventaDetalle`
- ✅ HTML tiene: `selectProductoVenta`, `totalVenta`, `carritoBody` (botón agregar es onclick inline)

**Estado:** INCONSISTENCIA - Nombres completamente diferentes

---

## Convención de Nombres Propuesta

### Estándar Sugerido:
- **Campos de formulario:** `[modulo][Campo]` (camelCase)
- **Campos de edición:** `edit[Modulo][Campo]` (camelCase)
- **Selectores:** `[modulo][Campo]` (camelCase)

### Ejemplos:
- `categoryName` → `catNombre`
- `editCategoryName` → `editCatNombre`
- `userUsername` → `usrUsername`
- `selectProductoVenta` → `ventaProducto`

## Correcciones Necesarias (Prioridad Alta)

1. **categorias.html:** Cambiar `categoryName` → `catNombre`, `categoryDesc` → `catDesc`, `editCategoryName` → `editCatNombre`, `editCategoryDesc` → `editCatDesc`
2. **usuarios.html:** Cambiar `userUsername` → `usrUsername`, `userNombre` → `usrNombre`, `userEmail` → `usrEmail`, `userPassword` → `usrPassword`
3. **ventas.html:** Cambiar `selectProductoVenta` → `ventaProducto`, `totalVenta` → `ventaTotal`, `carritoBody` → `tablaCarrito`
4. **Verificar modales editar** en productos, clientes y proveedores

## Bloque de Validación Sugerido

```javascript
function safeGetValue(id) {
  const el = document.getElementById(id);
  if (!el) {
    console.error(`Elemento no encontrado: ${id}`);
    return null;
  }
  return el.value;
}

// Uso:
const nombre = safeGetValue('catNombre') || '';
```

## Próximos Pasos

1. Aplicar correcciones de IDs en archivos HTML
2. Añadir validación de seguridad en todos los archivos JavaScript
3. Verificar modales de edición no leídos completamente
4. Probar cada módulo después de las correcciones
