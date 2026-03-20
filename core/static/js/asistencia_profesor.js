function getCSRFToken() {
    const match = document.cookie
        .split('; ')
        .find(c => c.startsWith('csrftoken='));
    return match ? match.split('=')[1] : null;
}

function showAttendanceToast(message, type) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.className   = 'toast show' + (type ? ' toast-' + type : '');
    setTimeout(() => toast.classList.remove('show'), 3500);
}

function handleAsistencia(button) {
    if (!button || button.disabled || button.classList.contains('is-done')) return;

    button.disabled = true;

    const url      = button.dataset.url;
    const horarioId = button.dataset.horario;

    if (!url || !horarioId) {
        showAttendanceToast('Error: datos del botón incompletos.', 'error');
        button.disabled = false;
        return;
    }

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken':  getCSRFToken(),
        },
        body: JSON.stringify({ horario_id: horarioId }),
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            showAttendanceToast(data.error, 'error');
            button.disabled = false;
            return;
        }

        if (data.tipo === 'entrada') {
          const esRetardo = data.estado === 'RETARDO';
            button.textContent = 'Registrar salida';
            button.classList.remove('is-done');
            button.disabled    = false;
            button.dataset.accion = 'salida';

            if (esRetardo) {
                showAttendanceToast('⚠️ Entrada registrada con retardo', 'error');

                const item = button.closest('.schedule-item');
                if (item) item.classList.add('is-retardo');
            } else {
                showAttendanceToast(data.message || 'Asistencia registrada', 'success');
            }
        } else if (data.tipo === 'salida') {
            button.textContent = '✓ Asistencia registrada';
            button.classList.add('is-done');
            button.disabled    = true;
            showAttendanceToast(data.message || 'Salida registrada', 'success');
        }
    })
    .catch(() => {
        showAttendanceToast('Error del servidor. Intenta de nuevo.', 'error');
        button.disabled = false;
    });
}
