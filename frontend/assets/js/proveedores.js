/**
 * Gestivoryx – Módulo de Proveedores
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
  document.querySelectorAll('[href="login.html"]').forEach((el) => {
    el.addEventListener("click", (e) => { e.preventDefault(); logout(); });
  });

  let proveedores = [];
  let editingId = null;

  function renderTable(retryCount = 0) {
    const tbody = document.getElementById("tablaProveedores");
    if (!tbody) {
      if (retryCount < 50) {
        console.warn(`renderTable: No se encontró tbody #tablaProveedores, reintentando en 100ms (intento ${retryCount + 1}/50)`);
        setTimeout(() => renderTable(retryCount + 1), 100);
      } else {
        console.error('renderTable: No se encontró tbody #tablaProveedores después de 50 intentos. Verificar que el ID en HTML sea exactamente "tablaProveedores" sin espacios ocultos.');
      }
      return;
    }
    tbody.innerHTML = "";
    proveedores.forEach((p) => {
      const badge = p.activo
        ? '<span class="badge badge-success">Activo</span>'
        : '<span class="badge badge-danger">Inactivo</span>';
      tbody.innerHTML += `<tr>
        <td>${p.id}</td>
        <td>${p.nombre}</td>
        <td>${p.contacto || "-"}</td>
        <td>${p.telefono || "-"}</td>
        <td>${p.email || "-"}</td>
        <td>${badge}</td>
        <td>
          <button class="btn btn-sm btn-warning btn-edit" data-id="${p.id}"><i class="fas fa-edit"></i></button>
          <button class="btn btn-sm btn-danger btn-delete" data-id="${p.id}"><i class="fas fa-trash"></i></button>
        </td>
      </tr>`;
    });
    document.querySelectorAll(".btn-edit").forEach((btn) => {
      btn.addEventListener("click", () => openEdit(parseInt(btn.dataset.id)));
    });
    document.querySelectorAll(".btn-delete").forEach((btn) => {
      btn.addEventListener("click", () => deleteProveedor(parseInt(btn.dataset.id)));
    });
  }

  async function loadProveedores() {
    try {
      proveedores = await api.get("/api/proveedores/?solo_activos=false");
      renderTable();
    } catch (e) {
      showToast("Error al cargar proveedores", "error");
    }
  }

  const formAdd = document.getElementById("formAgregarProveedor");
  if (formAdd) {
    formAdd.addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await api.post("/api/proveedores/", {
          nombre: safeGetValue("provNombre")?.trim() || "",
          contacto: safeGetValue("provContacto")?.trim() || null,
          telefono: safeGetValue("provTelefono")?.trim() || null,
          email: safeGetValue("provEmail")?.trim() || null,
          direccion: safeGetValue("provDireccion")?.trim() || null,
        });
        showToast("Proveedor creado", "success");
        closeModal("modalAgregarProveedor");
        formAdd.reset();
        await loadProveedores();
      } catch (err) { showToast(err.message, "error"); }
    });
  }

  const formEdit = document.getElementById("formEditarProveedor");
  if (formEdit) {
    formEdit.addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await api.put(`/api/proveedores/${editingId}`, {
          nombre: safeGetValue("editProvNombre")?.trim() || "",
          contacto: safeGetValue("editProvContacto")?.trim() || null,
          telefono: safeGetValue("editProvTelefono")?.trim() || null,
          email: safeGetValue("editProvEmail")?.trim() || null,
          direccion: safeGetValue("editProvDireccion")?.trim() || null,
        });
        showToast("Proveedor actualizado", "success");
        closeModal("modalEditarProveedor");
        await loadProveedores();
      } catch (err) { showToast(err.message, "error"); }
    });
  }

  function openEdit(id) {
    const p = proveedores.find((x) => x.id === id);
    if (!p) return;
    editingId = id;
    const set = (el, val) => { const e = document.getElementById(el); if (e) e.value = val || ""; };
    set("editProvNombre", p.nombre);
    set("editProvContacto", p.contacto);
    set("editProvTelefono", p.telefono);
    set("editProvEmail", p.email);
    set("editProvDireccion", p.direccion);
    openModal("modalEditarProveedor");
  }

  async function deleteProveedor(id) {
    if (!confirm("¿Desactivar este proveedor?")) return;
    try {
      await api.delete(`/api/proveedores/${id}`);
      showToast("Proveedor desactivado", "warning");
      await loadProveedores();
    } catch (err) { showToast(err.message, "error"); }
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

  await loadProveedores();
});
