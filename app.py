import streamlit as st
st.set_page_config(
    page_title="EasyJet DCF Model Analysis",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils import load_excel_file
from dcf_analyzer import DCFAnalyzer
from advanced_visualizations import AdvancedVisualizations
from monte_carlo import run_monte_carlo  # Ensure this function is defined in monte_carlo.py

# ------------------ THEME TOGGLE ------------------
theme = st.sidebar.selectbox("Select Theme", ["Dark Mode", "Light Mode"], index=0)

# In Dark Mode: black backgrounds (#000) and white text (#fff)
# In Light Mode: dark navy background (#001f3f) with white text
if theme == "Dark Mode":
    app_bg = "#000"
    plot_bg = "#000"
    text_color = "#fff"
    metric_text = "#fff"
else:
    app_bg = "#001f3f"  # Dark navy background
    plot_bg = "#001f3f"
    text_color = "#fff"
    metric_text = "#fff"

# ------------------ DYNAMIC CSS ------------------
st.markdown(f"""
<style>
/* 1) Overall app styling */
.stApp {{
    background-color: {app_bg} !important;
    color: {text_color} !important;
}}
h1, h2, h3, h4, p, span {{
    font-family: 'Inter', sans-serif;
    color: {text_color} !important;
}}

/* Force st.metric text to the chosen color */
[data-testid="metric-container"] {{
    background-color: transparent !important;
    color: {metric_text} !important;
}}
[data-testid="metric-container"] * {{
    color: {metric_text} !important;
    fill: {metric_text} !important;
}}

/* 2) Header boxes: dark grey (#333) background with bright blue (#00BFFF) text */
div[data-testid="stylable_container"][id="current_price_container"],
div[data-testid="stylable_container"][id="multiples_price_container"],
div[data-testid="stylable_container"][id="perpetuity_price_container"],
div[data-testid="stylable_container"][id="wacc_growth_container"] {{
    background-color: #333 !important;
    border-radius: 10px !important;
    padding: 15px !important;
}}
div[data-testid="stylable_container"][id="current_price_container"] *,
div[data-testid="stylable_container"][id="multiples_price_container"] *,
div[data-testid="stylable_container"][id="perpetuity_price_container"] *,
div[data-testid="stylable_container"][id="wacc_growth_container"] * {{
    color: #00BFFF !important;
    fill: #00BFFF !important;
}}

/* 3) Key Variables & Valuation Results: Force metric values to bright blue */
.dcf-key-variables [data-testid="stMetricValue"],
.valuation-results [data-testid="stMetricValue"],
[data-testid="stMetricValue"] {{
    color: #00BFFF !important;
    fill: #00BFFF !important;
}}

/* 4) Tabs styling */
.stTabs [data-baseweb="tab"] {{
    background-color: #FFA500 !important;
    color: #000 !important;
    border-radius: 4px 4px 0px 0px;
    padding-top: 10px;
    padding-bottom: 10px;
    margin-right: 2px;
}}
.stTabs [aria-selected="true"] {{
    background-color: #FF6600 !important;
    color: #000 !important;
    border-bottom: 2px solid #FF6600;
}}
.stTabs [data-baseweb="tab"] > div {{
    color: #000 !important;
}}

/* 5) Button styling */
div.stButton > button:first-child {{
    background-color: #1E88E5;
    color: white;
    border-radius: 5px;
    border: none;
    padding: 10px 25px;
    font-size: 16px;
}}
div.stButton > button:hover {{
    background-color: #1565C0;
    color: white;
}}

/* 6) Sidebar override: Force sidebar background to navy blue (#001f3f) with white text */
[data-testid="stSidebar"] > div:first-child {{
    background-color: #001f3f !important;
    color: #fff !important;
}}
[data-testid="stSidebar"] * {{
    color: #fff !important;
    fill: #fff !important;
}}
</style>
""", unsafe_allow_html=True)

def main():
    EXCEL_PATH = "attached_assets/EasyJet- complete.xlsx"
    dcf_analyzer = None
    adv_viz = None

    # Load the Excel file from attached_assets or via upload
    if os.path.exists(EXCEL_PATH):
        try:
            df_dict, _ = load_excel_file(EXCEL_PATH)
            if 'DCF' not in df_dict:
                st.error("The Excel file does not contain a 'DCF' tab.")
                return
            dcf_analyzer = DCFAnalyzer(df_dict['DCF'])
            adv_viz = AdvancedVisualizations(dcf_analyzer)
        except Exception as e:
            st.error(f"Error processing local Excel file: {e}")
            return
    else:
        st.info("No local Excel file found. Please upload your EasyJet financial model Excel file.")
        uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])
        if uploaded_file:
            try:
                df_dict, _ = load_excel_file(uploaded_file)
                if 'DCF' not in df_dict:
                    st.error("The uploaded file does not contain a 'DCF' tab.")
                    return
                dcf_analyzer = DCFAnalyzer(df_dict['DCF'])
                adv_viz = AdvancedVisualizations(dcf_analyzer)
            except Exception as e:
                st.error(f"Error processing the uploaded file: {e}")
                return
        else:
            st.warning("Please upload a valid Excel file.")
            return

    if not dcf_analyzer:
        st.error("Unable to initialize DCF Analyzer. Exiting.")
        return

    # Header with EasyJet logo and title
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("https://logos-download.com/wp-content/uploads/2016/03/EasyJet_logo_logotype_emblem.png", width=100)
    with col2:
        st.title("EasyJet Financial DCF Analysis Dashboard")
        st.subheader("Interactive analysis of EasyJet's Discounted Cash Flow model")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Main tabs: Interactive DCF Dashboard, Documentation, Monte Carlo
    main_tab1, main_tab2, main_tab3 = st.tabs([
        "📊 Interactive DCF Dashboard",
        "📝 Documentation",
        "🎲 Monte Carlo"
    ])

    # ------------------ TAB 1: INTERACTIVE DCF DASHBOARD ------------------
    with main_tab1:
        st.subheader("Main Financial Analysis")
        st.write("### Key Metrics")
        with st.container():
            st.markdown('<div class="dcf-key-variables">', unsafe_allow_html=True)
            dcf_analyzer.display_key_metrics()
            st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")
        with st.container():
            st.markdown('<div class="valuation-results">', unsafe_allow_html=True)
            dcf_analyzer.display_enterprise_value_chart()
            st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")
        with st.container():
            st.markdown('<div class="valuation-results">', unsafe_allow_html=True)
            dcf_analyzer.display_share_price_chart()
            st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")
        if adv_viz:
            adv_viz.display_visual_dashboard()

        st.subheader("Additional Advanced Visualizations")
        adv_tab1, adv_tab2, adv_tab3, adv_tab4, adv_tab5 = st.tabs([
            "3D EV Sensitivity",
            "Share Price Sunburst",
            "WACC Analysis",
            "Two-Factor Heatmap",
            "Peer Analysis"
        ])
        with adv_tab1:
            adv_viz._display_3d_sensitivity_with_real_data()
        with adv_tab2:
            adv_viz.display_share_price_sunburst()
        with adv_tab3:
            adv_viz.display_wacc_analysis_dashboard()
        with adv_tab4:
            adv_viz.display_two_factor_heatmap()
        with adv_tab5:
            adv_viz.display_peer_analysis()

    # ------------------ TAB 2: DOCUMENTATION ------------------
    with main_tab2:
        st.header("Documentation and Help")
        with st.expander("What is a DCF Analysis?", expanded=True):
            st.markdown("""
            Discounted Cash Flow (DCF) is a valuation method used to estimate the value of an investment based on its expected future cash flows.
            The DCF analysis determines the value of a company today by discounting future cash flows using a rate (WACC).

            **Key components include:**
            - Projected Free Cash Flows
            - Terminal Value
            - Discount Rate (WACC)
            - Present Value
            """)
        with st.expander("How to Use This Dashboard"):
            st.markdown("""
            ### Using the Interactive Features
            1. **Enterprise Value Analysis:** Explore the 3D visualizations and sensitivity charts.
            2. **Share Price Analysis:** Review charts breaking down the share price components.
            3. **Monte Carlo Simulation:** Adjust parameters to simulate future price scenarios.

            **Tips:**
            - Use the tabs to navigate.
            - Hover over charts for detailed information.
            - Adjust sliders to test various assumptions.
            """)
        with st.expander("Methodology & Calculations"):
            st.markdown("""
            ### DCF Methodology
            This dashboard uses historical financial data and projections for a DCF analysis.
            It includes:
            - Free Cash Flow Forecasts
            - Terminal Value Calculations (Perpetuity and Multiples Methods)
            - Sensitivity Analysis on key variables (WACC, Terminal Growth)

            **Monte Carlo Simulation:**
            The simulation randomly samples from historical returns to project possible future price scenarios.
            """)
        with st.expander("About EasyJet"):
            st.markdown("""
            **Company Overview:**
            EasyJet plc is a leading low-cost airline in Europe, operating over 1,000 routes.

            **Key Facts:**
            - Founded: 1995
            - Fleet: ~300 aircraft
            - Destinations: 150+ airports
            """)



    # ------------------ TAB 3: MONTE CARLO ------------------
    with main_tab3:
        st.header("Monte Carlo Simulation")
        try:
            returns_df = pd.read_csv("attached_assets/EZJ_L_returns.csv", index_col=0, parse_dates=True)
            st.markdown("### Ten years of historical returns data from Refinitiv API")
            st.dataframe(returns_df, height=300)
            returns_array = returns_df["Returns"].dropna().values
        except Exception as e:
            st.error(f"Error loading historical returns CSV: {e}")
            returns_array = None

        if dcf_analyzer:
            default_price = dcf_analyzer.variables.get("current_share_price", 1.0)
        else:
            default_price = 1.0

        if returns_array is not None:
            n_sims = st.slider("Number of Simulations", min_value=100, max_value=5000, value=1000, step=100)
            horizon = st.slider("Simulation Horizon (Days)", min_value=30, max_value=365, value=252, step=10)
            initial_price = st.number_input("Starting Price", value=float(default_price))

            if st.button("Run Monte Carlo Simulation"):
                final_prices = run_monte_carlo(
                    returns_array=returns_array,
                    n_simulations=n_sims,
                    horizon=horizon,
                    initial_price=initial_price
                )
                st.write(f"Mean Final Price: £{np.mean(final_prices):.2f}")
                st.write(f"Median Final Price: £{np.median(final_prices):.2f}")
                st.write(f"Max Final Price: £{max(final_prices):.2f}")
                st.write(f"Min Final Price: £{min(final_prices):.2f}")

                df_prices = pd.DataFrame({"Final Price": final_prices})
                fig = px.histogram(
                    df_prices,
                    x="Final Price",
                    nbins=50,
                    title="Distribution of Final Simulated Prices"
                )
                # Force the histogram bars and title to be bright blue
                fig.update_traces(marker_color="#00BFFF")
                fig.update_layout(
                    title_font_color="#00BFFF",
                    yaxis_title="Number of Simulations",
                    paper_bgcolor=plot_bg,
                    plot_bgcolor=plot_bg,
                    font_color=text_color
                )
                fig.update_xaxes(tickfont=dict(color=text_color))
                fig.update_yaxes(tickfont=dict(color=text_color))
                st.plotly_chart(fig, use_container_width=True)

        st.image("https://logos-download.com/wp-content/uploads/2016/03/EasyJet_logo_logotype_emblem.png", width=150)

    st.markdown("""
    <div style="background-color:#FFA500; padding:10px; border-radius:5px; margin-top:20px; text-align:center;">
      <p style="margin:0; font-size:14px; color:#000;">
        This interactive DCF analysis dashboard is for educational and analytical purposes only.
        It is not financial advice. Data is based on historical information and financial projections.
      </p>
    </div>
    """, unsafe_allow_html=True)

# Final CSS override to force header boxes to grey background (#444)
st.markdown("""
<style>
[data-testid="stylable_container"]#current_price_container,
[data-testid="stylable_container"]#multiples_price_container,
[data-testid="stylable_container"]#perpetuity_price_container,
[data-testid="stylable_container"]#wacc_growth_container {
    background-color: #444 !important;
}
</style>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
