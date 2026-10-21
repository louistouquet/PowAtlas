---
type: source
id: copernicus-neige
nom: Copernicus Land, produits neige haute résolution (FSC, GFSC, SWS, WDS)
producteur: Service de surveillance des terres Copernicus (CLMS), Agence européenne pour l'environnement, projet HR-WSI (suite de HR-S&I)
licence: accès « complet, ouvert et gratuit » selon la politique de données CLMS (Règlement délégué UE 1159/2013), avec mention obligatoire de la source ; pas de licence Creative Commons nommée sur les pages lues
acces: catalogue de recherche public sans compte (OData du Copernicus Data Space) ; téléchargement des fichiers = compte gratuit requis (Copernicus Data Space Ecosystem, WEkEO, ou compartiment S3 via script)
quotas: non lus (compte requis pour le téléchargement) ; catalogue : aucun refus sur 5 requêtes
delai: FSC : environ 6 h entre la prise de vue Sentinel-2 et la publication (2026-10-17 : prise de vue 10:28 UTC, publication 16:22 UTC) ; GFSC : produit quotidien avec latence maximale de 3 h après la fin de la journée
resolution: FSC 20 m (optique Sentinel-2) ; GFSC, SWS, WDS 60 m (radar Sentinel-1) ; tuiles Sentinel-2 de 110 km ; couverture neigeuse, pas de hauteur ni d'équivalent en eau
conservation: 2016 à aujourd'hui en archive avec retraitement en cours (données avant le 20 janvier 2025 en cours de retraitement entre le premier et le troisième trimestre 2026)
statut: a-tester
verifie_le: 2026-10-21
---

# Copernicus Land, produits neige haute résolution (FSC, GFSC, SWS, WDS)

Chaque affirmation porte sa source et sa date de consultation (2026-10-21 pour toutes), et une marque : **[vérifié]** (constaté par nous), **[producteur]** (documentation officielle), **[tiers]** ou **[hypothèse]**. Produits **dérivés de satellite** (observation indirecte par un algorithme), ni une mesure de station ni un modèle de neige.

## Contenu

- Description : manuel d'utilisation HR-WSI (version 1.3, 15/09/2026) : trois familles, couverture (FSC, GFSC), état de la neige (WDS, SWS), agrégats (phénologie SP) [producteur] (https://land.copernicus.eu/en/technical-library/product-user-manual-high-resolution-snow-products-europe/@@download/file).
  - **FSC** (Fractional Snow Cover) : fraction de neige au-dessus de la canopée (FSCTOC) et au sol (FSCOG), 0 à 100 %, 20 m, optique Sentinel-2, quasi temps réel ; inutilisable sous les nuages.
  - **GFSC** (Gap-filled FSC) : combine FSC et SWS ; comble les trous spatialement (même jour) puis temporellement avec les 7 jours précédents ; 60 m ; la couche `AT` donne la date d'acquisition de chaque pixel ; produit quotidien, latence maximale de 3 h après la fin du jour ; 5 jours de passes nécessaires pour une couverture complète en bonnes conditions.
  - **SWS** (SAR Wet Snow) : neige humide en haute montagne uniquement (tuiles sélectionnées), binaire, 60 m, Sentinel-1.
  - **WDS** (Wet/Dry Snow) : sec ou humide dans le masque de neige, 60 m.
