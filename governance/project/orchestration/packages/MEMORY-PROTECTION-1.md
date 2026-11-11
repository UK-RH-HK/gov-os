# MEMORY-PROTECTION-1: keeping a runaway process from taking WSL down again

Prepared 2026-11-11 15:20-16:00 UTC by a helper of the CTO (orchestrator DAEO-sdxk), class C2 (DEC-1120). Nothing on the
machine was changed. The only live tests were small, throwaway scopes (section 5) that are gone. Scratch folder:
`.gov-runtime/scratch/orchestrator/drafts/memory-protection/` (this file, `mem_guard.py`, `tmp/` with the evidence).

## 0. The short version (for the owner)

- **What happened.** At 14:18 about 2,161 tiny `rg` (ripgrep) processes, about 9 MB each, filled all 24 GB of the WSL
  machine. The kernel could not free memory by killing any one of them, so it killed the editor server twice instead. WSL
  went down until 14:30. Windows itself stayed up.
- **Layer 1, the memory cap, is already in place and did its job.** `.wslconfig` has said `memory=24GB`, `swap=8GB`,
  `autoMemoryReclaim=gradual` since 4 October. The cap is why Windows survived (it keeps 7.8 GB of the 31.8 GB). A different
  number would not have stopped this storm. **Recommendation: change nothing in `.wslconfig` now.** That also means no WSL
  restart is needed for this package, and DEC-1038 (3) ("no change before the RAM upgrade's restart") is not touched.
- **Layer 2, an early guard inside WSL, is the real fix.** `systemd-oomd` and `earlyoom` are not installed, would need
  `sudo` (refused to every session, DEC-953 item 2), and would not have worked on this failure anyway (section 3.1).
  Instead I wrote and rehearsed `mem_guard.py`, a small program in the CTO's tools. Once a second it counts `rg`
  processes. At more than 150 it marks them as "kill me first" for the kernel. At more than 300 (or 50 with memory
  under 3 GiB) it kills only the `rg` processes, by pid, and writes an inbox item naming the parent that spawned them.
  It never touches a session, a server, a lead, a test run or the editor. Modelled on 14:18, it would have stopped the storm
  about 6 seconds after it began, with about 13 GB still free, and nothing else would have been lost.
