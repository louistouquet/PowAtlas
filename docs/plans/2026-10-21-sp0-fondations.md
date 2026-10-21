# SP0 — Plan de mise en œuvre des fondations

> **Pour les agents exécutants :** SOUS-SKILL REQUIS : `superpowers:subagent-driven-development` (recommandé) ou `superpowers:executing-plans` pour exécuter ce plan tâche par tâche. Les étapes utilisent des cases à cocher (`- [ ]`).

**Objectif :** livrer le dépôt PowAtlas outillé (règles, agents, skills, CI, GitHub) et la recherche R0 qui aboutit au document « Cible et feuille de route » validé par le pilote.

**Architecture :** un dépôt de documentation et de configuration, sans code produit. Un seul script d'outillage (`scripts/check_docs.py`, bibliothèque standard Python uniquement) vérifie en CI les liens internes et la structure des fiches (source, expérience, recherche). La recherche R0 est conduite par des agents dédiés qui écrivent des rapports et des fiches validés par ce script, puis relus par l'agent `relecteur-scientifique`.

**Pile :** Markdown, Python 3.12 (bibliothèque standard, `unittest`), GitHub Actions, Claude Code (agents `.claude/agents/`, skills `.claude/skills/`), MCP alphaXiv, Hugging Face, Exa.

**Cadrage :** [`docs/specs/2026-10-21-sp0-fondations-design.md`](../specs/2026-10-21-sp0-fondations-design.md). L'exécutant lit le cadrage et ce plan.

## Contraintes globales

- Zéro euro. Aucun service payant. Exa : 10 $ de crédits gratuits par mois, aucun moyen de paiement ; recherches ciblées, pas d'agent Exa. Exclus : Hugging Face Jobs, Sandboxes, Inference Endpoints, création de Spaces ZeroGPU.
- Aucun compte créé sur un service tiers sans accord du pilote. Si un accès exige un compte, la fiche l'indique (`acces: compte gratuit requis`) et le test s'arrête là.
- Tests d'accès : téléchargements de 50 Mo maximum par test ; seules des métadonnées de moins de 100 Ko peuvent être commitées.
- Aucun secret, jeton ou lien signé dans Git.
- Code, noms de fonctions, commentaires et messages de CLI en anglais. README en anglais et en français. Cadrages, plans, méthode, fiches et rapports en français.
- Licences : code Apache-2.0 ; données, modèles et documentation produits par le projet CC-BY-4.0 ; données dérivées d'OpenStreetMap sous ODbL.
- Jamais de verdict de sécurité avalanche ; le BRA de Météo-France est cité comme référence.
- Définitions d'agents : modèles par famille (`opus`, `sonnet`, `haiku`), jamais par version.
- Pas de code produit en SP0 (`src/`, `pyproject.toml`, hook de démarrage : SP1). Le seul code est `scripts/check_docs.py`, sans dépendance externe.
- Emprise de travail « Alpes françaises » pour R0 (WGS84, EPSG:4326) : ouest 5.0, sud 43.5, est 7.9, nord 46.5.
- Git : une branche `claude/<sujet>` par tâche ou groupe de tâches, une PR, CI verte, fusion en un seul commit (squash). Chaque message de commit finit par les lignes `Co-Authored-By` et `Claude-Session` de la session.
- Les PR passent par l'API REST (`gh api repos/louistouquet/PowAtlas/pulls ...`) : GraphQL est bloqué depuis les sessions cloud.

## Points de vigilance (non couverts par le cadrage, testés dans la tâche 1)

1. Un lien Markdown à l'intérieur d'un bloc de code ne doit pas être vérifié (faux positifs sur les exemples).
2. Un lien avec ancre ou titre (`a.md#section`, `a.md "titre"`) se résout vers le fichier `a.md`.
3. Un fichier avec fins de ligne Windows (CRLF) est analysé comme un fichier LF.
4. Une valeur de champ vide ou fictive (`TODO`, `TBD`, `?`, `...`, `<à compléter>`) compte comme absente.
5. Les modèles de fiches dans `.claude/skills/*/template.md` ne sont pas contrôlés comme des fiches (ils contiennent des valeurs fictives), mais leurs liens le sont.

