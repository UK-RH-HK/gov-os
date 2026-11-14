import json
from pathlib import Path

W = Path("/home/usain/gov-os-worktrees/W2-130")
log = json.loads((W / ".gov-runtime/scratch/lead/log/aud-pin3-1.json").read_text())
r, sess = log["result"], log["session_id"]
head = "17487b4700861003d208de7f256a7d1e479c9562"
front = f"""---
type: probe
task: DAEO-q8cl
reviewer_session: {sess}
implementer_session: "independent-test-designer session 996a5e96-496b-487c-ae07-48ef600dfe94 (commit 83285c3c52c32b7f96936b815e2656604a6d97cb)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: {head}
decisions_applied: [DEC-1156, DEC-1164, DEC-1073, DEC-1010]
---

# Probe record: W2-130 (DAEO-q8cl), pin run 3's narrow independent check (a decided-behaviour test revision)

A fresh independent-auditor session (`{sess}`) ran on `claude-opus-5-5` at high effort, class C2, read-only, with
JUDGEMENT.md word for word in its brief. It probed head `{head[:12]}` of `w2/W2-130` (the lead's merge of
`w2/W2-130-tests`), narrow: this revision only, since `aafaf6259d10`. It wrote nothing (`git status` empty; sandbox
trial file absent; tripwire clean).

What it probed: the CTO's answers under DEC-1164 (18) and DEC-1156 (7) (listed for the owner's reading):
P-W2-130-PIN2-HEAD (a) (the two S4 cases that still read HEAD,
`test_s4_closed_missing_lists_per_closed_ticket_the_ids_its_sources_lack` and
`test_s4_no_record_lists_per_ticket_ids_that_name_no_record`, pinned at `counts-after.measured_at` with the pinned
tree's own `gov links`), and row F1 riding along (`variant_findings`, used by the S3/F3 cases, runs the marks commit's
own tool). One independent test designer commit, `83285c3c5`, in `tests/acceptance/W2-130/` only (README prose,
`conftest.py`, `test_w2_130_audit.py` docstring, `test_w2_130_sources.py`); no record, ticket, source or map row edited;
every case name kept. The CTO also asked whether any W2-130 or W2-175 case still reads a value that a later ticket event
or approved change moves (item 6).

Its verdict is **PASS**: six items pass, two findings, none blocking (neither in scope with ordinary work yes and fails
open or loses work).

## The lead's judgement of the findings

- **F1** (out of scope: two W2-130 S7 cases,
  `test_w2_130_lessons.py::test_s7_the_record_lists_each_lesson_with_its_sources_and_the_place_it_says_it_came_from` and
  `test_w2_130_lessons.py::test_s7_the_lessons_commit_changes_only_lessons_each_by_the_one_added_sources_line`, compare
  the record's lesson list with the lessons in the working tree; a lesson added after the land turns both red, shown by
  a scratch commit). Ordinary work: yes, because lessons are added routinely by approved changes. Consequence: other (a
  false red on a re-run of `gov accept W2-130`; fails closed, nothing lost). A row, brought to the CTO in the lead's
  return.
- **F2** (out of scope: W2-175's S1 to S5 read the role templates in the working tree and S5 asserts `version: 1.0.1`;
  the next approved template delta turns S5 red, shown by a scratch commit setting role-cto.md to 1.0.2). Ordinary work:
  yes, because template deltas go through CIT-P routinely. Consequence: other (a false red; fails closed, nothing lost).
  A row for the CTO; `test_w2_175_templates.py` is outside W2-130's paths.
- The cases the auditor lists as moved by HEAD-wide reads (S1, S2, S6, F2's drift list, S2/S6/S7's `head_findings`)
  judge HEAD itself; that is their point, as the test designer's commit body also states.

The lead's own runs at `{head[:12]}`: the two changed test files (sources and audit) 25 passed; `gov accept W2-130` 81
passed, 0 failed (all twelve lines pass); `gov accept W2-175` 51 passed, 0 failed; the scoped run (DEC-968) of
`tests/acceptance/W2-130` and `tests/acceptance/W2-175` 132 passed.

## The auditor's return, word for word

"""
out = W / "docs/probes/DAEO-q8cl/PR-DAEO-q8cl-pin3.md"
out.write_text(front + r.rstrip() + "\n", encoding="utf-8")
print("ok", out)
