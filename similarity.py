
"""Earth analogue similarity ranking engine.

Uses a provisional weighted-distance method.
This is not a trained machine-learning classifier.
Missing values are excluded from scoring.
"""

import math
import pandas as pd


EARTH_ROW_START = 2


def _num(value):
    if value is None:
        return None

    try:
        x = pd.to_numeric(value, errors="coerce")

        if pd.isna(x):
            return None

        x = float(x)

        return x if math.isfinite(x) else None

    except (TypeError, ValueError):
        return None


def _find_site(sheets, sheet_name, place):

    df = sheets.get(sheet_name)

    if df is None:
        return None

    # Special handling for the Daytime hours worksheet.
    if sheet_name == "Daytime hours":

        first_col = df.columns[0]

        rows = df[
            df[first_col].astype(str).str.strip()
            == str(place).strip()
        ]

        return None if rows.empty else rows.iloc[0]

    if "Place name" not in df.columns:
        return None

    rows = df[
        df["Place name"].astype(str).str.strip()
        == str(place).strip()
    ]

    return None if rows.empty else rows.iloc[0]


def _earth_value(sheets, place, sheet, column):

    row = _find_site(sheets, sheet, place)

    if row is None or column not in row.index:
        return None

    return _num(row[column])


def _mars_target(row):

    values = {}

    mean_columns = {
        "elevation": "Mean.2",
        "slope": "Mean.3",
        "igneous": "Mean.4",
        "sedimentary": "Mean.5",
        "metamorphic": "Mean.6",
        "olivine": "Mean.7",
        "pyroxene": "Mean.8",
        "plagioclase": "Mean.9",
        "clays": "Mean.10",
        "sulfates": "Mean.11",
        "iron_oxides": "Mean.12",
        "carbonates": "Mean.13",
        "pressure": "Mean.15",
        "temperature": "Mean.16",
        "water_ice": "Mean.17",
        "humidity": "Mean.18",
        "wind": "Mean.19",
        "daylight_summer": "Mean.20",
        "daylight_winter": "Mean.21",
        "radiation": "Mean.22",
    }

    for key, col in mean_columns.items():

        if col in row.index:
            values[key] = _num(row[col])

    # Mars elevation is stored in kilometres.
    # Earth elevation is stored in metres.
    if values.get("elevation") is not None:
        values["elevation"] *= 1000.0

    values["marsquake"] = _num(row.get("Value"))
    values["volcanic"] = _num(row.get("Value.1"))

    return values


def _moon_target(row):

    cols = {

        "elevation": "T01 AVG elevation",
        "slope": "T02 AVG slope",

        "plagioclase": "M01 Plagioclase AVG",
        "pyroxene": "M02 Pyroxene AVG",
        "olivine": "M03 Olivine AVG",

        "iron_oxides": "C01 FeO AVG",
        "tio2": "C02 TiO2 AVG",
        "mgo": "C03 MgO AVG",
        "alumina": "C04 Al2O3 AVG",
        "cao": "C05 CaO AVG",

        "roughness": "T04 Surface roughness rank",
        "temperature": "T08 Mean annual surface temperature",
        "ice": "T10 Avg % Ice ",

        "daylight_summer": "T13 Mean Daylight at LS 90",
        "daylight_winter": "T14 Mean Daylight at LS 270",

        "moonquakes": "T18 Moonquakes",
        "volcanic": "T19 Avg % Volcanoes",
    }

    return {
        key: _num(row.get(col))
        for key, col in cols.items()
    }


