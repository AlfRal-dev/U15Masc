#!/usr/bin/env python3
"""Génère index.html (rapport de duel USC vs prochain adversaire, format FDME)."""
import json, os, re, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DD = os.path.join(HERE, 'data')

data = json.load(open(os.path.join(DD, 'blocks.json')))
rencontres = json.load(open(os.path.join(DD, 'rencontres.json')))
hist_json = os.path.join(DD, 'history.json')
history = json.load(open(hist_json)) if os.path.exists(hist_json) else {}

TEAM_ID = '1846931'   # USC MAISONS-LAFFITTE HB
USC_LABEL = 'USML'
ADV_LABEL = 'Boucle de Seine (2)'
ADV_NOM = 'HB BOUCLE DE SEINE 78  (2)'
ADV_RE = re.compile(r'BOUCLE DE SEINE', re.I)
USC_RE = re.compile(r'USC MAISONS', re.I)
MOIS = {'1':'janvier','2':'février','3':'mars','4':'avril','5':'mai','6':'juin','7':'juillet',
        '8':'août','9':'septembre','10':'octobre','11':'novembre','12':'décembre'}
JOURS = {0:'lundi',1:'mardi',2:'mercredi',3:'jeudi',4:'vendredi',5:'samedi',6:'dimanche'}

SHORT = {
    'USC MAISONS-LAFFITTE HB': 'USML Maisons-Laffitte',
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
    'PLAISIR —LES CLAYES HB': 'Plaisir-Les Clayes',
    'PLAISIR -\xa0LES CLAYES HB': 'Plaisir-Les Clayes',
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
    'TS VICINOIS 88 HB': 'Ts Vicinois 88',
    'REGROUPEMENT BOUGIVAL LOUVECIENNES (U15M)': 'Bougival/Louveciennes',
    'U15M CDY 16EME DE FINALE': 'Coupe des Yvelines · 16e de finale',
    'U15M DEL 3\u00b0 / 4\u00b0 DIV POULE 3': 'U15M DEL 3\u00b0/4\u00b0 DIV · Poule 3',
    'U15M DEL 3\u00b0 / 4\u00b0 DIV POULE 4': 'U15M DEL 3\u00b0/4\u00b0 DIV · Poule 4',
    'U15M DHN POULE 8': 'U15M DHN · Poule 8',
    'U15M DHN POULE E': 'U15M DHN · Poule E',
    'U15M DHN POULE 10': 'U15M DHN · Poule 10',
    'U15M DHN POULE C': 'U15M DHN · Poule C',
    'U15M DHN POULE 7': 'U15M DHN · Poule 7',
    'U15M DHN POULE F': 'U15M DHN · Poule F',
    'U15M DPR FINALITES PLACE 1/2 - V1/V2 (20/09/26)': 'Pré-région · Finalité 1/2',
}

PAREN = re.compile(r'\s*\(.*$')

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def nom(s):
    return PAREN.split(str(s))[0].strip().title()

def short(t):
    return SHORT.get(t, t.title())

def fr(x, d=1):
    s = f'{x:.{d}f}'
    return s.replace('.', ',').replace('-0,', '0,')

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

# ---------------------------------------------------------------- classements
classements = sorted(data['competitions---mini-classement-or-ads']['classements'],
                     key=lambda c: int(c['place']))
stand_usc = next(c for c in classements if str(c['equipeId']) == TEAM_ID)

adv_row = None
adv_path = os.path.join(DD, 'blocks_adv.json')
if os.path.exists(adv_path):
    adv_data = json.load(open(adv_path))
    adv_bl = (adv_data.get('competitions---mini-classement-or-ads') or {}).get('classements') or []
    adv_row = next((c for c in sorted(adv_bl, key=lambda c: int(c['place']))
                    if ADV_RE.search(c.get('equipe_libelle',''))), None)
