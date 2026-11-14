import streamlit as st
from data_loader import load_all_data
from coordinate_processor import process_coordinates
from quadrangle_finder import find_quadrangle

st.set_page_config(page_title="Mars & Moon Analogue Model", page_icon="🌍", layout="centered")

@st.cache_data
def get_data():
    return load_all_data()

st.title("🌍 Mars & Moon Terrestrial Analogue Model")
st.write("Find the extraterrestrial quadrangle for a coordinate, then compare it with Earth locations.")
st.info("This is the first working stage: coordinate processing and quadrangle identification. The weighted Earth-analogue ranking will be added in the next stage.")

try:
    data = get_data()
except Exception as exc:
    st.error(f"Could not load the Excel datasets: {exc}")
    st.stop()

body = st.radio("Choose the body", ["Mars", "Moon"], horizontal=True)
entry_type = st.radio("What are you entering?", ["One coordinate", "A coordinate range"], horizontal=True)

with st.form("coordinate_form"):
    if entry_type == "One coordinate":
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude (°)", min_value=-90.0, max_value=90.0, value=0.0, step=0.1)
        with col2:
            longitude = st.number_input("Longitude (°)", min_value=-180.0, max_value=360.0, value=0.0, step=0.1)
        submitted = st.form_submit_button("Find quadrangle")
    else:
        st.caption("Enter the latitude limits and the two longitude limits of your rectangular area.")
        c1, c2 = st.columns(2)
        with c1:
            lat_min = st.number_input("Minimum latitude (°)", min_value=-90.0, max_value=90.0, value=-10.0, step=0.1)
            lon_start = st.number_input("Starting longitude (°)", min_value=-180.0, max_value=360.0, value=0.0, step=0.1)
        with c2:
            lat_max = st.number_input("Maximum latitude (°)", min_value=-90.0, max_value=90.0, value=10.0, step=0.1)
            lon_end = st.number_input("Ending longitude (°)", min_value=-180.0, max_value=360.0, value=20.0, step=0.1)
        submitted = st.form_submit_button("Calculate midpoint and find quadrangle")

if submitted:
    try:
        if entry_type == "One coordinate":
            lat, lon, method = process_coordinates(latitude=latitude, longitude=longitude)
        else:
            lat, lon, method = process_coordinates(
                lat_min=lat_min, lat_max=lat_max, lon_start=lon_start, lon_end=lon_end
            )

        st.subheader("Processed coordinate")
        a, b = st.columns(2)
        a.metric("Latitude", f"{lat:.4f}°")
        b.metric("East longitude", f"{lon:.4f}°")
        st.caption(method)

        match = find_quadrangle(
            body, lat, lon, data["mars_index"], data["moon_index"]
        )
        if match is None:
            st.warning("No quadrangle was found for this coordinate. Check the input and the coverage of the quadrangle grid.")
        else:
            st.success(f"Quadrangle found: {match['quadrangle']}")
            if body == "Mars":
                st.write(f"**Name:** {match['name']}")
                raw_row = data["mars_raw"].loc[
                    data["mars_raw"]["Quad"].astype(str) == str(match["quadrangle"])
                ].iloc[0]
                st.write("**Stored quadrangle data**")
                st.dataframe(raw_row.to_frame("Value"), use_container_width=True)
            else:
                raw_row = data["moon_raw"].loc[
                    data["moon_raw"]["Quadrangle"].astype(str) == str(match["quadrangle"])
                ].iloc[0]
                st.write("**Stored quadrangle data**")
                st.dataframe(raw_row.to_frame("Value"), use_container_width=True)
    except Exception as exc:
        st.error(str(exc))

st.divider()
st.caption("Data note: the supplied workbooks contain estimated/modelled values and missing entries. The later similarity stage will exclude unavailable parameters rather than treating them as zero.")
