"""Load the three supplied Excel workbooks into consistent data structures."""

from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"


def _number(value):
    return pd.to_numeric(value, errors="coerce")


def load_mars():
    # The Mars workbook has its column headers on Excel row 5.
    raw = pd.read_excel(DATA_DIR / "mars_data.xlsx", sheet_name="Quadrangles", header=4)
    df = pd.DataFrame({
        "quadrangle": raw["Quad"],
        "name": raw["Name"],
        "lat_min": _number(raw.iloc[:, 4]),
        "lat_max": _number(raw.iloc[:, 5]),
        "lon_min": _number(raw.iloc[:, 7]),
        "lon_max": _number(raw.iloc[:, 8]),
    })
    df = df.dropna(subset=["quadrangle", "lat_min", "lat_max", "lon_min", "lon_max"])
    df["quadrangle"] = df["quadrangle"].astype(str)
    # Exclude the workbook's final area-weighted summary row; it is not a location.
    df = df[df["quadrangle"].str.match(r"^MC-\d+$")]
    return df.reset_index(drop=True), raw


def load_moon():
    raw = pd.read_excel(DATA_DIR / "moon_data.xlsx", sheet_name="Actual Data", header=0)
    df = pd.DataFrame({
        "quadrangle": raw["Quadrangle"],
        "lat_min": _number(raw["min latitude (°)"]),
        "lat_max": _number(raw["max latitude (°)"]),
        "lon_west": _number(raw["West longitude E (°)"]),
        "lon_east": _number(raw["East longitude E (°)"]),
    })
    df = df.dropna(subset=["quadrangle", "lat_min", "lat_max", "lon_west", "lon_east"])
    df["quadrangle"] = df["quadrangle"].astype(str)
    return df.reset_index(drop=True), raw


def load_earth():
    # Earth data is split across parameter-specific worksheets.
    return pd.read_excel(DATA_DIR / "earth_data.xlsx", sheet_name=None)


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
