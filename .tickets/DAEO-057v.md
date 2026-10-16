---
id: DAEO-057v
status: open
deps: [DAEO-g0ip, DAEO-49o5]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: engineer
external-ref: W2-18
tags: [wave-2, implementation, standard]
wbs_id: W2-18
title: 'Pinned install: a product repository runs a fixed release, never the development copy'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-49o5
allowed_paths:
- src/gov/install/**
- src/gov/doctor/install*
- template/governance/kernel/hooks/**
- tests/unit/install/**
kpis:
  success:
  - gov install <version> installs the CLI and kernel of a hash-verified release into a per-repository tool environment pinned to the release's wheel hash, never an editable install [CAP-43].
  - gov doctor in a product repository fails when its gov is an editable install, resolves to another repository's src/, or differs from framework.lock [CAP-43, W2-H021].
  - The guard and kernel hooks a session runs are the pinned release's code, not the session tree's [W2-M123].
  - The kernel hooks import the pinned gov, never a product's own package named gov. With no gov installed, they say so clearly instead of blocking every call [W2-H032, W2-M279, W2-L172, W2-L230, W2-L173,
    W2-L174].
  - Two repositories on the machine can run two different releases side by side [CAP-43].
  failure:
  - A product session that imports this repository's src/gov is refused by doctor and reported.
profile: STANDARD
sources:
- CAP-43
est_loc: 140
acceptance_tests:
  path: tests/acceptance/W2-18/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- CAP-43
- W2-H032
- W2-H021
list_rows:
- W2-H021
- W2-H032
- W2-L047
- W2-L172
- W2-L173
- W2-L174
- W2-L230
- W2-L231
- W2-M069
- W2-M123
- W2-M127
- W2-M206
- W2-M279
- W2-M318
---
# W2-18 Pinned install: a product repository runs a fixed release, never the development copy

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-18), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/install/**` (new), `src/gov/doctor/install*`, `template/governance/kernel/hooks/**` (the import fallback only), `tests/unit/install/**`.
- **KPIs, success:**
  - `gov install <version>` installs the CLI and kernel of a hash-verified release into a per-repository tool environment pinned to the release's wheel hash, never an editable install [CAP-43].
  - `gov doctor` in a product repository fails when its `gov` is an editable install, resolves to another repository's `src/`, or differs from `framework.lock` [CAP-43, W2-H021].
  - The guard and kernel hooks a session runs are the pinned release's code, not the session tree's [W2-M123].
  - The kernel hooks import the pinned `gov`, never a product's own package named `gov`. With no `gov` installed, they say so clearly instead of blocking every call [W2-H032, W2-M279, W2-L172, W2-L230, W2-L173, W2-L174].
  - Two repositories on the machine can run two different releases side by side [CAP-43].
- **KPIs, failure:** a product session that imports this repository's `src/gov` is refused by doctor and reported.
