# The maintenance window's package: memory protection in two more layers (the owner's message, 11-11 ~15:30)

Read `LIFT-common.md` first (scratch only; change nothing on the machine: no `.wslconfig`, no systemd unit, no install,
no kill). Role: ACT-preparation helper, Sonnet high, class C2 (DEC-1120). Scratch folder:
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/memory-protection/` (temporary files in
its `tmp/`). Save `MEMORY-PROTECTION-1.md` early and extend it. Never open `~/gov-os-eval/` or `~/gov-os-runs/`.

## What happened (DECIDED-NOT-DONE rows 142-143; `journalctl -b -1 -k`, read-only)
At 14:18:47-14:19:10 UTC on 11-11 the kernel ran out of memory: 2,161 `rg` processes held 19.3 GB RSS + 1.1 GB swap of
20.7 GB; it killed the VS Code server's main thread (pid 1267) at 14:19:10 and 14:21:55, and systemd killed `init.scope`
at 14:23:30 (22.5 GB peak, 7.8 GB swap peak); WSL came back at 14:30. The resource gate (W2-20) controls only what Gov OS
launches, so the storm went past it. The machine: `free -b`, `nproc`, `/proc/meminfo`, the Windows host's RAM
(`powershell.exe -NoProfile -Command "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory"`, read-only), the current
`.wslconfig` (`/mnt/c/Users/usain/.wslconfig`, read only; it may not exist) and DEC-1038 (3) ("`.wslconfig` not before the
RAM upgrade") and RESTART-CLASSES.md's "What stays an ACT" (a WSL restart is the owner's).

## Two layers, each with: what it is, the exact config, what it would have done at 14:18, its risks, the ACT
1. **A memory and swap cap for WSL** (`.wslconfig`: `memory=`, `swap=`, and anything else that matters, e.g.
   `autoMemoryReclaim`), sized to this machine: leave Windows enough, keep today's working set (the embedding servers,
   the reranker, a lead's peak 2-3.2 GB, the dispatcher's limits in `dispatch/limits.json`, `machine.json`). Note DEC-1038
   (3)'s condition and whether this package changes it (the owner's). What a cap does when hit (the VM's own OOM, not
   Windows').
2. **An early guard inside WSL** that stops a runaway process before memory is exhausted, **never a Gov OS session or
   server first**: compare `systemd-oomd` (with a user slice and `ManagedOOMMemoryPressure`), `earlyoom` (is it installed?
   an install is an ACT), and a CTO script built on `oom_watch.sh` (`tools/oom_watch.sh`, which now has an rg tripwire,
   alert only). The protection order: `oom_score_adj` for the embedding servers, the reranker, the dispatcher, the
   sentinel, the CTO's Claude session and launched leads (how to set it for each, from their committed start lines in
   `RESTART-CLASSES.md`), and an avoid/prefer list (`rg` and editor helpers preferred to be killed). Threshold, check
   period, logging, the inbox item. Replay 14:18 against it: at what moment would it have acted, on which pids, and what
   would have survived.
3. **The planned WSL restart** (`wsl --shutdown` from Windows applies `.wslconfig`): the owner's steps, and the CTO's
   recovery after it, step by step, from today's recovery (RESTART-CLASSES classes 1-5, the CTO's watchers, the digests,
   the inbox, the store, the dispatcher's cron, the helpers): a numbered checklist with each check's command.
4. The ACT(s): class by `governance/project/operator/class-rules.yaml`, the owner's commands, the rollback, and a
   rehearsal where one is possible without changing the machine (e.g. the guard script against a planted memory hog in a
   `systemd-run --user --scope -p MemoryMax=` test scope, if systemd user scopes work here; say if not).
Plain language for the owner. Return the twelve fields, short. Estimate 2 h.
