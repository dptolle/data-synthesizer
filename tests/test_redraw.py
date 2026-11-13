"""Fake values that match a real value by chance are redrawn (owner decision).

All data is made up. To make chance matches likely, Faker is limited to a small
pool of common names, and four of them are the "real" names.
"""

import faker.providers.person
import pandas as pd
import pytest

POOL = [f"Common{i} Person" for i in range(12)]
REAL = POOL[:4]
N = 60


@pytest.fixture(autouse=True)
def small_name_pool(monkeypatch):
    monkeypatch.setattr(
        faker.providers.person.Provider, "name", lambda self: self.random_element(POOL)
    )


def _run(invoke, tmp_path, out_name, *extra):
    src = tmp_path / "people.csv"
    pd.DataFrame({"full_name": (REAL * N)[:N], "n": range(N)}).to_csv(src, index=False)
    out = tmp_path / out_name
    result = invoke("generate", src, "--seed", 5, "--rows", N, "--force", "-o", out, *extra)
    return result, out


def test_chance_matches_are_redrawn_so_no_real_value_reaches_the_output(invoke, tmp_path):
    result, out = _run(invoke, tmp_path, "o.csv")

    assert result.exit_code == 0, result.output
    names = set(pd.read_csv(out, dtype=str)["full_name"])
    assert names and names <= set(POOL)
    assert not names & set(REAL)


def test_redraw_keeps_the_output_repeatable(invoke, tmp_path):
    _, a = _run(invoke, tmp_path, "a.csv")
    _, b = _run(invoke, tmp_path, "b.csv")
    assert a.read_bytes() == b.read_bytes()
