# =========================================================
# INSTITUTIONAL INDICATOR ENGINE (PRODUCTION VERSION)
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
# SMA
# =========================================================

def SMA(series, period=20):

    return series.rolling(period).mean()

# =========================================================
# RSI
# =========================================================

def RSI(close, period=14):

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / period,
        min_periods=period
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
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
# ROLLING SHARPE RATIO
# =========================================================

def rolling_sharpe(close, window=50):

    returns = close.pct_change()

    rolling_mean = (
        returns.rolling(window).mean()
    )

    rolling_std = (
        returns.rolling(window).std()
    )

    sharpe = (
        rolling_mean / rolling_std
    ) * np.sqrt(252)

    return sharpe

# =========================================================
# MAX DRAWDOWN
# =========================================================

def max_drawdown(close):

    cumulative_max = close.cummax()

    drawdown = (
        close - cumulative_max
    ) / cumulative_max

    return drawdown

# =========================================================
# RATE OF CHANGE
# =========================================================

def ROC(close, period=12):

    return (
        (close - close.shift(period))
        /
        close.shift(period)
    ) * 100

# =========================================================
# MACD
# =========================================================

def MACD(close):

    ema12 = EMA(close, 12)
    ema26 = EMA(close, 26)

    macd = ema12 - ema26

    signal = EMA(macd, 9)

    histogram = macd - signal

    return macd, signal, histogram

# =========================================================
# BOLLINGER BANDS
# =========================================================

def BollingerBands(close, period=20):

    sma = SMA(close, period)

    std = close.rolling(period).std()

    upper = sma + (2 * std)
    lower = sma - (2 * std)

    bandwidth = (
        upper - lower
    ) / sma

    return upper, lower, bandwidth

# =========================================================
# VWAP
# =========================================================

def VWAP(df):

    typical_price = (
        df["high"] +
        df["low"] +
        df["close"]
    ) / 3

    volume_price = (
        typical_price * df["volume"]
    ).cumsum()

    cumulative_volume = (
        df["volume"].cumsum()
    )

    return volume_price / cumulative_volume

# =========================================================
# ADX
# =========================================================

def ADX(df, period=14):

    high = df["high"]
    low = df["low"]
    close = df["close"]

    plus_dm = high.diff()
    minus_dm = -low.diff()

    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()

    tr = pd.concat(
        [tr1, tr2, tr3],
        axis=1
    ).max(axis=1)

    atr = tr.rolling(period).mean()

    plus_di = (
        100 *
        plus_dm.rolling(period).sum()
        / atr
    )

    minus_di = (
        100 *
        minus_dm.rolling(period).sum()
        / atr
    )

    dx = (
        (plus_di - minus_di).abs()
        /
        (plus_di + minus_di)
    ) * 100

    adx = dx.rolling(period).mean()

    return adx

# =========================================================
# VOLUME SPIKE
# =========================================================

def volume_spike(volume, window=20):

    avg_volume = volume.rolling(window).mean()

    spike = volume / avg_volume

    return spike

# =========================================================
# RELATIVE STRENGTH
# =========================================================

def relative_strength(close, benchmark):

    benchmark = benchmark.replace(0, np.nan)

    rs = close / benchmark

    return rs

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
# INSTITUTIONAL ACCUMULATION SCORE
# =========================================================

def accumulation_score(df):

    score = 0

    latest = df.iloc[-1]

    if latest["close"] > latest["ema20"]:
        score += 1

    if latest["ema20"] > latest["ema50"]:
        score += 1

    if latest["volume_spike"] > 1.5:
        score += 1

    if latest["momentum_20"] > 5:
        score += 1

    if latest["adx"] > 25:
        score += 1

    return score

# =========================================================
# ADD ALL INDICATORS
# =========================================================

def add_indicators(df, benchmark_close=None):

    df = df.copy()

    # =====================================================
    # VALIDATION
    # =====================================================

    required_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    missing_cols = [
        c for c in required_cols
        if c not in df.columns
    ]

    if missing_cols:

        raise ValueError(
            f"Missing columns -> {missing_cols}"
        )

    # =====================================================
    # TREND
    # =====================================================

    df["ema20"] = EMA(df["close"], 20)
    df["ema50"] = EMA(df["close"], 50)
    df["ema200"] = EMA(df["close"], 200)

    df["sma20"] = SMA(df["close"], 20)
    df["sma50"] = SMA(df["close"], 50)

    # =====================================================
    # MOMENTUM
    # =====================================================

    df["rsi"] = RSI(df["close"])

    df["momentum_20"] = momentum(
        df["close"],
        20
    )

    df["roc_12"] = ROC(
        df["close"],
        12
    )

    # =====================================================
    # VOLATILITY
    # =====================================================

    df["atr"] = ATR(df)

    df["volatility"] = volatility(
        df["close"]
    )

    # =====================================================
    # MACD
    # =====================================================

    (
        df["macd"],
        df["macd_signal"],
        df["macd_hist"]
    ) = MACD(df["close"])

    # =====================================================
    # BOLLINGER BANDS
    # =====================================================

    (
        df["bb_upper"],
        df["bb_lower"],
        df["bb_bandwidth"]
    ) = BollingerBands(df["close"])

    # =====================================================
    # VWAP
    # =====================================================

    df["vwap"] = VWAP(df)

    # =====================================================
    # ADX
    # =====================================================

    df["adx"] = ADX(df)

    # =====================================================
    # VOLUME
    # =====================================================

    df["volume_sma20"] = SMA(
        df["volume"],
        20
    )

    df["volume_spike"] = volume_spike(
        df["volume"]
    )

    # =====================================================
    # RISK
    # =====================================================

    df["drawdown"] = max_drawdown(
        df["close"]
    )

    df["rolling_sharpe"] = rolling_sharpe(
        df["close"]
    )

    # =====================================================
    # RELATIVE STRENGTH
    # =====================================================

    if benchmark_close is not None:

        df["relative_strength"] = relative_strength(
            df["close"],
            benchmark_close
        )

    # =====================================================
    # TREND SCORE
    # =====================================================

    trend_scores = []

    for i in range(len(df)):

        temp = df.iloc[: i + 1]

        if len(temp) < 200:

            trend_scores.append(np.nan)

        else:

            try:

                trend_scores.append(
                    trend_strength(temp)
                )

            except:

                trend_scores.append(np.nan)

    df["trend_score"] = trend_scores

    # =====================================================
    # INSTITUTIONAL SCORE
    # =====================================================

    institutional_scores = []

    for i in range(len(df)):

        temp = df.iloc[: i + 1]

        if len(temp) < 50:

            institutional_scores.append(np.nan)

        else:

            try:

                institutional_scores.append(
                    accumulation_score(temp)
                )

            except:

                institutional_scores.append(np.nan)

    df["institutional_score"] = institutional_scores

    # =====================================================
    # CLEANUP
    # =====================================================

    df.replace(
        [np.inf, -np.inf],
        np.nan,
        inplace=True
    )

    return df