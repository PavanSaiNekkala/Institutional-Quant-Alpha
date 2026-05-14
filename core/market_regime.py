# =========================================================
# ADVANCED MARKET REGIME ENGINE
# =========================================================

import pandas as pd
import numpy as np

# =========================================================
# EMA TREND REGIME
# =========================================================

def ema_trend_regime(df):

    try:

        close = df["close"]

        ema20 = close.ewm(span=20).mean()
        ema50 = close.ewm(span=50).mean()
        ema100 = close.ewm(span=100).mean()
        ema200 = close.ewm(span=200).mean()

        latest = close.iloc[-1]

        # STRONG BULL

        if (
            latest > ema20.iloc[-1]
            and ema20.iloc[-1] > ema50.iloc[-1]
            and ema50.iloc[-1] > ema100.iloc[-1]
            and ema100.iloc[-1] > ema200.iloc[-1]
        ):

            return "STRONG_BULL"

        # BULL

        elif (
            latest > ema50.iloc[-1]
        ):

            return "BULL"

        # STRONG BEAR

        elif (
            latest < ema20.iloc[-1]
            and ema20.iloc[-1] < ema50.iloc[-1]
            and ema50.iloc[-1] < ema100.iloc[-1]
            and ema100.iloc[-1] < ema200.iloc[-1]
        ):

            return "STRONG_BEAR"

        # BEAR

        elif (
            latest < ema50.iloc[-1]
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

        vol = (
            returns
            .rolling(20)
            .std()
            .iloc[-1]
            * np.sqrt(252)
        )

        if vol > 0.45:

            return "EXTREME_VOLATILITY"

        elif vol > 0.30:

            return "HIGH_VOLATILITY"

        elif vol > 0.18:

            return "MODERATE_VOLATILITY"

        return "LOW_VOLATILITY"

    except:

        return "UNKNOWN"

# =========================================================
# MOMENTUM REGIME
# =========================================================

def momentum_regime(df):

    try:

        momentum_50 = (
            df["close"]
            .pct_change(50)
            .iloc[-1]
        ) * 100

        if momentum_50 > 25:

            return "STRONG_POSITIVE"

        elif momentum_50 > 10:

            return "POSITIVE"

        elif momentum_50 < -25:

            return "STRONG_NEGATIVE"

        elif momentum_50 < -10:

            return "NEGATIVE"

        return "NEUTRAL"

    except:

        return "UNKNOWN"

# =========================================================
# VOLUME REGIME
# =========================================================

def volume_regime(df):

    try:

        recent_volume = (
            df["volume"].tail(5).mean()
        )

        long_volume = (
            df["volume"].tail(50).mean()
        )

        ratio = recent_volume / long_volume

        if ratio > 2:

            return "INSTITUTIONAL_ACTIVITY"

        elif ratio > 1.3:

            return "HIGH_ACTIVITY"

        elif ratio < 0.7:

            return "LOW_ACTIVITY"

        return "NORMAL_ACTIVITY"

    except:

        return "UNKNOWN"

# =========================================================
# LIQUIDITY REGIME
# =========================================================

def liquidity_regime(df):

    try:

        traded_value = (

            df["close"]
            * df["volume"]

        ).tail(20).mean()

        if traded_value > 5e9:

            return "ULTRA_LIQUID"

        elif traded_value > 1e9:

            return "HIGH_LIQUID"

        elif traded_value > 2e8:

            return "MODERATE_LIQUID"

        return "LOW_LIQUID"

    except:

        return "UNKNOWN"

# =========================================================
# BREAKOUT REGIME
# =========================================================

def breakout_regime(df):

    try:

        latest_close = df["close"].iloc[-1]

        high_52w = (
            df["high"]
            .rolling(252)
            .max()
            .iloc[-1]
        )

        ratio = latest_close / high_52w

        if ratio >= 0.98:

            return "NEAR_BREAKOUT"

        elif ratio >= 0.90:

            return "BREAKOUT_SETUP"

        elif ratio <= 0.70:

            return "WEAK_STRUCTURE"

        return "NORMAL_STRUCTURE"

    except:

        return "UNKNOWN"

# =========================================================
# VOLATILITY COMPRESSION
# =========================================================

def volatility_compression_regime(df):

    try:

        returns = df["close"].pct_change()

        recent_vol = (
            returns.tail(10).std()
        )

        long_vol = (
            returns.tail(50).std()
        )

        ratio = recent_vol / long_vol

        if ratio < 0.5:

            return "VOLATILITY_COMPRESSION"

        elif ratio > 1.5:

            return "VOLATILITY_EXPANSION"

        return "NORMAL_VOLATILITY"

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
        ema100 = close.ewm(span=100).mean()
        ema200 = close.ewm(span=200).mean()

        score = 0

        if close.iloc[-1] > ema20.iloc[-1]:
            score += 20

        if ema20.iloc[-1] > ema50.iloc[-1]:
            score += 20

        if ema50.iloc[-1] > ema100.iloc[-1]:
            score += 20

        if ema100.iloc[-1] > ema200.iloc[-1]:
            score += 20

        if close.iloc[-1] > ema200.iloc[-1]:
            score += 20

        return score

    except:

        return 0

# =========================================================
# FINAL MARKET REGIME ENGINE
# =========================================================

def detect_market_regime(df):

    try:

        return {

            "market_trend":
                ema_trend_regime(df),

            "volatility_regime":
                volatility_regime(df),

            "momentum_regime":
                momentum_regime(df),

            "volume_regime":
                volume_regime(df),

            "liquidity_regime":
                liquidity_regime(df),

            "breakout_regime":
                breakout_regime(df),

            "volatility_compression_regime":
                volatility_compression_regime(df),

            "market_strength_score":
                market_strength_score(df)
        }

    except:

        return {

            "market_trend":
                "UNKNOWN",

            "volatility_regime":
                "UNKNOWN",

            "momentum_regime":
                "UNKNOWN",

            "volume_regime":
                "UNKNOWN",

            "liquidity_regime":
                "UNKNOWN",

            "breakout_regime":
                "UNKNOWN",

            "volatility_compression_regime":
                "UNKNOWN",

            "market_strength_score":
                0
        }
