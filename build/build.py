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
CASE_ASSETS = '/i18n/en/projects/aletea/assets/'
CASE_IMAGE = CASE_ASSETS + 'aletea-project.png'
COPY = {'en': {'home': '/',
        'nav': 'Projects',
        'home_title': 'Selected projects',
        'home_kicker': 'Beyond the apps',
        'home_intro': 'Design and development with organizations working alongside their communities.',
        'card_title': 'Aletea',
        'card_subtitle': 'Website and internal coordination tool',
        'card_text': 'Two tools supporting Aletea’s mission: helping autistic people and their families find '
                     'support and helping the team follow through on requests.',
        'read_case': 'Read the case study',
        'back': 'Back to projects',
        'description': 'Aletea takes a neurodiversity approach to improving quality of life for autistic '
                       'people and their families. Explore its website and coordination tool.',
        'art_alt': 'Aletea’s wordmark and an excerpt of the paths on its public website.',
        'title': 'Design and development portfolio',
        'skip': 'Skip to content',
        'folio': 'Portfolio · Design and development',
        'alt': 'Español',
        'location': 'Uruguayan civil association for autism',
        'scope': 'I designed and developed two tools with the Aletea team to help autistic people and their '
                 'families find support, and help the team follow through on requests.',
        'discover': 'Explore the projects',
        'public_short': 'Public website',
        'internal_short': 'Internal coordination',
        'related_short': 'Video work',
        'role_label': 'My role',
        'role': 'Ale / CorvusDevs · Experience design and development',
        'collab_label': 'Collaboration',
        'collab': 'With the Aletea team',
        'deliverables_label': 'Delivered work',
        'deliverables': 'Website, internal tool and video work',
        'nav_label': 'Case study sections',
        'index_short': 'Feature index',
        'site_head': 'A simpler path to guidance.',
        'site_lede': 'For a first-time visitor, “I need guidance” is clearer than the name of a department. '
                     'That became the starting point for the website.',
        'decision_label': 'The decision',
        'site_decision': 'Organize navigation around what people come to do: ask for guidance, find an '
                         'activity or look up a resource.',
        'result_label': 'What people can do today',
        'site_result': 'Find where to ask for guidance, check dates or browse resources from one website.',
        'site_cta': 'Visit Aletea’s website',
        'public_caption': 'Excerpt from Aletea’s Spanish homepage: original paths, icons and links, reframed '
                          'for this portfolio.',
        'mgr_head': 'Keep each request moving.',
        'mgr_lede': 'The work does not end when a form is submitted. The team needs to see what came in, who '
                    'is handling it and what happens next.',
        'mgr_decision': 'Bring intake, routing, ownership and follow-up together in a workflow the team can '
                        'pick back up.',
        'mgr_result': 'A request can move from a form to the team responsible for it, with a record of actions '
                      'and next steps.',
        'fake': 'Demo · fictional data',
        'fake_id': 'Example 01',
        'request': 'Question about joining an activity',
        'request_desc': 'A generic example. No contact or participant details.',
        'step_label': 'Explore the three example steps',
        'nojs': 'Example workflow: receive a form, route it to the responsible team and record the next step.',
        'manager_footer': 'Changes in this example are not stored or submitted.',
        'manager_caption': 'An interactive workflow demo, not a screenshot or a link to the live internal '
                           'tool.',
        'editorial_head': 'Telling the community’s story.',
        'editorial_lede': 'For Fútbol sin Barreras, I edited a thank-you video for volunteers with recorded '
                          'narration, synchronized captions and a sound mix. This portfolio shows the scope of '
                          'that editing without displaying footage of participants.',
        'film_cover_label': 'Video work · Aletea',
        'film_cover_line': 'An end-of-year thank-you to volunteers',
        'film_role': 'Editing, captions and sound mix',
        'film_format_label': 'Format',
        'film_format': 'Vertical video',
        'film_caption': 'The project’s public badge. This graphic is not a frame from the video.',
        'cap_kicker': 'Project scope',
        'cap_head': 'The work in detail.',
        'accessibility': 'Aletea uses WCAG 2.2 AA as a benchmark. Evaluation with people and assistive '
                         'technologies is still pending.',
        'credit': 'Designed and developed by CorvusDevs with the Aletea team. Their day-to-day work and '
                  'feedback shaped the decisions.',
        'cards': [('Find guidance', 'Find a first point of contact for talking with the team.', '/familias/'),
                  ('Check the agenda', 'See published activities and how to take part.', '/agenda/'),
                  ('Explore the library', 'Find guides, materials and references.', '/biblioteca/')],
        'flow': [('01 · Receive', 'Received', 'From: form', 'The request is ready to review and route.'),
                 ('02 · Route',
                  'Routed',
                  'Activities team',
                  'The responsible team takes the request. This does not confirm enrollment.'),
                 ('03 · Follow up',
                  'In follow-up',
                  'Next step recorded',
                  'The team records what guidance remains to be given.')],
        'inv': [('Public website',
                 ['Needs-based navigation',
                  'Agenda and activities',
                  'Search with categories',
                  'Digital library',
                  'Training and resources',
                  'Sections for families and autistic adults',
                  'Contact routes and forms',
                  'Blog, campaigns and transparency']),
                ('Internal coordination',
                 ['Form intake',
                  'Pending requests',
                  'Routing by team',
                  'Assigning responsibility',
                  'Role-based access',
                  'Replies and internal comments',
                  'Tasks and activity notices',
                  'Follow-up record']),
                ('Video editing',
                 ['Recorded narration and original footage',
                  'Synchronized captions',
                  'Voice and music mix',
                  'Vertical framing and export'])],
        'mission_first': 'Breaking down barriers.',
        'mission_last': 'Building community.',
        'ref_label_es': 'Detalle del sitio público',
        'route_label': 'Explore the public paths',
        'fsb_cta': 'Explore Fútbol sin Barreras',
        'fsb_alt': 'Official Fútbol sin Barreras badge'},
 'es': {'home': '/i18n/es/',
        'nav': 'Proyectos',
        'home_title': 'Proyectos seleccionados',
        'home_kicker': 'Más allá de las apps',
        'home_intro': 'Diseño y desarrollo junto a organizaciones que trabajan en comunidad.',
        'card_title': 'Aletea',
        'card_subtitle': 'Sitio web y Gestor interno',
        'card_text': 'Dos herramientas para acompañar la misión de Aletea: acercar apoyos a las personas '
                     'autistas y sus familias, y ayudar al equipo a dar seguimiento a las consultas.',
        'read_case': 'Ver el caso de estudio',
        'back': 'Volver a proyectos',
        'description': 'Desde la neurodiversidad, Aletea trabaja por una mejor calidad de vida para personas '
                       'autistas y sus familias. Conocé la web y el gestor.',
        'art_alt': 'Identidad de Aletea y un fragmento de los recorridos de su sitio público.',
        'title': 'Portafolio de diseño y desarrollo',
        'skip': 'Saltar al contenido',
        'folio': 'Portafolio · Diseño y desarrollo',
        'alt': 'English',
        'location': 'Asociación Civil Uruguaya de Autismo',
        'scope': 'Diseñé y desarrollé junto al equipo de Aletea dos herramientas para que las personas '
                 'autistas y sus familias encuentren apoyos, y para que el equipo pueda dar curso a cada '
                 'consulta.',
        'discover': 'Ver los proyectos',
        'public_short': 'Sitio público',
        'internal_short': 'Gestor interno',
        'related_short': 'Trabajo audiovisual',
        'role_label': 'Mi rol',
        'role': 'Ale / CorvusDevs · Diseño de experiencia y desarrollo',
        'collab_label': 'Colaboración',
        'collab': 'Con el equipo de Aletea',
        'deliverables_label': 'Trabajo entregado',
        'deliverables': 'Sitio, gestor y piezas audiovisuales',
        'nav_label': 'Secciones del caso',
        'index_short': 'Índice de funciones',
        'site_head': 'Orientación sin vueltas.',
        'site_lede': 'Para quien llega por primera vez, “necesito orientación” es más claro que el nombre de '
                     'un área. Ese fue el punto de partida del sitio.',
        'decision_label': 'La decisión',
        'site_decision': 'Ordenar la navegación por lo que la persona necesita hacer: pedir orientación, '
                         'buscar una actividad o encontrar un recurso.',
        'result_label': 'Lo que se puede hacer hoy',
        'site_result': 'Llegar a un canal de orientación, consultar fechas o buscar materiales desde el mismo '
                       'sitio.',
        'site_cta': 'Visitar el sitio de Aletea',
        'public_caption': 'Fragmento de la portada pública: rutas, íconos y enlaces originales. Encuadre '
                          'adaptado al portafolio.',
        'mgr_head': 'Que ninguna consulta pierda el hilo.',
        'mgr_lede': 'La consulta no termina al enviar un formulario. El equipo necesita saber qué llegó, quién '
                    'lo toma y qué seguimiento queda.',
        'mgr_decision': 'Reunir recepción, derivación, responsables y seguimiento en un flujo que el equipo '
                        'pueda retomar.',
        'mgr_result': 'Una consulta puede pasar del formulario a un equipo responsable, con un registro de '
                      'acciones y próximos pasos.',
        'fake': 'Demo · datos ficticios',
        'fake_id': 'Ejemplo 01',
        'request': 'Consulta para participar en una actividad',
        'request_desc': 'Ejemplo genérico, sin datos de contacto ni de participantes.',
        'step_label': 'Explorar los tres pasos de ejemplo',
        'nojs': 'Flujo ilustrado: recibir el formulario, derivar al equipo responsable y dejar registrado el '
                'próximo paso.',
        'manager_footer': 'Los cambios de estado de este ejemplo no se guardan ni se envían.',
        'manager_caption': 'Demo interactiva del flujo, no captura ni acceso al gestor real.',
        'editorial_head': 'La comunidad también se cuenta.',
        'editorial_lede': 'Para Fútbol sin Barreras, edité una pieza de agradecimiento al voluntariado con voz '
                          'grabada, montaje, subtítulos sincronizados y mezcla. Acá muestro el trabajo de '
                          'edición, sin reproducir imágenes de participantes.',
        'film_cover_label': 'Pieza audiovisual · Aletea',
        'film_cover_line': 'Agradecimiento de fin de año al voluntariado',
        'film_role': 'Montaje, subtítulos y mezcla',
        'film_format_label': 'Formato',
        'film_format': 'Video vertical',
        'film_caption': 'Escudo público del proyecto. Esta composición no es un fotograma de la pieza.',
        'cap_kicker': 'Alcance del proyecto',
        'cap_head': 'El trabajo, en detalle.',
        'accessibility': 'Aletea usa WCAG 2.2 AA como referencia. La evaluación con personas y tecnologías de '
                         'asistencia sigue pendiente.',
        'credit': 'Diseño y desarrollo por CorvusDevs, junto al equipo de Aletea. Su trabajo cotidiano y sus '
                  'devoluciones orientaron las decisiones.',
        'cards': [('Pedir orientación', 'Encontrá un primer canal para conversar con el equipo.', '/familias/'),
                  ('Consultar la agenda', 'Revisá las actividades publicadas y cómo participar.', '/agenda/'),
                  ('Explorar la biblioteca', 'Encontrá guías, materiales y referencias.', '/biblioteca/')],
        'flow': [('01 · Recibir',
                  'Recibida',
                  'Origen: formulario',
                  'La consulta queda disponible para revisar y derivar.'),
                 ('02 · Derivar',
                  'Derivada',
                  'Equipo de actividades',
                  'El equipo responsable toma la consulta; no se confirma una inscripción.'),
                 ('03 · Seguir',
                  'En seguimiento',
                  'Próximo paso registrado',
                  'El equipo deja asentado qué orientación falta dar.')],
        'inv': [('Sitio público',
                 ['Navegación por necesidades',
                  'Agenda y actividades',
                  'Buscador con categorías',
                  'Biblioteca digital',
                  'Formación y recursos',
                  'Páginas para familias y personas adultas autistas',
                  'Canales y formularios de contacto',
                  'Blog, campañas y transparencia']),
                ('Gestor interno',
                 ['Recepción de formularios',
                  'Cola de pendientes',
                  'Derivación por equipo',
                  'Asignación de responsables',
                  'Permisos por rol',
                  'Respuestas y comentarios internos',
                  'Tareas y avisos de actividad',
                  'Registro del seguimiento']),
                ('Edición audiovisual',
                 ['Montaje de voz y material original',
                  'Subtítulos sincronizados',
                  'Mezcla de voz y música',
                  'Composición y exportación vertical'])],
        'mission_first': 'Derribamos barreras.',
        'mission_last': 'Construimos comunidad.',
        'ref_label_es': 'Detalle del sitio público',
        'route_label': 'Probá estos recorridos',
        'fsb_cta': 'Conocé Fútbol sin Barreras',
        'fsb_alt': 'Escudo oficial de Fútbol sin Barreras'}}


