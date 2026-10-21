---
type: source
id: arome
nom: AROME France 0,01° et 0,025° (et AROME IFS 0,025°), paquets Météo-France
producteur: Météo-France
licence: Licence Ouverte 2.0 (Etalab) ; attribution : source (nom du concédant) et date de dernière mise à jour
acces: HTTPS anonyme, sans compte ni clé ; bucket S3 public meteofrance-pnt (OVH) listable et lisible, alias files.data.gouv.fr/meteofrance-pnt (redirection 302) ; accès par le portail API Météo-France non utilisé (compte gratuit requis, non créé)
quotas: aucune limite constatée sur plusieurs centaines de requêtes de plage de 400 octets ; limites du portail anonyme non documentées au 2026-10-21
delai: 1,8 à 5,6 h après l'heure du run selon le run et le paquet (Last-Modified constaté) ; AROME IFS : 6,6 à 7,5 h
resolution: 0,01° (grille EURW1S100, 2801 x 1791 points) et 0,025° (EURW1S40) ; pas de temps horaire ; 8 runs par jour, échéances 0 à 51 h
conservation: 14 jours (plus ancien run constaté : 2026-10-06 18 UTC le 2026-10-21)
statut: retenue
verifie_le: 2026-10-21
---

# AROME France 0,01° et 0,025° (paquets Météo-France)

Chaque affirmation porte sa source et sa date de consultation (2026-10-21 pour toutes), et une marque : **[vérifié]** (constaté par nous), **[producteur]** (documentation officielle), **[tiers]** ou **[hypothèse]**.

## Contenu

