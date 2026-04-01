from __future__ import annotations

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from typing import Optional


EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two points in kilometers."""
    lat1_r, lng1_r, lat2_r, lng2_r = map(radians, (lat1, lng1, lat2, lng2))
    dlat = lat2_r - lat1_r
    dlng = lng2_r - lng1_r

    a = sin(dlat / 2) ** 2 + cos(lat1_r) * cos(lat2_r) * sin(dlng / 2) ** 2
    c = 2 * asin(sqrt(a))
    return EARTH_RADIUS_KM * c


@dataclass(frozen=True)
class BoundingBox:
    min_lat: float
    max_lat: float
    min_lng: float
    max_lng: float


def bounding_box_km(lat: float, lng: float, radius_km: float) -> BoundingBox:
    """Approximate bounding box around a point for a radius in km."""
    # ~111.32 km per degree latitude
    lat_delta = radius_km / 111.32

    cos_lat = cos(radians(lat))
    if abs(cos_lat) < 1e-12:
        lng_delta = 180.0
    else:
        lng_delta = radius_km / (111.32 * cos_lat)

    return BoundingBox(
        min_lat=lat - lat_delta,
        max_lat=lat + lat_delta,
        min_lng=lng - lng_delta,
        max_lng=lng + lng_delta,
    )


def parse_float(value: object) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
