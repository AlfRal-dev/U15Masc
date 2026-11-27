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

tinfo_usc = f"{dif_u:+d} ({TOT_U['buts_marques']} – {TOT_U['buts_encaisses']}, {N_U} matchs)"
tinfo_adv = f"{dif_a:+d} ({TOT_A['buts_marques']} – {TOT_A['buts_encaisses']}, {N_A} matchs)"

# ------------------------------------------------- moyennes 5 derniers matchs FDME
usc_l5 = sorted(USC_SHEETS, key=lambda s: s.get('date') or '')[-5:]
adv_l5 = sorted(ADV_SHEETS, key=lambda s: s.get('date') or '')[-5:]

def l5_avg(sheets, k):
    n = len(sheets)
    return sum(s.get(k, 0) for s in sheets) / n if n else 0.0

def l5_ecart(sheets):
    return l5_avg(sheets, 'buts_marques') - l5_avg(sheets, 'buts_encaisses')

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
                 f'<td>{a_}</td><td class="hm">{fr(a_/s_)}</td><td>{cell_taux}</td></tr>')
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

bp_u, bc_u = int(stand_usc.get('butPlus', 0) or 0), int(stand_usc.get('butMoins', 0) or 0)
j_u = int(stand_usc.get('joue', 0) or 0)
bp_a, bc_a = int(adv_row.get('butPlus', 0) or 0), int(adv_row.get('butMoins', 0) or 0)
j_a = int(adv_row.get('joue', 0) or 0)

# ---- plan de match, score estimé, confrontations directes et communes
def median(vals):
    v = sorted(vals)
    n = len(v)
    if not n:
        return 0.0
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2

def sfv(v):
    s = sfp(v)
    return s[:-2] if s.endswith(',0') else s

def sfi(v):
    s = f'{round(v):+d}'
    return '0' if s in ('+0', '-0') else s

def ec_txt(v):
    return '0' if v == 0 else f'{v:+d}'

def comp_kw(sheets):
    kws = []
    for s in sheets:
        t = ((s.get('poule', '') or '') + ' ' + (s.get('competition', '') or '')).upper()
        if 'DHN' in t:
            kw = 'DHN'
        elif 'COUPE' in t or 'CDY' in t:
            kw = 'coupe'
        elif 'DPR' in t or 'PRE REGION' in t:
            kw = 'pré-région'
        else:
            kw = 'poule'
        if kw not in kws:
            kws.append(kw)
    if not kws:
        return 'poule'
    if len(kws) == 1:
        return kws[0]
    return ', '.join(kws[:-1]) + ' et ' + kws[-1]

def top_scorer(buters, total):
    if not buters or not total:
        return None, 0
    nmn, b = max(buters.items(), key=lambda kv: kv[1])
    return nmn, round(b / total * 100)

INV = {'V': 'D', 'N': 'N', 'D': 'V'}
RES_COLOR = {'V': 'var(--win)', 'N': 'var(--draw)', 'D': 'var(--loss)'}

def resline(res, s_me, s_adv, name, name_cls, lieu, meta, ecart):
    return (f'<div class="resline"><span class="badge badge-{res.lower()}">{res}</span>'
            f'<span class="scoreline"><strong>{s_me}</strong> \u2013 <strong>{s_adv}</strong></span>'
            f'<span class="vs2" style="flex:1"><b style="color:{name_cls}">{name}</b> \u00b7 {lieu}'
            f'<em class="meta">{meta}</em></span>'
            f'<b style="color:{RES_COLOR[res]}">{ecart}</b></div>')

h2h_list = [it for it in usc_hist if it['dp'][2] is not None and it['dp'][3] is not None
            and not nd(it['r']) and ADV_RE.search(it['dp'][1] or '')]

marg_u = [s.get('buts_marques', 0) - s.get('buts_encaisses', 0) for s in usc_l5]
marg_a = [s.get('buts_marques', 0) - s.get('buts_encaisses', 0) for s in adv_l5]
moy_u = sum(marg_u) / len(marg_u) if marg_u else 0.0
moy_a = sum(marg_a) / len(marg_a) if marg_a else 0.0
med_u, med_a = median(marg_u), median(marg_a)
ec_moy = (moy_u - moy_a) / 2
ec_med = (med_u - med_a) / 2
ec_ret = (ec_moy + ec_med) / 2
h2h_sentence = ''
if h2h_list:
    s_me, s_adv = h2h_list[-1]['dp'][2], h2h_list[-1]['dp'][3]
    ec_dir = s_me - s_adv
    ec_final = 0.8 * ec_ret + 0.2 * ec_dir
    h2h_sentence = (f" La confrontation directe ({sfi(ec_dir)}) compte pour 20 % de l'écart retenu,"
                    f" ce qui le porte à {sfv(round(ec_final, 1))}.")
