# =========================================================
# INSTITUTIONAL DAILY PIPELINE
# =========================================================

import pandas as pd
import numpy as np

from core.market_data import (
    update_market_data,
    load_parquet,
    save_parquet
)

from core.indicators import (
    add_indicators,
    sharpe_ratio,
    trend_strength
)

# =========================================================
# FACTOR SCORE ENGINE
# =========================================================

def compute_factor_scores(df):

    results = []

    symbols = df["symbol"].unique()

    for symbol in symbols:

        try:

            sdf = (
                df[df["symbol"] == symbol]
                .copy()
                .reset_index(drop=True)
            )

            if len(sdf) < 50:
                continue

            latest = sdf.iloc[-1]

            # =================================================
            # FACTORS
            # =================================================

            momentum_score = latest["momentum_20"]

            rsi_score = latest["rsi"]

            volatility_score = (
                100 - latest["volatility"] * 100
            )

            sharpe = sharpe_ratio(
                sdf["close"]
            )

            trend_score = trend_strength(sdf)

            # =================================================
            # MASTER SCORE
            # =================================================

            master_score = (

                momentum_score * 0.30 +

                sharpe * 15 +

                trend_score * 10 +

                volatility_score * 0.20 +

                rsi_score * 0.10

            )

            # =================================================
            # CLASSIFICATION
            # =================================================

            if master_score >= 80:

                signal = "STRONG_BUY"

            elif master_score >= 60:

                signal = "BUY"

            elif master_score >= 40:

                signal = "WATCH"

            elif master_score >= 20:

                signal = "HOLD"

            else:

                signal = "AVOID"

            # =================================================
            # EXPECTED RETURNS
            # =================================================

            expected_5d = (
                latest["atr"] * 1.5
            )

            expected_15d = (
                latest["atr"] * 3
            )

            expected_30d = (
                latest["atr"] * 5
            )

            # =================================================
            # HOLD DAYS
            # =================================================

            if signal == "STRONG_BUY":

                hold_days = 30

            elif signal == "BUY":

                hold_days = 20

            elif signal == "WATCH":

                hold_days = 10

            else:

                hold_days = 5

            # =================================================
            # SAVE RESULT
            # =================================================

            results.append({

                "symbol": symbol,

                "close": round(
                    latest["close"], 2
                ),

                "rsi": round(
                    latest["rsi"], 2
                ),

                "momentum_20": round(
                    latest["momentum_20"], 2
                ),

                "volatility": round(
                    latest["volatility"], 2
                ),

                "atr": round(
                    latest["atr"], 2
                ),

                "master_score": round(
                    master_score, 2
                ),

                "signal": signal,

                "expected_5d": round(
                    expected_5d, 2
                ),

                "expected_15d": round(
                    expected_15d, 2
                ),

                "expected_30d": round(
                    expected_30d, 2
                ),

                "hold_days": hold_days

            })

        except Exception as e:

            print(f"{symbol} ERROR -> {e}")

    return pd.DataFrame(results)

# =========================================================
# MAIN PIPELINE
# =========================================================

def run_pipeline():

    print("=" * 60)
    print("RUNNING INSTITUTIONAL PIPELINE")
    print("=" * 60)

    # =====================================================
    # STEP 1 — DOWNLOAD MARKET DATA
    # =====================================================

    update_market_data()

    # =====================================================
    # STEP 2 — LOAD MARKET DATA
    # =====================================================

    df = load_parquet(
        "market_data.parquet"
    )

    if df.empty:

        print("Market data empty")
        return

    # =====================================================
    # STEP 3 — COMPUTE INDICATORS
    # =====================================================

    indicator_results = []

    symbols = df["symbol"].unique()

    for symbol in symbols:

        try:

            sdf = (
                df[df["symbol"] == symbol]
                .copy()
                .reset_index(drop=True)
            )

            sdf = add_indicators(sdf)

            indicator_results.append(sdf)

        except Exception as e:

            print(f"{symbol} indicator error -> {e}")

    final_df = pd.concat(
        indicator_results,
        ignore_index=True
    )

    # =====================================================
    # STEP 4 — SAVE INDICATOR DATA
    # =====================================================

    save_parquet(
        final_df,
        "indicator_data.parquet"
    )

    # =====================================================
    # STEP 5 — COMPUTE FACTOR SCORES
    # =====================================================

    factor_df = compute_factor_scores(
        final_df
    )

    # =====================================================
    # STEP 6 — SAVE FACTOR DATA
    # =====================================================

    save_parquet(
        factor_df,
        "factor_scores.parquet"
    )

    print("=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    run_pipeline()