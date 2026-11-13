---
title: How does the tool handle messy CSV files?
type: grilling
status: closed
assignee: dptolle
blocked_by: []
---

## Question

Real CSV files vary. How does `csv-synth` deal with:
- `;` delimiters (common with Excel in Europe);
- text encodings (UTF-8, UTF-8 with BOM, cp1252);
- different date formats;
- empty columns and columns with only one value;
- very large files?

For each case: does the tool detect it automatically, need an option, or stop with a clear message? Is the Synthetic CSV written in the same format as the Source CSV (delimiter, encoding), or always in one standard format?

## Resolution

Decided with the owner on 2026-11-13.

1. **The output keeps the input's format**: same separator, encoding, decimal style and date style. Code written for the Synthetic CSV must work on the Source CSV unchanged.
2. **Separator**: detected automatically and printed. `--delimiter` overrides it.
3. **Encoding**: the tool tries UTF-8 (with or without BOM), then cp1252. It prints which one it used. `--encoding` overrides it.
4. **Decimal comma**: detected in number columns and kept in the output. `--decimal` overrides it.
5. **Dates**: the Settings file gets a 4th column, `format` (e.g. `%d.%m.%Y`). The tool fills it in for date columns, and the user can correct it there. Output dates use the same format. If a column mixes date styles, the tool stops and asks the user to set the format.
6. **Empty and one-value columns**: an empty column stays empty. A column with only one value keeps that value (it is a Shared label, not a Rare category). Missing values elsewhere appear about as often as in the input.
7. **Large files**: above 100,000 rows, the tool learns from a random sample of 100,000 rows and prints a note. `--fit-rows <n>` changes the limit. The output row count is unchanged (input rows, or `--rows`). The 100,000 figure must be tested on a normal laptop during building.

New options for `generate` and `inspect`: `--delimiter`, `--encoding`, `--decimal`, `--fit-rows`.

_Amended by the owner on 2026-11-13: the `--fit-rows` default is 500, not 100,000._