else:
    ec_final = ec_ret
base_v = (l5_avg(adv_l5, 'buts_marques') + l5_avg(usc_l5, 'buts_encaisses')) / 2
score_estime = f'\u2248 {round(base_v + ec_final)} \u2013 {round(base_v)}'
score_trline = ('<p class="trline"><b>Pondéré par les marges :</b> sur leurs 5 derniers matchs, '
                f"l'USML a une marge moyenne de {sfv(moy_u)} (médiane {sfv(med_u)}) et {esc(ADV_T)} "
                f"de {sfv(moy_a)} (médiane {sfv(med_a)}). L'écart retenu ({sfi(ec_ret)}) est la moyenne "
                f"entre l'écart calculé avec les moyennes ({sfi(ec_moy)}) et celui calculé avec les "
                f"médianes ({sfv(ec_med)}), pour limiter le poids des gros scores.{h2h_sentence}</p>")
score_note = ('<p class="note">Estimation simple, pas une prévision. Les 5 derniers matchs '
              f'mélangent {comp_kw(usc_l5 + adv_l5)}.</p>')

if h2h_list:
    parts = [f'<details style="margin-top:16px"><summary class="mlabel">Confrontation directe ({len(h2h_list)})</summary>']
    for it in h2h_list[-5:]:
        dom, advn, s_me, s_adv = it['dp']
        r = it['r']
        meta = f"{esc(short(r.get('poule', '')))} \u00b7 {fmt_date_long(r['date'])}"
        res_u = res_letter(it['dp'])
        parts.append(resline(res_u, s_me, s_adv, 'USML', 'var(--nous)',
                             'Domicile' if dom else 'Extérieur', meta, ec_txt(s_me - s_adv)))
        parts.append(resline(INV[res_u], s_adv, s_me, esc(ADV_T), 'var(--eux)',
                             'Domicile' if dom else 'Extérieur', meta, ec_txt(s_adv - s_me)))
    parts.append('    </details>')
    h2h_details = '\n      '.join(parts)
else:
    h2h_details = ('<details style="margin-top:16px"><summary class="mlabel">Confrontation directe (0)</summary>\n'
                   '      <p class="note">Aucune confrontation directe trouvée dans les données (poule, DHN, coupe).</p>\n'
                   '    </details>')

def by_opp(hist):
    d = {}
    for it in hist:
        dom, advn, s_me, s_adv = it['dp']
        if s_me is None or (s_me == 0 and s_adv == 0) or USC_RE.search(advn or ''):
            continue
        d[advn] = it
    return d

usc_by_opp, adv_by_opp = by_opp(usc_hist), by_opp(opp_hist)
communs = sorted(set(usc_by_opp) & set(adv_by_opp))
if communs:
    parts = [f'<details style="margin-top:16px"><summary class="mlabel">Adversaires communs ({len(communs)})</summary>']
    for k, opp in enumerate(communs):
        st = 'margin-top:10px' if k == 0 else 'margin-top:12px;border-top:2px dashed var(--line);padding-top:10px'
        parts.append(f'\n      <div class="mlabel" style="{st}">{esc(short(opp))}</div>')
        for it, side in ((usc_by_opp[opp], 'us'), (adv_by_opp[opp], 'them')):
            dom, advn, s_me, s_adv = it['dp']
            r = it['r']
            meta = f"{esc(short(r.get('poule', '')))} \u00b7 {fmt_date_long(r['date'])}"
            if side == 'us':
                parts.append(resline(res_letter(it['dp']), s_me, s_adv, 'USML', 'var(--nous)',
                                     'Domicile' if dom else 'Extérieur', meta, ec_txt(s_me - s_adv)))
            else:
                res_a = INV[res_letter(it['dp'])]
                parts.append(resline(res_a, s_adv, s_me, esc(ADV_T), 'var(--eux)',
                                     'Domicile' if dom else 'Extérieur', meta, ec_txt(s_adv - s_me)))
    parts.append('\n      <p class="note">Très peu de matchs : à nuancer, et les lieux diffèrent selon les équipes.</p>\n    </details>')
    communs_details = ''.join(parts)
