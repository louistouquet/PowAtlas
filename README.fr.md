# PowAtlas

*[English version](README.md)*

PowAtlas est un système open source pour comprendre et prévoir la neige en montagne, en commençant par les Alpes françaises. Il veut dire combien il va tomber, où et à quelle altitude, et comment le manteau neigeux évolue — chaque affirmation étant appuyée par des scores de vérification publics.

**État :** SP1 en cours. La collecte quotidienne des prévisions ouvertes (ICON-D2, ICON-EU, AROME, ARPEGE, IFS, AIFS) et des observations qui ne restent que quelques jours en ligne tourne sur GitHub Actions depuis octobre 2026 ; l'archive de référence est gardée sur la machine du pilote. **Aucune prévision ni aucun score n'est encore publié.**

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

## Collecte des données

Le paquet Python `powatlas` (`src/powatlas/`) collecte chaque source, la découpe sur les Alpes françaises et l'archive telle que publiée, avec un manifeste par unité (sha256, `Last-Modified` du producteur, champs absents). Sources et horaires : [`src/powatlas/catalogue.toml`](src/powatlas/catalogue.toml) ; workflow : [`.github/workflows/collect.yml`](.github/workflows/collect.yml) ; cadrage : [`docs/specs/2026-10-22-sp1-archive-design.md`](docs/specs/2026-10-22-sp1-archive-design.md) ; installation sur le PC du pilote : [`docs/collecte/installation-pc.md`](docs/collecte/installation-pc.md). Aucune donnée n'est stockée dans Git.

## Contribuer et licences

- Comment contribuer : [`CONTRIBUTING.md`](CONTRIBUTING.md).
- Code : [Apache-2.0](LICENSE) (voir aussi [`NOTICE`](NOTICE)).
- Données, modèles et documentation produits par le projet : CC-BY-4.0 ; les données tierces gardent leur licence — voir [`DATA_LICENSES.md`](DATA_LICENSES.md).
