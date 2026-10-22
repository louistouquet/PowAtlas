# État du projet

*Mis à jour le 2026-10-22.*

**La collecte quotidienne de SP1 tourne sur GitHub Actions depuis le 2026-10-22** : prévisions du cœur de score (run 00 UTC de ICON-D2, ICON-EU, AROME 0,025°, ARPEGE 0,1°, IFS 0,25°, AIFS Single) et observations qui ne restent que quelques jours en ligne. Aucune prévision ni aucun score n'est encore produit (SP2, SP3). L'archive de référence sur le PC du pilote n'existe pas encore : son installation est décrite dans [`docs/collecte/installation-pc.md`](docs/collecte/installation-pc.md).

## Ce qui existe et fonctionne

| Élément | État | Preuve |
|---|---|---|
| Dépôt public, règles de travail, vérificateur de documentation | en place depuis SP0 | CI `docs` verte sur chaque PR |
| Cadrage, décision 0005 et plan de SP1 | validés par le pilote le 2026-10-22 | [`docs/specs/2026-10-22-sp1-archive-design.md`](docs/specs/2026-10-22-sp1-archive-design.md), [`docs/plans/2026-10-22-sp1-archive.md`](docs/plans/2026-10-22-sp1-archive.md) |
| Paquet Python `powatlas` (Python 3.12) et CI `python` | en place | 192 tests `unittest` ; CI `python` verte ; hook de démarrage des sessions cloud `scripts/session-start.sh` |
| Workflow `collect.yml` (deux déclenchements par tâche, une unité par artefact, artefacts de 30 jours, issue `collecte` en cas de perte) | en service | lancements manuels du 2026-10-22, toutes les unités `complete` |
| ICON-D2, ICON-EU | collectés | run 2026-10-22 00 UTC : 6,9 Mo et 2,0 Mo |
| AROME 0,025° | collecté | runs 00 UTC du 2026-10-15 au 2026-10-22 (rattrapage de 7 jours), 6,6 à 7,3 Mo par run |
| ARPEGE 0,1° | collecté | runs 00 UTC du 2026-10-15 au 2026-10-22 (rattrapage de 7 jours), 1,2 à 1,3 Mo par run |
| IFS 0,25°, AIFS Single | collectés | runs 00 UTC du 2026-10-20 au 2026-10-22 : 0,9 à 1,1 Mo (IFS), 0,3 à 0,4 Mo (AIFS) |
| Observations : SLF (routes par station sur 7 jours), Arpa Piemonte, nivo-météo, base quotidienne Météo-France | collectées | copie du 2026-10-22 : 0,84 Mo, 22 Ko, 0,32 Mo, 1,9 Mo |
| `powatlas sync`, `status`, `backfill`, `backfill-probe` (PC du pilote) | écrits et testés | essais réels : rattrapage AIFS du 2025-12-01 et GFS de 2021 et 2026 `complete` ; pas encore lancés sur le PC |

## Pas encore fait

- **Déclenchements planifiés** : aucun n'est parti de 09:50 à 14:40 UTC le 2026-10-22 ; le premier est parti à 14:41 UTC (plan vide, tout était déjà complet). GitHub ne garantit pas ces déclenchements : la tâche `auto` ([PR 30](https://github.com/louistouquet/PowAtlas/pull/30)), appelée chaque heure par cron-job.org une fois le [guide](docs/collecte/declenchement-externe.md) suivi par le pilote, sert de filet. Essai réel de `auto` le 2026-10-22 à 15:04 UTC : les cinq tâches parcourues, toutes les unités complètes, rien à collecter.
- Archive de référence sur le PC du pilote, rattrapage historique (IFS, AIFS, GFS) : attendent l'installation du pilote.
- Priorité 2 (ICON-CH1, AROME 0,01° et niveaux de pression, IFS ENS) : après une semaine de cœur sans trou (plan, tâche 20).
- Horaires remesurés sur une semaine et figés (plan, tâche 21).
