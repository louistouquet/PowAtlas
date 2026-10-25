# Prochaine action

**SP1, suite du [plan](docs/plans/2026-10-22-sp1-archive.md)** : la collecte du cœur de score tourne sur GitHub Actions depuis le 2026-10-22 (voir [`STATUS.md`](STATUS.md)).

1. **Fait le 2026-10-25** : un run `workflow_dispatch` part chaque heure à la minute 17 (cron-job.org), sans trou du 2026-10-23 à 10:17 au 2026-10-25 à 14:17 UTC (API GitHub, lue le 2026-10-25) ; tous `success` sauf celui du 2026-10-24 à 18:17 (`failure`, perte d'Arpa).
2. **Suivi de la collecte, en autonomie** ([`docs/collecte/suivi.md`](docs/collecte/suivi.md)) : chaque session lit le bilan de santé et les rappels affichés au démarrage, et traite les erreurs. Les rappels redemandent au pilote `progress` jusqu'à la fin du rattrapage (au 2026-10-25 : AIFS fini, IFS 41 %, GFS 20 %) ; Arpa Piemonte est injoignable depuis le 2026-10-24, encore le 2026-10-25 à 14:50 UTC (cause probable chez le producteur, § 5 du suivi) : vérifier à chaque session s'il répond de nouveau.
3. **Mi-novembre**, après une semaine de cœur sans trou : priorité 2 (plan, tâche 20).
4. **Fin novembre** : horaires remesurés sur sept jours et figés, clôture de SP1 (plan, tâche 21) ; puis démarrage de SP2.

## Échéances à ne pas oublier

Rappelées automatiquement au début de chaque session par [`docs/collecte/rappels.toml`](docs/collecte/rappels.toml).

- **2027-10-22** : les deux jetons expirent le même jour, `PowAtlas cron-job` ([guide](docs/collecte/declenchement-externe.md#configuration-en-service)) et `PowAtlas sync` du PC (`.env`, [guide](docs/collecte/installation-pc.md)) ; les renouveler avant.
- **2028-03-10** : fin de la version d'API GitHub `2022-11-28` utilisée par cron-job.org ; la changer avant.
