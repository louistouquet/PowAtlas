"""Reading GRIB2 message headers by byte ranges (files without an index, e.g. Météo-France).

Only sections 0 to 4 are parsed, to identify each message (discipline,
parameter category and number, first fixed surface). The data itself is then
fetched by range and decoded by eccodes, which gives the authoritative keys.
GRIB2 octet positions below are 1-based in the WMO manual, 0-based here.
"""

from dataclasses import dataclass

from powatlas.http import HttpClient


@dataclass(frozen=True)
class HeaderInfo:
    offset: int
    length: int
    discipline: int
    category: int
    number: int
    template: int  # product definition template (0 instant, 8 statistical period, ...)
    level_type: int  # type of first fixed surface (code table 4.5)
    level_value: float | None  # None when the scaled value is missing


def parse_header(buf: bytes, offset: int) -> HeaderInfo:
    """Identify the message starting at ``buf[0]`` (located at ``offset`` in its file)."""
    if len(buf) < 16 or buf[:4] != b"GRIB":
        raise ValueError(f"no GRIB message at offset {offset}")
    if buf[7] != 2:
        raise ValueError(f"GRIB edition {buf[7]} at offset {offset}; only GRIB2 is supported")
    discipline = buf[6]
    length = int.from_bytes(buf[8:16], "big")
    p = 16
    while p + 5 <= len(buf):
        sec_len = int.from_bytes(buf[p : p + 4], "big")
        number = buf[p + 4]
        if sec_len < 5 or number > 7:
            raise ValueError(f"corrupt section at offset {offset + p}")
        if number == 4:
            if p + 34 > len(buf):
                break
            s = buf[p : p + sec_len]
            template = int.from_bytes(s[7:9], "big")
            if template not in (0, 8):
                raise ValueError(f"unsupported product definition template 4.{template} at offset {offset}")
            scale, value = s[23], int.from_bytes(s[24:28], "big")
            missing = scale == 255 or value == 0xFFFFFFFF
            level_value = None if missing else value / 10 ** (scale if scale < 128 else -(scale - 128))
            return HeaderInfo(offset, length, discipline, s[9], s[10], template, s[22], level_value)
        p += sec_len
    raise ValueError(f"section 4 not within the {len(buf)} header bytes read at offset {offset}")


def walk_messages(http: HttpClient, url: str, size: int, head_bytes: int) -> list[HeaderInfo]:
    """Headers of every message of a file of ``size`` bytes, one range request per message."""
    heads: list[HeaderInfo] = []
    offset = 0
    while offset < size:
        buf = http.get(url, byte_range=(offset, min(offset + head_bytes, size) - 1)).content
        h = parse_header(buf, offset)
        if h.length < 16 or offset + h.length > size:
            raise ValueError(f"{url}: message at {offset} of {h.length} bytes overruns the file size {size}")
        heads.append(h)
        offset += h.length
    return heads


def coalesce(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merge inclusive byte ranges that touch; overlapping ranges are an error."""
    merged: list[list[int]] = []
    for first, last in sorted(ranges):
        if merged and first <= merged[-1][1]:
            raise ValueError(f"overlapping ranges ending {merged[-1][1]} and starting {first}")
        if merged and first == merged[-1][1] + 1:
            merged[-1][1] = last
        else:
            merged.append([first, last])
    return [(a, b) for a, b in merged]
