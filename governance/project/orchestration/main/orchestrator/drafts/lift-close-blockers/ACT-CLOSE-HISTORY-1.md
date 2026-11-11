# ACT-CLOSE-HISTORY-1: the owner's commit that clears the pre-test refusals of the lift's closes

Class (O): the path map's ratchet lists and accepted history are read only from the owner's commits
(`governance/project/operator/class-rules.yaml`, id `path-map`). Prepared by a read-only helper on 11-11; nothing
in the main tree was touched. Rehearsed on a clone: see "Rehearsal". What the commit does not clear is in
"What no edit clears", which reads on its own.

## What

One commit by the owner on `w2/integrate`, changing one file, `governance/project/path-map.yaml`, under one
decision, DEC-1127:

1. **A new list, `accepted_history`, of 18 old merge commits**, each with `decision: DEC-1127`. They are merges
   made before the merge rule (a `Task:` trailer on every merge) was kept. `gov close` refuses a ticket for each
   one that changes the ticket's own paths: "work on the ticket that no ticket measured".
2. **One `load_sensitive` entry changed**, the warm-query latency case of W1-19
   (`tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95`):
   `decision` DEC-757 to DEC-1127, `fixed_by` W2-M332 to W2-155. The reason is kept.
3. **Three `acceptance_exemptions` entries changed**, `decision` to DEC-1127, the old decision kept in each
   entry's comment: `c9a086786444` (was DEC-900, now DONE), `ab169d051b82` and `15952bbfa576` (were DEC-1123,
   whose text names neither). W1-01 reads `decision` as `DEC-<n>` and ignores comments, so its rule is unchanged.

## Why

`gov close DAEO-blwa` (11-11 13:38 UTC) was refused for 7 findings: 6 of kind 1 and 1 of kind 2. The same two
kinds refuse the next closes (W2-123, W2-126, W2-92, W2-96, W2-122 again) and D-10's three (W1-01b, W2-66b,
W2-90c). The refusals come before any test and spend no attempt (DEC-868 (3)), but the repair ticket's own KPI
lines (`.tickets/DAEO-feon.md`) cannot be met by a code fix: the commits are history.

- **Kind 1** (`WORK_WITHOUT_TASK`, `_check_unmeasured`): the owner's list clears it. `gates.decision_records`
  subtracts every commit that `accepted_history` (or `acceptance_exemptions`, if its decision names the commit)
  lists, "whatever it changes" (DEC-923 (2)), before the gate runs. The trailer gate (`_check_trailers`) reads the
  same list but judges only the ticket's own commits, so it was never the blocker here.
- **Kind 2** (`LOAD_SENSITIVE_REFUSED`): DEC-757 is DONE (DEC-1098 (3)), and only an ACCEPTED owner decision
  that names the test counts. **DEC-1125 cannot be the entry's decision as first planned:** it is ACCEPTED, but its
  text names neither the test's file nor its name, so the ratchet would refuse it ("DEC-1125 does not name the
  test"; checked with `dec1125_names.py`). DEC-1127 names the test, as DEC-762 (3) did for its 17 entries.
  W1-19's test and W2-13's warm-latency test are both routed to the nightly (`tests/acceptance/serial-only.txt`),
  so no close runs either; W2-13's test has no entry and needs none.
- **The three exemption entries** did not clear what they listed: DEC-900's status is DONE, and DEC-1123's text
  does not name two of its commits, so `gates.owner_listed` ignored them.

## Before the owner's commit (the CTO)

1. Commit DEC-1127 in the register (`Role: orchestrator`, `Task: decision-record`, `Implements: DEC-1127`), from
   `DEC-1127-draft.md` in this folder. **The draft's status line says PROPOSED; change it to the owner's real
   answer first.** The ratchet reads only `ACCEPTED (owner, ...` and the decision must name each commit it lists
   (it does, by 12 digits).
2. Re-run the survey on a clone of the then-HEAD: `bash rehearse.sh` (this folder). It regenerates
   `entries.yaml`, `path-map-edit.diff` and `DEC-1127-draft.md` from the survey. Every merge made after
   11-11 13:44 without a `Task:` trailer that touches a lift ticket's paths is a new finding; the regenerated
   files cover it. Cheaper: give every new merge its ticket's `Task:` trailer from now on.
3. `git apply --check` the diff on the main tree (it must say nothing). The main tree must be clean.

## The commands (the owner, in `/home/usain/Dynamic-Agentic-Engineering-OS`, on `w2/integrate`)

