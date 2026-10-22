"""Decoding of GRIB2 messages on regular lat-lon grids, cropping and checks.

SP1 archives values as published: no unit conversion, no derived variable.
Decoded values are stored as float32; the relative rounding (about 6e-8) is far
below the packing precision of the source GRIB fields.
"""

from collections.abc import Iterator
from dataclasses import dataclass, replace
from datetime import datetime, timezone

import eccodes
import numpy as np

from powatlas.domain import BBox, crop_regular, normalize_lon

GRIB_KEYS: tuple[str, ...] = (
    "shortName",
    "paramId",
    "typeOfLevel",
    "level",
    "stepType",
    "stepRange",
    "units",
    "bitsPerValue",
    "packingType",
    "gridType",
    "Ni",
    "Nj",
    "latitudeOfFirstGridPointInDegrees",
    "longitudeOfFirstGridPointInDegrees",
    "iDirectionIncrementInDegrees",
    "jDirectionIncrementInDegrees",
    "centre",
    "generatingProcessIdentifier",
)

# Grid coordinates in GRIB2 are stored in micro-degrees.
GRID_TOLERANCE_DEG = 1e-6


class GridMismatch(ValueError):
    """The message grid differs from the grid declared in the catalogue."""


class RefTimeMismatch(ValueError):
    """The message reference time differs from the expected run."""


@dataclass(frozen=True)
class Field:
    short_name: str
    keys: dict
    ref_time: datetime
    step_end_minutes: int  # end of the step (or statistical period) after ref_time, minutes
    lats: np.ndarray  # (Nj,) degrees, storage order
    lons: np.ndarray  # (Ni,) degrees in [-180, 180), storage order
    values: np.ndarray  # (Nj, Ni) float32, NaN where the bitmap marks a missing value


    @property
    def step_end(self) -> int | None:
        """Step in whole hours, None for a sub-hourly step (e.g. ICON-D2 +24 h 15 min)."""
        hours, rest = divmod(self.step_end_minutes, 60)
        return hours if rest == 0 else None


@dataclass(frozen=True)
class GridSpec:
    ni: int
    nj: int
    lat_first: float
    lon_first: float
    di: float
    dj: float


def _message_length(data: bytes, offset: int) -> int:
    if data[offset : offset + 4] != b"GRIB":
        raise ValueError(f"no GRIB message at offset {offset}")
    edition = data[offset + 7]
    if edition != 2:
        raise ValueError(f"GRIB edition {edition} at offset {offset}; only GRIB2 is supported")
    length = int.from_bytes(data[offset + 8 : offset + 16], "big")
    if offset + length > len(data) or data[offset + length - 4 : offset + length] != b"7777":
        raise ValueError(f"truncated GRIB message at offset {offset}")
    return length


def _decode(message: bytes) -> Field:
    h = eccodes.codes_new_from_message(message)
    try:
        grid_type = eccodes.codes_get(h, "gridType")
        if grid_type != "regular_ll":
            raise ValueError(f"unsupported gridType {grid_type}")
        if (
            eccodes.codes_get(h, "iScansNegatively")
            or eccodes.codes_get(h, "jPointsAreConsecutive")
            or eccodes.codes_get(h, "alternativeRowScanning")
        ):
            raise ValueError("unsupported scanning mode")
        # Minutes: ICON-D2 files also hold quarter-hour steps that hours cannot express.
        eccodes.codes_set(h, "stepUnits", "m")
        keys = {k: eccodes.codes_get(h, k) for k in GRIB_KEYS if eccodes.codes_is_defined(h, k)}
        ni = eccodes.codes_get(h, "Ni")
        nj = eccodes.codes_get(h, "Nj")
        lat0 = eccodes.codes_get(h, "latitudeOfFirstGridPointInDegrees")
        lon0 = eccodes.codes_get(h, "longitudeOfFirstGridPointInDegrees")
        di = eccodes.codes_get(h, "iDirectionIncrementInDegrees")
        dj = eccodes.codes_get(h, "jDirectionIncrementInDegrees")
        sign = 1.0 if eccodes.codes_get(h, "jScansPositively") else -1.0
        # Coordinates are rebuilt from the first point and the increment: check them
        # against the last point so that a rounded increment cannot drift unnoticed.
        lat_last = eccodes.codes_get(h, "latitudeOfLastGridPointInDegrees")
        lon_last = eccodes.codes_get(h, "longitudeOfLastGridPointInDegrees")
        if abs(lat0 + sign * dj * (nj - 1) - lat_last) > 1e-3 or abs(
            float(normalize_lon(lon0 + di * (ni - 1))) - float(normalize_lon(lon_last))
        ) > 1e-3:
            raise ValueError("grid first point, increments and last point are inconsistent")
        values = eccodes.codes_get_values(h).astype(np.float64)
        if values.size != ni * nj:
            raise ValueError(f"{values.size} values for a {nj} x {ni} grid")
        if eccodes.codes_get(h, "bitmapPresent"):
            bitmap = eccodes.codes_get_array(h, "bitmap")
            values[bitmap == 0] = np.nan
        date = str(eccodes.codes_get(h, "dataDate"))
        hhmm = eccodes.codes_get(h, "dataTime")
        ref_time = datetime(
            int(date[:4]), int(date[4:6]), int(date[6:8]), hhmm // 100, hhmm % 100, tzinfo=timezone.utc
        )
        return Field(
            short_name=eccodes.codes_get(h, "shortName"),
            keys=keys,
            ref_time=ref_time,
            step_end_minutes=eccodes.codes_get_long(h, "endStep"),
            lats=lat0 + sign * dj * np.arange(nj),
            lons=normalize_lon(lon0 + di * np.arange(ni)),
            values=values.reshape(nj, ni).astype(np.float32),
        )
    finally:
        eccodes.codes_release(h)


def iter_fields(data: bytes) -> Iterator[Field]:
    """Decode every GRIB2 message of ``data`` (messages concatenated, as in a file)."""
    offset = 0
    while offset < len(data):
        length = _message_length(data, offset)
        yield _decode(data[offset : offset + length])
        offset += length


def crop_field(field: Field, bbox: BBox, margin_cells: int) -> Field:
    sj, si = crop_regular(field.lats, field.lons, bbox, margin_cells)
    return replace(
        field,
        lats=field.lats[sj].copy(),
        lons=field.lons[si].copy(),
        values=field.values[sj, si].copy(),
    )


def check_grid(field: Field, spec: GridSpec) -> None:
    k = field.keys
    actual = (
        k["Ni"],
        k["Nj"],
        k["latitudeOfFirstGridPointInDegrees"],
        float(normalize_lon(k["longitudeOfFirstGridPointInDegrees"])),
        k["iDirectionIncrementInDegrees"],
        k["jDirectionIncrementInDegrees"],
    )
    expected = (spec.ni, spec.nj, spec.lat_first, float(normalize_lon(spec.lon_first)), spec.di, spec.dj)
    same = actual[:2] == expected[:2] and all(
        abs(a - e) <= GRID_TOLERANCE_DEG for a, e in zip(actual[2:], expected[2:])
    )
    if not same:
        raise GridMismatch(f"{field.short_name}: grid {actual} differs from catalogue {expected}")


def check_ref_time(field: Field, expected: datetime) -> None:
    if field.ref_time != expected:
        raise RefTimeMismatch(
            f"{field.short_name}: run {field.ref_time.isoformat()} instead of {expected.isoformat()}"
        )
