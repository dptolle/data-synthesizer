# 11: Large files

**What to build:** Very large Source CSVs finish on a normal laptop. Above a limit, the tool learns from a random sample of rows. The output row count does not change. Source of truth: the spec (`docs/SPEC.md`).

**Blocked by:** 01 (Walking skeleton)

**Status:** ready-for-agent

- [ ] `--fit-rows <n>`, default 500 (owner decision, 2026-11-13). Above that, the tool fits on a random sample of that size and prints a note.
- [ ] The output row count is still the input row count, or `--rows`.
- [ ] Measure the time and memory of a fit at 500 and at 100,000 rows on a normal laptop, using a generated fake file. Report the numbers to the owner.
- [ ] A test (with a small `--fit-rows`) checks that sampling happens and the note is printed.
