# SP1 — Archive et observations

Document de cadrage · 22 octobre 2026 · statut : **validé par le pilote le 2026-10-22** (brainstorming du même jour)

Ce cadrage fixe ce que SP1 livre : un programme de collecte quotidienne des prévisions et des observations qui disparaissent vite, une archive de référence sur la machine du pilote et le rattrapage de l'historique disponible sur AWS. Il s'appuie sur [`docs/roadmap.md`](../roadmap.md) (« Liste d'archivage SP1 », « Décisions du pilote »), [R0.2](../research/R0.2-previsions-ouvertes.md), [R0.3](../research/R0.3-observations.md) et les décisions [0001 à 0005](../decisions/README.md). Il est volontairement court : la collecte doit tourner **avant le 1er novembre 2026**.

## 1. Décisions prises au brainstorming

| Sujet | Décision |
|---|---|
| Lieu d'exécution de la collecte (roadmap, décision 8) | **Hybride** : GitHub Actions collecte chaque jour et dépose des artefacts gardés 30 jours ; le PC du pilote les rapatrie et garde l'archive de référence. Bascule sur le PC seul (même code) si GitHub conteste l'usage d'Actions ([décision 0005](../decisions/0005-collecte-hybride-actions-et-pc.md)) |
| Ordre | Le **cœur de score** d'abord (run 00 UTC des six modèles de priorité 1, observations à 7 jours, copies datées Météo-France) ; le reste suit |
| Rattrapage de l'historique | **Complet, mois d'hiver seulement** (novembre à avril), échéances jusqu'à +78 h, exécuté sur le PC après la mise en service de la collecte quotidienne : IFS 0,25° depuis le 2024-02-01, AIFS Single opérationnel depuis son premier run du flux `aifs-single/0p25/oper/` (2025-02-26), GFS depuis la saison 2021-22 ; flux AIFS expérimentaux (2024 et février 2025) écartés |
| Priorité 2 (roadmap, question 5) | **Dans SP1, après une semaine du cœur sans trou** (vers mi-novembre) ; IFS ENS limité à +78 h et récupéré par le PC depuis AWS |
| État côté Actions | Porté par le **nom des artefacts** (une unité par artefact) ; aucun commit automatique, aucun service tiers |
| Format | NetCDF4 float32 compressé par unité ; observations brutes telles que reçues |

## 2. Faits établis pendant le cadrage (2026-10-22)

- **Copie AWS d'ECMWF** [vérifié, listings et index anonymes] : grille 0,4° « beta » seule du 2023-01-18 au 2024-01-31 ; **IFS 0,25° à partir du 2024-02-01** (chemin `AAAAMMJJ/00z/0p25/oper/` jusqu'au 2024-02-28, puis `AAAAMMJJ/00z/ifs/0p25/oper/` dès le 2024-02-29) ; AIFS expérimental (`aifs/0p25`) au moins depuis le 2024-03-01, avec `tp`, `cp`, `2t` et sans `sf` ; flux `aifs-single/0p25/experimental/oper/` à partir du 2025-02-10, puis flux opérationnel `aifs-single/0p25/oper/` présent le 2025-03-01 [vérifié par le relecteur scientifique le 2026-10-22] : d'où le `NoSuchKey` du 2025-02-20 sous `0p25/oper/`. La date exacte du passage au flux opérationnel est fixée par l'inventaire de la PR 9.
- **La chute de neige `sf` de l'IFS n'est publiée qu'à partir d'une date entre le 2025-11-15 et le 2025-12-15** [vérifié sur les index de l'échéance 24 h du run 00 UTC] : avant, `tp`, `2t`, vent et niveaux de pression ; `ptype`, `mn2t3`, `mx2t3` présents le 2025-06-01 ; `sd`, `sf`, `tcc` le 2025-12-15. Conséquence : pour les saisons rattrapées, la neige de l'IFS sera **dérivée** de `tp` et des températures en SP3, et marquée comme telle.
- **AWS limite le débit** : réponses `SlowDown` répétées depuis la session cloud, même à 15 s d'intervalle [vérifié]. Le rattrapage doit être lent et reprenable.
- **Téléchargement des artefacts** : l'API REST demande un jeton (« OAuth tokens and personal access tokens (classic) need the repo scope to use this endpoint ») ; le lien de téléchargement expire après 1 minute [producteur : https://docs.github.com/en/rest/actions/artifacts, consultée le 2026-10-22]. L'accès anonyme pour un dépôt public n'est pas traité par la page : on prévoit un jeton [hypothèse, à tester en PR 8].
- **Désactivation après 60 jours sans activité** : GitHub ne définit pas l'« activité » [producteur : https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows, consultée le 2026-10-22] ; le dépôt de l'action keepalive la plus connue est « disabled by GitHub Staff due to a violation of GitHub's terms of service » [vérifié : https://github.com/gautamkrishnar/keepalive-workflow, consultée le 2026-10-22]. **Aucune astuce de maintien artificiel** (écart assumé à l'« activité garantie du dépôt » de la feuille de route, validé par le pilote le 2026-10-22) : l'activité vient du travail réel (développement, bilan mensuel), une issue prévient à 45 jours sans commit sur `main`, et l'absence d'artefact pendant 48 h déclenche une alerte sur le PC.

