---
title: How is the code set up and tested?
type: grilling
status: closed
assignee: dptolle
blocked_by: []
---

## Question

How will the code be set up and tested?
- Which CLI library will it use (e.g. argparse, Typer, Click)?
- What is the project layout, and how is the uv/`pyproject.toml` setup done so that `uv tool install git+https://...` gives a `csv-synth` command?
- How is SDV's version pinned? The research applies to sdv 2.2.0.
- What gets tested:
  - a test that proves the tool runs with the network blocked;
  - tests for each privacy rule (no Identifying values, rare-category merge, label disguise, overlap check blocks saving);
  - a sample fake CSV for tests and demos.
- How do GitHub Actions run the tests on Windows, Apple-chip Mac and Linux?

## Resolution

Decided with the owner on 2026-11-13.

1. **CLI library: Typer**, for clear help text.
2. **Layout:** one package in `src/csv_synth/`, using uv's standard project layout. `pyproject.toml` declares the `csv-synth` script. The modules are:
   - `cli.py`: commands and options
   - `csvio.py`: CSV reading and writing (separator, encoding, decimals, dates)
   - `settings.py`: the Settings file
   - `detect.py`: our value-based personal-data checks
   - `privacy.py`: rare-category merge, label disguise, overlap check
   - `synth.py`: the only module that imports SDV
3. **SDV pinned exactly: `sdv==2.2.0`.** Upgrades are deliberate and only happen after the privacy tests pass again.
4. **Tests use pytest:**
   - privacy tests, at least one per privacy rule (no Identifying values, rare merge, disguise, overlap check blocks saving, model never saved);
   - an offline test that runs a full `generate` with the network blocked;
   - format tests (`;` separator, cp1252 encoding, decimal comma, date formats, output format matches input).
5. **Sample data:** a fake hotel CSV of about 500 rows in `examples/`, made with Faker by a script in the repo. It has a `;` / decimal-comma variant. Tests and the README use it.
6. **CI:** GitHub Actions on every push. It runs on Windows, Apple-chip Mac and Linux, with Python 3.10 and 3.14. On Linux, CI installs CPU-only torch.
7. **Privacy rules are built test-first:** each privacy test is written before the code it checks. Everything else is built normally.
