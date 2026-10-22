"""Synthetic GRIB2 messages for tests, built from eccodes samples (no third-party data)."""

import eccodes
import numpy as np


def make_message(
    short_name="tp",
    ni=11,
    nj=6,
    lat_first=47.0,
    lon_first=4.0,
    di=0.5,
    dj=1.0,
    date=20261101,
    time=0,
    step_range="0-24",
    values=None,
    missing_at=None,
    j_scans_positively=0,
    type_of_level="surface",
    level=0,
    step_units="h",
):
    """Return the bytes of one GRIB2 message on a regular lat-lon grid."""
    h = eccodes.codes_grib_new_from_samples("regular_ll_sfc_grib2")
    try:
        lat_last = lat_first + (nj - 1) * dj * (1 if j_scans_positively else -1)
        lon_last = lon_first + (ni - 1) * di
        for key, value in [
            ("Ni", ni),
            ("Nj", nj),
            ("jScansPositively", j_scans_positively),
            ("latitudeOfFirstGridPointInDegrees", lat_first),
            ("longitudeOfFirstGridPointInDegrees", lon_first),
            ("latitudeOfLastGridPointInDegrees", lat_last),
            ("longitudeOfLastGridPointInDegrees", lon_last),
            ("iDirectionIncrementInDegrees", di),
            ("jDirectionIncrementInDegrees", dj),
            ("dataDate", date),
            ("dataTime", time),
            ("typeOfLevel", type_of_level),
            ("level", level),
            ("shortName", short_name),
            ("stepUnits", step_units),
            ("stepRange", step_range),
        ]:
            eccodes.codes_set(h, key, value)
        if values is None:
            values = np.arange(ni * nj, dtype=float).reshape(nj, ni)
        values = np.array(values, dtype=float)
        if missing_at is not None:
            eccodes.codes_set(h, "bitmapPresent", 1)
            missing = eccodes.codes_get(h, "missingValue")
            values[missing_at] = missing
        eccodes.codes_set_values(h, values.ravel())
        return eccodes.codes_get_message(h)
    finally:
        eccodes.codes_release(h)
