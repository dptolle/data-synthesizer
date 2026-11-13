---
title: Which privacy guarantees does the tool promise?
type: grilling
status: closed
assignee: dptolle
blocked_by: ["002"]
---

## Question

Based on the facts found in "Does SDV send data anywhere or leak real values?", what exactly does the tool promise in its README, and how does it enforce each promise? For example: works fully offline, never makes network calls; PII columns are always replaced with fake values; rare categorical values are never copied; warnings when a column looks sensitive. For each promise: how is it enforced in the tool, and how can a user check it?

## Resolution

Decided with the owner on 2026-11-13.

1. **No Identifying values in the output, ever.** Shared labels (such as "Deluxe" or "Gold") may appear, because they make the Synthetic CSV useful for writing analysis code.
2. **Optional label disguise.** The user can choose to replace shared labels with stand-ins ("Deluxe" becomes "room_type_1"), keeping how often each appears. This works per column or for all columns. It is off by default. (How: see "Can SDV disguise category labels consistently?" — a pandas map before fitting.)
3. **Rare categories are merged into "Other" by default.** A category is rare if it appears in fewer than 5 rows. The user can change this threshold.
4. **No real min or max by default.** The tool turns off SDV's `enforce_min_max_values`. Chance matches on ordinary numbers are allowed.
5. **Overlap check before saving, every run.** The tool uses SDV's `get_pii_overlap` and `get_combination_overlap`. If any personal-data value or any whole real row appears in the output, the tool refuses to write the file and prints what it found.
6. **No network use.** The tool never calls SDV's demo-download code. A test in the repo proves the tool runs with the network blocked.

Consequence: SDV finds personal-data columns by column name only. So the user must be able to see and correct each column's type before synthesis. That belongs to "How does the user review and correct detected Metadata?"
