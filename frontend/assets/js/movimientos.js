/**
 * Gestivoryx – Módulo de Movimientos
 * Historial de movimientos de inventario con estadísticas dinámicas.
 */
document.addEventListener("DOMContentLoaded", async function () {
  if (!requireAuth()) return;
  document.querySelectorAll('[href="login.html"]').forEach((el) => {
    el.addEventListener("click", (e) => { e.preventDefault(); logout(); });
  });

  let movimientos = [];

  function renderTable(retryCount = 0) {
    const tbody = document.getElementById("tablaMovimientos");
    if (!tbody) {
      if (retryCount < 50) {
        console.warn(`renderTable: No se encontró tbody #tablaMovimientos, reintentando en 100ms (intento ${retryCount + 1}/50)`);
        setTimeout(() => renderTable(retryCount + 1), 100);
      } else {
        console.error('renderTable: No se encontró tbody #tablaMovimientos después de 50 intentos.');
      }
      return;
    }
    tbody.innerHTML = "";
    movimientos.forEach((m) => {
      const tipoBadge = m.tipo === "entrada"
        ? '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">Entrada</span>'
        : m.tipo === "salida"
        ? '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">Salida</span>'
        : '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-cyan-100 text-cyan-800">Ajuste</span>';
      
      tbody.innerHTML += `
        <tr class="hover:bg-gray-50 transition-colors">
          <td class="px-6 py-3.5 text-sm text-gray-600">#${m.id}</td>
          <td class="px-6 py-3.5 text-sm font-medium text-gray-900">${m.producto?.nombre || m.producto_id}</td>
          <td class="px-6 py-3.5 text-sm text-gray-700">${m.cantidad}</td>
          <td class="px-6 py-3.5">${tipoBadge}</td>
          <td class="px-6 py-3.5 text-sm text-gray-500">${m.motivo || "-"}</td>
          <td class="px-6 py-3.5 text-sm text-gray-500">${formatDate(m.creado_en)}</td>
        </tr>
      `;
    });
  }

  async function loadMovimientos() {
    try {
      movimientos = await api.get("/api/movimientos/");
      renderTable();
      updateSummaryCards();
    } catch (e) {
      console.error("Error al cargar movimientos:", e);
      showToast("Error al cargar movimientos", "error");
    }
  }

  function updateSummaryCards() {
    const total = movimientos.length;
    const entradas = movimientos.filter((m) => m.tipo === "entrada").length;
    const salidas = movimientos.filter((m) => m.tipo === "salida").length;
    const ajustes = movimientos.filter((m) => m.tipo === "ajuste").length;

    const elTotal = document.getElementById("cardTotalMovimientos");
    const elEntradas = document.getElementById("cardEntradas");
    const elSalidas = document.getElementById("cardSalidas");
    const elAjustes = document.getElementById("cardAjustes");

    if (elTotal) elTotal.textContent = total;
    if (elEntradas) elEntradas.textContent = entradas;
    if (elSalidas) elSalidas.textContent = salidas;
    if (elAjustes) elAjustes.textContent = ajustes;
  }

  function openModal(id) {
    const el = document.getElementById(id);
    if (el) { el.style.display = "block"; el.classList.add("show"); }
  }
  function closeModal(id) {
    const el = document.getElementById(id);
    if (el) { el.style.display = "none"; el.classList.remove("show"); }
  }

  await loadMovimientos();
});
