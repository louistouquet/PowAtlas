# Prochaine action

**SP1, suite du [plan](docs/plans/2026-10-22-sp1-archive.md)** : la collecte du cœur de score tourne sur GitHub Actions depuis le 2026-10-22 (voir [`STATUS.md`](STATUS.md)).

1. **Vérifier** qu'un run `workflow_dispatch` part chaque heure à la minute 17 (déclencheur cron-job.org créé le 2026-10-23, test réussi à 10:13 UTC).
2. **Vérifier** ([décision 0006](docs/decisions/0006-rattrapage-sur-le-pc-automatique.md)) que la tâche planifiée, enregistrée et lancée par le pilote le 2026-10-23, lance bien [`scripts/pc-daily.ps1`](scripts/pc-daily.ps1) (§ 4 du guide). Chaque jour, elle lance `sync` et une heure de rattrapage par source : AIFS et IFS finis en quelques semaines, puis GFS tenu à jour. Le lendemain, le pilote colle `Get-Content data\pc-daily.log -Tail 20` : on y lit le débit GFS. Le rattrapage AIFS lancé à la main peut être arrêté à tout moment.
3. **Mi-novembre**, après une semaine de cœur sans trou : priorité 2 (plan, tâche 20).
4. **Fin novembre** : horaires remesurés sur sept jours et figés, clôture de SP1 (plan, tâche 21) ; puis démarrage de SP2.

## Échéances à ne pas oublier

Rappelées automatiquement au début de chaque session par [`docs/collecte/rappels.toml`](docs/collecte/rappels.toml).

- **2027-10-22** : les deux jetons expirent le même jour, `PowAtlas cron-job` ([guide](docs/collecte/declenchement-externe.md#configuration-en-service)) et `PowAtlas sync` du PC (`.env`, [guide](docs/collecte/installation-pc.md)) ; les renouveler avant.
- **2028-03-10** : fin de la version d'API GitHub `2022-11-28` utilisée par cron-job.org ; la changer avant.
