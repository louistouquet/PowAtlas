# 0007 — SP2 : GitHub d'abord, Hugging Face au centre

Date : 2026-10-27 · Statut : acceptée (choix du pilote du 2026-10-27, sur recommandation de Claude ; les détails restent à fixer dans le cadrage SP2)

## Contexte
SP2 doit publier un tableau des scores de la neige fraîche des modèles bruts ([feuille de route](../roadmap.md), « Vérité terrain et tableau des scores »). Le 2026-10-27, le pilote a d'abord décidé : un seul code, l'historique d'abord (IFS, AIFS, GFS), puis la saison 2026-27, avec des scores calculés sur son PC. Plus tard le même jour, il a précisé :
- tout ce qui peut tourner sur GitHub y tourne, car GitHub tourne chaque jour et son PC n'est pas allumé tous les jours ;
- la publication se fait sur Hugging Face, configuré pour l'ensemble du projet ;
- ce que les rapports R0 et la feuille de route ont déjà tranché n'est pas reposé au pilote.

L'archive découpée sur l'emprise pèse 0,28 Go le 2026-10-27, rattrapage inachevé [vérifié par le pilote]. C'est bien moins que les 55 Go par saison de champs entiers estimés pour la [décision 0001](0001-archive-sur-la-machine-du-pilote.md). Faits relevés le 2026-10-27 dans la documentation de Hugging Face [producteur] :
- stockage public gratuit « best-effort », à utiliser avec retenue au-delà de « quelques gigaoctets » ;
- par dépôt, moins de 100 000 fichiers et moins de 10 000 entrées par dossier sont conseillés ;
- GitHub Actions peut écrire sans jeton stocké (« Trusted Publishers ») ([guide](../collecte/hugging-face.md)).

## Décision
- **Calcul sur GitHub Actions** dès que possible : extraction des prévisions aux stations, observations de Météo-France, scores. Cette règle remplace « calcul des scores sur le PC du pilote ». Le PC ne fait que ce que GitHub ne peut pas faire : rattrapage massif sur AWS ([décision 0006](0006-rattrapage-sur-le-pc-automatique.md)), GFS, et Arpa Piemonte, qui ne répond qu'au PC.
- **Organisation Hugging Face `PowAtlas`**, créée par le pilote ([décision 0002](0002-comptes-gratuits-et-secrets.md)), avec deux jeux publics :
  - `PowAtlas/archive` : copie publique de l'archive. GitHub Actions y dépose les unités qu'il collecte ; le PC, ce que lui seul collecte. Les fichiers sont regroupés (par source et par période) pour rester sous les limites de fichiers.
  - `PowAtlas/scores` : paires prévision/observation et tableaux de scores, calculés par GitHub Actions.
- **Archive de référence inchangée** : elle reste sur le PC ([décision 0001](0001-archive-sur-la-machine-du-pilote.md)). Hugging Face en est la copie publique, sans garantie de durée. Toujours aucune donnée dans Git.
- **Un seul code**, l'historique d'abord, puis la saison 2026-27 (décision du pilote du 2026-10-27).

## Conséquences
- Avant le premier envoi sur `PowAtlas/archive`, chaque source envoyée a une fiche dont la licence autorise la redistribution, vérifiée sur la page du producteur et datée. L'attribution exigée figure dans la fiche du jeu de données (`README.md`).
- Le cadrage SP2 fixe : le regroupement des fichiers, la fiche des jeux, les workflows (`collect.yml` reçoit `id-token: write` ; nouveau `scores.yml`), `huggingface_hub` 1.19 ou plus récent, et la commande d'envoi du PC.
- Si Hugging Face limite le stockage gratuit, le calcul de GitHub Actions perd sa source d'archive, mais l'archive du PC reste intacte. Le repli est à qualifier parmi d'autres offres gratuites ([décision 0004](0004-calcul-et-hebergements-gratuits.md)).
- La publication publique de l'archive, fonctionnalité de rang 2 reportée par la décision 0001, commence donc en SP2.
