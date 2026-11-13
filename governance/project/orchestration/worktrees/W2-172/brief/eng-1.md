Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-172/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief eng-1: engineer for DAEO-p8tv (W2-172), profile FULL, class C2

You are the engineer for ticket DAEO-p8tv (W2-172: the memory audit's driver and schedule). You implement the four new
subcommands of `python3 -m gov.memaudit` (`run`, `due`, `baseline`, `status`, plus the `figures` reader of Interface
item 6) and the cron wrapper `governance/project/orchestration/tools/memaudit_cron.sh`, until the independent acceptance
suite `tests/acceptance/W2-172/` passes. The ticket's `## Interface` section (items 1-12, the CTO's answers O1-O4 above
it) is the contract: you conform to it and never change it. A gap or a clash in it comes back as a package (status
PACKAGES: question, options with cost, recommendation, confidence, what it blocks), not as your own invention.

## The CTO's decision PKG-W2-172-TESTS-1 (DEC-1112 (3), 2026-11-12): binding, word for word; it is in the main tree's
## copy of the ticket and not yet in yours, so it is here
- **GATE-1 (a):** the driver splits `--gate-cmd`'s value with `shlex.split` and runs the words as given, so the default
  `gov resources --check` works; the Interface's "called with no arguments" reads "run as its words".
- **TD-1 (b):** the 12-line digest does not record `--force`; item 1's "and the digest" is corrected to the counts only.
- **TD-2 (b):** RN-NAME is judged by `STARTS.log` (an audit started), not by a refusal's `COUNTS.json`, so a refused run
  can be retried the same day.

