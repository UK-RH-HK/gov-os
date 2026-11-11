# LOAD-BALANCER-1: W2-20's resource gate after the re-pin, what bypasses it, how to close the gaps, and the sample day

Helper for the CTO (DAEO-sdxk), 11-11, read at about 15:25 to 15:40 UTC. Read-only: no config changed, no measurement run,
no lead started. The only live call was `gov resources --json` (the plain reading; it also removes dead registry entries,
and there were none). Code read: the main tree's `src/gov/` (w2/integrate head) and the pin's copy. The nine files that
matter (`launch/launcher.py`, `launch/gate.py`, `resources/{gate,command,measure,config,slots,registry,machine}.py`) are
byte-identical in `pin-797495bdfc70`, so what the pin runs is what is described here.

## 1. Is the gate live since the re-pin?

**Yes, for everything started by `gov launch`. No, for the dispatcher's leads, which are the biggest users.**

- `gov` on the PATH is `pin-797495bdfc70` since 13:31. It has `gov resources` (reading, `--check`, `--register`, `--slot`,
  `--sample`, `--remeasure`, `--init-config`, `--trip-wire`) and `gov launch`'s gate call:
  `src/gov/launch/launcher.py:474` (worker) and `:447` (lead) call `_admit_start` (`:391`), which calls
  `check_start` (`src/gov/launch/gate.py:44`). A shut gate refuses with `LAUNCH_REFUSED`; one `--gate-override DEC-NNN`
  starts it anyway and writes a line to `~/.gov-os/machine/launch.log` (`gate.py:117`). A started session is entered in
  the registry at `launcher.py:542`.
- The gate is open now: memory 15.2 GB free (needs 3 GiB + 2.04 GiB for one newcomer), load 4.9 against 20 cores, 2.6 busy
  cores, disk 821 GiB and 65 M inodes free, no slot held, GPU not asked. `gate.json` is the file ACT-GATE-CONFIG-2 wrote
  (11-09 15:08); every value is present, three are named "due for re-measure".
- **It was already in force before the re-pin for one path.** `tools/launch_worker.sh` runs `PYTHONPATH="$tree/src" python3 -m
  gov.cli.main launch` (line 54), i.e. the worktree's own code. W2-20 merged into integrate on 11-09 (`686c594f3997`), and every
  recent worktree has it (the 12 newest, checked). 51 of 91 worktrees that hold a launcher have it; the 40 without are old
  closed tickets (W2-104, W2-105, W2-11, W2-122, W2-123, W2-13, W2-136, W2-138, W2-141, W2-142, W2-145, W2-147 and the like).
  A worker launched from one of those is not gated.
- **Evidence that gate checks happen.** An open gate writes no log line (only overrides are logged, and `launch.log` does
  not exist: no override has ever been used). But every check reads the servers' CPU and appends a line to
  `~/.gov-os/machine/embedding-cpu.jsonl`. Since 13:31 UTC that file has checks at 14:04:31, 14:15:17, 15:11:54 and 15:25:05.
  The first three match the three worker launches in `log/spend.jsonl` (the W2-20 reviewer, ended 14:10; the W2-32
  test designer, ended 14:17; the W2-32 reviewer, ended 15:15). The fourth is my own reading. The same file shows checks at
  22:xx on 11-10, matching the 22:10 and 22:14 launches. The `sessions/` folder was last changed at 15:15:15, when the
  W2-32 reviewer's entry went.
- **The W2-170 lead (started 15:18:03 by the dispatcher) did NOT go through the gate.** No check was written at 15:18
  (between 15:11:54 and my 15:25:05 there is none), `launch.log` is absent, and the sessions folder was empty at 15:25.
  Cause is in section 2: the dispatcher starts leads with `dispatch/launch_now.sh`, which runs `claude -p` itself.

## 2. What goes through the gate and what bypasses it

