---
type: source
id: arpege
nom: ARPEGE 0,1° Europe et 0,25° monde, et PE-ARPEGE, Météo-France
producteur: Météo-France
licence: Licence Ouverte 2.0 (Etalab) ; attribution : source (nom du concédant) et date de dernière mise à jour
acces: HTTPS anonyme, sans compte ni clé ; bucket S3 public meteofrance-pnt (déterministe) et meteofrance-pe (ensemble) ; portail API non utilisé
quotas: aucune limite constatée ; limites du portail anonyme non documentées au 2026-10-21
delai: déterministe 2,9 à 5,6 h après l'heure du run (Last-Modified constaté) ; ensemble 3,2 à 6,5 h
resolution: 0,1° (grille EURAT01, 72N 20N 32W 42E) et 0,25° (GLOB025) ; 1 h jusqu'à 48 h puis 3 h ; 4 runs par jour (00, 06, 12, 18 UTC), échéances 0 à 102 h
conservation: déterministe 14 jours (plus ancien run constaté 2026-10-06 18 UTC) ; ensemble environ 2 jours (plus ancien run 2026-10-19 06 UTC)
statut: retenue
verifie_le: 2026-10-22
---

# ARPEGE (déterministe 0,1° et 0,25°) et PE-ARPEGE

Chaque affirmation porte sa source et sa date de consultation (2026-10-21), et une marque : **[vérifié]**, **[producteur]**, **[tiers]** ou **[hypothèse]**.

## Contenu

