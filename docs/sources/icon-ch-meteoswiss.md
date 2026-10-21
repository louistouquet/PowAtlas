---
type: source
id: icon-ch-meteoswiss
nom: ICON-CH1-EPS et ICON-CH2-EPS (MeteoSwiss, open data, API STAC)
producteur: Office fédéral de météorologie et de climatologie MeteoSwiss
licence: Creative Commons CC BY 4.0 ; mention « Source: MeteoSwiss » obligatoire, sans suggérer une caution de MeteoSwiss
acces: HTTPS anonyme, sans compte ni clé : catalogue STAC https://data.geo.admin.ch/api/stac/v1/ ; les fichiers sont servis par des liens signés fournis par le catalogue (non recopiés, non committables)
quotas: non documentés au 2026-10-21 ; aucune limite constatée sur une centaine de requêtes
delai: ICON-CH1 run 15 UTC : fichiers créés vers 16:53 UTC (environ 1 h 53) ; ICON-CH2 run 12 UTC : vers 14:48 UTC (environ 2 h 48)
resolution: ICON-CH1 1 km, 33 h, mise à jour toutes les 3 h ; ICON-CH2 2,1 km, 120 h, mise à jour toutes les 6 h ; ensemble (contrôle et membres perturbés), grille native ICON non régulière
conservation: 24 h (champ `expires` des éléments STAC : création plus 24 h environ)
statut: retenue
verifie_le: 2026-10-21
---

# ICON-CH1-EPS et ICON-CH2-EPS (MeteoSwiss)

Chaque affirmation porte sa source et sa date de consultation (2026-10-21), et une marque : **[vérifié]**, **[producteur]**, **[tiers]** ou **[hypothèse]**.

## Contenu

- Description : prévision d'ensemble haute résolution de MeteoSwiss (ICON-CH1-EPS : 1 km, 33 h, toutes les 3 h ; ICON-CH2-EPS : 2,1 km, 120 h, toutes les 6 h), « available for the last 24 hours » [producteur : description des collections STAC `ch.meteoschweiz.ogd-forecasting-icon-ch1` et `-ch2`].
- Runs et échéances : CH1 8 runs par jour (références 15, 18, 21, 00, 03 UTC constatées) jusqu'à 33 h ; CH2 4 runs par jour (référence 12 UTC constatée, échéances jusqu'à 4 j 22 h constatées sur les 100 premiers éléments) [vérifié sur les éléments STAC].
- Variables utiles à la neige (fichier `params_icon-ch1-eps.csv`, 118 paramètres, et `params_icon-ch2-eps.csv`, 119) [vérifié] : `TOT_PREC`, `SNOW_GSP` (neige grande échelle, équivalent en eau), `RAIN_GSP`, `GRAU_GSP` (graupel), `H_SNOW` (hauteur de neige, m), `W_SNOW` (équivalent en eau), `RHO_SNOW`, `SNOWC`, `FRESHSNW`, `T_SNOW`, `SNOWLMT` (limite des chutes de neige), `HZEROCL` (isotherme 0 °C), `T_2M`, vent, humidité, rayonnement, hydrométéores `QS`, `QR`, `QG`, `TQS`. Pas de `SNOW_CON` dans les deux listes [vérifié]. Les cumuls sont libellés « kg m-2 s-1 », unité ambiguë pour un cumul : à confirmer par lecture d'un fichier [producteur].
- Couverture de l'emprise des Alpes françaises (ouest 5.0, sud 43.5, est 7.9, nord 46.5) : emprise des collections : CH1 de 0,82 W à 17,71 E et de 42,03 N à 50,5 N ; CH2 de 0,77 W à 17,68 E et de 42,08 N à 50,48 N : l'emprise y est entière [producteur, `extent.spatial.bbox`]. Nombre de points sur l'emprise : environ 76 000 (1 km) et 17 000 (2,1 km) [hypothèse, calcul géométrique à 45 N ; grille native non lue].
- Formats : GRIB2, un fichier par variable, par échéance et par type de membre (`ctrl` ou `perturbed`, tous les membres perturbés dans un même fichier) ; fichiers de constantes de grille horizontale et verticale ; tailles lues par plage `bytes=0-0` : CH1 contrôle `TOT_PREC` et `SNOW_GSP` 2 296 159 o par échéance, `SNOWLMT` environ 2,24 Mo ; CH2 contrôle 567 951 o [vérifié] ; taille des fichiers `perturbed` non lue.
- Délai : voir en-tête [vérifié, `Last-Modified` et `created`].
- Conservation : « available for the last 24 hours » et propriété `expires` des éléments, environ 24 h après la création [vérifié, producteur].
- Documentation officielle : https://opendatadocs.meteoswiss.ch/ (conditions d'utilisation lues).
- Licence : « The 'Open Data' of MeteoSwiss are published accordingly under the Creative Commons Licence CC BY 4.0 » ; réutilisation commerciale permise ; adaptation permise ; mention « Source: MeteoSwiss » ; « you must ensure that it does not appear as if MeteoSwiss supports you or your use » ; les avertissements ne peuvent être redistribués que sans altération [producteur, https://opendatadocs.meteoswiss.ch/general/terms-of-use, consultée le 2026-10-21 ; résumé de la page par l'outil de lecture]. Le champ `license` des collections vaut `CC-BY` [vérifié].

## Test d'accès

- Date : 2026-10-21, 16:00 à 17:00 UTC, sans compte.
- Commande exacte : `curl -sS "https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-forecasting-icon-ch1"` ; `curl -sS "https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-forecasting-icon-ch1/items?limit=100&sortby=-properties.created"` ; téléchargement du fichier `params_icon-ch1-eps.csv` (lien signé pris dans les `assets` de la collection, non recopié) ; lecture de la taille de fichiers par requête `Range: bytes=0-0` sur les liens des éléments.
- Taille téléchargée : environ 0,3 Mo (JSON STAC et deux CSV de 11 Ko), aucun fichier de données entier.
- Résultat observé : HTTP 200 ; les liens signés répondent en GET (206 avec `Content-Range`), mais pas en HEAD (403) ; les éléments listés portent `forecast:reference_datetime`, `forecast:horizon`, `forecast:variable`, `forecast:perturbed`, `expires` [vérifié]. Les liens signés sont valables longtemps ; ne jamais les committer.

## Limites

- Conservation de 24 h : un job manqué n'est pas rattrapable, hors archive Open-Meteo (CH1 et CH2 depuis 2025-07-29, voir [open-meteo](open-meteo.md)).
- Grille native ICON (non régulière) : le découpage sur l'emprise exige les fichiers de constantes de grille et une réinterpolation (traitement du projet, non qualifié).
- Volume élevé pour l'ensemble complet (11 membres CH1 par variable et par échéance) : l'archive se limite au membre de contrôle et à des statistiques d'ensemble calculées côté client [hypothèse].
- Le domaine déborde largement les Alpes françaises vers la Suisse : utile pour la vérification sur des stations suisses.
- La sortie n'est pas un verdict de sécurité avalanche (référence : BRA Météo-France).

## Sources

- https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-forecasting-icon-ch1 — collection ICON-CH1-EPS — consultée le 2026-10-21
- https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-forecasting-icon-ch2 — collection ICON-CH2-EPS — consultée le 2026-10-21
- https://opendatadocs.meteoswiss.ch/general/terms-of-use — conditions d'utilisation — consultée le 2026-10-21
