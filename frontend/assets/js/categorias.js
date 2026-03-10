/**
 * Gestivoryx – Módulo de Categorías
 */
document.addEventListener("DOMContentLoaded", async function () {
  if (!requireAuth()) return;
  document.querySelectorAll('[href="login.html"]').forEach((el) => {
    el.addEventListener("click", (e) => { e.preventDefault(); logout(); });
  });

  let categorias = [];
  let editingId = null;

  function renderTable() {
    const tbody = document.querySelector("#tablaCategorias tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    categorias.forEach((c) => {
      const badge = c.activo
        ? '<span class="badge badge-success">Activo</span>'
        : '<span class="badge badge-danger">Inactivo</span>';
      tbody.innerHTML += `<tr>
        <td>${c.id}</td>
        <td>${c.nombre}</td>
        <td>${c.descripcion || "-"}</td>
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
      btn.addEventListener("click", () => deleteCategoria(parseInt(btn.dataset.id)));
    });
  }

  async function loadCategorias() {
    try {
      categorias = await api.get("/api/categorias/?solo_activas=false");
      renderTable();
      const boxes = document.querySelectorAll(".small-box h3");
      if (boxes[0]) boxes[0].textContent = categorias.filter((c) => c.activo).length;
    } catch (e) {
      showToast("Error al cargar categorías", "error");
    }
  }

  const formAdd = document.getElementById("formAgregarCategoria");
  if (formAdd) {
    formAdd.addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await api.post("/api/categorias/", {
          nombre: document.getElementById("catNombre").value.trim(),
          descripcion: document.getElementById("catDesc")?.value.trim() || null,
        });
        showToast("Categoría creada", "success");
        closeModal("modalAgregarCategoria");
        formAdd.reset();
        await loadCategorias();
      } catch (err) { showToast(err.message, "error"); }
    });
  }

  const formEdit = document.getElementById("formEditarCategoria");
  if (formEdit) {
    formEdit.addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await api.put(`/api/categorias/${editingId}`, {
          nombre: document.getElementById("editCatNombre").value.trim(),
          descripcion: document.getElementById("editCatDesc")?.value.trim() || null,
        });
        showToast("Categoría actualizada", "success");
        closeModal("modalEditarCategoria");
        await loadCategorias();
      } catch (err) { showToast(err.message, "error"); }
    });
  }

  function openEdit(id) {
    const c = categorias.find((x) => x.id === id);
    if (!c) return;
    editingId = id;
    const n = document.getElementById("editCatNombre");
    const d = document.getElementById("editCatDesc");
    if (n) n.value = c.nombre;
    if (d) d.value = c.descripcion || "";
    openModal("modalEditarCategoria");
  }

  async function deleteCategoria(id) {
    if (!confirm("¿Desactivar esta categoría?")) return;
    try {
      await api.delete(`/api/categorias/${id}`);
      showToast("Categoría desactivada", "warning");
      await loadCategorias();
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

  await loadCategorias();
});
