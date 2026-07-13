# Problemas de Sincronización Frontend-Backend - Gestivoryx
**Fecha:** 11 de julio de 2026
**Objetivo:** Identificar problemas de sincronización entre el backend y el frontend

## Análisis Realizado

Se revisaron todos los archivos JavaScript del frontend para verificar si existe sincronización automática después de operaciones CRUD.

## Hallazgos

### ✅ Código JavaScript CORRECTO

Todos los módulos YA tienen implementada la lógica de sincronización automática:

**categorias.js:**
- Línea 72: `await loadCategorias()` después de crear categoría
- Línea 88: `await loadCategorias()` después de actualizar categoría
- Línea 109: `await loadCategorias()` después de eliminar categoría

**clientes.js:**
- Línea 75: `await loadClientes()` después de crear cliente
- Línea 94: `await loadClientes()` después de actualizar cliente
- Línea 117: `await loadClientes()` después de eliminar cliente

**productos.js:**
- Línea 138: `await loadProductos()` después de crear producto
- Línea 164: `await loadProductos()` después de actualizar producto
- Línea 199: `await loadProductos()` después de eliminar producto

**proveedores.js:**
- Línea 75: `await loadProveedores()` después de crear proveedor
- Línea 94: `await loadProveedores()` después de actualizar proveedor
- Línea 117: `await loadProveedores()` después de eliminar proveedor

**usuarios.js:**
- Línea 82: `await loadUsuarios()` después de crear usuario
- Línea 92: `await loadUsuarios()` después de eliminar usuario

**ventas.js:**
- Línea 183: `await loadData()` después de crear venta
- Línea 216: `await loadData()` después de anular venta

**ajustes.js:**
- Línea 68: `await loadData()` después de registrar ajuste

## ❌ PROBLEMA REAL ENCONTRADO: Selectores DOM Incorrectos

### Descripción del Problema

El problema de sincronización NO estaba en la lógica de sincronización, sino en los selectores DOM de las funciones `renderTable()`.

**Causa raíz:** Los selectores CSS en JavaScript usaban `querySelector("#tabla tbody")` pero en el HTML los IDs están directamente en los elementos `<tbody>`, no en los elementos `<table>`.

### Ejemplo del Problema

**HTML (categorias.html):**
```html
<tbody id="tablaCategorias" class="divide-y divide-gray-50">
```

**JavaScript (categorias.js) - ANTES:**
```javascript
const tbody = document.querySelector("#tablaCategorias tbody"); // ❌ INCORRECTO
```

**JavaScript (categorias.js) - DESPUÉS:**
```javascript
const tbody = document.getElementById("tablaCategorias"); // ✅ CORRECTO
```

### Módulos Afectados

Todos los módulos tenían el mismo problema:
- categorias.js: `#tablaCategorias tbody` → `tablaCategorias`
- clientes.js: `#tablaClientes tbody` → `tablaClientes`
- productos.js: `#tablaProductos tbody` → `tablaProductos`
- proveedores.js: `#tablaProveedores tbody` → `tablaProveedores`
- ventas.js: `#tablaVentas tbody` → `tablaVentas`, `#tablaCarrito tbody` → `tablaCarrito`

## Solución Implementada

### 1. Corrección de Selectores

Se cambiaron todos los selectores de `querySelector("#tabla tbody")` a `getElementById("tabla")` para que coincidan con la estructura real del HTML.

### 2. Observador de Elementos con setTimeout

Se implementó un mecanismo de reintentos en todas las funciones `renderTable()` para manejar casos donde el DOM no esté completamente cargado:

```javascript
function renderTable(retryCount = 0) {
  const tbody = document.getElementById("tablaCategorias");
  if (!tbody) {
    if (retryCount < 50) {
      console.warn(`renderTable: No se encontró tbody #tablaCategorias, reintentando en 100ms (intento ${retryCount + 1}/50)`);
      setTimeout(() => renderTable(retryCount + 1), 100);
    } else {
      console.error('renderTable: No se encontró tbody #tablaCategorias después de 50 intentos. Verificar que el ID en HTML sea exactamente "tablaCategorias" sin espacios ocultos.');
    }
    return;
  }
  // ... resto del código
}
```

**Características:**
- Reintenta hasta 50 veces (5 segundos máximo)
- Espera 100ms entre cada intento
- Muestra advertencias durante los reintentos
- Muestra error descriptivo después de 50 intentos fallidos
- Previene errores de referencia de DOM

### 3. Logging de Diagnóstico

Se añadieron `console.log` en las funciones `load*()` y `renderTable()` para facilitar el debugging:

```javascript
async function loadCategorias() {
  try {
    categorias = await api.get("/api/categorias/?solo_activas=false");
    console.log('Datos recibidos desde API (categorias):', categorias);
    renderTable();
  } catch (e) {
    console.error('Error al cargar categorías:', e);
    showToast("Error al cargar categorías", "error");
  }
}
```

## Archivos Modificados

1. **categorias.js** - Corregido selector y añadido observador
2. **clientes.js** - Corregido selector y añadido observador
3. **productos.js** - Corregido selector y añadido observador
4. **proveedores.js** - Corregido selector y añadido observador
5. **ventas.js** - Corregidos selectores (tablaVentas, tablaCarrito) y añadido observador

## Estado

**✅ PROBLEMA RESUELTO**

El problema de sincronización estaba causado por selectores DOM incorrectos. Se han corregido todos los selectores y se ha implementado un mecanismo de reintentos para manejar casos de carga asíncrona del DOM.

## Recomendaciones para Debugging

1. **Abrir la consola del navegador** (F12) para ver los logs de diagnóstico
2. **Verificar que el backend esté corriendo** en la URL correcta
3. **Verificar el token JWT** en localStorage
4. **Si los reintentos continúan**, verificar que no haya espacios ocultos en los IDs del HTML
