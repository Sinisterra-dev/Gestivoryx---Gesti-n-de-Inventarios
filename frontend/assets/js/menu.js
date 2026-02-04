// Manejo del submenú
document.addEventListener('DOMContentLoaded', function() {
    // Botón para alternar el menú lateral
    const pushMenu = document.querySelector('[data-widget="pushmenu"]');
    const body = document.body;
    
    if (pushMenu) {
        pushMenu.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Alternar la clase 'sidebar-collapse' en el body
            if (window.innerWidth <= 991.98) {
                // En móviles, alternamos la clase 'sidebar-open' para mostrar/ocultar el menú
                body.classList.toggle('sidebar-open');
            } else {
                // En escritorio, alternamos la clase 'sidebar-collapse' para mostrar/ocultar el menú
                body.classList.toggle('sidebar-collapse');
            }
        });
    }
    
    // Cerrar el menú al hacer clic fuera de él en móviles
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 991.98 && 
            !e.target.closest('.main-sidebar') && 
            !e.target.closest('[data-widget="pushmenu"]') &&
            body.classList.contains('sidebar-open')) {
            body.classList.remove('sidebar-open');
        }
    });
    
    // Cerrar el menú al cambiar el tamaño de la ventana
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (window.innerWidth > 991.98) {
                // En pantallas grandes, asegurarse de que el menú esté visible
                body.classList.remove('sidebar-open');
                body.classList.remove('sidebar-collapse');
            } else {
                // En móviles, asegurarse de que el menú esté oculto por defecto
                if (!body.classList.contains('sidebar-open')) {
                    body.classList.add('sidebar-collapse');
                }
            }
        }, 250);
    });
    
    // Inicialización del menú para móviles
    if (window.innerWidth <= 991.98) {
        body.classList.add('sidebar-collapse');
    }

    // Manejar submenús
    document.querySelectorAll('.has-treeview > .nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            if (window.innerWidth >= 992) {
                e.preventDefault();
                const parent = this.parentElement;
                
                // Cerrar otros submenús abiertos
                document.querySelectorAll('.has-treeview.menu-open').forEach(openMenu => {
                    if (openMenu !== parent) {
                        openMenu.classList.remove('menu-open');
                    }
                });
                
                // Alternar este submenú
                parent.classList.toggle('menu-open');
            }
        });
    });

    // Cerrar submenú al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.has-treeview')) {
            document.querySelectorAll('.has-treeview.menu-open').forEach(menu => {
                menu.classList.remove('menu-open');
            });
        }
    });

    // Manejar el menú de usuario
    const userMenu = document.querySelector('.user-menu .dropdown-toggle');
    if (userMenu) {
        userMenu.addEventListener('click', function(e) {
            e.preventDefault();
            this.nextElementSibling.classList.toggle('show');
        });
    }

    // Cerrar menú de usuario al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.user-menu')) {
            const dropdown = document.querySelector('.user-menu .dropdown-menu');
            if (dropdown) {
                dropdown.classList.remove('show');
            }
        }
    });

    // Manejar el botón de cerrar sesión
    const logoutBtn = document.querySelector('.logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function() {
            window.location.href = 'login.html';
        });
    }
});