- Description : modèle global français ; jeux data.gouv.fr « Paquets Arpège - Résolution 0,1° » (EURAT01, 9 fichiers de 12 h par paquet : 00-12, 13-24, ..., 97-102 h) et « Résolution 0,25° » (GLOB025, 4 fichiers de 24 h : 00-24, 25-48, 49-72, 73-102 h) [producteur : métadonnées data.gouv.fr, licence `lov2`]. Ensemble PE-ARPEGE : un contrôle et 34 simulations, réseaux 0, 6, 12, 18, grilles EURAT01 0,1° et GLOB025 0,25° [producteur].
- Runs et échéances : 4 runs par jour ; jusqu'à 102 h ; dossier `arpege/` présent seulement aux runs 00, 06, 12, 18 UTC (les runs de 03, 09, 15, 21 UTC ne contiennent que `arome`) [vérifié, listings du 2026-10-19 au 2026-10-21].
- Variables utiles à la neige, lues dans les messages GRIB2 (`eccodes`) [vérifié] :
  - 0,1° SP1 (fichier 0-12 h, 325 messages, 77 Mo) : `2t`, humidité relative 2 m, `10u`, `10v`, rafales, `tp` (précipitation totale, cumul), `tsnowp` (neige, cumul), `tirf` (pluie, cumul), `csfwe` (neige convective, cumul), `lsfwe` (neige grande échelle, cumul), `sd` (équivalent en eau de la neige au sol, instantané), pression au niveau de la mer, nébulosité totale, rayonnement. SP2 : point de rosée 2 m, humidité spécifique, `sp`, T min et max 2 m, nébulosité basse, moyenne, haute, CAPE, hauteur de couche limite, flux ; HP1, HP2 : vent et point de rosée à des hauteurs de 20 à 50 m et plus ; IP1 : géopotentiel sur niveaux de pression, IP2 à IP4 non inspectés.
  - 0,25° SP1 à SP3 : mêmes grandeurs de surface (SP1 : `2t`, `2r`, vent 10 m, `tp`, `tsnowp`, pression mer ; SP3 : `csfwe`, `lsfwe`, `tsnowp`, `tirf`, flux, couches nuageuses, et d'autres paramètres non nommés).
  - Absents des paquets inspectés : isotherme 0 °C, limite pluie-neige, hauteur de neige en mètres, type de précipitation. `sd` (équivalent en eau) est présent à 0,1° SP1 [vérifié] ; IP2 à IP4 (0,1°) et IP, HP du 0,25° non inspectés.
- Couverture de l'emprise des Alpes françaises : entièrement dans EURAT01 (20 N à 72 N, 32 W à 42 E) ; 156 points (13 x 12) à 0,25° [vérifié sur GFS, même grille], environ 930 points à 0,1° [calcul].
- Formats : GRIB2, sans index [vérifié] ; ensemble : fichiers `.grib` d'environ 0,9 à 1,6 Go par échéance et par run (103 fichiers par run, 105 Go par run, grille EURAT01) [vérifié sur le listing de `meteofrance-pe`].
- Délai (Last-Modified, en heures après le run, premier au dernier fichier) [vérifié] : 0,1° run 00 UTC 2,9 à 3,6 ; run 06 UTC 3,7 à 4,3 ; 0,25° run 00 UTC 3,1 à 4,3 ; run 06 UTC 3,9 à 5,6. PE-ARPEGE EURAT01 : run 06 UTC 4,1 à 6,5, run 12 UTC du 2026-10-20 3,0 à 5,1.
- Conservation : déterministe 14 jours [vérifié et producteur, voir [arome](arome.md)] ; ensemble : 9 runs complets plus un run en cours dans `prod/data/arpege/eurat01/`, du 2026-10-19 06 UTC au 2026-10-21 12 UTC, soit un peu plus de 2 jours [vérifié].
- Actualité : « nouvelle grille 0,1° sur le globe pour l'API ARPEGE (2026-10-15) » et « anomalie des cumuls AROME et ARPEGE (2026-09-03) » listées sur l'accueil Confluence, textes non lus [producteur].
- Documentation officielle : voir Sources (description technique PDF inaccessible le 2026-10-21, site en maintenance).
- Licence : `lov2` dans les métadonnées de « Paquets Arpège » 0,1° et 0,25°, PE-ARPEGE GLOB025 et EURAT01 [producteur]. Conditions : voir [arome](arome.md) (paternité, date de mise à jour, pas de caution).

- **Paquets du run 00 UTC (inspection du 2026-10-22, run 2026-10-22 00 UTC)** [vérifié, listing S3 et lecture des en-têtes GRIB2 par plages d'octets, puis décodage `eccodes` d'un message par paramètre] :
  - `arpege/01/` contient `SP1`, `SP2`, `HP1`, `HP2`, `IP1` à `IP4` ; chaque paquet a 9 fichiers `arpege__01__<paquet>__<échéances>__<run>.grib2` (`000H012H`, ..., `085H096H`, `097H102H`), de 23 à 113 Mo ; dépôt de 02:54 à 03:30 UTC.
  - **`SP1` contient les 8 variables d'archivage** : `2t`, `10u`, `10v`, `tp` (0.1.52), `tsnowp` (0.1.66), `tirf` (0.1.65), `sd` (0.1.60, équivalent en eau de la neige au sol, kg m-2), `prmsl`, ainsi que `cp`, `lsp`, `csfwe`, `lsfwe`, rafales, `ssrd` et quelques paramètres locaux.
  - **Échéances du 0,1° : horaires de 0 à 102 h** pour les instantanés (et non « 1 h puis 3 h » comme écrit en R0.2 pour ce maillage) ; cumuls de 1 à 102 h ; `sd` horaire de 0 à 48 h, puis toutes les 3 h (51, 54, ..., 102).
  - Grille 0,1° : 741 x 521 points depuis 72 N et 328 E (32 W) ; messages de 0,02 à 0,47 Mo ; 312 messages dans le fichier `037H048H` de `SP1`.
## Test d'accès

- Complément du 2026-10-22 : `curl -sS "https://meteofrance-pnt.s3.rbx.io.cloud.ovh.net/?list-type=2&prefix=pnt/2026-10-22T00:00:00Z/arpege/01/SP1/"` (fichiers, tailles, dates de dépôt), puis lecture des en-têtes de chaque message par requêtes `Range` de 1 024 octets et décodage `eccodes` d'un message par paramètre (moins de 15 Mo lus). HTTP 206 sur toutes les plages.

- Date : 2026-10-21, 15:40 à 17:00 UTC, sans compte.
- Commande exacte : `curl -sS "https://meteofrance-pnt.s3.rbx.io.cloud.ovh.net/?list-type=2&prefix=pnt/2026-10-21T06:00:00Z/arpege/&max-keys=1000"` (74 fichiers 0,1° et 38 fichiers 0,25°, tailles et dates) ; `curl -sS "https://meteofrance-pe.s3.rbx.io.cloud.ovh.net/?list-type=2&prefix=prod/data/arpege/eurat01/&max-keys=1000"` (954 fichiers) ; lecture d'en-têtes par `Range: bytes=a-b` sur `arpege__01__SP1__000H012H`, `arpege__01__SP2__000H012H`, `arpege__025__SP1__000H024H`, `arpege__025__SP2__...`, `arpege__025__SP3__...` du run 06 UTC.
- Taille téléchargée : environ 1 Mo (listings et en-têtes de messages), aucun fichier entier.
- Résultat observé : HTTP 200 anonyme sur les listings et les lectures partielles ; 325 messages dans SP1 0,1° 0-12 h, 331 dans SP2, 344 dans SP1 0,25° 0-24 h, 459 dans SP2, 678 dans SP3 [vérifié].

## Limites

- Résolution de 0,1° (environ 11 km) : relief alpin lissé ; AROME est plus fin sur la France.
- Pas d'index : lecture sélective par parcours d'en-têtes ; fichiers de 77 Mo (0,1° SP1) à 450 Mo (0,25° SP3).
- PE-ARPEGE : 105 Go par run pour l'Europe entière, conservation de 2 jours, aucun découpage serveur : **écarté pour SP1** (volume de téléchargement) ; à réexaminer si un découpage ou une lecture sélective est qualifié.
- Contenus de IP2 à IP4 (0,1°) et des paquets 0,25° HP et IP non inspectés ; descriptions officielles inaccessibles le 2026-10-21.
- La sortie n'est pas un verdict de sécurité avalanche (référence : BRA Météo-France).

## Sources

- https://meteofrance-pnt.s3.rbx.io.cloud.ovh.net/ — bucket public des paquets PNT — consultée le 2026-10-21
- https://meteofrance-pe.s3.rbx.io.cloud.ovh.net/ — bucket public des ensembles — consultée le 2026-10-21
- https://www.data.gouv.fr/api/1/datasets/ (paquets-arpege-resolution-0-1deg, paquets-arpege-resolution-0-25deg, pe-arpege-eurat01, pe-arpege-glob025) — consultée le 2026-10-21
- https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/pages/621019138/Mod+les+et+donn+es+de+pr+vision — consultée le 2026-10-21
- https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/overview — consultée le 2026-10-21
