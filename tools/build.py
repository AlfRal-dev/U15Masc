#!/usr/bin/env python3
"""Génère index.html (rapport de match) à partir des données FFHB de la poule."""
import json, os, re, datetime, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DD = os.path.join(HERE, 'data')

data = json.load(open(os.path.join(DD, 'blocks.json')))
rencontres = json.load(open(os.path.join(DD, 'rencontres.json')))
hist_json = os.path.join(DD, 'history.json')
history = json.load(open(hist_json)) if os.path.exists(hist_json) else {}

TEAM_ID = '1846931'   # USC MAISONS-LAFFITTE HB (identifiant interne FFHB, poule actuelle)
MOIS = {'1':'janvier','2':'février','3':'mars','4':'avril','5':'mai','6':'juin','7':'juillet',
        '8':'août','9':'septembre','10':'octobre','11':'novembre','12':'décembre'}
JOURS = {0:'lundi',1:'mardi',2:'mercredi',3:'jeudi',4:'vendredi',5:'samedi',6:'dimanche'}

SHORT = {
    'USC MAISONS-LAFFITTE HB': 'USC Maisons-Laffitte',
    'SUD YVELINES HB LE PERRAY RAMBOUILLET (U15M)': 'Sud Yvelines HB',
    'CA MANTES LA VILLE / HBC ROSNY (U15M)': 'CA Mantes/Rosny',
    'VERSAILLES HBC (3)': 'Versailles HBC (3)',
    'VERSAILLES HBC (2)': 'Versailles HBC (2)',
    'VERSAILLES HBC': 'Versailles HBC',
    'CO GARGENVILLE': 'CO Gargenville',
    'SQY HB TRAPPES MONTIGNY (U15M3)': 'SQY HB Trappes (3)',
    'SQY HB MONTIGNY TRAPPES (U15M2)': 'SQY HB Trappes (2)',
    'LE CHESNAY / VERSAILLES GP 78': 'Le Chesnay/Versailles',
    'LE CHESNAY / VERSAILLES GP 78 (U15M PRE REGION)': 'Le Chesnay/Versailles',
    'HB ACHERES CONFLANS (U15M PRE REGION)': 'Achères-Conflans',
    'HB ACHERES CONFLANS': 'Achères-Conflans',
    'AS HB LES MUREAUX': 'AS Les Mureaux',
    'AS POISSY HB': 'AS Poissy',
    'AS ST-CYR/FONTENAY HB 78': 'St-Cyr/Fontenay',
    'TRIEL CHANTELOUP VERNOUILLET VERNEUIL HB': 'Triel-Chanteloup-Vern.',
    'TRIEL CHANTELOUP VERNOUILLET VERNEUIL HB (2)': 'Triel-Chanteloup-Vern. (2)',
    'ELANCOURT-MAUREPAS HB': 'Élancourt-Maurepas',
    'ELANCOURT-MAUREPAS HB U15M.1': 'Élancourt-Maurepas 1',
    'PLAISIR -\u00a0LES CLAYES HB': 'Plaisir-Les Clayes',
    'GUYANCOURT HB': 'Guyancourt',
    'US HOUDAN HB': 'US Houdan',
    "HB BOIS-D'ARCY": 'Bois-d\'Arcy',
    'HB BOUCLE DE SEINE 78': 'Boucle de Seine 78',
    'HB BOUCLE DE SEINE 78  (2)': 'Boucle de Seine 78 (2)',
    'HBC CONFLANS (2)': 'HBC Conflans (2)',
    'LE CHESNAY 78 HB (2)': 'Le Chesnay (2)',
    'CLOC ACHERES': 'CLOC Achères',
    'CLOC ACHERES (2)': 'CLOC Achères (2)',
    'CELLOIS HB': 'Cellois HB',
    'U15 MASCULINS': 'Championnat U15M',
    'U15 MASCULINS COUPE DES YVELINES': 'Coupe des Yvelines',
    'U15 MASCULINS DELAYAGE PRE-REGION : POULES': 'Délaage pré-région',
    'U15 MASCULINS DELAYAGE PRE-REGION : BARRAGES': 'Délaage pré-région · barrages',
    'U15 MASCULINS DELAYAGE PRE-REGION : FINALITES 1 A 6 (19/09/26)': 'Délaage pré-région · finalités',
    'U15 MASCULINS PHASE 3 : DELAYAGE DEPARTEMENTAL HAUT NIVEAU': 'Phase 3 · délaage haut niveau',
    'U15 MASCULINS PHASE 4 : DELAYAGE DEPARTEMENTAL HAUT NIVEAU': 'Phase 4 · délaage haut niveau',
    'U15 MASCULINS PHASE 5 : DELAYAGE DEPARTEMENTAL 1ERE A 6EME DIVISION': 'Phase 5 · délaage départemental',
    'U15M DHN POULE 8': 'U15M DHN · Poule 8',
    'U15M DHN POULE E': 'U15M DHN · Poule E',
    'U15M DHN POULE 10': 'U15M DHN · Poule 10',
    'U15M DHN POULE C': 'U15M DHN · Poule C',
    'U15M DHN POULE 7': 'U15M DHN · Poule 7',
    'U15M DHN POULE F': 'U15M DHN · Poule F',
    'U15M DPR POULE A': 'U15M Pré-région · Poule A',
    'U15M DPR FINALITES PLACE 1 A 4 - MATCH 1': 'Pré-région · Finalité places 1-4',
    'U15M DPR FINALITES PLACE 1/2 - V1/V2 (20/09/26)': 'Pré-région · Finalité 1/2',
    'U15M DEL 3° / 4° DIV POULE 3': 'U15M DEL 3°/4° DIV · Poule 3',
    'U15M DEL 1° / 2° DIV POULE 1': 'U15M DEL 1°/2° DIV · Poule 1',
    'U15M CDY 16EME DE FINALE': 'Coupe des Yvelines · 16e de finale',
}

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def short(t):
    return SHORT.get(t, t.title())

