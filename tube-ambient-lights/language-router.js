/* Corvus Pages language router v2 */
(function () {
  'use strict';
  var current = new URL(location.href);
  var script = document.currentScript;
  if (!script || !script.src) return;
  var siteRoot = new URL('.', script.src).pathname;
  var storageKey = 'corvus-pages-language:' + siteRoot;
  var alternates = new Map();
  document.querySelectorAll('link[rel~="alternate"][hreflang][href]').forEach(function (link) {
    var code = link.getAttribute('hreflang').toLowerCase();
    var target = new URL(link.href, current);
    if (code !== 'x-default' && target.origin === current.origin && target.pathname.startsWith(siteRoot)) {
      alternates.set(code, target);
    }
  });
  if (!alternates.has('en') || alternates.size < 2) return;

  function language(tag) {
    var value = String(tag || '').replace(/_/g, '-').toLowerCase();
    if (alternates.has(value)) return value;
    var parts = value.split('-');
    var base = parts[0];
    if (!base) return null;
    if (base === 'es' && alternates.has('es-419') &&
        parts.some(function (part) {
          return /^(ar|bo|br|bz|cl|co|cr|cu|do|ec|gt|hn|mx|ni|pa|pe|pr|py|sv|us|uy|ve)$/.test(part);
        })) return 'es-419';
    if (base === 'zh') {
      var traditional = parts.some(function (part) { return /^(hant|tw|hk|mo)$/.test(part); });
      var chinese = traditional ? 'zh-hant' : 'zh-hans';
      if (alternates.has(chinese)) return chinese;
    }
    if (base === 'no' && alternates.has('nb')) return 'nb';
    if (alternates.has(base)) return base;
    return Array.from(alternates.keys()).find(function (code) { return code.startsWith(base + '-'); }) || null;
  }

  function stored() {
    try { return language(localStorage.getItem(storageKey)); } catch (_) { return null; }
  }
  function save(value) {
    try {
      if (value === 'auto') localStorage.removeItem(storageKey);
      else localStorage.setItem(storageKey, value);
      return true;
    } catch (_) {
      return false;
    }
  }
  function browser() {
    var wanted = navigator.languages && navigator.languages.length
      ? navigator.languages : [navigator.language];
    for (var i = 0; i < wanted.length; i += 1) {
      var match = language(wanted[i]);
      if (match) return match;
    }
    return 'en';
  }
  function path(url) {
    return url.pathname.replace(/\/index\.html$/i, '/');
  }
  function localized() {
    return Array.from(alternates).some(function (entry) {
      return entry[0] !== 'en' && path(entry[1]) === path(current);
    });
  }
  function navigate(choice, sticky) {
    var target = new URL(alternates.get(choice).href);
    current.searchParams.forEach(function (value, key) {
      if (key !== 'lang') target.searchParams.append(key, value);
    });
    if (sticky) target.searchParams.set('lang', choice);
    target.hash = current.hash;
    if (path(target) !== path(current)) {
      location.replace(target.href);
      return true;
    }
    if (current.searchParams.has('lang') && !sticky) {
      history.replaceState(null, '', current.pathname + target.search + target.hash);
    }
    return false;
  }

  var request = current.searchParams.get('lang');
  if (request === 'auto') {
    save('auto');
    if (navigate(browser(), false)) return;
  } else if (request && language(request)) {
    var choice = language(request);
    if (navigate(choice, !save(choice) && choice === 'en')) return;
  } else if (!localized() && navigate(stored() || browser(), false)) {
    return;
  }

  document.addEventListener('click', function (event) {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    var control = event.target.closest('.lang-menu a[href], .locale-list a[href]');
    if (!control) return;
    var automatic = control.classList.contains('lang-default') || control.dataset.lang === 'auto';
    var value = automatic ? 'auto' : language(control.dataset.lang || control.getAttribute('lang'));
    var link = new URL(control.href, current);
    if (!value) {
      alternates.forEach(function (target, code) {
        if (target.origin === link.origin && path(target) === path(link)) value = code;
      });
    }
    if (!value) return;
    var persisted = save(value);
    if (automatic || (value === 'en' && !persisted)) {
      event.preventDefault();
      event.stopImmediatePropagation();
      var target = new URL(alternates.get('en').href);
      current.searchParams.forEach(function (param, key) {
        if (key !== 'lang') target.searchParams.append(key, param);
      });
      target.hash = current.hash;
      target.searchParams.set('lang', value);
      location.assign(target.href);
    }
  }, true);
})();
