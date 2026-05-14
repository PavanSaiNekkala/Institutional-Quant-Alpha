import sys
from pathlib import Path

# =========================================================
# FIX IMPORT PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# =========================================================
# IMPORTS
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
    page_title="Institutional Quant Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# LOAD DATA
# =========================================================

DATA_PATH = (
    ROOT_DIR
    / "data"
    / "parquet"
    / "institutional_dataset.parquet"
)

if not DATA_PATH.exists():

    st.error(
        "❌ institutional_dataset.parquet not found"
    )

    st.stop()

# =========================================================
# READ DATA
# =========================================================

try:

    df = pd.read_parquet(DATA_PATH)

except Exception as e:

    st.error(f"Dataset load failed: {e}")

    st.stop()

# =========================================================
# BASIC CLEANUP
# =========================================================

df.columns = [c.lower() for c in df.columns]

# =========================================================
# REQUIRED COLUMN CHECKS
# =========================================================

required_columns = [
    "institutional_score"
]

missing_cols = [
    c for c in required_columns
    if c not in df.columns
]

if missing_cols:

    st.error(
        f"Missing columns: {missing_cols}"
    )

    st.stop()

# =========================================================
# CREATE FALLBACK COLUMNS
# =========================================================

if "symbol" not in df.columns:
    df["symbol"] = np.arange(len(df))

if "momentum_20" not in df.columns:
    df["momentum_20"] = 0

# =========================================================
# CREATE SIGNAL COLUMN
# =========================================================

if "signal" not in df.columns:

    conditions = [

        df["institutional_score"] >= 80,

        df["institutional_score"] >= 65,

        df["institutional_score"] >= 50,

        df["institutional_score"] >= 35,
    ]

    choices = [

        "STRONG BUY",

        "BUY",

        "HOLD",

        "SELL"
    ]

    df["signal"] = np.select(

        conditions,

        choices,

        default="STRONG SELL"
    )

# =========================================================
# MARKET REGIME SAFE HANDLING
# =========================================================

try:

    regime = detect_market_regime(df)

except Exception:

    regime = {

        "regime": "NEUTRAL",

        "trend_strength": "N/A",

        "momentum": "N/A",

        "volatility": "N/A"
    }

# =========================================================
# TITLE
# =========================================================

st.title(
    "📊 Institutional Quant Dashboard"
)

st.markdown("---")

# =========================================================
# MARKET REGIME
# =========================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Market Regime",
    regime.get("regime", "N/A")
)

col2.metric(
    "Trend Strength",
    regime.get("trend_strength", "N/A")
)

col3.metric(
    "Momentum",
    regime.get("momentum", "N/A")
)

col4.metric(
    "Volatility",
    regime.get("volatility", "N/A")
)

st.markdown("---")

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.title(
    "⚙ Institutional Controls"
)

min_score = st.sidebar.slider(
    "Minimum Institutional Score",
    0,
    100,
    50
)

signal_options = sorted(
    df["signal"].unique().tolist()
)

selected_signals = st.sidebar.multiselect(
    "Signal Filter",
    signal_options,
    default=signal_options
)

# =========================================================
# FILTER DATA
# =========================================================

filtered_df = df[
    (df["institutional_score"] >= min_score)
    &
    (df["signal"].isin(selected_signals))
]

# =========================================================
# EMPTY CHECK
# =========================================================

if filtered_df.empty:

    st.warning(
        "No stocks match selected filters"
    )

    st.stop()

# =========================================================
# TOP STOCKS
# =========================================================

st.subheader(
    "🏆 Top Institutional Stocks"
)

top_df = (
    filtered_df
    .sort_values(
        "institutional_score",
        ascending=False
    )
    .head(25)
)

fig = px.bar(

    top_df,

    x="symbol",

    y="institutional_score",

    color="institutional_score",

    hover_data=["signal"],

    title="Top Institutional Stocks"
)

fig.update_layout(
    template="plotly_dark",
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================================
# SIGNAL DISTRIBUTION
# =========================================================

st.subheader(
    "📊 Signal Distribution"
)

signal_fig = px.histogram(

    filtered_df,

    x="signal",

    color="signal",

    title="Signal Distribution"
)

signal_fig.update_layout(
    template="plotly_dark",
    height=450
)

st.plotly_chart(
    signal_fig,
    use_container_width=True
)

# =========================================================
# MOMENTUM VS SCORE
# =========================================================

st.subheader(
    "⚡ Momentum vs Institutional Score"
)

scatter = px.scatter(

    filtered_df,

    x="momentum_20",

    y="institutional_score",

    color="signal",

    hover_data=["symbol"],

    title="Momentum vs Institutional Score"
)

scatter.update_layout(
    template="plotly_dark",
    height=550
)

st.plotly_chart(
    scatter,
    use_container_width=True
)

# =========================================================
# SCORE STATISTICS
# =========================================================

st.subheader(
    "📈 Institutional Statistics"
)

s1, s2, s3, s4 = st.columns(4)

s1.metric(
    "Stocks",
    len(filtered_df)
)

s2.metric(
    "Average Score",
    round(
        filtered_df[
            "institutional_score"
        ].mean(),
        2
    )
)

s3.metric(
    "Highest Score",
    round(
        filtered_df[
            "institutional_score"
        ].max(),
        2
    )
)

s4.metric(
    "Lowest Score",
    round(
        filtered_df[
            "institutional_score"
        ].min(),
        2
    )
)

# =========================================================
# DATA TABLE
# =========================================================

st.subheader(
    "📋 Institutional Dataset"
)

display_cols = [

    c for c in [

        "symbol",

        "institutional_score",

        "signal",

        "momentum_20",

        "rsi",

        "adx",

        "macd",

        "volatility",

        "trend_score"

    ]

    if c in filtered_df.columns
]

st.dataframe(

    filtered_df[
        display_cols
    ].sort_values(

        "institutional_score",

        ascending=False
    ),

    use_container_width=True
)

# =========================================================
# DOWNLOAD BUTTON
# =========================================================

csv = filtered_df.to_csv(index=False)

st.download_button(

    label="⬇ Download Filtered Dataset",

    data=csv,

    file_name="institutional_filtered.csv",

    mime="text/csv"
)
