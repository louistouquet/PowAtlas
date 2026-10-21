---
type: source
id: arpa-valle-aosta
nom: Valle d'Aoste, nivomètres du Centre fonctionnel régional (Dataview) et cartes de neige
producteur: Centre Fonctionnel de la Région autonome Vallée d'Aoste (Italie) ; auteur des relevés manuels AINEVA non précisé sur les pages lues
licence: Creative Commons Attribution 4.0 International (CC BY 4.0), affichée sur le portail Dataview (« Licenza per il riutilizzo dei dati pubblici »)
acces: PDF des dernières heures en HTTPS public sans compte (cf.regione.vda.it/allegati/bollettini/dettaglio/nivometri_Zona_*.pdf) ; données structurées (CSV) via le formulaire du portail Dataview (presidi2.regione.vda.it), non rempli : compte ou formulaire requis, non testé
quotas: non documentés au 2026-10-21
delai: PDF des nivomètres régénéré en continu (édition du 2026-10-21 à 17:18 heure locale constatée à la lecture) ; carte de hauteur de neige publiée chaque jour à 10:00
resolution: ponctuelle ; 41 entrées de nivomètres dans les quatre PDF de zone (stations en limite de zone possibles en double) ; hauteur de neige au sol (H, cm) toutes les 30 minutes
conservation: PDF : 24 h en tableau et 96 h en graphique ; Dataview : historique non documenté au 2026-10-21 ; carte de neige fraîche en images (1 jour et 3 jours) sans archive documentée
statut: a-tester
verifie_le: 2026-10-21
---

# Valle d'Aoste, nivomètres du Centre fonctionnel régional (Dataview) et cartes de neige

Chaque affirmation porte sa source et sa date de consultation (2026-10-21 pour toutes), et une marque : **[vérifié]** (constaté par nous), **[producteur]** (documentation officielle), **[tiers]** ou **[hypothèse]**.

## Contenu

