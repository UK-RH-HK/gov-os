# W2-23 (DAEO-kmcr), independent auditor, FULL review (one round, DEC-1010)

Budget: projection 6 USD. Class C2 on FULL.

**Role:** independent-auditor, a fresh read-only session. Write nothing in the repository; your verdict goes in your
return. **Worktree:** `/home/usain/gov-os-worktrees/W2-23`, branch `w2/W2-23`. **Probe:** head `fd1bc056f5ba` against base
`abef7e045133` (the `w2/integrate` head merged back at c735912bc; `git diff abef7e045133..fd1bc056f5ba` is exactly
W2-23's delta, 25 files). **Ticket:** `DAEO-kmcr` (W2-23), class C2, profile FULL.

## Step 0, before any work (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-kmcr`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kmcr','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` must work. If (a) wrote the file, stop and return. Then read
`EMG-common.md` beside it; its rules hold. First `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`,
`DAEO-kmcr`). No `gov retrieve` or `gov context`; search with Read and Grep, and once more in other words if the first
search does not answer (DEC-1065). No reset, checkout, clean, commit, merge or install; scripts and planted fixtures
only under your sandbox `TMPDIR`.

## What to audit

The ticket `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-kmcr.md` is the spec: judge each KPI line S1-S7 and
F1 against the code and the tests at the probe head, reading its **Interface** items 1-7 and the two "Delegated"
paragraphs as binding (the CTO's delegated decisions, DEC-1112 (3)). The governed context packet (ticket and mandatory
inputs) is `/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/lead/briefs/rev-context.md`; read decisions by id
in `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` (DEC-729, DEC-1052, DEC-954, DEC-315,
DEC-1112; DEC-838 for item 5's compaction rule).

The delta: `src/gov/adopt/safety.py` (new), `src/gov/adopt/stages.py` (call sites only, P-W2-23-1 (a): in `a0`, `a3`,
`_batch`, `a6`), `src/gov/adopt/project.py`, `src/gov/adopt/legacy.py`, `src/gov/adapters/command.py` and `merge.py`
(new, `gov adapters generate`); unit tests in `tests/unit/adopt/` and `tests/unit/adapters/` (with the moved fixture
programme, P-W2-23-6 (b)); acceptance tests `tests/acceptance/W2-23/` (independent test designer) and the one revised
W1-41 case (P-W2-23-5 (a)).

Probe as an adversary. In particular:
- S1/F1: can any restore path (`project.restore`, `project.commit`'s failure path, `_batch`) delete or overwrite an
  untracked or ignored file the tool did not write, a nested clone, or a file under an untracked directory? Does an
  untracked directory still raise anywhere?
- S4: a batch killed between steps (moves staged, no commit) and one failing at step 3: does the next
  `gov adopt --lite --stage A6` continue at the failed batch, are the rollback refs per run, is anything else staged
  refused naming the paths and never reset? Is there any window where the index is left half-staged?
- S2: the three files merged, programme lines first and in order, one marked block replaced in place on re-run, settings
  merged key by key, no compaction threshold anywhere (DEC-838); idempotence on a second run; a programme file with
  odd content (no trailing newline, CRLF, an existing marker pair, invalid JSON) must not lose the programme's text.
- S3: every form of Interface item 6; false positives that would make A8 pass wrongly.
- S5, S6, S7 as the ticket's verify lines say; for S6, quoting in hook command lines and subprocess calls in the delta.
- DEC-954 / P-W2-23-1 (a): does `stages.py` stay to call sites, with no hunk in W2-52's `run()` and `STAGE`?

Run the tests yourself (no edits), and judge every failure: in scope or not, and what it means.
`env HOME=/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src python3 -m pytest tests/unit/adopt tests/unit/adapters tests/acceptance/W2-23 tests/acceptance/W1-41 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
Facts from outside the sandbox (the lead, at this head): `gov accept W2-23` 22 passed, 0 failed (S1 2, S2 4, S3 2, S4 3,
S5 4, S6 4, S7 2, F1 1); `tests/acceptance/W1-41/test_w1_41_migration.py` 3 passed, 4 deselected. Inside the sandbox
some cases stop at `ADOPT_CODE_GRAPH_UNREADABLE` (the code graph cannot run there); that is the sandbox, not the code.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing):
`task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:`
Then your findings, each with an id (R1, R2 ...), the file:line, what happens, and a reproduction; then exactly one
fenced block opened by ```verdict holding JSON in this form (one entry per KPI line S1-S7, F1):
`{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "R1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`
Then one line: `VERDICT: READY` or `VERDICT: NOT READY`, with the probe head.
