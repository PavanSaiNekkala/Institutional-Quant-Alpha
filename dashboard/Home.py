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
# TITLE
# =========================================================

st.title("📊 Institutional Quant Dashboard")

st.markdown("---")

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙ Institutional Controls")

# ---------------------------------------------------------
# SCORE FILTER
# ---------------------------------------------------------

min_score = st.sidebar.slider(

    "Minimum Institutional Score",

    0,

    100,

    20
)

# ---------------------------------------------------------
# SIGNAL FILTER
# ---------------------------------------------------------

all_signals = sorted(

    df["signal"].dropna().unique()
)

default_signals = [

    s for s in [

        "STRONG BUY",
        "BUY",
        "HOLD"

    ]

    if s in all_signals
]

selected_signals = st.sidebar.multiselect(

    "Signal Filter",

    options=all_signals,

    default=default_signals
)

# ---------------------------------------------------------
# SECTOR FILTER
# ---------------------------------------------------------

all_sectors = sorted(

    df["sector"].fillna("Unknown").unique()
)

selected_sectors = st.sidebar.multiselect(

    "Sector Filter",

    options=all_sectors,

    default=all_sectors
)

# =========================================================
# FILTERED DATA
# =========================================================

filtered_df = df[

    (df["institutional_score"] >= min_score)

    &

    (df["signal"].isin(selected_signals))

    &

    (df["sector"].isin(selected_sectors))
]

# =========================================================
# EMPTY FILTER CHECK
# =========================================================

if filtered_df.empty:

    st.warning(
        "No stocks match filters. Reduce score or select BUY/HOLD."
    )

    st.stop()

# =========================================================
# KPI ROW
# =========================================================

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(

    "Market Regime",

    regime.get("regime", "N/A")
)

col2.metric(

    "Stocks",

    len(filtered_df)
)

col3.metric(

    "Avg Score",

    round(

        filtered_df["institutional_score"].mean(),

        2
    )
)

col4.metric(

    "Top Score",

    round(

        filtered_df["institutional_score"].max(),

        2
    )
)

col5.metric(

    "Avg Momentum",

    round(

        filtered_df["momentum_20"].mean(),

        2
    )
)

st.markdown("---")

# =========================================================
# TOP LEADERS
# =========================================================

left, right = st.columns([2, 1])

with left:

    st.subheader("🏆 Institutional Leaders")

    top_df = (

        filtered_df

        .sort_values(

            "institutional_score",

            ascending=False
        )

        .head(20)
    )

    fig = px.bar(

        top_df,

        x="symbol",

        y="institutional_score",

        color="institutional_score",

        hover_data=["signal", "sector"],

        template="plotly_dark"
    )

    fig.update_layout(height=500)

    st.plotly_chart(

        fig,

        use_container_width=True
    )

with right:

    st.subheader("📊 Signal Breakdown")

    pie = px.pie(

        filtered_df,

        names="signal",

        template="plotly_dark"
    )

    pie.update_layout(height=500)

    st.plotly_chart(

        pie,

        use_container_width=True
    )

# =========================================================
# SECTOR ANALYTICS
# =========================================================

st.subheader("🏭 Sector Analytics")

sector_df = (

    filtered_df

    .groupby("sector")

    .agg({

        "institutional_score": "mean",

        "momentum_20": "mean",

        "volatility": "mean",

        "symbol": "count"
    })

    .reset_index()
)

sector_df.columns = [

    "sector",

    "avg_score",

    "avg_momentum",

    "avg_volatility",

    "stocks"
]

sector_chart = px.treemap(

    sector_df,

    path=["sector"],

    values="stocks",

    color="avg_score",

    template="plotly_dark"
)

sector_chart.update_layout(height=600)

st.plotly_chart(

    sector_chart,

    use_container_width=True
)

# =========================================================
# MOMENTUM ANALYTICS
# =========================================================

left, right = st.columns(2)

with left:

    st.subheader("⚡ Momentum vs Score")

    scatter = px.scatter(

        filtered_df,

        x="momentum_20",

        y="institutional_score",

        size="adx",

        color="signal",

        hover_data=["symbol", "sector"],

        template="plotly_dark"
    )

    scatter.update_layout(height=600)

    st.plotly_chart(

        scatter,

        use_container_width=True
    )

with right:

    st.subheader("📈 RSI Heatmap")

    heat = px.density_heatmap(

        filtered_df,

        x="rsi",

        y="institutional_score",

        template="plotly_dark"
    )

    heat.update_layout(height=600)

    st.plotly_chart(

        heat,

        use_container_width=True
    )

# =========================================================
# VOLATILITY ANALYTICS
# =========================================================

st.subheader("🌪 Volatility Analytics")

vol_chart = px.box(

    filtered_df,

    x="signal",

    y="volatility",

    color="signal",

    template="plotly_dark"
)

vol_chart.update_layout(height=500)

st.plotly_chart(

    vol_chart,

    use_container_width=True
)

# =========================================================
# TABLE
# =========================================================

st.subheader("📋 Institutional Stock Screener")

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

styled_df = (

    filtered_df

    [display_cols]

    .sort_values(

        "institutional_score",

        ascending=False
    )
)

st.dataframe(

    styled_df,

    use_container_width=True,

    height=700
)

# =========================================================
# DOWNLOAD
# =========================================================

csv = styled_df.to_csv(index=False)

st.download_button(

    label="⬇ Download Institutional Dataset",

    data=csv,

    file_name="institutional_quant.csv",

    mime="text/csv"
)