def _earth_features(body, sheets, place):

    common = {

        "elevation": ("ALTITUDE & RELIEF", "Unnamed: 5"),
        "slope": ("SLOPE", "Unnamed: 5"),

        "temperature": ("TEMP", "Unnamed: 5"),
        "pressure": ("PRESSURE", "Unnamed: 5"),
        "humidity": ("humidity", "Unnamed: 5"),
        "wind": ("Wind Speed", "Unnamed: 5"),

        "radiation": ("Radiation", "Unnamed: 5"),

        "daylight_summer": ("Daytime hours", "Unnamed: 10"),
        "daylight_winter": ("Daytime hours", "Unnamed: 13"),

        "ice": ("icewater ", "Unnamed: 5"),

        "marsquake": ("Earthquakes", "Unnamed: 5"),
        "moonquakes": ("Earthquakes", "Unnamed: 5"),

        "volcanic": ("volcanic activity", "Unnamed: 5"),

        "roughness": ("roughness", "Roughness Scale (1-5)"),
    }

    result = {}

    for key, (sheet, column) in common.items():

        result[key] = _earth_value(
            sheets,
            place,
            sheet,
            column
        )


    # Mineralogy data
    mineral_row = _find_site(
        sheets,
        "Mineralology",
        place
    )

    mineral_mean_columns = {

        "iron_oxides": "Unnamed: 5",
        "tio2": "Unnamed: 9",
        "mgo": "Unnamed: 13",
        "alumina": "Unnamed: 17",
        "cao": "Unnamed: 21",

        "olivine": "Unnamed: 25",
        "pyroxene": "Unnamed: 29",
        "plagioclase": "Unnamed: 33",

        "clays": "Unnamed: 37",
        "sulfates": "Unnamed: 41",
        "carbonates": "Unnamed: 45",
    }

    for key, column in mineral_mean_columns.items():

        if mineral_row is not None:
            result[key] = _num(
                mineral_row.get(column)
            )
        else:
            result[key] = None


    # Rock profile
    rock_row = _find_site(
        sheets,
        "Rock profile",
        place
    )

    if rock_row is not None:

        result["sedimentary"] = _num(
            rock_row.get("Unnamed: 5")
        )

        result["igneous"] = _num(
            rock_row.get("Unnamed: 8")
        )

        result["metamorphic"] = _num(
            rock_row.get("Unnamed: 11")
        )

    else:

        result["sedimentary"] = None
        result["igneous"] = None
        result["metamorphic"] = None


    # Lunar atmosphere is not comparable to Earth's atmosphere.
    if body.lower() == "moon":

        result["pressure"] = None
        result["humidity"] = None
        result["wind"] = None

        # Lunar ordinal thermal inertia is not SI-compatible.
        result["thermal_inertia"] = None

    return result


def _feature_definitions(body):

    if body.lower() == "mars":

        keys = [

            "elevation",
            "slope",

            "igneous",
            "sedimentary",
            "metamorphic",

            "olivine",
            "pyroxene",
            "plagioclase",

            "clays",
            "sulfates",
            "iron_oxides",

            "temperature",
            "water_ice",
            "wind",

            "daylight_summer",
            "daylight_winter",
            "radiation",
        ]

        labels = {

            "elevation": "Mean elevation",
            "slope": "Mean slope",

            "igneous": "Igneous rock",
            "sedimentary": "Sedimentary rock",
            "metamorphic": "Metamorphic rock",

            "olivine": "Olivine",
            "pyroxene": "Pyroxene",
            "plagioclase": "Plagioclase",

            "clays": "Clays",
            "sulfates": "Sulfates",
            "iron_oxides": "Iron oxides",

            "temperature": "Annual mean temperature",
            "water_ice": "Near-surface water/ice",
            "wind": "Wind speed",

            "daylight_summer": "Daylight at Ls 90",
            "daylight_winter": "Daylight at Ls 270",

            "radiation": "Radiation",
        }

    else:

        keys = [

            "elevation",
            "slope",

            "plagioclase",
            "pyroxene",
            "olivine",

            "iron_oxides",
            "tio2",
            "mgo",
            "alumina",
            "cao",

            "roughness",
            "temperature",
            "ice",
        ]

        labels = {

            "elevation": "Mean elevation",
            "slope": "Mean slope",

            "plagioclase": "Plagioclase",
            "pyroxene": "Pyroxene",
            "olivine": "Olivine",

            "iron_oxides": "FeO",
            "tio2": "TiO₂",
            "mgo": "MgO",
            "alumina": "Al₂O₃",
            "cao": "CaO",

            "roughness": "Surface roughness",
            "temperature": "Mean annual temperature",
            "ice": "Ice percentage",
        }

    return [
        (key, labels[key], 1.0)
        for key in keys
    ]


