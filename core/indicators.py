# =========================================================
# INSTITUTIONAL INDICATOR ENGINE
# =========================================================

import pandas as pd
import numpy as np

# =========================================================
# EMA
# =========================================================

def EMA(series, period=20):

    return series.ewm(
        span=period,
        adjust=False
    ).mean()

# =========================================================
# RSI (Institutional EMA Version)
# =========================================================

def RSI(close, period=14):

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1/period,
        min_periods=period
    ).mean()

    avg_loss = loss.ewm(
        alpha=1/period,
        min_periods=period
    ).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi

# =========================================================
# ATR
# =========================================================

def ATR(df, period=14):

    high = df["high"]
    low = df["low"]
    close = df["close"]

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()

    tr = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    atr = tr.rolling(period).mean()

    return atr

# =========================================================
# VOLATILITY
# =========================================================

def volatility(close, window=20):

    returns = close.pct_change()

    vol = (
        returns.rolling(window).std()
        * np.sqrt(252)
    )

    return vol

# =========================================================
# MOMENTUM
# =========================================================

def momentum(close, period=20):

    return (
        close / close.shift(period) - 1
    ) * 100

# =========================================================
# SHARPE RATIO
# =========================================================

def sharpe_ratio(close):

    returns = close.pct_change().dropna()

    if returns.std() == 0:
        return 0

    sharpe = (
        returns.mean() /
        returns.std()
    ) * np.sqrt(252)

    return sharpe

# =========================================================
# TREND STRENGTH
# =========================================================

def trend_strength(df):

    close = df["close"]

    ema20 = EMA(close, 20)
    ema50 = EMA(close, 50)
    ema200 = EMA(close, 200)

    score = 0

    if close.iloc[-1] > ema20.iloc[-1]:
        score += 1

    if ema20.iloc[-1] > ema50.iloc[-1]:
        score += 1

    if ema50.iloc[-1] > ema200.iloc[-1]:
        score += 1

    return score

# =========================================================
# ADD ALL INDICATORS
# =========================================================

def add_indicators(df):

    df = df.copy()

    df["ema20"] = EMA(df["close"], 20)
    df["ema50"] = EMA(df["close"], 50)
    df["ema200"] = EMA(df["close"], 200)

    df["rsi"] = RSI(df["close"])

    df["atr"] = ATR(df)

    df["volatility"] = volatility(df["close"])

    df["momentum_20"] = momentum(df["close"], 20)

    return df