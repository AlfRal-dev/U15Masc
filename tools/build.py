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
ADV_LABEL = 'Versailles HBC (3)'
ADV_T = 'Versailles (3)'
ADV_NOM = 'VERSAILLES HBC (3)'
ADV_RE = re.compile(r'VERSAILLES\s+HBC\s*\(3\)', re.I)
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

def tranche_lab(i):
    return f"{i*5}–{(i+1)*5}"

def played(r):
    s1, s2 = r.get('equipe1Score'), r.get('equipe2Score')
    return s1 not in (None, '') and s2 not in (None, '')

def nd(r):
    return played(r) and str(r['equipe1Score']) == '0' and str(r['equipe2Score']) == '0'

# ---------------------------------------------------------------- classements
classements = sorted(data['competitions---mini-classement-or-ads']['classements'],
                     key=lambda c: int(c['place']))
stand_usc = next(c for c in classements if str(c['equipeId']) == TEAM_ID)

adv_row = next((c for c in classements if ADV_RE.search(c.get('equipe_libelle',''))), None)
if adv_row is None:
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

sel_poule_lib = (data['competitions---poule-selector'].get('selected_poule') or {}).get('libelle','')
poule_usc_info = poule_court(sel_poule_lib)
mdiv = re.search(r'DEL (.*?)\s*DIV', sel_poule_lib or '')
poule_div = re.sub(r'\s*/\s*', '/', mdiv.group(1)).strip(' .') if mdiv else '3\u00b0/4\u00b0'
poule_division = poule_div + ' division'
adv_path2 = os.path.join(DD, 'blocks_adv.json')
poule_adv_info = poule_usc_info if adv_row is not None else ''
if not poule_adv_info and os.path.exists(adv_path2):
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
            'buts_7m', 'buts_7m_adv', 'avertissements', 'buts_sup_num', 'buts_inf_num')}
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
kpi_adv = rank_kpi(adv_row, poule_adv_info or '3°/4° div', f'Classement {ADV_LABEL}', 'eux')

dif_u = TOT_U['buts_marques'] - TOT_U['buts_encaisses']
dif_a = TOT_A['buts_marques'] - TOT_A['buts_encaisses']

def kpi_card(label, value, sub, cls=''):
    c = f' {cls}' if cls else ''
    return (f'<div class="kpi{c}"><div class="label">{esc(label)}</div>'
            f'<div class="value">{esc(value)}</div><div class="sub">{sub}</div></div>')

kpis = '\n'.join([
    kpi_card('Classement USML', kpi_usc['rang'], f"{kpi_usc['pts']} pts · {kpi_usc['j']} matchs · {esc(kpi_usc['poule'])}", 'nous'),
    kpi_card('Différentiel USML', f'{dif_u:+d}', f"{TOT_U['buts_marques']} marqués / {TOT_U['buts_encaisses']} encaissés ({N_U} matchs)", 'nous'),
    kpi_card(f'Classement {ADV_LABEL}', kpi_adv['rang'], f"{kpi_adv['pts']} pts · {kpi_adv['j']} matchs · {esc(kpi_adv['poule'])}", 'eux'),
    kpi_card(f'Différentiel {ADV_LABEL}', f'{dif_a:+d}', f"{TOT_A['buts_marques']} marqués / {TOT_A['buts_encaisses']} encaissés ({N_A} matchs)", 'eux'),
])

# ------------------------------------------------- moyennes 5 derniers matchs FDME
usc_l5 = sorted(USC_SHEETS, key=lambda s: s.get('date') or '')[-5:]
adv_l5 = sorted(ADV_SHEETS, key=lambda s: s.get('date') or '')[-5:]

def l5_avg(sheets, k):
    n = len(sheets)
    return sum(s.get(k, 0) for s in sheets) / n if n else 0.0

def l5_ecart(sheets):
    return l5_avg(sheets, 'buts_marques') - l5_avg(sheets, 'buts_encaisses')

# ---- comparaison attaque / défense / arrêts
def trend_small(t5, v, favorable_up):
    if t5 > v:
        ok, sym = favorable_up, '\u2191'
    elif t5 < v:
        ok, sym = not favorable_up, '\u2193'
    else:
        return ''
    return f'<small class="tr {"ok" if ok else "ko"}">{sym} {fr(t5)}</small>'

