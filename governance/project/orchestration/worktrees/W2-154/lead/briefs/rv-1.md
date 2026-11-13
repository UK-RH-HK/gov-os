# Brief rv-1: W2-154 (DAEO-l4gf), independent auditor, a narrow check of S4 only (DEC-1154)

You are the independent-auditor for ticket DAEO-l4gf (W2-154), profile STANDARD, class C2: a fresh, read-only session.
S1-S3 were built, verified and reviewed earlier (verified head ae1d68394752). The owner then decided S4 (a) on
2026-11-13: the ticket's allowed paths gain `tests/acceptance/serial-only.txt` for S4 only (df8ba7007). Your check is
narrow: exactly the S4 change since ae1d68394752 on branch w2/W2-154 (head 7bcff333b). Do not re-review S1-S3.

## What changed since ae1d68394752
- f42c51629: a merge of w2/integrate into the branch (brings df8ba7007, the ticket's new path, and other tickets' landed work).
- ad4355943 (merged 7bcff333b): the test designer's S4 commit, `tests/acceptance/serial-only.txt` only (+3, -5).
See: `git -C /home/usain/gov-os-worktrees/W2-154 diff ae1d68394752 7bcff333b -- tests/acceptance/serial-only.txt` and
`git -C /home/usain/gov-os-worktrees/W2-154 show ad4355943`.

## The KPI line under check
S4 Once S1 holds, W1-16's ui_off entry returns to serial-only.txt (commented out on 2026-11-10 by the D-10 gate,
b78f862a9 / 6afff5d74), restored by a test designer with its Rewrite-Reason; the designer writes
tests/acceptance/serial-only.txt, never the implementer. Verify: after S1 passes, `git log` on
tests/acceptance/serial-only.txt shows the ui_off line restored in a commit with `Role: independent-test-designer` and a
Rewrite-Reason, and no commit by the engineer role touches that file [DEC-1112 (3), MR-3].
Also F3: `git diff --name-only w2/integrate...w2/W2-154` lists only the ticket's allowed paths (in the ticket's front matter,
/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-l4gf.md, read-only).

## Probe (each with the command and its output quoted)
1. The restored line is live (not a comment), names exactly `tests/acceptance/W1-16/test_w1_16_ui_off.py`, sits with the W1-16
   daemon entries, and the rest of the file is unchanged against 6afff5d74's parent (b78f862a9's era) except the comment.
2. The trailers of ad4355943: `Task: DAEO-l4gf`, `Role: independent-test-designer`, a `Rewrite-Reason:` naming DEC-1112 (3)
   and the owner's S4 (a); `Implements:` only ids of the ticket's `sources:`; no `Role: owner`, no `Decided-by:`. No commit
   with `Role: engineer` touches the file (whole history of the file).
3. The behaviour with the restored entry, by `--collect-only` only (never run the ui_off cases: they start the
   codebase-memory daemon). The close's serial-afterwards run gives pytest the plugin `gov_close_serial_only` with the
   variables `GOV_CLOSE_SERIAL_ONLY_OF` (the project's root), `GOV_CLOSE_SERIAL_ONLY_GIVEN` (the entries, one per line) and
   `GOV_CLOSE_SERIAL_ONLY_OUT` (the out file), and `src/gov/close/pytest_plugin` on PYTHONPATH (read
   `src/gov/close/command.py` about lines 900-975 and the plugin for the exact form). Check:
   a. a default run (no opt-in): the plugin prints `gov_close_serial_only: not in this run: tests/acceptance/W1-16/test_w1_16_ui_off.py`,
      exits 0, the out file names the entry, and no case of the file is collected;
   b. with `--optin=breadth` (see the project's conftest for the opt-in form): the file's cases are collected (nine items:
      seven functions, one parametrized x3) and no "not in this run" line.
   c. The parallel phase does not take the file's cases when opted in: the plugin, in the parallel run (with
      `GOV_CLOSE_SERIAL_ONLY_OF` and no GIVEN), deselects them (collect-only with `--optin=breadth`).
4. F3 as above.
Optional: the lead's verification run of this head (in progress or done) is in
/home/usain/gov-os-worktrees/W2-154/.gov-runtime/scratch/lead/log/verify/ (summary.txt, serial.txt, serial.xml); quote its
summary line if it is done when you finish.

## How you run anything
Read-only: write nothing in /home/usain/gov-os-worktrees/W2-154 and commit nothing. Scratch only under your `$TMPDIR`
(make `$TMPDIR/w2-154-rv1`). Every pytest, collect-only too, through:
```
env TMPDIR=<your scratch> PYTHONUSERBASE=/home/usain/.local HOME=<your scratch>/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-154/src:<plugin folder if needed> bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <ARGS> -p no:cacheprovider -o tmp_path_retention_policy=failed
```
run from /home/usain/gov-os-worktrees/W2-154 (a script under your scratch that `cd`s there and stops if the `cd` fails).
A heavy_slot gate wait is normal. Anything longer than one line goes in a script file under your scratch.
Reads are open except secrets, held-out qualification material's contents and the hidden half of any evaluation set; never
open the evaluation sets' root or any hidden or memory-verdict folder. No `gov retrieve` and no `gov context`: Read and Grep,
then once more in other words. Refused twice for the same call: stop and say so; never work around a refusal.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing), then the verdict block
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then a probe record in full, in markdown, ready to be committed by the CTO as docs/probes/DAEO-l4gf/PR-DAEO-l4gf.md
(front matter with `task: DAEO-l4gf`, `status:` PASS or FAIL, `head: 7bcff333b...`, `scope: S4 narrow check (DEC-1154)`),
each probe with its command and quoted output, each finding with severity, and ending in a fenced verdict block:
```
verdict: PASS | FAIL
head: <hash12>
findings: <count by severity>
```
