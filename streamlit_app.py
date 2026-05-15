import streamlit as st
import pandas as pd
from pathlib import Path

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Institutional Quant Alpha",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("📈 Institutional Quant Alpha Dashboard")

st.markdown("---")

# =========================================================
# PATHS
# =========================================================

SCANNER_DIR = Path("data/processed/scanners")

# =========================================================
# LOAD CSV
# =========================================================

def load_csv(file_name):

    path = SCANNER_DIR / file_name

    if path.exists():

        return pd.read_csv(path)

    return pd.DataFrame()

# =========================================================
# LOAD DATA
# =========================================================

top_institutional = load_csv(
    "top_institutional.csv"
)

smart_money = load_csv(
    "smart_money.csv"
)

breakouts = load_csv(
    "breakouts.csv"
)

momentum = load_csv(
    "momentum.csv"
)

volume = load_csv(
    "volume_expansion.csv"
)

# =========================================================
# DASHBOARD
# =========================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏦 Institutional",
    "💰 Smart Money",
    "🚀 Breakouts",
    "📈 Momentum",
    "📊 Volume"
])

# =========================================================
# TAB 1
# =========================================================

with tab1:

    st.subheader(
        "Top Institutional Accumulation"
    )

    st.dataframe(
        top_institutional,
        use_container_width=True
    )

# =========================================================
# TAB 2
# =========================================================

with tab2:

    st.subheader(
        "Smart Money Leaders"
    )

    st.dataframe(
        smart_money,
        use_container_width=True
    )

# =========================================================
# TAB 3
# =========================================================

with tab3:

    st.subheader(
        "Breakout Leaders"
    )

    st.dataframe(
        breakouts,
        use_container_width=True
    )

# =========================================================
# TAB 4
# =========================================================

with tab4:

    st.subheader(
        "Momentum Leaders"
    )

    st.dataframe(
        momentum,
        use_container_width=True
    )

# =========================================================
# TAB 5
# =========================================================

with tab5:

    st.subheader(
        "Volume Expansion Leaders"
    )

    st.dataframe(
        volume,
        use_container_width=True
    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.success(
    "Institutional Quant Alpha Running Successfully"
)
