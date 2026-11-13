```verdict
ticket: DAEO-p8tv
head: f706a77f5b7e
round: 1
verdict: PASS
blocking: 0
```

**Step 0, the sandbox check (launch_worker.sh):** (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-p8tv` failed as it should: `OSError: [Errno 30] Read-only file system`, and no file was made. (b) `git hash-object -w --stdin` worked (`1ae28402a1…`) and `git update-index --refresh` worked (exit 0). **ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing (exit 1). **Identity:** `git rev-parse HEAD` = `f706a77f5b7e0a641f29a90fda05ef05e2d30dc8`; `git status --porcelain` is empty when I finish.

Classification: 6 findings, 0 blocking. Four can be reached in ordinary work (R1-1, R1-2, R1-3, R1-5) and two cannot (R1-4, R1-6). None fails open or loses work. All are in scope.

```verdict
{"kpis": [
 {"kpi": "S1", "verdict": "pass", "findings": [{"id": "R1-4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S2", "verdict": "pass", "findings": []},
 {"kpi": "S3", "verdict": "pass", "findings": [{"id": "R1-6", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S4", "verdict": "pass", "findings": []},
 {"kpi": "S5", "verdict": "pass", "findings": [{"id": "R1-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S6", "verdict": "pass", "findings": []},
 {"kpi": "S7", "verdict": "pass", "findings": [{"id": "R1-3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "R1-5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S8", "verdict": "pass", "findings": []},
 {"kpi": "S9", "verdict": "pass", "findings": [{"id": "R1-1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "F1", "verdict": "pass", "findings": []},
 {"kpi": "F2", "verdict": "pass", "findings": []},
 {"kpi": "F3", "verdict": "pass", "findings": []},
 {"kpi": "F4", "verdict": "pass", "findings": []},
 {"kpi": "F5", "verdict": "pass", "findings": []}
]}
```

## Findings

**R1-1 — non-blocking — S9, Interface item 8 (set-up, "not due"), O4 — `governance/project/orchestration/tools/memaudit_cron.sh:20-28`**
- **What happens:** when the interpreter cannot import `gov`, the wrapper logs the run as "not due" and exits 0. Python's own "No module named" error exits 1, the same code `due` uses for "not due". The same happens when `run`/`due` are started outside the repository.
- **Shown by:** I ran the wrapper with its defaults (`/usr/bin/python3`, cwd an empty folder, planted runs folder and sets root). It exited 0 and wrote `{"due": false, "mode": "", "reason": "", "started": false, "exit": 0}`. `/usr/bin/python3 -m gov.memaudit due …` on its own exits 1 with `No module named 'gov'`.
- **Why it matters on this machine:** `gov` lives in the pinned venv (`~/.local/share/gov-os/pin-…/bin/python`), not in `/usr/bin/python3`.
  - The wrapper does not change to the repository, although item 8's set-up says "cwd is the repository". With no cwd, `--repo` falls back to the top level of the working directory.
  - ACT-MEMORY-AUDIT-CRON-1's drafted line has no `cd` and no `GOV_MEMAUDIT_PYTHON`.
  - Installed as drafted, the cron line would log "not due" every week and no audit would ever run. Releases are still held, because `status` would answer "not audited".
- Ordinary work: yes, because the drafted crontab line plus the O4 default hit it on the first firing. Consequence: other (no audit runs, misreported as "not due"; fails closed at the release check).
- **What would be right:** the wrapper counts a run as "not due" only when `due` printed `DUE no`; any other result is logged with its real code. It establishes the repository as cwd itself. Per DEC-803, the ACT that installs the crontab names a pinned interpreter that imports `gov`; that is an entry criterion of the ACT.
- **Evidence that would reverse it:** `/usr/bin/python3` on the target machine importing `gov` from the repository's cwd, and the ACT line changing to the repository first.

**R1-2 — non-blocking (a gap for the CTO) — S5 "a change to a retrieval path since the last audit", S7 RETRIEVAL line, item 9 — `src/gov/memaudit/schedule.py:165-171`**
- **What happens:** "the last audit commit" is read from the last `HISTORY.jsonl` line, and that includes an audit that stopped after USED (`measured: false`). A retrieval change made before such a stopped audit was measured by no audit, yet it stops counting as a back-to-weekly trigger. It also drops out of the next digest's RETRIEVAL list.
- **Shown by:** a planted repository with a retrieval change R on 10-20, then a stop after USED at A2 on 10-25 (after R). `HISTORY.jsonl` holds three calm measured lines at A1 and one stopped line at A2; now is 11-22.
  - With the stopped line, `due` gives `MODE monthly | DUE yes | REASON stable`.
  - Without the stopped line, `due` gives `MODE weekly | REASON retrieval`.
  - `status --since A1` answers `not audited` in both cases.
- Ordinary work: yes, because a stop after USED (a measure fault, a judge or auditor exit) is a planned path in S3. Consequence: other (the schedule can stay monthly, up to 28 days, over an unmeasured retrieval change; the release check still holds).
- **What would be right:** the trigger and the RETRIEVAL line start from the last *measured* audit's commit, or from the `AUDITS.log` line that S1 names as the start of the "changed since the last audit" list. The CTO decides which.
- **Evidence that would reverse it:** a CTO ruling that a stopped-after-USED audit counts as "the last audit".

**R1-3 — non-blocking (a gap) — S7/item 7 line 11, item 8 "gate busy" — `src/gov/memaudit/driver.py:116-121`, `digest.py:97-98`**
- **What happens:** a gate-busy stop prints `STOPPED judge gate busy`, but the digest says `STOP judge exit 2`. No child ran, so the 2 is invented. The line reads the same as the child's own exit 2: judge after USED, measure's "after USED" 2, or void's 2. Only `COUNTS.json` keeps `reason: "gate busy"`.
- **Shown by:** probe B, a gate that is open for measure and busy for judge, with the seam's defaults. The run made 62 gate calls and exited 2. The digest ends `STOP judge exit 2` / `OWNER stopped after USED at judge exit 2: the set is not run again`.
- Ordinary work: yes, because a full run or rebuild overlapping the audit for 60 minutes is enough. Consequence: other (the owner misreads why it stopped).
- **What would be right:** the digest names the gate as the cause. The Interface's line 11 has no form for this, so the CTO chooses one, e.g. `STOP <step> gate busy`.
- **Evidence that would reverse it:** a CTO ruling that `exit 2` is the intended form.

**R1-4 — non-blocking — S1 / item 2a — `src/gov/memaudit/driver.py:42-49, 179-180`**
- **What happens:** a launch step that exits 0 but whose last line is not a counts object is read as `{}`. For checker-1 that means a clean first pass, so round 2 is skipped and the step's cost is 0.
- **Shown by:** probe C, a wrapper launch script that drops the checker's counts line, with checker-1 marking q05 `revise`. The steps run were writer-1, preflight, checker-1, void, measure… with no writer-2 or checker-2. void dropped the question (`QUESTIONS kept 39 dropped 1; R1-WRONG 1`) and the run exited 0.
- Ordinary work: no, because the real launch script always ends its standard output with the counts line (`finish`, `indep_launch.py:480-481`). Consequence: other (the set is measured smaller; W2-170's void still drops the marked question).
- **What would be right:** a launch step that exits 0 without a readable counts object is a stop at that step.
- **Evidence that would reverse it:** the launch script's contract guaranteeing the counts line on exit 0, which in practice it already does. This is a recorded row.

**R1-5 — non-blocking (a gap) — S7 "after each stop … the questions kept, dropped" — `src/gov/memaudit/digest.py:86-90`**
- **What happens:** after a stop that comes after `void` (any stop after USED), the QUESTIONS line, and VERDICT, HIT5, MISSES and POOL with it, prints `not reached`, even though `DROPS.json` exists. These figures come only from step 12.
- **Shown by:** probe B's digest, which has `QUESTIONS not reached` after void ran.
- Ordinary work: yes. Consequence: other (the owner's line for a stopped-after-USED audit lacks the kept/dropped counts).
- **What would be right:** on a stop, the read-only `figures` child runs once, so the reached figures print. This is the CTO's choice.

**R1-6 — non-blocking — item 5 — `src/gov/memaudit/driver.py:253-274`**
- **What happens:** an unexpected end inside the cycle leaves the audit looking like one that has not run. In the probe it was a printed line refused by `say`. The process exits 4 with the `STARTS.log` line already written, and leaves `COUNTS.json` with `stop: null`, no STOPPED line and no digest.
- **Shown by:** probe E2, a launch path whose name holds `hidden`. Exit 4; lock free afterwards; STARTS 1; COUNTS present; DIGEST absent; no set made.
- Ordinary work: no, because it needs a crash or a refused path. Consequence: other. The lock is released and the set is not measured twice.
- **What would be right:** an unexpected end still records a stop at the current step in `COUNTS.json`.

## Probes run and results
1. **GATE-1 (a):** `--gate-cmd "<gate_stub> --check"` through the real driver. Exit 0; gate argv was `[['--check'], ['--check'], ['--check']]` (measure, judge, pool). **Sound.**
2. **Gate busy after USED (B):** stop at judge, exit 2, `used: true`, HISTORY line `measured: false, used: true`, OWNER line present. Under the seam with the defaults the polls are counted, not slept: 61 polls at judge. **Sound**, apart from R1-3.
3. **Churn:** at H the result was `(0.0294, True)` against an expected 3/102.
   - The tree-exclude glob `excl/**` removed both the 50 files and their in-window change.
   - A commit with an August author date and an in-window committer date was counted, so the window goes by committer time.
   - **Sound.**
4. **Due rule with a stopped-after-USED line:** R1-2.
5. **Lines that are not JSON** in HISTORY, STARTS (a truncated last line) and AUDITS.log: `due` and `run` both completed.
   - A truncated last STARTS line is skipped, and the line before it is used for RN-RECENT. Ordinary work: no (it needs an interrupted append); noted only.
6. **Lock:** free after a stop (E1) and after an unexpected end (E2). The descriptor is not inherited by children (`os.open` is close-on-exec by default; `subprocess` closes descriptors).
7. **Cron wrapper:** `grep -c crontab` is 0. `PY="${GOV_MEMAUDIT_PYTHON:-/usr/bin/python3}"` follows O4. Exit codes and the log line form were read and are sound. R1-1 found in a live run.
8. **Read against the code, without a separate run:**
   - **F1:** the driver's own process opens only `<runs>/indep/AUDITS.log` and the files under `<R>`, and reads `<link>.lock`, git and rebuild.yaml (via git). `say` only resolves the sets root itself (realpath). Under the root it opens, lists or stats nothing.
   - **F1, printed lines:** the STEP lines hold the root as a value, the brief under `indep-briefs/`, and `<link>/.gov-runtime/store.db`.
   - **F2:** the digest comes only from the `figures` line, the launch counts, git and the driver's counts. The `.err` files get the launch script's one status line.
   - **Item 3:** the checks run in the Interface's order.
   - **S3, USED boundary:** decided by the step and its code; an unknown measure code counts as after USED, which fails closed.
   - **S3, canary:** only launch steps, only 16, once.
   - **Partial files:** DIGEST.txt and COUNTS.json are written whole by rename.
   - **Measuring a rebuilt half:** W2-171's `declare` refuses `DC-STORE` (before USED) if the link has moved to another head mid-cycle. Fails closed.
   - **F5:** the engineer's commits bf21edd96 and f989ca89b touch only allowed paths. The acceptance-folder changes are the test designer's (5193add39, `Role: independent-test-designer`), so the engineer did not change the acceptance tests.
9. I did not re-run the 163-case suite or the unit tests; the lead ran them.

## Judgement on each engineer reading
- **Item 3, TD-2 (b), RN-NAME by `STARTS.log`:** faithful.
- **A refusal printed as the digest, whose line 11 is `REFUSED <code>`:** faithful. The line `REFUSED <code>` is printed, and nothing is written where `<A>/` already exists.
- **TD-1 (b), no `--force` in the digest:** faithful.
- **`due`/`status` fall back to the main line's tip when no link resolves:** a gap. Item 9 names only the link's head; low risk, but the CTO should confirm. `status --store-link` is an extra flag that changes no stated behaviour.
- **"The last audit commit" from HISTORY, else AUDITS.log:** a gap with a consequence (R1-2).
- **Reason-code mapping** (`start` below 3 measured lines; triggers in order `churn`, `retrieval`, `verdict`, `pool`; then `stable`; else `active`): faithful.
- **Polls counted, not slept, under `GOV_MEMAUDIT_NOW`:** a faithful reading of "measured by the clock seam" when that clock is fixed.
- **Gate-busy digest line `STOP <step> exit 2`:** changes a stated behaviour by inventing a code; a gap (R1-3). `shlex.split` follows GATE-1 (a).
- **Wrapper's default gate `$HOME/.local/bin/gov resources --check`:** faithful to O2, and more robust under cron's short PATH. If it is missing, the gate reads as busy, which fails closed.
- **Canary retry prints the STEP line once:** faithful.
- **A brief missing at C stops the step with code 10 and no child:** fills a gap sensibly (the launch script's own code).
- **COST names only the steps that cost; the other figures come from `figures` only:** faithful to F1, with a gap for stops (R1-5).

## Twelve fields
task: DAEO-p8tv
status: done — FULL review round 1 complete, PASS with 0 blocking findings
work_completed: Sandbox, identity and ps checks; read the ticket, the Interface, the change, the evidence readings, the launch script's contracts, and W2-170's/W2-171's `say`, `declare` and `drops`; ran 7 probes on planted worlds in the sandbox TMPDIR; judged all 6 findings and all 12 readings
files_changed: none (repository untouched; probe scripts and worlds only under `$TMPDIR/rev`)
evidence: the probe outputs quoted above (A to E, the due/churn probe, the wrapper run)
tests: none of the suites re-run (the lead's); probe scripts A to E went through heavy_slot.sh; the small due/churn probe and the wrapper run were run directly
discoveries:
- On this machine `/usr/bin/python3` cannot import `gov`; only the pinned venv can (R1-1).
- In the sandbox, heavy_slot.sh cannot remove its `/tmp/gov-os-heavy-prio-*` file ("Read-only file system"), but the runs went ahead.
risks: ACT-MEMORY-AUDIT-CRON-1 as drafted would never start an audit (R1-1)
lessons: none new
proposed_decisions:
- For R1-2: "the last audit" for the trigger and the RETRIEVAL line = the last measured audit's commit, or `AUDITS.log`'s.
- For R1-3: the gate-busy form of digest line 11.
- For R1-1: an entry criterion on ACT-MEMORY-AUDIT-CRON-1 — `cd` to the repository and a `GOV_MEMAUDIT_PYTHON` that imports `gov`.
unresolved: R1-2 and R1-3 (CTO's choice); R1-5 (optional)
recommended_next_action: land on this verdict; record R1-1 to R1-6 as rows; put R1-1's entry criterion on ACT-MEMORY-AUDIT-CRON-1 (DEC-803); the CTO decides R1-2 and R1-3 in a later package, with no round of its own (DEC-802)
guard_refusals:
- 20:2x | `mkdir .gov-runtime/scratch/rev-tmp` (Bash) | hook: "a reviewer or auditor writes only its own review or audit record … its own scratch, or /tmp (DEC-953 item 2)" | true (used the sandbox TMPDIR, as the brief allows)
- 20:2x | `git show -s/--name-only <commit>` (Bash) | guard (DEC-953): "could not decide: git cannot say whether a revision holds the hidden part; refused" | false-positive (the names came from `git log --format` and `git diff --name-only`)
- 20:2x | Write tool to `$TMPDIR/rev/probe.py` | permission not granted (no hook reason) | false-positive (the script was written into TMPDIR with Bash, as the brief prescribes; this is the one place a refused tool was followed by another form, and it is reported here)