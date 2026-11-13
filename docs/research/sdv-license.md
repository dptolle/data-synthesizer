# Is SDV's license OK for a public tool?

Researched 2026-11-13. This is a reading of the license texts, not legal advice.

## Short answer

Yes. A free, MIT-licensed CLI that installs SDV with `pip` and runs on the user's own machine is allowed. This holds for use at work and for commercial use. The only thing SDV forbids is running it as a "Synthetic Data Service" for other people.

## What SDV's license says

SDV uses the Business Source License 1.1 (BSL, SPDX id `BUSL-1.1`). PyPI lists SDV 2.2.0 as `BUSL-1.1`.
Source: https://github.com/sdv-dev/SDV/blob/main/LICENSE and https://pypi.org/pypi/sdv/json

### Additional Use Grant (the key part)

Quoted from the LICENSE file:

> You may make use of the Licensed Work, and derivatives of the Licensed Work, provided that you do not use the Licensed Work, or derivatives of the Licensed Work, for a Synthetic Data Service.
>
> A "Synthetic Data Service" is a commercial offering that allows third parties (other than your employees and contractors) to access the functionality of the Licensed Work so that such third parties directly benefit from the data specification, data transformation, machine learning, or synthetic data creation features of the Licensed Work.

Plain reading:

- Production use is allowed. This includes commercial use inside a company.
- Forbidden: selling or offering a commercial service where outside customers use SDV's features (for example a paid hosted "make synthetic data" web service or API).
- Employees and contractors do not count as third parties.

### Other terms in the same file

- You may copy, modify, redistribute and make non-production use. The Additional Use Grant adds production use.
- "All copies of the original and modified Licensed Work ... are subject to this License." You must "conspicuously display this License on each original or modified copy of the Licensed Work."
- Any use that breaks the license ends your rights, for all versions.
- No rights to DataCebo trademarks or logos.
- Software is "AS IS", no warranty.
- Change Date: four years after each version's release (see https://github.com/sdv-dev/SDV/releases). The Change License is MIT. Each version becomes MIT after about four years.
- If your use does not comply, you must buy a commercial license or stop using it.

## What this means for our tool

| Question | Answer | Why |
|---|---|---|
| Can the tool depend on SDV via pip? | Yes | A dependency is not a "Synthetic Data Service". We do not copy SDV code. |
| Can anyone install and run it, including at work? | Yes | Production and commercial use are covered by the grant. Local use by the user is their own use. |
| Can our tool stay MIT? | Yes | MIT covers our code only. SDV stays under BSL. pip installs SDV with its own LICENSE file. |
| Must we vendor or copy SDV? | No, and we should not | Copies must carry the BSL and stay under it. A pip dependency avoids this. |
| Is a hosted version OK? | No (unless licensed) | A paid web or API service for outsiders is the forbidden case. |

Obligations that pass to users: none beyond SDV's own license, which they accept when they install SDV. We found no notice or attribution rule that the README must repeat. Still, it is good practice to say in the README that the tool uses SDV, which is BSL-licensed, and to link the license. This is advice, not a requirement from the license.

Edge cases to keep in mind:

- If someone wraps our tool in a commercial hosted service, that person is the one who breaks the grant, not us. Our README can warn about it.
- The license says "derivatives". A tool that only imports SDV through pip is a normal dependent, not a copy of the work. The license text does not define this further. If we ever vendor SDV code, re-check.
- The SDV docs describe the public edition as for "small applications" and recommend SDV Enterprise "for enterprise use cases". This is marketing language, not part of the license text. Source: https://docs.sdv.dev/sdv/explore/sdv-community
- I did not find an official DataCebo license FAQ. `datacebo.com/blog/license-faq/` returns 404, and the SDV docs do not discuss commercial use. For a firm answer on a gray case, ask DataCebo. The LICENSE file is the controlling source.

## DataCebo sub-dependencies

SDV 2.2.0 requires `rdt`, `copulas`, `ctgan`, `deepecho` and `sdmetrics` (https://pypi.org/pypi/sdv/json).

| Package | License | Additional Use Grant forbids | Source |
|---|---|---|---|
| rdt | BSL 1.1 | a "Data Transform Service" (commercial offering for third parties) | https://github.com/sdv-dev/RDT/blob/main/LICENSE |
| copulas | BSL 1.1 | a "Synthetic Data Creation Service" | https://github.com/sdv-dev/Copulas/blob/main/LICENSE |
| ctgan | BSL 1.1 | a "Synthetic Data Creation Service" | https://github.com/sdv-dev/CTGAN/blob/main/LICENSE |
| deepecho | BSL 1.1 | a "Synthetic Data Creation Service" | https://github.com/sdv-dev/DeepEcho/blob/main/LICENSE |
| sdmetrics | MIT | nothing | https://github.com/sdv-dev/SDMetrics/blob/main/LICENSE |

All four BSL ones have the same shape: any use is fine unless it is a commercial service for outside third parties. Each has a four-year change date to MIT. PyPI metadata agrees (`BUSL-1.1` for the four, `MIT` for sdmetrics), for example https://pypi.org/pypi/ctgan/json.

## Is there a real problem?

No. If the tool stays a local CLI, the license is not a blocker. Remaining risks are only: (1) someone turns it into a paid hosted service, (2) our team later vendors SDV code, (3) a user's company has a blanket policy against non-OSI licenses. The BSL is "not an Open Source license" (the LICENSE says so), so strict corporate policies may block it even though the grant allows the use.

## Alternatives (only if risk 3 matters)

Single-table tabular synthesis libraries and their licenses, read from PyPI metadata. Check each repo's LICENSE before relying on it.

| Library | License | Notes | Source |
|---|---|---|---|
| synthcity | Apache-2.0 | Many models, heavy deps | https://pypi.org/pypi/synthcity/json |
| mostlyai (and mostlyai-engine) | Apache-2.0 | Local engine for tabular data | https://pypi.org/pypi/mostlyai/json |
| smartnoise-synth | MIT | Differential privacy focus | https://pypi.org/pypi/smartnoise-synth/json |
| be-great (GReaT) | MIT | LLM based, needs a model download | https://pypi.org/pypi/be-great/json |
| DataSynthesizer | MIT | Simple, older | https://pypi.org/pypi/datasynthesizer/json |
| synthpop (Python) | BSD (version not stated) | Early version 0.1.1, unverified | https://pypi.org/pypi/synthpop/json |
| ydata-synthetic | GPL-3.0+ | Copyleft, a poor fit for an MIT tool | https://pypi.org/pypi/ydata-synthetic/json |
| gretel-synthetics | Gretel "source-available", "Free To Use But Restricted" | Not open source | https://pypi.org/pypi/gretel-synthetics/json |

Older `ctgan` releases were MIT before the move to BSL. We did not verify which version changed, so do not rely on this.

## Answer

- Using SDV as a pip dependency in a free, MIT, local-only CLI is allowed, for anyone, at work and commercially.
- The one forbidden thing is offering SDV's features to outside third parties as a commercial service. A local CLI is not that.
- No notice or attribution duty passes to users beyond SDV's own license, which pip ships. Do not vendor SDV. A README note that SDV is BSL-licensed is recommended, with a warning that hosted commercial services are not covered.
- rdt, copulas, ctgan and deepecho are BSL with the same kind of grant. sdmetrics is MIT.
- Decision: go ahead with SDV. Switch only if a target user group bans non-OSI licenses. Then use Apache-2.0 or MIT options (synthcity, mostlyai, smartnoise-synth), and avoid GPL and "source-available" ones.
