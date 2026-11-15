---
type: probe
task: DAEO-zmo4
status: final
reviewer_session: 847c7349-8b00-4bfa-a5af-c89a0a2c11c0
implementer_session: 2f1c9b8c-8ee4-4687-9748-cd1e9fb3d24d
test_designer_session: 92a3afeb-a643-4948-9e7b-e71feb056134
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: a57d7c4dcdb2eaa4befae8e1e1e719f90a8fc25c
reviewed_commit: 66026a90391c8746d52319ea7478e41fd158d5a4
decisions_applied: [DEC-1154, DEC-1188, DEC-801, DEC-802, DEC-808, DEC-809, DEC-1010, DEC-820]
scope: "W2-174 narrow independent re-check (DEC-1154) of the change merged after the review round: the test designer's ffd6d8b03 (F2's cases judge this ticket's own commits), at a57d7c4dcdb2"
---

# Probe record: W2-174 (DAEO-zmo4), the narrow re-check at a57d7c4dcdb2 (DEC-1154)

## Summary

- **What was checked.** `git diff 66026a90391c..a57d7c4dcdb2`: the independent test designer's `ffd6d8b03` (session
  `92a3afeb`), merged by the lead at `c7000431f`, which makes both F2 acceptance cases judge the files named by this
  ticket's own commits (`Task: DAEO-zmo4`) instead of the stale base `f2b1d38af` (the review round's F5; the full
  suite's red at `66026a90391c`), and the lead's record of the review round, `PR-DAEO-zmo4-r2.md` (`a57d7c4dc`).
  Nothing under `src/` changed since the review.
- **Who checked.** A fresh read-only independent auditor (`claude-opus-5-5`, effort high, class C2), session
  `847c7349-8b00-4bfa-a5af-c89a0a2c11c0`, through `launch_worker.sh`, JUDGEMENT.md word for word in its brief. It
  wrote nothing in the worktree (`git status --short` empty).
- **The lead's evidence.** `gov accept W2-174` at `c7000431f`, no variable set: 222 passed, 0 failed, all eleven lines,
  none unmapped. The folder on the ticket merged `--no-ff` into `w2/integrate` in a throwaway detached worktree: 222
  passed. The review round's full suite (7,425 tests) had two reds: the F2 case fixed here, and
  `tests/unit/retrieval/test_w2_112_shared_reranker.py::test_the_running_service_writes_one_memory_line_per_request`
  (load-sensitive, 1 passed alone).
- **Verdict.** Pass. N1 (in scope, ordinary work no, fails open): a Wave 3 row. N2 (out of scope, other): the
  product close's `review_verdict` reads only a block committed with `Role: independent-auditor` alone; this record
  and r2 are committed by the lead with `Role: orchestrator`, as the first pass's and W2-88's were before they landed
  through the CTO's queue. The lead reports it to the CTO and puts no reviewer's role on its own commit.

## The auditor's return, word for word

pass. Findings: N1 is in scope, not reachable in ordinary work, and fails open (a Wave 3 row). N2 is out of scope, reachable in ordinary work, and fails closed (consequence other; a row the lead must act on before the close). No finding blocks.

