---
type: probe
task: DAEO-ecac
round: r3
kind: "narrow independent check of the CTO's path cases P1 (a) and P2 (a) (DEC-1156 (7); DEC-1154; --owner-named DEC-1154, DEC-1010)"
status: final
reviewer_session: 2a1c058b-7495-4349-ac60-a22b76f20883
implementer_session: "ead5e91f-c013-42f4-af39-78c33e8fced1"
reviewer_wrote_nothing: true
reviewer_model: claude-opus-5-5
reviewer_effort: low
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: pass
probed_commit: de09171e0638ba94013846fd5878f6e2655703ee
reviewed_range: "84b267971291..de09171e0638ba94013846fd5878f6e2655703ee"
previous_round: PR-DAEO-ecac-r2 (7bc20ff4a, pass, 0 blocking)
decisions_applied: [DEC-847, DEC-963, DEC-982, DEC-983, DEC-1154, DEC-1156, DEC-1010, DEC-801, DEC-802, DEC-808, DEC-809, DEC-820]
scope: "P1 (a): command.py's --tests-worktree diff against CIT-E §7 and its behaviour on planted repositories (success-10's second half); P2 (a): test_w2_20_round3.py's six-launch case is set-up only and still decided by the start lock; the range breaks none of the ticket's lines"
---

# PR-DAEO-ecac-r3: narrow independent check of P1 (a) and P2 (a)

## Summary
A fresh independent auditor (au-3) checked the range `84b267971..de09171e0` at head `de09171e0638`. The session was read-only and wrote nothing in the worktree. The range holds three commits:
- the lead's merge of `w2/integrate` (`4ae9dc091`);
- en-4's P1 (a) (`faeafc457`);
- en-4's P2 (a) (`de09171e0`).

What was found:
- **P1:** the diff matches CIT-E §7 hunk for hunk. `--tests-worktree` behaves as success-10 states, so **F5 is reversed and success-10 passes**.
- **P2:** set-up only, with no assertion changed. The case goes red with the start lock made a no-op (6 started), and green as it stands.
- **The merge:** it touches none of the ticket's paths.
- **Tests:** the ticket's unit files, the round-3 file and `tests/acceptance/W2-60b/` are green at the head.
- **New finding:** one row, F9 (in scope, ordinary work yes, consequence other). It does not block.

**Verdict: pass, 0 blocking findings.**

## Step 0 (EMG-d4b-launched.md, the sandbox check)
- **(a)** `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-W2-60b','w').write('x')"` failed with `OSError: [Errno 30] Read-only file system`, exit 1. No file was made (`ls`: no such file).
- **(b)** `echo sandbox-trial | git hash-object -w --stdin` returned `1ae28402a109c3397a44b19239a00adfa9472eb0`, exit 0. `git update-index --refresh` exited 0.
- **ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing (exit 1).
- **Refusal:** one guard refusal came at the start. A `find` line named the sets root inside an exclude pattern; the guard refused it once (DEC-1082 (3)). It was not repeated. The brief was then found with Glob under the orchestrator's scratch folder.

## What was checked and found sound
- **P1, the diff:**
  - The three hunks' bodies are line for line identical to the ```diff block in CIT-E §7 at `84b267971`.
  - The only differences are headers git adds: the `diff --git` line and the function-context text after `@@ … @@`.
  - Both have 3 hunks, and nothing else in `command.py` changed.
  - The CIT-E's own edits only mark §7 applied and add table rows 5 and 6. The §7 diff stays as the record.
- **P1, how it works:** `command.run` sends `--tests-worktree` to `launcher.tests_worktree` (`src/gov/launch/launcher.py:978-1010`, unchanged in the range). It does this after `--plan` and before any options, gate, lock or session code (`src/gov/launch/command.py:58-62`).
- **P1, behaviour:** probes P1.1 to P1.11 below cover the success path, every refusal, the start of no session, and no gate or lock. Every refusal made no tree. The only refusal that left a branch is F9. The branch is always at the tree's own HEAD, which differs from the main checkout's in the planted repository.
- **P2:**
  - The diff adds `import shutil`, six `copytree` copies of the planted project made before any launch, and `projects[i]` in place of `project` in the child's launch call.
  - No assertion or count changed, and neither did the slowed check or the memory figures.
  - The start lock is machine-wide (`$HOME/.gov-os/machine/launch.lock`, `src/gov/launch/gate.py:55-90`), not per folder, so the six launches still contend for it.
  - Proven by experiment: green as it stands (3 of 3 runs); red with a no-op lock (`assert (6 == 3)`, 3 of 3 runs); red without P2's set-up (`assert (1 == 3)`: the one-writer rule decided, as CIT-E row 6 says).
