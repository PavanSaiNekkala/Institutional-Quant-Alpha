# =========================================================
# INSTITUTIONAL SCORING ENGINE
# =========================================================

from core.institutional_score import generate_scores
import pandas as pd
import numpy as np


# =========================================================
# RELATIVE STRENGTH SCORE
# =========================================================

def relative_strength_score(df):

    try:

        returns_20 = (
            df["close"].pct_change(20).iloc[-1]
        )

        returns_50 = (
            df["close"].pct_change(50).iloc[-1]
        )

        score = (
            (returns_20 * 0.6) +
            (returns_50 * 0.4)
        ) * 100

        return round(score, 2)

    except:
        return 0


# =========================================================
# VOLUME EXPANSION SCORE
# =========================================================

def volume_score(df):

    try:

        recent_volume = (
            df["volume"].tail(5).mean()
        )

        avg_volume = (
            df["volume"].tail(50).mean()
        )

        ratio = recent_volume / avg_volume

        return round(ratio * 10, 2)

    except:
        return 0


# =========================================================
# MOMENTUM SCORE
# =========================================================

def momentum_score(df):

    try:

        momentum_20 = (
            df["close"].pct_change(20).iloc[-1]
        ) * 100

        return round(momentum_20, 2)

    except:
        return 0


# =========================================================
# VOLATILITY SCORE
# =========================================================

def volatility_score(df):

    try:

        returns = df["close"].pct_change()

        vol = (
            returns.rolling(20).std().iloc[-1]
            * np.sqrt(252)
        )

        score = max(0, 100 - (vol * 100))

        return round(score, 2)

    except:
        return 0


# =========================================================
# TREND SCORE
# =========================================================

def trend_score(df):

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
# ACCUMULATION SCORE
# =========================================================

def accumulation_score(df):

    try:

        recent_close = df["close"].tail(10)

        tight_range = (
            recent_close.max() -
            recent_close.min()
        ) / recent_close.mean()

        recent_volume = (
            df["volume"].tail(10).mean()
        )

        long_volume = (
            df["volume"].tail(50).mean()
        )

        volume_ratio = (
            recent_volume / long_volume
        )

        score = (
            (1 - tight_range) * 50
        ) + (volume_ratio * 50)

        return round(score, 2)

    except:
        return 0


# =========================================================
# SMART MONEY SCORE
# =========================================================

def smart_money_score(df):

    try:

        rs = relative_strength_score(df)
        vol = volume_score(df)
        trend = trend_score(df)
        accum = accumulation_score(df)

        final_score = (
            rs * 0.30 +
            vol * 0.20 +
            trend * 0.30 +
            accum * 0.20
        )

        return round(final_score, 2)

    except:
        return 0


# =========================================================
# FINAL INSTITUTIONAL SCORE
# =========================================================

def institutional_score(df):

    try:

        rs = relative_strength_score(df)
        vol = volume_score(df)
        momentum = momentum_score(df)
        trend = trend_score(df)
        volatility = volatility_score(df)
        accumulation = accumulation_score(df)

        score = (
            rs * 0.20 +
            vol * 0.15 +
            momentum * 0.20 +
            trend * 0.25 +
            volatility * 0.10 +
            accumulation * 0.10
        )

        return round(score, 2)

    except:
        return 0


# =========================================================
# GENERATE FULL SCORES
# =========================================================
a
def generate_scores(df):

    return {

        "institutional_score":
            institutional_score(df),

        "smart_money_score":
            smart_money_score(df),

        "relative_strength":
            relative_strength_score(df),

        "volume_score":
            volume_score(df),

        "momentum_score":
            momentum_score(df),

        "trend_score":
            trend_score(df),

        "volatility_score":
            volatility_score(df),

        "accumulation_score":
            accumulation_score(df)
    }
