task: DAEO-2bdu (W2-88), the narrow independent check of the NC-1/NC-2 fix at ed568a699e4fa82908fc3f8830e16733a8e7a5c4
status: DONE. NC-1 is fixed and NC-2 is fixed; no new finding is in scope, reachable in ordinary work and failing open or losing work. Overall verdict: pass.
work_completed: Step 0 checks. Read the diff 01ec6d2a7..ed568a699 and the code path `a9` → `install` → `_stage` → `commit` → `undone`/`undo`. Read the acceptance cases, both stand-ins, the unit tests and the README's run-6 section. Checked each commit's paths and trailers. Ran 13 probe cases in my TMPDIR on planted repositories (12 assert the stated behaviour and passed; P4c only observes and prints), with real git hooks, signing, a SIGINT sent during the commit, a clean filter, and a tracked record or brief.
files_changed: none
evidence: the probe files are `$TMPDIR/probe/test_probe_{a,b,c}.py` and `probe_base.py`; output is in `$TMPDIR/probe/run-bc.txt`. File A ran 4 cases (P1 to P4, all passed). Files B and C ran 8 cases (all passed). My `hash-object` vs `git add` check under a clean filter matched.
tests: every pytest went through heavy_slot.sh, with TMPDIR set to the sandbox, the empty HOME, `-p no:cacheprovider -o tmp_path_retention_policy=failed`. File A passed its 4 cases. The case P4b did not take: its signal landed after the run had ended, the stray KeyboardInterrupt ended the pytest session, and P4c replaces it. Files B and C passed 8 of 8. The first B+C attempt was stopped by my own `timeout 900` while it waited for a slot (a wait, not a refusal); the rerun passed. I re-ran none of the lead's suites; the lead's accept-6 is at 217 passed, 0 failed. Nothing from the real-model exclusions was in play: my cases use the unit suite's stand-ins only.
discoveries: if a SIGINT lands inside Python's 0.25 s grace period while `git commit` finishes, A9's own commit lands and the result is `HEAD_MOVED` with `cause: KeyboardInterrupt`. Nothing is lost (note 1). The unit test that checks `project.py` is unchanged compares against git history and will go red once the CTO's P2 changes `project.commit` (NC2-1).
risks: the engineer's three risks are classified in the notes: (1) row/other, (2) row/other, (3) a named residual.
lessons: a pytest piped through `tail` gives no interim output, and a hard `timeout` cuts off a queued slot wait. Write to a file in the background instead.
proposed_decisions: none
unresolved: none
recommended_next_action: the lead puts this check beside the scoped lead_verify result; READY is computed from the verdict block. NC2-1 becomes a row, for the CTO's P2 to change or drop that test.

# W2-88 (DAEO-2bdu): narrow independent check of the NC-1/NC-2 fix
probed_commit: ed568a699e4fa82908fc3f8830e16733a8e7a5c4
base: 01ec6d2a7

## Sandbox and identity
- Step 0 (EMG-d4b-launched.md):
  - (a) `open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-2bdu','w')` was refused with `OSError: [Errno 30] Read-only file system`, as required.
  - (b) `git hash-object -w --stdin` gave `1ae28402…`, exit 0, and `git update-index --refresh` exited 0.
- `printenv GOV_ROLE GOV_TICKET` gave `independent-auditor` and `DAEO-2bdu`.
- At the start, HEAD was ed568a699e4fa82908fc3f8830e16733a8e7a5c4 and `status --porcelain` was empty. At the end both are the same.
- `ps … [o]llama|[l]lama-server` shows nothing.

