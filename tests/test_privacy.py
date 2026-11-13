"""The overlap check, tested directly (the second agreed seam)."""

import pandas as pd

from csv_synth.privacy import check_overlap, describe

REAL = pd.DataFrame(
    {
        "contact": ["a@x.org", "b@x.org", "c@x.org", "d@x.org"],
        "full_name": ["Ann Lee", "Bob Ray", "Cy Dunn", "Di Fox"],
        "notes": ["alpha", "beta", "gamma", "delta"],
        "room": ["single", "double", "single", "suite"],
    }
)
TYPES = {"contact": "email", "full_name": "name", "notes": "text", "room": "category"}


def _synth(**changes):
    base = pd.DataFrame(
        {
            "contact": ["p@y.net", "q@y.net", "r@y.net"],
            "full_name": ["Xi One", "Yu Two", "Zo Three"],
            "notes": ["one", "two", "three"],
            "room": ["single", "double", "suite"],
        }
    )
    for col, values in changes.items():
        base[col] = values
    return base


def test_no_overlap_reports_nothing():
    assert check_overlap(REAL, _synth(), TYPES) == []


def test_shared_labels_in_category_column_are_allowed():
    # "room" is a category: shared labels may appear.
    assert check_overlap(REAL, _synth(room=["single", "single", "suite"]), TYPES) == []


def test_reports_exactly_the_columns_with_shared_personal_values():
    synth = _synth(contact=["a@x.org", "q@y.net", "r@y.net"], notes=["beta", "two", "three"])
    findings = check_overlap(REAL, synth, TYPES)

    assert sorted(f.column for f in findings if f.kind == "value") == ["contact", "notes"]
    assert [f.count for f in findings if f.column == "contact"] == [1]


def test_every_personal_type_is_checked():
    for ctype in ["email", "name", "address", "phone", "card", "id", "text"]:
        types = {**TYPES, "notes": ctype}
        findings = check_overlap(REAL, _synth(notes=["gamma", "x", "y"]), types)
        assert [f.column for f in findings] == ["notes"], ctype


def test_value_must_be_in_the_same_column():
    # A real email appearing in another column is not a finding for that column.
    synth = _synth(notes=["a@x.org", "x", "y"])
    assert check_overlap(REAL, synth, TYPES) == []


def test_whole_real_row_is_reported_even_without_types():
    synth = REAL.iloc[[1]].reset_index(drop=True)
    findings = check_overlap(REAL, synth, {})

    assert [(f.kind, f.count) for f in findings] == [("row", 1)]


def test_messages_name_columns_and_suggest_fix_but_never_show_values():
    synth = _synth(contact=["a@x.org", "b@x.org", "r@y.net"])
    text = "\n".join(describe(check_overlap(REAL, synth, TYPES)))

    assert "contact" in text
    assert "2" in text
    assert "Settings file" in text
    assert "a@x.org" not in text and "b@x.org" not in text


def test_row_message_never_shows_values():
    text = "\n".join(describe(check_overlap(REAL, REAL.iloc[[0]], {})))
    assert "row" in text
    assert "Ann Lee" not in text and "a@x.org" not in text
