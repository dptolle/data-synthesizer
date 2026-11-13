"""The rare-category merge also covers number-coded and true/false categories."""

import numpy as np
import pandas as pd


def _run(invoke, tmp_path, df, settings, rows):
    src = tmp_path / "s.csv"
    df.to_csv(src, index=False)
    (tmp_path / "s_settings.csv").write_text("column,type,action,format\n" + settings)
    out = tmp_path / "o.csv"
    result = invoke("generate", src, "--seed", 3, "--rows", rows, "-o", out)
    assert result.exit_code == 0, result.output
    return set(pd.read_csv(out, dtype=str).iloc[:, 1].dropna())


def test_rare_number_codes_are_merged(invoke, tmp_path):
    rng = np.random.default_rng(5)
    n = 200
    codes = list(rng.choice([1, 2, 3], n - 2)) + [987, 654]
    df = pd.DataFrame({"x": rng.normal(size=n), "grade": codes})
    shown = _run(invoke, tmp_path, df, "x,number,keep,\ngrade,category,keep,\n", 300)
    assert not shown & {"987", "654"}
    assert "Other" in shown


def test_rare_true_false_values_are_merged(invoke, tmp_path):
    rng = np.random.default_rng(6)
    n = 60
    df = pd.DataFrame({"x": rng.normal(size=n), "flag": [True] * (n - 2) + [False] * 2})
    shown = _run(invoke, tmp_path, df, "x,number,keep,\nflag,category,keep,\n", 100)
    assert "False" not in shown
