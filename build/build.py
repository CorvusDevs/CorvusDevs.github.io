#!/usr/bin/env python3
"""Build crawlable catalog pages from apps.json and the preserved locale shells."""
from datetime import date
from html import escape
from pathlib import Path
from string import Template
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
    improvements = json.loads((ROOT / 'build/improvement-ui.json').read_text())
    for locale, ui in configs.items():
        ui = dict(ui)
        extra = improvements[locale]
        ui['families'] = dict(ui['families'])
        ui['families']['media-play'] = [extra['mediaTitle'], extra['mediaDescription']]
        ui['families']['better-mac'] = [extra['toolsTitle'], extra['toolsDescription']]
        shell = (ROOT / 'build/templates' / f'{locale}.html').read_text()
        # The searchable catalog is the first destination after the hero.
        sections = re.findall(r'<section\b[^>]*>(?:(?!<section\b).)*?</section>', shell, re.S)
        catalog_section = next(section for section in sections if '<!-- CATALOG -->' in section)
        family_section = next(section for section in sections if '<!-- FAMILIES -->' in section)
        family_section_new = family_section.replace('id="apps"', 'id="families-section"')
        family_section_new = re.sub(r'<p class="section-intro">.*?</p>', '', family_section_new, count=1, flags=re.S)
        shell = shell.replace(family_section, family_section_new).replace(catalog_section, '')
        catalog_section = catalog_section.replace('<section class="section">', '<section class="section" id="apps">', 1)
        shell = shell.replace('</section>', '</section>\n' + catalog_section, 1)
        shell = re.sub(r'(<p class="hero-copy">).*?(</p>)', lambda m: m[1] + e(extra['heroIntro']) + m[2], shell, count=1, flags=re.S)
        story_section = next(section for section in sections if '<!-- STORIES -->' in section)
        story_new = re.sub(r'(<p class="section-intro">).*?(</p>)', lambda m: m[1] + e(extra['storiesIntro']) + m[2], story_section, count=1, flags=re.S)
        shell = shell.replace(story_section, story_new)
        # Keep the caption outside the picture, so it cannot obscure app controls.
        shell = re.sub(r'(<div class="shelf-screen">)(<img[^>]+>)(<div class="shelf-caption">.*?</div>)(</div>)', lambda m: m[1] + m[2] + m[4] + m[3], shell, count=1, flags=re.S)
        shell = shell.replace('</head>', '<link rel="stylesheet" href="/catalog-layout.css">\n</head>', 1)
        one_time = re.search(r'data-filter="one-time"[^>]*>([^<]+)</button>', shell)[1]
        free = re.search(r'data-filter="free"[^>]*>([^<]+)</button>', shell)[1]
        apps = rendered_apps(locale, data)
        by_slug = {a['slug']: a for a in apps}
        def badge(a):
            return f'<span class="status-badge">{e(ui[a["status"]])}</span>' if a.get('status') else ''
        def link(a):
            return f'<a href="{e(a["url"])}"><img src="{e(a["icon"])}" alt="" loading="lazy"><span>{e(a["name"])}</span></a>'
        rows = []
        for a in apps:
            model = one_time if a.get('appStoreId') else free if a['price'] == 'Free' else extra['trial'] if a['price'] == 'Free trial' else a['price']
            rows.append(f'<article class="app-row" data-slug="{e(a["slug"])}"><img src="{e(a["icon"])}" alt="" loading="lazy" width="48" height="48"><span><a class="app-name" href="{e(a["url"])}">{e(a["name"])}</a>{badge(a)}</span><span class="app-tag">{e(a["tagline"])}</span><span class="app-platform">{e(" · ".join(a["platforms"]))}</span><span class="app-price">{e(model)}</span><a class="row-action" href="{e(a["store"]["url"] if a.get("appStoreId") else a["url"])}" aria-label="{e(("App Store: " if a.get("appStoreId") else ui["action"] + ": ") + a["name"])}">{e("App Store" if a.get("appStoreId") else ui["action"])}</a></article>')
        families = ''.join(f'<article class="family"><h3 id="family-{e(key)}">{e(title)}</h3><p>{e(desc)}</p><details class="family-list-disclosure"><summary aria-describedby="family-{e(key)}">{e(extra["browseApps"])}</summary><ul class="family-list">' + ''.join('<li>' + link(a) + '</li>' for a in apps if a['family'] == key) + '</ul></details></article>' for key, (title, desc) in ui['families'].items())
        featured = [by_slug[s] for s in ['CorvusRecall', 'Stow', 'Corvus-Music-Player', 'Corvus-Player', 'Night-Crow-For-Safari', 'CorvusArcade']]
        icons = ''.join(f'<button aria-label="{e(a["name"])}" aria-pressed="{str(i == 0).lower()}" data-i="{i}"><img src="{e(a["icon"])}" alt="" width="44" height="44"></button>' for i, a in enumerate(featured))
        stories = ''.join(f'<article class="story"><div class="story-media"><img src="{e(a["screenshot"])}" alt="{e(a["name"])}" loading="lazy"></div><div class="story-copy"><span class="section-kicker">{e(" + ".join(a["platforms"]))}</span><h3>{e(a["name"])}</h3><p>{e(a["description"])}</p><a href="{e(a["url"])}">{e(ui["explore"].replace("${a.name}", a["name"]))}</a></div></article>' for a in (by_slug[s] for s in ['CorvusRecall', 'Stow', 'Corvus-Music-Player']))
        recent = sorted((a for a in apps if a.get('appStoreId')), key=lambda a: a['releaseDate'], reverse=True)[:5]
        activity = ''.join(f'<a class="activity-card" href="{e(a["url"])}">{badge(a)}<img src="{e(a["icon"])}" alt="" width="64" height="64" loading="lazy"><strong>{e(a["name"])}</strong><span>{e(a["tagline"])}</span><span>v{e(a["version"])} · <time datetime="{e(a["releaseDate"])}">{e(a["releaseDate"][:10])}</time></span></a>' for a in recent)
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
        shell = add_projects(shell, locale)
        out = ROOT / ('index.html' if locale == 'en' else f'i18n/{locale}/index.html')
        out.write_text(shell)
    urls = [BASE + '/'] + [BASE + f'/i18n/{locale}/' for locale in configs if locale != 'en'] + [a['url'] for a in data['apps']] + [BASE + '/privacy.html', BASE + '/terms.html'] + build_case_studies()
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(f'  <url><loc>{e(url)}</loc></url>' for url in urls) + '\n</urlset>\n')
    print(f'Built {len(configs)} static pages, {len(apps)} catalog entries each, {len(urls)} sitemap URLs.')

