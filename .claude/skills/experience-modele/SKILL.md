---
name: experience-modele
description: Use to prepare, run or conclude a model experiment (préparer, mener ou conclure un essai de modèle) in PowAtlas — forecast correction, downscaling, blending, snowpack or AI model trials. Produces an experiment record in docs/experiments/ with metrics fixed before the trial.
---

# Mener un essai de modèle

Tout essai de modèle a sa **fiche d'expérience** (`docs/experiments/<id>.md`). Elle fixe ce qu'on teste et comment on jugera **avant** de regarder le moindre résultat, puis garde le résultat et la décision, y compris en cas d'échec. Format : [`docs/methode.md`](../../../docs/methode.md#2-fiches). Modèle : [`template.md`](template.md). Code scientifique : skill `scientific-coding`.

## Protocole

1. **Hypothèse.** Une phrase testable : quelle amélioration, sur quelle variable (ex. neige fraîche à 24 h), quelle zone, quelles échéances, et pourquoi on y croit.
2. **Référence à battre.** Au minimum le modèle brut le plus simple disponible (ex. AROME brut au point de grille le plus proche). Une méthode qui ne bat pas la référence n'entre pas en production.
3. **Découpage par saisons entières.** Entraînement, validation et test sont des **saisons d'hiver complètes et distinctes** (ex. entraînement 2016-17 à 2022-23, validation 2023-24, test 2024-25). Jamais de jours tirés au hasard : des jours voisins partagent les mêmes situations météo et le score serait gonflé. Le jeu de test n'est touché qu'**une fois**, à la fin.
4. **Pas de fuite du futur.** Chaque donnée d'entrée doit avoir été **disponible à l'heure d'émission** de la prévision (délai de mise à disposition de la source, voir sa fiche). Pas de normalisation, de sélection de variables ni de réglage calculés sur la validation ou le test.
5. **Mesures fixées avant l'essai.** Scores (ex. erreur absolue moyenne, biais, CRPS, score de Brier pour un seuil), seuil de réussite face à la référence, méthode d'incertitude. Commiter la fiche à ce stade (statut `prevue`) et noter le commit dans la fiche.
6. **Mener l'essai** (statut `en-cours`) sans changer les mesures. Tout changement de protocole est noté et daté dans la fiche.
7. **Résultat avec incertitude.** Scores du modèle et de la référence sur le test, avec un intervalle obtenu par **rééchantillonnage par blocs temporels** (ex. blocs de 7 jours) pour respecter la dépendance entre jours voisins. Distinguer observé, modélisé et prévu.
8. **Décision** : garder, modifier ou abandonner, avec la raison et une **condition de réexamen** (ex. « après une saison supplémentaire d'archive »). Statut `terminee` ou `abandonnee`.
9. **Conserver les échecs.** Une fiche n'est jamais supprimée : un essai raté évite de le refaire.
10. **Relecture** par l'agent `relecteur-scientifique` avant la décision, puis `python3 scripts/check_docs.py` → `OK`.

Jamais de verdict de sécurité avalanche dans une fiche ou un résultat.
