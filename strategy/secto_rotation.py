# =========================================================
# INSTITUTIONAL SECTOR ROTATION ENGINE
# =========================================================

import pandas as pd
import numpy as np

# =========================================================
# NSE SECTOR MAP
# =========================================================

SECTOR_MAP = {

    "RELIANCE.NS": "Energy",
    "ONGC.NS": "Energy",
    "BPCL.NS": "Energy",

    "TCS.NS": "IT",
    "INFY.NS": "IT",
    "WIPRO.NS": "IT",

    "HDFCBANK.NS": "Banking",
    "ICICIBANK.NS": "Banking",
    "SBIN.NS": "Banking",
    "AXISBANK.NS": "Banking",

    "SUNPHARMA.NS": "Pharma",
    "DRREDDY.NS": "Pharma",

    "MARUTI.NS": "Auto",
    "TATAMOTORS.NS": "Auto",

    "LT.NS": "Infrastructure",

    "ITC.NS": "FMCG",

    "BHARTIARTL.NS": "Telecom"

}

# =========================================================
# ASSIGN SECTOR
# =========================================================

def assign_sector(symbol):

    return SECTOR_MAP.get(
        symbol,
        "Other"
    )

# =========================================================
# ADD SECTOR COLUMN
# =========================================================

def add_sector_data(df):

    df = df.copy()

    df["sector"] = df["symbol"].apply(
        assign_sector
    )

    return df

# =========================================================
# COMPUTE SECTOR STRENGTH
# =========================================================

def compute_sector_strength(df):

    df = add_sector_data(df)

    sector_stats = []

    sectors = df["sector"].unique()

    for sector in sectors:

        sdf = (
            df[df["sector"] == sector]
            .copy()
        )

        if sdf.empty:
            continue

        # =================================================
        # FACTORS
        # =================================================

        avg_score = sdf[
            "master_score"
        ].mean()

        avg_momentum = sdf[
            "momentum_20"
        ].mean()

        avg_rsi = sdf[
            "rsi"
        ].mean()

        breadth = (

            len(
                sdf[
                    sdf["momentum_20"] > 0
                ]
            )

            /

            max(len(sdf), 1)

        ) * 100

        # =================================================
        # FINAL SECTOR SCORE
        # =================================================

        sector_strength = (

            avg_score * 0.40 +

            avg_momentum * 0.30 +

            avg_rsi * 0.10 +

            breadth * 0.20

        )

        sector_stats.append({

            "sector": sector,

            "avg_score": round(
                avg_score,
                2
            ),

            "avg_momentum": round(
                avg_momentum,
                2
            ),

            "avg_rsi": round(
                avg_rsi,
                2
            ),

            "breadth": round(
                breadth,
                2
            ),

            "sector_strength": round(
                sector_strength,
                2
            )

        })

    sector_df = pd.DataFrame(
        sector_stats
    )

    sector_df = sector_df.sort_values(
        "sector_strength",
        ascending=False
    )

    return sector_df

# =========================================================
# BOOST STOCK SCORES
# =========================================================

def apply_sector_rotation_boost(
    factor_df,
    sector_df
):

    factor_df = add_sector_data(
        factor_df
    )

    sector_strength_map = dict(

        zip(

            sector_df["sector"],

            sector_df["sector_strength"]

        )

    )

    adjusted_scores = []

    for _, row in factor_df.iterrows():

        score = row["master_score"]

        sector_strength = sector_strength_map.get(
            row["sector"],
            50
        )

        # =============================================
        # BOOST STRONG SECTORS
        # =============================================

        if sector_strength >= 70:

            score *= 1.15

        elif sector_strength <= 40:

            score *= 0.85

        adjusted_scores.append(score)

    factor_df["adjusted_score"] = np.round(
        adjusted_scores,
        2
    )

    return factor_df