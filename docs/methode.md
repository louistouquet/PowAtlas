# Méthode de travail

Ce document décrit comment PowAtlas est construit. Il découle de la section 5 du [cadrage SP0](specs/2026-10-21-sp0-fondations-design.md) et s'applique à toutes les sessions, humaines ou IA. Le choix des modèles Claude et les règles d'économie sont dans [`modeles-claude.md`](modeles-claude.md).

## 1. Cycle d'un sous-projet

Chaque sous-projet (SP0 à SP6) suit le même cycle :

1. **Brainstorming** avec le pilote : but, contraintes, options.
2. **Cadrage** écrit dans `docs/specs/AAAA-MM-JJ-<sujet>-design.md`, validé par le pilote avant toute réalisation.
3. **Plan** découpé en petites tâches dans `docs/plans/AAAA-MM-JJ-<sujet>.md` : fichiers touchés, interfaces, étapes avec commandes et résultats attendus.
4. **Réalisation** en petites PR : tests automatiques, intégration continue verte, relecture par un agent, fusion en un seul commit par PR.
5. **Bilan** : mise à jour de `STATUS.md` (ce qui marche) et `NEXT.md` (prochaine action) ; les étapes terminées sont cochées dans le plan.

Rôles : **le pilote** fixe le cap, valide les cadrages et juge les résultats. **Claude** fait la recherche, le code et les PR, et fusionne après tests et relecture par un agent. Les documents qui demandent explicitement l'accord du pilote (cadrages, `docs/roadmap.md`) ne sont jamais fusionnés sans cet accord.

## 2. Fiches

Aucune donnée n'entre dans le projet sans sa **fiche source**, et aucun essai de modèle n'a lieu sans sa **fiche d'expérience**. Les recherches produisent des **rapports**. Les trois formats sont vérifiés en intégration continue par `scripts/check_docs.py`.

- **Fiche source** (`docs/sources/`) : producteur, contenu, licence, accès, quotas, délai de mise à disposition, résolution, durée de conservation, test réel d'accès (date, commande, résultat), limites. Procédure : skill `qualifier-source`.
- **Fiche d'expérience** (`docs/experiments/`) : hypothèse, référence à battre, données et découpage, mesures fixées **avant** l'essai, résultat, décision (garder, modifier, abandonner) et condition de réexamen. Les échecs sont conservés. Procédure : skill `experience-modele`.
- **Rapport de recherche** (`docs/research/`) : question, méthode, résultats, recommandation, questions ouvertes, sources.

### Formats des fiches

Chaque fiche commence par un bloc d'en-tête `---` ... `---` de lignes `cle: valeur`. Le champ `id` est égal au nom du fichier sans `.md`. Les dates sont au format `AAAA-MM-JJ`.

| Type | Dossier | Champs obligatoires | Valeurs contraintes | Sections obligatoires |
|---|---|---|---|---|
| `source` | `docs/sources/` | `type, id, nom, producteur, licence, acces, quotas, delai, resolution, conservation, statut, verifie_le` | `statut` ∈ `retenue, ecartee, a-tester` | `## Contenu`, `## Test d'accès`, `## Limites` |
| `experience` | `docs/experiments/` | `type, id, titre, statut, date, fictive, reference` | `statut` ∈ `prevue, en-cours, terminee, abandonnee` ; `fictive` ∈ `oui, non` | `## Hypothèse`, `## Référence à battre`, `## Données et découpage`, `## Mesures fixées avant l'essai`, `## Résultat`, `## Décision` |
| `recherche` | `docs/research/` | `type, id, titre, date, statut` | `statut` ∈ `brouillon, relue, validee` | `## Question`, `## Méthode`, `## Résultats`, `## Recommandation`, `## Questions ouvertes`, `## Sources` |

Les fichiers `README.md` de ces dossiers ne sont pas des fiches. Un champ non pertinent s'écrit `non applicable`, jamais vide. Les valeurs `TODO`, `TBD`, `?`, `...` et `<à compléter>` comptent comme absentes.

## 3. Rigueur scientifique

