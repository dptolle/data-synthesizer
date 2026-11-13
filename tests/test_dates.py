"""Dates: detected, format guessed, kept in the output (ticket 10). All data is made up."""

import numpy as np
import pandas as pd
import pytest

FORMATS = ["%d.%m.%Y", "%Y-%m-%d", "%m/%d/%Y"]


def _source(tmp_path, fmt, name="stays.csv", mixed=False, n=150):
    rng = np.random.default_rng(5)
    start = pd.Timestamp("2023-06-01") + pd.to_timedelta(rng.normal(0, 120, n).round().astype(int), unit="D")
    out = start + pd.to_timedelta(rng.integers(1, 10, n), unit="D")
    df = pd.DataFrame(
        {
            "checkin": start.strftime(fmt),
            "checkout": out.strftime(fmt),
            "nights": rng.integers(1, 10, n),
        }
    )
    if mixed:
        df.loc[0, "checkin"] = "2023-05-17"
        df.loc[1, "checkin"] = "17.05.2023"
    df.loc[::5, "checkout"] = np.nan
    path = tmp_path / name
    df.to_csv(path, index=False)
    return path


def _settings(path):
    return pd.read_csv(
        path.with_name(f"{path.stem}_settings.csv"), dtype=str, keep_default_na=False,
        encoding="utf-8-sig",
    ).set_index("column")


@pytest.mark.parametrize("fmt", FORMATS)
def test_inspect_detects_date_columns_and_their_format(invoke, tmp_path, fmt):
    src = _source(tmp_path, fmt)

    result = invoke("inspect", src)

    assert result.exit_code == 0, result.output
    s = _settings(src)
    assert s.loc["checkin", "type"] == "date" and s.loc["checkin", "format"] == fmt
    assert s.loc["checkout", "type"] == "date" and s.loc["checkout", "format"] == fmt
    assert s.loc["nights", "type"] == "number" and s.loc["nights", "format"] == ""


@pytest.mark.parametrize("fmt", FORMATS)
def test_generate_writes_dates_in_the_source_format(invoke, tmp_path, fmt):
    src = _source(tmp_path, fmt)
    out = tmp_path / "out.csv"

    result = invoke("generate", src, "-o", out, "--seed", "1")

    assert result.exit_code == 0, result.output
    got = pd.read_csv(out, dtype=str)
    for col in ("checkin", "checkout"):
        values = got[col].dropna()
        assert len(values) > 100
        parsed = pd.to_datetime(values, format=fmt, errors="coerce")
        assert parsed.notna().all()
    assert got["checkout"].isna().any()  # the missing date is kept as missing


def test_real_extreme_dates_are_not_reproduced_exactly(invoke, tmp_path):
    src = _source(tmp_path, "%Y-%m-%d")
    out = tmp_path / "out.csv"
    assert invoke("generate", src, "-o", out, "--seed", "1").exit_code == 0

    real = pd.to_datetime(pd.read_csv(src)["checkin"])
    synth = pd.to_datetime(pd.read_csv(out)["checkin"])
    assert synth.min() != real.min() or synth.max() != real.max()


def test_format_corrected_in_settings_file_is_used(invoke, tmp_path):
    # Day-first dates: the guess is month first (US); the owner corrects it.
    src = tmp_path / "d.csv"
    days = pd.Timestamp("2023-01-01") + pd.to_timedelta(np.arange(60), unit="D")
    pd.DataFrame({"day": days.strftime("%d/%m/%Y"), "n": range(60)}).to_csv(src, index=False)
    # Every day is 12 or less would be ambiguous; here some are above 12, so the
    # day-first format is the only one that fits and is guessed directly.
    assert invoke("inspect", src).exit_code == 0
    assert _settings(src).loc["day", "format"] == "%d/%m/%Y"

    # Ambiguous file (all days <= 12): guess is month first, owner corrects it.
    amb = tmp_path / "amb.csv"
    pd.DataFrame(
        {"day": [f"{d:02d}/{m:02d}/2023" for d in range(1, 13) for m in (1, 2, 3)]}
    ).to_csv(amb, index=False)
    assert invoke("inspect", amb).exit_code == 0
    path = amb.with_name("amb_settings.csv")
    text = path.read_text("utf-8-sig")
    assert "day,date,keep,%m/%d/%Y" in text
    path.write_text(text.replace("%m/%d/%Y", "%d/%m/%Y"), encoding="utf-8-sig")
    out = tmp_path / "out.csv"

    result = invoke("generate", amb, "-o", out, "--seed", "1")

    assert result.exit_code == 0, result.output
    got = pd.read_csv(out, dtype=str)["day"].dropna()
    assert pd.to_datetime(got, format="%d/%m/%Y", errors="coerce").notna().all()


