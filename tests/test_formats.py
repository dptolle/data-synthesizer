"""Messy CSV formats (ticket 09). All data is made up."""

import pandas as pd
import pytest

from csv_synth import csvio

ROWS = [
    ("Müller", "Café", 1.5, 10),
    ("Strauß", "Crème", 2.25, 20),
    ("Ängström", "Café", 3.0, 30),
] * 10


def _write(path, text, encoding):
    path.write_bytes(text.encode(encoding))
    return path


def _csv_text(sep=";", decimal=","):
    lines = [sep.join(["größe", "Café", "preis", "n"])]
    for a, b, p, n in ROWS:
        lines.append(sep.join([a, b, str(p).replace(".", decimal), str(n)]))
    return "\n".join(lines) + "\n"


@pytest.mark.parametrize(
    "sep,encoding,decimal",
    [
        (";", "cp1252", ","),
        (";", "utf-8-sig", ","),
        (",", "utf-8", "."),
        ("\t", "utf-8", "."),
        ("|", "cp1252", "."),
    ],
)
def test_format_is_detected_and_values_survive(tmp_path, sep, encoding, decimal):
    path = _write(tmp_path / "a.csv", _csv_text(sep, decimal), encoding)

    fmt = csvio.detect_format(path)
    df = csvio.read_source(path, fmt)

    assert (fmt.delimiter, fmt.encoding, fmt.decimal) == (sep, encoding, decimal)
    assert list(df.columns) == ["größe", "Café", "preis", "n"]
    assert set(df["größe"]) == {"Müller", "Strauß", "Ängström"}
    assert df["preis"].tolist()[:3] == [1.5, 2.25, 3.0]


def test_overrides_win_over_detection(tmp_path):
    path = _write(tmp_path / "a.csv", _csv_text(";", ","), "cp1252")

    fmt = csvio.detect_format(path, delimiter="|", encoding="latin-1", decimal=".")

    assert (fmt.delimiter, fmt.encoding, fmt.decimal) == ("|", "latin-1", ".")


def test_integers_and_text_with_commas_do_not_trigger_decimal_comma(tmp_path):
    path = _write(tmp_path / "a.csv", "a;b\n1,5 stars;3\nfoo, bar;4\n", "utf-8")

    assert csvio.detect_format(path).decimal == "."


@pytest.mark.parametrize("encoding", ["cp1252", "utf-8-sig", "utf-8"])
def test_written_file_has_the_source_separator_encoding_and_decimal(tmp_path, encoding):
    fmt = csvio.CsvFormat(";", encoding, ",")
    df = pd.DataFrame({"größe": ["Müller"], "preis": [1.5]})
    out = tmp_path / "out.csv"

    csvio.write_synthetic(df, out, fmt)

    expected = "größe;preis\nMüller;1,5\n".encode(encoding)
    assert out.read_bytes().replace(b"\r\n", b"\n") == expected


def test_utf8_bom_is_written_only_for_bom_sources(tmp_path):
    df = pd.DataFrame({"a": [1]})
    csvio.write_synthetic(df, tmp_path / "b.csv", csvio.CsvFormat(",", "utf-8-sig", "."))
    csvio.write_synthetic(df, tmp_path / "n.csv", csvio.CsvFormat(",", "utf-8", "."))

    assert (tmp_path / "b.csv").read_bytes().startswith(b"\xef\xbb\xbf")
    assert not (tmp_path / "n.csv").read_bytes().startswith(b"\xef\xbb\xbf")
