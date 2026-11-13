"""Fit GaussianCopula on a table and sample a synthetic one. Only module that imports SDV."""

import random
import re
from collections import Counter

import numpy as np
import pandas as pd

from csv_synth import privacy
from csv_synth.settings import FAKED_TYPES

# Personal type -> SDV PII sdtype. `pii` stays at its default (True), so Faker
# generates the values. Never set pii=False: that copies real values.
_PII_SDTYPE = {
    "email": "email",
    "name": "name",
    "address": "street_address",
    "phone": "phone_number",
    "card": "credit_card_number",
    # Free text is faked as a PII column until it gets its own handling.
    "text": "street_address",
}

_RUN = re.compile(r"\d+|[A-Z]+|[a-z]+|.", re.S)
_ALPHABET = {"d": "0123456789", "U": "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "l": "abcdefghijklmnopqrstuvwxyz"}
_REGEX_CLASS = {"d": "[0-9]", "U": "[A-Z]", "l": "[a-z]"}


def _shape(value: str) -> tuple:
    """Run-length shape of an ID: ("U", 2), ("-", 0), ("d", 5) for 'BK-12345'."""
    parts = []
    for run in _RUN.findall(value):
        if run.isdigit():
            parts.append(("d", len(run)))
        elif run.isalpha() and run.isupper():
            parts.append(("U", len(run)))
        elif run.isalpha() and run.islower():
            parts.append(("l", len(run)))
        else:
            parts.append((run, 0))
    return tuple(parts)


def _fix_constant_letters(shape: tuple, values: list) -> tuple:
    """A letter run that is the same in every ID (a prefix like 'BK') becomes a literal."""
    out, pos = [], 0
    for k, n in shape:
        width = n if k in _ALPHABET else len(k)
        if k in ("U", "l") and len({v[pos : pos + width] for v in values}) == 1:
            out.append((values[0][pos : pos + width], 0))
        else:
            out.append((k, n))
        pos += width
    return tuple(out)


def _id_regex(shape: tuple) -> str:
    return "".join(
        f"{_REGEX_CLASS[k]}{{{n}}}" if k in _REGEX_CLASS else re.escape(k)
        for k, n in shape
    )


def _id_draw(shape: tuple, rng: random.Random) -> str:
    return "".join(
        "".join(rng.choice(_ALPHABET[k]) for _ in range(n)) if k in _ALPHABET else k
        for k, n in shape
    )


def _renew_ids(values: pd.Series, real: set, shape: tuple, unique: bool, rng) -> pd.Series:
    """Replace any generated ID that equals a real ID (or repeats, if real IDs are unique)."""
    out = list(values)
    seen: set = set()
    for i, v in enumerate(out):
        tries = 0
        while v in real or (unique and v in seen):
            v = _id_draw(shape, rng)
            tries += 1
            if tries > 200:  # format space too small: add one digit/letter
                shape = tuple((k, n + 1) if k in _ALPHABET and j == max(
                    j2 for j2, (k2, _) in enumerate(shape) if k2 in _ALPHABET) else (k, n)
                    for j, (k, n) in enumerate(shape))
                tries = 0
        seen.add(v)
        out[i] = v
    return pd.Series(out, index=values.index)


def synthesize(
    real: pd.DataFrame,
    rows: int,
    seed: int,
    rare_threshold: int = 5,
    types: dict[str, str] | None = None,
    fit_rows: int | None = None,
    disguise: frozenset[str] | set[str] = frozenset(),
) -> pd.DataFrame:
    """Return `rows` synthetic rows with the same columns as `real`.

    `types` maps every column of `real` to its Settings file type (default: detected).
    Personal types are faked; only `category` columns get the rare merge.
    Columns named in `disguise` (must be `category`) get stand-in labels after the
    rare merge. The fitted model lives only in memory and is never saved.
    """
    from sdv.metadata import Metadata
    from sdv.single_table import GaussianCopulaSynthesizer

    # SDV 2.2.0 has no seed argument for fit/sample; seed the global RNGs it uses.
    random.seed(seed)
    np.random.seed(seed)

    # Entirely empty columns carry no information: leave them out of the model
    # and put them back empty afterwards.
    empty = [c for c in real.columns if real[c].isna().all()]
    data = real.drop(columns=empty)
    if types is None:
        from csv_synth.settings import detect_settings

        types = {s.column: s.type for s in detect_settings(real)}
    personal = {c: t for c, t in types.items() if t in FAKED_TYPES and c in data.columns}
    categories = [c for c, t in types.items() if t == "category" and c in data.columns]

    id_info = {}
    for col, kind in personal.items():
        if kind == "id":
            text = data[col].astype("string").str.strip()
            data[col] = text
            shape = Counter(_shape(v) for v in text.dropna()).most_common(1)[0][0]
            shape = _fix_constant_letters(shape, [v for v in text.dropna() if _shape(v) == shape])
            id_info[col] = (shape, set(text.dropna()), bool(text.dropna().is_unique))

    # Rare categories could identify someone: merge them before SDV sees them.
    # Only `category` columns: personal columns are faked, so merging them would
    # collapse all-unique values to "Other" first.
    for col in categories:
        if not pd.api.types.is_numeric_dtype(data[col]) and not pd.api.types.is_bool_dtype(data[col]):
            data[col] = privacy.merge_rare(data[col], rare_threshold)

    # Label disguise comes after the rare merge. The mapping lives in memory only.
    disguise_rng = np.random.default_rng(seed)
    for col in categories:
        if col in disguise:
            data[col] = privacy.disguise(data[col], col, disguise_rng)

    # Large files: learn from a random sample. Sampling comes after the rare-category
    # merge so that rarity is judged on the full data.
    if fit_rows is not None and len(data) > fit_rows:
        data = data.sample(n=fit_rows, random_state=seed)

    metadata = Metadata.detect_from_dataframes({"table": data})
    for col, kind in personal.items():
        if kind == "id":
            metadata.update_column(
                col, "table", sdtype="id", regex_format=_id_regex(id_info[col][0])
            )
        else:
            metadata.update_column(col, "table", sdtype=_PII_SDTYPE[kind])
    for col in categories:
        metadata.update_column(col, "table", sdtype="categorical")
    synthesizer = GaussianCopulaSynthesizer(metadata, enforce_min_max_values=False)
    synthesizer.fit({"table": data})
    out = synthesizer.sample(num_rows=rows)["table"]

    id_rng = random.Random(seed)
    for col, (shape, real_ids, unique) in id_info.items():
        out[col] = _renew_ids(out[col], real_ids, shape, unique, id_rng)

    for col in empty:
        out[col] = np.nan
    return out[list(real.columns)]
