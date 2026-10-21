"""Tests for check_docs.py (run: python3 -m unittest discover -s scripts -p 'test_*.py' -v)."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import check_docs

VALID_SOURCE = """---
type: source
id: arome
nom: AROME
producteur: Météo-France
licence: Licence Ouverte Etalab 2.0
acces: libre, sans compte
quotas: non applicable
delai: 2 h après le run
resolution: 0,025°
conservation: 24 h
statut: retenue
verifie_le: 2026-10-21
---

## Contenu

Variables.

## Test d'accès

Commande.

## Limites

Aucune.
"""


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")
    return path


class TempTree(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()


class LinkTests(TempTree):
    def test_broken_relative_link_is_reported(self):
        path = write(self.root, "a.md", "Voir [b](missing.md).\n")
        errors = check_docs.check_links(path, self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("missing.md", errors[0])
        self.assertTrue(errors[0].startswith("a.md:1:"))

    def test_existing_link_with_anchor_and_title_passes(self):
        write(self.root, "b.md", "# B\n")
        path = write(self.root, "a.md", 'Voir [b](b.md#sec "t").\n')
        self.assertEqual(check_docs.check_links(path, self.root), [])

    def test_links_inside_fenced_code_are_ignored(self):
        path = write(self.root, "a.md", "```\n[x](nope.md)\n```\n~~~\n[y](nope.md)\n~~~\n")
        self.assertEqual(check_docs.check_links(path, self.root), [])

    def test_links_inside_inline_code_are_ignored(self):
        path = write(self.root, "a.md", "Exemple : `[x](nope.md)`.\n")
        self.assertEqual(check_docs.check_links(path, self.root), [])

    def test_external_and_anchor_only_links_are_ignored(self):
        text = "[w](https://example.org/x) [m](mailto:a@b.c) [s](#sec)\n"
        path = write(self.root, "a.md", text)
        self.assertEqual(check_docs.check_links(path, self.root), [])

    def test_image_link_is_checked(self):
        path = write(self.root, "a.md", "![logo](img.png)\n")
        errors = check_docs.check_links(path, self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("img.png", errors[0])

    def test_percent_encoded_and_parent_links_resolve(self):
        write(self.root, "docs/mon fichier.md", "x\n")
        path = write(self.root, "docs/sub/a.md", "[x](../mon%20fichier.md)\n")
        self.assertEqual(check_docs.check_links(path, self.root), [])

    def test_error_reports_line_number(self):
        path = write(self.root, "a.md", "ligne 1\n\n[x](nope.md)\n")
        errors = check_docs.check_links(path, self.root)
        self.assertTrue(errors[0].startswith("a.md:3:"))


class FrontMatterTests(unittest.TestCase):
    def test_parses_key_values_and_colons_in_values(self):
        meta = check_docs.parse_front_matter(
            "---\ntype: source\nlicence: CC-BY-4.0 : voir https://x\n---\nbody\n"
        )
        self.assertEqual(meta["type"], "source")
        self.assertEqual(meta["licence"], "CC-BY-4.0 : voir https://x")

    def test_crlf_is_parsed_like_lf(self):
        lf = check_docs.parse_front_matter("---\na: 1\nb: deux\n---\nx\n")
        crlf = check_docs.parse_front_matter("---\r\na: 1\r\nb: deux\r\n---\r\nx\r\n")
        self.assertEqual(lf, {"a": "1", "b": "deux"})
        self.assertEqual(crlf, lf)

    def test_missing_front_matter_returns_none(self):
        self.assertIsNone(check_docs.parse_front_matter("# Titre\n\ntexte\n"))

    def test_unclosed_front_matter_returns_none(self):
        self.assertIsNone(check_docs.parse_front_matter("---\na: 1\n# Titre\n"))


class RecordTests(TempTree):
    def record(self, text: str, rel: str = "docs/sources/arome.md") -> list[str]:
        path = write(self.root, rel, text)
        return check_docs.check_record(path, self.root)

    def test_valid_source_record_passes(self):
        self.assertEqual(self.record(VALID_SOURCE), [])

    def test_crlf_record_passes(self):
        self.assertEqual(self.record(VALID_SOURCE.replace("\n", "\r\n")), [])

    def test_missing_front_matter_is_reported(self):
        errors = self.record("# AROME\n")
        self.assertEqual(len(errors), 1)
        self.assertIn("front matter", errors[0])

    def test_missing_field_is_reported(self):
        text = VALID_SOURCE.replace("licence: Licence Ouverte Etalab 2.0\n", "")
        errors = self.record(text)
        self.assertEqual(len(errors), 1)
        self.assertIn("licence", errors[0])

    def test_placeholder_values_count_as_missing(self):
        for placeholder in ["TODO", "TBD", "?", "...", "<à compléter>", ""]:
            with self.subTest(placeholder=placeholder):
                text = VALID_SOURCE.replace("quotas: non applicable", f"quotas: {placeholder}")
                errors = self.record(text)
                self.assertEqual(len(errors), 1, errors)
                self.assertIn("quotas", errors[0])

    def test_id_must_match_filename(self):
        errors = self.record(VALID_SOURCE.replace("id: arome", "id: autre"))
        self.assertEqual(len(errors), 1)
        self.assertIn("id", errors[0])

    def test_type_must_match_folder(self):
        errors = self.record(VALID_SOURCE.replace("type: source", "type: recherche"))
        self.assertEqual(len(errors), 1)
        self.assertIn("type", errors[0])

    def test_invalid_statut_and_date_are_reported(self):
        text = VALID_SOURCE.replace("statut: retenue", "statut: peut-etre").replace(
            "verifie_le: 2026-10-21", "verifie_le: 21/10/2026"
        )
        errors = self.record(text)
        self.assertEqual(len(errors), 2, errors)
        self.assertTrue(any("statut" in e for e in errors))
        self.assertTrue(any("verifie_le" in e for e in errors))

    def test_impossible_date_is_reported(self):
        errors = self.record(VALID_SOURCE.replace("2026-10-21", "2026-02-30"))
        self.assertEqual(len(errors), 1)
        self.assertIn("verifie_le", errors[0])

    def test_missing_section_is_reported(self):
        errors = self.record(VALID_SOURCE.replace("## Limites\n", ""))
        self.assertEqual(len(errors), 1)
        self.assertIn("Limites", errors[0])

    def test_section_inside_code_block_does_not_count(self):
        text = VALID_SOURCE.replace("## Limites\n", "```\n## Limites\n```\n")
        errors = self.record(text)
        self.assertEqual(len(errors), 1)
        self.assertIn("Limites", errors[0])

    def test_valid_experiment_and_research_records_pass(self):
        experiment = """---
