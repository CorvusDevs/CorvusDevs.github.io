# -*- coding: utf-8 -*-
# Generate a crawlable, pre-rendered static page per language under /i18n/<loc>/,
# plus hreflang alternates, sitemap.xml and robots.txt. Run from repo root AFTER build.py.
import json, os, re, html as _html

BASE = "https://corvusdevs.github.io"
T = json.loads(open("/tmp/T.json", encoding="utf-8").read()) if os.path.exists("/tmp/T.json") else None
if T is None:
    import subprocess
    subprocess.run(["node","-e",
        "const fs=require('fs');const h=fs.readFileSync('index.html','utf8');const m=h.match(/const T = (\\{[\\s\\S]*?\\n    \\});/);fs.writeFileSync('/tmp/T.json',JSON.stringify(eval('('+m[1]+')')))"],check=True)
    T = json.loads(open("/tmp/T.json", encoding="utf-8").read())

EN = set(T["en"].keys())
# complete non-English locales only (zh-Hant is partial -> skip)
LOCALES = [l for l in T if l != "en" and set(T[l].keys()) >= EN]
BCP47 = {"pt":"pt-BR","zh":"zh-Hans"}
def bcp(l): return BCP47.get(l, l)
esc = lambda s: _html.escape(s, quote=True)

MAIN = open("index.html", encoding="utf-8").read()

# ---- shared hreflang block (en + all complete locales + x-default) ----
def hreflang_block(canonical):
    rows = [f'<link rel="canonical" href="{canonical}">',
            f'<link rel="alternate" hreflang="en" href="{BASE}/">']
    for l in LOCALES:
        rows.append(f'<link rel="alternate" hreflang="{bcp(l)}" href="{BASE}/i18n/{l}/">')
    rows.append(f'<link rel="alternate" hreflang="x-default" href="{BASE}/">')
    return "\n    ".join(rows)

# replace the existing canonical+hreflang run (from <link rel="canonical"> through the x-default line)
HREF_RE = re.compile(r'<link rel="canonical".*?hreflang="x-default"[^>]*>', re.S)

# ---- body localizer: match the runtime walker exactly ----
DI = re.compile(r'(<)([a-zA-Z][a-zA-Z0-9]*)((?:\s+[a-zA-Z-]+="[^"]*")*?\s+)data-i18n="([^"]+)"((?:\s+[a-zA-Z-]+="[^"]*")*\s*)>(?:[^<]|<br\s*/?>)*</\2>')
DIH = re.compile(r'(<)([a-zA-Z][a-zA-Z0-9]*)((?:\s+[a-zA-Z-]+="[^"]*")*?\s+)data-i18n-html="([^"]+)"((?:\s+[a-zA-Z-]+="[^"]*")*\s*)>(?:[^<]|<br\s*/?>)*</\2>')
def localize_body(h, tr):
    def r1(m):
        pre,tag,mid,key,post = m.group(1,2,3,4,5)
        return f'{pre}{tag}{mid}data-i18n="{key}"{post}>{esc(tr[key])}</{tag}>' if key in tr else m.group(0)
    def r2(m):
        pre,tag,mid,key,post = m.group(1,2,3,4,5)
        return f'{pre}{tag}{mid}data-i18n-html="{key}"{post}>{tr[key]}</{tag}>' if key in tr else m.group(0)
    h = DI.sub(r1, h); h = DIH.sub(r2, h)
    h = h.replace('placeholder="Search apps"', f'placeholder="{esc(tr["f_search"])}"')  # data-i18n-ph
    return h

def localize_head(h, tr, loc):
    title = f"CorvusDevs: {tr['hero_title']}"
    desc = tr['hero_sub']
    canon = f"{BASE}/i18n/{loc}/"
    h = h.replace('<html lang="en">', f'<html lang="{bcp(loc)}">')
    # absolute asset URLs (page lives at /i18n/<loc>/, so relative paths would 404);
    # leave #anchors and href="/" alone so in-page nav still works
    for rel in ('icons/','flags/','avatar.png','favicon-32x32.png','favicon-16x16.png','apple-touch-icon.png','og-image.png'):
        h = h.replace(f'src="{rel}', f'src="{BASE}/{rel}').replace(f'href="{rel}', f'href="{BASE}/{rel}')
    h = h.replace('href="privacy"', f'href="{BASE}/privacy"').replace('href="terms"', f'href="{BASE}/terms"')
    h = HREF_RE.sub(hreflang_block(canon), h, count=1)
    h = re.sub(r'<title>[^<]*</title>', f'<title>{esc(title)}</title>', h, count=1)
    h = re.sub(r'(<meta name="description" content=")[^"]*(">)', lambda m:m.group(1)+esc(desc)+m.group(2), h, count=1)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*(">)', lambda m:m.group(1)+esc(title)+m.group(2), h, count=1)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*(">)', lambda m:m.group(1)+esc(desc)+m.group(2), h, count=1)
    h = re.sub(r'(<meta name="twitter:title" content=")[^"]*(">)', lambda m:m.group(1)+esc(title)+m.group(2), h, count=1)
    h = re.sub(r'(<meta name="twitter:description" content=")[^"]*(">)', lambda m:m.group(1)+esc(desc)+m.group(2), h, count=1)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*(">)', lambda m:m.group(1)+canon+m.group(2), h, count=1)
    # force this locale before the runtime auto-detect runs
    h = h.replace('</head>', f'<script>try{{localStorage.setItem("corvus-lang","{loc}")}}catch(e){{}}</script>\n</head>', 1)
    return h

n=0
for loc in LOCALES:
    tr = T[loc]
    page = localize_head(MAIN, tr, loc)
    page = localize_body(page, tr)
    os.makedirs(f"i18n/{loc}", exist_ok=True)
    open(f"i18n/{loc}/index.html","w",encoding="utf-8").write(page)
    n+=1

# ---- update the main page's hreflang to point at the locale pages ----
MAIN2 = HREF_RE.sub(hreflang_block(f"{BASE}/"), MAIN, count=1)
open("index.html","w",encoding="utf-8").write(MAIN2)

# ---- sitemap.xml + robots.txt ----
urls = [f"{BASE}/"] + [f"{BASE}/i18n/{l}/" for l in LOCALES]
sm = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls: sm.append(f"  <url><loc>{u}</loc></url>")
sm.append("</urlset>")
open("sitemap.xml","w",encoding="utf-8").write("\n".join(sm)+"\n")
open("robots.txt","w",encoding="utf-8").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")

print(f"generated {n} locale pages: {LOCALES}")
print(f"sitemap urls: {len(urls)}")
