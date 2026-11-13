# 02: Offline proof and GitHub Actions

**What to build:** Evidence for the main promise ("your data never leaves your computer"), and automatic tests on every supported system. A full `generate` run must succeed with all network access blocked. Every push runs the tests on Windows, Apple-chip macOS and Linux. Source of truth: the spec (`docs/SPEC.md`).

**Blocked by:** 01 (Walking skeleton)

**Status:** done

- [x] A test runs a full `csv-synth generate` with sockets blocked (pytest-socket). It passes, and it fails if anything tries to connect.
- [x] The tool never calls SDV's demo-dataset download.
- [x] GitHub Actions runs the full test suite on every push. Matrix: Windows, macOS (Apple chip) and Linux × Python 3.10 and 3.14.
- [x] On Linux, CI installs CPU-only torch, to avoid the multi-GB CUDA download. Record the exact working command; ticket 12 reuses it for the README. (Verified: `--index https://download.pytorch.org/whl/cpu`.)
- [x] SDV's local `sdv_logs.csv`: find out where and when SDV 2.2.0 writes it. **Ask the owner** whether to redirect it, disable it, or document it, then implement the choice with a test. (Owner chose: document only. SDV 2.2.0 never writes it; a test guards it.)

Verified on GitHub Actions run 43494867866 (2026-11-13): all 6 jobs passed (Windows, macOS, Linux x Python 3.10 and 3.14), including `uv tool install` and running `csv-synth`.
