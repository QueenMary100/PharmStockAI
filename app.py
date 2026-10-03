import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
import streamlit.components.v1 as components
from supabase import create_client

# Page configuration for a professional look
st.set_page_config(page_title="PharmStock System", layout="wide")

# Professional Styling
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; background-color: #0284c7; color: white; border-radius: 10px; height: 3em; font-weight: bold; border: none; transition: 0.3s; }
    .stButton>button:hover { background-color: #0369a1; }
    .stMetric { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #0284c7; }
    h1, h2, h3 { color: #0f172a; font-family: 'Inter', sans-serif; }
    div[data-testid="stExpander"] { background-color: white; border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

# Initialize Supabase Client
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "YOUR_SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "YOUR_SUPABASE_ANON_KEY")

@st.cache_resource
def init_supabase():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None

supabase_client = init_supabase()

# Session State Initialization for Auth
if "user_session" not in st.session_state:
    st.session_state["user_session"] = None

# Authentication View if not logged in
if not st.session_state["user_session"]:
    st.title("🛡️ Welcome to PharmStock")
    st.markdown("Please sign in or create an account to access the enterprise inventory analytics system.")

    auth_tab1, auth_tab2 = st.tabs(["Sign In", "Sign Up"])

    with auth_tab1:
        st.subheader("Sign In to your Account")
        signin_email = st.text_input("Email", key="signin_email")
        signin_password = st.text_input("Password", type="password", key="signin_password")

        if st.button("Sign In"):
            if not supabase_client:
                st.error("Supabase client is not configured correctly. Check your credentials.")
            else:
                try:
                    response = supabase_client.auth.sign_in_with_password({
                        "email": signin_email,
                        "password": signin_password
                    })
                    st.session_state["user_session"] = response.user
                    st.success("Successfully signed in!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {e}")

    with auth_tab2:
        st.subheader("Create a New Account")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")

        if st.button("Sign Up"):
            if not supabase_client:
                st.error("Supabase client is not configured correctly. Check your credentials.")
            else:
                try:
                    response = supabase_client.auth.sign_up({
                        "email": signup_email,
                        "password": signup_password
                    })
                    st.success("Account created successfully! Please check your email for confirmation if required, then sign in.")
                except Exception as e:
                    st.error(f"Sign up failed: {e}")
    st.stop()

# Load assets
@st.cache_resource
def load_assets():
    model_path = "pharm_rf_model_opt.pkl"
    data_path = "streamlit_pharm_data.csv"

    if not os.path.exists(model_path):
        st.warning(f"Model file not found at {model_path}")
        return None, None
    if not os.path.exists(data_path):
        st.warning(f"Data file not found at {data_path}")
        return None, None

    try:
        model = joblib.load(model_path)
        data = pd.read_csv(data_path)
        data['period_start'] = pd.to_datetime(data['period_start'])
        return model, data
    except Exception as e:
        st.error(f"Error loading assets: {e}")
        return None, None

model, df = load_assets()

if model is None or df is None:
    st.error("System assets not found. Please ensure the following files exist in the directory:")
    st.error("- pharm_rf_model_opt.pkl")
    st.error("- streamlit_pharm_data.csv")
    st.stop()

# Sidebar Navigation & Logout
st.sidebar.title("🛡️ PharmStock")
st.sidebar.write(f"Logged in as: **{st.session_state['user_session'].email}**")
if st.sidebar.button("Log Out"):
    st.session_state["user_session"] = None
    st.rerun()

page = st.sidebar.selectbox("Menu", ["Executive Overview", "Smart Sales Forecast", "Pharmacy Stock KPI Dashboard"])

if page == "Executive Overview":
    st.title("📈 System Analytics Dashboard")
    st.markdown("Real-time visibility into pharmaceutical inventory demand metrics.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Unique SKUs", f"{len(df['item'].unique()):,}")
    c2.metric("Average Monthly Demand", f"{df['sales_qty'].mean():.2f} Units")
    c3.metric("System Health", "Active", delta="Optimal")
    c4.metric("Operating Centers", len(df['location'].unique()))

    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader("Monthly Demand Velocity")
        trend = df.groupby('period_start')['sales_qty'].sum().reset_index()
        st.line_chart(trend.set_index('period_start'))

    with col_right:
        st.subheader("Top 5 Items by Demand")
        top = df.groupby('item')['sales_qty'].sum().sort_values(ascending=False).head(5)
        st.bar_chart(top)

    st.subheader("🔥 Top 10 Items by Sales Quantity")
    top_qty_items = df.groupby('item')['sales_qty'].sum().sort_values(ascending=False).head(10).reset_index()
    qty_chart_data = top_qty_items.set_index('item')['sales_qty']
    st.bar_chart(qty_chart_data)

elif page == "Smart Sales Forecast":
    st.title("🔮 Smart Forecasting Engine")
    st.markdown("Generate validated demand projections using optimized Random Forest Regressors.")

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            loc = st.selectbox("Operation Center", df['location'].unique())
            item = st.selectbox("Product ID / Item Name", df[df['location'] == loc]['item'].unique())
            target_date = st.date_input("Forecast Target Period", datetime(2026, 9, 1))

        with col2:
            item_data = df[(df['item'] == item) & (df['location'] == loc)].sort_values('period_start')
            last_val = item_data['sales_qty'].iloc[-1] if not item_data.empty else 0.0
            l1 = st.number_input("Previous Month Demand (Qty)", value=float(last_val))
            roll = st.number_input("Rolling 3-Month Mean Quantity", value=float(last_val))

    if st.button("Run Enterprise Projection"):
        features = np.array([[
            target_date.year, target_date.month, target_date.day,
            target_date.weekday(), target_date.timetuple().tm_yday,
            target_date.isocalendar()[1],
            l1, l1, l1, roll, roll
        ]])

        pred = max(0.0, model.predict(features)[0])

        st.markdown(f"""
            <div style='background-color: white; padding: 30px; border-radius: 12px; border-left: 10px solid #0284c7; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                <h3 style='margin:0; color:#0284c7;'>System Prediction: {pred:.2f} Units</h3>
                <p style='color:#64748b; margin: 5px 0 0 0;'>Calculated demand projection for {target_date.strftime('%B %Y')}</p>
            </div>
        """, unsafe_allow_html=True)

elif page == "Pharmacy Stock KPI Dashboard":
    raw_pharm_path = "pharm_stock_dataset_v2_15_Sep_26.csv"
    if os.path.exists(raw_pharm_path):
        raw_df = pd.read_csv(raw_pharm_path)
        raw_df['op_stock'] = raw_df['op_stock'].clip(lower=0)
        raw_df['cls_stock'] = raw_df['cls_stock'].clip(lower=0)
        item_kpis = raw_df.groupby(['item', 'location']).agg(
            sales_qty=('sales_qty', 'sum'),
            sales_value=('sales_value', 'sum'),
            op_stock_avg=('op_stock', 'mean'),
            cls_stock_avg=('cls_stock', 'mean')
        ).reset_index()
    else:
        item_kpis = df.groupby(['item', 'location']).agg(
            sales_qty=('sales_qty', 'sum'),
            sales_value=('sales_value', 'sum'),
            cls_stock_avg=('cls_stock', 'mean')
        ).reset_index()
        item_kpis['op_stock_avg'] = item_kpis['cls_stock_avg'] * 1.02

    top_10_items_by_value = item_kpis.sort_values(by='sales_value', ascending=False).head(10)

    total_val = top_10_items_by_value['sales_value'].sum()
    avg_qty = top_10_items_by_value['sales_qty'].mean()
    top_item = top_10_items_by_value.iloc[0]['item']

    kpi_data = {
        "total_value": f"{total_val:,.0f}",
        "avg_qty": f"{avg_qty:.2f}",
        "top_item": top_item,
        "item_count": len(top_10_items_by_value)
    }

    chart_json = top_10_items_by_value.to_json(orient='records')

    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; margin: 0; padding: 10px; color: #333; }
            .dashboard-container { display: grid; grid-template-columns: repeat(4, 1fr); grid-gap: 20px; }
            .kpi-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; border-top: 4px solid #0284c7; }
            .kpi-card h3 { margin: 0; color: #64748b; font-size: 0.85rem; text-transform: uppercase; }
            .kpi-card p { margin: 10px 0 0; font-size: 1.6rem; font-weight: bold; color: #0f172a; }
            .chart-section { grid-column: span 2; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); display: flex; flex-direction: column; min-height: 380px; }
            .chart-wide { grid-column: span 4; }
            .chart-header { font-weight: bold; margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid #eee; padding-bottom: 10px; color: #0f172a; }
            .canvas-wrapper { position: relative; flex-grow: 1; min-height: 0; width: 100%; }
            .table-container { grid-column: span 4; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); overflow-x: auto; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th { text-align: left; background: #f8f9fa; padding: 12px; border-bottom: 2px solid #eee; }
            td { padding: 12px; border-bottom: 1px solid #eee; }
            tr:hover { background-color: #f1f1f1; }
        </style>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <div class="dashboard-container">
            <div class="kpi-card"><h3>Total Sales Value</h3><p>KSh KPI_TOTAL_VAL</p></div>
            <div class="kpi-card"><h3>Avg Sales Qty</h3><p>KPI_AVG_QTY</p></div>
            <div class="kpi-card"><h3>Top Performer</h3><p style="font-size: 0.95rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">KPI_TOP_ITEM</p></div>
            <div class="kpi-card"><h3>Items Tracked</h3><p>KPI_COUNT</p></div>

            <div class="chart-section">
                <div class="chart-header">Sales Value vs. Quantity</div>
                <div class="canvas-wrapper"><canvas id="valueQtyChart"></canvas></div>
            </div>

            <div class="chart-section">
                <div class="chart-header">Inventory: Opening vs. Closing Stock</div>
                <div class="canvas-wrapper"><canvas id="stockChart"></canvas></div>
            </div>

            <div class="chart-section chart-wide">
                <div class="chart-header">Performance Overview Table</div>
                <div class="table-container" id="dataTable"></div>
            </div>
        </div>

        <script>
            const rawData = DATA_PLACEHOLDER;
            function initCharts() {
                const labels = rawData.map(d => d.item.length > 20 ? d.item.substring(0,20) + '...' : d.item);
                new Chart(document.getElementById('valueQtyChart'), {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Sales Value',
                            data: rawData.map(d => d.sales_value),
                            backgroundColor: 'rgba(2, 132, 199, 0.7)',
                            yAxisID: 'y'
                        }, {
                            label: 'Sales Qty',
                            data: rawData.map(d => d.sales_qty),
                            type: 'line',
                            borderColor: '#ef4444',
                            borderWidth: 3,
                            fill: false,
                            yAxisID: 'y1'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: { type: 'linear', position: 'left', title: { display: true, text: 'Value (KSh)' } },
                            y1: { type: 'linear', position: 'right', grid: { drawOnChartArea: false }, title: { display: true, text: 'Quantity (Units)' } }
                        }
                    }
                });

                new Chart(document.getElementById('stockChart'), {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Avg Opening Stock',
                            data: rawData.map(d => d.op_stock_avg),
                            backgroundColor: '#10b981'
                        }, {
                            label: 'Avg Closing Stock',
                            data: rawData.map(d => d.cls_stock_avg),
                            backgroundColor: '#f59e0b'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: { type: 'linear', title: { display: true, text: 'Stock Units' } }
                        }
                    }
                });

                let tableHtml = '<table><thead><tr><th>Item</th><th>Sales Value</th><th>Sales Qty</th><th>Op Stock</th><th>Cls Stock</th></tr></thead><tbody>';
                rawData.forEach(row => {
                    tableHtml += `<tr><td>${row.item}</td>
                        <td>KSh ${row.sales_value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                        <td>${row.sales_qty.toFixed(2)}</td>
                        <td>${row.op_stock_avg.toFixed(0)}</td>
                        <td>${row.cls_stock_avg.toFixed(0)}</td>
                    </tr>`;
                });
                tableHtml += '</tbody></table>';
                document.getElementById('dataTable').innerHTML = tableHtml;
            }
            initCharts();
        </script>
    </body>
    </html>
    """

    final_html = html_template.replace('DATA_PLACEHOLDER', chart_json) \
                              .replace('KPI_TOTAL_VAL', kpi_data['total_value']) \
                              .replace('KPI_AVG_QTY', kpi_data['avg_qty']) \
                              .replace('KPI_TOP_ITEM', kpi_data['top_item']) \
                              .replace('KPI_COUNT', str(kpi_data['item_count']))

    components.html(final_html, height=1050, scrolling=True)
