# 09: Messy CSV formats

**What to build:** Real-world CSVs just work, and the Synthetic CSV comes out in the same format as the Source CSV, so code written for one runs on the other unchanged. This covers `;` separators (European Excel), cp1252 or BOM encodings, and decimal commas. Source of truth: the spec (`docs/SPEC.md`); ticket "How does the tool handle messy CSV files?".

**Blocked by:** 07 (Settings file workflow)

**Status:** ready-for-agent

- [ ] The separator is detected automatically and printed. `--delimiter` overrides it.
- [ ] The encoding is detected (UTF-8, UTF-8 with BOM, then cp1252) and printed. `--encoding` overrides it.
- [ ] Decimal commas in number columns are detected. `--decimal` overrides this.
- [ ] The Synthetic CSV uses the same separator, encoding (including BOM) and decimal mark as the Source CSV.
- [ ] The Settings file is saved as UTF-8 with BOM, using the Source CSV's separator.
- [ ] `inspect` and `generate` both accept the three override options.
- [ ] Letters like ä, é and ß survive in column names and Shared labels.
- [ ] The Sample CSV script also writes a `;` / decimal-comma / cp1252 variant. Format tests cover each case.
- [ ] (Added by the owner, 2026-11-13) When the privacy check fails, `generate` still writes the Settings file (unless one was read), so the user can apply the suggested fix. No Synthetic CSV is written.
