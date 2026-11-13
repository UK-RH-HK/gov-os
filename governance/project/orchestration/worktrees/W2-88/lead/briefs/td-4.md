You are a fresh Independent Test Designer (MR-3). Ticket: DAEO-2bdu (W2-88, "Memory for any repository"), profile FULL, class C2, run 4. Your job is **one narrow revision of one case**, nothing else. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-88-tests` (branch `w2/W2-88-tests`, made from the ticket branch's head 14c7ec15c8d8, DEC-963); you never write the ticket's own worktree `/home/usain/gov-os-worktrees/W2-88`.

Your budget: about 30 minutes. One commit.

## Step 0, before any work (report it first in your return)
The sandbox check in the launcher's step-0 file beside this brief. Then `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-2bdu`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-88-tests`, `w2/W2-88-tests`). If anything differs, stop and say so.

## The case and why it is wrong
`tests/acceptance/W2-88/test_w2_88_s16_search_again.py::test_s16_a_planted_adoption_holds_the_discovery_skills_search_again_line` (added in this run, td-3) asserts the literal phrase "search again once" in the adopted copy of the discovery skill, with the red reason "W2-142 (DAEO-qskx) waits". W2-142 is **closed and merged** (`daf56805b`, `984a3ba97` on w2/integrate; ticket `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-qskx.md`, its S2). Its decided line, in Gov OS's `template/governance/kernel/skills/discovery/SKILL.md` (version 1.1.0, section "Retrieval bundle"), reads: "When the first bundle does not answer, the practitioner searches once more in its own words before treating the question as unanswered (the retrieval skill, step 7; DEC-1092 (1))." It does not contain the words "search again once". The ticket's KPI (S15 in the ticket's text: "adoption copies, unchanged, … the discovery skill's line (W2-142 S2) …"; its verify: the four-phrase string test "on a planted adoption's generated skill and T-0") puts the four phrases on the retrieval skill and T-0, and asks only that the discovery skill's line be copied unchanged.

## The revision
- Keep the case's copy checks (the copy exists and is byte-identical to Gov OS's discovery skill).
- Replace the "search again once" assertion with W2-142 S2's line as Gov OS ships it: the copy holds the sentence "searches once more in its own words before treating the question as unanswered" (whitespace-normalised, as the case already does). Read the sentence from W2-142's ticket and Gov OS's skill; do not read this ticket's implementation.
- Rename the case only if its name would now mislead (keep `test_s16_` and no `real`, `green_here` or `time_limit`); update its docstring and its README map row and red reason (on 14c7ec15c8d8 it should now be green: say "green on the head: the copy step is built and W2-142's line is in Gov OS's skill").
- Nothing else in the suite changes.
- Commit with `--trailer "Rewrite-Reason: W2-142 S2's decided wording (DAEO-qskx, closed); the KPI asks the line copied unchanged"`.

## What you may read
The ticket file `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-2bdu.md`, W2-142's ticket, the suite in your worktree, `template/governance/kernel/skills/`. **You never read the engineer's code** (DEC-820): not `src/gov/adopt/*`, `src/gov/store/layout.py`, `src/gov/store/loader.py`, `src/gov/rebuild/command.py`, nor `tests/unit/*/test_w2_88*`. Never open the evaluation sets' root or any hidden or memory-verdict folder. Search with the Read and Grep tools only (no `gov retrieve`, DEC-1065).

## How to run
`mkdir -p /home/usain/gov-os-worktrees/W2-88-tests/.gov-runtime/scratch/empty-home` first; use the sandbox's own `$TMPDIR` (a subfolder of it). From `/home/usain/gov-os-worktrees/W2-88-tests`: `env HOME=/home/usain/gov-os-worktrees/W2-88-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-88-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-88/test_w2_88_s16_search_again.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=line`. Never `-x`. A resource gate's refusal is a wait (DEC-1146). Show the revised case passes on the head, and that it fails against a copy of the discovery skill with that sentence removed (in your scratch, never in the ticket's paths).

## Commands, commits
- No shell variable as a write target; no here-document, no backticks, no `bash -c '…'`; anything longer goes in a script under `/home/usain/gov-os-worktrees/W2-88-tests/.gov-runtime/scratch/td/`, written with the Write tool. **Refused twice for the same call: stop and say so** (DEC-1142 (9)). On an authentication error, return `AUTH_REQUIRED`.
- Write only under `tests/acceptance/W2-88/`. Before the commit, check `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file. Never `--no-verify`, `core.hooksPath`, amend, rebase, reset, merge or push.
- `git commit -m "<subject>" --trailer "Task: DAEO-2bdu" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1098, DEC-1094, DEC-1092" --trailer "Rewrite-Reason: …" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-88`.

## Never
Never run `gov close`, `gov pause`, `gov rebuild` or `gov adopt` against a real repository or worktree; never touch `~/gov-os-workbench/examin/`; never ask or notify the owner; install nothing; never write a ticket file, the register or a plan file.

## Return
One message, your last. The twelve fields first, each a labelled line; then: the revised case (old and new assertion), its run on the head, the bite check, the sandbox check, read refusals met, the head commit (12 digits).

```
task: / status: (DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, with one line why) / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
Refused twice for the same call: stop and say so.
