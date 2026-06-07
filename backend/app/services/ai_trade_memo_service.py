import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_ai_trade_memo(trade: dict):
    prompt = f"""
You are QuantOS, an institutional trading decision assistant.

Write a concise investment committee memo for this proposed trade.

Do not give financial advice.
Do not guarantee returns.
Use only the data provided.

Trade:
{trade}

Return exactly this structure:

SUMMARY:
BULL CASE:
BEAR CASE:
INVALIDATION:
APPROVAL VIEW:
"""

    try:
        res = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )

        return res.output_text.strip()

    except Exception as e:
        print("AI memo generation failed:", e)
        return None