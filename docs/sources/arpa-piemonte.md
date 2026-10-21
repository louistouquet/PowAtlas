---
type: source
id: arpa-piemonte
nom: Arpa Piemonte, réseau nivométrique (hauteur de neige et neige fraîche journalières)
producteur: Arpa Piemonte (Agence régionale pour la protection de l'environnement du Piémont, Italie)
licence: Creative Commons Attribution 4.0 International (CC BY 4.0), mention « Fonte: Arpa Piemonte - www.arpa.piemonte.it »
acces: API REST publique sans compte ni clé : utility.arpa.piemonte.it/meteoidro/ (historique journalier, JSON paginé) et utility.arpa.piemonte.it/api_realtime/ (derniers jours) ; service cartographique ArcGIS avec jeton exigé
quotas: non documentés au 2026-10-21 ; aucune limite rencontrée sur 26 pages de 1 000 enregistrements
delai: temps réel : hauteur de neige validée automatiquement toutes les 20 minutes avec un retard d'environ une heure (producteur, service cartographique) ; journalier : dernier jour de la table nivo = 2026-06-30 le 2026-10-21 (hors saison, délai non mesurable)
resolution: ponctuelle ; 75 stations nivométriques actives dans l'emprise (130 au total depuis 1983) ; hauteur de neige au sol (hs) et neige fraîche des 24 h (hn) journalières en cm
conservation: stations depuis 1983-12-12 (première date de début) ; table journalière interrogeable sur toute la période (501 valeurs pour 1990-01-01 à 1990-01-10, 1 139 pour 2010-01-01 à 2010-01-10)
statut: retenue
verifie_le: 2026-10-21
---

# Arpa Piemonte, réseau nivométrique (hauteur de neige et neige fraîche journalières)

Chaque affirmation porte sa source et sa date de consultation (2026-10-21 pour toutes), et une marque : **[vérifié]** (constaté par nous), **[producteur]** (documentation officielle), **[tiers]** ou **[hypothèse]**.

## Contenu

- Description : Arpa Piemonte « se occupa della raccolta e validazione dei dati di altezza di neve fresca, di altezza di neve al suolo e delle sue caratteristiche attraverso la rete nivometrica automatica e manuale » [producteur] (https://www.arpa.piemonte.it/temi/neve-ghiacciai/neve). Observé, jamais modélisé dans les tables lues.
- Mesures [producteur] (https://indicatoriambientali.arpa.piemonte.it/indicatoriambientali/neve-e-ghiacciai/precipitazioni-nevose) :
  - Stations manuelles : un opérateur mesure chaque jour, à 8 h, sur une tablette nivométrique, la neige fraîche tombée dans les 24 dernières heures ; saisie au modèle AINEVA « Modello 1 », validée chaque jour par le prévisionniste de service.
  - Stations automatiques : capteurs de hauteur de neige et de température du manteau ; l'indicateur précise que leurs données « risultano differenti da quelle delle stazioni manuali » et doivent être corrigées avant comparaison ; le service cartographique précise que la mesure automatique n'est correcte qu'à partir de 5 à 10 cm.
  - Critique de qualité du producteur : « disomogeneità spaziale delle stazioni (in particolare alle basse quote) » et difficulté de mesure en fusion ou précipitation mixte.
- Variables constatées dans l'API historique (`dati_giornalieri_nivo`) [vérifié] : `hs` (hauteur de neige au sol, cm), `hn` (neige fraîche, cm), `tmax`, `tmin`, `data`. Période de mesure de `hn` : non documentée dans la réponse de l'API ; on suppose les 24 h terminées à 8 h locale pour les stations manuelles [hypothèse]. La distinction manuel ou automatique par station n'est pas documentée : `tipo_staz` et `campo_neve` sont présents sans définition au 2026-10-21. Observation [vérifié] : du 1er au 7 février 2026, 71 stations de l'emprise ont un `hn` ; **18** ont `campo_neve = S` (toutes `tipo_staz = N`), **53** ont `campo_neve = N` avec des codes multi-capteurs (`NPT`, `HNPTV`, `NPRTV`...), probablement automatiques [hypothèse]. Seules les 18 stations `S` sont proposées comme observation directe, sous réserve de confirmer le sens de `S` ; les autres sont traitées comme dérivées (le producteur dit que les données automatiques « risultano differenti » et ne sont fiables qu'au-delà de 5 à 10 cm).
- API en temps réel [vérifié] : `/api_realtime/pie_neve` renvoie `validated_snow_height` (entier, cm) à 08:00 heure locale, pour 80 stations, 7 jours (2026-10-15 à 2026-10-21) ; pas de neige fraîche dans cette route. Une requête avec `date_from` du 2025-12-01 renvoie une liste vide : fenêtre glissante de 7 jours.
- Couverture de l'emprise (ouest 5.0, sud 43.5, est 7.9, nord 46.5) [vérifié] :
  - 130 stations nivologiques référencées (`stazione_nivologica`) dont 106 actives (sans `data_fine`) ; 97 dans l'emprise dont 75 actives. Altitudes des stations actives de l'emprise : de 236 à 2 977 m, médiane 1 680 m. Le Piémont s'étend à l'est de 7.9 : les stations de l'emprise sont celles de l'ouest et du sud-ouest.
  - Hiver 2026 (1er janvier au 31 mars) : 72 stations de l'emprise avec `hn` renseigné, dont 18 à `campo_neve = S` (1 589 valeurs, 25 % positives, 18 stations par jour) ; médiane de 71 stations par jour (maximum 72) sur 90 jours ; `hn` strictement positif dans 1 885 des 6 339 valeurs, soit 30 % ; `hn` maximal constaté 100 cm.
  - API en temps réel : 80 stations de neige, 56 dans l'emprise (altitudes de 236 à 3 320 m) [vérifié].
- Profondeur d'archive : première station en 1983-12-12 ; points de mesure nivo historiques à partir de 1983 ; la table journalière contient des valeurs pour 1990 et 2010 [vérifié]. Un rapport annuel « Rendiconto Nivometrico » est publié [producteur].
- Fréquence : journalière (`dati_giornalieri_nivo`), 20 minutes pour le service cartographique des stations automatiques [producteur].
- Formats : JSON paginé (Django REST, `count`, `next`, `results`, `page_size` accepté jusqu'à 1 000), schéma OpenAPI 3.0.3 à `/schema/` [vérifié].
- Biais connus : stations manuelles sur champ de neige fixe, souvent à faible altitude ; écarts entre stations manuelles et automatiques ; sous 5 à 10 cm, le capteur automatique n'est pas fiable [producteur].
- Documentation officielle : voir Sources.
- Licence : « Salvo diversa indicazione, gli Open Data pubblicati da Arpa Piemonte sono rilasciati con licenza : Creative Commons Attribuzione 4.0 Internazionale (CC BY 4.0) » [producteur] (https://www.arpa.piemonte.it/note-legali, consultée le 2026-10-21, lue par l'outil de lecture de page). Attribution : « Fonte: Arpa Piemonte - www.arpa.piemonte.it », avec lien vers la page d'origine si possible ; usage commercial, redistribution et intégration autorisés ; responsabilité de l'utilisateur pour les données modifiées ; les données sont fournies « nello stato in cui si trovano », sans garantie de continuité. Exclusions : logos, marques, contenus tiers.

## Test d'accès

- Date : 2026-10-21, entre 16:10 et 16:45 UTC, sans compte, sans clé.
- Commande exacte :
  - `curl -sS -m 40 "https://utility.arpa.piemonte.it/api_realtime/pie_neve" -o pn.json` et `.../api_realtime/pie_anag` (registre des stations).
  - `curl -sS -m 40 "https://utility.arpa.piemonte.it/meteoidro/dati_giornalieri_nivo/?data_min=2026-02-01&data_max=2026-02-03" -o gn.json`
  - `curl -sS -m 40 "https://utility.arpa.piemonte.it/meteoidro/stazione_nivologica/?page_size=500" -o sn.json`
  - Pagination Python (`urllib.request`, `-I`) de `.../dati_giornalieri_nivo/?data_min=2026-01-01&data_max=2026-03-31&page_size=1000`.
  - `curl -sS "https://utility.arpa.piemonte.it/schema/"` (schéma OpenAPI), `curl -sS ".../dati_giornalieri_nivo_latest_date/fetch_latest/"`.
  - `curl -sS "https://webgis.arpa.piemonte.it/server/rest/services/meteorologia_clima/TR_neve/MapServer/0?f=pjson"`.
- Taille téléchargée : environ 3 Mo (pie_neve 58 098 octets, pie_anag 171 132, 26 pages de neige hivernale, stations 78 567).
- Résultat observé :
  - HTTP 200 sans authentification sur `api_realtime` et `meteoidro` ; 309 enregistrements pour les 3 premiers jours de février 2026 ; 9 270 enregistrements pour janvier à mars 2026.
  - `fetch_latest` : `{"data":"2026-06-30"}` pour la table nivo.
  - Le service ArcGIS des couches de neige répond `{"error":{"code":499,"message":"Token Required"}}` : jeton exigé, non utilisé (sans compte).
  - La page « Open data » renvoie par courriel (info.meteo@arpa.piemonte.it) l'accès aux radars et radiosondages : non demandé (contact extérieur interdit).

## Limites

- Dernier jour de la table journalière : 2026-06-30 au 2026-10-21 ; le rythme de mise à jour de la table hors temps réel n'est pas documenté. Pour la vérité terrain, comparer `hn` avec la date d'émission de la prévision une fois la saison commencée.
- Hors de l'emprise pour l'essentiel du Piémont (Alpes Pennines, Lépontines) : l'intérêt est pour les Alpes françaises du sud et du sud-est (Cuneese, vallée de Suse), et le Briançonnais en frontière.
- Distinguer manuel et automatique n'est pas documenté : seul le champ `campo_neve` (`S` ou `N`) s'en approche, sens à confirmer auprès d'Arpa Piemonte (contact extérieur non fait). Ne garder en vérité terrain que les 18 stations `S`, sous réserve.
- `hn` peut ne pas coïncider avec la fenêtre 24 h des prévisions (8 h locale = 06 ou 07 UTC) : mêmes enjeux de fenêtre que Météo-France.
- Aucune hauteur d'eau équivalente dans les tables lues.
- La page `note-legali` lue en version texte : le texte exact de la licence est à relire avant publication d'un produit dérivé.

## Sources

- https://www.arpa.piemonte.it/note-legali — consultée le 2026-10-21
- https://www.arpa.piemonte.it/scheda-informativa/open-data — consultée le 2026-10-21
- https://www.arpa.piemonte.it/temi/neve-ghiacciai/neve — consultée le 2026-10-21
- https://indicatoriambientali.arpa.piemonte.it/indicatoriambientali/neve-e-ghiacciai/precipitazioni-nevose — consultée le 2026-10-21
- https://utility.arpa.piemonte.it/api_realtime/openapi.json — consultée le 2026-10-21
- https://utility.arpa.piemonte.it/schema/ — consultée le 2026-10-21
- https://utility.arpa.piemonte.it/meteoidro/dati_giornalieri_nivo/ — consultée le 2026-10-21
- https://utility.arpa.piemonte.it/meteoidro/stazione_nivologica/ — consultée le 2026-10-21
- https://webgis.arpa.piemonte.it/server/rest/services/meteorologia_clima/TR_neve/MapServer?f=pjson — consultée le 2026-10-21
