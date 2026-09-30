import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime

# Page configuration for a professional look
st.set_page_config(page_title="PharmStock System", layout="wide")

# Professional Blue and White Styling
st.markdown("""
    <style>
    .main { background-color: #f0f4f8; }
    .stButton>button { width: 100%; background-color: #0056b3; color: white; border-radius: 12px; height: 3em; font-weight: bold; }
    .stMetric { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #0056b3; }
    .sidebar .sidebar-content { background-color: #ffffff; }
    h1, h2, h3 { color: #003366; }
    div[data-testid="stExpander"] { background-color: white; border-radius: 15px; }
    </style>
""", unsafe_allow_html=True)

# Load assets
@st.cache_resource
def load_assets():
    # Updated path to load the new optimized model
    model_path = "pharm_rf_model_opt.pkl"
    data_path = "streamlit_pharm_data.csv"
    model = joblib.load(model_path)
    data = pd.read_csv(data_path)
    data['period_start'] = pd.to_datetime(data['period_start'])
    return model, data

try:
    model, df = load_assets()
except Exception as e:
    st.error(f"System assets not found. Error: {e}. Please ensure analysis and training cells are executed.")
    st.stop()

# Sidebar Navigation
st.sidebar.title("🛡️ PharmStock System")
page = st.sidebar.selectbox("Menu", ["Executive Overview", "Smart Sales Forecast"])

if page == "Executive Overview":
    st.title("📈 System Analytics Dashboard")

    # KPI Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Items", len(df['item'].unique()))
    c2.metric("Avg demand", f"{df['sales_qty'].mean():.2f}")
    c3.metric("Stock Status", "Healthy")
    c4.metric("Active Locs", len(df['location'].unique()))

    # Visuals
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader("Monthly Revenue Velocity")
        trend = df.groupby('period_start')['sales_qty'].sum().reset_index()
        st.line_chart(trend.set_index('period_start'))

    with col_right:
        st.subheader("Top Items by Volume")
        top = df.groupby('item')['sales_qty'].sum().sort_values(ascending=False).head(5)
        st.bar_chart(top)

else:
    st.title("🔮 PharmStock System Forecasting Engine")
    st.write("Generate demand projections for individual SKUs.")

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            loc = st.selectbox("Operation Center", df['location'].unique())
            item = st.selectbox("Item ID", df[df['location']==loc]['item'].unique())
            target_date = st.date_input("Forecast Period", datetime(2026, 9, 1))

        with col2:
            # Auto-lag detection
            item_data = df[(df['item']==item) & (df['location']==loc)].sort_values('period_start')
            last_val = item_data['sales_qty'].iloc[-1] if not item_data.empty else 0.0

            l1 = st.number_input("Previous Month Qty", value=float(last_val))
            roll = st.number_input("Rolling 3-Month Mean", value=float(last_val))

    if st.button("Execute System Projection"):
        # Construct features based on trained model structure
        features = np.array([[
            target_date.year, target_date.month, target_date.day,
            target_date.weekday(), target_date.timetuple().tm_yday,
            target_date.isocalendar()[1],
            l1, l1, l1, roll, roll
        ]])

        pred = model.predict(features)[0]

        st.markdown(f"""
            <div style='background-color: white; padding: 30px; border-radius: 15px; border-left: 10px solid #0056b3; margin-top: 20px;'>
                <h3 style='margin:0; color:#0056b3;'>System Result: {pred:.2f} Units</h3>
                <p style='color:#64748b;'>Forecast generated for {target_date.strftime('%B %Y')}</p>
            </div>
        """, unsafe_allow_html=True)

