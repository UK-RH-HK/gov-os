# Brief rev-1: independent auditor (FULL review, round 1) for DAEO-emq1 (W2-115), class C3

Budget: projection 8 USD.

You are the independent auditor for ticket DAEO-emq1 (W2-115): `gov close`, the smart close (scoped runs only, a close
refused only by a red its own change caused, the culprit of a batch sent back, no lists, a close record, the nightly's
full secrets scan; the strict close kept built). `gov close` is the judge's core (class C3): probe hard. Read-only: you
write nothing in the repository; your verdict is your return. Probe head `569c2933d33c` of branch `w2/W2-115`
(`git -C /home/usain/gov-os-worktrees/W2-115 rev-parse HEAD` must show it; if not, stop and say so). This is round 1 of
at most 2 (DEC-1010).

## Step 0, before any work (report it first in your return)

`printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-emq1`). Do step 0 of
`/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id `DAEO-emq1`:
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-emq1','w').write('x')"` must FAIL. If it wrote
the file, stop and return.

## What to read
| what | path |
|---|---|
| ticket: KPI lines S1-S13 and F1-F4 with their Verify are the spec; then its sections "Interface", the "Delegated" paragraph, "PK-1 and PK-2" | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-emq1.md |
| the lead's naming for what the Interface leaves open (claims to check, not to trust) | /home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/lead/briefs/shared-interface.md |
| the code | src/gov/close/{command,select,batch,attribution,nightly,tool}.py; governance/project/close.yaml; template/governance/project/{close,test-map}.yaml |
| the whole change | `git -C /home/usain/gov-os-worktrees/W2-115 diff 0aec6e10c 569c2933d33c` (0aec6e10c is w2/integrate's head merged at 6831c6e3a; the diff is this ticket's work alone) |
| the measurement (S9) | docs/research/W2-115-smart-close.md |
| tests | tests/acceptance/W2-115/ (the independent test designer's), tests/unit/close/test_w2_115_*.py (the engineers'); the revised other-ticket cases: tests/acceptance/W1-39/test_w1_39_copy.py::test_copy_creates_the_overlay and W2-77's four key-set cases (td-3, d54172ffb) |
| the strict close's own suites (F4) | tests/acceptance/W1-30/, tests/acceptance/W2-07/ |
| the reviewer's verdict form (S11) | governance/project/briefs/JUDGEMENT.md |
| sources (grep docs/DECISION_REGISTER.md only by id, e.g. `### DEC-1083`) | DEC-983, DEC-982, DEC-979, DEC-968, DEC-966, DEC-953, DEC-1001, DEC-1002, DEC-1003, DEC-1010, DEC-1014, DEC-1015, DEC-1050, DEC-1083, DEC-959, DEC-988, DEC-989, DEC-1123, DEC-1125, DEC-1052, DEC-1079, CAP-33; the revisions: DEC-1142 (3), DEC-866 |

