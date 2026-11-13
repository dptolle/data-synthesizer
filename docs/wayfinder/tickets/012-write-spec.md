---
title: Write the build-ready spec
type: task
status: closed
assignee: dptolle
blocked_by: ["009", "010", "011"]
---

## Question

Gather every decision on the map into one spec, `docs/SPEC.md`, that a coding agent can build `csv-synth` from. It should cover: purpose, privacy rules, the processing steps (load → settings → rare merge / disguise → fit → sample → overlap check → write), commands and options, the Settings file format, messy-CSV handling, README outline, code setup and tests. Include the agent boundaries (Always / Ask first / Never). The Never list must include: never upload data, never save the fitted model, never vendor SDV. Check the spec against every closed ticket before calling it done.

## Resolution

Written as `docs/SPEC.md` (label `ready-for-agent`) with the `to-spec` template on 2026-11-13. Checked against every closed ticket.

Agreed with the owner while writing:
- Test seams: the CLI (main seam) and the overlap check (one extra seam).
- `disguise` only works on `category` columns; on any other type the tool stops.
- Our own overlap check covers personal and `text` columns, on top of SDV's checks.
- The offline test uses pytest-socket.
- The Settings file is saved as UTF-8 with BOM, using the Source CSV's separator.
- The Always / Ask first / Never rules for the building agent.
