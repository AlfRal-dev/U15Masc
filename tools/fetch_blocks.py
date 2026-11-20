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

html = get(BASE + '/competitions/').decode('utf-8', 'replace')
key = re.search(r'data-cfk="([^"]+)"', html).group(1)
print('key:', key)

def block(name, params):
    q = urllib.parse.urlencode({'block': name, **params})
    data = get(f'{BASE}/wp-json/competitions/v1/computeBlockAttributes?{q}', 'application/json').decode('utf-8', 'replace')
    if data.startswith('{') or data.startswith('['):
        return json.loads(data)
    raw = base64.b64decode(data)
    dec = bytes(b ^ ord(key[i % len(key)]) for i, b in enumerate(raw))
    return json.loads(dec.decode('utf-8'))

params = {
    'ext_saison_id': '22',
    'url_competition_type': 'departemental',
    'url_competition': 'u15-masculins-32350',
    'ext_poule_id': '199625',
}
out = {}
for name in ['competitions---poule-selector', 'competitions---rencontre-list', 'competitions---mini-classement-or-ads']:
    try:
        out[name] = block(name, params)
        print(name, 'OK')
    except Exception as e:
        print(name, 'FAIL:', e)
        out[name] = None
with open(os.path.join(os.path.dirname(__file__), 'data', 'blocks.json'), 'w') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
