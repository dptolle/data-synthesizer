"""Reading and writing CSV files (comma-separated, UTF-8 for now)."""

from pathlib import Path

import pandas as pd


def read_source(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8")


def write_synthetic(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, encoding="utf-8")
