"""Render Tube Ambient Lights launch pages. See tube/README.md."""
import argparse
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlparse

root = Path(__file__).resolve().parent.parent
build = root / 'build/tube'
product = root / 'tube-ambient-lights'
base = 'https://corvusdevs.github.io/tube-ambient-lights/'
load = lambda name: json.loads((build / name).read_text())
template = (build / 'launch.html').read_text()
locales = load('locales.json')
english = load('english.json')
config = load('release.json')
mac_enabled = config['mac']['sectionEnabled']
mac_labels = dict(line.split('\t', 1) for line in (build / 'mac-availability.tsv').read_text().splitlines())
assert set(mac_labels) == set(locales)
store = config['store']
mac_store = config['mac']['store']
app = 'Tube Ambient Lights for Safari'
for u in [store, mac_store]:
    assert urlparse(u).hostname == 'apps.apple.com' and urlparse(u).scheme == 'https' and u.endswith('/id6833198715')

parser = argparse.ArgumentParser()
parser.add_argument('--check', action='store_true')
parser.add_argument('--output', type=Path, default=product)
args = parser.parse_args()

if not (product / 'language-router.js').is_file():
    parser.error('Missing public Tube language-router.js')

def sent(text, n):
    # CJK punctuation is followed by a new sentence with no spaces.
    return ''.join(re.findall(r'.+?(?:[。।]|[.!?](?=\s|$)|$)\s*', text)[:n]).strip()

def cap(text):
    # Store headings use all caps; render normal reading case in cards.
    return text[0]+text[1:].lower() if text.isupper() else text

def card(title, body, css, art):
    return f'<article class="tile"><div class="tile-art {css}" aria-hidden="true">{art}</div><div class="tile-content"><h3>{escape(title)}</h3><p>{escape(body)}</p></div></article>'

