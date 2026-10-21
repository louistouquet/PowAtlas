---
type: source
id: camptocamp
nom: Camptocamp.org (topoguide collaboratif, sorties et conditions)
producteur: Camptocamp-Association (association de contributeurs bénévoles)
licence: CC BY-SA (contenu collaboratif) ; CC BY-NC-ND (contenu individuel : sorties, textes et photos) ; code de l'API sous AGPL v3
acces: API REST publique sans compte ni clé (https://api.camptocamp.org/outings, JSON), aucun quota documenté
quotas: non documentés au 2026-10-21 ; aucun refus sur une trentaine de requêtes à cadence modérée
delai: sorties publiées par les contributeurs, parfois le jour même (sortie du 2026-10-20 présente le 2026-10-21) ; délai médian non mesuré
resolution: ponctuelle (une sortie par ligne, avec géométrie) ; champs structurés qualitatifs de conditions et texte libre
conservation: archive complète depuis la création du site (identifiants de sorties à 7 chiffres) ; profondeur exacte non documentée
statut: ecartee
verifie_le: 2026-10-21
---

# Camptocamp.org (topoguide collaboratif, sorties et conditions)

Chaque affirmation porte sa source et sa date de consultation (2026-10-21 pour toutes), et une marque : **[vérifié]** (constaté par nous), **[producteur]** (documentation officielle), **[tiers]** ou **[hypothèse]**.

Statut `ecartee` comme vérité terrain quantitative : champs qualitatifs, déclaratifs, licence non commerciale et sans dérivation pour les sorties.

## Contenu

- Description : topoguide collaboratif de sports de montagne ; documents de type itinéraires, points de passage, sorties, rapports d'incident ; l'API V6 est publique (dépôt `c2corg/v6_api`, AGPL v3) [producteur] (https://www.camptocamp.org/articles/838875 et https://github.com/c2corg/v6_api).
- Champs structurés d'une sortie, constatés sur l'API [vérifié] : `date_start`, `date_end`, `activities` (par exemple `skitouring`, `hiking`), `condition_rating`, `snow_quantity`, `snow_quality`, `elevation_up_snow`, `elevation_down_snow`, `elevation_min`, `elevation_max`, `access_condition`, `lift_status`, `hut_status`, `areas` (massif, département, pays), `geometry`. Les textes `conditions`, `conditions_levels` et `weather` sont dans `locales`.
  - `snow_quantity` et `snow_quality` sont des valeurs ordinales (`excellent`, `good`, `average`, `poor`) : la quantité de neige **présente** ou la qualité, pas la neige fraîche en cm. La définition exacte de chaque niveau n'a pas été lue [non documenté ici].
- Remplissage sur un échantillon de 30 sorties de ski de randonnée de mars 2026 dans l'emprise [vérifié] : `snow_quantity` renseigné pour 23 sur 30, `snow_quality` pour 21 sur 30, une limite de neige (`elevation_up_snow` ou `elevation_down_snow`) pour 16 sur 30, texte de conditions pour 24 sur 30. Échantillon petit, indicatif seulement.
- Couverture de l'emprise (ouest 5.0, sud 43.5, est 7.9, nord 46.5) : requête `bbox=556597,5388389,879424,5860840` (EPSG:3857 de l'emprise) avec `act=skitouring` [vérifié] : 787 sorties de ski de randonnée en mars 2026 et 2 692 entre le 1er décembre 2025 et le 30 avril 2026, soit environ 25 sorties par jour en mars et 18 par jour sur l'hiver (calcul : 787 sur 31 jours, 2 692 sur 151 jours).
- Fréquence : continue, concentrée en saison et aux week-ends [hypothèse].
- Formats : JSON (API), GeoJSON pour la géométrie ; filtres `bbox`, `date=AAAA-MM-JJ,AAAA-MM-JJ`, `act=`, `limit`, `offset`, `u=` [vérifié sur les appels, producteur pour la liste].
- Biais connus : déclaratif, qualitatif, biais de sélection (les sorties ont lieu quand la neige est bonne), observation en un point et un instant ; aucune quantité de neige fraîche ; plusieurs langues [hypothèse et vérifié pour les champs].
- Documentation officielle : voir Sources.
- Licence : « Le contenu collaboratif texte et image est sous licence CC by-sa. Le contenu collaboratif coordonnées géographiques est sous double licence CC by-sa et Open Database Licence. Le contenu individuel texte, image et coordonnées géographiques est sous licence CC-by-nc-nd. » ; les sorties sont du contenu **individuel** (CC by-nc-nd) ; « la licence CC-by-nc-nd n'autorise pas l'utilisation commerciale » ; mention requise : nom du contributeur, lien vers le document source, nom et lien de la licence [producteur] (https://www.camptocamp.org/articles/106728/fr/licences-des-contenus, consultée le 2026-10-21). La même page précise que « les licences ne s'appliquent qu'à la mise en forme d'une information (texte ou image), mais pas à l'information elle-même. La copie d'une information est toujours autorisée (nom et altitude d'un sommet, quantité de neige, dénivelé, cotation, ...) » [producteur] : lecture favorable à la réutilisation de valeurs factuelles, mais il s'agit d'une position de l'association et non d'un avis juridique [hypothèse]. Le site ne publie pas de licence spécifique pour l'accès API ; le code de l'API est sous AGPL v3.

## Test d'accès

- Date : 2026-10-21, entre 16:40 et 17:10 UTC, sans compte, sans clé.
- Commande exacte :
  - `curl -sS -m 30 "https://api.camptocamp.org/outings?limit=1"`
  - `curl -sS -m 30 "https://api.camptocamp.org/outings?limit=3&date=2026-03-01,2026-03-31&bbox=556597,5388389,879424,5860840&act=skitouring" -o c2c3.json`
  - `curl -sS -m 30 "https://api.camptocamp.org/outings/1961745" -o c2o.json` (détail d'une sortie), puis 30 détails de sorties de mars 2026 par `urllib.request` (cadence de 5 par seconde au plus).
  - `curl -sS https://www.camptocamp.org/robots.txt`
- Taille téléchargée : environ 3 Mo (détail de sortie 75 015 octets × 31 environ, listes).
- Résultat observé :
  - HTTP 200 JSON sans authentification ; `total` 235 521 sorties pour une première requête avec une boîte voisine de l'emprise (EPSG:3857, 500000,5300000,880000,5800000), toutes dates et activités ; 787 en mars 2026 dans l'emprise pour le ski de randonnée.
  - `robots.txt` bloque certains robots de SEO et les pages d'utilisateur connecté, pas l'API.
  - L'identifiant 1 de sortie répond HTTP 404.

## Limites

- Licence des sorties CC BY-NC-ND : ni usage commercial ni œuvres dérivées ; redistribuer des sorties dans une archive ouverte CC BY 4.0 n'est pas permis ; seule une lecture humaine ou un usage interne de contrôle est sûr [hypothèse d'interprétation].
- Aucune neige fraîche en cm ; variables ordinales et texte libre.
- Biais de sélection et de déclaration ; couverture du Briançonnais et du Dauphiné, non évaluée ici.
- Vérification manuelle requise : la page `licences-des-contenus` n'a pas pu être relue par robot (contenu vide à la lecture automatique répétée) et `github.com/c2corg/v6_api` répond 403 à la lecture automatique ; les citations de licence ci-dessus viennent d'un résultat de recherche à relire à la main avant toute réutilisation.
- Nuance de la page de licences : « La copie d'une information est toujours autorisée (… quantité de neige …) » ; c'est la position de l'association, pas un avis juridique [hypothèse d'interprétation] ; l'exclusion de la vérité terrain reste justifiée par la nature ordinale et déclarative des champs.
- Pas de garantie de continuité de l'API (service bénévole) ; cadence modérée à respecter.
- À ne jamais présenter comme source de sécurité : les conditions sont des témoignages ; la référence est le BRA de Météo-France.

## Sources

- https://www.camptocamp.org/articles/106728/fr/licences-des-contenus — consultée le 2026-10-21
- https://www.camptocamp.org/articles/838875 — consultée le 2026-10-21
- https://github.com/c2corg/v6_api — consultée le 2026-10-21
- https://api.camptocamp.org/outings — consultée le 2026-10-21
- https://www.camptocamp.org/robots.txt — consultée le 2026-10-21