Two acceptance cases still plant only the audit folder (no `STARTS.log` line) and expect `RN-NAME`
(`test_s4_a_second_start_on_the_same_date_is_refused_rn_name_and_writes_nothing_there` and the `RN-NAME` pairs of
`test_s2_the_first_check_that_fails_refuses`). The test designer is revising them in parallel to plant a `STARTS.log`
line naming `<A>`; implement TD-2 (b), and report those cases as "awaiting the test designer's revision" if they are
the only reds left. Never edit `tests/acceptance/` (it is not yours, and a restore there is the test designer's).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-172 |
| branch | w2/W2-172 |
| your allowed paths | src/gov/memaudit/**, tests/unit/memaudit/**, governance/project/orchestration/tools/memaudit_cron.sh, docs/changes/W2-172-evidence.md |
| the ticket (read it first, whole: KPI lines and the Interface at its end) | /home/usain/gov-os-worktrees/W2-172/.tickets/DAEO-p8tv.md |
| the acceptance suite (read it: README.md maps each KPI line to its cases; conftest.py, w2_172_world.py, launch_stub.py, gate_stub.py, py_shim.py, w2_172_digest.py are how it reaches you) | tests/acceptance/W2-172/ |
| W2-170's and W2-171's code you call as children and never change in behaviour (their subcommands, exit codes, layout, `say`) | src/gov/memaudit/ (`__main__.py`, preflight.py, drops.py, declare.py, measure.py, judge.py, classes.py, pool.py, figures.py, say.py, layout.py, common.py); their Interfaces .tickets/DAEO-61vm.md and .tickets/DAEO-k1e2.md |
| the launch script (called, never changed): argv, exit codes 0/10-22 (16 the canary), the counts object as stdout's last line, the `AUDITS.log` line form | governance/project/orchestration/tools/indep_launch.py (docstring), governance/project/orchestration/indep-schemas/indep-counts.schema.json |
| the gate's own check (O2) | src/gov/resources/command.py (`gov resources --check`: exit 0 open) |
| the store link's build and lock | src/gov/rebuild/integration.py, governance/project/rebuild.yaml |
| the package | governance/project/orchestration/packages/MEMORY-AUDIT-1.md |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1101, DEC-1125, DEC-1097, DEC-1038, DEC-1050, DEC-1073 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## Held-out rules (DEC-820)
Never open the real sets root (`~/gov-os-eval`), the real runs folder (`~/gov-os-runs`), any hidden half or
memory-verdict folder, the real crontab. Never run the real launch script against real sets, a real model call or a
real search. The driver's own process opens no path under `--sets-root` (F1; the suite spies on it with an audit hook).

The ticket's context packet (`gov context DAEO-p8tv --role engineer --budget 20000`, built by your lead) follows; its
`ticket_text` is the same ticket file as above.

----

{
  "ticket": "DAEO-p8tv",
  "ticket_text": "---\nid: DAEO-p8tv\nstatus: in_progress\ndeps: [DAEO-61vm, DAEO-k1e2, DAEO-qz4p]\nlinks: [DAEO-52ku, DAEO-2bdu]\ncreated: 2026-11-11T01:20:40Z\ntype: task\npriority: 2\nassignee: engineer\nexternal-ref: W2-172\ntags: [wave-2, implementation, memory, audit, full, after-the-lift]\nwbs_id: W2-172\ntitle: 'The memory audit''s driver and schedule: the cycle through the launch script, the active and stable rule, the digest block, the release check (DEC-1101 (1)-(3), DEC-1125 (2))'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-61vm\n- DAEO-k1e2\n- DAEO-qz4p\nallowed_paths:\n- src/gov/memaudit/**\n- tests/unit/memaudit/**\n- governance/project/orchestration/tools/memaudit_cron.sh\n- docs/changes/W2-172-evidence.md\n- docs/probes/DAEO-p8tv/**  # the probe record (PKG-W2-172-IFACE-1, the CTO, 2026-11-12)\nkpis:\n  success:\n  - 'S1 One command, `python3 -m gov.memaudit run --sets-root <root>`, runs one audit in this order and no other: the writer''s round 1; the pre-flight (W2-170); the checker''s round 1; the writer''s round 2; the checker''s round 2; the drop and void rule; the declaration, the control and the measure (W2-171); the auditor, also with an empty misses file when there is no miss (the launch script writes the audits'' log line only when an auditor delivers, and that line is what the next audit''s \"changed since the last audit\" list starts from); the pool''s re-run. Each launch is the launch script''s command line with only `--sets-root <root>` named, the brief''s path under `governance/project/indep-briefs/memory-audit/` and its sha256 taken from `git show` at the audit commit (the script checks it against the owner''s approved list itself); the driver never opens a wall, a set or the approved list. The writer''s round 2 and the checker''s second pass run only when the first checker''s notes hold a `revise` or `reject`; a clean first pass goes straight to the measure. Verify: a planted sets root, repository and stub `claude` (W2-149''s): the call ledger shows the steps in that order for a set with revisions, and without the two second-round steps for a clean set; the printed command lines hold no `fixtures/`, `runs/` or `indep-walls/` [DEC-1101 (2)-(3), DEC-1125 (2)]'\n  - 'S2 The audit commit is the commit the integration store names as its build (its own commit stamp), so the measure needs no rebuild. The driver refuses, builds nothing and says why in the counts when that commit is more than 24 hours old, is not an ancestor of the main line, or the store is being rebuilt. The audit name is `memory-audit-<yyyymmdd>` (the set and the audit folder). Verify: planted store stamps: fresh and an ancestor (starts), 30 hours old (refuses), a side branch (refuses), a rebuild marker (refuses) [DEC-1101 (1), DEC-1125 (2)]'\n  - 'S3 A stop is a stop: any launch exit code other than 0 stops the cycle and the counts name the step and the code; only code 16 (the canary) is retried, once. A stop before `USED` leaves the set unmeasured and the next scheduled audit starts a new set; a stop after `USED` (a measure fault, a brake) is a line to the owner in the digest block and the set is not run again. Verify: planted exit codes 10, 20, 21, 22 (stop, no retry), 16 then 0 (goes on), 16 twice (stop); a planted fault after `USED` (marked for the owner, no second measure) [DEC-1101 (2), DEC-1097 (1)(g)]'\n  - 'S4 One audit at a time and not twice in a week: a lock file, and a refusal within 5 days of the last started audit unless `--force` is given (the owner''s word, recorded in the counts). Verify: a planted second start while the lock is held; a planted start 3 days after the last; `--force` allows it and the counts say so [DEC-1125 (2)]'\n  - 'S5 The rule that tells active from stable is computed, never chosen: `python3 -m gov.memaudit due --sets-root <root>` prints `weekly` or `monthly`, whether an audit is due now, and the reason. The measure of churn is the share of tracked paths changed in the 28 days before the audit commit, less the walls'' tree-exclude paths. Weekly is the start. **To monthly** when the last three audits each had churn under 5 %, no change to a retrieval path in the 28 days before each, a verdict that met the bar, and no pool regression. **Back to weekly at once** when any one holds before a monthly run: churn of 10 % or more, a change to a retrieval path since the last audit, a verdict below the bar, or a pool regression. Retrieval paths: `src/gov/retrieval/**`, `src/gov/retrieve/**`, `src/gov/store/**`, `src/gov/codeintel/**`, `governance/project/retrieval.yaml`, `governance/project/path-map.yaml`. Weekly is due after 6 days since the last audit, monthly after 28. Verify: planted histories: churn 40 % (weekly); three audits under 5 % with the rest met (monthly); then each of the four triggers alone (weekly again); `due` at 5, 6, 27 and 28 days [DEC-1125 (2), DEC-1101 (1)]'\n  - 'S6 The baseline: `python3 -m gov.memaudit baseline --sets-root <root> --commit <sha>` appends one line to the audits'' log (`AUDITS.log`) so that the first audit''s \"changed since the last audit\" list starts at that commit. It refuses a commit not in the repository, and a second baseline while an audit line exists. Verify: planted log empty (appends), one line (refuses), a commit not in the repository (refuses) [DEC-1101 (1)]'\n  - 'S7 The digest block: after each audit (and each stop) the driver writes `runs/indep/memaudit/<audit>/DIGEST.txt` and prints it, counts and ids only, in this order: the audit name and commit; the mode and why; the verdict line (right end to end, wrong claims, the exact interval, the scaled bar); hit@5 and gold in the first bundle beside it; the misses by class (the auditor''s five) and by rank bucket and namespace; the pool''s figures beside the last audit''s and any regression; the retrieval paths changed since the last audit (their names, from git); the questions kept, dropped and why by code; the cost per step in USD; the next audit''s due date. Verify: a planted audit: the block holds each line in that order and passes a schema check; grep for a planted question word, gold path and answer finds none [DEC-1101 (1)-(2), DEC-1125 (2)]'\n  - 'S8 A retrieval change waits for the next audit and is never measured by a separate run: `python3 -m gov.memaudit status --sets-root <root> --since <commit>` prints `audited` when a measured audit''s commit is at or after the last change to a retrieval path since `<commit>`, else `not audited, next due <date>`; a release cut reads it (DEC-1097 (4) folded into the audit, DEC-1125 (2)). Verify: planted audits and retrieval commits: before, after, none [DEC-1125 (2), DEC-1097 (4)]'\n  - 'S9 The cron wrapper `memaudit_cron.sh` runs `due` and starts the cycle only when an audit is due, with the pinned interpreter; it does nothing and exits 0 when none is due, appends one line per run to the audits'' cron log, and does not start the measure steps while the dispatcher holds a full run or a rebuild (the gate''s own check), waiting at most 60 minutes and then stopping with `gate busy`. It contains no crontab edit (the crontab is class (O), an ACT). Verify: planted `due` outputs and gate states: not due (no start, exit 0), due and idle (starts), due and busy for 61 minutes (stops `gate busy`); `grep -c crontab` of the wrapper is 0 [DEC-1125 (2), DEC-1038]'\n  failure:\n  - 'A wall, a set, the approved list or a run folder opened by the driver other than through the launch script, W2-170''s or W2-171''s code; a command line naming a folder under the sets root. Verify: S1''s planted run: the call ledger''s printed command lines hold no `fixtures/`, `runs/` or `indep-walls/`, and a file-access spy over the driver''s own process shows no open of those folders'\n  - 'A question, gold answer, answer or source path in the digest block, standard output or a log. Verify: S7''s planted audit with a planted question word, gold path and answer: grep of `DIGEST.txt`, standard output and the logs finds none'\n  - 'An audit started while another runs, or twice in 5 days without `--force`; a stopped audit''s set measured later. Verify: S4''s planted second start while the lock is held and a start 3 days after the last are refused; S3''s planted stop before `USED` leaves the set unmeasured and the next audit starts a new set'\n  - 'The crontab, the path map, the guard, `.claude/` or the walls'' template written. Verify: S9''s `grep -c crontab` of the wrapper is 0, and `git status` in the planted repository after a run shows no change to the path map, the guard, `.claude/` or the walls'' template'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'\nprofile: FULL\nsources:\n- DEC-1101\n- DEC-1125\n- DEC-1097\n- DEC-1038\n- DEC-1050\n- DEC-1073\nest_loc: 450\nacceptance_tests:\n  path: tests/acceptance/W2-172/\n  author: 'independent-test-designer (MR-3), Sonnet high (RUBRIC-2, class C2), from these KPI lines, before the engineer: planted roots, planted git histories, a stub `claude`, a stub launch script; never the real ~/gov-os-eval, ~/gov-os-runs or the crontab'\ntrack: B\nlist_rows: []\nreads:  # declared by the CTO 11-11 (gov brief READS_MISSING; DEC-1121): what it reads that it does not write\n- governance/project/path-map.yaml\n- governance/project/retrieval.yaml\n- governance/project/orchestration/packages/MEMORY-AUDIT-1.md\n- governance/project/indep-briefs/memory-audit/\nneeds: []\nwaits_on: []\n---\n# W2-172 The memory audit's driver and schedule\n\nThe cycle of one audit (DEC-1125 (2), DEC-1101 (1)-(3)): the launch script's calls in order, the rule that tells active\nfrom stable, the digest block, and the check a release cut reads. It calls W2-170's checks and W2-171's measure and\nholds nothing of its own about a set's content. After W2-170, W2-171 and W2-173.\n\n- **Schedule and install:** weekly, Monday 21:00 on the machine's clock (`packages/MEMORY-AUDIT-1.md` \u00a74). The crontab\n  line is class (O) and goes by an ACT, not by this ticket; the wrapper here only starts a due audit. `due` decides\n  weekly or monthly, so the line never changes.\n- **Alternatives (one line each):** the cron line starts the cycle directly (rejected: a monthly rhythm would need a\n  crontab edit each time); the CTO starts each audit by hand (rejected: DEC-1101 (2) asks for no session opened by\n  the owner or the CTO).\n- **Not here:** the checks (W2-170); the measure (W2-171); `--effort` and the delivery checks (W2-173); the crontab,\n  the approved list and the briefs' install (ACTs).\n\n[DEC-1101 (1)-(3); DEC-1125 (2)]\n\n## Interface (DEC-1052; PKG-W2-172-IFACE-1 (a), the CTO's delegated decision, DEC-1112 (3), 2026-11-12)\n\nThe lead's block, word for word, with the open points answered: **O1** the 24-hour age is the commit's committer time (as the KPI reads); **O2** the gate command is the product's own `gov resources --check` (not the CTO's scratch `gate_check.py`, which an adopted repository does not have); **O3** `run` refuses `RN-NOBASE` while `AUDITS.log` has no line; **O4** the pinned interpreter is `GOV_MEMAUDIT_PYTHON`, else `/usr/bin/python3`.\n\nStated by the CTO before the pair starts (DEC-1052; PKG-W2-172-IFACE-1, option (a)). The test designer writes tests to this block and the engineer conforms to it; neither changes it. A gap or a clash goes back to the CTO as a package. W2-170's Interface (DAEO-61vm) and W2-171's (DAEO-k1e2) hold and are called, never copied or changed: their subcommands, exit codes, layout and `say`. The launch script (`governance/project/orchestration/tools/indep_launch.py`, W2-149, W2-173, W2-178) is called and never changed. The three approved briefs are not changed (DEC-1129 (2)). Bracketed lines name the KPI lines each item serves.\n\n### 1 The command line [S1, S4-S8, F1]\nFour subcommands join `python3 -m gov.memaudit`: `run`, `due`, `baseline` and `status` (`--help`: exit 0). They print through `say` only (W2-170 \u00a71). Flags:\n\n| flag | used by | meaning and default |\n|---|---|---|\n| `--sets-root <root>` | all, required | as W2-170 \u00a71. The only flag that names the sets root; the driver never builds, opens, lists or stats a path under it (F1) |\n| `--repo <dir>` | all | the repository (the launch script's cwd). Default: the top level of the working directory |\n| `--store-link <path>` | `run`, `due` | the integration store's link. Default: `integration_store` of `governance/project/rebuild.yaml`, read with `git show <main line>:governance/project/rebuild.yaml` in `--repo` |\n| `--launch <file>` | `run` | the launch script. Default: `<repo>/governance/project/orchestration/tools/indep_launch.py`. The test seam for the stub launch script (W2-149's stub `claude` runs under the real script) |\n| `--gov <exe>`, `--claude <exe>` | `run` | passed on unchanged to W2-171's `measure`, `judge` and `pool` (W2-171 \u00a76) |\n| `--gate-cmd <exe>` | `run` | \u00a78; default none (no gate) when run by hand |\n| `--force` | `run` | the owner's word: lifts the 5-day refusal only (S4); recorded in the counts and the digest |\n| `--commit <rev>` | `baseline`, required | resolved with `git rev-parse --verify <rev>^{commit}` in `--repo` |\n| `--since <rev>` | `status`, required | as `--commit` |\n\n- **The runs folder is never a flag.** It is `$GOV_INDEP_RUNS_DIR`, else `~/gov-os-runs` (the launch script's own rule and W2-170 `preflight`'s default), and it is passed to every child in the environment. Every printed command line then holds no `runs/` (`gov-os-runs/` would match the KPI's grep).\n- **Clock seam:** `GOV_MEMAUDIT_NOW` (ISO 8601 UTC), when set, is \"now\" for every age and date (S2, S4, S5, S8, S9's wait). Nothing else reads the clock.\n\n### 2 The cycle [S1, S3, F1]\n`run` runs the steps below, in this order and no other, each as a child process with cwd `--repo`. Its environment is the driver's own plus `GOV_INDEP_RUNS_DIR`. Its standard error goes to `<R>/<A>/<step>.err` (\u00a74), never printed, and its standard output is kept in `<R>/<A>/<step>.out`. `<py>` is `sys.executable`; `<A>` is the audit's name (\u00a73); `<C>` is the audit commit (\u00a73).\n\n| # | step | command line |\n|---|---|---|\n| 1 | `writer-1` | `<py> <launch> --sets-root <root> --kind writer --brief governance/project/indep-briefs/memory-audit/writer.md --brief-sha256 <h> --commit <C> --set <A> --round 1` |\n| 2 | `preflight` | `<py> -m gov.memaudit preflight --sets-root <root> --audit <A> --repo <repo> --commit <C>` |\n| 3 | `checker-1` | launch, `--kind checker`, `checker.md`, `--round 1` |\n| 4 | `writer-2` | launch, `--kind writer`, `--round 2`: only when \u00a72a says so |\n| 5 | `checker-2` | launch, `--kind checker`, `--round 2`: only when \u00a72a says so |\n| 6 | `void` | `<py> -m gov.memaudit void --sets-root <root> --audit <A>` |\n| 7 | `measure` | `<py> -m gov.memaudit measure --sets-root <root> --audit <A> --repo <repo> --commit <C> --store <link>/.gov-runtime/store.db [--gov <exe>]` (W2-171's declaration, use-once marker, control and attempts) |\n| 8 | `judge` | `<py> -m gov.memaudit judge --sets-root <root> --audit <A> --repo <repo> [--gov] [--claude]` (writes `misses.jsonl`, empty when there is no miss) |\n| 9 | `auditor` | launch, `--kind auditor`, `auditor.md`, `--set <A> --audit <A>`: always, also with an empty misses file. The launch script appends the `AUDITS.log` line on delivery |\n| 10 | `classes` | `<py> -m gov.memaudit classes --sets-root <root> --audit <A>` |\n| 11 | `pool` | `<py> -m gov.memaudit pool --sets-root <root> --audit <A> --repo <repo> [--gov]` |\n| 12 | `figures` | `<py> -m gov.memaudit figures --sets-root <root> --audit <A>` (\u00a76; reads, writes nothing) |\n\n- `<h>` is the sha256 of the bytes `git show <C>:<brief path>` returns. The driver never opens `indep-walls/APPROVED`; the launch script checks it.\n- **2a, the second round.** The launch script's standard output ends with its counts object (`indep-counts.schema.json`). The driver parses only that last line, keeps it as `<R>/<A>/<step>.counts.json`, and runs steps 4 and 5 exactly when `checker-1`'s `out.revise + out.rejected > 0`. A clean first pass goes from step 3 to step 6.\n- Printed per step, before it starts, is one line: `STEP <name> <the command line>`. That is the KPI's \"printed command lines\" and the call ledger the tests read. It holds no `fixtures/`, `runs/` or `indep-walls/`.\n\n### 3 The audit commit and the refusals before anything starts [S2, S4, F3]\n- **The audit commit** `<C>` is `git -C <store-link> rev-parse HEAD`: the ready half's head, which is its build (`rebuild/integration.py`: the link points at the half built at that head). The measure's `--store` is that half's `store.db`, so nothing is rebuilt.\n- **The audit's name** `<A>` is `memory-audit-<yyyymmdd>`: the UTC date of now. It names both the set and the audit folder.\n- **The checks, in order.** The first one that fails refuses: it prints `REFUSED <code>`, writes `<R>/<A>/COUNTS.json` with `refused: <code>` where `<R>/<A>/` does not yet exist (otherwise it writes nothing there), starts no child and exits 1. A refusal is not a started audit.\n\n| code | refuses when |\n|---|---|\n| `RN-LOCK` | `<R>/LOCK` is held (an exclusive `flock`, non-blocking, held by `run` until it exits) |\n| `RN-NOBASE` | `<runs>/indep/AUDITS.log` is missing or holds no line (O3) |\n| `RN-RECENT` | the last line of `<R>/STARTS.log` is under 5 \u00d7 24 h before now and `--force` is not given |\n| `RN-REBUILD` | `<store-link>.lock` is held (a non-blocking `flock` try on it fails; when the try succeeds the lock is released at once) |\n| `RN-SIDE` | `<C>` is not an ancestor of `refs/heads/w2/integrate`, else of `refs/heads/main` (the launch script's main-line rule) |\n| `RN-STALE` | `<C>`'s committer time is more than 24 h before now (O1) |\n| `RN-NAME` | `<R>/<A>/` already exists: a second start on the same date, so a set is never run twice |\n\n- After the checks pass, `run` appends `{\"audit\",\"commit\",\"at\",\"force\"}` to `<R>/STARTS.log` before step 1. S4's \"last started audit\" is that file's last line.\n\n### 4 The driver's own folder `<R>` = `<runs>/indep/memaudit/` [S3, S4, S5, S7, S8, F2]\n```\nLOCK                 the one-at-a-time lock (flock)\nSTARTS.log           one JSON line per started audit\nHISTORY.jsonl        one JSON line per audit that reached step 12 or stopped after USED (\u00a75); the due rule and status read it\ncron.log             the wrapper's one line per run (\u00a78)\n<A>/COUNTS.json      the run's counts: audit, commit, force, mode, steps [{step, exit, retried}], stop {step, exit, used} | null, refused, cost {<step>: usd}\n<A>/DIGEST.txt       \u00a77\n<A>/<step>.out .err .counts.json\n```\n- Everything here holds counts, codes, ids, hashes and repository paths only (F2).\n- `HISTORY.jsonl` line: `{\"audit\",\"commit\",\"at\",\"mode\",\"churn\",\"retrieval_28d\",\"passes\",\"pool_regression\",\"measured\",\"used\"}`. `churn` is a fraction to 4 places; `retrieval_28d` and `pool_regression` are booleans; `passes` is a boolean, or null when not measured; `measured` is true only when step 12 ran.\n\n### 5 Stops [S3, F3]\n- **Any child exit other than 0 stops the cycle.** The one exception is a launch step that exits **16** (the canary): it runs once more with the same command line, and a second 16 stops. A stop prints `STOPPED <step> <exit>`, writes `COUNTS.json` and the digest, appends nothing to `HISTORY.jsonl` before USED, and exits 2. `void`'s exit 2 (a void audit) is a stop like any other.\n- **The USED boundary, known without opening the run folder.** Steps 1 to 6 are before USED. Step 7 is before USED when `measure` exits 1 or 4 (W2-170's `DC-` refusals come before `declare` writes `USED`) and after it when `measure` exits 0, 2 or 3 (W2-171 \u00a72). Steps 8 to 12 are after USED.\n- **A stop before USED:** the set stays unmeasured, and the next audit has a new date and so a new set (`RN-NAME`).\n- **A stop after USED:** the digest gains the owner line (\u00a77). `HISTORY.jsonl` gains the line with `measured: false, used: true`. Nothing in the driver runs that audit's steps again: no resume and no second `measure`.\n\n### 6 The figures, read by W2-170's and W2-171's files only through a child [S7, F1, F2]\n- `python3 -m gov.memaudit figures --sets-root <root> --audit <A>` (this ticket's) prints one JSON line built from `runs/<A>/FIGURES.json` (W2-171 \u00a710: `verdict`, `beside.hit5`, `beside.in_bundle`, `n_gold`, `bar`, `misses.by_rank`, `misses.by_namespace`, `classes`, `pool`, `spend.usd`) and from `DROPS.json` (W2-170: kept, dropped, counts by code).\n- That line holds numbers and fixed words only. A missing file gives `null` for its keys, and the command exits 0.\n- The driver's own process opens no path under the sets root. Every figure it uses comes from a child's standard output: the launch counts line, the `figures` line, and judge's `BESIDE ... spent <usd> USD` for the judge's cost.\n\n### 7 The digest block [S7, S3, F2]\nWritten whole by rename to `<R>/<A>/DIGEST.txt`, then printed line by line, after every audit, every stop and every `RN-` refusal that has an `<A>`. There are exactly these 12 lines in this order. A figure not reached prints its word followed by `not reached`.\n```\nAUDIT <A> commit <12 hex>\nMODE weekly|monthly reason <code>\nVERDICT right <r> of <n>; wrong <w>; exact <lo> to <hi> %; bar <need> right, <max> wrong: passes|misses\nHIT5 <a> of <ng>; first bundle <b>\nMISSES class gold_wrong <n> question_ambiguous <n> out_of_scope <n> retrieval_miss <n> answer_wrong <n>; rank 1-5 <n> 6-20 <n> none <n>; namespace embedded <n> keyword_only <n>\nPOOL hit5 <a> of <n> last <a'|none>; full <c> last <c'|none>; regression yes|no\nRETRIEVAL changed <k>[: <path> <path> ...]      the six globs (\u00a79) against git diff --name-only <last audit commit> <C>\nQUESTIONS kept <k> dropped <d>[; <CODE> <n> ...]\nCOST <step> <usd:.2f> ... total <usd:.2f>\nNEXT due <yyyy-mm-dd> <mode>\nSTOP none | STOP <step> exit <code> | REFUSED <code>\nOWNER none | OWNER stopped after USED at <step> exit <code>: the set is not run again\n```\n- The schema is one regular expression per line, in this order; the test writes its own from this block.\n- The retrieval paths are repository paths of the six globs, not a question's gold source (F2). S7's planted gold path is not one of them.\n\n### 8 The cron wrapper `memaudit_cron.sh` [S9, F4]\n- **Set-up:** bash. `PY=\"${GOV_MEMAUDIT_PYTHON:-/usr/bin/python3}\"` (O4); `ROOT=\"${GOV_MEMAUDIT_SETS_ROOT:-$HOME/gov-os-eval}\"`; cwd is the repository.\n- **Not due:** it runs `$PY -m gov.memaudit due --sets-root \"$ROOT\"`; exit 1 (not due) appends the log line and exits 0.\n- **Due:** it runs `run --sets-root \"$ROOT\" --gate-cmd \"${GOV_MEMAUDIT_GATE:-<the gate's check, O2>}\"` and exits with run's code.\n- **The gate:** before each of steps 7, 8 and 11 (the steps that search the store), `run` calls `--gate-cmd` with no arguments: exit 0 is open, anything else is busy. It polls every `GOV_MEMAUDIT_GATE_POLL_S` seconds (default 60) for at most `GOV_MEMAUDIT_GATE_MAX_S` (default 3600, measured by the clock seam). When the wait runs out it stops with `STOPPED <step> gate busy`, which is a \u00a75 stop at that step, and run exits 2.\n- **The log line:** one JSON line per run appended to `<R>/cron.log`: `{\"at\",\"due\",\"mode\",\"reason\",\"started\",\"exit\"}`.\n- **What it never holds:** the word `crontab` (`grep -c crontab` is 0). It writes nothing but `cron.log` and what `run` writes.\n\n### 9 `due`, the active and stable rule [S5]\n- **Retrieval globs:** `src/gov/retrieval/**`, `src/gov/retrieve/**`, `src/gov/store/**`, `src/gov/codeintel/**`, `governance/project/retrieval.yaml`, `governance/project/path-map.yaml`.\n- **Churn at a commit X:** the paths tracked at X (`git ls-tree -r --name-only X`), less those matched by `governance/project/indep-walls/tree-exclude.txt` at X (fnmatch, as the launch script matches it), is the denominator. The numerator is those of them that appear in `git log --name-only --format= --since=<X's committer time \u2212 28 d> --until=<X's committer time> X`. The result is a fraction to 4 places.\n- **`retrieval_28d` at X:** some path in that same log matches the retrieval globs.\n- **Mode.** Weekly while `HISTORY.jsonl` has fewer than 3 measured lines. Monthly when the last 3 measured lines each have `churn < 0.05`, `retrieval_28d` false, `passes` true and `pool_regression` false, and no back-to-weekly trigger holds. The triggers are computed now at the store link's head H: `churn(H) >= 0.10`; a retrieval-glob path in `git diff --name-only <last audit commit> H`; the last measured line's `passes` false; its `pool_regression` true.\n- **Due.** Weekly mode is due when 6 days or more have passed since the last line of `STARTS.log` (5 days: not due). Monthly mode is due at 28 days or more (27: not due). No `STARTS.log` line means due.\n- **Output and exit codes:** three lines, `MODE weekly|monthly`, `DUE yes|no next <yyyy-mm-dd>` and `REASON <code>`. Reason codes: `start`, `stable`, `churn`, `retrieval`, `verdict`, `pool`, `active`. Exit 0 when due, 1 when not due, 4 on usage.\n- `run` records the mode and reason of its own `due` computation in `COUNTS.json`, `HISTORY.jsonl` and the digest.\n\n### 10 `baseline` [S6]\n- It appends `{\"time\",\"commit\",\"run\":\"baseline\",\"audit\":\"baseline\"}` to `<runs>/indep/AUDITS.log`. That is the launch script's line form; its `last_audit` reads the last line's `commit`, and W2-170's selection lists do the same. It prints `BASELINE <12 hex>` and exits 0.\n- **Refusals (exit 1, nothing written):** `BL-COMMIT` when the commit does not resolve in `--repo`; `BL-EXISTS` when `AUDITS.log` holds any line.\n\n### 11 `status` [S8]\n- **The last retrieval change** is L = `git log -1 --format=%H <since>..<main line> -- <the six globs>` in `--repo`.\n- **No L:** it prints `audited` and exits 0.\n- **Audited:** some `HISTORY.jsonl` line with `measured: true` has a commit A with `git merge-base --is-ancestor L A`. It prints `audited` and exits 0.\n- **Otherwise:** it prints `not audited, next due <yyyy-mm-dd>` (\u00a79's date) and exits 1.\n\n### 12 Exit codes of `run`\n| exit | when |\n|---|---|\n| 0 | the audit ran to step 12 |\n| 1 | refused (\u00a73) |\n| 2 | stopped (\u00a75, \u00a78) |\n| 4 | usage, as W2-170 |\n\nNothing `run` writes lies outside `<R>`. The children write what their own Interfaces say. The driver writes nothing to the path map, the guard, `.claude/`, the walls' template or the crontab (F4).\n",
  "authority": [
    {
      "id": "DEC-1101",
      "sha256": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "reason": "declared in sources",
      "tokens": 876
    },
    {
      "id": "DEC-1125",
      "sha256": "4c6b238b79eb0ea478c32c2d17a386fc201b007b389ab87f4319bcf546ae3349",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4c6b238b79eb0ea478c32c2d17a386fc201b007b389ab87f4319bcf546ae3349",
      "reason": "declared in sources",
      "tokens": 945
    },
    {
      "id": "DEC-1097",
      "sha256": "30a2c6e0bb30d0534d5127aa2cf3a39460cebb7fb5fda84d34632479a8831955",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "30a2c6e0bb30d0534d5127aa2cf3a39460cebb7fb5fda84d34632479a8831955",
      "reason": "declared in sources",
      "tokens": 1506
    },
    {
      "id": "DEC-1038",
      "sha256": "ac51e5af436b7a1b2324b48fca09241508e9d6af6a05ed4ff8cb930a1bd53453",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ac51e5af436b7a1b2324b48fca09241508e9d6af6a05ed4ff8cb930a1bd53453",
      "reason": "declared in sources",
      "tokens": 920
    },
    {
      "id": "DEC-1050",
      "sha256": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "reason": "declared in sources",
      "tokens": 936
    },
    {
      "id": "DEC-1073",
      "sha256": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "reason": "declared in sources",
      "tokens": 1047
    },
    {
      "id": "DAEO-61vm",
      "sha256": "838076d20592cc01b7d21caf6ce5cbef0e9ee2a2c44dd05df03042e8acbe7b6c",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "838076d20592cc01b7d21caf6ce5cbef0e9ee2a2c44dd05df03042e8acbe7b6c",
      "reason": "declared in sources",
      "tokens": 1467
    },
    {
      "id": "DAEO-k1e2",
      "sha256": "85b0e20e6d1e5410459798110c058500bf447d7bb068e6fefe2b0d376f0e6877",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "85b0e20e6d1e5410459798110c058500bf447d7bb068e6fefe2b0d376f0e6877",
      "reason": "declared in sources",
      "tokens": 1644
    },
    {
      "id": "DAEO-qz4p",
      "sha256": "20b6817806e4939fe383b416c423c74c0613fd78c6536136d2a127157cac9101",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "20b6817806e4939fe383b416c423c74c0613fd78c6536136d2a127157cac9101",
      "reason": "declared in sources",
      "tokens": 1063
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1101",
      "sha256": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "551b823d94cb80e629f27431a58e2f6aa6c347de6844b79c3f99c947ca7993a1",
      "reason": "declared in sources",
      "tokens": 876
    },
    {
      "id": "DEC-1125",
      "sha256": "4c6b238b79eb0ea478c32c2d17a386fc201b007b389ab87f4319bcf546ae3349",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4c6b238b79eb0ea478c32c2d17a386fc201b007b389ab87f4319bcf546ae3349",
      "reason": "declared in sources",
      "tokens": 945
    },
    {
      "id": "DEC-1097",
      "sha256": "30a2c6e0bb30d0534d5127aa2cf3a39460cebb7fb5fda84d34632479a8831955",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "30a2c6e0bb30d0534d5127aa2cf3a39460cebb7fb5fda84d34632479a8831955",
      "reason": "declared in sources",
      "tokens": 1506
    },
    {
      "id": "DEC-1038",
      "sha256": "ac51e5af436b7a1b2324b48fca09241508e9d6af6a05ed4ff8cb930a1bd53453",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "ac51e5af436b7a1b2324b48fca09241508e9d6af6a05ed4ff8cb930a1bd53453",
      "reason": "declared in sources",
      "tokens": 920
    },
    {
      "id": "DEC-1050",
      "sha256": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "5aa4028efb141b7a31de8938bdf16151d33934312265d1f2bdf217b3735b2a28",
      "reason": "declared in sources",
      "tokens": 936
    },
    {
      "id": "DEC-1073",
      "sha256": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "reason": "declared in sources",
      "tokens": 1047
    },
    {
      "id": "DAEO-61vm",
      "sha256": "838076d20592cc01b7d21caf6ce5cbef0e9ee2a2c44dd05df03042e8acbe7b6c",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "838076d20592cc01b7d21caf6ce5cbef0e9ee2a2c44dd05df03042e8acbe7b6c",
      "reason": "declared in sources",
      "tokens": 1467
    },
    {
      "id": "DAEO-k1e2",
      "sha256": "85b0e20e6d1e5410459798110c058500bf447d7bb068e6fefe2b0d376f0e6877",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "85b0e20e6d1e5410459798110c058500bf447d7bb068e6fefe2b0d376f0e6877",
      "reason": "declared in sources",
      "tokens": 1644
    },
    {
      "id": "DAEO-qz4p",
      "sha256": "20b6817806e4939fe383b416c423c74c0613fd78c6536136d2a127157cac9101",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "20b6817806e4939fe383b416c423c74c0613fd78c6536136d2a127157cac9101",
      "reason": "declared in sources",
      "tokens": 1063
    }
  ],
  "supplementary": [],
  "supplementary_query": "The memory audit's driver and schedule: the cycle through the launch script, the active and stable rule, the digest block, the release check (DEC-1101 (1)-(3), DEC-1125 (2))\nS1 One command, `python3 -m gov.memaudit run --sets-root <root>`, runs one audit in this order and no other: the writer's round 1; the pre-flight (W2-170); the checker's round 1; the writer's round 2; the checker's round 2; the drop and void rule; the declaration, the control and the measure (W2-171); the auditor, also with an empty misses file when there is no miss (the launch script writes the audits' log line only when an auditor delivers, and that line is what the next audit's \"changed since the last audit\" list starts from); the pool's re-run. Each launch is the launch script's command line with only `--sets-root <root>` named, the brief's path under `governance/project/indep-briefs/memory-audit/` and its sha256 taken from `git show` at the audit commit (the script checks it against the owner's approved list itself); the driver never opens a wall, a set or the approved list. The writer's round 2 and the checker's second pass run only when the first checker's notes hold a `revise` or `reject`; a clean first pass goes straight to the measure. Verify: a planted sets root, repository and stub `claude` (W2-149's): the call ledger shows the steps in that order for a set with revisions, and without the two second-round steps for a clean set; the printed command lines hold no `fixtures/`, `runs/` or `indep-walls/` [DEC-1101 (2)-(3), DEC-1125 (2)]\nS2 The audit commit is the commit the integration store names as its build (its own commit stamp), so the measure needs no rebuild. The driver refuses, builds nothing and says why in the counts when that commit is more than 24 hours old, is not an ancestor of the main line, or the store is being rebuilt. The audit name is `memory-audit-<yyyymmdd>` (the set and the audit folder). Verify: planted store stamps: fresh and an ancestor (starts), 30 hours old (refuses), a side branch (refuses), a rebuild marker (refuses) [DEC-1101 (1), DEC-1125 (2)]\nS3 A stop is a stop: any launch exit code other than 0 stops the cycle and the counts name the step and the code; only code 16 (the canary) is retried, once. A stop before `USED` leaves the set unmeasured and the next scheduled audit starts a new set; a stop after `USED` (a measure fault, a brake) is a line to the owner in the digest block and the set is not run again. Verify: planted exit codes 10, 20, 21, 22 (stop, no retry), 16 then 0 (goes on), 16 twice (stop); a planted fault after `USED` (marked for the owner, no second measure) [DEC-1101 (2), DEC-1097 (1)(g)]\nS4 One audit at a time and not twice in a week: a lock file, and a refusal within 5 days of the last started audit unless `--force` is given (the owner's word, recorded in the counts). Verify: a planted second start while the lock is held; a planted start 3 days after the last; `--force` allows it and the counts say so [DEC-1125 (2)]\nS5 The rule that tells active from stable is computed, never chosen: `python3 -m gov.memaudit due --sets-root <root>` prints `weekly` or `monthly`, whether an audit is due now, and the reason. The measure of churn is the share of tracked paths changed in the 28 days before the audit commit, less the walls' tree-exclude paths. Weekly is the start. **To monthly** when the last three audits each had churn under 5 %, no change to a retrieval path in the 28 days before each, a verdict that met the bar, and no pool regression. **Back to weekly at once** when any one holds before a monthly run: churn of 10 % or more, a change to a retrieval path since the last audit, a verdict below the bar, or a pool regression. Retrieval paths: `src/gov/retrieval/**`, `src/gov/retrieve/**`, `src/gov/store/**`, `src/gov/codeintel/**`, `governance/project/retrieval.yaml`, `governance/project/path-map.yaml`. Weekly is due after 6 days since the last audit, monthly after 28. Verify: planted histories: churn 40 % (weekly); three audits under 5 % with the rest met (monthly); then each of the four triggers alone (weekly again); `due` at 5, 6, 27 and 28 days [DEC-1125 (2), DEC-1101 (1)]\nS6 The baseline: `python3 -m gov.memaudit baseline --sets-root <root> --commit <sha>` appends one line to the audits' log (`AUDITS.log`) so that the first audit's \"changed since the last audit\" list starts at that commit. It refuses a commit not in the repository, and a second baseline while an audit line exists. Verify: planted log empty (appends), one line (refuses), a commit not in the repository (refuses) [DEC-1101 (1)]\nS7 The digest block: after each audit (and each stop) the driver writes `runs/indep/memaudit/<audit>/DIGEST.txt` and prints it, counts and ids only, in this order: the audit name and commit; the mode and why; the verdict line (right end to end, wrong claims, the exact interval, the scaled bar); hit@5 and gold in the first bundle beside it; the misses by class (the auditor's five) and by rank bucket and namespace; the pool's figures beside the last audit's and any regression; the retrieval paths changed since the last audit (their names, from git); the questions kept, dropped and why by code; the cost per step in USD; the next audit's due date. Verify: a planted audit: the block holds each line in that order and passes a schema check; grep for a planted question word, gold path and answer finds none [DEC-1101 (1)-(2), DEC-1125 (2)]\nS8 A retrieval change waits for the next audit and is never measured by a separate run: `python3 -m gov.memaudit status --sets-root <root> --since <commit>` prints `audited` when a measured audit's commit is at or after the last change to a retrieval path since `<commit>`, else `not audited, next due <date>`; a release cut reads it (DEC-1097 (4) folded into the audit, DEC-1125 (2)). Verify: planted audits and retrieval commits: before, after, none [DEC-1125 (2), DEC-1097 (4)]\nS9 The cron wrapper `memaudit_cron.sh` runs `due` and starts the cycle only when an audit is due, with the pinned interpreter; it does nothing and exits 0 when none is due, appends one line per run to the audits' cron log, and does not start the measure steps while the dispatcher holds a full run or a rebuild (the gate's own check), waiting at most 60 minutes and then stopping with `gate busy`. It contains no crontab edit (the crontab is class (O), an ACT). Verify: planted `due` outputs and gate states: not due (no start, exit 0), due and idle (starts), due and busy for 61 minutes (stops `gate busy`); `grep -c crontab` of the wrapper is 0 [DEC-1125 (2), DEC-1038]\nA wall, a set, the approved list or a run folder opened by the driver other than through the launch script, W2-170's or W2-171's code; a command line naming a folder under the sets root. Verify: S1's planted run: the call ledger's printed command lines hold no `fixtures/`, `runs/` or `indep-walls/`, and a file-access spy over the driver's own process shows no open of those folders\nA question, gold answer, answer or source path in the digest block, standard output or a log. Verify: S7's planted audit with a planted question word, gold path and answer: grep of `DIGEST.txt`, standard output and the logs finds none\nAn audit started while another runs, or twice in 5 days without `--force`; a stopped audit's set measured later. Verify: S4's planted second start while the lock is held and a start 3 days after the last are refused; S3's planted stop before `USED` leaves the set unmeasured and the next audit starts a new set\nThe crontab, the path map, the guard, `.claude/` or the walls' template written. Verify: S9's `grep -c crontab` of the wrapper is 0, and `git status` in the planted repository after a run shows no change to the path map, the guard, `.claude/` or the walls' template\nAny change outside the paths above. Verify: `git diff --name-only` of the ticket's branch against its base lists only paths matched by the ticket's allowed_paths",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 16976,
  "budget": {
    "limit": 20000,
    "used": 16976
  },
  "hash": "6b613d9932bc0b2f5263c0c4641399e349451bc965ac071f1de9f56863418400"
}

----

## Rules
- Work test first against the suite: read README.md and the helpers, then implement. Keep the driver small and plain
  (estimate about 450 lines plus the wrapper); one new module for the driver (e.g. `src/gov/memaudit/driver.py`) and a
  small one for `due`/`status`/`baseline` if it reads better, wired into the existing `__main__.py`'s parser without
  changing the existing subcommands' behaviour. Print only through `say` (W2-170 item 1).
- Every child: cwd `--repo`, environment the driver's own plus `GOV_INDEP_RUNS_DIR`; stdout kept in `<R>/<A>/<step>.out`,
  stderr in `<R>/<A>/<step>.err`, never printed. One `STEP <name> <command line>` before each step. The driver never
  builds, opens, lists or stats a path under the sets root; every figure comes from a child's stdout (item 6).
- `GOV_MEMAUDIT_NOW` is the only clock (item 1), except where the suite's S9 gate case leaves it unset: then use the
  real UTC now. Bounded polls only.
- Add unit tests under `tests/unit/memaudit/` for the pieces the acceptance suite reaches only end to end (the churn
  computation, the mode rule, the USED boundary by step and exit, the digest's 12 lines), small and fast.
- Write `docs/changes/W2-172-evidence.md`: what was built, per KPI line the acceptance cases that show it and their
  result, the pytest summary lines, and any reading of the Interface you had to make (with the item number).
- **Every pytest through the heavy-slot gate**, TMPDIR outside the repository and outside ~/gov-os-runs (make the
  folders first with `mkdir -p /tmp/gov-w2-172-eng /home/usain/gov-os-worktrees/W2-172/.gov-runtime/scratch/empty-home`):
  `TMPDIR=/tmp/gov-w2-172-eng bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-172/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-172/src python3 -m pytest tests/acceptance/W2-172 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  and the same for `tests/unit/memaudit` and for `tests/acceptance/W2-170 tests/acceptance/W2-171` (they must stay
  green: you are not to change their behaviour). A single case: append `::<name>` to the folder. A heavy-slot or
  resource gate refusal is a wait: run again when it opens; it never counts as a refusal.
- The base-red rule: a case red on the base (80da3fbcca0d) for a reason outside this ticket is reported, not fixed.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-172/.gov-runtime/scratch/eng/,
  run with `bash <file>` or `python3 <file>`. Literal paths only as write targets.
- Commit your paths only, in batches as you go (at least one commit when the suite is green):
  `git commit -m "<subject>" --trailer "Task: DAEO-p8tv" --trailer "Role: engineer" --trailer "Implements: DEC-1101, DEC-1125, DEC-1097, DEC-1038, DEC-1050, DEC-1073" -- <your paths>`
  Never `Role: owner` or `Decided-by:`. No merge, no push, no edit of `.tickets/`, the register or `tests/acceptance/`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines of tests/acceptance/W2-172, tests/unit/memaudit and
tests/acceptance/W2-170 + W2-171) / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then `commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form |
the hook's reason | true or false-positive).