| Path | Gated? | By which line | Notes |
|---|---|---|---|
| `gov launch <worker role>` (bare, pinned) | **yes** | `launcher.py:474` -> `gate.py:44`; registered `:542` | refuses when shut; override logged |
| `gov launch orchestrator <ticket>` | **yes** | `launcher.py:447`; plan check `:439` | also refuses a ticket not in the approved ready list or with unmet waits |
| CTO's `tools/launch_worker.sh` | **yes, if the worktree has W2-20** | line 54 (`python3 -m gov.cli.main launch`, tree's own src) | the dry run (lines 87-100) does not call the gate; the launch does. 40 old worktrees lack it |
| Dispatcher's leads (`dispatch/dispatcher.py:2461` `default_launch_argv` -> `launch_now.sh:16` `exec claude -p`) | **no** | its own admission, `admit_safely` (`dispatcher.py:625`), from measured peaks and the Load Balancer's forecast; `tools/gate_check.py` shown for comparison | not registered, so the gate cannot see the leads. It reads them only as less free memory |
| `tools/launch_when_gate_opens.sh` (the owner's launch form) | **no** (an older gate) | `gate_check.py` in a loop, then `exec claude -p` | gate_check has its own numbers: floor 6.4 GiB, working 2.04 GiB (`tools/gate-config.json`), not the product's 3 GiB |
| CTO's helpers (Agent-tool subagents) | **no** | none; they live inside the CTO's process | their memory is in the CTO session's, which is not registered |
| The CTO session itself, the CTO sentinel (tmux, haiku) | **no** | started by the owner's editor and by tmux | never entered in the registry |
| Operator agent (cron `operator_launch.py`, every 10 min) | **no** | `operator_launch.py:43-45` runs `claude -p --restricted` itself | one session at a time, from its queue |
| Independent sessions (`tools/indep_launch.py`) | **no** | `indep_launch.py:1343, :1381` run `claude` under `timeout` | evaluation runs, own launcher |
| Editor: VS Code server, its extensions, language servers, Codex, ripgrep | **no** | none | about 6.0 GB resident now, the largest single consumer (the CTO's own `claude` is inside this figure, 0.5 GB) |
| Embedding servers and reranker | **read, not started or capped by the gate** | `resources/machine.py` readings; CPUs set by their own ACTs | llama servers 1.6 GB, reranker 1.6 GB |
| Test runs (`heavy_slot.sh`, `verify_lock.sh`, `gov accept`, pytest) | **partly: by another limiter** | `heavy_slot.sh:166-168` takes `/tmp/gov-os-heavy-slot-N.lock` (3 slots, 6 workers, `taskset`) | the gate has its own slots (`~/.gov-os/machine/slots/`, `gov resources --slot`, `slots.py:311`). Nothing uses them. The gate counts these runs only through free memory and load |
| Store rebuilds (`rebuild_slot.sh` -> `heavy_slot.sh`) | **partly**, same as tests | | `src/gov/rebuild/watch.py` mentions `gov resources --slot` in its comment only |
| `gov close` | **disk only, by its own function** | `src/gov/close/gates.py:226` `check_disk` (not W2-20's `check_disk`) | its regression runs go through `close_build.py` -> `heavy_slot.sh` |
| Landings, merge queue, nightly | **partly** (heavy_slot) | `merge_queue.py`, `close_build.py` | |

Two points worth saying plainly:

1. **There are two gates with different numbers.** The product's (floor 3 GiB, load below 20) and the dispatcher's (floor 6.4 GiB
   raised by `oom_watch.sh`, band 14 to 18 cores). The dispatcher's is the stricter one, so for leads the product gate would
   add only a backstop. Its real value for leads is the registry, not the refusal (section 4).
2. **There are two sets of heavy-job slots.** `heavy_slot.sh` (the one in use) and the product's. They do not know each other.
   Moving test runs to the product's slots is not free: they would keep off the CPUs 8-19 that the embedding servers own
   (`slots.py:64`, `cpu_set`), leaving 8 CPUs for 3 slots. The EMG-gitleaks measurement (comment in `heavy_slot.sh`) found
   runs more than twice as slow that way.

## 3. How to bring each bypass under the gate

Every change below to `governance/project/orchestration/tools/dispatch/**`, a crontab line or a hook is class (b) in
`~/gov-os-operator/install/class-rules.yaml` (rule "watchers" and "crontab"): it goes by an ACT with owner approval, not
by a helper. Items that only run a `gov` command are not changes.

| Bypass | Recommendation | Cost |
|---|---|---|
| **Dispatcher's leads** (the big one) | **A (now, small): two lines in `launch_now.sh`.** Before the launch: `gov resources --check || exit 3` (a shut gate then holds the lead, with the reading in `log/<W2>-<time>-launch.txt`). Replace `exec claude ...` by `claude ... & pid=$!; gov resources --register $pid --ticket $ID --session-role orchestrator; wait $pid`. | One ACT (class b), rehearsal in a clone. Leads then show in the gate's reading, count in the memory rule, and are sampled by the sample day. The dispatcher's own admission stays first. A small race (check and register are not under the start lock; starts are 120 s apart, so it is theoretical). **B (later, a ticket): launch leads with `gov launch orchestrator <ticket>`,** giving the gate, the plan check, the template and the registry in one place, as DEC-1088 (5) intended. |
| | B's extra costs: `GOV_PLAN_READY` must name the dispatcher's `dispatch/ready.txt`; the plan's waits must be met or a ticket gets a `plan_override`; `environ.py` drops `CLAUDE_CODE_SUBAGENT_MODEL` (the leads' subagents would lose `claude-opus-5-5`; `build_lead_settings`, `launcher.py:240`, would need to carry it: a W2-20 or W2-153 change); the dispatcher must read exit 3 and `LAUNCH_REFUSED` as "waits". The identity marker `GOV_ROLE":"orchestrator","GOV_TICKET` still appears in the argument text, so leads would still be recognised. | A new ticket with its own tests. Do after A and after the sample day. |
| **CTO session and its helpers** | Register the CTO's own `claude` pid once per session: `gov resources --register <pid> --ticket DAEO-sdxk --session-role orchestrator`. The subagents are in its process tree, so they are counted as the CTO's memory (no double charge: `registry.py:94`). | Free; no code. One working-size charge in the memory rule. A dead pid clears itself on the next reading. A helper that is a `launch_worker.sh` worker is already its own session. |
| **Test runs, rebuilds** | Keep `heavy_slot.sh` as the one limiter; keep the rule that every test and rebuild goes through it (EMG-common already says so). Do **not** move to `gov resources --slot` before W2-20's CPU-set rule is re-sized (it would starve the slots). | Free. The gate still sees them only through memory and load; that is the honest reading of what is running. |
| **`launch_when_gate_opens.sh`, `lead_chain2.sh`** | Retire (`lead_chain2.sh.retired` exists already); the dispatcher replaced them. | Nothing runs them. |
| **Operator agent, independent sessions** | Leave. One at a time, small, own walls. If the owner wants them counted: the same `--register` line after their `Popen`. | Class (b) ACTs for two small files; low value. |
| **Editor and other processes (6 GB of VS Code)** | Only a machine-level cap can bound them: that is MEMORY-PROTECTION-1's package. For sizing it: VS Code 6.0 GB, llama servers 1.6, reranker 1.6, everything else 0.5, of 24.6 GB total, now. | Not this package. |
| **Old worktrees without W2-20** | Before `launch_worker.sh` is used in one of them, merge integrate into it (the CTO's existing practice for stale worktrees). A cheap guard: have `launch_worker.sh` refuse when `grep -q _admit_start $tree/src/gov/launch/launcher.py` fails. | One small edit to a CTO tool (scratch tools are not in the class rules; confirm). |

Recommended order for the window: (1) register the CTO session; (2) prepare A as an ACT (it is what makes the sample day
meaningful); (3) run the sample day; (4) B as a ticket after.

## 4. The sample day and `--remeasure` (DEC-1105)

**DEC-1105 (owner, 11-09), the sentence:** "Then the CTO merges W2-20, runs `gov resources --sample` over a working day and
then `--remeasure`." (S16 per CPU and R2-F1 were the exception round before it; both done, merged 11-09.)

**What it is, exactly.**

- `gov resources --sample` (`resources/measure.py:60`) is one reading, a fraction of a second. It lists every session in
  the registry (`~/.gov-os/machine/sessions/`), measures each one's process-tree memory, notes whether
  `/tmp/gov-os-verify.lock` is held, adds each holder of one of the gate's own slots, and appends **one JSON line** to
  `~/.gov-os/machine/samples.jsonl`. Nothing else is written.
- "A working day" is not defined in the decision. The CTO's tool `tools/resources_sample_day.sh` (D30 in
  EMERGENCY-TOOLS-1, "not yet (after the re-pin)") reads it as 96 samples, one every 300 s: **8 hours**. The CTO runs it, in
  the background; the line goes to `log/resources-sample-day.log`; samples go to `samples.jsonl`. Today that file has two
  lines (11-09 16:23 and 16:24), both with an empty list (the merge-time tests, no session was registered).
- `gov resources --remeasure` (`measure.py:109`) reads the whole `samples.jsonl` and rewrites **three values of
  `~/.gov-os/machine/gate.json`**, each dated today with a source naming the samples (whole file replaced atomically, mode 0600; it prints old and new side by side):
  - `working_size_bytes`: the **largest** session sample taken while no verification run held the lock. This is the per-session
    charge in the memory rule `available + live >= 3 GiB + working_size x (running + 1)` (`resources/gate.py:103`).
    Today 2,191,601,664 B (2.04 GiB, DEC-947, dated 10-29).
  - `verification_peak_bytes`: the largest session sample at all. Today 7,582,199,808 B (7.06 GiB). Held in the file but not used by
    the memory rule now (DEC-983 removed the reservation).
  - `rebuild_peak_bytes`: the largest sample of a slot holder of kind `rebuild`. Today the same 7.06 GiB, "not yet measured".
  A value with no sample keeps its old value.
- Nothing else changes. `--sample` and `--remeasure` have no other effect; `due_for_remeasure` clears for a value once it is
  dated within seven days.

**The measured lead peak today.**

- `dispatch/peaks.json` (computed 15:19:01, 7-day window): the lead's p95 and max are both **243 MB**, from **one** sample, the
  W2-170 test-design lead (DAEO-61vm, ran 2 minutes). It is not a figure to rely on.
- `log/lead-mem.jsonl` (15,460 lines, 10-29 to 11-11; the whole tree of a lead: its session, workers, suites): 19,823 lead samples;
  p50 400 MB, **p95 4.09 GB, max 9.58 GB** (DAEO-s9qc, 10-30 22:00). Daily maxima 7.6, 9.6, 7.4, 7.7, 6.5 GB on 10-29 to 11-02.
  **No lead ran from 11-03 to 11-10**, and the only 11-11 samples are the 243 and 265 MB ones.
- The numbers in the brief (p95 2,026 MB, max 3,244 MB at 11-09 22:32) are **not in any file I read.** The nearest are the
  ones in ACT-GATE-CONFIG-1 ("LB peaks 11-09 12:27: a lead's p95 3,244 MB, max 6,513 MB"), which are the 11-02 window (daily max
  6,514 MB on 11-02). I would use 3.2 GB p95 and 6.5 GB max for the busy week, and say the week of 11-03 to 11-10 is empty.

**Is running them a config change that needs an ACT?** No, in my reading; but say so on the record.

- DEC-1105 names both commands and names the CTO as the one who runs them: that is the owner's permission.
- ACT-GATE-CONFIG-1 and -2 say it themselves: the file is written from the decisions "and does not edit values"; the working size is
  corrected "by W2-20's `gov resources --sample` over a working day, then `--remeasure`".
- Against that: the operator's `class-rules.yaml` rule `machine-gate` lists `~/.gov-os/machine/**` as class (b), control
  ("they decide what launches"). That rule is about an ACT's diff the operator agent reviews; the commands are the product writing its
  own figures under a standing owner decision. Safest form: cite DEC-1105 in the record; copy `gate.json` and `samples.jsonl` to
  scratch before `--remeasure`; if the guard refuses the first `--sample` call, take the refusal and ask the owner (no routing round).

**Three things to know before the sample day (each found in the code, none run).**

1. **Leads are not in the registry, so a day of samples will not measure a lead.** Only sessions started by `gov launch` (the
   `launch_worker.sh` workers, auditors, test designers) are sampled. The dispatcher's leads are not, nor is the CTO. The sample
   day would measure small sessions and set the "working size" from them. Fix: ACT A in section 3, or by hand: after each dispatcher
   start, `gov resources --register <lead pid> --ticket <DAEO id> --session-role orchestrator`, finding the pid from
   `ps -eo pid,args` (the line holding `GOV_TICKET":"<id>`).
2. **The verification lock has not been used since 10-31.** `verify_lock.sh` now only calls `heavy_slot.sh` (DEC-979 D1), and
   `/tmp/gov-os-verify.lock` does not exist. So every sample reads "no verification running", and `--remeasure`'s "working size
   outside verification" becomes the **largest sample of any kind, test runs inside a lead's tree included**: likely 6 to 9 GB for a
   lead, as in 10-29 to 11-02, against 2.04 GiB now. The gate would then admit far fewer registered sessions at once. With 15 GB free:
   at 2.04 GiB, about 5 (3 + 2.04 x 6 = 15.2 GiB); at 6.3 GiB (6.5 GB), **1** (a second start refused for memory, with honest
   work refused: DEC-1105's own basis, question 2). Dispatcher leads, being unregistered, would not be refused; workers launched
   by `launch_worker.sh` would. So: run the sample day, **read the samples first** (`samples_summary.py`, which prints what
   `--remeasure` would write beside the p50 and p95), and only then decide. If the maximum is far above the p95, ask the owner for the
   p95 (or a stated figure) to be written by an ACT (class b), instead of `--remeasure`'s maximum. (A real fix is a test-run marker for `heavy_slot.sh` or a rule change in W2-20: a ticket.)
3. **`tools/resources_sample_day.sh` runs `--remeasure` by itself at the end** and uses `pin-bcea09060ebc`'s Python with the main
   tree's `src` ("W2-20 is not on the pin until the re-pin": now stale). `resources_sample_day_v2.sh` beside this file uses the new
   pin, takes the same samples, **does not remeasure**, and writes its pid to `log/resources-sample-day.log.pid`. Also: `rebuild_peak_bytes` will not be
   measured (`heavy_slot.sh` holders are not the gate's slot holders); it stays at the verification-peak copy and keeps showing as "due".

**The exact commands, for the CTO in the window (none run by me).**

```
# 0. look: the plain reading (read-only)
gov resources --json
# 1. copies for the record (scratch, not the machine folder)
cp -p ~/.gov-os/machine/gate.json    /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/load-balancer/gate.json.before-remeasure
cp -p ~/.gov-os/machine/samples.jsonl /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/load-balancer/samples.jsonl.before
# 2. register the CTO's own session (its claude pid), and each lead after the dispatcher starts it
gov resources --register <pid> --ticket DAEO-sdxk --session-role orchestrator
gov resources --register <lead pid> --ticket <DAEO id> --session-role orchestrator
# 3. start the sampler detached, 96 x 300 s = 8 h (N= and EVERY= change it); stop early by: touch .../log/resources-sample-day.stop; or by pid with tools/proc.sh from log/resources-sample-day.log.pid
setsid -f bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/load-balancer/resources_sample_day_v2.sh
# 4. look at it any time (read-only)
python3 -I /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/load-balancer/samples_summary.py
tail -5 /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/resources-sample-day.log
# 5. after the day, if the summary's working-size line is a figure the CTO accepts (see point 2):
gov resources --remeasure --json      # prints old and new; writes gate.json (3 values), dated today
gov resources --json                  # the gate again; due_for_remeasure should list only rebuild_peak_bytes
```

Quick test of the sample step before leaving it: with a registered session, one `gov resources --sample --json` should return a
non-empty `samples` list; with none registered it returns `[]` (as on 11-09).

## Open items for the CTO

- The brief's lead peak figures could not be found (above).
- The three ACT candidates: A (`launch_now.sh`), the `launch_worker.sh` guard (a scratch tool), and the p95 write if section 4 point 2 bites.
- Not checked: whether a hand `--register` of a `claude -p` pid keeps its entry for the whole run (`registry.same_process` compares
  the process start; an `exec` keeps the pid, so it should). Try it on the first lead.
- Not read: the two forbidden folders, `gov-os-eval` and `gov-os-runs` (the registry and the logs I used are under `~/.gov-os/`).