- Variables utiles à la neige : couverture neigeuse (%) et neige humide (oui ou non). **Aucune hauteur de neige, aucune neige fraîche, aucun équivalent en eau.** Le catalogue de l'espace de données propose un produit d'équivalent en eau de la neige (SWE) à 5 km sur l'hémisphère nord, hors sujet (résolution) [vérifié, liste de collections du STAC].
- Usage pour la vérité terrain : vérifier a posteriori si de la neige couvre le sol à basse altitude après une chute (présence ou absence, ligne de neige), pas la quantité. Le passage de la neige humide par SWS permet de repérer la fonte [hypothèse].
- Couverture de l'emprise (ouest 5.0, sud 43.5, est 7.9, nord 46.5) : produits pan-européens par tuile Sentinel-2 ; tuile T32TLR (Alpes de Savoie) présente dans le catalogue [vérifié]. Nombre de tuiles pour l'emprise : non compté.
- Fréquence : FSC à chaque passage Sentinel-2 utile (2 à 3 dates par semaine sur la tuile T32TLR en octobre 2026 : 12, 15 et 17 octobre) ; GFSC quotidien [vérifié et producteur].
- Formats : GeoTIFF (COG), un produit par tuile, couches séparées ; FSC d'environ 2 à 17 Mo par produit de tuile, GFSC d'environ 4 Mo [vérifié par `ContentLength`]. Le manuel donne FSC 32 Mo, GFSC 4 Mo, SWS 1 Mo compressés pour l'ancien produit HR-S&I [producteur].
- Biais connus : nuages (FSC), forêt (transmittance, FSCOG compensée), ombres de relief, neige sous couvert ; GFSC peut afficher des informations de 7 jours ; la collection Wet/Dry est annoncée « Not yet validated » sur sa page [producteur] (https://land.copernicus.eu/en/products/snow/high-resolution-wet-dry-snow).
- Observé ou modélisé : satellite dérivé (algorithme d'inversion), ni mesure ni modèle de manteau.
- Documentation officielle : voir Sources.
- Licence : « The Copernicus land monitoring products and services are made available on a principle of full, open and free access, as established by the Commission Delegated Regulation (EU) No 1159/2013 » ; conditions : informer le public de la source, indiquer les adaptations, ne pas suggérer un soutien officiel de l'Union européenne [producteur] (https://land.copernicus.eu/en/data-policy, consultée le 2026-10-21). Mentions : « Generated using European Union's Copernicus Land Monitoring Service information; » pour un produit dérivé ; « European Union's Copernicus Land Monitoring Service information; » pour une redistribution. L'utilisateur détient les droits de propriété intellectuelle de ses produits. Aucune licence de type Creative Commons nommée.

## Test d'accès

- Date : 2026-10-21, entre 16:00 et 16:40 UTC, sans compte, sans clé.
- Commande exacte :
  - `curl -sS -m 40 "https://stac.dataspace.copernicus.eu/v1/collections?limit=200" -o stac.json` (liste de collections).
  - `curl -sS -G "https://catalogue.dataspace.copernicus.eu/odata/v1/Products" --data-urlencode "\$filter=Collection/Name eq 'CLMS' and contains(Name,'CLMS_WSI_FSC_020m_T32TLR') and OriginDate gt 2026-09-01T00:00:00.000Z" --data-urlencode "\$orderby=OriginDate desc" --data-urlencode "\$top=3"`, idem avec `CLMS_WSI_GFSC_060m`.
  - Gabarit (remplacer `ID_PRODUIT` par l'identifiant d'un produit FSC lu dans le catalogue ; ce n'est pas une URL réelle) : `curl -sS -r 0-200 "https://download.dataspace.copernicus.eu/odata/v1/Products(ID_PRODUIT)/\$value"`, sans jeton.
  - `curl -sS "https://land.copernicus.eu/en/products/snow"` (page, rendue côté navigateur, sans contenu utile en HTML brut).
- Taille téléchargée : environ 1,6 Mo (liste de collections) et quelques Ko de catalogue ; aucun produit téléchargé.
- Résultat observé :
  - Le catalogue répond HTTP 200 sans compte ; produits FSC de la tuile T32TLR : 2026-10-17 (prise de vue 10:28:22 UTC, publication 16:22:54 UTC), 2026-10-15 et 2026-10-12. Le catalogue contient aussi des produits GFSC de décembre 2023 publiés le 2026-10-21 (retraitement en cours).
  - Le téléchargement sans jeton renvoie HTTP 401 `{"code":"DAT-ZIP-604","message":"Token not found"}` : **compte gratuit requis** (non créé).
  - Le site rend ses pages en JavaScript ; les informations ont été lues dans la documentation (manuel PUM) et les pages produit.

## Limites

- Compte gratuit requis pour télécharger (Copernicus Data Space Ecosystem ou WEkEO) ; non créé ici, donc le téléchargement n'a pas été testé ; statut `a-tester`.
- Ne donne pas la neige fraîche : à utiliser seulement pour confirmer la présence de neige à basse altitude.
- Délai variable : prise de vue environ 6 h avant publication, mais couverture dépendante des nuages et du passage orbital (2 à 3 dates par semaine sur la tuile T32TLR en octobre) ; pas d'observation quotidienne en optique.
- Archive en retraitement (2016 à janvier 2025) : versions de méthode différentes de l'actuelle (les pages précisent que le contenu peut différer).
- Les accès annoncés : bucket S3 par script, WEkEO (inscription obligatoire), Copernicus Browser ; l'ancien catalogue HR-S&I a été fermé au 30 juin 2025 [producteur] (https://land.copernicus.eu/en/production-updates/european-snow-and-ice-data-production-has-concluded-the-catalogue-will-remain-accessible).
- Volume : plusieurs Mo par tuile et par jour, soit plusieurs dizaines de Mo par jour pour l'emprise [hypothèse].

## Sources

- https://land.copernicus.eu/en/data-policy — consultée le 2026-10-21
- https://land.copernicus.eu/en/products/snow/fractional-snow-cover — consultée le 2026-10-21
- https://land.copernicus.eu/en/products/snow/high-resolution-wet-dry-snow — consultée le 2026-10-21
- https://land.copernicus.eu/en/technical-library/product-user-manual-high-resolution-snow-products-europe/@@download/file — consultée le 2026-10-21
- https://land.copernicus.eu/en/faq/products/snow/what-is-the-spatial-resolution-of-high-resolution-snow-products — consultée le 2026-10-21
- https://land.copernicus.eu/en/production-updates/european-snow-and-ice-data-production-has-concluded-the-catalogue-will-remain-accessible — consultée le 2026-10-21
- https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/CLMS.html — consultée le 2026-10-21
- https://catalogue.dataspace.copernicus.eu/odata/v1/Products — consultée le 2026-10-21
- https://stac.dataspace.copernicus.eu/v1/collections — consultée le 2026-10-21
