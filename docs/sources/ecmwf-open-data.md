---
type: source
id: ecmwf-open-data
nom: ECMWF Open Data (IFS et AIFS, 0,25°)
producteur: ECMWF (Centre européen pour les prévisions météorologiques à moyen terme)
licence: CC BY 4.0 (Creative Commons Attribution 4.0 International), attribution ECMWF obligatoire
acces: HTTPS public sans compte, https://data.ecmwf.int/forecasts/ (fichiers GRIB2 globaux + index .index, lecture partielle par plages d'octets)
quotas: limite documentée de 500 à 2000 connexions simultanées pour tout le portail ; aucune limite par IP constatée sur le test ; limite par utilisateur non documentée pour l'accès anonyme au 2026-10-21
delai: environ 6 h 30 à 7 h 40 après l'heure du run (Last-Modified constaté), voir Contenu
resolution: 0,25° (environ 28 km), global, 1440 x 721 points ; pas de temps 3 h puis 6 h (IFS) ou 6 h (AIFS)
conservation: portail : 12 runs annoncés, 16 constatés le 2026-10-21 (4 jours calendaires) ; copie AWS : historique constaté depuis 2023-01-18 (0,4° beta), IFS 0,25° depuis le 2024-02-01 (constat du 2026-10-22), conservation non garantie [hypothèse]
statut: retenue
verifie_le: 2026-10-22
---

# ECMWF Open Data (IFS et AIFS, 0,25°)

Chaque affirmation porte sa source et sa date de consultation (2026-10-21, sauf les constats marqués du 2026-10-22), et une marque : **[vérifié]** (constaté par nous), **[producteur]** (documentation officielle), **[tiers]** ou **[hypothèse]**.

## Contenu

