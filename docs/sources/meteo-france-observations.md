---
type: source
id: meteo-france-observations
nom: Observations Météo-France (base climatologique quotidienne et horaire, archive SYNOP)
producteur: Météo-France
licence: Licence Ouverte 2.0 (Etalab), source à indiquer « Météo-France »
acces: HTTPS public sans compte, fichiers CSV compressés par département et par période sur meteo.data.gouv.fr (stockage meteofrance.s3.sbg.io.cloud.ovh.net) ; API du portail Météo-France (portail-api.meteofrance.fr) = compte gratuit requis
quotas: aucun quota documenté pour les fichiers ; API du portail : quotas non lus (compte requis, HTTP 401 sans jeton constaté)
delai: fichiers de l'année en cours mis à jour chaque jour (horaire 08:53 UTC, quotidien 08:50 à 09:00 UTC le 2026-10-21) ; dernière date quotidienne disponible J-2 (2026-10-19 le 2026-10-21)
resolution: ponctuelle ; quotidienne (HNEIGEF, NEIGETOT06, NEIGETOTX), horaire (NEIGETOT, HNEIGEF à 6 h), SYNOP à 3 h (ht_neige)
conservation: quotidien et horaire depuis l'ouverture des stations (séries de 1950 à 2024 en fichiers dédiés, 2025-2026 mise à jour quotidienne) ; archive SYNOP 1996 à 2026
statut: retenue
verifie_le: 2026-10-21
---

# Observations Météo-France (base climatologique quotidienne et horaire, archive SYNOP)

Chaque affirmation porte sa source et sa date de consultation (2026-10-21 pour toutes), et une marque : **[vérifié]** (constaté par nous), **[producteur]** (documentation officielle), **[tiers]** ou **[hypothèse]**. Observé uniquement.

## Contenu