- **No ACT is needed for the guard** (it is the CTO's own tool under `.gov-runtime/`, class "none" in the rule table). Three
  small decisions are the owner's (section 6): D1 the kill-by-program-name exception for `rg` only; D2 adding the guard
  to restart class 4; D3 leaving swap at 8 GB.
- **Two findings that need the CTO today** (section 7): `oom_watch.sh` has exited (a false trip at 15:23:34 from someone's
  scope test), so the rg tripwire is **not running**; and no memory samples exist for 14:18 (the sampler was down).

## 1. Facts checked today (read-only)

| Fact | Value | Source |
|---|---|---|
| Windows RAM | 31.8 GiB (34,186,006,528 bytes; 33,384,772 kB visible) | `powershell.exe ... TotalPhysicalMemory` |
| Windows free right now | 3.9 GB, with the WSL VM holding 20.1 GB (`vmmemWSL`) | `Get-CimInstance Win32_OperatingSystem` |
| `.wslconfig` (exists, dated 4 Oct) | `[wsl2] memory=24GB swap=8GB` and `[experimental] autoMemoryReclaim=gradual` | `/mnt/c/Users/usain/.wslconfig` |
| Linux view | 24,607,392 kB total (24 GiB), 8 GiB swap, 20 CPUs, kernel 6.18.33.2, systemd, PSI on | `/proc/meminfo`, `uname` |
| At the 14:18:47 dump | 6,291,103 pages RAM (exactly the 24 GiB cap); anonymous memory 21.9 GB; swap 7.1 of 8 GB used; free 215 MB | `journalctl -b -1 -k` |
| The task table (14:19:10) | 2,180 tasks; 2,161 are `rg`: 8-12 MB each (17.2 GB private + 3.4 GB shared binary), 1.2 GB in swap; no `oom_score_adj` set on any | parsed: `tmp/parse_tasks.py` |
| What the kernel killed | pid 1267 (the editor server's main thread), 873 MB, `oom_score_adj` 0, at 14:19:10 and 14:21:55; then systemd killed `init.scope` at 14:23:30 | kernel and systemd log |
| Why not an `rg` | the kernel kills the biggest single process; each `rg` scored about 10 MB, the editor server 873 MB. Killing it freed almost nothing, so the storm went on | the dump |
| Where processes live | all sessions, VS Code, both embedding servers, the reranker run in `init.scope` (no per-service cgroup); only the sentinel's tmux scope and cron are separate | `/proc/<pid>/cgroup` |
| Who has `rg` installed | no system `rg`; three bundles: VS Code's `@vscode/ripgrep-universal`, and the OpenAI ChatGPT/Codex extension's `rg` and `codex-path/rg` | `find` |
| The editor settings | `search.exclude` and `files.watcherExclude` for `.gov-runtime`, `gov-os-worktrees`, `gov-os-runs`, written 15:24:47 today (DECIDED-NOT-DONE row 142 (b)) | `~/.vscode-server/data/Machine/settings.json` |
| Missing data | no memory samples between 11-10 21:28 and 11-11 15:04 (row 143); nothing records the rate at which the storm grew | `log/lead-mem.jsonl` |
| Today's working set | used 8.0 GB: reranker 1.6, shared embedder 1.0, query embedder 0.56, VS Code about 3, Claude sessions about 1; leads p95 2.0 GB, max 3.2 GB; one lead's test run peaks at 7.1 GB | `ps`, `gate-config.json`, `peaks.json` |

Correction to the brief: `.wslconfig` is not missing; it already holds the cap.

## 2. Layer 1: the memory and swap cap for WSL

**What it is.** Windows gives the WSL virtual machine at most `memory` of RAM and `swap` of swap file. When the machine
inside is out of memory at the cap, the Linux kernel inside it does the killing (its own out-of-memory handling), not Windows.
Windows only loses what it lent.

**The exact config today (keep it):**
```
[wsl2]
memory=24GB
swap=8GB

[experimental]
autoMemoryReclaim=gradual
```
All 20 processors are used (no `processors=` line).

**Sizing for this machine.** Windows needs about 5-8 GB for itself, the editor and browsers: at the worst point Windows
keeps 31.8 - 24 = 7.8 GB, which is what held at 14:18 (Windows logs clean). Today Windows has only 3.9 GB free because the VM
sits on 11.4 GB of page cache; `gradual` returns that slowly and is right as it is (DEC-1038 (3), "recorded with it" (a)). The
legitimate working set is about 8 GB plus leads at 2-3.2 GB each plus a test run's 7 GB peak; the resource gate's forecast and
its 6.4 GB floor keep that under 24 GB. A lower cap would starve legitimate work; a higher one (26 GB) would leave Windows
5.8 GB and push it to page.

**What it would have done at 14:18.** It already did the one thing it can: the storm hit the 24 GB wall inside the VM and
stopped there; Windows was not harmed. It cannot stop the storm, only bound it. Options, costed:

| Option | Effect on 14:18 | Cost and risk | Needs |
|---|---|---|---|
| **1A. Keep 24GB / 8GB / gradual (recommended)** | none beyond today's | none | nothing |
| 1B. swap 8GB to 4GB | the VM would hit its wall about 4 GB of growth sooner (about 10 s at the storm's rate) and thrash for less time; the storm would still happen | a legitimate burst of 3-4 GB over RAM would be killed instead of slowed; swap use is 1.7 GB today | `wsl --shutdown`; changes DEC-1038 (3) (owner's) |
| 1C. at the RAM upgrade: `memory` = new RAM minus 8 GB, `swap` 8 GB | a bigger wall: a storm like this takes longer to hit it, so the guard (layer 2) matters more, not less | none beyond the restart | the upgrade's restart, as DEC-1038 (3) says |

**DEC-1038 (3).** Its condition ("no `.wslconfig` change before the RAM upgrade's planned restart") is untouched by 1A. Only 1B
would change it, and that is the owner's. I found no date for the RAM upgrade in the register or the orchestration files.

**The ACT (only if 1B or 1C is chosen).** `.wslconfig` is a Windows-side file, so by `class-rules.yaml` the `windows` hit makes it
class (O): the owner's own hands, not an operator bundle. Steps are in section 4. **Rollback:** copy the backup
`.wslconfig.bak-20261111` back over it and run `wsl --shutdown` again.

## 3. Layer 2: an early guard inside WSL

### 3.1 The four candidates

| | systemd-oomd | earlyoom | CTO script on `oom_watch.sh` | `mem_guard.py` (new, recommended) |
|---|---|---|---|---|
| Installed? | no (`/usr/lib/systemd/systemd-oomd` absent) | no | yes, but it exited (section 7) | not yet |
| Install | `apt` + `sudo`: class (O), refused to sessions | `apt` + `sudo`: same | none | none (tools lane) |
| Works on this failure? | **No.** It judges whole cgroups, and all our processes are in one, `init.scope`; acting there kills everything. It waits 20 s of pressure, the storm took about 42 s | **Partly.** `--prefer '(^|/)rg$'` would pick `rg`, but as I understand it (not installed, not tested) it kills one process per pass, and the storm made about 50 per second | **Alert only**, and every 30 s: at best one look during the storm | **Yes:** 1 s period, kills every `rg` in one pass |
| Names what to spare | cgroup settings | `--avoid` regex | whatever it is written to do | only `rg` is ever touched |
| Needs the owner for | sudo, install | sudo, install, a service | nothing | D1, D2 (section 6) |

### 3.2 The protection order, and what can and cannot be set

Tested today on a throwaway process (`tmp/adj_test.sh`): an ordinary user process **can raise** its own or its children's
`oom_score_adj` (up to 1000), **can lower it again only down to 0**, and **cannot go below 0** (refused). A child starts with
its parent's value. So "protect the servers with a negative value" needs root; without root the protection is relative:
mark the expendable ones high, leave the rest at 0.

| Process | Start line (RESTART-CLASSES) | `oom_score_adj` now | What is done without root | Only with the owner's `sudo` (later, optional) |
|---|---|---|---|---|
| shared embedding server :11434 (class 1) | `setsid -f nice -n 10 taskset -c 12-19 ollama serve` | 0 | left at 0 | `-500` |
| query embedding server :11435 (class 2) | wrapper `~/.local/bin/ollama` | 0 | left at 0 | `-500` |
| shared reranker (class 3) | started by a `gov retrieve` | 0 | left at 0 | `-500` |
| dispatcher | cron (`system.slice/cron.service`) | 0 | left at 0 | `-500` |
| sentinel (class 5) | `tmux new -d -s cto-sentinel ...` | 0 (its own user scope) | left at 0 | `-500` |
| the CTO's Claude session, leads | VS Code extension, dispatcher `claude -p` | 0 | left at 0 (a lead's 2-3 GB tree makes it the kernel's likelier pick than a 1 GB server) | `-300` for sessions |
| a lead's test run | `heavy_slot.sh` child | 0 | **optional:** `heavy_slot.sh` writes `600` to `/proc/self/oom_score_adj` before it runs the command (a CTO tool edit, tools lane) | none |
| `rg` (any of the three bundles) | the editor and extensions | 0 | **`mem_guard.py` sets 1000 on each** | none |
| editor and extension helpers | VS Code | 0 | **left alone**: the CTO's own session is a child of the extension host, and children inherit the parent's value, so raising the host would raise the session too | none |
| `dockerd`, `containerd` | systemd units | -500, -999 | already set by their units | none |

A `-500` for the servers is a new service per server or a command run after every start (a class (O) `sudo` step that the
recovery would have to repeat): **not proposed now.**

### 3.3 `mem_guard.py`: what it does

Source: `drafts/memory-protection/mem_guard.py` (about 250 lines, Python standard library only, one `/proc` pass of about
2 ms for today's 800 tasks). It is built on the same idea as `oom_watch.sh`, with `oom_watch.sh`'s inbox item format.

| Level | Trigger (`rg` = processes whose command and program file are both named `rg`, same user) | Action |
|---|---|---|
| 1 watch | more than 100 `rg`, or memory stall (PSI "full" avg10) above 1 % | one inbox item (P2), at most every 10 minutes, with each parent's pid, command and folder, and which `rg` binary |
| 2 mark | more than 150 `rg`, or 20+ `rg` with available memory under 5 GiB or stall above 5 % | every `rg` gets `oom_score_adj` 1000: if the kernel must kill, it picks an `rg` first |
| 3 stop | more than 300 `rg`, or 50+ `rg` with available memory under 3 GiB or stall above 20 % | SIGKILL every `rg` by pid (start time re-read just before each kill, so a reused pid is never hit); inbox item P1 with the parents. **Only when `MG_STOP=1`.** With `MG_STOP=0` it marks and alerts only |
| alert | available memory under 3 GiB with few `rg`, or any one program name with 400+ processes | inbox item P1 with the top memory users and per-name totals. **Nothing is killed** |

Settings are `MG_*` environment variables (every number above). A heartbeat file `log/mem-guard.alive` is touched every 10
s and every action is one line in `log/mem-guard.txt` (pids first 12, count, memory, stall). Thresholds sit far above normal
use (today 0 `rg`; a busy lead runs a handful). A false stop costs one search that is run again.

**What it deliberately does not do.** It does not stop the spawner. At 14:18 the parent is unknown (row 142 says "most likely the
editor side"); freezing the extension host would also freeze the CTO's own session, which is its child. The inbox item names
the parent, its folder, its command and the `rg` binary, so the CTO or the owner stops it by pid. A storm that continues at 50
per second is cut down every second; the memory held by `rg` stays under about 3 GB.

### 3.4 Replay of 14:18

Only one real number exists inside the storm (the 14:18:47 dump: 21.9 GB anonymous, 7.1 GB swap used, 2,161 `rg`). The growth
rate before it is **not recorded**, so the replay is modelled on explicit assumptions (`mem_guard.py --selftest`):

| Assumption | Guard trips | `rg` then | Available then |
|---|---|---|---|
| Storm from 14:18:05 (the dispatcher tick ended 14:18:14 normally) to 14:18:47: 51 `rg` per second, 16 GB available at the start | watch at +2 s, mark at +3 s, **stop at +6 s** | 102 / 154 / 308 | 15.0 / 14.5 / 13.0 GB |
| Slower: from 14:17:25 (the first kernel complaint), 26 per second | stop at about +12 s | about 310 | about 13 GB |

After the stop the storm, if its spawner keeps going, is cut every second: about 300 `rg` (3 GB) at most. **What would have
survived: everything**, the editor server, both embedders, the reranker, the sentinel, the CTO session, any lead. The kernel's
killer would never have run. The old tripwire (30 s period, alert only) would have written one inbox item at best.

**What it does not cover:** a storm of some other program (it alerts at 400 of one name, or at 3 GiB available, and leaves the
killing to the kernel), one big process growing (the same alert), and a machine too stalled for the guard to get CPU (not
tested; the guard is 11 MB and stays hot by running every second).

### 3.5 Rehearsal (done, live, no machine change)

`systemd-run --user --scope` works here (the user manager is running, the memory and pids controllers are delegated), and an
earlier probe by someone else (`gov-probe-cap-1`, 15:23) shows `MemoryMax` is enforced. I used scopes with no `MemoryMax` so no
kernel kill could occur and the CTO's watcher was not tripped:

1. **Scope limits** (`tmp/scope_inner.py`, scope `gov-rehearse-memprot-2`, `TasksMax=40`, `MemoryHigh=150M`): of 100 spawn
   attempts, 39 started and 61 were refused; a 400 MB hog was held at 157 MB with 275 MB pushed to swap; `oom_kill 0`.
   So a per-service task cap and memory cap would work here if the editor server were launched inside a scope (it is not; moving
   running processes out of `init.scope` was not tested and is not proposed).
2. **The guard against a planted storm** (`tmp/rehearse_inner.sh`, scope `gov-rehearse-memprot-4`, `TasksMax=300`, thresholds
   scaled to watch 20, mark 40, stop 60; report `tmp/rehearse-report.txt`, log `tmp/rehearse/guard.log`). Decoys were copies of
   `sleep` named `rg` (the storm), `claude` and `ollama` (to be spared), plus a 150 MB python hog.
   - Stop OFF, 70 `rg`: all 70 got `oom_score_adj` 1000; the `claude`, `ollama` decoys and the hog stayed at 0; the inbox got the
     "stop needed" item with parent pid, folder, command and the `rg` binary path.
   - Stop ON, 200 `rg` in about 1 s: 20 `rg` alive after (the rest killed by pid in 5 passes); `claude`, `ollama` and the hog
     alive; inbox item "rg-stopped" written.
3. The guard's `--once --dry-run` against the live machine: 0 `rg`, 17.2 GB available, level 0, 2 ms.

Defects seen in the rehearsal, none blocking: in the scaled test the "memory low" alert also fired because the test's 1 GB
limit is under the 3 GiB threshold (an artifact of scaling); the heartbeat is every 10 s so a guard that lives under 10 s writes
it once. Not tested: a real exhaustion (it would risk the machine).

### 3.6 Installing it (no ACT; the CTO's tools lane, DEC-979 (2))

```bash
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
cp $O/drafts/memory-protection/mem_guard.py $O/tools/mem_guard.py           # the CTO reviews it, commits it, syncs record/w2
python3 -I $O/tools/mem_guard.py --selftest                                  # expect all "ok"
cd $O && MG_STOP=1 setsid -f python3 -I tools/mem_guard.py >> log/mem-guard.out 2>&1 < /dev/null   # MG_STOP=1 only after D1
cat $O/log/mem-guard.alive; tail -3 $O/log/mem-guard.txt                      # alive within 10 s; "guard started"
```
**Check it is the only copy:** `ps -eo pid,args | grep 'tools/mem_guard.py' | grep -v grep` shows one line.
**Stop it (by pid, L-0075):** `bash $O/tools/proc.sh stop $(cut -d' ' -f3 $O/log/mem-guard.alive)`. **Rollback:** that, and delete
the tool. Nothing else is changed on the machine; its only effects are `oom_score_adj` writes and `SIGKILL`s on `rg` pids.

**Add it to restart class 4** (`RESTART-CLASSES.md`): the line above, and add `mem_guard` to the class's check
(`grep -E 'mem_sampler|kind_sampler|oom_watch|rerank_service_slot_hold|mem_guard'`), so the recovery restarts it every time (row
143's lesson).

## 4. Layer 3: the planned WSL restart (only if section 2's 1B or 1C is chosen, or at the RAM upgrade)

With 1A there is **no restart**: the guard is an ordinary program. This is the list for when there is one. A restart ends every
process: the CTO's and helpers' sessions, leads, both embedding servers, the reranker, the sentinel, watchers. Files survive.

**Before (CTO, about 10 minutes):**
1. `dispatch/status.txt` shows `leads running (0 ...)`, `heavy slots held: none`, `Jobs by phase: none`, no `log/act-in-progress.txt`.
2. `git status --short` clean on `w2/integrate`; `test ! -e .git/MERGE_HEAD && echo no merge in progress`.
3. Copy the servers' logs aside (RESTART-CLASSES rule 4): `cp ~/.ollama/serve-11434.log ~/.ollama/serve-11435.log $O/log/servers/` with the time in the names; `cp ~/.cache/gov-os/rerank.log $O/log/servers/rerank-<time>.log`.
4. `bash $O/tools/cto_checkpoint.sh "<next action>"`; write `log/cto-standby.txt` ("waits on the owner: WSL restart").
5. Tell the owner "ready"; the owner starts step 6.

**The owner's steps (Windows PowerShell, no administrator needed):**
6. Save work in the Windows editor; close it (the editor server dies with WSL anyway).
7. `Copy-Item "$env:USERPROFILE\.wslconfig" "$env:USERPROFILE\.wslconfig.bak-20261111"`
8. Edit `%USERPROFILE%\.wslconfig` to the chosen values (for 1B: `swap=4GB`; for 1C: `memory=<RAM-8>GB`).
9. `wsl --shutdown`
10. Wait 10 seconds, then `wsl -l -v`: `Ubuntu-24.04` shows `Stopped`.
11. `wsl -d Ubuntu-24.04` (this boots Linux; cron and docker start by themselves).
12. In that terminal: `free -b | head -2` (total about 25.2 GB for 24GB) and `grep SwapTotal /proc/meminfo` (4 GiB is 4194304 kB; 8 GiB is 8388608 kB).
13. Reopen the editor in the WSL folder (this starts the editor server and the Claude Code extension), then start the CTO's session with the w2-orchestrator prompt.
**Rollback:** the backup file copied back, then steps 9-13.

**After (CTO's recovery, in order; every start is logged in `log/restarts.jsonl`: time, class, reason, pid before and after, check):**
Let `O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator`.
- R1. Identity and bookkeeping: `cat $O/log/cto-session.txt` (register the new session id); `mv $O/log/cto-standby.txt $O/log/cto-standby.ended-HHMM.txt`.
- R2. The cap took effect: `free -b | head -2`; `grep -E 'MemTotal|SwapTotal' /proc/meminfo`; `systemctl is-system-running` (expect `running`).
- R3. Services that return alone: `crontab -l | grep -v '^#'` (the dispatcher's `run_tick.sh` line and the operator's line); `systemctl is-active cron docker`; `docker ps --format '{{.Names}} {{.Status}}'` (the two `asmo-*` containers, the owner's).
- R4. Class 1, the shared embedder: the RESTART-CLASSES class 1 commands (the log copy first, then `setsid -f nice -n 10 taskset -c 12-19 ... ollama serve`); check `taskset -cp $N; ps -o ni= -p $N` (12-19 and 10), `curl -s http://127.0.0.1:11434/api/ps` lists the model with `size_vram` > 0.
- R5. Class 2, the query embedder: `cat ~/.ollama/query-server-device` reads `gpu`; `cmp ~/.local/bin/ollama $O/tools/ollama_query_cpu_wrapper.sh`; GPU free at least 4096 MiB; then the class 2 start; check `grep -E 'offloaded [0-9]+/[0-9]+ layers' ~/.ollama/serve-11435.log | tail -1` shows 29/29, affinity 8-11.
- R6. `dispatch/status.txt` within a minute reads `layers: shared 29/29`, `layers: query 29/29`.
- R7. Class 3, the reranker: starts with the first search: `cd /home/usain/gov-os-worktrees/W2-00-store && GOV_RERANK_IDLE_S=43200 ~/.local/bin/gov retrieve "what decides a close" --json > /dev/null`; check `tail -2 ~/.cache/gov-os/rerank.log` shows `READY pid <n> device cuda:0`; a second search reports `rerank.by` = `service`.
- R8. Class 4, the watchers, one of each: the class 4 start lines (`mem_sampler.sh`, `kind_sampler.py --every 60`, `oom_watch.sh`, `rerank_service_slot_hold.py --watch`, **and `mem_guard.py`**); check `ps -eo pid,args | grep -E 'mem_sampler|kind_sampler|oom_watch|rerank_service_slot_hold|mem_guard' | grep -v grep` shows five; `tail -1 $O/log/oom-watch.txt` is a "watch started" line, not TRIPPED; `cat $O/log/mem-guard.alive` is under 10 s old.
- R9. Class 5, the sentinel: `tmux has-session -t cto-sentinel || <the step 3 line of MORNING-RESTART-2026-11-03.md>`; if it stops at the folder-trust prompt, the owner accepts (`tmux attach -t cto-sentinel`); check `log/deadman.log` has a new line within a few minutes and `dispatch/status.txt` says `sentinel: watched`.
- R10. The CTO's own waits (they were part of the dead session): re-arm `bash $O/tools/sentinel_check.sh` (while `dispatch/sentinel-expected` exists), `bash $O/tools/inbox_wait.sh` or `inbox_wait_quiet.sh`, `python3 $O/tools/helper_watch.py --every 300 --max 86400`, and any `wake_at.sh` timers the plan lists (for example the digests).
- R11. The inbox: `ls $O/dispatch/inbox` (the restart leaves "embedding server NOT RUNNING" and sentinel items); read each, move it to `inbox/read/`. A `sentinel-down` item: push the owner at once (standing rule).
- R12. The store: `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<a known question>"` answers (not `STORE_MISSING`) and its head matches `git -C /home/usain/gov-os-worktrees/W2-00-store rev-parse --short HEAD` (restarts.jsonl recorded `store bb9d29093` today).
- R13. The dispatcher: `tail -5 $O/dispatch/dispatch.log`; `dispatch/status.txt` timestamp under 2 minutes old, `inbox unread: 0`, `heavy slots held` empty, `leads running (0 ...)`. Any lead or run that was live at the shutdown is dead: compare `dispatch/started.txt` with the processes and restart those tickets by the plan.
- R14. In-session helpers died with the session: for each, check that its scratch output exists (`ls drafts/<name>`), re-run the ones that did not finish from their brief files.
- R15. The tree: `git status --short`, `git stash list` empty, no `.git/MERGE_HEAD`.
- R16. `/tmp` is empty of old slot locks (`ls /tmp/gov-os-heavy-slot-*.lock`); a heavy slot works: `bash $O/tools/heavy_slot.sh true`.
- R17. One line in the next digest: the restart, the `.wslconfig` change, and the check results.
Today's recovery (restarts.jsonl, 15:04-15:05) took about 35 minutes after WSL was back, mostly waiting for the CTO's session; the list above should take about 15.

## 5. The ACTs and decisions, by class (`class-rules.yaml`)

| Item | What | Class | Who runs it | Rollback |
|---|---|---|---|---|
| Guard tool `tools/mem_guard.py`, started by `setsid` | new CTO tool under `.gov-runtime/**` | none (row `cto-scratch`: O, not a control path; not an operator ACT) | the CTO, after its own review and commit (tools lane, DEC-979 (2)) | stop by pid, delete |
| `RESTART-CLASSES.md` class 4 line, `oom_watch.sh` fix, optional `heavy_slot.sh` line | repository files, ordinary commits | `unknown` (O, not control); the class-4 membership is the owner's approval (D2) | the CTO | revert the commit |
| `.wslconfig` edit (only 1B or 1C) | Windows file | (O): the `windows` hit; not expressible as an operator bundle | the owner, PowerShell, section 4 | backup file back, `wsl --shutdown` |
| `wsl --shutdown` | restart | (O): the owner's (RESTART-CLASSES "What stays an ACT") | the owner | n/a |
| `apt install systemd-oomd` or `earlyoom`; negative `oom_score_adj`; `vm.min_free_kbytes` | installs, sudo | (O), and `sudo` is refused to every session | the owner's terminal only | `apt remove`; reboot clears the rest |
| Editor settings (done 15:24:47) | `~/.vscode-server/data/Machine/settings.json` | `unknown` (O) | the owner | restore the file |

## 6. Proposed decisions (the CTO records; the owner decides)

- **D1: `rg` may be stopped by program name, by the guard only (recommend yes).** DEC-1073 (4) says every stop is by pid or
  process group "never a name match". The guard picks pids from `/proc` (command name and program file both `rg`, same user,
  start time re-read) and kills only those pids, but the choice of set is by name. Without D1, run with `MG_STOP=0`: it
  marks and alerts, the kernel does the killing. Confidence: medium-high that D1 is safe (an `rg` is cheap to rerun).
- **D2: add `mem_guard.py` to restart class 4** so every recovery restarts it (recommend yes).
- **D3: leave `swap` at 8 GB and `.wslconfig` unchanged now (recommend yes).** DEC-1038 (3) then stands as written.

## 7. Discoveries that need the CTO now

1. **`oom_watch.sh` is not running.** It tripped at 15:23:34 ("OOM lines 4") and, as written, exits after a trip. The 4 lines
   were a memory-cgroup kill inside someone's scope test (`gov-probe-cap-1`, 15:23:22: `constraint=CONSTRAINT_MEMCG`), not a
   real machine out-of-memory. Its test `grep -ci "out of memory\|oom-kill\|oom_reaper"` counts any such line. So the rg
   tripwire written under DEC-1132 (3) (a) lasted 3 minutes and is **off now**; `gate-config.json`'s floor was also rewritten
   (it already held the same value). Fix (CTO's tool): count only machine-wide kills and keep running:
   ```
   - ooms=$(journalctl -k --since "$START" --no-pager 2>/dev/null | grep -ci "out of memory\|oom-kill\|oom_reaper")
   + ooms=$(journalctl -k --since "$START" --no-pager 2>/dev/null | grep -ci "oom-kill:constraint=CONSTRAINT_NONE")
   ```
   and replace `exit 0` after a trip by re-arming after 10 minutes. Restart it per class 4 after the fix. **Anyone testing
   `MemoryMax` scopes trips it again.**
2. **No samples for 14:18** (row 143: the sampler was down since the 11-10 21:52 restart; now fixed). The growth rate of the storm is
   unknown, so the replay is a model. The guard writes a line for every level change, so the next one is on record.
3. **The spawner is still unknown.** Three `rg` bundles exist (VS Code's own search, the OpenAI extension's two). The inbox item
   names the binary and the parent, which settles it the next time. The editor settings written at 15:24 cover VS Code's own
   search only, not the OpenAI extension's.
4. **The kernel's choice is by size:** with all processes at 0, a memory shortage kills the biggest single process first: a lead's
   test run or the reranker before an `rg`. Only root can change that (section 3.2).
5. **This session itself is in `init.scope`.** Nothing but the sentinel's tmux scope and cron have their own cgroup, so no
   per-service memory or task cap exists. The scope rehearsal shows it would work if the editor server were launched inside one.

## 8. Files

- `mem_guard.py` (the guard, with `--selftest`, `--once`, `--dry-run`)
- `tmp/parse_tasks.py`, `tmp/sums.py` (parse the 14:19:10 task table from `tmp/kern-b1.txt`, the saved kernel log)
- `tmp/adj_test.sh` (the `oom_score_adj` rules), `tmp/scope_inner.py` (scope limits), `tmp/rehearse_inner.sh`, `tmp/rehearse-report.txt`,
  `tmp/rehearse/guard.log` and `tmp/rehearse/inbox/` (the guard rehearsal)
- `du -sh` of `tmp/`: under 1 MB, 30 files and folders.
