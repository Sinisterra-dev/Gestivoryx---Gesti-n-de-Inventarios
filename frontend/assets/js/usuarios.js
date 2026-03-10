/**
 * Gestivoryx – Módulo de Usuarios (solo admin)
 */
document.addEventListener("DOMContentLoaded", async function () {
  if (!requireAuth()) return;

  // ── Bind logout ────────────────────────────────────────────────────────────
  document.querySelectorAll('[href="login.html"]').forEach((el) => {
    el.addEventListener("click", (e) => { e.preventDefault(); logout(); });
  });

  const currentUser = getUser();

  let usuarios = [];

  function renderTable() {
    const tbody = document.getElementById("tablaUsuariosBody");
    if (!tbody) return;
    tbody.innerHTML = "";
    usuarios.forEach((u) => {
      const rolBadge = u.rol === "admin"
        ? '<span class="badge badge-primary">Administrador</span>'
        : '<span class="badge badge-info">Usuario</span>';
      const estadoBadge = u.activo
        ? '<span class="badge badge-success">Activo</span>'
        : '<span class="badge badge-danger">Inactivo</span>';
      const isSelf = currentUser && currentUser.id === u.id;
      tbody.innerHTML += `<tr>
        <td>${u.id}</td>
        <td>${u.nombre} <small class="text-muted">(${u.username})</small></td>
        <td>${u.email}</td>
        <td>${rolBadge}</td>
        <td>${estadoBadge}</td>
        <td>
          ${!isSelf ? `<button class="btn btn-sm btn-danger btn-delete-usr" data-id="${u.id}" title="Eliminar"><i class="fas fa-trash"></i></button>` : '<span class="text-muted">—</span>'}
        </td>
      </tr>`;
    });

    document.querySelectorAll(".btn-delete-usr").forEach((btn) => {
      btn.addEventListener("click", () => deleteUsuario(parseInt(btn.dataset.id)));
    });
  }

  async function loadUsuarios() {
    try {
      usuarios = await api.get("/api/usuarios/");
      renderTable();
    } catch (e) {
      if (e.message.includes("403") || e.message.includes("401")) {
        showToast("Solo administradores pueden ver usuarios", "warning");
      } else {
        showToast("Error al cargar usuarios: " + e.message, "error");
      }
    }
  }

  const formAdd = document.getElementById("formAgregarUsuario");
  if (formAdd) {
    formAdd.addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await api.post("/api/usuarios/", {
          username: document.getElementById("usrUsername").value.trim(),
          nombre: document.getElementById("usrNombre").value.trim(),
          email: document.getElementById("usrEmail").value.trim(),
          password: document.getElementById("usrPassword").value,
          rol: document.getElementById("usrRol").value,
        });
        showToast("Usuario creado exitosamente", "success");
        closeModal("modalAgregarUsuario");
        formAdd.reset();
        await loadUsuarios();
      } catch (err) { showToast(err.message, "error"); }
    });
  }

  async function deleteUsuario(id) {
    if (!confirm("¿Eliminar este usuario? Esta acción no se puede deshacer.")) return;
    try {
      await api.delete(`/api/usuarios/${id}`);
      showToast("Usuario eliminado", "warning");
      await loadUsuarios();
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

  // Wire the "Nuevo Usuario" button if it opens via data-target
  document.querySelectorAll("[data-target='#modalAgregarUsuario']").forEach((btn) => {
    btn.addEventListener("click", () => openModal("modalAgregarUsuario"));
  });

  await loadUsuarios();
});
