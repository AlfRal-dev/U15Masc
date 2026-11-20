#!/usr/bin/env python3
"""Génère index.html (rapport de match) à partir des données FFHB de la poule."""
import json, os, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DD = os.path.join(HERE, 'data')

data = json.load(open(os.path.join(DD, 'blocks.json')))
rencontres = json.load(open(os.path.join(DD, 'rencontres.json')))

TEAM_ID = '1846931'   # USC MAISONS-LAFFITTE HB (identifiant interne FFHB)
MOIS = {'1':'janvier','2':'février','3':'mars','4':'avril','5':'mai','6':'juin','7':'juillet',
        '8':'août','9':'septembre','10':'octobre','11':'novembre','12':'décembre'}
JOURS = {0:'lundi',1:'mardi',2:'mercredi',3:'jeudi',4:'vendredi',5:'samedi',6:'dimanche'}

def fmt_date(iso):
    d = datetime.date.fromisoformat(iso[:10])
    return f"{JOURS[d.weekday()]} {d.day} {MOIS[str(d.month)]} {d.year}"

def fmt_time(iso):
    return iso[11:16].replace(':', 'h')

def label(team_id):
    for r in rencontres:
        for side in ('1', '2'):
            if str(r[f'equipe{side}Id']) == str(team_id):
                return r[f'equipe{side}Libelle']
    return str(team_id)

def short(t):
    t = {'USC MAISONS-LAFFITTE HB': 'USC Maisons-Laffitte',
         'SUD YVELINES HB LE PERRAY RAMBOUILLET (U15M)': 'Sud Yvelines HB',
         'CA MANTES LA VILLE / HBC ROSNY (U15M)': 'CA Mantes/Rosny',
         'VERSAILLES HBC (3)': 'Versailles HBC (3)',
         'CO GARGENVILLE': 'CO Gargenville',
         'SQY HB TRAPPES MONTIGNY (U15M3)': 'SQY HB Trappes'}.get(t, t)
    return t

# ---- classement ----
classements = sorted(data['competitions---mini-classement-or-ads']['classements'],
                     key=lambda c: int(c['place']))

def form_icons(s):
    out = []
    for v in s.strip().split(';'):
        out.append({'1': 'V', '0': 'N', '-1': 'D'}.get(v, '?'))
    return out

rows = []
for c in classements:
    nous = str(c['equipeId']) == TEAM_ID
    rows.append({
        'place': c['place'], 'nom': c['equipe_libelle'], ' joue': c['joue'],
        'pts': c['point'], 'j': c['joue'], 'g': c['gagne'], 'n': c['nul'], 'p': c['perdu'],
        'bp': c['butPlus'], 'bc': c['butMoins'], 'diff': int(c['diff']),
        'form': form_icons(c['dernieresRencontres']), 'nous': nous,
    })

# ---- matches ----
def outcome(s1, s2):
    if s1 is None or s2 is None or s1 == '' or s2 == '':
        return None
    a, b = int(s1), int(s2)
    if a > b: return 'H'
    if a < b: return 'A'
    return 'N'

matches = []
for r in rencontres:
    matches.append({
        'journee': int(r['journeeNumero']), 'date': fmt_date(r['date']),
        'heure': fmt_time(r['date']),
        'e1': r['equipe1Libelle'], 'e2': r['equipe2Libelle'],
        's1': str(r['equipe1Score']) if r['equipe1Score'] is not None else '–',
        's2': str(r['equipe2Score']) if r['equipe2Score'] is not None else '–',
        'res': outcome(r['equipe1Score'], r['equipe2Score']),
        'v_points': TEAM_ID in (str(r['equipe1Id']), str(r['equipe2Id'])),
    })

# ---- équipe : résultats joués ----
mes = [m for m in matches if m['v_points']]
joues = [m for m in mes if m['res']]
stand_usc = next(c for c in classements if str(c['equipeId']) == TEAM_ID)

def res_usc(m):
    dom = m['e1'] == stand_usc['equipe_libelle']
    na, nb = int(m['s1']) if m['s1'] != '–' else 0, int(m['s2']) if m['s2'] != '–' else 0
    mf, ca = (na, nb) if dom else (nb, na)
    return ('V' if mf > ca else 'N' if mf == ca else 'D'), mf, ca, m

stats_usc = [res_usc(m) for m in joues]

# ---- prochain match / adversaire ----
prochain = next(m for m in mes if m['res'] is None)
adv_nom = prochain['e2'] if prochain['e1'] == stand_usc['equipe_libelle'] else prochain['e1']
adv_dom = prochain['e1'] == stand_usc['equipe_libelle']
adv_row = next(c for c in classements if c['equipe_libelle'] == adv_nom)
adv_matches = [res_usc({'e1': m['e1'], 'e2': m['e2'], 's1': m['s1'], 's2': m['s2']})
               for m in joues if adv_nom in (m['e1'], m['e2'])]

