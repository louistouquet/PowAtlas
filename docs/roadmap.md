# Cible et feuille de route

Document de synthèse de la recherche R0 · 21 octobre 2026 · statut : **proposé, à valider par le pilote**

Ce document tire les conclusions des cinq rapports R0 : [R0.1 Concurrence](research/R0.1-concurrence.md), [R0.2 Prévisions ouvertes](research/R0.2-previsions-ouvertes.md), [R0.3 Observations](research/R0.3-observations.md), [R0.4 Historique](research/R0.4-historique.md), [R0.5 Briques open source](research/R0.5-briques-open-source.md). Chaque rapport a été contrôlé (liens et licences) et relu par l'agent `relecteur-scientifique` ; tous les constats bloquants et importants ont été corrigés. Les chiffres viennent de ces rapports, qui donnent leurs sources datées ; ce document n'ajoute aucun fait nouveau, seulement des décisions proposées.

**En une phrase :** PowAtlas peut se distinguer par la **preuve** (scores publics de la neige fraîche, probabilités calibrées, données et code ouverts), pas par l'affichage, déjà bien servi ; la vérité terrain ouverte existe pour l'échéance 24 h ; l'archive des prévisions doit démarrer avant le 1er novembre 2026 ; le pilote a décidé qu'elle serait stockée sur sa machine (`D:\Codage\PowAtlas`) ; la collecte quotidienne sera un programme planifié dont le lieu d'exécution (PC, GitHub Actions ou les deux) est la première décision de SP1.

## Fonctionnalités de la v1

La v1 est ce que livrent SP1 à SP3. Les fonctionnalités sont classées par priorité ; chacune est reliée à la lacune constatée dans [R0.1](research/R0.1-concurrence.md) (section « Fonctionnalités où PowAtlas peut être meilleur »). Ce sont des hypothèses de positionnement : **aucune ne sera revendiquée sans score public face à une référence**.

| Rang | Fonctionnalité | Lacune constatée (R0.1) | Sous-projet | Condition pour la revendiquer |
|---|---|---|---|---|
| 1 | **Tableau public des scores de la neige fraîche** à 24, 48 et 72 h, par bande d'altitude, reproductible | Aucun service lu ne publie de score de la neige : Meteoblue publie des scores de précipitations (et de température [tiers, page non ouverte]) ; OpenSnow annonce « jusqu'à 50 % plus précis » sans score ; SkiWeather, Snow-Forecast, SnowSure : aucun score d'erreur | SP2 | Scores calculés sur des saisons entières, avec incertitude par blocs et code publié |
| 2 | **Archive ouverte et données ouvertes** : prévisions archivées, observations, fiches sources, code et expériences (échecs compris) | Modèles fermés chez OpenSnow, Snow-Forecast, Meteoblue ; SnowSure ne publie que sa documentation ; aucun projet ouvert équivalent trouvé pour les Alpes | SP1 (archive), SP2 | Jeu de données public avec fiche et licence, mis à jour chaque jour |
| 3 | **Méthode transparente** : modèles nommés, versions, délais, fiche source pour chaque entrée | OpenSnow, Snow-Forecast et SkiWeather ne nomment aucun modèle ; SnowSure annonce « sept modèles » sans détail | Dès SP1 | Chaque sortie renvoie à ses fiches sources |
| 4 | **Neige fraîche par bande d'altitude, par massif**, dans les bandes couvertes par la vérité terrain (1 200 à 2 400 m) ; **limite pluie-neige** seulement si une source de vérification est trouvée (aucune identifiée en R0.3) | Snow-Forecast : trois altitudes sans méthode ; Météo-France : neige à 1800 m et limite pluie-neige dans l'aperçu du BRA, sans score ni probabilité [tiers, non relu] | SP3 | Bat le meilleur modèle brut au tableau des scores, dans chaque bande d'altitude vérifiée |
| 5 | **Probabilités calibrées de neige fraîche** (quantiles, probabilité de dépasser des seuils fixés dans le protocole de SP2), avec diagramme de fiabilité publié | Aucune probabilité calibrée dont la fiabilité est publiée : OpenSnow donne une confiance qualitative, SkiWeather une fourchette | SP3 | Fiabilité et CRPS publiés, meilleurs que l'ensemble IFS brut |
| 6 | **Alertes poudre gratuites** par région, en plusieurs temps ; en v1, limitées au run 00 UTC (le seul vérifié) | Alertes personnalisées payantes chez OpenSnow (99,99 USD par an) ; WePowder non vérifié | SP3, après les rangs 1, 4 et 5 | Une alerte sans score n'apporte rien : publiée seulement avec ses taux de détection et de fausses alertes ; chaque alerte renvoie au BRA de Météo-France. Les runs 06, 12 et 18 UTC n'entrent dans les alertes qu'avec une règle de vérification et un archivage propres |

