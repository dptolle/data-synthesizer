"""The Settings file: one row per column with `column,type,action,format`.

It holds column names and settings only, never data values.
"""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from csv_synth.detect import detect_personal_columns

HEADER = ["column", "type", "action", "format"]
TYPES = ("email", "name", "address", "phone", "card", "id", "category", "number", "date", "text")
# Types whose values are always replaced by fake ones.
FAKED_TYPES = frozenset({"email", "name", "address", "phone", "card", "id", "text"})
ACTIONS = ("keep", "drop", "disguise")


class SettingsError(Exception):
    """The Settings file is unusable. The message is safe to show (no data values)."""


@dataclass(frozen=True)
class Setting:
    column: str
    type: str
    action: str = "keep"
    format: str = ""


def detect_settings(df: pd.DataFrame) -> list[Setting]:
    """Guess a Setting for every column of `df`."""
    personal = detect_personal_columns(df)
    out = []
    for col in df.columns:
        if col in personal:
            kind = personal[col]
        elif pd.api.types.is_numeric_dtype(df[col]) and not pd.api.types.is_bool_dtype(df[col]):
            kind = "number"
        else:
            kind = "category"
        out.append(Setting(str(col), kind))
    return out


def write_settings(settings: list[Setting], path: Path, sep: str = ",") -> None:
    """UTF-8 with BOM so Excel shows special letters correctly."""
    frame = pd.DataFrame([[s.column, s.type, s.action, s.format] for s in settings], columns=HEADER)
    frame.to_csv(path, index=False, sep=sep, encoding="utf-8-sig")


def read_settings(path: Path, sep: str | None = None) -> list[Setting]:
    """Read and validate a Settings file. Raises SettingsError with a clear message."""
    try:
        frame = pd.read_csv(
            path, dtype=str, keep_default_na=False, encoding="utf-8-sig", sep=sep, engine="python"
        )
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as exc:
        raise SettingsError(f"Cannot read the Settings file {path}: {exc}") from exc
    frame.columns = [str(c).strip() for c in frame.columns]
    if frame.columns.tolist() != HEADER:
        raise SettingsError(
            f"The Settings file {path} must start with the header {','.join(HEADER)}."
        )
    settings: list[Setting] = []
    problems: list[str] = []
    seen: set[str] = set()
    for _, row in frame.iterrows():
        column, kind, action, fmt = (str(row[h]).strip() for h in HEADER)
        kind, action = kind.lower(), action.lower()
        if column in seen:
            problems.append(f"column `{column}` appears more than once")
        seen.add(column)
        if kind not in TYPES:
            problems.append(
                f"column `{column}`: `{kind}` is not a valid type (use one of {', '.join(TYPES)})"
            )
        if action not in ACTIONS:
            problems.append(
                f"column `{column}`: `{action}` is not a valid action "
                f"(use one of {', '.join(ACTIONS)})"
            )
        elif action == "disguise" and kind != "category":
            problems.append(
                f"column `{column}`: `disguise` only works on type `category`, not `{kind}`"
            )
        settings.append(Setting(column, kind, action, fmt))
    if problems:
        raise SettingsError(f"The Settings file {path} has problems:\n- " + "\n- ".join(problems))
    return settings


def check_matches(settings: list[Setting], df: pd.DataFrame) -> None:
    """Stop if the CSV's columns and the Settings file's rows differ, or a type does not fit."""
    in_file = [s.column for s in settings]
    in_csv = [str(c) for c in df.columns]
    problems = [f"`{c}` is in the CSV but not in the Settings file" for c in in_csv if c not in in_file]
    problems += [f"`{c}` is in the Settings file but not in the CSV" for c in in_file if c not in in_csv]
    if problems:
        raise SettingsError(
            "The CSV and the Settings file do not match:\n- " + "\n- ".join(problems)
        )
    for s in settings:
        if s.type == "number" and s.action == "keep":
            col = df[s.column]
            if not pd.api.types.is_numeric_dtype(col) or pd.api.types.is_bool_dtype(col):
                raise SettingsError(
                    f"Column `{s.column}` is marked `number` but does not hold numbers. "
                    "Change its type in the Settings file."
                )


def types_of_kept(settings: list[Setting]) -> dict[str, str]:
    """Column -> type for every column that is not dropped."""
    return {s.column: s.type for s in settings if s.action != "drop"}


def disguised(settings: list[Setting]) -> list[str]:
    """Columns whose labels are replaced by stand-ins."""
    return [s.column for s in settings if s.action == "disguise"]
