# Hugging Face : mise en place par le pilote

Guide du 2026-10-27. Architecture retenue par le pilote le 2026-10-27 pour SP2 et la suite du projet : [décision 0007](../decisions/0007-hugging-face-au-centre-github-d-abord.md) ; détails fixés par le cadrage SP2 (à venir).

- `PowAtlas/archive` : la copie publique de l'archive, fichiers regroupés par source et par période (limites de fichiers ci-dessous). GitHub Actions y dépose chaque unité complète à la collecte ; le PC du pilote y envoie ce que lui seul collecte (rattrapage historique, GFS, Arpa Piemonte).
- `PowAtlas/scores` : les paires prévision/observation et les tableaux de scores, calculés par GitHub Actions.
- L'archive de référence reste sur le PC ([décision 0001](../decisions/0001-archive-sur-la-machine-du-pilote.md)). Celle de Hugging Face en est la copie publique, sans garantie de durée : elle ne remplace pas une sauvegarde du disque du PC.

Faits vérifiés le 2026-10-27 dans la documentation de Hugging Face :
- stockage public gratuit « best-effort », sans plafond garanti, à utiliser avec retenue au-delà de « quelques gigaoctets » ; par dépôt, moins de 100 000 fichiers et moins de 10 000 entrées par dossier, au plus 100 fichiers par envoi conseillés ([Storage limits](https://huggingface.co/docs/hub/storage-limits)) ;
- GitHub Actions peut écrire sans jeton stocké grâce aux « Trusted Publishers » : jeton d'une heure limité à un seul dépôt ([Trusted Publishers](https://huggingface.co/docs/hub/trusted-publishers)) ;
- le nom `PowAtlas` était libre (ni utilisateur ni organisation, réponse 404 de l'API).

Tout est gratuit : ne souscrire à aucune offre payante (PRO, Team, Enterprise). Ne jamais coller un jeton dans une session Claude, une issue ou un fichier du dépôt.

## 1. Créer l'organisation `PowAtlas`

1. Se connecter à huggingface.co avec le compte `LeTouq`.
2. Ouvrir https://huggingface.co/organizations/new.
3. Remplir :
   - *Organization Username* : `PowAtlas` ;
   - *Organization Full name* : `PowAtlas` ;
   - type : le choix le plus proche de « communauté » ou « open source » ;
   - site ou GitHub : `https://github.com/louistouquet/PowAtlas` si le formulaire le demande.
4. Valider, en restant sur l'offre gratuite.

## 2. Créer les deux jeux de données

Pour chacun, ouvrir https://huggingface.co/new-dataset :

| Champ | Premier | Second |
|---|---|---|
| *Owner* | `PowAtlas` | `PowAtlas` |
| *Dataset name* | `archive` | `scores` |
| *License* | `cc-by-4.0` | `cc-by-4.0` |
| *Visibility* | *Public* | *Public* |

Claude écrira ensuite la description (fiche du jeu, `README.md`) par le code.

Pourquoi `cc-by-4.0` pour `archive` (choix du 2026-10-27, à confirmer avant le premier envoi) : les sources collectées sont sous CC BY 4.0 (DWD, ECMWF, SLF, Arpa Piemonte), Licence Ouverte 2.0 (Météo-France) ou données ouvertes de la NOAA sans restriction (GFS), d'après le catalogue et les fiches. La Licence Ouverte 2.0 se déclare compatible avec CC BY [producteur, à relire sur la page d'Etalab avant le premier envoi]. La fiche du jeu listera les deux licences (`cc-by-4.0`, `etalab-2.0`, identifiants reconnus par Hugging Face) et, source par source, la licence d'origine et l'attribution exigée. `other` n'est utile que si une source impose une licence incompatible.

## 3. Autoriser GitHub Actions (sans jeton)

Sur chacun des deux jeux : page du jeu → *Settings* → *Trusted Publishers* → ajouter :

| Champ | `PowAtlas/archive` | `PowAtlas/scores` |
|---|---|---|
| *Provider* | GitHub Actions | GitHub Actions |
| `repository` | `louistouquet/PowAtlas` | `louistouquet/PowAtlas` |
| `branch` | `main` | `main` |
| `workflow` | `collect.yml` | `scores.yml` |

`scores.yml` n'existe pas encore : il sera écrit en SP2, sous ce nom. Côté dépôt, le plan SP2 ajoutera `id-token: write` aux permissions des deux workflows et `huggingface_hub` 1.19 ou plus récent. Le champ `branch = main` réserve l'écriture aux runs de `main` (un `workflow_dispatch` lancé depuis une autre branche sera refusé, c'est voulu). Si la rubrique *Trusted Publishers* n'apparaît pas, le dire dans une session : le repli est un jeton à droits limités rangé dans les secrets GitHub.

## 4. Jeton du PC (écriture sur `PowAtlas/archive` seulement)

1. Ouvrir https://huggingface.co/settings/tokens → *Create new token* → onglet *Fine-grained*.
2. *Token name* : `PowAtlas PC`.
3. *Repositories permissions* : chercher et choisir `datasets/PowAtlas/archive`, cocher l'écriture sur le contenu de ce dépôt (*Write access to contents/settings of selected repos*), et rien d'autre (aucune case dans *User permissions* ni *Org permissions*).
4. Créer, puis copier le jeton (`hf_...`) dans `D:\Codage\PowAtlas\.env` (ignoré par Git, jamais commité), sur une nouvelle ligne :

   ```text
   HF_TOKEN=hf_...
   ```

## 5. Contrôle

Dire dans une session que les étapes 1 à 4 sont faites. Claude vérifie depuis la session, sans jeton, que l'organisation existe (`https://huggingface.co/api/organizations/PowAtlas/overview` répond 200, et non 404) et que les pages des deux jeux s'affichent. Le jeton du PC est testé par la première commande d'envoi du plan SP2. Rien n'est envoyé avant que les licences de chaque source envoyée soient vérifiées et datées dans sa fiche ([décision 0007](../decisions/0007-hugging-face-au-centre-github-d-abord.md)).