else:
    communs_details = ('<details style="margin-top:16px"><summary class="mlabel">Adversaires communs (0)</summary>\n'
                       '      <p class="note">Aucun adversaire commun trouvé dans les données.</p>\n'
                       '    </details>')

cles_parts = []
if N_U and N_A:
    iu = max((i for i in TM_U if i < 10), key=lambda i: (TM_U.get(i, 0) - TC_U.get(i, 0)) / N_U)
    ia = max((i for i in TM_A if i < 10), key=lambda i: (TM_A.get(i, 0) - TC_A.get(i, 0)) / N_A)
    vu_e = (TM_U.get(iu, 0) - TC_U.get(iu, 0)) / N_U
    va_e = (TM_A.get(ia, 0) - TC_A.get(ia, 0)) / N_A
    titre_tr = 'Frapper tôt' if iu <= 3 else ('Frapper au cœur du match' if iu <= 6 else 'Frapper en fin de match')
    cles_parts.append(
        f'<p><b class="n">{titre_tr} :</b> notre meilleure tranche est {tranche_lab(iu)}\u2032'
        f' ({sfp(vu_e)} en moyenne). {esc(ADV_T)} est le plus fort entre {ia*5} et {(ia+1)*5}\u2032'
        f' ({sfp(va_e)}{" seulement" if va_e < 0 else ""}) : il faudra tenir à ce moment.</p>')
    cles_parts.append(
        f"<p><b class=\"n\">Rester discipliné :</b> nous recevons {fr(u2)} sanctions de 2\u2032 par match"
        f" contre {fr(a2)} pour {esc(ADV_T)}.</p>")
    nmu, mu = top_scorer(BUT_U, TOT_U['buts_marques'])
    nma, ma = top_scorer(BUT_A, TOT_A['buts_marques'])
    keepers_usc, keepers_adv = set(), set()
    for s in USC_SHEETS:
        keepers_usc |= set(s.get('gk_our', {}).keys())
    for s in ADV_SHEETS:
        keepers_adv |= set(s.get('gk_our', {}).keys())
    note_adv = ' et joue aussi dans les buts' if nma in keepers_adv else ''
    note_usc = ' et joue aussi dans les buts' if nmu in keepers_usc else ''
    cles_parts.append(
        f'<p><b class="e">Stopper {esc(nom(nma))} :</b> il signe {ma} % des buts de {esc(ADV_T)}{note_adv}.'
        f' Chez nous, {esc(nom(nmu))} signe {mu} % des buts{note_usc} : à protéger.</p>')
plan_cles = ''.join(cles_parts)

# ---- face à face (tableau d'égalité)
def sbrow(label, vu, va, better):
    if vu == va:
        cl = cr = ''
    elif (vu > va) == (better == 'high'):
        cl, cr = ' edge', ''
    else:
        cl, cr = '', ' edge'
    return (f'<div class="sbrow"><span class="sbv l{cl}">{vu}</span>'
            f'<span class="sbl">{label}</span><span class="sbv r{cr}">{va}</span></div>')

att_u, att_a = avg(TOT_U, 'buts_marques', N_U), avg(TOT_A, 'buts_marques', N_A)
def_u, def_a = avg(TOT_U, 'buts_encaisses', N_U), avg(TOT_A, 'buts_encaisses', N_A)
gar_u, gar_a = avg(TOT_U, 'arrets', N_U), avg(TOT_A, 'arrets', N_A)
faceafacesb = ('<div class="sbhead"><span style="color:var(--nous)">USML</span><span></span>'
               f'<span style="color:var(--eux)">{esc(ADV_T)}</span></div>'
               + sbrow('Attaque (buts / match)', fr(att_u), fr(att_a), 'high')
               + sbrow('Défense (encaissés / match)', fr(def_u), fr(def_a), 'low')
               + sbrow('Gardien (arrêts / match)', fr(gar_u), fr(gar_a), 'high')
               + sbrow("Discipline (2' reçues / match)", fr(u2), fr(a2), 'low'))
if h2h_list:
    it = h2h_list[-1]
    dom, advn, s_me, s_adv = it['dp']
    d = datetime.date.fromisoformat(it['r']['date'][:10])
    lbl = f"Dernière confrontation \u00b7 {d.day} {MOIS[str(d.month)][:3]}."
    faceafacesb += sbrow(lbl, s_me, s_adv, 'high')
faceafacesb += ('<div class="sbrow sbf"><div><span class="formseries">' + form_usc + '</span></div>'
                '<span class="sbl">Forme récente (5 derniers)</span>'
                '<div><span class="formseries">' + form_adv + '</span></div></div>')

