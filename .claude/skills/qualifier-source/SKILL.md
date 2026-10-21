---
name: qualifier-source
description: Use to qualify, evaluate or document a data source (qualifier, évaluer ou documenter une source de données) for PowAtlas — forecasts, observations, reanalyses, satellite, terrain. Produces a source record in docs/sources/ with a real access test.
---

# Qualifier une source de données

Une **fiche source** (`docs/sources/<id>.md`) est obligatoire avant qu'une donnée entre dans le projet. Elle dit ce que contient la source, sous quelle licence, comment y accéder, et ce qu'un test réel a montré. Format : [`docs/methode.md`](../../../docs/methode.md#2-fiches). Modèle : [`template.md`](template.md).

## Règles

- **Zéro euro, aucun compte.** Si l'accès exige un compte (même gratuit), écrire `acces: compte gratuit requis (<service>)`, ne pas créer le compte, et arrêter le test là.
- **50 Mo au plus** téléchargés par test. Préférer les index, catalogues, en-têtes HTTP (`curl -I`), lectures partielles (`curl -r 0-...`), métadonnées. Rien de téléchargé n'est commité, sauf des métadonnées de moins de 100 Ko.
- **Aucun secret** (clé, jeton, lien signé) dans la fiche ni dans les commandes recopiées.
- **Une page publique n'est pas une licence.** La licence est lue sur la page officielle du producteur, recopiée exactement, avec lien et date.
- Marquer chaque affirmation : **[vérifié]** (nous l'avons constaté), **[producteur]** (documentation officielle), **[tiers]** (autre source) ou **[hypothèse]**. Dater chaque source consultée.
- Ne jamais inventer une valeur. Inconnue après recherche → écrire ce qui manque (ex. `non documenté par le producteur au 2026-10-21`), jamais `TODO`, `?` ni vide.
- Jamais de verdict de sécurité avalanche ; le BRA de Météo-France est cité comme référence quand c'est pertinent.

## Procédure

1. **Documentation officielle.** Trouver les pages du producteur (portail de données, documentation technique, conditions d'utilisation). Pour les articles scientifiques, utiliser alphaXiv ; pour les jeux de données hébergés, la recherche Hugging Face ; pour le web, Exa (recherches ciblées) ou la recherche web intégrée.
2. **Licence exacte** : nom, version, lien, date de consultation, obligations d'attribution.
3. **Accès** : URL de base, protocole, compte requis ou non, formats (GRIB2, NetCDF, Zarr, CSV, API JSON…).
4. **Test réel d'accès** sans compte : une commande reproductible (`curl`, `python3` bibliothèque standard), exécutée maintenant. Noter la date, la commande exacte, la taille téléchargée et le résultat observé (code HTTP, liste de fichiers, extrait d'en-tête). Si le test échoue, le noter tel quel.
5. **Caractéristiques** : quotas et limites de débit ; délai de mise à disposition après le run ou la mesure ; durée de conservation sur le portail ; résolution spatiale et temporelle ; runs par jour et échéances ; variables utiles à la neige (chute de neige, équivalent en eau, précipitations et leur phase, hauteur de neige, température, isotherme 0 °C, limite pluie-neige, vent…) ; couverture de l'emprise des Alpes françaises (ouest 5.0, sud 43.5, est 7.9, nord 46.5, EPSG:4326).
6. **Statut** : `retenue` (utile et accessible légalement), `ecartee` (avec la raison) ou `a-tester` (accès ou licence à confirmer).
7. **Remplir le modèle** : recopier `template.md` dans `docs/sources/<id>.md`, remplacer chaque `<à compléter>`, supprimer le paragraphe d'instructions. Ajouter une section `## Sources` avec chaque URL et sa date de consultation.
8. **Vérifier** : `python3 scripts/check_docs.py` doit afficher `OK: ...`. Corriger toute erreur signalée.
