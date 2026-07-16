# Landing page build

`index.html` is generated. Do not edit it by hand.

## Regenerate
    python3 build/build.py     # run from the repo root

## What to edit
- `build/index.src.html` , the source template: SEO `<head>`, the translation catalog (`const T`), the language picker, and the Values / Coming-soon / Footer markup.
- `build/build.py` , the app list (`A`), which apps are featured, new-UI-string translations, and the featured/collection markup.
- `build/site_style.css` , all styles.

The build injects the new UI keys into every language, renders the Featured strip + collection, self-hosts nothing new (flags live in `flags/`), and strips long dashes.