def date_de(m):
    for r in rencontres:
        if r['equipe1Libelle'] == m['e1'] and r['equipe2Libelle'] == m['e2']:
            return r['date']
    return ''

adv_joues = []
for r in rencontres:
    if adv_nom in (r['equipe1Libelle'], r['equipe2Libelle']) and outcome(r['equipe1Score'], r['equipe2Score']):
        dom = r['equipe1Libelle'] == adv_nom
        a, b = int(r['equipe1Score']), int(r['equipe2Score'])
        mf, ca = (a, b) if dom else (b, a)
        adv_joues.append((r['journeeNumero'], fmt_date(r['date']), dom,
                          r['equipe1Libelle'], r['equipe2Libelle'], mf, ca,
                          'V' if mf > ca else 'N' if mf == ca else 'D'))

daynames = {'USC MAISONS-LAFFITTE HB': 'USC', adv_nom: 'Adv'}
TP = environ = None  # (placeholder, unused)

def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# ---- assemblage HTML ----
def badge(res):
    return f'<span class="badge badge-{res.lower()}">{res}</span>'

def diff_cell(d):
    cls = 'pos' if d > 0 else 'neg' if d < 0 else ''
    return f'<td class="diff {cls}">{d:+d}</td>' if d else '<td class="diff">0</td>'

stand_rows = ''.join(
    f'<tr class="{"nous" if r["nous"] else ""}">'
    f'<td class="place">{r["place"]}</td>'
    f'<td class="team">{"USC Maisons-Laffitte HB"}</td>' if r['nous'] else
    '' for r in rows)
# reconstruction simple
stand_rows = ''
for r in rows:
    nom = 'USC Maisons-Laffitte HB' if r['nous'] else esc(short(r['nom']))
    cls = ' class="nous-row"' if r['nous'] else ''
    fmb = ''.join(f'<span class="form {"f-v" if x=="V" else "f-n" if x=="N" else "f-d"}">{x}</span>' for x in r['form'])
    stand_rows += (f'<tr{cls}><td class="place">{r["place"]}</td><td class="team">{nom}</td>'
                   f'<td>{r["pts"]}</td><td>{r["j"]}</td><td>{r["g"]}</td><td>{r["n"]}</td>'
                   f'<td>{r["p"]}</td><td>{r["bp"]}</td><td>{r["bc"]}</td>'
                   f'<td class="diff {"pos" if r["diff"]>0 else "neg" if r["diff"]<0 else ""}">{r["diff"]:+d}</td>'
                   f'<td class="formcell">{fmb}</td></tr>')

uscar = []
for res, mf, ca, m in stats_usc:
    dom = m['e1'] == stand_usc['equipe_libelle']
    advn = m['e2'] if dom else m['e1']
    uscar.append(
        f'<li class="resline"><span class="badge badge-{res.lower()}">{res}</span>'
        f'<span class="scoreline"><strong>{mf}</strong> – <strong>{ca}</strong></span>'
        f'<span class="vs">{"à domicile" if dom else "à l’extérieur"} vs {esc(short(advn))} '
        f'<em class="meta">J{m["journee"]} · {m["date"]}</em></span></li>')

sched_rows = ''
for m in matches:
    pt = ' class="pt"' if m['v_points'] and False else ''
    e1cls = ' team usc' if m['e1'] == stand_usc['equipe_libelle'] else (' team opp2' if m['e1'] == adv_nom else ' team')
    e2cls = ' team usc' if m['e2'] == stand_usc['equipe_libelle'] else (' team opp2' if m['e2'] == adv_nom else ' team')
    hl = ' class="next-row"' if m is prochain else ''
    done = m['res'] is not None
    if done:
        score = (f'<span class="score win">{m["s1"]} – {m["s2"]}</span>'
                 if (m['res'] == 'H' and m['e1'] == stand_usc['equipe_libelle']) or
                    (m['res'] == 'A' and m['e2'] == stand_usc['equipe_libelle'])
                 else f'<span class="score">{m["s1"]} – {m["s2"]}</span>')
        resb = ''
        if m['v_points']:
            dom = m['e1'] == stand_usc['equipe_libelle']
            r2, _, _, _ = res_usc({'e1': m['e1'], 'e2': m['e2'],
                                   's1': m['s1'] if m['s1'] != '–' else 0,
                                   's2': m['s2'] if m['s2'] != '–' else 0})
            resb = badge(r2)
        else:
            resb = ''
    else:
        score = f'<span class="score tbd">à jouer</span>'
        resb = '<span class="badge badge-next res-mini">à venir</span>'
    sched_rows += (f'<tr{hl}><td class="jrn">J{m["journee"]}</td><td class="date">{m["date"]}<span class="heure">{m["heure"]}</span></td>'
                   f'<td class="{e1cls.strip()}">{esc(short(m["e1"]))}</td>'
                   f'<td class="scorecell">{score}</td>'
                   f'<td class="{e2cls.strip()}">{esc(short(m["e2"]))}</td>'
                   f'<td class="rescell">{resb}</td></tr>')

