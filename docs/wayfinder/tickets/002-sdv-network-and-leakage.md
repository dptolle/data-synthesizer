---
title: Does SDV send data anywhere or leak real values?
type: research
status: closed
assignee: claude (research subagent)
blocked_by: []
---

## Question

Two facts the "no data on the cloud" promise depends on:

1. **Network**: Does SDV, or any of its dependencies (e.g. RDT, Faker, copulas, torch, the SDV metadata or usage-tracking features), make network calls or send telemetry during install, import, metadata detection, fitting or sampling? Can everything run with the network switched off after install? Are there settings or environment variables to disable telemetry?
2. **Leakage**: In which ways can real values from the Source CSV appear in the Synthetic CSV? Consider categorical columns (rare values copied verbatim), PII sdtypes (email, address, name, credit card): are they always replaced with Faker values or can they be resampled from real values? Also consider ID columns, and min/max bounds on numeric and date columns. Which SDV settings control this (e.g. `enforce_min_max_values`, PII anonymization options, `pii` flags in metadata)?

## Resolution

Findings: branch `research/sdv-network-and-leakage`, file `docs/research/sdv-network-and-leakage.md`. Applies to sdv 2.2.0 (rdt 2.1.0, copulas 0.15.0, sdmetrics 0.33.0, faker 40.54.0).

**Network**
- There is no telemetry, update check or licence check in sdv, rdt, copulas, sdmetrics, ctgan or deepecho; this was checked by reading the source in the wheels.
- The only network code is the demo-dataset download (public S3), which the tool must never call.
- Install once while online; after that, everything runs offline.
- SDV writes a local `sdv_logs.csv` holding counts only (rows, columns, class name). "Writes no extra files" would therefore be false.

**Leakage: ways real values reach the Synthetic CSV**
- Categorical and boolean values are copied verbatim, including rare ones.
- Columns marked `pii: False` are copied.
- `id` columns that aren't primary keys and have no `regex_format` are copied.
- PII auto-detection uses column names only, so a column whose name isn't recognised stays categorical and gets copied.
- The real min and max of numeric and date columns appear by default (`enforce_min_max_values=True`).
- Columns with `pii: True` (the default for PII sdtypes) and primary keys get Faker or regex values. They only collide with real values by chance.

**Privacy checks available**
- `get_pii_overlap` and `get_combination_overlap` in sdv; `NewRowSynthesis`, DCR and `DisclosureProtection` in sdmetrics.
- Differential privacy is SDV Enterprise only.

**Caveat**
- The offline run test was killed, so these findings come from source code and docs, not an actual run. A socket-blocked test is needed to confirm them.

**Consequence**
- The README can truthfully say "no network used when generating".
- It cannot say "no real values in the output" unless the tool makes users review column types.
