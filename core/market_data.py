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
# INPUT FILE
# =========================================================

VALID_STOCKS_FILE = RAW_DATA_DIR / "valid_stocks.xlsx"

# =========================================================
# LOAD STOCK UNIVERSE FROM EXCEL
# =========================================================

def load_stock_universe():

    try:

        if not VALID_STOCKS_FILE.exists():

            print(f"File not found -> {VALID_STOCKS_FILE}")

            return []

        # Read Excel file
        df = pd.read_excel(VALID_STOCKS_FILE)

        if df.empty:

            print("Excel file is empty")

            return []

        # Possible column names
        possible_cols = [
            "symbol",
            "symbols",
            "ticker",
            "tickers",
            "stock",
            "stocks"
        ]

        symbol_col = None

        # Detect symbol column automatically
        for col in df.columns:

            if str(col).strip().lower() in possible_cols:
                symbol_col = col
                break

        # Fallback to first column
        if symbol_col is None:
            symbol_col = df.columns[0]

        # Clean symbols
        symbols = (
            df[symbol_col]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

        # Add NSE suffix if missing
        cleaned_symbols = []

        for s in symbols:

            if not s.endswith(".NS"):
                s = f"{s}.NS"

            cleaned_symbols.append(s)

        print(f"Loaded {len(cleaned_symbols)} stocks")

        return cleaned_symbols

    except Exception as e:

        print(f"Universe loading error -> {e}")

        return []

# =========================================================
# CLEAN YFINANCE DATAFRAME
# =========================================================

def clean_ohlcv(df):

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    df.columns = [str(c).lower() for c in df.columns]

    rename_map = {
        "adj close": "adj_close"
    }

    df.rename(columns=rename_map, inplace=True)

    df.reset_index(inplace=True)

    return df

# =========================================================
# DOWNLOAD SINGLE STOCK
# =========================================================

def download_single_stock(symbol, period="1y"):

    try:

        print(f"Downloading -> {symbol}")

        df = yf.download(
            symbol,
            period=period,
            auto_adjust=True,
            progress=False,
            threads=False
        )

        df = clean_ohlcv(df)

        if df.empty:

            print(f"No data -> {symbol}")

            return None

        df["symbol"] = symbol

        return df

    except Exception as e:

        print(f"ERROR: {symbol} -> {e}")

        return None

# =========================================================
# MEMORY OPTIMIZED DOWNLOAD ENGINE
# =========================================================

def optimize_dataframe(df):

    try:

        float_cols = df.select_dtypes(
            include=["float64"]
        ).columns

        int_cols = df.select_dtypes(
            include=["int64"]
        ).columns

        df[float_cols] = df[float_cols].astype(
            "float32"
        )

        df[int_cols] = df[int_cols].astype(
            "int32"
        )

        return df

    except:

        return df

# =========================================================
# DOWNLOAD MARKET DATA
# =========================================================

def download_market_data(
    symbols,
    period="1y",
    batch_size=50
):

    parquet_path = (
        PARQUET_DIR /
        "market_data.parquet"
    )

    all_batches = []

    total = len(symbols)

    for start in range(0, total, batch_size):

        end = start + batch_size

        batch_symbols = symbols[start:end]

        print("=" * 60)
        print(f"Processing Batch {start} -> {end}")
        print("=" * 60)

        batch_results = []

        for symbol in batch_symbols:

            try:

                df = download_single_stock(
                    symbol,
                    period
                )

                if df is not None and not df.empty:

                    df = optimize_dataframe(df)

                    batch_results.append(df)

            except Exception as e:

                print(f"{symbol} batch error -> {e}")

        # =================================================
        # SAVE BATCH
        # =================================================

        if batch_results:

            batch_df = pd.concat(
                batch_results,
                ignore_index=True
            )

            batch_df = optimize_dataframe(
                batch_df
            )

            all_batches.append(batch_df)

            print(
                f"Batch rows -> {len(batch_df)}"
            )

            # Free memory
            del batch_results

    # =====================================================
    # FINAL CONCAT
    # =====================================================

    if not all_batches:

        return pd.DataFrame()

    final_df = pd.concat(
        all_batches,
        ignore_index=True
    )

    final_df = optimize_dataframe(
        final_df
    )

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

    print("=" * 60)
    print("INSTITUTIONAL MARKET DATA ENGINE")
    print("=" * 60)

    # Load stock universe
    symbols = load_stock_universe()

    if not symbols:

        print("No valid symbols found")

        return

    print(f"Starting download for {len(symbols)} stocks")

    # Download data
    df = download_market_data(symbols)

    if df.empty:

        print("No market data downloaded")

        return

    # Save parquet
    save_parquet(df, "market_data.parquet")

    # Save CSV backup
    csv_path = RAW_DATA_DIR / "market_data.csv"

    df.to_csv(csv_path, index=False)

    print(f"CSV backup saved -> {csv_path}")

    print("=" * 60)
    print("Market data updated successfully")
    print("=" * 60)

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    update_market_data()