if adv_row is None:
    w = n = l = bp = bc = j = 0
    for r in sorted(history.get(ADV_NOM, []), key=lambda x: x.get('date') or '9999'):
        if not played(r) or nd(r) or not (ADV_RE.search(r['equipe1Libelle']) or ADV_RE.search(r['equipe2Libelle'])):
            continue
        dom = ADV_RE.search(r['equipe1Libelle']) is not None
        s_me = int(r.get('equipe1Score') if dom else r.get('equipe2Score'))
        s_adv = int(r.get('equipe2Score') if dom else r.get('equipe1Score'))
        j += 1; bp += s_me; bc += s_adv
        if s_me > s_adv: w += 1
        elif s_me == s_adv: n += 1
        else: l += 1
    adv_row = {'place': '—', 'point': str(2*w+n), 'joue': str(j), 'gagne': str(w),
               'nul': str(n), 'perdu': str(l), 'butPlus': str(bp), 'butMoins': str(bc)}

def rang(p):
    return '1ᵉʳ' if str(p) == '1' else f'{p}ᵉ'

def poule_court(libelle):
    m1 = re.search(r'POULE\s+(\S+)\s*$', libelle or '')
    m2 = re.search(r'DEL (\S.*?) DIV', libelle or '')
    parts = []
    if m2:
        parts.append(m2.group(1) + ' div')
    if m1:
        parts.append('poule ' + m1.group(1))
    return ' · '.join(parts) or (libelle or '')

poule_usc_info = poule_court((data['competitions---poule-selector'].get('selected_poule') or {}).get('libelle',''))
adv_path2 = os.path.join(DD, 'blocks_adv.json')
poule_adv_info = ''
if os.path.exists(adv_path2):
    adata = json.load(open(adv_path2))
    sp = (adata.get('competitions---poule-selector') or {}).get('selected_poule') or {}
    poule_adv_info = poule_court(sp.get('libelle',''))

# ------------------------------------------------------------------- history
def matched_libelle(r):
    for k in ('equipe1Libelle', 'equipe2Libelle'):
        if USC_RE.search(r[k]):
            return r[k]
    for k in ('equipe1Libelle', 'equipe2Libelle'):
        if ADV_RE.search(r[k]):
            return r[k]
    return None

usc_hist, opp_hist, next_items = [], [], []
_seen = set()
for team, ms in history.items():
    for r in sorted(ms, key=lambda x: x.get('date') or '9999'):
        _key = ('c', str(r.get('ext_rencontreId') or r.get('id')), str(r.get('ext_pouleId') or r.get('pouleId')))
        ml = matched_libelle(r)
        e1, e2 = r['equipe1Libelle'], r['equipe2Libelle']
        if not USC_RE.search(ml or ''):
            continue
        if _key in _seen:
            continue
        _seen.add(_key)
        dom = USC_RE.search(e1) is not None
        advn = e2 if dom else e1
        dp = (dom, advn, r.get('equipe1Score') if dom else r.get('equipe2Score'),
              r.get('equipe2Score') if dom else r.get('equipe1Score'))
        try:
            dp = (dp[0], dp[1], int(dp[2]) if dp[2] not in (None,'') else None,
                  int(dp[3]) if dp[3] not in (None,'') else None)
        except (TypeError, ValueError):
            dp = (dp[0], dp[1], None, None)
        usc_hist.append({'r': r, 'dp': dp})
        if not played(r) and r.get('date','9999') >= '2026-11-01':
            next_items.append((r['date'], 'COUPE' if 'COUPE' in r.get('competition','').upper() else 'CHAMPIONNAT', advn, dom, r))
for team, ms in history.items():
    for r in sorted(ms, key=lambda x: x.get('date') or '9999'):
        ml = matched_libelle(r)
        if USC_RE.search(ml or ''):
            continue
        if not ADV_RE.search(ml or ''):
            continue
        _key = ('c', str(r.get('ext_rencontreId') or r.get('id')), str(r.get('ext_pouleId') or r.get('pouleId')))
        e1, e2 = r['equipe1Libelle'], r['equipe2Libelle']
        dom = ADV_RE.search(e1) is not None
        advn = e2 if dom else e1
        if USC_RE.search(advn):
            continue
        if _key in _seen:
            continue
        _seen.add(_key)
        dp = (dom, advn, r.get('equipe1Score') if dom else r.get('equipe2Score'),
              r.get('equipe2Score') if dom else r.get('equipe1Score'))
        try:
            dp = (dp[0], dp[1], int(dp[2]) if dp[2] not in (None,'') else None,
                  int(dp[3]) if dp[3] not in (None,'') else None)
        except (TypeError, ValueError):
            dp = (dp[0], dp[1], None, None)
        opp_hist.append({'r': r, 'dp': dp})

