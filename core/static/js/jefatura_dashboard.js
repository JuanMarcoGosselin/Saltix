const breadcrumbs = {
  equipo: 'Mi equipo',
  asistencia: 'Asistencia',
  solicitudes: 'Solicitudes',
  reportes: 'Reportes'
};

let pendientes = 0;
let asistenciaPage = 1;
let asistenciaHasNext = false;
let asistenciaHasPrev = false;
let incidenciaPage = 1;
let incidenciaHasNext = false;
let incidenciaHasPrev = false;

function getInputValue(id) {
  const node = document.getElementById(id);
  return node ? node.value : '';
}

function getUrl(id) {
  return getInputValue(id);
}

function getCSRFToken() {
  const cookie = document.cookie.split(';').map(item => item.trim()).find(item => item.startsWith('csrftoken='));
  return cookie ? decodeURIComponent(cookie.split('=')[1]) : '';
}

function showToast(message, isError = false) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.style.background = isError ? '#c0392b' : '#1f8f5f';
  toast.classList.add('visible');
  setTimeout(() => toast.classList.remove('visible'), 2500);
}

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
  if (e.key === 'Escape') {
    closeSidebar();
    closeCorrectionModalDirect();
    closeAllHorarioModals();
  }
});

function syncSolicitudesUI() {
  const badge = document.getElementById('badge-sol');
  const cardBadge = document.getElementById('card-sol-badge');
  const cardVal = document.getElementById('card-sol-val');
  const subtitle = document.getElementById('sol-subtitle');

  if (badge) {
    badge.style.display = pendientes > 0 ? 'inline-flex' : 'none';
    badge.textContent = pendientes;
  }
  if (cardBadge) {
    cardBadge.style.display = pendientes > 0 ? 'inline-block' : 'none';
    cardBadge.textContent = pendientes;
  }
  if (cardVal) cardVal.textContent = pendientes;
  if (subtitle) {
    subtitle.textContent = pendientes > 0
      ? (pendientes + ' solicitud' + (pendientes > 1 ? 'es' : '') + ' esperan tu aprobacion')
      : 'Sin solicitudes pendientes';
  }
}

function asistenciaFilters(page = 1) {
  const params = new URLSearchParams();
  params.set('page', page);
  params.set('page_size', 10);

  const profesorId = getInputValue('filtro-asistencia-profesor');
  const fechaInicio = getInputValue('filtro-asistencia-inicio');
  const fechaFin = getInputValue('filtro-asistencia-fin');
  const estado = getInputValue('filtro-asistencia-estado');

  if (profesorId) params.set('profesor_id', profesorId);
  if (fechaInicio) params.set('fecha_inicio', fechaInicio);
  if (fechaFin) params.set('fecha_fin', fechaFin);
  if (estado) params.set('estado', estado);
  return params.toString();
}

function incidenciaFilters(page = 1) {
  const params = new URLSearchParams();
  params.set('page', page);
  params.set('page_size', 10);

  const profesorId = getInputValue('filtro-incidencia-profesor');
  const fechaInicio = getInputValue('filtro-incidencia-inicio');
  const fechaFin = getInputValue('filtro-incidencia-fin');
  const estado = getInputValue('filtro-incidencia-estado');

  if (profesorId) params.set('profesor_id', profesorId);
  if (fechaInicio) params.set('fecha_inicio', fechaInicio);
  if (fechaFin) params.set('fecha_fin', fechaFin);
  if (estado) params.set('estado', estado);
  return params.toString();
}

function estadoPillClass(estado) {
  if (estado === 'JUSTIFICADA' || estado === 'APROBADA') return 'pill-blue';
  if (estado === 'FALTA' || estado === 'RECHAZADA') return 'pill-red';
  if (estado === 'RETARDO' || estado === 'PENDIENTE') return 'pill-yellow';
  if (estado === 'CANCELADA') return 'pill-gray';
  return 'pill-green';
}

