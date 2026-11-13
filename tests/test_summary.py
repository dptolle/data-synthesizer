"""What the end summary shows (quality score) and what the overlap check compares."""

import re

import pandas as pd


def test_summary_prints_one_quality_score_without_values(invoke, source_csv):
    result = invoke("generate", source_csv, "--seed", 1)

    assert result.exit_code == 0, result.output
    match = re.search(r"Quality score: (\d{1,3}(?:\.\d)?)%", result.output)
    assert match and 0 <= float(match.group(1)) <= 100
    assert "single" not in result.output


def test_row_overlap_is_checked_against_the_disguised_data(invoke, tmp_path):
    # Output labels are the stand-ins, so a copied row can only match the disguised data.
    src = tmp_path / "tiny.csv"
    pd.DataFrame({"room": ["single", "double"] * 6}).to_csv(src, index=False)

    result = invoke("generate", src, "--seed", 1, "--disguise-all")

    assert result.exit_code == 0, result.output
    assert "Warning" in result.output and "exact copies" in result.output
