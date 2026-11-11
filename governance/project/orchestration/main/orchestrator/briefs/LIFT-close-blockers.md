# The lift's closes: every pre-measure finding, surveyed read-only, and the owner's path-map edit drafted

Read `LIFT-common.md` first (scratch only; the CTO's main tree must stay exactly at HEAD). Role: ACT-preparation
helper, Sonnet high, class C2 (DEC-1120). Scratch folder: `.gov-runtime/scratch/orchestrator/drafts/lift-close-blockers/`
(absolute: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/lift-close-blockers/`).

## What happened
`gov close DAEO-blwa` (W2-122) at 13:38 UTC refused, `CHECK_FAILED`, 7 findings, and filed repair ticket
`.tickets/DAEO-feon.md` (commit `ce8449ada`; read it):
- six `WORK_WITHOUT_TASK`: old merge commits (e.g. `5bf20b532` "Merge w2/integrate into w2/W2-112 (the CTO)",
  `1296a57bc`, `24b3bf2f6`) with no `Task:` trailer that touch W2-122's paths;
- one `LOAD_SENSITIVE_REFUSED`: `governance/project/path-map.yaml` `load_sensitive:` entry for
  `tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95` cites
  DEC-757, whose status is DONE, not ACCEPTED, so "it covers nothing".
The next closes are W2-123 (`DAEO-qzrq`), W2-126 (`DAEO-jpr0`), W2-92 (`DAEO-n0wb`), W2-96 (`DAEO-ouet`), and W2-122
again. A second refused close of one ticket stops it (the two-refusal rule), so nothing is retried until the owner
acts on a complete list.

## Your work
1. **The rules, from the code** (`src/gov/close/command.py`, `src/gov/close/history.py`, `src/gov/close/repo.py`;
   read, never run `gov close`): which gates run before any test; which refusals are counted (DEC-868 (3): the commit
   gates and the pre-close gate are not; say which these are); whether `accepted_history` (DEC-734: `{commit,
   decision}` entries in the path map, each decision ACCEPTED by the owner and naming the commit) also clears
   `WORK_WITHOUT_TASK` (`_check_unmeasured`), or only the trailer gate; and what else clears it (DEC-1123 (4)
   exempted W1-01's merges "by the owner's commit": find how, in the register and the path map).
2. **The survey, read-only,** for each of the six tickets above: every finding the pre-measure gates would give at
   HEAD (call the module's own functions from a Python script you write in your folder, with `PYTHONPATH` the main
   tree's `src`; a script that writes nothing; never a test run, never `gov close`). If a function cannot be called
   without writing, say so and compute the same answer with `git log` by the rule you read. Also every
   `load_sensitive` and `accepted_history` entry whose decision is not ACCEPTED by the owner (it would refuse every
   close). Table: ticket, gate, commit or entry, why.
3. **The draft for the owner's commit** (`path-map-edit.diff` in your folder, against HEAD's
   `governance/project/path-map.yaml`): (a) the W1-19 entry's `decision` to DEC-1125 and `fixed_by` to W2-155
   (`DAEO-ar89`), keeping its reason; if W2-13's warm-latency test also has an entry, the same; if it has none and
   a close would run it, say so; (b) the `accepted_history` entries for every commit in your survey, each with
   `decision: DEC-1127` (the decision the CTO will ask the owner for: "these merges are accepted as history"), unless
   step 1 shows another route is the right one. Check the edited file parses (`python3 -c "import yaml; ..."`) on a
   copy in your folder. Also the exact commit command the owner runs (`git commit` with `Role: owner`, the
   decision trailer), as `ACT-CLOSE-HISTORY-1.md` in your folder: what, why, the list, the command, the rollback,
   and a rehearsal: on a clone in your folder (`git clone --no-hardlinks` of the main tree), apply the diff and run
   your step-2 script again: zero pre-measure findings for the six tickets is the pass.
4. Any finding that the owner's edit cannot clear: name it, with your recommendation.

## Return
The twelve fields, short; the table; the counted-or-not answer; the files written. Estimate 1 to 1.5 h.
