# Prochaine action

**Le pilote valide la feuille de route** `docs/roadmap.md` (PR « SP0 tâche 12 », non fusionnée sans son accord) et répond à ses « Questions pour le pilote ». Ensuite : tâche 13 du plan (clôture de SP0), puis brainstorming de SP1 — urgent, l'archivage doit démarrer avant le 1er novembre 2026.

- Plan : [`docs/plans/2026-10-21-sp0-fondations.md`](docs/plans/2026-10-21-sp0-fondations.md) ; cadrage : [`docs/specs/2026-10-21-sp0-fondations-design.md`](docs/specs/2026-10-21-sp0-fondations-design.md).
- Méthode d'exécution : session pilote (voir [`CLAUDE.md`](CLAUDE.md)).

## À faire par le pilote (tâche 6, étape 4)

La session n'a pas été autorisée à modifier ces réglages ; à faire dans *Settings* du dépôt :
1. *Branches → Add rule* `main` : *Require a pull request before merging* ; *Require status checks to pass* : `docs` ; *Do not allow force pushes* (laisser décochée l'autorisation des *force pushes*).
2. *General → Pull Requests* : cocher *Automatically delete head branches* (et, au choix, ne garder que *Allow squash merging*).
3. Supprimer la branche fusionnée `claude/sp0-cadrage`.
