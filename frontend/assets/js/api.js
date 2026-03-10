/**
 * Gestivoryx – API client helper
 * Handles JWT auth, request building, and error handling for all frontend pages.
 */

// API base URL — change this to match your deployment environment
const API_BASE = window.GESTIVORYX_API_URL || "http://localhost:3000";

// ── Token helpers ────────────────────────────────────────────────────────────

function getToken() {
  return localStorage.getItem("gestivoryx_token");
}

function setToken(token) {
  localStorage.setItem("gestivoryx_token", token);
}

function getUser() {
  const raw = localStorage.getItem("gestivoryx_user");
  return raw ? JSON.parse(raw) : null;
}

function setUser(user) {
  localStorage.setItem("gestivoryx_user", JSON.stringify(user));
}

function logout() {
  localStorage.removeItem("gestivoryx_token");
  localStorage.removeItem("gestivoryx_user");
  window.location.href = "login.html";
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = "login.html";
    return false;
  }
  // Populate user info in sidebar if elements exist
  const user = getUser();
  if (user) {
    const nameEl = document.querySelector(".user-name");
    const roleEl = document.querySelector(".user-role");
    if (nameEl) nameEl.textContent = user.nombre || user.username;
    if (roleEl) roleEl.textContent = user.rol === "admin" ? "Administrador" : "Usuario";
    // Top bar username
    document.querySelectorAll(".d-none.d-md-inline").forEach((el) => {
      el.textContent = user.nombre || user.username;
    });
  }
  return true;
}

// ── Core API call ────────────────────────────────────────────────────────────

async function apiCall(method, path, body = null) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const options = { method, headers };
  if (body !== null) options.body = JSON.stringify(body);

  const resp = await fetch(`${API_BASE}${path}`, options);

  if (resp.status === 401) {
    logout();
    return null;
  }

  if (resp.status === 204) return null;

  const data = await resp.json().catch(() => null);

  if (!resp.ok) {
    const msg = data?.detail || `Error ${resp.status}`;
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }

  return data;
}

const api = {
  get: (path) => apiCall("GET", path),
  post: (path, body) => apiCall("POST", path, body),
  put: (path, body) => apiCall("PUT", path, body),
  delete: (path) => apiCall("DELETE", path),
};

// ── Toast notification ───────────────────────────────────────────────────────

function showToast(message, type = "success") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.style.cssText =
      "position:fixed;top:20px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:8px;";
    document.body.appendChild(container);
  }

  const colors = {
    success: "#28a745",
    error: "#dc3545",
    warning: "#ffc107",
    info: "#17a2b8",
  };

  const toast = document.createElement("div");
  toast.style.cssText = `background:${colors[type] || colors.info};color:${type === "warning" ? "#333" : "#fff"};padding:12px 20px;border-radius:6px;box-shadow:0 4px 12px rgba(0,0,0,.2);min-width:220px;font-size:14px;display:flex;align-items:center;gap:8px;`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.4s";
    setTimeout(() => toast.remove(), 400);
  }, 3500);
}

// ── Generic CRUD table helpers ────────────────────────────────────────────────

function formatCurrency(value) {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatDate(dateStr) {
  if (!dateStr) return "-";
  return new Intl.DateTimeFormat("es-CO", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(dateStr));
}
