# Prochaine action

**SP1 continue en tâche de fond** ([plan](docs/plans/2026-10-22-sp1-archive.md), [`STATUS.md`](STATUS.md)) ; **SP2 démarre**, accord du pilote du 2026-10-27.

1. **SP1, suivi** : Arpa réglée le 2026-10-27 (issue 50 fermée). Rattrapage IFS corrigé ([PR 60](https://github.com/louistouquet/PowAtlas/pull/60)) : le pilote relance l'IFS avec `--retry-given-up` après `git pull` et colle la fin du journal (GFS immobile à 179/906 depuis le 2026-10-25, cause à trouver) (rappel).
2. **SP2, cadrage** (skill *brainstorming*, puis `docs/specs/AAAA-MM-JJ-sp2-scores-design.md`, validé par le pilote, puis plan) : tableau public des scores de la neige fraîche des modèles bruts ([`roadmap.md`](docs/roadmap.md), « Vérité terrain et tableau des scores »).
   - **Précisé par le pilote le 2026-10-27, après coup** (prime sur la ligne « calcul des scores sur le PC » ci-dessous) : tout ce qui peut tourner sur GitHub y tourne (garanti, le PC ne l'est pas) ; publication sur Hugging Face, configurée pour l'ensemble du projet ; les questions déjà tranchées par les rapports R0 et la feuille de route sont tranchées dans le cadrage, pas reposées au pilote. **Retenu par le pilote le 2026-10-27** (question 2, [décision 0007](docs/decisions/0007-hugging-face-au-centre-github-d-abord.md)) : architecture « Hugging Face au centre » : organisation `PowAtlas`, jeux `archive` (alimenté par Actions à la collecte et par le PC pour ce que lui seul collecte) et `scores` (calculés par Actions) ; mise en place par le pilote : [`hugging-face.md`](docs/collecte/hugging-face.md).
   - **Décidé par le pilote le 2026-10-27** (repris dans la décision 0007) :
     - un seul code, l'historique d'abord, puis la saison 2026-27 ;
     - ~~calcul des scores sur le PC du pilote~~ : remplacé le même jour par le calcul sur GitHub Actions (décision 0007).
   - **Proposé, à confirmer au cadrage** :
     - historique = IFS, AIFS, GFS sur les saisons rattrapées (2024-25 et 2025-26), dès la fin du rattrapage ;
     - saison 2026-27 = tous les modèles collectés (ICON-D2, ICON-EU, AROME, ARPEGE, IFS, AIFS, GFS) ;
     - une sous-commande (par exemple `powatlas score`, à écrire) dans la tâche quotidienne du PC ;
     - seuls les tableaux de scores publiés. L'archive pesait 0,28 Go le 2026-10-27, rattrapage inachevé.
   - **Questions encore ouvertes, une à la fois** :
     - ~~où publier les scores~~ : Hugging Face (question 2 ci-dessus) ;
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
