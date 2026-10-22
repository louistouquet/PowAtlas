# SP0 — Fondations de PowAtlas

Document de cadrage · 21 octobre 2026 · statut : **validé par le pilote le 2026-10-21** ; décisions ultérieures du pilote dans [`docs/decisions/`](../decisions/README.md) et [`docs/roadmap.md`](../roadmap.md)

Ce document fixe ce que le projet vise, comment on travaille, avec quels outils, et ce que le sous-projet SP0 doit livrer. Il résume les décisions prises lors du brainstorming du 21 octobre 2026. Les choix techniques détaillés de chaque sous-projet suivant (SP1 à SP6) feront l'objet de leur propre cadrage.

## 1. Décisions validées

| Sujet | Décision |
|---|---|
| Nom | **PowAtlas** (vérifié libre le 21/10/2026 sur PyPI, Hugging Face, `.com`, `.org`, `.io`). Instagram : `powatlas` est pris par un compte inactif, on utilisera une variante (ex. `powatlas.ai`) ; un nom de domaine n'est pas acheté (zéro euro) |
| Licence du code | **Apache-2.0** |
| Licence de ce que le projet produit (données, modèles, documentation) | **CC-BY-4.0**, sauf données dérivées soumises à une licence de partage (ex. ODbL pour OpenStreetMap) |
| Territoire de départ | **Alpes françaises**, puis extension (arc alpin, Pyrénées, monde) |
| Budget | **Zéro euro**, calcul et hébergement compris : uniquement des offres gratuites |
| Premier pilier | **Prévision des chutes de neige**, avec l'archive d'observations construite en parallèle pour la vérifier |
| Rôles | **Le pilote** fixe le cap, valide les cadrages et juge les résultats. **Claude** fait la recherche, le code et les PR, et fusionne après tests et relecture par un agent |
| Preuve du « meilleur modèle » | Arbitre principal : **scores publics vérifiables**. Objectifs complémentaires : utilité terrain, reconnaissance scientifique, adoption et communauté |
| Stratégie de modèle | **Approche A** : système hybride en couches, arbitré par la vérification (section 4) |
| Dépôt | [`louistouquet/PowAtlas`](https://github.com/louistouquet/PowAtlas) (ex-`Clip-Studio`, vide au départ), **public depuis le 21 octobre 2026** |

## 2. Vision

PowAtlas veut être le système open source de référence pour comprendre et prévoir la neige en montagne : combien il va tomber, où et à quelle altitude ; ce qu'il y a au sol ; comment le manteau évolue ; où la neige est bonne. Chaque affirmation est appuyée par des scores publics.

Le projet s'adresse aux freeriders, randonneurs, skieurs, snowboardeurs, locaux et au grand public : des informations de base (état des stations, neige fraîche) jusqu'à l'analyse fine (couches du manteau, qualité de neige par altitude et exposition).

PowAtlas informe et analyse. **Il ne rend jamais de verdict de sécurité avalanche** : le bulletin d'estimation du risque d'avalanche (BRA) de Météo-France reste la référence et est toujours cité comme tel.

Inspirations : WePowder (alertes poudre par région, en plusieurs temps) et Snowdata (apprentissage sur plusieurs modèles météo, satellite et relevés des stations). Aucun projet open source équivalent n'a été trouvé pour les Alpes lors d'une première recherche ; R0 doit le confirmer.

## 3. Découpage en sous-projets

Chaque sous-projet suit son propre cycle : brainstorming, cadrage validé, plan, réalisation, bilan.

| # | Sous-projet | Contenu | Dépend de |
|---|---|---|---|
| SP0 | Fondations | Vision, méthode, outillage, dépôt public, recherche R0, document « Cible et feuille de route » | — |
| SP1 | Archive et observations | Archivage quotidien des prévisions ouvertes, collecte des mesures, historique (réanalyses), satellite ; publication ouverte | SP0 (R0.2 au minimum) |
| SP2 | Tableau des scores | Vérification automatique et publique des prévisions contre les mesures ; les modèles bruts sont la première référence à battre | SP1 |
| SP3 | Prévision v1 | Réduction d'échelle sur le relief, correction par apprentissage, combinaison de modèles, probabilités, alertes poudre | SP1, SP2, R3 |
| SP4 | Manteau neigeux | Simulation des couches et de la qualité de neige par massif, altitude et exposition ; historique des saisons | SP1, SP3, R4 |
| SP5 | Recherche IA avancée | Recherche exhaustive R5, essais sur GPU gratuits ; production seulement si le modèle gagne au tableau des scores | SP1, SP2, R5 |
| SP6 | Produits | API ouverte, site, carte, alertes, état des stations en direct, Instagram | SP2, SP3 |

**Ordre :** SP0, puis SP1 en urgence, puis SP2, SP3, SP4. SP5 démarre dès que l'archive contient assez de données. SP6 se construit progressivement.

**Urgence de SP1.** Les portails ouverts ne conservent que quelques jours de prévisions (environ 12 runs, soit 2 à 3 jours, pour l'[ECMWF Open Data](https://www.ecmwf.int/en/forecasts/datasets/open-data)). Chaque jour non archivé est perdu. Démarrer l'archivage en novembre 2026 donne une saison 2026-27 complète pour entraîner et vérifier. R0.2 est donc traité en premier.

> *Note du 2026-10-22 :* la saison 2026-27 sert d'abord à vérifier publiquement les modèles bruts, puis d'entraînement ; la première saison de test indépendante des modèles fins est 2027-28 ([`docs/roadmap.md`](../roadmap.md)). Objectif : collecte en service avant le 1er novembre 2026.

## 4. Stratégie de modèle (hypothèse à confirmer par R0)

Système en couches, chacune testable et remplaçable séparément ; le tableau des scores décide de ce qui passe en production.

1. **Archive des prévisions ouvertes** : AROME, ARPEGE, ECMWF IFS et AIFS, ICON et autres sources retenues par R0.2, archivées quotidiennement par GitHub Actions.
   *Note du 2026-10-22 :* lieu d'exécution de la collecte (machine du pilote, GitHub Actions ou les deux) à trancher en tête de SP1 ; archive de référence sur la machine du pilote ([décision 0001](../decisions/0001-archive-sur-la-machine-du-pilote.md)).
2. **Réduction d'échelle physique** : relief fin (IGN), limite pluie-neige, effet de l'altitude et des versants, densité de la neige fraîche.
3. **Correction par apprentissage et combinaison de modèles** : entraînées sur les écarts entre prévisions et mesures ; sortie probabiliste (« 70 % de chances de plus de 30 cm »).
4. **Manteau neigeux** : modèle ouvert (Crocus, SNOWPACK, FSM2 ou autre, choisi en R4), alimenté par la météo corrigée.
5. **Piste IA avancée** (SP5) : recherche exhaustive puis essais. Elle n'entre en production que si elle bat les couches 1 à 3 sur le tableau des scores.

Contraintes de calcul : tout le fonctionnement courant doit tenir dans les limites gratuites de GitHub Actions (dépôt public). L'entraînement lourd utilise des GPU gratuits (Kaggle, Colab), dont les quotas seront vérifiés en R0.5.

> *Note du 2026-10-22 :* la collecte quotidienne peut tourner sur la machine du pilote ([décision 0001](../decisions/0001-archive-sur-la-machine-du-pilote.md)) ; l'entraînement utilise la meilleure offre gratuite du moment ([décision 0004](../decisions/0004-calcul-et-hebergements-gratuits.md)).

## 5. Méthode de travail

### Cycle
1. Brainstorming avec le pilote, puis cadrage écrit dans `docs/specs/`, validé par le pilote.
2. Plan découpé en petites tâches dans `docs/plans/`.
3. Réalisation en petites PR : tests automatiques, intégration continue, relecture par un agent, fusion en un seul commit par PR.
4. Bilan : mise à jour de `STATUS.md` et `NEXT.md`.

### Fiches
- **Fiche source** (`docs/sources/`), une par source de données : producteur, contenu, licence, accès, quotas, délai de mise à disposition, résolution, durée de conservation, test réel d'accès (date, commande, résultat), limites. Aucune donnée n'entre dans le projet sans sa fiche.
- **Fiche d'expérience** (`docs/experiments/`), une par essai de modèle : hypothèse, référence à battre, données et découpage, mesures fixées **avant** l'essai, résultat, décision (garder, modifier, abandonner) et condition de réexamen. Les échecs sont conservés.

### Rigueur scientifique
- Aucune affirmation de qualité sans score face à une référence.
- Vérification sur des saisons entières mises de côté, jamais sur des jours voisins des données d'entraînement.
- Uniquement les données réellement disponibles au moment de l'émission de la prévision (pas de fuite du futur).
- Toujours distinguer observé, modélisé et prévu ; l'incertitude est affichée.
- Les faits instables (licences, accès, versions, quotas) sont vérifiés sur la source primaire et datés.

### Continuité
Le dépôt garde la mémoire, pas le fil de discussion. `STATUS.md` décrit ce qui marche, `NEXT.md` la prochaine action ; chaque session commence par les lire et se termine par les mettre à jour. Les choix structurants vont dans `docs/decisions/`. Les issues GitHub sont le seul outil de suivi, avec un jalon par sous-projet.

### Langues
Code, API et commentaires en anglais. README en anglais et en français. Cadrages, plans et documents de pilotage en français.

### Garde-fous
- Zéro euro : tout nouveau service doit être gratuit et répondre à un besoin nommé.
- Aucun compte créé ni contact extérieur sans accord du pilote.
- Aucun secret, jeton ou lien signé dans Git.
- Jamais de verdict de sécurité avalanche.
- Toute réutilisation de données respecte la licence de la source ; une page publique n'est pas une licence.

## 6. Outillage

### Outils retenus

| Outil | Usage |
|---|---|
| alphaXiv (MCP) | Source principale pour les articles : recherche, texte intégral, questions sur PDF, code associé |
| Hugging Face (MCP et skills) | Recherche de modèles et jeux de données ; publication de nos données et modèles (`hf-cli`) ; suivi d'expériences (`trackio`). *Note du 2026-10-22 : rôle précisé par la [décision 0004](../decisions/0004-calcul-et-hebergements-gratuits.md).* |
| Exa | Recherche web sémantique, en complément de la recherche web intégrée, dans la limite des **10 $ de crédits gratuits mensuels** : aucun moyen de paiement enregistré, recherches ciblées plutôt que l'agent Exa (plus coûteux) |
| Skill `scientific-coding` | Activé pour tout code scientifique |
| Skills *superpowers* et `deep-research` | Méthode (cadrage, plans, tests, vérification, relecture) et grosses recherches |
| `gh` | Issues, PR, CI, jalons |
| Supabase, Vercel | Non utilisés en SP0 ; à évaluer pour SP6 |

**Exclus (zéro euro) :** Hugging Face Jobs, Sandboxes, Inference Endpoints et création de Spaces ZeroGPU ; services météo payants ou propriétaires (AccuWeather, Xweather, Tomorrow.io).

### Modèles Claude et niveaux d'effort

Les définitions d'agents désignent les modèles par **famille** (`opus`, `sonnet`, `haiku`) et non par version : elles suivent automatiquement les nouvelles versions. Ce tableau vit dans `docs/modeles-claude.md` et est relu à chaque nouvelle génération de modèles.

| Rôle | Modèle | Effort |
|---|---|---|
| Pilote technique : cadrage, architecture, consolidation, intégration | Opus | high (xhigh pour les cadrages) |
| Grands arbitrages : architecture IA (SP5), synthèses finales de recherche, protocole de vérification | Opus | xhigh (max pour les décisions les plus critiques) |
| Agents de recherche : web, articles, synthèse | Sonnet | medium |
| Tri de masse : inventaires, contrôle de liens et de licences | Haiku | low |
| Code courant | Sonnet | medium |
| Code scientifique critique : scores, réduction d'échelle, apprentissage | Opus | high |
| Relecteur scientifique | Opus | high |
| Relecture de code standard | Sonnet | high |

### Règles d'économie de tokens
1. Commencer au modèle le moins cher qui suffit ; monter d'un cran seulement si la relecture trouve des problèmes.
2. Les lectures lourdes partent dans des agents qui rendent une synthèse sourcée.
3. Toute recherche est écrite dans le dépôt ; une recherche faite n'est jamais refaite, seulement mise à jour.
4. Chaque agent reçoit un mandat précis : question, format de sortie, nombre maximal de sources.
5. Au-delà de 3 agents en parallèle, feu vert explicite du pilote (déjà donné pour R0).
6. `CLAUDE.md` reste court ; les skills se chargent à la demande.

### À créer dans le dépôt
- `CLAUDE.md` (règles du projet) et `AGENTS.md` (renvoi vers `CLAUDE.md` pour les autres outils IA).
- Agents `.claude/agents/` :
  - `chercheur-sources` (sonnet, medium) : qualifie une source et remplit sa fiche ;
  - `relecteur-scientifique` (opus, high) : cherche fuites temporelles, affirmations non prouvées, erreurs statistiques, problèmes de licence.
- Skills `.claude/skills/` :
  - `qualifier-source` : procédure et modèle de fiche source, avec test réel d'accès ;
  - `experience-modele` : protocole et modèle de fiche d'expérience.
  - `verifier-prevision` viendra en SP2, avec le calcul des scores.
- Intégration continue : contrôle des liens internes de la documentation et de la présence des champs obligatoires dans les fiches.
- Le hook de démarrage des sessions cloud (installation de l'environnement Python) est créé en **SP1**, avec le premier code Python.

## 7. Programme de recherche

Chaque campagne produit des rapports dans `docs/research/` et des fiches sources dans `docs/sources/`. Les rapports citent leurs sources primaires avec date de consultation et distinguent fait vérifié, affirmation d'un tiers et hypothèse.

### R0 — dans SP0

| Axe | Question | Livrable |
|---|---|---|
| R0.2 Prévisions ouvertes *(en premier)* | AROME (dont versions immédiate et d'ensemble), ARPEGE, ECMWF IFS, AIFS et ENS, ICON, ICON-CH, GFS : accès, délai, variables neige, conservation, licence, volume quotidien sur les Alpes françaises | Liste exacte de ce que SP1 archive, avec fiches sources |
| R0.1 Concurrence | WePowder, Snowdata, OpenSnow, Snow-Forecast, Meteoblue, Bergfex, Météo-France Montagne, White Risk, Skitour, Camptocamp… : fonctionnalités, méthodes revendiquées, lacunes | Carte du marché et fonctionnalités où PowAtlas peut être meilleur |
| R0.3 Observations | Nivôse, réseau nivo-météo, stations Météo-France, hauteurs déclarées par les stations, stations frontalières (Suisse, Italie), satellite (couverture neigeuse, neige humide), retours de terrain | Ce qui peut servir de vérité terrain pour la neige fraîche à 24, 48 et 72 h |
| R0.4 Historique | S2M, CERRA, ERA5-Land, COMEPHORE et autres : couverture, résolution, licence | Base d'entraînement, de vérification et d'archives des saisons |
| R0.5 Briques open source | Modèles de manteau, méthodes de neige fraîche, bibliothèques de scores, outils (earthkit, Herbie, Open-Meteo…), projets neige existants, quotas GPU gratuits | Ce qu'on réutilise et ce qu'on construit |

**Exécution :** 5 agents de recherche en parallèle (Sonnet, medium), des agents Haiku pour contrôler liens et licences, consolidation par Opus (high), synthèse finale par Opus (xhigh), puis passage du relecteur scientifique.

**Livrable final de R0 :** `docs/roadmap.md`, « Cible et feuille de route » : fonctionnalités de la v1 par priorité, liste d'archivage de SP1, principes du tableau des scores, risques. Il est validé par le pilote.

### Campagnes suivantes (au début de leur sous-projet)
- **R3 — Prévision :** séparation pluie-neige, rapport neige fraîche / eau, réduction d'échelle orographique, post-traitement statistique et par apprentissage, combinaison de modèles, calibrage des probabilités.
- **R4 — Manteau neigeux :** comparaison des modèles de manteau, chaînes opérationnelles, classification de la qualité de neige pour skieurs, assimilation de données satellite.
- **R5 — IA (exhaustive) :** grands modèles météo par IA (GraphCast, GenCast, Aurora, AIFS, Pangu, FuXi, NeuralGCM, Prithvi WxC…), modèles régionaux (Anemoi, Varda…), réduction d'échelle générative (CorrDiff, diffusion, *flow matching*), world models (JEPA…), apprentissage guidé par la physique, stratégies d'entraînement à faible calcul. Synthèse par Opus en effort max.

## 8. Dépôt public

### Structure
```
README.md, README.fr.md, LICENSE, NOTICE, DATA_LICENSES.md
CLAUDE.md, AGENTS.md, STATUS.md, NEXT.md, CONTRIBUTING.md
docs/   vision.md · methode.md · roadmap.md · modeles-claude.md
        specs/ · plans/ · decisions/ · research/ · sources/ · experiments/
.claude/  agents/ · skills/
.github/  workflows/ · ISSUE_TEMPLATE/ (fiche source, expérience, bug)
```
Le code Python (`src/`, `tests/`, `pyproject.toml`) arrive avec SP1.

### Réglages GitHub
- Dépôt **public depuis le 21 octobre 2026** : chaque PR est vérifiée pour l'absence de secret et de contenu non redistribuable avant fusion.
- Branche `main` protégée : CI obligatoire, pas de *force push*, fusion en un seul commit par PR.
- Jalons SP0 à SP6 ; étiquettes par type (recherche, source, expérience, code, docs).
- Plus tard : organisation GitHub au nom du projet, créée par le pilote, puis transfert du dépôt.

## 9. Livrables et critères d'acceptation de SP0

SP0 est terminé quand :
1. Le dépôt contient les fichiers de la section 8, en anglais et en français là où c'est prévu.
2. `CLAUDE.md`, les 2 agents et les 2 skills existent. `qualifier-source` a produit au moins une fiche source réelle ; `experience-modele` a produit une fiche d'exemple, clairement marquée comme fictive puisqu'aucun modèle n'existe encore.
3. La CI passe sur `main`.
4. Les rapports R0.1 à R0.5 et les fiches des sources retenues pour SP1 sont fusionnés.
5. `docs/roadmap.md` est validé par le pilote.
6. `main` est protégée et les jalons SP0 à SP6 existent.
7. `NEXT.md` indique de démarrer le brainstorming de SP1.

## 10. Hors périmètre de SP0
Aucun code de traitement de données, aucun téléchargement automatique, aucun site, aucun compte Instagram, aucune création de compte sur des services tiers. Les comptes gratuits nécessaires (Hugging Face pour le projet, portail API Météo-France, Copernicus Data Space, Kaggle) seront demandés au pilote en SP1.

## 11. Risques et points ouverts
- **Disponibilité des observations :** l'accès ouvert aux données du réseau nivo-météo n'est pas confirmé. Sans vérité terrain suffisante, le tableau des scores est affaibli. R0.3 doit trancher.
- **Volume d'archive :** les limites de stockage gratuit (Hugging Face, GitHub) face au volume quotidien des prévisions sur les Alpes restent à mesurer en R0.2 et R0.5. *Mesuré (R0.2) et tranché le 2026-10-21 : archive de référence sur la machine du pilote ([décision 0001](../decisions/0001-archive-sur-la-machine-du-pilote.md)).*
- **Licences :** la licence exacte des prévisions archivées par Open-Meteo et de certaines sources communautaires n'est pas confirmée.
- **Crédits Exa :** 10 $ par mois ; si le quota est atteint, on bascule sur la recherche web intégrée jusqu'au mois suivant.
- **Organisation GitHub :** disponibilité du nom PowAtlas non vérifiée.