def fmt_date(iso):
    d = datetime.date.fromisoformat(iso[:10])
    return f"{JOURS[d.weekday()]} {d.day} {MOIS[str(d.month)]}"

def fmt_date_long(iso):
    d = datetime.date.fromisoformat(iso[:10])
    return f"{JOURS[d.weekday()]} {d.day} {MOIS[str(d.month)]} {d.year}"

def fmt_time(iso):
    return iso[11:16].replace(':', 'h')

def played(r):
    s1, s2 = r.get('equipe1Score'), r.get('equipe2Score')
    return s1 not in (None, '') and s2 not in (None, '')

def nd(r):
    return played(r) and str(r['equipe1Score']) == '0' and str(r['equipe2Score']) == '0'

def res_from_team_view(marked, dom, s_me, s_opp):
    if s_me is None:
        return None
    if s_me == 0 and s_opp == 0:
        return 'ND'
    return 'V' if s_me > s_opp else 'N' if s_me == s_opp else 'D'

# ---------------------------------------------------------------- classement
classements = sorted(data['competitions---mini-classement-or-ads']['classements'],
                     key=lambda c: int(c['place']))
stand_usc = next(c for c in classements if str(c['equipeId']) == TEAM_ID)
adv_nom = 'VERSAILLES HBC (3)'
adv_row = next(c for c in classements if c['equipe_libelle'] == adv_nom)

def form_icons(s):
    return [{'1':'V','0':'N','-1':'D'}.get(v,'?') for v in str(s).strip().split(';')]

def form_html(xs):
    return ''.join(f'<span class="form {"f-v" if x=="V" else "f-n" if x=="N" else "f-d"}">{x}</span>' for x in xs)

stand_rows = ''
for c in classements:
    nous = str(c['equipeId']) == TEAM_ID
    nom = 'USC Maisons-Laffitte HB' if nous else esc(short(c['equipe_libelle']))
    cls = ' class="nous-row"' if nous else ''
    d = int(c['diff'])
    diff = f'{d:+d}' if d else '0'
    stand_rows += (f'<tr{cls}><td class="place">{c["place"]}</td><td class="team">{nom}</td>'
                   f'<td>{c["point"]}</td><td>{c["joue"]}</td><td>{c["gagne"]}</td><td>{c["nul"]}</td>'
                   f'<td>{c["perdu"]}</td><td>{c["butPlus"]}</td><td>{c["butMoins"]}</td>'
                   f'<td class="diff {"pos" if d>0 else "neg" if d<0 else ""}">{diff}</td>'
                   f'<td class="formcell">{form_html(form_icons(c["dernieresRencontres"]))}</td></tr>')

