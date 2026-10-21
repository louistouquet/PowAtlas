---
type: source
id: icon-dwd
nom: ICON-D2 et ICON-EU (DWD, opendata.dwd.de)
producteur: Deutscher Wetterdienst (DWD)
licence: Creative Commons CC BY 4.0 ; mention de la source (DWD) obligatoire
acces: HTTPS anonyme, sans compte ni clé, https://opendata.dwd.de/weather/nwp/ (listing de répertoires, fichiers GRIB2 compressés .bz2, un fichier par champ et par échéance)
quotas: aucune limite documentée ni constatée sur le test ; politique d'usage du serveur non lue
delai: ICON-D2 : 0 h 44 (échéance 0) à 1 h 21 (échéance 48) après l'heure du run ; ICON-EU : 2 h 45 à 3 h 39 (run 12 UTC, échéance 120)
resolution: ICON-D2 0,02° (environ 2,2 km, 1215 x 746 points, 43,18 N à 58,08 N, 3,94 W à 20,34 E) ; ICON-EU 0,0625° (1377 x 657 points, 29,5 N à 70,5 N, 23,5 W à 62,5 E) ; pas horaire
conservation: environ 24 h : un seul run par créneau horaire est conservé, remplacé par celui du lendemain
statut: retenue
verifie_le: 2026-10-21
---

# ICON-D2 et ICON-EU (DWD)

Chaque affirmation porte sa source et sa date de consultation (2026-10-21), et une marque : **[vérifié]**, **[producteur]**, **[tiers]** ou **[hypothèse]**.

## Contenu

- Description : modèles de prévision régionaux du DWD ; ICON-D2 (Europe centrale, maille 2,2 km) et ICON-EU (Europe, 6,5 km), publiés sur `https://opendata.dwd.de/weather/nwp/icon-d2/grib/` et `.../icon-eu/grib/` par heure de run (`00` à `21`), puis par variable (un dossier par variable, par exemple `snow_gsp/`) [vérifié]. Existent aussi `icon-d2-eps` et `icon-eu-eps` (ensembles), non testés [vérifié pour l'existence des dossiers].
- Runs et échéances [vérifié, comptage des fichiers de `tot_prec` le 2026-10-21] :
  - ICON-D2 : 8 runs par jour (00, 03, ..., 21 UTC), tous de 0 à 48 h par pas de 1 h (49 échéances, 98 fichiers : une grille icosaédrique et une grille régulière lat-lon).
  - ICON-EU : 00, 06, 12, 18 UTC jusqu'à 120 h (93 fichiers : horaire jusqu'à 78 h puis 3 h) ; 03, 09, 15, 21 UTC jusqu'à 48 h (34 fichiers).
