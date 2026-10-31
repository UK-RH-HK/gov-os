---
id: DAEO-u5g6
status: open
deps: [DAEO-g0ip, DAEO-7r5e]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 4
assignee: engineer
external-ref: W2-43
tags: [wave-2, implementation, standard, wave-3, deferred]
wbs_id: W2-43
title: CI integrity and the secret-rule floor
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-7r5e
allowed_paths:
- src/gov/ci/**
- src/gov/secrets/**
- .github/workflows/**
- template/.github/workflows/**
- tests/unit/ci/**
- tests/unit/secrets/**
kpis:
  success:
  - The CI job is green on a push, with the approved tools installed by checksum [W2-H002, W2-M003, W2-M018, W2-M271].
  - CI compares the evidence note with the checkout's G3 declarations and refuses a mismatch [W2-H027].
  - Gitleaks scans every commit of the pushed range [W2-H028].
  - The template and canary secret rules hold whatever the project file says [W2-H008].
  - The store deletes securely, so removed text leaves no free-page copy [W2-H014].
  failure: []
profile: STANDARD
sources:
- DEC-729
est_loc: 140
acceptance_tests:
  path: tests/acceptance/W2-43/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- W2-H002
- H008
- H014
- H027
- H028
list_rows:
- W2-H002
- W2-H008
- W2-H014
- W2-H027
- W2-H028
- W2-L117
- W2-L170
- W2-L178
- W2-L179
- W2-L218
- W2-L222
- W2-L224
- W2-L225
- W2-M002
- W2-M003
- W2-M014
- W2-M018
- W2-M041
- W2-M043
- W2-M046
- W2-M090
- W2-M091
- W2-M154
- W2-M155
- W2-M168
- W2-M169
- W2-M171
- W2-M172
- W2-M269
- W2-M270
- W2-M271
- W2-M272
- W2-M273
---
# W2-43 CI integrity and the secret-rule floor

**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** K8 (DEC-941); the nightly is the integration check (DEC-952 1b; DEC-953 item 3).

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-43), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/ci/**`, `src/gov/secrets/**`, `.github/workflows/**`, `template/.github/workflows/**`, `tests/unit/ci/**`, `tests/unit/secrets/**`.
- **Needs first:** the owner's approval of pytest, openspec, rulesync and gitleaks on the CI runner (queued Q-8).
- **KPIs:**
  - The CI job is green on a push, with the approved tools installed by checksum [W2-H002, W2-M003, W2-M018, W2-M271].
  - CI compares the evidence note with the checkout's G3 declarations and refuses a mismatch [W2-H027].
  - gitleaks scans every commit of the pushed range [W2-H028].
  - The template and canary secret rules hold whatever the project file says [W2-H008].
  - The store deletes securely, so removed text leaves no free-page copy [W2-H014].
