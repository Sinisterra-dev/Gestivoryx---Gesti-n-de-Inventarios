/**
 * Gestivoryx – Módulo de Ventas
 * Permite crear ventas con múltiples productos y detalle de líneas.
 */
document.addEventListener("DOMContentLoaded", async function () {
  if (!requireAuth()) return;
  document.querySelectorAll('[href="login.html"]').forEach((el) => {
    el.addEventListener("click", (e) => { e.preventDefault(); logout(); });
  });

  let ventas = [];
  let productos = [];
  let clientes = [];
  let cartItems = [];

  // ── Load initial data ──────────────────────────────────────────────────────
  async function loadData() {
    try {
      [ventas, productos, clientes] = await Promise.all([
        api.get("/api/ventas/"),
        api.get("/api/productos/"),
        api.get("/api/clientes/"),
      ]);
      renderVentasTable();
      populateSelects();
    } catch (e) {
      showToast("Error cargando datos", "error");
    }
  }

  function populateSelects() {
    const clienteSelect = document.getElementById("ventaCliente");
    if (clienteSelect) {
      clienteSelect.innerHTML = '<option value="">Consumidor final</option>';
      clientes.forEach((c) => {
        clienteSelect.innerHTML += `<option value="${c.id}">${c.nombre}</option>`;
      });
    }

    const prodSelect = document.getElementById("ventaProducto");
    if (prodSelect) {
      prodSelect.innerHTML = '<option value="">Seleccionar producto...</option>';
      productos.forEach((p) => {
        prodSelect.innerHTML += `<option value="${p.id}" data-precio="${p.precio_venta}" data-stock="${p.stock}">${p.nombre} (Stock: ${p.stock}) - $${p.precio_venta.toLocaleString("es-CO")}</option>`;
      });
    }
  }

  // ── Ventas table ───────────────────────────────────────────────────────────
  function renderVentasTable() {
    const tbody = document.querySelector("#tablaVentas tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    ventas.forEach((v) => {
      const badge = v.estado === "completada"
        ? '<span class="badge badge-success">Completada</span>'
        : '<span class="badge badge-danger">Anulada</span>';
      tbody.innerHTML += `<tr>
        <td>${v.numero}</td>
        <td>${v.cliente ? v.cliente.nombre : "Consumidor final"}</td>
        <td>${v.detalles.length} producto(s)</td>
        <td>$${v.total.toLocaleString("es-CO")}</td>
        <td>${badge}</td>
        <td>${formatDate(v.creado_en)}</td>
        <td>
          <button class="btn btn-sm btn-info btn-view" data-id="${v.id}" title="Ver"><i class="fas fa-eye"></i></button>
          ${v.estado === "completada" ? `<button class="btn btn-sm btn-danger btn-anular" data-id="${v.id}" title="Anular"><i class="fas fa-times"></i></button>` : ""}
        </td>
      </tr>`;
    });

    document.querySelectorAll(".btn-view").forEach((btn) => {
      btn.addEventListener("click", () => viewVenta(parseInt(btn.dataset.id)));
    });
    document.querySelectorAll(".btn-anular").forEach((btn) => {
      btn.addEventListener("click", () => anularVenta(parseInt(btn.dataset.id)));
    });
  }

  // ── Cart management ────────────────────────────────────────────────────────
  function renderCart() {
    const tbody = document.querySelector("#tablaCarrito tbody");
    const totalEl = document.getElementById("ventaTotal");
    if (!tbody) return;
    tbody.innerHTML = "";
    let total = 0;
    cartItems.forEach((item, idx) => {
      const subtotal = item.precio * item.cantidad;
      total += subtotal;
      tbody.innerHTML += `<tr>
        <td>${item.nombre}</td>
        <td>$${item.precio.toLocaleString("es-CO")}</td>
        <td>
          <input type="number" class="form-control form-control-sm cart-qty" data-idx="${idx}"
            value="${item.cantidad}" min="1" max="${item.stock}" style="width:70px">
        </td>
        <td>$${subtotal.toLocaleString("es-CO")}</td>
        <td><button class="btn btn-sm btn-danger cart-remove" data-idx="${idx}"><i class="fas fa-trash"></i></button></td>
      </tr>`;
    });

    if (totalEl) {
      const descuento = parseFloat(document.getElementById("ventaDescuento")?.value || 0);
      totalEl.textContent = "$" + Math.max(0, total - descuento).toLocaleString("es-CO");
    }

    document.querySelectorAll(".cart-qty").forEach((input) => {
      input.addEventListener("change", () => {
        const idx = parseInt(input.dataset.idx);
        cartItems[idx].cantidad = parseInt(input.value) || 1;
        renderCart();
      });
    });
    document.querySelectorAll(".cart-remove").forEach((btn) => {
      btn.addEventListener("click", () => {
        cartItems.splice(parseInt(btn.dataset.idx), 1);
        renderCart();
      });
    });
  }

  const btnAddToCart = document.getElementById("btnAgregarCarrito");
  if (btnAddToCart) {
    btnAddToCart.addEventListener("click", () => {
      const sel = document.getElementById("ventaProducto");
      const opt = sel?.options[sel.selectedIndex];
      if (!opt || !opt.value) { showToast("Selecciona un producto", "warning"); return; }
      const id = parseInt(opt.value);
      const existing = cartItems.find((x) => x.producto_id === id);
      if (existing) {
        existing.cantidad += 1;
      } else {
        cartItems.push({
          producto_id: id,
          nombre: opt.text.split(" (Stock")[0],
          precio: parseFloat(opt.dataset.precio),
          stock: parseInt(opt.dataset.stock),
          cantidad: 1,
        });
      }
      renderCart();
      sel.value = "";
    });
  }

  const descInput = document.getElementById("ventaDescuento");
  if (descInput) descInput.addEventListener("input", renderCart);

  // ── Create sale ────────────────────────────────────────────────────────────
  const formVenta = document.getElementById("formNuevaVenta");
  if (formVenta) {
    formVenta.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!cartItems.length) { showToast("El carrito está vacío", "warning"); return; }
      const descuento = parseFloat(document.getElementById("ventaDescuento")?.value || 0);
      const cliente_id = document.getElementById("ventaCliente")?.value || null;
      const notas = document.getElementById("ventaNotas")?.value || null;
      try {
        await api.post("/api/ventas/", {
          cliente_id: cliente_id ? parseInt(cliente_id) : null,
          descuento,
          notas,
          detalles: cartItems.map((i) => ({
            producto_id: i.producto_id,
            cantidad: i.cantidad,
            precio_unitario: i.precio,
          })),
        });
        showToast("Venta registrada exitosamente", "success");
        cartItems = [];
        renderCart();
        formVenta.reset();
        closeModal("modalNuevaVenta");
        await loadData();
      } catch (err) { showToast(err.message, "error"); }
    });
  }

  // ── View / Anular ──────────────────────────────────────────────────────────
  function viewVenta(id) {
    const v = ventas.find((x) => x.id === id);
    if (!v) return;
    const detailEl = document.getElementById("ventaDetalle");
    if (!detailEl) return;
    let rows = v.detalles.map((d) =>
      `<tr><td>${d.producto?.nombre || d.producto_id}</td><td>${d.cantidad}</td><td>$${d.precio_unitario.toLocaleString("es-CO")}</td><td>$${d.subtotal.toLocaleString("es-CO")}</td></tr>`
    ).join("");
    detailEl.innerHTML = `
      <p><strong>Número:</strong> ${v.numero}</p>
      <p><strong>Cliente:</strong> ${v.cliente ? v.cliente.nombre : "Consumidor final"}</p>
      <p><strong>Fecha:</strong> ${formatDate(v.creado_en)}</p>
      <p><strong>Estado:</strong> ${v.estado}</p>
      <table class="table table-sm table-bordered">
        <thead><tr><th>Producto</th><th>Cant.</th><th>Precio</th><th>Subtotal</th></tr></thead>
        <tbody>${rows}</tbody>
        <tfoot><tr><td colspan="3"><strong>Descuento</strong></td><td>-$${v.descuento.toLocaleString("es-CO")}</td></tr>
        <tr><td colspan="3"><strong>Total</strong></td><td><strong>$${v.total.toLocaleString("es-CO")}</strong></td></tr></tfoot>
      </table>`;
    openModal("modalVerVenta");
  }

  async function anularVenta(id) {
    if (!confirm("¿Anular esta venta? El stock será restaurado.")) return;
    try {
      await api.delete(`/api/ventas/${id}`);
      showToast("Venta anulada", "warning");
      await loadData();
    } catch (err) { showToast(err.message, "error"); }
  }

  // ── Modals ─────────────────────────────────────────────────────────────────
  function openModal(id) {
    const el = document.getElementById(id);
    if (el) { el.style.display = "block"; el.classList.add("show"); }
  }
  function closeModal(id) {
    const el = document.getElementById(id);
    if (el) { el.style.display = "none"; el.classList.remove("show"); }
  }
  document.querySelectorAll("[data-dismiss='modal']").forEach((btn) => {
    btn.addEventListener("click", () => {
      const modal = btn.closest(".modal");
      if (modal) closeModal(modal.id);
    });
  });

  await loadData();
});
