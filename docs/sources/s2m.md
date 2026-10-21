---
type: source
id: s2m
nom: Réanalyse S2M (SAFRAN-SURFEX/ISBA-Crocus-MEPRA), Alpes, Pyrénées, Corse, 1958-2021
producteur: Météo-France et CNRS (CNRM, Centre d'Études de la Neige), diffusion AERIS
licence: CC BY 4.0 d'après les métadonnées DataCite du DOI (rightsList, lues le 2026-10-21) ; à confirmer sur la page AERIS, injoignable le 2026-10-21 depuis la session
acces: téléchargement libre annoncé par le producteur via AERIS, DOI 10.25326/37 (version v2020.2) ; accès réel non testé (portail injoignable depuis le sandbox)
quotas: non documenté au 2026-10-21
delai: dernière version documentée v2020.2 (1958-2021) ; le titre du DOI annonce « 1958 - present » et DataCite indique une mise à jour le 2025-02-04, extension à vérifier sur AERIS
resolution: massifs (environ 1000 km2), bandes d'altitude de 300 m, plat + 8 expositions x 2 pentes (20 et 40 degrés) ; météo horaire, neige quotidienne à 06:00 UTC
conservation: archive permanente (DOI AERIS) ; dernière version documentée arrêtée au 2021-08-01 06:00 UTC
statut: a-tester
verifie_le: 2026-10-21
---

# Réanalyse S2M (SAFRAN-SURFEX/ISBA-Crocus-MEPRA)

Chaque affirmation porte sa source (consultée le 2026-10-21) et une marque : **[vérifié]**, **[producteur]**, **[tiers]** ou **[hypothèse]**. Une réanalyse est **modélisée**, pas observée : S2M est une simulation du manteau neigeux pilotée par une analyse météo par massif, non une mesure.

## Contenu

- Description : réanalyse météorologique et du manteau neigeux sur les massifs français (Alpes, Pyrénées, Corse) : SAFRAN analyse la météo par massif et par tranche d'altitude, le modèle Crocus (dans SURFEX/ISBA) simule la neige, MEPRA estime des indices de stabilité à partir du manteau simulé. [producteur] (Vernay et al., 2022, ESSD 14, 1707-1733, https://essd.copernicus.org/articles/14/1707/2022/)
- Couverture temporelle : du 1958-08-01 06:00 UTC au 2021-08-01 06:00 UTC pour la version v2020.2 ; l'évaluation neige porte sur 1983-2020. [producteur] (même article). Le titre du DOI est « The S2M meteorological and snow cover reanalysis in the French mountainous areas (1958 - present) », mis à jour le 2025-02-04 selon DataCite, format « NetCDF 3 » [producteur : https://api.datacite.org/dois/10.25326/37, lu le 2026-10-21] : une extension après 2021 est possible mais non vérifiée (AERIS injoignable).
- Couverture spatiale : massifs de 3 zones (Alpes françaises, Pyrénées, Corse), en unités conceptuelles d'environ 1000 km2 ; bandes d'altitude espacées de 300 m ; chaque bande a une simulation en terrain plat et 8 expositions (N à NO) à 2 pentes (20 et 40 degrés). Un jeu séparé de 665 points-stations (435 Alpes, 208 Pyrénées, 22 Corse), tous au-dessus de 600 m, a son propre shapefile. [producteur] Nombre exact de massifs alpins : non relu au 2026-10-21. Le maillage n'est pas une grille régulière : la correspondance avec l'emprise (ouest 5.0, sud 43.5, est 7.9, nord 46.5) se fait par la géométrie des massifs (shapefiles fournis) [hypothèse].
- Variables utiles à la neige : météo horaire (FORCING : température 2 m, vent 10 m, humidité, nébulosité, rayonnements, précipitations, ainsi que l'altitude de l'isotherme 0 °C et la limite pluie-neige) ; neige quotidienne à 06:00 UTC (PRO) dont hauteur totale de neige (nom `DSN_T_ISBA`), fraction de précipitation solide ; indices MEPRA. [producteur] Les noms exacts des variables chute de neige et équivalent en eau n'ont pas pu être confirmés (tableaux 3 à 7 en images, portail AERIS injoignable) : à lire dans le fichier avant usage [hypothèse : variables de type `Snowf`, `Rainf`, `WSN_T_ISBA`].
- Fréquence : pas de temps horaire (FORCING), quotidien à 06:00 UTC (PRO) ; jours d'analyse SAFRAN de 06:00 la veille à 06:00 le jour. [producteur]
- Formats : NetCDF, `FORCING.nc` et `PRO.nc`, 63 fichiers annuels par zone, plus shapefiles de géométrie. [producteur]
- Volume : non documenté au 2026-10-21 (ni l'article ni DataCite ne le donnent ; champ `sizes` vide). Seule la zone Alpes serait utile : 63 fichiers annuels x 2 types pour la v2020.2 [producteur pour le découpage, volume inconnu].
- Limites déclarées par le producteur : aucune observation de neige assimilée (l'évaluation sur 665 sites est indépendante) ; précipitations reconstruites avec la climatologie AURELHY jusqu'au 2017-08-01, puis totaux 24 h ARPEGE avec chronologie 6 h ensuite ; hétérogénéité temporelle due au nombre croissant d'observations de température (refroidissement artificiel d'environ 1,4 °C sur la température minimale) ; écart quadratique (RMSD) **médian** par tranche d'altitude de moins de 10 cm à environ 40 cm, avec un rapport RMSD / hauteur moyenne proche de 100 % sous 1200 m ; variabilité fine de la neige non résolue (précipitations à l'échelle du massif) ; une seule configuration de Crocus, pas d'ensemble. [producteur]
- Documentation officielle : article ESSD ci-dessus ; DOI de données https://doi.org/10.25326/37.
- Licence : DataCite (métadonnées du DOI 10.25326/37) donne `rightsList` « Creative Commons Attribution 4.0 International » (identifiant SPDX `cc-by-4.0`, https://creativecommons.org/licenses/by/4.0/legalcode) [producteur, lu le 2026-10-21]. La page AERIS, qui fait foi, n'a pas pu être lue : **confirmer la licence sur AERIS avant toute redistribution**. La page de l'article ESSD précise que son propre contenu est sous CC BY 4.0, ce qui ne vaut pas licence des données. Aucune mention d'Etalab ni de Licence Ouverte trouvée.

## Test d'accès

- Date : 2026-10-21.
- Commande exacte : `curl -sS -m 30 -L -o /dev/null -w "%{http_code} %{url_effective}\n" https://doi.org/10.25326/37`, puis la même requête sur la page d'atterrissage AERIS (`https://www.aeris-data.fr/landing-page/?uuid=865730e8-edeb-4c6b-ae58-80f95166509b`), `https://api.aeris-data.fr/` et `https://thredds.aeris-data.fr/thredds/catalog.html`. Le résolveur DOI a répondu HTTP 302 vers la page AERIS ci-dessus [vérifié]. AERIS (page d'atterrissage, api, thredds) et le DOI : injoignables le 2026-10-21 depuis la session. `https://api.datacite.org/dois/10.25326/37` : HTTP 200 [vérifié].
- Taille téléchargée : 0 octet de données.
- Résultat observé : `www.aeris-data.fr` : erreur TLS (SSL_ERROR_SYSCALL) puis HTTP 503 par l'outil de lecture web ; `api.aeris-data.fr` et `thredds.aeris-data.fr` : « CONNECT tunnel failed, response 502 » via le proxy du sandbox. L'accès réel (fichiers, licence, volume) **n'a pas pu être testé** ; ce n'est pas la preuve d'une indisponibilité du producteur [vérifié pour l'échec, hypothèse pour la cause : filtrage du sandbox]. Recherche d'une copie Zenodo : l'API `https://zenodo.org/api/records?q=S2M%20Crocus%20SAFRAN%20reanalysis&size=8` n'a rendu aucun enregistrement pertinent ; data.gouv.fr n'a pas pu être interrogé de façon concluante (connexions coupées par le proxy de la session).

