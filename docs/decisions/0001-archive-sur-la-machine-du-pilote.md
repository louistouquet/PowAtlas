# 0001 — Archive de référence sur la machine du pilote

Date : 2026-10-21 · Statut : acceptée

## Contexte
R0.2 chiffre l'archive des prévisions de 4,7 Go (run 00 UTC) à 55 Go par saison. GitHub ne convient pas aux données (5 Go recommandés par dépôt, Git LFS limité à 10 Gio) ; Hugging Face n'offre qu'un stockage public « best-effort », sans plafond garanti ; GitHub Actions ne garde ses artefacts que 90 jours au plus et ses conditions d'utilisation laissent un doute sur un téléchargement quotidien massif ([R0.2](../research/R0.2-previsions-ouvertes.md), [R0.5](../research/R0.5-briques-open-source.md)).

## Décision
L'archive de référence et un clone complet du dépôt vivent sur la machine du pilote, dans `D:\Codage\PowAtlas` ; les données vont dans `D:\Codage\PowAtlas\data\`, ignoré par Git. **Aucune donnée ne va dans Git**, seulement le code et des métadonnées de moins de 100 Ko. Le lieu d'exécution de la collecte quotidienne (machine du pilote, GitHub Actions, ou les deux, option hybride recommandée) est la première décision du cadrage de SP1 ([roadmap, décision 8](../roadmap.md)).

## Conséquences
- Plus de limite de stockage liée à GitHub ou Hugging Face.
- La session cloud ne peut pas écrire sur cette machine : le pilote y lance le code de SP1.
- Nouveaux risques : machine éteinte (runs ICON perdus après 24 h) et disque unique (sauvegarde à prévoir).
- La publication publique de l'archive (fonctionnalité de rang 2) est reportée et sera qualifiée parmi les offres gratuites.
