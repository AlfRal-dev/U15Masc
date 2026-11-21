#!/usr/bin/env python3
"""Télécharge et agrège les feuilles de match (FDME) de l'USC et de HB Boucle de Seine 78 (2)."""
import json, os, re, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DD = os.path.join(HERE, 'data')
from pypdf import PdfReader

history = json.load(open(os.path.join(DD, 'history.json')))

USC_RE = re.compile(r'USC MAISONS', re.I)
BDS_RE = re.compile(r'BOUCLE DE SEINE', re.I)

def matched(r):
    for k in ('equipe1Libelle', 'equipe2Libelle'):
        if USC_RE.search(r[k]):
            return 'USC'
        if BDS_RE.search(r[k]):
            return 'ADV'
    return None

codes = {}
seen = set()
for team, ms in history.items():
    for r in ms:
        key = ('c', str(r.get('ext_rencontreId') or r.get('id')), str(r.get('ext_pouleId') or r.get('pouleId')))
        if key in seen:
            continue
        seen.add(key)
        s1, s2 = r.get('equipe1Score'), r.get('equipe2Score')
        if s1 in (None, '') or s2 in (None, ''):
            continue
        if str(s1) == '0' and str(s2) == '0':
            continue
        side = matched(r)
        if not side:
            continue
        code = r.get('fdmCode')
        if code:
            codes[code] = side

# association feuille -> équipes réelles + scores
meta = {}
for team, ms in history.items():
    for r in ms:
        c = r.get('fdmCode')
        if c and (r.get('equipe1Score') not in (None, '')):
            meta.setdefault(c, {
                'date': r.get('date'), 'poule': r.get('poule'),
                'competition': r.get('competition'),
                'e1': r['equipe1Libelle'], 'e2': r['equipe2Libelle'],
                's1': r['equipe1Score'], 's2': r['equipe2Score']})

def dl(code):
    path = os.path.join(DD, f'fdm_{code}.pdf')
    if os.path.exists(path):
        return path
    url = f'https://fdm.fdme.ffhandball.fr/{code[0]}/{code[1]}/{code[2]}/{code[3]}/{code}.pdf'
    req = urllib.request.Request(url, headers={'User-Agent': 'coach-report/1.0'})
    for attempt in range(3):
        try:
            data = urllib.request.urlopen(req, timeout=30).read()
            open(path, 'wb').write(data)
            time.sleep(0.4)
            return path
        except Exception as e:
            last = e; time.sleep(1+attempt)
    print(code, 'TELECHARGEMENT IMPOSSIBLE:', last)
    return None

ROSTER_LINE = re.compile(r'^(?:X\s+)?(\d{1,2})\s+(.+?)\s+(\d{10,13})\s+([A-Z]+)(.*)$')
ACTION = re.compile(r'^\s*(But(?:\s+7m)?|Arr[eê]t|2MN|Avertissement|Dis|Temps mort.*)\s+(.+)$')
TIME = re.compile(r'^(\d{2}):(\d{2})\s+(\d+)\s*-\s*(\d+)\s*$')

def parse_pdf(path, code):
    rd = PdfReader(path)
    t1 = rd.pages[0].extract_text()
    labels = {}
    rosters = {'REC': set(), 'VIS': set()}
    current = None
    expecting_label = False
    for line in t1.split('\n'):
        line = line.strip()
        if line.startswith('Club recevant'):
            current = 'REC'; expecting_label = True; continue
        if line.startswith('Club visiteur'):
            current = 'VIS'; expecting_label = True; continue
        if line.startswith('Capt') or line.startswith('D\u00e9roul') or line.startswith('Officiel'):
            expecting_label = False
            continue
        if not line:
            continue
        if expecting_label and current is not None:
            labels[current] = line
            expecting_label = False
            continue
        m = ROSTER_LINE.match(line)
        if m and current:
            rosters[current].add(m.group(2).strip())
    rec, vis = labels.get('REC', '?'), labels.get('VIS', '?')
    print(f'{code}: REC={rec} VIS={vis} joueurs REC={len(rosters["REC"])} VIS={len(rosters["VIS"])}')
    actions = []
    for page in rd.pages[1:]:
        txt = page.extract_text()
        pending = None
        for line in txt.split('\n'):
            line = line.strip()
            tm = TIME.match(line)
            if tm:
                pending = [int(tm.group(1))*60+int(tm.group(2)), int(tm.group(3)), int(tm.group(4))]
                continue
            if pending:
                am = ACTION.match(line)
                if am:
                    atype = 'but7m' if am.group(1).startswith('But 7m') else \
                            'but' if am.group(1) == 'But' else \
                            'arret' if am.group(1).startswith('Arr') else \
                            'excl2' if am.group(1) == '2MN' else \
                            'avert' if am.group(1).startswith('Avert') else \
                            'excl_dis' if am.group(1) == 'Dis' else 'autre'
                    who = am.group(2).strip()
                    side = 'REC' if who in rosters['REC'] and who not in rosters['VIS'] else \
                           'VIS' if who in rosters['VIS'] and who not in rosters['REC'] else None
                    actions.append({'t': pending[0], 's1': pending[1], 's2': pending[2],
                                    'type': atype, 'qui': who, 'cote': side})
                pending = None
    return {'code': code, 'recevant': rec, 'visiteur': vis,
            'rosters': {k: sorted(v) for k, v in rosters.items()}, 'actions': actions}