- **Way (i) versus way (ii):** way (i), six folders, was the better choice. It keeps the role, and so the launch path the case has always tested, an `engineer` writing launch. The machine-wide lock means the six folders do not weaken the contention, as the no-op-lock red shows. Way (ii), read-only auditors in one folder, would also have escaped the one-writer rule. But it would change the role under test and route launches through reviewer-specific code (the probe-record and verdict checks, `launcher.py:626ff`). That moves the case further from what it tested. No finding.
- **Nothing else broken:**
  - `git diff --stat 84b267971 4ae9dc091` over every path in the ticket's `allowed_paths`, `tests/acceptance/W2-60b` and `.claude/hooks` is empty. The merge touches none of them; its 57 files are other tickets' work.
  - `git diff --stat 84b267971 de09171e0` over `launcher.py`, `session_record.py`, `decide.py`, `src/gov/resources/`, `.claude/hooks` and `tests/acceptance/W2-60b` is empty. **The one-writer rule is unchanged by the range.**
- **No session started:**
  - A stand-in `claude` was first on `PATH` and never ran (no marker file).
  - `$HOME` was an empty scratch folder and stayed empty: no `.gov-os/machine`, so no start lock, registry entry or gate log.
  - No `.gov-runtime/` appeared in either the main checkout or the linked worktree.
- **Options combined with the flag:** `--tests-worktree` with `--plan` runs the plan; with gate options or `-- <args>` they are ignored. No session starts in either case, so this is not recorded as a finding.
- **The module path:** `python3 -m gov` cannot run, because there is no `gov/__main__.py` (already so before this ticket, not in the range). The probes used the real CLI module, `python3 -m gov.cli.main`, as the unit case does.

## Probes
Set-up: a scratch repository `M` under `$TMPDIR/au3/p1` on `main`, with `.tickets/T-1.md` (`in_progress`) and `.tickets/T-2.md` (`done`). A linked worktree `WT` was made with `git worktree add -b w2/X ../WT`, with one commit of its own: WT HEAD `da9b37b`, M HEAD `e0f9526`. Each run went through `run.sh <cwd> launch …`, which is `cd <cwd>`, then `HOME=<scratch>`, a stand-in `claude` first on `PATH`, `PYTHONPATH=<worktree>/src`, and `python3 -m gov.cli.main`.

- **P1.1, the success path from the linked worktree:** `launch independent-test-designer T-1 --tests-worktree`.
  - Printed `…/p1/WT-tests` and exited 0.
  - `WT-tests` is on `w2/X-tests` at `da9b37b`, WT's HEAD (not M's), and has a clean status.
  - `$HOME` stayed empty, there is no `.gov-runtime` in WT or M, and no stand-in marker.
- **P1.2, run again (path and branch both exist):** `LAUNCH_REFUSED: the tests worktree's path …/WT-tests is already there`, exit 1. `git worktree list` is unchanged.
- **P1.3, the branch exists, the path removed (`git worktree remove`):** `LAUNCH_REFUSED: the tests worktree's branch w2/X-tests is already there`, exit 1. No tree was made and no worktree was added.
- **P1.4, other roles:** engineer, independent-auditor, research, product-spec, qa-engineer and orchestrator each got `LAUNCH_REFUSED: --tests-worktree makes the independent test designer's own tree, not one for '<role>' (DEC-963)`, exit 1.
- **P1.5, an unknown ticket:** `LAUNCH_REFUSED: unknown ticket 'T-9'`, exit 1.
- **P1.6, a `done` ticket:** `LAUNCH_REFUSED: ticket 'T-2' is not in_progress (status: done)`, exit 1.
- **P1.7, an existing plain folder at the path:** refused (`… path … is already there`), exit 1, and the folder was left empty.
- **P1.7b, a dangling link at the path:** refused the same way, exit 1.
- **P1.8, the tree detached:** `LAUNCH_REFUSED: the tree …/WT is on no branch, so its tests branch cannot be named`, exit 1.
- **After P1.2 to P1.8:** only `main` and `w2/X` are left (the P1.3 branch was deleted by hand before P1.4). No `WT-tests`, `$HOME` empty, no marker.
- **P1.9, git fails part-way (the parent folder read-only):** linked worktree `ro/WY` on `w2/Y`, with `chmod 555 ro`.
  - `LAUNCH_REFUSED: git could not make the tests worktree …/ro/WY-tests on the branch w2/Y-tests: fatal: could not create leading directories of '…/ro/WY-tests/.git': Permission denied`, exit 1.
  - No tree was made, **but the branch `w2/Y-tests` was left** at `e0f9526`, WY's HEAD. This is F9.
