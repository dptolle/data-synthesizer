---
title: csv-synth — local synthetic copies of a CSV file
labels: [ready-for-agent]
source: docs/wayfinder/map.md (all decisions trace back to its closed tickets)
---

# csv-synth

Terms in **bold capitals** (Source CSV, Synthetic CSV, Structural proxy, Metadata, Settings file, Identifying value, Shared label, Rare category) are defined in `GLOSSARY.md`. Use them exactly.

## Problem Statement

Analysts want help from AI tools and colleagues to write analysis code. But their data is often confidential: emails, addresses, card numbers. They are not allowed to upload it. Running AI tools locally is hard and limited. And even AI tools in a terminal send data to the cloud.

What they need is a safe stand-in: a file with the same columns and structure, but no real personal values. They can share that stand-in, get working code back, and run the code on the real data on their own computer. Tools like SDV can make such a file. But SDV copies real values by default (categories, unrecognised columns, real min/max values), detects personal data by column name only, and needs Python skills to use.

## Solution

`csv-synth` is a free command-line tool, run from Git Bash, PowerShell, or a Mac/Linux shell. It takes one Source CSV and writes a Synthetic CSV next to it. Everything happens on the user's computer. After install, the tool makes no network connections.

The flow:

1. `csv-synth inspect data.csv` looks at the file and writes a Settings file: one row per column, with a guessed type, an action and (for dates) a format.
2. The user checks the Settings file in Excel or a text editor and corrects it if needed.
3. `csv-synth generate data.csv` makes the Synthetic CSV, using the Settings file.

A quick user can skip step 1. `generate` then guesses the settings, uses them, and writes them out for next time.

The Synthetic CSV is a Structural proxy. It is safe to share and realistic enough to write code against. It is not statistically reliable enough to draw conclusions from. It never contains Identifying values. The tool checks this before saving, and refuses to save if the check fails.

## User Stories

**Getting started**

1. As an analyst who is not a Python expert, I want to install the tool with two commands (install uv, then `uv tool install` from GitHub), so that I don't have to manage Python myself.
2. As a Windows user, I want the tool to work in both Git Bash and PowerShell, so that I can use my usual terminal.
3. As a Mac user with an Apple chip, I want the tool to work, so that I am not excluded.
4. As a Linux user, I want a README tip for installing the small CPU-only torch, so that I don't download several GB I don't need.
5. As a new user, I want to try the tool on an included sample CSV, so that I can see what it does before using my own data.
6. As a new user, I want `csv-synth --help` and `csv-synth generate --help` to explain every option in plain words, so that I don't need the README open all the time.
7. As a new user, I want the README to explain the typical workflow (make a synthetic copy, share it, get code back, run the code on the real data), so that I understand why the tool exists.

**Privacy**

