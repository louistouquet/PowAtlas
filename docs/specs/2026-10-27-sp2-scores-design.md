# SP2 — Tableau public des scores de la neige fraîche

Document de cadrage · 27 octobre 2026 · statut : **proposé au pilote** (brainstorming du 2026-10-27 ; sections 1 à 3 approuvées en séance, texte à valider)

Ce cadrage fixe ce que SP2 livre : un tableau public, recalculé chaque jour, des scores de la neige fraîche prévue par les modèles bruts, sur l'historique rattrapé puis sur la saison 2026-27. C'est la première référence publique du projet, préalable à toute revendication de SP3. Il s'appuie sur :
- [`docs/roadmap.md`](../roadmap.md), section « Vérité terrain et tableau des scores » ;
- les rapports [R0.3](../research/R0.3-observations.md) et [R0.5](../research/R0.5-briques-open-source.md) ;
- la [décision 0007](../decisions/0007-hugging-face-au-centre-github-d-abord.md) ;
- l'archive de SP1 ([cadrage SP1](2026-10-22-sp1-archive-design.md)).

## 1. Décisions prises au brainstorming

| Sujet | Décision |
|---|---|
| Ordre | Un seul code : l'**historique d'abord** (IFS, AIFS, GFS rattrapés), puis la saison 2026-27 au fil de l'eau (pilote, 2026-10-27) |
| Lieu du calcul | **GitHub Actions** dès que possible ; le PC du pilote seulement pour ce que GitHub ne peut pas faire (rattrapage AWS, GFS, Arpa Piemonte) ([décision 0007](../decisions/0007-hugging-face-au-centre-github-d-abord.md)) |
| Publication | Organisation Hugging Face `PowAtlas` : `PowAtlas/archive` (copie publique de l'archive) et `PowAtlas/scores` (paires et scores), créés par le pilote le 2026-10-27 ([guide](../collecte/hugging-face.md)) ; le dépôt GitHub ne garde que le code et un lien ; aucune donnée dans Git |
| Méthode | Tranchée par Claude à partir des rapports R0 et de la feuille de route, à la demande du pilote ; approuvée par le pilote le 2026-10-27 (sections 4 et 5) |

## 2. Faits établis pendant le cadrage (2026-10-27)

- **Hugging Face** [producteur, documentation lue le 2026-10-27] :
  - stockage public gratuit « best-effort », sans plafond garanti ;
  - par dépôt, moins de 100 000 fichiers et moins de 10 000 entrées par dossier conseillés ;
  - écriture depuis GitHub Actions sans jeton stocké (« Trusted Publishers », jeton d'une heure limité à un dépôt, `huggingface_hub` 1.19 ou plus récent, permission `id-token: write`).
- **Mise en place** : organisation `PowAtlas`, jeux `PowAtlas/archive` et `PowAtlas/scores` publics, licence `cc-by-4.0` [vérifié, API de Hugging Face, 2026-10-27]. Les Trusted Publishers et le jeton du PC sont déclarés faits par le pilote ; le premier envoi les testera.
- **Volume** : l'archive découpée pesait 0,28 Go le 2026-10-27 [vérifié par le pilote]. Une arborescence par source, année et mois donne moins de 70 fichiers par dossier et environ 5 000 fichiers par an [estimation], loin des limites.
- **Variables de neige archivées** (catalogue de SP1) :

  | Modèle | Variable | Note |
  |---|---|---|
  | IFS, AIFS | `sf` | équivalent eau, cumulé depuis le début du run |
  | ICON-D2, ICON-EU | `snow_gsp` + `snow_con` (`lsfwe`, `csfwe`) | équivalent eau |
  | AROME 0,025°, ARPEGE 0,1° | `tsnowp` | équivalent eau |
  | GFS | aucune | précipitation totale `apcp` et indicateur `csnow` seulement |

- **Échéances** :
  - AROME s'arrête à +51 h et ICON-D2 à +48 h : pas de cumul à 48 h (+6 à +54 h) pour eux ;
  - tous les autres modèles vont au-delà de +78 h.
- **Observations de Météo-France** ([fiche](../sources/meteo-france-observations.md)) :
  - la base quotidienne (`HNEIGEF`, `QHNEIGEF`) est servie en deux fichiers par département : `previous-1950-2024` et `latest-2025-2026` ;
  - le réseau nivo-météo publie les mêmes mesures (97,3 % des paires à moins de 1 cm d'écart [vérifié, R0.3]) : à ne compter qu'une fois.
- **Arpa Piemonte** ([fiche](../sources/arpa-piemonte.md)) :
  - l'API historique `meteoidro` donne `hn` par jour pour les 18 champs de neige manuels de l'emprise (`campo_neve = S`) ;
  - elle ne répond qu'au PC du pilote depuis le 2026-10-24 [vérifié] ;
  - sa table s'arrêtait au 2026-06-30 le 2026-10-21 : délai de mise à jour en saison inconnu.

## 3. Architecture

```
GitHub Actions                          PC du pilote
  collect.yml ── unité complète ──┐      powatlas publish (rattrapage, GFS, Arpa temps réel et meteoidro)
                                  ▼          │
                        PowAtlas/archive ◄───┘
                                  │
  scores.yml (chaque jour) ◄──────┘  + base quotidienne Météo-France (téléchargée par Actions)
     powatlas pairs  → paires prévision/observation (Parquet par saison)
     powatlas score  → tableaux de scores (CSV) + fiche du jeu
                                  ▼
                        PowAtlas/scores  ◄── lien depuis le README du dépôt
```

- **`PowAtlas/archive`** :
  - même arborescence que `data` : `forecasts/<source>/<AAAA>/<MM>/`, `observations/<source>/<AAAA>/<MM>/` ;
  - fichiers et manifestes inchangés ;
  - un envoi n'ajoute que les fichiers absents ou modifiés (comparaison des sha256 du manifeste) ;
  - au plus 100 fichiers par commit.
- **Envoi depuis GitHub Actions** : `collect.yml` envoie l'unité après la collecte, si elle est complète. Une unité partielle reste en artefact : le PC la rapatrie, et une collecte complète ultérieure la remplace.
- **Envoi depuis le PC** : `powatlas publish --data data` envoie ce que l'archive de Hugging Face n'a pas encore, quelle qu'en soit l'origine : rattrapage, GFS, Arpa, unités rapatriées. Il est ajouté à `scripts/pc-daily.ps1` après le rattrapage. Le jeton `HF_TOKEN` est lu dans `.env`, jamais dans Git.
- **`scores.yml`** :
  - planifié chaque jour, plus le déclenchement à la main ;
  - il télécharge depuis `PowAtlas/archive` les seuls fichiers de neige nécessaires et la base quotidienne de Météo-France ;
  - il recalcule les paires de la saison en cours (et, au premier passage, de tout l'historique), puis les scores, et les envoie sur `PowAtlas/scores` ;
  - un run en échec ne publie rien et le tableau précédent reste en ligne.
- **Préalables au premier envoi** ([décision 0007](../decisions/0007-hugging-face-au-centre-github-d-abord.md)) :
  - licences de chaque source envoyée vérifiées et datées dans sa fiche, Licence Ouverte 2.0 et sa compatibilité avec CC BY comprises ;
  - fiche du jeu `archive` (`README.md`) avec la licence d'origine et l'attribution exigée par chaque source.

## 4. Méthode des scores

Ce protocole est figé avant tout calcul. Il est repris dans le skill `verifier-prevision`, et toute modification ultérieure crée une version datée.

### 4.1 Observations

- **Vérité officielle** :
  - `HNEIGEF` de la base quotidienne de Météo-France, valeurs validées (codes `QHNEIGEF` 0 et 1) ;
  - stations de l'emprise (départements 04, 05, 06, 38, 73, 74, coordonnées dans la boîte de SP1) ;
  - coordonnées et altitude lues dans les fichiers.
- **Score provisoire, publié à part** : mêmes calculs avec les valeurs filtrées (code 9) en plus.
- **Complément** :
  - `hn` des 18 champs de neige manuels d'Arpa Piemonte (`campo_neve = S`), par `meteoidro`, sur les mêmes saisons, publié en plus du score français ;
  - les stations `N` (automatiques) sont exclues.
- **Exclus de la vérité terrain** : neige fraîche déduite d'une hauteur totale (Nivôse, IMIS, stations `N`), neige modélisée (S2M, `HN_1D` des IMIS), parcelles SLF (pas d'historique archivé avant octobre 2026 ; à ajouter en 2027-28). Le réseau nivo-météo n'est pas compté une seconde fois.

### 4.2 Prévision comparée

- **Runs et fenêtres** :
  - run 00 UTC du jour J uniquement ;
  - `HNEIGEF(J)` (fenêtre nominale 06 UTC J → 06 UTC J+1) est comparé au cumul prévu de +6 h à +30 h ;
  - 48 h : `HNEIGEF(J) + HNEIGEF(J+1)` contre le cumul de +6 h à +54 h ;
  - 72 h : trois jours contre le cumul de +6 h à +78 h ;
  - les sommes de 48 h et 72 h exigent toutes les valeurs et sont marquées **dérivées** ;
  - le décalage d'une à deux heures entre fenêtre nominale et relevé réel est déclaré comme incertitude.
- **Point de grille** :
  - le plus proche de la station (distance sur la sphère), sans interpolation ni correction d'altitude ;
  - la distance au point et l'altitude de la station sont publiées avec chaque paire ; l'orographie des modèles n'est pas archivée en SP1 [vérifié, catalogue], donc l'écart d'altitude grille-station n'est pas publié en SP2 (à ajouter avec l'orographie si SP3 en a besoin).
- **Neige prévue en équivalent eau (mm)** :
  - IFS, AIFS : `sf` × 1000 (m d'eau) ;
  - ICON : `lsfwe` + `csfwe` ;
  - AROME, ARPEGE : `tsnowp` ;
  - GFS : somme, sur les pas de 3 h de la fenêtre, de l'incrément de `apcp` quand `csnow` vaut 1 à la fin du pas, marquée **dérivée**.
- **Conversion en hauteur** :
  - officielle : densité fixe de 100 kg/m³, soit 1 mm d'eau pour 1 cm de neige, identique pour tous les modèles ;
  - sensibilité, publiée à part : densité de Hedstrom et Pomeroy (1998), fonction de la température à 2 m du modèle au pas de la chute ;
  - les deux sont déclarées ici, avant tout score.
- **Biais de référence** : la neige observée est tassée et peut avoir fondu. Elle est attendue plus basse que la chute modélisée ; ce biais n'est pas une erreur du modèle et la fiche du jeu le dit.

### 4.3 Mesures

- **Erreur absolue moyenne et biais (erreur moyenne)**, sur trois groupes de jours :
  - tous les jours ;
  - les jours avec au moins 1 cm observé ;
  - les jours avec au moins 1 cm prévu.
- **Seuils de 1, 5, 10, 20 et 30 cm** : taux de détection, taux de fausses alertes, biais de fréquence, *equitable threat score*.
- **Incertitude** :
  - intervalle à 95 % par rééchantillonnage de blocs de 7 jours consécutifs ;
  - 2 000 tirages, graine fixée et publiée ;
  - chaque bloc garde toutes les stations de ses dates.
- **Même échantillon pour tous** : chaque comparaison se fait sur l'intersection des couples station-date disponibles pour tous ses modèles. Le nombre de paires et les manques sont publiés par modèle. Comparaisons :
  - historique : IFS, AIFS et GFS sur leur période commune, et chaque modèle seul ;
  - 2026-27 : les sept modèles, puis les groupes où un modèle manque.
- **Strates** : bande d'altitude de la station (moins de 1 200 m, 1 200-1 800 m, 1 800-2 400 m, plus de 2 400 m, la dernière signalée comme peu fournie) ; mois ; saison.
- **Climatologie de référence** :
  - neige moyenne et fréquence de chaque seuil, par station et par mois, sur les hivers 1996-97 à 2022-23 ;
  - toutes ces saisons sont antérieures aux saisons scorées : aucune donnée future n'entre dans la référence.
- **Jamais de verdict de sécurité avalanche.** La fiche du jeu `scores` renvoie au bulletin d'estimation du risque d'avalanche (BRA) de Météo-France.

### 4.4 Saisons

L'hiver va de novembre à avril.

| Saison | Modèles disponibles | Rôle (feuille de route) |
|---|---|---|
| 2021-22 à 2022-23 | GFS | entraînement |
| 2023-24 | GFS ; IFS à partir du 2024-02-01 | entraînement |
| 2024-25 | GFS, IFS ; AIFS à partir du 2025-02-26 | entraînement |
| 2025-26 | GFS, IFS, AIFS | validation (exclue de tout étalonnage de neige dérivée, règle 8 de R0.3) |
| 2026-27 | les sept modèles | vérification publique des modèles bruts, puis entraînement de SP3 |
| 2027-28 | à venir | **test**, jamais consulté avant le gel |

Les modèles bruts n'ont rien d'entraîné. Les choix de cette section sont faits avant de voir le moindre score, donc aucune saison n'est consultée pour une mise au point. Les scores quotidiens de 2026-27 ne servent à aucun réglage de SP2.

## 5. Livraison

Petites PR, tests d'abord (TDD, données synthétiques), skill `scientific-coding`, relecture par l'agent `relecteur-scientifique` pour tout code de calcul. Le plan détaillé (`docs/plans/2026-10-27-sp2-scores.md`) découpe ainsi :

1. **Licences et fiche du jeu `archive`** : vérification datée sur les pages des producteurs ; `README.md` du jeu.
2. **Envoi vers `PowAtlas/archive`** :
   - `powatlas publish` (PC) ;
   - envoi depuis `collect.yml` (Trusted Publisher, `id-token: write`) ;
   - premier envoi de l'historique ;
   - ajout à `pc-daily.ps1`.
3. **Observations** :
   - lecture de la base quotidienne de Météo-France (valeurs, codes qualité, métadonnées des stations) ;
   - collecte `meteoidro` d'Arpa sur le PC, envoyée dans `archive`.
4. **Paires** (`powatlas pairs`) : extraction au point le plus proche, cumuls, conversions, Parquet par saison.
5. **Scores** (`powatlas score`) : mesures, blocs, climatologie, CSV et fiche du jeu `scores`.
6. **`scores.yml`** : calcul quotidien sur GitHub Actions, premier calcul de l'historique, lien dans les README.
7. **Skill `verifier-prevision`** (`.claude/skills/`) : ce protocole, pour SP3 et suivants.

## 6. Critères d'acceptation de SP2

- `PowAtlas/archive` contient l'historique IFS, AIFS et GFS rattrapé et les unités quotidiennes depuis la mise en service, avec une fiche qui donne licences et attributions.
- `PowAtlas/scores` publie, pour l'historique puis chaque jour de 2026-27 :
  - les paires ;
  - les tableaux de la section 4 avec intervalles, nombre de paires et manques par modèle ;
  - les scores officiels et provisoires séparés.
- Le calcul tourne sur GitHub Actions sans le PC ; un PC éteint ne retarde que GFS, Arpa et l'historique pas encore envoyé.
- Les tests passent (CI `python` et `windows`), la relecture scientifique ne laisse aucun constat bloquant, et le skill `verifier-prevision` existe.

## 7. Risques

| Risque | Parade |
|---|---|
| Hugging Face limite le stockage gratuit (« best-effort ») | Archive de référence intacte sur le PC ; volume modeste (moins de 1 Go par saison [estimation]) ; repli à qualifier parmi les offres gratuites (décision 0004) |
| Trusted Publishers indisponible ou refusé | Jeton à droits limités rangé dans les secrets GitHub |
| `meteoidro` pas à jour en saison, ou injoignable | Score français seul ; Arpa ajoutée dès que la table est à jour |
| Conversion par densité fixe trompeuse (neige tassée) | Biais de référence annoncé ; sensibilité Hedstrom-Pomeroy publiée à part ; aucune revendication de qualité sur la conversion elle-même |
| Peu de paires en haute altitude, événements corrélés d'un même jour | Strates d'altitude, blocs de 7 jours, nombre de dates distinctes publié |
| Lecture GFS dérivée (`csnow` instantané) | Marquée dérivée, publiée avec cette mention |
