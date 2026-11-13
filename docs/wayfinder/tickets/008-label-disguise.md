---
title: Can SDV disguise category labels consistently?
type: research
status: closed
assignee: claude (research subagent)
blocked_by: []
---

## Question

In sdv 2.2.0 / rdt 2.1.0, can a categorical column's real labels be replaced with consistent stand-ins (each real label always maps to the same fake label, e.g. "Deluxe" → "room_type_1"), while keeping how often each label appears? Does RDT's `PseudoAnonymizedFaker` (or another transformer) do this through `synthesizer.update_transformers`? Does the real-to-fake mapping get stored anywhere (it must not be written into the output)? Also: what is the simplest reliable way to merge rare categories (fewer than N rows) into "Other" before fitting? Show a minimal working code example for both.

## Resolution

Findings: branch `research/label-disguise`, file `docs/research/label-disguise.md`. Applies to sdv 2.2.0 / rdt 2.1.0. Tested in a torch-free environment.

**Disguising labels: yes, with plain pandas, not with RDT.**
- RDT's `PseudoAnonymizedFaker` is the wrong tool. It is rejected on categorical columns. It invents random labels and keeps how often each appears only poorly. It also stores the real labels inside the fitted synthesizer.
- Use a pandas map before `fit` instead: shuffle the labels, then number them (`room_type_1`, ...). Keep the map only in memory.
- In the test, label shares matched (0.385 real vs 0.386 synthetic), and the saved synthesizer held no real labels.

**Merging rare categories: yes, with plain pandas.** SDV has no feature for this. Use a short pandas step before `fit` that replaces any label seen in fewer than N rows with "Other". Pitfalls:
- Don't count or merge empty values.
- If "Other" is already a real label, pick an unused name.
- A pandas `category` column needs "Other" added first.
- A column where every label is rare becomes one single label.

**Privacy warning:** a fitted (pickled) SDV synthesizer can contain real values. The tool should never save it to disk.

**sdv 2.2.0 API notes for the builder:**
- With `Metadata`, `fit` and `sample` take and return a dict `{table: df}`.
- `update_transformers` needs `auto_assign_transformers` to run first.
- `Metadata.detect_from_dataframe` (singular) doesn't exist.
