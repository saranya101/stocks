BULLISH_WORDS = [
    "beats",
    "surges",
    "growth",
    "record",
    "profit",
    "upgrade",
    "bullish",
    "strong",
    "buyback",
    "expansion",
    "partnership"
]

BEARISH_WORDS = [
    "misses",
    "falls",
    "drops",
    "loss",
    "lawsuit",
    "downgrade",
    "bearish",
    "probe",
    "weak",
    "cuts",
    "warning",
    "layoffs"
]


def analyze_news_sentiment(articles):

    score = 0

    reasons = []

    for article in articles:

        text = (
            f"{article.get('title', '')} "
            f"{article.get('description', '')}"
        ).lower()

        bullish_hits = []

        bearish_hits = []

        for word in BULLISH_WORDS:

            if word in text:
                bullish_hits.append(word)

        for word in BEARISH_WORDS:

            if word in text:
                bearish_hits.append(word)

        if bullish_hits:

            score += len(bullish_hits) * 5

            reasons.append(
                f"Bullish keywords: {', '.join(bullish_hits)}"
            )

        if bearish_hits:

            score -= len(bearish_hits) * 5

            reasons.append(
                f"Bearish keywords: {', '.join(bearish_hits)}"
            )

    score = max(-50, min(50, score))

    if score > 15:
        label = "BULLISH NEWS"

    elif score < -15:
        label = "BEARISH NEWS"

    else:
        label = "NEUTRAL NEWS"

    return {
        "news_score": score,
        "news_label": label,
        "news_reasons": reasons
    }