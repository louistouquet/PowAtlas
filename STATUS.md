# État du projet

*Mis à jour le 2026-10-21.*

**Rien n'est opérationnel** : aucune donnée n'est collectée, aucune prévision n'est produite. Le projet termine sa phase de fondations (SP0).

## Ce qui existe et fonctionne

| Élément | État | Preuve |
|---|---|---|
| Dépôt public `louistouquet/PowAtlas` | en place | licence Apache-2.0, README anglais et français, `NOTICE`, `DATA_LICENSES.md`, `CONTRIBUTING.md` |
| Cadrage et plan de SP0 | validés par le pilote le 2026-10-21 | [`docs/specs/`](docs/specs/2026-10-21-sp0-fondations-design.md), [`docs/plans/`](docs/plans/2026-10-21-sp0-fondations.md) |
| Vérificateur de documentation `scripts/check_docs.py` | fonctionne | 33 tests `unittest` ; job CI `docs` vert sur chaque PR et sur `main` |
| Règles de travail (`CLAUDE.md`, `AGENTS.md`, `docs/methode.md`, `docs/modeles-claude.md`) | en place | PR #4 |
| Skills `qualifier-source` et `experience-modele` ; agents `chercheur-sources` et `relecteur-scientifique` | en place et testés | première fiche réelle `ecmwf-open-data` (PR #7) ; fiche fictive dont la faille a été trouvée par le relecteur (PR #6) |
| Réglages GitHub : jalons SP0 à SP6, étiquettes, modèles d'issues et de PR, issues de suivi | en place | PR #15 |
| Recherche R0 : 5 rapports relus (`statut: relue`) et 32 fiches sources | fusionnée | PR #16 à #19 (R0.1 à R0.5) |

## Pas encore fait (SP0)

- **Feuille de route** `docs/roadmap.md` : écrite et relue, **en attente de validation par le pilote** (tâche 12).
- **Protection de `main`** et suppression automatique des branches fusionnées : refusées à la session, à faire par le pilote (tâche 6, étape 4).
- Clôture de SP0 (tâche 13) après validation de la feuille de route.
