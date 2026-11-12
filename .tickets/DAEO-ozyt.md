---
id: DAEO-ozyt
status: in_progress
deps: [DAEO-r30l]
links: [DAEO-r30l, DAEO-5emz]
created: 2026-11-11T01:20:16Z
type: task
priority: 2
assignee: engineer
external-ref: W2-157
tags: [wave-2, implementation, standard, after-the-lift, gpu, capacity]
wbs_id: W2-157
title: 'The GPU backstop in the product: a named GPU job is paused at once when GPU memory passes its limit, spills into shared memory, or an embedder is not wholly on the GPU (EMERGENCY-TOOLS-1 D12; DEC-1067, DEC-1068 (4))'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-r30l
allowed_paths:
- src/gov/resources/backstop.py
- src/gov/resources/command.py  # the one option, --backstop
- src/gov/resources/config.py  # the one new value, gpu_backstop_limit_mib
- tests/unit/resources/test_w2_157*
- docs/changes/W2-157-evidence.md
reads:
- src/gov/resources/**
- governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md
needs:
- src/gov/resources/command.py
- src/gov/resources/config.py
waits_on:
- ref: DAEO-r30l
  reason: 'W2-20 owns src/gov/resources/** and its gate configuration; this ticket adds one module and one value after it merges'
kpis:
  success:
  - 'S1 `gov resources --backstop <pgid> [<pgid> ...]` watches the named process groups and, every 5 seconds (a configured value), pauses every live named group with SIGSTOP at once when GPU memory used is above the configured limit (`gpu_backstop_limit_mib` in the gate''s one configuration file, dated and sourced; this machine''s value 15,872 MiB, 15.5 GiB); a missing or malformed limit refuses to start, naming it. Verify: a stand-in `nvidia-smi` printing 15,800 then 15,900 MiB and a stand-in job in its own process group: the job is running at the first reading, stopped at the second, the trip logged with the reading [DEC-1067 (GPU safety), DEC-1068 (4)]'
  - 'S2 A spill into shared GPU memory trips it too: GPU memory used within 64 MiB of the card''s total. Verify: a stand-in reading of total minus 63 MiB trips it and total minus 65 MiB does not [DEC-1067 (GPU safety), DEC-1068 (4)]'
  - 'S3 An embedder not wholly on the GPU trips it: a model of an embedding server (the ports from the gate''s configuration) whose `size_vram` is below its `size`, or a line "offloaded N/M layers to GPU" with N below M in the server''s log written since the watch started. Verify: a stand-in server answering both forms, each tripping it once, and a line with N equal to M not tripping it [DEC-1067 (GPU safety), DEC-1068 (4), DEC-1030]'
  - 'S4 Only the named groups are touched: nothing is matched by name, a name that is not a process group id above 1 refuses to start (exit 2), and a group already ended is skipped and named. A trip writes one inbox item naming the reason, the groups paused and how to resume (`kill -CONT -- -<pgid>`) or stop them, then the watch ends; when every named group has ended on its own, the watch logs it and ends. Verify: a stand-in with an unrelated process of the same name left running after a trip; a refused argument "abc"; a job that ends first [DEC-1067 (GPU safety), DEC-1068 (4), DEC-1073]'
  - 'S5 It changes nothing else: it only reads the GPU, the servers'' answers and their logs, and writes its own log and the one inbox item. Verify: a filesystem-spy test over a run with no trip: only its log is written [DEC-1068 (4)]'
  failure:
  - 'A process outside the named groups paused or signalled. Verify: S4''s planted unrelated process of the same name, left running after a trip: its state is still running and it received no signal; any stop of it is this failure'
  - 'A trip on a reading under every limit, or a spill, an embedder partly on the CPU or a partial offload not tripping it. Verify: S1''s stand-in readings (15,800 MiB no trip), S2''s (total minus 65 MiB no trip, total minus 63 MiB trip) and S3''s stand-in server (N equal to M no trip; `size_vram` below `size` and N below M each trip): each reading gives the stated outcome'
  - 'A limit taken from anywhere but the gate''s configuration file. Verify: a planted configuration with a limit differing from the built-in value (and an environment variable and a command-line argument holding a third value): the trip happens at the file''s value only; a planted file with the limit missing or malformed refuses to start and names it'
  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'
profile: STANDARD
sources:
- DEC-1067
- DEC-1068
- DEC-1030
- DEC-1073
- DEC-1119
- DEC-1109
- DAEO-r30l  # W2-20
est_loc: 160
acceptance_tests:
  path: tests/acceptance/W2-157/
  author: 'independent-test-designer (MR-3), from these KPI lines; a stand-in nvidia-smi, a stand-in embedding server and planted process groups, never the real GPU or the shared servers'
track: A
list_rows: []
---
# W2-157 The GPU backstop in the product

Filed by the product-spec helper of the night audit (DAEO-sdxk's anti-drift audit (d), 2026-11-11) on EMERGENCY-TOOLS-1 row D12; **after the lift**, **before EXAMIN's copy** (§1 D12 "yes, GPU safety"; the copy shares this machine's GPU).

- **Problem.** The CTO's `gpu_backstop.sh` (`.gov-runtime/scratch/orchestrator/tools/gpu_backstop.sh`, DEC-1067 (GPU safety), DEC-1068 (4)) pauses a GPU job on a memory limit, a spill or a partial offload. It is a scratch tool. W2-20's gate refuses a start that lacks GPU room and stops the largest heavy job below a memory floor; neither watches a GPU job while it runs, and EMERGENCY-TOOLS-1 §3 retires the tool only once the product covers a spill. W2-137 S5 already names "the GPU backstop armed" as a step of its measure.
- **Approach.** One module beside W2-20's gate, started with `--backstop` and the job's process groups. Same triggers and the same pause as the script; the limit moves into the gate's configuration file. Alternative: fold it into W2-20's trip-wire (rejected: W2-20 is merged or in review and its trip-wire is on system memory, not the GPU).
- **Interface.** `gov resources --backstop <pgid>...`; the limit `gpu_backstop_limit_mib`; the poll period `gpu_backstop_every_s`. The inbox is the project's inbox folder (as W2-156's).
- **Non-goals.** No kill (a pause only; the owner or the CTO resumes or stops); no GPU scheduling (W2-20 S-lines on GPU shares); no change to the shared servers.
- **Rabbit holes.** Matching processes by name or `ps | grep` (the groups are named, nothing else); reading Windows' shared-usage counter (WSL cannot; the total-minus-64 MiB sign stands).

[DEC-1067 (GPU safety), DEC-1068 (4), DEC-1119 (5)]