# ------------------------------------------------- poule actuelle (blocs FFHB)
def outcome(s1, s2):
    if not played({'equipe1Score': s1, 'equipe2Score': s2}):
        return None
    a, b = int(s1), int(s2)
    return 'H' if a > b else 'A' if a < b else 'N'

def perspective(r):
    """(domicile, adversaire, notre_score, score_adv) si le match concerne l'USC."""
    e1, e2 = r['equipe1Libelle'], r['equipe2Libelle']
    usc1 = e1 == stand_usc['equipe_libelle']
    usc2 = e2 == stand_usc['equipe_libelle']
    if not (usc1 or usc2):
        return None
    dom = usc1
    s_me = r.get('equipe1Score') if dom else r.get('equipe2Score')
    s_adv = r.get('equipe2Score') if dom else r.get('equipe1Score')
    return dom, (e2 if dom else e1), s_me, s_adv

matches = []
for r in rencontres:
    matches.append({'raw': r, 'ordre': (int(r['journeeNumero']), r['date'])})

sched_rows = ''
for m in sorted(matches, key=lambda x: x['ordre']):
    r = m['raw']
    dp = perspective(r)
    e1cls = 'team usc' if r['equipe1Libelle'] == stand_usc['equipe_libelle'] else ('team opp2' if r['equipe1Libelle'] == adv_nom else 'team')
    e2cls = 'team usc' if r['equipe2Libelle'] == stand_usc['equipe_libelle'] else ('team opp2' if r['equipe2Libelle'] == adv_nom else 'team')
    nxt = not played(r) and dp is not None and r['date'][:10] <= '2026-11-30'
    hl = ' class="next-row"' if nxt else ''
    if dp:
        dom, advn, s_me, s_adv = dp
        if not played(r):
            score = '<span class="score tbd">à jouer</span>'
            resb = '<span class="badge badge-next res-mini">à venir</span>'
        else:
            me, ad = int(s_me), int(s_adv)
            win = me > ad
            score = (f'<span class="score win">{dom and me or ad} – {dom and ad or me}</span>'
                     if win else f'<span class="score">{dom and me or ad} – {dom and ad or me}</span>')
            res = 'V' if win else ('N' if me == ad and me != 0 else 'D')
            resb = (f'<span class="badge badge-{res.lower()}">{res}</span>'
                    if not (me == 0 and ad == 0) else
                    '<span class="badge badge-next res-mini">n.d.</span>')
    else:
        res_ = outcome(r.get('equipe1Score'), r.get('equipe2Score'))
        score = (f'<span class="score">{r["equipe1Score"]} – {r["equipe2Score"]}</span>'
                 if played(r) else '<span class="score tbd">à jouer</span>')
        resb = ''
    sched_rows += (f'<tr{hl}><td class="jrn">J{r["journeeNumero"]}</td>'
                   f'<td class="date">{fmt_date(r["date"])}<span class="heure">{fmt_time(r["date"])}</span></td>'
                   f'<td class="{e1cls}">{esc(short(r["equipe1Libelle"]))}</td>'
                   f'<td class="scorecell">{score}</td>'
                   f'<td class="{e2cls}">{esc(short(r["equipe2Libelle"]))}</td>'
                   f'<td class="rescell">{resb}</td></tr>')

# ----------------------------------------------------------------- historique
USC_RE = re.compile(r'USC MAISONS', re.I)
VER_RE = re.compile(r'VERSAILLES|LE CHESNAY', re.I)

def matched_libelle(r):
    for k in ('equipe1Libelle', 'equipe2Libelle'):
        v = r[k]
        if USC_RE.search(v) or VER_RE.search(v):
            return v
    return None

