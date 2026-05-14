# =========================================================
# INSTITUTIONAL SCORING ENGINE (UPGRADED)
# =========================================================

import pandas as pd
import numpy as np

# =========================================================
# NORMALIZATION
# =========================================================

def normalize(value, min_val=0, max_val=100):

    try:

        value = max(min_val, min(value, max_val))

        return round(
            ((value - min_val) / (max_val - min_val)) * 100,
            2
        )

    except:

        return 0

# =========================================================
# RELATIVE STRENGTH SCORE
# =========================================================

def relative_strength_score(df):

    try:

        r20 = df["close"].pct_change(20).iloc[-1]
        r50 = df["close"].pct_change(50).iloc[-1]
        r100 = df["close"].pct_change(100).iloc[-1]

        score = (
            r20 * 0.4 +
            r50 * 0.3 +
            r100 * 0.3
        ) * 100

        return round(score, 2)

    except:

        return 0

# =========================================================
# VOLUME SCORE
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

        return round(ratio * 20, 2)

    except:

        return 0

# =========================================================
# MOMENTUM SCORE
# =========================================================

def momentum_score(df):

    try:

        mom20 = (
            df["close"].pct_change(20).iloc[-1]
        ) * 100

        mom50 = (
            df["close"].pct_change(50).iloc[-1]
        ) * 100

        score = (
            mom20 * 0.6 +
            mom50 * 0.4
        )

        return round(score, 2)

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

        score = max(
            0,
            100 - (vol * 100)
        )

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
            recent_close.max()
            - recent_close.min()
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
            ((1 - tight_range) * 50)
            + (volume_ratio * 50)
        )

        return round(score, 2)

    except:

        return 0

# =========================================================
# BREAKOUT SCORE
# =========================================================

def breakout_score(df):

    try:

        latest_close = df["close"].iloc[-1]

        high_52w = (
            df["high"]
            .rolling(252)
            .max()
            .iloc[-1]
        )

        distance = (
            latest_close / high_52w
        ) * 100

        return round(distance, 2)

    except:

        return 0

# =========================================================
# PRICE STRUCTURE SCORE
# =========================================================

def price_structure_score(df):

    try:

        highs = df["high"].tail(20)
        lows = df["low"].tail(20)

        higher_highs = highs.diff().gt(0).sum()
        higher_lows = lows.diff().gt(0).sum()

        score = (
            (higher_highs + higher_lows)
            / 40
        ) * 100

        return round(score, 2)

    except:

        return 0

# =========================================================
# RISK REWARD SCORE
# =========================================================

def risk_reward_score(df):

    try:

        atr = (
            df["high"] - df["low"]
        ).rolling(14).mean().iloc[-1]

        latest_close = df["close"].iloc[-1]

        reward = (
            latest_close -
            df["close"].rolling(50).mean().iloc[-1]
        )

        rr = reward / atr

        return round(rr * 10, 2)

    except:

        return 0

# =========================================================
# LIQUIDITY SCORE
# =========================================================

def liquidity_score(df):

    try:

        traded_value = (
            df["close"] *
            df["volume"]
        ).tail(20).mean()

        score = traded_value / 1e7

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
        breakout = breakout_score(df)

        final_score = (

            rs * 0.25 +
            vol * 0.20 +
            trend * 0.25 +
            accum * 0.20 +
            breakout * 0.10

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
        breakout = breakout_score(df)
        structure = price_structure_score(df)

        score = (

            rs * 0.18 +
            vol * 0.12 +
            momentum * 0.18 +
            trend * 0.20 +
            volatility * 0.10 +
            accumulation * 0.10 +
            breakout * 0.07 +
            structure * 0.05

        )

        score = max(0, min(score, 100))

        return round(score, 2)

    except:

        return 0

# =========================================================
# GENERATE SCORES
# =========================================================

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
            accumulation_score(df),

        "breakout_score":
            breakout_score(df),

        "price_structure_score":
            price_structure_score(df),

        "risk_reward_score":
            risk_reward_score(df),

        "liquidity_score":
            liquidity_score(df)
    }