PUBLIC_SITE = 'https://aletea.org/'
CASE = {'en': '/i18n/en/projects/aletea/', 'es': '/i18n/es/projects/aletea/'}
COPY = {
    'en': {
        'home': '/', 'nav': 'Projects', 'home_kicker': 'Selected work',
        'home_intro': 'A look at work beyond our apps.',
        'card_title': 'Aletea',
        'card_text': 'A public website and an internal coordination tool for an Uruguayan civil association working alongside autistic people and their families.',
        'read_case': 'Read the case study', 'title': 'Aletea: a public website and an internal coordination tool',
        'description': 'A CorvusDevs case study in design and development with Aletea, from finding information to following up on a request.',
        'lang_menu': 'Language', 'lang_name': 'English', 'work': 'Case study · Uruguay',
        'headline': 'From finding help to following through.',
        'intro': 'Two connected projects for Aletea: a public website that helps people find where to start, and an internal tool that helps the team carry requests forward.',
        'website_cta': 'Visit the public website', 'role': 'Role',
        'role_detail': 'Experience design and development', 'collaboration': 'Collaboration',
        'collaboration_detail': 'With the Aletea team', 'public': '01 / Public website',
        'public_title': 'Give people a clear starting point.',
        'public_text': 'We organized the site around what visitors come to do: find guidance, check the agenda, or explore resources. People can start with a question without needing to know how the association is organized.',
        'links_title': 'Three routes into the site',
        'guide': 'Guidance', 'guide_text': 'Find the right way to get in touch.',
        'agenda': 'Agenda', 'agenda_text': 'See activities and dates in one place.',
        'resources': 'Resources', 'resources_text': 'Find guides and practical materials.',
        'internal': '02 / Internal coordination',
        'internal_title': 'Keep the next step visible.',
        'internal_text': 'The internal tool gives the team a place to receive requests, assign responsibility and record what happens next.',
        'demo': 'Illustrative demo · Fictional data',
        'demo_id': 'Example 01', 'demo_title': 'Question about joining an activity',
        'intake': 'Received', 'intake_text': 'A request arrives through a form.',
        'assign': 'Assigned', 'assign_text': 'The activities team takes responsibility.',
        'follow': 'Follow-up', 'follow_text': 'The next step is recorded for the team.',
        'demo_note': 'This is a simplified illustration, not a capture of the internal system. No real records are shown.',
        'credit': 'Design and development by CorvusDevs, in collaboration with the Aletea team. The team brought its day-to-day work and feedback to the design.',
        'back': 'Back to projects',
    },
    'es': {
        'home': '/i18n/es/', 'nav': 'Proyectos', 'home_kicker': 'Trabajos seleccionados',
        'home_intro': 'Una mirada a nuestro trabajo más allá de las apps.',
        'card_title': 'Aletea',
        'card_text': 'Un sitio público y un gestor interno para una asociación civil uruguaya que trabaja junto a personas autistas y sus familias.',
        'read_case': 'Ver el caso de estudio', 'title': 'Aletea: sitio público y gestor interno',
        'description': 'Un caso de diseño y desarrollo de CorvusDevs junto a Aletea, desde encontrar información hasta dar seguimiento a una consulta.',
        'lang_menu': 'Idioma', 'lang_name': 'Español', 'work': 'Caso de estudio · Uruguay',
        'headline': 'De encontrar orientación a dar seguimiento.',
        'intro': 'Dos proyectos conectados para Aletea: un sitio público que ayuda a encontrar por dónde empezar y un gestor interno que ayuda al equipo a dar curso a las consultas.',
        'website_cta': 'Visitar el sitio público', 'role': 'Rol',
        'role_detail': 'Diseño de experiencia y desarrollo', 'collaboration': 'Colaboración',
        'collaboration_detail': 'Con el equipo de Aletea', 'public': '01 / Sitio público',
        'public_title': 'Un punto de partida claro.',
        'public_text': 'Organizamos el sitio según lo que las personas necesitan hacer: pedir orientación, consultar la agenda o buscar recursos. Se puede empezar con una pregunta sin tener que conocer la estructura de la asociación.',
        'links_title': 'Tres entradas al sitio',
        'guide': 'Orientación', 'guide_text': 'Encontrá el canal adecuado para tu consulta.',
        'agenda': 'Agenda', 'agenda_text': 'Consultá las actividades y fechas en un solo lugar.',
        'resources': 'Recursos', 'resources_text': 'Encontrá guías y materiales prácticos.',
        'internal': '02 / Gestión interna',
        'internal_title': 'Que el próximo paso quede claro.',
        'internal_text': 'El gestor le da al equipo un lugar para recibir consultas, asignar responsabilidades y registrar qué sigue.',
        'demo': 'Demo ilustrativa · Datos ficticios',
        'demo_id': 'Ejemplo 01', 'demo_title': 'Consulta para participar en una actividad',
        'intake': 'Recibida', 'intake_text': 'La consulta llega por un formulario.',
        'assign': 'Asignada', 'assign_text': 'El equipo de actividades toma la consulta.',
        'follow': 'Seguimiento', 'follow_text': 'El equipo registra el próximo paso.',
        'demo_note': 'Es una ilustración simplificada, no una captura del gestor interno. No muestra registros reales.',
        'credit': 'Diseño y desarrollo de CorvusDevs, en colaboración con el equipo de Aletea, que aportó su experiencia cotidiana y devoluciones al diseño.',
        'back': 'Volver a proyectos',
    },
}


