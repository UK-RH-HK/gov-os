# ACT-NIGHTLY-RESTART-1: the nightly back, in the quiet hours, nothing else running, sized to memory (DEC-1132 (4))

Read `LIFT-common.md` first (scratch only; never edit the crontab, the nightly or any committed tool). Role:
ACT-preparation helper, Sonnet high, class C2 (DEC-1120). Scratch folder:
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/nightly-act/` (temporary files and any
clone under its `tmp/`, removed when done). Save the package early and extend it.

## Context
The nightly full run (`governance/project/orchestration/nightly/nightly.sh`; `crontab -l` shows its line commented by
DEC-1049) has been stopped with no ticket or date (SWITCHED-OFF-1 §3). D-10 runs 1 and 2 (11-10) were day-mode full runs:
`log/nightly/history.jsonl` and `log/nightly/digest.txt` give their durations and counts (run 2: parallel 1113 s, serial
1382 s, 9,612 + 134 passed). On 11-11 at 14:19 WSL ran out of memory (2,161 `rg` processes, 19.3 GB; DECIDED-NOT-DONE row
142; the machine: 23.5 GB RAM, 8 GB swap, 20 CPUs). The owner wants the nightly back after the lift's closes: in the quiet
hours (02:00-07:30 UTC), with nothing else running, sized to memory so it cannot exhaust it.

## Build `ACT-NIGHTLY-RESTART-1.md` with its bundle in the operator's form
1. **When and what:** the cron line (the time inside the quiet hours that fits the measured duration with margin), the
   command, day or night mode, the `lifted` and opt-in groups per DEC-1061 / D4-LIST (read them), and what it reports
   (DEC-852 (3), DEC-880: the digest's line).
2. **Nothing else running:** how it waits or refuses if a lead, a heavy slot, a rebuild, an ACT or a memory measure runs
   (the dispatcher's status and slots, `log/act-in-progress.txt`, `NIGHTLY-RUNNING` holds the dispatcher G9 already
   reads?): find what exists and use it; say what is missing.
3. **Sized to memory:** the worker count from measured peaks (per-worker RSS from the D-10 runs if recorded,
   `dispatch/peaks.json`, `phase-peaks.json`), with a hard cap: a systemd-run scope or cgroup `MemoryMax` (or `ulimit
   -v` if no systemd user scope) below available memory minus the floor (3 GB), so the kernel kills the run, not the
   machine; and the `rg`/process tripwire. Say exactly how the limit is applied and tested.
4. **The class** by `governance/project/operator/class-rules.yaml` (a crontab line is an ACT: which class), the owner's
   commands, the rollback (the line commented again), and a rehearsal: a short dry run of the wrapper under the memory cap
   with a planted memory hog proving the cap kills the hog and leaves the session and the servers alive; the wrapper's
   refusal when a planted lead/slot is running.
Return the twelve fields, short; the files; the rehearsal count. Estimate 1.5 h.
