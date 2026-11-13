---
title: Local CSV synthesizer CLI
labels: [wayfinder:map]
---

## Destination

A build-ready spec for a command-line tool (run from Git Bash or PowerShell, and ideally Mac/Linux shells) that takes one Source CSV and writes a Synthetic CSV using SDV, entirely on the user's own machine. The spec is detailed enough to hand to a coding agent, and covers the README that a stranger downloading it from GitHub would need.

## Notes

- **Domain**: privacy-preserving synthetic tabular data. Vocabulary lives in `/GLOSSARY.md`. Use its terms (Source CSV, Synthetic CSV, Structural proxy, Metadata).
- **Skills**: grilling tickets call `grilling` and `domain-modeling`. Research tickets call `research`.
- **Selling point**: NO DATA ON THE CLOUD. Every decision is checked against this. A promise made in the README must be true and verifiable.
- **Audience**: anyone who downloads it from GitHub, including data analysts who are not Python experts. The repo is public and MIT-licensed. The owner pushes; agents never push.
- **Agreed while charting**:
  - Single table only: one Source CSV in, one Synthetic CSV out per run.
  - Metadata is detected automatically by default, and the user can review and override it.
  - The Synthetic CSV's purpose is a Structural proxy. Statistical fidelity is a nice-to-have, not a requirement.
  - The tool has a built-in way to drop or keep columns (data minimization) before synthesizing.
- **Writing**: plain, simple English. Short sentences.

## Decisions so far

<!-- one line per closed ticket -->

- [Is SDV's license OK for a public tool?](tickets/001-sdv-license.md): yes. Depend on SDV via pip, never vendor it, and add a BSL note to the README.
- [Does SDV send data anywhere or leak real values?](tickets/002-sdv-network-and-leakage.md): no telemetry; offline after install (not yet run-tested). Leaks real values by default through categorical, non-PII, ID and min/max columns; only PII and key columns are faked.
- [How heavy is SDV to install, and on which platforms?](tickets/003-sdv-install-footprint.md): about 840 MB with torch, about 320 MB without (GaussianCopula works without torch). Python 3.10–3.14. uv is the easiest script route; a per-OS executable is possible but unmeasured.
- [Which privacy guarantees does the tool promise?](tickets/004-privacy-guarantees.md): no Identifying values ever; Shared labels allowed (optional disguise); rare categories merged into "Other"; no real min/max; an overlap check blocks saving; no network use.
- [How do users install the tool, and on which platforms?](tickets/005-install-method.md): command `csv-synth`, installed with `uv tool install` straight from GitHub, torch kept; Windows, Apple-chip Mac and Linux, tested in GitHub Actions.
- [Can SDV disguise category labels consistently?](tickets/008-label-disguise.md): yes, but with plain pandas before fitting, not RDT; rare-category merging is plain pandas too. A fitted synthesizer can contain real values, so it must never be saved.
- [How does the user review and correct detected Metadata?](tickets/006-metadata-review.md): automatic, plus our own value-based personal-data checks; corrections go in a simple CSV Settings file (`column, type, action`) using our own short type list; free text becomes fake sentences.
- [CLI commands and flags](tickets/007-cli-commands-and-flags.md): `inspect` and `generate` commands; `-o`, `--settings`, `--force`, `--rows`, `--seed`, `--rare-threshold`, `--disguise-all`; GaussianCopula only; the tool stops on settings mismatch or a failed privacy check; prints a summary with no data values.

## Not yet specified

<!-- All fog has graduated into tickets: messy CSVs, README, code setup and tests, and writing the spec. -->

## Out of scope

- Multi-table (relational) synthetic data: several linked CSVs in, a linked set out. Ruled out while charting; one table per run.
- Any cloud, hosted or web version. Local only, by design.
- Guaranteeing statistical fidelity good enough to draw conclusions from the Synthetic CSV.
- A torch-free build, a standalone program (`.exe`), and publishing to PyPI. All three were left for a later version in [How do users install the tool, and on which platforms?](tickets/005-install-method.md).
