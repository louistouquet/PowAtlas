---
type: source
id: nivose
nom: Nivôse (stations automatiques de haute montagne de Météo-France)
producteur: Météo-France (Centre d'études de la neige pour le réseau)
licence: Licence Ouverte Etalab 2.0 (mention « Source : Météo-France »)
acces: HTTPS public sans compte, fichiers CSV compressés de la base climatologique sur meteo.data.gouv.fr (jeux horaires et quotidiens) ; API du portail Météo-France = compte gratuit requis
quotas: aucun quota documenté pour le téléchargement des fichiers ; quotas de l'API du portail non lus (compte requis)
delai: fichiers rafraîchis une fois par jour (Last-Modified constaté 08:53 UTC le 2026-10-21 pour une dernière heure de mesure à 05 UTC) ; délai maximal documenté : non documenté au 2026-10-21
resolution: ponctuelle (20 stations dans l'emprise) ; hauteur totale de neige horaire (NEIGETOT) et quotidienne à 06 UTC (NEIGETOT06) ; aucune neige fraîche mesurée
conservation: quotidien depuis 1982 pour la plus ancienne (Bellecôte), de 1996 à 2011 pour les autres de Savoie ; horaire : début non vérifié ; fichiers mis à jour quotidiennement
statut: retenue
verifie_le: 2026-10-21
---

# Nivôse (stations automatiques de haute montagne de Météo-France)

Chaque affirmation porte sa source et sa date de consultation (2026-10-21 pour toutes), et une marque : **[vérifié]** (constaté par nous), **[producteur]** (documentation officielle), **[tiers]** ou **[hypothèse]**. Observé, jamais modélisé.

## Contenu

- Description : réseau de stations automatiques de haute montagne, sur pylône de 5 à 7 m, installées en secteur inaccessible à l'observation humaine ; Météo-France en compte 29, entre 1 300 et 3 100 m [producteur] (https://meteofrance.com/meteo-a-z/comment-prevoit-on-les-avalanches) ; 19 dans les Alpes selon une liste nominative [tiers] (https://fr.wikipedia.org/wiki/Niv%C3%B4se_%28station_m%C3%A9t%C3%A9o%29).
- Capteurs : thermomètre, hygromètre, anémomètre, capteur de hauteur de neige [tiers, Wikipédia]. Pour Bellecôte (73071403, 2 992 m) la fiche de poste officielle liste un « Capteur hauteur de neige Campbell SR50A », un capteur à ultrasons [producteur] (https://donneespubliques.meteofrance.fr/metadonnees_publiques/fiches/fiche_73071403.pdf).
- Transmission : toutes les heures par satellite (Météosat, Iridium) ou GPRS [tiers, Wikipédia].
- Variables utiles à la neige, constatées dans les fichiers ouverts [vérifié] :
  - fichier horaire (`H_<dep>_latest-2025-2026.csv.gz`) : `NEIGETOT` (hauteur totale de neige au sol, cm) avec code qualité `QNEIGETOT`. Pour les 6 Nivôse de Savoie : 93 506 valeurs de qualité 1 (validée), 1 197 de qualité 9 (filtrée), 28 de qualité 0 (protégée) sur 2025-01-01 à 2026-10-21 05 UTC. Maxima constatés : 164 à 321 cm selon la station.
  - fichier quotidien (`Q_<dep>_latest-2025-2026_autres-parametres.csv.gz`) : `NEIGETOT06` (épaisseur totale à 06 h, cm) et `NEIGETOTX` (épaisseur maximale 01 h à 24 h, cm). Les deux sont renseignés presque tous les jours sur 2025-01-01 à 2026-10-19 (651 à 657 jours sur 657 selon la station).
  - Aucune hauteur de neige fraîche (`HNEIGEF` vide pour toutes les stations Nivôse), aucun équivalent en eau (`CHARGENEIGE` vide sur le fichier de Savoie). La neige fraîche est donc **à dériver** de la hauteur totale (voir la fiche [`reseau-nivo-meteo`](reseau-nivo-meteo.md) pour le test de dérivation).
- Couverture de l'emprise (ouest 5.0, sud 43.5, est 7.9, nord 46.5) : 20 stations dont le nom finit par « -NIVOSE », toutes dans l'emprise (contrôle sur LAT et LON) [vérifié] : Restefond (04), Parpaillon, La Meije, Col Agnel, Galibier, Orcières (05), Millefonts (06), Aigleton, Le Gua, Les Écrins, Saint-Hilaire, Col de Porte (38), Bonneval, Bellecôte, Grande Parei, Allant, Le Chevril, Les Rochilles (73), Aiguilles Rouges, Couvercle (74). Contrôle fait sur les départements 04, 05, 06, 38, 73 et 74.
- Profondeur d'archive : première valeur de `NEIGETOT06` du fichier quotidien 1950-2024 de Savoie : Bellecôte 1982-01-30, Les Rochilles 1982-02-07, Bonneval 1996-01-09, Le Chevril 1996-11-08, Allant 2008-10-07, Grande Parei 2011-10-11 [vérifié]. Les autres départements n'ont pas été contrôlés.
- Fréquence : horaire (une valeur par heure, 15 796 à 15 798 lignes par station pour 2025-01-01 à 2026-10-21) [vérifié].
- Formats : CSV compressé, séparateur point-virgule, en-tête de 206 colonnes (fichier horaire) [vérifié].
- Biais connus : capteur à ultrasons sur pylône, donc mesure d'un point unique ; la hauteur maximale mesurable est la hauteur du capteur moins environ 50 cm (Bellecôte, pylône de 7 m : environ 6,50 m) [tiers, Wikipédia]. Le capteur voit la neige tassée, le vent et la fonte modifient la hauteur sans chute : toute neige fraîche déduite est un indice, pas une mesure. Sites d'altitude, sans observateur, souvent exposés au vent [hypothèse].
- Observé ou modélisé : observé (capteur). La chaîne SAFRAN-Crocus-MEPRA (voir [`s2m`](s2m.md)) est modélisée et séparée.
- Documentation officielle : voir Sources.
- Licence : « Sans redevance sous Licence Ouverte d'Etalab. La source à indiquer est "Météo-France". » [producteur] (https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/pages/888143886/Observations+in+situ, consultée le 2026-10-21) ; les jeux de données climatologiques portent « lov2 » (Licence Ouverte 2.0) dans le catalogue data.gouv.fr [vérifié] (https://www.data.gouv.fr/api/1/datasets/6569b4473bedf2e7abad3b72/).

## Test d'accès

- Date : 2026-10-21, vers 15:50 UTC, sans compte, sans clé.
- Commande exacte :
  - `curl -sS -m 120 -o H73.gz https://meteofrance.s3.sbg.io.cloud.ovh.net/data/synchro_ftp/BASE/HOR/H_73_latest-2025-2026.csv.gz`
  - `curl -sS -m 90 -o Qp_73.gz https://meteofrance.s3.sbg.io.cloud.ovh.net/data/synchro_ftp/BASE/QUOT/Q_73_previous-1950-2024_autres-parametres.csv.gz`
  - `curl -sS -m 60 -o Qa_73.gz https://meteofrance.s3.sbg.io.cloud.ovh.net/data/synchro_ftp/BASE/QUOT/Q_73_latest-2025-2026_autres-parametres.csv.gz`, idem pour les départements 04, 05, 06, 38 et 74.
  - Lecture avec `python3 -I` (module `csv`, `gzip`).
  - `curl -sS -o - https://public-api.meteofrance.fr/public/DPObs/v1/liste-stations` (test de l'API du portail sans identifiant).
- Taille téléchargée : 18 578 666 octets (horaire Savoie) + 10 857 539 (quotidien Savoie 1950-2024) + environ 1,9 Mo (six fichiers quotidiens récents) ; environ 31 Mo, sous le plafond de 50 Mo.
- Résultat observé :
  - HTTP 200 sur tous les fichiers ; `Accept-Ranges: bytes` constaté sur `nivo_2026.csv.gz` (même stockage) ; plusieurs coupures de connexion (curl 35) du proxy du bac à sable sur d'autres hôtes, résolues par reprise.
  - Les six Nivôse de Savoie sont présentes dans le fichier horaire avec `NEIGETOT` ; dernière heure 2026-10-21 05 UTC (04 UTC pour Le Chevril) alors que le fichier portait Last-Modified 08:53 GMT.
  - L'API du portail sans identifiant répond HTTP 401, `{"code":"900902","message":"Missing Credentials"}` : un jeton est exigé, donc `compte gratuit requis` pour l'API.

## Limites

- Aucune neige fraîche mesurée ni équivalent en eau : seule la hauteur totale est fournie.
- Le jeu `Archive réseau nivo-météorologique` (fichiers `nivo_AAAA.csv.gz`, voir [`reseau-nivo-meteo`](reseau-nivo-meteo.md)) ne contient **aucune** de ces 20 stations : le nom du dossier (`OBS/NIVOSE`) est trompeur, les noms de stations ne comportent pas « NIVOSE » mais ceux de stations de ski et de pisteurs [vérifié sur nivo_2025.csv.gz, 108 stations].
- Le fichier d'une année ne contient que 2025-2026 ; l'historique plus ancien est dans d'autres fichiers par période, de tailles de 5 à 40 Mo chacun.
- Délai de mise à disposition de l'ordre de quelques heures à une journée (mise à jour quotidienne) ; pas de flux horaire continu sans l'API du portail (compte requis).
- Les graphiques publics de meteofrance.com ne sont pas des données réutilisables : seuls les fichiers ouverts le sont [hypothèse, aucune licence lue pour les graphiques].
- Capteur unique par site : pas d'estimation de la représentativité spatiale.

## Sources

- https://meteofrance.com/meteo-a-z/comment-prevoit-on-les-avalanches — consultée le 2026-10-21
- https://fr.wikipedia.org/wiki/Niv%C3%B4se_%28station_m%C3%A9t%C3%A9o%29 — consultée le 2026-10-21
- https://donneespubliques.meteofrance.fr/metadonnees_publiques/fiches/fiche_73071403.pdf — consultée le 2026-10-21
- https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/pages/888143886/Observations+in+situ — consultée le 2026-10-21
- https://www.data.gouv.fr/api/1/datasets/6569b4473bedf2e7abad3b72/ — consultée le 2026-10-21
- https://www.data.gouv.fr/api/1/datasets/6569b51ae64326786e4e8e1a/ — consultée le 2026-10-21
- https://meteofrance.s3.sbg.io.cloud.ovh.net/data/synchro_ftp/BASE/HOR/H_descriptif_champs.csv — consultée le 2026-10-21
- https://public-api.meteofrance.fr/public/DPObs/v1/liste-stations — consultée le 2026-10-21
