# Restarts approved by class — the CTO's proposal for the owner (DEC-1052 O-6; D-3 item 12)

DEC-1052 decided that restarts of the repository's own servers from committed configs are approved by class, with no
ACT. This file proposes the classes. Each class names the server, the committed source its restart must follow, when it
may be restarted, the commands, and the check after. If the owner approves a class, its name goes into
DECISIONS-IN-FORCE's section "Approved restarts by class" with this file's commit. Until then every restart is an ACT.

**Basis (DEC-1052):** question 4 (fewer approvals: 8 ACTs on 2 Nov, most of them for this machinery) and question 2
(a restart from the committed config, with its check, loses no work; a search that runs during the restart fails once
and is run again).

## The rules for every class
1. **Only a restart:** the same binary, the same CPUs, nice level, device, model and log, from the committed source
   named in the class. Anything else (other CPUs, the device, another model, a new flag, an edit of the source) is a
   re-configuration and stays an ACT.
2. **Only for a reason:** the server is down; the dispatcher reports it HUNG or NOT RUNNING (`dispatch/status.txt`,
   `inbox-stale.txt`); it lost the GPU (a 0-layer or partial load, DEC-1030); it runs on other CPUs than its class
   says; or WSL or the machine was restarted.
3. **A quiet minute:** `dispatch/status.txt` shows `heavy slots held: none` and `Jobs by phase: none` (no rebuild, test
   run or memory measure), and no ACT is in progress on the same server (`log/act-in-progress.txt`).
4. **The old log first:** copy the server's log into `.gov-runtime/scratch/orchestrator/log/servers/` with the time
   in its name before the restart, because some of the start commands empty the log, and it holds the crash that
   `tools/server_log_scan.py` reports (DEC-1030).
5. **Once per incident:** if the check fails, or the same server needs a second restart within an hour, stop. Send the
   owner a P1 with a ping, because memory waits on it (R-11). Do not try a third time.
