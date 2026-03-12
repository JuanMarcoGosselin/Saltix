function toggleMenu() {
  const menu = document.getElementById('menu');
  menu.classList.toggle('open');
}

// Cierra el menÃº si el usuario hace clic fuera de la nav
document.addEventListener('click', function (e) {
  const nav = document.querySelector('.navtop');
  if (!nav.contains(e.target)) {
    document.getElementById('menu').classList.remove('open');
  }
});