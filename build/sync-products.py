#!/usr/bin/env python3
"""Apply shared public product fields to isolated website repositories."""
import argparse
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('slug', 'name', 'appStoreId', 'version', 'releaseDate', 'originalReleaseDate', 'platforms', 'requirements', 'store', 'metadataSource')

def sync_html(text, app):
    # Bind existing download anchors, including Apple's equivalent slug URLs.
    def bind_cta(m):
        anchor = m[0]
        href = re.search(r'href="([^"]+)"', anchor)
        if not href:
            return anchor
        url = urlsplit(href[1].replace('&amp;', '&'))
        identifier = re.search(r'/id(\d+)(?:/|$)', url.path)
        if url.hostname == 'apps.apple.com' and identifier and int(identifier[1]) == app['appStoreId'] and parse_qs(url.query).get('action') != ['write-review']:
            if 'data-product-store' not in anchor:
                anchor = anchor[:-1] + ' data-product-store>'
        return anchor
    text = re.sub(r'<a\b[^>]*>', bind_cta, text)
    # Footer links to the current changelog entry are current-version fields.
    def bind_version(m):
        value = m[2]
        prefix = 'v' if value.startswith('v') else ''
        return m[1] + prefix + '<span data-product-field="version">' + escape(app['version']) + '</span>' + m[3] if value.removeprefix('v') == app['version'] else m[0]
    text = re.sub(r'(<a\b[^>]*href="[^"]*changelog\.html"[^>]*>)([^<>]*)(</a>)', bind_version, text)
    values = {'version': app['version'], 'platforms': ' · '.join(app['platforms']),
              'requirements': ' · '.join(f'{system} {version}+' for system, version in app['requirements'].items())}
    pattern = r'(<(?P<tag>[a-zA-Z0-9]+)\b[^>]*\bdata-product-field="(?P<field>version|platforms|requirements)"[^>]*>)(?P<value>[^<]*)(</(?P=tag)>)'
    text = re.sub(pattern, lambda m: m[1] + escape(values[m['field']]) + m[5], text)
    def cta(m):
        return re.sub(r'href="[^"]*"', 'href="' + escape(app['store']['url'], quote=True) + '"', m[0])
    text = re.sub(r'<a\b[^>]*\bdata-product-store(?:="[^"]*")?[^>]*>', cta, text)
    def structured(m):
        try:
            payload = json.loads(m[2])
        except json.JSONDecodeError:
            return m[0]
        changed = False
        def visit(value):
            nonlocal changed
            if isinstance(value, dict):
                types = value.get('@type', [])
                types = [types] if isinstance(types, str) else types
                if set(types) & {'SoftwareApplication', 'MobileApplication', 'MacApplication'}:
                    value['softwareVersion'] = app['version']
                    changed = True
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)
        visit(payload)
        return m[1] + json.dumps(payload, ensure_ascii=False, indent=2).replace('<', '\\u003c') + m[3] if changed else m[0]
    return re.sub(r'(<script\b[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)', structured, text, flags=re.S)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--products', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    apps = json.loads((ROOT / 'apps.json').read_text())['apps']
    drift, missing, count = [], [], 0
    for app in apps:
        if not app.get('appStoreId'):
            continue
        repo = args.products / app['slug']
        public = repo / 'docs' if (repo / 'docs/index.html').exists() else repo
        if not (public / 'index.html').exists():
            missing.append(app['slug'])
            continue
        snapshot = {key: app[key] for key in FIELDS if key in app}
        snapshot['sourceCatalog'] = 'https://corvusdevs.github.io/apps.json'
        candidates = {public / 'product-data.json': json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n'}
        for page in [public / 'index.html', *sorted((public / 'i18n').glob('*/index.html'))]:
            candidates[page] = sync_html(page.read_text(), app)
        for path, rendered in candidates.items():
            current = path.read_text() if path.exists() else None
            if current != rendered:
                drift.append(str(path.relative_to(args.products)))
                if not args.check:
                    path.write_text(rendered)
        count += 1
    print(json.dumps({'mode': 'check' if args.check else 'write', 'products': count, 'changed_or_drifted_files': len(drift), 'missing': missing}, indent=2))
    if args.check and (drift or missing):
        for path in drift[:20]:
            print(path)
        raise SystemExit(1)

if __name__ == '__main__':
    main()