Ordre : R0.1 place les probabilités au 2e rang et l'ouverture au 4e. Ce document remonte l'ouverture et la transparence (rangs 2 et 3) parce qu'elles se livrent dès SP1 et SP2 sans attendre de modèle, et place les probabilités après la neige par altitude parce qu'elles exigent l'ensemble archivé et des saisons d'entraînement (SP3). L'ordre de valeur pour l'usager reste celui de R0.1.

Hors v1 : vue unifiée observé / modélisé / prévu (dépend du manteau neigeux, SP4) ; API et serveur MCP (SP6). **Jamais** : verdict de sécurité avalanche. PowAtlas renvoie au BRA de Météo-France et ne duplique ni le BRA ni les retours communautaires (Skitour, Camptocamp) : il les cite.

## Liste d'archivage SP1

Reprise de [R0.2](research/R0.2-previsions-ouvertes.md) (section « Liste d'archivage SP1 »), où sont détaillés variables, échéances, volumes, calculs, accès et horaires. Toutes les sources ci-dessous sont lisibles **sans compte**. L'emprise est découpée côté client (aucun serveur ne découpe) ; seules des métadonnées de moins de 100 Ko vont dans Git.

### Prévisions, par ordre de priorité

**Principe proposé : démarrer par le « cœur de score ».** La règle de vérification fixée en R0.3 ne compare aux observations que le **run 00 UTC** du jour J. Archiver d'abord ce run pour chaque source de priorité 1 coûte **4,7 Go par saison** (1er novembre au 30 avril, facteur de compression prudent 0,4 ; 1,6 à 3,6 Go aux taux mesurés) et environ 2 Go de téléchargement par jour, contre 18,7 Go et 7,6 Go par jour pour les quatre runs. Les runs 06, 12 et 18 UTC (environ trois quarts du volume) ne servent qu'aux alertes à court terme de SP3 : ils s'ajoutent si l'hébergement le permet.

| Ordre | Source (fiche) | Fenêtres de score couvertes par le run 00 UTC | Conservation sur le portail | Licence |
|---|---|---|---|---|
| 1 | ICON-D2, DWD ([`icon-dwd`](sources/icon-dwd.md)) | 24 h | **24 h, aucun rattrapage** | CC BY 4.0 |
| 2 | ICON-EU, DWD ([`icon-dwd`](sources/icon-dwd.md)) | 24, 48, 72 h | **24 h, aucun rattrapage** | CC BY 4.0 |
| 3 | AROME France 0,025°, Météo-France ([`arome`](sources/arome.md)) | 24 h (horizon 51 h < +54 h) | 14 jours | Licence Ouverte 2.0 |
| 4 | ARPEGE 0,1°, Météo-France ([`arpege`](sources/arpege.md)) | 24, 48, 72 h | 14 jours | Licence Ouverte 2.0 |
| 5 | ECMWF IFS 0,25° ([`ecmwf-open-data`](sources/ecmwf-open-data.md)) | 24, 48, 72 h | portail 12 runs annoncés ; copie AWS depuis 2023-01-18 (non garantie) | CC BY 4.0 |
| 6 | ECMWF AIFS Single ([`ecmwf-open-data`](sources/ecmwf-open-data.md)) | 24, 48, 72 h | idem | CC BY 4.0 |
| 7 (prio. 2) | ICON-CH1-EPS contrôle, MeteoSwiss ([`icon-ch-meteoswiss`](sources/icon-ch-meteoswiss.md)) | 24 h | 24 h | CC BY 4.0 |
| 8 (prio. 2) | AROME 0,01° réduit et niveaux de pression AROME (isotherme 0 °C à dériver) ([`arome`](sources/arome.md)) | 24 h | 14 jours | Licence Ouverte 2.0 |
| 9 (prio. 2) | ECMWF IFS ENS, `sf`, `tp`, `2t`, 50 membres | 24, 48, 72 h | comme IFS | CC BY 4.0 |
| 10 (prio. 3) | ICON-CH2-EPS, GFS ([`gfs`](sources/gfs.md)), AROME IFS | 24, 48, 72 h (sauf AROME IFS, 24 h) | 24 h à plusieurs années (GFS sur AWS) | CC BY 4.0 (ICON-CH2), NOAA, usage libre (GFS), Licence Ouverte 2.0 (AROME IFS) |

L'ordre suit l'urgence (conservation la plus courte d'abord) puis l'utilité pour les scores. Volumes : priorité 1 au run 00 UTC 4,7 Go par saison ; priorités 1 et 2 au run 00 UTC 16,6 Go ; priorités 1 et 2 avec tous leurs runs (4 runs, sauf AROME 0,01° et IFS ENS à 2 runs) 55 Go. L'IFS ENS est la seule source d'ensemble de la liste : le repousser retarde la référence probabiliste du rang 5, sauf rattrapage depuis la copie AWS. Non archivés : PE-ARPEGE (105 Go par run), AROME-PI et PE-AROME métropole (compte gratuit requis, décision du pilote), ECMWF 0,1° (surcoût sans gain prouvé), Open-Meteo (comparaison seulement, pas une archive).

**Exigences de fonctionnement**, toutes issues des relectures de R0.2 et R0.5, valables où que tourne le programme de collecte (décision 8) : deux déclenchements idempotents par run pour les sources à 24 h de conservation ; déclenchement manuel (`workflow_dispatch`) et détection automatique des runs manquants ; rattrapage quotidien de J-2 à J-7 pour AROME et ARPEGE (S3 Météo-France) et pour ECMWF et GFS (AWS) ; activité garantie du dépôt, car GitHub désactive les workflows planifiés d'un dépôt public après 60 jours sans activité ; horaire UTC de R0.2 à remesurer sur une semaine avant d'être figé.

**Rattrapage de l'historique (proposition, à confirmer en tête de SP1).** Pour que SP3 ait des saisons d'entraînement sans attendre plusieurs hivers, récupérer en SP1, sur l'emprise, ce que la copie AWS d'ECMWF conserve de l'IFS 0,25° et de l'AIFS, et l'historique de GFS (AWS, depuis 2021). La liste des dates de la copie AWS commence le 2023-01-18, mais seuls l'IFS 0,25° au 2025-01-01 et l'AIFS au 2026-06-01 ont été vérifiés ; les arborescences de 2024 n'ont pas été explorées ([`ecmwf-open-data`](sources/ecmwf-open-data.md)). D'après Open-Meteo ([`open-meteo`](sources/open-meteo.md)), l'IFS 0,25° n'existe que depuis le 2024-02-03 et l'AIFS Single depuis le 2025-02-20 : on peut donc espérer **l'IFS depuis février 2024 et l'AIFS depuis février 2025 au plus**, avec des changements de version et de résolution à documenter. Pour AROME, ARPEGE et ICON, aucune archive ouverte n'a été trouvée au-delà de 14 jours : leurs saisons d'entraînement commencent en 2026-27. Open-Meteo n'y change presque rien : son Historical Forecast n'est fait que des premières heures de chaque run (inutilisable à 24-72 h) ; seul Previous Runs (depuis janvier 2024 pour la plupart des modèles) donne des échéances décalées, licence par modèle à confirmer.

### Observations à archiver chaque jour

D'après [R0.3](research/R0.3-observations.md) (règle 10) : l'API du SLF ([`slf-imis`](sources/slf-imis.md)) et l'API temps réel d'Arpa Piemonte ([`arpa-piemonte`](sources/arpa-piemonte.md)) ne remontent que 7 jours ; elles s'archivent chaque jour dès SP1 (l'historique journalier d'Arpa Piemonte, lui, reste interrogeable depuis 1983). L'archive du réseau nivo-météo de Météo-France ([`reseau-nivo-meteo`](sources/reseau-nivo-meteo.md), 1996 à aujourd'hui) et la base climatologique quotidienne ([`meteo-france-observations`](sources/meteo-france-observations.md)) restent téléchargeables : on en garde une copie quotidienne avec la date de collecte et le code qualité, pour la traçabilité des scores.

## Vérité terrain et tableau des scores

De [R0.3](research/R0.3-observations.md) et [R0.4](research/R0.4-historique.md). Le protocole détaillé sera écrit en SP2 (skill `verifier-prevision`) et chaque essai suivra le skill `experience-modele`.

**Variable vérifiée.** Neige fraîche à 24 h, `HNEIGEF` de Météo-France : neige tombée de 06 UTC J à 06 UTC J+1 qui reste au sol à 06 h, relevée le matin de J+1 (vers 07-08 UTC en pratique). C'est une mesure manuelle **directe**, ouverte (Licence Ouverte 2.0), sur environ 80 stations de l'emprise, essentiellement entre 1 200 et 2 400 m. Compléments directs : 18 stations d'Arpa Piemonte à champ de neige manuel (`campo_neve = S`, sens établi par recoupement le 2026-10-22) et 16 parcelles d'étude du SLF (non testées en saison). Les cumuls 48 et 72 h sont des sommes de valeurs quotidiennes consécutives, toutes présentes : ils sont **dérivés** et marqués comme tels.

**Ce qui n'est pas une vérité terrain.** Neige fraîche déduite d'une hauteur totale (Nivôse, IMIS, stations automatiques d'Arpa) : publiée à part comme dérivée (le test de R0.3 montre une sous-estimation de 23 à 37 % selon l'estimateur sur postes manuels ; aucun étalonnage disponible pour les capteurs automatiques). Neige fraîche modélisée : réanalyses (S2M, ERA5-Land, CERRA), `HN_1D` des stations IMIS (calculé par SNOWPACK), cartes S3M de la Vallée d'Aoste ; jamais présentées comme des observations. Hauteurs déclarées des stations de ski, Skitour, Camptocamp : écartées.

**Alignement prévision / observation.** Run de **base** 00 UTC du jour J uniquement ; cumul prévu entre +6 et +30 h (24 h), +6 et +54 h (48 h), +6 et +78 h (72 h). Ce run n'est **disponible** qu'entre environ 04 et 07:40 UTC selon le modèle (IFS vers 07:34, AIFS de 05:45 à 07:34, AROME jusqu'à +5,6 h ; R0.2) : la fenêtre de 24 h commence donc parfois avant la disponibilité, écart à déclarer pour les modèles bruts. Pour les corrections de SP3, la prévision est réputée émise à l'heure de disponibilité du dernier modèle utilisé, et **tout prédicteur (observation comprise) doit être disponible à cette heure**, d'après les délais mesurés en R0.2 et R0.3 (le relevé nivo-météo de J n'arrive que le matin de J+1, la base quotidienne avec deux jours de retard). La variable prévue et sa conversion en hauteur (densité fixe ou modèle de densité) sont déclarées avant l'essai ; la neige tassée observée est attendue plus basse que la chute modélisée (biais de référence, à ne pas lire comme une erreur du modèle).

**Mesures.** Erreur absolue moyenne et biais, sur tous les jours, sur les jours avec neige observée d'au moins 1 cm **et** sur les jours avec neige prévue d'au moins 1 cm (une stratification sur l'observé seul favorise les modèles qui surestiment) ; pour les seuils, taux de détection, taux de fausses alertes et score de Brier ; pour les sorties probabilistes CRPS et diagramme de fiabilité. Les seuils diffèrent selon les rapports (1, 5, 10, 20 cm en R0.3 ; 5, 10, 20, 30 cm en R0.5) : ils seront harmonisés et figés dans le protocole de SP2, comme la longueur des blocs (une semaine proposée par R0.3), avant tout calcul. Incertitude par rééchantillonnage par blocs de dates consécutives, chaque bloc gardant toutes les stations des mêmes dates (les événements d'un même jour sont corrélés : 1 693 cas de 5 cm ou plus en 2025-26, mais sur 69 dates seulement). **Même échantillon pour tous** : les modèles comparés sont scorés sur l'intersection des couples station-date disponibles pour chacun (les runs ICON perdus ne se rattrapent pas, ceux d'ECMWF et de GFS si), et les manques sont publiés par modèle.

**Qualité et reproductibilité.** Code qualité et date de collecte archivés avec chaque observation ; scores **officiels** sur les valeurs validées (codes 1 et 0), score **provisoire** séparé sur les valeurs filtrées. Scores valables par bande d'altitude ; aucune vérité terrain suffisante au-dessus de 2 500 m.

**Références à battre**, avec la saison à partir de laquelle chacune est calculable :

| Référence | Modèles | Calculable à partir de |
|---|---|---|
| (1) Modèle brut au point de grille le plus proche, même conversion | tous (AROME, ARPEGE, ICON-D2, ICON-EU, IFS, AIFS) | 2026-27 (SP2) ; plus tôt pour IFS, AIFS, GFS si le rattrapage AWS est confirmé |
| (2) Climatologie des observations (neige fraîche par station et par date, sur les saisons d'entraînement, observations disponibles depuis 1996) | toutes les comparaisons | dès SP2 |
| (3) Correction simple du biais selon l'écart d'altitude grille-station, apprise sur les seules saisons d'entraînement | IFS, AIFS, GFS si rattrapés ; AROME, ARPEGE, ICON | 2026-27 pour les premiers (entraînés sur les saisons rattrapées) ; **2027-28** pour les modèles fins (entraînés sur 2026-27) |
| (4) Ensemble IFS brut, pour les probabilités | IFS ENS | dès son archivage (priorité 2) ou son rattrapage |

Les modèles bruts sont la première référence publique (cadrage, SP2).

**Saisons : proposition de rôles, à figer avant le protocole de SP2.** Le cadrage (§3) prévoit que 2026-27 serve à « entraîner et vérifier » ; la proposition le précise ainsi :

| Saison | IFS, AIFS, GFS (si rattrapés) | AROME, ARPEGE, ICON (archive PowAtlas) |
|---|---|---|
| 2023-24 (IFS dès février 2024 au plus) et 2024-25 (AIFS dès février 2025 au plus) | entraînement | non disponibles |
| 2025-26 | validation, **exclue de tout étalonnage de la neige dérivée** (règle 8 de R0.3 : cette saison a déjà servi au test de dérivation ; elle est exclue soit de l'étalonnage, soit du test, jamais des deux) | non disponibles |
| 2026-27 | vérification publique des modèles bruts (SP2), puis entraînement | vérification publique des modèles bruts (SP2), puis entraînement de SP3 |
| 2027-28 | **test**, touché une seule fois | **test** : première saison où une correction des modèles fins peut être revendiquée |

Une saison consultée pour la mise au point (choix de conversion, de seuils, de modèles) ne devient jamais saison de test. Tout étalonnage (y compris celui de la neige dérivée) se fait sur les seules saisons d'entraînement. Conséquence : une revendication de gain sur AROME, ARPEGE ou ICON n'est possible qu'au printemps 2028 ; sur l'IFS, plus tôt si le rattrapage est confirmé.

**Règle de non-fuite** ([R0.4](research/R0.4-historique.md)) : une réanalyse n'est **jamais un prédicteur** (elle n'existe pas à l'heure d'émission). Elle sert de cible modélisée, de climatologie calculée sur les saisons d'entraînement, ou de forçage d'une réduction d'échelle nommée comme telle. S2M (seule réanalyse conçue pour la neige alpine, 1958-2021 dans sa version documentée, rupture le 2017-08-01) et COMEPHORE (précipitations radar à 1 km, Licence Ouverte 2.0) sont les deux candidats les plus utiles à SP3.

## Réutiliser ou construire

De [R0.5](research/R0.5-briques-open-source.md) (tableau « réutiliser / construire »).

| Décision | Briques | Raison |
|---|---|---|
| **Réutiliser** | `scores`, `xskillscore` (scores) ; `xarray`, `zarr`, `eccodes`, `cfgrib`, `ecmwf-opendata` (données) ; `MetPy` (thermodynamique) | Licences Apache-2.0, MIT ou BSD, versions publiées en 2025-2026 |
| **Construire** | Archivage quotidien et rattrapage (SP1) ; scores propres à la neige et tableau public (SP2) ; module de neige fraîche et de séparation pluie-neige à options, testé contre les mesures (SP3) | Aucune brique existante ne fait cela pour les Alpes avec scores publics |
| **Évaluer en SP4** | Crocus via `snowtools` (CeCILL-C, référence Météo-France) contre SNOWPACK (LGPL-3.0) ; openAMUNDSEN ou FSM2 (MIT) comme modèles légers | Choix par une fiche d'expérience : score sur les hauteurs de neige mesurées et temps de calcul dans les limites gratuites |
| **Écarter** | `properscoring` (abandonnée depuis 2015) ; MET/METplus en CI (trop lourds) ; intégration de code AGPL (Open-Meteo) dans le code Apache-2.0 | Maintenance, poids, compatibilité de licence |

Méthodes de séparation pluie-neige candidates pour SP3 : température de bulbe humide de Wang 2019 (calibrée sur l'ouest des États-Unis : validité alpine à tester), Jennings 2018 ; densité de la neige fraîche de Hedstrom-Pomeroy 1998 (fonction de la température seule). Calcul : le programme de collecte sur la machine du pilote et/ou GitHub Actions (décision 8) ; GitHub Actions (jobs de 6 h, 4 vCPU, 16 Go, 14 Go de disque, gratuit en dépôt public) pour la CI et, si besoin, les calculs légers de scores ; Kaggle (30 h de GPU par semaine) pour les essais d'apprentissage, compte requis.

## Ordre des sous-projets

**Confirmé, avec trois ajustements.**

1. **SP1 se scinde en deux temps, l'archive des prévisions d'abord.** Raison : les prévisions ICON sont perdues après 24 h, AROME et ARPEGE après 14 jours, alors que les observations de Météo-France restent téléchargeables (archive depuis 1996). Les observations à 7 jours (SLF, API temps réel d'Arpa Piemonte) rejoignent le premier temps, car elles sont perdues aussi. Objectif : archivage du cœur de score en service **avant le 1er novembre 2026**, sous réserve des décisions du pilote ci-dessous ; le cadrage de SP1 doit donc être court.
2. **SP2 démarre pendant la saison 2026-27**, dès que les premières semaines d'archive et d'observations existent : vérifier les modèles bruts n'exige aucun entraînement. Raison : c'est la fonctionnalité de rang 1 et le préalable à toute revendication.
3. **SP3 s'appuie sur l'historique reconstitué** (IFS depuis février 2024 et AIFS depuis février 2025 au plus, GFS depuis 2021, à confirmer) en attendant que l'archive AROME, ARPEGE et ICON couvre plusieurs saisons ; le rôle des saisons ci-dessus précise le « entraîner et vérifier » du cadrage et est soumis au pilote. SP4 (manteau) suit SP3 ; SP5 attend au moins une saison complète d'archive ; SP6 se construit progressivement à partir de SP2.

## Risques

| Risque | Effet | Parade proposée |
|---|---|---|
| **Conditions d'utilisation de GitHub Actions** : charge « disproportionate to the benefits provided to users » et activité « unrelated to the production, testing, deployment, or publication of the software project » interdites | Un archivage quotidien de 2 à 19 Go pourrait être jugé non conforme ; l'archive s'arrêterait | Levé avec l'option A (machine du pilote) ; demeure avec l'option hybride C recommandée, avec bascule immédiate sur A si GitHub le conteste (décision 8) |
| **Machine du pilote éteinte ou hors ligne** (nouveau risque, conséquence de la décision) | Runs ICON perdus après 24 h ; AROME et ARPEGE après 14 jours | Tâche planifiée Windows qui rattrape tout ce qui reste disponible au réveil (ICON : dernières 24 h ; AROME, ARPEGE : 14 jours ; ECMWF, GFS : copie AWS) ; journal des runs manquants ; option à trancher en SP1 : un petit job Actions de secours pour ICON seul (environ 0,6 Go téléchargés par jour au run 00 UTC) |
| **Disque unique** : l'archive n'existe qu'à un seul endroit tant qu'elle n'est pas publiée | Perte de l'archive en cas de panne | Sauvegarde régulière (second disque ou support externe du pilote) ; publication publique dès qu'un hébergeur gratuit et fiable est qualifié |
| **Hébergement public de l'archive** (fonctionnalité de rang 2) : Hugging Face « best-effort », sans plafond garanti | Publication des données retardée | Le stockage de référence est la machine du pilote ; la publication est qualifiée plus tard parmi les offres gratuites (Hugging Face, Zenodo, Kaggle Datasets, GitHub Releases), sans demande de subvention |
| Workflows planifiés retardés, perdus, ou désactivés après 60 jours sans activité du dépôt | Runs ICON perdus (24 h de conservation) | Double déclenchement, détection des manques, rattrapage, activité garantie du dépôt |
| Comptes gratuits requis : Copernicus CDS (ERA5-Land, CERRA), portail API Météo-France (AROME-PI, PE-AROME, temps réel), Copernicus Data Space (satellite), Hugging Face (archive), Kaggle (GPU) | Sources inutilisables sans accord du pilote | Décision groupée du pilote au cadrage SP1 |
| Vérité terrain limitée à 1 200-2 400 m et à l'échéance 24 h directe | Scores faibles en haute altitude et à 48-72 h | Le dire dans chaque score ; dérivé publié à part ; chercher d'autres observations en SP2 |
| Non-stationnarité : changements de version d'AROME, changements de version et de résolution de l'IFS sur la période rattrapée, rupture de S2M en 2017 | Corrections apprises qui ne tiennent plus | Saison la plus récente en test ; versions de modèle archivées avec les données |
| Faits non encore confirmés : historique réel de la copie AWS d'ECMWF (arborescences 2023-2024, résolution), durée exacte de la période `perssfrai` (les codes `-99` et `-50` distinguent les relevés du matin et de l'après-midi, sans définition du producteur ; `HNEIGEF` reste la référence), origine du `hn` des stations automatiques d'Arpa, licence et extension de S2M (AERIS injoignable depuis la session), fin réelle de CERRA, contenu officiel des paquets AROME | Choix fondés sur des hypothèses marquées | Vérifications en tête du cadrage SP1, par recherche documentaire (pas de contact extérieur, décision 7) |
| Concurrence mal connue : WePowder et Snowdata illisibles depuis la session, plusieurs services non couverts | Positionnement à affiner | Nouvelle lecture en SP6 ; aucune revendication sans score |
| Méthode de recherche : plafond de 25 sources dépassé par plusieurs axes (jusqu'à environ 33) ; Exa indisponible pour R0.1, R0.2 et R0.4 (authentification refusée), utilisé par R0.3 et R0.5 | Coût de recherche plus élevé que prévu ; moins de recherche sémantique | Validation du pilote ; vérifier l'autorisation d'Exa dans les connecteurs |

## Décisions du pilote (2026-10-21)

Retours du pilote sur la première version de ce document :

1. **Stockage de l'archive et du dépôt sur la machine du pilote**, dans `D:\Codage\PowAtlas` : clone complet du dépôt, et données d'archive dans un sous-dossier ignoré par Git (`data/`). On pousse sur GitHub le code et les métadonnées de moins de 100 Ko quand c'est possible ; les données ne vont jamais dans Git. Conséquence : la machine du pilote garde l'archive de référence (zéro euro), ce qui lève la limite de stockage de GitHub ; le lieu d'exécution de la collecte est précisé par la décision 8 ; la session cloud ne peut pas écrire sur cette machine, le pilote y lance le code de SP1.
2. **Hugging Face** n'était envisagé que pour **héberger publiquement l'archive**. Pour l'entraînement (SP3, SP5) : les offres de calcul gratuites (Kaggle, Colab), et d'autres offres gratuites seulement si elles ne suffisent pas. Pour le site (SP6) : uniquement des hébergements gratuits et durables, à qualifier en SP6 ; premier candidat relevé le 2026-10-21 : GitHub Pages (site publié de 1 Go au plus, bande passante « soft » de 100 Go par mois, usage commercial interdit, ce qui convient à un projet non commercial) [producteur : https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits].
3. **Connecteurs** : le pilote a autorisé tous les connecteurs ; Exa répond de nouveau dans la session (test du 2026-10-21).

Second retour (2026-10-22) :

4. **Comptes gratuits : tous autorisés** (Copernicus CDS, Copernicus Data Space, portail API Météo-France, Hugging Face, Kaggle). Le pilote les crée lui-même au moment où SP1 en a besoin ; les jetons vont dans les secrets (GitHub ou fichier local ignoré par Git), jamais dans le dépôt.
5. **Entraînement** : la meilleure offre gratuite du moment, et d'autres offres gratuites en plus si nécessaire.
6. **Rattrapage de l'historique ECMWF en SP1 : oui.**
7. **Aucun contact extérieur** : le sens des codes `campo_neve` (Arpa Piemonte) et `perssfrai` (Météo-France) s'établit par recherche documentaire et par l'analyse des données publiques. Fait le 2026-10-22 : `campo_neve = S` = champ de neige à relevé manuel (preuve élevée) ; `perssfrai` `-99` / `-50` = relevé du matin / de l'après-midi d'après les données, sans définition du producteur (voir les fiches [`arpa-piemonte`](sources/arpa-piemonte.md) et [`reseau-nivo-meteo`](sources/reseau-nivo-meteo.md)).
8. **Qui collecte les données chaque jour, tout l'hiver ?** Ni une session Claude (elle ne tourne pas en continu), ni le site (SP6, bien plus tard) : un **programme planifié**, écrit et testé en SP1, qui tourne seul chaque jour. Le lieu d'exécution est la **première décision du cadrage SP1** :

| Option | Avantage | Limite |
|---|---|---|
| A. Machine du pilote seule (tâche planifiée Windows) | Aucun doute sur les conditions d'utilisation ; stockage direct dans `D:\Codage\PowAtlas\data` | Le PC doit être allumé chaque jour : un arrêt de plus de 24 h perd les runs ICON |
| B. GitHub Actions seul | Tourne sans le PC, gratuit en dépôt public | Doute sur les conditions d'utilisation d'Actions ; pas de stockage durable (artefacts 90 jours au plus) |
| **C. Hybride (recommandé)** | Actions collecte chaque jour le cœur de score (environ 2 Go téléchargés, environ 26 Mo conservés) et le dépose en artefact à durée courte ; le PC rapatrie dans `D:\Codage\PowAtlas\data` dès qu'il est allumé et garde l'archive de référence | Le doute sur Actions demeure : si GitHub le conteste, bascule immédiate sur l'option A, le code étant le même |

La recommandation C donne la meilleure chance d'avoir **un hiver complet sans trou**, ce qui compte le plus pour SP2 et SP3.

Les questions 2, 3, 4, 6 et 9 ci-dessous sont donc tranchées ; les autres restent ouvertes.

## Questions pour le pilote

1. **Validez-vous cette feuille de route**, en particulier le démarrage par le « cœur de score » (run 00 UTC, 4,7 Go par saison) et l'ordre des sous-projets ajusté ?
2. ~~GitHub Actions~~ — **à trancher en tête de SP1** : lieu d'exécution de la collecte quotidienne (décision 8 ; option hybride C recommandée).
3. ~~Hébergement de l'archive~~ — **tranché** : `D:\Codage\PowAtlas\data` sur la machine du pilote ; publication publique plus tard. Reste à prévoir : une sauvegarde de ce disque.
4. ~~Comptes gratuits~~ — **tranché** : tous autorisés, créés par le pilote au besoin (décision 4).
5. **Priorité 2** (AROME 0,01°, niveaux de pression AROME, ICON-CH1, IFS ENS ; 16,6 Go par saison au run 00 UTC avec la priorité 1) : dès novembre, ou après un mois de fonctionnement du cœur de score ? Repousser l'IFS ENS retarde la référence probabiliste, sauf rattrapage depuis AWS.
6. ~~Rattrapage de l'historique~~ — **tranché** : oui, en SP1 (décision 6). Les rôles des saisons proposés plus haut restent à confirmer au cadrage de SP2.
7. ~~Réglages GitHub restants~~ — **faits par le pilote** le 2026-10-22 (suppression automatique des branches fusionnées et des deux anciennes branches vérifiée ; la protection de `main` n'est pas lisible depuis la session).
8. **Méthode** : validez-vous le dépassement du plafond de 25 sources par axe constaté en R0 ? (Exa fonctionne de nouveau depuis le 2026-10-21.)
9. ~~Contacts extérieurs~~ — **tranché** : non ; recherche documentaire à la place (décision 7).
