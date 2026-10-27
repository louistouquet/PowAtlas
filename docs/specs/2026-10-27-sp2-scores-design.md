# SP2 — Tableau public des scores de la neige fraîche

Document de cadrage · 27 octobre 2026 · statut : **validé par le pilote le 2026-10-27** (brainstorming du même jour), puis corrigé le même jour après relecture scientifique (3 constats bloquants, 7 importants, 4 mineurs : section 8) ; les corrections sont signalées au pilote.

Ce cadrage fixe ce que SP2 livre : un tableau public, recalculé chaque jour, des scores de la neige fraîche prévue par les modèles bruts, sur l'historique rattrapé puis sur la saison 2026-27. C'est la première référence publique du projet, préalable à toute revendication de SP3. Il s'appuie sur [`docs/roadmap.md`](../roadmap.md) (« Vérité terrain et tableau des scores »), [R0.3](../research/R0.3-observations.md), [R0.5](../research/R0.5-briques-open-source.md), la [décision 0007](../decisions/0007-hugging-face-au-centre-github-d-abord.md) et l'archive de SP1 ([cadrage SP1](2026-10-22-sp1-archive-design.md)).

## 1. Décisions prises au brainstorming

| Sujet | Décision |
|---|---|
| Ordre | Un seul code : l'**historique d'abord** (IFS, AIFS, GFS rattrapés), puis la saison 2026-27 au fil de l'eau (pilote, 2026-10-27) |
| Lieu du calcul | **GitHub Actions** dès que possible ; le PC du pilote seulement pour ce que GitHub ne peut pas faire : rattrapage AWS, GFS, Arpa Piemonte ([décision 0007](../decisions/0007-hugging-face-au-centre-github-d-abord.md)) |
| Publication | Organisation Hugging Face `PowAtlas` : `PowAtlas/archive` (copie publique de l'archive) et `PowAtlas/scores` (paires et scores), créés par le pilote le 2026-10-27 ([guide](../collecte/hugging-face.md)) ; le dépôt GitHub ne garde que le code et un lien ; aucune donnée dans Git |
| Méthode | Tranchée par Claude à partir des rapports R0 et de la feuille de route, à la demande du pilote, approuvée par lui le 2026-10-27, puis corrigée après relecture (section 8) |

## 2. Faits établis pendant le cadrage (2026-10-27)

- **Hugging Face** [producteur, https://huggingface.co/docs/hub/storage-limits et https://huggingface.co/docs/hub/trusted-publishers, lues le 2026-10-27] :
  - stockage public gratuit « best-effort », sans plafond garanti ;
  - par dépôt, moins de 100 000 fichiers et moins de 10 000 entrées par dossier conseillés ;
  - écriture depuis GitHub Actions sans jeton stocké (« Trusted Publishers ») : jeton d'une heure limité à un dépôt, `huggingface_hub` 1.19 ou plus récent, permission `id-token: write`.
- **Mise en place** : organisation `PowAtlas`, jeux `PowAtlas/archive` et `PowAtlas/scores` publics, étiquetés `cc-by-4.0` [vérifié, API de Hugging Face, 2026-10-27]. Le pilote déclare avoir créé les Trusted Publishers et le jeton du PC ; le premier envoi les testera.
- **Volume** : l'archive découpée pesait 0,28 Go le 2026-10-27 [vérifié par le pilote]. Une arborescence par source, année et mois donne moins de 70 fichiers par dossier et environ 5 000 fichiers par an [estimation].
- **Neige prévue disponible** (catalogue de SP1, [fiche ECMWF](../sources/ecmwf-open-data.md)) :

  | Modèle | Variable | Unité | Disponibilité |
  |---|---|---|---|
  | IFS | `sf` | m d'équivalent eau | **seulement depuis le run du 2025-11-22** sur AWS [vérifié, 2026-10-22] ; avant : `tp` et `2t` seulement (`ptype` à partir de mi-2025) |
  | AIFS | `sf` | kg m-2 (= mm) | depuis le 2025-02-26 (flux opérationnel) |
  | ICON-D2, ICON-EU | `snow_gsp` + `snow_con` (`lsfwe`, `csfwe`) | kg m-2 | archive de SP1 (depuis le 2026-10-22) |
  | AROME 0,025°, ARPEGE 0,1° | `tsnowp` | kg m-2 | archive de SP1 |
  | GFS | aucune | — | `apcp` (kg m-2), `2t`, `csnow` |

  Les unités sont relues dans l'attribut `GRIB_units` de chaque variable archivée, jamais supposées.
- **Échéances** : AROME s'arrête à +51 h et ICON-D2 à +48 h, donc pas de cumul de 48 h (+6 à +54 h) pour eux. GFS va jusqu'à +78 h exactement, les autres au-delà.
- **Disponibilité des runs 00 UTC** ([roadmap](../roadmap.md), R0.2) : IFS vers 07:34 UTC, AIFS de 05:45 à 07:34, AROME jusqu'à +5,6 h. La fenêtre de 24 h commence à 06 UTC : pour les modèles bruts, elle commence donc parfois avant que le run soit disponible.
- **Observations de Météo-France** ([fiche](../sources/meteo-france-observations.md)) :
  - la base quotidienne (`HNEIGEF`, `QHNEIGEF`, colonnes `NUM_POSTE`, `NOM_USUEL`, `LAT`, `LON`, `ALTI`, `AAAAMMJJ`) est servie en deux fichiers par département, `Q_<dép>_previous-1950-2024_autres-parametres.csv.gz` et `Q_<dép>_latest-2025-2026_autres-parametres.csv.gz` [vérifié, listing du 2026-10-27] ;
  - SP1 archive chaque jour la copie datée du fichier `latest`, pas encore le fichier `previous` ;
  - les codes `QHNEIGEF` évoluent (une valeur filtrée peut être validée plus tard) ;
  - le réseau nivo-météo publie les mêmes mesures (97,3 % des paires à moins de 1 cm d'écart [vérifié, R0.3]) : à ne compter qu'une fois.
- **Arpa Piemonte** ([fiche](../sources/arpa-piemonte.md)) :
  - l'API historique `meteoidro` donne `hn` par jour pour les champs de neige manuels (`campo_neve = S`, 18 dans l'emprise) ;
  - mesure à 08 h locale [producteur] ; la date attribuée à la valeur n'est pas documentée [hypothèse] ;
  - l'API ne répond qu'au PC du pilote depuis le 2026-10-24 [vérifié] ; sa table s'arrêtait au 2026-06-30 le 2026-10-21, délai de mise à jour en saison inconnu.

## 3. Architecture

```
GitHub Actions                          PC du pilote
  collect.yml ── unité complète ──┐      powatlas publish (rattrapage, GFS, Arpa, unités rapatriées)
                                  ▼          │
                        PowAtlas/archive ◄───┘
                                  │
  scores.yml (chaque jour) ◄──────┘   (prévisions et observations datées, toutes lues dans l'archive)
     powatlas pairs  → paires prévision/observation (Parquet par saison)
     powatlas score  → tableaux de scores (CSV) + fiche du jeu
                                  ▼
                        PowAtlas/scores  ◄── lien depuis le README du dépôt
```

- **`PowAtlas/archive`** :
  - même arborescence que `data` : `forecasts/<source>/<AAAA>/<MM>/` et `observations/<source>/<AAAA>/<MM>/` ;
  - fichiers et manifestes inchangés ;
  - un envoi n'ajoute que les unités absentes ou modifiées (comparaison du manifeste), au plus 100 fichiers par commit.
- **Envoi depuis GitHub Actions** : `collect.yml` envoie l'unité après la collecte quand elle est complète. Une unité partielle reste en artefact : le PC la rapatrie, et une collecte complète ultérieure la remplace.
- **Envoi depuis le PC** : `powatlas publish --data data` envoie ce que l'archive de Hugging Face n'a pas encore, quelle qu'en soit l'origine. Il est ajouté à `scripts/pc-daily.ps1` ; le jeton `HF_TOKEN` est lu dans `.env`, jamais dans Git.
- **Observations versionnées** :
  - `scores.yml` ne lit que des copies datées de l'archive, jamais le serveur de Météo-France en direct ;
  - la copie du fichier `previous-1950-2024` est ajoutée à la collecte (une copie datée, renouvelée quand le fichier change) ;
  - chaque tableau publie la date de collecte et le sha256 des fichiers d'observation utilisés.
- **`scores.yml`** :
  - planifié chaque jour, plus le déclenchement à la main ;
  - il télécharge depuis `PowAtlas/archive` les seuls fichiers nécessaires ;
  - il recalcule les paires de la saison en cours (et, au premier passage, de tout l'historique), puis les scores, et les envoie sur `PowAtlas/scores` ;
  - un run en échec ne publie rien et le tableau précédent reste en ligne.
- **Licences et attributions** ([décision 0007](../decisions/0007-hugging-face-au-centre-github-d-abord.md)) :
  - avant le premier envoi, la licence de chaque source envoyée est vérifiée sur la page du producteur et datée dans sa fiche, y compris la compatibilité de la Licence Ouverte 2.0 avec CC BY et les conditions de la NOAA ;
  - si une source ne permet pas une diffusion sous CC BY 4.0, l'étiquette du jeu concerné passe à `other` ;
  - les fiches des deux jeux (`archive` et `scores`, qui redistribue observations et prévisions dans ses paires) donnent, source par source, la licence d'origine et l'attribution exigée.

## 4. Méthode des scores

Ce protocole est figé avant tout calcul. Il est repris dans le skill `verifier-prevision`, et toute modification ultérieure crée une version datée, appliquée seulement aux scores calculés après elle.

### 4.1 Observations

- **Vérité officielle** :
  - `HNEIGEF` de la base quotidienne de Météo-France, valeurs validées (codes `QHNEIGEF` 0 et 1) ;
  - stations des départements 04, 05, 06, 38, 73 et 74 situées dans la boîte de SP1 ;
  - coordonnées et altitude lues dans les fichiers.
- **Score provisoire, publié à part** : mêmes calculs avec les valeurs de code 9 en plus. Toute autre valeur de `QHNEIGEF` (vide, autre code) est exclue des deux.
- **Aucun filtre ajouté après coup** : les valeurs validées sont gardées telles quelles, y compris les fortes valeurs (question ouverte de R0.3 sur 99 cm). Le nombre de valeurs supérieures ou égales à 99 cm est publié.
- **Complément** :
  - `hn` des champs de neige manuels d'Arpa Piemonte (`campo_neve = S`), par `meteoidro`, publié en plus du score français, jamais mélangé avec lui ;
  - les stations `N` (automatiques) sont exclues.
- **Exclus de la vérité terrain** : neige déduite d'une hauteur totale (Nivôse, IMIS, stations `N`), neige modélisée (S2M, `HN_1D` des IMIS), parcelles SLF (pas d'historique archivé avant octobre 2026 ; à ajouter en 2027-28). Le réseau nivo-météo n'est pas compté une seconde fois.

### 4.2 Prévision comparée

- **Runs et fenêtres, Météo-France** :
  - run 00 UTC du jour J uniquement ;
  - `HNEIGEF(J)` (fenêtre nominale 06 UTC J → 06 UTC J+1) est comparé au cumul prévu de +6 h à +30 h ;
  - 48 h : `HNEIGEF(J) + HNEIGEF(J+1)` contre +6 h à +54 h ;
  - 72 h : trois jours contre +6 h à +78 h ;
  - les sommes de 48 h et 72 h exigent toutes les valeurs et sont marquées **dérivées**.
- **Runs et fenêtres, Arpa** :
  - `hn(D)` (relevé à 08 h locale le jour D, soit 07 UTC l'hiver) est comparé au cumul du run 00 UTC de D-1, de +7 h à +31 h ;
  - **contrôle de l'alignement, déclaré ici** : sur la seule saison d'entraînement 2024-25, corrélation entre `hn(D)` des stations `S` et la moyenne de `HNEIGEF` des stations françaises des départements 73 et 74 pour les jours D-2, D-1 et D. L'alignement retenu est celui de corrélation maximale ; s'il n'est pas D-1, la fenêtre d'Arpa est décalée en conséquence et le changement est publié.
- **Écarts déclarés** :
  - le relevé réel des postes a lieu vers 07-08 UTC, soit 1 à 2 h après la fin nominale de la fenêtre ;
  - la fenêtre commence à 06 UTC, alors que le run 00 UTC n'est disponible qu'entre environ 04 et 07:40 UTC selon le modèle. Pour les modèles bruts, ce n'est pas une fuite : le run est émis à 00 UTC et n'utilise aucune observation postérieure. Mais un utilisateur ne l'aurait pas eu à 06 UTC. Cet écart est publié par modèle.
- **Point de grille** :
  - le plus proche de la station (distance sur la sphère), sans interpolation ni correction d'altitude ;
  - la distance au point et l'altitude de la station sont publiées avec chaque paire ;
  - l'orographie des modèles n'est pas archivée en SP1 [vérifié, catalogue], donc l'écart d'altitude grille-station n'est pas publié en SP2 (à ajouter avec l'orographie si SP3 en a besoin).
- **Neige prévue en équivalent eau (mm)** :

  | Cas | Calcul | Marque |
  |---|---|---|
  | IFS, runs avec `sf` (depuis le 2025-11-22) | `sf`, converti selon `GRIB_units` (m → × 1000) | directe |
  | AIFS | `sf` (kg m-2 = mm, × 1) | directe |
  | ICON | `lsfwe` + `csfwe` | directe |
  | AROME, ARPEGE | `tsnowp` | directe |
  | IFS, runs sans `sf` (2024-02-01 au 2025-11-21) ; GFS | somme, sur les pas de la fenêtre, de l'incrément de précipitation totale (`tp` ou `apcp`) quand la température à 2 m du modèle en fin de pas est inférieure ou égale à 1,0 °C | **dérivée** |

  - La règle dérivée est la même pour l'IFS et GFS (seuil de 1 °C, ordre de grandeur des seuils de séparation pluie-neige en température de l'air [hypothèse, à sourcer dans le skill]). Le `csnow` de GFS n'est pas utilisé.
  - L'IFS « dérivé » et l'IFS « direct » sont publiés comme deux lignes distinctes. Sur les runs qui ont les deux (depuis le 2025-11-22), l'écart entre eux est publié : c'est la mesure de l'erreur propre à la dérivation.
- **Conversion en hauteur** :
  - **officielle** : densité fixe de 100 kg/m³, soit 1 mm d'eau pour 1 cm de neige, identique pour tous les modèles ;
  - **sensibilité, publiée à part** : densité de Hedstrom et Pomeroy (1998), ρ = 67,92 + 51,25 · exp(T / 2,59) kg/m³ ;
    - T est la température à 2 m du modèle en fin de chaque pas, en °C, plafonnée à 0 °C, ce qui donne ρ ≤ 119,2 kg/m³ ;
    - elle s'applique à la neige de ce pas (3 h, ou 6 h pour l'AIFS) ;
  - les deux sont déclarées ici, avant tout score.
