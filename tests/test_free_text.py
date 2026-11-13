"""Free text is detected as `text` and replaced by fake sentences (ticket 05).

All data is made up with Faker.
"""

import importlib.util
import pathlib

import pandas as pd
import pytest
from faker import Faker

from csv_synth import privacy
from csv_synth.detect import detect_personal_columns

N = 150


@pytest.fixture
def notes_df():
    fake = Faker()
    Faker.seed(7)
    return pd.DataFrame(
        {
            "guest_notes": [f"{fake.sentence(nb_words=12)} Ref {i}" for i in range(N)],
            "room_type": ["single", "double", "suite"] * (N // 3),
            "nights": [(i % 7) + 1 for i in range(N)],
        }
    )


def _generate(invoke, df, tmp_path, *extra):
    src = tmp_path / "notes.csv"
    df.to_csv(src, index=False)
    result = invoke("generate", src, "--seed", 5, *extra)
    assert result.exit_code == 0, result.output
    return result, pd.read_csv(tmp_path / "notes_synthetic.csv", dtype=str)


def test_mostly_unique_text_is_detected_as_text(notes_df):
    assert detect_personal_columns(notes_df) == {"guest_notes": "text"}


def test_short_repeated_labels_are_not_text():
    df = pd.DataFrame({"room_type": ["single", "double"] * 50})
    assert detect_personal_columns(df) == {}


def test_unique_short_codes_are_not_text():
    df = pd.DataFrame({"code": [f"x{i}" for i in range(100)]})
    assert "code" not in detect_personal_columns(df)


def test_no_real_text_reaches_output(invoke, notes_df, tmp_path):
    _, out = _generate(invoke, notes_df, tmp_path)
    assert not set(notes_df["guest_notes"]) & set(out["guest_notes"].dropna())


def test_output_is_sentences_of_similar_length(invoke, notes_df, tmp_path):
    _, out = _generate(invoke, notes_df, tmp_path)
    real_len = notes_df["guest_notes"].str.len().mean()
    fake_len = out["guest_notes"].str.len().mean()
    assert 0.6 * real_len < fake_len < 1.4 * real_len
    assert out["guest_notes"].str.contains(" ").all()


def test_text_is_never_passed_to_sdv_as_categorical(invoke, notes_df, tmp_path, monkeypatch):
    from sdv.metadata import Metadata

    seen = {}
    real_detect = Metadata.detect_from_dataframes

    def spy(frames, *a, **k):
        seen["columns"] = list(frames["table"].columns)
        return real_detect(frames, *a, **k)

    monkeypatch.setattr(Metadata, "detect_from_dataframes", spy)
    _generate(invoke, notes_df, tmp_path)
    assert "guest_notes" not in seen["columns"]


def test_missing_text_values_do_not_break(invoke, notes_df, tmp_path):
    notes_df.loc[::5, "guest_notes"] = None
    _, out = _generate(invoke, notes_df, tmp_path)
    assert len(out) == N


def test_same_seed_gives_identical_text(invoke, notes_df, tmp_path):
    src = tmp_path / "notes.csv"
    notes_df.to_csv(src, index=False)
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    assert invoke("generate", src, "--seed", 3, "-o", a).exit_code == 0
    assert invoke("generate", src, "--seed", 3, "-o", b).exit_code == 0
    assert a.read_bytes() == b.read_bytes()


def test_overlap_check_covers_text_columns():
    real = pd.DataFrame({"notes": [f"a long free text number {i}" for i in range(30)]})
    findings = privacy.check_overlap(real, real.copy(), {"notes": "text"})
    assert [(f.kind, f.column) for f in findings if f.blocks] == [("value", "notes")]
    clean = pd.DataFrame({"notes": [f"other words {i}" for i in range(30)]})
    assert not [f for f in privacy.check_overlap(real, clean, {"notes": "text"}) if f.blocks]


def test_sample_csv_has_a_free_text_column():
    path = pathlib.Path(__file__).parent.parent / "scripts" / "make_sample_csv.py"
    spec = importlib.util.spec_from_file_location("make_sample_csv", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    df = mod.make_sample(200)
    assert detect_personal_columns(df)["guest_notes"] == "text"
