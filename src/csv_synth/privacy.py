"""The overlap check: no personal value and no whole real row may appear in the output.

Interface: `check_overlap(real, synthetic, column_types)` returns findings,
`describe(findings)` turns them into messages. Findings hold only column names
and counts, never data values. The check never fixes anything.
"""

from dataclasses import dataclass

import pandas as pd

# Column types whose values must never appear in the same column of the output.
PERSONAL_TYPES = frozenset({"email", "name", "address", "phone", "card", "id", "text"})

_TABLE = "table"


@dataclass(frozen=True)
class Finding:
    kind: str  # "value": shared values in one personal column; "row": whole real rows
    column: str | None  # the column for "value", None for "row"
    count: int  # number of distinct shared values / rows


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
                "Fix in the Settings file: check that every column holding names, "
                "emails, ids or similar has a personal type, and that no column "
                "is marked as safe to copy by mistake."
            )
    return lines


def _tables(real: pd.DataFrame, synthetic: pd.DataFrame):
    return {_TABLE: real}, {_TABLE: synthetic}
