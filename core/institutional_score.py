# =========================================================
# ADVANCED INSTITUTIONAL SCORING ENGINE
# =========================================================

import pandas as pd
import numpy as np

# =========================================================
# RELATIVE STRENGTH
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

        mom100 = (
            df["close"].pct_change(100).iloc[-1]
        ) * 100

        score = (
            mom20 * 0.4 +
            mom50 * 0.3 +
            mom100 * 0.3
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

        score = ratio * 20

        return round(score, 2)

    except:

        return 0

# =========================================================
# DELIVERY ACCUMULATION SCORE
# =========================================================

def accumulation_score(df):

    try:

        recent_close = df["close"].tail(15)

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
# VOLATILITY COMPRESSION
# =========================================================

def volatility_score(df):

    try:

        returns = df["close"].pct_change()

        vol = (
            returns
            .rolling(20)
            .std()
            .iloc[-1]
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
# BREAKOUT PROBABILITY
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

        score = (
            latest_close / high_52w
        ) * 100

        return round(score, 2)

    except:

        return 0

# =========================================================
# PRICE STRUCTURE
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
# LIQUIDITY SCORE
# =========================================================

def liquidity_score(df):

    try:

        traded_value = (

            df["close"]
            * df["volume"]

        ).tail(20).mean()

        score = traded_value / 1e7

        return round(score, 2)

    except:

        return 0

# =========================================================
# GAP STRENGTH
# =========================================================

def gap_strength_score(df):

    try:

        gap = (

            (
                df["open"]
                - df["close"].shift(1)
            )

            / df["close"].shift(1)

        ).iloc[-1] * 100

        return round(gap, 2)

    except:

        return 0

# =========================================================
# ATR EXPANSION SCORE
# =========================================================

def atr_expansion_score(df):

    try:

        tr = pd.concat([

            df["high"] - df["low"],

            (
                df["high"]
                - df["close"].shift()
            ).abs(),

            (
                df["low"]
                - df["close"].shift()
            ).abs()

        ], axis=1).max(axis=1)

        atr20 = tr.rolling(20).mean()

        ratio = (
            atr20.iloc[-1]
            / atr20.iloc[-20]
        )

        return round(ratio * 50, 2)

    except:

        return 0

# =========================================================
# VOLUME DELIVERY TREND
# =========================================================

def volume_trend_score(df):

    try:

        vol5 = df["volume"].tail(5).mean()

        vol20 = df["volume"].tail(20).mean()

        score = (
            vol5 / vol20
        ) * 100

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

        liquidity = liquidity_score(df)

        final_score = (

            rs * 0.20 +

            vol * 0.15 +

            trend * 0.20 +

            accum * 0.20 +

            breakout * 0.15 +

            liquidity * 0.10

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

        momentum = momentum_score(df)

        trend = trend_score(df)

        volume = volume_score(df)

        volatility = volatility_score(df)

        accumulation = accumulation_score(df)

        breakout = breakout_score(df)

        structure = price_structure_score(df)

        liquidity = liquidity_score(df)

        gap = gap_strength_score(df)

        atr = atr_expansion_score(df)

        volume_trend = volume_trend_score(df)

        score = (

            rs * 0.14 +

            momentum * 0.14 +

            trend * 0.14 +

            volume * 0.10 +

            volatility * 0.08 +

            accumulation * 0.10 +

            breakout * 0.08 +

            structure * 0.05 +

            liquidity * 0.05 +

            gap * 0.04 +

            atr * 0.04 +

            volume_trend * 0.04

        )

        score = max(
            0,
            min(score, 100)
        )

        return round(score, 2)

    except:

        return 0

# =========================================================
# GENERATE ALL SCORES
# =========================================================

def generate_scores(df):

    return {

        "institutional_score":
            institutional_score(df),

        "smart_money_score":
            smart_money_score(df),

        "relative_strength":
            relative_strength_score(df),

        "momentum_score":
            momentum_score(df),

        "trend_score":
            trend_score(df),

        "volume_score":
            volume_score(df),

        "volatility_score":
            volatility_score(df),

        "accumulation_score":
            accumulation_score(df),

        "breakout_score":
            breakout_score(df),

        "price_structure_score":
            price_structure_score(df),

        "liquidity_score":
            liquidity_score(df),

        "gap_strength_score":
            gap_strength_score(df),

        "atr_expansion_score":
            atr_expansion_score(df),

        "volume_trend_score":
            volume_trend_score(df)
    }
