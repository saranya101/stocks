def make_decision(score):
    if score >= 50:
        return "BUY"

    elif score >= 20:
        return "WATCH"

    elif score >= 0:
        return "HOLD / WAIT"

    else:
        return "AVOID"