"""Reading and writing CSV files. Detects the separator, encoding and decimal mark,
and writes the Synthetic CSV in the same format as the Source CSV."""

import codecs
import csv
import io
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

_CANDIDATES = [",", ";", "\t", "|"]
_COMMA_NUMBER = re.compile(r"^\s*[-+]?\d+,\d+\s*$")
_PLAIN_NUMBER = re.compile(r"^\s*[-+]?\d+(\.\d+)?\s*$")
_BOM = codecs.BOM_UTF8


class FormatError(Exception):
    """The file cannot be read with the chosen or detected format. Safe to show."""


@dataclass(frozen=True)
class CsvFormat:
    delimiter: str = ","
    encoding: str = "utf-8"  # "utf-8-sig" means UTF-8 with BOM
    decimal: str = "."

    def describe(self) -> str:
        enc = "utf-8 with BOM" if self.encoding == "utf-8-sig" else self.encoding
        sep = "tab" if self.delimiter == "\t" else f"'{self.delimiter}'"
        return f"separator {sep}, encoding {enc}, decimal mark '{self.decimal}'"


def detect_encoding(raw: bytes) -> str:
    if raw.startswith(_BOM):
        return "utf-8-sig"
    try:
        raw.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError as exc:
        # A cut-off multi-byte letter at the end of the sample is not an error.
        if exc.start >= len(raw) - 3 and exc.reason == "unexpected end of data":
            return "utf-8"
        return "cp1252"


def _header_line(text: str) -> str:
    return text.lstrip("﻿").splitlines()[0] if text.strip() else ""


def detect_delimiter(header: str) -> str:
    best, best_count = ",", 1
    for cand in _CANDIDATES:
        try:
            fields = next(csv.reader(io.StringIO(header), delimiter=cand))
        except (StopIteration, csv.Error):
            continue
        if len(fields) > best_count:
            best, best_count = cand, len(fields)
    return best


def _detect_decimal(df: pd.DataFrame) -> str:
    """A decimal comma if some column has numbers like 1,5 and no plain numbers with a point."""
    for col in df.columns:
        values = df[col].dropna().astype(str)
        values = values[values.str.strip() != ""]
        if values.empty:
            continue
        comma = values.map(lambda v: bool(_COMMA_NUMBER.match(v)))
        plain = values.map(lambda v: bool(_PLAIN_NUMBER.match(v)))
        if comma.any() and (comma | plain).all() and not values.str.contains(".", regex=False).any():
            return ","
    return "."


def detect_format(
    path: Path,
    delimiter: str | None = None,
    encoding: str | None = None,
    decimal: str | None = None,
) -> CsvFormat:
    """Work out the format of `path`; any given option wins over the guess."""
    with open(path, "rb") as fh:
        raw = fh.read(1_000_000)
    enc = encoding or detect_encoding(raw)
    try:
        text = raw.decode(enc, errors="replace")
    except LookupError as exc:
        raise FormatError(f"Unknown encoding `{enc}` (--encoding).") from exc
    sep = delimiter or detect_delimiter(_header_line(text))
    if decimal is None:
        try:
            sample = pd.read_csv(
                io.StringIO(text), sep=sep, dtype=str, keep_default_na=False, nrows=5000
            )
        except (pd.errors.ParserError, pd.errors.EmptyDataError):
            sample = pd.DataFrame()
        decimal = _detect_decimal(sample)
    return CsvFormat(sep, enc, decimal)


def read_source(path: Path, fmt: CsvFormat | None = None) -> pd.DataFrame:
    fmt = fmt or detect_format(path)
    try:
        return pd.read_csv(path, sep=fmt.delimiter, encoding=fmt.encoding, decimal=fmt.decimal)
    except UnicodeDecodeError as exc:
        raise FormatError(
            f"The file cannot be read as {fmt.encoding}. Try another --encoding (for example cp1252)."
        ) from exc
    except pd.errors.EmptyDataError as exc:
        raise FormatError("The file is empty.") from exc


def _unencodable(text: str, encoding: str) -> int:
    return sum(1 for ch in text if not _encodable(ch, encoding))


def _encodable(ch: str, encoding: str) -> bool:
    try:
        ch.encode(encoding)
        return True
    except UnicodeEncodeError:
        return False


def write_synthetic(df: pd.DataFrame, path: Path, fmt: CsvFormat | None = None) -> int:
    """Write the file. Returns how many characters the encoding could not hold (written as ?)."""
    fmt = fmt or CsvFormat()
    replaced = sum(_unencodable(str(c), fmt.encoding) for c in df.columns)
    for col in df.columns:
        if df[col].dtype == object or pd.api.types.is_string_dtype(df[col]):
            replaced += sum(
                _unencodable(v, fmt.encoding) for v in df[col].dropna() if isinstance(v, str)
            )
    # `replace` keeps a faked value with a letter the encoding lacks from stopping the run.
    df.to_csv(
        path,
        index=False,
        sep=fmt.delimiter,
        decimal=fmt.decimal,
        encoding=fmt.encoding,
        errors="replace",
        lineterminator="\n",
    )
    return replaced
