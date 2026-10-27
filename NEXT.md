# Prochaine action

**SP1 continue en tâche de fond** ([plan](docs/plans/2026-10-22-sp1-archive.md), [`STATUS.md`](STATUS.md)) ; **SP2 démarre**, accord du pilote du 2026-10-27.

1. **D'abord, Arpa Piemonte par le PC** (SP1, petite tâche, TDD, une PR) : Arpa refuse les réseaux de centres de données mais répond au PC du pilote ([`suivi.md`](docs/collecte/suivi.md#5-constats-en-cours), § 5). À faire :
   - collecte d'Arpa dans `scripts/pc-daily.ps1` (unité du jour rangée dans l'archive comme `sync` le fait) ;
   - retrait d'Arpa de la tâche `observations` d'Actions, sinon une issue de perte s'ouvre chaque jour ;
   - rangement de la copie du 2026-10-27 faite à la main dans `data\pc-collect` ;
   - fermeture de l'issue 50.
   Tant que ce n'est pas fait, le pilote refait la copie au moins tous les 7 jours (rappel).
2. **SP2, cadrage** (skill *brainstorming*, puis `docs/specs/AAAA-MM-JJ-sp2-scores-design.md`, validé par le pilote, puis plan) : tableau public des scores de la neige fraîche des modèles bruts ([`roadmap.md`](docs/roadmap.md), « Vérité terrain et tableau des scores »).
   - **Déjà décidé par le pilote le 2026-10-27** :
     - périmètre « C » : un seul code ; d'abord l'historique (IFS, AIFS, GFS sur 2024-25 et 2025-26, dès la fin du rattrapage), puis la saison 2026-27 avec les six modèles ;
     - calcul sur le PC du pilote (`powatlas score` dans la tâche quotidienne) ; seuls les tableaux de scores sont publiés. L'archive entière pèse 0,28 Go le 2026-10-27.
   - **Questions encore ouvertes, une à la fois** :
     - où publier les scores (dépôt, GitHub Pages, Hugging Face), compte tenu de la règle « aucune donnée dans Git » ;
     - observations historiques à rapatrier pour 2024-26 et pour la climatologie (base quotidienne `HNEIGEF` depuis 1996, Arpa `meteoidro`, SLF) ;
     - conversion de la neige prévue en hauteur ;
     - seuils et longueur des blocs ;
     - rôle des saisons ;
     - lien avec le skill `verifier-prevision` prévu par la feuille de route.
3. **Suivi de la collecte, en autonomie** ([`docs/collecte/suivi.md`](docs/collecte/suivi.md)) : bilan de santé et rappels au démarrage ; `progress` redemandé au pilote jusqu'à la fin du rattrapage (au 2026-10-25 : AIFS fini, IFS 41 %, GFS 20 %).
4. **Mi-novembre** : priorité 2 (plan SP1, tâche 20). **Fin novembre** : horaires figés, clôture de SP1 (tâche 21).

## Échéances à ne pas oublier

Rappelées automatiquement au début de chaque session par [`docs/collecte/rappels.toml`](docs/collecte/rappels.toml).

- **2027-10-22** : les deux jetons expirent le même jour, `PowAtlas cron-job` ([guide](docs/collecte/declenchement-externe.md#configuration-en-service)) et `PowAtlas sync` du PC (`.env`, [guide](docs/collecte/installation-pc.md)) ; les renouveler avant.
- **2028-03-10** : fin de la version d'API GitHub `2022-11-28` utilisée par cron-job.org ; la changer avant.
