import base64, json, os, re, time, urllib.request, urllib.parse

BASE = 'https://www.ffhandball.fr'
UA = 'team-report-coach (fetch of public competition data)'
SEASON = '22'

def get(url, accept='text/html'):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'accept': accept})
    last = None
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:
            last = e; time.sleep(1+i)
    raise last

key = re.search(r'data-cfk="([^"]+)"', get(BASE + '/competitions/').decode()).group(1)

def block(name, params):
    q = urllib.parse.urlencode({'block': name, **params})
    data = get(f'{BASE}/wp-json/competitions/v1/computeBlockAttributes?{q}', 'application/json').decode('utf-8', 'replace')
    if data.startswith('{') or data.startswith('['):
        return json.loads(data)
    raw = base64.b64decode(data)
    return json.loads(bytes(b ^ ord(key[i % len(key)]) for i, b in enumerate(raw)).decode())

import unicodedata
def slugify(lib, id_):
    s = unicodedata.normalize('NFD', lib).encode('ascii','ignore').decode().lower()
    s = re.sub(r'[^a-z0-9]+','-',s).strip('-')
    return f'{s}-{id_}'

COMPS = [
    {'libelle':'U15 MASCULINS','type':'DEPARTEMENTAL','id':'32350'},
    {'libelle':'U15 MASCULINS COUPE DES YVELINES','type':'DEPARTEMENTAL','id':'33743'},
]
TEAMS = [
    {'match': re.compile(r'MAISONS[- ]LAFFITTE', re.I), 'nom': 'USC MAISONS-LAFFITTE HB'},
    {'match': re.compile(r'VERSAILLES', re.I), 'nom': 'VERSAILLES HBC (3)'},
    {'match': re.compile(r'BOUCLE DE SEINE', re.I), 'nom': 'HB BOUCLE DE SEINE 78  (2)'},
]

def first_poules(c):
    base = {'ext_saison_id': SEASON, 'url_competition_type': c['type'].lower(), 'url_competition': slugify(c['libelle'], c['id'])}
    sel = block('competitions---poule-selector', base)
    time.sleep(0.2)
    return base, sel.get('poules') or []

overall = {}
for c in COMPS:
    base, poules = first_poules(c)
    print(f"== {c['libelle']} : {len(poules)} poules")
    for p in poules:
        pid = str(p.get('ext_pouleId') or p.get('id'))
        try:
            sel = block('competitions---poule-selector', {**base, 'ext_poule_id': pid})
        except Exception as e:
            print('  poule', pid, 'FAIL', e); time.sleep(0.3); continue
        opts = sel.get('equipe_options') or []
        phase_lib = ''
        for ph in sel.get('phases') or []:
            if str(ph.get('id')) == str((sel.get('selected_poule') or {}).get('phaseId')):
                phase_lib = ph.get('libelle','')
        sel_poule = (sel.get('selected_poule') or {}).get('libelle','')
        found = []
        for t in TEAMS:
            ids = {str(o['id']) for o in opts if t['match'].search(o.get('libelle','') or '')}
            if ids:
                found.append((t, ids))
        if found:
            print(f"  poule {pid} ({phase_lib} / {sel_poule}): " + ', '.join(t['nom'] for t,_ in found))
            allr = {}
            for j in range(1, 9):
                try:
                    m = block('competitions---rencontre-list', {**base, 'ext_poule_id': pid, 'numero_journee': str(j)})
                except Exception as e:
                    break
                ren = m.get('rencontres') or []
                if not ren:
                    break
                for r in ren:
                    allr[str(r['id'])] = r
                time.sleep(0.15)
            for r in allr.values():
                for t, ids in found:
                    if str(r.get('equipe1Id')) in ids or str(r.get('equipe2Id')) in ids:
                        overall.setdefault(t['nom'], {})
                        overall[t['nom']].setdefault(str(r['id']), {
                            'competition': c['libelle'], 'phase': phase_lib,
                            'poule': sel_poule, 'ext_pouleId': pid, **r})
        time.sleep(0.2)

out = {t: sorted(v.values(), key=lambda r: (r.get('date') or '9999')) for t, v in overall.items()}
for t, ms in out.items():
    print(len(ms), 'matchs pour', t)
os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
json.dump(out, open(os.path.join(os.path.dirname(__file__), 'data', 'history.json'),'w'), ensure_ascii=False, indent=1)