for lang, d in locales.items():
    t = d['localized']
    path = d['path']
    own = base if lang == 'en' else base + path
    locpath = '/tube-ambient-lights/' + (str(Path(path).parent) + '/' if '/' in path else '')
    support = locpath + ('support.es.html' if lang == 'es' else 'support.html')
    privacy = locpath + ('privacy.es.html' if lang == 'es' else 'privacy.html')
    menu = ''.join(f'<a href="{base + item["path"] if k != "en" else base}" lang="{k}" hreflang="{k}" dir="{item["direction"]}"{ " aria-current=\"page\"" if k == lang else ""}>{escape(item["name"])}</a>' for k,item in sorted(locales.items()))
    language = f'<details class="locale"><summary aria-label="{escape(t["language"])}: {escape(d["name"])}"><span aria-hidden="true">文A</span></summary><div class="locale-list">{menu}</div></details>'
    alternates = '\n'.join(f'<link rel="alternate" hreflang="{k}" href="{base + item["path"] if k != "en" else base}">' for k,item in sorted(locales.items()))
    rich = lang in ('en','es','es-419')
    title = 'Color beyond <em>the frame.</em>' if lang == 'en' else 'El color sale <em>del cuadro.</em>' if rich else escape(d['title'])
    body = template.replace('El color sale <em>del cuadro.</em>', title)
    if lang == 'en':
        for a,b in sorted(english.items(),key=lambda val:-len(val[0])):
            body=body.replace(a,escape(b))
    elif lang == 'es':
        for a,b in [('Extendé','Extiende'),('Probá','Prueba'),('Arrastrá','Arrastra'),('usá','usa'),('Mostrá','Muestra'),('Elegí','Elige'),('Ajustá','Ajusta'),('Descargá','Descarga'),('Encontrala','Encuéntrala'),('Activala','Actívala'),('Habilitá','Habilita'),('permití','permite'),('Abrí','Abre'),('Reproducí','Reproduce'),('Revisá','Revisa'),('Prendé','Enciende')]:
            body=body.replace(a,b)
        body=re.sub(r'\bvideos?\b',lambda x:x[0].replace('video','vídeo'),body)
    elif not rich:
        body=body.replace('Ir al contenido','↓').replace('<a class="skip" href="#main">↓</a>', f'<a class="skip" href="#main" aria-label="{escape(d["title"])}">↓</a>')
        body=body.replace('En esta página',escape(t['features'])).replace('>Demo<','>'+escape(d['compare'])+'<').replace('>Funciones<','>'+escape(t['features'])+'<').replace('>Instalación<','>'+escape(cap(d['automatic'][0]))+'<')
        body=re.sub(r'<div class="wrap"><ul class="facts".*?</ul></div>','',body,flags=re.S)
        body=body.replace('Ver en el App Store','App Store').replace('Probá el efecto',escape(t['compare_button']))
        body=body.replace('Extendé los colores de YouTube alrededor del reproductor. Una luz suave que cambia con cada escena, sin salir de Safari.',escape(d['lead']))
        body=body.replace('Vista ilustrativa · Comparativa real más abajo',escape(t['illustration'])).replace('alt="Auroras turquesa y violeta sobre un lago, enmarcadas por un halo de los mismos colores."','alt=""')
        head=f'<div class="section-head"><p class="kicker">01 / {escape(t["captures"])}</p><h2>{escape(d["compare"])}</h2></div>'
        body=re.sub(r'(<section class="module wrap" id="demo">)<div class="section-head">.*?</div>',lambda m:m[1]+head,body,count=1,flags=re.S)
        body=body.replace('Dos capturas del mismo fotograma. Sin efecto, el fondo queda blanco. Con el efecto, el azul del cielo y el verde del pasto se extienden alrededor del reproductor.',escape(d['compare']+' · '+d['off']+' / '+d['on'])).replace('Mostrá más o menos luz ambiental',escape(d['compare'])).replace('Vistas de la comparativa',escape(d['compare']))
        body=body.replace('>Comparar<','>'+escape(t['compare_button'])+'<').replace('>Sin luz<','>'+escape(d['off'])+'<').replace('>Con luz<','>'+escape(d['on'])+'<')
        body=re.sub(r'<p class="kicker">Capturas reales · iPad</p><h3>.*?</h3><p>.*?</p>',f'<p class="kicker">{escape(t["captures"])}</p><h3>{escape(d["title"])}</h3><p>{escape(d["lead"])}</p>',body,count=1)
        arts=re.findall(r'<div class="tile-art \w+" aria-hidden="true">(.*?)</div><div class="tile-content">',body,re.S)
        assert len(arts)==3
        feature='<div class="section-head"><p class="kicker">02 / Tube Ambient Lights</p><h2>'+escape(t['features'])+'</h2></div><div class="grid">'
        feature+=card(d['title'],d['lead'],'tint',arts[0])+card(cap(d['controls'][0]),sent(d['controls'][1],2),'precision',arts[1])+card(cap(d['local_title']),d['privacy_blurb'],'privacy',arts[2])
        feature+='</div>'
        start=body.index('<div class="section-head">',body.index('id="funciones"'))
        end=body.index('</div></section>',body.index('</article></div>',start))
        body=body[:start]+feature+'\n'+body[end:]
        start=body.index('<div class="section-head">',body.index('id="instalar"'))
        end=body.index('</section>',start)
        setup=f'<div class="section-head"><p class="kicker">03 / Safari</p><h2>{escape(cap(d["automatic"][0]))}</h2><p>{escape(d["setup"])}</p></div>'
        setup+=f'<div class="questions"><h2>{escape(cap(d["limits"][0]))}</h2><div><p>{escape(d["limits"][1])}</p></div></div>'
        body=body[:start]+setup+body[end:]
        body=body.replace('Prendé la luz.',escape(d['title'])).replace('>Soporte<',f'>{escape(d["support"])}<').replace('>Privacidad<',f'>{escape(d["privacy"])}<')
    body=body.replace('© Blender Foundation','© 2008 Blender Foundation')
    devices='Safari · iPhone + iPad' + (' + Mac' if mac_enabled else '')
    requirements = 'iOS / iPadOS 17+' + (' · macOS ' + config['mac']['minimumMacOS'].removesuffix('.0') + '+' if mac_enabled else '')
    ios_extra = {'en':'iOS and iPadOS 17 or later','es':'iOS y iPadOS 17 o posterior','es-419':'iOS y iPadOS 17 o posterior'}.get(lang, sent(d['req'],1))
    platform = ('<div class="platforms" id="platforms"><article data-platform="ios"><h3>iPhone + iPad</h3><p>'+escape(ios_extra)+'</p>'
                + f'<a class="buy" aria-label="App Store: iPhone + iPad" href="{escape(store)}">App Store <span aria-hidden="true">↗</span></a></article>')
    if mac_enabled:
        platform+=('<article data-platform="mac"><h3>Mac</h3><p>'+escape(sent(d['mac'],1))+'</p>'
                   + f'<a class="buy" aria-label="App Store: Mac" href="{escape(mac_store)}">App Store <span aria-hidden="true">↗</span></a>'
                   + f'<p class="availability">{escape(mac_labels[lang])}</p></article>')
    platform+='</div>'
    subs=dict(LANGUAGE=language, STORE=store, SUPPORT=support, PRIVACY=privacy, LEGAL=d['legal'], DEVICES=devices, HERO_REQUIREMENTS=requirements, PLATFORMS=platform)
    body=re.sub(r'@@(\w+)@@',lambda m:subs[m[1]],body)
    desc=escape(d['lead'])
    head=f'''<!doctype html>
<html lang="{lang}" dir="{d['direction']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{app}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0b0b14">
<meta property="og:type" content="website">
<meta property="og:title" content="{app}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{own}">
<meta property="og:image" content="{base}media/launch-hero.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{own}">
<link rel="alternate" hreflang="x-default" href="{base}">
{alternates}
<link rel="icon" href="/icons/tube-ambient-lights.png">
<link rel="stylesheet" href="{base.removeprefix('https://corvusdevs.github.io')}launch.css">
<script src="/tube-ambient-lights/language-router.js"></script>
<script defer src="/tube-ambient-lights/launch.js"></script>
</head>
<body>'''
    output=head+body+'</body>\n</html>\n'
    dest=args.output/path
    if args.check:
        assert dest.read_text() == output, f'Out of date: {dest}'
    else:
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(output)
print(f'{len(locales)} localized launch pages, Mac {"section enabled, availability deferred to the App Store" if mac_enabled else "section hidden"}')
