# Rapport U15 Masculins — USC Maisons-Laffitte HB

Page web de suivi de l'équipe U15 Masculins de l'USC Maisons-Laffitte Handball
(Championnat Départemental Yvelines — « U15M DEL 3°/4° DIV POULE 3 », saison 2026-2027),
générée à partir des données officielles de [ffhandball.fr](https://www.ffhandball.fr/competitions/saison-2026-2027-22/departemental/u15-masculins-32350/poule-199625/).

## Contenu

- `index.html` — le rapport de duel (autonome, aucun serveur requis : double-cliquer pour l'ouvrir) :
  prochain rendez-vous (Coupe des Yvelines vs HB Boucle de Seine 78 (2)), KPI de classement,
  comparaison attaque/défense/arrêts, forme récente, gardiens, discipline (2'/7 m),
  top 5 buteurs des deux équipes, rythme du match par tranches de 5 minutes, et en annexe
  classement + calendrier de notre poule.
- `tools/build.py` — régénère `index.html` depuis les données (`tools/data/`).
- `tools/fetch_history.py` — récupère l'historique complet (délaage + Coupe des Yvelines)
  de l'USC et de Versailles HBC via la recherche club de ffhandball.fr.
- `tools/fetch_fdms.py` — télécharge et analyse les feuilles de match électroniques (FDME)
  de l'USC et de HB Boucle de Seine 78 (2) : moyennes de buts/arrêts/2 min/écarts en supériorité et
  infériorité numérique, écarts de buts par tranche de 5 min, top 5 buteurs (dépend de `pypdf`).
- `tools/fetch_blocks.py` / `tools/fetch_matches.py` — récupèrent classement et calendrier
  depuis la route publique `wp-json/competitions/v1/computeBlockAttributes` de ffhandball.fr,
  décodés comme le navigateur le fait (base64 + XOR avec la clé `data-cfk` de la page).

## Mettre à jour après une journée de championnat

```bash
cd tools
python3 fetch_blocks.py      # met à jour data/blocks.json (classement, poule)
python3 fetch_matches.py     # met à jour data/rencontres.json (tous les matchs)
python3 fetch_history.py     # (optionnel) historique USC / Versailles (3)
python3 fetch_fdms.py        # (optionnel) statistiques des feuilles de match (FDME)
python3 build.py             # régénère index.html
```

## Mise à jour automatique

Un déploiement GitHub Actions (`.github/workflows/update.yml`) rafraîchit les données
lundi-dimanche (cron : 05h10, 11h10, 17h10 UTC) puis commite `index.html` si les
données ont changé. Déclenchement manuel possible : onglet *Actions* →
« Mise a jour du rapport FFHB » → *Run workflow*.

## Paramétrage

Dans `tools/build.py` : `TEAM_ID` identifie l'équipe suivie (USC Maisons-Laffitte HB).
La date de mise à jour affichée est variable `maj` (à ajuster au fil de la saison).

Données : © Ligue/Comité via FFHandball — arrêtées au 19 novembre 2026.
