---
type: source
id: era5
nom: ERA5 (réanalyse globale horaire, 0,25 degré, 1940 à aujourd'hui)
producteur: ECMWF pour Copernicus Climate Change Service (C3S) ; copie Google Cloud (ARCO-ERA5) par Google
licence: CC BY 4.0 sur le catalogue Copernicus (CDS) ; mention exigée par la licence Copernicus (clause 5.1) ; la copie Google renvoie à l'ancienne licence Copernicus
acces: CDS (cds.climate.copernicus.eu) : compte gratuit requis ; copie Zarr publique sans compte : gs://gcp-public-data-arco-era5 (lecture anonyme HTTPS testée)
quotas: CDS : files d'attente et limites de requête, non lues au 2026-10-21 ; bucket Google : aucun quota documenté sur la page consultée
delai: ERA5T environ 5 jours ; version consolidée 2 à 3 mois plus tard (CDS) ; copie Google : réanalyse finale jusqu'au 2026-06-30 et ERA5T jusqu'au 2026-10-15 constatés le 2026-10-21
resolution: 0,25 degré (environ 28 km), horaire ; ensemble EDA 0,5 degré toutes les 3 h
conservation: archive permanente depuis 1940
statut: retenue
verifie_le: 2026-10-21
---

# ERA5

Chaque affirmation porte sa source (consultée le 2026-10-21) et une marque : **[vérifié]**, **[producteur]**, **[tiers]** ou **[hypothèse]**. ERA5 est une réanalyse **modélisée** (modèle + assimilation d'observations), pas une observation.

## Contenu

- Description : réanalyse atmosphérique globale ECMWF, estimations horaires de nombreuses variables, avec ensemble d'incertitude à 10 membres toutes les 3 h ; données depuis 1940. [producteur] (catalogue CDS)
- Couverture temporelle : 1940-01-01 à 2026-10-15 d'après l'extension temporelle du catalogue CDS [vérifié] ; mise à jour quotidienne [producteur] ; dans la copie Google, `valid_time_start` 1940-01-01, `valid_time_stop` 2026-06-30 (final), `valid_time_stop_era5t` 2026-10-15, `last_updated` 2026-10-21 03:46 UTC [vérifié].
- Variables utiles à la neige (liste du formulaire CDS) [vérifié] : `snowfall` et `snow_depth` (toutes deux en m d'équivalent en eau, unité lue dans les métadonnées Zarr), `snow_density`, `snow_albedo`, `snowmelt`, `snow_evaporation`, `temperature_of_snow_layer`, `total_column_snow_water`, `convective_snowfall`, `large_scale_snowfall` (et leurs équivalents en taux), `mean_snowfall_rate`, `mean_snowmelt_rate` ; plus `total_precipitation`, `precipitation_type`, `zero_degree_level`, `2m_temperature` et les niveaux de pression. Pas de hauteur de neige en mètres de neige : la hauteur physique se déduit de l'équivalent en eau et de la densité [hypothèse].
- Couverture de l'emprise (ouest 5.0, sud 43.5, est 7.9, nord 46.5) : produit global. À 0,25 degré, environ 12 x 13 points, soit environ 156 points [hypothèse, calcul]. À 28 km, le relief alpin est très lissé.
- Fréquence : horaire.
- Formats : GRIB et NetCDF via CDS [producteur] ; Zarr (blosc/lz4, blocs d'une heure sur la grille globale 721 x 1440) dans la copie Google [vérifié].
- Volume sur l'emprise (calcul, non téléchargé) : l'axe temps de la copie Google compte 1 323 648 heures mais il est **pré-alloué** jusqu'à fin 2090 ; la série réelle va de 1940-01-01 à 2026-10-15 (`valid_time_stop_era5t`), soit 31 699 jours = 760 776 heures [vérifié pour les bornes, calcul pour le total]. Sur l'emprise : 760 776 h x 156 points x 4 octets = environ 0,47 Go bruts par variable sur toute la série [hypothèse, calcul] ; une dizaine de variables : environ 4,7 Go bruts. Avec la copie Google, le bloc d'une heure est un champ **global** : extraire une série locale lit un bloc d'environ 0,4 Mo par variable et par heure (395 Ko constaté pour `snow_depth`), soit environ 300 Go de transfert par variable pour toute la série (760 776 x 0,395 Mo) [hypothèse, calcul] : à éviter ; préférer la file d'attente CDS avec sélection de zone, ou un jeu de séries temporelles CDS.
- Copies ouvertes sans compte : Google ARCO-ERA5 (ci-dessus). Une copie Earthmover (Icechunk/Zarr v3, 1940-2025, environ 31 km) est listée sur AWS Marketplace [tiers : https://aws.amazon.com/marketplace/pp/prodview-ggs5znhej4ol2, non testée]. Hugging Face : l'API de recherche (`https://huggingface.co/api/datasets?search=era5&limit=8&sort=downloads&direction=-1`) renvoie plusieurs jeux nommés ERA5 (par exemple `nmasi/era5`, `jacobbieker/era5-6hour`) avec des licences hétérogènes (cc-by-nc-4.0, mit, cc-by-4.0 ou aucune) ; contenu et provenance non lus, non qualifiés ici [vérifié pour la liste, non lu pour le contenu].
- Documentation officielle : catalogue CDS `reanalysis-era5-single-levels`, DOI 10.24381/cds.adbb2d47.
- Licence : l'API du catalogue CDS donne `license: CC-BY-4.0` (lien https://spdx.org/licenses/CC-BY-4.0) et le formulaire propose la licence « CC-BY licence » dont le texte dit « This dataset is released for use under the CC-BY licence » [vérifié, lu le 2026-10-21] : c'est la licence en vigueur retenue. La FAQ du README de la copie Google dit « Yes, you can use our ERA5 data according to the terms of the Copernicus license » et renvoie à l'ancien PDF « licence-to-use-copernicus-products » (Licence to Use Copernicus Products), demande aux chercheurs de citer le travail et aux usagers commerciaux de reconnaître le C3S [producteur de la copie : https://raw.githubusercontent.com/google-research/arco-era5/main/README.md, lu le 2026-10-21] ; la page Google dit seulement que son contenu est sous CC BY 4.0 et son code sous Apache 2.0. Mention exigée par la licence Copernicus (clause 5.1) : pour une diffusion, une mention du type « Generated using Copernicus Climate Change Service information [année] » ; pour des produits modifiés, « Contains modified Copernicus Climate Change Service information [année] », avec l'avertissement que ni la Commission européenne ni l'ECMWF ne sont responsables de l'usage fait des données [producteur : https://apps.ecmwf.int/datasets/licences/copernicus/, lu le 2026-10-21].

## Test d'accès

- Date : 2026-10-21, vers 15:30 à 15:45 UTC.
- Commande exacte :
  - `curl -sS https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-era5-single-levels` (HTTP 200, 7 666 octets) et le formulaire lié.
  - `curl -sS -X POST -H 'Content-Type: application/json' -d '{"inputs":{...}}' https://cds.climate.copernicus.eu/api/retrieve/v1/processes/reanalysis-era5-land/execution` (requête de retrait anonyme sur ERA5-Land, sans compte) : HTTP 401 `authentication required` [vérifié]. Même régime attendu pour ERA5 : `compte gratuit requis` ; aucun compte créé.
  - `curl -sS https://storage.googleapis.com/gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3/.zmetadata` (HTTP 200, 132 785 octets) puis `curl -sS -o sd.chunk https://storage.googleapis.com/gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3/snow_depth/1000000.0.0` (HTTP 200).
- Taille téléchargée : environ 0,6 Mo au total (métadonnées 132 785 octets, bloc `snow_depth` 394 947 octets, catalogue et formulaire).
- Résultat observé : lecture anonyme du bucket sans clé [vérifié] ; `snow_depth` de forme [1323648, 721, 1440], blocs [1, 721, 1440], type float32, unité « m of water equivalent » ; variables de neige listées ci-dessus présentes [vérifié]. Le listing des préfixes `ar/` montre aussi des versions plus anciennes (1959-2022) à ne pas utiliser pour les saisons récentes.

## Limites

- CDS : compte gratuit requis, files d'attente, limites par requête (non lues).
- Résolution 28 km : biais d'altitude et de précipitations attendus sur les Alpes ; produit modélisé, jamais une mesure.
- Copie Google : blocs d'une heure globaux, mauvais pour les séries locales ; mises à jour par le seul producteur de la copie (dépend d'un tiers, pas d'un engagement documenté).
- Entre la réanalyse finale (jusqu'au 2026-06-30 dans la copie) et ERA5T (jusqu'au 2026-10-15), les valeurs récentes peuvent être révisées [producteur : ERA5T remplacée par la version finale].
- Pas de verdict de sécurité avalanche : référence BRA Météo-France.

## Sources

- https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-era5-single-levels — catalogue CDS ERA5 — consultée le 2026-10-21
- https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview — page du jeu — consultée le 2026-10-21
- https://object-store.os-api.cci2.ecmwf.int:443/cci2-prod-catalogue/licences/cc-by/cc-byv1_2b61eb0b42e053566cb9447c1d2847a69a275c095e00fca00bad1bf5326a9432.md — texte de la licence CC-BY du CDS — consultée le 2026-10-21
- https://storage.googleapis.com/gcp-public-data-arco-era5/ — bucket ARCO-ERA5 — consultée le 2026-10-21
- https://github.com/google-research/arco-era5 — dépôt ARCO-ERA5 — consultée le 2026-10-21
- https://docs.cloud.google.com/storage/docs/public-datasets/era5 — page Google Cloud ERA5 — consultée le 2026-10-21
- https://raw.githubusercontent.com/google-research/arco-era5/main/README.md — README ARCO-ERA5 (FAQ licence) — consultée le 2026-10-21
- https://apps.ecmwf.int/datasets/licences/copernicus/ — Licence to Use Copernicus Products (clause 5.1) — consultée le 2026-10-21
- https://aws.amazon.com/marketplace/pp/prodview-ggs5znhej4ol2 — copie Earthmover ERA5 (non testée) — consultée le 2026-10-21
- https://huggingface.co/api/datasets?search=era5&limit=8&sort=downloads&direction=-1 — recherche Hugging Face — consultée le 2026-10-21
