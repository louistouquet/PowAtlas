"""Working domain (French Alps) and cropping of model grids to it.

Coordinates are degrees, WGS84. Longitudes are compared in [-180, 180).
"""

from dataclasses import dataclass

import numpy as np

# Points lying exactly on a bounding-box edge are kept despite float rounding
# of grid coordinates (e.g. -3.94 + 447 * 0.02 = 4.999999999).
EDGE_TOLERANCE_DEG = 1e-9


@dataclass(frozen=True)
class BBox:
    west: float
    south: float
    east: float
    north: float

    def __post_init__(self) -> None:
        if not (self.west < self.east and self.south < self.north):
            raise ValueError(f"degenerate bounding box {self}")


ALPS = BBox(west=5.0, south=43.5, east=7.9, north=46.5)


def normalize_lon(lon: np.ndarray) -> np.ndarray:
    """Map longitudes (degrees) to [-180, 180)."""
    return (np.asarray(lon, dtype=np.float64) + 180.0) % 360.0 - 180.0


def _axis_slice(coord: np.ndarray, low: float, high: float, margin_cells: int, name: str) -> slice:
    """Contiguous slice of a 1D coordinate (monotonic, or a normalized global grid) covering [low, high] plus a margin.

    The grid must cover the interval to within one grid step on each side;
    otherwise the domain is not inside the grid and cropping would silently
    return a truncated field.
    """
    if coord.ndim != 1 or coord.size < 2:
        raise ValueError(f"{name}: expected a 1D coordinate with at least 2 points")
    # Median, not max: a global grid normalized to [-180, 180) has one jump of 360.
    step = float(np.median(np.abs(np.diff(coord))))
    if coord.min() > low + step or coord.max() < high - step:
        raise ValueError(
            f"{name}: domain [{low}, {high}] not inside grid [{coord.min()}, {coord.max()}]"
        )
    inside = np.flatnonzero(
        (coord >= low - EDGE_TOLERANCE_DEG) & (coord <= high + EDGE_TOLERANCE_DEG)
    )
    if inside.size == 0:
        raise ValueError(f"{name}: no grid point inside [{low}, {high}]")
    if inside.size != inside[-1] - inside[0] + 1:
        raise ValueError(f"{name}: points inside [{low}, {high}] are not contiguous")
    start = max(int(inside[0]) - margin_cells, 0)
    stop = min(int(inside[-1]) + 1 + margin_cells, coord.size)
    return slice(start, stop)


def crop_regular(
    lats: np.ndarray, lons: np.ndarray, bbox: BBox, margin_cells: int
) -> tuple[slice, slice]:
    """Slices (j, i) of a regular lat-lon grid covering ``bbox`` plus ``margin_cells``.

    ``lats`` (Nj) and ``lons`` (Ni) are the 1D coordinates in storage order
    (either direction). The slices index a values array of shape (Nj, Ni).
    """
    if margin_cells < 0:
        raise ValueError("margin_cells must be >= 0")
    sj = _axis_slice(np.asarray(lats, dtype=np.float64), bbox.south, bbox.north, margin_cells, "lat")
    si = _axis_slice(normalize_lon(lons), bbox.west, bbox.east, margin_cells, "lon")
    return sj, si


def crop_points(lats: np.ndarray, lons: np.ndarray, bbox: BBox, margin_deg: float) -> np.ndarray:
    """Indices of scattered points (unstructured grids) inside ``bbox`` widened by ``margin_deg``."""
    lats = np.asarray(lats, dtype=np.float64)
    lons = normalize_lon(lons)
    if lats.shape != lons.shape or lats.ndim != 1:
        raise ValueError("lats and lons must be 1D arrays of the same length")
    tol = EDGE_TOLERANCE_DEG
    mask = (
        (lons >= bbox.west - margin_deg - tol)
        & (lons <= bbox.east + margin_deg + tol)
        & (lats >= bbox.south - margin_deg - tol)
        & (lats <= bbox.north + margin_deg + tol)
    )
    return np.flatnonzero(mask)
