---
id: DAEO-p8tv
status: in_progress
deps: [DAEO-61vm, DAEO-k1e2, DAEO-qz4p]
links: [DAEO-52ku, DAEO-2bdu]
created: 2026-11-11T01:20:40Z
type: task
priority: 2
assignee: engineer
external-ref: W2-172
tags: [wave-2, implementation, memory, audit, full, after-the-lift]
wbs_id: W2-172
title: 'The memory audit''s driver and schedule: the cycle through the launch script, the active and stable rule, the digest block, the release check (DEC-1101 (1)-(3), DEC-1125 (2))'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-61vm
- DAEO-k1e2
- DAEO-qz4p
allowed_paths:
- src/gov/memaudit/**
- tests/unit/memaudit/**
- governance/project/orchestration/tools/memaudit_cron.sh
- docs/changes/W2-172-evidence.md
kpis:
  success:
  - 'S1 One command, `python3 -m gov.memaudit run --sets-root <root>`, runs one audit in this order and no other: the writer''s round 1; the pre-flight (W2-170); the checker''s round 1; the writer''s round 2; the checker''s round 2; the drop and void rule; the declaration, the control and the measure (W2-171); the auditor, also with an empty misses file when there is no miss (the launch script writes the audits'' log line only when an auditor delivers, and that line is what the next audit''s "changed since the last audit" list starts from); the pool''s re-run. Each launch is the launch script''s command line with only `--sets-root <root>` named, the brief''s path under `governance/project/indep-briefs/memory-audit/` and its sha256 taken from `git show` at the audit commit (the script checks it against the owner''s approved list itself); the driver never opens a wall, a set or the approved list. The writer''s round 2 and the checker''s second pass run only when the first checker''s notes hold a `revise` or `reject`; a clean first pass goes straight to the measure. Verify: a planted sets root, repository and stub `claude` (W2-149''s): the call ledger shows the steps in that order for a set with revisions, and without the two second-round steps for a clean set; the printed command lines hold no `fixtures/`, `runs/` or `indep-walls/` [DEC-1101 (2)-(3), DEC-1125 (2)]'
  - 'S2 The audit commit is the commit the integration store names as its build (its own commit stamp), so the measure needs no rebuild. The driver refuses, builds nothing and says why in the counts when that commit is more than 24 hours old, is not an ancestor of the main line, or the store is being rebuilt. The audit name is `memory-audit-<yyyymmdd>` (the set and the audit folder). Verify: planted store stamps: fresh and an ancestor (starts), 30 hours old (refuses), a side branch (refuses), a rebuild marker (refuses) [DEC-1101 (1), DEC-1125 (2)]'
  - 'S3 A stop is a stop: any launch exit code other than 0 stops the cycle and the counts name the step and the code; only code 16 (the canary) is retried, once. A stop before `USED` leaves the set unmeasured and the next scheduled audit starts a new set; a stop after `USED` (a measure fault, a brake) is a line to the owner in the digest block and the set is not run again. Verify: planted exit codes 10, 20, 21, 22 (stop, no retry), 16 then 0 (goes on), 16 twice (stop); a planted fault after `USED` (marked for the owner, no second measure) [DEC-1101 (2), DEC-1097 (1)(g)]'
  - 'S4 One audit at a time and not twice in a week: a lock file, and a refusal within 5 days of the last started audit unless `--force` is given (the owner''s word, recorded in the counts). Verify: a planted second start while the lock is held; a planted start 3 days after the last; `--force` allows it and the counts say so [DEC-1125 (2)]'
  - 'S5 The rule that tells active from stable is computed, never chosen: `python3 -m gov.memaudit due --sets-root <root>` prints `weekly` or `monthly`, whether an audit is due now, and the reason. The measure of churn is the share of tracked paths changed in the 28 days before the audit commit, less the walls'' tree-exclude paths. Weekly is the start. **To monthly** when the last three audits each had churn under 5 %, no change to a retrieval path in the 28 days before each, a verdict that met the bar, and no pool regression. **Back to weekly at once** when any one holds before a monthly run: churn of 10 % or more, a change to a retrieval path since the last audit, a verdict below the bar, or a pool regression. Retrieval paths: `src/gov/retrieval/**`, `src/gov/retrieve/**`, `src/gov/store/**`, `src/gov/codeintel/**`, `governance/project/retrieval.yaml`, `governance/project/path-map.yaml`. Weekly is due after 6 days since the last audit, monthly after 28. Verify: planted histories: churn 40 % (weekly); three audits under 5 % with the rest met (monthly); then each of the four triggers alone (weekly again); `due` at 5, 6, 27 and 28 days [DEC-1125 (2), DEC-1101 (1)]'
  - 'S6 The baseline: `python3 -m gov.memaudit baseline --sets-root <root> --commit <sha>` appends one line to the audits'' log (`AUDITS.log`) so that the first audit''s "changed since the last audit" list starts at that commit. It refuses a commit not in the repository, and a second baseline while an audit line exists. Verify: planted log empty (appends), one line (refuses), a commit not in the repository (refuses) [DEC-1101 (1)]'
  - 'S7 The digest block: after each audit (and each stop) the driver writes `runs/indep/memaudit/<audit>/DIGEST.txt` and prints it, counts and ids only, in this order: the audit name and commit; the mode and why; the verdict line (right end to end, wrong claims, the exact interval, the scaled bar); hit@5 and gold in the first bundle beside it; the misses by class (the auditor''s five) and by rank bucket and namespace; the pool''s figures beside the last audit''s and any regression; the retrieval paths changed since the last audit (their names, from git); the questions kept, dropped and why by code; the cost per step in USD; the next audit''s due date. Verify: a planted audit: the block holds each line in that order and passes a schema check; grep for a planted question word, gold path and answer finds none [DEC-1101 (1)-(2), DEC-1125 (2)]'
  - 'S8 A retrieval change waits for the next audit and is never measured by a separate run: `python3 -m gov.memaudit status --sets-root <root> --since <commit>` prints `audited` when a measured audit''s commit is at or after the last change to a retrieval path since `<commit>`, else `not audited, next due <date>`; a release cut reads it (DEC-1097 (4) folded into the audit, DEC-1125 (2)). Verify: planted audits and retrieval commits: before, after, none [DEC-1125 (2), DEC-1097 (4)]'
  - 'S9 The cron wrapper `memaudit_cron.sh` runs `due` and starts the cycle only when an audit is due, with the pinned interpreter; it does nothing and exits 0 when none is due, appends one line per run to the audits'' cron log, and does not start the measure steps while the dispatcher holds a full run or a rebuild (the gate''s own check), waiting at most 60 minutes and then stopping with `gate busy`. It contains no crontab edit (the crontab is class (O), an ACT). Verify: planted `due` outputs and gate states: not due (no start, exit 0), due and idle (starts), due and busy for 61 minutes (stops `gate busy`); `grep -c crontab` of the wrapper is 0 [DEC-1125 (2), DEC-1038]'
  failure:
  - 'A wall, a set, the approved list or a run folder opened by the driver other than through the launch script, W2-170''s or W2-171''s code; a command line naming a folder under the sets root. Verify: S1''s planted run: the call ledger''s printed command lines hold no `fixtures/`, `runs/` or `indep-walls/`, and a file-access spy over the driver''s own process shows no open of those folders'
  - 'A question, gold answer, answer or source path in the digest block, standard output or a log. Verify: S7''s planted audit with a planted question word, gold path and answer: grep of `DIGEST.txt`, standard output and the logs finds none'
  - 'An audit started while another runs, or twice in 5 days without `--force`; a stopped audit''s set measured later. Verify: S4''s planted second start while the lock is held and a start 3 days after the last are refused; S3''s planted stop before `USED` leaves the set unmeasured and the next audit starts a new set'
  - 'The crontab, the path map, the guard, `.claude/` or the walls'' template written. Verify: S9''s `grep -c crontab` of the wrapper is 0, and `git status` in the planted repository after a run shows no change to the path map, the guard, `.claude/` or the walls'' template'
  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'
profile: FULL
sources:
- DEC-1101
- DEC-1125
- DEC-1097
- DEC-1038
- DEC-1050
- DEC-1073
est_loc: 450
acceptance_tests:
  path: tests/acceptance/W2-172/
  author: 'independent-test-designer (MR-3), Sonnet high (RUBRIC-2, class C2), from these KPI lines, before the engineer: planted roots, planted git histories, a stub `claude`, a stub launch script; never the real ~/gov-os-eval, ~/gov-os-runs or the crontab'
track: B
list_rows: []
reads:  # declared by the CTO 11-11 (gov brief READS_MISSING; DEC-1121): what it reads that it does not write
- governance/project/path-map.yaml
- governance/project/retrieval.yaml
- governance/project/orchestration/packages/MEMORY-AUDIT-1.md
- governance/project/indep-briefs/memory-audit/
needs: []
waits_on: []
---
# W2-172 The memory audit's driver and schedule

The cycle of one audit (DEC-1125 (2), DEC-1101 (1)-(3)): the launch script's calls in order, the rule that tells active
from stable, the digest block, and the check a release cut reads. It calls W2-170's checks and W2-171's measure and
holds nothing of its own about a set's content. After W2-170, W2-171 and W2-173.

- **Schedule and install:** weekly, Monday 21:00 on the machine's clock (`packages/MEMORY-AUDIT-1.md` §4). The crontab
  line is class (O) and goes by an ACT, not by this ticket; the wrapper here only starts a due audit. `due` decides
  weekly or monthly, so the line never changes.
- **Alternatives (one line each):** the cron line starts the cycle directly (rejected: a monthly rhythm would need a
  crontab edit each time); the CTO starts each audit by hand (rejected: DEC-1101 (2) asks for no session opened by
  the owner or the CTO).
- **Not here:** the checks (W2-170); the measure (W2-171); `--effort` and the delivery checks (W2-173); the crontab,
  the approved list and the briefs' install (ACTs).

[DEC-1101 (1)-(3); DEC-1125 (2)]
