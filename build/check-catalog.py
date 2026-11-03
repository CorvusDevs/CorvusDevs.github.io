#!/usr/bin/env python3
"""Focused contract checks for public catalog identity, links and static content."""
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]

class Catalog(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.rows, self.links, self.ids, self.missing_alt = [], [], [], []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.append(a['id'])
        if tag == 'article' and 'app-row' in a.get('class', '').split():
            self.rows.append(a.get('data-slug'))
        if tag == 'a':
            self.links.append(a.get('href'))
        if tag == 'img' and 'alt' not in a:
            self.missing_alt.append(a.get('src'))

def validate_page(text, apps):
    doc = Catalog(text)
    expected = {a['slug'] for a in apps}
    errors = []
    if len(doc.rows) != len(apps) or set(doc.rows) != expected:
        errors.append('static catalog rows differ from manifest')
    if len(doc.ids) != len(set(doc.ids)):
        errors.append('duplicate IDs')
    if doc.missing_alt:
        errors.append('image alt attributes missing')
    for app in apps:
        if app['url'] not in doc.links:
            errors.append('missing product link: ' + app['slug'])
        if app['store']['url'] not in doc.links:
            errors.append('missing purchase/download link: ' + app['slug'])
    for link in doc.links:
        if not link or link == '#':
            errors.append('empty link')
    return errors

def main():
    data = json.loads((ROOT / 'apps.json').read_text())
    apps = data['apps']
    assert len(apps) == 20 and sum(bool(a.get('appStoreId')) for a in apps) == 15
    assert len({a['slug'] for a in apps}) == len(apps)
    # Positive/negative controls establish that the scanner detects the original gap.
    assert validate_page('<div id="catalog"></div>', apps)
    errors = []
    pages = [ROOT / 'index.html', *sorted((ROOT / 'i18n').glob('*/index.html'))]
    source = ROOT.parent / 'evidence/apple-us.json'
    if source.exists():
        apple = {a['trackId']: a for a in json.loads(source.read_text())['results'] if a.get('wrapperType') == 'software'}
        assert set(apple) == {a['appStoreId'] for a in apps if a.get('appStoreId')}
        for app in apps:
            if app.get('appStoreId'):
                a = apple[app['appStoreId']]
                assert app['version'] == a['version'] and app['releaseDate'] == a['currentVersionReleaseDate']
                assert str(a['trackId']) in app['store']['url']
    for app in apps:
        icon = urlsplit(app['icon']).path.lstrip('/')
        assert (ROOT / icon).is_file(), icon
    for page in pages:
        text = page.read_text()
        for error in validate_page(text, apps):
            errors.append(str(page.relative_to(ROOT)) + ': ' + error)
        payload = json.loads(re.search(r'<script id="appsData" type="application/json">(.*?)</script>', text, re.S)[1])
        assert len(payload) == 20
        for local, app in zip(payload, apps):
            for key in ('slug', 'store', 'platforms', 'version', 'releaseDate'):
                assert local.get(key) == app.get(key), (page, app['slug'], key)
        assert 'viewport-fit=cover' in text
        for marker in ('ac-no-horizontal-scroll', 'ac-nav-hamburger', 'ac-footer-mobile'):
            assert marker in text
        for script in re.finditer(r'<script([^>]*)>(.*?)</script>', text, re.S):
            if 'application/' not in script[1] and script[2].strip():
                checked = subprocess.run(['node', '--check'], input=script[2], text=True, capture_output=True)
                assert checked.returncode == 0, (page, checked.stderr)
    sitemap = ET.parse(ROOT / 'sitemap.xml')
    urls = {node.text for node in sitemap.findall('.//{*}loc')}
    assert {a['url'] for a in apps} <= urls
    if errors:
        raise SystemExit('\n'.join(errors))
    print(json.dumps({'pages': len(pages), 'static_app_entries': len(pages) * len(apps), 'app_store_products': 15, 'sitemap_urls': len(urls), 'errors': 0}, indent=2))

if __name__ == '__main__':
    main()
