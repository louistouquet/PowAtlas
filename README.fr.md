# PowAtlas

*[English version](README.md)*

PowAtlas est un système open source pour comprendre et prévoir la neige en montagne, en commençant par les Alpes françaises. Il veut dire combien il va tomber, où et à quelle altitude, et comment le manteau neigeux évolue — chaque affirmation étant appuyée par des scores de vérification publics.

**État :** fondations du projet en cours (SP0). **Rien n'est encore opérationnel.**

## Principes

- **Données ouvertes uniquement** : chaque source est documentée avec sa licence et attribuée.
- **Zéro euro** : uniquement des offres gratuites, pour le calcul comme pour l'hébergement.
- **Scores publics** : aucune affirmation de qualité sans comparaison publiée face à une référence.
- **Jamais de verdict de sécurité avalanche.** PowAtlas informe et analyse ; le bulletin d'estimation du risque d'avalanche (BRA) de Météo-France reste la référence.

## Feuille de route

| # | Sous-projet | Contenu |
|---|---|---|
| SP0 | Fondations | Vision, méthode, outillage, dépôt public, recherche initiale (R0), cible et feuille de route |
| SP1 | Archive et observations | Archivage quotidien des prévisions ouvertes, mesures, réanalyses, satellite ; publication ouverte |
| SP2 | Tableau des scores | Vérification automatique et publique des prévisions contre les mesures |
| SP3 | Prévision v1 | Réduction d'échelle sur le relief, correction par apprentissage, combinaison de modèles, probabilités, alertes poudre |
| SP4 | Manteau neigeux | Couches et qualité de neige par massif, altitude et exposition |
| SP5 | Recherche IA avancée | Modèles météo par IA, en production seulement s'ils gagnent au tableau des scores |
| SP6 | Produits | API ouverte, site, carte, alertes, état des stations en direct |

Pour en savoir plus : [`docs/vision.md`](docs/vision.md). Index de la documentation : [`docs/README.md`](docs/README.md).

## Contribuer et licences

- Comment contribuer : [`CONTRIBUTING.md`](CONTRIBUTING.md).
- Code : [Apache-2.0](LICENSE) (voir aussi [`NOTICE`](NOTICE)).
- Données, modèles et documentation produits par le projet : CC-BY-4.0 ; les données tierces gardent leur licence — voir [`DATA_LICENSES.md`](DATA_LICENSES.md).