```
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/lift-close-blockers
cd /home/usain/Dynamic-Agentic-Engineering-OS
git status --short                     # must print nothing
git apply --check "$D/path-map-edit.diff" && git apply "$D/path-map-edit.diff"
python3 -c "import yaml; d=yaml.safe_load(open('governance/project/path-map.yaml')); print(len(d['accepted_history']), d['load_sensitive'][0]['decision'], [e['decision'] for e in d['acceptance_exemptions']])"   # prints: 18 DEC-1127 ['DEC-1127', 'DEC-1031', 'DEC-1123', 'DEC-1123', 'DEC-1123', 'DEC-1127', 'DEC-1127']
git diff --stat                        # one file, 45 insertions, 5 deletions
git commit -m "Owner decision DEC-1127: accepted_history lists eighteen old merges; the W1-19 load_sensitive entry and three acceptance_exemptions entries take DEC-1127 (ACT-CLOSE-HISTORY-1)" \
  --trailer "Task: decision-record" --trailer "Implements: DEC-1127" --trailer "Role: owner" \
  -- governance/project/path-map.yaml
git log -1 --format='%h %(trailers:only)'
```

The `Role: owner` trailer must be in the final trailer block (the ratchet reads it from there). After the commit
the CTO rebuilds the store (`STORE_STALE` otherwise) and runs the closes.

## The 18 commits

