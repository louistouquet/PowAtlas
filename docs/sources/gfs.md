---
type: source
id: gfs
nom: GFS 0,25° (NOAA/NCEP), copie AWS Open Data et NOMADS
producteur: NOAA / NCEP (National Weather Service, États-Unis)
licence: « NOAA data disseminated through NODD are open to the public and can be used as desired » (registre AWS Open Data) ; attribution demandée ; ne pas suggérer l'aval de NOAA ; « If you modify NOAA data, you may not state or imply that it is original, unaltered NOAA data » ; pas de licence Creative Commons
acces: HTTPS anonyme, sans compte, bucket S3 public noaa-gfs-bdp-pds (us-east-1) avec fichiers d'index .idx ; NOMADS (nomads.ncep.noaa.gov) non testé au-delà de la liste
quotas: aucune limite documentée sur la page du bucket ; NOMADS applique des limites de débit, non lues
delai: échéance 0 du run 12 UTC déposée à 15:33 UTC (environ 3 h 33), échéance 24 h à 15:40 UTC
resolution: 0,25° (1440 x 721 points), horaire jusqu'à 120 h puis toutes les 3 h jusqu'à 384 h ; 4 runs par jour (00, 06, 12, 18 UTC)
conservation: copie AWS : historique depuis 2021 (préfixes `gfs.20210101/` ... `gfs.20261021/`) ; NOMADS : non documentée ici
statut: retenue
verifie_le: 2026-10-21
---

# GFS 0,25° (NOAA)

Chaque affirmation porte sa source et sa date de consultation (2026-10-21), et une marque : **[vérifié]**, **[producteur]**, **[tiers]** ou **[hypothèse]**.

## Contenu

- Description : modèle global américain, « 4 times a day, every 6 hours starting at midnight UTC » [producteur : registre AWS Open Data du bucket `noaa-gfs-bdp-pds`]. Fichiers `gfs.tHHz.pgrb2.0p25.fFFF` (GRIB2, environ 480 à 530 Mo par échéance) et `.idx` (index texte, 32 à 41 Ko) sous `gfs.AAAAMMJJ/HH/atmos/` [vérifié].
- Runs et échéances : 4 par jour [producteur] ; échéances horaires jusqu'à 120 h puis toutes les 3 h jusqu'à 384 h : 209 fichiers `f000` à `f384` listés pour le run 2026-10-20 00 UTC, `f120`, `f123`, `f126`... au-delà de 120 h [vérifié, listing S3].
- Variables utiles à la neige, lues dans l'index de l'échéance 24 h (743 messages) et dans les champs téléchargés [vérifié] : `CSNOW` (neige catégorielle, instantanée et moyenne 18-24 h), `CRAIN`, `CFRZR`, `CICEP`, `SNOD` (hauteur de neige, m), `WEASD` (équivalent en eau de la neige accumulée, kg m-2), `APCP` (précipitation, cumul), `PRATE`, `TMP:2 m above ground`, `DPT`, `RH`, `HGT:0C isotherm` (hauteur de l'isotherme 0 °C), `RH:0C isotherm`, vent 10 m, `GUST`, `PRMSL`, `TCDC`, `PWAT`. Pas de champ de chute de neige en cm, pas de limite pluie-neige directe.
- Couverture de l'emprise des Alpes françaises : mondial ; découpage à 13 x 12 = 156 points (maille de 28 km) [vérifié]. Les champs `sde` (`SNOD`) et `sdwe` (`WEASD`) portent des valeurs maximales de 9999 dans l'emprise : valeur de remplissage probable, cause non élucidée [vérifié pour la valeur, hypothèse pour l'interprétation].
- Lecture sélective : l'index donne l'offset de chaque message ; 9 champs de neige lus par plages d'octets représentent 4 011 374 octets pour l'échéance 24 h (`HGT:0C isotherm` 953 912 o, `TMP:2 m` 879 078 o, `PRATE` 575 876 o, `SNOD` 556 312 o, `WEASD` 543 544 o, `APCP` 356 158 o, `CRAIN` 86 310 o, `CSNOW` 33 731 et 26 453 o) [vérifié] ; soit environ 4,0 Mo par échéance, 0,8 % du fichier.
- Documentation officielle : https://registry.opendata.aws/noaa-gfs-bdp-pds/ ; https://www.emc.ncep.noaa.gov/emc/pages/numerical_forecast_systems/gfs.php (non lue).
- Licence : « NOAA data disseminated through NODD are open to the public and can be used as desired. » ; attribution demandée pour les données non modifiées ; ne pas prétendre ou suggérer l'aval de NOAA ; « If you modify NOAA data, you may not state or imply that it is original, unaltered NOAA data » (clause à reprendre dans les métadonnées de l'archive découpée) [producteur, registre AWS, consultée le 2026-10-21 ; la clause sur les données modifiées a été portée par la relecture, libellé à revérifier sur la page].

## Test d'accès

- Date : 2026-10-21, 15:50 à 16:20 UTC, sans compte.
- Commande exacte : `curl -sS "https://noaa-gfs-bdp-pds.s3.amazonaws.com/?delimiter=/&prefix=gfs.20261021/"` (préfixes `00/`, `06/`, `12/`) ; `curl -sS -o gfs_f024.idx https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.20261021/12/atmos/gfs.t12z.pgrb2.0p25.f024.idx` (41 254 o, 743 lignes) ; `curl -sS -I .../gfs.t12z.pgrb2.0p25.f024` (`Content-Length: 527027983`, `Accept-Ranges: bytes`, `Last-Modified: Wed, 21 Oct 2026 15:40:13 GMT`) ; lectures `Range: bytes=a-b` des 9 messages listés ci-dessus ; `curl --http1.1 https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/` : HTTP 200.
- Taille téléchargée : 4,05 Mo.
- Résultat observé : HTTP 200 anonyme ; champs lus et validés avec `eccodes` (`sdwe`, `sde`, `2t`, `prate`, `tp`, `csnow`, `crain`, `gh` isotherme zéro), grille 1440 x 721 [vérifié]. Le listing `gfs.2021...` commence à `gfs.20210101/` ; `gfs.20230101/00/atmos/gfs.t00z.pgrb2.0p25.f024` (534 412 062 o) existe [vérifié].

## Limites

- Maille de 28 km : relief alpin très lissé ; utile surtout comme référence mondiale et comme source de secours.
- Le fichier entier fait 0,5 Go : toute lecture passe par l'index et les plages d'octets.
- Historique disponible sur la copie AWS : l'archivage quotidien de SP1 n'est pas urgent pour GFS (backfill possible) [hypothèse : politique de conservation AWS non lue].
- Valeurs 9999 dans `SNOD` et `WEASD` à interpréter avant usage.
- La sortie n'est pas un verdict de sécurité avalanche (référence : BRA Météo-France).

## Sources

- https://noaa-gfs-bdp-pds.s3.amazonaws.com/ — bucket GFS (listing, index, fichiers) — consultée le 2026-10-21
- https://registry.opendata.aws/noaa-gfs-bdp-pds/ — registre AWS Open Data : licence, fréquence — consultée le 2026-10-21
- https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/ — NOMADS (liste) — consultée le 2026-10-21