- Description : trois jeux ouverts de Météo-France. (1) « Données climatologiques de base - quotidiennes » : toutes les stations « depuis leur ouverture, pour tous les paramètres disponibles », données « ayant subi un contrôle climatologique » [producteur] (https://www.data.gouv.fr/api/1/datasets/6569b51ae64326786e4e8e1a/). (2) « Données climatologiques de base - horaires » [producteur] (https://www.data.gouv.fr/api/1/datasets/6569b4473bedf2e7abad3b72/). (3) « Archive Synop OMM » : messages internationaux SYNOP, fréquence de 3 h [producteur] (https://www.data.gouv.fr/api/1/datasets/686f8595b351c06a3a790867/ et page Confluence « Observations in situ »).
- Variables de neige du fichier quotidien (`autres-parametres`), définitions du producteur [producteur] (https://meteofrance.s3.sbg.io.cloud.ovh.net/data/synchro_ftp/BASE/QUOT/Q_descriptif_champs_autres-parametres.csv) :
  - `HNEIGEF` : « hauteur de neige fraîche tombée en 24 heures (de 06h FU le jour J à 06h FU le jour J+1) qui reste au sol à 06h FU. La valeur relevée à J+1 est affectée au jour J (en cm) » ;
  - `NEIGETOT06` : épaisseur totale de neige au sol à 06 h (cm) ; `NEIGETOTX` : épaisseur maximale quotidienne entre 01 h et 24 h FU (cm) ; `NEIG` : occurrence de neige ; `SOLNEIGE` : occurrence de sol couvert de neige.
  - Codes qualité : 9 filtrée (contrôles de premier niveau), 1 validée, 0 protégée (validée définitivement par le climatologue) [producteur].
- Variables de neige du fichier horaire [producteur] (https://meteofrance.s3.sbg.io.cloud.ovh.net/data/synchro_ftp/BASE/HOR/H_descriptif_champs.csv) : `HNEIGEF` (neige fraîche tombée en 6 h, aux heures synoptiques principales, cm), `HNEIGEFI3` (3 h) et `HNEIGEFI1` (1 h) facultatifs, `NEIGETOT` (hauteur totale, cm), `TSNEIGE`, `TUBENEIGE`, `ESNEIGE`, `CHARGENEIGE` (charge de neige, kg/m2). Dans le fichier de Savoie 2025-2026, `HNEIGEF` n'est renseigné qu'à 06 et 12 UTC (4 577 et 1 857 valeurs) et `CHARGENEIGE` est vide [vérifié].
- Variables de neige du fichier SYNOP : `ht_neige` (hauteur totale), `ssfrai`, `perssfrai`, `etat_sol`, `rr1` à `rr24` [vérifié sur l'en-tête de synop_2025.csv.gz].
- Couverture de l'emprise (ouest 5.0, sud 43.5, est 7.9, nord 46.5), fichiers 2025-01-01 à 2026-10-19 des départements 04, 05, 06, 38, 73, 74 [vérifié] :
  - `HNEIGEF` renseigné pour 102 stations de l'emprise (34 stations en Savoie et 28 en Haute-Savoie avant filtre sur l'emprise) ; médiane de 81 stations par jour (maximum 90) du 2026-01-01 au 2026-03-31.
  - `NEIGETOT06` renseigné pour 174 stations ; médiane de 155 stations par jour (maximum 161) sur la même période. Beaucoup sont des stations de vallée (hauteurs nulles) et les 20 Nivôse (voir [`nivose`](nivose.md)).
  - La part des stations de `HNEIGEF` qui est le réseau nivo-météo n'est pas distinguée ici : les noms de stations sont ceux des stations de ski (par exemple Flaine, Bessans, Courchevel), identiques à [`reseau-nivo-meteo`](reseau-nivo-meteo.md) [vérifié par noms] ; test de rapprochement (observations `ssfrai` de décembre à mars 2025 du jeu nivo-météo, appariées par identifiant WIGOS à `HNEIGEF` du jour précédent dans les départements 04, 05, 06, 38, 73, 74) : 5 323 paires, dont 5 182 (97,3 %) à moins de 1 cm d'écart, écart médian nul ; ce sont donc **les mêmes mesures publiées deux fois** (les 3 821 observations non appariées viennent surtout de départements non chargés, Pyrénées et Corse) [vérifié]. Ne jamais compter ces stations deux fois dans le tableau des scores.
  - Qualité des valeurs `HNEIGEF` de l'emprise : code 1 pour 16 426 valeurs, code 9 pour 11 563 [vérifié]. Dans l'échantillon de 10 565 paires du test de dérivation (nov. 2025 à avr. 2026), 3 402 ont `QHNEIGEF` = 9 (filtrée, non validée) [vérifié]. Les scores officiels doivent se calculer sur les valeurs validées (codes 1 et 0) ; archiver le code qualité et la date de collecte avec chaque valeur ; publier un score provisoire séparé.
  - Archive SYNOP 2025 : 13 stations de l'emprise, toutes de plaine ou de vallée (Lyon-Saint-Exupéry, Grenoble-Saint-Geoirs, Chambéry-Aix, Bourg-Saint-Maurice, Embrun, Nice...), `ht_neige` renseigné ; `ssfrai` presque absent (seule Lyon-Saint-Exupéry, en limite ouest) [vérifié]. Peu utile pour la neige de montagne.
- Profondeur d'archive : Savoie (73), première valeur `HNEIGEF` quotidienne en 1950 pour 6 stations ; 102 stations de Savoie ont au moins une valeur sur 1950-2024 ; première `NEIGETOT06` de Bellecôte le 1982-01-30 [vérifié sur Q_73_previous-1950-2024].
- Délai : le fichier quotidien est mis à jour une fois par jour et la dernière date de mesure disponible était J-2 le 2026-10-21 (2026-10-19) [vérifié] ; le fichier horaire va jusqu'à la veille au matin (05 UTC pour Savoie à 15:50 UTC) [vérifié]. Pour la vérité terrain, compter 2 jours de délai [hypothèse prudente].
- Formats : CSV compressé gzip, séparateur point-virgule ; en-tête de 206 colonnes pour l'horaire [vérifié].
- Biais connus : stations de ski et de vallée (voir [`reseau-nivo-meteo`](reseau-nivo-meteo.md)), `HNEIGEF` est une mesure manuelle sur les postes de montagne et de ski (noms de postes comme `PRALOGNAN_NEIGE`) [hypothèse, protocole non lu] ; valeur de 99 cm de `HNEIGEF` maximale en Savoie, à contrôler comme possible valeur limite ou aberrante [hypothèse].
- Documentation officielle : voir Sources.
- Licence : jeux annoncés en « lov2 » (Licence Ouverte 2.0) dans l'API data.gouv.fr [vérifié] ; la version 2.0 vient de ce champ, la page Confluence écrivant seulement « Licence Ouverte d'Etalab » ; data.gouv.fr a été injoignable par intermittence depuis la session (reprises) ; « Sans redevance sous Licence Ouverte d'Etalab. La source à indiquer est "Météo-France". » [producteur] (https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/pages/888143886/Observations+in+situ, consultée le 2026-10-21).

## Test d'accès

- Date : 2026-10-21, entre 15:30 et 16:30 UTC, sans compte, sans clé.
- Commande exacte :
  - `curl -sS -m 30 https://www.data.gouv.fr/api/1/datasets/6569b51ae64326786e4e8e1a/ -o d.json` (catalogue du jeu quotidien : 628 ressources) et idem pour `6569b4473bedf2e7abad3b72` (1 463 ressources) et `686f8595b351c06a3a790867` (SYNOP).
  - `curl -sS -m 60 -o Qa_73.gz https://meteofrance.s3.sbg.io.cloud.ovh.net/data/synchro_ftp/BASE/QUOT/Q_73_latest-2025-2026_autres-parametres.csv.gz`, idem départements 04, 05, 06, 38, 74 ; `-I` sur `H_73_latest-2025-2026.csv.gz` ; `curl -sS -m 90 -o synop_2025.gz https://meteofrance.s3.sbg.io.cloud.ovh.net/data/OBS/SYNOP/synop_2025.csv.gz`.
  - `curl -sS https://public-api.meteofrance.fr/public/DPObs/v1/liste-stations` sans identifiant.
- Taille téléchargée : six fichiers quotidiens (environ 1,9 Mo), fichier SYNOP 2025 (15 902 285 octets), fichiers de Savoie quotidiens 1950-2024 et horaire 2025-2026 (voir [`nivose`](nivose.md)) ; au plus 18,6 Mo pour un même test (plafond de 50 Mo respecté).
- Résultat observé :
  - HTTP 200 pour les fichiers ; `Content-Length` 18 578 666 et `Last-Modified: Wed, 21 Oct 2026 08:53:10 GMT` pour l'horaire de Savoie ; 403 263 octets et 09:00:34 GMT pour le quotidien de Savoie.
  - L'API du portail sans identifiant : HTTP 401 `Missing Credentials` ; `compte gratuit requis` pour l'API.
  - Plusieurs « Connection reset by peer » du proxy sur `data.gouv.fr`, résolus par reprise.

## Limites

- Délai de J-2 pour la base quotidienne : pas de vérité terrain temps réel par ce canal sans l'API du portail (compte gratuit requis, non créé).
- `HNEIGEF` est la neige fraîche **restante au sol à 06 h** : elle sous-estime les chutes avec fonte ou tassement ; fenêtre **nominale** fixe de 06 à 06 UTC (échéances +6 à +30 h d'un run 00 UTC) ; le relevé réel des postes de montagne a lieu surtout vers 07-08 UTC (4 807 des 7 048 observations nivo-météo de décembre à mars 2025 ; 379 à 06 UTC ; environ 1 000 entre 10 et 14 UTC), donc la fenêtre réellement mesurée est décalée d'une à deux heures et varie selon la station.
- Les valeurs `HNEIGEF` peuvent être vides pour les stations non nivo ; compter les jours avec valeur et non les jours avec zéro.
- Fichiers départementaux nombreux (628 et 1 463 ressources) : télécharger par département et période, pas de filtre par emprise côté serveur.
- Archive SYNOP : stations essentiellement de plaine ; non utile comme vérité terrain en montagne.
- Pas d'équivalent en eau de la neige fraîche dans ces fichiers.

## Sources

- https://www.data.gouv.fr/api/1/datasets/6569b51ae64326786e4e8e1a/ — consultée le 2026-10-21
- https://www.data.gouv.fr/api/1/datasets/6569b4473bedf2e7abad3b72/ — consultée le 2026-10-21
- https://www.data.gouv.fr/api/1/datasets/686f8595b351c06a3a790867/ — consultée le 2026-10-21
- https://meteofrance.s3.sbg.io.cloud.ovh.net/data/synchro_ftp/BASE/QUOT/Q_descriptif_champs_autres-parametres.csv — consultée le 2026-10-21
- https://meteofrance.s3.sbg.io.cloud.ovh.net/data/synchro_ftp/BASE/HOR/H_descriptif_champs.csv — consultée le 2026-10-21
- https://meteofrance.s3.sbg.io.cloud.ovh.net/data/OBS/SYNOP/synop_2025.csv.gz — consultée le 2026-10-21
- https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/pages/888143886/Observations+in+situ — consultée le 2026-10-21
- https://portail-api.meteofrance.fr/web/ — consultée le 2026-10-21
- https://public-api.meteofrance.fr/public/DPObs/v1/liste-stations — consultée le 2026-10-21
