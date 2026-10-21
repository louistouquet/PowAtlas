---
type: source
id: cerra
nom: CERRA et CERRA-Land (réanalyses régionales européennes à 5,5 km, 1984 à 2026)
producteur: Météo-France et partenaires pour Copernicus Climate Change Service (C3S)
licence: CC BY 4.0 (catalogue Copernicus CDS) ; mention exigée par la licence Copernicus (clause 5.1)
acces: compte gratuit requis (CDS) ; aucune copie ouverte sans compte trouvée
quotas: non lus au 2026-10-21 (files d'attente et limites par requête du CDS)
delai: CERRA mise à jour mensuelle avec retard de quelques mois ; CERRA-Land irrégulière ; la documentation Confluence est en désaccord avec le catalogue (voir Contenu)
resolution: 5,5 km, projection conique conforme de Lambert, grille 1069 x 1069 ; analyses toutes les 3 h
conservation: archive permanente (DOI CDS)
statut: retenue
verifie_le: 2026-10-21
---

# CERRA et CERRA-Land

Chaque affirmation porte sa source (consultée le 2026-10-21) et une marque : **[vérifié]**, **[producteur]**, **[tiers]** ou **[hypothèse]**. Ce sont des réanalyses **modélisées**, pas des observations.

## Contenu

- Description : CERRA est une réanalyse régionale européenne à 5,5 km (assimilation d'observations dans le modèle HARMONIE-AROME, 106 niveaux) ; CERRA-Land est une réanalyse de surface qui rejoue SURFEX avec les analyses CERRA de température, humidité et la précipitation analysée par MESCAN. [producteur] (catalogue CDS, Confluence)
- Couverture temporelle :
  - CERRA, niveaux de surface : 1984-09-01 à 2026-07-31 selon l'extension du catalogue CDS et les contraintes du formulaire (dernier couple année-mois : 2026-07) [vérifié le 2026-10-21] ; mise à jour mensuelle [producteur].
  - CERRA-Land : 1984-09-01 à 2025-12-31 (dernier couple année-mois du formulaire : 2025-12) [vérifié] ; mise à jour « irrégulière » [producteur].
  - **Désaccord apparent, probablement une documentation antérieure à la reprise** : le formulaire CDS de CERRA liste 503 mois sans trou de 1984-09 à 2026-07 [calcul de la relecture sur les contraintes, non refait ici ; dernier couple année-mois 2026-07 vérifié], le titre du catalogue dit « from 1984 to present » et `cads:update_frequency` vaut « Monthly » [vérifié]. La page Confluence « Product User Guide » annonce une période finissant le 2021-06-30 et, dans sa FAQ, une suspension de la production « until the contract is signed » ; elle est donc antérieure à la reprise [hypothèse] ; Open-Meteo indique aussi « 1985 à juin 2021 » [producteur tiers]. Une requête réelle avec un compte gratuit reste la confirmation à obtenir avant de compter sur 2021-2026.
- Résolution : 5,5 km (CERRA et CERRA-Land), grille Lambert 1069 x 1069 ; analyses 3-horaires (00, 03, ..., 21 UTC), prévisions courtes horaires ; CERRA-EDA (ensemble) à 11 km et 6 h. [producteur]
- Couverture de l'emprise (ouest 5.0, sud 43.5, est 7.9, nord 46.5) : le domaine couvre toute l'Europe, Alpes comprises. Environ 41 x 61 points, soit environ 2 500 [hypothèse, calcul : 226 km x 333 km à 5,5 km].
- Variables utiles à la neige (formulaires CDS) [vérifié] :
  - CERRA surface : `snow_density`, `snow_depth`, `snow_depth_water_equivalent`, `snow_fall_water_equivalent`, `total_precipitation`, `2m_temperature` ; la densité est absente là où il n'y a pas de neige [producteur].
  - CERRA-Land : `fraction_of_snow_cover`, `snow_albedo`, `snow_density`, `snow_depth`, `snow_depth_water_equivalent`, `snow_melt`, `temperature_of_snow_layer`, `total_precipitation`.
  - Pas de variable de type de précipitation ni d'isotherme 0 °C dans les listes lues (la phase se déduit de la température) [vérifié pour l'absence].
- Formats : GRIB (et NetCDF4 expérimental selon le formulaire UERRA, non relu pour CERRA) [hypothèse pour CERRA].
- Volume sur l'emprise (calcul, non téléchargé) : 2 500 points x 4 octets x 8 analyses par jour x 366 jours x 42 ans = environ 1,2 Go bruts par variable [hypothèse, calcul].
- Limites déclarées : résultats en terrain complexe (montagnes, côtes) « généralement moins fiables » que sur terrain homogène ; précipitations difficiles à reconstruire, extrêmes moins bien captés ; pas de limites propres à la neige dans le guide. [producteur]
- Documentation officielle : DOI CDS 10.24381/cds.622a565a (CERRA surface) et 10.24381/cds.a7f3cd0b (CERRA-Land) ; https://confluence.ecmwf.int/display/CKB/Copernicus+European+Regional+ReAnalysis+%28CERRA%29%3A+Product+User+Guide.
- Licence : `license: CC-BY-4.0` dans l'API du catalogue pour CERRA et CERRA-Land ; le formulaire propose « CC-BY licence » (« This dataset is released for use under the CC-BY licence ») [vérifié, lu le 2026-10-21]. Mention exigée par la licence Copernicus (clause 5.1) : pour une diffusion, une mention du type « Generated using Copernicus Climate Change Service information [année] » ; pour des produits modifiés, « Contains modified Copernicus Climate Change Service information [année] », avec l'avertissement que ni la Commission européenne ni l'ECMWF ne sont responsables de l'usage fait des données [producteur : https://apps.ecmwf.int/datasets/licences/copernicus/, lu le 2026-10-21].

## Test d'accès

- Date : 2026-10-21, vers 15:30 à 15:50 UTC.
- Commande exacte : `curl -sS https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-cerra-single-levels` (HTTP 200, 6 844 octets), idem pour `reanalysis-cerra-land` (HTTP 200, 6 614 octets), puis lecture des fichiers de formulaire et de contraintes liés. Retrait de données : non tenté pour CERRA ; la même route sur ERA5-Land (`.../processes/reanalysis-era5-land/execution`, qui répond 405 à un GET : POST attendu) a rendu HTTP 401 `authentication required` [vérifié], et le CDS applique le même mécanisme à tous ses jeux [hypothèse].
- Taille téléchargée : environ 0,5 Mo (catalogues, formulaires, contraintes).
- Résultat observé : **`compte gratuit requis`** pour le retrait ; aucun compte créé, test arrêté là.

## Limites

- Compte gratuit CDS obligatoire ; aucune copie ouverte sans compte trouvée (Open-Meteo propose CERRA jusqu'en 2021 selon sa page, accès et licence d'usage à lire, voir [open-meteo-archive](open-meteo-archive.md)).
- Fin de série à confirmer par requête réelle (catalogue : 2026-07 ; guide antérieur : 2021) : à trancher avant de décider si CERRA sert à l'archive des saisons récentes.
- Modèle d'assimilation sans neige observée dans cette fiche : la neige est celle de SURFEX, non validée ici contre des stations.
- Pas de verdict de sécurité avalanche : référence BRA Météo-France.

## Sources

- https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-cerra-single-levels — catalogue CDS CERRA — consultée le 2026-10-21
- https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-cerra-land — catalogue CDS CERRA-Land — consultée le 2026-10-21
- https://confluence.ecmwf.int/display/CKB/Copernicus+European+Regional+ReAnalysis+%28CERRA%29%3A+Product+User+Guide — guide produit CERRA — consultée le 2026-10-21
- https://apps.ecmwf.int/datasets/licences/copernicus/ — Licence to Use Copernicus Products (clause 5.1) — consultée le 2026-10-21
- https://open-meteo.com/en/docs/historical-weather-api — période CERRA citée par Open-Meteo — consultée le 2026-10-21
