# =========================================================
# INSTITUTIONAL QUANT PLATFORM V2
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from risk.regime_engine import (
    detect_market_regime
)

from strategy.sector_rotation import (
    compute_sector_strength
)

from core.meta_factor_engine import (
    compute_meta_factors
)

from signals.signal_engine import (
    generate_signals
)

from portfolio.optimizer import (
    optimize_portfolio
)

from monitoring.health_check import (
    generate_monitoring_report
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(

    page_title="Institutional Quant Platform",

    page_icon="📊",

    layout="wide",

    initial_sidebar_state="expanded"

)

# =========================================================
# LOAD FACTOR DATA
# =========================================================

@st.cache_data(ttl=3600)

def load_data():

    return pd.read_parquet(
        "data/parquet/factor_scores.parquet"
    )

factor_df = load_data()

# =========================================================
# REGIME ENGINE
# =========================================================

regime_data = detect_market_regime(
    factor_df
)

# =========================================================
# SECTOR ENGINE
# =========================================================

sector_df = compute_sector_strength(
    factor_df
)

# =========================================================
# META FACTORS
# =========================================================

meta_df = compute_meta_factors(

    factor_df,
    sector_df,
    regime_data

)

# =========================================================
# SIGNAL ENGINE
# =========================================================

signal_df = generate_signals(
    meta_df
)

# =========================================================
# PORTFOLIO
# =========================================================

portfolio_df = optimize_portfolio(

    signal_df,
    regime_data,
    total_capital=1000000

)

# =========================================================
# MONITORING
# =========================================================

monitoring_report = generate_monitoring_report(

    portfolio_df,
    regime_data

)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(
    "⚙️ Institutional Controls"
)

selected_signals = st.sidebar.multiselect(

    "Filter Signals",

    signal_df["signal"].unique(),

    default=signal_df["signal"].unique()

)

search_stock = st.sidebar.text_input(
    "Search Symbol"
)

min_confidence = st.sidebar.slider(

    "Minimum Confidence",

    0,

    100,

    50

)

# =========================================================
# FILTER DATA
# =========================================================

filtered_df = signal_df.copy()

filtered_df = filtered_df[

    filtered_df["signal"].isin(
        selected_signals
    )

]

filtered_df = filtered_df[

    filtered_df["confidence"]
    >= min_confidence

]

if search_stock:

    filtered_df = filtered_df[

        filtered_df["symbol"]

        .str.contains(
            search_stock.upper(),
            na=False
        )

    ]

# =========================================================
# HEADER
# =========================================================

st.title(
    "📊 Institutional Quant Platform"
)

st.caption(
    "Institutional Portfolio Intelligence System"
)

# =========================================================
# REGIME PANEL
# =========================================================

st.subheader(
    "🌍 Market Regime"
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Regime",
        regime_data["regime"]
    )

with col2:

    st.metric(
        "India VIX",
        regime_data["vix"]
    )

with col3:

    st.metric(
        "Market Breadth",
        regime_data["breadth"]
    )

with col4:

    st.metric(
        "NIFTY",
        regime_data["nifty_close"]
    )

# =========================================================
# PORTFOLIO SUMMARY
# =========================================================

st.subheader(
    "💼 Portfolio Summary"
)

summary = monitoring_report["summary"]

c1, c2, c3, c4, c5 = st.columns(5)

with c1:

    st.metric(
        "Positions",
        summary.get(
            "total_positions",
            0
        )
    )

with c2:

    st.metric(
        "Allocation",
        summary.get(
            "total_allocation",
            0
        )
    )

with c3:

    st.metric(
        "Confidence",
        summary.get(
            "avg_confidence",
            0
        )
    )

with c4:

    st.metric(
        "Meta Score",
        summary.get(
            "avg_meta_score",
            0
        )
    )

with c5:

    st.metric(
        "Expected 30D",
        summary.get(
            "avg_expected_30d",
            0
        )
    )

# =========================================================
# RISK ALERTS
# =========================================================

st.subheader(
    "🚨 Institutional Risk Alerts"
)

alerts = monitoring_report["alerts"]

if alerts:

    for alert in alerts:

        st.warning(alert)

else:

    st.success(
        "No active institutional risk alerts"
    )

# =========================================================
# SECTOR EXPOSURE
# =========================================================

st.subheader(
    "🏢 Sector Exposure"
)

sector_exposure_df = monitoring_report[
    "sector_exposure"
]

if not sector_exposure_df.empty:

    fig = px.treemap(

        sector_exposure_df,

        path=["sector"],

        values="portfolio_weight"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================================================
# SIGNAL DISTRIBUTION
# =========================================================

st.subheader(
    "📈 Signal Distribution"
)

signal_distribution_df = monitoring_report[
    "signal_distribution"
]

if not signal_distribution_df.empty:

    pie_fig = px.pie(

        signal_distribution_df,

        names="signal",

        values="count",

        hole=0.5

    )

    st.plotly_chart(
        pie_fig,
        use_container_width=True
    )

# =========================================================
# TOP SIGNALS
# =========================================================

st.subheader(
    "🚀 Institutional Signal Rankings"
)

display_columns = [

    "symbol",
    "sector",
    "theme",
    "signal",
    "confidence",
    "meta_score",
    "expected_5d",
    "expected_15d",
    "expected_30d",
    "hold_days",
    "upside_score"

]

st.dataframe(

    filtered_df[display_columns],

    use_container_width=True,

    height=600

)

# =========================================================
# META SCORE ANALYTICS
# =========================================================

st.subheader(
    "📊 Meta Score Analytics"
)

scatter_fig = px.scatter(

    filtered_df,

    x="confidence",

    y="meta_score",

    color="signal",

    size="upside_score",

    hover_name="symbol"

)

st.plotly_chart(
    scatter_fig,
    use_container_width=True
)

# =========================================================
# SYSTEM HEALTH
# =========================================================

st.subheader(
    "🖥️ System Health"
)

health = monitoring_report[
    "system_health"
]

health_df = pd.DataFrame(

    list(health.items()),

    columns=["Component", "Status"]

)

st.dataframe(

    health_df,

    use_container_width=True

)