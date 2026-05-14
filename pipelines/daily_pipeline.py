# =========================================================
# INSTITUTIONAL DAILY PIPELINE (ADVANCED VERSION)
# =========================================================

import pandas as pd
import numpy as np

from core.market_data import (
    update_market_data,
    load_parquet,
    save_parquet
)

import core.indicators as indicators

# =========================================================
# SAFE VALUE
# =========================================================

def safe_value(v, default=0):

    try:

        if pd.isna(v):
            return default

        if np.isinf(v):
            return default

        return float(v)

    except:

        return default

# =========================================================
# SIGNAL ENGINE
# =========================================================

def generate_signal(score):

    if score >= 85:
        return "STRONG_BUY"

    elif score >= 70:
        return "BUY"

    elif score >= 55:
        return "ACCUMULATE"

    elif score >= 40:
        return "WATCH"

    elif score >= 25:
        return "HOLD"

    return "AVOID"

# =========================================================
# HOLD DAYS ESTIMATION
# =========================================================

def estimate_hold_days(signal):

    mapping = {

        "STRONG_BUY": 30,
        "BUY": 20,
        "ACCUMULATE": 15,
        "WATCH": 10,
        "HOLD": 5,
        "AVOID": 0

    }

    return mapping.get(signal, 5)

# =========================================================
# FACTOR SCORE ENGINE
# =========================================================

def compute_factor_scores(df):

    results = []

    if df.empty:

        print("Factor scoring skipped -> empty dataframe")

        return pd.DataFrame()

    symbols = df["symbol"].unique()

    print(f"Scoring {len(symbols)} symbols")

    for symbol in symbols:

        try:

            sdf = (
                df[df["symbol"] == symbol]
                .copy()
                .reset_index(drop=True)
            )

            if len(sdf) < 200:

                print(f"{symbol} skipped -> insufficient history")

                continue

            latest = sdf.iloc[-1]

            # =================================================
            # FACTOR EXTRACTION
            # =================================================

            momentum_score = safe_value(
                latest.get("momentum_20")
            )

            rsi_score = safe_value(
                latest.get("rsi")
            )

            volatility_score = (
                100 -
                safe_value(
                    latest.get("volatility")
                ) * 100
            )

            trend_score = (
                safe_value(
                    latest.get("trend_score")
                ) * 15
            )

            institutional_score = (
                safe_value(
                    latest.get("institutional_score")
                ) * 10
            )

            sharpe_score = (
                safe_value(
                    latest.get("rolling_sharpe")
                ) * 10
            )

            adx_score = safe_value(
                latest.get("adx")
            )

            volume_score = (
                safe_value(
                    latest.get("volume_spike")
                ) * 10
            )

            roc_score = safe_value(
                latest.get("roc_12")
            )

            macd_score = safe_value(
                latest.get("macd_hist")
            ) * 20

            drawdown_penalty = abs(
                safe_value(
                    latest.get("drawdown")
                ) * 100
            )

            # =================================================
            # MASTER INSTITUTIONAL SCORE
            # =================================================

            master_score = (

                momentum_score * 0.20 +

                rsi_score * 0.10 +

                volatility_score * 0.10 +

                trend_score * 0.15 +

                institutional_score * 0.15 +

                sharpe_score * 0.10 +

                adx_score * 0.05 +

                volume_score * 0.05 +

                roc_score * 0.05 +

                macd_score * 0.05 -

                drawdown_penalty * 0.05

            )

            # =================================================
            # CLAMP SCORE
            # =================================================

            master_score = max(
                0,
                min(master_score, 100)
            )

            # =================================================
            # SIGNAL
            # =================================================

            signal = generate_signal(master_score)

            hold_days = estimate_hold_days(signal)

            # =================================================
            # EXPECTED RETURNS
            # =================================================

            atr = safe_value(latest.get("atr"))

            expected_5d = atr * 1.5
            expected_15d = atr * 3
            expected_30d = atr * 5

            # =================================================
            # SAVE RESULT
            # =================================================

            results.append({

                "symbol": symbol,

                "close": round(
                    safe_value(latest.get("close")),
                    2
                ),

                "master_score": round(
                    master_score,
                    2
                ),

                "signal": signal,

                "hold_days": hold_days,

                # =============================================
                # CORE FACTORS
                # =============================================

                "rsi": round(
                    rsi_score,
                    2
                ),

                "momentum_20": round(
                    momentum_score,
                    2
                ),

                "volatility": round(
                    safe_value(
                        latest.get("volatility")
                    ),
                    4
                ),

                "atr": round(
                    atr,
                    2
                ),

                "adx": round(
                    adx_score,
                    2
                ),

                "roc_12": round(
                    roc_score,
                    2
                ),

                "volume_spike": round(
                    safe_value(
                        latest.get("volume_spike")
                    ),
                    2
                ),

                "rolling_sharpe": round(
                    safe_value(
                        latest.get("rolling_sharpe")
                    ),
                    2
                ),

                "institutional_score": round(
                    safe_value(
                        latest.get("institutional_score")
                    ),
                    2
                ),

                "trend_score": round(
                    safe_value(
                        latest.get("trend_score")
                    ),
                    2
                ),

                # =============================================
                # EXPECTED RETURNS
                # =============================================

                "expected_5d": round(
                    expected_5d,
                    2
                ),

                "expected_15d": round(
                    expected_15d,
                    2
                ),

                "expected_30d": round(
                    expected_30d,
                    2
                )

            })

        except Exception as e:

            print(f"{symbol} FACTOR ERROR -> {e}")

    factor_df = pd.DataFrame(results)

    if factor_df.empty:

        return factor_df

    # =====================================================
    # RANKING
    # =====================================================

    factor_df = factor_df.sort_values(
        by="master_score",
        ascending=False
    )

    factor_df["rank"] = range(
        1,
        len(factor_df) + 1
    )

    return factor_df

# =========================================================
# MAIN PIPELINE
# =========================================================

def run_pipeline():

    print("=" * 60)
    print("RUNNING INSTITUTIONAL PIPELINE")
    print("=" * 60)

    # =====================================================
    # STEP 1 — UPDATE MARKET DATA
    # =====================================================

    try:

        update_market_data()

    except Exception as e:

        print(f"MARKET DATA ERROR -> {e}")

        return

    # =====================================================
    # STEP 2 — LOAD DATA
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

            sdf.columns = [
                str(c).lower()
                for c in sdf.columns
            ]

            if "close" not in sdf.columns:

                print(f"{symbol} skipped -> close missing")

                continue

            sdf = indicators.add_indicators(sdf)

            indicator_results.append(sdf)

            print(f"{symbol} indicators completed")

        except Exception as e:

            print(f"{symbol} indicator error -> {e}")

    # =====================================================
    # VALIDATION
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

    # =====================================================
    # STEP 4 — SAVE INDICATORS
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
    # STEP 5 — FACTOR ENGINE
    # =====================================================

    factor_df = compute_factor_scores(
        final_df
    )

    if factor_df.empty:

        print("Factor dataframe empty")

        return

    # =====================================================
    # STEP 6 — SAVE FACTORS
    # =====================================================

    try:

        save_parquet(
            factor_df,
            "factor_scores.parquet"
        )

        print("Factor scores saved")

    except Exception as e:

        print(f"FACTOR SAVE ERROR -> {e}")

    # =====================================================
    # COMPLETED
    # =====================================================

    print("=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    run_pipeline()