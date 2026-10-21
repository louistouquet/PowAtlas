---
type: source
id: slf-imis
nom: Réseau IMIS et parcelles d'étude du SLF (Suisse)
producteur: WSL Institut pour l'étude de la neige et des avalanches SLF (Davos)
licence: CC BY 4.0 (Creative Commons Attribution 4.0), lien visible vers www.slf.ch obligatoire
acces: API REST publique sans compte ni clé (https://measurement-api.slf.ch, 7 jours au plus) ; archive par fichiers sur https://measurement-data.slf.ch (index de fichiers public, sans compte constaté)
quotas: aucun quota chiffré documenté ; interdiction d'un usage pouvant altérer l'infrastructure du SLF ; inscription à une liste de diffusion recommandée pour les données en direct
delai: mesures toutes les 30 minutes (délai de publication non mesuré) ; valeurs journalières à 06 UTC du jour J déjà présentes dans l'API à 16:30 UTC le 2026-10-21
resolution: ponctuelle ; 50 stations IMIS dans l'emprise (29 de neige à terrain plat, 18 de vent, 2 de transport de neige, 1 de pente neigeuse) et 16 parcelles d'étude manuelles
conservation: API : 1, 3 ou 7 jours seulement ; archive : 1992 à 2024 (jeu EnviDat), fichiers au-delà de 7 jours sur le portail de fichiers
statut: retenue
verifie_le: 2026-10-21
---

# Réseau IMIS et parcelles d'étude du SLF (Suisse)

Chaque affirmation porte sa source et sa date de consultation (2026-10-21 pour toutes), et une marque : **[vérifié]** (constaté par nous), **[producteur]** (documentation officielle), **[tiers]** ou **[hypothèse]**.

## Contenu

- Description : IMIS (Intercantonal Measurement and Information System) compte près de 200 stations automatiques dans les Alpes suisses et le Jura, la plupart au-dessus de la limite des arbres (2 000 à 3 000 m), qui enregistrent en général toutes les 30 minutes [producteur] (https://www.envidat.ch, jeu DOI 10.16904/envidat.406). L'API liste 208 stations (206 CH, 2 LI) : 128 de neige à terrain plat, 67 de vent, 7 de transport de neige, 6 de pente [vérifié].
- Stations de neige : sur terrain plat à l'abri du vent ; les stations de vent sont sur crêtes ou sommets [producteur, EnviDat].
- **Mesuré ou modélisé** (point central) [producteur] (https://measurement-data.slf.ch/README.md) [vérifié sur l'API et le README] :
  - `HS` : hauteur de neige, épaisseur totale instantanée (cm) ; sur le fichier journalier : médiane des dernières 24 h à 06 UTC. **Mesurée.**
  - `HN_1D` : hauteur de neige nouvelle des 24 dernières heures (cm) « modeled by SNOWPACK at 6 UTC ». **Modélisée** (modèle SNOWPACK appliqué à la hauteur mesurée), à ne pas présenter comme observation.
  - Parcelles d'étude manuelles (`study-plot`) : `HS`, `HN_1D` et `HNW_1D` (équivalent en eau de la neige nouvelle des dernières 24 h, mm) ; il s'agit de mesures manuelles, donc **observées** [producteur, README ; nature manuelle déduite de « Measurements from manual study plots »]. **Non testé** : `study-plot/measurements` ne renvoyait qu'une station, hors emprise, le 2026-10-21 (saison non commencée) ; à retester en saison.
  - Autres variables des stations IMIS : température de l'air, humidité, vent moyen et rafale, température de surface et de la neige (sol, 25, 50, 100 cm), rayonnement ondes courtes réfléchi ; précipitations par pluviomètre non chauffé, **inutilisable à basse température en hiver** [producteur, README].
- Couverture de l'emprise (ouest 5.0, sud 43.5, est 7.9, nord 46.5) [vérifié] : 50 stations IMIS (Valais, Vaud, Berne, Fribourg ; 29 neige, 18 vent, 2 transport de neige, 1 pente) et 16 parcelles d'étude (Zermatt, Arolla, Morgins, Leysin...). Dans le fichier journalier sur 7 jours : 232 valeurs pour 29 stations de l'emprise, dont 8 `HN_1D` vides.
- Fréquence : 30 min (IMIS), journalière à 06 UTC (journalier et parcelles), événementielle pour les précipitations (60 min sans précipitation) [producteur].
- Formats : JSON (API, OpenAPI 1.1.0 en ReDoc), CSV (`daily_snow.csv`, `<station>_pluvio.csv`, par station) sur le portail de fichiers [vérifié].
- Biais connus : stations à plus de 2 000 m en moyenne, hors stations de ski ; `HN_1D` des stations IMIS est modélisé (README du producteur). Observation du 2026-10-21 : `HS` = 0 cm avec `HN_1D` = 10,3 cm (ANV2), 8,4 (ANV3), 8,6 (ARO3) ; ce n'est **pas** une preuve d'incohérence, `HS` du fichier journalier étant la médiane des dernières 24 h, et on ne retient que le caractère modélisé établi par le README [vérifié]. Le mode de mesure du capteur de hauteur n'est pas précisé dans les sources lues [non documenté au 2026-10-21].
- Documentation officielle : voir Sources.
- Licence : « The data is subject to the licence CC BY 4.0 » ; « there must be a clearly visible reference to the data source », pour un produit numérique un lien vers www.slf.ch ; publications scientifiques : citer le DOI https://doi.org/10.16904/envidat.406 ; « The data that can be obtained through the channels mentioned on this page are free of charge » ; aucune restriction d'usage commercial ou de redistribution sur la page ; « By obtaining the data, the client accepts the terms of use on this page » [producteur] (https://www.slf.ch/en/services-and-products/slf-data-service, consultée le 2026-10-21, lue par l'outil de lecture de page, non en HTML brut). La fiche EnviDat affiche pour le jeu « Other (Specified in the description) » et renvoie vers ces conditions [vérifié].

## Test d'accès

- Date : 2026-10-21, entre 16:00 et 16:30 UTC, sans compte, sans clé.
- Commande exacte :
  - `curl -sS -m 30 https://measurement-api.slf.ch/public/api/imis/stations -o slf_st.json`
  - `curl -sS -m 30 https://measurement-api.slf.ch/public/api/imis/station/AMD2/measurements`
  - `curl -sS -m 40 "https://measurement-api.slf.ch/public/api/imis/daily-snow?period_in_days=7" -o ds7.json`
  - `curl -sS -m 30 https://measurement-api.slf.ch/public/api/study-plot/stations -o sp.json`
  - `curl -sS -m 30 https://measurement-api.slf.ch/openapi.json -o slf_openapi.json`
  - `curl -sS -m 30 "https://measurement-api.slf.ch/public/api/imis/station/ZER2/measurements?period_in_days=400"` (test de la profondeur : renvoie HTTP 422, la période refusée ; seules 1, 3 ou 7 sont autorisées, par exemple `period_in_days=7`)
  - `curl -sS -m 30 https://measurement-data.slf.ch/README.md`, puis `https://measurement-data.slf.ch/imis/` et `/imis/data/`.
- Taille téléchargée : environ 0,3 Mo au total (stations 31 504 octets, journalier 7 jours 84 759 octets, une station 16 246 octets, README 5 332 octets).
- Résultat observé :
  - HTTP 200 sans authentification sur toutes les routes de lecture ; JSON.
  - Le paramètre `period_in_days` n'accepte que 1, 3 ou 7 : HTTP 422 `Input should be 1, 3 or 7` pour 30, 365 et 400. L'API ne sert donc **pas** d'archive ; l'historique se prend sur le portail de fichiers.
  - Le portail de fichiers (`h5ai`) liste `/imis/`, `/study-plot/` et `README.md` en accès libre ; `/imis/data/` propose `by_station/` et `daily_snow_values/`. Le contenu des fichiers n'a pas été téléchargé (taille non mesurée).
  - Un test sur 7 jours : 1 033 lignes pour tout le réseau, 232 pour l'emprise (29 stations), dates 2026-10-14 à 2026-10-21.

## Limites

- API limitée à 7 jours : archiver chaque jour (même logique que les prévisions) ; historique 1992-2024 via les fichiers (EnviDat) et le portail, volume non mesuré ici.
- `HN_1D` des stations IMIS est **modélisé** ; la neige fraîche **observée** de référence viendrait des parcelles d'étude manuelles (16 dans l'emprise, mesure quotidienne selon le producteur, **non testées** en dehors de la saison) ; ne pas mélanger.
- Stations en Suisse, rive est/sud du Valais surtout, pas dans les massifs français : utile pour les Alpes du Nord frontalières (Mont-Blanc, Chablais), pas pour Vercors ou Écrins.
- Stations en altitude, exposées : la hauteur reflète un site précis ; absence d'équivalent en eau automatique de la neige fraîche.
- Données du dernier jour provisoires (non validées) [hypothèse : l'API ne précise pas le niveau de validation].
- Aucun compte créé ; l'inscription à la liste de diffusion (data@slf.ch) n'a pas été faite : contact extérieur interdit par le mandat.

## Sources

- https://measurement-api.slf.ch/ — consultée le 2026-10-21
- https://measurement-api.slf.ch/openapi.json — consultée le 2026-10-21
- https://measurement-api.slf.ch/public/api/imis/stations — consultée le 2026-10-21
- https://measurement-api.slf.ch/public/api/imis/daily-snow?period_in_days=7 — consultée le 2026-10-21
- https://measurement-data.slf.ch/README.md — consultée le 2026-10-21
- https://www.slf.ch/en/services-and-products/slf-data-service — consultée le 2026-10-21
- https://www.envidat.ch/api/action/package_search?q=doi:10.16904/envidat.406&rows=1 — consultée le 2026-10-21