- **P1.10, run from a subfolder of the tree:** `LAUNCH_REFUSED: unknown ticket 'T-1'`, exit 1. The root is the working directory, so the ticket is not found and no `sub-tests` is made: it fails closed.
- **P1.11, `--root <WT>` given from elsewhere:** exit 0, `WT-tests` on `w2/X-tests`, `$HOME` still empty.
- **P2, the case as it stands:** `heavy_slot.sh python3 -m pytest tests/unit/resources/test_w2_20_round3.py::test_f1_launches_started_together_admit_only_those_the_memory_rule_admits` passed 3 of 3 runs (`1 passed in 1.38s`, `1.39s`, `1.44s`).
- **P2, with a no-op lock:** a scratch pytest plugin `$TMPDIR/au3/p2/au3_noop_lock.py`, loaded with `-p au3_noop_lock` (autouse; it monkeypatches `gov.launch.gate.StartLock` with a class whose `__init__` and `release` do nothing). The tree is untouched. Failed 3 of 3 runs, at `assert _count(marks, "started-") == 3 …` with `AssertionError: assert (6 == 3)`.
- **P2, without P2's set-up:** a scratch plugin `au3_one_folder.py` makes `shutil.copytree` return its source, so all six launches go into one folder. Failed with `assert (1 == 3)` (1 started).
- **Tests at the head:**
  - Command: `heavy_slot.sh python3 -m pytest tests/unit/launch/test_session_record*.py tests/unit/telemetry/test_sessionlog*.py tests/unit/resources/test_w2_20_round3.py tests/acceptance/W2-60b/ -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
  - Result: **243 passed, 3 deselected in 31.10s**, 0 failed.
  - The 3 deselected are deselected by the project's own collection even with no `-m` or `-k` (`243/246 tests collected (3 deselected)` in a plain collect). `-k "real or green_here or time_limit"` and `-m local_only` each match 0 items, so the brief's exclusion itself left nothing out.
  - The acceptance folder collects 55 items, all in the passed set.

## Findings

### F9: a git failure part-way leaves the tests branch behind
- **What:** `launcher.tests_worktree` checks for the path and the branch, then runs `git worktree add -b <branch>-tests <tree>-tests HEAD` (`src/gov/launch/launcher.py:1005`). When git fails after it has made the branch but before the tree exists, the launch is refused correctly (no tree, no session). But the branch `<branch>-tests` is left at the tree's HEAD. A retry after the cause is fixed is then refused with "the tests worktree's branch … is already there" until someone deletes the branch by hand.
- **How reached:** probe P1.9 (above): the branch `w2/Y-tests` was left at `e0f9526` after a refusal with exit 1.
- **KPI line:** success-10.
- **Scope:** in.
- **Ordinary work: yes,** because any failure git meets while making the folder does it. Examples: a path git cannot create, a full disk, or a run from a launched (sandboxed) session where `/home/usain/gov-os-worktrees` and `.git/worktrees` are read-only while the main `.git`'s refs are writable (step 0 (a) shows that folder read-only here).
- **Consequence: other.** It does not fail open: no tree, no session, and the stray branch is at the right head and holds no work. No work is lost. It costs a manual `git branch -D` before the retry.
- **What would reverse it:** a refusal after a failed `worktree add` that deletes the branch it made (or makes the branch only after the folder succeeds). The same P1.9 probe would then leave no `w2/Y-tests`. Alternatively, evidence that the git version in use rolls back the branch itself.
- **Disposition:** a recorded row (DEC-1010). It does not block, and it can ride along in any resume (DEC-802).

### F5 (round 2): reversed
`gov launch --tests-worktree` is now wired through `command.py` (P1 (a)) and behaves as success-10 states (P1.1 to P1.11). F5's reversal condition is met.

## Round 2's rows kept (lines this range does not touch keep round 2's verdict)
- F2 (success-10, success-12; in; ordinary work no; fails open): a writer whose start record cannot be written is invisible to the one-writer check. Wave 3 row; the range does not change it.
- F3 (success-7; in; ordinary work no; other): the role-file reading depends on two headings and a name prefix. Wave 3 row (CIT-E §9).
- F4 (success-4; in; ordinary work yes; other): the window is measured only from the result line. Row.
- F6 (success-1; in; ordinary work yes; other): one 429 written in both forms counts twice. Row.
- F7 (failure-2, success-1; in; ordinary work yes; other): a sub-agent with no plain model puts a null in `subagents.value.models`. Row.
- F8 (success-7; out; ordinary work yes; other): a sixth role launches, but the product guard refuses its writes until it joins `KNOWN_ROLES`. Row.

**Classification of this round's findings:** F9 is in scope, ordinary work yes, consequence other (one row, not blocking). F5 is reversed. Rows F2 to F4 and F6 to F8 are kept unchanged. No finding blocks. Recommendation: pass.

```verdict
{"kpis": [{"kpi": "success-1", "verdict": "pass", "findings": [{"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-2", "verdict": "pass", "findings": []}, {"kpi": "success-3", "verdict": "pass", "findings": []}, {"kpi": "success-4", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-5", "verdict": "pass", "findings": []}, {"kpi": "success-6", "verdict": "pass", "findings": []}, {"kpi": "success-7", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F8", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-8", "verdict": "pass", "findings": []}, {"kpi": "success-9", "verdict": "pass", "findings": []}, {"kpi": "success-10", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F9", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-11", "verdict": "pass", "findings": []}, {"kpi": "success-12", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "failure-1", "verdict": "pass", "findings": []}, {"kpi": "failure-2", "verdict": "pass", "findings": [{"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "failure-3", "verdict": "pass", "findings": []}]}
```

task: DAEO-ecac (W2-60b), au-3, the narrow independent check of the CTO's path cases P1 (a) and P2 (a)
status: complete; judgement pass, 0 blocking findings
work_completed: step 0 (passed); P1's diff compared with CIT-E §7 (hunk bodies identical, 3 hunks, nothing else); P1's behaviour probed on planted repositories through the real CLI module (P1.1 to P1.11); P2's diff read (set-up only, no assertion changed); the six-launch case run as it stands (green 3 of 3), with a no-op start lock (red 3 of 3, 6 started) and without P2's set-up (red, 1 started); the merge and the range checked against the ticket's paths and the one-writer code; the ticket's unit files, the round-3 file and the acceptance folder run at the head
files_changed: none in the worktree; scratch files only under $TMPDIR/au3 (planted repositories, run.sh, two pytest plugins, extracted diffs)
evidence: src/gov/launch/command.py:32-33,42-44,61-62; src/gov/launch/launcher.py:978-1010; src/gov/launch/gate.py:55-90; tests/unit/resources/test_w2_20_round3.py:94-99,125; docs/changes/W2-60b-CIT-E.md §7 at 84b267971; probes P1.1 to P1.11 and P2 above
tests: 243 passed, 3 deselected (by the project's own collection; the brief's -m/-k exclusion matched 0 more), 0 failed: tests/unit/launch/test_session_record*.py, tests/unit/telemetry/test_sessionlog*.py, tests/unit/resources/test_w2_20_round3.py, tests/acceptance/W2-60b/ (55 collected); the six-launch case green 3 of 3, red 3 of 3 with a no-op lock
discoveries: F9 (a git failure part-way through `worktree add -b` leaves the tests branch, which blocks the retry); `python3 -m gov` has no `__main__` (already so, not in the range; the CLI module is `gov.cli.main`)
risks: F9 is likeliest if `--tests-worktree` is run from a sandboxed session, where the worktrees folder is read-only and branch refs are writable; F2 is still open as a Wave 3 row
lessons: a machine-wide lock can be checked in isolation by giving each launch its own folder: the no-op-lock red shows the contention survives that set-up
proposed_decisions: none
unresolved: none for this check; rows F2 to F4 and F6 to F9 stay recorded
recommended_next_action: the lead commits this record as PR-DAEO-ecac-r3.md; F9 goes into the ticket's row list (delete the branch if `worktree add` fails, or make the branch only after the folder exists), riding along in any resume (DEC-802), not a round

```
$ git -C /home/usain/gov-os-worktrees/W2-60b status --short
```
(empty)
