"""Privacy rules applied with plain pandas: rare-category merge (more in later tickets)."""

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