usc_hist.sort(key=lambda it: it['r'].get('date') or '9999')
opp_hist.sort(key=lambda it: it['r'].get('date') or '9999')
usc_five = [it for it in usc_hist if played(it['r']) and not nd(it['r'])][-5:][::-1]
opp_five = [it for it in opp_hist if played(it['r']) and not nd(it['r'])][-5:][::-1]
next_items.sort(key=lambda x: x[0])

# ----------------------------------------------------- statistiques FDME agg
fdm_path = os.path.join(DD, 'fdm_stats.json')
fdm = json.load(open(fdm_path)) if os.path.exists(fdm_path) else {}
USC_SHEETS = fdm.get('USC', [])
ADV_SHEETS = fdm.get('ADV', [])
N_USC, N_ADV = len(USC_SHEETS), len(ADV_SHEETS)

def agg_sheets(sheets):
    n = len(sheets)
    tot = {k: sum(s.get(k, 0) for s in sheets) for k in
           ('buts_marques', 'buts_encaisses', 'arrets', 'deux_reçues', 'deux_donnees',
            'buts_7m', 'buts_7m_adv', 'avertissements')}
    tm, tc = {}, {}
    for s in sheets:
        for k, v in s.get('tranches_m', {}).items():
            tm[int(k)] = tm.get(int(k), 0) + v
        for k, v in s.get('tranches_c', {}).items():
            tc[int(k)] = tc.get(int(k), 0) + v
    buteurs = {}
    for s in sheets:
        for nom_, b in s.get('buteurs', {}).items():
            buteurs[nom_] = buteurs.get(nom_, 0) + b
    return n, tot, tm, tc, buteurs

N_U, TOT_U, TM_U, TC_U, BUT_U = agg_sheets(USC_SHEETS)
N_A, TOT_A, TM_A, TC_A, BUT_A = agg_sheets(ADV_SHEETS)

def avg(tot, k, n):
    return tot[k] / n if n else 0.0

# ---- KPI
def rank_kpi(row, poule_info, nomcarte, classe):
    pts, j = int(row['point']), int(row['joue'])
    d = int(row.get('butPlus', 0)) - int(row.get('butMoins', 0)) if row.get('butPlus') is not None else 0
    return {'classe': classe, 'nom': nomcarte, 'rang': rang(row['place']), 'pts': pts, 'j': j, 'poule': poule_info}

kpi_usc = rank_kpi(stand_usc, poule_usc_info, 'Classement USML', 'nous')
kpi_adv = rank_kpi(adv_row, poule_adv_info or '3°/4° div', 'Classement Boucle de Seine (2)', 'eux')

dif_u = TOT_U['buts_marques'] - TOT_U['buts_encaisses']
dif_a = TOT_A['buts_marques'] - TOT_A['buts_encaisses']

def kpi_card(label, value, sub, cls=''):
    c = f' {cls}' if cls else ''
    return (f'<div class="kpi{c}"><div class="label">{esc(label)}</div>'
            f'<div class="value">{esc(value)}</div><div class="sub">{sub}</div></div>')

kpis = '\n'.join([
    kpi_card('Classement USML', kpi_usc['rang'], f"{kpi_usc['pts']} pts · {kpi_usc['j']} matchs · {esc(kpi_usc['poule'])}", 'nous'),
    kpi_card('Différentiel USML', f'{dif_u:+d}', f"{TOT_U['buts_marques']} marqués / {TOT_U['buts_encaisses']} encaissés ({N_U} matchs)", 'nous'),
    kpi_card('Classement Boucle de Seine (2)', kpi_adv['rang'], f"{kpi_adv['pts']} pts · {kpi_adv['j']} matchs · {esc(kpi_adv['poule'])}", 'eux'),
    kpi_card('Différentiel Boucle de Seine (2)', f'{dif_a:+d}', f"{TOT_A['buts_marques']} marqués / {TOT_A['buts_encaisses']} encaissés ({N_A} matchs)", 'eux'),
])

