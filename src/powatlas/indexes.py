"""Index files of producers that publish one: ECMWF ``.index`` (JSON lines)."""

import json
from dataclasses import dataclass


@dataclass(frozen=True)
class IndexEntry:
    param: str
    levtype: str
    levelist: str | None
    step: str  # as written by the producer (e.g. "24"); compared to the file's own step
    offset: int
    length: int


def parse_ecmwf_index(text: bytes) -> list[IndexEntry]:
    entries = []
    for line in text.decode("utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        entries.append(IndexEntry(row["param"], row["levtype"], row.get("levelist"), str(row["step"]),
                                  int(row["_offset"]), int(row["_length"])))
    return entries
