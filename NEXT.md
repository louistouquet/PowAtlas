# Prochaine action

**SP1 continue en tâche de fond** ([plan](docs/plans/2026-10-22-sp1-archive.md), [`STATUS.md`](STATUS.md)) ; **SP2 démarre**, accord du pilote du 2026-10-27.

1. **SP1, suivi** : Arpa réglée le 2026-10-27 (issue 50 fermée). Rattrapage IFS corrigé ([PR 60](https://github.com/louistouquet/PowAtlas/pull/60)) : le pilote relance l'IFS avec `--retry-given-up` après `git pull` et colle la fin du journal (GFS immobile à 179/906 depuis le 2026-10-25, cause à trouver) (rappel).
2. **SP2, réalisation** : cadrage validé par le pilote le 2026-10-27 puis corrigé après relecture scientifique ([`docs/specs/2026-10-27-sp2-scores-design.md`](docs/specs/2026-10-27-sp2-scores-design.md), section 8 : corrections à faire confirmer par le pilote avant fusion) ; plan [`docs/plans/2026-10-27-sp2-scores.md`](docs/plans/2026-10-27-sp2-scores.md). Prochaine tâche : tâche 1 (licences vérifiées, fiches des jeux), puis tâche 2 (`powatlas publish`). Hugging Face prêt (organisation `PowAtlas`, jeux `archive` et `scores` publics et vides).
3. **Suivi de la collecte, en autonomie** ([`docs/collecte/suivi.md`](docs/collecte/suivi.md)) : bilan de santé et rappels au démarrage ; `progress` redemandé au pilote jusqu'à la fin du rattrapage (au 2026-10-27 : AIFS fini, IFS 46 %, GFS 20 %, GFS immobile depuis le 2026-10-25 : lire la fin de `data\pc-daily.log`).
4. **Mi-novembre** : priorité 2 (plan SP1, tâche 20). **Fin novembre** : horaires figés, clôture de SP1 (tâche 21).

## Échéances à ne pas oublier

Rappelées automatiquement au début de chaque session par [`docs/collecte/rappels.toml`](docs/collecte/rappels.toml).

- **2027-10-22** : les deux jetons expirent le même jour, `PowAtlas cron-job` ([guide](docs/collecte/declenchement-externe.md#configuration-en-service)) et `PowAtlas sync` du PC (`.env`, [guide](docs/collecte/installation-pc.md)) ; les renouveler avant.
- **2028-03-10** : fin de la version d'API GitHub `2022-11-28` utilisée par cron-job.org ; la changer avant.
