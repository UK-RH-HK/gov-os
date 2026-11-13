# Brief rev-1: independent auditor for DAEO-p8tv (W2-172), FULL review round 1, class C2

You are the independent auditor (a fresh, read-only session) for ticket DAEO-p8tv (W2-172: the memory audit's driver
and schedule: `python3 -m gov.memaudit run|due|baseline|status|figures` and the cron wrapper
`governance/project/orchestration/tools/memaudit_cron.sh`). Audit the branch head **f706a77f5b7e** of `w2/W2-172` in
/home/usain/gov-os-worktrees/W2-172 against the ticket's KPI lines (S1-S9, F1-F5) and its `## Interface` (items 1-12,
O1-O4), with the CTO's decision PKG-W2-172-TESTS-1 below, which binds and is in the main tree's ticket copy but not yet
in the worktree's:

- **GATE-1 (a):** the driver splits `--gate-cmd`'s value with `shlex.split` and runs the words as given, so the default
  `gov resources --check` works; the Interface's "called with no arguments" reads "run as its words".
- **TD-1 (b):** the 12-line digest does not record `--force`; item 1's "and the digest" is corrected to the counts only.
- **TD-2 (b):** RN-NAME is judged by `STARTS.log` (an audit started), not by a refusal's `COUNTS.json`, so a refused run
  can be retried the same day.

You change nothing in the repository: no edit, no commit, no merge. Your verdict is your return.

## What to read
| what | path |
|---|---|
| the ticket (KPI lines, Interface at its end) | /home/usain/gov-os-worktrees/W2-172/.tickets/DAEO-p8tv.md |
| the change | `git -C /home/usain/gov-os-worktrees/W2-172 diff 80da3fbcca0d..f706a77f5b7e -- src governance docs tests/unit` (driver.py, schedule.py, digest.py, `__main__.py`, memaudit_cron.sh, tests/unit/memaudit/test_driver.py, docs/changes/W2-172-evidence.md, whose "Readings" section lists the engineer's readings of the Interface) |
| the independent acceptance suite (163 cases, all green at this head) | tests/acceptance/W2-172/ (README.md maps KPI lines to cases) |
| W2-170's and W2-171's code and Interfaces (called as children, never changed) | src/gov/memaudit/; .tickets/DAEO-61vm.md, .tickets/DAEO-k1e2.md |
| the launch script (called, never changed) | governance/project/orchestration/tools/indep_launch.py, indep-schemas/indep-counts.schema.json |
| the sources (read by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1101, DEC-1125, DEC-1097, DEC-1038, DEC-1050, DEC-1073 |

Search with Read, Grep and Glob; search again once in different words if the first does not answer (DEC-1065).

## What to probe (at least these; add your own)
1. Each KPI line and failure line against the code, not only against the tests: where a test is weaker than its line,
   probe the line directly.
2. The engineer's readings (evidence file, "Readings"): each one against the Interface's words. Say which are faithful,
   which change a stated behaviour, and which are gaps the CTO must decide. In particular: the gate-busy digest line
   (`STOP <step> exit 2`, "gate busy" only in the STOPPED line and COUNTS); polls counted, not slept, under
   `GOV_MEMAUDIT_NOW`; "the last audit commit" from HISTORY.jsonl else AUDITS.log; the reason-code mapping; `status`
   taking `--store-link`; the main line's tip when no link resolves.
3. GATE-1 (a): no acceptance case runs a multi-word `--gate-cmd` through the driver. Probe it (e.g. a planted gate
   script given as `"<script> --check"`).
4. F1: the driver's own process opens, lists or stats no path under `--sets-root` (and the runs folder of the audit set),
   and no printed line names `fixtures/`, `runs/` or `indep-walls/`. F2: no question, gold answer, answer or source path
   reaches the digest, stdout or the driver's files.
5. S3's USED boundary by step and exit code, the canary retry (only 16, only launch steps, once), and that nothing after
   a stop after USED runs that audit again.
6. S5's churn: the denominator less tree-exclude matches at X, the 28-day window by X's committer time, and the
   monthly/weekly rule and due days (5/6, 27/28).
7. The cron wrapper: the pinned interpreter (O4), no `crontab` word, the log line, exit codes.
8. Robustness the tests may miss: the lock released on every exit path, partial files (DIGEST.txt written whole by
   rename), a child that prints no counts line, an `AUDITS.log` or `HISTORY.jsonl` line that is not JSON.

Your probes are read-only on the repository and run by Bash in your own TMPDIR (DEC-1144 (7)): make
`/home/usain/gov-os-worktrees/W2-172/.gov-runtime/scratch/rev-tmp` (or use the sandbox's TMPDIR if that is refused)
and plant everything there; scripts longer than one line go there too. Any pytest goes through the heavy-slot gate:
`TMPDIR=<your tmp> bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=<an empty folder in your tmp> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-172/src python3 -m pytest <path> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`.
A heavy-slot or resource refusal is a wait. Never open the real `~/gov-os-eval`, `~/gov-os-runs`, a hidden half, a
memory-verdict folder or the crontab; never run a real model call or a real search.
Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
another form (DEC-1142 (9)).

The ticket's context packet (`gov context DAEO-p8tv --role independent-auditor --budget 20000`) follows.

----

