---
title: What goes in the README?
type: grilling
status: closed
assignee: dptolle
blocked_by: []
---

## Question

What does the README say, and in what order, for a stranger who finds the repo on GitHub? Known parts:
- what the tool is for, and the "no data on the cloud" promise in wording that is true (see "Which privacy guarantees does the tool promise?");
- install steps with uv;
- a worked example of the `inspect` → edit → `generate` flow;
- the Settings file format;
- a note that SDV is BSL-licensed.

Open questions:
- Should it tell Linux users how to avoid the multi-GB CUDA version of torch?
- What limits should it state honestly (for example, a Structural proxy only, not statistically faithful)?
- Should a sample fake CSV be included for trying the tool?

## Resolution

Decided with the owner on 2026-11-13. The README is in English only.

**Sections, in order**
1. What it is: two sentences plus the main promise.
2. Typical use: make a synthetic copy → share it with an AI tool or a colleague → get analysis code back → run the code on the real data locally.
3. Install: uv, then `uv tool install git+https://github.com/dptolle/data-synthesizer`. Includes a short tip for Linux users on installing CPU-only torch; the exact command must be tested during building.
4. Quick start: one run on the sample CSV in `examples/`.
5. Workflow: `inspect` → edit the Settings file → `generate`.
6. Settings file: its columns (`column, type, action, format`), the types and the actions.
7. All options: a table.
8. Privacy: what is promised and what is not.
9. Limits.
10. License: MIT, plus a note that SDV is BSL-licensed and hosted commercial services are not covered.

**Promise wording** (each sentence must be backed by a test)
- "Your data never leaves your computer. After installing, the tool makes no network connections."
- "Emails, names, addresses, phone numbers, card numbers and free text from your file never appear in the output. The tool checks this before it saves."
- "The output still shows your column names, common category labels and overall patterns. Check it before you share it."

**Not a legal guarantee:** the README states clearly that the tool is not a legal guarantee of anonymisation (e.g. under GDPR), and that users must follow their own organisation's rules.

**Limits stated**
- The synthetic file has the right structure, but its statistics are not reliable for conclusions.
- One table per run.
- The install is large (about 840 MB).
- Intel Macs are not supported.
