"""Privacy tests: personal columns are detected and faked (ticket 03).

All data here is made up with Faker; no real data is involved.
"""

import pandas as pd
import pytest
from faker import Faker

from csv_synth.detect import detect_personal_columns

N = 150
PERSONAL = ["email", "name", "address", "phone", "card", "booking_id"]


@pytest.fixture
def personal_df():
    fake = Faker()
    Faker.seed(123)
    return pd.DataFrame(
        {
            "email": [f"{i}.{fake.user_name()}@{fake.domain_name()}" for i in range(N)],
            "name": [f"{fake.first_name()} {fake.last_name()}{i}" for i in range(N)],
            "address": [f"{fake.street_address()} #{i}" for i in range(N)],
            "phone": [f"+49 170 {1000000 + i * 7}" for i in range(N)],
            "card": [fake.credit_card_number("visa16") for _ in range(N)],
            "booking_id": [f"BK-{i:05d}" for i in range(N)],
            "nights": [(i % 7) + 1 for i in range(N)],
        }
    )


def _generate(invoke, df, tmp_path, *extra):
    src = tmp_path / "people.csv"
    df.to_csv(src, index=False)
    result = invoke("generate", src, "--seed", 5, *extra)
    assert result.exit_code == 0, result.output
    out = pd.read_csv(tmp_path / "people_synthetic.csv", dtype=str)
    return result, out


def test_detects_every_personal_type(personal_df):
    found = detect_personal_columns(personal_df)
    assert found == {
        "email": "email",
        "name": "name",
        "address": "address",
        "phone": "phone",
        "card": "card",
        "booking_id": "id",
    }


def test_detection_uses_values_not_only_names():
    fake = Faker()
    df = pd.DataFrame(
        {
            "contact": [f"u{i}@{fake.domain_name()}" for i in range(50)],
            "reach": [f"+1 555 010 {i:04d}" for i in range(50)],
            "token": [fake.credit_card_number("visa16") for _ in range(50)],
            "room_type": ["single", "double"] * 25,
        }
    )
    assert detect_personal_columns(df) == {
        "contact": "email",
        "reach": "phone",
        "token": "card",
    }


def test_plain_columns_are_not_flagged():
    df = pd.DataFrame(
        {"price": [1.5, 2.5, 3.5] * 10, "room_type": ["a", "b", "c"] * 10}
    )
    assert detect_personal_columns(df) == {}


@pytest.mark.parametrize("col", PERSONAL)
def test_no_real_value_reaches_output(invoke, personal_df, tmp_path, col):
    _, out = _generate(invoke, personal_df, tmp_path)
    real_values = set(personal_df[col].astype(str))
    assert not real_values & set(out[col].dropna())


def test_misleading_column_name_still_faked(invoke, personal_df, tmp_path):
    df = personal_df.rename(columns={"email": "contact"})
    _, out = _generate(invoke, df, tmp_path)
    assert not set(df["contact"]) & set(out["contact"].dropna())
    assert out["contact"].str.contains("@").all()


def test_faked_values_have_matching_shape(invoke, personal_df, tmp_path):
    _, out = _generate(invoke, personal_df, tmp_path)
    assert out["email"].str.contains("@").all()
    assert out["booking_id"].str.fullmatch(r"BK-\d{5}").all()


def test_ids_stay_unique_when_source_ids_are_unique(invoke, personal_df, tmp_path):
    _, out = _generate(invoke, personal_df, tmp_path)
    assert out["booking_id"].is_unique


def test_numeric_ids_are_not_copied(invoke, tmp_path):
    df = pd.DataFrame({"customer_id": range(1000, 1000 + N), "x": range(N)})
    _, out = _generate(invoke, df, tmp_path)
    assert not set(map(str, df["customer_id"])) & set(out["customer_id"])


def test_missing_values_in_faked_column_do_not_break(invoke, personal_df, tmp_path):
    personal_df.loc[::4, "email"] = None
    _, out = _generate(invoke, personal_df, tmp_path)
    assert len(out) == N


def test_same_seed_still_identical_with_faked_columns(invoke, personal_df, tmp_path):
    src = tmp_path / "people.csv"
    personal_df.to_csv(src, index=False)
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    assert invoke("generate", src, "--seed", 3, "-o", a).exit_code == 0
    assert invoke("generate", src, "--seed", 3, "-o", b).exit_code == 0
    assert a.read_bytes() == b.read_bytes()


def test_summary_lists_faked_columns_by_name_only(invoke, personal_df, tmp_path):
    result, _ = _generate(invoke, personal_df, tmp_path)
    assert "faked" in result.output.lower()
    for col in PERSONAL:
        assert col in result.output
        for v in personal_df[col].head(20).astype(str):
            assert v not in result.output


def test_rare_merge_applies_only_to_category_columns(invoke, personal_df, tmp_path, monkeypatch):
    from csv_synth import privacy

    seen = []
    real_merge = privacy.merge_rare

    def spy(series, *a, **k):
        seen.append(series.name)
        return real_merge(series, *a, **k)

    monkeypatch.setattr(privacy, "merge_rare", spy)
    personal_df["room_type"] = ["single", "double", "suite"] * (N // 3)
    _generate(invoke, personal_df, tmp_path)
    assert seen == ["room_type"]