**Step 0, the sandbox check (launch_worker.sh):**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-zmo4` failed with `OSError: [Errno 30] Read-only file system`, and no file was left.
- (b) `git hash-object -w --stdin` worked (`1ae28402a109…`) and `git update-index --refresh` worked (exit 0).
- The `ps` check for ollama or llama-server showed nothing.
- HEAD is `a57d7c4dcdb2eaa4befae8e1e1e719f90a8fc25c`.

**What I checked and found sound:**
- **The diff.** `git diff 66026a90391c..a57d7c4dcdb2` touches only `tests/acceptance/W2-174/{test_w2_174_scope.py,w2_174_support.py,README.md}` and `docs/probes/DAEO-zmo4/PR-DAEO-zmo4-r2.md`. `git diff --stat … -- src/` is empty, so nothing under `src/` changed since the review.
  - In the test file, only `_names_changed_since_base` changed.
  - The support file only gained `TICKET_ID = "DAEO-zmo4"`.
  - The README changed only the F2 paragraph, the two F2 rows' notes and one note on the base.
- **(1) F2 still catches what it forbids.** I tested in a throwaway clone in `$TMPDIR`.
  - The clean head passes both F2 cases.
  - These changes each made the right case fail and name the file:
    - an uncommitted change to `src/gov/brief/__init__.py`;
    - a new untracked file under `template/governance/kernel/templates/`;
    - a commit with `Task: DAEO-zmo4` to `src/gov/brief/`;
    - the same to `src/gov/adopt/stages.py`;
    - the same to `template/governance/kernel/schemas/adoption-verdict.schema.json`.
  - On the ticket merged into `origin/w2/integrate` (`9fa839cba`) with `merge --no-ff --no-edit`, the same way `batch.py:485` merges: the clean merge passes both cases, and the planted brief and `stages.py` commits merged the same way make them fail.
  - The `W2_174_BASE` override still works the old way: `aa717e110` gives 2 passed, and `f2b1d38af` reproduces the review's F5 red on `stages.py`.
  - All 12 non-merge commits of this ticket since `f2b1d38af`, from every role and both passes, carry `Task: DAEO-zmo4`. The regex `^Task: DAEO-zmo4$` matches them per line.
  - This is the same way the close finds a ticket's commits (`_check_trailers` and `_check_containment` in `src/gov/close/command.py`).
- **(2) No other case or map row was weakened.** `parse_map` of the README gives the same result at `66026a90391c` and at the head: success-1..7 = 9, 15, 2, 36, 12, 11, 96 and failure-1..4 = 15, 2, 6, 20. Every line holds the same items as before. The brief's run of `test_w2_174_scope.py` at the head gave 7 passed.
- **(3) The record's form is sound.**
  - The front matter of `PR-DAEO-zmo4-r2.md` validates against `probe.schema.json` with no errors.
  - It has exactly one unquoted, unindented ```` ```verdict ```` block, which parses as JSON and names all 11 lines.
  - But see N2: the close does not accept it as committed.

**N1. A commit without the `Task:` trailer, or a merge commit, is no longer seen by F2.**
- What it is: when `W2_174_BASE` is not set, the cases judge only commits that carry `Task: DAEO-zmo4`, using `--no-merges`. Two kinds of change to a guarded path now pass where the old base diff caught them:
  - a commit with no trailer that changes only guarded paths;
  - a conflict fix inside a merge of integrate into the branch.
- How I reached it: in the clone, a commit with `Role: engineer` and no `Task:` line, changing `src/gov/brief/__init__.py`, gave 2 passed.
- KPI line: F2.
- Ordinary work: no, because every commit of this ticket in the range carries the trailer (12 of 12, all roles), and the commit rules in every brief require it. A commit without a trailer that also touches any of the ticket's own paths is already refused by the close's `WORK_WITHOUT_TASK` (`_check_unmeasured`). To get through, a commit has to lack the trailer and touch only guarded paths, or a merge's conflict fix has to edit `src/gov/brief/`, the kernel templates or schemas. The close's own containment check has the same blind spot.
- Consequence: fails open.
- Scope: in.
- What would reverse it: a commit of a ticket worker in this repository's history with no `Task:` trailer that changes only paths outside its ticket.

**N2. As committed, the close refuses the r2 record, and a narrow-check record that names only F2 would also be refused.**
- What it is: `review_verdict` (`src/gov/close/command.py:1718`) runs in the scoped close, which is on (`governance/project/close.yaml`: `close: scoped`), and in the merge queue's pre-check (`batch.py:742`).
  - It requires the newest record's verdict block to be last written by a commit whose role is `independent-auditor` alone.
  - It also requires that block to name every line of the ticket (7 success, 4 failure).