def test_mixed_date_styles_stop_and_name_the_settings_file(invoke, tmp_path):
    src = _source(tmp_path, "%Y-%m-%d", mixed=True)
    out = tmp_path / "out.csv"

    result = invoke("generate", src, "-o", out, "--seed", "1")

    assert result.exit_code != 0
    assert "checkin" in result.output and "format" in result.output.lower()
    assert "Settings file" in result.output
    assert not out.exists()
    # The settings file is saved so the format can be set there.
    s = _settings(src)
    assert s.loc["checkin", "type"] == "date" and s.loc["checkin", "format"] == ""


def test_a_format_that_does_not_fit_the_values_stops(invoke, tmp_path):
    src = _source(tmp_path, "%Y-%m-%d", mixed=True)
    invoke("generate", src, "-o", tmp_path / "o.csv", "--seed", "1")
    path = src.with_name("stays_settings.csv")
    path.write_text(
        path.read_text("utf-8-sig").replace("checkin,date,keep,", "checkin,date,keep,%Y-%m-%d"),
        encoding="utf-8-sig",
    )

    result = invoke("generate", src, "-o", tmp_path / "o.csv", "--seed", "1")

    assert result.exit_code != 0
    assert "checkin" in result.output and "%Y-%m-%d" in result.output


def _ambiguous(tmp_path):
    amb = tmp_path / "amb.csv"
    pd.DataFrame(
        {"day": [f"{d:02d}/{m:02d}/2023" for d in range(1, 13) for m in (1, 2, 3)]}
    ).to_csv(amb, index=False)
    return amb


def test_inspect_warns_about_ambiguous_slash_dates(invoke, tmp_path):
    amb = _ambiguous(tmp_path)
    result = invoke("inspect", amb)
    assert result.exit_code == 0, result.output
    assert "Warning" in result.output and "day" in result.output
    assert "amb_settings.csv" in result.output and "%m/%d/%Y" in result.output
    assert "01/02/2023" not in result.output


def test_generate_warns_about_ambiguous_dates_only_when_the_format_was_guessed(invoke, tmp_path):
    amb = _ambiguous(tmp_path)
    first = invoke("generate", amb, "-o", tmp_path / "o1.csv", "--seed", "1")
    assert first.exit_code == 0, first.output
    assert "Warning" in first.output and "`day`" in first.output
    assert "amb_settings.csv" in first.output

    second = invoke("generate", amb, "-o", tmp_path / "o2.csv", "--seed", "1")
    assert second.exit_code == 0, second.output
    assert "month first" not in second.output


def test_unambiguous_dates_give_no_ambiguity_warning(invoke, tmp_path):
    src = _source(tmp_path, "%d/%m/%Y")  # days above 12 occur, only day first fits
    result = invoke("inspect", src)
    assert "month first" not in result.output


def test_inspect_warns_about_mixed_date_styles(invoke, tmp_path):
    src = _source(tmp_path, "%Y-%m-%d", mixed=True)
    result = invoke("inspect", src)
    assert result.exit_code == 0, result.output
    assert "Warning" in result.output and "`checkin`" in result.output
    assert "mix" in result.output and "stays_settings.csv" in result.output
