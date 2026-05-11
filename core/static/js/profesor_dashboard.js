// Saltix · Dashboard Profesor

const breadcrumbs = {
    inicio: 'Inicio',
    recibos: 'Mis Recibos',
    historial: 'Historial de Pagos',
    asistencias: 'Mis Asistencias',
    perfil: 'Mi Perfil',
};

// Navegación de páginas
function showPage(id, btn) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

    const page = document.getElementById('page-' + id);
    if (page) page.classList.add('active');
    if (btn) btn.classList.add('active');

    const crumb = document.getElementById('breadcrumb');
    if (crumb) crumb.innerHTML = `<strong>${breadcrumbs[id] || id}</strong>`;

    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.remove('open');

    try {
        localStorage.setItem('profesor_active_page', id);
    } catch (_) {}
}

function restoreActivePage() {
    let pageId = '';
    try {
        pageId = localStorage.getItem('profesor_active_page') || '';
    } catch (_) {}

    if (!pageId || !document.getElementById('page-' + pageId)) {
        const defaultBtn = document.querySelector('.nav-item.active');
        const m = defaultBtn?.getAttribute('onclick')?.match(/showPage\('([^']+)'\)/);
        pageId = m ? m[1] : 'inicio';
    }

    const btn = Array.from(document.querySelectorAll('.nav-item'))
        .find(b => {
            const onclick = b.getAttribute('onclick') || '';
            return onclick.includes(`'${pageId}'`) || b.dataset.page === pageId;
        });

    showPage(pageId, btn);
}

// Stats
function aplicarStats(stats) {
    if (!stats) return;
    ['asistencias', 'retardos', 'faltas', 'justificadas'].forEach(key => {
        const el = document.getElementById('stat-' + (key === 'justificadas' ? 'justif' : key.slice(0, -1)));
        if (el) el.textContent = stats[key];
    });
}

// Modal
let activeAsistenciaId = null;

function openJustifyModal(asistenciaId, label) {
    activeAsistenciaId = Number(asistenciaId);

    const hidden = document.getElementById('asistencia-id-input');
    if (hidden) hidden.value = String(activeAsistenciaId);

    const fechaLabel = document.getElementById('modal-fecha-label');
    if (fechaLabel) fechaLabel.textContent = label || '';

    document.getElementById('motivo-select').value = '';
    document.getElementById('motivo-desc').value = '';

    document.getElementById('modal-overlay').classList.add('open');
}

function closeModal(e) {
    if (e.target === document.getElementById('modal-overlay')) {
        closeModalDirect();
    }
}

function closeModalDirect() {
    document.getElementById('modal-overlay').classList.remove('open');
    activeAsistenciaId = null;
    document.getElementById('asistencia-id-input').value = '';
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    return parts.length === 2 ? parts.pop().split(';').shift() : null;
}

function submitJustificacion() {
    const motivoSel = document.getElementById('motivo-select');

    if (!motivoSel.value) {
        motivoSel.style.borderColor = 'var(--red)';
        showToast('⚠️ Selecciona un motivo para continuar.');
        return;
    }

    motivoSel.style.borderColor = '';

    const desc = (document.getElementById('motivo-desc')?.value || '').trim();
    const motivoFinal = desc ? `${motivoSel.value}: ${desc}` : motivoSel.value;

    if (!activeAsistenciaId) {
        showToast('⚠️ No se encontró la falta a justificar.');
        return;
    }

    const url = document.getElementById('justificar-url')?.value || '/profesores/justificar-asistencia/';
    const btn = document.getElementById('btn-submit-justif');

    btn.disabled = true;
    btn.textContent = 'Enviando…';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') || '',
        },
        body: JSON.stringify({
            asistencia_id: activeAsistenciaId,
            motivo: motivoFinal,
        }),
    })
    .then(res => res.json().then(data => ({ ok: res.ok, data })))
    .then(({ ok, data }) => {
	        if (!ok) throw new Error(data.message || data.error || 'No se pudo justificar.');
        closeModalDirect();
        showToast('✅ Justificación enviada correctamente');
        setTimeout(() => refreshFaltas(), 350);
    })
    .catch(err => showToast(err.message || 'Error al enviar la justificación'))
    .finally(() => {
        btn.disabled = false;
        btn.textContent = 'Enviar justificación ›';
    });
}

