from app.services.market_monitor import (
    run_market_monitor
)

def to_float(value):
    if hasattr(value, "iloc"):
        return float(value.iloc[0])

    if hasattr(value, "item"):
        return float(value.item())

    return float(value)

run_market_monitor()