(() => {
  const view = document.querySelector('.compare');
  const slider = document.getElementById('split');
  const menu = document.querySelector('.locale');
  document.addEventListener('click', event => {
    if (menu?.open && !menu.contains(event.target)) menu.open = false;
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu?.open) {
      menu.open = false;
      menu.querySelector('summary').focus();
    }
  });
  if (!view || !slider) return;
  const buttons = [...document.querySelectorAll('.preset button')];
  const seam = view.querySelector('.seam');
  const [left, right] = view.querySelectorAll('.scene-label');
  const percent = new Intl.NumberFormat(document.documentElement.lang, {style: 'percent'});
  function render() {
    const n = Number(slider.value);
    view.style.setProperty('--split', n + '%');
    slider.setAttribute('aria-valuetext', n === 100 ? left.textContent : n === 0 ? right.textContent : percent.format((100-n)/100) + ' · ' + right.textContent);
    seam.hidden = n === 0 || n === 100;
    left.hidden = n < 17;
    right.hidden = n > 83;
    buttons.forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.value) === n)));
  }
  function slide(event) {
    const rect = view.getBoundingClientRect();
    slider.value = Math.round(Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width)) * 100);
    render();
  }
  view.addEventListener('pointerdown', event => {
    if (event.button !== 0) return;
    view.setPointerCapture(event.pointerId);
    slide(event);
  });
  view.addEventListener('pointermove', event => {
    if (view.hasPointerCapture(event.pointerId)) slide(event);
  });
  view.addEventListener('dragstart', event => event.preventDefault());
  slider.addEventListener('input', render);
  buttons.forEach(button => button.addEventListener('click', () => {
    slider.value = button.dataset.value;
    render();
  }));
  slider.closest('.demo-inputs').hidden = false;
  view.classList.add('interactive');
  render();
})();
