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
conservation: 4 jours calendaires, 16 runs constatés le 2026-10-21 (la documentation annonce les 12 derniers runs)
statut: retenue
verifie_le: 2026-10-21
---

# ECMWF Open Data (IFS et AIFS, 0,25°)

Chaque affirmation porte sa source et sa date de consultation (2026-10-21 pour toutes), et une marque : **[vérifié]** (constaté par nous), **[producteur]** (documentation officielle), **[tiers]** ou **[hypothèse]**.

## Contenu

- Description : prévisions numériques globales publiées par l'ECMWF : IFS (modèle physique, déterministe HRES `oper`/`scda`, ensemble ENS `enfo`) et AIFS (modèle d'apprentissage automatique, `aifs-single` déterministe, `aifs-ens` ensemble). Quatre cycles par jour (00, 06, 12, 18 UTC). [producteur] (page open-data ECMWF) ; arborescence des 4 cycles et des 4 familles `ifs`, `aifs-single`, `aifs-ens` [vérifié] sur `/forecasts/20261021/`.
- Runs et échéances (0,25°) :
  - IFS HRES `oper` : cycles 00 et 12 UTC, 85 échéances, 0 à 144 h par 3 h puis 150 à 360 h par 6 h [vérifié] ; cycles 06 et 18 UTC, 49 échéances, 0 à 144 h par 3 h [vérifié]. Le flux `scda` n'apparaît pas dans l'arborescence 0,25° `ifs` : seuls `oper`, `enfo`, `waef`, `wave` y figurent [vérifié] ; les cycles 06 et 18 UTC sont servis par le flux `oper` (49 échéances) [vérifié].
  - IFS ENS `enfo` : fichiers `-ef` (nom constaté `20261021000000-24h-enfo-ef.grib2`), mêmes 85 échéances que HRES au cycle 00 [vérifié] ; l'index d'une échéance ne liste que le type `pf`, 50 membres [vérifié] ; fichiers `-ep` (probabilités) à 240 h et 360 h seulement [vérifié].
  - AIFS Single `oper` : 4 cycles, 61 échéances, 0 à 360 h par 6 h [vérifié].
  - AIFS ENS `enfo` : fichiers séparés `-cf` (contrôle) et `-pf` (perturbés), 61 échéances, 0 à 360 h par 6 h [vérifié].
  - Résolution 0,1° IFS ajoutée à partir du 20 octobre 2026 (répertoire `ifs/0p1/` présent) [producteur] [vérifié] ; non qualifiée ici.
- Variables utiles à la neige, présence réelle dans les fichiers `.index` du run 2026-10-21 00 UTC, échéance 24 h [vérifié] :
  - IFS HRES (191 champs) : `sf` (chute de neige), `sd` (hauteur d'eau équivalente de neige, la variable `sde` n'existe pas), `rsn` (densité de la neige), `asn` (albédo de la neige), `tp` et `tprate` (précipitations totales), `cp`, `ptype` (type de précipitation), `2t`, `2d`, `skt`, `mn2t3` et `mx2t3` (min/max 2 m sur 3 h), `tcc`, `10u`, `10v`, `10fg`, `msl`, `sp`, plus niveaux de pression (`gh`, `t`, `q`, `u`, `v`, `r`... sur 14 niveaux).
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
- Conservation sur le portail : le 2026-10-21 à 15:38 UTC, `/forecasts/` listait 4 dates (20261018 à 20261021) ; les cycles 00, 06, 12 et 18 UTC des 18, 19 et 20 octobre répondaient HTTP 200 et un fichier du 18 octobre 00 UTC était présent [vérifié]. La page ECMWF annonce « Data are retained for the most recent 12 forecast runs » [producteur] : le constat (16 runs) est plus généreux, ne pas s'y fier. L'archivage doit donc télécharger chaque run dans les 2 jours, avec marge [hypothèse].
- Tailles (index du run 2026-10-21 00 UTC, échéance 24 h) [vérifié] :
  - IFS HRES, fichier complet 99 883 680 octets (environ 100 Mo), 191 champs.
  - AIFS Single, fichier complet 55 908 327 octets (environ 56 Mo), 122 champs.
  - IFS ENS `-ef`, fichier complet 4 405 125 250 octets (environ 4,4 Go) pour une échéance.
  - AIFS ENS `-cf`, fichier complet 57 932 324 octets (environ 58 Mo).
  - Un champ global de surface IFS HRES : `sf` 160 406 o, `sd` 34 987 o, `tp` 391 431 o, `ptype` 940 917 o, `2t` 318 530 o, `rsn` 216 224 o, `tcc` 463 369 o, `10u` 737 894 o, `10v` 732 210 o (environ 0,03 à 0,9 Mo). Une lecture des 12 champs neige (`sf sd rsn asn tp ptype 2t mn2t3 mx2t3 tcc 10u 10v`) pèse environ 4,7 Mo par échéance globale, donc environ 400 Mo par run de 85 échéances (somme des `_length` de l'échéance 24 h multipliée par 85) [hypothèse d'extrapolation].
  - Emprise seule après découpage côté client : environ 169 valeurs par champ, soit moins de 1 Ko non compressé par champ et échéance (environ 0,2 Mo par run pour 12 champs sur 85 échéances) [hypothèse, calcul]. Le serveur ne découpe pas : le téléchargement transporte toujours le champ global complet.
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
- Les fichiers temporaires du test restent hors du dépôt et sont supprimés à la fin.

