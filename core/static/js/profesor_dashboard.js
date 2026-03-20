const breadcrumbs = {
    inicio:      'Inicio',
    recibos:     'Mis Recibos',
    historial:   'Historial de Pagos',
    asistencias: 'Mis Asistencias',
    perfil:      'Mi Perfil',
};
const PAGE_STORAGE_KEY = 'profesor_active_page';

// ── Navegación entre páginas ──────────────────

function getNavButtons() {
    return Array.from(document.querySelectorAll('.nav-item'));
}

function getPageFromButton(btn) {
    if (!btn) return '';
    if (btn.dataset.page) return btn.dataset.page;
    const m = (btn.getAttribute('onclick') || '').match(/showPage\('([^']+)'\)/);
    return m ? m[1] : '';
}

function findNavButton(pageId) {
    return getNavButtons().find(btn => getPageFromButton(btn) === pageId);
}

function saveActivePage(pageId) {
    if (!pageId) return;
    try { localStorage.setItem(PAGE_STORAGE_KEY, pageId); } catch (_) {}
}

function restoreActivePage() {
    let pageId = '';
    try { pageId = localStorage.getItem(PAGE_STORAGE_KEY) || ''; } catch (_) {}
    if (!pageId || !document.getElementById('page-' + pageId)) {
        const defaultBtn = getNavButtons().find(btn => btn.classList.contains('active'));
        pageId = getPageFromButton(defaultBtn) || 'inicio';
    }
    showPage(pageId, findNavButton(pageId));
}

function showPage(id, btn) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const page = document.getElementById('page-' + id);
    if (page) page.classList.add('active');
    if (btn) btn.classList.add('active');
    const crumb = document.getElementById('breadcrumb');
    if (crumb) crumb.innerHTML = '<strong>' + (breadcrumbs[id] || id) + '</strong>';
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.remove('open');
    saveActivePage(id);
}

function actualizarContadores() {
    const tbody = document.getElementById('faltas-tbody');
    if (!tbody) return;

    let faltas = 0, retardos = 0;
    tbody.querySelectorAll('tr[data-estado]').forEach(row => {
        const estado = row.dataset.estado;
        if (estado === 'FALTA')   faltas++;
        if (estado === 'RETARDO') retardos++;
    });

    const el = (id) => document.getElementById(id);
    if (el('stat-faltas'))  el('stat-faltas').textContent  = faltas;
    if (el('stat-retardo')) el('stat-retardo').textContent = retardos;
}


let activeAsistenciaId = null;

function openJustifyModal(asistenciaId, label, estado) {
    activeAsistenciaId = Number(asistenciaId);
    const hidden = document.getElementById('asistencia-id-input');
    if (hidden) hidden.value = String(activeAsistenciaId);

    const title = document.getElementById('modal-title');
    if (title) title.textContent = estado === 'RETARDO' ? 'Justificar retardo' : 'Justificar falta';

    const fechaLabel = document.getElementById('modal-fecha-label');
    if (fechaLabel) fechaLabel.textContent = label || '';

    const motivoSel  = document.getElementById('motivo-select');
    const motivoDesc = document.getElementById('motivo-desc');
    const fileLabel  = document.getElementById('file-label');
    if (motivoSel)  motivoSel.value  = '';
    if (motivoDesc) motivoDesc.value = '';
    if (fileLabel) fileLabel.innerHTML = '<input type="file" id="file-input" accept=".pdf,.jpg,.png" onchange="handleFile(this)">📎 Adjunta un comprobante (PDF, JPG, PNG)';

    const overlay = document.getElementById('modal-overlay');
    if (overlay) overlay.classList.add('open');
}

function closeModal(e) {
    if (e.target === document.getElementById('modal-overlay')) closeModalDirect();
}

function closeModalDirect() {
    const overlay = document.getElementById('modal-overlay');
    if (overlay) overlay.classList.remove('open');
    activeAsistenciaId = null;
    const hidden = document.getElementById('asistencia-id-input');
    if (hidden) hidden.value = '';
}

