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
});