def rank_earth_analogues(
    body,
    quadrangle_row,
    earth_sheets,
    top_n=3
):


    body = body.strip().lower()

    if body not in {"mars", "moon"}:
        raise ValueError(
            "Body must be Mars or Moon."
        )

    if body == "mars":
        target = _mars_target(quadrangle_row)
    else:
        target = _moon_target(quadrangle_row)

    definitions = _feature_definitions(body)

    coords = earth_sheets.get("COORDINATES")

    if coords is None or "Place name" not in coords.columns:
        raise ValueError(
            "The Earth workbook is missing its COORDINATES worksheet."
        )

    sites = coords.iloc[EARTH_ROW_START:].dropna(
        subset=["Place name"]
    )

    records = []
    details = []

    earth_cache = {

        str(site["Place name"]).strip():
        _earth_features(
            body,
            earth_sheets,
            str(site["Place name"]).strip()
        )

        for _, site in sites.iterrows()
    }

    feature_values = {

        key: [
            _num(values.get(key))
            for values in earth_cache.values()
        ]

        for key, _, _ in definitions
    }


    for _, site in sites.iterrows():

        place = str(
            site["Place name"]
        ).strip()

        earth = earth_cache[place]

        weighted_score = 0.0
        available_weight = 0.0

        possible_weight = sum(
            weight
            for _, _, weight in definitions
        )

        matches = []


        for key, label, weight in definitions:

            target_value = _num(
                target.get(key)
            )

            earth_value = _num(
                earth.get(key)
            )

            if target_value is None or earth_value is None:
                continue


            # Normalize difference using the observed
            # spread among the available Earth sites.
            vals = [
                value
                for value in feature_values[key]
                if value is not None
            ]

            spread = (
                max(vals) - min(vals)
                if len(vals) > 1
                else 0.0
            )

            scale = max(
                spread,
                abs(target_value) * 0.25,
                1.0
            )


            similarity = max(
                0.0,
                1.0 - abs(
                    target_value - earth_value
                ) / scale
            ) * 100.0


            weighted_score += similarity * weight
            available_weight += weight

            matches.append(
                (
                    label,
                    similarity,
                    target_value,
                    earth_value
                )
            )


        if available_weight == 0:
            continue


        coverage = (
            100.0 * available_weight / possible_weight
        )

        final_score = (
            weighted_score / available_weight
        )


        records.append({

            "Earth analogue": place,

            "Terrain type": site.get(
                "Terrain type"
            ),

            "Country / region": site.get(
                "Country and region"
            ),

            "Similarity (%)": round(
                final_score, 1
            ),

            "Data coverage (%)": round(
                coverage, 1
            ),
        })


        for label, score, target_value, earth_value in matches:

            details.append({

                "Earth analogue": place,

                "Parameter": label,

                "Similarity (%)": round(
                    score, 1
                ),

                "Target value": target_value,

                "Earth value": earth_value,
            })


    ranked = pd.DataFrame(records)

    if ranked.empty:

        return (
            ranked,
            pd.DataFrame(
                columns=[
                    "Earth analogue",
                    "Parameter",
                    "Similarity (%)",
                    "Target value",
                    "Earth value"
                ]
            )
        )


    ranked = ranked.sort_values(

        ["Similarity (%)", "Data coverage (%)"],

        ascending=False

    ).head(top_n).reset_index(drop=True)


    ranked.insert(
        0,
        "Rank",
        range(1, len(ranked) + 1)
    )


    details_df = pd.DataFrame(details)

    details_df = details_df[
        details_df["Earth analogue"].isin(
            ranked["Earth analogue"]
        )
    ]

    details_df = details_df.sort_values(
        ["Earth analogue", "Similarity (%)"],
        ascending=[True, False]
    )


    return ranked, details_df