- Description : réseau hydrométéorologique régional (température, précipitation, hauteur de neige, vent, hydrométrie) du Centre fonctionnel, portail Dataview pour les données observées [producteur] (http://cf.regione.vda.it/it/mappa-dati-stazioni-periferiche). La partie nivologique manuelle (modèles AINEVA MOD1, MOD23) alimente aussi les cartes [producteur] (https://www.regione.vda.it/mappeneve/altezza_neve_min2000_i.aspx).
- Mesures, observé et modélisé séparés [producteur] (même page de cartes) :
  - **Observé** : hauteur de neige au sol des nivomètres automatiques (médiane des valeurs de 30 minutes entre 6 h et 9 h pour la carte) ; relevés manuels journaliers MOD1 entre 7 h et 9 h dans des champs de neige fixes, plutôt plats et abrités du vent ; relevés MOD23 ; paline (perches) observées souvent aux jumelles par les commissions locales avalanches (précision non centimétrique).
  - **Modélisé** : la carte de hauteur de neige spatialisée vient du modèle S3M (Snow Multidata Mapping and Modeling, résolution 500 m, horaire, tourne depuis 2009 avec la Fondation CIMA) qui assimile les nivomètres automatiques, les images MODIS et un équivalent en eau hebdomadaire. À ne pas confondre avec une observation.
  - Cartes de neige fraîche (« Mappe di neve » : centimètres de neige fraîche des dernières 24 h et des 3 derniers jours) ; nature (observée, interpolée ou modélisée) non précisée sur la page lue [vérifié, non documenté].
- Variables constatées dans les PDF `nivometri_Zona_*` : `H(cm)` hauteur de neige au sol toutes les 30 minutes, température, vent pour les stations équipées [vérifié] ; **aucune neige fraîche** ni équivalent en eau dans ces PDF : à dériver de la hauteur (voir [`reseau-nivo-meteo`](reseau-nivo-meteo.md)).
- Couverture de l'emprise (ouest 5.0, sud 43.5, est 7.9, nord 46.5) : la Vallée d'Aoste est à l'intérieur de l'emprise (stations de 1 029 m à plus de 2 000 m ; longitude 7.83 pour la plus orientale lue). Dénombrement [vérifié] : zone A 5, zone B 8 (de 1 370 à 2 270 m : Gressoney, Champorcher, Ayas, Fénis), zone C 8, zone D 20, soit 41 entrées ; fiche d'altitude par station dans chaque PDF.
- Fréquence : 30 minutes [vérifié sur les PDF].
- Formats : PDF (tableaux et graphiques) ; CSV et ZIP via Dataview [producteur, interface] ; images pour les cartes.
- Biais connus : relevés manuels sur champs fixes, nivomètres automatiques sensibles au vent et à la fonte ; les PDF avertissent de « valeurs anormales » possibles car publiés en temps réel [vérifié] (« non si può escludere la presenza saltuaria di valori anomali »).
- Documentation officielle : voir Sources.
- Licence : le portail Dataview affiche « Attribuzione 4.0 Internazionale (CC BY 4.0) – Licenza per il riutilizzo dei dati pubblici » avec le résumé de la licence (partager, adapter, y compris à but commercial, avec attribution) et un lien vers le texte intégral (https://creativecommons.org/licenses/by/4.0/legalcode.it) [vérifié] (https://presidi2.regione.vda.it/str_dataview_download, consultée le 2026-10-21). Le texte précis d'attribution demandé à l'utilisateur : « fornire un link alla licenza e indicare se sono state effettuate delle modifiche » ; formule de mention de la source propre à la Région non lue [non documenté].

## Test d'accès

- Date : 2026-10-21, entre 16:30 et 17:20 UTC, sans compte, sans clé.
- Commande exacte :
  - `curl -sS -m 40 https://presidi2.regione.vda.it/str_dataview_download -o vda.html` (portail Dataview, extraction des liens et de la licence).
  - `curl -sS -m 40 -L -o nivB2.pdf https://cf.regione.vda.it/allegati/bollettini/dettaglio/nivometri_Zona_B.pdf`, puis zones A, C et D ; lecture avec `pdftotext -layout`.
- Taille téléchargée : PDF zone A 580 697, B 785 397, C 718 626, D 1 782 753 octets ; page Dataview 50 403 octets ; environ 3,9 Mo au total.
- Résultat observé :
  - Page Dataview HTTP 200 ; elle propose des « pacchetti .zip o PDF » sans formulaire pour la précipitation, la température et les nivomètres « ultime ore » ; le téléchargement personnalisé (« Compila tutti i campi obbligatori ») exige un formulaire avec un motif de demande pour documents officiels : non rempli.
  - Le lien HTTP (sans TLS) `http://cf.regione.vda.it/...` répond 301 vers HTTPS ; la version HTTPS renvoie un PDF (HTTP 200, `application/pdf`).
  - PDF zone B : « Dati Nivometrici Zona B », 8 stations triées par altitude, édition du 21 octobre 2026 17:18, 9 pages ; chaque station : altitude, coordonnées WGS84, tableau des dernières 24 h (heure locale), graphique 96 h.
  - Aucune API JSON ni CSV directe trouvée sans formulaire.

## Limites

- Pas de flux structuré ouvert confirmé : le PDF n'est pas une archive exploitable (fenêtre de 24 h à 96 h) ; archiver chaque jour demanderait d'extraire les tableaux de PDF ou de remplir le formulaire de Dataview (compte ou formulaire, non fait).
- Pas de neige fraîche mesurée dans les PDF ; la carte « neve fresca » n'est pas une donnée tabulée.
- Les entrées en limite de zone sont comptées en double dans mon dénombrement (41 entrées) ; le nombre de stations distinctes n'est pas établi.
- Biais d'altitude : 1 029 à environ 2 300 m, peu de stations d'altitude.
- Les cartes S3M sont modélisées ; ne pas les utiliser comme vérité terrain.
- Statut `a-tester` : accès structuré (CSV) et conditions du formulaire à confirmer ; la licence CC BY 4.0 est lue sur le portail.

## Sources

- https://presidi2.regione.vda.it/str_dataview_download — consultée le 2026-10-21
- http://cf.regione.vda.it/it/mappa-dati-stazioni-periferiche — consultée le 2026-10-21
- https://cf.regione.vda.it/it/mappe — consultée le 2026-10-21
- https://www.regione.vda.it/mappeneve/altezza_neve_min2000_i.aspx — consultée le 2026-10-21
- https://cf.regione.vda.it/allegati/bollettini/dettaglio/nivometri_Zona_B.pdf — consultée le 2026-10-21
- https://cf.regione.vda.it/allegati/bollettini/dettaglio/nivometri_Zona_D.pdf — consultée le 2026-10-21