- Description : prévisions numériques globales publiées par l'ECMWF : IFS (modèle physique, déterministe HRES flux `oper`, ensemble ENS flux `enfo` ; le flux `scda` n'existe pas dans l'arborescence 0,25° constatée, voir ci-dessous) et AIFS (modèle d'apprentissage automatique, `aifs-single` déterministe, `aifs-ens` ensemble). Quatre cycles par jour (00, 06, 12, 18 UTC). [producteur] (page open-data ECMWF) ; arborescence des 4 cycles et des 4 familles `ifs`, `aifs-single`, `aifs-ens` [vérifié] sur `/forecasts/20261021/`.
- Runs et échéances (0,25°) :
  - IFS HRES `oper` : cycles 00 et 12 UTC, 85 échéances, 0 à 144 h par 3 h puis 150 à 360 h par 6 h [vérifié] ; cycles 06 et 18 UTC, 49 échéances, 0 à 144 h par 3 h [vérifié]. Le flux `scda` n'apparaît pas dans l'arborescence 0,25° `ifs` : seuls `oper`, `enfo`, `waef`, `wave` y figurent [vérifié] ; les cycles 06 et 18 UTC sont servis par le flux `oper` (49 échéances) [vérifié].
  - IFS ENS `enfo` : fichiers `-ef` (nom constaté `20261021000000-24h-enfo-ef.grib2`), mêmes 85 échéances que HRES au cycle 00 [vérifié] ; l'index d'une échéance ne liste que le type `pf`, 50 membres [vérifié] ; fichiers `-ep` (probabilités) à 240 h et 360 h seulement [vérifié].
  - AIFS Single `oper` : 4 cycles, 61 échéances, 0 à 360 h par 6 h [vérifié].
  - AIFS ENS `enfo` : fichiers séparés `-cf` (contrôle) et `-pf` (perturbés), 61 échéances, 0 à 360 h par 6 h [vérifié].
  - Résolution 0,1° IFS : « from 20 October 2026 », IFS aussi à 0,1° ; « the AIFS streams remain 0.25° only » ; le 0,1° est publié environ 2 h après le 0,25° [producteur] (page open-data ECMWF, consultée le 2026-10-21). Répertoires `ifs/0p1/{oper,enfo,waef,wave}` présents sur la copie AWS le 2026-10-21 ; fichiers séparés `-fc-pl` (niveaux de pression, 370 638 187 o pour l'échéance 0 h) et `-fc-sfc` (surface, 76 479 791 o) pour `oper` ; ENS 0,1° : `ef-pl` 15 445 983 271 o et `ef-sfc` 3 449 446 215 o pour l'échéance 0 h [vérifié, listing S3 anonyme]. Verdict : 4 à 25 fois plus gros que le 0,25° pour un gain sans intérêt avant la réduction d'échelle ; non retenu pour SP1 (le 0,25° suffit, la grille 0,1° est à réexaminer en SP3) [hypothèse].
  - ENS, précision : la page open-data ne donne pas le nombre de membres ; l'index d'une échéance du fichier `-ef` du portail liste 50 occurrences de `pf` par champ (50 membres perturbés) et le contrôle `cf` n'y figure pas [vérifié] ; pour 00 et 12 UTC les échéances sont 0 à 144 h par 3 h puis 150 à 360 h par 6 h, pour 06 et 18 UTC 0 à 144 h par 3 h ; AIFS ENS : 0 à 360 h par 6 h aux quatre cycles [producteur].
- Variables utiles à la neige, présence réelle dans les fichiers `.index` du run 2026-10-21 00 UTC, échéance 24 h [vérifié] :
  - IFS HRES (191 champs) : `sf` (chute de neige), `sd` (hauteur d'eau équivalente de neige, la variable `sde` n'existe pas), `rsn` (densité de la neige), `asn` (albédo de la neige), `tp` et `tprate` (précipitations totales), `cp`, `ptype` (type de précipitation), `2t`, `2d`, `skt`, `mn2t3` et `mx2t3` (min/max 2 m sur 3 h jusqu'à 144 h ; **à partir de 150 h : `mn2t6` et `mx2t6`**, sur 6 h [vérifié sur les index des échéances 144 h et 150 h du run 2026-10-21 00 UTC]), `tcc`, `10u`, `10v`, `10fg`, `msl`, `sp`, plus niveaux de pression (`gh`, `t`, `q`, `u`, `v`, `r`... sur 14 niveaux).
  - Absentes : `deg0l` (isotherme 0 °C) et `sde`, aucun champ de profondeur de neige en mètres. L'isotherme 0 °C devra être dérivée de `gh` et `t` aux niveaux de pression ou de `2t` [vérifié pour l'absence ; dérivation = hypothèse].
  - IFS ENS : mêmes variables de surface que HRES (`sf`, `sd`, `rsn`, `asn`, `tp`, `ptype`, `2t`, `mn2t3`, `mx2t3`, `tcc`, `10u`, `10v`), 50 occurrences chacune dans l'index d'une échéance [vérifié].
  - AIFS Single (122 champs) : `sf`, `tp`, `cp`, `2t`, `2d`, `skt`, `tcc`, `10u`, `10v`, `msl`, `sp`, `fscov` (nom du paramètre tel que listé), niveaux de pression ; absentes : `sd`, `rsn`, `ptype`, `mn2t3`/`mx2t3` [vérifié]. `fscov` : signification non documentée dans cet index, à ne pas interpréter sans la documentation du producteur.
  - AIFS ENS : même liste de surface que AIFS Single (108 champs dans le fichier `-cf`) [vérifié].
- Couverture de l'emprise des Alpes françaises (ouest 5.0, sud 43.5, est 7.9, nord 46.5) : les fichiers sont globaux (1440 x 721 points, pas de 0,25° vérifié dans la section 3 du GRIB2 lu). L'emprise couvre environ 12 x 13 points, soit 0,02 % de la grille [hypothèse, calcul : 2,9° / 0,25° par 3° / 0,25°]. À 28 km, le relief alpin est très lissé : les valeurs sont celles d'un modèle global, pas d'un modèle de montagne [hypothèse].
- Fréquence : 4 runs par jour pour IFS et AIFS [producteur] [vérifié].
- Formats : GRIB2 (`Content-Type: application/grib`) et fichier d'index JSON-lines `.index` (un objet par champ avec `param`, `levtype`, `step`, `type`, `_offset`, `_length`) [vérifié].
- Délai de mise à disposition (Last-Modified, UTC, arrondi à la minute, valeur de la date de dépôt sur le portail, pas l'heure d'initialisation du calcul) [vérifié] :
  - IFS HRES 00 UTC : 07:34 (soit environ 7 h 34 après l'heure du run), 12 UTC : 19:34, soit environ 7 h 34 ; 06 UTC (échéances 0 à 144 h) : 12:27, soit environ 6 h 27 après.
  - IFS ENS 00 UTC : 07:40.
  - AIFS Single 00 UTC : échéance 0 h à 05:45, échéance 24 h à 05:52, échéance 360 h à 07:34 (dépôt étalé sur environ 1 h 50).
  - AIFS ENS 00 UTC : échéance 24 h `-cf` à 06:44, 360 h `-pf` à 07:40.
  - La documentation ne donne pas de délai chiffré pour l'IFS 0,25° (« publié à la fin du calendrier de diffusion ») ni pour l'AIFS [producteur].
- Copies cloud : la page open-data cite AWS (`registry.opendata.aws/ecmwf-forecasts/`), Azure (`ai4edataeuwest.blob.core.windows.net/ecmwf/`) et Google Cloud (BigQuery public data) ; elle ne dit ni si un compte est nécessaire, ni si la licence diffère [producteur]. Test AWS : le bucket `ecmwf-forecasts` (région eu-central-1) se liste et se lit en HTTPS anonyme, sans compte ni clé : `https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com/?delimiter=/` rend la liste des dates depuis `20230118/` jusqu'à `20261021/` (295 dates en 2026, journalières) ; `20261021/00z/ifs/0p25/oper/` liste `20261021000000-0h-oper-fc.grib2` et `.index`, `20261010/00z/ifs/0p25/oper/` 173 clés et `20250101/00z/ifs/0p25/oper/` 172 clés, `20260601/00z/aifs-single/0p25/oper/` 125 clés (les arborescences de 2024 sont différentes, non explorées) [vérifié]. La copie AWS conserve donc des années d'historique, contre 12 runs sur le portail : **les runs ECMWF d'un jour manqué par SP1 restent récupérables sur AWS** ; la page ne garantit pas cette durée [hypothèse : politique de conservation AWS non lue]. Licence des copies : aucune mention séparée, la licence CC BY 4.0 du produit s'applique [hypothèse, non confirmée par la page de copie] ; Azure et GCP non testés.
- **Historique de la copie AWS (constat du 2026-10-22)** [vérifié, listings et index anonymes du run 00 UTC, échéance 24 h] :
  - du 2023-01-18 au 2024-01-31 : seulement `AAAAMMJJ/00z/0p4-beta/` (grille 0,4° « beta ») ;
  - IFS 0,25° à partir du 2024-02-01, sous `AAAAMMJJ/00z/0p25/{oper,enfo,waef,wave}/` jusqu'au 2024-02-28, puis sous `AAAAMMJJ/00z/ifs/0p25/` dès le 2024-02-29 ;
  - champs de surface de l'IFS 0,25° : le 2024-02-01, 11 seulement (`10u`, `10v`, `2t`, `lsm`, `msl`, `ro`, `skt`, `sp`, `st`, `tcwv`, `tp`) ; le 2024-06-01 et le 2024-11-01, 28 et 29 (ajout de `2d`, `asn`, rayonnements, sols...) ; le 2025-06-01 et le 2025-11-15, 32 (ajout de `ptype`, `mn2t3`, `mx2t3`, `10fg`, `tprate`) ; le 2025-12-15 et le 2026-01-01, 35 avec **`sf`, `sd` et `tcc`**. **La chute de neige `sf` n'existe donc qu'à partir d'une date entre le 2025-11-15 et le 2025-12-15** ; précisé le 2026-10-22 (index de l'échéance 24 h) : absente le 2025-11-20, présente le 2025-11-22 et ensuite (2025-11-21 non lisible : `SlowDown` répétés), avec `sd` en même temps ;
  - AIFS expérimental sous `AAAAMMJJ/00z/aifs/0p25/oper/` au moins depuis le 2024-03-01 (champs de surface : `10u`, `10v`, `2d`, `2t`, `cp`, `msl`, `skt`, `sp`, `tcw`, `tp` ; pas de `sf`) ; AIFS Single sous `aifs-single/0p25/experimental/oper/` à partir du 2025-02-10 (et jusqu'au 2025-02-25), puis sous `aifs-single/0p25/oper/` (flux opérationnel) **à partir du 2025-02-26** [vérifié le 2026-10-22, listings du run 00 UTC du 20 au 1er mars] : d'où l'index absent le 2025-02-20 sous `0p25/oper/` ; heure de dépôt historique plus tardive qu'aujourd'hui (`LastModified` 08:34 pour l'IFS du 2025-01-01) ;
  - débit : le bucket a répondu `SlowDown` (« Please reduce your request rate ») à une partie des requêtes, même espacées de 15 s, depuis le proxy de la session cloud : un rattrapage doit être lent et reprenable. **Depuis le PC du pilote (connexion domestique, 2026-10-23)** : `powatlas backfill-probe --source ifs-0p25 --day 2025-01-10` a lu 60 plages d'octets (4 échéances) en 12,2 s, soit 4,90 requêtes par seconde, **sans aucun `SlowDown`**, pour 41,9 Mo [vérifié]. Le débit est borné par l'intervalle minimal de 0,2 s entre requêtes de `powatlas` (5 requêtes par seconde au plus), pas par le bucket : les `SlowDown` venaient donc probablement du proxy de la session cloud [hypothèse].
- **Unités publiées (constat du 2026-10-22)** : l'IFS donne `tp` en m et `sf` en « m of water equivalent », l'AIFS donne `tp` et `sf` en kg m-2 ; l'archive garde les unités du producteur (attribut `GRIB_units`), toute comparaison les convertit explicitement.
- Conservation sur le portail : le 2026-10-21 à 15:38 UTC, `/forecasts/` listait 4 dates (20261018 à 20261021) ; les cycles 00, 06, 12 et 18 UTC des 18, 19 et 20 octobre répondaient HTTP 200 et un fichier du 18 octobre 00 UTC était présent [vérifié]. La page ECMWF annonce « Data are retained for the most recent 12 forecast runs » [producteur] : le constat (16 runs) est plus généreux, ne pas s'y fier. L'archivage doit donc télécharger chaque run dans les 2 jours, avec marge [hypothèse].
- Tailles (index du run 2026-10-21 00 UTC, échéance 24 h) [vérifié] :
  - IFS HRES, fichier complet 99 883 680 octets (environ 100 Mo), 191 champs.
  - AIFS Single, fichier complet 55 908 327 octets (environ 56 Mo), 122 champs.
  - IFS ENS `-ef`, fichier complet 4 405 125 250 octets (environ 4,4 Go) pour une échéance.
  - AIFS ENS `-cf`, fichier complet 57 932 324 octets (environ 58 Mo).
  - Un champ global de surface IFS HRES : `sf` 160 406 o, `sd` 34 987 o, `tp` 391 431 o, `ptype` 940 917 o, `2t` 318 530 o, `rsn` 216 224 o, `tcc` 463 369 o, `10u` 737 894 o, `10v` 732 210 o (environ 0,03 à 0,9 Mo). Une lecture des 12 champs neige (`sf sd rsn asn tp ptype 2t mn2t3 mx2t3 tcc 10u 10v`) pèse environ 4,7 Mo par échéance globale, donc environ 400 Mo par run de 85 échéances (somme des `_length` de l'échéance 24 h multipliée par 85) [hypothèse d'extrapolation].
  - Emprise seule après découpage côté client : 156 valeurs par champ (13 x 12 points, mesuré sur la grille GFS identique), soit moins de 1 Ko non compressé par champ et échéance (environ 0,2 Mo par run pour 12 champs sur 85 échéances) [hypothèse, calcul]. Le serveur ne découpe pas : le téléchargement transporte toujours le champ global complet.
- Documentation officielle : voir Sources.
- Licence : « This data product is published under a Creative Commons Attribution 4.0 International (CC BY 4.0). » [producteur] (https://apps.ecmwf.int/datasets/licences/general/, consultée le 2026-10-21) ; la page open-data ECMWF écrit « Creative Commons CC-BY-4.0 licence » et renvoie aux Terms of Use ECMWF [producteur]. Attribution exigée : « © [année] European Centre for Medium-Range Weather Forecasts (ECMWF) », source www.ecmwf.int, mention de la licence, avertissement d'absence de garantie, et indication des modifications apportées aux données. Pour un service construit à partir des données : « This service is based on data and products of the European Centre for Medium-Range Weather Forecasts (ECMWF) » [producteur]. Texte exact des Terms of Use non relu intégralement ici : à relire avant publication d'un produit dérivé [hypothèse].

## Test d'accès

- Date : 2026-10-21, entre 15:30 et 15:40 UTC, sans compte, sans clé.
- Commande exacte :
  - `curl -sS https://data.ecmwf.int/forecasts/` (liste des dates), puis `curl -sS https://data.ecmwf.int/forecasts/20261021/00z/ifs/0p25/oper/` (liste des fichiers).
  - `curl -sS -o ifs24.index https://data.ecmwf.int/forecasts/20261021/00z/ifs/0p25/oper/20261021000000-24h-oper-fc.index`, et les index équivalents pour `aifs-single/0p25/oper`, `ifs/0p25/enfo` (`-ef`) et `aifs-ens/0p25/enfo` (`-cf`).
  - `curl -sS -I` sur les fichiers `.grib2` pour `Content-Length`, `Last-Modified`, `Accept-Ranges`.
  - Lecture partielle d'un champ : `curl -sS -r 28922873-29083278 -o sf.grib2 https://data.ecmwf.int/forecasts/20261021/00z/ifs/0p25/oper/20261021000000-24h-oper-fc.grib2` (plage = `_offset` et `_offset + _length - 1` du champ `sf` lus dans l'index).
- Taille téléchargée : environ 2,2 Mo d'index (41 540 + 29 538 + 2 078 568 + 25 777 octets), 160 406 octets pour le champ `sf`, plus deux pages HTML de liste de 0,4 à 0,5 Mo chacune ; au total environ 6 Mo, sous le plafond de 50 Mo.
- Résultat observé :
  - HTTP 200 sur toutes les listes et index ; `Accept-Ranges: bytes` ; `Content-Type: application/grib`.
  - La première tentative de `GET /forecasts/` a reçu « Empty reply from server » (curl 52) à travers le proxy du sandbox ; la requête identique répétée juste après a réussi (HTTP 200, 430 257 octets). Un `GET /forecasts` sans barre finale renvoie 404. Des échecs ponctuels sont donc possibles : prévoir des reprises.
  - La lecture partielle a rendu HTTP (200 et non 206 : code lu à travers le proxy du sandbox) avec 160 406 octets exactement égaux à `_length`, début `GRIB`, fin `7777`, édition 2, grille de 1 038 240 points, Ni 1440, Nj 721 [vérifié].
  - Le répertoire racine liste 4 dates et un dossier `wis2/` ; le portail propose aussi des listes JSON ou CSV via l'en-tête `Accept` et un accès S3 et WebDAV pour les comptes connectés (page d'aide du portail, non utilisés ici) [producteur].
- Complément du 2026-10-22 (copie AWS, sans compte) : `curl -sS "https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com/?list-type=2&delimiter=/&prefix=<AAAAMMJJ>/00z/"` pour une vingtaine de dates de 2024 à 2026, puis téléchargement des index `<AAAAMMJJ>000000-24h-oper-fc.index` (environ 18 à 45 Ko chacun, une douzaine d'index, moins de 1 Mo au total) et comptage des champs `levtype = sfc` avec `python3 -I`. Résultat : voir « Historique de la copie AWS » dans Contenu ; plusieurs réponses HTTP 503 `SlowDown`, une réponse `NoSuchKey` pour `20250220/00z/aifs-single/0p25/oper/20250220000000-24h-oper-fc.index`.
- Les fichiers temporaires du test restent hors du dépôt et sont supprimés à la fin.

## Limites

- Fichiers globaux : aucun découpage côté serveur. Le gain vient de la lecture par plages d'octets de quelques champs, puis d'un découpage local sur l'emprise (outil non qualifié ici).
- IFS ENS en un fichier `-ef` de 4,4 Go par échéance : seule la lecture par plages d'octets est raisonnable (50 membres x champ x 85 échéances) ; le coût en nombre de requêtes est élevé (50 plages par champ et par échéance) [hypothèse].
- Absence de `deg0l`, `sde`, hauteur de neige : isotherme 0 °C et limite pluie-neige à dériver (champs de pression `gh`, `t`, ou `ptype`), ce qui est un traitement du projet, pas une donnée du producteur.
- AIFS ne fournit ni `sd`, ni `ptype`, ni `rsn`, ni min/max 2 m.
- Conservation du portail courte (12 runs annoncés, 16 constatés le 2026-10-21, soit 4 jours calendaires) : pas d'historique sur le portail. La copie AWS affiche un historique constaté depuis 2023-01-18 (liste des dates), conservation non garantie par le producteur [hypothèse] : un run manqué est probablement récupérable sur AWS, pas sur le portail.
- Copie AWS : avant décembre 2025, l'IFS 0,25° n'a pas de chute de neige `sf` (constat du 2026-10-22) ; la neige des saisons rattrapées devra être dérivée de `tp` et des températures, et marquée comme dérivée.
- Résolution de 28 km sur des Alpes très relief : biais de précipitation et d'altitude attendus, à corriger par post-traitement ; la sortie n'est pas un verdict de sécurité avalanche (référence : BRA Météo-France).
- Limite de connexions par client non documentée pour l'accès anonyme ; limite globale annoncée 500 (Confluence) ou 500 à 2000 (page open-data), sources discordantes [producteur].
- Les sommes de volumes pour un run entier sont des extrapolations à partir de l'échéance 24 h.
- Copies Azure et GCP : non testées ; AWS testée (voir Contenu), sans garantie de conservation écrite par le producteur.

## Sources

- https://data.ecmwf.int/forecasts/ — consultée le 2026-10-21
- https://data.ecmwf.int/forecasts/20261021/00z/ifs/0p25/oper/ — consultée le 2026-10-21
- https://data.ecmwf.int/forecasts/20261021/00z/aifs-single/0p25/oper/ — consultée le 2026-10-21
- https://data.ecmwf.int/forecasts/20261021/00z/aifs-ens/0p25/enfo/ — consultée le 2026-10-21
- https://data.ecmwf.int/forecasts/20261021/00z/ifs/0p25/enfo/ — consultée le 2026-10-21
- https://www.ecmwf.int/en/forecasts/datasets/open-data — consultée le 2026-10-21
- https://apps.ecmwf.int/datasets/licences/general/ — consultée le 2026-10-21
- https://confluence.ecmwf.int/display/DAC/ECMWF+open+data%3A+real-time+forecasts+from+IFS+and+AIFS — consultée le 2026-10-21
- https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com/ — copie AWS, liste anonyme — consultée le 2026-10-21 et le 2026-10-22 (historique 2023-2026, index de l'échéance 24 h)
