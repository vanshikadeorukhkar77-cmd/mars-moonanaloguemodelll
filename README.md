# Mars & Moon Terrestrial Analogue Model

This starter version loads the supplied Mars, Moon and Earth Excel workbooks and implements:
1. Single-coordinate input.
2. Coordinate-range midpoint calculation (FMP).
3. Mars/Moon quadrangle lookup.
4. Display of the selected quadrangle's stored parameter data.

The weighted Earth-analogue similarity ranking is the next development stage.

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Install dependencies:

   `pip install -r requirements.txt`

4. Start the app:

   `streamlit run app.py`

## GitHub

Upload the complete project folder, including the `data` folder, to a GitHub repository.
Do not rename the Excel files inside `data` unless you also update `data_loader.py`.

## Important data conventions

- User-entered longitude may be negative or positive.
- The coordinate processor converts longitude to 0–360° east for matching.
- Longitude intervals crossing 0°/360° are supported.
- Moon pressure, humidity and wind are not used for comparison in the planned Moon model.
- Suitability is omitted for now.
- The current app is a coordinate/quadrangle foundation, not yet a trained machine-learning model.
