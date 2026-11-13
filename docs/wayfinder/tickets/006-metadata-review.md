---
title: How does the user review and correct detected Metadata?
type: grilling
status: closed
assignee: dptolle
blocked_by: ["004", "008"]
---

## Question

Metadata is detected automatically by default, and the user can override it (agreed while charting). How does that work in practice? For example: the tool saves the detected Metadata to a file the user can edit and pass back in; an interactive review step in the terminal; or both. What is the file format, how is it validated, and what happens when detection is probably wrong (like the billing address detected as an ID in the video)? Which semantic types must the user be warned about, given the promises in "Which privacy guarantees does the tool promise?"

## Resolution

Decided with the owner on 2026-11-13.

1. **Automatic by default, with our own safety checks.** SDV detects personal data by column name only. The tool also inspects the values. It treats a column as personal if its values look like emails, card numbers or phone numbers, or if almost every value is different (free text). The overlap check before saving still catches anything that slips through.
2. **Corrections are made with a settings file**, not with questions in the terminal (interactive input is unreliable in Git Bash on Windows). The tool writes the file, the user edits it, and the next run uses it. The file can be reused.
3. **The settings file is our own simple CSV** with one row per column: `column, type, action`. `action` is `keep`, `drop` or `disguise`. It can be edited in Excel. It holds column names only, never data values.
4. **The types are our own short list.** The tool maps them to SDV types:
   - `email`, `name`, `address`, `phone`, `card`, `id`: always replaced with fake values
   - `category`: Shared labels, kept; Rare categories become "Other"
   - `number`, `date`: newly generated values
   - `text`: free text
5. **Free-text columns are replaced with fake sentences of similar length.** No real text survives.

_Amended by "How does the tool handle messy CSV files?": the Settings file has a 4th column, `format`, for date formats._