def keep_opp(r):
    ml = matched_libelle(r)
    if ml is None:
        return False
    if '(2)' in ml or 'LE CHESNAY 78 HB' in ml or ml.startswith('ELANCOURT'):
        return False
    return True

def last_five_rows(rows):
    out = []
    for item in rows:
        r = item['r']
        dom, advn, s_me, s_adv = item['dp']
        if not played(r) or nd(r):
            continue
        res = 'V' if s_me > s_adv else 'N' if s_me == s_adv else 'D'
        badge = f'<span class="badge badge-{res.lower()}">{res}</span>'
        out.append(
            f'<li class="resline">{badge}'
            f'<span class="scoreline"><strong>{s_me}</strong> – <strong>{s_adv}</strong></span>'
            f'<span class="vs">{"à domicile" if dom else "à l’extérieur"} vs {esc(short(advn))}'
            f'<em class="meta">{esc(short(r.get("poule","")))} · {fmt_date_long(r["date"])} · {fmt_time(r["date"])}</em></span></li>')
    return ''.join(out)

usc_hist, opp_hist, next_items = [], [], []
_seen = set()
for team, ms in history.items():
    for r in sorted(ms, key=lambda x: x.get('date') or '9999'):
        _key = ('c', str(r.get('ext_rencontreId') or r.get('id')), str(r.get('ext_pouleId') or r.get('pouleId')))
        if _key in _seen:
            continue
        _seen.add(_key)
        ml = matched_libelle(r)
        usc = USC_RE.search(ml or '')
        if usc:
            e1, e2 = r['equipe1Libelle'], r['equipe2Libelle']
            dom = bool(USC_RE.search(e1))
            advn = e2 if dom else e1
            dp = (dom, advn, r.get('equipe1Score') if dom else r.get('equipe2Score'),
                  r.get('equipe2Score') if dom else r.get('equipe1Score'))
            s_me, s_adv = dp[2], dp[3]
            try:
                dp = (dom, advn, int(s_me) if s_me not in (None,'') else None,
                      int(s_adv) if s_adv not in (None,'') else None)
            except (TypeError, ValueError):
                dp = (dom, advn, None, None)
            item = {'r': r, 'dp': dp, 'competition': r.get('competition',''),
                    'phase': '', 'poule': r.get('poule','')}
            usc_hist.append(item)
            if not played(r) and r.get('date','9999') >= '2026-11-01':
                next_items.append((r['date'], 'COUPE DES YVELINES' if 'COUPE' in r.get('competition','').upper() else 'CHAMPIONNAT', advn, dom, r))
        elif VER_RE.search(ml or '') and keep_opp(r):
            e1, e2 = r['equipe1Libelle'], r['equipe2Libelle']
            dom = VER_RE.search(e1) is not None and USC_RE.search(e1) is None
            advn = e2 if dom else e1
            dp = (dom, advn, r.get('equipe1Score') if dom else r.get('equipe2Score'),
                  r.get('equipe2Score') if dom else r.get('equipe1Score'))
            s_me, s_adv = dp[2], dp[3]
            try:
                dp = (dom, advn, int(s_me) if s_me not in (None,'') else None,
                      int(s_adv) if s_adv not in (None,'') else None)
            except (TypeError, ValueError):
                dp = (dom, advn, None, None)
            item = {'r': r, 'dp': dp, 'competition': r.get('competition',''),
                    'phase': '', 'poule': r.get('poule','')}
            opp_hist.append(item)

usc_hist.sort(key=lambda it: it['r'].get('date') or '9999')
opp_hist.sort(key=lambda it: it['r'].get('date') or '9999')
usc_five = [it for it in usc_hist if played(it['r']) and not nd(it['r'])][-5:][::-1]
opp_five = [it for it in opp_hist if played(it['r']) and not nd(it['r'])][-5:][::-1]
next_items.sort(key=lambda x: x[0])

