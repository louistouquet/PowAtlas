---
type: source
id: arome-pi
nom: AROME Prévision Immédiate (AROME-PI), Météo-France
producteur: Météo-France
licence: Licence Ouverte 2.0 (Etalab) attendue, non lue pour ce jeu précis ; à confirmer à l'ouverture du compte
acces: compte gratuit requis (portail API Météo-France, portail-api.meteofrance.fr) ; non créé, test d'accès arrêté
quotas: non documentés au 2026-10-21 (non lus : portail non lisible sans compte)
delai: « 30 minutes après chaque heure » [producteur : page Confluence]
resolution: 0,01° et 0,025° ; pas de 15 minutes ; échéances 0 à 360 minutes ; un run par heure (24 par jour)
conservation: non documentée au 2026-10-21
statut: a-tester
verifie_le: 2026-10-21
---

# AROME Prévision Immédiate (AROME-PI)

Chaque affirmation porte sa source et sa date de consultation (2026-10-21), et une marque : **[vérifié]**, **[producteur]**, **[tiers]** ou **[hypothèse]**.

## Contenu

- Description : prévision à très courte échéance d'AROME, 24 runs par jour (0 à 23 UTC), pas de 15 minutes de 0 à 360 minutes, grilles 0,01° et 0,025°, GRIB2 ; disponible 30 minutes après chaque heure [producteur : page Confluence « Modèles et données de prévision », consultée le 2026-10-21]. Un forum d'utilisateurs la décrit comme une extension d'AROME mise à jour toutes les heures [tiers].
- Variables utiles à la neige : non lues (accès par compte). La présence de neige ou de phase de précipitation dans les paquets AROME-PI n'est pas confirmée au 2026-10-21 [hypothèse : champs proches de ceux des paquets AROME, voir [arome](arome.md)].
- Couverture de l'emprise des Alpes françaises (ouest 5.0, sud 43.5, est 7.9, nord 46.5) : non vérifiée ; la grille 0,01° d'AROME France couvre 12 W à 16 E, 37,5 N à 55,4 N [producteur pour la grille AROME, non confirmée pour AROME-PI].
- Fréquence, échéances : voir en-tête.
- Formats : GRIB2 [producteur].
- Documentation officielle : https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/pages/621019138/Mod+les+et+donn+es+de+pr+vision (consultée le 2026-10-21).
- Licence : non lue pour ce jeu. Les jeux AROME et ARPEGE du même producteur sont sous Licence Ouverte 2.0 (voir [arome](arome.md)) ; la présence d'AROME-PI sur data.gouv.fr n'a pas été trouvée par l'API de recherche (aucun résultat pour « arome pi » le 2026-10-21) [vérifié].

## Test d'accès

- Date : 2026-10-21.
- Commande exacte : `curl -sS -I https://portail-api.meteofrance.fr/` : HTTP 302 (redirection vers le portail applicatif) [vérifié] ; la recherche `https://www.data.gouv.fr/api/1/datasets/?q=arome+pi&page_size=10` rend 0 résultat [vérifié] ; le bucket public `meteofrance-pnt` (voir [arome](arome.md)) liste `arome`, `aromeifs`, `arpege`, `arome-om`, `phealth`, `vague-surcote` : pas d'AROME-PI [vérifié].
- Taille téléchargée : environ 1 Ko.
- Résultat observé : aucun accès anonyme à AROME-PI trouvé. Des outils tiers indiquent qu'il faut s'inscrire gratuitement sur le portail puis s'abonner à l'API « Arome Instantané », avec clé d'API, jeton d'une heure ou identifiant d'application [tiers, recherche web, non vérifié par un compte].

## Limites

- `compte gratuit requis (portail API Météo-France)` : le test s'arrête ; la création du compte relève du pilote (cadrage SP0, section 10).
- Rétention, quotas, contenu des paquets, licence du jeu : non documentés au 2026-10-21.
- Intérêt probable pour l'alerte à quelques heures, pas pour l'archive de prévision à 24-72 h ; non prioritaire pour SP1 [hypothèse].
- La sortie n'est pas un verdict de sécurité avalanche (référence : BRA Météo-France).

## Sources

- https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/pages/621019138/Mod+les+et+donn+es+de+pr+vision — consultée le 2026-10-21
- https://portail-api.meteofrance.fr/ — portail API (redirection, compte requis) — consultée le 2026-10-21
- https://www.data.gouv.fr/api/1/datasets/?q=arome+pi — recherche de jeux — consultée le 2026-10-21
- Recherche web « Météo-France API portail AROME-PI clé API compte gratuit » (outils tiers : meteofrance-publicapi, meteole) — consultée le 2026-10-21
