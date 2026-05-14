import pandas as pd
import numpy as np

# =========================================================
# DETECT MARKET REGIME
# =========================================================

def detect_market_regime(df):

    try:

        if df.empty:

            return {
                "regime": "UNKNOWN",
                "trend_strength": 0,
                "momentum": 0,
                "volatility": 0
            }

        # =================================================
        # BASIC METRICS
        # =================================================

        avg_score = df["institutional_score"].mean()

        momentum = df["momentum_20"].mean()

        volatility = df["volatility"].mean()

        bullish_pct = (
            (df["signal"] == "STRONG BUY").mean()
        ) * 100

        # =================================================
        # TREND STRENGTH
        # =================================================

        trend_strength = round(
            (
                avg_score * 0.5
                + bullish_pct * 0.3
                + momentum * 0.2
            ),
            2
        )

        # =================================================
        # REGIME CLASSIFICATION
        # =================================================

        if (
            avg_score > 70
            and momentum > 5
            and bullish_pct > 40
        ):

            regime = "BULLISH"

        elif (
            avg_score < 40
            and momentum < -5
        ):

            regime = "BEARISH"

        else:

            regime = "SIDEWAYS"

        # =================================================
        # OUTPUT
        # =================================================

        return {

            "regime": regime,

            "trend_strength": round(
                trend_strength,
                2
            ),

            "momentum": round(
                momentum,
                2
            ),

            "volatility": round(
                volatility,
                2
            )
        }

    except Exception as e:

        print(
            f"Market regime error: {e}"
        )

        return {

            "regime": "UNKNOWN",

            "trend_strength": 0,

            "momentum": 0,

            "volatility": 0
        }