def add_projects(shell, locale):
    if locale not in COPY:
        return shell
    c = {k: e(v) for k, v in COPY[locale].items() if isinstance(v, str)}
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
        f'<h2 id="projects-title">{c["home_title"]}</h2></div><p class="section-intro">{c["home_intro"]}</p></div>'
        f'<article class="portfolio-card"><div class="portfolio-art">'
        f'<img src="{CASE_IMAGE}" width="1200" height="630" loading="lazy" decoding="async" alt="{c["art_alt"]}"></div>'
        f'<div class="portfolio-card-body"><h3>{c["card_title"]}<span>{c["card_subtitle"]}</span></h3><p>{c["card_text"]}</p>'
        f'<a class="button" href="{CASE[locale]}">{c["read_case"]}<span aria-hidden="true">↗</span></a></div>'
        '</article></div></section>\n'
    )
    return shell.replace(section, card + section, 1)


def build_case_studies():
    template = Template((ROOT / 'build/templates/aletea-case.html').read_text(encoding='utf-8'))
    for locale, copy in COPY.items():
        other = 'es' if locale == 'en' else 'en'
        values = {k: e(v) for k, v in copy.items() if isinstance(v, str)}
        values.update(lang=locale, og_locale='en_US' if locale == 'en' else 'es_UY',
                      canonical=BASE + CASE[locale], en_url=BASE + CASE['en'], es_url=BASE + CASE['es'],
                      alt_path=CASE[other], alt_lang=other, og_image=BASE + CASE_IMAGE)
        values['public_cards'] = ''.join(
            f'<a class="webstep" href="{e(PUBLIC_SITE.rstrip("/") + path)}"><strong>{e(title)}</strong>'
            f'<span>{e(detail)}</span><b aria-hidden="true">↗</b></a>'
            for title, detail, path in copy['cards']
        )
        values['steps'] = ''.join(
            f'<button class="flowstep" type="button" aria-pressed="{str(i == 0).lower()}" '
            f'data-status="{e(status)}" data-owner="{e(owner)}" data-detail="{e(detail)}">{e(step)}</button>'
            for i, (step, status, owner, detail) in enumerate(copy['flow'])
        )
        _, first_status, first_owner, first_detail = copy['flow'][0]
        values.update(first_status=e(first_status), first_owner=e(first_owner), first_detail=e(first_detail))
        values['inventories'] = ''.join(
            '<details' + (' open' if i == 0 else '') + '><summary>' + e(name) + '</summary><ul>'
            + ''.join('<li>' + e(item) + '</li>' for item in items) + '</ul></details>'
            for i, (name, items) in enumerate(copy['inv'])
        )
        out = ROOT / CASE[locale].strip('/') / 'index.html'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(template.substitute(values), encoding='utf-8')
    return [BASE + url for url in CASE.values()]


if __name__ == '__main__':
    build()