uscar_tot = stand_usc
adv_form = ''.join(f'<span class="form {"f-v" if x=="V" else "f-n" if x=="N" else "f-d"}">{x}</span>'
                   for x in form_icons(adv_row['dernieresRencontres']))
adv_res_html = ''
for (jn, dt, dom, e1, e2, mf, ca, res) in adv_joues:
    adv_res_html += (f'<li class="resline"><span class="badge badge-{res.lower()}">{res}</span>'
                     f'<span class="scoreline"><strong>{mf}</strong> – <strong>{ca}</strong></span>'
                     f'<span class="vs">{"à domicile" if dom else "à l’extérieur"} vs '
                     f'{esc(short(e2 if dom else e1))} <em class="meta">J{jn} · {dt}</em></span></li>')

equipes_liens = ''.join(
    f'<span class="chip">{esc(short(o["libelle"]))}</span>'
    for o in data['competitions---poule-selector']['equipe_options'])

maj = '19 novembre 2026'

note_adv = (
    f"Sur ses {adv_row['joue']} derniers matchs, {esc(short(adv_nom))} marque en moyenne "
    f"{int(adv_row['butPlus'])/int(adv_row['joue']):.1f} buts et en concède "
    f"{int(adv_row['butMoins'])/int(adv_row['joue']):.1f}. "
    f"Moyennes USC : {int(uscar_tot['butPlus'])/int(uscar_tot['joue']):.1f} marqués / "
    f"{int(uscar_tot['butMoins'])/int(uscar_tot['joue']):.1f} encaissés. "
    f"Le match se joue {('à domicile' if adv_dom else 'à l’extérieur')}."
)

html = open(os.path.join(HERE, 'template.html')).read()
for k, v in list(locals().items()):
    pass  # placeholders remplacés explicitement ci-dessous

html = (html
  .replace('/*__DATA__*/', '')
  .replace('__STAND_ROWS__', stand_rows)
  .replace('__USC_RES__', ''.join(uscar))
  .replace('__USC_PTS__', uscar_tot['point'])
  .replace('__USC_J__', uscar_tot['joue'])
  .replace('__USC_G__', uscar_tot['gagne'])
  .replace('__USC_N__', uscar_tot['nul'])
  .replace('__USC_P__', uscar_tot['perdu'])
  .replace('__USC_BP__', uscar_tot['butPlus'])
  .replace('__USC_BC__', uscar_tot['butMoins'])
  .replace('__USC_DIFF__', uscar_tot['diff'])
  .replace('__USC_PLACE__', uscar_tot['place'])
  .replace('__AVG_MARQUE__', f"{int(uscar_tot['butPlus'])/int(uscar_tot['joue']):.1f}")
  .replace('__AVG_ENCAISSE__', f"{int(uscar_tot['butMoins'])/int(uscar_tot['joue']):.1f}")
  .replace('__NEXT_J__', f"J{prochain['journee']}")
  .replace('__NEXT_DATE__', prochain['date'])
  .replace('__NEXT_HEURE__', prochain['heure'])
  .replace('__NEXT_DOM__', 'à domicile' if adv_dom else 'à l’extérieur')
  .replace('__ADV_NOM__', esc(short(adv_nom)))
  .replace('__ADV_NOM_FULL__', esc(adv_nom))
  .replace('__ADV_PLACE__', adv_row['place'])
  .replace('__ADV_PTS__', adv_row['point'])
  .replace('__ADV_J__', adv_row['joue'])
  .replace('__ADV_G__', adv_row['gagne'])
  .replace('__ADV_N__', adv_row['nul'])
  .replace('__ADV_P__', adv_row['perdu'])
  .replace('__ADV_BP__', adv_row['butPlus'])
  .replace('__ADV_BC__', adv_row['butMoins'])
  .replace('__ADV_DIFF__', adv_row['diff'])
  .replace('__ADV_RES__', adv_res_html)
  .replace('__ADV_FORM__', adv_form)
  .replace('__NOTE_ADV__', note_adv)
  .replace('__AVG_ADV_MARQUE__', f"{int(adv_row['butPlus'])/int(adv_row['joue']):.1f}")
  .replace('__AVG_ADV_ENCAISSE__', f"{int(adv_row['butMoins'])/int(adv_row['joue']):.1f}")
  .replace('__SCHED_ROWS__', sched_rows)
  .replace('__POULE__', 'U15M DEL 3°/4° DIV POULE 3')
  .replace('__MAJ__', maj)
  .replace('__EQUIPES_CHIPS__', equipes_liens)
)

open(os.path.join(os.path.dirname(HERE), 'index.html'), 'w').write(html)
print('index.html généré,', len(html), 'octets')
