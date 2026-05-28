from datetime import datetime
import pytz


US_MARKET_TZ = pytz.timezone(
    "US/Eastern"
)


def get_market_state():

    now = datetime.now(
        US_MARKET_TZ
    )

    hour = now.hour
    minute = now.minute

    current_time = (
        hour * 60 + minute
    )

    market_open = 9 * 60 + 30
    market_close = 16 * 60

    premarket = 4 * 60
    afterhours = 20 * 60

    if market_open <= current_time < market_close:

        session = "MARKET_OPEN"

    elif premarket <= current_time < market_open:

        session = "PREMARKET"

    elif market_close <= current_time < afterhours:

        session = "AFTER_HOURS"

    else:

        session = "MARKET_CLOSED"

    return {
        "session": session,
        "timestamp": now.isoformat()
    }