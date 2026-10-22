"""Index files of producers that publish one: ECMWF ``.index`` (JSON lines), NCEP ``.idx`` (GFS)."""

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


@dataclass(frozen=True)
class IdxEntry:
    var: str
    level: str
    desc: str  # time description, e.g. "anl", "24 hour fcst", "0-1 day acc fcst"
    offset: int
    length: int | None  # None for the last record (runs to the end of the file)


def parse_gfs_idx(text: bytes) -> list[IdxEntry]:
    """``num:offset:d=AAAAMMJJHH:VAR:level:desc:`` lines; a record ends where the next begins."""
    rows = []
    for line in text.decode("utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split(":")
        if len(parts) < 6:
            raise ValueError(f"malformed idx line: {line!r}")
        rows.append((int(parts[1]), parts[3], parts[4], parts[5]))
    entries = []
    for i, (offset, var, level, desc) in enumerate(rows):
        length = rows[i + 1][0] - offset if i + 1 < len(rows) else None
        if length is not None and length <= 0:
            raise ValueError(f"idx offsets not increasing at record {i + 1}")
        entries.append(IdxEntry(var, level, desc, offset, length))
    return entries
