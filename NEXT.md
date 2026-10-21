# Prochaine action

**Recherche R0 en cours (tâches 7 à 11 du plan SP0)**, puis la tâche 12 (« Cible et feuille de route », à valider par le pilote) : [`docs/plans/2026-10-21-sp0-fondations.md`](docs/plans/2026-10-21-sp0-fondations.md). Suivi : issues du jalon `SP0 — Fondations`.

- Cadrage validé par le pilote le 21 octobre 2026 : [`docs/specs/2026-10-21-sp0-fondations-design.md`](docs/specs/2026-10-21-sp0-fondations-design.md).
- Méthode d'exécution : session pilote (voir [`CLAUDE.md`](CLAUDE.md)).

## À faire par le pilote (tâche 6, étape 4)

La session n'a pas été autorisée à modifier ces réglages ; à faire dans *Settings* du dépôt :
1. *Branches → Add rule* `main` : *Require a pull request before merging* ; *Require status checks to pass* : `docs` ; *Do not allow force pushes* (laisser décochée l'autorisation des *force pushes*).
2. *General → Pull Requests* : cocher *Automatically delete head branches* (et, au choix, ne garder que *Allow squash merging*).
3. Supprimer la branche fusionnée `claude/sp0-cadrage`.
