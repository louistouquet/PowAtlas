# Prochaine action

**SP1 continue en tâche de fond** ([plan](docs/plans/2026-10-22-sp1-archive.md), [`STATUS.md`](STATUS.md)) ; **SP2 démarre**, accord du pilote du 2026-10-27.

1. **Arpa Piemonte par le PC : vérification** (SP1). Depuis le 2026-10-27, Arpa est dans la tâche `pc` du catalogue : la tâche quotidienne du PC la collecte (`collect-pc`) et range les copies faites à la main (`store`), plus GitHub Actions ([`suivi.md`](docs/collecte/suivi.md#5-constats-en-cours), § 5). Reste à recevoir du pilote la sortie de `store`, `dates` et `collect-pc` (rappel), puis à fermer l'[issue 50](https://github.com/louistouquet/PowAtlas/issues/50) avec les jours couverts.
2. **SP2, cadrage** (skill *brainstorming*, puis `docs/specs/AAAA-MM-JJ-sp2-scores-design.md`, validé par le pilote, puis plan) : tableau public des scores de la neige fraîche des modèles bruts ([`roadmap.md`](docs/roadmap.md), « Vérité terrain et tableau des scores »).
   - **Décidé par le pilote le 2026-10-27** (à reporter dans une décision 0007 avec le cadrage) :
     - un seul code, l'historique d'abord, puis la saison 2026-27 ;
     - calcul des scores sur le PC du pilote.
   - **Proposé, à confirmer au cadrage** :
     - historique = IFS, AIFS, GFS sur les saisons rattrapées (2024-25 et 2025-26), dès la fin du rattrapage ;
     - saison 2026-27 = tous les modèles collectés (ICON-D2, ICON-EU, AROME, ARPEGE, IFS, AIFS, GFS) ;
     - une sous-commande (par exemple `powatlas score`, à écrire) dans la tâche quotidienne du PC ;
     - seuls les tableaux de scores publiés. L'archive pesait 0,28 Go le 2026-10-27, rattrapage inachevé.
   - **Questions encore ouvertes, une à la fois** :
     - où publier les scores (dépôt, GitHub Pages, Hugging Face), compte tenu de la règle « aucune donnée dans Git » ;
     - observations historiques à rapatrier pour 2024-26 et pour la climatologie (base quotidienne `HNEIGEF` depuis 1996, Arpa `meteoidro`, SLF) ;
     - conversion de la neige prévue en hauteur ;
     - seuils et longueur des blocs ;
     - rôle des saisons ;
     - lien avec le skill `verifier-prevision` prévu par la feuille de route.
3. **Suivi de la collecte, en autonomie** ([`docs/collecte/suivi.md`](docs/collecte/suivi.md)) : bilan de santé et rappels au démarrage ; `progress` redemandé au pilote jusqu'à la fin du rattrapage (au 2026-10-27 : AIFS fini, IFS 46 %, GFS 20 %, GFS immobile depuis le 2026-10-25 : lire la fin de `data\pc-daily.log`).
4. **Mi-novembre** : priorité 2 (plan SP1, tâche 20). **Fin novembre** : horaires figés, clôture de SP1 (tâche 21).

## Échéances à ne pas oublier

Rappelées automatiquement au début de chaque session par [`docs/collecte/rappels.toml`](docs/collecte/rappels.toml).

- **2027-10-22** : les deux jetons expirent le même jour, `PowAtlas cron-job` ([guide](docs/collecte/declenchement-externe.md#configuration-en-service)) et `PowAtlas sync` du PC (`.env`, [guide](docs/collecte/installation-pc.md)) ; les renouveler avant.
- **2028-03-10** : fin de la version d'API GitHub `2022-11-28` utilisée par cron-job.org ; la changer avant.
