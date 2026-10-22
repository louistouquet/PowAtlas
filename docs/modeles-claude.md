# Modèles Claude, niveaux d'effort et économie

Ce document fixe quel modèle Claude fait quoi, à quel niveau d'effort, et comment limiter la consommation. Il découle de la section 6 du [cadrage SP0](specs/2026-10-21-sp0-fondations-design.md).

## Règle : modèles par famille

Les définitions d'agents (`.claude/agents/*.md`) et les documents du projet désignent les modèles par **famille** — `opus`, `sonnet`, `haiku` — et **jamais par version**. Elles suivent ainsi automatiquement les nouvelles versions.

**Relecture :** ce tableau est relu à chaque nouvelle génération de modèles Claude (nouveaux niveaux d'effort, nouveaux rapports coût / capacité). La relecture est notée dans `docs/decisions/` si elle change une affectation.

## Rôles

| Rôle | Modèle | Effort |
|---|---|---|
| Pilote technique : cadrage, architecture, consolidation, intégration | Opus | high (xhigh pour les cadrages) |
| Grands arbitrages : architecture IA (SP5), synthèses finales de recherche, protocole de vérification | Opus | xhigh (max pour les décisions les plus critiques) |
| Agents de recherche : web, articles, synthèse | Sonnet | medium |
| Tri de masse : inventaires, contrôle de liens et de licences | Haiku | low |
| Code courant | Sonnet | medium |
| Code scientifique critique : scores, réduction d'échelle, apprentissage | Opus | high |
| Relecteur scientifique (`relecteur-scientifique`) | Opus | high |
| Relecture de code standard | Sonnet | high |

## Règles d'économie de tokens

1. Commencer au modèle le moins cher qui suffit ; monter d'un cran seulement si la relecture trouve des problèmes.
2. Les lectures lourdes partent dans des agents qui rendent une synthèse sourcée.
3. Toute recherche est écrite dans le dépôt ; une recherche faite n'est jamais refaite, seulement mise à jour.
4. Chaque agent reçoit un mandat précis : question, format de sortie, nombre maximal de sources, fichiers qu'il a le droit d'écrire.
5. Au-delà de 3 agents en parallèle, feu vert explicite du pilote (déjà donné pour R0, environ 7 agents).
6. `CLAUDE.md` reste court ; les skills se chargent à la demande.

## Budget Exa

- Exa est utilisé dans la limite des **10 $ de crédits gratuits mensuels**, sans aucun moyen de paiement enregistré.
- Recherches ciblées (`web_search_exa`, `web_fetch_exa`) plutôt que l'agent Exa, plus coûteux.
- Plafond par mandat d'agent : 15 recherches Exa.
- **Bascule :** si le quota est atteint (erreur de crédit ou de quota), on passe à la recherche web intégrée (`WebSearch`, `WebFetch`) jusqu'au mois suivant, et on le note dans le rapport en cours.

## Autres outils de recherche

- **alphaXiv** (MCP) : source principale pour les articles scientifiques (recherche, texte intégral, questions sur PDF, code associé).
- **Hugging Face** (MCP et skills) : recherche de modèles et de jeux de données ; plus tard, éventuellement, publication de l'archive et des modèles du projet ([décision 0004](decisions/0004-calcul-et-hebergements-gratuits.md)).
- Recherche web intégrée : complément, et repli quand Exa est épuisé.
