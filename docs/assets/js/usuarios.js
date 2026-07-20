/**
 * Gestivoryx – Módulo de Usuarios (solo admin)
 */

// ── IMMEDIATE ADMIN ROLE CHECK ─────────────────────────────────────────────────────
// Check role BEFORE DOMContentLoaded to prevent any data leakage
(function() {
  const userStr = localStorage.getItem('gestivoryx_user');
  if (!userStr) {
    console.warn("⛔ No user found in localStorage");
    return;
  }
  
  try {
    const user = JSON.parse(userStr);
    if (!user || user.rol !== "admin") {
      console.warn("⛔ Acceso denegado: Usuario no es administrador");
      document.body.innerHTML = `
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; font-family:sans-serif; background:#f3f4f6;">
          <div style="text-align:center; padding:2rem; background:white; border-radius:1rem; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);">
            <svg style="width:4rem; height:4rem; color:#ef4444; margin-bottom:1rem;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <h2 style="font-size:1.5rem; font-weight:600; color:#1f2937; margin-bottom:0.5rem;">Acceso Denegado</h2>
            <p style="color:#6b7280; margin-bottom:1.5rem;">No tienes permisos de administrador para ver esta sección.</p>
            <button onclick="window.location.href='dashboard.html'" style="padding:0.75rem 1.5rem; background:#0891b2; color:white; border:none; border-radius:0.5rem; cursor:pointer; font-weight:500;">Volver al Dashboard</button>
          </div>
        </div>`;
      throw new Error("Acceso denegado: No es administrador");
    }
  } catch (e) {
    console.error("Error parsing user data:", e);
  }
})();

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

  const currentUser = getUser();
  console.log("👤 Usuario actual cargado:", currentUser);

  let usuarios = [];

  function renderTable() {
    const tbody = document.getElementById("tablaUsuarios");
    if (!tbody) {
      console.error("❌ No se encontró tbody con id 'tablaUsuarios'");
      return;
    }
    try {
      console.log("📊 Intentando renderizar tabla con", usuarios.length, "usuarios");
      tbody.innerHTML = "";
      usuarios.forEach((u) => {
        console.log("👤 Procesando usuario:", u);
        const rolBadge = u.rol === "admin"
          ? '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">Admin</span>'
          : '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-cyan-100 text-cyan-800">Usuario</span>';
        const estadoBadge = u.activo
          ? '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">Activo</span>'
          : '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">Inactivo</span>';
        const isSelf = currentUser && currentUser.id === u.id;
        tbody.innerHTML += `<tr class="hover:bg-gray-50/50 transition-colors">
          <td class="px-4 py-3 text-sm text-gray-500">${u.id}</td>
          <td class="px-4 py-3 text-sm font-medium text-gray-800">${u.nombre}</td>
          <td class="px-4 py-3 text-sm text-gray-600 font-mono">${u.username}</td>
          <td class="px-4 py-3 text-sm text-gray-600">${u.email}</td>
          <td class="px-4 py-3">${rolBadge}</td>
          <td class="px-4 py-3">${estadoBadge}</td>
          <td class="px-4 py-3">
            <div class="flex items-center gap-1">
              ${!isSelf ? `<button class="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-colors btn-delete-usr" data-id="${u.id}" title="Eliminar usuario">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>` : '<span class="text-slate-300 text-xs">—</span>'}
            </div>
          </td>
        </tr>`;
      });
      console.log("✅ Tabla renderizada exitosamente");
      
      // Bind delete buttons after rendering
      document.querySelectorAll(".btn-delete-usr").forEach((btn) => {
        btn.addEventListener("click", () => deleteUsuario(parseInt(btn.dataset.id)));
      });
    } catch (error) {
      console.error("❌ Error al pintar la tabla:", error);
      alert("Error al pintar la tabla: " + error.message);
    }
  }

  async function loadUsuarios() {
    try {
      console.log("📥 Cargando usuarios desde /api/usuarios/");
      usuarios = await api.get("/api/usuarios/");
      console.log("✅ Usuarios recibidos del backend:", usuarios);
      renderTable();
    } catch (e) {
      console.error("❌ Error al cargar usuarios:", e);
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
          username: safeGetValue("usrUsername")?.trim() || "",
          nombre: safeGetValue("usrNombre")?.trim() || "",
          email: safeGetValue("usrEmail")?.trim() || "",
          password: safeGetValue("usrPassword") || "",
          rol: safeGetValue("usrRol") || "usuario",
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
