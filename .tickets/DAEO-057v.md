---
id: DAEO-057v
status: open
deps: [DAEO-g0ip, DAEO-49o5]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 4
assignee: engineer
external-ref: W2-18
tags: [wave-2, implementation, standard, wave-3, deferred]
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
  - 'gov install <version> installs the CLI and kernel of a hash-verified release into a per-repository tool environment pinned to the release''s wheel hash, never an editable install. Verify: in a planted repository, `gov install <version>` exits 0; the tool environment''s record holds the release''s wheel hash and the hash check passed; the installed package metadata shows no editable install; a planted release with a wrong wheel hash is refused and installs nothing [CAP-43]'
  - 'gov doctor in a product repository fails when its gov is an editable install, resolves to another repository''s src/, or differs from framework.lock. Verify: three planted product repositories (editable install, gov resolving to another repository''s src/, a gov differing from framework.lock) each make `gov doctor` exit non-zero naming the case; a repository with the pinned gov matching framework.lock exits 0 [CAP-43, W2-H021]'
  - 'The guard and kernel hooks a session runs are the pinned release''s code, not the session tree''s. Verify: in a planted product repository holding its own differing copy of the guard, a hook call prints the path of the module it ran and that path is inside the pinned release''s environment, never the session tree [W2-M123]'
  - 'The kernel hooks import the pinned gov, never a product''s own package named gov. With no gov installed, they say so clearly instead of blocking every call. Verify: a planted product repository with its own package named gov: the hook imports the pinned one (its printed module path); a planted environment with no gov: the hook prints one clear message naming the missing gov and the call is not blocked [W2-H032, W2-M279, W2-L172, W2-L230, W2-L173,
    W2-L174]'
  - 'Two repositories on the machine can run two different releases side by side. Verify: two planted repositories pinned to releases A and B: `gov --version` run in each prints A in one and B in the other, with no change to either after running both [CAP-43]'
  failure:
  - 'A product session that imports this repository''s src/gov is refused by doctor and reported. Verify: a planted product session whose path resolves to this repository''s src/gov: `gov doctor` exits non-zero and names the import; it must never exit 0 for that case.'
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

**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** The rest of K7 (DEC-941 item 3); W2-81 and EXAMIN install W2-16's release (DEC-954 Q8c).

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-18), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/install/**` (new), `src/gov/doctor/install*`, `template/governance/kernel/hooks/**` (the import fallback only), `tests/unit/install/**`.
- **KPIs, success:**
  - `gov install <version>` installs the CLI and kernel of a hash-verified release into a per-repository tool environment pinned to the release's wheel hash, never an editable install [CAP-43].
  - `gov doctor` in a product repository fails when its `gov` is an editable install, resolves to another repository's `src/`, or differs from `framework.lock` [CAP-43, W2-H021].
  - The guard and kernel hooks a session runs are the pinned release's code, not the session tree's [W2-M123].
  - The kernel hooks import the pinned `gov`, never a product's own package named `gov`. With no `gov` installed, they say so clearly instead of blocking every call [W2-H032, W2-M279, W2-L172, W2-L230, W2-L173, W2-L174].
  - Two repositories on the machine can run two different releases side by side [CAP-43].
- **KPIs, failure:** a product session that imports this repository's `src/gov` is refused by doctor and reported.

**D9-FATES (DEC-1083):** Wave 3 by DEC-1083 (D9-FATES, as P1-PLAN §C); the status is kept.