La fiche [`ecmwf-open-data`](../sources/ecmwf-open-data.md) est mise à jour avec ces constats.

## 3. Architecture

Un seul paquet Python, `powatlas` (dans `src/`, Python 3.12 ; dépendances `numpy`, `eccodes`, `netCDF4`, `requests` ; tests `unittest`). Mêmes commandes partout :

| Commande | Où | Rôle |
|---|---|---|
| `powatlas collect --task <tâche>` | Actions (et PC en mode secours) | Collecte les unités attendues de la tâche dans sa fenêtre de rattrapage, sans refaire ce qui est complet |
| `powatlas sync` | PC | Rapatrie les artefacts nouveaux, vérifie les empreintes, range dans `data/` (pour une unité vue plusieurs fois : `complete` avant `partielle`, puis la plus récente), met à jour l'inventaire ; alerte si aucun artefact depuis 48 h |
| `powatlas backfill --source <s> --from <date> --to <date>` | PC | Rattrapage historique depuis AWS, reprenable, à débit limité |
| `powatlas status` | partout | Tableau des unités complètes, partielles et manquantes, par source et par jour |

**Catalogue.** `src/powatlas/catalogue.toml` décrit chaque source : URL, run, échéances, variables, géométrie de grille attendue, conservation, fenêtre de rattrapage, tâche, fiche source. Un adaptateur par famille : DWD (ICON), Météo-France PNT (AROME, ARPEGE), ECMWF, GFS, SLF, Arpa Piemonte, observations Météo-France ; plus tard MeteoSwiss (ICON-CH1).

**Unité.** Une source × un run pour les prévisions ; une source × un jour de collecte pour les observations. État : `complete`, `partielle` ou `manquante`. Un artefact par unité, nommé `<source>__<AAAAMMJJTHHZ>__<état>` ; chaque job lit la liste des artefacts par l'API (jeton intégré du workflow ; permissions `actions: read`, `contents: read`, et `issues: write` pour l'issue `collecte`) pour savoir ce qui manque. Une unité partielle est recollectée en entier tant que la source la garde.

**Répartition.**

