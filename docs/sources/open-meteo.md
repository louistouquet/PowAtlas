---
type: source
id: open-meteo
nom: Open-Meteo Weather Forecast, Historical Forecast et Previous Runs API
producteur: Open-Meteo.com (agrège des modèles de DWD, Météo-France, ECMWF, NOAA, MeteoSwiss et autres)
licence: données de l'API sous CC BY 4.0 selon la page https://open-meteo.com/en/licence (lue par la fiche open-meteo-archive ; cette page ne mentionne ni usage commercial ni quota) ; les pages Historical Forecast et Previous Runs lues ici n'énoncent aucune licence de données ; les modèles amont gardent leurs licences ; la restriction « usage non commercial » de l'API gratuite vient de https://open-meteo.com/en/pricing (lue par la fiche open-meteo-archive)
acces: HTTPS sans compte ni clé pour l'offre gratuite (api.open-meteo.com, historical-forecast-api.open-meteo.com, previous-runs-api.open-meteo.com) ; requêtes par point
quotas: 600 appels par minute, 5 000 par heure, 10 000 par jour, 300 000 par mois pour l'offre gratuite non commerciale (voir open-meteo-archive) ; limite journalière atteinte (HTTP 429) sur l'API de prévision lors du test
delai: non documenté au 2026-10-21 (les pages lues indiquent une mise à jour toutes les 1 à 6 h selon le modèle)
resolution: celle de chaque modèle (AROME France HD 1,3 km, ICON-D2 2 km, ICON-CH1 1 km...) ; horaire, 15 minutes pour certaines variables
conservation: Historical Forecast : depuis 2022-11-13 (AROME France HD) ; Previous Runs : « most models are archived from January 2024 »
statut: a-tester
verifie_le: 2026-10-21
---

# Open-Meteo : prévisions historiques et exécutions précédentes

Chaque affirmation porte sa source et sa date de consultation (2026-10-21), et une marque : **[vérifié]**, **[producteur]**, **[tiers]** ou **[hypothèse]**. La réanalyse servie par la même société est décrite dans [open-meteo-archive](open-meteo-archive.md).

## Contenu

- Description : trois services complémentaires. **Weather Forecast API** : prévisions courantes d'un modèle choisi (`models=meteofrance_arome_france_hd`). **Historical Forecast API** : « Historical forecasts archived from the Weather Forecast API — same models, same parameters, same response format » ; « Each run's first few hours are stitched into a continuous hourly timeseries » ; « Not suitable for long time series due to model version changes over time » [producteur : https://open-meteo.com/en/docs/historical-forecast-api]. **Previous Runs API** : « Data from past model runs is aligned to fixed lead-time offsets of 1–7 days » (variables `_previous_day1` à `_previous_day7`) [producteur : https://open-meteo.com/en/docs/previous-runs-api].
- Intérêt pour PowAtlas : source d'**historique de prévisions avant novembre 2026**, non reconstituable autrement (conservation de 14 jours pour AROME, 24 h pour ICON-D2 et ICON-CH). Début des archives (Historical Forecast, « Available Since ») : AROME France HD 2022-11-13 ; AROME France 2024-01-02 ; ARPEGE Europe 2022-11-13 ; ICON-D2 et ICON-EU 2022-11-24 ; GFS 2021-03-23 ; ECMWF IFS 0,25° 2024-02-03 ; AIFS 0,25° Single 2025-02-20 ; ICON-CH1 et ICON-CH2 2025-07-29 [producteur]. Mais ce sont des séries aux **premières heures de chaque run** (donc proches d'une analyse), pas des échéances de 24 à 72 h : elles ne permettent pas de vérifier une prévision à 24, 48, 72 h. Seule la Previous Runs API fournit des échéances décalées (jour 1 à 7), à partir de janvier 2024 pour la plupart des modèles [producteur].
- Variables neige : horaire `Snowfall`, `Snow Depth`, `Freezing level height` ; 15 minutes : `Snowfall`, `Snowfall height`, `Freezing level height` ; quotidien : `Snowfall Sum`, `Snowfall Water Equivalent Sum` [producteur, Historical Forecast]. Previous Runs : `snowfall` listée ; `snow_depth` et `freezing_level_height` non mentionnées [producteur]. Une requête réelle à la Previous Runs API (`temperature_2m` et `temperature_2m_previous_day1`, `ecmwf_ifs025`, 3 jours) a rendu des valeurs, altitude de maille 2223 m pour 45,1 N 6,4 E [vérifié].
- Couverture de l'emprise : mondiale, par point ; une requête par point de grille ou par site.
- Formats : JSON (CSV et autres selon la documentation, non testés).
- Documentation officielle : voir Sources.
- Licence : les pages Historical Forecast et Previous Runs ne proposent que trois offres d'usage (« Non-Commercial », « Commercial », « Self-Hosted ») sans en énoncer les termes, et la seule mention de droit d'auteur est « © 2022-2026 Copyright: Open-Meteo.com » [producteur, pages lues le 2026-10-21]. La restriction non commerciale de l'offre gratuite ne figure pas sur les pages de documentation lues ni sur la page de licence : elle vient de la page de tarifs (fiche [open-meteo-archive](open-meteo-archive.md)). La page de licence, lue par la fiche [open-meteo-archive](open-meteo-archive.md), donne « API data are offered under Attribution 4.0 International (CC BY 4.0) » avec attribution et renvoi aux licences amont [producteur, lecture de cette autre fiche, non relue ici]. **La licence des prévisions archivées reste donc non confirmée pour chaque modèle** : la redistribution de séries Open-Meteo dans l'archive publique de PowAtlas n'est pas autorisée tant que chaque licence amont n'est pas lue (le cadrage SP0 le note aussi).

