# =========================================================
# INSTITUTIONAL DAILY PIPELINE
# =========================================================

import pandas as pd
import numpy as np
from pathlib import Path
import traceback

from core.market_data import load_parquet
from core.indicators import add_indicators
from core.institutional_score import generate_scores
from core.market_regime import detect_market_regime
from strategy.trade_decision_engine import trade_decision

# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PARQUET_DIR = BASE_DIR / "data" / "parquet"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# LOAD MARKET DATA
# =========================================================

def load_market_data():

    path = PARQUET_DIR / "market_data.parquet"

    if not path.exists():

        print("market_data.parquet not found")

        return pd.DataFrame()

    return pd.read_parquet(path)

# =========================================================
# PROCESS STOCK
# =========================================================

def process_stock(symbol_df):

    try:

        symbol_df = symbol_df.copy()

        symbol_df.sort_values(
            "date",
            inplace=True
        )

        # =========================================
        # INDICATORS
        # =========================================

        symbol_df = add_indicators(symbol_df)

        # =========================================
        # INSTITUTIONAL SCORES
        # =========================================

        scores = generate_scores(symbol_df)

        for key, value in scores.items():

            symbol_df[key] = value

        # =========================================
        # SMART MONEY SIGNAL
        # =========================================

        symbol_df["smart_money_signal"] = np.where(

            (
                (symbol_df["institutional_score"] > 60)
                &
                (symbol_df["smart_money_score"] > 50)
            ),

            "ACCUMULATION",

            "NORMAL"
        )

        # =========================================
        # MARKET REGIME
        # =========================================

        regime = detect_market_regime(symbol_df)

        symbol_df["market_regime"] = regime

        # =========================================
        # TRADE DECISION
        # =========================================

        symbol_df["trade_decision"] = (

            symbol_df.apply(
                trade_decision,
                axis=1
            )
        )

        return symbol_df

    except Exception as e:

        print(f"PROCESS ERROR -> {e}")

        traceback.print_exc()

        return pd.DataFrame()

# =========================================================
# RUN PIPELINE
# =========================================================

def run_pipeline():

    print("=" * 60)
    print("RUNNING INSTITUTIONAL PIPELINE")
    print("=" * 60)

    df = load_market_data()

    if df.empty:

        print("No market data available")

        return

    print(f"Loaded rows: {len(df)}")

    processed = []

    symbols = df["symbol"].unique()

    print(f"Total symbols: {len(symbols)}")

    for symbol in symbols:

        try:

            print(f"Processing -> {symbol}")

            stock_df = df[
                df["symbol"] == symbol
            ].copy()

            result = process_stock(stock_df)

            if not result.empty:

                processed.append(result)

        except Exception as e:

            print(f"FAILED -> {symbol}")

            print(e)

    if len(processed) == 0:

        print("No processed stocks")

        return

    # =========================================
    # FINAL DATAFRAME
    # =========================================

    final_df = pd.concat(
        processed,
        ignore_index=True
    )

    output_columns = [

        "date",
        "symbol",

        "open",
        "high",
        "low",
        "close",
        "volume",

        "ema20",
        "ema50",
        "ema200",

        "rsi",
        "atr",
        "volatility",
        "momentum_20",

        "institutional_score",
        "smart_money_score",

        "relative_strength",
        "volume_score",
        "momentum_score",
        "trend_score",
        "volatility_score",
        "accumulation_score",
        "breakout_score",
        "price_structure_score",
        "risk_reward_score",
        "liquidity_score",

        "smart_money_signal",
        "market_regime",
        "trade_decision"
    ]

    final_df = final_df[
        [c for c in output_columns if c in final_df.columns]
    ]

    # =========================================
    # SAVE OUTPUT
    # =========================================

    output_path = (
        OUTPUT_DIR /
        "institutional_pipeline_output.parquet"
    )

    csv_output = (
        OUTPUT_DIR /
        "institutional_pipeline_output.csv"
    )

    final_df.to_parquet(
        output_path,
        index=False
    )

    final_df.to_csv(
        csv_output,
        index=False
    )

    print("=" * 60)
    print("PIPELINE COMPLETED")
    print("=" * 60)

    print(f"Rows: {len(final_df)}")

    print(f"Saved -> {output_path}")

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    run_pipeline()
