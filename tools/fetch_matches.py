import base64, json, os, re, time, urllib.request, urllib.parse

BASE = 'https://www.ffhandball.fr'
UA = 'team-report-coach (fetch of public competition data)'

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

base = {'ext_saison_id':'22','url_competition_type':'departemental','url_competition':'u15-masculins-32350','ext_poule_id':'199625'}
all_ren = {}
for j in range(1, 8):
    try:
        m = block('competitions---rencontre-list', {**base, 'numero_journee': str(j)})
        ren = m.get('rencontres') or []
        for r in ren:
            all_ren[str(r['id'])] = r
        print(f'journee {j}: {len(ren)} matches')
    except Exception as e:
        print(f'journee {j} FAIL: {e}')
    time.sleep(0.3)

json.dump(sorted(all_ren.values(), key=lambda r: (r.get('journeeNumero') or '99', r.get('date') or '')), open(os.path.join(os.path.dirname(__file__), 'data', 'rencontres.json'), 'w'), ensure_ascii=False, indent=1)
print('total unique matches:', len(all_ren))
