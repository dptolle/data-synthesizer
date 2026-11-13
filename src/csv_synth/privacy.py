"""Privacy rules applied with plain pandas: rare-category merge and the overlap check.

The overlap check: no personal value may appear in the output (this blocks saving).
Whole real rows copied by chance only produce a warning with a count.
Interface: `check_overlap(real, synthetic, column_types)` returns findings,
`describe(findings)` turns them into messages. Findings hold only column names
and counts, never data values. The check never fixes anything.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


# --- Rare-category merge ----------------------------------------------------


def _unused_name(base: str, taken: set) -> str:
    if base not in taken:
        return base
    i = 2
    while f"{base}_{i}" in taken:
        i += 1
    return f"{base}_{i}"


def merge_rare(series: pd.Series, threshold: int = 5, other: str = "Other") -> pd.Series:
    """Return a copy where labels seen in fewer than `threshold` rows become `other`.

    Empty values are not counted or merged. If `other` already is a real label,
    an unused name is used instead. A column with a single distinct label is a
    Shared label and is left alone.
    """
    counts = series.value_counts(dropna=True)
    if len(counts) <= 1:
        return series.copy()
    rare = counts[counts < threshold].index
    if len(rare) == 0:
        return series.copy()
    name = _unused_name(other, set(counts.index))
    out = series.copy()
    if isinstance(out.dtype, pd.CategoricalDtype):
        out = out.cat.add_categories([name])
    mask = out.isin(rare)
    out[mask] = name
    if isinstance(out.dtype, pd.CategoricalDtype):
        out = out.cat.remove_unused_categories()
    return out


# --- Label disguise --------------------------------------------------------


def disguise(series: pd.Series, column: str, rng) -> pd.Series:
    """Return a copy where each distinct label becomes `<column>_<n>`.

    The labels are shuffled before numbering so the numbers do not reveal their
    order. Empty values stay empty. The label-to-stand-in mapping exists only
    inside this call: it is not returned, stored or written anywhere.
    """
    labels = list(series.dropna().unique())
    order = rng.permutation(len(labels))
    mapping = {label: f"{column}_{int(n) + 1}" for label, n in zip(labels, order)}
    out = series.astype(object).map(mapping)
    return out.where(series.notna(), np.nan)


# --- Overlap check ----------------------------------------------------------

from dataclasses import dataclass


# Column types whose values must never appear in the same column of the output.
PERSONAL_TYPES = frozenset({"email", "name", "address", "phone", "card", "id", "text"})

_TABLE = "table"


@dataclass(frozen=True)
class Finding:
    kind: str  # "value": shared values in one personal column; "row": whole real rows
    column: str | None  # the column for "value", None for "row"
    count: int  # number of distinct shared values / rows

    @property
    def blocks(self) -> bool:
        """Shared personal values block saving; copied whole rows only warn."""
        return self.kind == "value"


def check_overlap(
    real: pd.DataFrame, synthetic: pd.DataFrame, column_types: dict[str, str]
) -> list[Finding]:
    """Compare `synthetic` with `real`. An empty list means the check passed.

    `column_types` maps column name to type; columns missing from it are treated
    as non-personal (only the whole-row check covers them).
    """
    from sdv.evaluation.utils import get_combination_overlap, get_pii_overlap

    findings: list[Finding] = []
    for col in real.columns:
        if column_types.get(col) not in PERSONAL_TYPES or col not in synthetic.columns:
            continue
        tables = _tables(real[[col]].dropna(), synthetic[[col]].dropna())
        count = get_pii_overlap(*tables, _TABLE, col, verbose=False)
        # Our own direct check, in case SDV's does not see the column (e.g. `text`).
        direct = len(set(tables[0][_TABLE][col]) & set(tables[1][_TABLE][col]))
        if max(count, direct):
            findings.append(Finding("value", col, max(count, direct)))

    shared = [c for c in real.columns if c in synthetic.columns]
    if shared and len(synthetic):
        tables = _tables(real[shared], synthetic[shared])
        rows = get_combination_overlap(*tables, _TABLE, shared, verbose=False)
        if rows:
            findings.append(Finding("row", None, rows))
    return findings


def describe(findings: list[Finding]) -> list[str]:
    """Human-readable lines for the findings: column names and counts only."""
    lines = []
    for f in findings:
        if f.kind == "value":
            lines.append(
                f"- Column `{f.column}`: {f.count} value(s) also appear in the real data. "
                f"Fix in the Settings file: set column `{f.column}` to a personal type "
                "such as `email`, `name`, `address`, `phone`, `card`, `id` or `text`."
            )
        else:
            lines.append(
                f"- {f.count} synthetic row(s) are exact copies of real rows. "
                "This can happen by chance in small tables. If the table has "
                "names, emails, ids or similar, check they have a personal type "
                "in the Settings file."
            )
    return lines


def _tables(real: pd.DataFrame, synthetic: pd.DataFrame):
    return {_TABLE: real}, {_TABLE: synthetic}