- Variables utiles à la neige, présentes dans les dossiers du run 12 UTC [vérifié] : `snow_gsp` (neige grande échelle, équivalent en eau, cumul, `lsfwe`), `snow_con` (neige convective, cumul, `csfwe`), `tot_prec` (précipitation totale, cumul), `rain_gsp`, `rain_con`, `grau_gsp` (graupel), `h_snow` (hauteur de neige, m, `sde`), `w_snow` (équivalent en eau du manteau, kg m-2, `sd`), `rho_snow` (densité), `freshsnw`, `snowc` (couverture), `t_snow`, `snowlmt` (hauteur de la limite des chutes de neige au-dessus du niveau de la mer, m), `hzerocl` (hauteur de l'isotherme 0 °C, m), `ww` (temps significatif), `t_2m`, `td_2m`, `relhum_2m`, `u_10m`, `v_10m`, `vmax_10m`, `pmsl`, `clct`. Lecture réelle (échéance 24 h, `eccodes`) : D2 `lsfwe`, `csfwe`, `tp`, `lsrr` (pluie grande échelle), `sde`, `sd`, `rsn`, `FRESHSNW`, `SNOWLMT`, `HZEROCL`, `2t` ; ICON-EU `lsfwe`, `csfwe`, `tp`, `sde`, `sd`, `SNOWLMT`, `HZEROCL`, `2t` [vérifié]. ICON-D2 donne donc, contrairement à AROME, la limite pluie-neige, l'isotherme 0 °C, la hauteur de neige et l'équivalent en eau.
- Couverture de l'emprise des Alpes françaises (ouest 5.0, sud 43.5, est 7.9, nord 46.5) : ICON-D2 couvre 43,18 N à 58,08 N : la limite sud est à 0,32° sous celle de l'emprise, les Alpes françaises y sont entières [vérifié, en-tête de grille] ; ICON-EU couvre tout. Découpage mesuré : 150 x 145 = 21 750 points à 0,02° (87 000 octets en float32 par champ), 2 303 points à 0,0625° [vérifié pour D2, calcul pour EU].
- Fréquence : voir Runs ; formats : GRIB2 compressé bzip2 ; les fichiers de cumul et d'isothermes de la grille régulière contiennent 4 messages, structure non élucidée (à inspecter avant d'écrire le code d'archivage) [vérifié].
- Délai (Last-Modified, run 12 UTC du 2026-10-21) [vérifié] : ICON-D2 `snow_gsp` échéance 0 à 12:44 UTC, échéance 48 (grille régulière) à 13:21 UTC ; ICON-EU `SNOW_GSP` échéance 0 à 14:45 UTC, échéance 120 à 15:38 UTC.
- Conservation : le dossier `icon-d2/grib/15/` contenait à 15:47 UTC 92 fichiers du run 2026-10-20 15 UTC et 9 du run 2026-10-21 15 UTC (suppression des anciens fichiers à mesure que le nouveau run arrive) ; les dossiers 00, 06, 09, 12, 18, 21 ne contiennent qu'un run ; idem pour ICON-EU [vérifié]. La conservation est donc de 24 h environ par créneau ; le producteur ne la documente pas sur la page lue [hypothèse pour la règle de suppression].
- Taille par échéance, grille régulière, D2 à l'échéance 24 h (bz2) [vérifié] : `tot_prec` 3,0 Mo, `snowlmt` 3,9 Mo, `hzerocl` 3,9 Mo, `t_2m` 0,9 Mo, `snow_gsp` 0,17 Mo, `snow_con` 0,08 Mo, `h_snow` 0,02 Mo ; ICON-EU : `t_2m` 1,0 Mo, `snowlmt` 1,1 Mo, `hzerocl` 0,96 Mo, `tot_prec` 0,59 Mo, `snow_gsp` 0,04 Mo.
- Documentation officielle : https://www.dwd.de/EN/ourservices/opendata/opendata.html non lue ; conditions d'utilisation : voir Licence.
- Licence : la page « Legal notice » du DWD (https://www.dwd.de/EN/service/legal_notice/legal_notice.html, consultée le 2026-10-21) indique pour les contenus généraux : « Re-use is permitted solely under the terms of the Creative Commons license BY 4.0 » et pour les open data que les données « may be re-used under the Creative Commons licence conditions » (CC BY 4.0), à condition de citer la source ; la page ne traite explicitement ni la redistribution, ni l'obligation d'indiquer les modifications, ni la GeoNutzV [producteur, résumé de la page par l'outil de lecture, formulation exacte à relire]. Règles et modèles de mention de la source : page liée, non lue.

## Test d'accès

- Date : 2026-10-21, 15:45 à 16:10 UTC, sans compte.
- Commande exacte : `curl -sS https://opendata.dwd.de/weather/nwp/icon-d2/grib/12/` (liste des variables) ; `curl -sS https://opendata.dwd.de/weather/nwp/icon-d2/grib/12/snow_gsp/` (fichiers) ; `curl -sS -I https://opendata.dwd.de/weather/nwp/icon-d2/grib/12/snow_gsp/icon-d2_germany_regular-lat-lon_single-level_2026102112_048_2d_snow_gsp.grib2.bz2` ; téléchargement de `.../icon-d2/grib/12/<variable>/icon-d2_germany_regular-lat-lon_single-level_2026102112_024_2d_<variable>.grib2.bz2` pour 11 variables ; `.../icon-eu/grib/12/<variable>/icon-eu_europe_regular-lat-lon_single-level_2026102112_024_<VARIABLE>.grib2.bz2` pour 8 variables ; décompression `bunzip2`, lecture `eccodes`.
- Taille téléchargée : 15,0 Mo pour ICON-D2 (11 fichiers compressés) et 3,9 Mo pour ICON-EU (8 fichiers).
- Résultat observé : HTTP 200 sur tous les listings et fichiers ; `Last-Modified` renseigné ; pas de `Accept-Ranges` testé ; grille D2 1215 x 746, premier point 43,18 N 356,06 E, pas 0,02° ; grille EU 1377 x 657, pas 0,0625° [vérifié].

## Limites

- Conservation de 24 h : un job manqué n'est pas rattrapable (hors archive Open-Meteo, voir [open-meteo](open-meteo.md)).
- Un fichier par champ et par échéance : 49 requêtes par champ et par run pour ICON-D2 ; pas de lecture partielle utile, mais pas de découpage serveur non plus (grille entière de 1215 x 746 points).
- Les 4 messages des fichiers de cumul et les unités (`kg m-2` en cumul depuis le début du run) sont à confirmer avant tout calcul de neige fraîche sur 24 h.
- ICON-D2 s'arrête à 43,18 N : la bordure sud de l'emprise reste couverte, pas au-delà.
- Les ensembles `icon-d2-eps` et `icon-eu-eps` ne sont pas qualifiés.
- La sortie n'est pas un verdict de sécurité avalanche (référence : BRA Météo-France).

## Sources

- https://opendata.dwd.de/weather/nwp/ — répertoire des données NWP — consultée le 2026-10-21
- https://opendata.dwd.de/weather/nwp/icon-d2/grib/12/ — ICON-D2, run 12 UTC — consultée le 2026-10-21
- https://opendata.dwd.de/weather/nwp/icon-eu/grib/12/ — ICON-EU, run 12 UTC — consultée le 2026-10-21
- https://www.dwd.de/EN/service/legal_notice/legal_notice.html — mentions légales et réutilisation — consultée le 2026-10-21
