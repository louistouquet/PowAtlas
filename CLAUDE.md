# PowAtlas — instructions pour Claude (version d'amorçage)

Cette version sera remplacée par la tâche 2 du plan SP0.

## Début de session
1. Lire `NEXT.md`, puis le cadrage `docs/specs/2026-10-21-sp0-fondations-design.md` et le plan `docs/plans/2026-10-21-sp0-fondations.md`.
2. `git status`, branche courante, PR ouvertes (`gh api repos/louistouquet/PowAtlas/pulls`). Finir une PR en cours avant d'en ouvrir une autre.
3. Respecter les « Contraintes globales » du plan : zéro euro, aucun compte tiers créé sans accord, aucun secret dans Git, jamais de verdict de sécurité avalanche, modèles désignés par famille (`opus`, `sonnet`, `haiku`).

## Exécution
- Méthode choisie par le pilote : **session pilote** (skill `superpowers:executing-plans`). Les recherches R0 (tâches 7 à 11) partent dans des agents parallèles comme le plan l'indique ; un relecteur indépendant vérifie l'ensemble à la fin.
- Une branche `claude/<sujet>` par tâche, PR par l'API REST (GraphQL bloqué), CI verte, fusion en un seul commit.

## Fin de session
Cocher les étapes terminées dans le plan, mettre à jour `NEXT.md` (et `STATUS.md` quand il existera).
