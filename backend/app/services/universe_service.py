import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def get_sp500_tickers():
    file = BASE_DIR / "data" / "sp500.csv"

    df = pd.read_csv(file)

    return (
        df["Symbol"]
        .astype(str)
        .str.replace(".", "-", regex=False)
        .tolist()
    )


def get_nasdaq100_tickers():
    file = BASE_DIR / "data" / "nasdaq100.csv"

    df = pd.read_csv(file)

    return (
        df["Symbol"]
        .astype(str)
        .str.replace(".", "-", regex=False)
        .tolist()
    )