All are two-parent merges with no `Task:`, `Role:` or `Implements:` trailer.

    - `6ed6a5aed047` (2026-11-02): Merge emg/query: the DEC-1033 emergency patch (fix b): a question's ...
    - `1296a57bc60b` (2026-11-03): Merge w2/W2-91 into w2/W2-91-tests: the engineer's merge of integrate ...
    - `24b3bf2f67e5` (2026-11-06): Merge w2/integrate into w2/W2-134-tests (the CTO): the W2-134 ticket
    - `ffbf0392d236` (2026-11-06): Merge w2/integrate into w2/W2-32 (the CTO): S11 re-worded (DEC-1086 A), ...
    - `e3355def9f99` (2026-11-06): Merge w2/W2-32 into w2/integrate (the CTO, DEC-1086 A, DEC-1087 (1)): ...
    - `afea87dca49d` (2026-11-06): Merge w2/integrate into w2/W2-135-tests (the CTO): W2-32 S11 merged; ...
    - `2bb3705dbd0f` (2026-11-06): Merge w2/integrate into w2/W2-129 (the CTO): TESTS-READY and the ...
    - `2b733c4589b8` (2026-11-06): Merge w2/integrate into w2/W2-116 (the CTO): TESTS-READY and the ...
    - `87cadea156e4` (2026-11-06): Merge w2/integrate into w2/W2-129-tests (the CTO): S16 added (DEC-1088 ...
    - `75acb0ff22e7` (2026-11-06): Merge w2/W2-116 into w2/integrate (the CTO, DEC-1087 (3)): the ...
    - `419f828a8b51` (2026-11-06): Merge w2/integrate into w2/W2-129 (the CTO)
    - `ff64f14835f6` (2026-11-06): Merge w2/W2-135 into w2/integrate (the CTO, DEC-1086 B, DEC-1087 (1)): ...
    - `5bf20b53224d` (2026-11-06): Merge w2/integrate into w2/W2-112 (the CTO): the memory release for ...
    - `f67e57deb9dd` (2026-11-09): W2-128 tests: integrate merged (the interface's ref and string items, ...
    - `befa57695c38` (2026-11-09): Merge w2/integrate into W2-56: the ticket's round-2 points (P-S7), ...
    - `3f93c137a4b6` (2026-11-10): W2-153-tests: integrate merged (ACT-SETS-GLOBS-1's hook 74f8dbea4761 ...
    - `c667bc49ca0a` (2026-11-10): W2-153-tests: integrate merged (round 2b, f3c15908d)
    - `08c31e7ffee0` (2026-11-10): scratch: the designer's S-D10a/b cases beside the engineer's code, for ...

## Rollback

`git revert <the owner's commit>` as the owner (`Role: owner` in the revert's trailers). It restores the path map
byte for byte, and the closes are refused again as before. Do not reset or amend. If the path map must change
again before the revert, the CTO prepares a new diff with `rehearse.sh`.

## Rehearsal (11-11, a fresh clone at the main tree's HEAD, `8c18fa300`; `rehearsal.log`)

`rehearse.sh` clones the main tree with `--no-hardlinks`, runs the survey, builds the diff, commits the DEC-1127
draft (with the accepted status the CTO will write) as the orchestrator, applies the diff, checks it parses,
commits as the owner, and runs the survey again.

| ticket | pre-measure findings before | after | containment (counted) |
|---|---|---|---|
| DAEO-blwa (W2-122) | 7 | 0 | none |
| DAEO-qzrq (W2-123) | 11 | 0 | none |
| DAEO-jpr0 (W2-126) | 14 | 0 | 2 findings |
| DAEO-n0wb (W2-92) | 15 | 0 | 7 findings |
| DAEO-ouet (W2-96) | 7 | 1 (probe gate) | 2 findings |
| DAEO-vhad (W1-01b) | 5 | 0 | none |
| DAEO-zuiy (W2-66b) | 5 | 0 | none |
| DAEO-fu3n (W2-90c, still `open`) | 5 | 0 | none |

D-10's three have the same four commits as the lift tickets (all inside the 18) and the same load_sensitive
refusal; with the edit they have no pre-measure and no containment finding at HEAD.
After the edit: `load_sensitive` 24 of 24 entries count, `accepted_history` 18 of 18 accepted, `acceptance_exemptions`
7 of 7 clear their commit. `gov.check.pathmap` and `gov.check.schema` exit 0 on the clone. W1-01's acceptance
folder on the clone after the owner's commit: 54 passed (12 deselected by its conftest); `w101.log`.

## What no edit clears: the counted findings for W2-126, W2-92 and W2-96

The owner's commit clears every refusal that comes before the tests, except W2-96's probe gate. Two more gates
refuse, and no path-map edit reaches either. Both come from the guard's and the probe's own rules, which read no
list of the path map.

**1. Containment (counted: each refusal spends one of three attempts).** Run read-only at HEAD with the edit
applied (`containment.py`, `containment.txt`):

| ticket | commits | why |
|---|---|---|
| DAEO-jpr0 (W2-126) | `15c80ebb72b7`, `b32fdb80f5fc` | merges whose own change is an acceptance test or a ticket file, not git's own merge of their parents |
| DAEO-n0wb (W2-92) | `720a2cbb66e0`, `4e9ba434eb70`, `a01fc5f456cd`, `295d23c5112c`, `e270a5206b60`, `0024c753aaf6` | the engineer's commits of `docs/changes/W2-92-evidence.md`, which the ticket's `allowed_paths` do not list |
| DAEO-n0wb (W2-92) | `5fc7681a1214` (11-11, a test designer) | changes `tests/conftest.py`; a test designer may write only `tests/acceptance/**` |
| DAEO-ouet (W2-96) | `65fa76dc3cf2`, `6bcbbcdd5511` (11-10, a test designer) | change `tests/unit/accept/test_w2_96_*.py` and `w2_96_reap.py`; same rule |

**2. W2-96's probe gate (FULL profile).** It stops at its first finding; three stand (`probe_all.py`,
`probe-all-ouet.txt`): the `independent-auditor` commits `3f975a3e6ea5` and `efb8acb1b596` of another ticket
(DAEO-h2k3, 11-05 and 11-04) lie in W2-96's range, and the gate refuses any such commit in a FULL ticket's range
(DEC-137); and `1905b29699a7` (Role: orchestrator, 11-10) changes the ticket file and
`governance/project/orchestration/DECISIONS-IN-FORCE.md` after the final probe's commit `8f6e66a17572`, while the
integration-side-edit exception needs the ticket file to be the only path. Every FULL ticket opened before 11-04
gets the first refusal once it has a probe record (W2-05 shows it already).

**Options (DEC-105 form).**

- **A. Apply now, in code.** Two changes: the probe gate's reviewer-role refusal applies only to commits that name
  the ticket or change its work, and its ticket-file exception also covers orchestrator commits whose other paths
  are orchestration records; and the containment judgement reads `accepted_history` as the close's other commit
  gate does (`src/gov/guard/containment.py` is a control: an ACT). Cost: a ticket, an independent review and a wheel
  re-pin, so days. It clears W2-96's probe gate and all containment findings for every ticket, and fixes the same
  false refusal for the product.
- **B. Re-baseline, ticket by ticket (recommended for now, confidence medium).** For W2-96: the owner decides its
  `profile` is STANDARD, so the probe gate does not run (its four passing probe records stay as evidence); one line in
  its ticket file. For the containment commits: an owner decision that names them as history, and the ticket closes
  with `tk close` named for the exit auditor (DEC-492, DEC-757 (1)). For W2-92's six `docs/changes` commits only, adding
  `docs/changes/W2-92-evidence.md` to its `allowed_paths` also works, but DEC-757 (6) forbids editing a reviewed
  ticket: an owner call. Cost: one decision, no code; W2-126, W2-92 and W2-96 close by `tk close`, not a clean
  `gov close`.
- **C. Defer.** Close W2-122, W2-123 and D-10's three now (no pre-measure or containment finding; their tests are not surveyed), and hold W2-126, W2-92 and W2-96
  until A lands. Cost: those three wait days; the lift waits on them.

Until the owner chooses, do not run `gov close` on W2-126, W2-92 or W2-96: each refusal at the containment gate is
counted, and three stop the ticket.
