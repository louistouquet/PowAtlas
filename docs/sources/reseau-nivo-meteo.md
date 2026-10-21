---
type: source
id: reseau-nivo-meteo
nom: Archive du réseau nivo-météorologique (stations de ski et postes de montagne, Météo-France)
producteur: Météo-France, avec les stations de sports d'hiver partenaires conventionnées
licence: Licence Ouverte 2.0 (Etalab), source à indiquer « Météo-France »
acces: HTTPS public sans compte, fichiers annuels nivo_AAAA.csv.gz sur meteofrance.s3.sbg.io.cloud.ovh.net, catalogue sur meteo.data.gouv.fr et data.gouv.fr ; API du portail Météo-France = compte gratuit requis
quotas: aucun quota documenté pour les fichiers ; quotas de l'API du portail non lus (compte requis)
delai: fichier de l'année en cours mis à jour une fois par jour (Last-Modified 06:30 UTC le 2026-10-21) ; délai médian entre la mesure et son insertion constaté à 1,4 h (90 % sous 4,4 h) sur le fichier 2026
resolution: ponctuelle, 79 à 81 stations dans l'emprise ; en pratique une observation par station et par jour, surtout entre 06 et 09 UTC ; neige fraîche (ssfrai) en m, hauteur totale (ht_neige) en m
conservation: archive annuelle depuis 1996 (31 fichiers, de nivo_1996 à nivo_2026), mise à jour quotidienne de l'année en cours
statut: retenue
verifie_le: 2026-10-21
---

# Archive du réseau nivo-météorologique (stations de ski et postes de montagne, Météo-France)

Chaque affirmation porte sa source et sa date de consultation (2026-10-21 pour toutes), et une marque : **[vérifié]** (constaté par nous), **[producteur]** (documentation officielle), **[tiers]** ou **[hypothèse]**.

**Conclusion sur le point du cadrage : l'accès ouvert aux données du réseau nivo-météo est confirmé.** Le jeu est publié sans compte, sous Licence Ouverte 2.0, avec un téléchargement testé le 2026-10-21 (voir Test d'accès). Voir le rapport [R0.3](../research/R0.3-observations.md).

## Contenu