- How I reached it:
  - At the head, `review_verdict` returns `VERDICT_NOT_REVIEWER`: the block "was last written by a57d7c4dcdb2 with Role: orchestrator".
  - In the clone, a newer record whose block names only F2, committed with `Role: independent-auditor`, gives `VERDICT_MALFORMED` ("no verdict for the KPI line(s) S1, S2, S3, S4, S5, S6, S7, F1, F3, F4").
  - A block naming all eleven lines committed with `Role: orchestrator` gives `VERDICT_NOT_REVIEWER`.
  - The same block committed with `Role: independent-auditor` alone gives `READY`.
  - W2-88's records were also committed with `Role: orchestrator` and it landed anyway. I did not establish how.
- What it means for this record: the block below names all eleven lines, not only F2 as the brief's form shows. For lines other than F2 its pass says only that this change does not weaken them: no `src/` change, and the map items are the same. The r2 round's verdict and its non-blocking rows stand for those lines.
- KPI line: none; this is the record and the close, not the pass.
- Ordinary work: yes, because the lead committing a record with the lead's own role is the usual practice (see `git log -- docs/probes/DAEO-2bdu`).
- Consequence: other. It fails closed: the close refuses and nothing lands wrongly.
- Scope: out.
- What would reverse it: a close or merge-queue run at this head that returns READY from the record as committed, or the commits above showing a route that skips `review_verdict`.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "S6", "verdict": "pass", "findings": []}, {"kpi": "S7", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": [{"id": "N1", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "N2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F3", "verdict": "pass", "findings": []}, {"kpi": "F4", "verdict": "pass", "findings": []}]}
```

- task: DAEO-zmo4 (W2-174), the narrow independent re-check (DEC-1154) of `ffd6d8b03` (merged at `c7000431f`) at head `a57d7c4dcdb2`
- status: done; pass, no blocking finding
- work_completed: sandbox check; diff scope, with no `src/` change confirmed; F2 tested with planted changes in a clone, both in the ticket branch and on the `--no-ff` merge into `w2/integrate`, plus the override; README map compared through `parse_map`; probe record front matter validated against the schema and its block parsed; READY computed through `review_verdict`
- files_changed: none
- evidence:
  - planted runs: A, E1, E2, B, C, D and G in the branch, F1–F3 on integrate `9fa839cba`, and the override with `aa717e110` and `f2b1d38af`, all as listed above
  - `parse_map` gives the same items at `66026a90391c` and at `a57d7c4dcdb2`
  - `review_verdict` at the head returns `VERDICT_NOT_REVIEWER`
  - the clone simulations give `VERDICT_MALFORMED`, `VERDICT_NOT_REVIEWER` and `READY` as described in N2
- tests: the brief's command on `test_w2_174_scope.py` gave 7 passed, and the `-m "not local_only" -k "not real and not green_here and not time_limit"` filter deselected nothing in that file. The F2 cases (`-k test_f2`) ran in the clone for every planted state. I did not rerun `gov accept W2-174`; I used the lead's 222 passed.
- discoveries: N2. The close needs the newest record's block written by a commit with `Role: independent-auditor` alone, and naming all eleven lines.
- risks: N1, a Wave 3 row. N2: if this record or r2 is committed with `Role: orchestrator`, the close at this head refuses with `VERDICT_NOT_REVIEWER`.
- lessons: a narrow-check record becomes the newest record under `docs/probes/<ticket>/`, so its block alone decides READY. It has to name every KPI line, not only the line it checked.
- proposed_decisions: none from me. For the lead: commit this record's verdict block in a commit whose only role is `independent-auditor`, as `c638a82fe` (W2-88b) did, or settle with the CTO how the close reads lead-committed records.
- unresolved: how W2-88 landed past `review_verdict` with records committed as `orchestrator`; I did not check this.
- recommended_next_action: commit this record as described under proposed_decisions, then run the close or merge queue for W2-174. I recommend no new round.

`git status --short` in the worktree: empty (no output). The `$TMPDIR` clone has been removed.
