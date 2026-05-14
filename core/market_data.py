# =========================================================
# INSTITUTIONAL MARKET DATA ENGINE
# =========================================================

import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import warnings

warnings.filterwarnings("ignore")

# =========================================================
# DATA PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PARQUET_DIR = BASE_DIR / "data" / "parquet"
CACHE_DIR = BASE_DIR / "data" / "cache"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PARQUET_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# NSE STOCK UNIVERSE
# =========================================================

DEFAULT_UNIVERSE = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "LT.NS",
    "ITC.NS",
    "BHARTIARTL.NS",
    "AXISBANK.NS"
]

# =========================================================
# CLEAN YFINANCE DATAFRAME
# =========================================================

# =========================================================
# CLEAN OHLCV DATA
# =========================================================

def clean_ohlcv(df):

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    # =====================================================
    # HANDLE MULTIINDEX COLUMNS
    # =====================================================

    if isinstance(df.columns, pd.MultiIndex):

        df.columns = df.columns.get_level_values(0)

    # =====================================================
    # STANDARDIZE COLUMN NAMES
    # =====================================================

    df.columns = [
        str(c).strip().lower().replace(" ", "_")
        for c in df.columns
    ]

    # =====================================================
    # RESET INDEX
    # =====================================================

    df.reset_index(inplace=True)

    # =====================================================
    # ENSURE REQUIRED COLUMNS EXIST
    # =====================================================

    required_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    for col in required_cols:

        if col not in df.columns:

            print(f"Missing column -> {col}")

            return pd.DataFrame()

    return df

# =========================================================
# DOWNLOAD SINGLE STOCK
# =========================================================

def download_single_stock(symbol, period="1y"):

    try:

        df = yf.download(
            symbol,
            period=period,
            auto_adjust=True,
            progress=False,
            threads=False
        )

        df = clean_ohlcv(df)

        if df.empty:
            return None

        df["symbol"] = symbol

        return df

    except Exception as e:

        print(f"ERROR: {symbol} -> {e}")

        return None

# =========================================================
# MULTITHREADED DOWNLOAD ENGINE
# =========================================================

def download_market_data(
    symbols,
    period="1y",
    max_workers=5
):

    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        dfs = executor.map(
            lambda s: download_single_stock(s, period),
            symbols
        )

        for df in dfs:

            if df is not None and not df.empty:
                results.append(df)

    if not results:
        return pd.DataFrame()

    final_df = pd.concat(results, ignore_index=True)

    return final_df

# =========================================================
# SAVE PARQUET
# =========================================================

def save_parquet(df, filename):

    path = PARQUET_DIR / filename

    df.to_parquet(path, index=False)

    print(f"Saved -> {path}")

# =========================================================
# LOAD PARQUET
# =========================================================

def load_parquet(filename):

    path = PARQUET_DIR / filename

    if not path.exists():
        return pd.DataFrame()

    return pd.read_parquet(path)

# =========================================================
# FETCH & STORE MARKET DATA
# =========================================================

def update_market_data():

    print("Downloading market data...")

    df = download_market_data(DEFAULT_UNIVERSE)

    if df.empty:

        print("No market data downloaded")

        return

    save_parquet(df, "market_data.parquet")

    print("Market data updated successfully")

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    update_market_data()