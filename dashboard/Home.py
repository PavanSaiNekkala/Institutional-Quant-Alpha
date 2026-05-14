import yfinance as yf
from datetime import datetime
import sys
from pathlib import Path

# =========================================================
# ROOT PATH FIX
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

# =========================================================
# SAFE IMPORT
# =========================================================

try:

    from core.market_regime import detect_market_regime

except:

    def detect_market_regime(df):

        return {

            "regime": "NEUTRAL",
            "trend_strength": "N/A",
            "momentum": "N/A",
            "volatility": "N/A"
        }

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(

    page_title="Institutional Quant Dashboard",

    page_icon="📈",

    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""

<style>

.main {
    background-color: #0E1117;
}

section[data-testid="stSidebar"] {
    background-color: #161B22;
}

div[data-testid="metric-container"] {

    background-color: #161B22;

    border: 1px solid #30363D;

    padding: 15px;

    border-radius: 12px;
}

h1, h2, h3 {
    color: white;
}

</style>

""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================

st.title("📊 Institutional Quant Dashboard")

st.caption(
    f"Last Updated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)

st.markdown("---")

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

    st.error("Dataset not found")

    st.stop()

try:

    df = pd.read_parquet(DATA_PATH)

except Exception as e:

    st.error(f"Load Error: {e}")

    st.stop()

# =========================================================
# CLEAN COLUMNS
# =========================================================

df.columns = [c.lower() for c in df.columns]

# =========================================================
# FALLBACKS
# =========================================================

fallbacks = {

    "symbol": np.arange(len(df)),
    "sector": "Unknown",
    "momentum_20": 0,
    "volatility": 0,
    "adx": 0,
    "rsi": 50,
    "institutional_score": 0
}

for col, val in fallbacks.items():

    if col not in df.columns:

        df[col] = val

# =========================================================
# SIGNAL CREATION
# =========================================================

if "signal" not in df.columns:

    conditions = [

        df["institutional_score"] >= 80,
        df["institutional_score"] >= 65,
        df["institutional_score"] >= 50,
        df["institutional_score"] >= 35
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
# MARKET REGIME
# =========================================================

try:

    regime = detect_market_regime(df)

except:

    regime = {

        "regime": "NEUTRAL",
        "trend_strength": "N/A",
        "momentum": "N/A",
        "volatility": "N/A"
    }

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.title("⚙ Institutional Controls")

# SCORE FILTER

min_score = st.sidebar.slider(

    "Minimum Institutional Score",

    0,
    100,
    20
)

# SIGNAL FILTER

signal_options = sorted(

    df["signal"]
    .dropna()
    .astype(str)
    .unique()
)

selected_signals = st.sidebar.multiselect(

    "Signal Filter",

    signal_options,

    default=[]
)

# SECTOR FILTER

df["sector"] = (

    df["sector"]
    .fillna("Unknown")
    .astype(str)
)

sector_options = sorted(

    df["sector"]
    .unique()
)

selected_sectors = st.sidebar.multiselect(

    "Sector Filter",

    sector_options,

    default=[]
)

# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()

filtered_df = filtered_df[
    filtered_df["institutional_score"] >= min_score
]

if len(selected_signals) > 0:

    filtered_df = filtered_df[
        filtered_df["signal"]
        .isin(selected_signals)
    ]

if len(selected_sectors) > 0:

    filtered_df = filtered_df[
        filtered_df["sector"]
        .isin(selected_sectors)
    ]

# =========================================================
# UNIVERSE METRICS
# =========================================================

st.sidebar.markdown("---")

st.sidebar.metric(
    "Loaded Stocks",
    len(df)
)

st.sidebar.metric(
    "Filtered Stocks",
    len(filtered_df)
)

# =========================================================
# EMPTY DATA FIX
# =========================================================

if filtered_df.empty:

    st.warning(
        "No stocks match filters. Reduce score or clear filters."
    )

    st.stop()

# =========================================================
# LIVE MARKET OVERVIEW
# =========================================================

st.subheader("📡 Live Market Overview")

indices = {

    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "SENSEX": "^BSESN"
}

market_cols = st.columns(3)

for i, (name, ticker) in enumerate(indices.items()):

    try:

        live = yf.Ticker(ticker)

        hist = live.history(period="2d")

        latest_close = round(hist["Close"].iloc[-1], 2)

        prev_close = round(hist["Close"].iloc[-2], 2)

        change = latest_close - prev_close

        pct = round((change / prev_close) * 100, 2)

        market_cols[i].metric(

            label=name,

            value=f"{latest_close}",

            delta=f"{pct}%"
        )

    except:

        market_cols[i].metric(

            label=name,

            value="N/A",

            delta="N/A"
        )

st.markdown("---")

# =========================================================
# KPI ROW
# =========================================================

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric(
    "Market Regime",
    regime.get("regime", "N/A")
)

k2.metric(
    "Stocks",
    len(filtered_df)
)

k3.metric(
    "Avg Score",
    round(filtered_df["institutional_score"].mean(), 2)
)

k4.metric(
    "Top Score",
    round(filtered_df["institutional_score"].max(), 2)
)

k5.metric(
    "Avg Momentum",
    round(filtered_df["momentum_20"].mean(), 2)
)

st.markdown("---")

# =========================================================
# MARKET BREADTH
# =========================================================

st.subheader("📈 Market Breadth")

advancers = len(
    filtered_df[
        filtered_df["signal"]
        .isin(["BUY", "STRONG BUY"])
    ]
)

decliners = len(
    filtered_df[
        filtered_df["signal"]
        .isin(["SELL", "STRONG SELL"])
    ]
)

neutral = len(
    filtered_df[
        filtered_df["signal"] == "HOLD"
    ]
)

breadth_df = pd.DataFrame({

    "Category": [
        "Advancers",
        "Decliners",
        "Neutral"
    ],

    "Count": [
        advancers,
        decliners,
        neutral
    ]
})

breadth_fig = px.pie(

    breadth_df,

    names="Category",

    values="Count",

    hole=0.55,

    template="plotly_dark"
)

st.plotly_chart(
    breadth_fig,
    use_container_width=True
)

# =========================================================
# HEATMAP
# =========================================================

st.subheader("🔥 Institutional Heatmap")

heatmap_df = (

    filtered_df
    .sort_values(
        "institutional_score",
        ascending=False
    )
    .head(30)
)

heatmap_fig = px.treemap(

    heatmap_df,

    path=["sector", "symbol"],

    values="institutional_score",

    color="institutional_score",

    template="plotly_dark"
)

st.plotly_chart(
    heatmap_fig,
    use_container_width=True
)

# =========================================================
# MOMENTUM SCATTER
# =========================================================

st.subheader("⚡ Momentum Analytics")

scatter = px.scatter(

    filtered_df,

    x="momentum_20",

    y="institutional_score",

    size="adx",

    color="signal",

    hover_data=["symbol", "sector"],

    template="plotly_dark"
)

scatter.update_layout(height=700)

st.plotly_chart(
    scatter,
    use_container_width=True
)

# =========================================================
# TOP STOCKS
# =========================================================

st.subheader("🏆 Institutional Leaders")

top_df = (

    filtered_df

    .sort_values(
        "institutional_score",
        ascending=False
    )

    .head(25)
)

leader_fig = px.bar(

    top_df,

    x="symbol",

    y="institutional_score",

    color="institutional_score",

    hover_data=["signal", "sector"],

    template="plotly_dark"
)

leader_fig.update_layout(height=600)

st.plotly_chart(
    leader_fig,
    use_container_width=True
)

# =========================================================
# DATA TABLE
# =========================================================

st.subheader("📋 Institutional Screener")

display_cols = [

    c for c in [

        "symbol",
        "sector",
        "institutional_score",
        "signal",
        "momentum_20",
        "rsi",
        "adx",
        "volatility"

    ]

    if c in filtered_df.columns
]

table_df = (

    filtered_df

    [display_cols]

    .sort_values(
        "institutional_score",
        ascending=False
    )
)

st.dataframe(

    table_df,

    use_container_width=True,

    height=700
)

# =========================================================
# DOWNLOAD
# =========================================================

csv = table_df.to_csv(index=False)

st.download_button(

    label="⬇ Download Institutional Dataset",

    data=csv,

    file_name="institutional_quant.csv",

    mime="text/csv"
)
