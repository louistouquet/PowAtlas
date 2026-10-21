---
type: source
id: skitour
nom: Skitour.fr (topo-guide et sorties de ski de randonnée)
producteur: Skitour (association de bénévoles, éditeur du site skitour.fr)
licence: CC BY-SA 4.0 (données collaboratives du topoguide) et CC BY-NC-ND 4.0 (données personnelles : textes et photos des sorties)
acces: pages de sorties lisibles sans compte ; API officielle = compte gratuit requis (clé « cle » à récupérer depuis le profil, une clé par application) ; aucune API testée
quotas: API : 1 000 transactions par 24 heures et 60 par minute, davantage sur demande [producteur]
delai: sorties publiées par les utilisateurs au fil de l'eau, souvent le jour même ou le lendemain ; délai non mesuré
resolution: ponctuelle (par sortie : massif, point de départ, date) ; texte libre de conditions ; pas de variable numérique de neige
conservation: archives de sorties depuis plusieurs années (numéros de sorties à 6 chiffres) ; profondeur exacte non documentée au 2026-10-21
statut: ecartee
verifie_le: 2026-10-21
---

# Skitour.fr (topo-guide et sorties de ski de randonnée)

Chaque affirmation porte sa source et sa date de consultation (2026-10-21 pour toutes), et une marque : **[vérifié]** (constaté par nous), **[producteur]** (documentation officielle), **[tiers]** ou **[hypothèse]**.

Statut `ecartee` comme vérité terrain quantitative : texte libre, déclaratif, licence non commerciale et sans dérivation pour les sorties, API sous clé.

## Contenu

- Description : site communautaire de ski de randonnée en France ; chaque sortie est un compte rendu (massif, départ, topos associés, orientation, dénivelé, cotation) et une rubrique « Conditions nivologiques, accès & météo » [vérifié sur la sortie 188738, consultée le 2026-10-21].
- Contenu de la rubrique de conditions, constaté sur un exemple : météo et températures, conditions d'accès, altitude de chaussage et déchaussage, « conditions pour le ski », « conditions nivo et activité avalancheuse » et une note de « skiabilité » ; exemple lu : « fonte généralisée », altitude de chaussage 2 400 m [vérifié]. Les valeurs de neige fraîche en centimètres ne sont pas un champ structuré (texte libre) [vérifié sur l'exemple ; autres sorties non lues].
- Variables utiles à la neige : aucune numérique ; indications qualitatives (qualité de neige, limite de la neige, signalement d'avalanches, de chutes récentes) dans le texte.
- Couverture de l'emprise (ouest 5.0, sud 43.5, est 7.9, nord 46.5) : massifs alpins (l'exemple lu concerne la Haute Maurienne, Alpes Grées Sud) ; nombre de sorties dans l'emprise non compté. Skitour couvre aussi les Pyrénées et d'autres massifs.
- Fréquence : continue, forte en saison ; irrégulière et biaisée vers les bonnes conditions et les week-ends (les skieurs sortent quand la neige est bonne) [hypothèse].
- Formats : HTML ; API JSON (`/api/massifs`, `/api/sommets`, `/api/departs`, `/api/refuges`, topos et sorties) [producteur] (https://skitour.fr/api/).
- Biais connus : déclaratif, subjectif, biais de sélection (jours et lieux), absence de mesure standardisée ; observation d'un lieu et d'une heure précis, souvent d'altitude moyenne à haute, sans quantité de neige fraîche comparable [hypothèse].
- Documentation officielle : voir Sources.
- Licence : « Les données sur skitour sont sous licence CC by-sa 4.0 (Données collaboratives du topoguide) et CC-by-nc-nd 4.0 (Données personnelles = sorties textes et photos). Vous pouvez les utiliser dans le respect de la licence, de façon brute ou compliée. Chaque page qui présente des données issues de l'API [...] doit fournir un lien vers la ressource liée sur skitour.fr [...] et citer l'auteur le cas échéant. L'utilisation de photos hors contexte est soumise à autorisation préalable de l'auteur. » ; « L'utilisation de l'API est ouverte à toutes les applications, qu'elles soient commerciales ou non. Une application = une clé. » [producteur] (https://skitour.fr/api/, consultée le 2026-10-21). La page de confidentialité confirme : contenu collaboratif en CC-by-sa 4.0 [producteur] (https://skitour.fr/confidentialite). Les sorties (CC BY-NC-ND) interdisent l'usage commercial et les œuvres dérivées : un jeu de données dérivé publié sous CC BY 4.0 par le projet n'est pas compatible [hypothèse d'interprétation, à confirmer en droit].

## Test d'accès

- Date : 2026-10-21, vers 16:50 UTC, sans compte.
- Commande exacte :
  - `curl -sS -m 30 -L https://skitour.fr/ -o sk.html`
  - `curl -sS -m 30 -L https://skitour.fr/api/ -o sk_api.html`
  - `curl -sS -m 30 -L https://skitour.fr/sorties/188738 -o sk_out.html`
  - `curl -sS -m 30 -L https://skitour.fr/confidentialite` et `https://skitour.fr/robots.txt`
- Taille téléchargée : environ 0,2 Mo (accueil 64 670 octets, API 25 070, sortie 43 874, confidentialité 17 076, robots 36).
- Résultat observé :
  - HTTP 200 sur toutes les pages publiques ; `robots.txt` : `User-agent: *` et `Disallow: /membres/` uniquement.
  - La page API précise que chaque requête doit porter l'en-tête `cle` obtenu depuis la modification du profil : **compte gratuit requis**, aucune clé créée, aucun appel d'API testé. Une clé d'exemple figure dans la documentation ; elle n'est ni utilisée ni recopiée.

## Limites

- Aucune variable numérique de neige fraîche : texte libre à interpréter ; extraction automatique non fiable.
- Licence des sorties (BY-NC-ND) incompatible avec une redistribution en données ouvertes CC BY 4.0 et avec les œuvres dérivées ; usage à titre de référence qualitative humaine seulement.
- Compte et clé requis pour l'API ; quotas de 1 000 requêtes par jour.
- Un moissonnage des pages est techniquement permis par `robots.txt` mais non encouragé par la page API ; non fait.
- À ne jamais présenter comme source de sécurité : mentions d'avalanches ou de conditions sont des témoignages, la référence est le BRA de Météo-France.

## Sources

- https://skitour.fr/api/ — consultée le 2026-10-21
- https://skitour.fr/confidentialite — consultée le 2026-10-21
- https://skitour.fr/sorties/188738 — consultée le 2026-10-21
- https://skitour.fr/robots.txt — consultée le 2026-10-21
- https://skitour.fr/ — consultée le 2026-10-21
