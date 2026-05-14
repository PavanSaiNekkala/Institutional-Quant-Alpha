# =========================================================
# INSTITUTIONAL SIGNAL ENGINE
# =========================================================

import pandas as pd
import numpy as np

# =========================================================
# SIGNAL CLASSIFICATION
# =========================================================

def classify_signal(score):

    if score >= 85:
        return "STRONG_BUY"

    elif score >= 70:
        return "BUY"

    elif score >= 55:
        return "WATCH"

    elif score >= 40:
        return "HOLD"

    return "AVOID"

# =========================================================
# CONFIDENCE ENGINE
# =========================================================

def compute_confidence(row):

    confidence = 50

    # =====================================================
    # MOMENTUM
    # =====================================================

    if row["momentum_20"] > 10:
        confidence += 10

    elif row["momentum_20"] < 0:
        confidence -= 10

    # =====================================================
    # RSI
    # =====================================================

    if 55 <= row["rsi"] <= 75:
        confidence += 10

    elif row["rsi"] > 85:
        confidence -= 10

    # =====================================================
    # VOLATILITY
    # =====================================================

    if row["volatility"] < 25:
        confidence += 10

    else:
        confidence -= 10

    # =====================================================
    # SECTOR STRENGTH
    # =====================================================

    if row["sector_strength"] > 70:
        confidence += 10

    elif row["sector_strength"] < 40:
        confidence -= 10

    # =====================================================
    # THEME STRENGTH
    # =====================================================

    if row["theme_strength"] > 70:
        confidence += 5

    # =====================================================
    # QUALITY
    # =====================================================

    if row["quality_factor"] > 70:
        confidence += 5

    return max(
        min(confidence, 100),
        0
    )

# =========================================================
# EXPECTANCY ENGINE
# =========================================================

def expected_returns(row):

    volatility = row["volatility"]

    trend = row["trend_factor"]

    # =====================================================
    # RETURN MODEL
    # =====================================================

    expected_5d = (

        trend * 0.15

    ) / max(volatility, 1)

    expected_15d = (

        trend * 0.35

    ) / max(volatility, 1)

    expected_30d = (

        trend * 0.60

    ) / max(volatility, 1)

    return (

        round(expected_5d, 2),

        round(expected_15d, 2),

        round(expected_30d, 2)

    )

# =========================================================
# HOLD DAYS
# =========================================================

def estimate_hold_days(signal):

    mapping = {

        "STRONG_BUY": 30,

        "BUY": 20,

        "WATCH": 10,

        "HOLD": 5,

        "AVOID": 0

    }

    return mapping.get(signal, 5)

# =========================================================
# SIGNAL ENGINE
# =========================================================

def generate_signals(df):

    results = []

    for _, row in df.iterrows():

        score = row["meta_score"]

        # =================================================
        # SIGNAL
        # =================================================

        signal = classify_signal(score)

        # =================================================
        # CONFIDENCE
        # =================================================

        confidence = compute_confidence(
            row
        )

        # =================================================
        # EXPECTED RETURNS
        # =================================================

        (

            exp_5d,
            exp_15d,
            exp_30d

        ) = expected_returns(row)

        # =================================================
        # HOLD DAYS
        # =================================================

        hold_days = estimate_hold_days(
            signal
        )

        # =================================================
        # UPSIDE SCORE
        # =====================================================

        upside_score = (

            exp_30d * confidence

        ) / 100

        # =================================================
        # FINAL RESULT
        # =================================================

        results.append({

            "symbol": row["symbol"],

            "sector": row["sector"],

            "theme": row["theme"],

            "signal": signal,

            "confidence": round(
                confidence,
                2
            ),

            "meta_score": round(
                score,
                2
            ),

            "expected_5d": exp_5d,

            "expected_15d": exp_15d,

            "expected_30d": exp_30d,

            "hold_days": hold_days,

            "upside_score": round(
                upside_score,
                2
            )

        })

    signal_df = pd.DataFrame(
        results
    )

    signal_df = signal_df.sort_values(

        "upside_score",

        ascending=False

    )

    return signal_df