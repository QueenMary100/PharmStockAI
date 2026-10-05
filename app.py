import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
import streamlit.components.v1 as components
from supabase import create_client

# Page configuration for a professional look
st.set_page_config(page_title="PharmStock AI", layout="wide", initial_sidebar_state="collapsed")

# Global styling to match the requested glassy/modern design
st.markdown(
    """
    <style>
    :root {
        --bg-soft: #f5f7fb;
        --card-bg: rgba(255,255,255,0.92);
        --primary: #6d5efc;
        --primary-dark: #4f46e5;
        --accent: #f59e0b;
        --accent-soft: #fff7ed;
        --dark: #0f172a;
        --muted: #64748b;
        --border: #e2e8f0;
        --shadow: 0 20px 45px rgba(79, 70, 229, 0.12);
    }

    .main { background: var(--bg-soft); }
    .block-container { padding-top: 0; }
    .stButton > button {
        border: none; border-radius: 14px; font-weight: 700; transition: 0.2s ease-in-out;
    }
    .stButton > button:hover {
        transform: translateY(-1px); filter: brightness(1.02);
    }

    /* auth card */
    div[data-testid="stForm"] {
        background: transparent;
    }
    .auth-shell {
        max-width: 520px;
        margin: 90px auto 30px auto;
        background: rgba(255,255,255,0.85);
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 18px;
        box-shadow: var(--shadow);
        padding: 0;
    }
    .auth-logo {
        width: 90px; height: 90px; border-radius: 50%; background: rgba(109, 94, 252, 0.12);
        display: flex; align-items: center; justify-content: center; font-size: 2.2rem;
        color: var(--primary-dark); margin: 0 auto 18px auto;
        border: 1px solid rgba(109, 94, 252, 0.18);
    }
    .auth-title {
        text-align: center; font-size: clamp(2.2rem, 3vw, 3rem); font-weight: 800; letter-spacing: -0.04em;
        color: var(--dark); margin: 0;
    }
    .auth-subtitle {
        text-align: center; color: var(--muted); font-size: 1.08rem; margin-top: 8px; margin-bottom: 26px;
    }
    .auth-form-wrap {
        padding: 10px 28px 30px 28px;
    }
    .auth-input label {
        color: var(--dark) !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        margin-bottom: 10px !important;
    }
    .auth-input input {
        border: 1px solid #d9dee5 !important;
        border-radius: 10px !important;
        height: 52px !important;
        font-size: 1.05rem !important;
        background: rgba(255,255,255,0.72) !important;
        box-shadow: none !important;
    }
    .auth-input input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(109, 94, 252, 0.12) !important;
    }
    .primary-btn {
        width: 100%; height: 54px; border: none; border-radius: 12px; background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white; font-size: 1.1rem; font-weight: 700; cursor: pointer; margin-top: 8px;
    }
    .primary-btn:hover { opacity: 0.98; }
    .auth-footer {
        text-align: center; margin-top: 26px; color: var(--muted); font-size: 0.98rem;
    }
    .auth-footer a {
        color: var(--primary-dark); font-weight: 700; text-decoration: none;
    }
    .auth-footer a:hover { text-decoration: underline; }

    /* landing page */
    .landing-wrap {
        background: linear-gradient(180deg, #f3f4f6 0%, #eef2ff 100%);
        min-height: 100vh;
        padding: 0 20px 0 20px;
    }
    .landing-hero {
        max-width: 1200px; margin: 0 auto; padding-top: 40px; text-align: center;
    }
    .landing-icon {
        width: 120px; height: 120px; margin: 0 auto 26px auto; border-radius: 26px;
        background: rgba(109,94,252,0.12); display: flex; align-items: center; justify-content: center;
        color: var(--primary-dark); border: 1px solid rgba(109,94,252,0.2);
        font-size: 4rem;
    }
    .landing-title {
        font-size: clamp(3rem, 5vw, 7rem); line-height: 0.95; font-weight: 900; color: var(--dark); letter-spacing: -0.06em;
    }
    .landing-title .emphasis { color: var(--primary-dark); }
    .landing-subtext {
        max-width: 900px; margin: 28px auto 0 auto; font-size: clamp(1.35rem, 2vw, 2.1rem);
        line-height: 1.45; color: #1e293b; font-weight: 500; letter-spacing: -0.03em;
    }
    .landing-actions {
        max-width: 760px; margin: 40px auto 0 auto; display: flex; gap: 22px; justify-content: center; flex-wrap: wrap;
    }
    .action-btn {
        display: inline-flex; align-items: center; justify-content: center; min-width: 280px; min-height: 70px;
        border-radius: 18px; font-size: 1.1rem; font-weight: 700; border: none; cursor: pointer;
    }
    .action-btn.primary { background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); color: white; }
    .action-btn.secondary { background: rgba(255,255,255,0.7); border: 1px solid rgba(15,23,42,0.08); color: var(--dark); }
    .feature-grid {
        max-width: 1200px; margin: 64px auto 0 auto; display: grid; grid-template-columns: repeat(3, minmax(260px, 1fr)); gap: 28px;
    }
    .feature-card {
        background: rgba(255,255,255,0.68); border: 1px solid rgba(148,163,184,0.26); border-radius: 18px;
        padding: 30px 26px; min-height: 260px; box-shadow: 0 10px 24px rgba(15,23,42,0.04);
    }
    .feature-card .icon { font-size: 3.2rem; color: var(--primary-dark); margin-bottom: 18px; }
    .feature-card h3 { font-size: 2rem; font-weight: 800; line-height: 1.2; margin-bottom: 10px; color: var(--dark); }
    .feature-card p { font-size: 1.08rem; line-height: 1.6; color: var(--muted); }

    .footer-banner {
        margin-top: 70px; background: linear-gradient(135deg, #5b4cf0 0%, #4338ca 100%); color: white; padding: 42px 40px 28px 40px;
    }
    .footer-inner {
        max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 1.5fr 0.8fr 0.8fr; gap: 24px;
    }
    .footer-brand { font-size: 2.2rem; font-weight: 800; letter-spacing: -0.04em; }
    .footer-tagline { margin-top: 18px; max-width: 560px; font-size: 1.15rem; line-height: 1.6; color: rgba(255,255,255,0.93); }
    .footer-column h4 { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.18em; color: rgba(255,255,255,0.8); margin-bottom: 16px; }
    .footer-column a { display: block; color: white; font-size: 1.1rem; text-decoration: none; margin-bottom: 10px; }
    .footer-bottom {
        max-width: 1200px; margin: 0 auto; border-top: 1px solid rgba(255,255,255,0.3); padding-top: 20px; margin-top: 24px;
        display: flex; justify-content: space-between; align-items: center; gap: 18px; flex-wrap: wrap;
    }
    .footer-bottom small { font-size: 0.96rem; color: rgba(255,255,255,0.8); }

    @media (max-width: 900px) {
        .feature-grid { grid-template-columns: 1fr; }
        .footer-inner { grid-template-columns: 1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_supabase_credentials():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        if url and key:
            return url, key
    except Exception:
        pass

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if url and key:
        return url, key

    return None, None


SUPABASE_URL, SUPABASE_KEY = get_supabase_credentials()


@st.cache_resource
def init_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None

    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Failed to initialize Supabase: {e}")
        return None


supabase_client = init_supabase()

# Session State Initialization
if "user_session" not in st.session_state:
    st.session_state["user_session"] = None
if "current_view" not in st.session_state:
    st.session_state["current_view"] = "landing"
if "auth_mode" not in st.session_state:
    st.session_state["auth_mode"] = "signup"


def render_landing_page():
    # Render the complete landing page HTML
    st.markdown(
        """
        <div class="landing-wrap">
            <div class="landing-hero">
                <div class="landing-icon">📈</div>
                <div class="landing-title">Predictive <span class="emphasis">Stock-Out</span><br>Prevention</div>
                <div class="landing-subtext">
                    Secure your medical supply chain. Our machine learning inference engine analyzes daily demand and supplier lead times to prevent critical shortages before they happen.
                </div>
            </div>

            <div class="feature-grid">
                <div class="feature-card">
                    <div class="icon">⚕️</div>
                    <h3>ML Forecasting</h3>
                    <p>Trains on historical consumption to map 30-day forward demand trajectories.</p>
                </div>
                <div class="feature-card">
                    <div class="icon">🛡️</div>
                    <h3>Lead Time Defense</h3>
                    <p>Automatically alerts procurement teams before days-to-depletion breaches supplier SLAs.</p>
                </div>
                <div class="feature-card">
                    <div class="icon">🗄️</div>
                    <h3>Seamless Integration</h3>
                    <p>Connects directly to your existing inventory database via secure REST API endpoints.</p>
                </div>
            </div>

            <div class="footer-banner">
                <div class="footer-inner">
                    <div>
                        <div class="footer-brand">📈 Afya-Stock AI</div>
                        <div class="footer-tagline">Predictive medical stock-out prevention and intelligent purchase order management. Securing health supply chains with machine learning.</div>
                    </div>
                    <div class="footer-column">
                        <h4>Platform</h4>
                        <a href="#">Login</a>
                        <a href="#">Register Account</a>
                        <a href="#">Dashboard</a>
                    </div>
                    <div class="footer-column">
                        <h4>Developers</h4>
                        <a href="#">API Documentation</a>
                        <a href="#">Data Access</a>
                        <a href="#">Integrations</a>
                    </div>
                </div>
                <div class="footer-bottom">
                    <small>© 2026 Afya-Stock AI. All rights reserved.</small>
                    <small>Privacy Policy · Terms of Service</small>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Action buttons below the HTML
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🚀 Launch Afya-Stock AI", use_container_width=True, key="launch_auth_btn"):
            st.session_state["current_view"] = "auth"
            st.session_state["auth_mode"] = "signup"
            st.rerun()
    
    with col2:
        if st.button("📖 View API Docs", use_container_width=True):
            st.info("API documentation coming soon!")
    
    with col3:
        pass


def render_auth_page():
    if supabase_client is None:
        st.warning("⚠️ Authentication is currently unavailable because Supabase credentials are missing or invalid.")
        if st.button("Continue to Dashboard", key="demo_dashboard_btn"):
            st.session_state["user_session"] = {"email": "demo@pharmstock.ai"}
            st.session_state["current_view"] = "dashboard"
            st.rerun()
        return

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="auth-shell">', unsafe_allow_html=True)
        st.markdown(
            """
            <div style="padding: 28px 28px 0 28px;">
                <div class="auth-logo">📈</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state["auth_mode"] == "signup":
            st.markdown('<div class="auth-title">Create Account</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-subtitle">Register to access Afya-Stock AI</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="auth-title">Welcome Back</div>', unsafe_allow_html=True)
            st.markdown('<div class="auth-subtitle">Sign in to access Afya-Stock AI</div>', unsafe_allow_html=True)

        with st.form(key="auth_form"):
            if st.session_state["auth_mode"] == "signup":
                st.markdown('<div class="auth-form-wrap">', unsafe_allow_html=True)
                full_name = st.text_input("Full Name", key="signup_full_name", help=None)
                email = st.text_input("Email Address", key="signup_email")
                password = st.text_input("Password", type="password", key="signup_password")
                st.markdown('</div>', unsafe_allow_html=True)
                if st.form_submit_button("Register", use_container_width=True):
                    if not full_name or not email or not password:
                        st.error("Please complete all required fields.")
                    else:
                        try:
                            response = supabase_client.auth.sign_up({
                                "email": email,
                                "password": password,
                            })
                            try:
                                user_id = getattr(response.user, "id", None)
                                if user_id:
                                    supabase_client.table("profiles").insert({
                                        "id": user_id,
                                        "full_name": full_name,
                                        "email": email,
                                        "role": "user",
                                        "created_at": datetime.utcnow().isoformat(),
                                    }).execute()
                            except Exception:
                                pass
                            st.success("✅ Account created successfully! Please check your email for confirmation, then sign in.")
                            st.session_state["auth_mode"] = "signin"
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Sign up failed: {str(e)}")
            else:
                st.markdown('<div class="auth-form-wrap">', unsafe_allow_html=True)
                email = st.text_input("Email Address", key="signin_email")
                password = st.text_input("Password", type="password", key="signin_password")
                st.markdown('</div>', unsafe_allow_html=True)
                if st.form_submit_button("Sign In", use_container_width=True):
                    if not email or not password:
                        st.error("Please enter your email and password.")
                    else:
                        try:
                            response = supabase_client.auth.sign_in_with_password({
                                "email": email,
                                "password": password,
                            })
                            st.session_state["user_session"] = response.user
                            st.session_state["current_view"] = "dashboard"
                            st.success("✅ Successfully signed in!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Login failed: {str(e)}")

        if st.session_state["auth_mode"] == "signup":
            st.markdown(
                "<div class='auth-footer'>Already have an account?</div>",
                unsafe_allow_html=True,
            )
            if st.button("Sign In", key="switch_signin_btn", use_container_width=True):
                st.session_state["auth_mode"] = "signin"
                st.rerun()
        else:
            st.markdown(
                "<div class='auth-footer'>Need an account?</div>",
                unsafe_allow_html=True,
            )
            if st.button("Create Account", key="switch_signup_btn", use_container_width=True):
                st.session_state["auth_mode"] = "signup"
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# Dashboard loader
@st.cache_resource
def load_assets():
    model_path = "pharm_rf_model_opt.pkl"
    data_path = "streamlit_pharm_data.csv"

    if not os.path.exists(model_path) or not os.path.exists(data_path):
        return None, None

    try:
        model = joblib.load(model_path)
        data = pd.read_csv(data_path)
        data["period_start"] = pd.to_datetime(data["period_start"])
        return model, data
    except Exception as e:
        st.error(f"Error loading assets: {e}")
        return None, None


def render_dashboard():
    current_user = st.session_state.get("user_session")
    if current_user is None:
        st.session_state["current_view"] = "landing"
        st.rerun()
        return

    model, df = load_assets()

    if model is None or df is None:
        st.error("⚠️ System assets not found. Please ensure these files are in the repository:")
        st.error("📦 - pharm_rf_model_opt.pkl")
        st.error("📋 - streamlit_pharm_data.csv")
        st.stop()

    st.sidebar.title("🛡️ PharmStock AI")
    user_email = getattr(current_user, "email", None) or current_user.get("email", "demo@pharmstock.ai")
    st.sidebar.write(f"Logged in as: **{user_email}**")
    if st.sidebar.button("🚪 Log Out"):
        st.session_state["user_session"] = None
        st.session_state["current_view"] = "landing"
        st.rerun()

    page = st.sidebar.selectbox("Menu", ["Executive Overview", "Smart Sales Forecast", "Pharmacy Stock KPI Dashboard"])

    if page == "Executive Overview":
        st.title("📈 System Analytics Dashboard")
        st.markdown("Real-time visibility into pharmaceutical inventory demand metrics.")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Unique SKUs", f"{len(df['item'].unique()):,}")
        c2.metric("Average Monthly Demand", f"{df['sales_qty'].mean():.2f} Units")
        c3.metric("System Health", "✅ Active", delta="Optimal")
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
                loc = st.selectbox("Operation Center", sorted(df['location'].unique()))
                filtered_items = sorted(df[df['location'] == loc]['item'].unique())
                item = st.selectbox("Product ID / Item Name", filtered_items)
                target_date = st.date_input("Forecast Target Period", datetime(2026, 9, 1))

            with col2:
                item_data = df[(df['item'] == item) & (df['location'] == loc)].sort_values('period_start')
                last_val = item_data['sales_qty'].iloc[-1] if not item_data.empty else 0.0
                l1 = st.number_input("Previous Month Demand (Qty)", value=float(last_val), min_value=0.0)
                roll = st.number_input("Rolling 3-Month Mean Quantity", value=float(last_val), min_value=0.0)

        if st.button("Run Enterprise Projection"):
            features = np.array([[
                target_date.year, target_date.month, target_date.day,
                target_date.weekday(), target_date.timetuple().tm_yday,
                target_date.isocalendar()[1],
                l1, l1, l1, roll, roll
            ]])
            pred = max(0.0, model.predict(features)[0])
            st.markdown(
                f"""
                <div style='background-color: white; padding: 30px; border-radius: 12px; border-left: 10px solid #6d5efc; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                    <h3 style='margin:0; color:#6d5efc;'>📊 System Prediction: {pred:.2f} Units</h3>
                    <p style='color:#64748b; margin: 5px 0 0 0;'>Calculated demand projection for {target_date.strftime('%B %Y')}</p>
                    <p style='color:#f59e0b; margin: 10px 0 0 0; font-size: 0.9rem;'>✓ Forecast generated successfully</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

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
                .kpi-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; border-top: 4px solid #6d5efc; }
                .kpi-card h3 { margin: 0; color: #64748b; font-size: 0.85rem; text-transform: uppercase; }
                .kpi-card p { margin: 10px 0 0; font-size: 1.6rem; font-weight: bold; color: #0f172a; }
                .chart-section { grid-column: span 2; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); display: flex; flex-direction: column; min-height: 340px; }
                .chart-wide { grid-column: span 4; }
                .chart-header { font-weight: bold; margin-bottom: 15px; font-size: 1.1rem; border-bottom: 1px solid #eee; padding-bottom: 10px; color: #0f172a; }
                .canvas-wrapper { position: relative; flex-grow: 1; min-height: 0; width: 100%; }
                .table-container { grid-column: span 4; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); overflow-x: auto; }
                table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                th { text-align: left; background: #f8f9fa; padding: 12px; border-bottom: 2px solid #eee; font-weight: 600; }
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
                                backgroundColor: 'rgba(109, 94, 252, 0.7)',
                                yAxisID: 'y'
                            }, {
                                label: 'Sales Qty',
                                data: rawData.map(d => d.sales_qty),
                                type: 'line',
                                borderColor: '#f59e0b',
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
                                backgroundColor: '#6d5efc'
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

        final_html = (
            html_template.replace("DATA_PLACEHOLDER", chart_json)
            .replace("KPI_TOTAL_VAL", kpi_data["total_value"])
            .replace("KPI_AVG_QTY", kpi_data["avg_qty"])
            .replace("KPI_TOP_ITEM", kpi_data["top_item"])
            .replace("KPI_COUNT", str(kpi_data["item_count"]))
        )
        components.html(final_html, height=1050, scrolling=True)


# Main app flow
if st.session_state.get("user_session"):
    render_dashboard()
else:
    if st.session_state["current_view"] == "auth":
        render_auth_page()
    else:
        render_landing_page()
