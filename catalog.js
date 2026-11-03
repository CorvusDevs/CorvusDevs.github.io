/* Filtering enhances the static catalog; all product links work without JavaScript. */
(() => {
  'use strict';
  const apps = JSON.parse(document.getElementById('appsData').textContent);
  const ui = JSON.parse(document.getElementById('catalogUI').textContent);
  const bySlug = new Map(apps.map(app => [app.slug, app]));
  const rows = [...document.querySelectorAll('#catalog .app-row')];
  const search = document.getElementById('search');
  const clear = document.getElementById('clearSearch');
  const empty = document.getElementById('empty');
  const countLabel = document.getElementById('resultCount');
  let active = 'all';
  function matches(app) {
    if (active === 'all') return true;
    if (active === 'new') return app.isNew;
    if (active === 'updated') return app.isRecent;
    if (active === 'free' || active === 'one-time') return app.purchase === active;
    return app.family === active || app.platforms.includes(active);
  }
  function render() {
    const q = search.value.toLocaleLowerCase().trim();
    let count = 0;
    rows.forEach(row => {
      const app = bySlug.get(row.dataset.slug);
      row.hidden = !matches(app) || !!q && ![app.name, app.tagline, app.description].join(' ').toLocaleLowerCase().includes(q);
      if (!row.hidden) count++;
    });
    empty.style.display = count ? 'none' : 'block';
    countLabel.textContent = ui.count.replace('${count}', count);
    clear.hidden = !q && active === 'all';
  }
  function setFilter(value) {
    active = value;
    document.querySelectorAll('#filters button').forEach(button => button.setAttribute('aria-pressed', button.dataset.filter === active));
    render();
  }
  search.addEventListener('input', render);
  clear.addEventListener('click', () => { search.value = ''; setFilter('all'); search.focus(); });
  document.getElementById('filters').addEventListener('click', event => {
    const button = event.target.closest('button[data-filter]');
    if (button) setFilter(button.dataset.filter);
  });
  const featured = ['CorvusRecall', 'Stow', 'Corvus-Music-Player', 'Corvus-Player', 'Night-Crow-For-Safari', 'CorvusArcade'].map(slug => bySlug.get(slug));
  function showFeatured(i) {
    const app = featured[i];
    const shot = document.getElementById('shelfShot');
    shot.src = app.screenshot || app.icon;
    shot.alt = app.name;
    document.getElementById('shelfName').textContent = app.name;
    document.getElementById('shelfMeta').textContent = app.tagline;
    document.querySelectorAll('#shelfIcons button').forEach((button, n) => button.setAttribute('aria-pressed', n === i));
  }
  document.getElementById('shelfIcons').addEventListener('click', event => {
    const button = event.target.closest('button[data-i]');
    if (button) showFeatured(Number(button.dataset.i));
  });
  showFeatured(0);
  render();
})();
