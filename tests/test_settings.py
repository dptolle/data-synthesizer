"""Settings file workflow (ticket 07). All data is made up."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def people(tmp_path):
    rng = np.random.default_rng(7)
    n = 120
    df = pd.DataFrame(
        {
            "contact": [f"zq{i}@example.org" for i in range(n)],
            "room": rng.choice(["single", "double"], n),
            "price": rng.normal(100, 10, n).round(2),
            "secretnote": [f"MARKER-{i}-xyz" for i in range(n)],
        }
    )
    path = tmp_path / "people.csv"
    df.to_csv(path, index=False)
    return path


def _settings(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def _edit(path, column, **changes):
    s = _settings(path)
    for key, value in changes.items():
        s.loc[s["column"] == column, key] = value
    s.to_csv(path, index=False, encoding="utf-8-sig")


def test_inspect_writes_settings_next_to_input(invoke, people):
    result = invoke("inspect", people)
    assert result.exit_code == 0, result.output
    s = _settings(people.with_name("people_settings.csv"))
    assert list(s.columns) == ["column", "type", "action", "format"]
    assert list(s["column"]) == ["contact", "room", "price", "secretnote"]
    by = dict(zip(s["column"], s["type"]))
    assert by["contact"] == "email"
    assert by["room"] == "category"
    assert by["price"] == "number"
    assert set(s["action"]) == {"keep"}
    assert set(s["format"]) == {""}


def test_inspect_settings_option_and_no_overwrite(invoke, people, tmp_path):
    target = tmp_path / "mine.csv"
    assert invoke("inspect", people, "--settings", target).exit_code == 0
    assert target.exists()
    again = invoke("inspect", people, "--settings", target)
    assert again.exit_code != 0 and "--force" in again.output
    assert invoke("inspect", people, "--settings", target, "--force").exit_code == 0


def test_settings_file_has_no_data_values(invoke, people):
    invoke("inspect", people)
    text = people.with_name("people_settings.csv").read_text(encoding="utf-8-sig")
    assert "MARKER" not in text and "zq0@" not in text and "single" not in text


def test_generate_writes_settings_when_missing(invoke, people):
    assert invoke("generate", people, "--seed", 1).exit_code == 0
    assert people.with_name("people_settings.csv").exists()


def test_generate_with_settings_option_writes_there(invoke, people, tmp_path):
    target = tmp_path / "custom.csv"
    assert invoke("generate", people, "--seed", 1, "--settings", target).exit_code == 0
    assert target.exists()
    assert not people.with_name("people_settings.csv").exists()


def test_existing_settings_never_overwritten_even_with_force(invoke, people):
    invoke("inspect", people)
    path = people.with_name("people_settings.csv")
    _edit(path, "secretnote", action="drop")
    before = path.read_bytes()
    r = invoke("generate", people, "--seed", 1, "--force")
    assert r.exit_code == 0, r.output
    assert path.read_bytes() == before


def test_drop_removes_column_and_summary_lists_it(invoke, people):
    invoke("inspect", people)
    _edit(people.with_name("people_settings.csv"), "secretnote", action="drop")
    r = invoke("generate", people, "--seed", 1)
    assert r.exit_code == 0, r.output
    out = pd.read_csv(people.with_name("people_synthetic.csv"))
    assert "secretnote" not in out.columns
    assert "Dropped: secretnote" in r.output


def test_correcting_type_changes_synthesis(invoke, people):
    invoke("inspect", people)
    _edit(people.with_name("people_settings.csv"), "room", type="email")
    r = invoke("generate", people, "--seed", 1)
    assert r.exit_code == 0, r.output
    out = pd.read_csv(people.with_name("people_synthetic.csv"))
    assert out["room"].str.contains("@").all()


def test_mismatched_columns_stop_and_list_differences(invoke, people):
    invoke("inspect", people)
    df = pd.read_csv(people).rename(columns={"price": "cost"})
    df.to_csv(people, index=False)
    r = invoke("generate", people, "--seed", 1)
    assert r.exit_code != 0
    assert "price" in r.output and "cost" in r.output
    assert not people.with_name("people_synthetic.csv").exists()


@pytest.mark.parametrize(
    "field,value",
    [("type", "colour"), ("action", "burn"), ("action", "disguise")],
)
def test_invalid_settings_stop_with_message(invoke, people, field, value):
    invoke("inspect", people)
    _edit(people.with_name("people_settings.csv"), "contact", **{field: value})
    r = invoke("generate", people, "--seed", 1)
    assert r.exit_code != 0
    assert value in r.output and "contact" in r.output
    assert not people.with_name("people_synthetic.csv").exists()


@pytest.mark.parametrize(
    "kind", ["name", "address", "phone", "card", "id", "text", "date", "number", "category"]
)
def test_every_listed_type_is_accepted(invoke, people, kind):
    invoke("inspect", people)
    column = "price" if kind in ("date", "number") else "secretnote"
    _edit(people.with_name("people_settings.csv"), column, type=kind)
    r = invoke("generate", people, "--seed", 1)
    assert "not a valid type" not in r.output
    assert r.exit_code == 0, r.output


def test_number_type_on_text_column_stops(invoke, people):
    invoke("inspect", people)
    _edit(people.with_name("people_settings.csv"), "secretnote", type="number")
    r = invoke("generate", people, "--seed", 1)
    assert r.exit_code != 0 and "secretnote" in r.output
