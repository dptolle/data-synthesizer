"""Messy CSV formats through the command line (ticket 09). All data is made up."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def messy(tmp_path):
    rng = np.random.default_rng(3)
    n = 120
    df = pd.DataFrame(
        {
            "größe": rng.normal(10, 2, n).round(2),
            "Café": rng.choice(["Müller", "Strauß", "Crème"], n),
            "n": rng.integers(1, 9, n),
        }
    )
    path = tmp_path / "messy.csv"
    df.to_csv(path, index=False, sep=";", decimal=",", encoding="cp1252")
    return path


def _people(tmp_path):
    src = tmp_path / "people.csv"
    pd.DataFrame(
        {"email": [f"user{i}@example.org" for i in range(20)], "n": range(20)}
    ).to_csv(src, index=False)
    return src


def test_inspect_prints_format_and_writes_bom_settings_with_source_separator(invoke, messy):
    result = invoke("inspect", messy)

    assert result.exit_code == 0, result.output
    assert "cp1252" in result.output
    assert "';'" in result.output and "','" in result.output
    raw = messy.with_name("messy_settings.csv").read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    assert text.splitlines()[0] == "column;type;action;format"
    assert "größe;number" in text and "Café;category" in text


def test_inspect_overrides_are_accepted(invoke, messy):
    result = invoke("inspect", messy, "--delimiter", ";", "--encoding", "cp1252", "--decimal", ",")

    assert result.exit_code == 0, result.output
    assert "größe;number" in messy.with_name("messy_settings.csv").read_text("utf-8-sig")


def test_wrong_encoding_override_gives_a_clear_error(invoke, messy):
    result = invoke("inspect", messy, "--encoding", "utf-8")

    assert result.exit_code != 0
    assert "--encoding" in result.output


def test_unknown_encoding_and_bad_delimiter_are_rejected(invoke, messy):
    assert invoke("inspect", messy, "--encoding", "nope-9").exit_code != 0
    assert invoke("inspect", messy, "--delimiter", ";;").exit_code != 0
    assert invoke("inspect", messy, "--decimal", ";").exit_code != 0


def test_generate_output_matches_source_format(invoke, messy):
    result = invoke("generate", messy, "--seed", 1)

    assert result.exit_code == 0, result.output
    out = messy.with_name("messy_synthetic.csv")
    raw = out.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert raw.decode("cp1252").splitlines()[0] == "größe;Café;n"
    synth = pd.read_csv(out, sep=";", decimal=",", encoding="cp1252")
    assert set(synth["Café"]) <= {"Müller", "Strauß", "Crème"}
    assert synth["größe"].dtype.kind == "f"
    assert messy.with_name("messy_settings.csv").read_bytes().startswith(b"\xef\xbb\xbf")


def test_generate_reads_an_edited_semicolon_settings_file(invoke, messy):
    invoke("inspect", messy)
    s = messy.with_name("messy_settings.csv")
    s.write_text(
        s.read_text("utf-8-sig").replace("Café;category;keep;", "Café;category;drop;"),
        encoding="utf-8-sig",
    )

    result = invoke("generate", messy, "--seed", 1)

    assert result.exit_code == 0, result.output
    header = messy.with_name("messy_synthetic.csv").read_bytes().decode("cp1252").splitlines()[0]
    assert header == "größe;n"


def test_privacy_failure_still_writes_settings_but_no_synthetic(invoke, tmp_path, monkeypatch):
    import csv_synth.synth

    src = _people(tmp_path)
    monkeypatch.setattr(csv_synth.synth, "synthesize", lambda real, rows, seed, *a: real.copy())

    result = invoke("generate", src)

    assert result.exit_code != 0
    assert not (tmp_path / "people_synthetic.csv").exists()
    assert (tmp_path / "people_settings.csv").exists()
    assert "people_settings.csv" in result.output


def test_privacy_failure_does_not_overwrite_a_settings_file_that_was_read(
    invoke, tmp_path, monkeypatch
):
    import csv_synth.synth

    src = _people(tmp_path)
    invoke("inspect", src)
    s = tmp_path / "people_settings.csv"
    before = s.read_bytes()
    monkeypatch.setattr(csv_synth.synth, "synthesize", lambda real, rows, seed, *a: real.copy())

    result = invoke("generate", src)

    assert result.exit_code != 0
    assert s.read_bytes() == before


def test_write_synthetic_replaces_and_counts_unencodable_characters(tmp_path):
    from csv_synth.csvio import CsvFormat, write_synthetic

    df = pd.DataFrame({"a": ["ł", "ok", "łł"], "b": [1, 2, 3]})
    path = tmp_path / "o.csv"
    count = write_synthetic(df, path, CsvFormat(",", "cp1252", "."))
    assert count == 3
    assert path.read_bytes().decode("cp1252").splitlines()[1] == "?,1"
    assert write_synthetic(df[["b"]], path, CsvFormat()) == 0


def test_generate_warns_with_a_count_but_no_values_for_replaced_characters(
    invoke, messy, monkeypatch
):
    import csv_synth.synth as synth_mod

    def fake(real, rows, *args, **kwargs):
        out = real.head(5).copy()
        out["Café"] = "ł"
        return out

    monkeypatch.setattr(synth_mod, "synthesize", fake)
    result = invoke("generate", messy, "--seed", 1)

    assert result.exit_code == 0, result.output
    assert "Warning" in result.output and "5 character" in result.output
    assert "ł" not in result.output