// Toast
function showToast(msg) {
    const t = document.getElementById('toast');
    if (!t) return;
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3500);
}

// Navegación de semanas
let currentWeekOffset = 0;
let isLoadingFaltas = false;

function clampWeekOffset(value) {
    return Math.max(-1, Math.min(window.MAX_WEEK_OFFSET ?? 0, Number(value || 0)));
}

function applyFaltasResponse(data) {
    if (!data) return;

    const tbody = document.getElementById('faltas-tbody');
    if (tbody && data.rows_html) tbody.innerHTML = data.rows_html;

    aplicarStats(data.stats);

    const horarioTbody = document.getElementById('horario-tbody');
    if (horarioTbody && data.horario_html) horarioTbody.innerHTML = data.horario_html;

    const calLabel = document.querySelector('.month-selector .month-label');
    if (calLabel && data.semana_inicio && data.semana_fin) {
        calLabel.textContent = `Semana del ${data.semana_inicio} al ${data.semana_fin}`;
    }

    // Botones prev/next
    const calPrev = document.getElementById('cal-week-prev');
    if (calPrev) {
        calPrev.dataset.weekOffset = data.week_offset_prev;
        calPrev.href = `?week_offset=${data.week_offset_prev}`;
        const disable = data.week_offset_prev < -1;
        calPrev.style.pointerEvents = disable ? 'none' : '';
        calPrev.style.opacity = disable ? '0.4' : '';
    }

    const calNext = document.getElementById('cal-week-next');
    if (calNext) {
        calNext.dataset.weekOffset = data.week_offset_next;
        calNext.href = `?week_offset=${data.week_offset_next}`;
        const disable = data.week_offset_next > data.max_week_offset;
        calNext.style.pointerEvents = disable ? 'none' : '';
        calNext.style.opacity = disable ? '0.4' : '';
    }

    currentWeekOffset = data.week_offset;
    if (data.max_week_offset !== undefined) window.MAX_WEEK_OFFSET = data.max_week_offset;
}

function loadFaltas(weekOffset, pushState = true) {
    if (isLoadingFaltas) return;

    const offset = clampWeekOffset(weekOffset);
    isLoadingFaltas = true;

    const url = `${window.location.pathname}?week_offset=${offset}&partial=faltas`;

    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(res => res.json().then(data => ({ ok: res.ok, data })))
        .then(({ ok, data }) => {
	            if (!ok) throw new Error(data.message || data.error || 'No se pudo cargar.');
            applyFaltasResponse(data);
            if (pushState) {
                history.pushState({ weekOffset: offset }, '', `?week_offset=${offset}`);
            }
        })
        .catch(err => showToast(err.message || 'Error al actualizar'))
        .finally(() => isLoadingFaltas = false);
}

function refreshFaltas() {
    const params = new URLSearchParams(window.location.search);
    loadFaltas(params.get('week_offset') || 0, false);
}

// Exponer globales
window.showPage = showPage;
window.closeModal = closeModal;
window.closeModalDirect = closeModalDirect;
window.submitJustificacion = submitJustificacion;

// Init
restoreActivePage();

// Event listeners
document.addEventListener('click', (e) => {
    // Modal justificar
    const row = e.target.closest('#faltas-table tbody tr[data-asistencia-id]');
    if (row) {
        e.preventDefault();
        if (row.dataset.incidenciaPendiente === '1') {
            showToast('Ya existe una justificación en revisión para este registro.');
            return;
        }
        openJustifyModal(row.dataset.asistenciaId, row.dataset.modalLabel);
        return;
    }

    // Navegación semanas
    const link = e.target.closest('#cal-week-prev, #cal-week-next');
    if (link) {
        e.preventDefault();
        loadFaltas(Number(link.dataset.weekOffset || 0));
    }
});

window.addEventListener('popstate', () => refreshFaltas());
