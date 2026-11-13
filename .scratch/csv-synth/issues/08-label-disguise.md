# 08: Label disguise

**What to build:** For users whose category labels are secret, the `disguise` action replaces each real label with a consistent stand-in (`<column>_1`, `<column>_2`, …). The frequencies are kept and the words disappear. `--disguise-all` does this for every `category` column. Build this **test-first**. Source of truth: the spec (`docs/SPEC.md`), "Privacy rules"; research note `docs/research/label-disguise.md`.

**Blocked by:** 06 (Rare categories and the real range), 07 (Settings file workflow)

**Status:** done

- [x] Disguise is done with plain pandas before fitting: shuffle the distinct labels, number them, and keep the mapping in memory only. RDT's `PseudoAnonymizedFaker` is NOT used.
- [x] Disguise runs after the rare-category merge.
- [x] `disguise` in the Settings file works per column. `--disguise-all` applies it to every `category` column.
- [x] `disguise` on any type other than `category` stops the tool with a clear message.
- [x] Tests: no real label appears in a disguised column; label shares in the output are close to the input's; the mapping appears in no file the tool writes.
- [x] The summary lists disguised columns.
