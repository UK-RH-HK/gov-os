# ACT-GATE-CONFIG-2: W2-20's machine gate file rewritten for round 2's format, frozen from W2-20's head 28fbcfebf

> **Superseded figure (2026-11-12, DEC-1149):** the gate's working size is now 805,306,368 B (0.75 GiB) per live
> session (ACT-P95-1, applied 16:53). The 2.04 GiB (2,191,601,664 B, DEC-947 item 2) figure below is kept as history.

- **For:** the owner's operator. It replaces one file under HOME, outside every repository, and keeps the old one. It
  changes no tracked file.
- **By:** the CTO, 2026-11-09, on the CTO's ruling of the same day (1). Built and rehearsed with HOME pointed at a
  throwaway home. Nothing live is changed until the operator runs §3.
- **Under:** DEC-1103 (1), as ACT-GATE-CONFIG-1 (`d7490945`). W2-20 (branch `w2/W2-20`, head `28fbcfebf`, worktree
  `~/gov-os-worktrees/W2-20`).
- **Why:** W2-20's round 2 built its configuration to the designer's stated interface, which renamed the keys
  (`floor_bytes` → `memory_floor_bytes`, `trip_floor_bytes` → `oom_floor_bytes`, `gpu_shares` as one dated object
  `{embedder_mib, reranker_mib}`, `disk_path` dropped). ACT-GATE-CONFIG-1's file (sha256 `de4fb326288d…`, round 1's
  keys) no longer loads, so W2-20's gate shuts on it and refuses every launch from W2-20's tree, round 3's engineer
  included: "LAUNCH_REFUSED: the resource gate is shut: config: memory_floor_bytes: missing …" (seen 14:4x today, and in
  the rehearsal's "before" step).
- **The format is frozen from 28fbcfebf (the CTO's ruling):** round 3 must not change key names or meanings; its brief
  says so and a designer's case pins it, so no further re-ACT is needed before W2-20 merges.

## 1. What changes
- **Moved aside, kept:** `~/.gov-os/machine/gate.json` (ACT-1's file, `de4fb326288d80d9d627ad910542ae5d86834c98a3d8895c0e16b9ece2fcd457`)
  goes to `drafts/gate-config-2/backup/gate.json.act1`, with its sha256 beside it.
- **Written:** `gov resources --init-config` from W2-20's code at `28fbcfebf` (its `config.py`, sha256 `560c8d58d35a…`,
  is checked) writes the new file atomically, mode 0600, never over an existing file (P-3). The values come from the
  decisions; the only machine input is the process's CPU set (CPUs 8-19 present: the decided server sets), so the
  operator runs it from a plain terminal, not inside a heavy slot or a taskset. The file no longer names HOME, so the
  rehearsal's bytes are the real bytes: `drafts/gate-config-2/gate.json.expected`, 2,082 bytes, sha256
  `52e32fc182d6e07c856512eb6926e7442eb16c856b46194f35d522e238c44034`. `apply.sh` refuses if init would write other
  bytes.
- **Keys written:** `memory_floor_bytes` 3 GiB (DEC-942 item 2), `oom_floor_bytes` 2 GiB (DEC-947 item 5),
  `working_size_bytes` 2.04 GiB (DEC-947 item 2), `verification_peak_bytes` 7.06 GiB (DEC-947 item 1),
  `rebuild_peak_bytes` = the verification peak (DEC-1001 (d), P-7), `disk_floor_bytes` 100 GiB and `inode_floor`
  10,000,000 (DEC-898 item 1), `verification_lock`, `gpu_margin` 0.10 (DEC-950 item 2), `gpu_shares` embedder and
  reranker 3,584 MiB each (DEC-1032 item 1), `heavy_slots` 3 (DEC-979 item 1 D1), each `{value, date, source}`; and
  `embedding_servers` (shared 12-19 nice 10; query 8-11 nice 0 on the GPU; the live servers' own). Same values as
  ACT-1's file where both have the key.
- **Note (as in ACT-1):** the working size 2.04 GiB is below today's measured lead p95 (3.2 GB). Only the newcomer is
  counted at it; W2-20's `gov resources --sample` over a working day, then `--remeasure`, corrects it after the merge.

## 2. The rehearsal (`drafts/gate-config-2/rehearsal.log`; HOME = `~/gov-os-runs/GATE-CONFIG-2-rehearsal/home`, its
machine folder a copy of the real one, ACT-1's file included). 2026-11-09 14:56:00–14:56:01, **0 failures**.

| Step | Result |
|---|---|
| The real `~/.gov-os/machine` before and after | `cpu-stat.json gate.json server-cpu.json sessions slots`; gate.json `de4fb326288d…` both times |
| **Before:** W2-20's launch admission (`_admit_start`) on ACT-1's file | **refused**, `LAUNCH_REFUSED`: "config: memory_floor_bytes: missing …" |
| `apply.sh check`, then `apply` | state old; ACT-1's file moved to `backup/gate.json.act1` (`de4fb326288d…`); written 2,082 bytes, mode 0600, sha256 = `52e32fc182d6…`, the rehearsed bytes; `config.load()` clean |
| Idempotent | a second `apply`: "already applied"; a second `--init-config`: `RESOURCE_CONFIG_EXISTS`, exit 1; the file unchanged |
| **Admits** | the launch admission for an engineer, no GPU need: **ADMITTED**; with a 1,024 MiB need (kind other): **ADMITTED** (round 2's `[N/A]` handling, ACT-1's note 2 resolved); `gov resources --check`: exit 0 |
| **Refuses over the limits** | a launch declaring 20,000 MiB of GPU (the card has 16,303): **refused**, "gpu: reading 2152, limit 22000"; `gov resources --check --gpu-need-mib 20000`: exit 3; a planted load of 5.0 on 4 processors: exit 3 |
| `apply.sh undo` | the new file removed (its hash matched); ACT-1's file put back (`de4fb326288d…`); the machine folder as before; the launch admission refused again on the old file |

## 3. The operator's steps (about a minute; a plain terminal, not in a slot; W2-20's worktree must still hold 28fbcfebf's `config.py`)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
A=.gov-runtime/scratch/orchestrator/drafts/gate-config-2
bash $A/apply.sh check     # W2-20's config.py = 28fbcfebf's, the pin's python runs W2-20's code; init would write 52e32fc182d6…; state old (ACT-1's file) (exit 0)
bash $A/apply.sh apply     # ACT-1's file moved to $A/backup/gate.json.act1 (sha256 kept); W2-20's `gov resources --init-config`; written sha256 checked = 52e32fc182d6…; the gate admits a session (exit 0) and refuses a 20000 MiB GPU start (exit 3)
git commit --allow-empty -m "ACT-GATE-CONFIG-2: ~/.gov-os/machine/gate.json rewritten for W2-20's frozen format by its gov resources --init-config (28fbcfebf; sha256 52e32fc182d6e07c856512eb6926e7442eb16c856b46194f35d522e238c44034); ACT-1's file kept (de4fb326288d)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1103" --trailer "Role: owner"
```
- **What `apply` runs:** `cd ~/gov-os-worktrees/W2-20 && PYTHONPATH=$PWD/src <the pin's python> -m gov.cli.main
  resources --init-config`, the pin's python being the shebang of `~/.local/bin/gov`; `apply` checks that it imports
  W2-20's `config.py` and that the file is 28fbcfebf's.
- **If the file there is neither ACT-1's nor the expected one,** `apply` backs it up to `$A/backup/gate.json.found` with
  its sha256 and stops: it never overwrites.
- **Undo:** `bash $A/apply.sh undo`: removes the new file if it still hashes as written (else moves it into
  `$A/backup/`), puts ACT-1's file back (its sha256 checked) and removes any side file apply's own gate reading made.
  After undo, W2-20's launches are refused again, as today.

**Then the CTO:** W2-20's round 3 (the review's F1, F2, F4, F6, F8), its runs outside the sandbox, review round 2, and
the merge.

## 4. The files (scratch)
| File | sha256 (first 12) | What |
|---|---|---|
| `drafts/gate-config-2/apply.sh` | `8dd17662ef6f` | check, apply and undo; 28fbcfebf's `config.py`, ACT-1's and the new file's hashes pinned |
| `drafts/gate-config-2/expected.py` | `c54e3f854c55` | the bytes `init()` would write for this CPU set, from W2-20's `template()`; writes nothing |
| `drafts/gate-config-2/gate.json.expected` | `52e32fc182d6` | the exact file (CPUs 0-19) |
| `drafts/gate-config-2/rehearse.sh`, `launch_gate.py`, `rehearsal.log` | `f8073400267f`, `bf17c50b82af`, `fe825c196cf3` | the rehearsal and its record |

[DEC-1103 (1), the CTO's ruling 2026-11-09 (1), DEC-947, DEC-942, DEC-950, DEC-898, DEC-979, DEC-1032, DEC-1001 (d), DEC-1088 (5)(b), P-3]
