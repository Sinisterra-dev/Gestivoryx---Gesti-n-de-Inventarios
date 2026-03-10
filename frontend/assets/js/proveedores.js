/**
 * Gestivoryx – Módulo de Proveedores
 */
document.addEventListener("DOMContentLoaded", async function () {
  if (!requireAuth()) return;
  document.querySelectorAll('[href="login.html"]').forEach((el) => {
    el.addEventListener("click", (e) => { e.preventDefault(); logout(); });
  });

  let proveedores = [];
  let editingId = null;

  function renderTable() {
    const tbody = document.querySelector("#tablaProveedores tbody");
    if (!tbody) return;
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
          nombre: document.getElementById("provNombre").value.trim(),
          contacto: document.getElementById("provContacto")?.value.trim() || null,
          telefono: document.getElementById("provTelefono")?.value.trim() || null,
          email: document.getElementById("provEmail")?.value.trim() || null,
          direccion: document.getElementById("provDireccion")?.value.trim() || null,
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
          nombre: document.getElementById("editProvNombre").value.trim(),
          contacto: document.getElementById("editProvContacto")?.value.trim() || null,
          telefono: document.getElementById("editProvTelefono")?.value.trim() || null,
          email: document.getElementById("editProvEmail")?.value.trim() || null,
          direccion: document.getElementById("editProvDireccion")?.value.trim() || null,
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