| Où | Sources | Volume |
|---|---|---|
| Actions, `collect.yml` (planifié, plus `workflow_dispatch`) | ICON-D2, ICON-EU (24 h) ; AROME 0,025°, ARPEGE 0,1° (14 jours) ; IFS, AIFS depuis le portail (4 jours) ; SLF, Arpa Piemonte temps réel (7 jours) ; copie datée du réseau nivo-météo et de la base quotidienne (`HNEIGEF`, départements 04, 05, 06, 38, 73, 74) ; puis ICON-CH1, AROME 0,01° réduit et niveaux de pression AROME (priorité 2) | environ 2 Go téléchargés par jour (3,3 Go avec la priorité 2) ; environ 26 Mo d'artefacts par jour, **gardés 30 jours** (environ 0,8 Go conservés ; R0.5 relève un plafond de stockage d'artefacts « non documenté » pour un dépôt public : rétention courte par prudence, `sync` passant au moins chaque semaine) |
| PC du pilote, tâche planifiée Windows (chaque jour où le PC est allumé et à l'ouverture de session ; au moins une fois par semaine) | `sync` ; rattrapage historique IFS, AIFS, GFS ; GFS en continu ; IFS ENS (priorité 2) | environ 185 Go une seule fois (calcul en section 5), puis environ 10 Go par semaine (IFS ENS 8,3 Go, GFS environ 0,7 Go) |

**Horaires de départ (UTC)**, hors des heures pleines, tirés de R0.2 et à **remesurer sur une semaine avant d'être figés** :

| Tâche | Sources | 1er déclenchement | 2e déclenchement |
|---|---|---|---|
| `icon-d2` | ICON-D2 | 02:35 | 08:35 |
| `icon-eu` | ICON-EU (et ICON-CH1 en priorité 2) | 05:05 | 10:35 |
| `meteofrance-pnt` | AROME, ARPEGE | 06:50 | 12:50 |
| `ecmwf` | IFS, AIFS (IFS 00 UTC publié vers 07:34) | 08:50 | 14:50 |
| `observations` | SLF, Arpa Piemonte, nivo-météo, base quotidienne | 09:50 | 17:50 |

**Fenêtres de rattrapage** (unités recollectées si absentes ou partielles) : ICON, le run du jour ; AROME et ARPEGE, J-7 à J ; IFS et AIFS, J-2 à J sur le portail (12 runs annoncés : le run 00 UTC de J-3 en sort à 08:50), au-delà depuis AWS par le PC ; observations à 7 jours, couvertes par la réponse de 7 jours de chaque appel (pour le SLF, routes par station sur 7 jours des stations de l'emprise, les routes globales ne couvrant que 24 h ; constat de la relecture du 2026-10-22) ; copies Météo-France, un jour manqué perd seulement la copie de ce jour.

**Alertes.** Le premier déclenchement reste vert même si des unités manquent. Une unité encore manquante au second déclenchement ou à la fin de sa fenêtre fait échouer le job (courriel de GitHub) et ouvre ou commente une issue étiquetée `collecte`. Sur le PC, `sync` signale l'absence d'artefact depuis 48 h ; la réactivation manuelle d'un workflow désactivé est décrite dans le guide d'installation.

## 4. Archive et journal

**SP1 archive, il n'interprète pas.** Unités et cumuls restent ceux du producteur ; aucune variable dérivée, aucune conversion : elles relèvent de SP2 et SP3.

**Prévisions** : un fichier NetCDF4 par unité, valeurs en float32, compression zlib avec *shuffle* (pas de quantification 16 bits : l'écart du float32 au champ décodé, environ 6 x 10^-8 en relatif, est très inférieur au pas d'empaquetage du GRIB ; le volume reste de 1,6 à 4,7 Go par saison au cœur). Dimensions `step x lat x lon` (`member` en plus pour l'ENS) sur la grille native, découpée sur l'emprise (ouest 5,0, sud 43,5, est 7,9, nord 46,5) **avec une marge de 2 mailles de la source** ; ICON-CH1 garde ses cellules natives en une dimension, sans réinterpolation. Attributs : source, fiche, licence et mention exigée (pour le GFS, la clause NOAA : des données modifiées ne sont pas présentées comme les données originales), URL **sans lien signé**, heure de collecte, **`Last-Modified` du producteur pour chaque fichier lu** (heure de disponibilité, indispensable pour la règle de non-fuite de SP3, en quotidien comme en rattrapage : un rattrapage date de 2026 par sa collecte, mais garde la date de dépôt du producteur), clés GRIB de chaque champ (`shortName`, `paramId`, type et valeur de niveau, `stepType`, unités, bits d'empaquetage, version du modèle quand elle existe), version et commit de `powatlas`.

**Observations** : réponses brutes telles que reçues (JSON ou CSV), compressées, horodatées à la collecte : c'est la copie datée qui garde les codes qualité du moment.

**Disposition sur le PC** (`D:\Codage\PowAtlas\data\`, ignoré par Git) :

```text
data/forecasts/<source>/<AAAA>/<MM>/<source>_<AAAAMMJJTHHZ>.nc
data/observations/<source>/<AAAA>/<MM>/<source>_<AAAAMMJJTHHMMZ>_<réponse>.<ext>.gz
data/journal/inventaire.jsonl
```

Chaque fichier a son manifeste `.json` : empreinte sha256, taille, état, mode (`quotidien`, `rattrapage`, `historique`), flux du producteur (par exemple `aifs-single/0p25/oper`), heures de collecte, `Last-Modified` le plus ancien et le plus récent des fichiers lus, URL, champs absents.

**Journal** : manifestes ; inventaire en ajout seul sur le PC ; résumé de chaque job Actions ; issue `collecte` pour les pertes définitives. `powatlas status` donne les manques par source et par jour, que SP2 publiera par modèle (règle « même échantillon pour tous »).

**Contrôles bloquants** (l'unité échoue plutôt que d'archiver une erreur) :
1. date et heure du run lues dans le GRIB différentes du run attendu (le dossier `00/` d'ICON garde le run de la veille jusqu'à son remplacement) ;
2. géométrie de grille différente du catalogue (changement de version ou de résolution signalé, jamais dilué) ;
3. échéance ou variable attendue absente : unité `partielle` ;
4. empreinte non conforme au rapatriement : rejet.

Les valeurs manquantes du GRIB (bitmap) deviennent `NaN` avec `_FillValue`. En rattrapage historique, les champs absents à une date (par exemple `sf` avant décembre 2025) sont listés dans le manifeste sans bloquer l'unité.

## 5. Périmètre détaillé

**Cœur de score, run 00 UTC** (variables et échéances de R0.2, environ 4,7 Go par saison) :

| Source | Variables | Échéances |
|---|---|---|
| ICON-D2 | `t_2m`, `tot_prec`, `snow_gsp`, `snow_con`, `h_snow`, `w_snow`, `hzerocl`, `snowlmt` | 0 à 48 h |
| ICON-EU | mêmes 8 variables | 0 à 120 h |
| AROME 0,025° | `2t`, `2r`, `10u`, `10v`, `tp`, `tsnowp`, `tgrp` | 0 à 51 h |
| ARPEGE 0,1° | `2t`, `10u`, `10v`, `tp`, `tsnowp`, `tirf`, `sd`, pression au niveau de la mer | 0 à 102 h |
| IFS 0,25° | `sf`, `sd`, `rsn`, `tp`, `ptype`, `2t`, `mn2t3`/`mx2t3` (puis `mn2t6`/`mx2t6`), `tcc`, `10u`, `10v`, `t`, `gh`, `r` à 850 hPa | 85 échéances, 0 à 360 h |
| AIFS Single | `sf`, `tp`, `2t`, `tcc`, `10u`, `10v` | 61 échéances, 0 à 360 h |

**Observations quotidiennes** : SLF (routes publiques sans paramètre de station de `openapi.json`, lu le 2026-10-22 : `imis/stations`, `imis/measurements`, `imis/measurements-precipitation`, `imis/daily-snow?period_in_days=7`, `study-plot/stations`, `study-plot/measurements` ; le `HN_1D` des stations IMIS est **modélisé** par SNOWPACK et marqué ainsi dans le catalogue, celui des parcelles est observé) ; Arpa Piemonte temps réel (`pie_neve`, `pie_anag`) ; fichier `nivo_<année>.csv.gz` du réseau nivo-météo ; fichiers `Q_<dép>_latest-<saison>_autres-parametres.csv.gz` de la base quotidienne des six départements (nom constaté le 2026-10-22 : `latest-2025-2026` ; nom de la saison suivante découvert par listing du bucket).

**Rattrapage historique (PC)**, mois de novembre à avril, run 00 UTC, échéances de 0 à +78 h **par pas de 3 h** (27 échéances ; 14 au pas de 6 h pour l'AIFS) :

| Source | Période | Jours | Champs | Requêtes (plages) | Téléchargement |
|---|---|---|---|---|---|
| IFS 0,25° | 2024-02-01 au 2026-04-30 | 452 (89 + 182 + 181) | jusqu'à 14 (champs du cœur présents à la date, plus `t`, `gh`, `r` à 850 hPa) | 14 x 27 x 452 = 171 000 au plus | 0,4 Mo x 171 000 = environ 68 Go |
| AIFS Single | flux opérationnel, du 2025-02-26 au 2026-04-30 | environ 245 (64 + 181) | 6 | 6 x 14 x 242 = 20 300 | environ 10 Go |
| GFS 0,25° | saisons 2021-22 à 2025-26 (une seule version du modèle, GFS v16 et suivantes, chemin `atmos/`) | 906 (5 x 181, plus le 29 février 2024) | 8 (`CSNOW`, `CRAIN`, `APCP`, `PRATE`, `SNOD`, `WEASD`, température à 2 m, hauteur de l'isotherme 0 °C) | 8 x 27 x 906 = 196 000 | 4,3 à 4,4 Mo mesurés par échéance (relecture du 2026-10-22) x 27 x 906 = environ 107 Go |
| **Total** | | | | **environ 387 000** | **environ 185 Go** |

Calcul [hypothèse] : tailles par champ mesurées en R0.2 et sur la fiche [`ecmwf-open-data`](../sources/ecmwf-open-data.md), extrapolées à toutes les dates ; les plages contiguës d'un même fichier sont fusionnées en une requête, ce qui réduit le nombre de requêtes. **Faisabilité à mesurer d'abord** : la PR 9 commence par un essai de débit depuis le PC du pilote (la cause des `SlowDown`, proxy de la session cloud ou bucket, n'est pas établie). Si le débit soutenu est trop faible, l'ordre de réduction est : GFS au pas de 6 h, puis IFS limité aux champs `tp`, `2t`, `sf`, `t` à 850 hPa, puis saisons les plus anciennes en dernier. GFS en continu ensuite.

**Priorité 2**, après une semaine du cœur sans trou : ICON-CH1-EPS contrôle, AROME 0,01° réduit, niveaux de pression AROME (Actions) ; IFS ENS `sf`, `tp`, `2t`, 50 membres, jusqu'à +78 h (PC, depuis AWS, environ 8 Go par semaine).

**Hors SP1** : runs 06, 12 et 18 UTC (décision en SP3) ; publication publique de l'archive ; lecture et contrôle des observations (SP2) ; sauvegarde du disque du pilote (le guide recommande une copie mensuelle de `data/` sur un disque externe).

## 6. Livraison

Seul ICON doit tourner le 1er novembre (24 h en ligne). Ensuite : SLF et Arpa avant le 8 novembre (7 jours) ; AROME et ARPEGE avant le 15 (14 jours) ; IFS et AIFS restent rattrapables sur AWS ; nivo-météo depuis 1996. Les PR suivent cette urgence :

| PR | Contenu | Cible |
|---|---|---|
| 1 | Ce cadrage, décision 0005, fiche `ecmwf-open-data` mise à jour | 22 oct. |
| 2 | Plan `docs/plans/2026-10-22-sp1-archive.md` | 23 oct. |
| 3 | Socle : paquet, catalogue, découpage, HTTP avec reprises, lecture GRIB, écriture NetCDF et manifeste, unités et fenêtres ; job CI `python` ; hook de démarrage des sessions cloud | 24 oct. |
| 4 | **ICON-D2, ICON-EU et `collect.yml`** (artefacts, deux déclenchements, état, issue `collecte`) ; premiers runs réels | 26 oct. |
| 5 | Observations SLF, Arpa Piemonte, nivo-météo, base quotidienne | 28 oct. |
| 6 | AROME et ARPEGE (lecture des en-têtes GRIB par plages d'octets) | 30 oct. |
| 7 | IFS et AIFS (portail, index, plages d'octets) | 31 oct. |
| 8 | PC : `sync`, `status`, alerte de 45 jours sans commit, guide d'installation Windows et tâche planifiée (jeton demandé au pilote à cette étape) | début nov. |
| 9 | Rattrapage historique IFS, AIFS, GFS ; GFS en continu | nov. |
| 10 | Priorité 2 | mi-nov. |
| 11 | Horaires remesurés et figés ; clôture de SP1 | fin nov. |

En cas de retard, les PR 4 et 5 passent avant tout ; le reste glisse sans perte de données.

**Tests et relecture.** TDD avec `unittest` ; skill `scientific-coding` pour le découpage, le GRIB et les contrôles. **Aucune donnée tierce dans le dépôt** : messages GRIB de test fabriqués à partir des modèles d'`eccodes`, index synthétiques, réseau simulé ; aucun appel réseau dans les tests unitaires. Chaque adaptateur est validé par un lancement réel (`workflow_dispatch`) avant d'être déclaré en service, résultat noté dans sa PR. Nouveau job CI `python`, à ajouter par le pilote aux vérifications obligatoires de `main`. Relecture par un agent à chaque PR (`relecteur-scientifique` pour le découpage et les contrôles).

**Hook de démarrage des sessions cloud** (cadrage SP0, §6) : `.claude/settings.json` lance `scripts/session-start.sh`, actif seulement en session cloud, idempotent, qui installe `pip install -e .[dev]` et vérifie `import eccodes`.

## 7. Critères d'acceptation de SP1

1. Le run 00 UTC des six modèles du cœur et les observations SLF et Arpa Piemonte sont collectés chaque jour sans intervention, du 1er novembre (ICON) ou de leur date de mise en service au 30 novembre, avec chaque manque visible dans `powatlas status` et, s'il est définitif, dans une issue `collecte`.
2. L'archive de référence existe sur le PC du pilote, rapatriée par `sync`, empreintes vérifiées.
3. Le rattrapage historique IFS, AIFS et GFS est fait sur les mois d'hiver prévus, avec ses champs absents listés.
4. La priorité 2 tourne.
5. Les horaires sont remesurés sur une semaine et figés ; `STATUS.md` et `NEXT.md` sont à jour.

## 8. Risques

| Risque | Parade |
|---|---|
| GitHub conteste l'usage d'Actions | Bascule sur le PC seul (décision 0005), même code |
| Workflows planifiés retardés, perdus ou désactivés | Deux déclenchements, fenêtres de rattrapage, `workflow_dispatch`, issue à 45 jours sans commit, alerte de 48 h sur le PC (dont la tâche tourne chaque jour où le PC est allumé) ; pas d'astuce de maintien |
| Changement de format chez un producteur | Contrôles bloquants de grille et de date ; issue `collecte` |
| Débit limité par AWS | Essai de débit d'abord, rattrapage lent et reprenable avec reprise sur `SlowDown`, ordre de réduction fixé (section 5) |
| Charge sur les serveurs des producteurs | Requêtes espacées de 0,2 s au moins par job, 4 jobs en parallèle au plus (environ 20 requêtes par seconde au pire, pendant un rattrapage de 7 jours) ; un run ARPEGE complet demande environ 3 250 requêtes (en-têtes et plages), AROME environ 1 000, IFS environ 1 000 (85 index et environ 12,5 plages par échéance, environ 420 Mo), AIFS environ 370 ; budget de 75 min par unité, au-delà de quoi l'unité est écrite `partial` |
| Stockage d'artefacts plafonné | Rétention de 30 jours ; volume conservé environ 0,8 Go |
| Disque unique du pilote | Copie mensuelle recommandée ; publication publique plus tard |
| Faits encore à mesurer : 4 messages des fichiers de cumul ICON, contenu des paquets AROME, routes SLF, nom annuel des fichiers de la base quotidienne, arborescence `aifs-single` | Une étape d'inspection en tête de chaque PR d'adaptateur |
