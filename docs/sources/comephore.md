---
type: source
id: comephore
nom: COMEPHORE (réanalyse horaire des lames d'eau radar et pluviomètres, France métropolitaine)
producteur: Météo-France
licence: Licence Ouverte v2.0 (identifiant `lov2` sur data.gouv.fr)
acces: HTTPS public sans compte : fichiers tar mensuels sur le stockage objet lié par data.gouv.fr (jeu « Réanalyses Coméphore »)
quotas: non documenté au 2026-10-21
delai: archive complétée chaque mois pour le mois N-2 (mois d'août 2026 déposé le 2026-09-23) ; fréquence de mise à jour déclarée mensuelle
resolution: 1 km x 1 km (grille 1536 x 1536, projection stéréographique polaire), pas de temps horaire
conservation: archive permanente depuis 1997-01-01 (356 tars mensuels de 1997-01 à 2026-08)
statut: retenue
verifie_le: 2026-10-21
---

# COMEPHORE

Chaque affirmation porte sa source (consultée le 2026-10-21) et une marque : **[vérifié]**, **[producteur]**, **[tiers]** ou **[hypothèse]**. COMEPHORE est une **estimation** (fusion radar et pluviomètres), pas une mesure directe de la pluie sur chaque pixel.

## Contenu

- Description : réanalyse horaire des précipitations par fusion des données des radars et des pluviomètres sur la France métropolitaine. [producteur] (data.gouv.fr, PDF descriptif)
- Variables : cumul de précipitations en 1/10 mm (`RR`), incertitude du cumul en 1/10 mm (`ERR`), code de qualification radar (`QUALIF`). [producteur] Valeur manquante 65535 (RR, ERR) et 255 (QUALIF). **Aucune variable de neige** : les précipitations sont totales, sans distinction pluie ou neige, ni équivalent en eau de neige. La phase se déduit d'une autre source (température, isotherme) [hypothèse].
- Couverture temporelle : 1997-01-01 à 2026-08 (dernier tar `H_COMEPHORE_202608`, 231 331 840 octets, déposé le 2026-09-23) [vérifié par l'API data.gouv.fr] ; `temporal_coverage` du jeu : 1997-01-01 à 2026-09-23 [vérifié].
- Couverture de l'emprise (ouest 5.0, sud 43.5, est 7.9, nord 46.5) : France métropolitaine entière, Alpes françaises comprises ; coin nord-ouest de la grille à 53,670 N, -9,965 E, 1 pixel = 1 km. [producteur] Environ 230 x 330 km utiles, soit environ 3 % des pixels [hypothèse, calcul].
- Qualité radar : avant 2007, `QUALIF` indique la disponibilité du radar (0 à 3) ; depuis 2007, c'est le code qualité radar de 0 à 100 des lames d'eau 5 minutes. [producteur] En montagne, la couverture radar est limitée par le relief : non documenté dans ce qui a été lu, à vérifier par `QUALIF` sur l'emprise [hypothèse].
- Fréquence : 1 fichier par heure, date de fin de cumul en UTC (nom du fichier et étiquette `TIFFTAG_DATETIME`). [producteur]
- Formats : GeoTIFF, entiers non signés sur 2 octets (RR, ERR) ou 1 octet (QUALIF), tar mensuels contenant `AAAA/AAAAMMJJHH_RR.gtif`, `_ERR.gtif`, `_QUALIF.gtif`. [producteur] Constaté sur le tar d'août 2026 : 3 fichiers par heure ; `RR` d'une heure de 23 634 octets compressés ; en-têtes TIFF 1536 x 1536, 16 bits, `TIFFTAG_SOFTWARE` = COMEPHORE, date 2026:08:01 01:00:00 [vérifié].
- Volume : somme des tailles des 356 tars : 72,85 Go pour toute la France (environ 0,2 Go par mois) [vérifié par l'API data.gouv.fr]. Pas de découpage côté serveur : un tar mensuel est un fichier de 0,2 Go ; sur l'emprise, environ 3 % de pixels, soit environ 2 à 3 Go après découpage si la compression est proportionnelle [hypothèse, calcul].
- Documentation officielle : PDF « Réanalyse des lames d'eau COMEPHORE » ; page Météo-France https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/ (non lue ici).
- Licence : champ `license: lov2` sur la fiche data.gouv.fr (API `https://www.data.gouv.fr/api/2/datasets/reanalyses-comephore/`), `access_type: open` [vérifié, lu le 2026-10-21]. L'API `https://www.data.gouv.fr/api/1/datasets/licenses/` donne pour `lov2` le titre « Licence Ouverte / Open Licence version 2.0 » (https://www.etalab.gouv.fr/licence-ouverte-open-licence) [vérifié, lu le 2026-10-21]. Attribution de la source Météo-France à prévoir.

## Test d'accès

- Date : 2026-10-21, vers 15:44 UTC, sans compte.
- Commande exacte : `curl -sS -I https://meteofrance.s3.sbg.io.cloud.ovh.net/data/synchro_ftp/REANALYSES/COMEPHORE/H_COMEPHORE_202608.tar` (HTTP 200, `Content-Length: 231331840`, `Accept-Ranges: bytes`) puis `curl -sS -r 0-3000000 -o part.tar <même URL>` (HTTP 206, 3 000 001 octets), `tar -tvf part.tar` et extraction de `2026/2026080101_RR.gtif`. Liste des 357 ressources : `curl -sS "https://www.data.gouv.fr/api/2/datasets/reanalyses-comephore/resources/?page_size=100&page=1"` (pages 1 à 4).
- Taille téléchargée : environ 3,4 Mo (3 Mo du tar, 0,4 Mo de listes JSON) et un PDF de 283 842 octets.
- Résultat observé : accès anonyme et lecture par plages d'octets confirmés [vérifié]. Les URL data.gouv.fr ont été instables depuis la session (code 000 ou `Connection reset by peer` à plusieurs reprises, y compris pour l'API des licences, lue ensuite par l'outil de lecture web). Plusieurs requêtes vers `www.data.gouv.fr` ont été coupées (`Connection reset by peer`) par le proxy du sandbox puis ont abouti à la répétition : prévoir des reprises.

## Limites

- Précipitations seulement : pas de neige, pas de phase, pas de température.
- Un utilisateur a signalé un « changement de coordonnées à partir d'août 2024 » (fil de discussion data.gouv.fr clos le 2026-01-30, contenu des réponses non affiché) : la stabilité de la grille avant et après août 2024 n'est pas vérifiée. Lire ce fil et comparer les en-têtes GeoTIFF de 2024-07 et 2024-08 avant tout empilement de séries [non résolu].
- Projection stéréographique polaire : le producteur recommande GDAL et ne répond pas aux questions de géodésie fines (fil du 2026-09-02).
- Produit à ne pas confondre avec une mesure : en montagne, la qualité radar est limitée (QUALIF à examiner), et la fusion avec les pluviomètres dépend de la densité du réseau [hypothèse].
- Retard N-2 : inutilisable pour la vérification récente ; adapté à l'archive et à la vérification de saisons passées.
- Pas de verdict de sécurité avalanche : référence BRA Météo-France.

## Sources

- https://www.data.gouv.fr/datasets/reanalyses-comephore/ — jeu de données Réanalyses Coméphore — consultée le 2026-10-21
- https://www.data.gouv.fr/api/2/datasets/reanalyses-comephore/ — API data.gouv.fr (licence, couverture) — consultée le 2026-10-21
- https://static.data.gouv.fr/resources/reanalyses-comephore/20260909-150531/radar-donnees-comephore-descriptif-20250604.pdf — descriptif Météo-France — consultée le 2026-10-21
- https://meteofrance.s3.sbg.io.cloud.ovh.net/data/synchro_ftp/REANALYSES/COMEPHORE/H_COMEPHORE_202608.tar — tar mensuel testé — consultée le 2026-10-21
- https://www.data.gouv.fr/api/1/datasets/licenses/ — liste des licences data.gouv.fr (`lov2`) — consultée le 2026-10-21
- https://www.data.gouv.fr/datasets/reanalyses-comephore/discussions — discussions — consultée le 2026-10-21
