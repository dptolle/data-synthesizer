# 12: README

**What to build:** A README that lets a stranger on GitHub understand, install and use the tool within minutes. It promises nothing the tests don't prove. English only. Source of truth: the spec (`docs/SPEC.md`), "README"; ticket "What goes in the README?".

**Blocked by:** 02 (Offline proof and GitHub Actions), 05 (Free text is replaced), 08 (Label disguise), 10 (Dates), 11 (Large files)

**Status:** done

- [x] The 10 sections, in the spec's order: what it is; typical use; install; quick start; workflow; Settings file; all options; privacy; limits; license.
- [x] Install: uv, then `uv tool install` from GitHub, plus the CPU-only torch tip for Linux, using the command proven in ticket 02.
- [x] The quick start uses the Sample CSV, and its commands are run once to confirm they work.
- [x] The three promise sentences use the spec's exact wording. Each one links to the test that proves it.
- [x] It states clearly that the tool is not a legal guarantee of anonymisation (e.g. under GDPR), and that users must follow their own organisation's rules.
- [x] Limits: Structural proxy only (statistics not reliable for conclusions), one table per run, about 840 MB install, no Intel Macs.
- [x] License: MIT, plus a note that SDV is BSL-licensed and hosted commercial services are not covered.
- [x] The options table matches `--help` for both commands.
- [x] Changing any promise wording requires asking the owner first.
