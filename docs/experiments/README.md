# Fiches d'expérience

Une fiche par essai de modèle (correction statistique, réduction d'échelle, combinaison de modèles, manteau neigeux, IA). **Aucun essai sans fiche, et les échecs sont conservés.**

La fiche fixe **avant l'essai** l'hypothèse, la référence à battre, les données et le découpage (saisons entières mises de côté, données disponibles à l'heure d'émission), les scores et le seuil de réussite. Elle reçoit ensuite le résultat, avec son incertitude, et la décision (garder, modifier, abandonner) avec sa condition de réexamen.

- Procédure et modèle : skill [`experience-modele`](../../.claude/skills/experience-modele/SKILL.md) et son [modèle](../../.claude/skills/experience-modele/template.md) ; relecture par l'agent `relecteur-scientifique`.
- Format vérifié en CI par `scripts/check_docs.py` : voir [`../methode.md`](../methode.md#2-fiches).
- Statuts : `prevue`, `en-cours`, `terminee`, `abandonnee`. Champ `fictive: oui` pour les exemples.

| Fiche | Statut | Note |
|---|---|---|
| [`exemple-fictif-correction-neige-fraiche.md`](exemple-fictif-correction-neige-fraiche.md) | prevue | **Exemple fictif**, aucun résultat réel |
