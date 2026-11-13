import numpy as np
import pandas as pd


def _write(tmp_path, df):
    p = tmp_path / "s.csv"
    df.to_csv(p, index=False)
    return p


def test_rare_categories_do_not_appear_in_output(invoke, tmp_path):
    rng = np.random.default_rng(1)
    n = 200
    labels = list(rng.choice(["a", "b"], n - 2)) + ["Acme Holdings Ltd", "Zed Corp"]
    src = _write(tmp_path, pd.DataFrame({"x": rng.normal(size=n), "account": labels}))
    out = tmp_path / "o.csv"
    assert invoke("generate", src, "--seed", 3, "--rows", 300, "-o", out).exit_code == 0
    synth = pd.read_csv(out)
    assert not set(synth["account"].dropna()) & {"Acme Holdings Ltd", "Zed Corp"}


def test_rare_threshold_option_changes_merge(invoke, tmp_path):
    rng = np.random.default_rng(2)
    n = 200
    labels = list(rng.choice(["a", "b"], n - 8)) + ["mid"] * 8
    src = _write(tmp_path, pd.DataFrame({"x": rng.normal(size=n), "account": labels}))
    out = tmp_path / "o.csv"
    args = ("generate", src, "--seed", 3, "--rows", 300, "-o", out)
    assert invoke(*args, "--rare-threshold", 10).exit_code == 0
    assert "mid" not in set(pd.read_csv(out)["account"])
    assert invoke(*args, "--rare-threshold", 5, "--force").exit_code == 0
    assert "mid" in set(pd.read_csv(out)["account"])


def test_real_min_and_max_are_not_reproduced(invoke, tmp_path):
    rng = np.random.default_rng(4)
    df = pd.DataFrame({"price": rng.normal(100, 20, 300).round(4)})
    src = _write(tmp_path, df)
    out = tmp_path / "o.csv"
    assert invoke("generate", src, "--seed", 5, "--rows", 2000, "-o", out).exit_code == 0
    synth = pd.read_csv(out)["price"]
    assert synth.min() != df["price"].min()
    assert synth.max() != df["price"].max()
    assert synth.min() < df["price"].min() or synth.max() > df["price"].max()
