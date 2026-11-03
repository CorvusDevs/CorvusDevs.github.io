# Landing page build

`index.html` and `i18n/*/index.html` are generated. Do not edit them by hand.

## Regenerate
    python3 build/build.py     # run from the repo root

## What to edit
- `apps.json`: shared product identity, links, platforms, current versions, release dates, and requirements. Preserve the five direct-download products unless separately authorized.
- `apps.<locale>.json`: translated product taglines and descriptions. The public page aliases `pt` to `pt-BR` and `zh` to `zh-Hans`.
- `build/templates/<locale>.html`: preserved branded page shells, localized navigation, SEO, and styles. Catalog placeholders are rendered statically.
- `build/ui.json`: existing translated catalog labels and family descriptions.
- `catalog.js`: search, filters and featured-image selection. Links and catalog content work without JavaScript.

The old `index.src.html` and `site_style.css` are historical source from a previous design and are not used by this build.

## Product websites

Run `python3 build/sync-products.py --products ../products` to write `docs/product-data.json`, update marked current-version/platform/requirement fields and App Store CTAs, and synchronize JSON-LD versions across isolated public product checkouts. Use `--check` to detect drift without writing. Historical changelog versions are never replaced.

Release labels use verified App Store dates and the catalog's `updated` snapshot date. New and recently updated mean within 45 days; the activity shelf orders the five latest public App Store versions. Refresh the metadata and rebuild when making a catalog update. No live Apple API calls or price changes occur during the build.

The build creates 20 crawlable app entries per maintained page and a sitemap including product pages. Before review, run `python3 build/check-catalog.py` and `python3 build/sync-products.py --products ../products --check`.
