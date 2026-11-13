# 10: Dates

**What to build:** Date columns are detected, their format is guessed and written to the Settings file's `format` column, and the Synthetic CSV writes dates in the same format. The user can correct the format in the Settings file. Source of truth: the spec (`docs/SPEC.md`); ticket "How does the tool handle messy CSV files?".

**Blocked by:** 09 (Messy CSV formats)

**Status:** ready-for-agent

- [ ] Date columns are detected as `date`. Their format (e.g. `%d.%m.%Y`, `%Y-%m-%d`, `%m/%d/%Y`) is filled in the `format` column.
- [ ] Dates are synthesized as SDV `datetime` with that format, and written in the same format.
- [ ] A format corrected in the Settings file is used.
- [ ] A column with mixed date styles stops the tool and asks the user to set the format in the Settings file.
- [ ] Real min/max dates are not reproduced exactly (follows from ticket 06).
- [ ] The Sample CSV script adds check-in and check-out dates in both sample variants.
