# =========================================================
# INSTITUTIONAL DAILY PIPELINE
# =========================================================

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from pathlib import Path

# =========================================================
# INTERNAL IMPORTS
# =========================================================

from core.market_data import (
    update_market_data,
    load_parquet
)

from core.indicators import (
    add_indicators
)

# =========================================================
# BASE PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PARQUET_DIR = (
    BASE_DIR
    / "data"
    / "parquet"
)

PARQUET_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =========================================================
# MEMORY OPTIMIZATION
# =========================================================

def optimize_dataframe(df):

    df = df.copy()

    float_cols = df.select_dtypes(
        include=["float64"]
    ).columns

    int_cols = df.select_dtypes(
        include=["int64"]
    ).columns

    for col in float_cols:
        df[col] = pd.to_numeric(
            df[col],
            downcast="float"
        )

    for col in int_cols:
        df[col] = pd.to_numeric(
            df[col],
            downcast="integer"
        )

    return df

# =========================================================
# CLEAN DATA
# =========================================================

def clean_market_data(df):

    df = df.copy()

    # remove duplicates
    df = df.drop_duplicates()

    # sort
    if "symbol" in df.columns and "date" in df.columns:

        df = df.sort_values(
            by=["symbol", "date"]
        )

    # remove invalid close
    if "close" in df.columns:

        df = df[
            df["close"] > 0
        ]

    return df

# =========================================================
# PROCESS SINGLE STOCK
# =========================================================

def process_single_stock(symbol, market_df):

    try:

        temp = market_df[
            market_df["symbol"] == symbol
        ].copy()

        if temp.empty:
            return None

        # sort by date
        if "date" in temp.columns:
            temp = temp.sort_values("date")

        # add indicators
        temp = add_indicators(temp)

        # latest row only
        latest = temp.iloc[-1:].copy()

        return latest

    except Exception as e:

        print(f"PROCESS ERROR -> {symbol} -> {e}")

        return None

# =========================================================
# BUILD FINAL DATASET
# =========================================================

def build_final_dataset(market_df):

    print("\nBuilding institutional dataset...")

    symbols = market_df["symbol"].unique()

    processed = []

    total = len(symbols)

    for idx, symbol in enumerate(symbols, start=1):

        print(f"[{idx}/{total}] Processing -> {symbol}")

        result = process_single_stock(
            symbol,
            market_df
        )

        if result is not None:
            processed.append(result)

    if not processed:

        print("No processed stocks available")

        return pd.DataFrame()

    final_df = pd.concat(
        processed,
        ignore_index=True
    )

    # clean
    final_df = clean_market_data(final_df)

    # optimize memory
    final_df = optimize_dataframe(final_df)

    return final_df

# =========================================================
# SAVE OUTPUTS
# =========================================================

def save_outputs(final_df):

    parquet_path = (
        PARQUET_DIR
        / "institutional_dataset.parquet"
    )

    csv_path = (
        PARQUET_DIR
        / "institutional_dataset.csv"
    )

    # parquet
    final_df.to_parquet(
        parquet_path,
        index=False
    )

    # csv
    final_df.to_csv(
        csv_path,
        index=False
    )

    print(f"\nSaved Parquet -> {parquet_path}")
    print(f"Saved CSV -> {csv_path}")

# =========================================================
# DISPLAY SUMMARY
# =========================================================

def display_summary(final_df):

    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)

    print(f"Total Stocks     : {final_df['symbol'].nunique()}")

    print(f"Total Rows       : {len(final_df):,}")

    if "close" in final_df.columns:

        print(
            f"Average Price    : "
            f"{round(final_df['close'].mean(), 2)}"
        )

    if "rsi" in final_df.columns:

        print(
            f"Average RSI      : "
            f"{round(final_df['rsi'].mean(), 2)}"
        )

    if "momentum_20" in final_df.columns:

        print(
            f"Average Momentum : "
            f"{round(final_df['momentum_20'].mean(), 2)}"
        )

    print("=" * 60)

# =========================================================
# MAIN PIPELINE
# =========================================================

def main():

    try:

        print("=" * 60)
        print("STARTING INSTITUTIONAL PIPELINE")
        print("=" * 60)

        # =================================================
        # STEP 1 -> DOWNLOAD MARKET DATA
        # =================================================

        print("\nSTEP 1 -> Updating Market Data")

        update_market_data()

        # =================================================
        # STEP 2 -> LOAD MARKET DATA
        # =================================================

        print("\nSTEP 2 -> Loading Market Data")

        market_df = load_parquet(
            "market_data.parquet"
        )

        if market_df.empty:

            print("Market data is empty")

            return

        print(
            f"Loaded rows -> "
            f"{len(market_df):,}"
        )

        # =================================================
        # STEP 3 -> CLEAN
        # =================================================

        print("\nSTEP 3 -> Cleaning Market Data")

        market_df = clean_market_data(
            market_df
        )

        market_df = optimize_dataframe(
            market_df
        )

        # =================================================
        # STEP 4 -> BUILD DATASET
        # =================================================

        print("\nSTEP 4 -> Calculating Indicators")

        final_df = build_final_dataset(
            market_df
        )

        if final_df.empty:

            print("Final dataset empty")

            return

        # =================================================
        # STEP 5 -> SAVE
        # =================================================

        print("\nSTEP 5 -> Saving Outputs")

        save_outputs(final_df)

        # =================================================
        # STEP 6 -> SUMMARY
        # =================================================

        display_summary(final_df)

        print("\nPIPELINE COMPLETED SUCCESSFULLY")

    except Exception as e:

        print("\nPIPELINE FAILED")
        print(str(e))

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    main()
