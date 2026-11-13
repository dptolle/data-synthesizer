"""Fit GaussianCopula on a table and sample a synthetic one. Only module that imports SDV."""

import random

import numpy as np
import pandas as pd


def synthesize(real: pd.DataFrame, rows: int, seed: int) -> pd.DataFrame:
    """Return `rows` synthetic rows with the same columns as `real`.

    The fitted model lives only in memory and is never saved.
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

    metadata = Metadata.detect_from_dataframes({"table": data})
    synthesizer = GaussianCopulaSynthesizer(metadata, enforce_min_max_values=False)
    synthesizer.fit({"table": data})
    out = synthesizer.sample(num_rows=rows)["table"]

    for col in empty:
        out[col] = np.nan
    return out[list(real.columns)]