## Limites

- Dernière version documentée arrêtée à 2021 : ne couvre pas les saisons 2021-2022 et suivantes tant qu'une extension n'est pas confirmée ; ne peut pas servir à la vérification en temps quasi réel.
- Non-stationnarité : rupture de méthode au 2017-08-01 (climatologie AURELHY puis totaux ARPEGE) et refroidissement artificiel d'environ 1,4 °C sur la température minimale dû au nombre croissant d'observations [producteur] : une période récente est un test naturel de dérive ; tout usage en entraînement ou en vérification exige des saisons entières mises de côté fixées à l'avance et une incertitude par blocs temporels (méthode §3).
- Pour la vérification, préférer des observations (stations, mesures de neige) : S2M est un modèle.
- Données par massif et tranche d'altitude, pas une grille : l'usage comme variable d'entraînement exige un choix explicite de rattachement (massif, altitude) des points de prévision.
- Quotas, volume, noms exacts des variables et licence sur AERIS non vérifiés : statut `a-tester` jusqu'à un test depuis un réseau qui joint AERIS.
- Produit modélisé : ne mesure aucune hauteur de neige et ne dit rien du risque d'avalanche. Le BRA de Météo-France reste la référence ; les indices MEPRA ne sont pas un verdict de sécurité.

## Sources

- https://essd.copernicus.org/articles/14/1707/2022/ — Vernay et al., The S2M reanalysis (ESSD 14, 1707) — consultée le 2026-10-21
- https://doi.org/10.25326/37 — DOI AERIS du jeu S2M (redirection constatée) — consultée le 2026-10-21
- https://www.aeris-data.fr/landing-page/?uuid=865730e8-edeb-4c6b-ae58-80f95166509b — page AERIS (injoignable le 2026-10-21 depuis la session) — consultée le 2026-10-21
- https://api.datacite.org/dois/10.25326/37 — métadonnées DataCite du DOI (licence, titre, mise à jour) — consultée le 2026-10-21
- https://zenodo.org/api/records?q=S2M%20Crocus%20SAFRAN%20reanalysis&size=8 — recherche Zenodo (sans résultat) — consultée le 2026-10-21
