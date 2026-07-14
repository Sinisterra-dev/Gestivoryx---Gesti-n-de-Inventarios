/**
 * Gestivoryx – Módulo de Productos
 * CRUD completo conectado al backend API.
 */
function safeGetValue(id) {
  const el = document.getElementById(id);
  if (!el) {
    console.error(`Elemento no encontrado: ${id}`);
    return null;
  }
  return el.value;
}

document.addEventListener("DOMContentLoaded", async function () {
  if (!requireAuth()) return;

  // ── Bind logout ────────────────────────────────────────────────────────────
  document.querySelectorAll('[href="login.html"]').forEach((el) => {
    el.addEventListener("click", (e) => { e.preventDefault(); logout(); });
  });

  let productos = [];
  let categorias = [];
  let proveedores = [];
  let editingId = null;

  // ── Load selects ───────────────────────────────────────────────────────────
  async function loadSelects() {
    try {
      [categorias, proveedores] = await Promise.all([
        api.get("/api/categorias/"),
        api.get("/api/proveedores/"),
      ]);
      const catSelect = document.getElementById("productCategory");
      const provSelect = document.getElementById("productProveedor");
      const catEdit = document.getElementById("editProductCategory");
      const provEdit = document.getElementById("editProductProveedor");

      [catSelect, catEdit].forEach((sel) => {
        if (!sel) return;
        sel.innerHTML = '<option value="">Sin categoría</option>';
        categorias.forEach((c) => {
          sel.innerHTML += `<option value="${c.id}">${c.nombre}</option>`;
        });
      });

      [provSelect, provEdit].forEach((sel) => {
        if (!sel) return;
        sel.innerHTML = '<option value="">Sin proveedor</option>';
        proveedores.forEach((p) => {
          sel.innerHTML += `<option value="${p.id}">${p.nombre}</option>`;
        });
      });
    } catch (e) {
      console.warn("Error cargando selects:", e);
    }
  }

  // ── Render table ───────────────────────────────────────────────────────────
  function renderTable(retryCount = 0) {
    const tbody = document.getElementById("tablaProductos");
    if (!tbody) {
      if (retryCount < 50) {
        console.warn(`renderTable: No se encontró tbody #tablaProductos, reintentando en 100ms (intento ${retryCount + 1}/50)`);
        setTimeout(() => renderTable(retryCount + 1), 100);
      } else {
        console.error('renderTable: No se encontró tbody #tablaProductos después de 50 intentos. Verificar que el ID en HTML sea exactamente "tablaProductos" sin espacios ocultos.');
      }
      return;
    }
    console.log('renderTable: Intentando pintar', productos.length, 'productos');
    tbody.innerHTML = "";
    productos.forEach((p) => {
      const stockClass = p.stock <= p.stock_minimo ? "text-danger fw-bold" : "";
      const estadoBadge = p.activo
        ? '<span class="badge badge-success">Activo</span>'
        : '<span class="badge badge-danger">Inactivo</span>';
      tbody.innerHTML += `
        <tr>
          <td>${p.id}</td>
          <td><strong>${p.nombre}</strong></td>
          <td>${p.categoria ? p.categoria.nombre : "-"}</td>
          <td>$${p.precio_venta.toLocaleString("es-CO")}</td>
          <td class="${stockClass}">${p.stock}</td>
          <td>${estadoBadge}</td>
          <td>
            <button class="btn btn-sm btn-warning btn-edit" data-id="${p.id}" title="Editar">
              <i class="fas fa-edit"></i>
            </button>
            <button class="btn btn-sm btn-danger btn-delete" data-id="${p.id}" title="Eliminar">
              <i class="fas fa-trash"></i>
            </button>
          </td>
        </tr>`;
    });
    console.log('renderTable: Tabla actualizada con HTML');
    // Bind action buttons
    document.querySelectorAll(".btn-edit").forEach((btn) => {
      btn.addEventListener("click", () => openEditModal(parseInt(btn.dataset.id)));
    });
    document.querySelectorAll(".btn-delete").forEach((btn) => {
      btn.addEventListener("click", () => deleteProducto(parseInt(btn.dataset.id)));
    });
  }

  // ── Load products ──────────────────────────────────────────────────────────
  async function loadProductos() {
    try {
      productos = await api.get("/api/productos/?solo_activos=false");
      console.log('Datos recibidos desde API (productos):', productos);
      renderTable();
      
      // Update summary cards
      const total = productos.filter((p) => p.activo).length;
      const enStock = productos.filter((p) => p.activo && p.stock > p.stock_minimo).length;
      const bajoStock = productos.filter((p) => p.activo && p.stock > 0 && p.stock <= p.stock_minimo).length;
      const agotados = productos.filter((p) => p.activo && p.stock === 0).length;
      
      const elTotal = document.getElementById("cardTotalProductos");
      const elEnStock = document.getElementById("cardEnStock");
      const elBajoStock = document.getElementById("cardBajoStock");
      const elAgotados = document.getElementById("cardAgotados");
      
      if (elTotal) elTotal.textContent = total;
      if (elEnStock) elEnStock.textContent = enStock;
      if (elBajoStock) elBajoStock.textContent = bajoStock;
      if (elAgotados) elAgotados.textContent = agotados;
    } catch (e) {
      console.error('Error al cargar productos:', e);
      showToast("Error al cargar productos", "error");
    }
  }

  // ── Create / Update product ────────────────────────────────────────────────
  const formAdd = document.getElementById("formAgregarProducto");
  if (formAdd) {
    formAdd.addEventListener("submit", async (e) => {
      e.preventDefault();
      const data = {
        codigo: safeGetValue("productCode")?.trim() || "",
        nombre: safeGetValue("productName")?.trim() || "",
        descripcion: safeGetValue("productDesc")?.trim() || null,
        precio_compra: parseFloat(safeGetValue("productPriceCompra") || 0),
        precio_venta: parseFloat(safeGetValue("productPrice") || 0),
        stock: parseInt(safeGetValue("productStock") || 0),
        stock_minimo: parseInt(safeGetValue("productStockMin") || 5),
        unidad: safeGetValue("productUnidad")?.trim() || null,
        categoria_id: safeGetValue("productCategory") || null,
        proveedor_id: safeGetValue("productProveedor") || null,
      };
      try {
        await api.post("/api/productos/", data);
        showToast("Producto creado exitosamente", "success");
        closeModal("modalAgregarProducto");
        formAdd.reset();
        await loadProductos();
      } catch (err) {
        showToast(err.message, "error");
      }
    });
  }

  const formEdit = document.getElementById("formEditarProducto");
  if (formEdit) {
    formEdit.addEventListener("submit", async (e) => {
      e.preventDefault();
      const data = {
        nombre: safeGetValue("editProductName")?.trim() || "",
        descripcion: safeGetValue("editProductDesc")?.trim() || null,
        precio_compra: parseFloat(safeGetValue("editProductPriceCompra") || 0),
        precio_venta: parseFloat(safeGetValue("editProductPrice") || 0),
        stock: parseInt(safeGetValue("editProductStock") || 0),
        stock_minimo: parseInt(safeGetValue("editProductStockMin") || 5),
        unidad: safeGetValue("editProductUnidad")?.trim() || null,
        categoria_id: safeGetValue("editProductCategory") || null,
        proveedor_id: safeGetValue("editProductProveedor") || null,
      };
      try {
        await api.put(`/api/productos/${editingId}`, data);
        showToast("Producto actualizado", "success");
        closeModal("modalEditarProducto");
        await loadProductos();
      } catch (err) {
        showToast(err.message, "error");
      }
    });
  }

  // ── Open edit modal ────────────────────────────────────────────────────────
  function openEditModal(id) {
    const p = productos.find((x) => x.id === id);
    if (!p) return;
    editingId = id;
    const setVal = (selector, value) => {
      const el = document.getElementById(selector);
      if (el) el.value = value ?? "";
    };
    setVal("editProductName", p.nombre);
    setVal("editProductCode", p.codigo);
    setVal("editProductDesc", p.descripcion);
    setVal("editProductPriceCompra", p.precio_compra);
    setVal("editProductPrice", p.precio_venta);
    setVal("editProductStock", p.stock);
    setVal("editProductStockMin", p.stock_minimo);
    setVal("editProductUnidad", p.unidad);
    setVal("editProductCategory", p.categoria_id);
    setVal("editProductProveedor", p.proveedor_id);
    openModal("modalEditarProducto");
  }

  // ── Delete product ─────────────────────────────────────────────────────────
  async function deleteProducto(id) {
    if (!confirm("¿Desactivar este producto?")) return;
    try {
      await api.delete(`/api/productos/${id}`);
      showToast("Producto desactivado", "warning");
      await loadProductos();
    } catch (err) {
      showToast(err.message, "error");
    }
  }

  // ── Modal helpers ──────────────────────────────────────────────────────────
  function openModal(id) {
    const el = document.getElementById(id);
    if (el) { el.style.display = "block"; el.classList.add("show"); document.body.classList.add("modal-open"); }
  }
  function closeModal(id) {
    const el = document.getElementById(id);
    if (el) { el.style.display = "none"; el.classList.remove("show"); document.body.classList.remove("modal-open"); }
  }

  // Bind close buttons
  document.querySelectorAll("[data-dismiss='modal']").forEach((btn) => {
    btn.addEventListener("click", () => {
      const modal = btn.closest(".modal");
      if (modal) closeModal(modal.id);
    });
  });

  // ── Search ─────────────────────────────────────────────────────────────────
  const searchInput = document.getElementById("searchProducto");
  if (searchInput) {
    searchInput.addEventListener("input", async () => {
      const q = searchInput.value.trim();
      try {
        productos = await api.get(`/api/productos/?solo_activos=false&q=${encodeURIComponent(q)}`);
        renderTable();
      } catch (e) {}
    });
  }

  // ── Init ───────────────────────────────────────────────────────────────────
  await loadSelects();
  await loadProductos();
});
