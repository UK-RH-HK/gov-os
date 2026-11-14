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

