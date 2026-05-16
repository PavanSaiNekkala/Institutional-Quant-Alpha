# =========================================================
# TRADE DECISION ENGINE
# =========================================================

def trade_decision(row):

    try:

        # =====================================================
        # SCORES
        # =====================================================

        institutional_score = float(
            row.get("institutional_score", 0)
        )

        smart_money_score = float(
            row.get("smart_money_score", 0)
        )

        breakout_score = float(
            row.get("breakout_score", 0)
        )

        final_score = float(
            row.get("FINAL_SCORE", 0)
        )

        # =====================================================
        # PRICE DATA
        # =====================================================

        cmp_price = float(
            row.get("CMP", 0)
        )

        atr = float(
            row.get("ATR_14", 0)
        )

        # =====================================================
        # FALLBACK ATR
        # =====================================================

        if atr <= 0:

            atr = cmp_price * 0.025

        # =====================================================
        # MARKET REGIME
        # =====================================================

        market_regime = row.get(
            "MARKET_REGIME",
            "SIDEWAYS"
        )

        regime_multiplier_map = {

            "BULL": 1.4,
            "SIDEWAYS": 1.0,
            "BEAR": 0.7

        }

        regime_multiplier = regime_multiplier_map.get(
            market_regime,
            1.0
        )

        # =====================================================
        # SCORE MULTIPLIER
        # =====================================================

        if final_score >= 90:

            score_multiplier = 2.2

        elif final_score >= 80:

            score_multiplier = 1.8

        elif final_score >= 70:

            score_multiplier = 1.5

        elif final_score >= 60:

            score_multiplier = 1.2

        else:

            score_multiplier = 1.0

        # =====================================================
        # STOP LOSS
        # =====================================================

        stop_loss = round(

            cmp_price - (atr * 2),

            2

        )

        # =====================================================
        # TARGET
        # =====================================================

        target = round(

            cmp_price +

            (

                atr *

                3 *

                score_multiplier *

                regime_multiplier

            ),

            2

        )

        # =====================================================
        # EXPECTED DAILY MOVE
        # =====================================================

        expected_daily_move = atr * 0.60

        # =====================================================
        # ESTIMATED DAYS
        # =====================================================

        estimated_days = round(

            max(

                1,

                (

                    target - cmp_price

                ) /

                max(expected_daily_move, 1)

            )

        )

        # =====================================================
        # RISK REWARD
        # =====================================================

        risk = max(

            cmp_price - stop_loss,

            1

        )

        reward = max(

            target - cmp_price,

            0

        )

        rr_ratio = round(

            reward / risk,

            2

        )

        # =====================================================
        # TRADE QUALITY
        # =====================================================

        if rr_ratio >= 3:

            trade_quality = "EXCELLENT"

        elif rr_ratio >= 2:

            trade_quality = "STRONG"

        elif rr_ratio >= 1:

            trade_quality = "MODERATE"

        else:

            trade_quality = "WEAK"

        # =====================================================
        # TRADE SIGNAL
        # =====================================================

        if (

            institutional_score >= 75

            and smart_money_score >= 70

            and breakout_score >= 80

            and rr_ratio >= 2

        ):

            signal = "STRONG_BUY"

        elif (

            institutional_score >= 60

            and rr_ratio >= 1.5

        ):

            signal = "BUY"

        elif institutional_score <= 30:

            signal = "SELL"

        else:

            signal = "HOLD"

        # =====================================================
        # RETURN
        # =====================================================

        return {

            "TRADE_SIGNAL": signal,

            "STOP_LOSS": stop_loss,

            "TARGET": target,

            "RR_RATIO": rr_ratio,

            "ESTIMATED_DAYS": estimated_days,

            "TRADE_QUALITY": trade_quality

        }

    except Exception:

        return {

            "TRADE_SIGNAL": "HOLD",

            "STOP_LOSS": 0,

            "TARGET": 0,

            "RR_RATIO": 0,

            "ESTIMATED_DAYS": 0,

            "TRADE_QUALITY": "UNKNOWN"

        }
