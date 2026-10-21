---
type: source
id: uerra-mescan-surfex
nom: UERRA (UERRA-HARMONIE et MESCAN-SURFEX), réanalyse régionale européenne 1961-2019
producteur: Météo-France, SMHI et partenaires (projet UERRA) pour Copernicus Climate Change Service (C3S)
licence: CC BY 4.0 (catalogue Copernicus CDS)
acces: compte gratuit requis (CDS)
quotas: non lus au 2026-10-21
delai: non applicable (série finie, mise à jour non prévue)
resolution: MESCAN-SURFEX 5,5 km (grille 1069 x 1069), UERRA-HARMONIE 11 km (565 x 565) ; analyses à 00, 06, 12 et 18 UTC
conservation: archive permanente (DOI CDS)
statut: a-tester
verifie_le: 2026-10-21
---

# UERRA (UERRA-HARMONIE et MESCAN-SURFEX)

Chaque affirmation porte sa source (consultée le 2026-10-21) et une marque : **[vérifié]**, **[producteur]**, **[tiers]** ou **[hypothèse]**. Réanalyse **modélisée**, pas observée. Précurseur de CERRA ; utile seulement si CERRA ne couvre pas la période voulue.

## Contenu

- Description : analyses de surface et de proche surface issues de UERRA-HARMONIE (assimilation variationnelle 3D) et de MESCAN-SURFEX (analyse de surface par interpolation optimale, SURFEX rejoué hors ligne). Prévisions jusqu'à 30 h disponibles par l'API CDS seulement. [producteur]
- Couverture temporelle : 1961-01 à 2019-07 [producteur, titre du catalogue « from 1961 to 2019 », page de documentation] ; mise à jour « Not planned » (non prévue) [vérifié, `cads:update_frequency`]. L'`extent` temporel du catalogue ne montre que 2018-10-18 à 2019-07-31 : incohérence propre à l'API, non résolue.
- Résolution : MESCAN-SURFEX 5,5 km, UERRA-HARMONIE 11 km. [producteur] Aucun détail propre aux Alpes lu.
- Variables utiles à la neige (formulaire CDS) [vérifié] : `snow_density` et `snow_depth_water_equivalent` (kg/m2) ; pas de hauteur de neige en mètres ni de chute de neige dans la liste lue. Les listes complètes (19 variables) n'ont pas été relues en détail pour les précipitations ni la température.
- Couverture de l'emprise : domaine européen, Alpes comprises [hypothèse : domaine identique à CERRA, non vérifié pour UERRA].
- Formats : GRIB et NetCDF4 (expérimental) [vérifié].
- Volume : non calculé (variables et fréquence non figées).
- Documentation officielle : DOI CDS 10.24381/cds.32b04ec5. La documentation ne mentionne ni limites propres à la neige ni la version corrigée « UERRA-Land2 ». Une communication de conférence EMS 2022 dit que UERRA-Land2 (1961-2019) était disponible sur demande à Météo-France [tiers : https://meetingorganizer.copernicus.org/EMS2022/EMS2022-578.html, résumé de recherche, non relu].
- Licence : `license: CC-BY-4.0` dans l'API du catalogue [vérifié].

## Test d'accès

- Date : 2026-10-21.
- Commande exacte : `curl -sS https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-uerra-europe-single-levels` puis lecture du formulaire lié.
- Taille téléchargée : moins de 0,2 Mo de métadonnées.
- Résultat observé : catalogue lisible sans compte (HTTP 200) ; retrait de données non tenté ; **`compte gratuit requis`** (même mécanisme que les autres jeux CDS, vérifié sur ERA5-Land avec HTTP 401).

## Limites

- Finit en 2019 : ne sert ni à l'archive des saisons récentes ni à la vérification récente ; intérêt limité à un entraînement sur 1961-2019 si CERRA ne convient pas.
- Compte CDS requis ; qualité en montagne non qualifiée ici.
- Pas de verdict de sécurité avalanche : référence BRA Météo-France.

## Sources

- https://cds.climate.copernicus.eu/api/catalogue/v1/collections/reanalysis-uerra-europe-single-levels — catalogue CDS UERRA — consultée le 2026-10-21
- https://cds.climate.copernicus.eu/datasets/reanalysis-uerra-europe-single-levels?tab=doc — documentation CDS UERRA — consultée le 2026-10-21
- https://meetingorganizer.copernicus.org/EMS2022/EMS2022-578.html — résumé EMS 2022 (UERRA-Land2) — consultée le 2026-10-21
