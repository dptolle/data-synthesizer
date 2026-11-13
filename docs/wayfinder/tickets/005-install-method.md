---
title: How do users install the tool, and on which platforms?
type: grilling
status: closed
assignee: dptolle
blocked_by: ["001", "003"]
---

## Question

Using the facts from "Is SDV's license OK for a public tool?" and "How heavy is SDV to install, and on which platforms?", choose how a non-expert downloads and installs the tool (pip/pipx, uv, standalone executable, or a combination), which operating systems and Python versions are officially supported, and whether it is published to PyPI or installed straight from the GitHub repo. This includes whether to accept torch (simpler, about 840 MB) or ship a torch-free build (about 320 MB, needs a custom environment or executable).

## Resolution

Decided with the owner on 2026-11-13.

1. **Keep torch.** Install SDV normally (about 840 MB on Windows). A torch-free build is left for later.
2. **Install with uv only.** The user installs uv first, then runs `uv tool install`. uv installs Python if needed. A standalone program (`.exe`) is left for later.
3. **Supported systems:** Windows (Git Bash and PowerShell), Mac with Apple chips, and Linux. Intel Macs are not supported, because current torch has no build for them. Tests run on all three systems with GitHub Actions.
4. **Install straight from GitHub:** `uv tool install git+https://github.com/dptolle/data-synthesizer`. Publishing to PyPI is left for later.
5. **The tool is named `csv-synth`.** This is both the command and the package name. The repo keeps its name `data-synthesizer`. (`data-synthesizer` was avoided because it clashes with the existing DataSynthesizer package.)

Python versions follow SDV: 3.10 to 3.14.