## Formats des fiches (contrat partagé par les tâches 1, 4, 5 et 7 à 12)

Chaque fiche commence par un bloc d'en-tête `---` ... `---` de lignes `cle: valeur`. Le champ `id` est égal au nom du fichier sans `.md`. Les dates sont au format `AAAA-MM-JJ`.

| Type | Dossier | Champs obligatoires | Valeurs contraintes | Sections obligatoires |
|---|---|---|---|---|
| `source` | `docs/sources/` | `type, id, nom, producteur, licence, acces, quotas, delai, resolution, conservation, statut, verifie_le` | `statut` ∈ `retenue, ecartee, a-tester` | `## Contenu`, `## Test d'accès`, `## Limites` |
| `experience` | `docs/experiments/` | `type, id, titre, statut, date, fictive, reference` | `statut` ∈ `prevue, en-cours, terminee, abandonnee` ; `fictive` ∈ `oui, non` | `## Hypothèse`, `## Référence à battre`, `## Données et découpage`, `## Mesures fixées avant l'essai`, `## Résultat`, `## Décision` |
| `recherche` | `docs/research/` | `type, id, titre, date, statut` | `statut` ∈ `brouillon, relue, validee` | `## Question`, `## Méthode`, `## Résultats`, `## Recommandation`, `## Questions ouvertes`, `## Sources` |

Les fichiers `README.md` de ces dossiers ne sont pas des fiches. Un champ non pertinent s'écrit `non applicable`, jamais vide.

---

### Tâche 1 : vérificateur de documentation et CI

**Exécutant recommandé :** Sonnet, effort medium, skill `scientific-coding` non requis (outillage).

**Fichiers :**
- Créer : `scripts/check_docs.py`
- Créer : `scripts/test_check_docs.py`
- Créer : `.github/workflows/docs.yml`

