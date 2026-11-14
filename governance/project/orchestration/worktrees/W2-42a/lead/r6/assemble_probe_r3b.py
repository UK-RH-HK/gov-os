"""The R3 F1 follow-up's narrow check probe record: the lead's judgement, then the reviewer's return as returned."""
import json
L = "/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/log/"
OUT = "/home/usain/gov-os-worktrees/W2-42a/docs/probes/DAEO-03ub/PR-DAEO-03ub-r3b.md"
r = json.load(open(L + "a7.json"))["result"]
front = """---
type: probe
task: DAEO-03ub
reviewer_session: 3d1b1a34-54a8-45b7-84ba-b5091bd2bf12
implementer_session: 74eb50b0-f21e-4ada-8a7d-fbbf0d615105
implementer_session_first_batch: e653e1fc-4fb7-442d-990a-93d7eb49335b
test_designer_session: 39ec021b-6fb2-43eb-8c8f-4c84cf8ac629
test_designer_second_batch_session: 1eee15f0-14c5-4531-8589-930893293879
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 9196ce961adf7d4a0d314dc6012cde8c84d2bca7
base_commit: 209ec8464f9e0c7a148a823279b60323ce348463
decisions_applied: [DEC-1164, DEC-1174, DEC-1154, DEC-409, DEC-958, DEC-1028, DEC-136, DEC-968, DEC-808]
---

# Probe record: W2-42a (DAEO-03ub), the narrow independent check of the R3 F1 follow-up (DEC-1164 (18), DEC-1154)

## The lead's judgement

- **What was checked.** Only the change 209ec8464..9196ce961, the CTO's answer (a) to the R3 check's F1
  (PR-DAEO-03ub-r3.md). Under the decided rule, read-only here-string forms with an expanded text stay free:
  `read`/`mapfile`/`readarray` and a loop's here-string are data, and so is an expanded text given to the data readers
  `sed`, `awk`, `bc`, `grep`, `wc`, `cut`, `tr` and `sort`. A writing `sed`/`awk` script is judged on its script. Shells,
  `xargs`, `source`, `eval` and the readers not named keep R3's fail-closed rule, and nothing R3's cases refuse becomes
  allowed. The change is two test-design batches and two engineer commits:
  - merge 289432d3a (td-8): tests/acceptance/W2-42a/test_w2_42a_here_string_ro.py, 53 cases, red 21 on 209ec8464;
  - eng-5's 885b0d0f6;
  - merge 98eff3c84 (td-9): test_w2_42a_here_string_ro_2.py, 23 cases, red 17 on 885b0d0f6. These pin the lead's own
    finding at 885b0d0f6: a read-bound variable used as a command's name, and `mapfile`/`readarray -C` callbacks;
  - eng-6's 9196ce961.

  Both batches added README map rows. The engineer commits touch src/gov/guard/bash_writes.py, the unit files
  tests/unit/guard/test_w2_42a_here_string_ro*.py and docs/changes/W2-42a-evidence.md. This is the CTO's own P2
  follow-up (DEC-1164 (18)), landed on a narrow independent check (DEC-1154). It is not a review round under DEC-1010.
- **Who probed.** A fresh read-only independent auditor (claude-opus-5-5, high), launched by the ticket lead with
  `launch_worker.sh`. Brief: `.gov-runtime/scratch/lead/r6/a7.md` (JUDGEMENT.md word for word). Log:
  `.gov-runtime/scratch/lead/log/a7.json`. Its tripwire is clean and `git status` is empty.
- **At this head:**
  - `gov accept W2-42a`: 990 passed, 0 failed, 2 skipped.
  - The scoped set, run once with the opt-in tiers collected (GOV_TESTS_OPTIN=lifted,breadth): 4011 passed, 2 xfailed,
    6 failed. Its folders are the R3 round's: tests/unit/guard, tests/acceptance/W2-42a, tests/unit/hooks, DEC-409's
    cases in tests/unit/pause, tests/unit/containment/test_w1_50_freeze_flag.py, tests/acceptance/W1-50, W1-28 and
    W2-16.
  - The 6 failures are W2-33's fixture copy (`tests/acceptance/W2-33/w2_33_support.py:376`; 4 in W1-50, 2 in W1-28),
    the same 6 as in the previous rounds and outside the guard.
- **The verdict block, as returned:** RO, NRA and DEC409 all pass.
  - The findings are F1, F3 and F4 (NRA: in scope, ordinary work no, fails open), F2 (RO: in scope, ordinary work
    yes, consequence other; it fails closed and none of it is a regression from the base) and F5 (performance, out of
    scope).
- **READY, by code (JUDGEMENT.md).** No finding is in scope, ordinary work yes and fails open or loses work.
- **Rows** (for the live-hook ACT's hardening list; recorded, not a round):
  - F1: here-string data run as a command through a copy, an array, a pipe to a shell, `trap`, `set --` or a read
    inside `$(…)`. Every sibling without a here-string is allowed at both commits (the parser's older general gap).
  - F2: `awk 'NR>1'`, `sed` labels and branches, readers the rule does not name, and eng-6's false positives
    (`xargs echo "$a"`) are refused. All are refused at the base too.
  - F3: `ssh`/`docker exec -i` in a loop body over a here-string.
  - F4: a gawk indirect call to a split `system`.
  - F5: `decide()` slows past about 250 read-bound variables in one call (the regex cache).
- **Judgement: pass.**

## The reviewer's record (as returned)

"""
open(OUT, "w").write(front + r.rstrip() + "\n")
print("written", OUT, r.count("```verdict"))