def comp_metric(label, vu, va, t5u=None, t5a=None, favorable_up=True):
    mx = max(vu, va, 0.001) * 1.15
    return (f'<div class="metric"><div class="mlabel">{esc(label)}</div>'
            f'<div class="comp">'
            f'<div class="side l"><span class="val">{fr(vu)}{trend_small(t5u, vu, favorable_up) if t5u is not None else ""}</span>'
            f'<span class="track"><i style="width:{vu/mx*100:.0f}%"></i></span></div>'
            f'<div class="side r"><span class="track"><i style="width:{va/mx*100:.0f}%"></i></span>'
            f'<span class="val">{fr(va)}{trend_small(t5a, va, favorable_up) if t5a is not None else ""}</span></div>'
            f'</div></div>')

comp_rows = (comp_metric('Buts marqués', avg(TOT_U, 'buts_marques', N_U), avg(TOT_A, 'buts_marques', N_A),
                         l5_avg(usc_l5, 'buts_marques'), l5_avg(adv_l5, 'buts_marques'))
             + comp_metric('Buts encaissés', avg(TOT_U, 'buts_encaisses', N_U), avg(TOT_A, 'buts_encaisses', N_A),
                           l5_avg(usc_l5, 'buts_encaisses'), l5_avg(adv_l5, 'buts_encaisses'), False)
             + comp_metric('Arrêts du gardien', avg(TOT_U, 'arrets', N_U), avg(TOT_A, 'arrets', N_A)))

# ---- forme
def res_letter(dp):
    s_me, s_adv = dp[2], dp[3]
    if s_me is None:
        return None
    return 'V' if s_me > s_adv else 'N' if s_me == s_adv else 'D'

html_form = lambda five: ''.join(
    f'<span class="form f-{res_letter(it["dp"]).lower()}">{res_letter(it["dp"])}'
    f'<small>{it["dp"][2]}-{it["dp"][3]}</small></span>' for it in five)
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
            f'<span class="vs2">{"Domicile" if dom else "Extérieur"} vs {esc(short(advn))}'
            f'<em class="meta">{esc(short(r.get("poule","")))} · {fmt_date_long(r["date"])} · {fmt_time(r["date"])}</em></span></li>')
    return ''.join(out)

