"""Find the Mars or Moon quadrangle containing a coordinate."""

def longitude_is_inside(longitude_360: float, west_or_min: float, east_or_max: float) -> bool:
    """Check a longitude against a 0..360 interval, including wraparound."""
    lon = float(longitude_360) % 360.0
    start = float(west_or_min) % 360.0
    end = float(east_or_max) % 360.0

    # A 0..360 interval means all longitudes.
    if abs(float(east_or_max) - float(west_or_min)) >= 359.999:
        return True

    if start <= end:
        return start <= lon <= end
    return lon >= start or lon <= end


def find_quadrangle(body: str, latitude: float, longitude_360: float, mars_df, moon_df):
    """Return the matching quadrangle row, or None if no row contains the point."""
    body = body.strip().lower()

    if body == "mars":
        df = mars_df
        for _, row in df.iterrows():
            lat_min, lat_max = float(row["lat_min"]), float(row["lat_max"])
            if lat_min <= latitude <= lat_max and longitude_is_inside(
                longitude_360, row["lon_min"], row["lon_max"]
            ):
                return row
    elif body == "moon":
        df = moon_df
        for _, row in df.iterrows():
            lat_min, lat_max = float(row["lat_min"]), float(row["lat_max"])
            if lat_min <= latitude <= lat_max and longitude_is_inside(
                longitude_360, row["lon_west"], row["lon_east"]
            ):
                return row
    else:
        raise ValueError("Body must be 'Mars' or 'Moon'.")

    return None
