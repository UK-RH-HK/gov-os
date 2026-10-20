
## This repository adopted (2026-10-11; for the exit auditor; DEC-615, DEC-617, DEC-624, DEC-625)

`gov adopt --lite` ran its eight stages on `w1/integrate`. The path map moves nothing; the 116 tracked files of the old `cli/` tree were deleted from the active tree in one batch, after a fresh independent auditor's verdict (`docs/audit/wave-1/adoption-path-map-verdict.md`, pass). They stay in history, at the backup ref `refs/gov/adoption/backup/8b23e345a02b` and at the rollback ref `refs/gov/adoption/rollback/batch-1`. Stage A8 retired nothing; the adapter generation that follows it is the owner's step (DEC-616).

**The adoption's commits.** The stage commits are the tool's own and carry no trailers; the verdict's commit carries `Task:` and the auditor's role alone, as stage A5 demands.

| Commit | Subject |
|---|---|
| `f0d47572` | gov adopt --lite A0: safety baseline |
| `69946e60` | gov adopt --lite A1: inventory |
| `9e4734e2` | gov adopt --lite A2: classification |
| `89ce8e46` | gov adopt --lite A3: target path map |
| `21e8bf0e` | gov adopt --lite A4: batched plan |
| `b87ac775` | Adoption A5: the independent auditor's verdict on the path map |
| `26076eca` | gov adopt --lite A5: independent review of the path map |
| `cb2f641e` | gov adopt --lite A6: batch 1 |
| `c2d6a39e` | gov adopt --lite A6: controlled migration |
| `1c33dd28` | gov adopt --lite A8: legacy import and retirement |