function renderAsistencias(results) {
  const tbody = document.getElementById('tabla-asistencias-body');
  if (!tbody) return;
  if (!results.length) {
    tbody.innerHTML = '<tr><td colspan="6">Sin registros de asistencia.</td></tr>';
    return;
  }
  tbody.innerHTML = results.map(item => `
    <tr data-asistencia-id="${item.id}">
      <td>${item.profesor_nombre}</td>
      <td>${item.fecha.split('-').reverse().join('/')}</td>
      <td>${item.horario || '-'}</td>
      <td><span class="pill ${estadoPillClass(item.estado)}">${item.estado_label}</span></td>
      <td>${item.observaciones || '-'}</td>
      <td class="actions-cell">
        <button class="btn-outline btn-sm" type="button" onclick="abrirModalCorreccion(${item.id}, '${item.estado}', ${JSON.stringify(item.observaciones || '')})">Corregir</button>
        ${item.cancelada_institucional ? '' : `<button class="btn-primary btn-sm" type="button" onclick="cancelarAsistencia(${item.id})">Cancelar</button>`}
      </td>
    </tr>
  `).join('');
}

function renderIncidencias(results) {
  const tbody = document.getElementById('tabla-incidencias-body');
  if (!tbody) return;
  if (!results.length) {
    tbody.innerHTML = '<tr><td colspan="6">No hay solicitudes por revisar.</td></tr>';
    return;
  }
  tbody.innerHTML = results.map(item => `
    <tr data-incidencia-id="${item.id}">
      <td>${item.profesor_nombre}</td>
      <td>${item.fecha_ausencia.split('-').reverse().join('/')}</td>
      <td>${item.tipo_label}</td>
      <td>${item.motivo}</td>
      <td><span class="pill ${estadoPillClass(item.estado)}">${item.estado_label}</span></td>
      <td class="actions-cell">
        ${item.estado === 'PENDIENTE'
          ? `<button class="btn-approve" type="button" onclick="resolverSolicitud(${item.id}, 'aprobar')">Aprobar</button>
             <button class="btn-reject" type="button" onclick="resolverSolicitud(${item.id}, 'rechazar')">Rechazar</button>`
          : '<span class="table-subtitle">Resuelta</span>'}
      </td>
    </tr>
  `).join('');
}

async function cargarAsistencias(page = 1) {
  const url = `${getUrl('url-listar-asistencias')}?${asistenciaFilters(page)}`;
  const response = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
  const data = await response.json();
  if (!response.ok || !data.ok) {
    showToast(data.message || data.error || 'No se pudieron cargar las asistencias.', true);
    return;
  }
  asistenciaPage = data.page;
  asistenciaHasNext = data.has_next;
  asistenciaHasPrev = data.has_prev;
  renderAsistencias(data.results);
  document.getElementById('asistencias-page-label').textContent = `Pagina ${data.page}`;
  document.getElementById('asistencias-prev').disabled = !data.has_prev;
  document.getElementById('asistencias-next').disabled = !data.has_next;
}

async function cargarIncidencias(page = 1) {
  const url = `${getUrl('url-listar-incidencias')}?${incidenciaFilters(page)}`;
  const response = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
  const data = await response.json();
  if (!response.ok || !data.ok) {
    showToast(data.message || data.error || 'No se pudieron cargar las incidencias.', true);
    return;
  }
  incidenciaPage = data.page;
  incidenciaHasNext = data.has_next;
  incidenciaHasPrev = data.has_prev;
  pendientes = typeof data.pending_total === 'number'
    ? data.pending_total
    : data.results.filter(item => item.estado === 'PENDIENTE').length;
  renderIncidencias(data.results);
  document.getElementById('incidencias-page-label').textContent = `Pagina ${data.page}`;
  document.getElementById('incidencias-prev').disabled = !data.has_prev;
  document.getElementById('incidencias-next').disabled = !data.has_next;
  syncSolicitudesUI();
}

function cambiarPaginaAsistencias(direction) {
  const nextPage = direction < 0 ? asistenciaPage - 1 : asistenciaPage + 1;
  if (nextPage < 1) return;
  if (direction < 0 && !asistenciaHasPrev) return;
  if (direction > 0 && !asistenciaHasNext) return;
  cargarAsistencias(nextPage);
}

function cambiarPaginaIncidencias(direction) {
  const nextPage = direction < 0 ? incidenciaPage - 1 : incidenciaPage + 1;
  if (nextPage < 1) return;
  if (direction < 0 && !incidenciaHasPrev) return;
  if (direction > 0 && !incidenciaHasNext) return;
  cargarIncidencias(nextPage);
}

