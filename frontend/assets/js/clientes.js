/**
 * Gestivoryx – Módulo de Clientes
 */
document.addEventListener("DOMContentLoaded", async function () {
  if (!requireAuth()) return;
  document.querySelectorAll('[href="login.html"]').forEach((el) => {
    el.addEventListener("click", (e) => { e.preventDefault(); logout(); });
  });

  let clientes = [];
  let editingId = null;

  function renderTable() {
    const tbody = document.querySelector("#tablaClientes tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    clientes.forEach((c) => {
      const badge = c.activo
        ? '<span class="badge badge-success">Activo</span>'
        : '<span class="badge badge-danger">Inactivo</span>';
      tbody.innerHTML += `<tr>
        <td>${c.id}</td>
        <td>${c.nombre}</td>
        <td>${c.documento || "-"}</td>
        <td>${c.telefono || "-"}</td>
        <td>${c.email || "-"}</td>
        <td>${badge}</td>
        <td>
          <button class="btn btn-sm btn-warning btn-edit" data-id="${c.id}"><i class="fas fa-edit"></i></button>
          <button class="btn btn-sm btn-danger btn-delete" data-id="${c.id}"><i class="fas fa-trash"></i></button>
        </td>
      </tr>`;
    });
    document.querySelectorAll(".btn-edit").forEach((btn) => {
      btn.addEventListener("click", () => openEdit(parseInt(btn.dataset.id)));
    });
    document.querySelectorAll(".btn-delete").forEach((btn) => {
      btn.addEventListener("click", () => deleteCliente(parseInt(btn.dataset.id)));
    });
  }

  async function loadClientes() {
    try {
      clientes = await api.get("/api/clientes/?solo_activos=false");
      renderTable();
    } catch (e) {
      showToast("Error al cargar clientes", "error");
    }
  }

  const formAdd = document.getElementById("formAgregarCliente");
  if (formAdd) {
    formAdd.addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await api.post("/api/clientes/", {
          nombre: document.getElementById("cliNombre").value.trim(),
          documento: document.getElementById("cliDocumento")?.value.trim() || null,
          telefono: document.getElementById("cliTelefono")?.value.trim() || null,
          email: document.getElementById("cliEmail")?.value.trim() || null,
          direccion: document.getElementById("cliDireccion")?.value.trim() || null,
        });
        showToast("Cliente creado", "success");
        closeModal("modalAgregarCliente");
        formAdd.reset();
        await loadClientes();
      } catch (err) { showToast(err.message, "error"); }
    });
  }

  const formEdit = document.getElementById("formEditarCliente");
  if (formEdit) {
    formEdit.addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await api.put(`/api/clientes/${editingId}`, {
          nombre: document.getElementById("editCliNombre").value.trim(),
          documento: document.getElementById("editCliDocumento")?.value.trim() || null,
          telefono: document.getElementById("editCliTelefono")?.value.trim() || null,
          email: document.getElementById("editCliEmail")?.value.trim() || null,
          direccion: document.getElementById("editCliDireccion")?.value.trim() || null,
        });
        showToast("Cliente actualizado", "success");
        closeModal("modalEditarCliente");
        await loadClientes();
      } catch (err) { showToast(err.message, "error"); }
    });
  }

  function openEdit(id) {
    const c = clientes.find((x) => x.id === id);
    if (!c) return;
    editingId = id;
    const set = (el, val) => { const e = document.getElementById(el); if (e) e.value = val || ""; };
    set("editCliNombre", c.nombre);
    set("editCliDocumento", c.documento);
    set("editCliTelefono", c.telefono);
    set("editCliEmail", c.email);
    set("editCliDireccion", c.direccion);
    openModal("modalEditarCliente");
  }

  async function deleteCliente(id) {
    if (!confirm("¿Desactivar este cliente?")) return;
    try {
      await api.delete(`/api/clientes/${id}`);
      showToast("Cliente desactivado", "warning");
      await loadClientes();
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

  await loadClientes();
});
