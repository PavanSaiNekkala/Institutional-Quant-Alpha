# =========================================================
# INSTITUTIONAL DAILY PIPELINE (ADVANCED)
# =========================================================

import pandas as pd
import numpy as np
from pathlib import Path
import traceback

from core.market_data import load_parquet
from core.indicators import add_indicators

from core.institutional_score import (
    generate_scores
)

from core.market_regime import (
    detect_market_regime
)

from strategy.trade_decision_engine import (
    trade_decision
)

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PARQUET_DIR = (
    BASE_DIR / "data" / "parquet"
)

OUTPUT_DIR = (
    BASE_DIR / "data" / "processed"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =========================================================
# LOAD MARKET DATA
# =========================================================

def load_market_data():

    path = (
        PARQUET_DIR /
        "market_data.parquet"
    )

    if not path.exists():

        print(
            "market_data.parquet not found"
        )

        return pd.DataFrame()

    df = pd.read_parquet(path)

    return df

# =========================================================
# SMART MONEY SIGNAL
# =========================================================

def smart_money_signal(row):

    try:

        if (

            row["institutional_score"] >= 75

            and

            row["smart_money_score"] >= 70

            and

            row["volume_score"] >= 20

            and

            row["breakout_score"] >= 90

        ):

            return "STRONG_ACCUMULATION"

        elif (

            row["institutional_score"] >= 60

            and

            row["smart_money_score"] >= 55

        ):

            return "ACCUMULATION"

        elif (

            row["institutional_score"] <= 30

        ):

            return "DISTRIBUTION"

        return "NEUTRAL"

    except:

        return "UNKNOWN"

# =========================================================
# PROCESS SINGLE STOCK
# =========================================================

def process_stock(symbol_df):

    try:

        symbol_df = symbol_df.copy()

        symbol_df.sort_values(
            "date",
            inplace=True
        )

        # =====================================
        # ADD INDICATORS
        # =====================================

        symbol_df = add_indicators(
            symbol_df
        )

        # =====================================
        # INSTITUTIONAL SCORES
        # =====================================

        scores = generate_scores(
            symbol_df
        )

        for key, value in scores.items():

            symbol_df[key] = value

        # =====================================
        # MARKET REGIME
        # =====================================

        regime = detect_market_regime(
            symbol_df
        )

        for key, value in regime.items():

            symbol_df[key] = value

        # =====================================
        # SMART MONEY SIGNAL
        # =====================================

        symbol_df[
            "smart_money_signal"
        ] = symbol_df.apply(
            smart_money_signal,
            axis=1
        )

        # =====================================
        # TRADE DECISION
        # =====================================

        symbol_df[
            "trade_decision"
        ] = symbol_df.apply(
            trade_decision,
            axis=1
        )

        return symbol_df

    except Exception as e:

        print(
            f"PROCESS ERROR -> {e}"
        )

        traceback.print_exc()

        return pd.DataFrame()

# =========================================================
# RUN PIPELINE
# =========================================================

def run_pipeline():

    print("=" * 60)

    print(
        "RUNNING ADVANCED "
        "INSTITUTIONAL PIPELINE"
    )

    print("=" * 60)

    # =====================================
    # LOAD DATA
    # =====================================

    df = load_market_data()

    if df.empty:

        print(
            "No market data available"
        )

        return

    print(
        f"Loaded rows: {len(df)}"
    )

    processed = []

    symbols = (
        df["symbol"]
        .dropna()
        .unique()
    )

    print(
        f"Total symbols: "
        f"{len(symbols)}"
    )

    # =====================================
    # PROCESS EACH SYMBOL
    # =====================================

    for symbol in symbols:

        try:

            print(
                f"Processing -> {symbol}"
            )

            stock_df = df[
                df["symbol"] == symbol
            ].copy()

            if stock_df.empty:

                continue

            result = process_stock(
                stock_df
            )

            if not result.empty:

                processed.append(
                    result
                )

        except Exception as e:

            print(
                f"FAILED -> {symbol}"
            )

            print(e)

    # =====================================
    # FINAL DATAFRAME
    # =====================================

    if len(processed) == 0:

        print(
            "No processed stocks"
        )

        return

    final_df = pd.concat(

        processed,

        ignore_index=True

    )

    # =====================================
    # OUTPUT COLUMNS
    # =====================================

    output_columns = [

        # BASIC

        "date",
        "symbol",

        "open",
        "high",
        "low",
        "close",
        "volume",

        # INDICATORS

        "ema20",
        "ema50",
        "ema200",

        "rsi",
        "atr",
        "volatility",
        "momentum_20",

        # INSTITUTIONAL SCORES

        "institutional_score",
        "smart_money_score",

        "relative_strength",
        "momentum_score",
        "trend_score",
        "volume_score",

        "volatility_score",
        "accumulation_score",
        "breakout_score",

        "price_structure_score",
        "liquidity_score",

        "gap_strength_score",
        "atr_expansion_score",
        "volume_trend_score",

        # MARKET REGIME

        "market_trend",
        "volatility_regime",
        "momentum_regime",

        "volume_regime",
        "liquidity_regime",

        "breakout_regime",

        "volatility_compression_regime",

        "market_strength_score",

        # SIGNALS

        "smart_money_signal",

        "trade_decision"
    ]

    # =====================================
    # FILTER EXISTING COLUMNS
    # =====================================

    final_df = final_df[

        [

            c for c in output_columns

            if c in final_df.columns

        ]

    ]

    # =====================================
    # SORTING
    # =====================================

    final_df.sort_values(

        by=[

            "institutional_score",
            "smart_money_score"

        ],

        ascending=False,

        inplace=True

    )

    # =====================================
    # SAVE OUTPUTS
    # =====================================

    parquet_output = (

        OUTPUT_DIR /

        "institutional_pipeline_output.parquet"

    )

    csv_output = (

        OUTPUT_DIR /

        "institutional_pipeline_output.csv"

    )

    final_df.to_parquet(

        parquet_output,

        index=False

    )

    final_df.to_csv(

        csv_output,

        index=False

    )

    # =====================================
    # SUMMARY
    # =====================================

    print("=" * 60)

    print(
        "PIPELINE COMPLETED"
    )

    print("=" * 60)

    print(
        f"Final Rows: "
        f"{len(final_df)}"
    )

    print(
        f"Saved -> "
        f"{parquet_output}"
    )

    print(
        f"Saved -> "
        f"{csv_output}"
    )

    # =====================================
    # TOP STOCKS
    # =====================================

    try:

        top = final_df[[

            "symbol",
            "institutional_score",
            "smart_money_score",
            "trade_decision"

        ]].head(10)

        print("\nTOP STOCKS\n")

        print(top)

    except:

        pass

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    run_pipeline()
