# =========================================================
# INSTITUTIONAL MONITORING ENGINE
# =========================================================

import pandas as pd
import numpy as np
from datetime import datetime

# =========================================================
# PORTFOLIO SUMMARY
# =========================================================

def portfolio_summary(portfolio_df):

    if portfolio_df.empty:

        return {}

    summary = {

        "total_positions": len(portfolio_df),

        "total_allocation": round(

            portfolio_df["allocation"].sum(),

            2

        ),

        "avg_confidence": round(

            portfolio_df["confidence"].mean(),

            2

        ),

        "avg_meta_score": round(

            portfolio_df["meta_score"].mean(),

            2

        ),

        "avg_expected_30d": round(

            portfolio_df["expected_30d"].mean(),

            2

        )

    }

    return summary

# =========================================================
# SECTOR EXPOSURE
# =========================================================

def sector_exposure(portfolio_df):

    if portfolio_df.empty:

        return pd.DataFrame()

    sector_df = (

        portfolio_df

        .groupby("sector")

        ["portfolio_weight"]

        .sum()

        .reset_index()

    )

    sector_df = sector_df.sort_values(

        "portfolio_weight",

        ascending=False

    )

    return sector_df

# =========================================================
# SIGNAL DISTRIBUTION
# =========================================================

def signal_distribution(portfolio_df):

    if portfolio_df.empty:

        return pd.DataFrame()

    signal_df = (

        portfolio_df

        .groupby("signal")

        .size()

        .reset_index(name="count")

    )

    return signal_df

# =========================================================
# RISK ALERTS
# =========================================================

def risk_alerts(

    portfolio_df,
    regime_data

):

    alerts = []

    # =====================================================
    # REGIME ALERT
    # =====================================================

    regime = regime_data["regime"]

    if regime == "HIGH_RISK":

        alerts.append(

            "⚠️ High volatility regime detected"

        )

    elif regime == "BEAR":

        alerts.append(

            "⚠️ Bear market conditions active"

        )

    # =====================================================
    # CONCENTRATION ALERT
    # =====================================================

    if not portfolio_df.empty:

        max_weight = portfolio_df[
            "portfolio_weight"
        ].max()

        if max_weight > 15:

            alerts.append(

                "⚠️ High single-position concentration"

            )

    # =====================================================
    # SECTOR CONCENTRATION
    # =====================================================

    sector_df = sector_exposure(
        portfolio_df
    )

    if not sector_df.empty:

        largest_sector = sector_df[
            "portfolio_weight"
        ].max()

        if largest_sector > 35:

            alerts.append(

                "⚠️ Excessive sector concentration"

            )

    # =====================================================
    # LOW CONFIDENCE
    # =====================================================

    if not portfolio_df.empty:

        avg_confidence = portfolio_df[
            "confidence"
        ].mean()

        if avg_confidence < 60:

            alerts.append(

                "⚠️ Low portfolio confidence"

            )

    return alerts

# =========================================================
# SYSTEM HEALTH
# =========================================================

def system_health():

    health = {

        "timestamp": datetime.now(),

        "pipeline_status": "HEALTHY",

        "data_status": "UPDATED",

        "risk_engine": "ACTIVE",

        "signal_engine": "ACTIVE",

        "portfolio_engine": "ACTIVE"

    }

    return health

# =========================================================
# COMPLETE MONITORING REPORT
# =========================================================

def generate_monitoring_report(

    portfolio_df,
    regime_data

):

    report = {

        "summary": portfolio_summary(
            portfolio_df
        ),

        "sector_exposure": sector_exposure(
            portfolio_df
        ),

        "signal_distribution": signal_distribution(
            portfolio_df
        ),

        "alerts": risk_alerts(

            portfolio_df,
            regime_data

        ),

        "system_health": system_health()

    }

    return report