- Description : observations « issues des stations de montagne opérées par les partenaires conventionnés avec Météo-France pour la surveillance du manteau neigeux en période hivernale » [producteur] (https://www.data.gouv.fr/api/1/datasets/68aeced879316c333d564f95/, champ description). Les pisteurs des stations fournissent des observations deux fois par jour (température, vent, couverture nuageuse, précipitations, hauteur et qualité de la neige, transport de neige, avalanches) et un profil détaillé du manteau une fois par semaine [producteur] (https://meteofrance.com/meteo-a-z/comment-prevoit-on-les-avalanches). Le réseau compte 146 stations entre 800 et 3 200 m (Alpes, Corse, Pyrénées) [producteur, même page]. Fréquence annoncée : « 12 h » [producteur] (page Confluence « Observations in situ »).
- Variables utiles à la neige (descriptif technique officiel, colonnes réelles identiques) [producteur] [vérifié] :
  - `ssfrai` : hauteur de la neige fraîche, m ; `perssfrai` : période de mesure de la neige fraîche, annoncée en 1/10 d'heure ; `neige_fraiche` : hauteur de neige fraîche, m (second champ, voir Limites) ;
  - `ht_neige` : hauteur totale de la couche de neige, glace, autre, au sol, m ; `ht_neige_alti` : hauteur de neige en altitude, m ;
  - `rr24` : précipitations des 24 dernières heures, mm ; `t`, `tn12`, `tx12`, `tn24`, `tx24` (K) ; `ff`, `dd` (vent) ; `ww`, `w1`, `w2` (temps présent et passé) ;
  - `teneur_eau` (teneur en eau liquide), `m_vol_neige` (masse volumique, kg/m3), `grain_*`, `etat_neige`, `prof_sonde`, `chasse_neige`, `aval_*` (avalanche observée ; c'est une observation du pisteur, pas un verdict de sécurité : référence = BRA de Météo-France).
- Mesure : `ssfrai` est une mesure manuelle sur planche à neige à l'observation du matin, `ht_neige` une mesure manuelle (sonde) ; pas d'équivalent en eau de la neige fraîche mesuré directement : seul `m_vol_neige` (densité) est parfois fourni [hypothèse sur la méthode, d'après le descriptif des champs ; protocole de pisteur non lu].
- Couverture de l'emprise (ouest 5.0, sud 43.5, est 7.9, nord 46.5) [vérifié] :
  - Liste officielle des stations (`observations-liste-postes-nivo-20250710.csv`, 124 lignes) : 86 dans l'emprise, 38 hors emprise (Pyrénées, Corse).
  - Données 2025 : 108 stations dont 81 dans l'emprise ; données 2026 (au 2026-10-11) : 109 stations dont 79 dans l'emprise ; 2024 : 110 stations dont 81 dans l'emprise.
  - Altitudes de 790 m (Vacheresse) à 3 200 m (Les 2 Alpes Jandri).
  - Alpes du Nord largement couvertes (Savoie, Haute-Savoie), Alpes du Sud moins (Abriès, Risoul, Vars, Les Orres, Nevache, Montgenèvre, Valberg, Isola, La Foux d'Allos, Pra Loup, Auron, Super Dévoluy).
- Fréquence réelle sur 2025, mois de décembre à mars, dans l'emprise [vérifié] : 7 198 observations pour 6 470 jours-stations ; 5 743 jours-stations avec une seule observation, 726 avec deux, 1 avec trois ; 97,9 % des observations ont un `ssfrai` renseigné ; `ssfrai` strictement positif dans 1 957 observations, soit 28 % ; heures dominantes 07 et 08 UTC (4 807 sur 7 048). Médiane de 64 stations qui rapportent un `ssfrai` par jour d'hiver, maximum de 77.
- Distribution des valeurs `ssfrai` positives en 2025 (m) : médiane 0,04 ; 90e centile 0,17 ; maximum 0,50 [vérifié].
- Profondeur d'archive : 1996 à 2026 en fichiers annuels ; la description du jeu précédent (« Données d'observations du réseau nivo-météorologique », ancien catalogue) indique une disponibilité depuis décembre 2010 [tiers, résultat de recherche data.gouv.fr non relu sur la page]. Le remplissage de `ssfrai` avant 2024 n'a pas été contrôlé ici (2024 et 2025 seulement).
- Formats : CSV compressé gzip. **Séparateur virgule en 2024, point-virgule en 2025 et 2026** ; `geo_id_wmo` perd son zéro initial en 2026 (`7393` au lieu de `07393`) ; `insert_time` renseigné sur 100 % des lignes 2026 et vide dans les fichiers 2024 et 2025 contrôlés [vérifié].
- Observé ou modélisé : observé (humain). La hauteur de neige simulée du modèle Crocus (S2M) est un produit séparé, voir [`s2m`](s2m.md).
- Documentation officielle : voir Sources.
- Note : data.gouv.fr et l'API ont été injoignables par intermittence depuis la session (coupures du proxy, reprises) ; la mention « version 2.0 » vient de `lov2` et du catalogue data.gouv.fr, la page Confluence écrivant seulement « Licence Ouverte d'Etalab ».
- Licence : « Licence Ouverte / Open Licence version 2.0 » [producteur] (https://www.data.gouv.fr/datasets/archive-reseau-nivo-meteorologique, consultée le 2026-10-21 ; champ `license` = `lov2` dans l'API) ; « Sans redevance sous Licence Ouverte d'Etalab. La source à indiquer est "Météo-France". Quelques suggestions : "Source : Météo-France" ou "Informations créées à partir de données de Météo-France". » [producteur] (https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/pages/888143886/Observations+in+situ, consultée le 2026-10-21).

### Dérivation de la neige fraîche à partir de la hauteur totale (test du projet)

Seules les stations sans `ssfrai` (Nivôse, voir [`nivose`](nivose.md)) imposent de dériver. Test sur la base climatologique quotidienne (voir [`meteo-france-observations`](meteo-france-observations.md)), 97 stations de l'emprise qui ont à la fois `HNEIGEF` (neige fraîche mesurée) et `NEIGETOT06` (hauteur totale à 06 h), du 2025-11-01 au 2026-04-30, 10 565 paires jour-station [vérifié] :

- Différence `NEIGETOT06(J+1) - NEIGETOT06(J)` comparée à `HNEIGEF(J)` (la valeur lue à J+1 est affectée au jour J).
- Corrélation entre `HNEIGEF` et la différence positive : 0,91.
- Quand `HNEIGEF` vaut au moins 5 cm (1 693 cas, sur 69 dates distinctes sur 181) : médiane de la différence 9 cm ; trois estimateurs du rapport hausse / `HNEIGEF` : moyenne des rapports 0,63 (intervalle par blocs d'une semaine du relecteur : 0,54 à 0,71), rapport des sommes 0,70, médiane 0,77 ; la moyenne est tirée vers le bas par 11,8 % de cas à différence nulle ou négative malgré la chute. Le dérivé **sous-estime donc de 23 à 37 % selon l'estimateur**. Corrélation 0,91 (relecteur : 0,89 à 0,93, r = 0,915 reproduit à l'identique).
- Au seuil de 5 cm sur la hausse : taux de détection (POD) 0,76 à 0,77 (23 % des chutes de 5 cm ou plus manquées), part d'alertes fausses 4,8 % ; au seuil de 3 cm : POD 0,84, part d'alertes fausses 13 %. 3 402 des 10 565 paires ont `QHNEIGEF` = 9 (filtrée, non validée).
- Quand `HNEIGEF` vaut 0 (7 683 cas) : la différence atteint 3 cm ou plus dans 0,9 % des cas et 5 cm ou plus dans 0,5 % (faux positifs : vent, mesure).
- Ces chiffres sont **dérivés** et propres à des postes manuels (même observateur, même heure pour les deux mesures) ; ils ne valent pas pour les Nivôse ni les capteurs d'altitude exposés au vent (étalonnage non disponible, dérivé brut) [hypothèse]. Tout étalonnage se fait sur les seules saisons d'entraînement ; 2025-2026 sert ici de test, donc elle est exclue de tout étalonnage ultérieur.

## Test d'accès

- Date : 2026-10-21, entre 15:30 et 16:10 UTC, sans compte, sans clé.
- Commande exacte :
  - `curl -sS -m 30 https://www.data.gouv.fr/api/1/datasets/68aeced879316c333d564f95/ -o nivo.json` (catalogue : titre, licence, ressources).
  - `curl -sS -m 40 -I https://meteofrance.s3.sbg.io.cloud.ovh.net/data/OBS/NIVOSE/nivo_2026.csv.gz`
  - `curl -sS -m 60 -o nivo_2026.csv.gz https://meteofrance.s3.sbg.io.cloud.ovh.net/data/OBS/NIVOSE/nivo_2026.csv.gz`, idem `nivo_2025.csv.gz` et `nivo_2024.csv.gz`.
  - `curl -sS -o desc.pdf https://static.data.gouv.fr/resources/archive-reseau-nivo-meteorologique/20260422-141132/observations-descriptif-technique-donnees-nivo-20260422.pdf` puis `pdftotext -layout desc.pdf`.
  - `curl -sS -o postes.csv https://static.data.gouv.fr/resources/archive-reseau-nivo-meteorologique/20260422-141208/observations-liste-postes-nivo-20250710.csv`
  - Lecture avec `python3 -I` (modules `csv`, `gzip`).
- Taille téléchargée : 322 428 (2026) + 374 804 (2025) + 354 021 (2024) octets de données, 415 282 octets de PDF, 5 486 octets de liste de postes ; environ 1,5 Mo au total.
- Résultat observé :
  - HTTP 200 sur toutes les ressources ; `Content-Length` 322 428 et `Last-Modified: Wed, 21 Oct 2026 06:30:15 GMT` pour `nivo_2026.csv.gz` ; 10 518 lignes pour 2025 ; 8 478 lignes pour 2026 (dernière date de mesure 2026-10-13).
  - Plusieurs échecs ponctuels « Connection reset by peer » (proxy du bac à sable) sur `data.gouv.fr` et `static.data.gouv.fr`, résolus par une nouvelle tentative.
  - Dans le catalogue : 31 fichiers annuels de 1996 à 2026, plus le descriptif et la liste de postes ; `temporal_coverage` 1996-01-01 à 2026-09-09 ; `last_modified` 2026-10-21 ; `frequency` quotidienne.

## Limites

- Le jeu est **déclaratif et manuel** : des pisteurs, surtout le matin, avec des protocoles de station variables ; biais de station : sites de domaines skiables, donc potentiellement damés, abrités ou remaniés par le vent [hypothèse] ; altitude médiane 1 788 m, 80 stations sur 86 de l'emprise entre 1 200 et 2 400 m, 3 au-dessus de 2 500 m, 2 sous 1 200 m [vérifié sur la liste officielle]. Aucun profil de qualité de la mesure fourni par le producteur dans les fichiers.
- Une seule observation par jour en pratique, malgré l'annonce « 12 h » : les neiges fraîches à 24 h sont possibles, mais pas de fenêtre glissante précise ; 48 et 72 h par somme de jours consécutifs (dérivé).
- `perssfrai` prend les valeurs `-99` (6 140 observations de décembre à mars 2025 avec `ssfrai`) et `-50` (908), alors que le descriptif annonce une durée en 1/10 d'heure : la signification de ces codes n'est pas documentée au 2026-10-21. La période exacte de la neige fraîche est donc **inconnue** ; ne pas supposer 24 h.
- `neige_fraiche` (en plus de `ssfrai`) est renseigné dans 2 314 lignes en 2025 (2 196 en 2026) ; relation avec `ssfrai` non documentée. Le projet utilise `ssfrai`.
- Fichiers par année avec séparateurs différents ; homogénéiser à la lecture.
- Une même station apparaît sous plusieurs noms (`ISOLA` et `ISOLA_NIVO`, `Les Portes en Valgaudemar` et `LES PORTES EN VALGAUDEMAR_NIVO`, `SUPER DEVOLUY_NIVO` et `_NIVO2`) : dédupliquer par identifiant OMM et nom.
- Mêmes mesures de neige fraîche que `HNEIGEF` de la base climatologique quotidienne (97,3 % d'accord à 1 cm près sur 5 323 paires, voir [`meteo-france-observations`](meteo-france-observations.md)) : une seule source de vérité, pas deux.
- Ne contient pas les stations automatiques Nivôse (voir [`nivose`](nivose.md)).
- Hors saison les observations sont rares (une trentaine à une soixantaine par mois en mai à octobre pour 80 stations).
- Les observations d'avalanche (`aval_*`) et d'estimation de risque (`aval_risque`) sont des observations de pisteurs, à ne jamais utiliser comme verdict de sécurité ; référence : BRA de Météo-France.

## Sources

- https://www.data.gouv.fr/api/1/datasets/68aeced879316c333d564f95/ — consultée le 2026-10-21
- https://www.data.gouv.fr/datasets/archive-reseau-nivo-meteorologique — consultée le 2026-10-21
- https://meteofrance.s3.sbg.io.cloud.ovh.net/data/OBS/NIVOSE/nivo_2025.csv.gz — consultée le 2026-10-21
- https://static.data.gouv.fr/resources/archive-reseau-nivo-meteorologique/20260422-141132/observations-descriptif-technique-donnees-nivo-20260422.pdf — consultée le 2026-10-21
- https://static.data.gouv.fr/resources/archive-reseau-nivo-meteorologique/20260422-141208/observations-liste-postes-nivo-20250710.csv — consultée le 2026-10-21
- https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/pages/888143886/Observations+in+situ — consultée le 2026-10-21
- https://confluence-meteofrance.atlassian.net/wiki/spaces/OpenDataMeteoFrance/pages/1351516182 — consultée le 2026-10-21
- https://meteofrance.com/meteo-a-z/comment-prevoit-on-les-avalanches — consultée le 2026-10-21