## Test d'accès

- Date : 2026-10-21, 16:10 à 17:00 UTC, sans compte ni clé.
- Commande exacte : `curl -sS "https://api.open-meteo.com/v1/forecast?latitude=45.1&longitude=6.4&hourly=snowfall,temperature_2m&models=meteofrance_arome_france_hd&forecast_days=2"` ; `curl -sS "https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=45.1&longitude=6.4&start_date=2026-10-01&end_date=2026-10-02&hourly=temperature_2m,snowfall&models=meteofrance_arome_france_hd"` ; `curl -sS "https://previous-runs-api.open-meteo.com/v1/forecast?latitude=45.1&longitude=6.4&hourly=temperature_2m,temperature_2m_previous_day1&models=ecmwf_ifs025&past_days=2&forecast_days=1"`.
- Taille téléchargée : environ 3 Ko.
- Résultat observé : Weather Forecast API : erreur TLS du proxy au premier essai ; Historical Forecast API : HTTP 429 `{"reason":"Daily API request limit exceeded. Please try again tomorrow.","error":true}` (quota partagé par adresse IP déjà consommé) ; Previous Runs API : HTTP 200, 2 287 octets de JSON [vérifié].

## Limites

- Offre gratuite réservée à un usage non commercial, 10 000 appels par jour : suffisant pour des contrôles ponctuels, pas pour un archivage quotidien de la grille entière.
- Historique composé des premières heures de chaque run, avec changements de version de modèle : inadapté à la vérification à 24-72 h ; Previous Runs limité à 7 jours d'avance.
- Licence des données archivées non confirmée par modèle ; dépendance à un tiers sans garantie de disponibilité.
- Les valeurs reprennent les biais de chaque modèle ; `snowfall` est un équivalent en eau converti à densité fixe, pas une mesure de neige fraîche (voir [open-meteo-archive](open-meteo-archive.md)).
- La sortie n'est pas un verdict de sécurité avalanche (référence : BRA Météo-France).

## Sources

- https://open-meteo.com/en/docs/historical-forecast-api — Historical Forecast API — consultée le 2026-10-21
- https://open-meteo.com/en/docs/previous-runs-api — Previous Runs API — consultée le 2026-10-21
- https://open-meteo.com/en/licence — licence (lue par la fiche open-meteo-archive) — consultée le 2026-10-21
- https://open-meteo.com/en/pricing — tarifs (lus par la fiche open-meteo-archive) — consultée le 2026-10-21
- https://historical-forecast-api.open-meteo.com/v1/forecast — point d'accès testé — consultée le 2026-10-21
- https://previous-runs-api.open-meteo.com/v1/forecast — point d'accès testé — consultée le 2026-10-21
