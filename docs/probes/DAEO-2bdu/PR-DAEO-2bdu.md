---
type: probe
task: DAEO-2bdu
round: narrow check 2, after the first narrow check failed on NC-1 (DEC-1154's practice; the owner's P1-W2-88-NC-1 (a), 2026-11-13)
reviewer_session: 46ae9c42-9432-4df6-88b4-66d2a9425758
implementer_session: 393dbe31-d0db-417b-ab0d-92a448a8dfe7 (eng-5, run 6's fix aa476d394d30); test designer td-8 1a119ff5-d62d-47b7-a1ee-dca626d11fd6 (9990563fc8d9)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: pass
probed_commit: ed568a699e4fa82908fc3f8830e16733a8e7a5c4
decisions_applied: [DEC-1154, DEC-1010, DEC-136, DEC-820, DEC-1052, DEC-1120, DEC-801, DEC-802, DEC-808]
---

# Probe record: W2-88 (DAEO-2bdu), narrow independent check of the NC-1/NC-2 fix: PASS

Earlier records in this folder:

- the first narrow check (FAIL on NC-1) is `PR-DAEO-2bdu-nc-1.md`;
- round 2 (the last, DEC-1010) is `PR-DAEO-2bdu-round-2.md`;
- round 1 is `PR-DAEO-2bdu-round-1.md`.

This record is the narrow check the owner's decision P1-W2-88-NC-1 (a) called for. It covers only the change since 01ec6d2a7.

## The lead's judgement and triage

- **Who checked.** A fresh, read-only Independent Auditor (`46ae9c42-9432-4df6-88b4-66d2a9425758`, claude-opus-5-5, effort high, class C2).
  - It was started through `launch_worker.sh` / `gov launch` under the OS sandbox on 2026-11-13.
  - Its brief carried `governance/project/briefs/JUDGEMENT.md` word for word, plus the run-6 interface (`.gov-runtime/scratch/lead/briefs/run6-interface.md`).
  - Step 0 held. HEAD was ed568a699e4f, and `git status --porcelain` was empty at the start and at the end.
  - Its tripwire shows no change in this ticket's trees.
- **What it checked.** The change since 01ec6d2a7, against NC-1's and NC-2's stated behaviour:
  - the engineer's commit aa476d394d30 (`fabric.py`, `tests/unit/adopt/test_w2_88_nc1.py`);
  - the lead's 5aaff3dd8 (the evidence file's copy-step text);
  - td-8's cases 9990563fc8d9, merged at ed568a699e4f (`test_w2_88_nc1_commit.py`, `standin_nc1/`, `standin_nc2/`, the README's "Run 6 revisions").
- **The lead's verification at the head** (run outside the sandbox):
  - **`gov accept W2-88`:** outcome pass, every KPI line pass; 217 passed, 0 failed, 0 skipped (`.gov-runtime/scratch/lead/log/accept-6.txt`).
  - **td-8's cases were red on 01ec6d2a7 for the reasons the README states:**
    - Case C: the edit was reset to the committed text, the staged file was deleted, and a `reset` entry appeared in the reflog.
    - Case D, both parameters: A9's copies were left in the index.
  - **The rebuild:** ok, complete, `not_built` empty, four digests (`log/rebuild-6.txt`).
  - **lead_verify** (scoped, DEC-968) at ed568a699e4f: RED. The parallel run took 2,436 s: 6,269 tests, 3 failed, 11 skipped. The serial run passed 3 of 3 (`log/verify/parallel.xml`, `serial.xml`, `verify.log`). The three failures:
    - `tests/acceptance/W2-23/test_w2_23_space.py:94` (`context_watch.py` not in the settings' hook lines). This is a known red of the environment and integrate's; it was red in rounds 1 and 2 and in the first narrow check, and it is not this branch's.
    - Two load-sensitive W2-124 timing cases: `test_w2_124_s1_semantic_fails_named.py::test_s1_hung_or_transient_failing_embedder_raises_rebuild_failed_semantic[hung]` (72 s against 60 s) and `[part-way-500]` (62 s against 60 s). Run again alone once, both passed (2 passed in 43 s, `log/w2-124-alone.txt`, `log/w2-124-alone.xml`). The change touches no W2-124 path, no `src/gov/rebuild` file and no `src/gov/retrieval` file.
- **The verdict is PASS.** NC-1 and NC-2 are fixed, and success-3 and success-16 pass. The triage:

| finding | severity | triage |
|---|---|---|
| NC2-1: `test_w2_88_nc1.py::test_project_commit_and_restore_are_unchanged_since_01ec6d2a7` pins `project.py` to git history. It will go red when the CTO's P2 changes `project.commit` for A1 to A8. | minor (in scope; ordinary work: yes; consequence: other, a false red, nothing lost or failing open) | a row for the CTO's P2: P2 drops or replaces that test. The behavioural guard (`project.commit` and `project.restore` stubbed to raise while A9 still succeeds or refuses correctly) stays. |
| note 1: a SIGINT inside Python's 0.25 s grace period, while A9's own commit finishes, gives `HEAD_MOVED` with `cause: KeyboardInterrupt` over a commit that landed | row (ordinary work: no; consequence: other) | run 5's decided `HEAD_MOVED` rule; nothing is lost |
| note 2: the engineer's risks. (1) The mode is not compared. (2) A window of milliseconds between `hash-object` and `git add`. (3) A successful commit takes whatever was staged during the run. | rows (1) and (2): ordinary work no, consequence other; (3) is the interface's named residual | residuals |
| note 3: a partial write (a full disk) leaves bytes that are not A9's, which the undo keeps. The next A9 then refuses `ADOPT_WOULD_OVERWRITE`. | row (ordinary work: no; consequence: other) | the same as before the change |
| note 4: Case C's docstring still says "exit 2"; the assertion checks 1, as the lead corrected | text only | a row for the next edit of the suite |

The checker's report follows, unchanged.

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