# ---- heatmap écart par tranche de 5'
def heat_cell(v, var):
    if v > 0:
        bg = f'rgba(26,158,92,{min(0.85, round(0.08 + 0.187 * v, 2)):.2f})'
    elif v < 0:
        bg = f'rgba(210,60,60,{min(0.85, round(0.08 + 0.187 * abs(v), 2)):.2f})'
    else:
        bg = 'var(--line)'
    return f'<span style="background:{bg};border-top:3px solid {var}"><b>{sfp(round(v, 1))}</b></span>'

heatmap = ('<div class="hlegend"><span><i class="dot" style="background:var(--nous)"></i>USML (ligne du haut)</span>'
           f'<span><i class="dot" style="background:var(--eux)"></i>{esc(ADV_T)} (ligne du bas)</span></div>')
for demi, lo in (('1re mi-temps', 0), ('2e mi-temps', 5)):
    cells = ''
    for i in range(lo, lo + 5):
        du = (TM_U.get(i, 0) - TC_U.get(i, 0)) / N_U if N_U else 0
        da = (TM_A.get(i, 0) - TC_A.get(i, 0)) / N_A if N_A else 0
        cells += (f'<div class="hc"><small>{tranche_lab(i)}\'</small>'
                  f'{heat_cell(du, "var(--nous)")}{heat_cell(da, "var(--eux)")}</div>')
    heatmap += f'<div class="hsl">{demi}</div><div class="hs">{cells}</div>'

