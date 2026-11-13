# 01: Walking skeleton: `generate` makes a Synthetic CSV

**What to build:** A user installs the tool with `uv tool install` from the GitHub repo and gets a working `csv-synth` command. `csv-synth generate <file>` reads a simple Source CSV (comma-separated, UTF-8, only number and category columns) and writes a Synthetic CSV next to it, using SDV's GaussianCopula. It ends with a short summary. This is the thinnest end-to-end path. Later tickets add privacy, settings and formats to it. Source of truth: the spec (`docs/SPEC.md`). Use the terms in the Glossary.

**Blocked by:** None (can start immediately)

**Status:** done

- [x] The project uses uv's standard src layout. `uv tool install git+<repo>` installs a `csv-synth` command. Python 3.10–3.14. (Verified by CI in ticket 02.)
- [x] `sdv==2.2.0` is pinned exactly in the project dependencies. Typer is the CLI library.
- [x] Only the `synth` module imports SDV. The module split follows the spec (`cli`, `csvio`, `settings`, `detect`, `privacy`, `synth`). Create a module only when it is first needed.
- [x] `csv-synth generate <file>` writes `<input>_synthetic.csv` next to the input by default. `-o` sets another name.
- [x] If the output exists, the tool stops with a clear message. `--force` allows overwriting.
- [x] `--rows <n>` sets the row count. The default is the Source CSV's row count.
- [x] `--seed <n>` gives identical output for identical input. Without it, a random seed is used and printed. Verify that SDV 2.2.0 really makes this repeatable. If it doesn't, report this to the owner before working around it.
- [x] Empty columns stay empty. Missing values appear about as often as in the input.
- [x] The fitted model is never written to disk. A test checks that no new files appear apart from the expected outputs (SDV's `sdv_logs.csv` is handled in ticket 02).
- [x] At the end, a summary prints rows and columns written, with no data values.
- [x] `csv-synth --help` and `csv-synth generate --help` explain every option in plain words.
- [x] A script in the repo uses Faker to generate a fake hotel Sample CSV (about 500 rows; first version: numbers, categories, some missing values). Later tickets extend it.
- [x] pytest tests drive the CLI in-process (Typer's test runner) on small temporary CSVs and check only files, messages and exit codes. SDV is never mocked.
