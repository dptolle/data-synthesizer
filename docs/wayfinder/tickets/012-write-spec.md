---
title: Write the build-ready spec
type: task
status: open
assignee:
blocked_by: ["009", "010", "011"]
---

## Question

Gather every decision on the map into one spec, `docs/SPEC.md`, that a coding agent can build `csv-synth` from. It should cover: purpose, privacy rules, the processing steps (load → settings → rare merge / disguise → fit → sample → overlap check → write), commands and options, the Settings file format, messy-CSV handling, README outline, code setup and tests. Include the agent boundaries (Always / Ask first / Never). The Never list must include: never upload data, never save the fitted model, never vendor SDV. Check the spec against every closed ticket before calling it done.
