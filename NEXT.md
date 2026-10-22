# Prochaine action

**SP1 en cours : réaliser la PR 3 (socle) du [plan SP1](docs/plans/2026-10-22-sp1-archive.md)**, puis la PR 4 (ICON et workflow `collect.yml`), qui doit tourner en réel vers le 26 octobre. Urgence : ICON doit être collecté **avant le 1er novembre 2026** (24 h de conservation) ; SLF et Arpa Piemonte avant le 8 novembre ; AROME et ARPEGE avant le 15 novembre.

- Cadrage validé : [`docs/specs/2026-10-22-sp1-archive-design.md`](docs/specs/2026-10-22-sp1-archive-design.md) ; décision [0005](docs/decisions/0005-collecte-hybride-actions-et-pc.md) (collecte hybride).
- Exécution du plan : tâche par tâche, TDD, skill `scientific-coding`, une PR par groupe, CI verte, relecture par un agent.

## Ce que le pilote aura à faire (le plan le demandera au bon moment)

1. Après la PR 3 : ajouter la vérification `python` aux vérifications obligatoires de `main`.
2. Après la PR 8 (début novembre) : suivre `docs/collecte/installation-pc.md` sur `D:\Codage\PowAtlas` (Python 3.12, jeton GitHub à grain fin en lecture seule dans `.env`, tâche planifiée Windows).
3. PR 9 : lancer l'essai de débit puis le rattrapage historique sur le PC.
