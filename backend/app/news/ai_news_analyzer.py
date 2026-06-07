import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


EVENT_WEIGHTS = {
    "EARNINGS": 1.2,
    "GUIDANCE": 1.3,
    "ANALYST_RATING": 0.8,
    "LAWSUIT": 1.1,
    "REGULATION": 1.2,
    "POLICY": 1.35,
    "POLITICIAN_TRADE": 1.25,
    "TARIFF": 1.3,
    "PRODUCT": 0.8,
    "PARTNERSHIP": 0.8,
    "MACRO": 0.9,
    "SECTOR": 0.8,
    "M&A": 1.3,
    "MANAGEMENT": 0.9,
    "SEC_FILINGS": 1.1,
    "CONTRACT": 1.1,
    "NOISE": 0,
}


def safe_json_parse(content):
    try:
        return json.loads(content)
    except Exception:
        cleaned = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )
        return json.loads(cleaned)


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def analyze_article_with_ai(ticker, article):
    prompt = f"""
You are an elite hedge fund news analyst.

Analyze this article for ticker: {ticker}.

Your job:
Decide if this article contains a market-moving catalyst that could affect the stock.

Return ONLY valid JSON with this exact structure:

{{
  "relevance_score": 0,
  "sentiment": "NEUTRAL",
  "impact_score": 0,
  "confidence": 0,
  "event_type": "NOISE",
  "time_horizon": "NONE",
  "trade_relevance": "LOW",
  "reason": "short explanation"
}}

Allowed sentiment values:
BULLISH, BEARISH, NEUTRAL

Allowed event_type values:
EARNINGS, GUIDANCE, ANALYST_RATING, LAWSUIT, REGULATION, POLICY,
POLITICIAN_TRADE, TARIFF, PRODUCT, PARTNERSHIP, MACRO, SECTOR,
M&A, MANAGEMENT, SEC_FILINGS, CONTRACT, NOISE

Allowed time_horizon values:
INTRADAY, SHORT_TERM, MEDIUM_TERM, LONG_TERM, NONE

Allowed trade_relevance values:
HIGH, MEDIUM, LOW

Important catalyst rules:
- POLICY includes government policy, White House action, tariffs, export controls, subsidies, regulation, elections, defense/AI/crypto/energy policy.
- POLITICIAN_TRADE includes public disclosures of politicians buying/selling stocks, including Donald Trump, Congress members, or politically exposed figures.
- TARIFF includes tariff threats, tariff changes, China trade restrictions, import/export duties.
- SEC_FILINGS includes insider transactions, 13F, 8-K, 10-Q, 10-K, S-1, ownership changes.
- CONTRACT includes major government or enterprise deals.
- If article is not clearly about the company, sector, or catalyst affecting ticker, event_type must be NOISE.
- Be conservative. Do not overstate impact.
- impact_score must be from -50 to +50.
- relevance_score and confidence must be 0 to 100.

Article:
Title: {article.get("title")}
Description: {article.get("description")}
Source: {article.get("source")}
Published: {article.get("published_at")}
URL: {article.get("url")}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a conservative financial news analyst. Return only valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content
    result = safe_json_parse(content)

    event_type = result.get("event_type", "NOISE")
    impact_score = float(result.get("impact_score", 0))
    relevance_score = float(result.get("relevance_score", 0))
    confidence = float(result.get("confidence", 0))

    return {
        "relevance_score": clamp(relevance_score, 0, 100),
        "sentiment": result.get("sentiment", "NEUTRAL"),
        "impact_score": clamp(impact_score, -50, 50),
        "confidence": clamp(confidence, 0, 100),
        "event_type": event_type,
        "event_weight": EVENT_WEIGHTS.get(event_type, 1),
        "time_horizon": result.get("time_horizon", "NONE"),
        "trade_relevance": result.get("trade_relevance", "LOW"),
        "reason": result.get("reason", "No reason provided.")
    }


def get_news_label(score):
    if score >= 25:
        return "STRONG BULLISH CATALYST"
    elif score >= 12:
        return "BULLISH CATALYST"
    elif score <= -25:
        return "STRONG BEARISH CATALYST"
    elif score <= -12:
        return "BEARISH CATALYST"
    else:
        return "NEUTRAL NEWS"


def analyze_news_with_ai(
    ticker,
    articles,
    relevance_threshold=35,
    debug=False
):
    analyzed_articles = []
    total_score = 0
    confidence_sum = 0

    for article in articles:
        try:
            result = analyze_article_with_ai(ticker, article)

            if debug:
                print("\n====================")
                print("ARTICLE:", article.get("title"))
                print("AI RESULT:", result)

        except Exception as e:
            if debug:
                print("AI NEWS ERROR:", e)
            continue

        if result["relevance_score"] < relevance_threshold:
            continue

        if result["event_type"] == "NOISE":
            continue

        weighted_impact = (
            result["impact_score"]
            * (result["confidence"] / 100)
            * (result["relevance_score"] / 100)
            * result["event_weight"]
        )

        analyzed_article = {
            **article,
            "ai_relevance": result["relevance_score"],
            "ai_sentiment": result["sentiment"],
            "ai_impact_score": result["impact_score"],
            "ai_weighted_impact": round(weighted_impact, 2),
            "ai_confidence": result["confidence"],
            "event_type": result["event_type"],
            "event_weight": result["event_weight"],
            "time_horizon": result["time_horizon"],
            "trade_relevance": result["trade_relevance"],
            "ai_reason": result["reason"],
        }

        analyzed_articles.append(analyzed_article)

        total_score += weighted_impact
        confidence_sum += result["confidence"]

    total_score = round(clamp(total_score, -50, 50), 2)

    average_confidence = 0
    if analyzed_articles:
        average_confidence = round(confidence_sum / len(analyzed_articles), 2)

    analyzed_articles = sorted(
        analyzed_articles,
        key=lambda x: abs(x.get("ai_weighted_impact", 0)),
        reverse=True,
    )

    return {
        "news_score": total_score,
        "news_label": get_news_label(total_score),
        "news_confidence": average_confidence,
        "relevant_articles": analyzed_articles,
    }