6. **Recorded:** one line in `log/restarts.jsonl` (time, class, reason, pid before and after, the check's result),
   listed in the next digest. The basis's symptom trigger (DEC-1052) reads it: repeated restarts are assessed.

## Class 1 — the shared embedding server, 127.0.0.1:11434
- **Source (committed):** `governance/project/orchestration/packages/ACT-OLLAMA-CAP-1.md` ("The cap", steps 2-6) and
  `governance/project/orchestration/MORNING-RESTART-2026-11-03.md` step 1: `/home/usain/.local/ollama/bin/ollama
  serve` on CPUs 12-19 at nice 10, on the GPU, log `~/.ollama/serve-11434.log`, model `qwen3-embedding:0.6b` pinned.
- **Commands:**
  ```bash
  PID=$(ss -ltnp | grep ':11434 ' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2)
  [ -n "$PID" ] && { tr '\0' ' ' < /proc/$PID/cmdline; echo; kill $PID; for i in $(seq 1 40); do ss -ltn | grep -q ':11434 ' || break; sleep 0.5; done; }
  ss -ltn | grep -q ':11434 ' || setsid -f nice -n 10 taskset -c 12-19 /home/usain/.local/ollama/bin/ollama serve > /home/usain/.ollama/serve-11434.log 2>&1 < /dev/null
  sleep 5; curl -s -m 120 http://127.0.0.1:11434/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm","keep_alive":-1}' | head -c 60; echo
  ```
  If something restarted it without its caps in the gap (the new pid's affinity is not 12-19, or the log says the
  address is in use), stop that one and repeat the start once (ACT-OLLAMA-CAP-1 step 4).
- **Check:** `N=$(ss -ltnp | grep ':11434 ' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2); taskset -cp $N; ps -o ni= -p $N`
  shows 12-19 and 10, also for its `llama-server` child; `curl -s http://127.0.0.1:11434/api/ps` lists the model with
  `size_vram` > 0; within a minute `dispatch/status.txt` reads `layers: shared 29/29`.

## Class 2 — the query embedding server, 127.0.0.1:11435
- **Source (committed):** `packages/ACT-QUERY-GPU-2.md` (steps 1-5) and `MORNING-RESTART-2026-11-03.md` step 2. It
  starts through the wrapper `~/.local/bin/ollama` (its source `.gov-runtime/scratch/orchestrator/tools/
  ollama_query_cpu_wrapper.sh`, committed on `record/w2` under `governance/project/orchestration/main/orchestrator/
  tools/`): the GPU, CPUs 8-11, nice 0, log `~/.ollama/serve-11435.log`, the device read from
  `~/.ollama/query-server-device`.
- **Before:** `cat ~/.ollama/query-server-device` reads `gpu`, and the restart never writes that file: a change of
  device is an ACT (ACT-QUERY-GPU-2's undo included). `cmp ~/.local/bin/ollama
  .gov-runtime/scratch/orchestrator/tools/ollama_query_cpu_wrapper.sh` is silent: if not, stop (the wrapper is under
  `~/.local/bin`, so changing it is an ACT). GPU memory free at least 4096 MiB
  (`/usr/lib/wsl/lib/nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits`), or stop.
- **Commands:**
  ```bash
  Q=$(ss -ltnp | grep ':11435 ' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2)
  [ -n "$Q" ] && { tr '\0' ' ' < /proc/$Q/cmdline; echo; kill $Q; sleep 3; }
  ss -ltn | grep -q ':11435 ' || OLLAMA_HOST=127.0.0.1:11435 setsid -f ~/.local/bin/ollama serve < /dev/null
  sleep 5; curl -s -m 120 http://127.0.0.1:11435/api/embed -d '{"model":"qwen3-embedding:0.6b","input":"warm","keep_alive":-1}' | head -c 60; echo
  ```
- **Check (ACT-QUERY-GPU-2 step 5):** `grep -E 'offloaded [0-9]+/[0-9]+ layers' ~/.ollama/serve-11435.log | tail -1`
  shows 29/29; the pid's affinity 8-11 and `tr '\0' '\n' < /proc/$N/environ | grep -c '^CUDA_VISIBLE_DEVICES=-1$'`
  prints 0; three two-text questions under 0.5 s each; `dispatch/status.txt` reads `layers: query 29/29`.

## Class 3 — the shared reranker service (W2-112)
- **Source (committed):** the pinned gov's `gov/retrieval/rerank_service.py` (W2-112's code, `pin-9894b0cf`), started
  by a search through `gov/retrieval/rerank.py`; socket, start lock and log in `~/.cache/gov-os/` (`rerank.sock`,
  `rerank.lock`, `rerank.log`). The interim GPU-slot module (`gov-reranker-gpu-slot.pth`, ACT-RERANK-GPU-SLOTS-1 and
  ACT-RERANK-WAIT-1) stays as it is.
- **Before:** the slot watcher runs (class 4; DEC-1043 (2): no private reranker beside the service); the GPU has at
  least the service's share and headroom free (3.5 + 2 GiB; the service refuses itself otherwise, `REFUSED` in
  `rerank.log`).
- **Commands:**
  ```bash
  T=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/tree_busy.sh
  for P in $(bash $T --cmd rerank_service.py | awk '/^BUSY/{print $2}'); do kill -TERM $P; done
  # the force-stop (DEC-1068 (f)): a service still alive 30 s after SIGTERM (e.g. stuck in a CUDA call) gets SIGKILL
  for i in $(seq 1 15); do bash $T --cmd rerank_service.py | grep -q '^BUSY' || break; sleep 2; done
  for P in $(bash $T --cmd rerank_service.py | awk '/^BUSY/{print $2}'); do kill -KILL $P; done; sleep 3
  cd /home/usain/gov-os-worktrees/W2-00-store && GOV_RERANK_IDLE_S=43200 ~/.local/bin/gov retrieve "what decides a close" --json > /dev/null
  ```
  (`GOV_RERANK_IDLE_S=43200` keeps it for 12 hours with no search, as the owner kept it on 2026-11-03. The service
  inherits the setting from the search that starts it; the 13:45 start's exact command line is not on record, so this
  line is the proposed form.)
- **Check:** `tail -2 ~/.cache/gov-os/rerank.log` shows `READY pid <n> device cuda:0` and no `END` or `REFUSED` after
  it; a second `gov retrieve "<question>" --json` from `~/gov-os-worktrees/W2-00-store` gives `rerank.by` = `service`;
  the GPU's used memory stays under its budget (14,255 MiB; `dispatch/status.txt`'s `GPU rule` line).
- **Not in this class:** the service's code or model changing (a re-pin, an ACT); a private reranker; the service on
  the CPU (never).

## Class 4 — the CTO's watchers and samplers
- **Source (committed):** the scripts in `.gov-runtime/scratch/orchestrator/tools/`, each matching its last copy on
  `record/w2` (`governance/project/orchestration/main/orchestrator/tools/<name>`), started as
  `MORNING-RESTART-2026-11-03.md` step 4 says: `mem_sampler.sh`, `kind_sampler.py --every 60`, `oom_watch.sh`,
  `rerank_service_slot_hold.py --watch`.
- **Before:** `git -C /home/usain/Dynamic-Agentic-Engineering-OS show record/w2:governance/project/orchestration/main/orchestrator/tools/<name> | cmp - .gov-runtime/scratch/orchestrator/tools/<name>`
  is silent. If it is not, sync first (`sync_context.py --commit`), or say why the two copies differ.
- **Commands:** the matching line of step 4, for the one that stopped:
  ```bash
  O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
  cd /home/usain/Dynamic-Agentic-Engineering-OS && setsid -f bash $O/tools/mem_sampler.sh > /dev/null 2>&1 < /dev/null
  cd $O && setsid -f python3 tools/kind_sampler.py --every 60 > /dev/null 2>&1 < /dev/null
  cd $O/tools && setsid -f bash oom_watch.sh > /dev/null 2>&1 < /dev/null
  cd $O && setsid -f python3 tools/rerank_service_slot_hold.py --watch >> log/rerank-slot-hold.log 2>&1 < /dev/null
  ```
- **Check:** exactly one process of each (`ps -eo pid,args | grep -E 'mem_sampler|kind_sampler|oom_watch|rerank_service_slot_hold' | grep -v grep`);
  a second copy is stopped, the older one first. While a service runs, the slot watcher holds the other GPU slot
  (`dispatch/status.txt`'s rerankers line).
- **Not needed:** your session's own background waits (`tools/inbox_wait_quiet.sh`, `tools/wake_at.sh`). They are
  part of your session, not a server.

## Class 5 — the sentinel (O-5's one net), tmux `cto-sentinel`
- **Source (committed):** `governance/project/orchestration/tools/sentinel-brief.md` and `tools/deadman.py`
  (ACT-SENTINEL-1); the start line of `MORNING-RESTART-2026-11-03.md` step 3.
- **When:** after a WSL restart, or when the dispatcher's stale line says `sentinel:` (no heartbeat for 2 hours) and
  `tmux has-session -t cto-sentinel` fails.
- **Commands:** step 3's `tmux new -d -s cto-sentinel '…'` line, unchanged.
- **Check:** `log/deadman.log` gets a new line within a few minutes; `dispatch/status.txt` reads `sentinel: watched`.
  If Claude Code stops at its folder-trust prompt, accepting it is the owner's (`tmux attach -t cto-sentinel`). The
  restart stays approved, but that step needs a ping (work waits on the owner).

## What stays an ACT (DEC-1038 (1), scoped by O-6)
- Any install: packages (pip, apt, npm), a new Ollama model (`ollama pull`), a new tool in the reranker environment.
- A new service, or any change to how an existing one runs: CPUs, nice, the device (`~/.ollama/query-server-device`),
  the model, flags, environment, its unit or wrapper.
- Crontab lines: the dispatcher's, the nightly's (commented by DEC-1049), the runs sweep's (commented by DEC-1050).
- `.wslconfig` (not before the RAM upgrade, DEC-1038 (3)); a WSL or machine restart (the owner's).
- `~/.local/bin`: the pinned gov (a re-pin, a rollback beyond DEC-1037 (1)'s instant one inside a re-pin window), the
  `ollama` wrapper, `owner-ping`.
- `~/.local/share` (the pins, the reranker environment, `gov-reranker-gpu-slot.pth`), `~/.config`, other `~/.ollama`
  files, environment files.
- `.claude/` settings and hooks (Claude Code's own safety check asks for these anyway).
- Anything that needs `sudo`.

## Not a machine change at all (no class and no ACT needed)
Edits inside the repository and its scratch, such as the dispatcher's `dispatch/config.json`, the CTO's tools, and
`log/` and `drafts/`. These follow the ordinary rules: commits, the tools lane (DEC-979 (2)), and the basis.
