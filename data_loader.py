
"""Load the three supplied Excel workbooks."""

from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent


def load_mars():
    raw = pd.read_excel(
        DATA_DIR / "mars_data.xlsx",
        sheet_name="Quadrangles",
        header=4
    )

    df = pd.DataFrame({
        "quadrangle": raw["Quad"],
        "name": raw["Name"],
        "lat_min": pd.to_numeric(raw.iloc[:, 4], errors="coerce"),
        "lat_max": pd.to_numeric(raw.iloc[:, 5], errors="coerce"),
        "lon_min": pd.to_numeric(raw.iloc[:, 7], errors="coerce"),
        "lon_max": pd.to_numeric(raw.iloc[:, 8], errors="coerce"),
    })

    df = df.dropna(
        subset=["quadrangle", "lat_min", "lat_max", "lon_min", "lon_max"]
    )

    df["quadrangle"] = df["quadrangle"].astype(str)

    return df.reset_index(drop=True), raw


def load_moon():
    raw = pd.read_excel(
        DATA_DIR / "moon_data.xlsx",
        sheet_name="Actual Data"
    )

    df = pd.DataFrame({
        "quadrangle": raw["Quadrangle"],
        "lat_min": pd.to_numeric(raw["min latitude (°)"], errors="coerce"),
        "lat_max": pd.to_numeric(raw["max latitude (°)"], errors="coerce"),
        "lon_west": pd.to_numeric(raw["West longitude E (°)"], errors="coerce"),
        "lon_east": pd.to_numeric(raw["East longitude E (°)"], errors="coerce"),
    })

    df = df.dropna(
        subset=["quadrangle", "lat_min", "lat_max", "lon_west", "lon_east"]
    )

    df["quadrangle"] = df["quadrangle"].astype(str)

    return df.reset_index(drop=True), raw


def load_earth():
    return pd.read_excel(
        DATA_DIR / "earth_data.xlsx",
        sheet_name=None
    )


def load_all_data():
    mars_index, mars_raw = load_mars()
    moon_index, moon_raw = load_moon()
    earth_sheets = load_earth()

    return {
        "mars_index": mars_index,
        "mars_raw": mars_raw,
        "moon_index": moon_index,
        "moon_raw": moon_raw,
        "earth_sheets": earth_sheets,
    }
