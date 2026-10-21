---
type: source
id: hauteurs-stations-ski
nom: Hauteurs de neige déclarées par les stations de ski (bulletins d'enneigement)
producteur: stations de sports d'hiver, diffusées par l'ANMSM, des prestataires (Lumiplan, Skiplan) et des agrégateurs tiers
licence: aucune licence ouverte lue au 2026-10-21 (ANMSM : diffusion sur demande d'abonnement, conditions générales non lues ; agrégateurs tiers : aucune licence publiée)
acces: pas d'accès ouvert constaté ; abonnement par formulaire auprès de l'ANMSM (non rempli) ; agrégateur tiers open-piste sans clé mais sans licence
quotas: non documentés au 2026-10-21
delai: bulletins mis à jour par les stations, souvent quotidiens ; agrégateur tiers open-piste : 4 collectes par jour (4, 7, 13 et 20 h UTC)
resolution: ponctuelle, par station (hauteur « bas » et « sommet » de domaine skiable) ; neige fraîche déclarée avec date
conservation: non documentée au 2026-10-21 ; open-piste publie des exports Parquet quotidiens depuis une date non documentée (exemple constaté : 2026-03-24)
statut: ecartee
verifie_le: 2026-10-21
---

# Hauteurs de neige déclarées par les stations de ski (bulletins d'enneigement)

Chaque affirmation porte sa source et sa date de consultation (2026-10-21 pour toutes), et une marque : **[vérifié]** (constaté par nous), **[producteur]** (documentation officielle), **[tiers]** ou **[hypothèse]**.

Statut `ecartee` pour la vérité terrain : aucune licence de réutilisation lue, mesure déclarative sans protocole commun publié. Le canal ouvert et sûr pour les observations de stations de ski est le réseau nivo-météo de Météo-France ([`reseau-nivo-meteo`](reseau-nivo-meteo.md)), où ces stations (Courchevel, Flaine, Tignes...) fournissent déjà leurs mesures sous Licence Ouverte 2.0.

## Contenu

- Description : hauteurs de neige (en bas et en haut du domaine), neige fraîche et qualité de neige publiées par chaque station dans son bulletin. Observé (déclaratif), jamais modélisé.
- Qui les publie :
  - ANMSM (Association nationale des maires des stations de montagne) : « gère et distribue » le bulletin neige (état d'enneigement, indices pour la pratique de la glisse), saisi par chaque station « dans le respect de la Charte de qualité des données neige », agrégé et transmis à « plus d'une centaine » de partenaires ; la distribution « à titre gracieux » passe par un formulaire de demande d'abonnement qui donne des identifiants de syndication ; les conditions générales sont à demander par courriel [producteur] (https://www.anmsm.fr/publicationsdata/donn-es-des-stations).
  - Prestataires techniques (Lumiplan, Skiplan) dont le flux alimente des agrégateurs [tiers] (https://www.hauteurdeneige.com/sources-et-licences.html).
  - Agrégateurs tiers : `open-piste` (API JSON et exports Parquet sans clé, 148 stations dont environ 103 dans les Alpes) [tiers] (https://open-piste.raed.workers.dev/) ; `hauteurdeneige.com` (bulletins reçus des stations ; cite aussi les données Météo-France sous Licence Ouverte 2.0) [tiers].
- Variables utiles à la neige constatées dans `open-piste` pour une station (Val Thorens) : `base_snow_depth_cm`, `summit_snow_depth_cm`, `base_fresh_snow_cm`, `base_fresh_snow_date`, `summit_fresh_snow_cm`, `summit_fresh_snow_date`, `avalanche_risk` (valeur reprise du BRA, jamais un verdict du projet) [vérifié]. Période de mesure de la neige fraîche : non documentée au 2026-10-21.
- Couverture de l'emprise (ouest 5.0, sud 43.5, est 7.9, nord 46.5) : environ 103 stations alpines annoncées par `open-piste` [tiers], nombre exact dans l'emprise non compté.
- Fréquence : 4 collectes par jour pour `open-piste` (4, 7, 13, 20 h UTC) [tiers, page de l'agrégateur].
- Formats : JSON (API), Parquet (exports quotidiens).
- Biais connus : déclaratif ; peut être orienté commercial (les stations ont intérêt à annoncer de la neige) ; altitude et site de la mesure non standardisés ; bulletins « recopiés hors saison » à écarter (constaté par un agrégateur) ; neige fraîche avec période variable [tiers et hypothèse].
- Documentation officielle : voir Sources.
- Licence : aucune lue. `open-piste` ne publie aucune licence dans sa description OpenAPI (`info` : titre, version 0.1.0, description) ni sur sa page [vérifié] ; le jeu est un moissonnage de bulletins de stations, donc la réutilisation dépend des droits de chaque station [hypothèse]. ANMSM : « Conditions Générales d'Utilisation » non publiées sur la page lue. Une page publique n'est pas une licence.

## Test d'accès

- Date : 2026-10-21, vers 16:20 UTC, sans compte, sans clé.
- Commande exacte :
  - `curl -sS -m 30 https://open-piste.raed.workers.dev/health`
  - `curl -sS -m 30 https://open-piste.raed.workers.dev/openapi.json -o op.json`
  - `curl -sS -m 30 https://open-piste.raed.workers.dev/resorts/val-thorens -o vt.json`
  - Lecture de la page ANMSM et de la page `hauteurdeneige.com/sources-et-licences.html` (recherche web).
- Taille téléchargée : environ 9 Ko au total (OpenAPI 7 693 octets, station 913 octets, health environ 200 octets).
- Résultat observé :
  - `/health` : HTTP 200, `{"status":"ok","resorts":148,...,"lastSuccessfulScrape":"2026-10-21T14:02:18Z"}` ; données météo pour 147 stations.
  - Pour Val Thorens, tous les champs de neige fraîche sont `null` (hors saison, 0 cm de neige au sol) ; aucun champ de licence ni de source par station.
  - Formulaire de l'ANMSM non rempli (contact extérieur interdit par le mandat) : accès par abonnement, `compte gratuit requis` assimilé (identifiants de syndication).

## Limites

- Aucune licence de réutilisation : le projet ne peut pas redistribuer ces valeurs dans son archive ouverte (CC-BY-4.0) sans accord. À ne pas utiliser comme vérité terrain.
- Mesure non vérifiée ni homogénéisée ; le biais commercial n'est pas quantifié.
- Archive historique : non documentée ; les exports `open-piste` existent depuis une date inconnue.
- Le jeu data.gouv.fr « Hauteur de neige » (SIG-GR) est un service WMS du Luxembourg (licence `notspecified`), sans rapport avec les Alpes françaises [vérifié].
- Un moissonnage de pages de stations par le projet serait soumis aux conditions de chaque site : non évalué, non recommandé.

## Sources

- https://www.anmsm.fr/publicationsdata/donn-es-des-stations — consultée le 2026-10-21
- https://www.hauteurdeneige.com/sources-et-licences.html — consultée le 2026-10-21
- https://open-piste.raed.workers.dev/ — consultée le 2026-10-21
- https://open-piste.raed.workers.dev/openapi.json — consultée le 2026-10-21
- https://www.data.gouv.fr/api/1/datasets/686bc1784627187cf5cf7c45/ — consultée le 2026-10-21
