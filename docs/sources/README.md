# Fiches sources

Une fiche par source de données (prévisions, observations, réanalyses, satellite, relief). **Aucune donnée n'entre dans le projet sans sa fiche.**

Une fiche dit ce que contient la source, sous quelle licence exacte, comment y accéder (compte requis ou non), avec quels quotas, quel délai de mise à disposition, quelle résolution et quelle durée de conservation, et ce qu'un **test réel d'accès** a montré (date, commande, taille, résultat). Chaque affirmation est marquée **[vérifié]**, **[producteur]**, **[tiers]** ou **[hypothèse]** et datée.

- Procédure et modèle : skill [`qualifier-source`](../../.claude/skills/qualifier-source/SKILL.md) et son [modèle](../../.claude/skills/qualifier-source/template.md) ; agent `chercheur-sources`.
- Format vérifié en CI par `scripts/check_docs.py` : voir [`../methode.md`](../methode.md#2-fiches).
- Statuts : `retenue` (utilisée par le projet), `ecartee` (avec la raison), `a-tester` (accès ou licence à confirmer).
- Les sources `retenue` sont reportées dans [`DATA_LICENSES.md`](../../DATA_LICENSES.md) quand leurs données sont intégrées.