**The trailers base is now `1c33dd28`** (the adoption's last commit; before: `429815b5`). The check `product-traceability-trailers` reported these 40 commits without `Implements:` at the last run before the move (`gov check` on the real store at `4e636645`); every one was named at its ticket's close:

| Commit | Ticket | Date and subject |
|---|---|---|
| `a7eb92579404` | `DAEO-0i6h` | 2026-10-09 W1-35 follow-up: acceptance cases for the orchestration skill, the ticket lead section, the five briefs, the check and the status route (DEC-537, DEC-539, DEC-541) |
| `2c71bc64b376` | `DAEO-2lwj` | 2026-10-07 Merge W1-30: gov close (DEC-453, DEC-454, DEC-470, DEC-476, DEC-480, DEC-482) |
| `6f2130c8e9e1` | `DAEO-2lwj` | 2026-10-07 Merge w1/integrate into w1/W1-30 (register v0.123) |
| `52f44aab3fd7` | `DAEO-2lwj` | 2026-10-07 Merge w1/integrate into w1/W1-30 (register v0.122, W1-26 and W1-27 follow-ups) |
| `01c195156fbc` | `DAEO-2lwj` | 2026-10-07 W1-30: gov close — containment, context, governance checks, stale evidence, traceability, probe, receipt, repair tickets, ticket closing via tk |
| `29af064698c5` | `DAEO-2lwj` | 2026-10-07 Merge w1/integrate into w1/W1-30 (judge_commits of W1-50, W1-27, W1-29 and W1-25 follow-ups) |
| `2fb783321abf` | `DAEO-2lwj` | 2026-10-07 W1-30: bring w1_07_support.py to the integrate version plus the close lines (DEC-412) |
| `e17d0fddecfd` | `DAEO-2lwj` | 2026-10-07 W1-30 round-4 cases: the traceability cases assert the ticket's own check (DEC-425) |
| `71bda7c9012b` | `DAEO-2lwj` | 2026-10-07 W1-30 round-4 cases: the ticket tool is in the suite's project; not applicable is never green (DEC-425, DEC-447) |
| `af6fe34ec733` | `DAEO-2lwj` | 2026-10-07 W1-30 round-4 cases: the suite runs without PYTHONPATH; close measures containment, context, checks and the owner's decision (DEC-453, DEC-454) |
| `93c0a79d43e8` | `DAEO-2lwj` | 2026-10-07 W1-30: update acceptance tests for owner decisions A1–A8 and items B1–B7 |
| `1d7d0af5239f` | `DAEO-2lwj` | 2026-10-07 Merge w1/integrate into w1/W1-30 (W1-26 follow-up, W1-29 hooks, W1-35 skills) |
| `451b5c324d17` | `DAEO-2lwj` | 2026-10-07 W1-30: add test for iteration field leak in escalation outcome (DEC-136) |
| `cc63360c7419` | `DAEO-2lwj` | 2026-10-07 W1-30: add judgement to unit test probe helper |
| `596cabb5e7e0` | `DAEO-2lwj` | 2026-10-07 W1-30: add checkpoints to inline test setups |
| `6828941a78e4` | `DAEO-2lwj` | 2026-10-07 W1-30: fix test infrastructure for checkpoint, probe judgement, escalation file |
| `5137c356c39c` | `DAEO-2lwj` | 2026-10-07 W1-30: fix watchdog test trigger to use valid value |
| `148f7584ccba` | `DAEO-2lwj` | 2026-10-06 Merge w1/integrate into w1/W1-30 |
| `6b2b8bc84a5a` | `DAEO-2lwj` | 2026-10-06 W1-30: add second-start acceptance tests (11 points) |
| `1cb2791a7350` | `DAEO-2lwj` | 2026-10-06 W1-30: bring w1_07_support.py to integrate version plus close lines (DEC-412) |
| `067fd58883d8` | `DAEO-2lwj` | 2026-10-06 W1-30: add probe-gate fail-open tests (reviewer findings) |
| `609f1c95b653` | `DAEO-2lwj` | 2026-10-06 W1-30: assert trailer check status, not family status |
| `0d5eb8c6010a` | `DAEO-2lwj` | 2026-10-06 W1-30 acceptance tests: gov close (49 cases, 7 files, red-first) |
| `ca5889c9c27e` | `DAEO-3ef2` | 2026-10-07 Merge W1-38: rulesync adapters and the adapter-portability check (DEC-468, DEC-469, DEC-471, DEC-481) |
| `c55e3191edb2` | `DAEO-3ef2` | 2026-10-07 Merge w1/integrate into w1/W1-38 (register v0.123, W1-30, W1-26 and W1-27 follow-ups) |
| `58380aed90e7` | `DAEO-3ef2` | 2026-10-07 Merge w1/integrate into w1/W1-38 (register v0.119, W1-27 follow-up) |
| `deead8f9e98b` | `DAEO-3ef2` | 2026-10-07 W1-38: undo the eight kernel skill edits of a95e54a3 (outside the ticket's paths) |
| `a95e54a33a45` | `DAEO-3ef2` | 2026-10-07 W1-38 implementation: rulesync adapters and .claude ownership |
| `4d664c74aa6a` | `DAEO-3ef2` | 2026-10-07 W1-38 acceptance tests: complete replacement from KPIs |
| `b8137e355486` | `DAEO-3ef2` | 2026-10-07 Merge w1/integrate into w1/W1-38 |
| `bb4edb1bab77` | `DAEO-3ef2` | 2026-10-07 W1-38 acceptance tests: rulesync adapters and .claude ownership |
| `7112564a0bc4` | `DAEO-7nne` | 2026-10-10 W1-15 acceptance tests for the round of DEC-596: the template's rulesync hooks source carries the time limit and the entry for a failed tool call (DEC-600) |
| `ac979053fd4b` | `DAEO-7nne` | 2026-10-10 W1-15 acceptance tests for the round of DEC-595: the scan in parallel and a time limit a declaration may state (DEC-600) |
| `15a0dbc4ac32` | `DAEO-emkd` | 2026-10-08 W1-02 follow-up: acceptance cases for more spellings of a read of the settings file and the held-out file (DEC-508, DEC-525); 71 red, 10 green before implementation |
| `56f1476dbfac` | `DAEO-emkd` | 2026-10-08 W1-02: acceptance cases for refused reads of the settings file and the held-out file, and for the hook-listing helper (DEC-508, DEC-525); 202 red, 164 green before implementation |
| `b355fa243d9b` | `DAEO-fygv` | 2026-10-07 W1-26 follow-up: residuals; close (DEC-463, DEC-473, DEC-474) |
| `8f0dcc8d2ae2` | `DAEO-fygv` | 2026-10-07 Merge W1-26 follow-up: a declared check flags a commit citing an unrecorded decision (DEC-463, DEC-473, DEC-474, DEC-479) |
| `73af9c20d478` | `DAEO-fygv` | 2026-10-07 Merge w1/integrate into w1/W1-26d (register v0.121) |
| `39cfeb9b3b5f` | `DAEO-fygv` | 2026-10-07 Merge w1/integrate into w1/W1-26d (register v0.120, W1-27 follow-up) |
| `e3d2cc1b3db4` | `DAEO-fygv` | 2026-10-07 W1-26 follow-up cases: a commit citing an unrecorded decision is flagged (DEC-463) |

**The auditor's findings, on the Wave 2 list:** a unit case that skips for good now that its origin is gone (`tests/unit/retrieval/test_lexical.py`); documents that point to `cli/` as present (`README.md`, `docs/SOURCES.md`, ADR-0002, one line of the work breakdown); the `carried-code` namespace's `cli/**` pattern and retention text; dead entries in the gitleaks configuration, the doctor's list of historical paths and one closed ticket. The kernel has no record type for an audit report (the verdict is typed `research`).
