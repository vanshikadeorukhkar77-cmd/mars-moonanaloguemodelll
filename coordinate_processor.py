"""Coordinate helpers for single points and rectangular coordinate ranges."""

def normalize_longitude_360(longitude: float) -> float:
    """Convert longitude to the 0..360 east-positive convention."""
    return float(longitude) % 360.0


def midpoint_latitude(lat_min: float, lat_max: float) -> float:
    """Arithmetic midpoint of the latitude limits."""
    if lat_min > lat_max:
        raise ValueError("Minimum latitude must be less than or equal to maximum latitude.")
    if not (-90 <= lat_min <= 90 and -90 <= lat_max <= 90):
        raise ValueError("Latitude must be between -90° and 90°.")
    return (float(lat_min) + float(lat_max)) / 2.0


def midpoint_longitude(lon_start: float, lon_end: float) -> float:
    """
    Midpoint along the shorter eastward/westward arc.
    Handles ranges crossing the -180/180 (or 0/360) boundary.
    The result uses 0..360 east longitude.
    """
    start = normalize_longitude_360(lon_start)
    end = normalize_longitude_360(lon_end)
    eastward_span = (end - start) % 360.0
    if eastward_span <= 180.0:
        midpoint = start + eastward_span / 2.0
    else:
        midpoint = end + (360.0 - eastward_span) / 2.0
    return midpoint % 360.0


def process_coordinates(
    latitude: float | None = None,
    longitude: float | None = None,
    lat_min: float | None = None,
    lat_max: float | None = None,
    lon_start: float | None = None,
    lon_end: float | None = None,
) -> tuple[float, float, str]:
    """Return (latitude, east longitude 0..360, explanation)."""
    is_range = any(v is not None for v in (lat_min, lat_max, lon_start, lon_end))

    if is_range:
        if None in (lat_min, lat_max, lon_start, lon_end):
            raise ValueError("For a coordinate range, enter all four limits: minimum/maximum latitude and start/end longitude.")
        lat = midpoint_latitude(lat_min, lat_max)
        lon = midpoint_longitude(lon_start, lon_end)
        return lat, lon, "Midpoint calculated from the supplied coordinate range (FMP)."

    if latitude is None or longitude is None:
        raise ValueError("Enter either one latitude/longitude point or all four coordinate-range limits.")
    if not -90 <= float(latitude) <= 90:
        raise ValueError("Latitude must be between -90° and 90°.")
    return float(latitude), normalize_longitude_360(float(longitude)), "Single coordinate used directly."