## NC-1 and NC-2
| Item of the stated behaviour | State | Code | How I probed it |
|---|---|---|---|
| NC-1.1: A9's commit is its own step; no `git reset --hard`, no checkout; `project.commit` and `project.restore` are off A9's path | fixed | fabric.py:308-341, 738; project.py and stages.py diff empty | read the path; P1, P2, P3, P10: reflog unchanged |
| NC-1.1: the record counts among what A9 wrote and staged (unstaged only while its entry is A9's blob, deleted only while its bytes are A9's) | fixed | fabric.py:327-336, 259-289 | P1, P6 (a record tracked at HEAD is given back its old bytes and its index entry), P8 (clean filter), P10 (the record's `git add` fails because the path is ignored) |
| NC-1.1: refusal by a `pre-commit` hook, a `commit-msg` hook or signing | fixed | fabric.py:339-340 → project.py:40-49 | P1 (exit_code 1), P2 (exit_code 1), P3 (`gpg.program=/bin/false`, exit_code 128) |
| NC-1.1: an interrupt during the commit | fixed | fabric.py:681-685 | P4: a real SIGINT to the process while a slow `pre-commit` hook ran. KeyboardInterrupt came back, HEAD was unmoved, nothing of A9 was left, and there was no `index.lock` |
| NC-1.2: edit kept, staged file still staged, untracked file kept, HEAD and branch unmoved, no `reset` in the reflog | fixed | — | P1, P2, P3, P8, P9, P10: status is exactly ` M a.md`, `A  new.txt`, `?? untracked.txt`; HEAD and reflog are unchanged |
| NC-1.2: the folders A9 made are removed only when empty | fixed | fabric.py:290-294 | P1 (`.claude`, `governance/kernel` and `governance/adoption` gone) |
| NC-1.3: `ADOPT_GIT_FAILED`; the message names `git commit` and carries git's text; `details.exit_code` | fixed | project.py:46-48 | P1 and P2 messages end with the hook's word |
| NC-1.3: HEAD moved, so `HEAD_MOVED` with `cause: "ADOPT_GIT_FAILED"` | fixed | fabric.py:295-305 | P5 |
| NC-1.4: on success, one commit with message `gov adopt --lite A9: memory fabric`, holding the copies and the record (plus whatever was staged, the named residual) | fixed (unchanged) | fabric.py:338-341, 739-740 | P7: HEAD~1 is the start commit; the commit holds 5 copies, the record and `new.txt` |
| NC-1.4: an untracked file at the record's path gives `ADOPT_WOULD_OVERWRITE`, the file kept byte for byte, and the undo runs | fixed | fabric.py:322-325 | read the code, plus the unit test `test_an_untracked_file_at_the_records_path_…`; the raise comes before `written` is extended, so the file is never touched |
| NC-2: an interrupt the moment `install`'s `git add` returns leaves no copy in the index or the tree; status clean | fixed | fabric.py:223-226 (blobs named before the add) | P8b (with a clean filter); unit tests `…copies_add_returns…` and `…replaced_tracked_file_back`; acceptance Case D, two parameters |
| NC-2: a copy that replaced a tracked file gets its start-commit content back | fixed | fabric.py:284-286 | P9 (with a refused commit); the unit replaced-file test (with an interrupt after the add) |

## What I probed and found sound
1. `git diff 01ec6d2a7 ed568a699 -- src/gov/adopt/project.py src/gov/adopt/stages.py` is 0 lines. A1 to A8 still commit through `run.finish` → `project.commit` (stages.py:49-56; the call sites at stages.py:160, 172, 182, 397, 425, 461, plus safety.py and legacy.py). A9 never went through `_RefreshFirst`, which wraps only A6 (stages.py:594).
2. The record's bytes are unchanged: the same `record_text` with the same `session` and `stands_on`, UTF-8. The result dict has the same keys as `run.finish` gave (fabric.py:739-740 vs stages.py:56).
3. The blob is hashed before the add and with git's filters (`hash-object -- paths`, `hash-object --stdin --path=rel`), and it equals what `git add` stages. Checked by hand under a `tr a-z A-Z` clean filter (both gave `e427984…`), and in P8 and P8b.
4. Comparing the blob without the mode (fabric.py:266) is what makes a replaced tracked file with mode 100755 undo correctly. The only entry it unstages that A9 "did not stage" is one whose content is A9's own bytes for that path. That is the interface's own rule ("counts as staged by A9").
5. Paths are named before their writes (fabric.py:219-223, 330-335). An interrupt between naming and writing leaves nothing behind, because the bytes are not A9's and there is no index entry.
6. The refusal is never swallowed: `undone` returns and `a9` re-raises the original (fabric.py:684-685). An interrupt with HEAD unmoved stays KeyboardInterrupt (P4).
7. Scope of the commits:
   - Each non-merge commit has `Task: DAEO-2bdu`.
   - aa476d394 (engineer) touches only `src/gov/adopt/fabric.py` and `tests/unit/adopt/test_w2_88_nc1.py`.
   - 5aaff3dd8 (orchestrator) touches only `docs/changes/W2-88-evidence.md`.
   - 9990563fc (test designer) touches only `tests/acceptance/W2-88/**`.
   - Every `Implements:` id is in the ticket's `sources:`.
   - The merge ed568a699 brings in only td-8's four files.
   - The engineer touched no acceptance test. Both workers branched from 01ec6d2a7.
8. The README's run-6 map names three node ids, all present in `test_w2_88_nc1_commit.py`: Case C, and Case D with its two parameters.
9. The acceptance cases assert behaviour, not code:
   - Case C checks first that the plant took (stand-in lines, hook marker), then the refusal code, the exit code 1, `details.exit_code`, the hook's word, HEAD and branch, the reflog, the edit, the staged file, the copies and record, the folders and the exact porcelain.
   - Case D checks that the plant fired, the interrupt, HEAD, the copies and an empty status.
   - The unit tests block `project.commit` and `project.restore` with a stand-in that raises, and assert the same behaviours.

## Findings
**NC2-1 (success-16), minor. A unit test pins W2-23's file to git history instead of testing behaviour.**
- **What is wrong:** `tests/unit/adopt/test_w2_88_nc1.py::test_project_commit_and_restore_are_unchanged_since_01ec6d2a7` runs `git diff --quiet 01ec6d2a7 -- src/gov/adopt/project.py` in the repository.
- **When it goes wrong:** once the CTO's separate P2 changes `project.commit`'s reset for A1 to A8, as is planned, this test goes red on every branch after it. It also fails wherever 01ec6d2a7 is not in the history.
- **Reproduce:** read the test; any later commit that edits `project.py` makes it fail.
- **Behaviour it should have:** the run-6 guarantee is already held by behaviour. The other unit tests block `project.commit` and `project.restore` with a stand-in that raises (`no_project_commit`). This test should be dropped or replaced by that behavioural check when P2 lands.
- **What reverses it:** a ruling that the test is meant to be temporary and goes with P2.
- Ordinary work: yes, because P2 is a decided, ordinary next change to project.py.
- Consequence: other (a false red that blocks a later merge; nothing is lost, nothing fails open).

## Notes, not findings
1. **An interrupt inside Python's grace period around A9's own commit** (P4c, forced with a `pre-commit` hook that sleeps 0.1 s; a hook that exits at once did not take, P4b):
   - Python waits 0.25 s for the child after a SIGINT, the commit finishes in that time, and HEAD moves to A9's own commit.
   - The result is `HEAD_MOVED` with `cause: KeyboardInterrupt`, while A9's commit stands complete. The copies and record stay committed and are not removed, which is correct; the edit is kept, and `new.txt` went into the commit (residual 3).
   - This is run 5's decided `HEAD_MOVED` rule, and the first check noted it too.
   - Ordinary work: no, because the signal must land in a fraction of a second.
   - Consequence: other (it reports not-ok on a commit that landed; nothing is lost and nothing fails open).
2. **The engineer's three risks:**
   - (1) The mode is not compared: a staged chmod of A9's own copy is undone, together with A9's bytes. Ordinary work: no, because it needs a mode change of A9's just-written file during the run. Consequence: other. A row.
   - (2) A copy edited between `hash-object` and `git add` (milliseconds): the index then holds an entry that is not A9's blob, and the tree bytes are not A9's, so both stay, with someone's edit staged. Ordinary work: no, because of the millisecond window. Consequence: other (nothing lost). A row.
   - (3) A successful commit takes whatever was staged during the run (seen in P7). This is the interface's named residual. Ordinary work: yes. Consequence: other, nothing lost.
3. **A partial write** (for example a full disk) of the record or of a copy leaves bytes that are not A9's, so the undo keeps them. An untracked partial record then makes the next A9 refuse `ADOPT_WOULD_OVERWRITE`. This matches the interface's "only while still A9's bytes" and was the same before the change. Ordinary work: no. Consequence: other.
4. **Stale docstring:** Case C's docstring still says "exit 2", but the assertion checks 1, as the lead corrected. Text only.
5. **Uncovered ways in the acceptance cases:** they do not cover the record's write or add failing, a real interrupt mid-commit, `HEAD_MOVED`, or the undo after `WOULD_OVERWRITE`. The README names this (reading (e)). The unit tests and my P4, P5 and P10 cover them, and all were sound.

```verdict
{"kpis": [{"kpi": "success-3", "verdict": "pass", "findings": []}, {"kpi": "success-16", "verdict": "pass", "findings": [{"id": "NC2-1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}], "overall": "pass"}
```