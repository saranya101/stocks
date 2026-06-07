import pandas as pd
from pathlib import Path
from fastapi import APIRouter

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

UNIVERSE_FILES = {
    "us_largecap": "us_largecap.csv",
    "sp500": "us_largecap.csv",
    "nasdaq100": "nasdaq100.csv",
    "sti30": "sti30.csv",
}


def load_universe(filename: str):
    file_path = DATA_DIR / filename

    if not file_path.exists():
        return []

    df = pd.read_csv(file_path)

    return (
        df["Symbol"]
        .astype(str)
        .str.strip()
        .tolist()
    )


@router.get("/universe")
def get_universe(universe: str = "us_largecap", limit: int = 50):
    filename = UNIVERSE_FILES.get(universe)

    if not filename:
        return {
            "universe": universe,
            "limit": limit,
            "count": 0,
            "tickers": [],
        }

    tickers = load_universe(filename)[:limit]

    return {
        "universe": universe,
        "limit": limit,
        "count": len(tickers),
        "tickers": tickers,
    }