function handleFile(input) {
    const label = document.getElementById('file-label');
    if (!label) return;
    if (input.files && input.files.length > 0) {
        label.innerHTML = `<input type="file" id="file-input" accept=".pdf,.jpg,.png" onchange="handleFile(this)">✅ <strong>${input.files[0].name}</strong> adjunto`;
    }
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function submitJustificacion() {
    const motivoSel = document.getElementById('motivo-select');
    if (!motivoSel || !motivoSel.value) {
        if (motivoSel) motivoSel.style.borderColor = 'var(--red)';
        showToast('⚠️ Selecciona un motivo para continuar.');
        return;
    }
    motivoSel.style.borderColor = '';

    const desc        = (document.getElementById('motivo-desc')?.value || '').trim();
    const motivoFinal = desc ? `${motivoSel.value}: ${desc}` : motivoSel.value;

    const asistenciaId = activeAsistenciaId
        || Number(document.getElementById('asistencia-id-input')?.value || 0);

    if (!asistenciaId) {
        showToast('⚠️ No se encontró la falta a justificar.');
        return;
    }

    const url = document.getElementById('justificar-url')?.value || '/profesores/justificar-asistencia/';

    const btn = document.getElementById('btn-submit-justif');
    if (btn) { btn.disabled = true; btn.textContent = 'Enviando…'; }

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type':   'application/json',
            'X-CSRFToken':    getCookie('csrftoken') || '',
        },
        body: JSON.stringify({ asistencia_id: asistenciaId, motivo: motivoFinal }),
    })
    .then(async (res) => {
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data.error || 'No se pudo justificar.');
        return data;
    })
    .then(() => {
        closeModalDirect();
        showToast('✅ Justificación enviada correctamente');
        // Refrescar la tabla de faltas sin recargar la página
        setTimeout(() => refreshFaltas(), 350);
    })
    .catch((err) => {
        showToast(err.message || 'Error al enviar la justificación');
    })
    .finally(() => {
        if (btn) { btn.disabled = false; btn.textContent = 'Enviar justificación ›'; }
    });
}


function showToast(msg) {
    const t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3500);
}


function getFaltasStateFromLocation() {
    const params  = new URLSearchParams(window.location.search || '');
    const weekOffset = Math.max(0, Number(params.get('week_offset') || 0) || 0);
    const page       = Math.max(1,  Number(params.get('page')        || 1) || 1);
    return { weekOffset, page };
}

let currentFaltasState = getFaltasStateFromLocation();
let isLoadingFaltas    = false;

function buildUrlWithState(state) {
    const params = new URLSearchParams(window.location.search || '');
    params.delete('partial');
    params.set('week_offset', String(state.weekOffset || 0));
    if ((state.page || 1) > 1) params.set('page', String(state.page));
    else params.delete('page');
    const qs = params.toString();
    return window.location.pathname + (qs ? `?${qs}` : '');
}