- Description : modèle atmosphérique français à aire limitée (maille 1,3 km) ; paquets GRIB2 regroupant des paramètres par thème (SP surface, HP hauteur, IP niveaux isobares). Jeux data.gouv.fr « Paquets Arome - Résolution 0,01° » (grille EURW1S100, 55,4N 37,5N 12W 16E, un fichier par heure d'échéance) et « Résolution 0,025° » (EURW1S40, fichiers de 6 h : 00-06, 07-12, ..., 49-51) ; licence `lov2` dans les métadonnées [producteur : API data.gouv.fr, consultée le 2026-10-21]. Variante « Paquets Arome IFS 0,025° » : AROME initialisé par l'IFS de l'ECMWF [producteur].
- Runs et échéances : 8 runs par jour (00, 03, 06, 09, 12, 15, 18, 21 UTC), chacun jusqu'à 51 h ; 52 fichiers horaires pour le 0,01°, 9 fichiers de 6 h pour le 0,025° [vérifié, listings S3 des runs du 2026-10-21]. AROME IFS : 4 runs (00, 06, 12, 18 UTC), 9 fichiers de 6 h [vérifié].
- Variables utiles à la neige, lues dans les messages GRIB2 (ranges d'octets de 400 octets, puis `eccodes`) [vérifié] :
  - 0,01°, SP2 (9 champs, 19,3 Mo par heure) : `tsnowp` (chute de neige totale, cumul, kg m-2), `tirf` (pluie, cumul), `tgrp` (graupel, cumul), `sp`, nébulosité basse, moyenne, haute, CAPE, un champ non nommé (catégorie 16, numéro 193). SP1 (6 champs, 23,2 Mo) : `2t`, `2r`, `10u`, `10v`, rafales U et V. SP3 : 1 champ (catégorie 5, numéro 7, 3,9 Mo). HP1 : vent et humidité à 10, 20, 50 et 100 m (71,9 Mo par heure).
  - 0,025°, SP1 (97 messages sur 0 à 6 h) : `2t`, `2r`, `10u`, `10v`, vitesse et direction du vent à 10 m, rafales, `tp` (précipitation totale, cumul), `tsnowp` (neige, cumul), `tgrp` (graupel, cumul), pression au niveau de la mer, nébulosité totale, rayonnement descendant courtes longueurs d'onde (cumul). SP2 : `tirf` (pluie, cumul), humidité spécifique et point de rosée à 2 m, `sp`, T min et max 2 m, CAPE, hauteur de couche limite, flux. SP3 : flux de surface. HP1 à HP3 : vent, humidité, point de rosée, réflectivité à des hauteurs de 10 à 3000 m. IP1 à IP5 : température, humidité, vent U et V, géopotentiel sur 24 niveaux de pression (10 000 à 100 000 Pa par 2 500 Pa), plus vorticité, hydrométéores.
  - Absents des paquets lus : isotherme 0 °C, limite pluie-neige, hauteur de neige, équivalent en eau du manteau, type de précipitation [vérifié sur SP1 à SP3, HP2, HP3, IP1 à IP5 du 0,025° et SP1 à SP3, HP1 du 0,01° ; HP1 du 0,025° lu sur ses 300 premiers messages seulement]. La phase est donnée par les cumuls séparés `tsnowp`, `tirf`, `tgrp` ; l'isotherme 0 °C est à dériver de `t` et `gh` sur niveaux isobares (traitement du projet, [hypothèse]).
  - Les cumuls n'existent qu'à partir de +1 h [tiers : jeu de données Hugging Face tiers cité par la recherche web, non relu].
- Couverture de l'emprise des Alpes françaises (ouest 5.0, sud 43.5, est 7.9, nord 46.5) : entièrement dans la grille (12 W à 16 E, 37,5 N à 55,4 N) ; découpage mesuré : 300 x 290 points = 87 000 points à 0,01° (348 000 octets par champ en float32), environ 14 000 points à 0,025° [vérifié pour 0,01°, calcul pour 0,025°]. Le découpage est à faire côté client (pas de découpage serveur).
- Formats : GRIB2, un message par champ et par échéance, **sans fichier d'index** (seuls des `.grib2` dans le listing) [vérifié] : la lecture sélective impose de parcourir les en-têtes de messages par plages d'octets (Section 0 : longueur du message) ou de télécharger le paquet entier.
- Délai : Last-Modified, en heures après l'heure du run, du premier au dernier fichier [vérifié] : run 00 UTC 1,95 à 2,9 (une exception IP1 à 5,6) ; run 03 UTC 1,8 à 2,8 ; run 06 UTC 4,2 à 5,6 ; run 09 UTC 3,4 à 4,3. AROME IFS : run 00 UTC 6,8 à 7,5 ; run 06 UTC 6,6 à 7,4. Les valeurs varient d'un run à l'autre : prévoir une marge jusqu'à 6 h (8 h pour AROME IFS).
- Conservation : 14 jours. Constat : le listing `pnt/` contenait 119 préfixes de runs, du 2026-10-06 18:00 UTC au 2026-10-21 12:00 UTC [vérifié] ; jeu data.gouv.fr « Données PNT - rétention 14 jours » : « Les paquets de données des Prévisions Numériques du Temps sont archivés 14 jours » [producteur].
- Taille des paquets, un run entier (somme S3) : 0,01° SP1 1,17 Go, SP2 1,03 Go, SP3 0,20 Go, HP1 3,7 Go ; 0,025° SP1 0,47 Go, SP2 0,37 Go, SP3 0,51 Go, HP1 6,0 Go, HP2 4,8 Go, IP1 3,8 Go, IP2 1,5 Go, IP3 6,0 Go, IP4 0,6 Go, IP5 1,2 Go [vérifié].
- Documentation officielle : page Confluence « Modèles et données de prévision » (résolutions, formats ; ne donne ni noms de paquets, ni paramètres, ni délais) ; descriptions techniques en PDF sur donneespubliques.meteofrance.fr, inaccessibles le 2026-10-21 (page de maintenance, connexions réinitialisées) : le contenu des paquets ci-dessus vient donc de la lecture des fichiers, pas du PDF. Actualités Confluence citées : anomalie des cumuls AROME et ARPEGE (2026-09-03) et nouvelles ressources AROME IFS (2026-07-08), texte non lu [producteur].
- Licence : métadonnées data.gouv.fr `license: lov2` (« Licence Ouverte / Open Licence version 2.0 ») pour les jeux 0,01°, 0,025° et AROME IFS [producteur]. Texte (https://github.com/etalab/licence-ouverte/blob/master/LO.md, consulté le 2026-10-21) : réutilisation libre, y compris commerciale, adaptation et redistribution, « sous réserve de : mentionner la paternité de l'Information : sa source (a minima le nom du Concédant) et la date de la dernière mise à jour de l'Information réutilisée » ; la mention ne doit pas suggérer une caution du concédant [producteur].

## Test d'accès

- Date : 2026-10-21, entre 15:40 et 17:00 UTC, sans compte.
- Commandes exactes (extraits) :
  - `curl -sS "https://meteofrance-pnt.s3.rbx.io.cloud.ovh.net/?list-type=2&delimiter=/&prefix=pnt/&max-keys=1000"` (liste des runs) puis le même appel avec `prefix=pnt/2026-10-21T09:00:00Z/arome/` (liste des fichiers, tailles, dates).
  - `curl -sS -I "https://meteofrance-pnt.s3.rbx.io.cloud.ovh.net/pnt/2026-10-21T09:00:00Z/arome/001/SP2/arome__001__SP2__01H__2026-10-21T09:00:00Z.grib2"` : HTTP 200, `Content-Length: 19308098`, `Accept-Ranges: bytes`.
  - Téléchargement complet de `.../arome/001/SP1/arome__001__SP1__01H__2026-10-21T09:00:00Z.grib2` (23 239 186 o) et `.../001/SP3/...` (3 878 478 o), puis `.../001/SP2/...` (19 308 098 o) ; lecture avec `eccodes` 2.50.0.
  - Lecture des en-têtes de messages par `Range: bytes=a-b` (400 octets) sur les fichiers 0,025° SP1, SP2, SP3, HP1 à HP3, IP1 à IP5 du run 09 UTC (aucun fichier entier).
  - `curl -sS -I "https://files.data.gouv.fr/meteofrance-pnt/pnt/2026-10-21T09:00:00Z/arome/001/SP2/arome__001__SP2__01H__2026-10-21T09:00:00Z.grib2"` : HTTP 302 vers le bucket ci-dessus.
- Taille téléchargée : 46,4 Mo en deux séries (26,1 Mo puis 19,3 Mo) plus quelques Mo de plages d'en-têtes et de listings XML (0,4 Mo pour le listing complet).
- Résultat observé : HTTP 200, listings XML S3 (`ListBucketResult`) accessibles anonymement ; grille 2801 x 1791, 0,01°, premier point 55,4 N 348,0 E (12 W), dernier 37,5 N 16,0 E ; run `dataDate 20261021 dataTime 900`, échéance 1 ; SP1 = 6 messages, SP2 = 9, SP3 = 1 ; les connexions vers `www.data.gouv.fr` sont réinitialisées par intermittence à travers le proxy du sandbox (lors du contrôle des liens, les URL de l'API `www.data.gouv.fr/api/1/...` ont été injoignables : code 000 après 3 essais ; les métadonnées citées ont été lues pendant la session après plusieurs essais), le bucket S3 non [vérifié].

## Limites

- Aucun découpage ni index côté serveur : la lecture de quelques champs exige de parcourir des fichiers de 20 Mo (0,01°, un par heure) ou de 50 à 800 Mo (0,025°, par bloc de 6 h) ; le coût est en nombre de requêtes de plage, non testé à l'échelle d'un run.
- Pas d'isotherme 0 °C ni de limite pluie-neige ni de hauteur de neige dans les paquets lus ; phase de précipitation par cumuls séparés.
- Délais variables (1,8 à 5,6 h) et un run (06 UTC) nettement plus tardif que les autres le 2026-10-21 ; un incident de cumuls annoncé le 2026-09-03 (texte non lu).
- Conservation de 14 jours seulement : pas d'historique ; hors archive d'Open-Meteo (voir [open-meteo](open-meteo.md)), qui reconstitue des séries à partir des premières heures de chaque run, pas des runs complets.
- Le contenu exact des paquets n'est pas confirmé par la documentation officielle (PDF inaccessible) : relire le PDF quand le site rouvre.
- La sortie n'est pas un verdict de sécurité avalanche (référence : BRA Météo-France).

## Sources

- https://meteofrance-pnt.s3.rbx.io.cloud.ovh.net/ — bucket public des paquets PNT — consultée le 2026-10-21
- https://www.data.gouv.fr/api/1/datasets/ (paquets-arome-resolution-0-01deg, paquets-arome-resolution-0-025deg, paquets-arome-ifs-resolution-0-025deg, donnees-pnt-retention-14-jours) — métadonnées, licence, rétention — consultée le 2026-10-21
- https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/pages/621019138/Mod+les+et+donn+es+de+pr+vision — modèles et données de prévision — consultée le 2026-10-21
- https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/overview — page d'accueil de l'espace Open Data Météo-France — consultée le 2026-10-21
- https://github.com/etalab/licence-ouverte/blob/master/LO.md — texte de la Licence Ouverte 2.0 — consultée le 2026-10-21
- https://donneespubliques.meteofrance.fr/client/document/descriptiontechnique_paquetsarome_donneespubliques_v2_20240402_367.pdf — description technique des paquets AROME (inaccessible : maintenance) — consultée le 2026-10-21
- https://files.data.gouv.fr/meteofrance-pnt/pnt/ — alias du bucket — consultée le 2026-10-21
