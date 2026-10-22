# Prochaine action

**SP1, suite du [plan](docs/plans/2026-10-22-sp1-archive.md)** : la collecte du cœur de score tourne sur GitHub Actions depuis le 2026-10-22 (voir [`STATUS.md`](STATUS.md)).

1. **Pilote, dès que possible** : créer le déclencheur horaire sur cron-job.org ([`docs/collecte/declenchement-externe.md`](docs/collecte/declenchement-externe.md)), puis demander à une session Claude de vérifier qu'un run `workflow_dispatch` part chaque heure à la minute 17. Les planifications GitHub ont démarré le 2026-10-22 à 14:41 UTC, sans garantie d'heure ni d'exécution.
2. **Pilote** : ajouter la vérification `python` aux vérifications obligatoires de `main`.
3. **Pilote, début novembre** : suivre [`docs/collecte/installation-pc.md`](docs/collecte/installation-pc.md) sur `D:\Codage\PowAtlas` (jeton GitHub à grain fin en lecture seule dans `.env`, `sync`, `status`, essai de débit, tâche planifiée Windows), puis coller les sorties dans une session Claude ; ensuite lancer le rattrapage historique (§ 5 du guide).
4. **Mi-novembre**, après une semaine de cœur sans trou : priorité 2 (plan, tâche 20).
5. **Fin novembre** : horaires remesurés sur sept jours et figés, clôture de SP1 (plan, tâche 21) ; puis démarrage de SP2.