# ---- sanctions de 2' par joueur
def excl_rows(sheets, key, n, total):
    tot = {}
    for s in sheets:
        for nmn, k in s.get(key, {}).items():
            tot[nmn] = tot.get(nmn, 0) + k
    top = sorted(tot.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    if not total:
        return ''
    return ''.join(
        f'<li><span class="rank">{i}</span><span class="nm">{esc(nom(nmn))}'
        f'<span class="share"><span class="track"><i style="width:{b/total*100:.0f}%"></i></span>'
        f'<em>{fr(b/total*100, 0)} %</em></span></span>'
        f'<span class="pts">{b} <small>\u00b7 {fr(b/n)}/match</small></span></li>'
        for i, (nmn, b) in enumerate(top, 1))

sanctions_usc = excl_rows(USC_SHEETS, 'excl_our', N_U, TOT_U['deux_re\u00e7ues'])
sanctions_adv = excl_rows(ADV_SHEETS, 'excl_our', N_A, TOT_A['deux_re\u00e7ues'])
if N_U == N_A:
    sanctions_note = f"Part = part des sanctions de 2' de l'équipe sur {N_U} matchs."
else:
    sanctions_note = (f"Part = part des sanctions de 2' de l'équipe ({N_U} matchs pour l'USML, "
                      f"{N_A} pour {ADV_LABEL}).")

# ---- domicile vs extérieur (5 derniers matchs)
def venue_split(sheets):
    dom, ext = [], []
    for s in sheets:
        rec = (s.get('score') or [' ', ' '])[0]
        (dom if (USC_RE.search(rec) or ADV_RE.search(rec)) else ext).append(s)
    return dom, ext

def side_avg(sheets, k):
    return sum(s.get(k, 0) for s in sheets) / len(sheets) if sheets else 0.0

def dom_metric(label, vu, va, signed=False):
    mx = max(abs(vu), abs(va)) * 1.15 or 1
    fu = sfp(vu) if signed else fr(vu)
    fa = sfp(va) if signed else fr(va)
    return (f'<div class="metric"><div class="mlabel">{label}</div><div class="comp">'
            f'<div class="side l"><span class="val">{fu}</span>'
            f'<span class="track"><i style="width:{abs(vu)/mx*100:.0f}%"></i></span></div>'
            f'<div class="side r"><span class="track"><i style="width:{abs(va)/mx*100:.0f}%"></i></span>'
            f'<span class="val">{fa}</span></div></div></div>')

usc_dom, usc_ext = venue_split(usc_l5)
adv_dom, adv_ext = venue_split(adv_l5)
u_ec = side_avg(usc_dom, 'buts_marques') - side_avg(usc_dom, 'buts_encaisses')
a_ec = side_avg(adv_ext, 'buts_marques') - side_avg(adv_ext, 'buts_encaisses')
domext = (f'<div class="comp" style="margin-bottom:6px"><div class="side l"><span class="name">USML à domicile</span></div>'
          f'<div class="side r" style="justify-content:flex-end"><span class="name">{esc(ADV_T)} à l\'extérieur</span></div></div>'
          + dom_metric('Buts marqués', side_avg(usc_dom, 'buts_marques'), side_avg(adv_ext, 'buts_marques'))
          + dom_metric('Buts encaissés', side_avg(usc_dom, 'buts_encaisses'), side_avg(adv_ext, 'buts_encaisses'))
          + dom_metric('Écart de buts', u_ec, a_ec, signed=True))
ue_m, ue_c = side_avg(usc_ext, 'buts_marques'), side_avg(usc_ext, 'buts_encaisses')
ad_m, ad_c = side_avg(adv_dom, 'buts_marques'), side_avg(adv_dom, 'buts_encaisses')
domext += (f"<p class=\"trline\">Pour comparaison : USML à l'extérieur <b>{fr(ue_m)} \u2013 {fr(ue_c)} ({sfp(ue_m-ue_c)})</b>"
           f" \u00b7 {esc(ADV_T)} à domicile <b>{fr(ad_m)} \u2013 {fr(ad_c)} ({sfp(ad_m-ad_c)})</b></p>")
poule_note = ''
if j_u and j_a:
    if j_u == j_a:
        nj = f'({j_u} matchs chacun)'
    else:
        nj = f'({j_u} pour l\'USML, {j_a} pour {ADV_LABEL})'
    poule_note = (f' En poule {esc(poule_div)} div. seulement {nj} : USML {sfp((bp_u-bc_u)/j_u)}, '
                  f'{esc(ADV_T)} {sfp((bp_a-bc_a)/j_a)}.')
domext += (f"<p class=\"note\">Moyennes par match sur les 5 derniers matchs : USML {len(usc_dom)} à domicile et "
           f"{len(usc_ext)} à l'extérieur, {esc(ADV_T)} {len(adv_dom)} à domicile et {len(adv_ext)} à l'extérieur. "
           f"Échantillon très réduit.{poule_note}</p>")

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
                   f'<td>{c["perdu"]}</td><td class="hm">{c["butPlus"]}</td><td class="hm">{c["butMoins"]}</td>'
                   f'<td>{d:+d}</td></tr>')

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
  .replace('__KPI_USC_RANK__', f"{rang(stand_usc['place'])} \u00b7 {stand_usc['point']} pts \u00b7 {esc(poule_usc_info)}")
  .replace('__KPI_ADV_RANK__', f"{rang(adv_row['place'])} \u00b7 {adv_row['point']} pts \u00b7 {esc(poule_adv_info or '3\u00b0/4\u00b0 div')}")
  .replace('__LOGO_USC__', logo_usc)
  .replace('__LOGO_ADV__', logo_adv)
  .replace('__ADV_NAME__', esc(ADV_LABEL))
  .replace('__MATCH_LINE1__', esc(match_line1))
  .replace('__MATCH_LINE2__', esc(match_line2))
  .replace('__MATCH_META__', esc(match_meta))
  .replace('__TINFO_USC_DIFF__', esc(tinfo_usc))
  .replace('__TINFO_ADV_DIFF__', esc(tinfo_adv))
  .replace('__FACEAFACE__', faceafacesb)
  .replace('__PLAN_CLES__', plan_cles)
  .replace('__SCORE_ESTIME__', score_estime)
  .replace('__SCORE_TRLINE__', score_trline)
  .replace('__SCORE_NOTE__', score_note)
  .replace('__H2H_DETAILS__', h2h_details)
  .replace('__COMMUNS_DETAILS__', communs_details)
  .replace('__BUT_USC__', but_usc)
  .replace('__BUT_ADV__', but_adv)
  .replace('__BUT_NOTE__', esc(but_note))
  .replace('__GK_ROWS__', gk_rows_all)
  .replace('__DISC_ROWS__', disc_rows)
  .replace('__DISC_NOTE__', esc(disc_note))
  .replace('__HEATMAP__', heatmap)
  .replace('__TR_USC__', tr_usc)
  .replace('__TR_ADV__', tr_adv)
  .replace('__SANCTIONS_USC__', sanctions_usc)
  .replace('__SANCTIONS_ADV__', sanctions_adv)
  .replace('__SANCTIONS_NOTE__', esc(sanctions_note))
  .replace('__DOMEXT__', domext)
  .replace('__STAND_ROWS__', stand_rows)
  .replace('__GEN__', gen)
)

out_path = os.path.join(os.path.dirname(HERE), 'index.html')
open(out_path, 'w').write(html)
print('index.html g\u00e9n\u00e9r\u00e9,', len(html), 'octets')
