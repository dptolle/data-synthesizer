# 07: Settings file workflow

**What to build:** The user can see and correct how each column is handled. `csv-synth inspect <file>` writes a Settings file: one row per column with `column, type, action, format`. The user edits it, for example in Excel. `generate` then uses it. A quick user can skip `inspect`: `generate` detects the settings, uses them, and writes them out for next time. The Settings file holds column names only, never data values. Source of truth: the spec (`docs/SPEC.md`), "Settings file" and "Commands and options".

**Blocked by:** 03 (Personal columns are always faked)

**Status:** done

- [x] `csv-synth inspect <file>` writes `<input>_settings.csv` next to the input by default. `--settings <file>` sets another name.
- [x] The header is `column,type,action,format`. `type` comes from the spec's short list. `action` is `keep` or `drop` (`disguise` arrives in ticket 08). `format` stays empty until ticket 10.
- [x] `generate` with `--settings`: if the file exists, it is read and used. If not, the detected settings are written there.
- [x] `generate` without `--settings` reads `<input>_settings.csv` if it exists. Otherwise it writes it.
- [x] A Settings file that was just read is never overwritten, even with `--force`.
- [x] `drop` removes the column from the output.
- [x] Corrections work: changing a column's type in the file changes how it is synthesized (e.g. `category` to `email`).
- [x] If the CSV's columns and the Settings file's rows don't match, the tool stops and lists the differences.
- [x] Invalid types or actions stop the tool with a clear message.
- [x] A test checks that the Settings file contains no data values.
- [x] The summary lists dropped columns.
