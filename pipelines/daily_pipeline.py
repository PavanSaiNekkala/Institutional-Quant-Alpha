# =========================================================
# IMPORTS
# =========================================================

import pandas as pd
import numpy as np
from pathlib import Path
import traceback

from core.market_data import load_parquet
from core.indicators import add_indicators

from core.institutional_score import (
    generate_scores
)

from core.market_regime import (
    detect_market_regime
)

# =========================================================
# SAFE TRADE DECISION IMPORT
# =========================================================

try:

    from strategy.trade_decision_engine import (
        trade_decision
    )

except Exception:

    print(
        "WARNING: trade_decision_engine "
        "not found. Using fallback."
    )

    def trade_decision(row):

        try:

            if (
                row.get(
                    "institutional_score",
                    0
                ) >= 75
            ):

                return "BUY"

            elif (
                row.get(
                    "institutional_score",
                    0
                ) <= 30
            ):

                return "SELL"

            return "HOLD"

        except:

            return "HOLD"
