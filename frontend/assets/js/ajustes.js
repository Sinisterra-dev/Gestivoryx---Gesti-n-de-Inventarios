/**
 * Gestivoryx – Módulo de Ajustes y Configuración
 * Configuración de empresa y seguridad del sistema.
 */
document.addEventListener("DOMContentLoaded", async function () {
  if (!requireAuth()) return;
  document.querySelectorAll('[href="login.html"]').forEach((el) => {
    el.addEventListener("click", (e) => { e.preventDefault(); logout(); });
  });

  // ── Get current user from localStorage ─────────────────────────────────────────────
  const userStr = localStorage.getItem('gestivoryx_user');
  let currentUser = null;
  if (userStr) {
    try {
      currentUser = JSON.parse(userStr);
      console.log("👤 Usuario actual cargado desde localStorage:", currentUser);
    } catch (e) {
      console.error("❌ Error al parsear usuario de localStorage:", e);
    }
  } else {
    console.error("❌ No se encontró usuario en localStorage");
  }

  // ── Cargar datos iniciales ───────────────────────────────────────────────────────
  async function loadInitialData() {
    try {
      console.log("📥 Cargando datos iniciales...");
      
      // Cargar datos del usuario actual desde la API
      if (currentUser && currentUser.id) {
        const userData = await api.get(`/api/usuarios/${currentUser.id}`);
        console.log("✅ Datos del usuario cargados:", userData);
        
        // Auto-rellenar campos de perfil si existen
        const nombreInput = document.getElementById("empresaNombre");
        const emailInput = document.getElementById("empresaEmail");
        
        if (nombreInput && userData.nombre) {
          nombreInput.value = userData.nombre;
        }
        if (emailInput && userData.email) {
          emailInput.value = userData.email;
        }
      }

      // Cargar configuración de empresa desde localStorage (si existe)
      const empresaConfig = localStorage.getItem("gestivoryx_empresa_config");
      if (empresaConfig) {
        console.log("📦 Configuración de empresa encontrada en localStorage");
        const config = JSON.parse(empresaConfig);
        
        const telefonoInput = document.getElementById("empresaTelefono");
        const direccionInput = document.getElementById("empresaDireccion");
        const monedaSelect = document.getElementById("empresaMoneda");
        
        if (telefonoInput && config.telefono) telefonoInput.value = config.telefono;
        if (direccionInput && config.direccion) direccionInput.value = config.direccion;
        if (monedaSelect && config.moneda) monedaSelect.value = config.moneda;
      }
      
      console.log("✅ Datos iniciales cargados exitosamente");
    } catch (err) {
      console.error("❌ Error al cargar datos iniciales:", err);
      // No mostramos error al usuario ya que son datos opcionales
    }
  }

  await loadInitialData();

  // ── Configuración General ───────────────────────────────────────────────────────
  const formConfigGeneral = document.getElementById("formConfigGeneral");
  if (formConfigGeneral) {
    formConfigGeneral.addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        console.log("💾 Guardando configuración de empresa...");
        
        const config = {
          nombre: document.getElementById("empresaNombre")?.value || "Gestivoryx",
          email: document.getElementById("empresaEmail")?.value || "",
          telefono: document.getElementById("empresaTelefono")?.value || "",
          direccion: document.getElementById("empresaDireccion")?.value || "",
          moneda: document.getElementById("empresaMoneda")?.value || "COP"
        };
        
        console.log("📦 Configuración a guardar:", config);
        
        // Guardar en localStorage
        localStorage.setItem("gestivoryx_empresa_config", JSON.stringify(config));
        
        console.log("✅ Configuración guardada en localStorage");
        showToast("Configuración guardada correctamente", "success");
      } catch (err) {
        console.error("❌ Error al guardar configuración:", err);
        showToast(err.message, "error");
      }
    });
  }

  // ── Cambiar Contraseña ───────────────────────────────────────────────────────────
  const formCambiarPassword = document.getElementById("formCambiarPassword");
  if (formCambiarPassword) {
    formCambiarPassword.addEventListener("submit", async (e) => {
      e.preventDefault();
      const currentPassword = document.getElementById("currentPassword").value;
      const newPassword = document.getElementById("newPassword").value;
      const confirmPassword = document.getElementById("confirmPassword").value;

      console.log("🔐 Intentando cambiar contraseña");
      console.log("Usuario actual:", currentUser);

      if (!currentPassword || !newPassword || !confirmPassword) {
        showToast("Completa todos los campos", "warning");
        return;
      }

      if (newPassword !== confirmPassword) {
        showToast("Las contraseñas no coinciden", "error");
        return;
      }

      if (newPassword.length < 6) {
        showToast("La contraseña debe tener al menos 6 caracteres", "error");
        return;
      }

      try {
        // Usar el endpoint PUT /api/usuarios/{id} con el campo password
        if (!currentUser || !currentUser.id) {
          showToast("Error: No se pudo identificar el usuario actual", "error");
          console.error("❌ No hay usuario actual en localStorage");
          return;
        }

        console.log(`📤 Enviando petición a /api/usuarios/${currentUser.id}`);
        console.log("Payload:", { password: newPassword });

        const response = await api.put(`/api/usuarios/${currentUser.id}`, {
          password: newPassword
        });

        console.log("✅ Respuesta del servidor:", response);
        showToast("Contraseña actualizada correctamente", "success");
        formCambiarPassword.reset();
      } catch (err) {
        console.error("❌ Error al cambiar contraseña:", err);
        console.error("Mensaje de error:", err.message);
        
        // Mostrar error específico según el tipo
        if (err.message.includes("401") || err.message.includes("403")) {
          showToast("Error: No tienes permisos para realizar esta acción", "error");
        } else if (err.message.includes("404")) {
          showToast("Error: Usuario no encontrado", "error");
        } else if (err.message.includes("422")) {
          showToast("Error: Datos inválidos. Verifica que la contraseña tenga al menos 6 caracteres", "error");
        } else {
          showToast("Error al actualizar contraseña: " + err.message, "error");
        }
      }
    });
  }
});

