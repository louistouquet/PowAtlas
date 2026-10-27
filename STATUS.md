# État du projet

*Mis à jour le 2026-10-27.*

**La collecte quotidienne de SP1 tourne sur GitHub Actions depuis le 2026-10-22** : prévisions du cœur de score (run 00 UTC de ICON-D2, ICON-EU, AROME 0,025°, ARPEGE 0,1°, IFS 0,25°, AIFS Single) et observations qui ne restent que quelques jours en ligne. Aucune prévision ni aucun score n'est encore produit (SP2, SP3). L'archive de référence sur le PC du pilote existe depuis le 2026-10-23 ([installation](docs/collecte/installation-pc.md)) : 0,28 Go le 2026-10-27, rattrapage historique inachevé.

## Ce qui existe et fonctionne

| Élément | État | Preuve |
|---|---|---|
| Dépôt public, règles de travail, vérificateur de documentation | en place depuis SP0 | CI `docs` verte sur chaque PR |
| Cadrage, décision 0005 et plan de SP1 | validés par le pilote le 2026-10-22 | [`docs/specs/2026-10-22-sp1-archive-design.md`](docs/specs/2026-10-22-sp1-archive-design.md), [`docs/plans/2026-10-22-sp1-archive.md`](docs/plans/2026-10-22-sp1-archive.md) |
| Paquet Python `powatlas` (Python 3.12) et CI `python` | en place | 240 tests `unittest` ; CI `python` verte ; hook de démarrage des sessions cloud `scripts/session-start.sh` |
| Workflow `collect.yml` (deux déclenchements par tâche, une unité par artefact, artefacts de 30 jours, issue `collecte` en cas de perte) | en service | lancements manuels du 2026-10-22, toutes les unités `complete` |
| ICON-D2, ICON-EU | collectés | run 2026-10-22 00 UTC : 6,9 Mo et 2,0 Mo |
| AROME 0,025° | collecté | runs 00 UTC du 2026-10-15 au 2026-10-22 (rattrapage de 7 jours), 6,6 à 7,3 Mo par run |
| ARPEGE 0,1° | collecté | runs 00 UTC du 2026-10-15 au 2026-10-22 (rattrapage de 7 jours), 1,2 à 1,3 Mo par run |
| IFS 0,25°, AIFS Single | collectés | runs 00 UTC du 2026-10-20 au 2026-10-22 : 0,9 à 1,1 Mo (IFS), 0,3 à 0,4 Mo (AIFS) |
| Observations : SLF (routes par station sur 7 jours), nivo-météo, base quotidienne Météo-France sur GitHub Actions ; Arpa Piemonte sur le PC du pilote | collectées ; Arpa ne répond plus à GitHub Actions depuis le 2026-10-24, mais répond au PC du pilote : depuis le 2026-10-27, la tâche quotidienne du PC la collecte (`collect-pc`) et range les copies faites à la main (`store`) ; la copie du 2026-10-27, rangée, couvre du 20 au 26 octobre : rien de perdu ([issue 50](https://github.com/louistouquet/PowAtlas/issues/50), fermée) | copie du 2026-10-22 : 0,84 Mo, 22 Ko, 0,32 Mo, 1,9 Mo ; tests `tests/test_pc.py` |
| Suivi (bilan de santé et rappels au début de chaque session, `powatlas progress` sur le PC) | en service depuis le 2026-10-25 | procédure : [`docs/collecte/suivi.md`](docs/collecte/suivi.md) |
| `powatlas sync`, `status`, `backfill`, `backfill-probe` (PC du pilote) | écrits et testés | essais réels : rattrapage AIFS du 2025-12-01 et GFS de 2021 et 2026 `complete` ; sur le PC du pilote (Windows, Python 3.14) depuis le 2026-10-23 : premier `sync` de 38 artefacts, `status` complet les 22 et 23 octobre, tâche planifiée quotidienne créée sans droits d'administrateur, essais de débit IFS et AIFS à 4,9 et 5,0 requêtes par seconde sans `SlowDown` ; rattrapage AIFS lancé à la main le 2026-10-23 (environ 47 s par run, HTTP 503 du bucket) ; depuis la [décision 0006](docs/decisions/0006-rattrapage-sur-le-pc-automatique.md), rattrapage automatique par la tâche quotidienne, rythme qui ralentit sur 503 et partiels dus au serveur repris |

## Pas encore fait

- **Déclenchements planifiés** : tous partis le 2026-10-22 depuis le cron de 09:50, avec un retard qui baisse : 09:50 → 14:41 UTC (observations), 10:35 → 15:32 (icon-eu), 12:50 → 17:39 (meteofrance-pnt), 14:50 → 18:52 (ecmwf), 17:50 → 20:51 (observations), soit de 4 h 50 à 3 h ; le 2026-10-23, 02:35 → 07:53 (icon-d2) et 05:05 → 09:52 (icon-eu), ceux de 06:50 et 08:50 pas encore partis à 10:13. Chaque run a reconnu sa tâche et trouvé toutes les unités déjà complètes. GitHub ne garantit ni l'heure ni l'exécution de ces déclenchements : la tâche `auto` ([PR 30](https://github.com/louistouquet/PowAtlas/pull/30)), appelée chaque heure à la minute 17 par cron-job.org ([guide](docs/collecte/declenchement-externe.md), tâche créée par le pilote le 2026-10-23), sert de filet. Test du pilote le 2026-10-23 à 10:13 UTC (réponse 204) : le run a collecté les 8 unités encore à faire (AROME, ARPEGE, IFS, AIFS du jour et les 4 observations), toutes complètes en 10 min. Essai réel de `auto` le 2026-10-22 à 15:04 UTC : les cinq tâches parcourues, toutes les unités complètes, rien à collecter.
- Rattrapage historique en cours sur le PC du pilote (au 2026-10-27 : AIFS fini, IFS 207/452 soit 46 %, GFS 179/906 soit 20 %, GFS sans progrès depuis le 2026-10-25 ; runs IFS du 2025-02-26 au plus tard au 2026-02-01 au moins `missing` à cause de la lecture des extrêmes de température en tables GRIB2 34, corrigée le 2026-10-27, à reprendre par le PC) ; archive (`data`) de 0,28 Go le 2026-10-27, mesurée par le pilote, rattrapage inachevé. Le volume téléchargé (environ 185 Go au cadrage) n'est pas écrit sur le disque : le code découpe en mémoire et n'écrit que l'emprise [vérifié, lecture du code le 2026-10-27].
- Premier passage de `collect-pc` par la tâche planifiée du PC (essai à la main réussi le 2026-10-27).
- Hugging Face (organisation `PowAtlas`, jeux `archive` et `scores`) : à créer par le pilote ([guide](docs/collecte/hugging-face.md)).
- Priorité 2 (ICON-CH1, AROME 0,01° et niveaux de pression, IFS ENS) : après une semaine de cœur sans trou (plan, tâche 20).
- Horaires remesurés sur une semaine et figés (plan, tâche 21).