8. As an analyst with confidential data, I want my data never to leave my computer, so that I don't break my organisation's rules.
9. As an analyst, I want emails, names, addresses, phone numbers, card numbers and IDs replaced with fake values, so that no person can be identified from the Synthetic CSV.
10. As an analyst, I want free-text columns (notes, comments) replaced with fake sentences of similar length, so that no real text survives.
11. As an analyst, I want categories that appear in fewer than 5 rows merged into "Other", so that a rare value (such as one company's name) can't identify anyone.
12. As an analyst, I want to change the rare-category threshold, so that I can be stricter or looser for my data.
13. As an analyst whose category labels are secret (for example product codes), I want to disguise labels as stand-ins such as `room_type_1`, so that the words disappear while their frequencies stay.
14. As an analyst, I want to disguise labels column by column or all at once, so that I only hide what is secret.
15. As an analyst, I want numbers and dates not to reproduce the real minimum and maximum, so that extreme real values don't leak.
16. As an analyst, I want the tool to detect personal data by its values as well as its column name, so that a column called `contact` holding emails is still treated as personal.
17. As an analyst, I want the tool to check the output against my data before saving, so that a mistake can't leak real values.
18. As an analyst, if that check fails, I want no file written, a list of the columns that overlap, and a suggested fix for the Settings file, so that I can correct it myself.
19. As an analyst, I want the tool never to save its trained model, so that real values aren't left behind in a hidden file.
20. As an analyst, I want to drop columns I don't need, so that I share as little as possible.
21. As an analyst, I want the README to say honestly what is and isn't protected (column names, common labels and overall patterns remain visible), so that I check the output before sharing it.
22. As an analyst in the EU, I want the README to say that the tool is not a legal guarantee of anonymisation, so that I don't wrongly rely on it for GDPR compliance.

**Settings file**

23. As a careful user, I want to run `inspect` first and check the guessed types before any synthetic data is made, so that I stay in control.
24. As a user, I want the Settings file to be a simple CSV (`column, type, action, format`), so that I can edit it in Excel.
25. As a user, I want a short list of types (`email`, `name`, `address`, `phone`, `card`, `id`, `category`, `number`, `date`, `text`), so that I don't need to learn SDV's terms.
26. As a user, I want the actions `keep`, `drop` and `disguise`, so that each column's handling is in one place.
27. As a user, I want the Settings file to contain only column names and settings, never data values, so that it is safe to share too.
28. As a user, I want to name the Settings file with `--settings`, so that I can keep several versions.
29. As a user, I want the same `--settings` name to work for both steps (`inspect` writes it, `generate` reads it), so that the workflow is easy to remember.
30. As a user, I want `generate` never to overwrite a Settings file it has just read, so that my edits are safe.
31. As a user, I want to reuse a Settings file next month on a new export of the same data, so that I don't repeat my corrections.
32. As a user, if the CSV's columns don't match the Settings file, I want the tool to stop and list the differences, so that a new column holding personal data isn't handled by guesswork.

**Generating**

33. As a user, I want the Synthetic CSV to have the same number of rows as the Source CSV by default, so that it looks like the real thing.
34. As a user, I want to choose the number of rows with `--rows`, so that I can make a small sample to share.
35. As a user, I want `--seed` to give the same output for the same input, and the tool to print the seed it used, so that I can repeat a run.
36. As a user, I want the output named `<input>_synthetic.csv` next to the input by default, and `-o` to change it, so that I know where to find it.
37. As a user, I want the tool to refuse to overwrite existing files unless I add `--force`, so that I don't lose work.
38. As a user, I want a short summary at the end (rows and columns written; which columns were faked, disguised or dropped; the privacy check result; the quality score), with no data values in it, so that I know what happened.

**Messy files**

39. As a European Excel user, I want `;` separators detected automatically, so that my file just works.
40. As a user, I want the encoding detected (UTF-8, UTF-8 with BOM, cp1252), so that letters like ä, é and ß survive.
41. As a user, I want decimal commas (`1,5`) detected, so that my numbers are read correctly.
42. As a user, I want options to override the detected separator, encoding and decimal mark, so that I can fix a wrong guess.
43. As a user, I want the Synthetic CSV to use the same separator, encoding, decimal mark and date format as my Source CSV, so that code written for one works on the other unchanged.
44. As a user, I want date formats guessed and written to the Settings file, so that I can correct them in one place.
45. As a user, if one column mixes date styles, I want the tool to stop and ask me to set the format, so that dates aren't silently broken.
46. As a user, I want empty columns to stay empty and one-value columns to keep their value, so that the structure matches.
47. As a user, I want missing values to appear about as often as in my data, so that my code handles them.
48. As a user with a very large file, I want the tool to learn from a random sample of 100,000 rows by default, with `--fit-rows` to change this, so that it finishes on a normal laptop.

**Maintainer**

49. As the maintainer, I want SDV pinned to an exact version, so that a new SDV release can't quietly weaken the privacy promises.
50. As the maintainer, I want tests to run automatically on Windows, Mac and Linux with the oldest and newest supported Python, so that every platform keeps working.
51. As the maintainer, I want a test proving the tool runs with the network blocked, so that the main promise is backed by evidence.
52. As the maintainer, I want every privacy promise in the README backed by a test, so that the README never claims more than the tool does.
53. As the maintainer, I want the sample CSV generated by a script in the repo, so that anyone can see it is fake.

## Implementation Decisions

**Packaging and install**
- Python package named `csv-synth`, providing a `csv-synth` command. The repo stays named `data-synthesizer`.
- Uses uv's standard project layout with a src layout. Installed with `uv tool install git+https://github.com/dptolle/data-synthesizer`. Not published to PyPI.
- Python 3.10 to 3.14 (SDV's range). Supported systems: Windows, Apple-chip macOS, Linux. Intel Macs are not supported (current torch has no build for them).
- SDV pinned exactly to `sdv==2.2.0`. `uv tool install` resolves from `pyproject.toml`, not from the lock file, so the exact pin must be there. All research applies to sdv 2.2.0 / rdt 2.1.0 / copulas 0.15.0 / sdmetrics 0.33.0.
- torch is installed (default SDV dependencies). It is not used.
- SDV is installed as a dependency, never copied into the repo (BSL 1.1 licence; see the license ticket).
- CLI library: Typer.

**Modules** (one package, split by job)
- `cli`: the `inspect` and `generate` commands and their options. Prints messages and the summary. Sets exit codes.
- `csvio`: reading and writing CSVs. Detects the separator, encoding and decimal mark, and writes the output in the same format.
- `settings`: creating, reading, validating and writing the Settings file. Checks that its columns match the CSV.
- `detect`: guesses each column's type from its name and values (email, card, phone patterns; nearly-all-unique text), and guesses date formats.
- `privacy`: rare-category merge, label disguise, and the final overlap check.
- `synth`: the only module that imports SDV. Builds the SDV Metadata from the Settings file, fits GaussianCopula, and samples.

**Processing steps for `generate`**
1. Read the Source CSV (detect or apply the separator, encoding and decimal mark).
2. Load the Settings file if `--settings` points to an existing file (or `<input>_settings.csv` exists). Otherwise detect the settings. Stop if the columns don't match.
3. Drop the columns marked `drop`.
4. Merge Rare categories into "Other" in `category` columns (threshold `--rare-threshold`, default 5).
5. Disguise labels in columns marked `disguise` (or in all `category` columns with `--disguise-all`).
6. If there are more than `--fit-rows` rows (default 100,000), take a random sample to learn from.
7. Fit GaussianCopula and sample `--rows` rows (default: the Source CSV's row count), using `--seed`.
8. Run the overlap check against the prepared real data. On failure, write no Synthetic CSV and exit non-zero, but still write the Settings file (unless one was read), so the user can apply the suggested fix (owner decision, 2026-11-13).
9. Write the Synthetic CSV in the Source CSV's format, then the Settings file (unless one was read), then print the summary.

**Settings file**
- CSV with the header `column,type,action,format`. One row per Source CSV column. Column names only, never values.
- `type`: one of `email`, `name`, `address`, `phone`, `card`, `id`, `category`, `number`, `date`, `text`.
- `action`: `keep`, `drop` or `disguise`. `disguise` is only valid for `category`. On any other type, the tool stops with a clear message.
- `format`: a date format such as `%d.%m.%Y`, filled in for `date` columns and empty otherwise.
- Saved as UTF-8 with BOM (so Excel reads special letters correctly), using the same separator as the Source CSV (so a European `;` user's Excel opens it in columns).

**Type → SDV mapping**
- `email`, `name`, `address`, `phone`, `card`: SDV PII sdtypes with `pii: True`, so they are always Faker-generated. Never set `pii: False`.
- `id`: SDV `id` sdtype with a generated format, so real IDs are never copied (SDV copies non-key `id` columns that have no `regex_format`).
- `text`: SDV does not fake free text. The tool replaces it with Faker sentences of similar length after sampling (or treats it as an anonymised PII column). It is never passed to SDV as `categorical`.
- `category`: SDV `categorical`, after the rare merge and optional disguise.
- `number`, `date`: SDV `numerical` / `datetime` (with `datetime_format` from the Settings file).
- The synthesizer is created with `enforce_min_max_values=False`.

**Privacy rules (non-negotiable)**
- No Identifying values in the Synthetic CSV. Shared labels may appear.
- Rare categories (fewer than `--rare-threshold` rows, default 5) are merged into "Other" before fitting. Empty values are not counted or merged. If "Other" already exists as a real label, use an unused name. pandas `category` dtypes need the new label added first. A column where every label is rare becomes a single label.
- Label disguise is done with plain pandas before fitting: shuffle the distinct labels, number them `<column>_1`, `<column>_2`, … and keep the mapping in memory only. Do NOT use RDT's `PseudoAnonymizedFaker`: it is rejected on categorical columns, keeps frequencies poorly, and stores real labels inside the fitted synthesizer.
- The overlap check runs on every `generate`, using SDV's `get_pii_overlap` and `get_combination_overlap`, plus our own direct check that no value from any `email`, `name`, `address`, `phone`, `card`, `id` or `text` column appears in that column of the output (SDV's checks don't know our `text` type). If any personal or `text` value overlaps, write no file, name the columns, suggest a Settings file change, and exit non-zero. If whole real rows appear (which can happen by chance in small tables), save the file but print a warning with the count only (owner decision, 2026-11-13). Never fix anything automatically.
- The fitted SDV model is never saved to disk (pickles can contain real values).
- The tool never calls SDV's demo-dataset download (the only network code in SDV).
- SDV 2.2.0 never writes `sdv_logs.csv` (its logging is off by default). It only copies a small logger settings file, with no data, into the per-user SDV data folder (e.g. `%LOCALAPPDATA%\sdv-dev\sdv`). The README mentions this. A test fails if `sdv_logs.csv` ever appears. Don't claim "no files written" (owner decision, 2026-11-13).

**Commands and options**

| Option | Commands | Default | Purpose |
|---|---|---|---|
| `-o <file>` | generate | `<input>_synthetic.csv` next to the input | Synthetic CSV name |
| `--settings <file>` | both | `<input>_settings.csv` next to the input | `inspect`: where to write. `generate`: read if it exists, otherwise write there |
| `--force` | both | off | Allow overwriting existing output files |
| `--rows <n>` | generate | Source CSV row count | Rows to generate |
| `--seed <n>` | generate | random; printed | Repeatable output |
| `--rare-threshold <n>` | generate | 5 | Labels seen in fewer rows become "Other" |
| `--disguise-all` | generate | off | Disguise every `category` column |
| `--delimiter <c>` | both | detected | Override the separator |
| `--encoding <name>` | both | detected (UTF-8, then cp1252) | Override the encoding |
| `--decimal <c>` | both | detected | Override the decimal mark |
| `--fit-rows <n>` | generate | 100,000 | Learn from a random sample above this size |

- The method is always GaussianCopula. There is no option to choose another.
- Per-column choices live only in the Settings file. Options are for whole-run choices only.
- Any existing output file stops the run unless `--force` is given. A Settings file that was just read is never overwritten, even with `--force`.
- The summary and all messages contain no data values, only column names and counts.

**SDV 2.2.0 API notes** (found in research; verify while building)
- With the `Metadata` class, `fit`, `auto_assign_transformers` and `sample` take and return a dict `{table_name: DataFrame}`.
- `update_transformers` needs `auto_assign_transformers` to run first.
- `Metadata.detect_from_dataframe` (singular) does not exist. Use the plural form or build the Metadata from the Settings file directly.
- `import sdv` works without torch (SDV PR #2570).

**README** (English only, sections in this order)
1. What it is: two sentences plus the main promise.
2. Typical use: synthetic copy → share → get code back → run it on real data locally.
3. Install: uv, then `uv tool install …`; a tip for CPU-only torch on Linux (command tested during building).
4. Quick start on the sample CSV.
5. Workflow: `inspect` → edit → `generate`.
6. Settings file reference.
7. All options (table).
8. Privacy: what is promised and what is not.
9. Limits: Structural proxy only, one table per run, about 840 MB install, no Intel Macs.
10. License: MIT, plus a note that SDV is BSL-licensed and hosted commercial services are not covered.

Promise wording (each sentence must be backed by a test):
- "Your data never leaves your computer. After installing, the tool makes no network connections."
- "Emails, names, addresses, phone numbers, card numbers and free text from your file never appear in the output. The tool checks this before it saves."
- "The output still shows your column names, common category labels and overall patterns. Check it before you share it."

The README also states clearly that the tool is not a legal guarantee of anonymisation (e.g. under GDPR), and that users must follow their own organisation's rules.

## Testing Decisions

**What makes a good test here:** it checks only what a user can see: files written, their contents, messages printed, exit codes. It never checks internal functions, SDV calls or intermediate DataFrames. Then the tests survive refactoring and SDV upgrades, and they prove the README's promises directly.

**Seams** (agreed with the owner)
1. **The CLI (main seam).** Tests call `csv-synth inspect` / `generate` in-process (Typer's test runner) on small CSVs in a temp directory, then read the output files. Nearly everything is tested here.
2. **The overlap check (one extra seam).** The earlier rules prevent leaks, so a real leak is hard to force through the CLI. The check is tested directly: give it a "real" and a "synthetic" table that share values, and assert that it reports the right columns. The CLI test for "check fails → no file written" may also force the check through this seam.
3. **Personal-data detection (added with owner approval during building).** Detection is tested directly too, because it is cheap and pins down detection bugs.

No other seams. SDV is never mocked. Tests use the real sdv 2.2.0.

**Test-first:** every privacy rule is built test-first: write the failing test, then the code. Other features are built normally, with tests.

**Test groups**
- **Privacy**: no Identifying values in the output for each personal type, including a column with an unhelpful name (e.g. `contact` holding emails); rare merge (threshold, "Other" collision, nulls); disguise (labels replaced, frequencies kept, mapping not in any file); no real min/max reproduced; overlap check blocks saving and names columns; no model file written anywhere.
- **Offline**: a full `generate` run with sockets blocked (e.g. pytest-socket) must succeed.
- **Formats**: `;` separator, cp1252, UTF-8 with BOM, decimal comma, several date formats, mixed date formats (stops), empty and one-value columns; the output format matches the input.
- **Settings workflow**: `inspect` then `generate` with the same `--settings`; a read Settings file is never overwritten; column mismatch stops with a list; `--force` behaviour; default file names.
- **Options**: `--rows`, `--seed` (same seed → same output), `--fit-rows`.

**Sample data:** a script in the repo uses Faker to generate a fake hotel CSV of about 500 rows (emails, addresses, card numbers, rare categories, a free-text column, dates, numbers with missing values), plus a `;` / decimal-comma / cp1252 variant. Tests and the README quick start use it.

**CI:** GitHub Actions on every push. Matrix: Windows, macOS (Apple chip), Linux × Python 3.10 and 3.14. On Linux, install CPU-only torch to avoid the multi-GB download.

**Prior art:** none. The repo is new.

## Out of Scope

- Multi-table (relational) data: one Source CSV per run.
- Any cloud, hosted or web version.
- Guaranteed statistical fidelity.
- A torch-free build, a standalone executable (`.exe`), and publishing to PyPI (later versions).
- Choosing synthesizers other than GaussianCopula.
- Interactive questions in the terminal (unreliable in Git Bash). All corrections go through the Settings file.
- Differential privacy (SDV Enterprise only).
- A separate report file. The summary is printed only.
- README translations.

## Further Notes

**Verify during building** (open facts, not open decisions)
- `--seed` gives fully repeatable output with SDV 2.2.0.
- `--fit-rows` default: owner first chose 500, then 100,000 after measurement (100,000 rows: about 90 s and 414 MB on a laptop; 500: about 34 s, 381 MB).
- The exact command for CPU-only torch on Linux, with `uv tool install`.
- The offline claim with a real socket-blocked run. The research read the source code but did not run it offline.

**Boundaries for the building agent**
- **Always**: use the Glossary terms; write each privacy test before its code; run the full test suite before reporting a step done; keep SDV imports in the `synth` module only; use only the fake sample data.
- **Ask first**: changing the SDV version; adding a dependency other than Typer, Faker, pytest or pytest-socket; changing any README promise wording; changing a default (threshold, file names, `--fit-rows`); anything that adds an option or changes the Settings file format.
- **Never**: upload, send or print real data; add any network call; save the fitted model; copy SDV code into the repo; set `pii: False` on a personal type; weaken or skip the overlap check; push to GitHub (the owner pushes).

**Decision record:** every decision here comes from a closed ticket in `docs/wayfinder/tickets/`. Research findings are on the local branches `research/sdv-license`, `research/sdv-network-and-leakage`, `research/sdv-install-footprint` and `research/label-disguise`. The builder should merge or copy the `docs/research/` files to `main` before building, so they are available.

**Decisions made with the owner during building (2026-11-13)**
- Whole real rows found by the overlap check only produce a warning with a count. Personal and `text` value overlap still blocks saving.
- `--fit-rows` default: 100,000 (after measurement).
- Personal-data detection is a third test seam.
- SDV 2.2.0 never writes `sdv_logs.csv`. The README documents the small SDV settings file in the user's data folder.
- When the privacy check fails, the Settings file is still written (unless one was read).
- In a disguised column, the merged "Other" label is disguised too.
- When `generate` writes a Settings file during a `--disguise-all` run, it records `disguise` for every `category` column.
- Characters that the output encoding can't hold are replaced with `?`, and the tool prints a warning with the count.
- Ambiguous slash dates (every day 12 or less) are assumed month first (`%m/%d/%Y`), with a warning naming the column and pointing to the Settings file. `inspect` also warns about columns with mixed date styles.
