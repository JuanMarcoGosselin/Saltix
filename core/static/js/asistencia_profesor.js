function showAttendanceToast(message) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3000);
}

function markAttendance(button) {
  if (!button || button.classList.contains('is-done')) return;
  button.classList.add('is-done');
  button.textContent = 'Asistencia registrada';
  showAttendanceToast('Asistencia registrada correctamente');

}
function markExit(button) {
  if (!button || button.classList.contains('is-done')) return;
  button.classList.add('is-done');
  button.textContent = 'Salida registrada';
  showAttendanceToast('Salida registrada correctamente');
  
}