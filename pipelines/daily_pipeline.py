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

    if df.empty:
        print("Factor scoring skipped -> empty dataframe")
        return pd.DataFrame()

    symbols = df["symbol"].unique()

    for symbol in symbols:

        try:

            sdf = (
                df[df["symbol"] == symbol]
                .copy()
                .reset_index(drop=True)
            )

            if len(sdf) < 50:
                print(f"{symbol} skipped -> insufficient data")
                continue

            required_cols = [
                "close",
                "momentum_20",
                "rsi",
                "volatility",
                "atr"
            ]

            missing_cols = [
                c for c in required_cols
                if c not in sdf.columns
            ]

            if missing_cols:
                print(
                    f"{symbol} missing columns -> {missing_cols}"
                )
                continue

            latest = sdf.iloc[-1]

            # =================================================
            # FACTORS
            # =================================================

            momentum_score = float(
                latest["momentum_20"]
            )

            rsi_score = float(
                latest["rsi"]
            )

            volatility_score = (
                100 - float(latest["volatility"]) * 100
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

            print(f"{symbol} FACTOR ERROR -> {e}")

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

    try:

        update_market_data()

    except Exception as e:

        print(f"MARKET DATA ERROR -> {e}")
        return

    # =====================================================
    # STEP 2 — LOAD MARKET DATA
    # =====================================================

    try:

        df = load_parquet(
            "market_data.parquet"
        )

    except Exception as e:

        print(f"LOAD ERROR -> {e}")
        return

    if df.empty:

        print("Market data empty")
        return

    print(f"Loaded rows -> {len(df)}")

    # =====================================================
    # STEP 3 — COMPUTE INDICATORS
    # =====================================================

    indicator_results = []

    symbols = df["symbol"].unique()

    print(f"Processing {len(symbols)} symbols")

    for symbol in symbols:

        try:

            sdf = (
                df[df["symbol"] == symbol]
                .copy()
                .reset_index(drop=True)
            )

            if sdf.empty:
                continue

            sdf.columns = [
                str(c).lower()
                for c in sdf.columns
            ]

            if "close" not in sdf.columns:

                print(
                    f"{symbol} skipped -> close missing"
                )

                continue

            sdf = add_indicators(sdf)

            indicator_results.append(sdf)

            print(f"{symbol} indicators completed")

        except Exception as e:

            print(f"{symbol} INDICATOR ERROR -> {e}")

    # =====================================================
    # SAFETY CHECK
    # =====================================================

    if len(indicator_results) == 0:

        print("No indicator results generated")
        return

    final_df = pd.concat(
        indicator_results,
        ignore_index=True
    )

    if final_df.empty:

        print("Final dataframe empty")
        return

    print(f"Final rows -> {len(final_df)}")

    # =====================================================
    # STEP 4 — SAVE INDICATOR DATA
    # =====================================================

    try:

        save_parquet(
            final_df,
            "indicator_data.parquet"
        )

        print("Indicator data saved")

    except Exception as e:

        print(f"SAVE ERROR -> {e}")

    # =====================================================
    # STEP 5 — COMPUTE FACTOR SCORES
    # =====================================================

    factor_df = compute_factor_scores(
        final_df
    )

    if factor_df.empty:

        print("Factor dataframe empty")
        return

    print(f"Factor rows -> {len(factor_df)}")

    # =====================================================
    # STEP 6 — SAVE FACTOR DATA
    # =====================================================

    try:

        save_parquet(
            factor_df,
            "factor_scores.parquet"
        )

        print("Factor scores saved")

    except Exception as e:

        print(f"FACTOR SAVE ERROR -> {e}")

    print("=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    run_pipeline()