next_rows = []
for dt, tag, advn, dom, r in next_items[:3]:
    ncls = 'tag-coupe' if 'COUPE' in tag else ''
    next_rows.append(
        f'<div class="nrow"><span class="ntag {ncls}">{"Coupe des Yvelines" if "COUPE" in tag else "Championnat J" + str(r.get("journeeNumero",""))}</span>'
        f'<span class="nwho">{"vs" if not dom else "recevra"} {esc(short(advn))}</span>'
        f'<span class="nwhen">{"@" if dom else "@ "}{fmt_date_long(dt)}<br>{fmt_time(dt)} · {"à domicile" if dom else "à l’extérieur"}</span></div>')
next_list = ''.join(next_rows) or '<div class="nrow">Plus de rencontre programmée</div>'

usc_tot = stand_usc
adv_tot = adv_row

note_adv = (
    f"Bilan en championnat 3°/4° division : {adv_row['gagne']} victoire(s), {adv_row['nul']} nul(s), "
    f"{adv_row['perdu']} défaite(s). Le club de Versailles aligne plusieurs équipes ((2), (3)) ; "
    f"les 5 derniers matchs listés ici concernent l’équipe (3) et l’entente Le Chesnay/Versailles."
)

maj_raw = data['competitions---poule-selector']['selected_poule'].get('dateDernierUpdateEnfants') or ''
maj_date = datetime.date.fromisoformat(maj_raw.strip()[:10]) if maj_raw.strip() else None
maj = f"{maj_date.day} {MOIS[str(maj_date.month)]} {maj_date.year}" if maj_date else 'inconnue'

equipes_liens = ''.join(f'<span class="chip">{esc(short(o["libelle"]))}</span>'
                        for o in data['competitions---poule-selector']['equipe_options'])

def badge(res):
    return f'<span class="badge badge-{res.lower()}">{res}</span>'

html = open(os.path.join(HERE, 'template.html')).read()
html = (html
  .replace('__STAND_ROWS__', stand_rows)
  .replace('__SCHED_ROWS__', sched_rows)
  .replace('__NEXT_LIST__', next_list)
  .replace('__USC_HIST__', last_five_rows(usc_five))
  .replace('__ADV_HIST__', last_five_rows(opp_five))
  .replace('__USC_PTS__', usc_tot['point'])
  .replace('__USC_J__', usc_tot['joue'])
  .replace('__USC_G__', usc_tot['gagne'])
  .replace('__USC_N__', usc_tot['nul'])
  .replace('__USC_P__', usc_tot['perdu'])
  .replace('__USC_BP__', usc_tot['butPlus'])
  .replace('__USC_BC__', usc_tot['butMoins'])
  .replace('__USC_DIFF__', usc_tot['diff'])
  .replace('__USC_PLACE__', usc_tot['place'])
  .replace('__AVG_MARQUE__', f"{int(usc_tot['butPlus'])/int(usc_tot['joue']):.1f}")
  .replace('__AVG_ENCAISSE__', f"{int(usc_tot['butMoins'])/int(usc_tot['joue']):.1f}")
  .replace('__ADV_PLACE__', adv_row['place'])
  .replace('__ADV_PTS__', adv_row['point'])
  .replace('__ADV_G__', adv_row['gagne'])
  .replace('__ADV_N__', adv_row['nul'])
  .replace('__ADV_P__', adv_row['perdu'])
  .replace('__ADV_TOT__', str(len(opp_hist)))
  .replace('__ADV_BP__', adv_row['butPlus'])
  .replace('__ADV_BC__', adv_row['butMoins'])
  .replace('__ADV_DIFF__', adv_row['diff'])
  .replace('__ADV_FORM__', form_html(form_icons(adv_row['dernieresRencontres'])))
  .replace('__AVG_ADV_MARQUE__', f"{int(adv_row['butPlus'])/int(adv_row['joue']):.1f}")
  .replace('__AVG_ADV_ENCAISSE__', f"{int(adv_row['butMoins'])/int(adv_row['joue']):.1f}")
  .replace('__NOTE_ADV__', note_adv)
  .replace('__POULE__', 'U15M DEL 3°/4° DIV POULE 3')
  .replace('__MAJ__', maj)
  .replace('__EQUIPES_CHIPS__', equipes_liens)
)

out_path = os.path.join(os.path.dirname(HERE), 'index.html')
open(out_path, 'w').write(html)
print('index.html généré,', len(html), 'octets')
