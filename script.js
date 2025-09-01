document.addEventListener('DOMContentLoaded', () => {
  const burger = document.querySelector('.burger');
  const nav = document.querySelector('header nav ul');
  const backdrop = document.getElementById('menu-backdrop');
  if (!burger || !nav) return;

  const openMenu = () => {
    nav.classList.add('show');
    document.body.classList.add('menu-open');
    burger.setAttribute('aria-expanded', 'true');
  };
  const closeMenu = () => {
    nav.classList.remove('show');
    document.body.classList.remove('menu-open');
    burger.setAttribute('aria-expanded', 'false');
  };

  burger.addEventListener('click', () => {
    if (nav.classList.contains('show')) closeMenu(); else openMenu();
  });
  backdrop && backdrop.addEventListener('click', closeMenu);
  nav.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });
});