const breadcrumbs = {
    equipo: 'Mi equipo',
    asistencia: 'Asistencia',
    solicitudes: 'Solicitudes',
    reportes: 'Reportes'
  };

  let pendientes = parseInt('{{ solicitudes_pendientes_total|default:"0" }}', 10);
  if (isNaN(pendientes)) pendientes = 0;

  function showPage(id, btn) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById('page-' + id).classList.add('active');
    if (btn) btn.classList.add('active');
    document.getElementById('breadcrumb-text').textContent = breadcrumbs[id] || id;
    closeSidebar();
  }

  function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const isOpen = sidebar.classList.contains('open');
    isOpen ? closeSidebar() : openSidebar();
  }

  function openSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const hamburger = document.getElementById('hamburger-btn');
    sidebar.classList.add('open');
    if (overlay) overlay.classList.add('visible');
    if (hamburger) hamburger.textContent = 'X';
  }

  function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const hamburger = document.getElementById('hamburger-btn');
    sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('visible');
    if (hamburger) hamburger.textContent = '\u2630';
  }

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeSidebar();
  });

  function syncSolicitudesUI() {
    const badge = document.getElementById('badge-sol');
    const cardBadge = document.getElementById('card-sol-badge');
    const cardVal = document.getElementById('card-sol-val');
    const subtitle = document.getElementById('sol-subtitle');
    const list = document.getElementById('solicitudes-list');

    if (badge) {
      if (pendientes > 0) {
        badge.style.display = 'inline-flex';
        badge.textContent = pendientes;
      } else {
        badge.style.display = 'none';
      }
    }

    if (cardBadge) {
      if (pendientes > 0) {
        cardBadge.style.display = 'inline-block';
        cardBadge.textContent = pendientes;
      } else {
        cardBadge.style.display = 'none';
      }
    }

    if (cardVal) cardVal.textContent = pendientes;

    if (subtitle) {
      subtitle.textContent = pendientes > 0
        ? (pendientes + ' solicitud' + (pendientes > 1 ? 'es' : '') + ' esperan tu aprobacion')
        : 'Sin solicitudes pendientes';
    }

    if (list && pendientes === 0 && !list.querySelector('.solicitud-card')) {
      const empty = document.createElement('div');
      empty.className = 'solicitud-card';
      empty.innerHTML = '<div class="sol-info"><div class="sol-name">Sin solicitudes pendientes</div><div class="sol-desc">No hay solicitudes por revisar.</div></div>';
      list.appendChild(empty);
    }
  }

  function resolverSolicitud(btn, accion) {
    const card = btn.closest('.solicitud-card');
    card.style.transition = 'opacity .3s, transform .3s';
    card.style.opacity = '0';
    card.style.transform = 'translateX(30px)';

    setTimeout(() => {
      card.remove();
      pendientes = Math.max(0, pendientes - 1);
      syncSolicitudesUI();
    }, 300);
  }

  syncSolicitudesUI();
