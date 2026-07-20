// Gestivoryx — Lógica de la barra lateral para el nuevo diseño con Tailwind CSS
document.addEventListener('DOMContentLoaded', function () {
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('menu-toggle');
  const mainContent = document.getElementById('main-content');

  // Alternar visibilidad del sidebar en dispositivos móviles
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('-translate-x-full');
      if (mainContent) mainContent.classList.toggle('ml-0');
    });
  }

  // Cerrar el sidebar al hacer clic fuera de él en móviles
  document.addEventListener('click', function (e) {
    if (
      window.innerWidth < 768 &&
      sidebar &&
      !sidebar.contains(e.target) &&
      toggleBtn &&
      !toggleBtn.contains(e.target) &&
      !sidebar.classList.contains('-translate-x-full')
    ) {
      sidebar.classList.add('-translate-x-full');
    }
  });

  // ── User Profile Dropdown ───────────────────────────────────────────────────────
  const userMenuBtn = document.getElementById('userMenuBtn');
  const userDropdown = document.getElementById('userDropdown');
  const logoutBtn = document.getElementById('logoutBtn');

  if (userMenuBtn && userDropdown) {
    userMenuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      userDropdown.classList.toggle('hidden');
    });

    // Cerrar dropdown al hacer clic fuera
    document.addEventListener('click', (e) => {
      if (!userMenuBtn.contains(e.target) && !userDropdown.contains(e.target)) {
        userDropdown.classList.add('hidden');
      }
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      localStorage.removeItem('gestivoryx_user');
      localStorage.removeItem('gestivoryx_token');
      window.location.href = 'login.html';
    });
  }
});