import os
from pathlib import Path

import gdown
import joblib
import numpy as np
import pandas as pd
import streamlit as st

# Page configuration
st.set_page_config(page_title="PharmStock AI Forecaster", layout="wide")

st.title("💊 PharmStock AI: Sales Forecasting Dashboard")
st.write("Predict future sales quantities using our trained Random Forest model.")

# The model is too large for GitHub/Streamlit source uploads, so download it
# from the public Google Drive file once and reuse the local cached copy.
MODEL_FILE_ID = "1DsKNdWVxov-jedRoPpQ6bu-aoUvLMvsm"
MODEL_CACHE_PATH = Path(os.getenv("PHARM_MODEL_PATH", ".streamlit_cache/pharm_rf_model.pkl"))
DATA_PATH = Path(
    os.getenv(
        "PHARM_DATA_PATH",
        "/content/drive/MyDrive/ENGAGEMary_Diana/Engage_Pharm_Data/models/streamlit_pharm_data.csv",
    )
)


@st.cache_resource(show_spinner="Loading forecasting model and data...")
def load_assets():
    MODEL_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not MODEL_CACHE_PATH.exists():
        downloaded_path = gdown.download(
            id=MODEL_FILE_ID,
            output=str(MODEL_CACHE_PATH),
            quiet=False,
        )
        if downloaded_path is None:
            raise RuntimeError(
                "The model could not be downloaded. Check that the Google Drive file "
                "is shared as 'Anyone with the link'."
            )

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Sales data was not found at {DATA_PATH}. Set the PHARM_DATA_PATH "
            "environment variable to the deployed CSV location."
        )

    model = joblib.load(MODEL_CACHE_PATH)
    data = pd.read_csv(DATA_PATH)
    return model, data


try:
    model, df = load_assets()
except Exception as exc:
    st.error(f"Unable to load application assets: {exc}")
    st.info(
        "The model is downloaded from Google Drive. The CSV still needs to be "
        "available locally or configured with PHARM_DATA_PATH."
    )
    st.stop()

# Sidebar inputs for user selection
st.sidebar.header("Forecast Parameters")
selected_location = st.sidebar.selectbox("Select Location", df["location"].unique())
filtered_items = df[df["location"] == selected_location]["item"].unique()
selected_item = st.sidebar.selectbox("Select Item", filtered_items)

# Pull recent historical stats for this item to set smart defaults
item_subset = df[(df["item"] == selected_item) & (df["location"] == selected_location)]
recent_sales = item_subset["sales_qty"].iloc[-1] if not item_subset.empty else 1.0

st.subheader(f"Forecasting for: `{selected_item}` at `{selected_location}`")

# Input features configuration matching your training schema
col1, col2 = st.columns(2)

with col1:
    year = st.number_input("Year", min_value=2023, max_value=2030, value=2026)
    month = st.slider("Month", min_value=1, max_value=12, value=9)
    day = st.number_input("Day", min_value=1, max_value=31, value=1)
    dayofweek = st.slider("Day of Week (0=Mon, 6=Sun)", 0, 6, 1)

with col2:
    sales_qty_lag1 = st.number_input("Sales Qty (1 Month Ago)", value=float(recent_sales))
    sales_qty_lag2 = st.number_input("Sales Qty (2 Months Ago)", value=float(recent_sales))
    sales_qty_lag3 = st.number_input("Sales Qty (3 Months Ago)", value=float(recent_sales))
    sales_qty_roll_mean3 = st.number_input("3-Month Rolling Mean Sales", value=float(recent_sales))
    sales_qty_roll_mean6 = st.number_input("6-Month Rolling Mean Sales", value=float(recent_sales))

# Additional time-based feature calculation
date_value = pd.Timestamp(f"{year}-{month:02d}-{day:02d}")
dayofyear = date_value.dayofyear
weekofyear = date_value.isocalendar().week

# Construct feature array in the exact order the model expects
input_features = np.array(
    [[
        year,
        month,
        day,
        dayofweek,
        dayofyear,
        weekofyear,
        sales_qty_lag1,
        sales_qty_lag2,
        sales_qty_lag3,
        sales_qty_roll_mean3,
        sales_qty_roll_mean6,
    ]]
)

# Prediction button
if st.button("Generate Prediction", type="primary"):
    prediction = model.predict(input_features)[0]

    st.success(f"### Predicted Sales Quantity: {prediction:.2f} units")

    # Simple stockout warning heuristic
    if prediction > sales_qty_lag1:
        st.warning(
            "⚠️ **High Demand Alert:** Predicted sales exceed last month's quantity. "
            "Consider increasing reorder quantities."
        )
    else:
        st.info("ℹ️ **Stable Demand:** Sales projected to remain steady or decrease.")
