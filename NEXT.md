# Prochaine action

**SP1, suite du [plan](docs/plans/2026-10-22-sp1-archive.md)** : la collecte du cœur de score tourne sur GitHub Actions depuis le 2026-10-22 (voir [`STATUS.md`](STATUS.md)).

1. **Vérifier les déclenchements planifiés** du workflow `collect` (onglet *Actions*, événement `schedule`). Le 2026-10-22, aucun n'était encore parti ; s'ils ne partent toujours pas, c'est le point à régler en premier, avant le 1er novembre. En attendant, `workflow_dispatch` (tâche `icon-d2`, `icon-eu`, `meteofrance-pnt`, `ecmwf`, `observations`) collecte à la main.
2. **Pilote** : ajouter la vérification `python` aux vérifications obligatoires de `main`.
3. **Pilote, début novembre** : suivre [`docs/collecte/installation-pc.md`](docs/collecte/installation-pc.md) sur `D:\Codage\PowAtlas` (jeton GitHub à grain fin en lecture seule dans `.env`, `sync`, `status`, essai de débit, tâche planifiée Windows), puis coller les sorties dans une session Claude ; ensuite lancer le rattrapage historique (§ 5 du guide).
4. **Mi-novembre**, après une semaine de cœur sans trou : priorité 2 (plan, tâche 20).
5. **Fin novembre** : horaires remesurés sur sept jours et figés, clôture de SP1 (plan, tâche 21) ; puis démarrage de SP2.
