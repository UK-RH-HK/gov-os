---
id: DAEO-xwro
status: closed
deps: []
links: [DAEO-rmhj]
created: 2026-11-07T18:26:34Z
type: task
priority: 1
assignee: engineer
external-ref: W2-141
tags: [wave-2, implementation, guard, standard]
wbs_id: W2-141
title: 'The guard refuses an engineer''s search that can reach its own ticket''s acceptance folder (Grep, Glob, and Bash recursive searches) unless the call excludes it, saying how (DEC-1093 (2))'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/guard/reads.py
- src/gov/guard/role_paths.py
- tests/unit/guard/test_w2_141*
- docs/changes/W2-141-evidence.md
# .claude/hooks/role_reads.py out of the paths: a launched session cannot edit it (DEC-315); the hook as built stays staged in docs/changes/W2-141-hook/** below, applied to the live file by the operator's ACT; the CTO's delegated decision (DEC-1112 (3))
- docs/changes/W2-141-hook/**  # the hook as built, staged for the operator's ACT (a launched worker cannot edit .claude/, DEC-315) [changed, DEC-1093 (2); DEC-1102]
- tests/unit/hooks/test_live_hook.py  # its one G14_PASSED case that S1 now refuses (the designer's round-2 P-2) [changed, DEC-1093 (2); DEC-1102]
- tests/unit/guard/test_reads.py  # its rows that expect the old refusal of a search into the own acceptance folder (the engineer's round-1 report) [changed, DEC-1093 (2); DEC-1102]
- tests/conftest.py  # the live-hook suites' temporary call-log folder (GOV_GUARD_CALLS_DIR) [changed, DEC-1108 (5); DEC-1109 (2)]
kpis:
  success:
  - 'S1 For an engineer on ticket T, a Grep or Glob tool call whose path and pattern can reach tests/acceptance/<T>/ (the repository root, tests/, tests/acceptance/, a pattern such as **/*.py) is refused unless the call excludes that folder; the refusal names the folder and says how to exclude it (for Grep a glob such as !tests/acceptance/<T>/**). Verify: planted calls, each refused or allowed as stated [DEC-1093 (2), DEC-1056, DEC-1059]'
  - 'S2 The same for Bash recursive searches: grep -r / -R, rg, ag, ack, find (with a reading action or piped into a reader) and the like, started at a folder that holds tests/acceptance/<T>/, refused unless the command excludes it (grep --exclude-dir, rg -g ''!…'', find -not -path / -prune); the refusal says how. Verify: planted commands [DEC-1093 (2)]'
  - 'S3 Nothing else changes: an engineer''s search that cannot reach its own acceptance folder, or that excludes it, is allowed; other tickets'' acceptance tests stay readable (DEC-963); the test designer, reviewer, auditor and orchestrator are unaffected; a grep for the tests'' names by pattern only stays allowed (guard4_check''s G-14 cases). Verify: the existing G-14 cases and guard4_check.py pass unchanged, plus planted allowed calls [DEC-1093 (2), DEC-963]'
  - 'S4 The suites write no real call log (DEC-1108 (5); DEC-1109 (2)): every test that runs the guard hook (the live `.claude/hooks/pretooluse.py` or the template''s copy) runs it with GOV_GUARD_CALLS_DIR set to a folder of its own under the test''s temporary folder, set once for the whole suite in tests/conftest.py (autouse, as the vector cache''s folder is) and carried by every suite that builds the hook''s environment itself; no test reads or writes ~/.gov-os/guard-calls. Verify: a scoped run of the suites that run the hook, with a scratch HOME, leaves no <scratch HOME>/.gov-os/guard-calls folder, and one planted case shows a hook call''s line lands in the temporary folder [DEC-1108 (5), DEC-1109 (2)]'
  failure:
  - 'An engineer''s search reaching its own acceptance folder allowed without an exclusion.'
  - 'A refusal that does not say how to exclude the folder.'
  - 'Any role or call other than S1 and S2 newly refused.'
  - 'A test run that appends to, creates or reads the real ~/.gov-os/guard-calls (S4) [DEC-1108 (5)]'
profile: STANDARD
sources:
- DEC-820
- DEC-826
- DEC-877
- DEC-1109
- DEC-1108
- DEC-1093
- DEC-1056
- DEC-1059
- DEC-963
- DEC-1052
- DEC-1102
- DEC-315
- DEC-1112
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W2-141/
  author: independent-test-designer (MR-3), from these KPI lines, before the engineer; planted calls against the guard's decide function, no real session
track: B
list_rows: []
needs:
- src/gov/guard/reads.py
waits_on: []
---
# W2-141 The guard: an engineer's search into its own acceptance folder

The owner's DEC-1093 (2), from the gap W2-138's engineer reported (it saw six call-site lines of its own acceptance
tests through a repository-wide Grep after its build; `.tickets/DAEO-rmhj.md`, "Built").

- **Judged (JUDGEMENT):** ordinary work, yes (a broad search is normal); consequence, fails open (G-14's separation is
  bypassed). A round is justified.
- **Timing:** tests first; built beside the experiments; applied with the guard's operator ACT at the lift's re-pin
  (the guard is the operator's, P-ACT-SPLIT (a)).
- **Until then:** every engineer brief carries the exclusion line (keep `!tests/acceptance/<own ticket>/**` in every
  Grep glob, and the matching exclusion in any recursive Bash search).
- **Where:** `src/gov/guard/reads.py` already judges Grep and Glob calls (its tool-name branches) and recursive Bash
  reads; the engineer extends them for the engineer's own acceptance folder.
- **Est.:** about 120 lines with tests, half a day with its review.

**The hook side (the CTO, 2026-11-09) [changed, DEC-1093 (2); DEC-1102]:** the designer found that integrate's
`decide` already refuses the broad searches; the gap W2-138 hit is in the live hook `.claude/hooks/role_reads.py`, which
lets a search from a folder above through. That hook is now in the paths. A launched worker cannot edit `.claude/`
(the launcher's DEC-315 deny rules, whatever `allowed_paths` names), so the engineer builds the changed hook as a
whole-file copy at `docs/changes/W2-141-hook/role_reads.py` and tests it there; the CTO prepares the ACT from the
merged branch and the owner's operator applies it to `.claude/hooks/role_reads.py` at the lift's re-pin. The
acceptance tests load the staged copy when it exists, else the live hook. The exclusion line's grep form is the
base name (`--exclude-dir=<WBS id>`; GNU grep matches the base name), fixed in EMG-common (the designer's P-1).

**The designer's round-2 points settled (the CTO, 2026-11-09) [changed, DEC-1093 (2); DEC-1102]:** P-1: the live hook
routes only Read, NotebookRead, Grep and Bash to `role_reads` (`.claude/hooks/pretooluse.py`, the G-14 block), so S1's Glob half
needs Glob added there: the engineer stages that one-word change as `docs/changes/W2-141-hook/pretooluse.py` (a whole-file
copy), applied in the same operator ACT. P-2: `tests/unit/hooks/test_live_hook.py`'s `G14_PASSED` case
`grep -r foo tests/` contradicts S1; the engineer revises it (the unit test is in the paths). The CTO checks
`guard4_check.py`'s cases against S1 when preparing the ACT.

[DEC-1093]

**D-6 part 2 placed here (CTO, 2026-11-09; DEC-1108 (5), DEC-1109 (2)):** S4, its failure line and the `tests/conftest.py` path are DECIDED-NOT-DONE row 60 ("the live-hook suites' temporary folder ... W2-141's acceptance file by its designer"). Tests only: W2-141's test designer on `w2/W2-141-d6-tests`, one review; plan item D in `governance/project/orchestration/packages/LIFT-1/D6-PART2.md`. No product code changes (the hook already reads GOV_GUARD_CALLS_DIR, ACT-GUARD-CALLLOG-1).

**The staged hook rebuilt on ACT-SETS-GLOBS-1's hook (CTO's helper, 2026-11-10; DECIDED-NOT-DONE row 78, DEC-1112 (3)):** `beec1f2f8`, review READY by verdict.py (`.gov-runtime/scratch/orchestrator/reviews/W2-141-rebase-review.md`). Rows:
- F1 (in, other): the README's rebuild note names rules 2b, 2c and 2d but not the call log or `Narrow`.
- F2 (in, other): the rehearsal's "failures: 0" does not count the suites or the replay compare's exit; the README's "Before the ACT" omits `drafts/g14/test_g14.py`'s four engineer near-miss cases (searches from above), which S1/S2 now refuse: the re-pin ACT revises them or expects them red.
- F3 (out, other): the README's rollback does not say to commit it and merge it into the worktrees.
- F4 (out, other): the pair was rehearsed with today's pin, not the re-pin's: re-run `drafts/w2-141-rebase/rehearse.sh` with the candidate pin when preparing the ACT.
- D1 (the guard, other): the live guard refuses a git diff of two blob references (`<rev>:<path>`), since `reads.py`'s `patched()` resolves each revision word as a commit; a false refusal (it also refused a Bash line that only carried that text in a heredoc). `git show` into scratch and `git diff --no-index` work.