# ---- comparaison attaque / défense / arrêts
def comp_row(label, vu, va, hint=''):
    mx = max(vu, va, 0.001) * 1.15
    hint = f' {hint}' if hint else ''
    return (f'<div class="metric"><div class="mlabel">{esc(label)}{hint}</div>'
            f'<div class="comp">'
            f'<div class="side l"><span class="name">USML</span><span class="val">{fr(vu)}</span>'
            f'<span class="track"><i style="width:{vu/mx*100:.0f}%"></i></span></div>'
            f'<div class="side r"><span class="track"><i style="width:{va/mx*100:.0f}%"></i></span>'
            f'<span class="val">{fr(va)}</span><span class="name">Boucle (2)</span></div>'
            f'</div></div>')

comp_rows = (comp_row('Buts marqués par match', avg(TOT_U, 'buts_marques', N_U), avg(TOT_A, 'buts_marques', N_A))
             + comp_row('Buts encaissés par match (plus bas = mieux)', avg(TOT_U, 'buts_encaisses', N_U), avg(TOT_A, 'buts_encaisses', N_A))
             + comp_row('Arrêts du gardien par match', avg(TOT_U, 'arrets', N_U), avg(TOT_A, 'arrets', N_A)))

# ---- forme
def res_letter(dp):
    s_me, s_adv = dp[2], dp[3]
    if s_me is None:
        return None
    return 'V' if s_me > s_adv else 'N' if s_me == s_adv else 'D'

html_form = lambda five: ''.join(
    f'<span class="form f-{res_letter(it["dp"]).lower()}">{res_letter(it["dp"])}</span>' for it in five)
form_usc = html_form(usc_five)
form_adv = html_form(opp_five)

def serie(five):
    if not five:
        return 'aucun match avec feuille'
    s0 = res_letter(five[0]['dp'])
    k = 0
    for it in five:
        if res_letter(it['dp']) == s0:
            k += 1
        else:
            break
    mot = {'V': 'victoire(s)', 'N': 'nul(s)', 'D': 'défaite(s)'}[s0]
    return f'{k} {mot} consécutives' if k > 1 else ('1 ' + mot[:1].upper() + mot[1:2] + (' consécutive' if k == 1 and s0 != 'N' else ''))

def hist_rows(five):
    out = []
    for i, it in enumerate(five, 1):
        r = it['r']
        dom, advn, s_me, s_adv = it['dp']
        if not played(r) or nd(r):
            continue
        res = res_letter(it['dp'])
        out.append(
            f'<li class="resline"><span class="badge badge-{res.lower()}">{res}</span>'
            f'<span class="scoreline"><strong>{s_me}</strong> – <strong>{s_adv}</strong></span>'
            f'<span class="vs2">{"à domicile" if dom else "à l’extérieur"} vs {esc(short(advn))}'
            f'<em class="meta">{esc(short(r.get("poule","")))} · {fmt_date_long(r["date"])} · {fmt_time(r["date"])}</em></span></li>')
    return ''.join(out)

usc_hist_html = hist_rows(usc_five)
adv_hist_html = hist_rows(opp_five)
form_note = (f"Série en cours — USML : {serie(usc_five)} ; Boucle de Seine (2) : {serie(opp_five)}. "
             f"Les deux équipes ont déjà joué leur phase de délavage (pré-région puis DHN) avant la poule 3°/4° division."
             )

