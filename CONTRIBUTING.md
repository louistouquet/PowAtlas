# Contributing to PowAtlas

*Résumé en français [plus bas](#résumé-en-français).*

Thank you for your interest. PowAtlas is in its foundation phase (SP0): the most useful contributions right now are data sources, research pointers and corrections to the documentation.

## Licences of contributions

- Contributions are accepted under the licence of the file they touch: **Apache-2.0** for code, **CC-BY-4.0** for documentation and data produced by the project.
- There is **no CLA**. By opening a pull request you confirm you have the right to submit the contribution under that licence.
- Third-party data must come with a licence that allows reuse; a public web page is not a licence. See [`DATA_LICENSES.md`](DATA_LICENSES.md).

## Proposing a data source

Open an issue with the **"Propose a source"** template (*Proposer une source*): name, link, known licence, and why it is useful for snow. Every source used by the project gets a source record in `docs/sources/`.

## Pull requests

- Green CI (`docs` job). Locally: `python3 -m unittest discover -s scripts -p 'test_*.py'` and `python3 scripts/check_docs.py`.
- **One question per pull request**: small, focused changes.
- **No secrets**, tokens or signed links — the repository is public.
- No avalanche safety verdicts: PowAtlas informs; the official avalanche bulletin (BRA, Météo-France) remains the reference.
- Pull requests are squash-merged.

## Languages

- Code, comments, CLI messages and API: English.
- READMEs: English and French.
- Design documents, plans, records and research reports: French (questions and issues in English are welcome).

---

## Résumé en français

- Les contributions sont acceptées sous la licence du fichier concerné : **Apache-2.0** pour le code, **CC-BY-4.0** pour la documentation et les données produites par le projet. **Pas de CLA.**
- Pour proposer une source de données, ouvrez une issue avec le modèle **« Proposer une source »** (nom, lien, licence connue, utilité pour la neige).
- Règles de PR : CI verte, **une question par PR**, **aucun secret**, jamais de verdict de sécurité avalanche, fusion en un seul commit.
- Langues : code et commentaires en anglais ; README en anglais et en français ; cadrages, plans, fiches et rapports en français.
- Méthode complète : [`docs/methode.md`](docs/methode.md).
