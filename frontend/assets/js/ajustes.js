/**
 * Gestivoryx – Módulo de Ajustes de Inventario (Movimientos)
 */
document.addEventListener("DOMContentLoaded", async function () {
  if (!requireAuth()) return;
  document.querySelectorAll('[href="login.html"]').forEach((el) => {
    el.addEventListener("click", (e) => { e.preventDefault(); logout(); });
  });

  let movimientos = [];
  let productos = [];

  async function loadData() {
    try {
      [movimientos, productos] = await Promise.all([
        api.get("/api/movimientos/"),
        api.get("/api/productos/"),
      ]);
      renderTable();
      populateProductSelect();
    } catch (e) {
      showToast("Error cargando datos", "error");
    }
  }

  function populateProductSelect() {
    const sel = document.getElementById("movProducto");
    if (!sel) return;
    sel.innerHTML = '<option value="">Seleccionar producto...</option>';
    productos.forEach((p) => {
      sel.innerHTML += `<option value="${p.id}">${p.nombre} (Stock: ${p.stock})</option>`;
    });
  }

  function renderTable() {
    const tbody = document.querySelector("#tablaAjustes tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    movimientos.forEach((m) => {
      const typeClass = m.tipo === "entrada" ? "badge-success" : m.tipo === "salida" ? "badge-danger" : "badge-warning";
      tbody.innerHTML += `<tr>
        <td>${m.id}</td>
        <td>${m.producto?.nombre || m.producto_id}</td>
        <td><span class="badge ${typeClass}">${m.tipo}</span></td>
        <td>${m.cantidad}</td>
        <td>${m.stock_anterior} → ${m.stock_nuevo}</td>
        <td>${m.motivo || "-"}</td>
        <td>${formatDate(m.creado_en)}</td>
        <td>${m.usuario?.nombre || "-"}</td>
      </tr>`;
    });
  }

  const form = document.getElementById("formAjuste");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await api.post("/api/movimientos/", {
          producto_id: parseInt(document.getElementById("movProducto").value),
          tipo: document.getElementById("movTipo").value,
          cantidad: parseInt(document.getElementById("movCantidad").value),
          motivo: document.getElementById("movMotivo")?.value.trim() || null,
        });
        showToast("Movimiento registrado", "success");
        closeModal("modalAjuste");
        form.reset();
        await loadData();
      } catch (err) { showToast(err.message, "error"); }
    });
  }

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
