# 05: Free text is replaced

**What to build:** Free-text columns (notes, comments) are detected as type `text` and replaced with fake sentences of similar length, so no real text survives. SDV would otherwise copy them as categories. Build this **test-first**. Source of truth: the spec (`docs/SPEC.md`), "Type → SDV mapping".

**Blocked by:** 03 (Personal columns are always faked), 04 (Privacy check blocks saving)

**Status:** ready-for-agent

- [ ] A text column where almost every value is different is detected as `text`. The exact threshold is chosen while building and noted in the code.
- [ ] `text` columns are never passed to SDV as categorical. The output holds Faker sentences of about the same length as the real values.
- [ ] The privacy test checks that no real text value appears in the output.
- [ ] The overlap check from ticket 04 covers `text` columns, and a test proves it.
- [ ] The Sample CSV script adds a free-text column (e.g. guest notes).
