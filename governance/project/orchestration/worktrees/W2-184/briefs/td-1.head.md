# Brief: independent test designer, W2-184 (DAEO-6f0s), batch td-1

You are the independent test designer for ticket DAEO-6f0s (W2-184), profile FULL: RUBRIC-2 at launch. You write the
acceptance cases from the ticket's KPI lines (S1-S5, F1) and the interface below, before the implementation exists.
Use your test-design skill. Do not read the engineer's work on this ticket (branch w2/W2-184 past b624fa3c1, or the
tree /home/usain/gov-os-worktrees/W2-184 beyond its base files); read the base code freely
(`src/gov/launch/*.py` at b624fa3c1) to build fixtures that reach the launcher.

## Where you write
- Your tree: /home/usain/gov-os-worktrees/W2-184-tests, branch w2/W2-184-tests (based on b624fa3c1). Write only
  `tests/acceptance/W2-184/` there (a README.md, a conftest.py and support module if you need them, the test files).
- The ticket: /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-6f0s.md (read-only). Its context bundle:
  /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/briefs/ctx-td.md (JSON; the ticket text and its sources).
- The interface is at the end of this brief, word for word (also at
  /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/briefs/INTERFACE.md). Test against it; where it says
  **[settled]**, that point is decided: test it as written.

## What to write
1. A case per role and criticality on fixture role files (S1): fixture projects in tmp folders with their own
   `governance/project/criticality.yaml` and role files carrying `Launch default` and `Launch by criticality` lines
   (the "on FULL ... otherwise" form included), each role x C0..C3 (and FULL vs not for the FULL form), asserting the
   launch line's `--model` / `--effort` and the record's `model`, `effort`, `tier`, `criticality`, `model_source`.
   The ticket's `class` must not change the result (plant a misleading `class`). A missing or malformed
   `Launch by criticality` line refuses; a missing or malformed `criticality.yaml` refuses when read (1.4), and the
   absent-file case of 1.4 launches with `criticality: null`. Effort floor: low/medium after `--` on a high table
   refused; max after `--` without `--reason` refused, with it accepted and recorded as `effort_reason`.
2. S2: a planted trial record accepted (records `trial`, `model_source: trial`); a model after `--` with no trial
   refused naming both models; each bad trial (missing, malformed, wrong role, wrong criticality, fewer than two
   tickets, this ticket missing, a non-Opus reviewer, a bad id) refused; `CLAUDE_CODE_SUBAGENT_MODEL` in the settings'
   env and `subagent_model` equal the final model.
3. S3: the record's keys of section 8 present: one launch by criticality, one with a trial, one promoted, each record
   their fields; a plain launch (a role with only `Launch default`, no trial, no promotion) records `trial`,
   `promotion`, `effort_reason`, `owner_named`, `review_round` null.
4. S4: a planted FULL ticket: two `independent-auditor` launches in the same project: the first Opus high
   (`review_round` 1), the second Opus max (`review_round` 2, `effort_source: probe`), no `--reason` needed; the same
   setting twice refused (e.g. the second with `--effort high` after `--`), accepted with `--owner-named DEC-NNN` and
   recorded; a third launch refused without `--owner-named`; a non-FULL ticket's auditor with max after `--` needs
   `--reason`; a malformed `--owner-named` refused.
5. S5: planted probe records under `docs/probes/<ticket id>/`: one set with two failed reviews, one with a fail-open
   finding (a fenced `verdict` block, JUDGEMENT.md's JSON form, `"consequence": "fails open"`), one with neither:
   the first two launch on the `opus` model at the table's effort with `promotion: {reason, record}` and
   `model_source: promotion`; the third does not; a lower model after `--` refused on a promoted ticket; a trial
   refused on a promoted ticket.
6. F1: the three failure lines as named cases (a model below its tier with no trial refused; a promotion recorded and
   applied; an effort below high on a judgement role refused).
7. Every refusal: exit code 1 / LAUNCH_REFUSED, no new launch record left, no session started (the stand-in CLI not
   called), the message naming what the interface says it names.

How to drive launches: W2-60a's cases (`tests/acceptance/W2-60a/w2_60a_support.py`: a sandbox HOME, a stand-in CLI
at `~/.local/bin/claude`, an open resource gate, `gov launch` through the entry point, the record folder) show the
working pattern; you may import or copy from it (copy into your folder if you change it). Cases that need `--reason`,
`--trial` or `--owner-named` call `gov.launch.launcher.launch(..., reason=, trial=, owner_named=)` in a child Python
process with the same environment (interface 7.2: the CLI options are outside this ticket's paths).

Each case must be red on the base (b624fa3c1) for the stated reason (the field missing, the refusal not made, the
model not resolved), not for a fixture error: run your folder on the base and list, per case, why it is red. Cases
that already pass on the base because they check unchanged behaviour (e.g. a plain launch still works) are allowed
only where they guard the interface's compatibility rule (1.4, 3.2); name them as green-on-base in the README.
Mark nothing `local_only` unless it needs a real CLI; none should.

## How to run tests (every pytest)
```
env HOME=/home/usain/gov-os-worktrees/W2-184-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-184-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-184 -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
Use the session's own `$TMPDIR` for scratch (`/tmp` is read-only in the sandbox); make the empty-home folder first
under `.gov-runtime/scratch/` of your tree. No `gov retrieve`, no `gov context`: search with Read and Grep, and search
again once in other words if the first search does not answer.

## Commit (in your tree, your paths only; trailers in ONE final paragraph)
```
git -C /home/usain/gov-os-worktrees/W2-184-tests add tests/acceptance/W2-184
git -C /home/usain/gov-os-worktrees/W2-184-tests commit -m "W2-184 (DAEO-6f0s): acceptance cases for RUBRIC-2 at launch (S1-S5, F1)" --trailer "Task: DAEO-6f0s" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1167, DEC-1120, DEC-1119, DEC-839, DEC-1010" -- tests/acceptance/W2-184
```
No merge, no push, no edit outside `tests/acceptance/W2-184/`. Refused twice for the same action by the guard, the
sandbox or a hook: stop and say so; never work around it.

## Return (your last message): the twelve fields, each a labelled line
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: /
proposed_decisions: / unresolved: / recommended_next_action:
In `tests:` the count of cases and, per KPI line, the case names and why each is red on the base. In `evidence:` the
commit hash and the pytest summary line on the base. Name any point of the interface you found ambiguous in
`discoveries:` (with how you tested it).

---
# THE INTERFACE (word for word)

