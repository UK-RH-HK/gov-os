# W2-23 (DAEO-kmcr), independent auditor, FULL review round 2 — S3 only (the last round, DEC-1010)

Budget: projection 4 USD. Class C2 on FULL.

**Role:** independent-auditor, a fresh read-only session. Write nothing in the repository; your verdict goes in your
return. **Worktree:** `/home/usain/gov-os-worktrees/W2-23`, branch `w2/W2-23`. **Probe:** head `3e7194a45a58`; this
round's change is `fd1bc056f5ba..3e7194a45a58` (the acceptance cases merged at 4111fab26 from 9dc7b24af, test designer;
the fix 3e7194a45, engineer). **Ticket:** `DAEO-kmcr` (W2-23), class C2, profile FULL.

## Step 0, before any work (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-kmcr`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kmcr','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` must work. If (a) wrote the file, stop and return. Then read
`EMG-common.md` beside it; its rules hold. First `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`,
`DAEO-kmcr`). No `gov retrieve` or `gov context`; search with Read and Grep, and once more in other words if the first
search does not answer (DEC-1065). No reset, checkout, clean, commit, merge or install; scripts and planted fixtures
only under your sandbox `TMPDIR`.

## Scope: S3 only

Round 1 (another reviewer) passed S1, S2, S4, S5, S6, S7 and F1 and failed S3 on two findings. The CTO decided a fix
round limited to S3 (ticket `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-kmcr.md`, last paragraph
"Delegated ... run 3's P-W2-23-7 (a)"; binding, DEC-1112 (3)). Judge only S3 — "The A8 dependency proof finds every
listed citation form" — against **Interface item 6** and that paragraph. Round 1's two findings, as reported:
- **R1:** a folder citation or a `../` relative-tail citation followed by a full stop (end of a sentence) was not found
  (`safety.citations`, `src/gov/adopt/safety.py`).
- **R2:** a citation of the store's folder was found only when it was a file's immediate parent folder; a store whose
  files all sit in subfolders, cited by the folder that holds them, was not found. The CTO's reading of "the store's
  folder": **the deepest folder holding all the store's files, and each folder between it and a file.** (So for a
  single-file store, its folder is that file's own parent; a folder above the store's folder is not a citation.)

Check that R1 and R2 are fixed through the A8 proof (`src/gov/adopt/legacy.py` `_proof` calls `safety.citations`),
and probe as an adversary whether the change: breaks any other listed form of item 6 (a word character or `-` before
the path or id; backslashes; URL-encoding; another letter case; a path split across lines; a glob; an id in prose);
lets a citation of the store in an ordinary sentence still slip through (fails open); or now finds something item 6
does not list in a way that would wrongly hold back a store in ordinary work. Rows already triaged from round 1 (R3:
leading-wildcard and brace globs skipped on purpose; R4-R9 on other lines) are not to be re-raised. Context packet
(ticket and mandatory inputs): `/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/lead/briefs/rev-context-2.md`;
decisions by id in `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` (DEC-729, DEC-1052,
DEC-954, DEC-315, DEC-1112, DEC-1010).

Run the tests yourself (no edits), and judge every failure:
`env HOME=/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src python3 -m pytest tests/unit/adopt/test_safety.py tests/acceptance/W2-23/test_w2_23_citations.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
Facts from outside the sandbox (the lead, at this head): `gov accept W2-23` 29 passed, 0 failed (S3 9: the 2 old
cases and 7 new); W1-41 3 passed. Inside the sandbox some MOVE cases stop at `ADOPT_CODE_GRAPH_UNREADABLE` (the code
graph cannot run there); that is the sandbox, not the code, and none is an S3 case.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing):
`task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:`
Then your findings, each with an id (R2-1, R2-2 ...), the file:line, what happens, and a reproduction; then exactly one
fenced block opened by ```verdict holding JSON in this form (S3 only):
`{"kpis": [{"kpi": "S3", "verdict": "pass|fail", "findings": [{"id": "R2-1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`
Then one line: `VERDICT: READY` or `VERDICT: NOT READY`, with the probe head.