function applyFaltasResponse(data) {
    if (!data) return;

    const tbody = document.getElementById('faltas-tbody');
    if (tbody && typeof data.rows_html === 'string') {
        tbody.innerHTML = data.rows_html;
        actualizarContadores(); // recalcular contadores tras actualizar tbody
    }

    const countEl = document.getElementById('faltas-count-total');
    if (countEl && typeof data.count_total === 'number') {
        const n = data.count_total;
        countEl.textContent = `${n} pendiente${n === 1 ? '' : 's'}`;
    }

    const semanaEl  = document.getElementById('faltas-semana-label');
    const periodoEl = document.getElementById('faltas-periodo-label');
    if (semanaEl  && data.semana_inicio && data.semana_fin)
        semanaEl.textContent  = `Semana: ${data.semana_inicio} – ${data.semana_fin}`;
    if (periodoEl && data.periodo_inicio && data.periodo_fin)
        periodoEl.textContent = `Periodo: ${data.periodo_inicio} – ${data.periodo_fin}`;

    const labelEl = document.getElementById('month-label');
    if (labelEl && data.page_number && data.num_pages)
        labelEl.textContent = `Página ${data.page_number} de ${data.num_pages}`;

    const prevBtn = document.getElementById('faltas-page-prev');
    const nextBtn = document.getElementById('faltas-page-next');
    if (prevBtn) prevBtn.disabled = !data.has_previous;
    if (nextBtn) nextBtn.disabled = !data.has_next;

    const prevWeek = document.getElementById('faltas-week-prev');
    const nextWeek = document.getElementById('faltas-week-next');
    if (prevWeek && typeof data.week_offset_prev === 'number') {
        prevWeek.dataset.weekOffset = String(data.week_offset_prev);
        prevWeek.href = `?week_offset=${data.week_offset_prev}`;
        const disable = typeof data.max_week_offset === 'number' && data.week_offset >= data.max_week_offset;
        prevWeek.style.pointerEvents = disable ? 'none' : '';
        prevWeek.style.opacity       = disable ? '0.5'  : '';
    }
    if (nextWeek && typeof data.week_offset_next === 'number') {
        nextWeek.dataset.weekOffset = String(data.week_offset_next);
        nextWeek.href = `?week_offset=${data.week_offset_next}`;
        const disable = data.week_offset === 0;
        nextWeek.style.pointerEvents = disable ? 'none' : '';
        nextWeek.style.opacity       = disable ? '0.5'  : '';
    }

    currentFaltasState = {
        weekOffset: Number(data.week_offset  || 0),
        page:       Number(data.page_number  || 1),
    };
}

function loadFaltas(state, opts = {}) {
    if (isLoadingFaltas) return;
    const options   = { push: true, ...opts };
    const nextState = {
        weekOffset: Math.max(0, Number(state.weekOffset || 0) || 0),
        page:       Math.max(1, Number(state.page        || 1) || 1),
    };
    isLoadingFaltas = true;

    const baseUrl  = buildUrlWithState(nextState);
    const fetchUrl = baseUrl + (baseUrl.includes('?') ? '&' : '?') + 'partial=faltas';

    fetch(fetchUrl, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
    .then(async (res) => {
        const data = await res.json().catch(() => null);
        if (!res.ok) throw new Error((data && data.error) || 'No se pudo cargar la tabla.');
        return data;
    })
    .then((data) => {
        applyFaltasResponse(data);
        if (options.push) {
            const url = buildUrlWithState(currentFaltasState);
            history.pushState({ faltas: currentFaltasState }, '', url);
        }
    })
    .catch((err) => showToast(err.message || 'Error al actualizar'))
    .finally(() => { isLoadingFaltas = false; });
}

function refreshFaltas() {
    loadFaltas(getFaltasStateFromLocation(), { push: false });
}

function changeFaltasPage(dir) {
    const delta = Number(dir || 0) || 0;
    if (!delta) return;
    loadFaltas({ ...currentFaltasState, page: currentFaltasState.page + delta }, { push: true });
}

window.changeFaltasPage = changeFaltasPage;
window.showPage         = showPage;
window.closeModal       = closeModal;
window.closeModalDirect = closeModalDirect;
window.handleFile       = handleFile;
window.submitJustificacion = submitJustificacion;


restoreActivePage();
actualizarContadores();

document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-justificar-btn]');
    const row = btn ? btn.closest('tr[data-asistencia-id]') : e.target.closest('#faltas-table tbody tr[data-asistencia-id]');
    if (!row) return;
    e.preventDefault();
    openJustifyModal(row.dataset.asistenciaId, row.dataset.modalLabel, row.dataset.estado);
});

document.addEventListener('click', (e) => {
    const link = e.target.closest('#faltas-week-prev, #faltas-week-next');
    if (!link) return;
    e.preventDefault();
    const offset = Number(link.dataset.weekOffset || 0) || 0;
    loadFaltas({ weekOffset: offset, page: 1 }, { push: true });
});

document.addEventListener('click', (e) => {
    const link = e.target.closest('#cal-week-prev, #cal-week-next');
    if (!link) return;
    e.preventDefault();
    const offset = Number(link.dataset.weekOffset || 0) || 0;
    loadFaltas({ weekOffset: offset, page: 1 }, { push: true });
});

window.addEventListener('popstate', () => refreshFaltas());
