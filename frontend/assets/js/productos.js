/**
 * Gestivoryx – Módulo de Productos
 * CRUD completo conectado al backend API.
 */

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
  function renderTable() {
    const tbody = document.querySelector("#tablaProductos tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    productos.forEach((p) => {
      const stockClass = p.stock <= p.stock_minimo ? "text-danger fw-bold" : "";
      const estadoBadge = p.activo
        ? '<span class="badge badge-success">Activo</span>'
        : '<span class="badge badge-danger">Inactivo</span>';
      tbody.innerHTML += `
        <tr>
          <td>${p.id}</td>
          <td><i class="fas fa-box text-muted"></i></td>
          <td><strong>${p.nombre}</strong><br><small class="text-muted">${p.codigo}</small></td>
          <td>${p.categoria ? p.categoria.nombre : "-"}</td>
          <td>$${p.precio_venta.toLocaleString("es-CO")}</td>
          <td class="${stockClass}">${p.stock} ${p.unidad || "uds"}</td>
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
      renderTable();
      // Update stats boxes
      const activos = productos.filter((p) => p.activo).length;
      const bajoStock = productos.filter((p) => p.activo && p.stock <= p.stock_minimo).length;
      const agotados = productos.filter((p) => p.activo && p.stock === 0).length;
      const boxes = document.querySelectorAll(".small-box h3");
      if (boxes[0]) boxes[0].textContent = activos;
      if (boxes[1]) boxes[1].textContent = bajoStock;
      if (boxes[2]) boxes[2].textContent = agotados;
    } catch (e) {
      showToast("Error al cargar productos", "error");
    }
  }

  // ── Create / Update product ────────────────────────────────────────────────
  const formAdd = document.getElementById("formAgregarProducto");
  if (formAdd) {
    formAdd.addEventListener("submit", async (e) => {
      e.preventDefault();
      const data = {
        codigo: document.getElementById("productCode").value.trim(),
        nombre: document.getElementById("productName").value.trim(),
        descripcion: document.getElementById("productDesc")?.value.trim() || null,
        precio_compra: parseFloat(document.getElementById("productPriceCompra")?.value || 0),
        precio_venta: parseFloat(document.getElementById("productPrice").value),
        stock: parseInt(document.getElementById("productStock").value),
        stock_minimo: parseInt(document.getElementById("productStockMin")?.value || 5),
        unidad: document.getElementById("productUnidad")?.value.trim() || null,
        categoria_id: document.getElementById("productCategory")?.value || null,
        proveedor_id: document.getElementById("productProveedor")?.value || null,
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
        nombre: document.getElementById("editProductName").value.trim(),
        descripcion: document.getElementById("editProductDesc")?.value.trim() || null,
        precio_compra: parseFloat(document.getElementById("editProductPriceCompra")?.value || 0),
        precio_venta: parseFloat(document.getElementById("editProductPrice").value),
        stock: parseInt(document.getElementById("editProductStock").value),
        stock_minimo: parseInt(document.getElementById("editProductStockMin")?.value || 5),
        unidad: document.getElementById("editProductUnidad")?.value.trim() || null,
        categoria_id: document.getElementById("editProductCategory")?.value || null,
        proveedor_id: document.getElementById("editProductProveedor")?.value || null,
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
