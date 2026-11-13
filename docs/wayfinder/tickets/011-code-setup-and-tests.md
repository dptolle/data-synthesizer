---
title: How is the code set up and tested?
type: grilling
status: open
assignee:
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
