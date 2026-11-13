"""Label disguise (ticket 08). All data is made up."""

import numpy as np
import pandas as pd
import pytest

from csv_synth.privacy import disguise


def test_disguise_replaces_every_label_with_numbered_stand_ins():
    s = pd.Series(["Alpha"] * 6 + ["Beta"] * 3 + ["Gamma"] * 1, dtype=object)
    out = disguise(s, "room", np.random.default_rng(0))
    assert set(out) == {"room_1", "room_2", "room_3"}
    assert sorted(out.value_counts().tolist()) == [1, 3, 6]  # shares kept


def test_disguise_is_consistent_and_keeps_empty_cells():
    s = pd.Series(["a", "b", "a", None, "b", "a"], dtype=object)
    out = disguise(s, "c", np.random.default_rng(1))
    assert out[0] == out[2] == out[5] and out[1] == out[4] and out[0] != out[1]
    assert out.isna().sum() == 1 and pd.isna(out[3])


def test_stand_in_numbers_do_not_follow_sorted_label_order():
    labels = [f"L{i:02d}" for i in range(30)]
    s = pd.Series(labels, dtype=object)
    out = disguise(s, "c", np.random.default_rng(2))
    assert out.tolist() != [f"c_{i + 1}" for i in range(30)]


def test_numeric_and_category_dtype_columns_work_and_input_is_untouched():
    n = pd.Series([10, 20, 10, 30])
    assert set(disguise(n, "c", np.random.default_rng(3))) <= {"c_1", "c_2", "c_3"}
    c = pd.Series(["x", "y", "x"], dtype="category")
    assert set(disguise(c, "c", np.random.default_rng(3))) <= {"c_1", "c_2"}
    assert c.tolist() == ["x", "y", "x"]


# --- through the command line ------------------------------------------------

REAL = ["Penthouse-Zeta", "Cellar-Omega", "Garden-Sigma"]


@pytest.fixture
def hotel(tmp_path):
    rng = np.random.default_rng(5)
    n = 300
    df = pd.DataFrame(
        {
            "price": rng.normal(100, 10, n).round(2),
            "room": rng.choice(REAL, n, p=[0.6, 0.3, 0.1]),
            "view": rng.choice(["sea", "city"], n),
        }
    )
    path = tmp_path / "hotel.csv"
    df.to_csv(path, index=False)
    return path


def _set(settings, column, **changes):
    s = pd.read_csv(settings, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    for k, v in changes.items():
        s.loc[s["column"] == column, k] = v
    s.to_csv(settings, index=False, encoding="utf-8-sig")


def _run(invoke, hotel, *extra):
    out = hotel.with_name("out.csv")
    r = invoke("generate", hotel, "--seed", 1, "--rows", 1000, "-o", out, *extra)
    return r, out


def test_disguise_action_hides_labels_keeps_shares_and_lists_column(invoke, hotel):
    invoke("inspect", hotel)
    _set(hotel.with_name("hotel_settings.csv"), "room", action="disguise")
    r, out = _run(invoke, hotel)
    assert r.exit_code == 0, r.output
    synth = pd.read_csv(out)
    assert set(synth["room"]) <= {"room_1", "room_2", "room_3"}
    assert set(synth["view"]) <= {"sea", "city"}  # other columns untouched
    shares = sorted(synth["room"].value_counts(normalize=True).tolist())
    assert shares == pytest.approx([0.1, 0.3, 0.6], abs=0.08)
    line = [x for x in r.output.splitlines() if x.startswith("Disguised")]
    assert line and "room" in line[0]


def test_mapping_is_in_no_written_file(invoke, hotel):
    invoke("inspect", hotel)
    _set(hotel.with_name("hotel_settings.csv"), "room", action="disguise")
    r, out = _run(invoke, hotel)
    assert r.exit_code == 0, r.output
    for f in hotel.parent.iterdir():
        if f != hotel:  # the Source CSV legitimately holds the real labels
            text = f.read_text(encoding="utf-8-sig")
            assert not any(label in text for label in REAL), f.name
    assert not any(label in r.output for label in REAL)


def test_disguise_all_covers_every_category_column(invoke, hotel):
    r, out = _run(invoke, hotel, "--disguise-all")
    assert r.exit_code == 0, r.output
    synth = pd.read_csv(out)
    assert set(synth["room"]) <= {"room_1", "room_2", "room_3"}
    assert set(synth["view"]) <= {"view_1", "view_2"}
    assert synth["price"].dtype.kind == "f"


def test_rare_merge_runs_before_disguise(invoke, tmp_path):
    rng = np.random.default_rng(8)
    n = 200
    labels = list(rng.choice(["a", "b"], n - 2)) + ["rare1", "rare2"]
    p = tmp_path / "s.csv"
    pd.DataFrame({"x": rng.normal(size=n), "acct": labels}).to_csv(p, index=False)
    out = tmp_path / "o.csv"
    r = invoke("generate", p, "--seed", 1, "--rows", 500, "-o", out, "--disguise-all")
    assert r.exit_code == 0, r.output
    # 2 big labels + merged "Other" = 3 stand-ins, not 4
    assert set(pd.read_csv(out)["acct"]) <= {"acct_1", "acct_2", "acct_3"}


@pytest.mark.parametrize("column", ["price", "contact"])
def test_disguise_on_non_category_stops_with_message(invoke, hotel, column):
    df = pd.read_csv(hotel)
    df["contact"] = [f"zq{i}@example.org" for i in range(len(df))]
    df.to_csv(hotel, index=False)
    invoke("inspect", hotel)
    _set(hotel.with_name("hotel_settings.csv"), column, action="disguise")
    r, out = _run(invoke, hotel)
    assert r.exit_code != 0
    assert column in r.output and "disguise" in r.output and "category" in r.output
    assert not out.exists()


def test_disguise_all_skips_dropped_columns(invoke, hotel):
    invoke("inspect", hotel)
    _set(hotel.with_name("hotel_settings.csv"), "view", action="drop")
    r, out = _run(invoke, hotel, "--disguise-all")
    assert r.exit_code == 0, r.output
    assert "view" not in pd.read_csv(out).columns