**Interfaces :**
- Produit : la commande `python3 scripts/check_docs.py [--root CHEMIN]` qui code retour 0 si tout est valide, 1 sinon, et affiche chaque erreur sur une ligne `chemin/relatif:ligne: message`. En cas de succès, elle affiche `OK: <n> markdown files, <m> records checked`. Toutes les tâches suivantes l'exécutent comme vérification.
- Produit (dans `scripts/check_docs.py`) :
  - `parse_front_matter(text: str) -> dict[str, str] | None`
  - `iter_markdown_files(root: Path) -> list[Path]` (ignore `.git/`, triée)
  - `check_links(path: Path, root: Path) -> list[str]`
  - `check_record(path: Path, root: Path) -> list[str]` (contrôle de fiche selon le dossier, d'après le tableau « Formats des fiches »)
  - `main(argv: list[str] | None = None) -> int`

- [x] **Étape 1 : écrire les tests qui échouent** dans `scripts/test_check_docs.py` (`unittest`, chaque test crée son arborescence dans un `tempfile.TemporaryDirectory`) :

```python
class LinkTests(unittest.TestCase):
    def test_broken_relative_link_is_reported(self):        # link target "missing.md" absent -> 1 error containing "missing.md"
    def test_existing_link_with_anchor_and_title_passes(self):  # target "b.md#sec" with a "t" title, b.md present -> []
    def test_links_inside_fenced_code_are_ignored(self):    # link to "nope.md" inside a fenced code block -> []
    def test_external_and_anchor_only_links_are_ignored(self):  # https://..., mailto:, #sec -> []
    def test_image_link_is_checked(self):                   # image target "img.png" absent -> 1 error

class FrontMatterTests(unittest.TestCase):
    def test_parses_key_values_and_colons_in_values(self):  # "licence: CC-BY-4.0 : voir https://x" -> value keeps text after first colon
    def test_crlf_is_parsed_like_lf(self):
    def test_missing_front_matter_returns_none(self):

class RecordTests(unittest.TestCase):
    def test_valid_source_record_passes(self):              # docs/sources/arome.md with all fields/sections -> []
    def test_missing_field_is_reported(self):               # without "licence" -> error contains "licence"
    def test_placeholder_values_count_as_missing(self):     # each of TODO, TBD, ?, ..., <à compléter> -> error
    def test_id_must_match_filename(self):                  # id: autre in arome.md -> error contains "id"
    def test_invalid_statut_and_date_are_reported(self):    # statut: peut-etre ; verifie_le: 21/10/2026 -> 2 errors
    def test_missing_section_is_reported(self):             # no "## Limites" -> error contains "Limites"
    def test_readme_in_record_folder_is_not_a_record(self):
    def test_skill_templates_are_not_records(self):         # .claude/skills/x/template.md with placeholders -> []

class MainTests(unittest.TestCase):
    def test_main_returns_1_and_prints_errors(self):
    def test_main_returns_0_on_clean_tree(self):
```

- [x] **Étape 2 : lancer les tests et constater l'échec**

Commande : `python3 -m unittest discover -s scripts -p 'test_*.py' -v`
Attendu : ÉCHEC (`ModuleNotFoundError: No module named 'check_docs'`).

- [x] **Étape 3 : implémenter `scripts/check_docs.py`.** Les règles des fiches sont une table `RECORD_RULES: dict[str, RecordRule]` (dossier relatif → type attendu, champs, valeurs contraintes, sections) recopiée du tableau « Formats des fiches ». Les liens sont repérés par l'expression `!?\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)` hors blocs ```` ``` ````. Les cibles sont décodées (`urllib.parse.unquote`) et résolues depuis le dossier du fichier.

- [x] **Étape 4 : relancer les tests jusqu'au succès**

Commande : `python3 -m unittest discover -s scripts -p 'test_*.py' -v`
Attendu : tous les tests `OK`.

- [x] **Étape 5 : exécuter le vérificateur sur le dépôt**

Commande : `python3 scripts/check_docs.py`
Attendu : `OK: ...`, code retour 0.

- [x] **Étape 6 : créer `.github/workflows/docs.yml`** : déclenché sur `push` vers `main` et sur `pull_request` ; un job nommé `docs` sur `ubuntu-latest` avec `actions/checkout@v4`, `actions/setup-python@v5` (`python-version: "3.12"`), puis les deux commandes des étapes 4 et 5.

- [x] **Étape 7 : commit, PR, CI verte, fusion**

```bash
git add scripts .github/workflows/docs.yml
git commit -m "Add documentation checker and CI"
```
Ouvrir la PR, attendre le job `docs` vert (`gh api repos/louistouquet/PowAtlas/commits/<sha>/check-runs --jq '.check_runs[] | .name + " " + .conclusion'`), puis fusionner (squash).

---

### Tâche 2 : règles de travail pour Claude et les contributeurs IA

**Exécutant recommandé :** Opus, effort high (ces fichiers gouvernent toutes les sessions suivantes).

**Fichiers :**
- Modifier : `CLAUDE.md` (remplace la version d'amorçage)
- Créer : `AGENTS.md`, `docs/methode.md`, `docs/modeles-claude.md`

**Interfaces :**
- Consomme : la commande de vérification de la tâche 1.
- Produit : `docs/methode.md` et `docs/modeles-claude.md`, cités par les skills et agents des tâches 4 et 5.

- [x] **Étape 1 : écrire `docs/methode.md`** (français) à partir de la section 5 du cadrage : cycle (brainstorming, cadrage, plan, PR, bilan), fiches et leurs formats (renvoi au tableau de ce plan, recopié), règles de rigueur scientifique, continuité (`STATUS.md`, `NEXT.md`, `docs/decisions/`, issues et jalons), langues, garde-fous, procédure Git (branche `claude/<sujet>`, PR par API REST, CI, squash, lignes de fin de commit).
- [x] **Étape 2 : écrire `docs/modeles-claude.md`** : le tableau rôles / modèle / effort et les 6 règles d'économie de tokens de la section 6 du cadrage, la règle « modèles par famille », et la consigne de relecture du tableau à chaque nouvelle génération de modèles. Ajouter le budget Exa et la règle de bascule vers la recherche web intégrée.
- [x] **Étape 3 : réécrire `CLAUDE.md`** (anglais ou français, 80 lignes au plus) : rituel de début de session (lire `NEXT.md`, `STATUS.md`, le cadrage et le plan en cours ; `git status` ; PR ouvertes), résumé des garde-fous de ce plan, outils (alphaXiv pour les articles, Hugging Face, Exa dans le budget, skill `scientific-coding` pour tout code scientifique), liens vers `docs/methode.md` et `docs/modeles-claude.md`, commandes de vérification, rituel de fin de session (mettre à jour `STATUS.md` et `NEXT.md`).
- [x] **Étape 4 : écrire `AGENTS.md`** : 5 lignes au plus, qui renvoient vers `CLAUDE.md` pour tout outil IA autre que Claude Code.
- [x] **Étape 5 : vérifier**

Commande : `python3 scripts/check_docs.py` — Attendu : `OK`.
Contrôle de relecture : `wc -l CLAUDE.md` ≤ 80 ; chaque garde-fou des « Contraintes globales » apparaît dans `CLAUDE.md` ou dans un document qu'il cite.

- [x] **Étape 6 : commit, PR, CI, fusion.**

---

### Tâche 3 : documents publics et gouvernance

**Exécutant recommandé :** Sonnet, effort medium.

**Fichiers :**
- Modifier : `README.md` (anglais), `NEXT.md` (remplace la version d'amorçage)
- Créer : `README.fr.md`, `docs/vision.md`, `docs/README.md`, `docs/decisions/README.md`, `CONTRIBUTING.md`, `NOTICE`, `DATA_LICENSES.md`, `STATUS.md`

- [ ] **Étape 1 : `docs/vision.md`** (français) : sections 2, 3 et 4 du cadrage (vision, sous-projets, stratégie en couches, contraintes de calcul), en langage accessible au grand public.
- [ ] **Étape 2 : `README.md` (anglais) et `README.fr.md` (miroir français)** : présentation en deux phrases, état (« SP0 en cours, rien d'opérationnel »), principes (données ouvertes, zéro euro, scores publics, pas de verdict avalanche), tableau SP0 à SP6, liens vers `docs/vision.md`, `CONTRIBUTING.md` et les licences. Chaque README pointe vers l'autre.
- [ ] **Étape 3 : `CONTRIBUTING.md`** (anglais puis résumé français) : contributions sous la licence du fichier concerné (Apache-2.0 pour le code, CC-BY-4.0 pour la documentation et les données), sans CLA ; proposer une source par l'issue « Proposer une source » ; règles de PR (CI verte, une question par PR, pas de secret) ; langues.
- [ ] **Étape 4 : `NOTICE`** : `PowAtlas` / `Copyright 2026 PowAtlas contributors` / mention que les données tierces gardent leurs licences, avec renvoi à `DATA_LICENSES.md`.
- [ ] **Étape 5 : `DATA_LICENSES.md`** : politique (productions du projet en CC-BY-4.0 ; données tierces sous leur licence ; une page publique n'est pas une licence) ; attributions types : Météo-France (Licence Ouverte Etalab 2.0), ECMWF (CC-BY-4.0), OpenStreetMap (ODbL) ; tableau vide « Données tierces intégrées » à remplir en SP1 depuis les fiches `retenue`.
- [ ] **Étape 6 : `docs/README.md`** (index de tous les documents) et **`docs/decisions/README.md`** (format d'une décision : contexte, décision, conséquences, date ; numérotation `NNNN-titre.md`).
- [ ] **Étape 7 : `STATUS.md`** (ce qui existe et fonctionne réellement, avec la date) et **`NEXT.md`** (prochaine tâche de ce plan non cochée).
- [ ] **Étape 8 : vérifier** — `python3 scripts/check_docs.py` → `OK` ; les liens croisés des deux README fonctionnent.
- [ ] **Étape 9 : commit, PR, CI, fusion.**

---

### Tâche 4 : skill `qualifier-source`, agent `chercheur-sources` et première fiche réelle

**Exécutant recommandé :** Opus, effort high pour écrire le skill et l'agent ; l'agent lui-même tourne en Sonnet, effort medium.

**Fichiers :**
- Créer : `.claude/skills/qualifier-source/SKILL.md`, `.claude/skills/qualifier-source/template.md`
- Créer : `.claude/agents/chercheur-sources.md`
- Créer : `docs/sources/README.md`, `docs/sources/ecmwf-open-data.md`

**Interfaces :**
- Consomme : format `source` (tableau « Formats des fiches ») et le vérificateur de la tâche 1.
- Produit : l'agent `chercheur-sources` (appelé par les tâches 7 à 10) et le skill `qualifier-source` qu'il suit.

- [ ] **Étape 1 : `template.md`** : une fiche `source` complète dont chaque valeur est `<à compléter>`, avec, sous `## Test d'accès`, le gabarit : date, commande exacte, taille téléchargée, résultat observé.
- [ ] **Étape 2 : `SKILL.md`** : en-tête `name: qualifier-source` et une `description` qui déclenche le skill pour « qualifier, évaluer ou documenter une source de données ». Procédure : trouver la documentation officielle ; relever la licence exacte avec lien et date ; tester l'accès sans compte (50 Mo au plus, sinon `compte gratuit requis`) ; relever quotas, délai de mise à disposition, conservation, résolution, variables utiles à la neige, couverture de l'emprise des Alpes françaises ; distinguer vérifié, affirmé par le producteur et hypothèse ; remplir le modèle ; lancer `python3 scripts/check_docs.py`.
- [ ] **Étape 3 : `.claude/agents/chercheur-sources.md`** : en-tête `name: chercheur-sources`, `description` (qualifie une ou plusieurs sources et écrit leurs fiches), `model: sonnet`, `effort: medium`. Consignes : suivre le skill `qualifier-source` ; n'écrire que les fichiers nommés dans son mandat ; au plus 15 recherches Exa par mandat ; rendre un résumé de 10 lignes au plus avec la liste des fichiers écrits.
- [ ] **Étape 4 : tester l'agent sur un cas réel.** Lancer l'agent `chercheur-sources` avec le mandat : « Qualifie l'ECMWF Open Data (IFS et AIFS, résolution 0,25°) pour l'archivage de prévisions de neige sur les Alpes françaises. Écris uniquement `docs/sources/ecmwf-open-data.md`. »
- [ ] **Étape 5 : vérifier la fiche**

Commande : `python3 scripts/check_docs.py` — Attendu : `OK`, et le nombre de fiches contrôlées augmente de 1.
Contrôle manuel : relancer la commande de la section `## Test d'accès` de la fiche et obtenir le même type de résultat. Si l'agent a ignoré son mandat (autres fichiers modifiés, champs inventés), corriger `SKILL.md` ou l'agent, puis recommencer l'étape 4.

- [ ] **Étape 6 : `docs/sources/README.md`** (rôle des fiches, renvoi au skill) ; commit, PR, CI, fusion.

---

### Tâche 5 : skill `experience-modele`, agent `relecteur-scientifique` et fiche d'exemple

**Exécutant recommandé :** Opus, effort high.

**Fichiers :**
- Créer : `.claude/skills/experience-modele/SKILL.md`, `.claude/skills/experience-modele/template.md`
- Créer : `.claude/agents/relecteur-scientifique.md`
- Créer : `docs/experiments/README.md`, `docs/experiments/exemple-fictif-correction-neige-fraiche.md`

**Interfaces :**
- Produit : l'agent `relecteur-scientifique` (appelé par les tâches 7 à 12) et le skill `experience-modele` (utilisé à partir de SP2).

- [ ] **Étape 1 : `template.md`** : une fiche `experience` complète, valeurs `<à compléter>`.
- [ ] **Étape 2 : `SKILL.md`** : en-tête `name: experience-modele`, description qui le déclenche pour « préparer, mener ou conclure un essai de modèle ». Protocole : hypothèse ; référence à battre ; découpage par saisons entières mises de côté ; uniquement des données disponibles à l'heure d'émission ; mesures et seuil de réussite fixés avant l'essai ; résultat avec intervalle d'incertitude par blocs temporels ; décision et condition de réexamen ; conservation des échecs.
- [ ] **Étape 3 : `.claude/agents/relecteur-scientifique.md`** : en-tête `name: relecteur-scientifique`, `model: opus`, `effort: high`, `tools: Read, Glob, Grep, Bash, WebFetch, WebSearch` (pas d'écriture). Mission : chercher fuites temporelles, découpages qui se chevauchent, affirmations sans source ou sans date, confusion observé / modélisé / prévu, erreurs statistiques, problèmes de licence, verdicts de sécurité implicites. Sortie : liste de constats, chacun avec fichier, ligne, gravité (`bloquant`, `important`, `mineur`) et correction proposée.
- [ ] **Étape 4 : écrire la fiche d'exemple** avec `fictive: oui`, `statut: prevue`, et un avertissement en tête de corps « Exemple fictif, aucun résultat réel ». Y placer volontairement **une** faille : le découpage `## Données et découpage` tire les jours de test au hasard dans les mêmes saisons que l'entraînement.
- [ ] **Étape 5 : tester l'agent.** Lancer `relecteur-scientifique` sur la fiche d'exemple. Attendu : un constat `bloquant` sur le découpage aléatoire par jours (fuite temporelle). S'il ne le trouve pas, renforcer sa consigne et relancer.
- [ ] **Étape 6 : corriger la fiche** (découpage par saisons entières), garder dans `## Décision` une note expliquant la faille trouvée par le relecteur, puis `python3 scripts/check_docs.py` → `OK`.
- [ ] **Étape 7 : `docs/experiments/README.md`** ; commit, PR, CI, fusion.

---

### Tâche 6 : réglages GitHub

**Exécutant recommandé :** Sonnet, effort medium.

**Fichiers :**
- Créer : `.github/ISSUE_TEMPLATE/source.yml`, `.github/ISSUE_TEMPLATE/experience.yml`, `.github/ISSUE_TEMPLATE/bug.yml`, `.github/ISSUE_TEMPLATE/config.yml`, `.github/pull_request_template.md`

- [ ] **Étape 1 : modèles d'issues** (formulaires YAML, en anglais avec titres français entre parenthèses) : `source.yml` (nom, lien, licence connue, utilité pour la neige) ; `experience.yml` (hypothèse, référence, données) ; `bug.yml` ; `config.yml` avec `blank_issues_enabled: true`. Modèle de PR : résumé, vérifications lancées, sources ou licences touchées, case « aucun secret ».
- [ ] **Étape 2 : jalons** : créer `SP0 — Fondations`, `SP1 — Archive et observations`, `SP2 — Tableau des scores`, `SP3 — Prévision v1`, `SP4 — Manteau neigeux`, `SP5 — Recherche IA avancée`, `SP6 — Produits` avec `gh api repos/louistouquet/PowAtlas/milestones -f title=...`.
Vérification : `gh api repos/louistouquet/PowAtlas/milestones --jq length` → `7`.
- [ ] **Étape 3 : étiquettes** `recherche`, `source`, `experience`, `code`, `docs` (`gh api repos/louistouquet/PowAtlas/labels -f name=... -f color=...`).
- [ ] **Étape 4 : protection de `main` et suppression automatique des branches fusionnées.** Essayer `gh api -X PUT repos/louistouquet/PowAtlas/branches/main/protection` (PR obligatoire, vérification `docs` obligatoire, pas de *force push*) et `gh api -X PATCH repos/louistouquet/PowAtlas -F delete_branch_on_merge=true`. Si le proxy refuse (HTTP 403), demander au pilote de le faire dans *Settings* et lui donner la liste exacte : *Branches → Add rule `main` → Require a pull request, Require status checks: `docs`, Do not allow force pushes* ; *General → Automatically delete head branches* ; supprimer la branche restante `claude/sp0-cadrage`.
- [ ] **Étape 5 : issues de suivi** : une issue par tâche restante de ce plan (7 à 13), rattachée au jalon SP0, avec l'étiquette adaptée.
- [ ] **Étape 6 : vérifier, commit, PR, CI, fusion.**

---

### Tâches 7 à 11 : recherche R0 (5 axes en parallèle)

Ces cinq tâches partagent la même procédure. Elles sont lancées **en même temps** (feu vert du pilote donné pour environ 7 agents) ; R0.2 est consolidée et fusionnée en premier.

**Procédure commune**

- [ ] **Étape 1 : lancer l'agent de recherche** (`chercheur-sources` pour les axes avec fiches, sinon agent généraliste Sonnet, effort medium) avec un mandat qui contient : la question, la liste des fichiers qu'il possède (et lui seul), au plus 25 sources consultées, au plus 15 recherches Exa, l'obligation d'utiliser alphaXiv pour les articles et la recherche Hugging Face pour les modèles et jeux de données, le format `recherche` du rapport, et la règle de citation : chaque affirmation porte sa source primaire et sa date de consultation, et est marquée comme vérifiée, affirmée par un tiers ou hypothèse. Le responsable (Opus, effort high) consolide ensuite les résultats.
- [ ] **Étape 2 : contrôler les liens et les licences** avec un agent Haiku (effort low) : chaque URL du rapport et des fiches répond (HTTP 200 ou redirection), et chaque licence citée correspond à la page citée. Corriger les écarts.
- [ ] **Étape 3 : relecture** par `relecteur-scientifique`. Corriger tous les constats `bloquant` et `important`. Passer le rapport en `statut: relue`.
- [ ] **Étape 4 : vérifier** — `python3 scripts/check_docs.py` → `OK`.
- [ ] **Étape 5 : commit, PR, CI, fusion**, puis fermer l'issue de l'axe.

| Tâche | Axe | Rapport | Fiches possédées par l'axe | Contenu attendu en plus du format |
|---|---|---|---|---|
| 7 *(en premier)* | R0.2 Prévisions ouvertes | `docs/research/R0.2-previsions-ouvertes.md` | AROME (0,01° et 0,025°), AROME-PI, PE-AROME, ARPEGE, ECMWF IFS/AIFS/ENS (compléter `ecmwf-open-data.md`), ICON-EU et ICON-D2 (DWD), ICON-CH1 et ICON-CH2 (MeteoSwiss), GFS, archives de prévisions d'Open-Meteo | Section `### Liste d'archivage SP1` : pour chaque source retenue, variables, runs par jour, échéances, découpage sur l'emprise, volume estimé en Mo par jour et en Go par saison, méthode d'accès, licence, priorité. Faisabilité du stockage gratuit (limites Hugging Face pour un jeu de données public, limites GitHub Actions) vérifiée sur la documentation officielle |
| 8 | R0.1 Concurrence | `docs/research/R0.1-concurrence.md` | aucune | Tableau par service : fonctionnalités, méthodes revendiquées, sources de données affichées, prix, lacunes. Liste priorisée des fonctionnalités où PowAtlas peut être meilleur |
| 9 | R0.3 Observations | `docs/research/R0.3-observations.md` | Nivôse, réseau nivo-météo, observations Météo-France (SYNOP, base climatologique), hauteurs déclarées par les stations, SLF/IMIS, Arpa Valle d'Aosta et Piemonte, Copernicus neige (FSC, GFSC, SWS), Skitour, Camptocamp | Pour la neige fraîche à 24, 48 et 72 h : quelles mesures (neige fraîche ou hauteur totale), fréquence, profondeur d'archive, biais connus (station damée, abritée…). Recommandation de vérité terrain pour le tableau des scores |
| 10 | R0.4 Historique | `docs/research/R0.4-historique.md` | S2M, CERRA et CERRA-Land, ERA5 et ERA5-Land, COMEPHORE, autres réanalyses pertinentes | Couverture temporelle et spatiale, résolution, variables neige, licence, compte requis ou non. Ce qui sert à l'entraînement, à la vérification et aux archives des saisons |
| 11 | R0.5 Briques open source | `docs/research/R0.5-briques-open-source.md` | aucune (logiciels, pas des données) | Tableau réutiliser / construire : modèles de manteau, méthodes de neige fraîche et de séparation pluie-neige, bibliothèques de scores, outils (earthkit, Herbie, cfgrib, Open-Meteo…), projets neige open source existants, quotas réels des GPU gratuits (Kaggle, Colab), avec licence et date de dernière version |

---

### Tâche 12 : « Cible et feuille de route »

**Exécutant recommandé :** Opus, effort xhigh pour la synthèse ; `relecteur-scientifique` pour la relecture.

**Fichiers :**
- Créer : `docs/roadmap.md`
- Modifier : `docs/research/R0.*.md` (`statut: validee` après accord du pilote)

**Interfaces :**
- Consomme : les 5 rapports R0 et les fiches `retenue`.

- [ ] **Étape 1 : écrire `docs/roadmap.md`** (français) avec les sections : `## Fonctionnalités de la v1` (classées, chacune reliée à une lacune de R0.1) ; `## Liste d'archivage SP1` (reprise de R0.2, ordonnée par priorité) ; `## Vérité terrain et tableau des scores` (de R0.3 et R0.4 : variables, mesures, échéances, références à battre) ; `## Réutiliser ou construire` (de R0.5) ; `## Ordre des sous-projets` (confirmé ou modifié, avec raison) ; `## Risques` ; `## Questions pour le pilote`.
- [ ] **Étape 2 : relecture** par `relecteur-scientifique` ; corriger les constats `bloquant` et `important`.
- [ ] **Étape 3 : vérifier** — `python3 scripts/check_docs.py` → `OK`.
- [ ] **Étape 4 : PR et présentation au pilote.** Résumer la feuille de route en chat avec le lien de la PR. **Ne pas fusionner avant l'accord explicite du pilote.** Intégrer ses retours.
- [ ] **Étape 5 : après accord**, passer les rapports en `statut: validee`, fusionner.

---

### Tâche 13 : clôture de SP0

**Exécutant recommandé :** Opus, effort high.

**Fichiers :**
- Modifier : `STATUS.md`, `NEXT.md`

- [ ] **Étape 1 : vérifier un par un les 7 critères** de la section 9 du cadrage, avec la preuve de chacun (commande lancée et résultat, ou lien GitHub).
- [ ] **Étape 2 : relecture d'ensemble** de SP0 par `relecteur-scientifique` (cohérence entre cadrage, méthode, `CLAUDE.md`, roadmap). Corriger.
- [ ] **Étape 3 : mettre à jour `STATUS.md`** (ce qui existe) et **`NEXT.md`** : « Démarrer le brainstorming de SP1 (archive et observations) à partir de `docs/roadmap.md` ».
- [ ] **Étape 4 : commit, PR, CI, fusion** ; fermer le jalon SP0.
