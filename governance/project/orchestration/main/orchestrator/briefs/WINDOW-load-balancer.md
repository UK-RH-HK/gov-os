# The maintenance window's package: W2-20's resource gate since the re-pin, its bypasses, and its re-measure (the owner's message, 11-11 ~15:30)

Read `LIFT-common.md` first (scratch only; read-only elsewhere: change no config, start no lead, run no sample day yet).
Role: research helper, Sonnet high, class C2 (DEC-1120). Scratch folder:
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/load-balancer/`. Save `LOAD-BALANCER-1.md`
early and extend it. Never open `~/gov-os-eval/` or `~/gov-os-runs/`.

## Answer
1. **Is W2-20's resource gate live since the re-pin** (pin-797495bdfc70, 13:31 UTC 11-11)? Evidence: `gov resources`
   (the pinned gov; its help and a read-only status call), `src/gov/launch/` (where `gov launch` calls the gate), the gate's
   config and state files, any gate decision logged since 13:31 (the W2-170 lead started 15:18 by the dispatcher: did it go
   through the gate?).
2. **What goes through it and what bypasses it:** `gov launch`; the dispatcher (`governance/project/orchestration/tools/dispatch/
   dispatcher.py`, `dispatch/launch_now.sh`: it launches `claude -p` directly, with its own forecast admission); the CTO's
   `tools/launch_worker.sh` (calls `gov launch`?); the CTO's in-session helpers (Agent tool subagents: inside the CTO's own
   process); the editor (VS Code, its extensions, ripgrep); test runs (`heavy_slot.sh`, `gov accept`, pytest); rebuilds; the
   operator agent. A table: path, gated (yes/no/partly), by which code line.
3. **How to bring each bypass under it,** with a recommendation and its cost: e.g. the dispatcher's launches through `gov
   launch`; helpers counted by a heartbeat or launched as workers; test runs inside the heavy slot always; the editor and other
   processes only by a machine-level cap (that is the other package, MEMORY-PROTECTION-1).
4. **The sample day and `--remeasure` (DEC-1105):** read DEC-1105 and W2-20's ticket (`.tickets/DAEO-r30l.md`, S19 and the
   remeasure lines); say exactly what "the sample day" is (how long, what it records, who runs it, where the output goes),
   what `--remeasure` changes (which file, which value: the working size of a lead), the measured lead peak today
   (`dispatch/peaks.json`: p95 2026 MB, max 3244 MB at 2026-11-09 22:32; `log/lead-mem.jsonl`), whether running them is a
   config change that needs an ACT or is DEC-1105's own permission, and the exact commands, so the CTO can run them in the
   window. Do not run them.
Plain language for the owner. Return the twelve fields, short. Estimate 1.5 h.
