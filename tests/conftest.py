import numpy as np
import pandas as pd
import pytest
from typer.testing import CliRunner

from csv_synth.cli import app


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def invoke(runner):
    def _invoke(*args):
        return runner.invoke(app, [str(a) for a in args])

    return _invoke


@pytest.fixture
def source_csv(tmp_path):
    """A small fake Source CSV: numbers, a category, and missing values."""
    rng = np.random.default_rng(0)
    n = 120
    df = pd.DataFrame(
        {
            "nights": rng.integers(1, 10, n),
            "price": rng.normal(150, 30, n).round(2),
            "room_type": rng.choice(["single", "double", "suite"], n),
            "rating": rng.normal(4, 0.5, n).round(1),
        }
    )
    df.loc[rng.choice(n, 30, replace=False), "rating"] = np.nan
    df["empty_col"] = np.nan
    path = tmp_path / "hotel.csv"
    df.to_csv(path, index=False)
    return path