async function postJSON(url, payload) {
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken(),
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: JSON.stringify(payload)
  });
  const contentType = response.headers.get('content-type') || '';
  if (!contentType.includes('application/json')) {
    throw new Error('El servidor devolvio una respuesta inesperada. Recarga la pagina e intenta de nuevo.');
  }
  const data = await response.json();
  if (!response.ok || !data.ok) {
    throw new Error(data.message || data.error || 'Operacion no completada.');
  }
  return data;
}

async function resolverSolicitud(incidenciaId, accion) {
  const url = accion === 'aprobar' ? getUrl('url-aprobar-incidencia') : getUrl('url-rechazar-incidencia');
  try {
    await postJSON(url, { incidencia_id: incidenciaId });
    const message = accion === 'aprobar' ? 'Solicitud aprobada correctamente.' : 'Solicitud rechazada correctamente.';
    window.location.href = `?page=solicitudes&ok=${encodeURIComponent(message)}`;
  } catch (error) {
    showToast(error.message, true);
  }
}

async function cancelarAsistencia(asistenciaId) {
  try {
    await postJSON(getUrl('url-cancelar-asistencia'), { asistencia_id: asistenciaId });
    showToast('Asistencia cancelada institucionalmente.');
    await cargarAsistencias(asistenciaPage);
  } catch (error) {
    showToast(error.message, true);
  }
}

function abrirModalCorreccion(asistenciaId, estado, observaciones) {
  document.getElementById('correccion-asistencia-id').value = asistenciaId;
  document.getElementById('correccion-estado').value = estado === 'CANCELADA' ? 'FALTA' : estado;
  document.getElementById('correccion-observaciones').value = observaciones || '';
  document.getElementById('correccion-modal').classList.add('visible');
}

function closeCorrectionModal(event) {
  if (event.target.id === 'correccion-modal') {
    closeCorrectionModalDirect();
  }
}

function closeCorrectionModalDirect() {
  const modal = document.getElementById('correccion-modal');
  if (modal) modal.classList.remove('visible');
}

function openHorarioModal(profesorId) {
  const modal = document.getElementById('horario-modal-' + profesorId);
  if (modal) modal.classList.add('visible');
}

function closeHorarioModal(event, profesorId) {
  if (event.target.id === 'horario-modal-' + profesorId) {
    closeHorarioModalDirect(profesorId);
  }
}

function closeHorarioModalDirect(profesorId) {
  const modal = document.getElementById('horario-modal-' + profesorId);
  if (modal) modal.classList.remove('visible');
}

function closeAllHorarioModals() {
  document.querySelectorAll('[id^="horario-modal-"]').forEach(modal => {
    modal.classList.remove('visible');
  });
}

async function guardarCorreccion() {
  const asistenciaId = parseInt(document.getElementById('correccion-asistencia-id').value, 10);
  const estado = document.getElementById('correccion-estado').value;
  const observaciones = document.getElementById('correccion-observaciones').value;
  try {
    await postJSON(getUrl('url-corregir-asistencia'), {
      asistencia_id: asistenciaId,
      estado,
      observaciones
    });
    closeCorrectionModalDirect();
    showToast('Asistencia corregida correctamente.');
    await cargarAsistencias(asistenciaPage);
  } catch (error) {
    showToast(error.message, true);
  }
}

document.addEventListener('DOMContentLoaded', function() {
  pendientes = parseInt((document.getElementById('card-sol-val')?.textContent || '0').trim(), 10) || 0;
  syncSolicitudesUI();
  const asistenciasPrev = document.getElementById('asistencias-prev');
  const incidenciasPrev = document.getElementById('incidencias-prev');
  if (asistenciasPrev) asistenciasPrev.disabled = true;
  if (incidenciasPrev) incidenciasPrev.disabled = true;
  if (window.SALTIX_INITIAL_PAGE && window.SALTIX_INITIAL_PAGE !== 'equipo') {
    const navButton = Array.from(document.querySelectorAll('.nav-item')).find(btn =>
      (btn.getAttribute('onclick') || '').includes("'" + window.SALTIX_INITIAL_PAGE + "'")
    );
    showPage(window.SALTIX_INITIAL_PAGE, navButton);
  }
});
