---
type: source
id: era5-land
nom: ERA5-Land (réanalyse des surfaces continentales, 0,1 degré, 1950 à aujourd'hui)
producteur: ECMWF pour Copernicus Climate Change Service (C3S)
licence: CC BY 4.0 (catalogue Copernicus CDS) ; mention exigée par la licence Copernicus (clause 5.1)
acces: compte gratuit requis (CDS) ; aucune copie Zarr anonyme qualifiée ; accès indirect sans compte via Open-Meteo (voir open-meteo-archive)
quotas: non lus au 2026-10-21 (files d'attente et limites par requête du CDS)
delai: ERA5-Land-T environ 5 jours ; version consolidée 2 à 3 mois plus tard
resolution: 0,1 degré (environ 9 km, grille régulière du CDS), horaire
conservation: archive permanente depuis 1950
statut: retenue
verifie_le: 2026-10-21
---

# ERA5-Land

Chaque affirmation porte sa source (consultée le 2026-10-21) et une marque : **[vérifié]**, **[producteur]**, **[tiers]** ou **[hypothèse]**. ERA5-Land est une simulation de surface **modélisée**, pilotée par l'atmosphère ERA5 ; les observations n'y entrent qu'indirectement. Ce n'est pas une mesure.

## Contenu

- Description : rejeu de la composante terre du modèle ECMWF avec le forçage atmosphérique ERA5, corrigé en température, humidité et pression pour la différence d'altitude entre la grille ERA5 et la grille ERA5-Land (« lapse rate correction »). [producteur] (catalogue CDS, documentation Confluence)
- Couverture temporelle : 1950-01-01 à 2026-10-15 d'après le catalogue CDS [vérifié] ; mise à jour quotidienne (ERA5-Land-T) puis remplacée par la version finale environ 2 mois après le mois concerné. [producteur]
- Résolution : grille régulière 0,1 x 0,1 degré (environ 9 km, ~0,08 degré natif) ; horaire. [producteur] Sur l'emprise : environ 29 x 31 points, soit environ 900 points [hypothèse, calcul].
- Variables utiles à la neige (formulaire CDS) [vérifié] : `snow_depth` (m, hauteur physique de neige), `snow_depth_water_equivalent` (m d'équivalent en eau), `snowfall` (m d'équivalent en eau, cumul depuis 00 UTC), `snow_cover` (%), `snow_density`, `snow_albedo`, `snowmelt`, `snow_evaporation`, `temperature_of_snow_layer`, plus `total_precipitation` et `2m_temperature`. Unités et conventions d'accumulation : [producteur] (documentation Confluence). Pas de phase des précipitations ni de `zero_degree_level` dans la liste du formulaire [vérifié] : la phase doit se déduire de la température [hypothèse].
- Limites de qualité signalées par le producteur : la hauteur de neige de 10 m ou plus est une valeur par défaut posée sur les glaciers (à traiter comme zone de glacier) ; problèmes d'initialisation de l'Antarctique. [producteur]. Open-Meteo avertit que la hauteur de neige ERA5-Land tend à être surestimée [tiers, https://open-meteo.com/en/docs/historical-weather-api].
- Formats : GRIB et NetCDF. Pas de copie anonyme Zarr trouvée (la recherche du 2026-10-21 n'a donné que des copies d'ERA5 non-Land) [vérifié pour l'absence dans les résultats].
- Volume sur l'emprise (calcul, non téléchargé) : 673 104 heures (1950-01-01 à 2026-10-15) x 900 points x 4 octets = environ 2,4 Go bruts par variable [hypothèse, calcul].
- Documentation officielle : catalogue CDS `reanalysis-era5-land`, DOI 10.24381/cds.e2161bac ; https://confluence.ecmwf.int/display/CKB/ERA5-Land%3A+data+documentation.
- Licence : `license: CC-BY-4.0` dans l'API du catalogue, licence « CC-BY licence » dans le formulaire, texte « This dataset is released for use under the CC-BY licence » [vérifié, lu le 2026-10-21]. Mention exigée par la licence Copernicus (clause 5.1) : pour une diffusion, une mention du type « Generated using Copernicus Climate Change Service information [année] » ; pour des produits modifiés, « Contains modified Copernicus Climate Change Service information [année] », avec l'avertissement que ni la Commission européenne ni l'ECMWF ne sont responsables de l'usage fait des données [producteur : https://apps.ecmwf.int/datasets/licences/copernicus/, lu le 2026-10-21].

## Test d'accès

- Date : 2026-10-21, vers 15:30 à 15:45 UTC.
- Commande exacte : `curl -sS https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-era5-land` (HTTP 200, 5 537 octets), puis `curl -sS -X POST -H 'Content-Type: application/json' -d '{"inputs":{"variable":["snow_depth"],"year":"2020","month":"01","day":"01","time":"00:00","data_format":"grib","area":[46.5,5.0,43.5,7.9],"product_type":"reanalysis"}}' https://cds.climate.copernicus.eu/api/retrieve/v1/processes/reanalysis-era5-land/execution`.
- Taille téléchargée : environ 12 Ko (catalogue et formulaire) ; aucune donnée.
- Résultat observé : HTTP 401 `{"type":"permission denied","detail":"authentication required"}` : le retrait de données exige un compte. **`compte gratuit requis`** ; aucun compte créé, test arrêté là [vérifié].

## Limites

- Compte gratuit CDS obligatoire pour télécharger ; files d'attente.
- Hauteur de neige modélisée sans assimilation de neige, au pas de 9 km : le relief alpin reste lissé ; la neige d'ERA5-Land n'a pas de score face aux stations dans ce dépôt (à établir avant tout usage d'entraînement).
- Pas de copie ouverte sans compte qualifiée : le volume doit passer par le CDS ou par Open-Meteo (quotas et licence d'usage à lire, voir [open-meteo-archive](open-meteo-archive.md)).
- Pas de verdict de sécurité avalanche : référence BRA Météo-France.
- L'URL `.../processes/reanalysis-era5-land/execution` répond 405 à un GET (POST attendu) : normal.

## Sources

- https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-era5-land — catalogue CDS ERA5-Land — consultée le 2026-10-21
- https://confluence.ecmwf.int/display/CKB/ERA5-Land%3A+data+documentation — documentation ERA5-Land — consultée le 2026-10-21
- https://apps.ecmwf.int/datasets/licences/copernicus/ — Licence to Use Copernicus Products (clause 5.1) — consultée le 2026-10-21
- https://open-meteo.com/en/docs/historical-weather-api — remarque sur la hauteur de neige ERA5-Land — consultée le 2026-10-21
