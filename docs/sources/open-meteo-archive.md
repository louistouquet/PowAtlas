---
type: source
id: open-meteo-archive
nom: Open-Meteo Historical Weather API (ERA5, ERA5-Land, CERRA, IFS)
producteur: Open-Meteo.com (agrège des données ECMWF et Copernicus)
licence: données de l'API sous CC BY 4.0 selon la page de licence ; usage de l'API gratuit réservé au non commercial ; amont (Copernicus) sous ses propres termes
acces: HTTPS public sans compte ni clé pour l'API gratuite (`archive-api.open-meteo.com`) ; accès réel obtenu une fois par la relecture (HTTP 200), puis limite journalière partagée atteinte (HTTP 429) lors de mes essais
quotas: 600 appels par minute, 5 000 par heure, 10 000 par jour, 300 000 par mois (page de tarifs, offre gratuite non commerciale incluant l'API historique)
delai: non documenté au 2026-10-21 (suit ERA5, environ 5 jours pour ERA5T)
resolution: ERA5 0,25 degré, ERA5-Land 0,1 degré, CERRA 5 km, IFS 9 km ; horaire
conservation: non documenté au 2026-10-21
statut: a-tester
verifie_le: 2026-10-21
---

# Open-Meteo Historical Weather API

Chaque affirmation porte sa source (consultée le 2026-10-21) et une marque : **[vérifié]**, **[producteur]**, **[tiers]** ou **[hypothèse]**. Les données servies sont des réanalyses **modélisées**.

## Contenu

- Description : interface JSON qui sert ERA5, ERA5-Land, ECMWF IFS (depuis 2017) et CERRA par point, sans fichier GRIB. [producteur] (page de documentation)
- Couverture temporelle : ERA5 1940 à aujourd'hui, ERA5-Land 1950 à aujourd'hui, IFS 2017 à aujourd'hui, CERRA 1985 à juin 2021. [producteur] (la période CERRA contredit le catalogue CDS, voir [cerra](cerra.md))
- Variables neige : chute de neige (`snowfall`, en cm) pour ERA5, CERRA, IFS ; hauteur de neige (`snow_depth`, en m) pour ERA5-Land et CERRA, pas ERA5 ni IFS ; la page avertit : « Snow depth in ERA5-Land tends to be overestimated ». [producteur] Conversion citée mot pour mot : « For the water equivalent in millimeter, divide by 7. E.g. 7 cm snow = 10 mm precipitation water equivalent. » **La règle (diviser par 7) et l'exemple (7 cm = 10 mm) se contredisent** ; seul l'exemple est cohérent avec une densité fixe de 100 kg/m3 : mm = cm x 10/7 [hypothèse fondée sur l'exemple]. La chute de neige en cm est donc une conversion à densité fixe d'un équivalent en eau modélisé, pas une mesure de hauteur de neige fraîche.
- Couverture de l'emprise : globale ; requêtes par point, donc une requête par point de grille ou par site d'intérêt.
- Formats : JSON (CSV et autres selon la documentation, non testés).
- Volume : non applicable (requêtes par points).
- Documentation officielle : https://open-meteo.com/en/docs/historical-weather-api.
- Licence : « API data are offered under Attribution 4.0 International (CC BY 4.0) » ; attribution obligatoire avec lien vers open-meteo.com ; les sources amont ont leurs propres licences (Copernicus : voir [era5](era5.md), clause 5.1) [producteur, lu le 2026-10-21]. Page de tarifs : la colonne « Free / Open-Access API » est cochée pour « Historical Weather API » ; l'API gratuite est « for non-commercial use, rate-limited to 10,000 calls/day, and carries no uptime guarantee » [producteur]. La FAQ qui dit que les API historique, climat, ensemble et rayonnement satellite demandent l'offre Professionnelle vise les offres payantes (« Standard » contre « Professional ») et ne contredit pas la colonne gratuite [producteur, lecture de la relecture ; la page n'est pas sans ambiguïté]. La page ne dit pas si un projet open source relève du « non commercial » : à lire dans les conditions d'utilisation.

## Test d'accès

- Date : 2026-10-21, vers 15:50 UTC.
- Commande exacte : `curl -sS "https://archive-api.open-meteo.com/v1/archive?latitude=45.9&longitude=6.9&start_date=2023-12-01&end_date=2023-12-02&hourly=snowfall,snow_depth,temperature_2m&models=era5_land"`.
- Taille téléchargée : 86 octets.
- Résultat observé : mes deux essais ont rendu HTTP 429 `{"reason":"Daily API request limit exceeded. Please try again tomorrow.","error":true}` [vérifié] (le premier précédé d'une erreur TLS du proxy). Une relecture indépendante a rejoué la commande et obtenu HTTP 200 (JSON, altitude de maille 2492 m, `snowfall` en cm, `snow_depth` en m) puis 429 [rapporté par la relecture, non reproduit par moi] : quota partagé et intermittent. L'altitude de maille (2492 m pour un point à 45,9 N 6,9 E) est utile : elle permet de mesurer l'écart d'altitude entre la maille et un site.

## Limites

- Quota quotidien de 10 000 appels par IP et réglage non commercial : un entraînement par point de grille sur 40 ans consomme vite le quota ; à réserver à des essais.
- Quota partagé et intermittent (voir Test d'accès) ; dépend d'un tiers sans garantie de disponibilité ; ne remplace pas une copie locale.
- Les valeurs sont celles d'ERA5, ERA5-Land et CERRA ; elles héritent de leurs biais en montagne.
- Pas de verdict de sécurité avalanche : référence BRA Météo-France.

## Sources

- https://open-meteo.com/en/docs/historical-weather-api — documentation de l'API d'archive — consultée le 2026-10-21
- https://open-meteo.com/en/licence — licence — consultée le 2026-10-21
- https://open-meteo.com/en/pricing — tarifs et limites — consultée le 2026-10-21
- https://archive-api.open-meteo.com/v1/archive — point d'accès testé — consultée le 2026-10-21
