/**
 * Gestivoryx – Dashboard
 * Carga dinámica de estadísticas desde el backend API.
 */
document.addEventListener("DOMContentLoaded", async function () {
  if (!requireAuth()) return;

  // ── Load dashboard statistics ───────────────────────────────────────────────
  async function loadDashboardStats() {
    try {
      // Cargar datos en paralelo para mejor rendimiento
      const [productos, ventas] = await Promise.all([
        api.get("/api/productos/?solo_activos=false"),
        api.get("/api/ventas/")
      ]);

      // Calcular estadísticas de productos
      const totalProductos = productos.filter((p) => p.activo).length;
      const bajoStock = productos.filter((p) => p.activo && p.stock <= p.stock_minimo).length;
      const agotados = productos.filter((p) => p.activo && p.stock === 0).length;

      // Calcular estadísticas de ventas
      const hoy = new Date();
      hoy.setHours(0, 0, 0, 0);
      const ventasHoy = ventas.filter((v) => {
        const ventaFecha = new Date(v.creado_en);
        ventaFecha.setHours(0, 0, 0, 0);
        return ventaFecha.getTime() === hoy.getTime() && v.estado === "completada";
      }).length;

      const mesActual = new Date();
      mesActual.setDate(1);
      mesActual.setHours(0, 0, 0, 0);
      const ingresosMes = ventas
        .filter((v) => {
          const ventaFecha = new Date(v.creado_en);
          ventaFecha.setHours(0, 0, 0, 0);
          return ventaFecha >= mesActual && v.estado === "completada";
        })
        .reduce((sum, v) => sum + v.total, 0);

      // Actualizar tarjetas del dashboard
      const elTotalProductos = document.getElementById("totalProductos");
      const elVentasHoy = document.getElementById("ventasHoy");
      const elIngresosMes = document.getElementById("ingresosMes");
      const elBajoStock = document.getElementById("bajoStock");

      if (elTotalProductos) {
        elTotalProductos.textContent = totalProductos.toLocaleString("es-CO");
      }
      if (elVentasHoy) {
        elVentasHoy.textContent = ventasHoy;
      }
      if (elIngresosMes) {
        elIngresosMes.textContent = "$" + (ingresosMes / 1000000).toFixed(1) + "M";
      }
      if (elBajoStock) {
        elBajoStock.textContent = bajoStock;
      }

      // Cargar ventas recientes para la tabla
      loadRecentSales(ventas);

    } catch (e) {
      console.error("Error cargando estadísticas del dashboard:", e);
      showToast("Error cargando estadísticas", "error");
    }
  }

  // ── Load recent sales table ───────────────────────────────────────────────────
  function loadRecentSales(ventas) {
    const tbody = document.getElementById("tablaVentasRecientes");
    if (!tbody) return;

    // Ordenar por fecha descendente y tomar las 5 más recientes
    const ventasRecientes = ventas
      .sort((a, b) => new Date(b.creado_en) - new Date(a.creado_en))
      .slice(0, 5);

    tbody.innerHTML = "";
    ventasRecientes.forEach((v) => {
      const badge = v.estado === "completada"
        ? '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">Completada</span>'
        : v.estado === "pendiente"
        ? '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">Pendiente</span>'
        : '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">Anulada</span>';

      const fecha = new Date(v.creado_en);
      const fechaFormateada = fecha.toLocaleDateString("es-CO", {
        day: "numeric",
        month: "short",
        hour: "2-digit",
        minute: "2-digit"
      });

      tbody.innerHTML += `
        <tr class="hover:bg-gray-50 transition-colors">
          <td class="px-6 py-3.5 text-sm text-gray-600">#${v.numero}</td>
          <td class="px-6 py-3.5 text-sm font-medium text-gray-900">${v.cliente ? v.cliente.nombre : "Consumidor final"}</td>
          <td class="px-6 py-3.5 text-sm text-gray-700">$${v.total.toLocaleString("es-CO")}</td>
          <td class="px-6 py-3.5">${badge}</td>
          <td class="px-6 py-3.5 text-sm text-gray-500">${fechaFormateada}</td>
        </tr>
      `;
    });
  }

  // ── Init ─────────────────────────────────────────────────────────────────────
  await loadDashboardStats();
});