type: experience
id: essai
titre: Essai
statut: prevue
date: 2026-10-21
fictive: oui
reference: modèle brut
---
## Hypothèse
## Référence à battre
## Données et découpage
## Mesures fixées avant l'essai
## Résultat
## Décision
"""
        research = """---
type: recherche
id: R0.2-previsions
titre: Prévisions
date: 2026-10-21
statut: brouillon
---
## Question
## Méthode
## Résultats
## Recommandation
## Questions ouvertes
## Sources
"""
        self.assertEqual(self.record(experiment, "docs/experiments/essai.md"), [])
        self.assertEqual(self.record(research, "docs/research/R0.2-previsions.md"), [])

    def test_invalid_fictive_value_is_reported(self):
        text = """---
type: experience
id: essai
titre: Essai
statut: prevue
date: 2026-10-21
fictive: peut-etre
reference: modèle brut
---
## Hypothèse
## Référence à battre
## Données et découpage
## Mesures fixées avant l'essai
## Résultat
## Décision
"""
        errors = self.record(text, "docs/experiments/essai.md")
        self.assertEqual(len(errors), 1)
        self.assertIn("fictive", errors[0])

    def test_readme_in_record_folder_is_not_a_record(self):
        self.assertEqual(self.record("# Fiches sources\n", "docs/sources/README.md"), [])

    def test_skill_templates_are_not_records(self):
        text = VALID_SOURCE.replace("AROME", "<à compléter>").replace("id: arome", "id: <à compléter>")
        self.assertEqual(self.record(text, ".claude/skills/x/template.md"), [])

    def test_file_outside_record_folders_is_not_a_record(self):
        self.assertEqual(self.record("# Vision\n", "docs/vision.md"), [])


class MainTests(TempTree):
    def run_main(self) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = check_docs.main(["--root", str(self.root)])
        return code, out.getvalue()

    def test_main_returns_1_and_prints_errors(self):
        write(self.root, "README.md", "[x](missing.md)\n")
        write(self.root, "docs/sources/arome.md", VALID_SOURCE.replace("## Limites\n", ""))
        code, output = self.run_main()
        self.assertEqual(code, 1)
        lines = output.strip().splitlines()
        self.assertEqual(len(lines), 2, output)
        self.assertIn("README.md:1:", output)
        self.assertIn("docs/sources/arome.md:", output)

    def test_main_returns_0_on_clean_tree(self):
        write(self.root, "README.md", "[s](docs/sources/arome.md)\n")
        write(self.root, "docs/sources/arome.md", VALID_SOURCE)
        write(self.root, "docs/sources/README.md", "# Fiches\n")
        code, output = self.run_main()
        self.assertEqual(code, 0)
        self.assertEqual(output.strip(), "OK: 3 markdown files, 1 records checked")

    def test_iter_markdown_files_skips_git_and_is_sorted(self):
        write(self.root, "b.md", "x\n")
        write(self.root, "a.md", "x\n")
        write(self.root, ".git/x.md", "[x](nope.md)\n")
        write(self.root, ".superpowers/sdd/brief.md", "[x](nope.md)\n")
        files = check_docs.iter_markdown_files(self.root)
        self.assertEqual([p.relative_to(self.root).as_posix() for p in files], ["a.md", "b.md"])


if __name__ == "__main__":
    unittest.main()
