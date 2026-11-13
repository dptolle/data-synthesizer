# 06: Rare categories and the real range

**What to build:** Rare categories, which could identify someone, are merged into "Other" before SDV learns from the data. Numbers and dates no longer reproduce the real minimum and maximum. Build this **test-first**. Source of truth: the spec (`docs/SPEC.md`), "Privacy rules"; research note `docs/research/label-disguise.md`.

**Blocked by:** 01 (Walking skeleton)

**Status:** done

- [x] In `category` columns, labels seen in fewer than `--rare-threshold` rows (default 5) become "Other". This happens with plain pandas, before fitting.
- [x] Empty values are not counted or merged.
- [x] If "Other" already exists as a real label, an unused name is chosen instead.
- [x] Columns with a pandas `category` dtype work (the new label is added first).
- [x] A column where every label is rare becomes a single label, without crashing.
- [x] A column with only one value keeps it: it is a Shared label, not a Rare category.
- [x] The synthesizer uses `enforce_min_max_values=False`. A test shows the real min and max of a number column are not reproduced exactly.
- [x] The Sample CSV script adds rare categories (e.g. one-off corporate account names).
