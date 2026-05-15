# =========================================================
# TRADE DECISION ENGINE
# =========================================================

def trade_decision(row):

    try:

        institutional_score = row.get(
            "institutional_score",
            0
        )

        smart_money_score = row.get(
            "smart_money_score",
            0
        )

        breakout_score = row.get(
            "breakout_score",
            0
        )

        if (
            institutional_score >= 75
            and smart_money_score >= 70
            and breakout_score >= 80
        ):

            return "STRONG_BUY"

        elif institutional_score >= 60:

            return "BUY"

        elif institutional_score <= 30:

            return "SELL"

        return "HOLD"

    except Exception:

        return "HOLD"
