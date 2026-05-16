const breadcrumbs = {
  inicio: 'Inicio',
  periodos: 'Periodos de Nomina',
  historial: 'Historial de Nominas',
  reportes: 'Reportes Financieros',
};

const PAGE_STORAGE_KEY = 'contabilidad_active_page';

let nominaFilter = 'todos';

function getContabilidadNavButtons() {
  return Array.from(document.querySelectorAll('.nav-item[data-page]'));
}

function findContabilidadNavButton(pageId) {
  return getContabilidadNavButtons().find((button) => button.dataset.page === pageId);
}

function buildDashboardSectionUrl(button, pageId) {
  const baseUrl = button?.dataset.dashboardUrl || '';
  if (!baseUrl) return '';
  return `${baseUrl}#${encodeURIComponent(pageId)}`;
}

function showPage(id, btn) {
  const page = document.getElementById(`page-${id}`);
  if (!page) {
    const destination = buildDashboardSectionUrl(btn, id);
    if (destination) window.location.href = destination;
    return;
  }

  document.querySelectorAll('.page').forEach((pageItem) => pageItem.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach((item) => item.classList.remove('active'));
  page.classList.add('active');
  if (btn) btn.classList.add('active');
  const breadcrumb = document.getElementById('breadcrumb-text');
  if (breadcrumb) breadcrumb.textContent = breadcrumbs[id] || id;
  if (window.location.hash !== `#${id}`) {
    history.replaceState(null, '', `#${id}`);
  }
  saveActivePage(id);
  closeSidebar();
}

function saveActivePage(pageId) {
  if (!pageId) return;
  try { localStorage.setItem(PAGE_STORAGE_KEY, pageId); } catch (error) {}
}

function getStoredPage() {
  try { return localStorage.getItem(PAGE_STORAGE_KEY) || ''; } catch (error) { return ''; }
}

function getRequestedPage() {
  const params = new URLSearchParams(window.location.search);
  if (params.has('page')) return params.get('page') || '';
  return decodeURIComponent((window.location.hash || '').replace('#', '')) || '';
}

function setupContabilidadSidebar() {
  const currentPreviewPage = document.getElementById('page-nomina-gen');
  if (currentPreviewPage) {
    getContabilidadNavButtons().forEach((button) => button.classList.remove('active'));
    return;
  }

  const initialPage = getRequestedPage() || getStoredPage() || 'inicio';
  const pageExists = document.getElementById(`page-${initialPage}`);
  const pageId = pageExists ? initialPage : 'inicio';
  showPage(pageId, findContabilidadNavButton(pageId));
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

function filterHistorial(filter, button) {
  document.querySelectorAll('#historial-tabs .tab-btn').forEach((tab) => tab.classList.remove('active'));
  if (button) button.classList.add('active');
  const rows = document.querySelectorAll('#historial-tbody tr[data-status]');
  rows.forEach((row) => {
    const status = row.dataset.status || '';
    row.hidden = !(filter === 'todos' || status === filter);
  });
}

function searchPeriodos(value) {
  const term = (value || '').trim().toLowerCase();
  const rows = document.querySelectorAll('#periodos-tbody tr[data-search]');
  rows.forEach((row) => {
    row.hidden = term && !(row.dataset.search || '').includes(term);
  });
}

function showToast(message, type) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.className = 'toast show';
  if (type) toast.classList.add(`toast-${type}`);
  window.setTimeout(() => toast.classList.remove('show'), 10000);
}

const numberWords = [
  'cero', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho',
  'nueve', 'diez', 'once', 'doce', 'trece', 'catorce', 'quince', 'dieciseis',
  'diecisiete', 'dieciocho', 'diecinueve', 'veinte', 'veintiuno', 'veintidos',
  'veintitres', 'veinticuatro', 'veinticinco', 'veintiseis', 'veintisiete',
  'veintiocho', 'veintinueve',
];
const tensWords = ['', '', '', 'treinta', 'cuarenta', 'cincuenta', 'sesenta', 'setenta', 'ochenta', 'noventa'];
const hundredWords = ['', 'ciento', 'doscientos', 'trescientos', 'cuatrocientos', 'quinientos', 'seiscientos', 'setecientos', 'ochocientos', 'novecientos'];

function numberToSpanishWords(value) {
  const number = Math.trunc(Math.abs(value));
  if (number < 30) return numberWords[number];
  if (number < 100) {
    const ten = Math.trunc(number / 10);
    const unit = number % 10;
    return unit === 0 ? tensWords[ten] : `${tensWords[ten]} y ${numberWords[unit]}`;
  }
  if (number === 100) return 'cien';
  if (number < 1000) {
    const hundred = Math.trunc(number / 100);
    const rest = number % 100;
    return rest === 0 ? hundredWords[hundred] : `${hundredWords[hundred]} ${numberToSpanishWords(rest)}`;
  }
  if (number < 1000000) {
    const thousand = Math.trunc(number / 1000);
    const rest = number % 1000;
    const prefix = thousand === 1 ? 'mil' : `${numberToSpanishWords(thousand)} mil`;
    return rest === 0 ? prefix : `${prefix} ${numberToSpanishWords(rest)}`;
  }
  const million = Math.trunc(number / 1000000);
  const rest = number % 1000000;
  const prefix = million === 1 ? 'un millon' : `${numberToSpanishWords(million)} millones`;
  return rest === 0 ? prefix : `${prefix} ${numberToSpanishWords(rest)}`;
}

function formatMoney(value) {
  return `$ ${Number(value || 0).toLocaleString('es-MX', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function moneyToSpanishText(value) {
  const amount = Math.max(0, Number(value || 0));
  const centsTotal = Math.round(amount * 100);
  const pesos = Math.trunc(centsTotal / 100);
  const cents = centsTotal % 100;
  const pesoLabel = pesos === 1 ? 'peso' : 'pesos';
  return `${numberToSpanishWords(pesos)} ${pesoLabel} ${String(cents).padStart(2, '0')}/100 M.N.`.toUpperCase();
}

function readTotal(selector) {
  const element = document.querySelector(selector);
  if (!element) return 0;
  if (!element.dataset.currentTotal) {
    element.dataset.currentTotal = element.dataset.baseTotal || '0';
  }
  return Number.parseFloat(element.dataset.currentTotal || '0') || 0;
}

function writeTotal(selector, value) {
  const element = document.querySelector(selector);
  if (!element) return;
  element.dataset.currentTotal = String(value);
  element.textContent = formatMoney(value);
}

function updateNominaPreviewTotals(type, amount) {
  const perception = readTotal('[data-total-percepciones]');
  const deduction = readTotal('[data-total-deducciones]');
  const nextPerception = type === 'PERCEPCION' ? perception + amount : perception;
  const nextDeduction = type === 'DEDUCCION' ? deduction + amount : deduction;
  const nextNet = Math.max(0, nextPerception - nextDeduction);

  writeTotal('[data-total-percepciones]', nextPerception);
  writeTotal('[data-total-deducciones]', nextDeduction);
  writeTotal('[data-total-neto]', nextNet);

  const netText = document.querySelector('[data-total-neto-text]');
  if (netText) netText.textContent = moneyToSpanishText(nextNet);
}

function setupNominaConceptForm() {
  const form = document.getElementById('concept-form');
  if (!form) return;
  if (form.method && form.method.toLowerCase() === 'post') return;

  form.addEventListener('submit', (event) => {
    event.preventDefault();

    const typeInput = document.getElementById('concept-type');
    const nameInput = document.getElementById('concept-name');
    const amountInput = document.getElementById('concept-amount');

    const type = typeInput.value;
    const name = nameInput.value.trim();
    const amount = Number.parseFloat(amountInput.value || '0');

    if (!name || !Number.isFinite(amount) || amount <= 0) {
      showToast('Agrega concepto y monto valido.', 'error');
      return;
    }

    const table = document.querySelector(`[data-concept-table="${type}"]`);
    if (!table) return;

    const emptyRow = document.getElementById(type === 'DEDUCCION' ? 'empty-deduccion-row' : 'empty-percepcion-row');
    if (emptyRow) emptyRow.remove();

    const row = document.createElement('div');
    row.className = 'paper-concepts-row';

    const concept = document.createElement('strong');
    concept.textContent = name;

    const amountCell = document.createElement('strong');
    amountCell.className = type === 'DEDUCCION' ? 'amount-neg' : 'amount-pos';
    amountCell.textContent = `$ ${amount.toLocaleString('es-MX', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;

    row.append(concept, amountCell);
    table.append(row);
    updateNominaPreviewTotals(type, amount);
    form.reset();
    showToast('Concepto agregado al preview.', 'success');
  });
}

document.addEventListener('DOMContentLoaded', () => {
  setupContabilidadSidebar();
  setupNominaConceptForm();
});
