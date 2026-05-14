# =========================================================
# INSTITUTIONAL PORTFOLIO OPTIMIZER
# =========================================================

import pandas as pd
import numpy as np

# =========================================================
# POSITION SIZE
# =========================================================

def calculate_position_size(

    capital,
    confidence,
    volatility

):

    # =====================================================
    # RISK BUDGET
    # =====================================================

    risk_budget = capital * 0.02

    # =====================================================
    # VOLATILITY ADJUSTMENT
    # =====================================================

    vol_adjustment = max(
        volatility,
        1
    )

    size = (

        risk_budget

        *

        (confidence / 100)

    ) / vol_adjustment

    return round(size, 2)

# =========================================================
# REGIME ALLOCATION
# =========================================================

def regime_cash_allocation(regime):

    mapping = {

        "BULL": 0.95,

        "SIDEWAYS": 0.70,

        "BEAR": 0.40,

        "HIGH_RISK": 0.20

    }

    return mapping.get(regime, 0.50)

# =========================================================
# MAX SECTOR EXPOSURE
# =========================================================

MAX_SECTOR_EXPOSURE = 0.30

# =========================================================
# MAX POSITION WEIGHT
# =========================================================

MAX_POSITION_WEIGHT = 0.10

# =========================================================
# PORTFOLIO OPTIMIZER
# =========================================================

def optimize_portfolio(

    signal_df,
    regime_data,
    total_capital=1000000

):

    # =====================================================
    # FILTER HIGH QUALITY SIGNALS
    # =====================================================

    df = signal_df.copy()

    df = df[

        df["signal"].isin(

            ["STRONG_BUY", "BUY"]

        )

    ]

    if df.empty:

        return pd.DataFrame()

    # =====================================================
    # SORT BY UPSIDE
    # =====================================================

    df = df.sort_values(

        "upside_score",

        ascending=False

    )

    # =====================================================
    # REGIME CASH CONTROL
    # =====================================================

    invested_capital = (

        total_capital

        *

        regime_cash_allocation(

            regime_data["regime"]

        )

    )

    # =====================================================
    # TRACKERS
    # =====================================================

    portfolio = []

    used_capital = 0

    sector_exposure = {}

    # =====================================================
    # BUILD PORTFOLIO
    # =====================================================

    for _, row in df.iterrows():

        sector = row["sector"]

        # =================================================
        # POSITION SIZE
        # =================================================

        allocation = calculate_position_size(

            invested_capital,

            row["confidence"],

            max(row["expected_30d"], 1)

        )

        # =================================================
        # MAX POSITION LIMIT
        # =================================================

        max_allowed = (

            total_capital

            *

            MAX_POSITION_WEIGHT

        )

        allocation = min(

            allocation,

            max_allowed

        )

        # =================================================
        # SECTOR EXPOSURE
        # =================================================

        current_sector = sector_exposure.get(
            sector,
            0
        )

        projected_sector = (

            current_sector + allocation

        ) / total_capital

        if projected_sector > MAX_SECTOR_EXPOSURE:

            continue

        # =================================================
        # CAPITAL LIMIT
        # =================================================

        if used_capital + allocation > invested_capital:

            break

        # =================================================
        # SAVE POSITION
        # =================================================

        sector_exposure[sector] = (

            current_sector + allocation

        )

        used_capital += allocation

        portfolio.append({

            "symbol": row["symbol"],

            "sector": sector,

            "theme": row["theme"],

            "signal": row["signal"],

            "confidence": row["confidence"],

            "meta_score": row["meta_score"],

            "allocation": round(
                allocation,
                2
            ),

            "portfolio_weight": round(

                allocation

                /

                total_capital

                *

                100,

                2

            ),

            "expected_30d": row["expected_30d"],

            "hold_days": row["hold_days"]

        })

    portfolio_df = pd.DataFrame(
        portfolio
    )

    return portfolio_df