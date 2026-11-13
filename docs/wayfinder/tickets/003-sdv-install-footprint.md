---
title: How heavy is SDV to install, and on which platforms?
type: research
status: closed
assignee: claude (research subagent)
blocked_by: []
---

## Question

What does installing SDV pull in (dependencies such as torch, total download and disk size), and which Python versions and operating systems (Windows, macOS, Linux) does it support? Can the heavy parts (e.g. torch, needed only for deep-learning synthesizers) be avoided if we only use GaussianCopula? How well do the options work for a non-expert user: `pip`/`pipx`, `uv tool install` / `uvx`, and a standalone executable (PyInstaller or similar) — what size would each be, and what are the known pitfalls on Windows?

## Resolution

Findings: branch `research/sdv-install-footprint`, file `docs/research/sdv-install-footprint.md`. Applies to sdv 2.2.0.

**Size and platforms**
- A default `pip install sdv` pulls in torch through `ctgan` and `deepecho`.
- On Windows it measured about 841 MB on disk, of which torch is 489 MB.
- On Linux the default install is several GB because of the CUDA packages. This comes from PyPI metadata; Linux and Mac were not measured.
- SDV supports Python 3.10 to 3.14 and has no OS limit of its own. Torch 2.15 has no Intel-Mac wheel.

**Torch-free option**
- GaussianCopula works without torch: `import sdv` works without it since SDV PR #2570.
- Tested: about 317 MB, and fit and sample work.
- There is no official light install (`sdv[light]` does not exist). A package's dependency list can't exclude torch, so a torch-free build needs an environment built without it, such as a standalone executable built from one.

**Install routes**
- `uv tool install` is the best script-based route because uv installs Python itself.
- pip and pipx need a working Python already installed.
- PyInstaller executables must be built per OS (in CI), and antivirus false positives are a known problem. Executable size was not measured; the estimate is 100–200 MB.

**Not measured**
- Executable size, total download size, and Linux or Mac installs.

**Research suggestion**
- A standalone executable per OS, built without torch, for analysts, with `uv tool install` as the second route.
- The first decision is whether to accept torch (simple, about 840 MB) or build without it (about 320 MB, more work).
