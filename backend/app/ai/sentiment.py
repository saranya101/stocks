from openai import OpenAI
from dotenv import load_dotenv

import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def analyze_sentiment(article):

    prompt = f"""
    Analyze this financial news article.

    Return:
    - BULLISH
    - BEARISH
    - NEUTRAL

    Also explain briefly.

    Article:
    {article}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content