---
title: Is SDV's license OK for a public tool?
type: research
status: closed
assignee: claude (research subagent)
blocked_by: []
---

## Question

SDV is published under the Business Source License (BSL), not a standard open-source license. Can a free, public, MIT-licensed GitHub tool depend on SDV and be installed and used by anyone, including at work and for commercial purposes? What exactly does the BSL forbid, and does any SDV-related obligation (notices, attribution, restrictions the README must state) pass on to our users? If the license is a real problem, which alternative libraries for single-table tabular synthesis exist, and what are their licenses?

## Resolution

**Yes, use SDV.** Findings: branch `research/sdv-license`, file `docs/research/sdv-license.md`.

- SDV is under BSL 1.1. Its Additional Use Grant allows every use except running a commercial "Synthetic Data Service", meaning one where outside third parties use SDV's features. A free, MIT-licensed, local tool installed with pip is fine for anyone, including at work and for commercial purposes.
- Depend on SDV through pip. Never vendor (copy) it into this repo, because copies must carry the BSL.
- rdt, copulas, ctgan and deepecho are also BSL 1.1 with similar grants. sdmetrics is MIT. Each BSL version becomes MIT four years after its release.
- The README should state that SDV is BSL-licensed and that hosted commercial services are not covered.
- Remaining risk: some employers ban licenses that aren't OSI-approved. Fallback libraries if needed: synthcity, mostlyai, smartnoise-synth, be-great, DataSynthesizer (Apache-2.0 or MIT). Avoid ydata-synthetic (GPL) and gretel-synthetics.
- No official DataCebo license FAQ was found. The answer rests on the LICENSE files. This is not legal advice.
