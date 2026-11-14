
import streamlit as st
from data_loader import load_all_data
from coordinate_processor import process_coordinates
from quadrangle_finder import find_quadrangle

st.set_page_config(
    page_title="Mars & Moon Analogue Model",
    page_icon="🌍",
    layout="centered"
)


@st.cache_data
def get_data():
    return load_all_data()


st.title("🌍 Mars & Moon Terrestrial Analogue Model")

st.write(
    "Identify terrestrial analogues for selected locations "
    "on Mars and the Moon."
)

st.info(
    "Enter a coordinate or coordinate range to identify "
    "the corresponding quadrangle."
)

try:
    data = get_data()
except Exception as exc:
    st.error(f"Could not load the datasets: {exc}")
    st.stop()


body = st.radio(
    "Choose the celestial body",
    ["Mars", "Moon"],
    horizontal=True
)

entry_type = st.radio(
    "Coordinate input",
    ["One coordinate", "A coordinate range"],
    horizontal=True
)

with st.form("coordinate_form"):

    if entry_type == "One coordinate":

        col1, col2 = st.columns(2)

        with col1:
            latitude = st.number_input(
                "Latitude (°)",
                min_value=-90.0,
                max_value=90.0,
                value=0.0
            )

        with col2:
            longitude = st.number_input(
                "Longitude (°)",
                min_value=-180.0,
                max_value=360.0,
                value=0.0
            )

        submitted = st.form_submit_button("Find analogues")

    else:

        col1, col2 = st.columns(2)

        with col1:
            lat_min = st.number_input(
                "Minimum latitude (°)",
                min_value=-90.0,
                max_value=90.0,
                value=-10.0
            )

            lon_start = st.number_input(
                "Starting longitude (°)",
                min_value=-180.0,
                max_value=360.0,
                value=0.0
            )

        with col2:
            lat_max = st.number_input(
                "Maximum latitude (°)",
                min_value=-90.0,
                max_value=90.0,
                value=10.0
            )

            lon_end = st.number_input(
                "Ending longitude (°)",
                min_value=-180.0,
                max_value=360.0,
                value=20.0
            )

        submitted = st.form_submit_button("Find analogues")


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
                "Please check your input."
            )

        else:

            st.success("Quadrangle successfully identified!")

            st.write(f"**Selected body:** {body}")

            st.write(
                f"**Quadrangle:** {match['quadrangle']}"
            )

            st.caption(method)

            st.info(
                "The quadrangle's parameter data has been retrieved "
                "internally. The terrestrial analogue comparison "
                "will appear here once the similarity engine is added."
            )

    except Exception as exc:

        st.error(str(exc))


st.divider()

st.caption(
    "Mars and Moon terrestrial analogue identification model."
)