- **Biais de référence** : la neige observée est tassée et peut avoir fondu. Elle est attendue plus basse que la chute modélisée ; ce biais n'est pas une erreur du modèle, et la fiche du jeu le dit.

### 4.3 Mesures

- **Erreur absolue moyenne et biais (erreur moyenne)**, sur trois groupes de jours :
  - tous les jours ;
  - les jours avec au moins 1 cm observé ;
  - les jours avec au moins 1 cm prévu. Ce dernier groupe dépend du modèle, donc il n'est pas comparable d'un modèle à l'autre ; la fiche le dit.
- **Seuils de 1, 5, 10, 20 et 30 cm**, atteints si la valeur est supérieure ou égale au seuil, sans arrondi de la prévision (l'observation est en cm entiers). Pour chaque seuil :
  - taux de détection, TP / (TP + FN) ;
  - rapport de fausses alertes, FP / (TP + FP) ;
  - biais de fréquence ;
  - *equitable threat score* ;
  - score de Brier de la prévision prise comme probabilité 0 ou 1.
- **Climatologie de référence** :
  - par station et par mois, sur les hivers 1996-97 à 2020-21, tous antérieurs aux saisons scorées (GFS dès 2021-22) : aucune donnée de la période évaluée n'entre dans la référence ;
  - **médiane** climatologique, pour l'erreur absolue, et **fréquence** climatologique de chaque seuil, pour le score de Brier ;
  - scores de compétence : 1 − EAM(modèle) / EAM(climatologie) et 1 − Brier(modèle) / Brier(climatologie). Taux de détection et ETS ne se calculent que pour les modèles.
- **Incertitude, par rééchantillonnage apparié** :
  - blocs de 7 jours consécutifs, sans chevauchement, comptés à partir du 1er novembre de chaque saison et coupés à la fin de la saison (le dernier bloc peut être plus court) ;
  - chaque bloc garde toutes les stations de ses dates ;
  - 2 000 tirages avec remise, graine fixée et publiée, **mêmes blocs tirés pour tous les modèles et la climatologie** ;
  - intervalle à 95 % par la méthode des percentiles, pour chaque score et pour chaque différence entre deux modèles ou entre un modèle et la climatologie.
- **Même échantillon pour tous** : chaque comparaison se fait sur l'intersection des couples station-date disponibles pour tous ses modèles. Le nombre de paires, le nombre de dates distinctes et les manques sont publiés par modèle. Comparaisons :
  - historique : IFS (direct, dérivé), AIFS et GFS sur leurs périodes communes, et chaque modèle seul ;
  - 2026-27 : les sept modèles, puis les groupes où un modèle manque.
- **Strates** :
  - bande d'altitude de la station : moins de 1 200 m, 1 200-1 800 m, 1 800-2 400 m, plus de 2 400 m (peu fournie, signalée) ;
  - mois ;
  - saison.
- **Versions des modèles** : le cycle de chaque modèle (IFS, AIFS, GFS, AROME, ARPEGE, ICON) par saison est publié d'après la documentation des producteurs, daté. Les scores d'une saison qui mélange plusieurs cycles le disent.
- **Jamais de verdict de sécurité avalanche.** La fiche du jeu `scores` renvoie au bulletin d'estimation du risque d'avalanche (BRA) de Météo-France.

### 4.4 Saisons

L'hiver va de novembre à avril.

| Saison | Modèles disponibles | Rôle (feuille de route) |
|---|---|---|
| 1996-97 à 2020-21 | observations seules | climatologie de référence |
| 2021-22 à 2022-23 | GFS (dérivé) | entraînement |
| 2023-24 | GFS ; IFS dérivé à partir du 2024-02-01 | entraînement |
| 2024-25 | GFS, IFS dérivé ; AIFS à partir du 2025-02-26 | entraînement (contrôle d'alignement d'Arpa) |
| 2025-26 | GFS, AIFS ; IFS dérivé jusqu'au 2025-11-21, direct ensuite | validation (exclue de tout étalonnage de neige dérivée, règle 8 de R0.3) |
| 2026-27 | les sept modèles | vérification publique des modèles bruts, puis entraînement de SP3 |
| 2027-28 | à venir | **test** : touché une seule fois, aucun réglage sur ses scores quotidiens |

- Les modèles bruts n'ont rien d'entraîné. Les choix de cette section sont faits avant de voir le moindre score ; le seul réglage fait sur des données (alignement d'Arpa) n'utilise que 2024-25.
- Les scores quotidiens de 2026-27 ne servent à aucun réglage de SP2.

## 5. Livraison

Petites PR, tests d'abord (TDD, données synthétiques), skill `scientific-coding`, relecture par l'agent `relecteur-scientifique` pour tout code de calcul. Le plan détaillé ([`docs/plans/2026-10-27-sp2-scores.md`](../plans/2026-10-27-sp2-scores.md)) découpe ainsi :

1. **Licences et fiches des jeux** : vérification datée sur les pages des producteurs ; `README.md` des deux jeux.
2. **Envoi vers `PowAtlas/archive`** :
   - `powatlas publish` (PC) ;
   - envoi depuis `collect.yml` (Trusted Publisher, `id-token: write`) ;
   - premier envoi de l'historique ;
   - ajout à `pc-daily.ps1`.
3. **Observations** :
   - copie datée du fichier `previous-1950-2024` ;
   - lecture de la base quotidienne (valeurs, codes, stations) depuis l'archive ;
   - collecte `meteoidro` d'Arpa sur le PC, envoyée dans `archive`.
4. **Paires** (`powatlas pairs`) : extraction au point le plus proche, cumuls, règles directe et dérivée, conversions, Parquet par saison.
5. **Scores** (`powatlas score`) : mesures, climatologie, rééchantillonnage apparié, CSV, fiche du jeu `scores`.
6. **`scores.yml`** : calcul quotidien sur GitHub Actions, premier calcul de l'historique, lien dans les README.
7. **Skill `verifier-prevision`** (`.claude/skills/`) : ce protocole, pour SP3 et suivants.

## 6. Critères d'acceptation de SP2

- `PowAtlas/archive` contient l'historique IFS, AIFS et GFS rattrapé, les observations datées et les unités quotidiennes depuis la mise en service, avec une fiche qui donne licences et attributions.
- `PowAtlas/scores` publie, pour l'historique puis chaque jour de 2026-27 :
  - les paires ;
  - les tableaux de la section 4, avec intervalles, nombre de paires, de dates et manques par modèle ;
  - les scores officiels et provisoires séparés ;
  - les directs et les dérivés séparés ;
  - la provenance des observations (date de collecte, sha256).
- Le calcul tourne sur GitHub Actions sans le PC ; un PC éteint ne retarde que GFS, Arpa et l'historique pas encore envoyé.
- Les tests passent (CI `python` et `windows`), la relecture scientifique ne laisse aucun constat bloquant, et le skill `verifier-prevision` existe.

## 7. Risques

| Risque | Parade |
|---|---|
| Hugging Face limite le stockage gratuit (« best-effort ») | Archive de référence intacte sur le PC ; volume modeste (moins de 1 Go par saison [estimation]) ; repli à qualifier parmi les offres gratuites (décision 0004) |
| Trusted Publishers indisponible ou refusé | Jeton à droits limités rangé dans les secrets GitHub |
| `meteoidro` pas à jour en saison, ou injoignable | Score français seul ; Arpa ajoutée dès que la table est à jour |
| Neige dérivée (IFS avant le 2025-11-22, GFS) trompeuse | Marquée dérivée, publiée à part ; écart dérivé/direct mesuré sur l'IFS depuis le 2025-11-22 |
| Conversion par densité fixe trompeuse (neige tassée) | Biais de référence annoncé ; sensibilité Hedstrom-Pomeroy publiée à part ; aucune revendication de qualité sur la conversion elle-même |
| Peu de paires en haute altitude, événements corrélés d'un même jour | Strates d'altitude, blocs de 7 jours appariés, nombre de dates distinctes publié |

## 8. Corrections après relecture scientifique (2026-10-27)

Changements par rapport au texte approuvé en séance, signalés au pilote :
- **IFS** :
  - neige `sf` seulement depuis le 2025-11-22 ; avant, neige dérivée de `tp` et de la température à 2 m, publiée à part ;
  - GFS suit la même règle dérivée (au lieu de `csnow`) ;
  - conversion des unités selon `GRIB_units` : l'AIFS est déjà en mm.
- **Climatologie** : arrêtée à 2020-21, pour ne chevaucher aucune saison scorée.
- **Arpa** : fenêtre et contrôle d'alignement déclarés.
- **Mesures** :
  - écart entre disponibilité du run et début de la fenêtre déclaré ;
  - formule de Hedstrom-Pomeroy et ses bornes figées ;
  - scores de compétence face à la climatologie (médiane, Brier) ;
  - rééchantillonnage apparié, avec intervalles sur les différences.
- **Observations** :
  - lues dans l'archive datée, fichier `previous` ajouté, provenance publiée ;
  - règles de seuil, de codes qualité et de fortes valeurs figées.
- **Licences et versions** : licences vérifiées avant envoi pour les deux jeux, versions des modèles publiées.
