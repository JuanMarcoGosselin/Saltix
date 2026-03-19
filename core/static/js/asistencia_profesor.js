function getCSRFToken() {
  let cookieValue = null;

  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');

    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();

      if (cookie.startsWith('csrftoken=')) {
        cookieValue = cookie.substring('csrftoken='.length);
        break;
      }
    }
  }

  return cookieValue;
}

function showAttendanceToast(message) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3000);
}

function handleAsistencia(button) {
  if (!button || button.classList.contains('is-done')) return;

  button.disabled = true;

  const url = button.dataset.url;
  const horarioId = button.dataset.horario;

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken()
    },
    body: JSON.stringify({
      horario_id: horarioId
    })
  })
  .then(res => res.json())
  .then(data => {

    if (data.error) {
      showAttendanceToast(data.error, 'error');
      button.disabled = false;
      return;
    }

    if (data.tipo === 'entrada') {
      button.textContent = 'Registrar salida';
      button.classList.remove('is-done');
    }

    else if (data.tipo === 'salida') {
      button.textContent = 'Salida registrada';
      button.classList.add('is-done');
    }

    showAttendanceToast(data.message, 'success');
  })
  .catch(() => {
    showAttendanceToast('Error del servidor', 'error');
    button.disabled = false;
  });
}