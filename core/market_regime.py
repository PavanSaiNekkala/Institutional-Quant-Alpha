# =========================================================
# MARKET REGIME ENGINE
# =========================================================

import pandas as pd
import numpy as np

# =========================================================
# MARKET TREND
# =========================================================

def market_trend(df):

    try:

        close = df["close"]

        ema20 = close.ewm(span=20).mean()
        ema50 = close.ewm(span=50).mean()
        ema200 = close.ewm(span=200).mean()

        latest_close = close.iloc[-1]

        if (
            latest_close > ema20.iloc[-1]
            and ema20.iloc[-1] > ema50.iloc[-1]
            and ema50.iloc[-1] > ema200.iloc[-1]
        ):

            return "STRONG_BULL"

        elif (
            latest_close > ema50.iloc[-1]
        ):

            return "BULL"

        elif (
            latest_close < ema20.iloc[-1]
            and ema20.iloc[-1] < ema50.iloc[-1]
            and ema50.iloc[-1] < ema200.iloc[-1]
        ):

            return "STRONG_BEAR"

        elif (
            latest_close < ema50.iloc[-1]
        ):

            return "BEAR"

        return "SIDEWAYS"

    except:

        return "UNKNOWN"

# =========================================================
# VOLATILITY REGIME
# =========================================================

def volatility_regime(df):

    try:

        returns = df["close"].pct_change()

        volatility = (
            returns.rolling(20).std().iloc[-1]
            * np.sqrt(252)
        )

        if volatility > 0.40:

            return "HIGH_VOLATILITY"

        elif volatility > 0.25:

            return "MODERATE_VOLATILITY"

        return "LOW_VOLATILITY"

    except:

        return "UNKNOWN"

# =========================================================
# MOMENTUM REGIME
# =========================================================

def momentum_regime(df):

    try:

        momentum = (
            df["close"]
            .pct_change(50)
            .iloc[-1]
        ) * 100

        if momentum > 20:

            return "STRONG_MOMENTUM"

        elif momentum > 5:

            return "POSITIVE_MOMENTUM"

        elif momentum < -20:

            return "STRONG_NEGATIVE"

        elif momentum < -5:

            return "NEGATIVE_MOMENTUM"

        return "NEUTRAL"

    except:

        return "UNKNOWN"

# =========================================================
# MARKET STRENGTH SCORE
# =========================================================

def market_strength_score(df):

    try:

        close = df["close"]

        ema20 = close.ewm(span=20).mean()
        ema50 = close.ewm(span=50).mean()
        ema200 = close.ewm(span=200).mean()

        score = 0

        if close.iloc[-1] > ema20.iloc[-1]:
            score += 25

        if ema20.iloc[-1] > ema50.iloc[-1]:
            score += 25

        if ema50.iloc[-1] > ema200.iloc[-1]:
            score += 25

        if close.iloc[-1] > ema200.iloc[-1]:
            score += 25

        return score

    except:

        return 0

# =========================================================
# FINAL MARKET REGIME
# =========================================================

def detect_market_regime(df):

    try:

        trend = market_trend(df)

        volatility = volatility_regime(df)

        momentum = momentum_regime(df)

        strength = market_strength_score(df)

        return {

            "market_trend": trend,

            "volatility_regime": volatility,

            "momentum_regime": momentum,

            "market_strength_score": strength
        }

    except:

        return {

            "market_trend": "UNKNOWN",

            "volatility_regime": "UNKNOWN",

            "momentum_regime": "UNKNOWN",

            "market_strength_score": 0
        }
