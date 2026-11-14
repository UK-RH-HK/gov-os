# Brief: engineer, W2-184 (DAEO-6f0s), batch eng-1

You are the engineer for ticket DAEO-6f0s (W2-184), profile FULL: RUBRIC-2 at launch. Build the interface below in the
ticket's allowed paths, with unit tests, until it holds and every existing suite stays green. Use your
test-driven-development skill. The acceptance cases are being written in parallel by an independent test designer;
you do not see them, and you never write under `tests/acceptance/`.

## Where you work
- Your tree: /home/usain/gov-os-worktrees/W2-184, branch w2/W2-184 (head b624fa3c1). Write only these paths:
  `src/gov/launch/launcher.py`, `src/gov/launch/role.py`, `src/gov/launch/record.py`, `src/gov/launch/criticality.py`
  (new), `governance/project/criticality.yaml` (new), `tests/unit/launch/test_w2_184_*.py` (new),
  `docs/changes/W2-184-CIT-E.md` (new), and scratch under `.gov-runtime/scratch/eng/`.
- The ticket: /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-6f0s.md (read-only); its context bundle:
  /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/briefs/ctx-eng.md (JSON: the ticket and its sources).
- The interface is at the end of this brief, word for word (also in `.gov-runtime/scratch/briefs/INTERFACE.md`).
  Points marked **[settled]** are decided; build them as written. If a point cannot be built as written, stop and say
  so in `unresolved:`; do not invent another behaviour.
- `src/gov/launch/command.py` is NOT in the paths (interface 7.2): do not edit it. Write the patch you would make to
  it (the three options `--reason`, `--trial`, `--owner-named`, passed to `launcher.launch`) as a unified diff in
  `.gov-runtime/scratch/eng/command.py.diff`, uncommitted, for the lead's package.
- No kernel file (`template/governance/kernel/**`) changes; the kernel role files' lines are read as they are.

## Context you need
- W2-60a's launcher (`launcher.py` `_check_own_args`, `_worker_plan`, `_launch_line`) and role reader (`role.py`
  `_one_line`, `read_role`, `launch_default`) are the base: extend them; keep W2-60a's refusals and record fields.
- `gov.guard.decide._load_ticket(str(root), id)` returns the ticket's front matter; its `allowed_paths` entries can
  keep an inline `  # comment` tail (strip it, interface 1.2).
- The record folder: `gov.launch.record.folder(root)`; records are `<session id>.json` with `record: gov-launch`.
- Probe records: `docs/probes/<ticket id>/*.md` (front matter per
  `template/governance/kernel/schemas/probe.schema.json`, `judgement` pass|passed|fail|failed); the verdict block's
  form is in `governance/project/briefs/JUDGEMENT.md` (last bullet).
- The kernel role files (`template/governance/kernel/roles/*.md`) carry the real `Launch by criticality` lines
  (engineer, independent-test-designer, qa-engineer with the "on FULL ... otherwise" form). Your parser must accept all
  of them: add a unit case that parses each kernel role file's line.
- `gov launch --plan` stays as it is (DEC-1167 (2)). Lead launches are untouched.
- Fixtures in other suites (tests/acceptance/W2-60a, W2-153, W2-58, W2-50, W2-56, W2-116, tests/unit/launch,
  tests/unit/resources/test_w2_20_*) have no `criticality.yaml`, role files with only `Launch default` (some with
  effort max, e.g. the auditor), no probe records: they must stay green (interface 1.4, 3.2). Do not edit them.

## Order
1. `criticality.py` and `criticality.yaml` with unit tests; 2. the role line parser; 3. the launcher's resolution
(table, floor, max/reason, after --, trial, promotion, probe and same-setting, record keys) with unit tests;
4. `docs/changes/W2-184-CIT-E.md`: a short change record (what changed, the evidence: test counts, the settled points,
the command.py package); 5. run the regression set below; 6. commit after each green step (several commits are fine).

## How to run tests (every pytest goes through heavy_slot.sh)
```
env HOME=/home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-184/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Regression set before your last commit: `tests/unit/launch tests/acceptance/W2-60a tests/acceptance/W2-153
tests/acceptance/W2-58 tests/acceptance/W2-56 tests/acceptance/W2-116 tests/acceptance/W2-50
tests/unit/resources/test_w2_20_unit_launch.py tests/unit/resources/test_w2_20_round3.py`. Run it once on the base
first (before your change) and keep its failures list, so you can show which reds were there before you (name each
with file:line; do not fix other tickets' cases). Use the session's own `$TMPDIR` (`/tmp` is read-only in the sandbox).
No `gov retrieve`, no `gov context`: search with Read and Grep, and search again once in other words if needed.

## Commit (your paths only; trailers in ONE final paragraph)
```
git -C /home/usain/gov-os-worktrees/W2-184 commit -m "<subject: W2-184 (DAEO-6f0s): ...>" --trailer "Task: DAEO-6f0s" --trailer "Role: engineer" --trailer "Implements: DEC-1120, DEC-1119, DEC-1167, DEC-839, DEC-1010" -- <your paths>
```
No merge, no push, no edit outside your paths. Refused twice for the same action by the guard, the sandbox or a hook:
stop and say so; never work around it.

## Return (your last message): the twelve fields, each a labelled line
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: /
proposed_decisions: / unresolved: / recommended_next_action:
In `evidence:` each commit hash and the regression set's summary line before and after. In `tests:` your unit counts.
Name in `discoveries:` anything in the interface you found ambiguous and how you built it.

---
# THE INTERFACE (word for word)

