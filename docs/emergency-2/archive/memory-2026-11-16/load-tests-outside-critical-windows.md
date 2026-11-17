---
name: load-tests-outside-critical-windows
description: "a ticket whose KPIs need loaded runs (load 20/50+, burn.py) gets its load window named in the brief, outside critical-path work, and the CTO opens it"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-15T02:10:07.067Z
---

On 2026-11-15 at about 02:00, W2-111's lead started `burn.py 22 1500` (22 processes, 25 min) for its load-20/50+ KPIs. That shut the machine's resource gate (load about 48 against nproc 20) and blocked W2-88's last workers, on EXAMIN's critical path for release 0.1.0. I asked the lead to stop it and moved the loaded runs to after the re-pin.

**Why:** a deliberate load generator takes the whole machine. Critical-path work never waits (DEC-1157), and the gate refuses every start while the load is up.

**How to apply:** every brief for a ticket with loaded-run KPIs says "no load generator until the CTO opens the load window". The CTO opens it only when no critical-path lead, land, release step or nightly needs the gate. Related: [[gate-refusal-is-a-wait]], [[dec-1157-no-holds]].

**For a lead (merged from [[load-window-before-burn]], the W2-111 lead's note of the same night):** ask the CTO for a load window by SendMessage, saying how long, and do only quiet runs until then. Keep burners in their own process group with a self-ending limit, and stop them by -pgid through proc.sh. A lead cannot see which other tickets are on the critical path; the gate is shared. Related: [[waits-by-pid-only]].

**Memory files are never removed from Bash:** the guard refuses an `rm` outside the project as a catastrophic delete (DEC-953 item 2; refused 11-15 02:10). A duplicate stays, marked merged in the index.