- Aucune affirmation de qualité sans score face à une référence (au minimum le modèle brut).
- Vérification sur des **saisons entières mises de côté**, jamais sur des jours voisins des données d'entraînement.
- Uniquement les données réellement disponibles au moment de l'émission de la prévision : pas de fuite du futur.
- Mesures et seuils de réussite fixés **avant** l'essai ; incertitude estimée par blocs temporels.
- Toujours distinguer **observé**, **modélisé** et **prévu** ; l'incertitude est affichée.
- Les faits instables (licences, accès, versions, quotas) sont vérifiés sur la source primaire et datés. Dans les rapports, chaque affirmation porte sa source et sa date de consultation, et est marquée **[vérifié]** (constaté par nous), **[producteur]** (documentation officielle du producteur), **[tiers]** (autre source) ou **[hypothèse]**.
- Code scientifique : skill `scientific-coding` ; relecture par l'agent `relecteur-scientifique`.

## 4. Continuité

Le dépôt garde la mémoire, pas le fil de discussion.

- `STATUS.md` décrit ce qui existe et fonctionne réellement, avec la date.
- `NEXT.md` donne la prochaine action. Chaque session commence par le lire et se termine par le mettre à jour.
- Les choix structurants vont dans `docs/decisions/` (format : contexte, décision, conséquences, date ; fichiers `NNNN-titre.md`).
- Une recherche faite n'est jamais refaite, seulement mise à jour.
- Les **issues GitHub** sont le seul outil de suivi, avec un jalon par sous-projet (`SP0 — Fondations` à `SP6 — Produits`) et des étiquettes par type (`recherche`, `source`, `experience`, `code`, `docs`).

## 5. Langues

- Code, noms de fonctions, commentaires, messages de CLI et API : **anglais**.
- README : anglais (`README.md`) et français (`README.fr.md`).
- Cadrages, plans, méthode, fiches, rapports et documents de pilotage : **français**.

## 6. Garde-fous

- **Zéro euro**, calcul et hébergement compris : tout nouveau service doit être gratuit et répondre à un besoin nommé. Exclus : Hugging Face Jobs, Sandboxes, Inference Endpoints, création de Spaces ZeroGPU, services météo payants ou propriétaires.
- **Aucun compte** créé sur un service tiers ni contact extérieur sans accord du pilote. Si un accès exige un compte, la fiche l'indique (`acces: compte gratuit requis`) et le test s'arrête là.
- **Tests d'accès** : 50 Mo téléchargés au plus par test ; seules des métadonnées de moins de 100 Ko peuvent être commitées.
- **Aucun secret**, jeton ou lien signé dans Git. Le dépôt est public : chaque PR est vérifiée pour l'absence de secret et de contenu non redistribuable.
- **Jamais de verdict de sécurité avalanche.** Le bulletin d'estimation du risque d'avalanche (BRA) de Météo-France reste la référence et est toujours cité comme tel.
- **Licences** : code Apache-2.0 ; données, modèles et documentation produits par le projet CC-BY-4.0 ; données dérivées d'OpenStreetMap sous ODbL. Toute réutilisation respecte la licence de la source : une page publique n'est pas une licence.
- **Modèles Claude** désignés par famille (`opus`, `sonnet`, `haiku`), jamais par version.

## 7. Procédure Git

1. Une branche `claude/<sujet>` par tâche ou groupe de tâches, partie de `main` à jour.
2. Avant de pousser : `python3 -m unittest discover -s scripts -p 'test_*.py'` et `python3 scripts/check_docs.py` (puis les tests du code Python à partir de SP1).
3. Chaque message de commit finit par les lignes `Co-Authored-By` et `Claude-Session` de la session.
4. Une PR par branche, ouverte par l'API REST de GitHub (GraphQL est bloqué depuis les sessions cloud) : `gh api repos/louistouquet/PowAtlas/pulls -f title=... -f head=... -f base=main -f body=...`, ou les outils GitHub MCP quand `gh` n'est pas disponible. La PR suit le modèle `.github/pull_request_template.md`.
5. Attendre le job `docs` vert, puis fusionner en un seul commit (*squash*).
6. Finir une PR en cours avant d'en ouvrir une autre.
