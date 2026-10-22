# État du projet

*Mis à jour le 2026-10-22.*

**Rien n'est opérationnel** : aucune donnée n'est encore collectée, aucune prévision n'est produite. Les fondations (SP0) sont terminées ; la prochaine étape est SP1 (archive et observations).

## Ce qui existe et fonctionne

| Élément | État | Preuve |
|---|---|---|
| Dépôt public `louistouquet/PowAtlas` | en place | licence Apache-2.0, README anglais et français, `NOTICE`, `DATA_LICENSES.md`, `CONTRIBUTING.md` |
| Cadrage et plan de SP0 | validés par le pilote le 2026-10-21 | [`docs/specs/`](docs/specs/2026-10-21-sp0-fondations-design.md), [`docs/plans/`](docs/plans/2026-10-21-sp0-fondations.md) |
| Vérificateur de documentation `scripts/check_docs.py` | fonctionne | 33 tests `unittest` ; job CI `docs` vert sur chaque PR et sur `main` |
| Règles de travail (`CLAUDE.md`, `AGENTS.md`, `docs/methode.md`, `docs/modeles-claude.md`) | en place | PR #4, mises à jour par la clôture de SP0 |
| Décisions du pilote | 4 enregistrées | [`docs/decisions/`](docs/decisions/README.md) (0001 à 0004) |
| Skills `qualifier-source` et `experience-modele` ; agents `chercheur-sources` et `relecteur-scientifique` | en place et testés | fiche réelle `ecmwf-open-data` (PR #7) ; faille de la fiche fictive trouvée par le relecteur (PR #6) |
| Réglages GitHub | en place | jalons SP0 à SP6, étiquettes, modèles d'issues et de PR (PR #15) ; `main` protégée, vérification `docs` obligatoire, branches fusionnées supprimées automatiquement (faits par le pilote le 2026-10-22) |
| Recherche R0 : 5 rapports et 32 fiches (26 sources) | **validée par le pilote** le 2026-10-22 | PR #16 à #19 |
| Cible et feuille de route [`docs/roadmap.md`](docs/roadmap.md) | **validée par le pilote** le 2026-10-22 | PR #21 |

## Pas encore fait

Tout ce qui produit ou collecte des données : c'est SP1, à démarrer d'urgence (collecte en service avant le 1er novembre 2026). Voir [`NEXT.md`](NEXT.md).
