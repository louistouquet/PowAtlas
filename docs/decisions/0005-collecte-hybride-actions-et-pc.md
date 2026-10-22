# 0005 — Collecte hybride : GitHub Actions collecte, le PC du pilote archive

Date : 2026-10-22 · Statut : acceptée

## Contexte
La collecte quotidienne doit tourner tout l'hiver sans session Claude ([roadmap, décision 8](../roadmap.md)). Trois lieux étaient possibles : le PC du pilote seul (aucun doute sur les conditions d'utilisation, mais un PC éteint plus de 24 h perd les runs ICON), GitHub Actions seul (pas de stockage durable : artefacts de 90 jours au plus, contraire à la [décision 0001](0001-archive-sur-la-machine-du-pilote.md)), ou les deux. Les conditions d'utilisation d'Actions laissent un doute sur un téléchargement quotidien de plusieurs Go ([R0.2](../research/R0.2-previsions-ouvertes.md)).

## Décision
Option hybride : **GitHub Actions collecte chaque jour** les sources à conservation courte (ICON, AROME, ARPEGE, ECMWF du portail, observations à 7 jours, copies Météo-France) et dépose des artefacts gardés 90 jours ; **le PC du pilote les rapatrie** dans `D:\Codage\PowAtlas\data\` et fait tout ce qui reste disponible sur AWS (rattrapage historique, IFS ENS, GFS). Si GitHub conteste l'usage d'Actions, la collecte bascule immédiatement sur le PC seul, avec le même code.

## Conséquences
- La collecte démarre dès la fusion sur `main`, sans attendre l'installation du PC ; un PC éteint plusieurs semaines ne perd rien tant qu'il rapatrie avant 90 jours.
- Le pilote crée un jeton GitHub à grain fin, en lecture seule, limité au dépôt, pour télécharger les artefacts ; il reste dans un fichier local ignoré par Git.
- Aucune astuce de maintien artificiel du workflow planifié : l'activité vient du développement réel ; le PC alerte si aucun artefact n'arrive pendant 48 h.
- Charge d'Actions limitée aux sources qui l'exigent (environ 2 Go par jour au cœur, 3,3 Go avec la priorité 2) ; les gros volumes d'AWS passent par le PC.
- Détails : [cadrage SP1](../specs/2026-10-22-sp1-archive-design.md).
