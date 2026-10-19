"""Build Sawt: python3 src/build.py  ->  writes index.html at the repo root.

Optional: --artifact PATH also writes the body-only version used for the claude.ai artifact.
"""
import json, glob, os, bz2, collections, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify import classify

here = os.path.dirname(os.path.abspath(__file__))
raw = {}
for f in sorted(glob.glob(os.path.join(here, 'data', '*.json'))):
    d = json.load(open(f, encoding='utf-8'))
    for s in (d if isinstance(d, list) else [d]):
        raw[s['st']] = s

GUIDE_STATES = ['AL','AZ','CA','CO','CT','DE','FL','GA','IL','IN','KS','MD','MA','MI','MN','MO','NV','NH','NJ','NY','NC','OH','PA','RI','TN','TX','VA','WA','WI']

# ---------- ZIP data ----------
zips = json.load(bz2.open(os.path.join(here, 'vendor', 'zips.json.bz2')))
zips = [z for z in zips if z.get('active') and z['zip_code_type'] in ('STANDARD', 'PO BOX')]
zip3 = collections.defaultdict(collections.Counter)
for z in zips:
    zip3[z['zip_code'][:3]][z['state']] += 1
zip3_str = ''.join(k + v.most_common(1)[0][0] for k, v in sorted(zip3.items()))

def tidy_city(c):
    return c.replace('Saint ', 'St. ') if c.startswith('Saint ') else c

ALLCO = collections.defaultdict(set)
for z in zips:
    if z['county']: ALLCO[z['state']].add(z['county'])

# ---------- contests ----------
DATA = {}
problems = []
for st, s in raw.items():
    contests, by_office = [], {}
    for it in s['items']:
        meta = classify(st, it)
        for c in meta['c']:
            if c not in ALLCO.get(st, set()):
                problems.append((st, it[2] if it[0] != 'M' else it[1], c))
        if it[0] == 'M':
            contests.append({'s': 'M', 'o': it[1], 'p': it[2], 'l': it[3], 'x': it[4] if len(it) > 4 else '',
                             'f': meta['f'], 'd': '', 'r': meta['r'], 'g': meta['g'], 'j': meta['j'],
                             'c': meta['c'], 'y': meta['y'], 'b': meta['b']})
            continue
        key = it[2]
        if key not in by_office:
            con = {'s': it[0], 'o': it[2], 'f': meta['f'], 'd': meta['d'], 'r': meta['r'], 'g': meta['g'],
                   'j': meta['j'], 'c': meta['c'], 'y': meta['y'], 'b': meta['b'], 'n': []}
            by_office[key] = con; contests.append(con)
        by_office[key]['n'].append([it[1], it[3]] + ([it[4]] if len(it) > 4 and it[4] else []))
    for con in contests:  # drop empty fields to save space
        for k in ['d', 'y', 'b', 'x']:
            if k in con and not con[k]:
                del con[k]
        if not con['c']:
            del con['c']
        if con.get('j') == 'st':
            del con['j']
    DATA[st] = {'name': s['name'], 'c': contests}


def relevant(st, city):
    d = DATA.get(st)
    if not d: return False
    if city in REL_CITIES[st]: return True
    return any(city.lower() in b for b in REL_BODIES[st])
REL_CITIES = {st: {c.get('y') for c in d['c'] if c.get('y')} for st, d in DATA.items()}
REL_BODIES = {st: [c['b'].lower() for c in d['c'] if c.get('b')] for st, d in DATA.items()}
ZIPS = {}
for st in GUIDE_STATES:
    rows = [z for z in zips if z['state'] == st]
    cities, counties = [], sorted({z['county'] for z in rows if z['county']})
    cidx = {}
    def ci(name):
        name = tidy_city(name)
        if name not in cidx:
            cidx[name] = len(cities); cities.append(name)
        return cidx[name]
    kidx = {k: i for i, k in enumerate(counties)}
    def b36(n):
        s = ''
        while True:
            n, r = divmod(n, 36); s = '0123456789abcdefghijklmnopqrstuvwxyz'[r] + s
            if n == 0: return s
    parts, prev = [], 0
    for z in sorted(rows, key=lambda r: r['zip_code']):
        if not z['county']:
            continue
        names = [z['city']] + [a for a in (z.get('acceptable_cities') or []) if a]
        rel = [ci(a) for a in names if relevant(st, tidy_city(a))][:3]
        n = int(z['zip_code'])
        parts.append(','.join([b36(n - prev), b36(kidx[z['county']])] + [b36(a) for a in rel]))
        prev = n
    ZIPS[st] = {'ci': cities, 'co': counties, 'z': ';'.join(parts)}

if problems:
    print('COUNTY PROBLEMS:'); [print('  ', p) for p in problems]

if '--dump' in sys.argv:
    for st in sys.argv[sys.argv.index('--dump') + 1:]:
        for c in sorted(DATA[st]['c'], key=lambda c: c['r']):
            print(f"{c['r']:6} {c['g']:8} {c.get('j','st'):3} {c['o'][:60]:60} | fam={c['f'][:40]} d={c.get('d','')} y={c.get('y','')} b={c.get('b','')} c={','.join(c.get('c',[]))[:50]}")

blob = json.dumps(DATA, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
zblob = json.dumps(ZIPS, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
tpl = open(os.path.join(here, 'template.html'), encoding='utf-8').read()
out = tpl.replace('__DATA__', blob).replace('__ZIPS__', zblob).replace('__ZIP3__', json.dumps(zip3_str))
if '--artifact' in sys.argv:
    open(sys.argv[sys.argv.index('--artifact') + 1], 'w', encoding='utf-8').write(out)

# Standalone page for GitHub Pages: everything before <header> goes in <head>
SITE = 'https://ebeid.github.io/sawt-voter-guide/'
DESC = "Unofficial step-by-step guide to CAIR Action's 2026 endorsements. Enter a ZIP code, walk through your ballot, share your list. 7 languages."
head_part, body_part = out.split('<header class="band">', 1)
head_part = head_part.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{DESC}">
<meta name="theme-color" content="#1A3270">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="apple-mobile-web-app-title" content="Sawt">
<meta property="og:type" content="website">
<meta property="og:title" content="Sawt Ballot Guide">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{SITE}">
<meta property="og:image" content="{SITE}og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px);color-scheme:light}}body{{margin:0;font:14px system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
{head_part.strip()}
</head>
<body>
<header class="band">{body_part}
</body>
</html>
"""
root = os.path.dirname(here)
open(os.path.join(root, 'index.html'), 'w', encoding='utf-8').write(page)
total = sum(len(s['c']) for s in DATA.values())
print(f'{len(DATA)} states, {total} contests, data {len(blob)/1024:.0f} KB, zips {len(zblob)/1024:.0f} KB, page {len(out.encode())/1024:.0f} KB')
