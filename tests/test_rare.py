import numpy as np
import pandas as pd

from csv_synth.privacy import merge_rare


def make(counts, nulls=0):
    values = [label for label, n in counts.items() for _ in range(n)]
    return pd.Series(values + [np.nan] * nulls, dtype=object)


def test_labels_under_threshold_become_other():
    out = merge_rare(make({"big": 10, "four": 4, "five": 5, "one": 1}), 5)
    assert out.value_counts().to_dict() == {"big": 10, "five": 5, "Other": 5}


def test_empty_values_are_not_counted_or_merged():
    out = merge_rare(make({"big": 10, "tiny": 1}, nulls=3), 5)
    assert out.isna().sum() == 3
    assert (out == "Other").sum() == 1


def test_existing_other_gets_an_unused_name_for_merged_rows():
    out = merge_rare(make({"big": 10, "Other": 8, "tiny": 1}), 5)
    assert (out == "Other").sum() == 8
    assert out.value_counts().to_dict()["Other_2"] == 1
    out = merge_rare(make({"big": 10, "Other": 8, "Other_2": 6, "tiny": 1}), 5)
    assert out.value_counts().to_dict()["Other_3"] == 1


def test_category_dtype_works():
    s = make({"big": 10, "tiny": 1}, nulls=2).astype("category")
    out = merge_rare(s, 5)
    assert (out == "Other").sum() == 1
    assert out.isna().sum() == 2


def test_all_rare_becomes_single_label_without_crash():
    out = merge_rare(make({"a": 1, "b": 2, "c": 1}), 5)
    assert out.unique().tolist() == ["Other"]


def test_single_value_column_keeps_its_value():
    out = merge_rare(make({"only": 2}), 5)
    assert out.unique().tolist() == ["only"]


def test_does_not_modify_input():
    s = make({"big": 10, "tiny": 1})
    merge_rare(s, 5)
    assert "tiny" in set(s)
