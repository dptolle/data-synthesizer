---
title: How does the tool handle messy CSV files?
type: grilling
status: open
assignee:
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
