# PowAtlas — instructions pour Claude

PowAtlas : système open source pour comprendre et prévoir la neige en montagne (Alpes françaises d'abord), appuyé sur des scores publics. Dépôt public `louistouquet/PowAtlas`.

## Début de session
1. Lire `NEXT.md`, puis `STATUS.md`, puis le cadrage (`docs/specs/`) et le plan (`docs/plans/`) en cours.
   Transmettre au pilote les « PowAtlas reminders » affichés au démarrage (`scripts/reminders.py`) ; mettre à jour [`docs/collecte/rappels.toml`](docs/collecte/rappels.toml) dès qu'il annonce une action faite (dernier `sync`, jeton renouvelé, rattrapage fini).
2. `git status`, branche courante, PR ouvertes. Finir une PR en cours avant d'en ouvrir une autre.
3. Respecter les « Contraintes globales » du plan en cours (ex. en SP0 : pas de code produit, emprise de travail des Alpes françaises).
4. Méthode complète : [`docs/methode.md`](docs/methode.md). Modèles et économie : [`docs/modeles-claude.md`](docs/modeles-claude.md).

## Garde-fous (non négociables)
- **Zéro euro** : uniquement des offres gratuites ; pas de Hugging Face Jobs, Sandboxes, Inference Endpoints ni Spaces ZeroGPU ; pas de service météo payant.
- **Comptes** : tous les comptes gratuits sont autorisés, mais seul le pilote les crée ; jetons dans les secrets GitHub ou un fichier local ignoré par Git, jamais dans le dépôt. **Aucun contact extérieur** : recherche documentaire à la place.
- **Tests d'accès** : 50 Mo au plus par test ; seules des métadonnées de moins de 100 Ko sont commitées.
- **Aucune donnée dans Git** : archive de référence sur la machine du pilote (`D:\Codage\PowAtlas\data`).
- **Décisions du pilote** : [`docs/decisions/`](docs/decisions/README.md) ; elles priment sur les cadrages antérieurs.
- **Aucun secret**, jeton ou lien signé dans Git (dépôt public).
- **Jamais de verdict de sécurité avalanche** ; le BRA de Météo-France est cité comme référence.
- **Licences** : code Apache-2.0 ; productions du projet CC-BY-4.0 ; dérivés d'OpenStreetMap ODbL ; toute donnée tierce suit sa licence (une page publique n'est pas une licence).
- **Rigueur** : aucune affirmation de qualité sans score face à une référence ; saisons entières mises de côté ; pas de fuite du futur ; observé / modélisé / prévu toujours distingués ; faits instables vérifiés sur la source primaire et datés.
- **Agents** : modèles désignés par famille (`opus`, `sonnet`, `haiku`), jamais par version.
- **Langues** : code, commentaires et CLI en anglais ; README en anglais et en français ; cadrages, plans, fiches et rapports en français.

## Outils
- Articles : **alphaXiv** (MCP) en priorité.
- Modèles et jeux de données : **Hugging Face** (MCP, skills `huggingface-*`).
- Web : **Exa** dans le budget de 10 $ par mois (recherches ciblées, pas d'agent Exa, 15 recherches au plus par mandat), sinon recherche web intégrée.
- Code scientifique : skill **`scientific-coding`** obligatoire.
- Méthode : skills *superpowers* (cadrage, plans, TDD, vérification, relecture) ; `deep-research` pour les grosses recherches.
- Projet : skills `qualifier-source` et `experience-modele` (`.claude/skills/`) ; agents `chercheur-sources` et `relecteur-scientifique` (`.claude/agents/`).

## Fiches
Sources (`docs/sources/`), expériences (`docs/experiments/`), rapports (`docs/research/`) : formats dans [`docs/methode.md`](docs/methode.md#2-fiches). Aucune donnée sans fiche source ; aucun essai sans fiche d'expérience.

## Vérifications
```bash
python3 -m unittest discover -s scripts -p 'test_*.py' -v   # tests du vérificateur
python3 scripts/check_docs.py                                 # liens et fiches → "OK: ..."
.venv/bin/python -m unittest discover -s tests -v              # tests du paquet powatlas (.venv créé par scripts/session-start.sh)
```

## Git
- Une branche `claude/<sujet>` par tâche, une PR par l'API REST (`gh api repos/louistouquet/PowAtlas/pulls ...` ; GraphQL bloqué) ou les outils GitHub MCP.
- CI `docs` verte, relecture par un agent, fusion en un seul commit (*squash*).
- Messages de commit terminés par les lignes `Co-Authored-By` et `Claude-Session` de la session.
- Ne jamais fusionner sans accord du pilote un document qui le demande (cadrage, `docs/roadmap.md`).

## Fin de session
Cocher les étapes terminées dans le plan, mettre à jour `STATUS.md` (ce qui marche) et `NEXT.md` (prochaine action).