usc_hist_html = hist_rows(usc_five)
adv_hist_html = hist_rows(opp_five)
form_note = (f"Série en cours — USML : {serie(usc_five)} ; {ADV_LABEL} : {serie(opp_five)}. "
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
              gk_rows(ADV_SHEETS, 'gk_our', 'buts_encaisses', ADV_T, 'tag-eux')

# ---- discipline
def sfp(v):
    s = f'{v:+.1f}'.replace('.', ',')
    return '0,0' if s in ('+0,0', '-0,0') else s

def drow(label, vu, va):
    return f'<tr><td class="team">{esc(label)}</td><td><b>{vu}</b></td><td><b>{va}</b></td></tr>'

def avg_signed(tot, key, n, neg=False):
    return sfp(-avg(tot, key, n) if neg else avg(tot, key, n)) if n else '\u2014'

disc_rows = (drow("2' reçues", fr(avg(TOT_U, 'deux_reçues', N_U)), fr(avg(TOT_A, 'deux_reçues', N_A)))
             + drow("2' données", fr(avg(TOT_U, 'deux_donnees', N_U)), fr(avg(TOT_A, 'deux_donnees', N_A)))
             + drow('7m marqués', fr(avg(TOT_U, 'buts_7m', N_U)), fr(avg(TOT_A, 'buts_7m', N_A)))
             + drow('7m subis', fr(avg(TOT_U, 'buts_7m_adv', N_U)), fr(avg(TOT_A, 'buts_7m_adv', N_A)))
             + drow('Écart net en supériorité', avg_signed(TOT_U, 'buts_sup_num', N_U), avg_signed(TOT_A, 'buts_sup_num', N_A))
             + drow('Écart net en infériorité', avg_signed(TOT_U, 'buts_inf_num', N_U, neg=True), avg_signed(TOT_A, 'buts_inf_num', N_A, neg=True)))

u2, a2 = avg(TOT_U, 'deux_reçues', N_U), avg(TOT_A, 'deux_reçues', N_A)
p2_u = "L'USML se pénalise plus que son adversaire" if u2 > a2 else "L'USML est plus disciplinée que son adversaire"
disc_note = f"{p2_u} ({fr(u2)} contre {fr(a2)} sanctions de 2' reçues par match)."

# ---- buteurs (part des buts de l'équipe)
def but_rows(buters, n, total):
    if not total:
        return ''
    top = sorted(buters.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    return ''.join(
        f'<li><span class="rank">{i}</span><span class="nm">{esc(nom(nmn))}'
        f'<span class="share"><span class="track"><i style="width:{b/total*100:.1f}%"></i></span>'
        f'<em>{fr(b/total*100, 0)} %</em></span></span>'
        f'<span class="pts">{b} but{"s" if b > 1 else ""} <small>· {fr(b/n)}/match</small></span></li>'
        for i, (nmn, b) in enumerate(top, 1))

but_usc = but_rows(BUT_U, N_U, TOT_U['buts_marques'])
but_adv = but_rows(BUT_A, N_A, TOT_A['buts_marques'])
but_note = (f"Total, moyenne par match et part des buts de l'équipe ({N_U} matchs)."
            if N_U == N_A else
            f"Total, moyenne par match et part des buts de l'équipe ({N_U} matchs pour l'USML, {N_A} pour {ADV_LABEL}).")

# ---- poule vs toutes compétitions
def poule_cell(bp, bc, j):
    if not j:
        return '<b>\u2014</b>'
    return f'<b>{fr(bp/j)} \u2013 {fr(bc/j)} ({sfp((bp-bc)/j)}) · {j} m.</b>'

def fdm_cell(sheets):
    n = len(sheets)
    if not n:
        return '<b>\u2014</b>'
    bm = sum(s.get('buts_marques', 0) for s in sheets)
    bc = sum(s.get('buts_encaisses', 0) for s in sheets)
    return f'<b>{fr(bm/n)} \u2013 {fr(bc/n)} ({sfp((bm-bc)/n)}) · {n} m.</b>'

bp_u, bc_u = int(stand_usc.get('butPlus', 0) or 0), int(stand_usc.get('butMoins', 0) or 0)
j_u = int(stand_usc.get('joue', 0) or 0)
bp_a, bc_a = int(adv_row.get('butPlus', 0) or 0), int(adv_row.get('butMoins', 0) or 0)
j_a = int(adv_row.get('joue', 0) or 0)
poule_rows = (f'<tr><td class="team">Poule {esc(poule_div)} div.</td><td>{poule_cell(bp_u, bc_u, j_u)}</td>'
              f'<td>{poule_cell(bp_a, bc_a, j_a)}</td></tr>'
              f'<tr><td class="team">Toutes compétitions</td><td>{fdm_cell(usc_l5)}</td>'
              f'<td>{fdm_cell(adv_l5)}</td></tr>')

# ---- probabilité de victoire
ec_u = avg(TOT_U, 'buts_marques', N_U) - avg(TOT_U, 'buts_encaisses', N_U)
ec_a = avg(TOT_A, 'buts_marques', N_A) - avg(TOT_A, 'buts_encaisses', N_A)
form_u, form_a = l5_ecart(usc_l5), l5_ecart(adv_l5)
next_home = next_items[0][3] if next_items else True
prob_M = (ec_u - ec_a) + 0.5 * (form_u - form_a) + (1.5 if next_home else -1.5)
prob = int(round(max(2, min(98, 50 + 0.9 * prob_M))))
prob_titre = "L'USML part favorite." if prob >= 50 else "L'USML n'est pas favorite."
prob_ecart = f"{sfp(ec_u)} par match pour l'USML contre {sfp(ec_a)} pour {ADV_T}"
prob_bar = f'<i style="width:{prob}%"></i>'

def top_buteur_share(buters, total):
    if not buters or not total:
        return '\u2014', 0
    nmn, b = max(buters.items(), key=lambda kv: kv[1])
    return esc(nom(nmn)), round(b / total * 100)

def tranche_entre(i):
    return f'entre {i*5} et {(i+1)*5}\u2032'

cles_parts = []
if N_U and N_A:
    iu = max((i for i in TM_U if i < 10), key=lambda i: (TM_U.get(i, 0) - TC_U.get(i, 0)) / N_U)
    ia = max((i for i in TM_A if i < 10), key=lambda i: (TM_A.get(i, 0) - TC_A.get(i, 0)) / N_A)
    vu_e = (TM_U.get(iu, 0) - TC_U.get(iu, 0)) / N_U
    va_e = (TM_A.get(ia, 0) - TC_A.get(ia, 0)) / N_A
    titre_tr = 'Frapper tôt' if iu <= 3 else ('Frapper au cœur du match' if iu <= 6 else 'Frapper en fin de match')
    nmu, mu = top_buteur_share(BUT_U, TOT_U['buts_marques'])
    nma, ma = top_buteur_share(BUT_A, TOT_A['buts_marques'])
    cles_parts.append(
        f'<p><b class="n">{titre_tr} :</b> notre meilleure tranche est {tranche_lab(iu)}\u2032'
        f' (écart de {sfp(vu_e)} en moyenne). {esc(ADV_T)} est au plus fort {tranche_entre(ia)}'
        f' (écart de {sfp(va_e)}{" seulement" if va_e < 0 else ""}), il faudra tenir à ce moment.</p>')
    cles_parts.append(
        f'<p><b class="n">Rester discipliné :</b> nous recevons {fr(u2)} sanctions de 2\u2032 par match'
        f' contre {fr(a2)} pour {esc(ADV_T)}.</p>')
    if ma > mu:
        fin = 'leur jeu est plus concentré sur un seul joueur.'
    else:
        fin = 'le jeu est moins concentré sur un seul joueur.'
    cles_parts.append(
        f'<p><b class="e">Marquer les bons joueurs :</b> {nmu} signe {mu} % de nos buts.'
        f' Chez {esc(ADV_T)}, {nma} en signe {ma} %, {fin}</p>')
prob_cles = ''.join(cles_parts)

# ---- rythme par tranches de 5'
def slice_maxes(pairs):
    m = 1.0
    for tm, tc, n in pairs:
        for i in range(10):
            m = max(m, abs((tm.get(i, 0) - tc.get(i, 0)) / n) if n else 0)
    return m

def rhythm_html(tmu, tcu, nu, tma, tca, na, mx):
    def val(d):
        s = f'{d:+.1f}'.replace('.', ',')
        return '0,0' if s in ('+0,0', '-0,0') else s
    cols = ''
    for i in range(10):
        du = (tmu.get(i, 0) - tcu.get(i, 0)) / nu if nu else 0
        da = (tma.get(i, 0) - tca.get(i, 0)) / na if na else 0
        hm = round(abs(du) / mx * 38) if mx else 0
        ha = round(abs(da) / mx * 38) if mx else 0
        cols += (f'<div class="rhcol"><div class="bars">'
                 f'<span class="barwrap"><i class="barv m{" neg" if du < 0 else ""}" style="height:{max(hm, 2)}px"></i></span>'
                 f'<span class="barwrap"><i class="barv e{" neg" if da < 0 else ""}" style="height:{max(ha, 2)}px"></i></span>'
                 f'</div><div class="rhvalue"><span class="vu">{val(du)}</span>'
                 f' <span class="va">{val(da)}</span></div>'
                 f'<div class="rhlabel">{tranche_lab(i)}\'</div></div>')
    return cols

MX = slice_maxes([(TM_U, TC_U, N_U), (TM_A, TC_A, N_A)])
rhythm = rhythm_html(TM_U, TC_U, N_U, TM_A, TC_A, N_A, MX)

def best_worst(tm, tc, n):
    if not n:
        return ''
    def diff(i):
        return (tm.get(i, 0) - tc.get(i, 0)) / n
    bi = max((i for i in tm if i < 10), key=lambda i: diff(i))
    wi = min((i for i in tm if i < 10), key=lambda i: diff(i))
    def txt(i):
        return (f"{tranche_lab(i)}′ ({fr(tm.get(i,0)/n)} marqués / {fr(tc.get(i,0)/n)} encaissés)")
    return f"Meilleure tranche : <b>{txt(bi)}</b>", f"Pire tranche : <b>{txt(wi)}</b>"

bu, wu = best_worst(TM_U, TC_U, N_U)
ba, wa = best_worst(TM_A, TC_A, N_A)
tr_usc = f"USML — {bu} · {wu}"
tr_adv = f"{ADV_LABEL} — {ba} · {wa}"

# ------------------------------------------------------------- classement/calendrier
stand_rows = ''
for c in classements:
    nous = str(c['equipeId']) == TEAM_ID
    adv = bool(ADV_RE.search(c.get('equipe_libelle', '')))
    nnm = 'USML Maisons-Laffitte' if nous else esc(short(c['equipe_libelle']))
    cls = ' class="nous"' if nous else (' class="eux"' if adv else '')
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
    if tag == 'COUPE':
        match_line1, match_line2 = 'Coupe des Yvelines', '16e de finale'
    elif r.get('journeeNumero'):
        match_line1, match_line2 = 'Championnat', f'Journée {r["journeeNumero"]}'
    else:
        match_line1, match_line2 = 'Championnat', 'À venir'
    match_meta = f'{fmt_date_long(dt)} · {fmt_time(dt)} · {"Domicile" if dom else "Extérieur"}'
else:
    match_line1, match_line2 = 'Championnat', 'À venir'
    match_meta = 'Aucun match programmé dans les données'


LOGO_BASE = 'https://media-logos-clubs.ffhandball.fr/128/'

def logo_img(src, alt):
    if not src:
        return ''
    return f'<img class="logo" src="{LOGO_BASE}{src.rsplit(".", 1)[0]}.webp" alt="{esc(alt)}" loading="lazy">'

logo_usc = logo_img(stand_usc.get('structure_logo'), 'USC Maisons-Laffitte HB')
logo_adv = logo_img(adv_row.get('structure_logo') if adv_row else '', ADV_LABEL)

gen = datetime.date.today().strftime('%d/%m/%Y')

html = open(os.path.join(HERE, 'template.html')).read()
html = (html
  .replace('__KPI_USC_RANK__', f"{rang(stand_usc['place'])} · {stand_usc['point']} pts · {esc(poule_usc_info)}")
  .replace('__KPI_ADV_RANK__', f"{rang(adv_row['place'])} · {adv_row['point']} pts · {esc(poule_adv_info or '3°/4° div')}")
  .replace('__LOGO_USC__', logo_usc)
  .replace('__LOGO_ADV__', logo_adv)
  .replace('__ADV_NAME__', esc(ADV_LABEL))
  .replace('__ADV_SMALL__', esc(ADV_T))
  .replace('__MATCH_LINE1__', esc(match_line1))
  .replace('__MATCH_LINE2__', esc(match_line2))
  .replace('__MATCH_META__', esc(match_meta))
  .replace('__KPIS__', kpis)
  .replace('__PROB_NUM__', f'{prob} %')
  .replace('__PROB_TITRE__', esc(prob_titre))
  .replace('__PROB_ECART__', esc(prob_ecart))
  .replace('__PROB_BAR__', prob_bar)
  .replace('__PROB_CLES__', prob_cles)
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
  .replace('__RHYTHM__', rhythm)
  .replace('__TR_USC__', tr_usc)
  .replace('__TR_ADV__', tr_adv)
  .replace('__BUT_USC__', but_usc)
  .replace('__BUT_ADV__', but_adv)
  .replace('__BUT_NOTE__', esc(but_note))
  .replace('__POULE_ROWS__', poule_rows)
  .replace('__POULE_DIVISION__', esc(poule_division))
  .replace('__STAND_ROWS__', stand_rows)
  .replace('__GEN__', gen)
)

out_path = os.path.join(os.path.dirname(HERE), 'index.html')
open(out_path, 'w').write(html)
print('index.html généré,', len(html), 'octets')
