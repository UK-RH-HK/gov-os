# Brief: independent test designer, W2-184 (DAEO-6f0s), batch td-7 (R1-R3, the narrow check's F1-F3)

You are a fresh independent test designer for DAEO-6f0s (W2-184). The ticket landed (d79c8c939) and was reopened on
2026-11-14 by the CTO under the owner's standing rule DEC-1180 (4) ("a defect spotted is fixed in the same flow"), for
the three findings of the narrow independent check (`docs/probes/DAEO-6f0s/PR-DAEO-6f0s-f1.md`, F1-F3; read it). The
ticket's KPI lines R1, R2 and R3 (`.tickets/DAEO-6f0s.md` in the main checkout
/home/usain/Dynamic-Agentic-Engineering-OS, read-only; its last paragraph) are yours to test, as described behaviour
(DEC-136). The interface for them is **section 10** at the end of this brief (stated by the ticket lead, DEC-1052);
sections 1-9 are the interface as it stands. Do not read the engineer's work in `src/gov/launch/`: test the behaviour
as described. You are launched on Opus because the ticket is promoted (DEC-1120 (3)).

Context: /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/briefs/ctx-td-5.md (JSON from `gov context`, made
for td-5; today's `gov context` is BLOCKED because DEC-1180 is not yet in the store). DEC-1180 (4), word for word:
"Standing: no deferral. Do now everything that can be done now. Nothing waits for the next morning, the next digest or
a later batch, and a defect spotted is fixed in the same flow. ..."

## What to write
1. **A new file `tests/unit/launch/test_w2_184_r_fixes.py`** (the KPI lines name `tests/unit/launch/`; it is in the
   ticket's `allowed_paths` as `tests/unit/launch/test_w2_184_*.py`). Name the cases `test_r1_*`, `test_r2_*`,
   `test_r3_*`. You may import the acceptance folder's support module (`tests/acceptance/W2-184/w2_184_support.py`
   and its helpers, by a `sys.path` insert of that folder) or build your own fixtures; do not edit the support module
   in a way that changes any existing case. At least:
   - **R1:** `gov launch orchestrator <ticket>` (and `lead`) given `--reason x`, `--trial t1`, `--owner-named
     DEC-1` each alone, and all three together: exit 2, stderr names the option(s) given and says a lead takes none
     of them; nothing starts (the stand-in CLI is never run), no launch record is written, the gate is not consulted.
     An empty value (`--reason ""`) is refused the same way. A lead launch without them is unchanged (it starts as the
     existing lead cases say). A worker launch with each option is unchanged (one case per option is enough, e.g. the
     keyword case's result through the CLI). The direct call `launcher.launch(root, "orchestrator", tk, [],
     reason="x")` refuses (LAUNCH_REFUSED) before anything starts.
   - **R2:** `gov.launch.record.write(records, record)`: (a) a write interrupted after the temporary file's create and
     before or during its bytes (e.g. a child process whose `os.write` or `os.fsync` is replaced by `os._exit`, or a
     raised `OSError`) leaves **no** `<session_id>.json`; (b) a normal write leaves the whole record under
     `<session_id>.json` and no `.tmp` file; (c) a leftover temporary file (`.<session_id>.<anything>.tmp`, empty or
     partial) in the record folder does not refuse a launch that reads the folder (a worker launch in a project with
     a `criticality.yaml`), nor a later write of the same session id; (d) a planted non-JSON `<name>.json` still
     refuses such a launch, naming it; (e) two writers of the same session id (two processes, or a second call): one
     final record whose bytes are one writer's whole record; the other is refused as "already there"; (f) an existing
     final-name file is never overwritten.
   - **R3:** under the ticket worktree and the tests worktree (as `test_w2_184_f1_tests_worktree.py` builds them): a
     stale launch-root copy of `docs/probes/<id>/01-review.md` without the fail-open finding and a newer ticket-branch
     copy of the same path with it: the test designer's launch from the tests worktree is promoted, `a fail-open
     finding`, naming the root-relative path; the reverse (the launch-root copy has it, the other not): promoted too;
     two identical copies of one failed record count once (one failed review, not two); two **differing** copies of
     one failed record are still one failed review (10.3 (b)); a copy under another root whose front matter is not
     YAML still refuses, naming the file.
2. **Revise to R3** the existing acceptance cases that assert P-td5-2's first-copy rule:
   `tests/acceptance/W2-184/test_w2_184_f1_tests_worktree.py::test_f1_a_path_under_both_roots_is_read_from_the_launch_root_s_copy`
   (named by the KPI line) and, if it asserts the same rule,
   `test_f1_a_path_under_two_other_roots_is_read_from_the_first_root_in_sorted_order`. Rename each to say what it now
   checks, and note it in the folder's `README.md`. This commit carries `Rewrite-Reason: DEC-1180 (4), rv-f1 F3` in
   its trailer block. Keep every other existing case.
3. **Each new or revised case must be red at your tree's head (bbe1510f8) for the stated reason** (R1: the lead
   starts or argparse's exit is not 2 with that message; R2: the create-then-write leaves an empty final-name file; R3:
   the first copy wins). A case already green at the head is fine only where it pins behaviour that must stay
   (the "unchanged" cases, the non-JSON refusal, the two writers); name those as such. Report, per case, red or green
   at the head and the failing line.

**Do not open, list or read anything under `fixtures/evaluation/` or any `hidden` folder.**

## Where you write
- Your tree: /home/usain/gov-os-worktrees/W2-184-tests, branch w2/W2-184-tests (at bbe1510f8). Write only
  `tests/unit/launch/test_w2_184_r_fixes.py`, `tests/acceptance/W2-184/` and files under the session's own `$TMPDIR`
  (no new folder under `.gov-runtime/scratch/`).

## How to run tests (every pytest through heavy_slot.sh; long runs in the background, never with `&`)
```
env HOME=/home/usain/gov-os-worktrees/W2-184-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-184-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
(Make the empty-home folder first if it is missing: it is under your tree.) Before you commit, the whole of
`tests/acceptance/W2-184` and `tests/unit/launch` must run with only your new or revised cases red. No `gov retrieve`,
no `gov context`: Read and Grep, and once more in other words.

## Commit (your paths only; trailers in ONE final paragraph, no blank line inside it)
```
git -C /home/usain/gov-os-worktrees/W2-184-tests commit -m "W2-184 (DAEO-6f0s) tests: R1-R3 (the narrow check's F1-F3, DEC-1180 (4)): a lead refuses the three options, the launch record written atomically, every root's copy of a probe record read" --trailer "Task: DAEO-6f0s" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1180, DEC-1120, DEC-1010" --trailer "Rewrite-Reason: DEC-1180 (4), rv-f1 F3" -- tests/unit/launch/test_w2_184_r_fixes.py tests/acceptance/W2-184
```
No merge, no push. Refused twice for the same action: stop and say so; never work around it.

## Return (your last message): the twelve fields, each a labelled line
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: /
proposed_decisions: / unresolved: / recommended_next_action:
In `tests:` give each new or revised case with red/green at bbe1510f8 and the failing line of each red one.

---
# THE INTERFACE (word for word, with the round-1 and round-2 amendments and section 10, R1-R3)

