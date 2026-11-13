# Brief rev-2: independent auditor (FULL review, round 2, the last) for DAEO-emq1 (W2-115), class C3

Budget: projection 8 USD. Keep your context short; cut long outputs to head and tail.

You are the independent auditor for ticket DAEO-emq1 (W2-115): `gov close`, the smart close (scoped runs only, a close
refused only by a red its own change caused, the culprit of a batch sent back, no lists, a close record, the nightly's
full secrets scan; the strict close kept built). `gov close` is the judge's core (class C3): probe hard. Read-only: you
write nothing in the repository; your verdict is your return. Probe head `f39289d3a379` of branch `w2/W2-115`
(`git -C /home/usain/gov-os-worktrees/W2-115 rev-parse HEAD` must show it; if not, stop and say so). This is **round 2
of 2, the last** (DEC-1010): a finding that still blocks goes to the CTO as a package; there is no round 3.

## Step 0, before any work (report it first in your return)

`printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-emq1`). Do step 0 of
`/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id `DAEO-emq1`:
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-emq1','w').write('x')"` must FAIL. If it wrote
the file, stop and return.

## Round 1 and what was decided

Round 1 (`docs/probes/DAEO-emq1/PR-DAEO-emq1-round-1.md`, read it whole) failed on F-1 (blocking, fails open: reds
judged against the parent of the oldest trailered commit, not the green base). The CTO's decisions (the ticket's lines
"PK-3 (a)", "PK-4", "PK-5" near its end):
- **PK-3 (a)**: F-1 fixed: a red is judged against the green base when it is an ancestor of HEAD, else the parent of
  the ticket's oldest own commit (DEC-988 item 3, DEC-989); **F-3** folded in (a batch culprit whose red is its own
  new test is blamed once confirmed with that candidate alone); **F-7** folded in (the research doc states its method
  honestly, its script inline).
- **PK-4** (F-4, who commits the probe record vs S11's writer check): a row for the CTO's launch tool, not this
  ticket; it does not block this land. **PK-5** (F-5, the green base in a scoped project while the nightly is red): the
  owner's, not this round; it does not block this land.
- F-2, F-6, F-8, F-9 were not changed this round. Re-report any round-1 finding only if this round's change made it
  new or worse; say which.

## What changed in this round (probe this first and hardest)

| commit | what |
|---|---|
| 451a775fa | the independent test designer's new acceptance cases (F-1: 4, F-3: 4) in tests/acceptance/W2-115/ |
| bdbf7f069 | F-7: docs/research/W2-115-smart-close.md's method and inline script |
| 4810c0828 | F-1: `select.head_without_change`; the close uses it as the base |
| b5ae48b88 | F-3: `batch.isolate` confirms an absent red with the candidate alone |
| 99dbe5450 | red iteration 1 (S4/F-1): the nightly's record replaces the run on the base only when it excuses the red |
| f39289d3a | red iteration 1 (S6/F3): the run on the rest leaves out targets the rest's commit does not hold |
| d8db5bb6f | the lead: round 1's probe record gains `implementer_session` (probe.schema.json) |

The fix round's code alone: `git -C /home/usain/gov-os-worktrees/W2-115 diff ce6a2addf f39289d3a -- src tests/unit docs/research`.
The ticket's whole change: `git -C /home/usain/gov-os-worktrees/W2-115 diff 010399309 f39289d3a` (010399309 is
w2/integrate's head merged at 1a3664a20; the diff is this ticket's work alone).

In particular probe:
1. F-1: plant a green record at G, an untrailered commit breaking a test, then trailered work: the scoped close must
   refuse `RED_CAUSED`, mark the red caused, open no repair ticket. Then the green base **not** an ancestor of HEAD;
   then no green base. Any path where a red the change caused is excused (fails open)? Did the selection (S2, S3) move?
2. 99dbe5450: the nightly's record is the free first step (S4). When the night at the base has the red with the same
   failure type, it is not the change's without a run; otherwise the red runs on the base. Can a night's record excuse
   a red with another failure type, a timeout or no record? Is the night read at the right commit?
3. F-3 and f39289d3a: a batch A, B, C where A adds a red test: A goes back, B and C land on the same run, A confirmed
   red with A alone before anything lands. A red that is not red with A alone: the batch refuses. Can the targets
   filter let the rest land **untested** (an empty or shrunken target list, a culprit adding a test function to an
   existing file, a renamed file)? Can an absent red confirmed by a timeout or an unknown result blame a candidate?
4. F-7: does the document state exactly what was run and computed, and does its inline script reproduce the table?
5. The test designer's discovery: a refused scoped close writes no close record (the refusal is the record). Judge it
   against S7 ("each close writes its close record ... every red with its reason"); say whether it is a finding, its
   scope and consequence.

