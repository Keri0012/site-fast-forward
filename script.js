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

// === Header burger interactions ===
document.addEventListener('DOMContentLoaded', () => {
  const burger = document.querySelector('.burger');
  const nav = document.querySelector('header nav ul');
  const backdrop = document.getElementById('menu-backdrop');
  if (burger && nav) {
    const openMenu = () => { nav.classList.add('show'); document.body.classList.add('menu-open'); burger.setAttribute('aria-expanded','true'); };
    const closeMenu = () => { nav.classList.remove('show'); document.body.classList.remove('menu-open'); burger.setAttribute('aria-expanded','false'); };
    burger.addEventListener('click', () => { nav.classList.contains('show') ? closeMenu() : openMenu(); });
    backdrop && backdrop.addEventListener('click', closeMenu);
    nav.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMenu(); });
  }
});


// === Instagram embed fallback: use iframe if embed.js failed ===
window.addEventListener('load', () => {
  const needsFallback = !window.instgrm || !window.instgrm.Embeds;
  if (!needsFallback) { try { window.instgrm.Embeds.process(); } catch(e){} return; }
  document.querySelectorAll('blockquote.instagram-media[data-instgrm-permalink]').forEach(bq => {
    const url = bq.getAttribute('data-instgrm-permalink');
    if (!url) return;
    const iframe = document.createElement('iframe');
    iframe.src = url.replace(/\/?$/, '/') + 'embed';
    iframe.width = '100%';
    iframe.height = '640';
    iframe.setAttribute('frameborder','0');
    iframe.setAttribute('scrolling','no');
    iframe.setAttribute('allowtransparency','true');
    bq.replaceWith(iframe);
  });
});
