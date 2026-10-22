"""Registry of source adapters, indexed by ``Source.family``.

An adapter collects one unit and returns its manifest::

    collect(unit, source, http, out_dir, mode, settings) -> Manifest
"""

from pathlib import Path
from typing import Protocol

from powatlas.catalogue import Source
from powatlas.http import HttpClient
from powatlas.units import Unit
from powatlas.writer import Manifest


class Adapter(Protocol):
    def collect(
        self, unit: Unit, source: Source, http: HttpClient, out_dir: Path, mode: str, settings: dict
    ) -> Manifest: ...


ADAPTERS: dict[str, Adapter] = {}
