import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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


def analyze_article_with_ai(ticker, article):
    prompt = f"""
You are an elite hedge fund news analyst.

Analyze this article for ticker: {ticker}.

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

Allowed event_type values:
EARNINGS, GUIDANCE, ANALYST_RATING, LAWSUIT, REGULATION, PRODUCT,
PARTNERSHIP, MACRO, SECTOR, M&A, MANAGEMENT, SEC_FILINGS, NOISE

Allowed time_horizon values:
INTRADAY, SHORT_TERM, MEDIUM_TERM, LONG_TERM, NONE

Allowed trade_relevance values:
HIGH, MEDIUM, LOW

Rules:
- If article is not clearly about the company/stock, event_type must be NOISE.
- Be conservative.
- Do not overstate impact.
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

    return {
        "relevance_score": float(result.get("relevance_score", 0)),
        "sentiment": result.get("sentiment", "NEUTRAL"),
        "impact_score": float(result.get("impact_score", 0)),
        "confidence": float(result.get("confidence", 0)),
        "event_type": result.get("event_type", "NOISE"),
        "time_horizon": result.get("time_horizon", "NONE"),
        "trade_relevance": result.get("trade_relevance", "LOW"),
        "reason": result.get("reason", "No reason provided.")
    }


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

        analyzed_article = {
            **article,
            "ai_relevance": result["relevance_score"],
            "ai_sentiment": result["sentiment"],
            "ai_impact_score": result["impact_score"],
            "ai_confidence": result["confidence"],
            "event_type": result["event_type"],
            "time_horizon": result["time_horizon"],
            "trade_relevance": result["trade_relevance"],
            "ai_reason": result["reason"]
        }

        analyzed_articles.append(analyzed_article)

        weighted_impact = (
            result["impact_score"]
            * (result["confidence"] / 100)
            * (result["relevance_score"] / 100)
        )

        total_score += weighted_impact
        confidence_sum += result["confidence"]

    total_score = round(max(-50, min(50, total_score)), 2)

    average_confidence = 0
    if len(analyzed_articles) > 0:
        average_confidence = round(
            confidence_sum / len(analyzed_articles),
            2
        )

    if total_score >= 15:
        label = "BULLISH NEWS"
    elif total_score <= -15:
        label = "BEARISH NEWS"
    else:
        label = "NEUTRAL NEWS"

    return {
        "news_score": total_score,
        "news_label": label,
        "news_confidence": average_confidence,
        "relevant_articles": analyzed_articles
    }