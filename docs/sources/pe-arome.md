---
type: source
id: pe-arome
nom: PE-AROME (ensemble AROME), Météo-France
producteur: Météo-France
licence: Licence Ouverte 2.0 (Etalab) pour le jeu public Nouvelle-Calédonie (métadonnées `lov2`) ; métropole non lue
acces: métropole : compte gratuit requis (portail API Météo-France), non créé ; seul PE-AROME Nouvelle-Calédonie est en accès anonyme (bucket S3 public meteofrance-pe)
quotas: non documentés au 2026-10-21
delai: Nouvelle-Calédonie : environ 6 h après l'heure du run (Last-Modified) ; métropole non constaté
resolution: 0,025° ; contrôle plus 24 membres perturbés (25 scénarios) ; échéances horaires jusqu'à 51 h ; réseaux 03, 09, 15, 21 UTC (« 6-hourly, from 03 UTC ») pour la métropole
conservation: Nouvelle-Calédonie : plus de 2 jours (48 fichiers par run constatés) ; métropole non documentée
statut: a-tester
verifie_le: 2026-10-21
---

# PE-AROME (ensemble AROME)

Chaque affirmation porte sa source et sa date de consultation (2026-10-21), et une marque : **[vérifié]**, **[producteur]**, **[tiers]** ou **[hypothèse]**.

## Contenu

- Description : prévision d'ensemble d'AROME : un membre de contrôle et 24 perturbés pour la métropole, horaire jusqu'à H+51, 0,025°, GRIB2, réseaux toutes les 6 h à partir de 03 UTC [producteur : page Confluence « Modèles et données de prévision », consultée le 2026-10-21]. Jeu data.gouv.fr « PE Arome NCALED0025 » : « un membre de contrôle et un ensemble de 15 simulations », réseaux 6 et 18 UTC, grille NCALED0025, 0,025° [producteur : métadonnées data.gouv.fr].
- Variables utiles à la neige : non lues pour la métropole. Un fichier du jeu Nouvelle-Calédonie pèse 505 à 652 Mo par échéance (membres et champs groupés) [vérifié sur la liste du jeu] ; contenu non inspecté (hors zone d'intérêt).
- Couverture de l'emprise des Alpes françaises : sans objet pour la Nouvelle-Calédonie ; le bucket public `meteofrance-pe` ne contient que `prod/data/arome/ncaled0025/` pour AROME (listing du 2026-10-21) et `prod/data/arpege/{eurat01,glob025}/` : **aucun PE-AROME métropolitain en accès anonyme** [vérifié].
- Fréquence, échéances : voir en-tête.
- Formats : GRIB [vérifié sur les noms de fichiers `.grib`].
- Documentation officielle : voir Sources.
- Licence : `lov2` pour le jeu Nouvelle-Calédonie [producteur] ; pour la métropole, non lue.

## Test d'accès

- Date : 2026-10-21.
- Commande exacte : `curl -sS "https://meteofrance-pe.s3.rbx.io.cloud.ovh.net/?list-type=2&delimiter=/&prefix=prod/data/arome/"` : HTTP 200, un seul préfixe `ncaled0025/` ; `curl -sS "https://meteofrance-pe.s3.rbx.io.cloud.ovh.net/?list-type=2&delimiter=/&prefix=prod/data/arpege/"` : `eurat01/`, `glob025/`.
- Taille téléchargée : environ 3 Ko (listings XML).
- Résultat observé : accès anonyme aux listings ; aucun dossier métropole ; aucun fichier téléchargé.

## Limites

- `compte gratuit requis (portail API Météo-France)` pour l'ensemble métropolitain, par analogie avec AROME-PI et selon la page Confluence qui cite deux portails (portail API et meteo.data.gouv) [hypothèse : mode d'accès non lu directement] ; le test s'arrête.
- Volume : à raison de 25 membres et de centaines de Mo par échéance sur la zone entière, un run complet se compte en dizaines de Go de téléchargement ; sans découpage serveur, c'est hors de portée d'un job gratuit [hypothèse, extrapolée de la Nouvelle-Calédonie].
- Non retenue pour SP1 tant que l'accès métropolitain n'est pas confirmé par un compte ouvert par le pilote ; l'ensemble d'ECMWF (voir [ecmwf-open-data](ecmwf-open-data.md)) fournit la dimension probabiliste en attendant.
- La sortie n'est pas un verdict de sécurité avalanche (référence : BRA Météo-France).

## Sources

- https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/pages/621019138/Mod+les+et+donn+es+de+pr+vision — consultée le 2026-10-21
- https://www.data.gouv.fr/api/1/datasets/ (pe-arome-ncaled0025) — consultée le 2026-10-21
- https://meteofrance-pe.s3.rbx.io.cloud.ovh.net/ — bucket public des ensembles — consultée le 2026-10-21
