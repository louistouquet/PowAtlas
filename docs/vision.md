# Vision de PowAtlas

*Version grand public des sections 2 à 4 du [cadrage SP0](specs/2026-10-21-sp0-fondations-design.md), 21 octobre 2026.*

## Ce que PowAtlas veut être

PowAtlas veut devenir le système open source de référence pour comprendre et prévoir la neige en montagne :

- **combien** il va tomber, **où** et **à quelle altitude** ;
- **ce qu'il y a au sol** aujourd'hui ;
- **comment le manteau neigeux évolue** au fil de la saison ;
- **où la neige est bonne** pour skier.

Chaque affirmation sera appuyée par des **scores publics** : on compare nos prévisions aux mesures réelles, et tout le monde peut voir le résultat.

Le projet s'adresse aux freeriders, randonneurs, skieurs, snowboardeurs, habitants des vallées et au grand public, depuis l'information de base (état des stations, neige fraîche) jusqu'à l'analyse fine (couches du manteau, qualité de neige selon l'altitude et l'orientation des pentes).

On commence par les **Alpes françaises**, puis on étendra à l'arc alpin, aux Pyrénées et au reste du monde.

## Ce que PowAtlas ne fera jamais

PowAtlas informe et analyse. **Il ne dit jamais si une pente est sûre ou dangereuse vis-à-vis des avalanches.** Le bulletin d'estimation du risque d'avalanche (BRA) de Météo-France reste la référence et sera toujours cité comme tel.

## Principes

- **Données ouvertes** : uniquement des sources dont la licence permet la réutilisation, citées et attribuées.
- **Zéro euro** : calcul et hébergement sur des offres gratuites.
- **Scores publics** : aucune affirmation de qualité sans comparaison chiffrée à une référence.
- **Transparence** : on distingue toujours ce qui est observé, ce qui est simulé et ce qui est prévu, et on affiche l'incertitude.

Inspirations : WePowder (alertes poudre par région) et Snowdata (apprentissage sur plusieurs modèles météo, satellite et relevés des stations).

## Les étapes du projet

Chaque étape (« sous-projet ») suit son propre cycle : discussion, cadrage validé, plan, réalisation, bilan.

| # | Étape | En clair | Dépend de |
|---|---|---|---|
| SP0 | Fondations | Méthode, outils, dépôt public, première recherche, feuille de route | — |
| SP1 | Archive et observations | Sauvegarder chaque jour les prévisions ouvertes, collecter les mesures, l'historique et le satellite | SP0 |
| SP2 | Tableau des scores | Comparer automatiquement et publiquement les prévisions aux mesures | SP1 |
| SP3 | Prévision v1 | Affiner les prévisions sur le relief, les corriger par apprentissage, combiner les modèles, donner des probabilités et des alertes poudre | SP1, SP2 |
| SP4 | Manteau neigeux | Simuler les couches et la qualité de la neige par massif, altitude et orientation | SP1, SP3 |
| SP5 | Recherche IA avancée | Tester les nouveaux modèles météo par IA ; ils n'entrent en service que s'ils gagnent au tableau des scores | SP1, SP2 |
| SP6 | Produits | API ouverte, site, carte, alertes, état des stations, Instagram | SP2, SP3 |

**Pourquoi l'archive est urgente.** Les portails ouverts ne gardent les prévisions que quelques jours (24 heures pour certains modèles, environ 2 à 3 jours pour l'ECMWF Open Data). Chaque jour non sauvegardé est perdu. La collecte doit tourner avant le 1er novembre 2026 : la saison 2026-27 servira d'abord à vérifier publiquement les modèles bruts, puis à entraîner ; la première saison de test indépendante des modèles corrigés sera 2027-28.

## Comment la prévision sera construite

Une hypothèse de départ, à confirmer par la recherche R0 : un système **en couches**, chacune testable et remplaçable séparément. Le tableau des scores décide de ce qui passe en service.

1. **Archive des prévisions ouvertes** : AROME, ARPEGE, ECMWF IFS et AIFS, ICON et autres, sauvegardées chaque jour.
2. **Affinage sur le relief** : relief fin, limite pluie-neige, effet de l'altitude et des versants, densité de la neige fraîche.
3. **Correction par apprentissage et combinaison des modèles** : apprises sur les écarts passés entre prévisions et mesures ; résultat en probabilités (« 70 % de chances de plus de 30 cm »).
4. **Manteau neigeux** : un modèle ouvert de simulation du manteau, alimenté par la météo corrigée.
5. **Piste IA avancée** : elle n'entre en service que si elle bat les couches 1 à 3 au tableau des scores.

**Contraintes de calcul.** Tout reste gratuit. La collecte quotidienne tourne sur la machine du pilote, sur GitHub Actions ou sur les deux, et l'archive de référence est conservée sur la machine du pilote. L'entraînement utilisera la meilleure offre de calcul gratuite du moment (par exemple les GPU gratuits de Kaggle ou Colab).
