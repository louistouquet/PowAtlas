"""Command-line entry point: ``powatlas <command>``."""

import argparse

from powatlas import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="powatlas", description=__doc__)
    parser.add_argument("--version", action="version", version=f"powatlas {__version__}")
    parser.add_subparsers(dest="command")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 2
    raise AssertionError(f"unhandled command {args.command}")