def side_of(vq):
    if vq in ('REC', 'VIS'):
        return vq
    return None

def compute(stats, our_label):
    """our_label: libellé exact de notre équipe (recevant ou visiteur de la feuille)."""
    our = 'REC' if stats['recevant'] == our_label else 'VIS'
    opp = 'VIS' if our == 'REC' else 'REC'
    a = stats['actions']
    def our_is(cote):
        return cote == our
    m = {
        'buts_marques': sum(1 for x in a if x['type'] in ('but', 'but7m') and x['cote'] == our),
        'buts_encaisses': sum(1 for x in a if x['type'] in ('but', 'but7m') and x['cote'] == opp),
        'arrets': sum(1 for x in a if x['type'] == 'arret' and x['cote'] == our),
        'deux_reçues': sum(1 for x in a if x['type'] == 'excl2' and x['cote'] == our),
        'deux_donnees': sum(1 for x in a if x['type'] == 'excl2' and x['cote'] == opp),
        'tranches': {i: 0 for i in range(13)},
    }
    for x in a:
        if x['type'] in ('but', 'but7m') and x['cote'] in (our, opp):
            minute = x['t'] // 60
            tr = min(int(minute // 5), 12)
            m['tranches'][tr] += 1 if x['cote'] == our else -1
    # supériorité / infériorité numériques
    susp = {'REC': [], 'VIS': []}
    sup = inf = 0
    for x in sorted(a, key=lambda z: z['t']):
        if x['type'] == 'excl2':
            susp[x['cote']].append(x['t'])
        if x['type'] in ('but', 'but7m') and x['cote'] in (our, opp):
            other = opp if x['cote'] == our else our
            if susp[other]:
                susp[other].pop(0)
            if x['cote'] == our and susp[opp]:
                pass
            scoring_side = x['cote']
            def active(side, t):
                return any(s <= t < s + 120 for s in susp[side])
            if scoring_side == our and active(opp, x['t']):
                sup += 1
            if scoring_side == opp and active(our, x['t']):
                inf += 1
    m['buts_sup_num'] = sup
    m['buts_inf_num'] = inf
    buteurs = {}
    for x in a:
        if x['type'] in ('but', 'but7m') and x['cote'] == our:
            buteurs[x['qui']] = buteurs.get(x['qui'], 0) + 1
    m['buteurs'] = buteurs
    return m

result = {'USC': [], 'ADV': []}
for code, side in sorted(codes.items()):
    path = dl(code)
    if not path:
        continue
    try:
        st = parse_pdf(path, code)
    except Exception as e:
        print(code, 'PARSE FAIL', e)
        continue
    mm = meta.get(code, {})
    both = [st['recevant'], st['visiteur']]
    label = None
    for cand in both:
        if USC_RE.search(cand):
            label = cand; break
    if label is None and side == 'ADV':
        cands = [c for c in both if BDS_RE.search(c)]
        label = next((c for c in cands if '(2)' in c), cands[0] if cands else None)
    if label not in both:
        print(code, 'équipe non trouvée sur la feuille:', both); continue
    stats = compute(st, label)
    assert sum(stats['buteurs'].values()) == stats['buts_marques'], \
        f'{code}: buteurs {sum(stats["buteurs"].values())} != buts {stats["buts_marques"]}'
    stats.update({'code': code, 'date': mm.get('date'), 'poule': mm.get('poule'),
                  'competition': mm.get('competition'),
                  'adversaire': st['visiteur'] if st['recevant'] == label else st['recevant'],
                  'score': [st['recevant'], st['visiteur']]})
    result[side].append(stats)
    print(code, stats['buts_marques'], stats['buts_encaisses'],
          'arrêts', stats['arrets'], '2\'', stats['deux_reçues'], '/', stats['deux_donnees'],
          'sup', stats['buts_sup_num'], 'inf', stats['buts_inf_num'])

json.dump(result, open(os.path.join(DD, 'fdm_stats.json'), 'w'), ensure_ascii=False, indent=1)
print('feuilles USC:', len(result['USC']), '/ Boucle de Seine (2):', len(result['ADV']))