def add_projects(shell, locale):
    if locale not in COPY:
        return shell
    c = {k: e(v) for k, v in COPY[locale].items()}
    about = '<li><a href="#principles">'
    section = '<section class="section" id="principles">'
    assert shell.count(about) == shell.count(section) == 1
    shell = shell.replace(about, f'<li><a href="#projects">{c["nav"]}</a></li>' + about, 1)
    shell = shell.replace('</head>', '<link rel="stylesheet" href="/i18n/en/projects/aletea/portfolio.css">\n</head>', 1)
    shell, nav_count = re.subn(
        r'const navProduct=.*?updateNav\(\);',
        """const navSections=['apps','projects','principles'].map(id=>[document.getElementById(id),document.querySelector('.nav-links a[href="#'+id+'"]')]);
function updateNav(){const y=scrollY+160;let active;for(const pair of navSections)if(y>=pair[0].offsetTop)active=pair;for(const pair of navSections){if(pair===active)pair[1].setAttribute('aria-current','true');else pair[1].removeAttribute('aria-current')}}
addEventListener('scroll',updateNav,{passive:true});updateNav();
navSections[1][1].addEventListener('click',()=>{document.body.classList.remove('nav-open');document.querySelector('.nav-toggle').setAttribute('aria-expanded','false')});""",
        shell, count=1,
    )
    assert nav_count == 1
    card = (
        f'<section class="section" id="projects" aria-labelledby="projects-title"><div class="shell">'
        f'<div class="section-head"><div><div class="section-kicker">{c["home_kicker"]}</div>'
        f'<h2 id="projects-title">{c["nav"]}</h2></div><p class="section-intro">{c["home_intro"]}</p></div>'
        f'<article class="portfolio-card"><div class="portfolio-art" aria-hidden="true">'
        '<svg viewBox="0 0 320 180" width="320" height="180" fill="none" focusable="false">'
        '<rect x="35" y="41" width="154" height="107" rx="15" stroke="currentColor" stroke-width="2"/>'
        '<path d="M35 65h154M57 89h77m-77 16h51m-51 16h64" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        '<rect x="166" y="20" width="119" height="95" rx="14" fill="#174347" stroke="currentColor" stroke-width="2"/>'
        '<path d="M188 52h73m-73 30h73" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        '<path d="M204 52l4 4 8-8m11 34 4 4 8-8" stroke="#fbe09e" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        '</svg></div>'
        f'<div class="portfolio-card-body"><h3>{c["card_title"]}</h3><p>{c["card_text"]}</p>'
        f'<a class="button" href="{CASE[locale]}">{c["read_case"]}<span aria-hidden="true">↗</span></a></div>'
        '</article></div></section>\n'
    )
    return shell.replace(section, card + section, 1)


def build_case_studies():
    template = Template((ROOT / 'build/templates/aletea-case.html').read_text(encoding='utf-8'))
    for locale, copy in COPY.items():
        other = 'es' if locale == 'en' else 'en'
        public = dict(copy, locale=locale, og_locale='en_US' if locale == 'en' else 'es_UY',
                      canonical=BASE + CASE[locale], en_url=BASE + CASE['en'],
                      es_url=BASE + CASE['es'], alt=CASE[other], alt_lang=other,
                      alt_name=COPY[other]['lang_name'], public_url=PUBLIC_SITE)
        out = ROOT / CASE[locale].strip('/') / 'index.html'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(template.substitute({k: e(v) for k, v in public.items()}), encoding='utf-8')
    return [BASE + url for url in CASE.values()]


if __name__ == '__main__':
    build()
