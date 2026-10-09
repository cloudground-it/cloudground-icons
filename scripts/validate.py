"""Check every icon follows the grid rules: python3 scripts/validate.py [icons] [icons.json]."""
import json, os, re, sys
import xml.etree.ElementTree as ET
D = sys.argv[1] if len(sys.argv) > 1 else 'icons'
JSON = sys.argv[2] if len(sys.argv) > 2 else 'icons.json'
NS = '{http://www.w3.org/2000/svg}'
ROOT = {'viewBox': '0 0 24 24', 'fill': 'none', 'stroke': 'currentColor', 'stroke-width': '1.75',
        'stroke-linecap': 'square', 'stroke-linejoin': 'miter'}
ALLOWED = {'path': {'d'}, 'circle': {'cx', 'cy', 'r'}, 'rect': {'x', 'y', 'width', 'height'}, 'line': {'x1', 'y1', 'x2', 'y2'}}
EXTRA = {'fill': {'currentColor'}, 'stroke': {'none'}, 'stroke-linecap': {'butt'}}
errs = []
icons = json.load(open(JSON))
svgs = sorted(f[:-4] for f in os.listdir(D) if f.endswith('.svg'))
names = [i['name'] for i in icons]
if len(svgs) != len(icons): errs.append(f'count svg={len(svgs)} json={len(icons)}')
if len(set(names)) != len(names): errs.append('duplicate names')
if sorted(names) != svgs: errs.append('json/svg name mismatch')
for n in svgs:
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', n): errs.append(f'{n}: not kebab-case')
    raw = open(os.path.join(D, n + '.svg')).read()
    if re.search(r'transform|id=|style|class=', raw): errs.append(f'{n}: forbidden attr')
    root = ET.fromstring(raw)
    if root.tag != NS + 'svg' or dict(root.attrib) != ROOT: errs.append(f'{n}: root attrs {root.attrib}')
    for el in root:
        t = el.tag.replace(NS, '')
        if t not in ALLOWED: errs.append(f'{n}: element {t}'); continue
        for k, v in el.attrib.items():
            if k in ALLOWED[t]: continue
            if k in EXTRA and v in EXTRA[k]: continue
            errs.append(f'{n}: {t} {k}={v}')
        if el.attrib.get('fill') == 'currentColor':
            w = float(el.attrib.get('width', 0)); 
            if t != 'rect' or w > 2.5: errs.append(f'{n}: fill on non-dot')
        if len(list(el)): errs.append(f'{n}: nested children')
    inner = raw[raw.index('>') + 1: raw.rindex('</svg>')]
    j = next(i for i in icons if i['name'] == n)
    if j['svg_inner'] != inner: errs.append(f'{n}: json svg_inner differs')
    if not j['tags'] or not j['group']: errs.append(f'{n}: missing tags/group')
print('\n'.join(errs) or f'OK: {len(svgs)} icons, all valid')
if errs:
    sys.exit(1)
