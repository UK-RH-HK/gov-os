---
id: DAEO-49o5
status: in_progress
deps: [DAEO-g0ip, DAEO-ha8z]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: engineer
external-ref: W2-16
tags: [wave-2, implementation, full]
wbs_id: W2-16
title: Immutable, hash-pinned releases (CAP-43.b lite)
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-ha8z
allowed_paths:
- src/gov/lock/**
- src/gov/release/**
- copier.yml
- template/framework.lock*
- tests/unit/lock/**
- tests/unit/release/**
- docs/releases/**
- src/gov/check/commands.py
kpis:
  success:
  - 'gov release <version> builds a release from a clean w2/integrate commit [CAP-43.b lite]. Its manifest holds: the semantic version and the commit; every shipped file with its sha256; the wheel hash,
    the CLI version and the schema versions; release notes; the manifest''s own hash'
  - The owner tags the release commit (agents never tag); the tag is not signed (CAP-02.c stays in Wave 3, DEC-722).
  - 'A release is immutable: building the same version from another commit, or changing a file after release, is refused [CAP-43].'
  - Framework.lock records the release version and manifest hash, at copy as well as at update. A missing lock fails, and a project cannot silence the lock comparison [W2-L227, W2-H029 (the silencing part),
    W2-M174, W2-M175].
  - The vendored skills carry their licence and version in the release [W2-L002, W2-L014].
  failure:
  - A release whose files or manifest do not match their hashes is refused by gov install, gov update and gov doctor.
profile: FULL
sources:
- CAP-43.b
- DEC-722
- CAP-02.c
- CAP-43
- DEC-752
- DEC-753
- DEC-954
est_loc: 150
acceptance_tests:
  path: tests/acceptance/W2-16/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- CAP-43.b (lite
- DEC-722)
list_rows:
- W2-H029
- W2-L002
- W2-L014
- W2-L227
- W2-M174
- W2-M175
---
# W2-16 Immutable, hash-pinned releases (CAP-43.b lite)

**DEC-954 Q8c:** cuts a numbered, frozen release that W2-81 and EXAMIN's copy install; the owner tags it. Finished after ACT 1.

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-16), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Needs first:** W2-49 (Contract v4.2).
- **Allowed paths:** `src/gov/lock/**`, `src/gov/release/**` (new), `copier.yml`, `template/framework.lock*`, `tests/unit/lock/**`, `tests/unit/release/**`, `docs/releases/**`, `src/gov/check/commands.py` (the one line that records `release`, made after W2-20 closes; DEC-753).
- **KPIs, success:**
  - `gov release <version>` builds a release from a clean `w2/integrate` commit [CAP-43.b lite]. Its manifest holds:
    - the semantic version and the commit;
    - every shipped file with its sha256;
    - the wheel hash, the CLI version and the schema versions;
    - release notes;
    - the manifest's own hash.
  - The owner tags the release commit (agents never tag); the tag is not signed (CAP-02.c stays in Wave 3, DEC-722).
  - A release is immutable: building the same version from another commit, or changing a file after release, is refused [CAP-43].
  - `framework.lock` records the release version and manifest hash, at copy as well as at update. A missing lock fails, and a project cannot silence the lock comparison [W2-L227, W2-H029 (the silencing part), W2-M174, W2-M175].
  - The vendored skills carry their licence and version in the release [W2-L002, W2-L014].
- **KPIs, failure:** a release whose files or manifest do not match their hashes is refused by `gov install`, `gov update` and `gov doctor`.
- **DEC-752 (owner, 2026-10-17):** a stacked early start on W2-49's held branch; it merges W2-49's later changes in and re-verifies, and merges only after W2-49 has closed.