# ---- gardiens
def gk_rows(sheets, gk_key, be_key, team_name, team_cls):
    acc = {}
    for s in sheets:
        tk = s.get(gk_key, {})
        tot = sum(tk.values())
        be = s.get(be_key, 0)
        for nmn, k in tk.items():
            e = acc.setdefault(nmn, [0, 0.0, 0])
            e[0] += k; e[2] += 1
            if tot:
                e[1] += be * k / tot
    rows = ''
    top = sorted(acc.items(), key=lambda kv: (-kv[1][2], -kv[1][0]))[:2]
    for nmn, (a_, be_, s_) in top:
        taux = a_ / (a_ + be_) * 100 if (a_ + be_) else None
        nmn_disp = esc(nom(nmn))
        cell_taux = '—' if taux is None else f'{fr(taux, 0)} %'
        rows += (f'<tr><td class="team {team_cls}">{team_name}</td><td class="team">{nmn_disp}</td>'
                 f'<td>{a_}</td><td>{fr(a_/s_)}</td><td>{cell_taux}</td></tr>')
    return rows

gk_rows_all = gk_rows(USC_SHEETS, 'gk_our', 'buts_encaisses', 'USML', '') + \
              gk_rows(ADV_SHEETS, 'gk_our', 'buts_encaisses', 'Boucle (2)', 'tag-eux')

# ---- discipline
def disc_row(label, key, share_of=None):
    vu = avg(TOT_U, key, N_U); va = avg(TOT_A, key, N_A)
    def cell(v, base):
        if not v:
            return '<b>0</b>' + (' <small>0 %</small>' if base else '')
        if base:
            return f'<b>{fr(v)}</b> <small>{fr(v / base * 100, 0)} %</small>'
        return f'<b>{fr(v)}</b>'
    bu = avg(TOT_U, share_of, N_U) if share_of else None
    ba_ = avg(TOT_A, share_of, N_A) if share_of else None
    return (f'<tr><td class="team">{esc(label)}</td><td>{cell(vu, bu)}</td><td>{cell(va, ba_)}</td></tr>')

disc_rows = (disc_row("2' reçues / match", 'deux_reçues')
             + disc_row("2' données / match", 'deux_donnees')
             + disc_row('Buts sur 7 m marqués / match', 'buts_7m')
             + disc_row('Buts sur 7 m subis / match', 'buts_7m_adv')
             + disc_row('Avertissements / match', 'avertissements'))

u2, a2 = avg(TOT_U, 'deux_reçues', N_U), avg(TOT_A, 'deux_reçues', N_A)
p2_u = "L'USML se pénalise plus que son adversaire" if u2 > a2 else "L'USML est plus disciplinée que son adversaire"
disc_note = (f"{p2_u} ({fr(u2)} contre {fr(a2)} sanctions de 2' reçues par match). "
             f"Pour les 7 m, la fédération ne publie pas les essais manqués : seul le nombre de buts "
             f"sur 7 m est disponible.")

