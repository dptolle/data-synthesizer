# 02: Offline proof and GitHub Actions

**What to build:** Evidence for the main promise ("your data never leaves your computer"), and automatic tests on every supported system. A full `generate` run must succeed with all network access blocked. Every push runs the tests on Windows, Apple-chip macOS and Linux. Source of truth: the spec (`docs/SPEC.md`).

**Blocked by:** 01 (Walking skeleton)

**Status:** ready-for-agent

- [ ] A test runs a full `csv-synth generate` with sockets blocked (pytest-socket). It passes, and it fails if anything tries to connect.
- [ ] The tool never calls SDV's demo-dataset download.
- [ ] GitHub Actions runs the full test suite on every push. Matrix: Windows, macOS (Apple chip) and Linux × Python 3.10 and 3.14.
- [ ] On Linux, CI installs CPU-only torch, to avoid the multi-GB CUDA download. Record the exact working command; ticket 12 reuses it for the README.
- [ ] SDV's local `sdv_logs.csv`: find out where and when SDV 2.2.0 writes it. **Ask the owner** whether to redirect it, disable it, or document it, then implement the choice with a test.
