"""Find columns that hold personal data, using column names and value patterns.

SDV's own detection looks at column names only, so a column called `contact`
that holds emails would be copied. Here values are checked as well.
Types: email, name, address, phone, card, id, text.
"""

import re

import pandas as pd

# Share of non-empty values that must match a pattern to call the column that type.
_MATCH_SHARE = 0.8

# Free text: non-numeric, at least 90% of values distinct, and sentence-like
# (at least 80% contain a space, mean length at least 15 characters). Chosen so
# that unique short codes and labels stay out, while notes and comments are in.
_TEXT_UNIQUE = 0.9
_TEXT_SPACED = 0.8
_TEXT_MIN_LENGTH = 15

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE = re.compile(r"^\+?[\d\s().\-/]{7,25}$")

_NAME_HINTS = {
    "email": {"email", "mail", "emailaddress"},
    "card": {"card", "cardnumber", "creditcard", "ccnumber", "cc", "pan"},
    "phone": {"phone", "telephone", "tel", "mobile", "fax", "handy", "telefon"},
    "address": {"address", "addr", "street", "adresse", "strasse"},
    "name": {
        "name", "firstname", "lastname", "surname", "fullname", "forename",
        "vorname", "nachname",
    },
    "id": {"id", "ids", "uuid", "guid", "ref"},
}


def _tokens(column: str) -> set[str]:
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", str(column))
    parts = [p.lower() for p in re.split(r"[^A-Za-z0-9]+", spaced) if p]
    return set(parts) | {"".join(parts)}


def _luhn(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2:
            d = d * 2 - 9 if d > 4 else d * 2
        total += d
    return total % 10 == 0


def _share(values: pd.Series, test) -> float:
    return sum(1 for v in values if test(v)) / len(values)


def _is_card(v: str) -> bool:
    digits = re.sub(r"[\s-]", "", v)
    return digits.isdigit() and 13 <= len(digits) <= 19 and _luhn(digits)


def _is_phone(v: str) -> bool:
    if not _PHONE.match(v):
        return False
    digits = sum(c.isdigit() for c in v)
    # Bare digit strings are too often plain numbers; need a + or a separator.
    return 7 <= digits <= 15 and not v.isdigit()


def _digit_like(values: pd.Series) -> bool:
    return _share(values, lambda v: bool(re.fullmatch(r"[\d\s-]{8,}", v))) >= _MATCH_SHARE


def _by_value(values: pd.Series) -> str | None:
    if _share(values, lambda v: bool(_EMAIL.match(v))) >= _MATCH_SHARE:
        return "email"
    if _share(values, _is_card) >= _MATCH_SHARE:
        return "card"
    if _share(values, _is_phone) >= _MATCH_SHARE:
        return "phone"
    return None


def _by_name(column: str, values: pd.Series) -> str | None:
    tokens = _tokens(column)
    for kind, hints in _NAME_HINTS.items():
        if tokens & hints:
            if kind == "card" and not _digit_like(values):
                continue
            return kind
    return None


def _is_text(raw: pd.Series, values: pd.Series) -> bool:
    if pd.api.types.is_numeric_dtype(raw) or pd.api.types.is_datetime64_any_dtype(raw):
        return False
    return (
        values.nunique() / len(values) >= _TEXT_UNIQUE
        and _share(values, lambda v: " " in v) >= _TEXT_SPACED
        and values.str.len().mean() >= _TEXT_MIN_LENGTH
    )


def detect_personal_columns(df: pd.DataFrame) -> dict[str, str]:
    """Map each personal column to its type. Columns that are not personal are left out."""
    found: dict[str, str] = {}
    for col in df.columns:
        values = df[col].dropna().astype(str).str.strip()
        values = values[values != ""]
        if values.empty:
            continue
        kind = _by_value(values) or _by_name(col, values)
        if kind is None and _is_text(df[col], values):
            kind = "text"
        if kind:
            found[col] = kind
    return found