# ---- joueurs clés
def players_rows(buters, n, start=1):
    top = sorted(buters.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    return ''.join(
        f'<li><span class="rank">{i}</span><span class="nm">{esc(nom(nmn))}</span>'
        f'<span class="pts">{b} but{"s" if b > 1 else ""} <small>· {fr(b/n)}/match</small></span></li>'
        for i, (nmn, b) in enumerate(top, start))

players_usc = players_rows(BUT_U, N_U)
players_adv = players_rows(BUT_A, N_A)

# ---- résumé de la situation
def gk_top(sheets, gk_key, be_key):
    acc = {}
    for s in sheets:
        tk = s.get(gk_key, {})
        tot = sum(tk.values())
        for nmn, k in tk.items():
            e = acc.setdefault(nmn, [0, 0])
            e[0] += k; e[1] += 1
    if not acc:
        return '—'
    nmn, (a_, n_) = sorted(acc.items(), key=lambda kv: (-kv[1][1], -kv[1][0]))[0]
    return f"{nom(nmn)} — {a_} arrêts · {n_} m."

def srow(label, u, a):
    return f'<tr><td class="team">{esc(label)}</td><td>{u}</td><td>{a}</td></tr>'

def top_buteur(buters, n):
    if not buters:
        return '—'
    nmn, b = max(buters.items(), key=lambda kv: kv[1])
    return f"{esc(nom(nmn))} — {b} buts ({fr(b/n)}/m.)" if n else f"{esc(nom(nmn))} — {b} buts"

situation_rows = (
    srow('Poule', esc(poule_usc_info), esc(poule_adv_info or '3°/4° div'))
    + srow('Classement', f"{kpi_usc['rang']} · {kpi_usc['pts']} pts · {kpi_usc['j']} matchs",
           f"{kpi_adv['rang']} · {kpi_adv['pts']} pts · {kpi_adv['j']} matchs")
    + srow('Série en cours', esc(serie(usc_five)), esc(serie(opp_five)))
    + srow('Buts marqués / match', fr(avg(TOT_U, 'buts_marques', N_U)), fr(avg(TOT_A, 'buts_marques', N_A)))
    + srow('Buts encaissés / match', fr(avg(TOT_U, 'buts_encaisses', N_U)), fr(avg(TOT_A, 'buts_encaisses', N_A)))
    + srow('Arrêts / match', fr(avg(TOT_U, 'arrets', N_U)), fr(avg(TOT_A, 'arrets', N_A)))
    + srow("2' reçues / match", fr(u2), fr(a2))
    + srow('Gardien le plus utilisé', esc(gk_top(USC_SHEETS, 'gk_our', 'buts_encaisses')),
           esc(gk_top(ADV_SHEETS, 'gk_our', 'buts_encaisses')))
    + srow('Meilleur buteur', top_buteur(BUT_U, N_U), top_buteur(BUT_A, N_A))
)

# ---- rythme par tranches de 5'
def tranche_lab(i):
    return f"{i*5}–{(i+1)*5}"

def slice_maxes(pairs):
    m = 1.0
    for tm, tc, n in pairs:
        for d in (tm, tc):
            for v in d.values():
                m = max(m, v / n if n else 0)
    return m

def rhythm_html(tm, tc, n, mx):
    cols = ''
    for i in range(13):
        if i == 12 and tm.get(i, 0) == 0 and tc.get(i, 0) == 0:
            continue
        hm = round(tm.get(i, 0) / n / mx * 80) if n else 0
        hc = round(tc.get(i, 0) / n / mx * 80) if n else 0
        cols += (f'<div class="rhcol"><div class="bars">'
                 f'<i class="barv m" style="height:{max(hm,2)}px"></i>'
                 f'<i class="barv e" style="height:{max(hc,2)}px"></i>'
                 f'</div><div class="rhlabel">{tranche_lab(i)}\'</div></div>')
    return cols

MX = slice_maxes([(TM_U, TC_U, N_U), (TM_A, TC_A, N_A)])
rhythm_usc = rhythm_html(TM_U, TC_U, N_U, MX)
rhythm_adv = rhythm_html(TM_A, TC_A, N_A, MX)

def best_worst(tm, tc, n):
    if not n:
        return ''
    def diff(i):
        return (tm.get(i, 0) - tc.get(i, 0)) / n
    bi = max((i for i in tm), key=lambda i: diff(i))
    wi = min((i for i in tm), key=lambda i: diff(i))
    def txt(i):
        return (f"{tranche_lab(i)}′ ({fr(tm.get(i,0)/n)} marqués / {fr(tc.get(i,0)/n)} encaissés)")
    return f"Meilleure tranche : <b>{txt(bi)}</b>", f"Pire tranche : <b>{txt(wi)}</b>"

bu, wu = best_worst(TM_U, TC_U, N_U)
ba, wa = best_worst(TM_A, TC_A, N_A)
tr_usc = f"USML — {bu} · {wu}"
tr_adv = f"Boucle de Seine (2) — {ba} · {wa}"

tr_tip = (f"À exploiter : frapper fort sur notre meilleure tranche "
          f"({tranche_lab(max(TM_U, key=lambda i: TM_U.get(i, 0) - TC_U.get(i, 0)))}′), et rester solides "
          f"pendant leur pic de pression ({tranche_lab(max(TM_A, key=lambda i: TM_A.get(i, 0) - TC_A.get(i, 0)))}′).")

# ------------------------------------------------------------- classement/calendrier
stand_rows = ''
for c in classements:
    nous = str(c['equipeId']) == TEAM_ID
    nnm = 'USML Maisons-Laffitte' if nous else esc(short(c['equipe_libelle']))
    cls = ' class="nous"' if nous else ''
    d = int(c['diff'])
    stand_rows += (f'<tr{cls}><td>{c["place"]}</td><td class="team {"" if nous else ""}">{nnm}</td>'
                   f'<td>{c["point"]}</td><td>{c["joue"]}</td><td>{c["gagne"]}</td><td>{c["nul"]}</td>'
                   f'<td>{c["perdu"]}</td><td>{c["butPlus"]}</td><td>{c["butMoins"]}</td>'
                   f'<td>{d:+d}</td></tr>')

def outcome(s1, s2):
    if not played({'equipe1Score': s1, 'equipe2Score': s2}):
        return None
    a, b = int(s1), int(s2)
    return 'H' if a > b else 'A' if a < b else 'N'

# ------------------------------------------------------------------- prochain match
if next_items:
    dt, tag, advn, dom, r = next_items[0]
    match_tag = 'Coupe des Yvelines · 16e de finale' if tag == 'COUPE' else f'Championnat · J{r.get("journeeNumero","")}'
    match_meta = f'{fmt_date_long(dt)} · {fmt_time(dt)} · {"à domicile" if dom else "à l’extérieur"}'
else:
    match_tag = 'Championnat'
    match_meta = 'Aucun match programmé dans les données'

situation_note = f"Prochain match : {match_tag} — {match_meta}."

maj_raw = (data['competitions---poule-selector'].get('selected_poule') or {}).get('dateDernierUpdateEnfants') or ''
maj_date = datetime.date.fromisoformat(maj_raw.strip()[:10]) if maj_raw.strip() else None
maj = f"{maj_date.day} {MOIS[str(maj_date.month)]} {maj_date.year}" if maj_date else 'inconnue'
gen = datetime.date.today().strftime('%d/%m/%Y')

html = open(os.path.join(HERE, 'template.html')).read()
html = (html
  .replace('__KPI_USC_RANK__', f"{rang(stand_usc['place'])} · {stand_usc['point']} pts · {esc(poule_usc_info)}")
  .replace('__KPI_ADV_RANK__', f"{rang(adv_row['place'])} · {adv_row['point']} pts · {esc(poule_adv_info or '3°/4° div')}")
  .replace('__MATCH_TAG__', esc(match_tag))
  .replace('__MATCH_META__', esc(match_meta))
  .replace('__KPIS__', kpis)
  .replace('__COMP_ROWS__', comp_rows)
  .replace('__N_FDM_USC__', str(N_U))
  .replace('__N_FDM_ADV__', str(N_A))
  .replace('__FORM_USC__', form_usc)
  .replace('__FORM_ADV__', form_adv)
  .replace('__USC_HIST__', usc_hist_html)
  .replace('__ADV_HIST__', adv_hist_html)
  .replace('__FORM_NOTE__', esc(form_note))
  .replace('__GK_ROWS__', gk_rows_all)
  .replace('__DISC_ROWS__', disc_rows)
  .replace('__DISC_NOTE__', esc(disc_note))
  .replace('__PLAYERS_USC__', players_usc)
  .replace('__PLAYERS_ADV__', players_adv)
  .replace('__RHYTHM_USC__', rhythm_usc)
  .replace('__RHYTHM_ADV__', rhythm_adv)
  .replace('__TR_USC__', tr_usc)
  .replace('__TR_ADV__', tr_adv)
  .replace('__TR_TIP__', esc(tr_tip))
  .replace('__STAND_ROWS__', stand_rows)
  .replace('__SITUATION_ROWS__', situation_rows)
  .replace('__SITUATION_NOTE__', esc(situation_note))
  .replace('__GEN__', gen)
  .replace('__MAJ__', maj)
)

out_path = os.path.join(os.path.dirname(HERE), 'index.html')
open(out_path, 'w').write(html)
print('index.html généré,', len(html), 'octets')
