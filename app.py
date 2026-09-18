# %%writefile app.py
import streamlit as st
import pandas as pd
import numpy as np
import joblib

# Page configuration
st.set_page_config(page_title="PharmStock AI Forecaster", layout="wide")

st.title("💊 PharmStock AI: Sales Forecasting Dashboard")
st.write("Predict future sales quantities using our trained Random Forest model.")

# Load saved model and data
@st.cache_resource
def load_assets():
    model = joblib.load("/content/drive/MyDrive/ENGAGEMary_Diana/Engage_Pharm_Data/models/pharm_rf_model.pkl")
    data = pd.read_csv("/content/drive/MyDrive/ENGAGEMary_Diana/Engage_Pharm_Data/models/streamlit_pharm_data.csv")
    return model, data

model, df = load_assets()

# Sidebar inputs for user selection
st.sidebar.header("Forecast Parameters")
selected_location = st.sidebar.selectbox("Select Location", df['location'].unique())
filtered_items = df[df['location'] == selected_location]['item'].unique()
selected_item = st.sidebar.selectbox("Select Item", filtered_items)

# Pull recent historical stats for this item to set smart defaults
item_subset = df[(df['item'] == selected_item) & (df['location'] == selected_location)]
recent_sales = item_subset['sales_qty'].iloc[-1] if not item_subset.empty else 1.0

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
dayofyear = pd.Timestamp(f"{year}-{month:02d}-{day:02d}").dayofyear
weekofyear = pd.Timestamp(f"{year}-{month:02d}-{day:02d}").isocalendar().week

# Construct feature array in the exact order the model expects
input_features = np.array([[
    year, month, day, dayofweek, dayofyear, weekofyear,
    sales_qty_lag1, sales_qty_lag2, sales_qty_lag3,
    sales_qty_roll_mean3, sales_qty_roll_mean6
]])

# Prediction button
if st.button("Generate Prediction", type="primary"):
    prediction = model.predict(input_features)[0]
    
    st.success(f"### Predicted Sales Quantity: {prediction:.2f} units")
    
    # Simple stockout warning heuristic
    if prediction > sales_qty_lag1:
        st.warning("⚠️ **High Demand Alert:** Predicted sales exceed last month's quantity. Consider increasing reorder quantities.")
    else:
        st.info("ℹ️ **Stable Demand:** Sales projected to remain steady or decrease.")
