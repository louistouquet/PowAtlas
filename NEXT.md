# Prochaine action

**Démarrer le brainstorming de SP1 (archive et observations) à partir de [`docs/roadmap.md`](docs/roadmap.md)**, dans une nouvelle session, avec le prompt ci-dessous. SP0 est clos le 2026-10-22. Urgent : la collecte quotidienne doit être en service **avant le 1er novembre 2026**, sinon le début de l'hiver 2026-27 est perdu.

- Décisions du pilote : [`docs/decisions/`](docs/decisions/README.md) et la section « Décisions du pilote » de la feuille de route.
- SP0 pour mémoire : [cadrage](docs/specs/2026-10-21-sp0-fondations-design.md), [plan](docs/plans/2026-10-21-sp0-fondations.md).

## Prompt de démarrage de SP1

```text
Démarre SP1 (Archive et observations) de PowAtlas.

1. Lis CLAUDE.md, NEXT.md, STATUS.md, puis docs/roadmap.md (surtout « Liste d'archivage SP1 » et
   « Décisions du pilote »), docs/research/R0.2-previsions-ouvertes.md et docs/research/R0.3-observations.md.
   Lis aussi docs/decisions/ (décisions 0001 à 0004). SP0 est clos.
2. Suis le cycle de docs/methode.md : skill superpowers:brainstorming avec moi, cadrage
   docs/specs/AAAA-MM-JJ-sp1-archive-design.md, plan docs/plans/AAAA-MM-JJ-sp1-archive.md, puis réalisation
   en petites PR (TDD, skill scientific-coding, CI verte, relecture par un agent).
3. Urgence : la collecte quotidienne doit tourner AVANT LE 1er NOVEMBRE 2026. Vise un cadrage court et
   livre d'abord le « cœur de score » ; le reste suit.
4. Première question à trancher avec moi : où tourne la collecte chaque jour (roadmap, décision 8) —
   A : mon PC seul (tâche planifiée Windows), B : GitHub Actions seul, C : hybride recommandé
   (Actions collecte chaque jour, mon PC rapatrie et garde l'archive de référence).
5. Périmètre de départ : run 00 UTC de ICON-D2, ICON-EU, AROME 0,025°, ARPEGE 0,1°, ECMWF IFS 0,25° et AIFS
   sur l'emprise des Alpes françaises (4,7 Go par saison) ; observations qui ne restent que 7 jours en ligne
   (SLF, API temps réel d'Arpa Piemonte) ; copie quotidienne datée du réseau nivo-météo de Météo-France ;
   rattrapage de l'historique ECMWF (IFS depuis février 2024, AIFS depuis février 2025 au plus, à confirmer)
   et GFS depuis AWS. Exigences : double déclenchement pour ICON (24 h de conservation), détection et
   rattrapage des runs manquants, journal des métadonnées.
6. Décisions déjà prises (roadmap, « Décisions du pilote ») : archive de référence et clone complet du dépôt
   sur mon PC dans D:\Codage\PowAtlas (données dans data/, ignoré par Git ; jamais de données dans Git) ;
   tous les comptes gratuits autorisés, c'est moi qui les crée quand tu me le demandes, et les jetons ne vont
   jamais dans Git ; aucun contact extérieur ; entraînement sur la meilleure offre gratuite.
7. Crée en SP1 le hook de démarrage des sessions cloud pour l'environnement Python (cadrage SP0, §6).
```

## Dossier local `D:\Codage\PowAtlas`

1. Installer Git pour Windows et Python 3.12 si ce n'est pas fait.
2. `git clone https://github.com/louistouquet/PowAtlas.git D:\Codage\PowAtlas`
3. Mettre à jour avec `git pull` dans ce dossier. Les données d'archive iront dans `D:\Codage\PowAtlas\data\`, ignoré par Git ; le code de collecte arrive avec SP1.
