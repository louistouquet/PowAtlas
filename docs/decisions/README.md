# Décisions

Ce dossier garde les choix structurants du projet : ceux qu'on ne veut pas rediscuter à chaque session, ou dont il faut retrouver la raison plus tard (voir [`../methode.md`](../methode.md), section « Continuité »).

## Format

Un fichier par décision, nommé `NNNN-titre.md` : numéro sur 4 chiffres, croissant et jamais réutilisé, puis un titre court en minuscules avec tirets (ex. `0001-licence-des-donnees.md`).

```markdown
# NNNN — Titre de la décision

Date : AAAA-MM-JJ · Statut : proposée | acceptée | remplacée par NNNN

## Contexte
Le problème, les contraintes, les options envisagées.

## Décision
Ce qui est décidé, en une ou deux phrases.

## Conséquences
Ce que la décision rend plus facile, plus difficile, et ce qu'il faudra surveiller.
```

Une décision n'est jamais effacée : si elle change, une nouvelle décision la remplace et l'ancienne passe en `remplacée par NNNN`.

## Liste

| N° | Décision | Date | Statut |
|---|---|---|---|
| [0001](0001-archive-sur-la-machine-du-pilote.md) | Archive de référence sur la machine du pilote ; aucune donnée dans Git | 2026-10-21 | acceptée |
| [0002](0002-comptes-gratuits-et-secrets.md) | Comptes gratuits autorisés, créés par le pilote ; secrets hors du dépôt | 2026-10-22 | acceptée |
| [0003](0003-aucun-contact-exterieur.md) | Aucun contact extérieur ; recherche documentaire à la place | 2026-10-22 | acceptée |
| [0004](0004-calcul-et-hebergements-gratuits.md) | Calcul d'entraînement et hébergements : le meilleur du gratuit | 2026-10-22 | acceptée |
| [0005](0005-collecte-hybride-actions-et-pc.md) | Collecte hybride : GitHub Actions collecte, le PC du pilote archive | 2026-10-22 | acceptée |

