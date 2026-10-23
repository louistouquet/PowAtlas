# Prochaine action

**SP1, suite du [plan](docs/plans/2026-10-22-sp1-archive.md)** : la collecte du cœur de score tourne sur GitHub Actions depuis le 2026-10-22 (voir [`STATUS.md`](STATUS.md)).

1. **Vérifier** qu'un run `workflow_dispatch` part chaque heure à la minute 17 (déclencheur cron-job.org créé le 2026-10-23, test réussi à 10:13 UTC).
2. **Pilote** : ajouter la vérification `python` aux vérifications obligatoires de `main`.
3. **Pilote** : lancer le rattrapage historique (§ 5 du guide, au moins 24 h de téléchargement au total d'après les essais IFS et AIFS, par tranches de 3 h ; AIFS d'abord, puis IFS, puis GFS, dont le débit sera mesuré par sa première tranche) et coller les sorties dans une session Claude. Installation, premier `sync` et essai de débit faits le 2026-10-23.
4. **Mi-novembre**, après une semaine de cœur sans trou : priorité 2 (plan, tâche 20).
5. **Fin novembre** : horaires remesurés sur sept jours et figés, clôture de SP1 (plan, tâche 21) ; puis démarrage de SP2.

## Échéances à ne pas oublier

- **2027-10-22** : le jeton `PowAtlas cron-job` expire ; le renouveler avant ([guide](docs/collecte/declenchement-externe.md#configuration-en-service)). Faire de même pour le jeton `PowAtlas sync` du PC à sa date d'expiration.
- **2028-03-10** : fin de la version d'API GitHub `2022-11-28` utilisée par cron-job.org ; la changer avant.
