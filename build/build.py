#!/usr/bin/env python3
"""Build crawlable catalog pages from apps.json and the preserved locale shells."""
from datetime import date
from html import escape
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://corvusdevs.github.io'
e = lambda v: escape(str(v), quote=True)

def json_script(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')

def rendered_apps(locale, data):
    locale = {'pt': 'pt-BR', 'zh': 'zh-Hans'}.get(locale, locale)
    translations = ROOT / f'apps.{locale}.json'
    localized = json.loads(translations.read_text()) if translations.exists() else {}
    as_of = date.fromisoformat(data['updated'])
    apps = []
    for original in data['apps']:
        a = dict(original)
        a.update({k: v for k, v in localized.get(a['slug'], {}).items() if k in ('tagline', 'description')})
        a.pop('status', None)
        a['isNew'] = False
        a['isRecent'] = False
        if a.get('appStoreId'):
            a['isNew'] = 0 <= (as_of - date.fromisoformat(a['originalReleaseDate'][:10])).days <= 45
            a['isRecent'] = 0 <= (as_of - date.fromisoformat(a['releaseDate'][:10])).days <= 45
            if a['isNew']:
                a['status'] = 'new'
            elif a['isRecent']:
                a['status'] = 'updated'
        apps.append(a)
    return apps

def build():
    data = json.loads((ROOT / 'apps.json').read_text())
    configs = json.loads((ROOT / 'build/ui.json').read_text())
    for locale, ui in configs.items():
        apps = rendered_apps(locale, data)
        by_slug = {a['slug']: a for a in apps}
        def badge(a):
            return f'<span class="status-badge">{e(ui[a["status"]])}</span>' if a.get('status') else ''
        def link(a):
            return f'<a href="{e(a["url"])}"><img src="{e(a["icon"])}" alt="" loading="lazy"><span>{e(a["name"])}</span></a>'
        rows = []
        for a in apps:
            rows.append(f'<article class="app-row" data-slug="{e(a["slug"])}"><img src="{e(a["icon"])}" alt="" loading="lazy" width="48" height="48"><span><a class="app-name" href="{e(a["url"])}">{e(a["name"])}</a>{badge(a)}</span><span class="app-tag">{e(a["tagline"])}</span><span class="app-platform">{e(" · ".join(a["platforms"]))}</span><span class="app-price">{e(a["price"])}</span><a class="row-action" href="{e(a["store"]["url"] if a.get("appStoreId") else a["url"])}" aria-label="{e(("App Store: " if a.get("appStoreId") else ui["action"] + ": ") + a["name"])}">{e("App Store" if a.get("appStoreId") else ui["action"])}</a></article>')
        families = ''.join(f'<article class="family"><h3>{e(title)}</h3><p>{e(desc)}</p><ul class="family-list">' + ''.join('<li>' + link(a) + '</li>' for a in apps if a['family'] == key) + '</ul></article>' for key, (title, desc) in ui['families'].items())
        featured = [by_slug[s] for s in ['CorvusRecall', 'Stow', 'Corvus-Music-Player', 'Corvus-Player', 'Night-Crow-For-Safari', 'CorvusArcade']]
        icons = ''.join(f'<button aria-label="{e(a["name"])}" aria-pressed="{str(i == 0).lower()}" data-i="{i}"><img src="{e(a["icon"])}" alt="" width="44" height="44"></button>' for i, a in enumerate(featured))
        stories = ''.join(f'<article class="story"><div class="story-media"><img src="{e(a["screenshot"])}" alt="{e(a["name"])}" loading="lazy"></div><div class="story-copy"><span class="section-kicker">{e(" + ".join(a["platforms"]))}</span><h3>{e(a["name"])}</h3><p>{e(a["description"])}</p><a href="{e(a["url"])}">{e(ui["explore"].replace("${a.name}", a["name"]))}</a></div></article>' for a in (by_slug[s] for s in ['CorvusRecall', 'Stow', 'Corvus-Music-Player']))
        recent = sorted((a for a in apps if a.get('appStoreId')), key=lambda a: a['releaseDate'], reverse=True)[:5]
        activity = ''.join(f'<a class="activity-card" href="{e(a["url"])}">{badge(a)}<img src="{e(a["icon"])}" alt="" width="64" height="64" loading="lazy"><strong>{e(a["name"])}</strong><span>{e(a["tagline"])}</span><span>v{e(a["version"])} · <time datetime="{e(a["releaseDate"])}">{e(a["releaseDate"][:10])}</time></span></a>' for a in recent)
        shell = (ROOT / 'build/templates' / f'{locale}.html').read_text()
        shell = shell.replace('--accent:#1674d1', '--accent:#1266ba')
        language = re.search(r'<span class="lang-current">([^<]+)</span>', shell)
        if language:
            shell = shell.replace('<button class="lang-btn" aria-expanded="false">', '<button class="lang-btn" aria-expanded="false" aria-haspopup="true" aria-label="' + e(language[1]) + '">')
        shell = re.sub(r'(<a\b[^>]*href="#apps"[^>]*>[^<]*)17([^<]*</a>)', lambda m: m[1] + str(len(apps)) + m[2], shell)
        first = featured[0]
        shell = re.sub(r'(<img id="shelfShot" )[^>]*>', lambda _: '<img id="shelfShot" src="' + e(first['screenshot']) + '" alt="' + e(first['name']) + '">', shell)
        shell = re.sub(r'(<strong id="shelfName">).*?(</strong>)', lambda m: m[1] + e(first['name']) + m[2], shell)
        shell = re.sub(r'(<span id="shelfMeta">).*?(</span>)', lambda m: m[1] + e(first['tagline']) + m[2], shell)
        for name, content in {'CATALOG': ''.join(rows), 'FAMILIES': families, 'STORIES': stories, 'ACTIVITY': activity, 'SHELFICONS': icons}.items():
            shell = shell.replace('<!-- ' + name + ' -->', content)
        shell = shell.replace('<!-- CATALOG_DATA -->', '<script id="appsData" type="application/json">' + json_script(apps) + '</script>\n<script id="catalogUI" type="application/json">' + json_script({'count': ui['count']}) + '</script>')
        shell = shell.replace('<p id="resultCount" aria-live="polite"></p>', '<p id="resultCount" aria-live="polite">' + e(ui['count'].replace('${count}', str(len(apps)))) + '</p>')
        out = ROOT / ('index.html' if locale == 'en' else f'i18n/{locale}/index.html')
        out.write_text(shell)
    urls = [BASE + '/'] + [BASE + f'/i18n/{locale}/' for locale in configs if locale != 'en'] + [a['url'] for a in data['apps']] + [BASE + '/privacy.html', BASE + '/terms.html']
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(f'  <url><loc>{e(url)}</loc></url>' for url in urls) + '\n</urlset>\n')
    print(f'Built {len(configs)} static pages, {len(apps)} catalog entries each, {len(urls)} sitemap URLs.')

if __name__ == '__main__':
    build()