Then re-check the rest briefly (round 1 found S1, S3, F2, S8, S10, S13 and S11's parsing sound): S1-S11, S13 and F1-F4,
each including its Verify's planted cases, failing closed; plant mutations of the fail-open paths changed this round on
a mirror copy under your sandbox TMPDIR, never in the tree (point PYTHONPATH at the mirror). Scope:
`git diff --name-only 010399309 f39289d3a` lists only the ticket's `allowed_paths:`, `tests/acceptance/W2-115/**`, the
six W1-39/W2-77 files (td-3) and the probe record; the acceptance tests changed only in the test designer's commits.

## What to read

| what | path |
|---|---|
| ticket: KPI lines S1-S13 and F1-F4 with their Verify are the spec; its sections "Interface", "Delegated", "PK-1 and PK-2", the PK-3..PK-5 lines | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-emq1.md |
| the lead's naming for what the Interface leaves open (claims to check, not to trust) | /home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/lead/briefs/shared-interface.md |
| the code | src/gov/close/{command,select,batch,attribution,nightly,tool}.py; governance/project/close.yaml; template/governance/project/{close,test-map}.yaml |
| the measurement (S9) | docs/research/W2-115-smart-close.md |
| tests | tests/acceptance/W2-115/ (the independent test designer's), tests/unit/close/test_w2_115_*.py (the engineers') |
| the strict close's own suites (F4) | tests/acceptance/W1-30/, tests/acceptance/W2-07/ |
| the reviewer's verdict form (S11) | governance/project/briefs/JUDGEMENT.md |
| sources (grep docs/DECISION_REGISTER.md only by id, e.g. `### DEC-1083`) | DEC-983, DEC-982, DEC-979, DEC-968, DEC-966, DEC-953, DEC-1001, DEC-1002, DEC-1003, DEC-1010, DEC-1014, DEC-1015, DEC-1050, DEC-1083, DEC-959, DEC-988, DEC-989, DEC-1123, DEC-1125, DEC-1052, DEC-1079, CAP-33 |

Search with Read, Grep and Glob; if a first search does not answer, search once more in different words, then answer
from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context`.

Out of this round (do not judge as missing): **S12** (the trailers switch: a kernel check file that waits for its
CIT-P, independent review and the owner's approval, CAP-33). Judge S12 as `"verdict": "pass"` with a finding
`{"scope": "out", ...}` naming it deferred. The merge-queue lines are W2-115b's (DAEO-j9z6).

## Runs

Planted folders only (pytest's tmp_path or your TMPDIR), never a real close of this repository, never a real
`gov launch`. **Every pytest run goes through the heavy-slot gate**, with a TMPDIR outside the repository and outside
`~/gov-os-runs`, `PYTHONUSERBASE=/home/usain/.local`, an empty `HOME`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`:

    env HOME=/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local TMPDIR=/tmp PYTHONPATH=/home/usain/gov-os-worktrees/W2-115/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <folder or file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"

(if TMPDIR=/tmp is refused in your sandbox, use your sandbox's TMPDIR). The base-red rule: a red that is not this
ticket's and also fails on w2/integrate's head is a shared base red, not blocking: the six W2-96 signal cases in
tests/unit/accept/test_w2_96_{run2,review3,review4}.py and the two W2-153 cases
(tests/unit/adapters/test_w2_153_compose.py::test_the_twelve_sources_are_the_composition[],
test_w2_153_portability.py::test_this_repositorys_sources_are_the_composition; red alone on w2/integrate f29fa36521e3).
The lead's verify of this head: RED parallel 4594 tests, 8 failed (those eight alone), 6 skipped; serial 1 entry
green; gov accept 85 passed 0 failed (S12 has no tests by P4).

A session refused twice for an action stops and says so; it never reaches the same effect by another command, form
or file (DEC-1142 (9)).

Judge against ADR-0001's threat model (DEC-801): a finding is blocking only if an honest agent or operator hits it in
ordinary work and it fails open (closes what it must not: a caused red excused, a culprit landed, an unexplained batch
closed, a rest landed untested, a full suite or a list read in the scoped close, a false READY) or loses work. For each
blocking finding, say the smallest fix, the planted input that shows it, and two or three options with their cost (the
CTO decides it as a package).

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
Number this round's findings R2-1, R2-2, ... Then the per-KPI block (a fenced block with the info string `verdict`,
JSON: `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "R2-1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}`,
one entry for each of S1-S13 and F1-F4). Then `guard_refusals:` (none, or each: time | form | the hook's reason | true
or false-positive).
