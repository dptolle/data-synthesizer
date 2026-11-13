import re

import numpy as np
import pandas as pd
import pytest
from typer.testing import CliRunner

from csv_synth.cli import app


@pytest.fixture
def runner():
    return CliRunner()


_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


class PlainResult:
    """A CLI result whose output has terminal colour codes removed.

    Typer forces coloured help when GITHUB_ACTIONS is set, which splits option
    names like `--fit-rows` with escape codes. Tests check what a user reads,
    so they look at the plain text.
    """

    def __init__(self, result):
        self._result = result

    def __getattr__(self, name):
        return getattr(self._result, name)

    @property
    def output(self):
        return _ANSI.sub("", self._result.output)


@pytest.fixture
def invoke(runner):
    def _invoke(*args):
        return PlainResult(runner.invoke(app, [str(a) for a in args]))

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
