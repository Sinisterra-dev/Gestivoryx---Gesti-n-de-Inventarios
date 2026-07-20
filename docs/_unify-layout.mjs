import fs from 'fs';
import path from 'path';

const dir = path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Z]:)/, '$1'));
const admin = fs.readFileSync(path.join(dir, 'admin.html'), 'utf8');

const HEAD_ASSETS = `  <!-- Tailwind CSS via CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Font Awesome 6 para iconos -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" />
  <!-- Fuente Inter de Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
  <!-- Estilos personalizados del tema -->
  <link rel="stylesheet" href="assets/css/tailwind-theme.css" />
  <style>body { font-family: 'Inter', sans-serif; }</style>`;

const FOOTER = `    <!-- Pie de página -->
    <footer class="px-6 py-4 border-t border-gray-100 bg-white">
      <p class="text-xs text-gray-400 text-center">© 2024 Gestivoryx · Sistema de Gestión de Inventarios</p>
    </footer>
  </div>`;

const NAV_ITEMS = [
  { href: 'admin.html', label: 'Dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { href: 'lista_productos.html', label: 'Productos', icon: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4' },
  { href: 'categorias.html', label: 'Categorías', icon: 'M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z' },
  { href: 'proveedores.html', label: 'Proveedores', icon: 'M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2' },
  { href: 'clientes.html', label: 'Clientes', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z' },
  { href: 'ventas.html', label: 'Ventas', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  { href: 'movimientos.html', label: 'Movimientos', icon: 'M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4' },
  { href: 'usuarios.html', label: 'Usuarios', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z' },
  { href: 'ajustes.html', label: 'Ajustes', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z', icon2: 'M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
];

const ACTIVE = 'text-cyan-400 bg-slate-800 border-l-2 border-cyan-400';
const INACTIVE = 'text-slate-400 hover:text-white hover:bg-slate-800';

function buildNav(activeHref) {
  return NAV_ITEMS.map(({ href, label, icon, icon2 }) => {
    const cls = href === activeHref ? ACTIVE : INACTIVE;
    const paths = icon2
      ? `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${icon}"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${icon2}"/>`
      : `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${icon}"/>`;
    return `      <a href="${href}" class="flex items-center gap-3 px-3 py-2.5 rounded-xl ${cls} transition-colors group">
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">${paths}</svg>
        <span class="text-sm font-medium">${label}</span>
      </a>`;
  }).join('\n\n');
}

function buildShell(activeHref, title, subtitle) {
  return `<body class="bg-gray-50 overflow-x-hidden">

  <!-- ============================================================
       Barra lateral de navegación fija con fondo oscuro
       ============================================================ -->
  <aside id="sidebar" class="fixed inset-y-0 left-0 w-64 bg-slate-900 z-30 flex flex-col transition-transform duration-300">

    <!-- Logotipo de Gestivoryx -->
    <div class="flex items-center gap-3 px-6 py-5 border-b border-slate-800">
      <div class="w-8 h-8 bg-cyan-500 rounded-lg flex items-center justify-center flex-shrink-0">
        <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
        </svg>
      </div>
      <span class="text-white font-bold text-lg tracking-tight">Gestivoryx</span>
    </div>

    <!-- Panel de usuario — clases requeridas por api.js: .user-name y .user-role -->
    <div class="px-6 py-4 border-b border-slate-800">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 bg-slate-700 rounded-full flex items-center justify-center flex-shrink-0">
          <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
          </svg>
        </div>
        <div class="min-w-0">
          <p class="user-name text-sm font-medium text-white truncate">Cargando...</p>
          <p class="user-role text-xs text-slate-400">Usuario</p>
        </div>
      </div>
    </div>

    <!-- Menú de navegación principal -->
    <nav class="flex-1 px-4 py-4 space-y-1 overflow-y-auto scrollbar-hide">

${buildNav(activeHref)}
    </nav>

    <!-- Botón de cerrar sesión -->
    <div class="px-4 py-4 border-t border-slate-800">
      <button onclick="logout()" class="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-slate-400 hover:text-red-400 hover:bg-slate-800 transition-colors">
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
        </svg>
        <span class="text-sm font-medium">Cerrar Sesión</span>
      </button>
    </div>
  </aside>

  <!-- ============================================================
       Contenido principal desplazado a la derecha del sidebar
       ============================================================ -->
  <div id="main-content" class="ml-64 flex flex-col min-h-screen">

    <!-- Encabezado superior de la página -->
    <header class="bg-white border-b border-gray-100 px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between sticky top-0 z-20">
      <!-- Botón para alternar el sidebar en móviles + Título de la página -->
      <div class="flex items-center gap-4">
        <button id="menu-toggle" class="p-2 rounded-xl text-gray-500 hover:bg-gray-100 transition-colors md:hidden">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
        <div>
          <h1 class="text-lg font-semibold text-gray-900">${title}</h1>
          <p class="text-xs text-gray-500">${subtitle}</p>
        </div>
      </div>

      <!-- Información del usuario en el header -->
      <div class="relative">
        <button id="userMenuBtn" class="flex items-center gap-2 focus:outline-none">
          <span class="text-sm text-gray-500 hidden sm:block">Bienvenido,</span>
          <div class="flex items-center gap-2 bg-gray-50 px-3 py-1.5 rounded-xl border border-gray-100">
            <div class="w-7 h-7 bg-cyan-500 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </div>
            <span class="user-name text-sm font-medium text-gray-700">Usuario</span>
          </div>
        </button>
        <!-- Dropdown Menu -->
        <div id="userDropdown" class="hidden absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-100 py-2 z-50">
          <a href="ajustes.html" class="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            Ajustes
          </a>
          <div class="border-t border-gray-100 my-1"></div>
          <button id="logoutBtn" class="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
            Cerrar Sesión
          </button>
        </div>
      </div>
    </header>

`;
}

function fixHead(html) {
  const seoEnd = html.indexOf('<!-- ═══════════════════════════════════════════════════ -->');
  if (seoEnd === -1) throw new Error('SEO block not found');
  const headEnd = html.indexOf('</head>');
  const seoBlock = html.slice(0, seoEnd + '<!-- ═══════════════════════════════════════════════════ -->'.length);
  return seoBlock + '\n\n' + HEAD_ASSETS + '\n</head>\n';
}

function extractMainInner(html) {
  const mainStart = html.search(/<main class="flex-1 py-6 px-4 sm:px-6 lg:px-8">/);
  if (mainStart === -1) throw new Error('main not found');
  const innerStart = html.indexOf('<div class="max-w-7xl mx-auto space-y-6">', mainStart);
  if (innerStart === -1) throw new Error('max-w-7xl wrapper not found');
  const innerContentStart = innerStart + '<div class="max-w-7xl mx-auto space-y-6">'.length;
  const mainClose = html.indexOf('</main>', innerContentStart);
  if (mainClose === -1) throw new Error('</main> not found');
  let inner = html.slice(innerContentStart, mainClose).trim();
  // Remove stray closing div if present before </main>
  inner = inner.replace(/\s*<\/div>\s*$/, '').trim();
  return inner;
}

function extractTail(html) {
  const mainClose = html.indexOf('</main>');
  if (mainClose === -1) throw new Error('</main> not found for tail');
  let tail = html.slice(mainClose + '</main>'.length);
  // Remove existing footer blocks and main-content closing div
  tail = tail.replace(/<!--[^]*?-->\s*/g, (m) => m.includes('footer') || m.includes('Pie') || m.includes('FIN CONTENIDO') ? '' : m);
  tail = tail.replace(/<footer[\s\S]*?<\/footer>\s*/gi, '');
  tail = tail.replace(/\s*<\/div>\s*(?=<!--|\s*<(?:div|script))/i, '\n');
  tail = tail.replace(/<!-- ===== FIN CONTENIDO PRINCIPAL ===== -->\s*/g, '');
  return tail.trim();
}

const pages = [
  { file: 'ventas.html', active: 'ventas.html', title: 'Ventas', subtitle: 'Registro y seguimiento de ventas' },
  { file: 'lista_productos.html', active: 'lista_productos.html', title: 'Productos', subtitle: 'Gestión del inventario de productos' },
  { file: 'categorias.html', active: 'categorias.html', title: 'Categorías', subtitle: 'Gestión de categorías de productos' },
  { file: 'proveedores.html', active: 'proveedores.html', title: 'Proveedores', subtitle: 'Gestión de proveedores del inventario' },
  { file: 'clientes.html', active: 'clientes.html', title: 'Clientes', subtitle: 'Gestión de cartera de clientes' },
  { file: 'movimientos.html', active: 'movimientos.html', title: 'Movimientos de Inventario', subtitle: 'Historial de entradas y salidas' },
  { file: 'ajustes.html', active: 'ajustes.html', title: 'Ajustes', subtitle: 'Configuración del sistema' },
];

for (const page of pages) {
  const filePath = path.join(dir, page.file);
  const html = fs.readFileSync(filePath, 'utf8');
  const head = fixHead(html);
  const mainInner = extractMainInner(html);
  const tail = extractTail(html);

  const output = head + buildShell(page.active, page.title, page.subtitle) +
    `    <!-- Contenido principal del dashboard -->
    <main class="flex-1 py-6 px-4 sm:px-6 lg:px-8">
      <div class="max-w-7xl mx-auto space-y-6">

${mainInner}
      </div>
    </main>

${FOOTER}

${tail}
</body>
</html>
`;

  fs.writeFileSync(filePath, output, 'utf8');
  console.log('Updated:', page.file);
}

fs.unlinkSync(path.join(dir, '_unify-layout.mjs'));
console.log('Done.');