## Limites

- Fichiers globaux : aucun découpage côté serveur. Le gain vient de la lecture par plages d'octets de quelques champs, puis d'un découpage local sur l'emprise (outil non qualifié ici).
- IFS ENS en un fichier `-ef` de 4,4 Go par échéance : seule la lecture par plages d'octets est raisonnable (50 membres x champ x 85 échéances) ; le coût en nombre de requêtes est élevé (50 plages par champ et par échéance) [hypothèse].
- Absence de `deg0l`, `sde`, hauteur de neige : isotherme 0 °C et limite pluie-neige à dériver (champs de pression `gh`, `t`, ou `ptype`), ce qui est un traitement du projet, pas une donnée du producteur.
- AIFS ne fournit ni `sd`, ni `ptype`, ni `rsn`, ni min/max 2 m.
- Conservation courte (2 à 4 jours selon la mesure du 2026-10-21, 12 runs annoncés) : pas d'historique ; tout run non archivé est perdu.
- Résolution de 28 km sur des Alpes très relief : biais de précipitation et d'altitude attendus, à corriger par post-traitement ; la sortie n'est pas un verdict de sécurité avalanche (référence : BRA Météo-France).
- Limite de connexions par client non documentée pour l'accès anonyme ; limite globale annoncée 500 (Confluence) ou 500 à 2000 (page open-data), sources discordantes [producteur].
- Les sommes de volumes pour un run entier sont des extrapolations à partir de l'échéance 24 h.
- Copies cloud (AWS, Azure, GCP) annoncées par le producteur comme alternative : non testées ici [producteur].

## Sources

- https://data.ecmwf.int/forecasts/ — consultée le 2026-10-21
- https://data.ecmwf.int/forecasts/20261021/00z/ifs/0p25/oper/ — consultée le 2026-10-21
- https://data.ecmwf.int/forecasts/20261021/00z/aifs-single/0p25/oper/ — consultée le 2026-10-21
- https://data.ecmwf.int/forecasts/20261021/00z/aifs-ens/0p25/enfo/ — consultée le 2026-10-21
- https://data.ecmwf.int/forecasts/20261021/00z/ifs/0p25/enfo/ — consultée le 2026-10-21
- https://www.ecmwf.int/en/forecasts/datasets/open-data — consultée le 2026-10-21
- https://apps.ecmwf.int/datasets/licences/general/ — consultée le 2026-10-21
- https://confluence.ecmwf.int/display/DAC/ECMWF+open+data%3A+real-time+forecasts+from+IFS+and+AIFS — consultée le 2026-10-21
