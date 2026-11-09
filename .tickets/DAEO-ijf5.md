---
id: DAEO-ijf5
status: in_progress
deps: []
links: []
created: 2026-11-09T21:30:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-150
tags: [wave-2, implementation, memory, refactor, standard]
wbs_id: W2-150
title: 'Memory''s import closure free of the gates: E-2''s four coupling edges untangled (P1-6 item 1, D-6 part 2; DEC-1039 (2), DEC-1109 (2))'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/util/**
- src/gov/store/loader.py
- src/gov/close/fingerprint.py
- src/gov/close/select.py
- src/gov/guard/decide.py
- src/gov/guard/runs.py
- src/gov/guard/reads.py
- src/gov/tasks/tickets.py
- src/gov/retrieve/command.py
- src/gov/decisions/__init__.py
- src/gov/decisions/register.py
- src/gov/secrets/__init__.py
- src/gov/retrieval/measure.py
- tests/unit/util/**
- docs/changes/W2-150-evidence.md
kpis:
  success:
  - 'S1 Memory''s static import closure holds none of the gates: following every import statement (module level and inside functions) from the memory modules (every module of gov.retrieval, gov.retrieve, gov.store and gov.secrets) through src/gov reaches no module of gov.close or gov.guard and not gov.decisions.checker. Verify: a static walk of src/gov''s imports on the branch [DEC-1039 (2), DEC-1040 (1), P1-PLAN P1-6 item 1]'
  - 'S2 The four edges, each gone: store/loader.py no longer imports gov.close.fingerprint (of_commit''s path classification, guard.decide''s _match_pattern and tasks.tickets'' TICKETS_REL live in gov.util or gov.store); retrieve/command.py no longer pulls gov.decisions.checker (gov.decisions'' __init__ imports its submodules lazily, or leave_out moves to gov.store or gov.util); secrets/__init__.py no longer imports gov.guard.runs (runs.root moves to gov.util); retrieval/measure.py no longer imports gov.guard.reads (the evaluation-set reading it uses moves to gov.util or gov.store). Verify: grep of the four files and the static walk [P1-PLAN §A P1-6, INVESTIGATION-1 part E E-2]'
  - 'S3 Public calls unchanged: every moved name stays importable from its old module with the same behaviour (gov.close.fingerprint.of_commit, gov.guard.decide._match_pattern, gov.tasks.tickets.TICKETS_REL, gov.guard.runs.root, gov.decisions.register.leave_out, gov.guard.reads.evaluation_sets and the names measure.py used); no acceptance test changes. Verify: the touched packages'' existing unit and acceptance suites pass unchanged, scoped (no full suite) [DEC-1040 (1)]'
  - 'S4 The guard''s hot path no slower and no different: the guard''s decisions on its own unit suite are unchanged, and the hook''s import of gov.guard.decide pulls no new module beyond gov.util. Verify: tests/unit/guard scoped; the CTO''s hook_timing.py before and after, median of five [DEC-1052 basis (3)]'
  - 'S5 The unit tests move with their helpers: each moved helper has its unit cases under tests/unit/util/ (the old ones stay where they test the old name) [DEC-136, P1-PLAN P1-6]'
  failure:
  - 'A gate (close, guard, decisions.checker) still reached from memory''s closure.'
  - 'A moved name no longer importable from its old module, or a behaviour change in any guard decision, close fingerprint or selection.'
  - 'An acceptance test edited to fit the move.'
profile: STANDARD
sources:
- DEC-1039
- DEC-1040
- DEC-1109
- DEC-1052
- DEC-136
est_loc: 250
acceptance_tests:
  path: tests/acceptance/W2-150/
  author: 'independent-test-designer (MR-3), from these KPI lines before the engineer: a static import walk over src/gov (ast, every import statement, function-level included) from the memory modules, asserting S1 and S2; importability of each old name (S3); never the hidden half, no GPU, no network'
track: B
list_rows: []
needs: []
waits_on: []
---
# W2-150 Memory's import closure free of the gates (E-2's four edges)

Card: P1-PLAN §A P1-6 item 1 and §D (DEC-1039 (2), DEC-1040 (1)), the code tidy-up's part 2 restarted by DEC-1109 (2).
INVESTIGATION-1 part E's E-2 measured memory's closure at 18,063 lines in 77 modules, almost all of it the gates'
code brought in by four edges for small helpers: `store/loader.py → close.fingerprint.of_commit → close.select →
guard.decide._match_pattern` and `tasks.tickets`; `retrieve/command.py → gov.decisions` (its `__init__` pulls
`checker → guard.containment_merge`); `secrets/__init__.py → guard.runs → guard.decide`; `retrieval/measure.py →
guard.reads`. Untangled, EXAMIN's copy of memory is about 7,600 product lines, and a memory diff stops selecting the
close and guard suites (the CTO checks `select_tests.py` on a `src/gov/retrieval/` diff).

- **Why a new ticket (checked):** the four edges cross W2-92 (`loader.py`), W2-55 (`decisions/**`, `retrieve/**`),
  W2-61h (`measure.py`) and the guard's and close's own files; no open ticket holds them together. D-6 part 1
  (`8305dd13`) ran under the orchestrator's task; part 2 gets its own ticket so its tests come first.
- **The move (P1-PLAN §A):** `of_commit`'s path classification, `_match_pattern`, `TICKETS_REL`, `runs.root` and
  `leave_out` into `gov.util`/`gov.store`; `gov.decisions/__init__` made lazy; the old modules re-import the moved
  names. `retrieval/synthesis.py` stays (DEC-953). `guard/decide.py` changes only by importing from `gov.util`.
- **Plan:** `governance/project/orchestration/packages/LIFT-1/D6-PART2.md` item E. Tests first, then the engineer,
  one review. Overlaps: W2-139/W2-140 touch none of these paths.

**Filed 2026-11-09 by the CTO (DEC-1109 (2)).**
