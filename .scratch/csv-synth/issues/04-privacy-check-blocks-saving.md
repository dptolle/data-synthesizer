# 04: Privacy check blocks saving

**What to build:** Before writing anything, `generate` compares the Synthetic CSV with the prepared real data. If any personal value appears in the output, the tool writes no file. (Amended by the owner: whole real rows only produce a warning with a count.) It names the overlapping columns, suggests a Settings file fix (e.g. "set column `contact` to type `email`"), and exits with an error code. It never fixes anything by itself. The check is the second agreed test seam: it is tested directly, because the other rules make a real leak hard to produce through the CLI. Build this **test-first**. Source of truth: the spec (`docs/SPEC.md`), "Privacy rules" and "Testing Decisions".

**Blocked by:** 01 (Walking skeleton)

**Status:** done

- [x] The check uses SDV's `get_pii_overlap` and `get_combination_overlap`.
- [x] Our own direct check: no value from any `email`, `name`, `address`, `phone`, `card`, `id` or `text` column appears in that column of the output.
- [x] Seam tests: given a "real" table and a "synthetic" table that share values, the check reports exactly the right columns. Given tables with no overlap, it reports nothing.
- [x] CLI test: when the check fails, no output file exists afterwards, the message names the columns and suggests a fix, and the exit code is non-zero.
- [x] Messages and the summary never contain data values, only column names and counts.
- [x] The summary reports the check result on success.
