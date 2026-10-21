#!/usr/bin/env python3
"""Check PowAtlas documentation: internal links and record structure.

Usage: python3 scripts/check_docs.py [--root PATH]

Exit code 0 when everything is valid, 1 otherwise. Each error is printed on
one line as ``relative/path:line: message``. Standard library only.
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

LINK_RE = re.compile(r'!?\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
INLINE_CODE_RE = re.compile(r"(`+)(?:(?!\1).)+?\1")
FENCE_RE = re.compile(r"^\s{0,3}(```|~~~)")
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

SKIPPED_DIRS = {".git", ".superpowers"}
PLACEHOLDERS = {"", "todo", "tbd", "?", "...", "…", "<à compléter>"}
DATE_FIELDS = {"date", "verifie_le"}


@dataclass(frozen=True)
class RecordRule:
    type: str
    fields: tuple[str, ...]
    allowed: dict[str, tuple[str, ...]]
    sections: tuple[str, ...]


# Copied from the "Formats des fiches" table of docs/plans/2026-10-21-sp0-fondations.md.
RECORD_RULES: dict[str, RecordRule] = {
    "docs/sources": RecordRule(
        type="source",
        fields=(
            "type", "id", "nom", "producteur", "licence", "acces", "quotas",
            "delai", "resolution", "conservation", "statut", "verifie_le",
        ),
        allowed={"statut": ("retenue", "ecartee", "a-tester")},
        sections=("Contenu", "Test d'accès", "Limites"),
    ),
    "docs/experiments": RecordRule(
        type="experience",
        fields=("type", "id", "titre", "statut", "date", "fictive", "reference"),
        allowed={
            "statut": ("prevue", "en-cours", "terminee", "abandonnee"),
            "fictive": ("oui", "non"),
        },
        sections=(
            "Hypothèse", "Référence à battre", "Données et découpage",
            "Mesures fixées avant l'essai", "Résultat", "Décision",
        ),
    ),
    "docs/research": RecordRule(
        type="recherche",
        fields=("type", "id", "titre", "date", "statut"),
        allowed={"statut": ("brouillon", "relue", "validee")},
        sections=(
            "Question", "Méthode", "Résultats", "Recommandation",
            "Questions ouvertes", "Sources",
        ),
    ),
}


def read_lines(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def parse_front_matter(text: str) -> dict[str, str] | None:
    """Return the ``key: value`` pairs of a leading ``---`` block, or None."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    meta: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return meta
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return None


def iter_markdown_files(root: Path) -> list[Path]:
    files = []
    for path in root.rglob("*.md"):
        rel_parts = path.relative_to(root).parts
        if any(part in SKIPPED_DIRS for part in rel_parts[:-1]):
            continue
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def iter_prose_lines(lines: list[str]):
    """Yield (line_number, line) for lines outside fenced code blocks."""
    fence = None
    for number, line in enumerate(lines, start=1):
        match = FENCE_RE.match(line)
        if match:
            if fence is None:
                fence = match.group(1)
            elif match.group(1) == fence:
                fence = None
            continue
        if fence is None:
            yield number, line


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def check_links(path: Path, root: Path) -> list[str]:
    errors = []
    for number, line in iter_prose_lines(read_lines(path)):
        line = INLINE_CODE_RE.sub("", line)
        for match in LINK_RE.finditer(line):
            target = match.group(1)
            if target.startswith("#") or SCHEME_RE.match(target):
                continue
            target = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not target:
                continue
            base = root if target.startswith("/") else path.parent
            resolved = (base / target.lstrip("/")).resolve()
            if not resolved.exists():
                errors.append(f"{rel(path, root)}:{number}: broken link to {match.group(1)}")
    return errors


def record_rule_for(path: Path, root: Path) -> RecordRule | None:
    if path.name == "README.md":
        return None
    folder = path.parent.relative_to(root).as_posix()
    for prefix, rule in RECORD_RULES.items():
        if folder == prefix or folder.startswith(prefix + "/"):
            return rule
    return None


def is_valid_date(value: str) -> bool:
    if not DATE_RE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def check_record(path: Path, root: Path) -> list[str]:
    rule = record_rule_for(path, root)
    if rule is None:
        return []
    name = rel(path, root)
    lines = read_lines(path)
    meta = parse_front_matter("\n".join(lines))
    if meta is None:
        return [f"{name}:1: missing front matter (expected a '---' block)"]

    line_of = {}
    for number, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            break
        if ":" in line:
            line_of.setdefault(line.split(":", 1)[0].strip(), number)

    errors = []
    for field in rule.fields:
        value = meta.get(field)
        where = f"{name}:{line_of.get(field, 1)}"
        if value is None or value.strip().lower() in PLACEHOLDERS:
            errors.append(f"{where}: missing or placeholder value for field '{field}'")
            continue
        if field == "type" and value != rule.type:
            errors.append(f"{where}: field 'type' is '{value}', expected '{rule.type}'")
        elif field == "id" and value != path.stem:
            errors.append(f"{where}: field 'id' is '{value}', expected '{path.stem}' (file name)")
        elif field in rule.allowed and value not in rule.allowed[field]:
            allowed = ", ".join(rule.allowed[field])
            errors.append(f"{where}: field '{field}' is '{value}', expected one of: {allowed}")
        elif field in DATE_FIELDS and not is_valid_date(value):
            errors.append(f"{where}: field '{field}' is '{value}', expected a date AAAA-MM-JJ")

    headings = {line.rstrip() for _, line in iter_prose_lines(lines)}
    for section in rule.sections:
        if f"## {section}" not in headings:
            errors.append(f"{name}:1: missing section '## {section}'")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check documentation links and records.")
    parser.add_argument("--root", default=Path(__file__).resolve().parent.parent, type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()

    errors: list[str] = []
    files = iter_markdown_files(root)
    records = 0
    for path in files:
        errors.extend(check_links(path, root))
        if record_rule_for(path, root) is not None:
            records += 1
            errors.extend(check_record(path, root))

    for error in errors:
        print(error)
    if errors:
        return 1
    print(f"OK: {len(files)} markdown files, {records} records checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