Search with Read, Grep and Glob; if a first search does not answer, search once more in different words, then answer
from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context`.

Out of this round (do not judge as missing): **S12** (the trailers switch: a kernel check file that waits for its
CIT-P, independent review and the owner's approval, CAP-33; `traceability.py` and the check yaml are untouched by
design); the merge-queue lines moved to W2-115b (DAEO-j9z6) by P1 (b). Judge S12 as `"verdict": "pass"` with a
finding `{"scope": "out", ...}` naming it deferred, or omit it and say why; do not fail the round on it.

## What to probe (at least these; find more)
1. Each of S1-S11, S13 and F1-F4: does the code do what the line says, including each Verify's planted cases, and fail
   closed? In particular:
   - S1/F4: no `close.yaml` runs strict; an unreadable file or another value is refused; the strict close's verdicts
     and refusals are unchanged (run W1-30 and W2-07's suites; compare against `git show 0aec6e10c:src/gov/close/command.py`).
   - S2/F2: a change no mapping covers is refused with its reason (`SELECTION_REFUSED`), never widened; no full-suite
     run anywhere in the scoped path; no accepted-reds or load-sensitive list opened or written (trace every `open`
     and every list path in the scoped path).
   - S3: `--select` prints exactly the set the close runs (one code path, or two that can drift?).
   - S4/F1: a red is "not the change's" only if the head without the batch has it red with the same failure type; a
     timeout or a missing record never matches; the nightly's recorded result read first; only load-sensitive cases
     get 3 rounds; no nightly-baseline clone. Look for any way an unrelated-looking red the change did cause is
     excused (fails open), or a red is judged on the wrong tree.
   - S5: an unowned red opens a repair ticket in `.tickets/`; where, with what content, and what if one exists.
   - S6/F3: the culprit found by building without each candidate (never by reverting merged code); an unexplained
     red, or a candidate that cannot be isolated, closes nothing; nothing lands before the culprit is found.
   - S7: every field of the close record present; a missing field a failed check.
   - S8: the nightly sets `GOV_SECRETS_FULL_SCAN=1` for the rebuild even when the caller's environment lacks it, and
     the record's `secrets_full_scan` says so; can the record say it ran when it did not?
   - S10: the warm clone reused (same folder, reset, stores kept); one that cannot be reset replaced and recorded.
     Can a dirty or wrong-head warm clone give a false green?
   - S11: READY computed from the reviewer's fenced block; malformed or incomplete refuses; a block last written by a
     non-reviewer commit refuses. Look for a way a lead's block passes.
   - S13: exit codes 0/1/2/3, `select.json`, a JUnit file per phase, one summary line, exit file written last; a
     killed run is 3, never 0.
2. Scope: `git diff --name-only 0aec6e10c 569c2933d33c` lists only the ticket's `allowed_paths:` plus
   `tests/acceptance/W2-115/**` and the six W1-39/W2-77 files (td-3). The acceptance tests changed only in the test
   designer's commits (`git log --format='%h %(trailers:key=Role,valueonly)' 0aec6e10c..569c2933d33c -- tests/acceptance`).
3. The two revised other-ticket cases: still exact (no subset check), and W2-77's `cleanup` still only on a failed
   removal.
4. The tests: would they catch a wrong implementation? Plant a few mutations of the fail-open paths (S4's matching,
   S6's isolation, S11's writer check, S2's refusal) on a mirror copy under your sandbox TMPDIR, never in the tree
   (the suites pin the tree's src: point PYTHONPATH at the mirror).
5. Smell for this repository's own names baked into product code (`w2/`, `integrate`, `DAEO-`, CTO tool paths) in
   `src/gov/close/`.

Runs: planted folders only (pytest's tmp_path or your TMPDIR), never a real close of this repository, never a real
`gov launch`. **Every pytest run goes through the heavy-slot gate**, with a TMPDIR outside the repository and outside
`~/gov-os-runs`, `PYTHONUSERBASE=/home/usain/.local`, an empty `HOME`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`:

    env HOME=/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local TMPDIR=/tmp PYTHONPATH=/home/usain/gov-os-worktrees/W2-115/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <folder or file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"

(if TMPDIR=/tmp is refused in your sandbox, use your sandbox's TMPDIR). Known and not this ticket's (the base-red
rule: also red on w2/integrate's head): the six W2-96 signal cases in tests/unit/accept/test_w2_96_{run2,review3,review4}.py.
The lead's verify of this head: RED parallel 4448 tests, 6 failed (the six W2-96 signal cases alone), 6 skipped; serial 1 entry green; gov accept 77 passed 0 failed (S12 has no tests by P4).

Refused twice for the same call: stop and say so; never reach the same effect by another command, form or file
(DEC-1142 (9)).

Judge against ADR-0001's threat model (DEC-801): a finding is blocking only if an honest agent or operator hits it in
ordinary work and it fails open (closes what it must not: a caused red excused, a culprit landed, an unexplained batch
closed, a full suite or a list read in the scoped close, a false READY) or loses work. For each blocking finding, say
the smallest fix and the planted input that shows it.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE or ESCALATION) / work_completed /
files_changed (none) / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then a fenced verdict block:
```
verdict: PASS | FAIL
head: <hash12>
findings: <n>
- <id> | <severity: blocking, major, minor> | <KPI line> | <file:line> | <what is wrong, the planted input and the wrong output>
```
Then the per-KPI block (a fenced block with the info string `verdict`, JSON:
`{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F-1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}`,
one entry for each of S1-S13 and F1-F4). Then `guard_refusals:` (none, or each: time | form | the hook's reason | true
or false-positive).
