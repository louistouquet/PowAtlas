---
type: experience
id: exemple-fictif-correction-neige-fraiche
titre: Correction statistique de la neige fraîche à 24 h prévue par AROME (exemple fictif)
statut: prevue
date: 2026-10-21
fictive: oui
reference: AROME brut, cumul de neige à 24 h au point de grille le plus proche
---

# Correction statistique de la neige fraîche à 24 h prévue par AROME

> **Exemple fictif, aucun résultat réel.** Cette fiche illustre le format et le protocole du skill `experience-modele`. Aucun modèle, aucune donnée et aucun score n'existent encore dans PowAtlas ; les sources citées n'ont pas encore leurs fiches, et les faits qui en dépendent sont marqués [hypothèse].

## Hypothèse

Une régression quantile par gradient boosting qui prend en entrée la prévision AROME (cumul de neige et de précipitations, température à 2 m, isotherme 0 °C, vent à 10 m), l'altitude de la station et l'écart d'altitude entre la station et le point de grille réduit l'erreur sur la **neige fraîche à 24 h** aux stations nivo-météorologiques des Alpes françaises. Prévision émise à 06 UTC le jour J à partir du run de 00 UTC, pour la fenêtre 06 UTC J → 06 UTC J+1 (0 à 24 h après l'émission ; échéances 6 à 30 h du run). Raison : malgré sa résolution fine (environ 1,3 km [hypothèse], à confirmer par la fiche source AROME), AROME lisse encore le relief ; on s'attend à un biais lié à l'altitude et aux situations de retour d'est.

## Référence à battre

1. AROME brut : cumul de neige prévu entre les échéances 6 et 30 h au point de grille le plus proche de chaque station, converti en hauteur avec une densité fixe de 100 kg/m³ [hypothèse : valeur usuelle de neige fraîche, à sourcer en R3].
2. AROME corrigé linéairement du biais en fonction de l'écart d'altitude grille-station, appris sur les saisons d'entraînement seulement.

Pour le score de Brier, la probabilité de la référence 1 vaut 1 si la prévision dépasse 20 cm, 0 sinon. Score attendu de la référence : inconnu tant que l'archive n'existe pas ; il sera calculé sur les saisons de validation avant l'essai et noté ici.

## Données et découpage

- Données d'entrée : prévisions AROME archivées, run de 00 UTC, échéances 6 à 30 h (fiche source à créer). Disponibilité d'une archive gratuite couvrant les saisons ci-dessous : [hypothèse], à confirmer par la fiche source ; l'archive doit reproduire ce qui était diffusé en temps réel (pas de fichiers retraités).
- Vérité terrain : neige fraîche à 24 h relevée le **matin du jour J+1** (fenêtre 06 UTC J → 06 UTC J+1, heure exacte du relevé à préciser dans la fiche source) aux stations du réseau nivo-météorologique de plus de 1 000 m (fiche source à créer). Liste des stations et traitement des valeurs manquantes (jour exclu pour la station concernée) fixés avant l'essai.
- Disponibilité à l'heure d'émission : le run AROME de 00 UTC doit être disponible avant 06 UTC [hypothèse], à vérifier par le champ `delai` de la fiche source AROME. Le relevé du matin du jour J, connu à l'émission, peut servir d'entrée ; aucune observation postérieure à 06 UTC J n'est utilisée.
- Entraînement : saisons d'hiver complètes (1er décembre au 30 avril) 2018-19 à 2022-23.
- Validation (réglage des hyperparamètres et score de la référence) : saison 2023-24.
- Test (mis de côté, touché une seule fois, à la fin) : saison 2024-25, la plus récente, pour se placer dans la version d'AROME la plus proche de l'usage réel.
- Limite : AROME a changé de version au cours de la période [hypothèse, à dater dans la fiche source] ; la relation apprise peut ne pas être stationnaire.

## Mesures fixées avant l'essai

- Scores : erreur absolue moyenne (MAE, en cm) de la médiane prévue et biais moyen, sur tous les jours et séparément sur les jours avec neige observée (≥ 1 cm) ; score de Brier de l'événement « plus de 20 cm » (probabilité tirée des quantiles prévus).
- Seuil de réussite, sur la saison de test : la borne inférieure de l'intervalle à 95 % de la réduction relative de MAE (tous jours) face à la meilleure des deux références est au moins de 10 %, et la borne supérieure de l'intervalle de l'écart de Brier (modèle moins référence) est inférieure ou égale à 0,005.
- Incertitude : intervalles à 95 % par rééchantillonnage par blocs de 7 dates consécutives de la saison de test (1 000 tirages), chaque bloc gardant toutes les stations de ces dates ; même méthode pour la MAE, le biais et le Brier.
- Commit de cette fiche avant l'essai : sans objet (exemple fictif) ; forme attendue : `<sha court>` du AAAA-MM-JJ, statut `prevue`.

## Résultat

Aucun : exemple fictif, l'essai n'a pas eu lieu.

## Décision

- Décision : sans objet tant que l'essai n'a pas eu lieu.
- Raison : exemple fictif.
- Condition de réexamen : quand l'archive AROME et les observations nivo-météorologiques couvriront au moins les sept saisons du découpage (cinq d'entraînement, une de validation, une de test).
- **Note de relecture (2026-10-21).** La première version de cette fiche contenait volontairement une faille : les jours d'entraînement, de validation et de test étaient tirés au hasard (70 / 15 / 15 %) dans les mêmes saisons. L'agent `relecteur-scientifique` l'a classée `bloquant` : des jours voisins d'une même perturbation se retrouvent dans l'entraînement et dans le test, ce qui gonfle le score (fuite par autocorrélation). Le découpage est maintenant fait par saisons entières distinctes. La même relecture a fait préciser la fenêtre de la cible, la disponibilité des entrées, la sortie probabiliste, le seuil de réussite et le rééchantillonnage par dates communes à toutes les stations.
