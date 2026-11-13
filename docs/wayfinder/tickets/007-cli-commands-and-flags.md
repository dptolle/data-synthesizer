---
title: CLI commands and flags
type: grilling
status: closed
assignee: dptolle
blocked_by: ["006"]
---

## Question

What commands and flags does the tool have? This covers: the main run (Source CSV in, Synthetic CSV out), the metadata review/override flow from "How does the user review and correct detected Metadata?", dropping or keeping columns, row count, seed, synthesizer choice, an optional quality report, output file naming, and overwrite behaviour. Also: how the Settings file is created, passed in and reused; the rare-category threshold; and the rule that the fitted SDV model is never saved to disk (it can contain real values). Each flag needs a default and a one-line purpose.

## Resolution

Decided with the owner on 2026-11-13.

**Commands**
- `csv-synth inspect <file.csv>` only writes the Settings file.
- `csv-synth generate <file.csv>` writes the Synthetic CSV. It also writes the settings it used, unless it was given an existing Settings file.

**Options**

| Option | Default | Purpose |
|---|---|---|
| `-o <file>` | `<input>_synthetic.csv` next to the input | Name of the Synthetic CSV (`generate`) |
| `--settings <file>` | `<input>_settings.csv` next to the input | `inspect`: where the file is written. `generate`: if the file exists, it is read; if not, it is written there. |
| `--force` | off | Allow overwriting an existing output file |
| `--rows <n>` | same as input | Number of rows to generate |
| `--seed <n>` | random; the seed used is printed | Same input gives the same output (check during building that SDV fully supports this) |
| `--rare-threshold <n>` | 5 | Labels seen in fewer rows become "Other" |
| `--disguise-all` | off | Disguise the labels of every `category` column |

**Rules**
- `generate` never overwrites a Settings file it has just read.
- Per-column choices (type, drop, disguise) go only in the Settings file. Options cover whole-run choices only.
- The method is always GaussianCopula. There is no option to choose another.
- The fitted SDV model is never saved to disk.
- If the Settings file and the CSV columns don't match, the tool stops and lists the columns that don't match.
- If the privacy check fails, the tool writes no file. It names the overlapping columns and suggests a fix for the Settings file. It never fixes anything by itself.
- At the end, the tool prints a short summary with no data values: rows and columns written; which columns were faked, disguised or dropped; the privacy check result; SDV's quality score.
