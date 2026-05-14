# =========================================================
# INSTITUTIONAL MARKET REGIME ENGINE
# =========================================================

import pandas as pd
import numpy as np
import yfinance as yf

# =========================================================
# MARKET BENCHMARKS
# =========================================================

NIFTY_SYMBOL = "^NSEI"

VIX_SYMBOL = "^INDIAVIX"

# =========================================================
# FETCH MARKET DATA
# =========================================================

def fetch_market_data():

    nifty = yf.download(
        NIFTY_SYMBOL,
        period="6mo",
        auto_adjust=True,
        progress=False
    )

    vix = yf.download(
        VIX_SYMBOL,
        period="6mo",
        auto_adjust=True,
        progress=False
    )

    return nifty, vix

# =========================================================
# CALCULATE MARKET BREADTH
# =========================================================

def market_breadth(factor_df):

    advancing = len(
        factor_df[
            factor_df["momentum_20"] > 0
        ]
    )

    declining = len(
        factor_df[
            factor_df["momentum_20"] <= 0
        ]
    )

    total = max(
        advancing + declining,
        1
    )

    breadth = (
        advancing / total
    ) * 100

    return round(breadth, 2)

# =========================================================
# DETECT REGIME
# =========================================================

def detect_market_regime(factor_df):

    nifty, vix = fetch_market_data()

    if nifty.empty or vix.empty:

        return {

            "regime": "UNKNOWN",

            "vix": None,

            "breadth": None

        }

    close = nifty["Close"]

    # =====================================================
    # MOVING AVERAGES
    # =====================================================

    sma20 = close.rolling(20).mean()

    sma50 = close.rolling(50).mean()

    current_price = close.iloc[-1]

    # =====================================================
    # VIX
    # =====================================================

    current_vix = float(
        vix["Close"].iloc[-1]
    )

    # =====================================================
    # BREADTH
    # =====================================================

    breadth = market_breadth(
        factor_df
    )

    # =====================================================
    # REGIME LOGIC
    # =====================================================

    if current_vix > 22:

        regime = "HIGH_RISK"

    elif (
        current_price > sma20.iloc[-1]
        and
        sma20.iloc[-1] > sma50.iloc[-1]
        and
        breadth > 60
    ):

        regime = "BULL"

    elif (

        current_price < sma50.iloc[-1]
        and
        breadth < 40

    ):

        regime = "BEAR"

    else:

        regime = "SIDEWAYS"

    # =====================================================
    # OUTPUT
    # =====================================================

    return {

        "regime": regime,

        "vix": round(current_vix, 2),

        "breadth": breadth,

        "nifty_close": round(
            current_price,
            2
        )

    }