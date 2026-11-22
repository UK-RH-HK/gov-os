# Lead brief: W2-207, the run-time tool's slice 4, built and green on its branch (the live cut-over is the CTO's, by day, after 0.1.5)

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it. Name: `w2-207-runtime`; worktree
`/home/usain/gov-os-worktrees/E2-w2-207-runtime`, branch `e2/w2-207-runtime` from `w2/integrate`. **Do not merge, and
do not touch the live machine:** no crontab edit, no change to `~/.gov-os/`, no change to the scratch tools under
`.gov-runtime/scratch/orchestrator/tools/` or `governance/project/orchestration/tools/dispatch/`, no hook registered in
the main tree's settings. Everything is built and proved on the branch, against planted machines and scratch homes; the
CTO runs the cut-over steps by day after release 0.1.5. Built and green by tomorrow, 2026-11-23. Every helper Sonnet.

**The ticket:** W2-207, `.tickets/DAEO-rt4s.md` (read it whole: KPI lines RT-1, RT-3, RT-5, RT-6, RT-7, D8, F1 and its
order of the cut-over). EMERGENCY-2 §6.3 (RT-1 to RT-8). Audit 3 of 2026-11-17 and slices 1 to 3 (W2-205 and earlier)
built the pieces; read `docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md` §6 fix 19 (the scratch dispatcher, two
watchers, slots from constants).

## The owner's words for the dispatcher and the load balancer (2026-11-22), new KPI lines you add to the ticket
"The dispatcher and load balancer must be agnostic of the machine they run on, well designed and scoped: on any machine
they read its capacity (CPU, memory, GPU, disk) and size the work to it, so the work stays within limits here and on any
machine it is hosted on later; on a machine too small to operate, they refuse with an error that says why. Test it
against small and large machines."
- **MA-1 Capacity read, never assumed.** At start and on each pass the tool reads the machine: logical CPUs (and the
  cgroup/affinity limit if lower), total and available memory (and the cgroup memory limit), GPU presence, model and free
  VRAM (none is a valid answer), free disk and free inodes on the work filesystems. No machine-specific constant remains
  in the dispatcher, the slots or the load gate (today: `heavy_slots.conf`'s 3, the gate of 20, the load ceiling of 12,
  `mem_guard`'s figures): each limit is a rule over the reading (for example slots = f(CPUs, memory), the load gate =
  f(CPUs)), its formula in one committed config with the owner's current values reproduced on this machine.
- **MA-2 Work sized to it.** Leads, test slots and `-n auto` workers admitted from the reading; the GPU embedders never
  spill (RT-4; DEC-1158 (3)): GPU work admitted only while free VRAM covers it; a machine with no GPU runs no embedder
  and says so (no CPU fallback, DEC-1065), memory search then FTS-only and named.
- **MA-3 Too small: refuse, saying why.** Below a floor (for example fewer than 4 CPUs, under 8 GB memory, under a disk
  or inode floor), the tool refuses to start work with one error naming each resource short, its reading and its floor
  (for example `RUNTIME_MACHINE_TOO_SMALL: memory 6.0 GB < 8 GB; free disk 3 GB < 10 GB`).
- **MA-4 Proved on small and large machines.** The reading is injectable; tests run planted profiles at least: a 2-CPU
  4 GB no-GPU laptop (refused, named), a 4-CPU 8 GB no-GPU machine (one lead, one slot, FTS-only named), this machine
  (20 CPUs, 24 GB, a 16 GB GPU: today's limits reproduced), a 64-CPU 256 GB two-GPU server (more slots, no constant
  capping it), and a cgroup-limited container (the cgroup limit wins over the host's figures).
- **MA-5 The embedders come back.** After a machine restart the shared embedding servers (ports 11434, 11435) were down
  and nothing started them (2026-11-22: memory fell to FTS-only until the CTO ran `gov.retrieval.ollama.safe_restart`).
  The pass checks them and starts a down server under its cap through `safe_restart` (never a running or foreign one),
  once per pass, recorded; on a machine with no GPU, MA-2 holds.

## The flow and green
Write MA-1 to MA-5 into the ticket's KPIs (the CTO approves them by this brief), each with its verify and a failure
line. Test designer (Sonnet) writes the acceptance tests, red on the base; engineer (Sonnet) to `gov accept W2-207`
green. Return: branch and head; each KPI line with its tests; the cut-over steps as an ordered runbook for the CTO
(exact commands, the check after each, the rollback of each), with F1's order; reds not yours; the trial figures.
If RT-1 across tickets runs long, split it as the ticket's own note allows and say so.
