# =========================================================
# INSTITUTIONAL QUANT PLATFORM
# =========================================================

import streamlit as st
import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go

from core.market_regime import detect_market_regime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Institutional Quant Platform",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data(ttl=3600)
def load_data():

    try:

        df = pd.read_parquet(
            "data/parquet/factor_scores.parquet"
        )

        return df

    except Exception as e:

        st.error(f"Data loading failed: {e}")

        return pd.DataFrame()

factor_df = load_data()

# =========================================================
# EMPTY CHECK
# =========================================================

if factor_df.empty:

    st.warning(
        "No factor data found. Run pipeline first."
    )

    st.stop()

# =========================================================
# MARKET REGIME
# =========================================================

regime_data = detect_market_regime(
    factor_df
)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(
    "⚙️ Institutional Controls"
)

# Signal Filter
signal_options = sorted(
    factor_df["signal"].dropna().unique()
)

selected_signals = st.sidebar.multiselect(

    "Filter Signals",

    signal_options,

    default=signal_options
)

# Search
search_stock = st.sidebar.text_input(
    "Search Symbol"
)

# Score Filter
min_score = st.sidebar.slider(

    "Minimum Institutional Score",

    0,

    100,

    60
)

# =========================================================
# FILTER DATA
# =========================================================

filtered_df = factor_df.copy()

filtered_df = filtered_df[
    filtered_df["signal"].isin(
        selected_signals
    )
]

filtered_df = filtered_df[
    filtered_df["institutional_score"]
    >= min_score
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
    "Institutional Intelligence Dashboard"
)

# =========================================================
# MARKET REGIME PANEL
# =========================================================

st.subheader(
    "🌍 Market Regime"
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Regime",
        regime_data.get(
            "regime",
            "UNKNOWN"
        )
    )

with col2:

    st.metric(
        "Trend",
        regime_data.get(
            "trend_strength",
            0
        )
    )

with col3:

    st.metric(
        "Volatility",
        round(
            regime_data.get(
                "volatility",
                0
            ),
            2
        )
    )

with col4:

    st.metric(
        "Momentum",
        round(
            regime_data.get(
                "momentum",
                0
            ),
            2
        )
    )

# =========================================================
# TOP LEVEL METRICS
# =========================================================

st.subheader(
    "📈 Institutional Metrics"
)

m1, m2, m3, m4, m5 = st.columns(5)

with m1:

    st.metric(
        "Stocks",
        len(filtered_df)
    )

with m2:

    st.metric(
        "Avg Score",
        round(
            filtered_df[
                "institutional_score"
            ].mean(),
            2
        )
    )

with m3:

    st.metric(
        "Avg RSI",
        round(
            filtered_df["rsi"].mean(),
            2
        )
    )

with m4:

    st.metric(
        "Avg Momentum",
        round(
            filtered_df[
                "momentum_20"
            ].mean(),
            2
        )
    )

with m5:

    st.metric(
        "Avg Sharpe",
        round(
            filtered_df[
                "sharpe_ratio"
            ].mean(),
            2
        )
    )

# =========================================================
# SIGNAL DISTRIBUTION
# =========================================================

st.subheader(
    "📊 Signal Distribution"
)

signal_counts = (
    filtered_df["signal"]
    .value_counts()
    .reset_index()
)

signal_counts.columns = [
    "signal",
    "count"
]

fig_signal = px.pie(

    signal_counts,

    names="signal",

    values="count",

    hole=0.5
)

st.plotly_chart(
    fig_signal,
    use_container_width=True
)

# =========================================================
# SECTOR DISTRIBUTION
# =========================================================

if "sector" in filtered_df.columns:

    st.subheader(
        "🏢 Sector Distribution"
    )

    sector_counts = (
        filtered_df["sector"]
        .value_counts()
        .reset_index()
    )

    sector_counts.columns = [
        "sector",
        "count"
    ]

    fig_sector = px.treemap(

        sector_counts,

        path=["sector"],

        values="count"
    )

    st.plotly_chart(
        fig_sector,
        use_container_width=True
    )

# =========================================================
# META FACTOR SCATTER
# =========================================================

st.subheader(
    "📊 Institutional Scatter Analysis"
)

scatter_fig = px.scatter(

    filtered_df,

    x="institutional_score",

    y="momentum_20",

    color="signal",

    size="volume_ratio",

    hover_name="symbol"
)

st.plotly_chart(
    scatter_fig,
    use_container_width=True
)

# =========================================================
# TOP STOCKS
# =========================================================

st.subheader(
    "🚀 Top Institutional Stocks"
)

display_columns = [

    "symbol",
    "sector",
    "signal",
    "institutional_score",
    "rsi",
    "momentum_20",
    "trend_score",
    "sharpe_ratio",
    "volume_ratio",
    "volatility"

]

available_columns = [

    c for c in display_columns

    if c in filtered_df.columns
]

top_df = filtered_df.sort_values(

    "institutional_score",

    ascending=False
)

st.dataframe(

    top_df[available_columns],

    use_container_width=True,

    height=700
)

# =========================================================
# RAW DATA
# =========================================================

with st.expander(
    "View Raw Data"
):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )
