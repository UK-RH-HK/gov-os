---
id: DAEO-tgk2
status: in_progress
deps: []
links: []
created: 2026-10-29T15:55:50Z
type: task
priority: 1
assignee: engineer
external-ref: W2-76
tags: [wave-2, implementation, standard, rebuild]
wbs_id: W2-76
title: 'gov rebuild: per-stage timings, a 30-minute watchdog that records what it waits on, and one rebuild at a time on the machine'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/rebuild/**
- tests/unit/rebuild/test_w2_76*
- tests/conftest.py
- tests/acceptance/W1-07/w1_07_support.py
- tests/acceptance/W1-27/w1_27_support.py
- tests/acceptance/W1-27/test_w1_27_rebuild_r8_no_embeddings.py
- tests/acceptance/W1-30/w1_30_support.py
- tests/acceptance/W1-41/w1_41_support.py
- tests/acceptance/W2-50/w2_50_support.py
- tests/acceptance/W2-54/w2_54_support.py
- tests/acceptance/W2-69/w2_69_support.py
kpis:
  success:
  - 'gov rebuild''s output and record give the time of each stage (the lexical, semantic and code-index stores, the secrets filter where it runs, the compaction), not the lexical stage alone [DEC-939 item 2, row W2-L451]'
  - 'A rebuild that passes 30 minutes (a value the project may set) writes, and keeps updating while it runs, a record of the stages done with their times and of each of its processes'' state and wait channel and the load, flags itself as slow in its output, and goes on to the end: the watchdog never stops or fails a rebuild [DEC-939 item 2]'
  - 'One store rebuild at a time on the machine: every gov rebuild, in every session on this machine (the main tree, a worktree, a clone, sandboxed or not), takes one machine-wide rebuild lock. A rebuild that waits for it says what it waits for, and records the wait apart from its own stages [DEC-939 item 2, row W2-M408]'
  - 'Fail closed: a lock it cannot create or take is never ignored; the rebuild waits, or refuses with the reason, and never runs beside another unannounced [DEC-866]'
  - 'Everything a rebuild builds is unchanged: the same stores, the same digest on the same tree [DEC-889]'
  failure:
  - Two rebuilds running at once on the machine; a rebuild stopped by the watchdog; a slow rebuild with no record; a stage's time missing.
profile: STANDARD
sources:
- DEC-939
- DEC-889
- DEC-866
- DEC-898
est_loc: 80
acceptance_tests:
  path: tests/acceptance/W2-76/
  author: independent-test-designer (MR-3); written before implementation
track: A
list_rows: [W2-M408, W2-L451]
---
# W2-76 gov rebuild: per-stage timings, a 30-minute watchdog, one rebuild at a time on the machine

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-76), from P1-MORNING-2026-10-29 item 2 (owner, DEC-939 item 2).

- **Why:**
  - On 2026-10-29 a main-tree rebuild took 6 h 39 min (04:10 to 10:49), against about 5 minutes on a quiet machine, while W2-68's lead rebuilt its own stores. Its output timed only the lexical stage.
  - The timed re-run at 12:23 took 271 s, with Ollama answering. No memory pressure or hung task was logged. The likeliest cause is concurrent rebuilds contending for the code-graph daemon or gitleaks.
- **Until it lands:** the orchestrator's rebuilds run through `tools/rebuild_diag.sh` under `flock /tmp/gov-os-rebuild.lock`, and the leads' rebuilds and the nightly's clone rebuild under the same lock.
- **The lock's path:** a path every session on the machine can reach, sandboxed ones included. The lead measures which (the launcher's sandbox and the guard decide what a worker may write) and says so in the design.
- **Place:** a free slot (DEC-936 item 2). STANDARD: no review; one test designer, one engineer.
