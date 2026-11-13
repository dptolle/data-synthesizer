"""Guess and check date formats. Dates are read as text and never converted by pandas."""

import pandas as pd

# Order matters for ambiguous values (all days 12 or less): the first fitting format
# wins. Slash dates default to month first; the user can correct it in the Settings file.
CANDIDATES = (
    "%Y-%m-%d",
    "%d.%m.%Y",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%d.%m.%Y %H:%M",
    "%Y-%m-%d %H:%M",
    "%m/%d/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
)

# Share of non-empty values that must look like a date (in some style) for the column to be `date`.
_DATE_SHARE = 0.8


def _parses(values: pd.Series, fmt: str) -> pd.Series:
    return pd.to_datetime(values, format=fmt, errors="coerce").notna()


def _clean(series: pd.Series) -> pd.Series:
    values = series.dropna().astype(str).str.strip()
    return values[values != ""]


def guess(series: pd.Series) -> tuple[bool, str]:
    """Return (is_date, format). `format` is empty when the styles are mixed."""
    if pd.api.types.is_numeric_dtype(series) or pd.api.types.is_bool_dtype(series):
        return False, ""
    values = _clean(series)
    if values.empty:
        return False, ""
    fits = {fmt: _parses(values, fmt) for fmt in CANDIDATES}
    for fmt, ok in fits.items():
        if ok.all():
            return True, fmt
    any_style = pd.concat(fits.values(), axis=1).any(axis=1)
    return (True, "") if any_style.mean() >= _DATE_SHARE else (False, "")


def misfits(series: pd.Series, fmt: str) -> int:
    """How many non-empty values do not match `fmt`."""
    return int((~_parses(_clean(series), fmt)).sum())
