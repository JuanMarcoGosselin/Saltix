const breadcrumbs = {
  inicio: 'Inicio',
  nomina: 'Procesar Nomina',
  historial: 'Historial de Pagos',
  deducciones: 'Deducciones',
  bonos: 'Bonos',
  planteles: 'Planteles',
  reportes: 'Reportes Financieros',
};

let nominaFilter = 'todos';

function showPage(id, btn) {
  document.querySelectorAll('.page').forEach((page) => page.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach((item) => item.classList.remove('active'));
  const page = document.getElementById(`page-${id}`);
  if (page) page.classList.add('active');
  if (btn) btn.classList.add('active');
  const breadcrumb = document.getElementById('breadcrumb-text');
  if (breadcrumb) breadcrumb.textContent = breadcrumbs[id] || id;
  closeSidebar();
}

function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  if (sidebar.classList.contains('open')) closeSidebar();
  else openSidebar();
}

function openSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  const hamburger = document.getElementById('hamburger-btn');
  if (sidebar) sidebar.classList.add('open');
  if (overlay) overlay.classList.add('visible');
  if (hamburger) hamburger.textContent = 'X';
}

function closeSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  const hamburger = document.getElementById('hamburger-btn');
  if (sidebar) sidebar.classList.remove('open');
  if (overlay) overlay.classList.remove('visible');
  if (hamburger) hamburger.textContent = '\u2630';
}

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') closeSidebar();
});

function filterNomina(filter, button) {
  nominaFilter = filter;
  document.querySelectorAll('#nomina-tabs .tab-btn').forEach((tab) => tab.classList.remove('active'));
  if (button) button.classList.add('active');
  const rows = document.querySelectorAll('#nomina-tbody tr[data-status]');
  rows.forEach((row) => {
    const status = row.dataset.status || '';
    row.hidden = !(filter === 'todos' || status === filter);
  });
}

function searchHistorial(value) {
  const term = (value || '').trim().toLowerCase();
  const rows = document.querySelectorAll('#historial-tbody tr[data-search]');
  rows.forEach((row) => {
    row.hidden = term && !(row.dataset.search || '').includes(term);
  });
}

function togglePlantel(id) {
  const body = document.getElementById(`body-${id}`);
  const chevron = document.getElementById(`chevron-${id}`);
  if (!body) return;
  const isOpen = body.classList.contains('open');
  if (isOpen) {
    body.style.maxHeight = `${body.scrollHeight}px`;
    requestAnimationFrame(() => { body.style.maxHeight = '0'; });
    body.classList.remove('open');
    if (chevron) chevron.style.transform = 'rotate(-90deg)';
  } else {
    body.classList.add('open');
    body.style.maxHeight = `${body.scrollHeight}px`;
    window.setTimeout(() => { body.style.maxHeight = 'none'; }, 380);
    if (chevron) chevron.style.transform = 'rotate(0deg)';
  }
}

function openModalDeduccion() {
  const modal = document.getElementById('modal-ded');
  if (modal) modal.classList.add('open');
}

function openModalBono() {
  const modal = document.getElementById('modal-bono');
  if (modal) modal.classList.add('open');
}

function showToast(message) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  window.setTimeout(() => toast.classList.remove('show'), 3200);
}
