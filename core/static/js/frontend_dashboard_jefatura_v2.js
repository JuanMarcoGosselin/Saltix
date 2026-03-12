const breadcrumbs = {equipo:'Mi equipo',asistencia:'Asistencia',solicitudes:'Solicitudes',reportes:'Reportes'};
  let pendientes = 3;

  /* ── Navegación ── */
  function showPage(id, btn) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById('page-' + id).classList.add('active');
    btn.classList.add('active');
    document.getElementById('breadcrumb-text').textContent = breadcrumbs[id] || id;
    closeSidebar();
  }

  /* ── Sidebar ── */
  function toggleSidebar() {
    const isOpen = document.getElementById('sidebar').classList.contains('open');
    isOpen ? closeSidebar() : openSidebar();
  }

  function openSidebar() {
    document.getElementById('sidebar').classList.add('open');
    document.getElementById('sidebar-overlay').classList.add('visible');
    document.getElementById('hamburger-btn').textContent = '✕';
  }

  function closeSidebar() {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('sidebar-overlay').classList.remove('visible');
    document.getElementById('hamburger-btn').textContent = '☰';
  }

  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeSidebar(); });

  /* ── Solicitudes ── */
  function resolverSolicitud(btn, accion) {
    const card = btn.closest('.solicitud-card');
    card.style.transition = 'opacity .3s, transform .3s';
    card.style.opacity = '0';
    card.style.transform = 'translateX(30px)';

    setTimeout(() => {
      card.remove();
      pendientes = Math.max(0, pendientes - 1);

      const badge    = document.getElementById('badge-sol');
      const cardBadge = document.getElementById('card-sol-badge');
      const cardVal  = document.getElementById('card-sol-val');
      const subtitle = document.getElementById('sol-subtitle');

      if (pendientes > 0) {
        badge.textContent    = pendientes;
        cardBadge.textContent = pendientes;
        cardVal.textContent  = pendientes;
        subtitle.textContent = pendientes + ' solicitud' + (pendientes > 1 ? 'es' : '') + ' esperan tu aprobación';
      } else {
        badge.style.display     = 'none';
        cardBadge.style.display = 'none';
        cardVal.textContent     = '0';
        subtitle.textContent    = 'Sin solicitudes pendientes ✅';
      }
    }, 300);
  }
