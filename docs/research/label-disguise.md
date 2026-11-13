# Can SDV disguise category labels consistently?

Tested with sdv 2.2.0 and rdt 2.1.0 (installed without torch), single-table `GaussianCopulaSynthesizer`, Python 3.13.

## Short answer

- RDT's `PseudoAnonymizedFaker` is the wrong tool for this. It does not work on a normal categorical column. On a "pii" column it makes random 4-letter fake labels, keeps the real-to-fake map inside the fitted synthesizer, and I could not show it keeps label frequencies.
- Use plain pandas instead. Map each real label to a stand-in (`room_type_1`, ...) before `fit`. Keep the map only in memory. Frequencies are kept, and the fitted synthesizer never sees the real labels.
- Merge rare labels into "Other" with plain pandas before fit. No SDV or RDT feature is needed.

## Q1. Consistent stand-in labels

### What `PseudoAnonymizedFaker` does

- The docs say it replaces values with fake ones in a reversible way, using Python Faker. The map is consistent, and `get_mapping()` returns it. [RDT docs](https://docs.sdv.dev/rdt/transformers-glossary/generic-pii-anonymization/pseudoanonymizedfaker)
- The docs warn that anyone with the transformer can look up the mapping and recover the real values. They point to `AnonymizedFaker` if recovery must be impossible. Same page.
- The default fake value is a random 4-character string from `lexify`. It is made without looking at the real data. Same page.
- Source: `PseudoAnonymizedFaker` keeps `_mapping_dict` and `_reverse_mapping_dict` as attributes and fills them in `_fit`. [rdt/transformers/pii/anonymizer.py](https://github.com/sdv-dev/RDT/blob/main/rdt/transformers/pii/anonymizer.py) (also checked in the installed rdt 2.1.0).

### What I saw when I ran it

1. On a column with sdtype `categorical`, `update_transformers` fails: `InvalidConfigError: Column 'room' is a categorical column, which is incompatible with the 'PseudoAnonymizedFaker' transformer.`
2. It is accepted only if the column is declared as a PII-style column, for example `sdtype="unknown", pii=True`. That column is no longer a normal category.
3. `update_transformers` must be called after `auto_assign_transformers` (or `preprocess`). Before that it raises `NotFittedError`. See [Flexible Preprocessing](https://docs.sdv.dev/sdv/modeling/configuration/preprocessing).
4. The fake labels are random 4-letter strings. The real-to-fake map came back from `get_transformers()["room"].get_mapping()`, for example `{'Standard': 'fEBr', 'Deluxe': 'dvgu', 'Suite': 'YoRv'}`.
5. `pickle.dumps(synthesizer)` contained the real label `Deluxe` as bytes. So the map (and the real labels) are stored inside a pickled synthesizer. Never pickle or save such a synthesizer if the labels are secret.
6. Frequencies: in a 6-label test the sampled fake-label counts did not match the real counts well (real 385/350/111/65 empty/60, sampled 233/217/188/132/129/77/24 in 1000 rows, with more distinct values than the real data). I would not rely on it to keep frequencies.
7. Fake values are random, so a fake label could equal a real one by coincidence. The docs say this too.

### Recommended approach: pandas stand-ins before fit

SDV then models ordinary categorical text. Frequencies come from the model as usual. The real labels never enter SDV, so they are not in the synthesizer or any pickle (I checked: no real label bytes in the pickle).

```python
import numpy as np, pandas as pd
from sdv.metadata import Metadata
from sdv.single_table import GaussianCopulaSynthesizer

def disguise(df, col, prefix, rng):
    labels = sorted(df[col].dropna().unique())          # NaN is not a label
    shuffled = rng.permutation(labels)                  # hide the sort order
    mapping = {str(l): f"{prefix}_{i + 1}" for i, l in enumerate(shuffled)}
    out = df.copy()
    out[col] = out[col].map(lambda v: mapping.get(str(v)) if pd.notna(v) else v)
    return out                                          # mapping is NOT returned or saved

rng = np.random.default_rng()
safe = disguise(df, "room", "room_type", rng)

meta = Metadata.detect_from_dataframes({"t": safe})
meta.update_column("room", sdtype="categorical", table_name="t")
synth = GaussianCopulaSynthesizer(meta)
synth.fit({"t": safe})
out = synth.sample(1000)["t"]
```

Result of my run (6 labels plus 5% empty cells, 1000 rows): real and synthetic shares matched closely, for example `room_type_2` 0.385 real vs 0.386 synthetic, `room_type_1` 0.111 vs 0.118, empty 0.065 vs 0.066. The mapping existed only in a local variable. (My test used a direct dict; the helper above is the same idea, but I ran the dict version, not this exact function.)

Notes:

- Shuffle the labels before numbering. Numbering in sorted order leaks the order of the real labels.
- Do the rare-label merge first, then disguise. Then "Other" is just another label. Decide whether "Other" keeps its name (readable) or also becomes a stand-in.
- Consistency holds within one run, because it is one dict. Keeping the same stand-ins across runs needs a stored map, which is a leak risk. Default should be a fresh random map each run.
- In sdv 2.2.0 with `Metadata`, `fit`, `auto_assign_transformers` and `sample` use a dict `{table_name: df}`. Passing a bare DataFrame raised `InvalidDataTypeError`, and `sample` returned a dict. `Metadata.detect_from_dataframe` (singular) does not exist; use `detect_from_dataframes`. I did not test `SingleTableMetadata`.

## Q2. Merging rare categories into "Other"

I found no SDV or RDT setting that does this. Do it in pandas before `fit`. The [Flexible Preprocessing](https://docs.sdv.dev/sdv/modeling/configuration/preprocessing) and [GaussianCopulaSynthesizer](https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer) docs list no such feature.

```python
def merge_rare(s, min_count=5, other="Other"):
    counts = s.value_counts(dropna=True)        # empty cells are never counted
    rare = counts[counts < min_count].index
    return s.where(~s.isin(rare), other)        # NaN stays NaN
```

Test run with `min_count=20`: Cabin (10) and Shack (19) became `Other` (29 rows). Empty cells stayed empty (65). Big labels were untouched.

Pitfalls:

- **"Other" already exists as a real label.** The code above would silently mix real "Other" rows with merged rare rows. Better: if `other` is already a value in the column, pick an unused name (such as `Other_2`) and tell the user.
- **Empty cells (NaN).** Do not count them as a category and do not merge them. SDV handles missing values in categorical columns itself (the synthetic data had them at about the same rate).
- **Threshold.** Use `<` for "fewer than N rows". A label with exactly N rows stays.
- **Only one column is protected.** Merging one column does not stop a rare combination of columns. That is a different problem.
- **Dtype.** For pandas `category` dtype, `where` with a new value fails unless "Other" is added as a category first. Convert with `astype(object)`. Do not use `astype(str)`, because it turns NaN into the text "nan".
- **Merging can leave one label.** If everything is rare, the column becomes all "Other". Warn the user.

## Sources

- RDT docs, PseudoAnonymizedFaker: https://docs.sdv.dev/rdt/transformers-glossary/generic-pii-anonymization/pseudoanonymizedfaker
- SDV docs, Flexible Preprocessing (`update_transformers`, `get_transformers`): https://docs.sdv.dev/sdv/modeling/configuration/preprocessing
- SDV docs, GaussianCopulaSynthesizer: https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer
- RDT source, anonymizer: https://github.com/sdv-dev/RDT/blob/main/rdt/transformers/pii/anonymizer.py
- Own test runs in a throwaway venv (sdv 2.2.0, rdt 2.1.0), deleted afterwards.

## Answer

1. Yes, but not with RDT. `PseudoAnonymizedFaker` rejects categorical columns, makes random labels, and stores the real-to-fake map and the real labels inside the synthesizer (they appear in a pickle). Map labels with pandas before `fit` instead, shuffle before numbering, and keep the map only in memory. Frequencies were kept in my test.
2. Use a short pandas function before `fit`. Count non-null values, merge those under N into "Other", leave NaN alone, and pick an unused name if "Other" already exists. Merge first, then disguise.
