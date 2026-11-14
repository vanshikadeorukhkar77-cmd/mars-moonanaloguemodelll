
import streamlit as st

from data_loader import load_all_data
from coordinate_processor import process_coordinates
from quadrangle_finder import find_quadrangle
from similarity import rank_earth_analogues


st.set_page_config(
    page_title="Mars & Moon Analogue Model",
    page_icon="🌍",
    layout="wide"
)


st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #0F131A;

    background-image:
        radial-gradient(circle, white 1px, transparent 1.5px),
        radial-gradient(circle, white 1px, transparent 1.5px),
        radial-gradient(circle, rgba(255,255,255,0.7) 1px, transparent 1.5px),
        radial-gradient(circle, rgba(255,255,255,0.5) 1px, transparent 1.5px);

    background-size:
        100px 100px,
        150px 150px,
        200px 200px,
        120px 120px;

    background-position:
        0 0,
        40px 60px,
        100px 30px,
        70px 90px;

    color: white;
}

/* All general text */
.stApp,
.stApp p,
.stApp label,
.stApp span,
.stApp li {
    color: #FFFFFF;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #1B2836;
}

/* Headings */
h1, h2, h3, h4 {
    color: #E6B566 !important;
}

/* Input fields */
.stNumberInput input,
.stTextInput input {
    background-color: #253746;
    color: #FFFFFF;
    border: 1px solid #E6B566;
}

/* Buttons */
.stButton button,
.stFormSubmitButton button {
    background-color: #C77D3B;
    color: #FFFFFF;
    border-radius: 10px;
    border: none;
    font-weight: bold;
}

/* Button hover */
.stButton button:hover,
.stFormSubmitButton button:hover {
    background-color: #E6B566;
    color: #101820;
}

/* Metrics */
[data-testid="stMetric"] {
    background-color: #1B2836;
    padding: 15px;
    border-radius: 12px;
}

/* Expanders */
[data-testid="stExpander"] {
    background-color: #1B2836;
    border: 1px solid #E6B566;
    border-radius: 10px;
}

/* Links */
a {
    color: #E6B566 !important;
}

/* Dividers */
hr {
    border-color: #526273;
}

</style>
""", unsafe_allow_html=True)



@st.cache_data
def get_data():
    return load_all_data()


st.title("🌍 Vanshika is the best person ever")

st.write(
    "Locate a Mars or Moon quadrangle using coordinates "
    "and identify the three closest Earth analogue locations."
)


# Load datasets
try:
    data = get_data()

except Exception as exc:
    st.error(f"Could not load Excel datasets: {exc}")
    st.stop()


# Select planetary body
body = st.radio(
    "Choose planetary body",
    ["Mars", "The Moon"],
    horizontal=True
)


entry_type = st.radio(
    "Choose coordinate input type",
    ["One coordinate", "A range of coordinates"],
    horizontal=True
)


# Coordinate input
with st.form("coordinate_form"):

    if entry_type == "One coordinate":

        col1, col2 = st.columns(2)

        with col1:
            latitude = st.number_input(
                "Latitude (°)",
                min_value=-90.0,
                max_value=90.0,
                value=0.0,
                step=0.1
            )

        with col2:
            longitude = st.number_input(
                "Longitude (°)",
                min_value=-180.0,
                max_value=360.0,
                value=0.0,
                step=0.1
            )

        submitted = st.form_submit_button(
            "Find quadrangle and Earth analogues",
            type="primary"
        )

    else:

        st.caption(
            "Enter the latitude and longitude limits "
            "of your rectangular region."
        )

        c1, c2 = st.columns(2)

        with c1:
            lat_min = st.number_input(
                "Minimum latitude (°)",
                min_value=-90.0,
                max_value=90.0,
                value=-10.0,
                step=0.1
            )

            lon_start = st.number_input(
                "Starting longitude (°)",
                min_value=-180.0,
                max_value=360.0,
                value=0.0,
                step=0.1
            )

        with c2:
            lat_max = st.number_input(
                "Maximum latitude (°)",
                min_value=-90.0,
                max_value=90.0,
                value=10.0,
                step=0.1
            )

            lon_end = st.number_input(
                "Ending longitude (°)",
                min_value=-180.0,
                max_value=360.0,
                value=20.0,
                step=0.1
            )

        submitted = st.form_submit_button(
            "Calculate midpoint and compare",
            type="primary"
        )


# Process submitted coordinates
if submitted:

    try:

        if entry_type == "One coordinate":

            lat, lon, method = process_coordinates(
                latitude=latitude,
                longitude=longitude
            )

        else:

            lat, lon, method = process_coordinates(
                lat_min=lat_min,
                lat_max=lat_max,
                lon_start=lon_start,
                lon_end=lon_end
            )


        # Display processed coordinates
        st.subheader("Processed coordinates")

        col1, col2 = st.columns(2)

        col1.metric("Latitude", f"{lat:.4f}°")
        col2.metric("East longitude", f"{lon:.4f}°")

        st.caption(method)


        # Find quadrangle
        match = find_quadrangle(
            body,
            lat,
            lon,
            data["mars_index"],
            data["moon_index"]
        )


        if match is None:

            st.warning(
                "No quadrangle was found for these coordinates. "
                "Please check the input and dataset coverage."
            )

        else:

            st.success(
                f"Yay! {body} quadrangle found: {match['quadrangle']}"
            )

            # Retrieve original quadrangle row
            if body == "Mars":

                raw_df = data["mars_raw"]
                id_col = "Quad"

                st.write(
                    f"**Quadrangle name:** {match['name']}"
                )

            else:

                raw_df = data["moon_raw"]
                id_col = "Quadrangle"


            raw_matches = raw_df[
                raw_df[id_col].astype(str)
                == str(match["quadrangle"])
            ]


            if raw_matches.empty:

                st.error(
                    "Could not retrieve the selected quadrangle data."
                )

            else:

                quadrangle_row = raw_matches.iloc[0]


                # Earth analogue comparison
                st.divider()

                st.header("🌎 Top 3 Earth Analogue Locations")

                with st.spinner(
                    "Calculating Earth analogue similarities..."
                ):

                    ranked, details = rank_earth_analogues(
                        body,
                        quadrangle_row,
                        data["earth_sheets"],
                        top_n=3
                    )


                if ranked.empty:

                    st.warning(
                        "Not enough shared numeric parameters "
                        "were available for comparison."
                    )

                else:

                    st.caption(
                        "Results are ranked using a provisional "
                        "weighted similarity calculation. "
                        "Data coverage shows how many configured "
                        "parameters could be compared."
                    )

                    st.dataframe(
                        ranked,
                        hide_index=True,
                        use_container_width=True
                    )


                    # Detailed parameter comparisons
                    st.subheader(
                        "Parameter-level comparison"
                    )

                    for _, result in ranked.iterrows():

                        place = result["Earth analogue"]

                        with st.expander(
                            f"#{int(result['Rank'])} — {place} "
                            f"({result['Similarity (%)']:.1f}% similarity)"
                        ):

                            subset = details[
                                details["Earth analogue"] == place
                            ].drop(
                                columns=["Earth analogue"]
                            )

                            st.dataframe(
                                subset,
                                hide_index=True,
                                use_container_width=True
                            )


    except Exception as exc:

        st.error(
            f"Could not complete the comparison: {exc}"
        )


st.divider()

st.caption(
    "Vanshika's note: The similarity engine is a provisional "
    "weighted-distance ranking, not a trained ML classifier. "
    "The supplied Earth workbook DOES NOT contain values "
    "that are 100% correct :(. Results should be treated as exploratory, "
    "not scientifically validated predictions."
)
