# Prochaine action

**Le pilote valide la feuille de route** `docs/roadmap.md` (PR « SP0 tâche 12 », non fusionnée sans son accord ; ses décisions du 2026-10-21 y sont intégrées). Ensuite : tâche 13 du plan (clôture de SP0), puis brainstorming de SP1 — urgent, l'archivage doit démarrer avant le 1er novembre 2026, sur la machine du pilote.

- Plan : [`docs/plans/2026-10-21-sp0-fondations.md`](docs/plans/2026-10-21-sp0-fondations.md) ; cadrage : [`docs/specs/2026-10-21-sp0-fondations-design.md`](docs/specs/2026-10-21-sp0-fondations-design.md).
- Méthode d'exécution : session pilote (voir [`CLAUDE.md`](CLAUDE.md)).

## À faire par le pilote : réglages GitHub (tâche 6, étape 4)

Le proxy des sessions cloud refuse ces écritures (HTTP 403 « not permitted through this proxy », constaté le 2026-10-21) : elles se font dans l'interface GitHub du dépôt.
1. *Settings → Branches → Add branch protection rule* (ou *Rules → Rulesets → New ruleset*), cible `main` : cocher *Require a pull request before merging* (0 approbation requise) ; *Require status checks to pass before merging*, ajouter `docs` ; laisser **décochées** *Allow force pushes* et *Allow deletions*. Ne pas cocher *Do not allow bypassing the above settings*, pour que les fusions de Claude par PR restent possibles.
2. *Settings → General → Pull Requests* : cocher *Automatically delete head branches* ; ne garder que *Allow squash merging*.
3. *Code → Branches* : supprimer `claude/sp0-cadrage` et `claude/sp0-plan` (fusionnées par les PR #1 et #2, leur contenu est dans `main`).

## À faire par le pilote : dossier local `D:\Codage\PowAtlas`

1. Installer Git pour Windows et Python 3.12 si ce n'est pas fait.
2. `git clone https://github.com/louistouquet/PowAtlas.git D:\Codage\PowAtlas`
3. Mettre à jour avec `git pull` dans ce dossier. Les données d'archive iront dans `D:\Codage\PowAtlas\data\`, ignoré par Git ; le code d'archivage et la tâche planifiée Windows arrivent avec SP1.
