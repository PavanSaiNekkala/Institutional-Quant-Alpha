import sys
from pathlib import Path

# =========================================================
# FIX IMPORT PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

# =========================================================
# IMPORTS
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from core.market_regime import detect_market_regime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Institutional Quant Dashboard",
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
        "Dataset not found"
    )

    st.stop()

df = pd.read_parquet(DATA_PATH)

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

regime = detect_market_regime(df)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Market Regime",
    regime["regime"]
)

col2.metric(
    "Trend Strength",
    regime["trend_strength"]
)

col3.metric(
    "Momentum",
    regime["momentum"]
)

col4.metric(
    "Volatility",
    regime["volatility"]
)

st.markdown("---")

# =========================================================
# TOP STOCKS
# =========================================================

top_df = (
    df.sort_values(
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
    title="Top Institutional Stocks"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================================
# SIGNAL DISTRIBUTION
# =========================================================

signal_fig = px.histogram(
    df,
    x="signal",
    color="signal",
    title="Signal Distribution"
)

st.plotly_chart(
    signal_fig,
    use_container_width=True
)

# =========================================================
# MOMENTUM VS SCORE
# =========================================================

scatter = px.scatter(
    df,
    x="momentum_20",
    y="institutional_score",
    color="signal",
    hover_data=["symbol"],
    title="Momentum vs Institutional Score"
)

st.plotly_chart(
    scatter,
    use_container_width=True
)

# =========================================================
# DATA TABLE
# =========================================================

st.subheader(
    "Institutional Dataset"
)

st.dataframe(
    df.sort_values(
        "institutional_score",
        ascending=False
    ),
    use_container_width=True
)
