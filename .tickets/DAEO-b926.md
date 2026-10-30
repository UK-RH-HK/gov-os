---
id: DAEO-b926
status: open
deps: [DAEO-g0ip, DAEO-csj8, DAEO-btt7, DAEO-swdu, DAEO-49o5]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: orchestrator
external-ref: W2-29
tags: [wave-2, integration, full]
wbs_id: W2-29
title: EXAMIN adoption on the real repository
class: integration
state_class: AUTHORITATIVE
role: orchestrator
depends_on:
- DAEO-g0ip
- DAEO-csj8
- DAEO-btt7
- DAEO-swdu
- DAEO-49o5
allowed_paths:
- docs/plan/wave-2/examin-real/**
kpis:
  success:
  - The same steps as W2-27, on the real repository, on an adoption branch the owner merges after green CI. The first real ticket closes with gov close at exit 0. Only the pinned, hash-verified release
    is used.
  failure: []
profile: FULL
sources:
- DEC-727
est_loc: 0
acceptance_tests:
  judged_by: 'its class (WBS §0 rule 1, W2-07): its named evidence files'
track: B
closes:
- Track B
list_rows: []
---
# W2-29 EXAMIN adoption on the real repository

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-29), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Needs first (DEC-727):** W2-25 passed; W2-15b reported; W2-28's verdict; the owner's go (queued Q-9); a backup of `~/EXAMIN APP` (archive and backup ref, A0); and the owner's adoption branch.
- **KPIs:** the same steps as W2-27, on the real repository, on an adoption branch the owner merges after green CI. The first real ticket closes with `gov close` at exit 0. Only the pinned, hash-verified release is used.

## Queued owner package Q-16 (recorded 2026-10-16)

EXAMIN's real repository carries 9 uncommitted entries (6 modified, 3 untracked; the owner's copy, made from it, shows the same at head `a7cf346`). An adoption works from a commit, so before W2-29 starts the owner decides what happens to them: for example, commit them on EXAMIN's own branch first, stash or move them aside and restore them after the adoption, or leave them and let the adoption's A0 backup and the untracked-file rules (W2-23) carry them. The package is raised when W2-29 is next, with W2-26's list of the entries.

**The 9 entries, by path (given by the owner, 2026-10-16).** The decision on them still comes at W2-29.
- Modified (6): `.gitignore`, `CLAUDE.md`, `archive/plans/PLAN_C.md`, `archive/plans/PLAN_D.md`, `archive/plans/PLAN_V3.md`, `product/data/cpc_subclasses.txt`.
- Untracked (3): `AGENTS.md`, `TRANSFER-2026-09-18.md`, `spec/audits/`.
- Note for the package: `CLAUDE.md` (modified) and `AGENTS.md` (untracked) are files the adoption's generation must preserve (W2-H050, W2-23).
