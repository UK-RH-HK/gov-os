"""The narrow check's probe record: the lead's judgement, then the reviewer's return as returned."""
import json
L = "/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/log/"
OUT = "/home/usain/gov-os-worktrees/W2-42a/docs/probes/DAEO-03ub/PR-DAEO-03ub-apos-2.md"
r = json.load(open(L + "a5.json"))["result"]
front = """---
type: probe
task: DAEO-03ub
reviewer_session: 1e12d42f-b828-4265-8523-b54c8113f99b
implementer_session: d10c1d58-56f7-49d8-8bd5-d20929c6488f
test_designer_session: 8bfdec80-6a0b-4683-822f-07ef2fe3fec6
reviewer_wrote_nothing: true
commissioned_by: "orchestrator (W2-42a ticket lead)"
judged_by: "orchestrator (W2-42a ticket lead)"
judgement: pass
probed_commit: a62cd8c11439f35c3cb885087823d257d564fbda
base_commit: 692bc41bd177
decisions_applied: [DEC-1174, DEC-1164, DEC-1154, DEC-409, DEC-1010, DEC-958, DEC-1028, DEC-801, DEC-802, DEC-808]
---

# Probe record: W2-42a (DAEO-03ub), the narrow independent check of the F1/F4 fix (DEC-1164 (18), DEC-1174 (1), APOS-3/APOS-4)

## The lead's judgement

- **What was checked.** Only the change 692bc41bd..a62cd8c11: the test designer's merge c461d79de
  (tests/acceptance/W2-42a/test_w2_42a_apostrophe_2.py, 80 cases, red 28 on 692bc41bd: 21 F1 fail-opens, 7 F4
  refusals) and the engineer's fa77bb331, 1388fcec6, 07fb14799, a62cd8c11 (src/gov/guard/bash_writes.py,
  tests/unit/guard/test_w2_42a_apos2.py, docs/changes/W2-42a-evidence.md; decide.py untouched), against the CTO's
  decisions P-03ub-APOS-3 (1) (F1: a `#` inside `${…}` never starts a comment) and P-03ub-APOS-4 (a) (F4: a
  here-string holding ` #` is read; departure 1 accepted by name), DEC-409, and fail-closed. This is the CTO's own P2
  round (DEC-1164 (18)) landed on a narrow independent check (DEC-1154); it is not a review round under DEC-1010.
- **Who probed.** A fresh read-only independent auditor (Opus, high), launched by the ticket lead with
  `launch_worker.sh`; brief `.gov-runtime/scratch/lead/r4/a5.md` (JUDGEMENT.md word for word); log
  `.gov-runtime/scratch/lead/log/a5.json`. Its tripwire shows no change in W2-42a's tree; `git status` empty.
- **At this head:** `gov accept W2-42a` 883 passed, 0 failed, 2 skipped (the strict xfails); the scoped set with the
  opt-in tiers collected (GOV_TESTS_OPTIN=lifted,breadth: tests/unit/guard, tests/acceptance/W2-42a, tests/unit/hooks,
  DEC-409's cases in tests/unit/pause, tests/unit/containment/test_w1_50_freeze_flag.py, tests/acceptance/W1-50,
  W1-28, W2-16) 3751 passed, 2 xfailed, 6 failed, the 6 being W2-33's fixture copy
  (`tests/acceptance/W2-33/w2_33_support.py:376`, FileNotFoundError on the copied source's
  `template/governance/kernel/roles`), the same 6 as on 692bc41bd, outside the guard and this change.
- **READY, by code.** The verdict block passes HASH, HSTR, DEP1, DEC409 and FC. No finding is in scope, ordinary work
  yes and fails open or loses work.
- **Rows (recorded, not a round):**
  - R1 (FC, in scope, ordinary work no, fails open): `$${` opens a `${` at the second `$`, so two apostrophe comments
    can pair over a write until a later bare `}`.
  - R2 (DEC409, in scope, ordinary work no, fails open): the same `$${` misread hides the lift form.
  - R4 (out of scope, older than this change, ordinary work no, fails open): a backslash-newline between `$` and `{`.
  - R5 (out of scope, older than this change, ordinary work no, fails open): `<<` inside `${…}` on a prefix
    assignment.
  - R3 (out of scope, older than this change, ordinary work yes, fails open): the line parser splits a command at
    `<<`/`<<<` (decide.py:583), so a write argument after a here-string (`tee <<< "…" file`) is missed. It does not
    block this change; it goes to the CTO to decide (ride along under DEC-802 or a Wave 3 row).
  - Carried from the previous check (ordinary work no): F2 (a commented backtick plus a multi-line backtick hides a
    write; fails open) and F5 (a one-line backtick comment refused).
- **Judgement: pass.**

## The reviewer's record (as returned)

"""
open(OUT, "w").write(front + r.rstrip() + "\n")
print("written", OUT, r.count("```verdict"))
