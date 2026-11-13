---
title: What goes in the README?
type: grilling
status: open
assignee:
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
