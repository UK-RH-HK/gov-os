# ACT-GATE-CONFIG-1: W2-20's machine gate file, written by `gov resources --init-config` from W2-20's code (DEC-1103 (1))

> **Superseded figure (2026-11-12, DEC-1149):** the gate's working size is now 805,306,368 B (0.75 GiB) per live
> session (ACT-P95-1, applied 16:53). The 2.04 GiB (2,191,601,664 B, DEC-947 item 2) figure below is kept as history.

- **For:** the owner's operator. It writes one file under HOME, outside every repository, and changes no tracked file.
- **By:** the CTO, 2026-11-09. Built and rehearsed with HOME pointed at a throwaway home. Nothing live is changed until
  the operator runs §3.
- **Under:** DEC-1103 (1), option (a). W2-20 (branch `w2/W2-20`, head `b0acd966b`, worktree `~/gov-os-worktrees/W2-20`).
  The values are checked against DEC-1052 O-A1 (the Load Balancer's measured limits).
- **Order:** before W2-20 merges. **The file must exist first.** W2-20 puts `_admit_start` in `gov launch` for every
  lead and every worker. With no file, `config.load()` reports a fault and the gate shuts on it, so every launch after
  the merge would be refused (`RESOURCE_GATE_SHUT`, exit 3). The rehearsal's "before" step shows this refusal.

## 1. What the command does (W2-20's `src/gov/resources/config.py`, `init()` and `template()`)
- **What it writes:** `gov resources --init-config` writes `~/.gov-os/machine/gate.json` (HOME's), and only when no
  file is there (P-3).
  - The write is atomic: a temporary file in the same folder, then `os.replace`. The mode is 0600.
  - A second run refuses with `RESOURCE_CONFIG_EXISTS` (exit 1) and leaves the file alone. **So it is idempotent by
    refusal** (rehearsed).
- **Where the values come from:** the decisions. It measures nothing. Only two inputs come from the machine:
  - HOME, which gives `disk_path`;
  - the process's own CPU set (`os.sched_getaffinity`). If CPUs 8-19 are present, the embedding servers get the
    decided sets. If not, it derives them from the CPUs it has. **So the operator runs it from a plain terminal, not
    inside a heavy slot or a taskset.** `apply.sh` refuses when the bytes would differ from the reviewed ones.
- **Measured figures:** the three of them (working size, verification peak, rebuild peak) carry their decision
  dates. Each is more than seven days old, so the reading names all three "due for re-measure". They still count.
- **Who else reads the file:** the main tree's `gov.retrieval.ollama` (W2-123) already reads its `embedding_servers`
  section when gov starts or restarts an embedding server.
  - With the file, a gov-started query server goes to CPUs 8-11 at nice 0. Without it, the default is the highest 8
    CPUs at nice 10.
  - The file's sets are the live servers' own (§2), so a gov restart now matches what runs.

## 2. The values written for this machine (20 CPUs, 23.5 GB, RTX 5070 Ti 16,303 MiB), checked against the measured limits

`drafts/gate-config/gate.json.expected` holds the exact file, sha256 `de4fb326288d…`. The rehearsal's file is the same
byte for byte except `disk_path`, which is the throwaway home there.

| Key | Value written (source in the file) | Measured / the Load Balancer (dispatch `status.txt` 12:41, `heavy_slots.conf`, live processes) | Check |
|---|---|---|---|
| `floor_bytes` | 3 GiB (DEC-947 item 5) | LB's admission floor 3,072 MB (the trip-wire's) | equal |
| `trip_floor_bytes` | 2 GiB (DEC-947 item 5) | — | below the floor, as the loader requires |
| `working_size_bytes` | 2,191,601,664 B = 2.04 GiB (DEC-947 item 2, dated 10-29) | LB peaks 11-09 12:27: a lead's **p95 3,244 MB**, max 6,513 MB | **below the measured p95** (see note 1); named due for re-measure |
| `verification_peak_bytes` | 7,582,199,808 B = 7.06 GiB (DEC-947 item 1, 10-29) | — | due for re-measure |
| `rebuild_peak_bytes` | the verification peak (DEC-1001 (d), P-7: not measured) | — | due for re-measure |
| `disk_path`, `disk_floor_bytes`, `inode_floor` | `/home/usain`; 100 GiB; 10,000,000 (DEC-898 item 1) | 827 GiB free; 64.9 M inodes free | open, with a wide margin |
| `heavy_slots` | 3 (DEC-979 item 1 D1) | `heavy_slots.conf` SLOTS=3, WORKERS=6; LB "heavy slots 3 x 6" | equal |
| `gpu_margin` | 0.10 (DEC-950 item 2) | — | as decided |
| `gpu_shares` | embedder 3.5 GiB, reranker 3.5 GiB (3,584 MiB), headroom 2 GiB (DEC-1032 item 1) | LB: headroom 2,048 MiB; reranker peak 3,589 MB; 2 reranker GPU slots priced | headroom equal. The reranker share is about the measured peak. The gate keeps one reranker share, while the LB prices two. See note 2 |
| `embedding_servers.shared` | 127.0.0.1:11434, CPUs 12-19, nice 10 | pid 6627: affinity 12-19, nice 10 | equal |
| `embedding_servers.query` | 127.0.0.1:11435, CPUs 8-11, nice 0, device gpu | pid 7034: affinity 8-11, nice 0; on the GPU (29/29 layers) | equal |
| (the load limit, not in the file) | `min(load1, load15) < nproc` = 20 | the LB's band 14-18 | the gate is the hard limit; the LB dispatches below it |

At the rehearsal, memory had 15.4 GiB against a need of 5.0 GiB (the floor plus one newcomer). There were no live
sessions in the registry. The gate was open.

**Note 1 (the working size).** The file's working size (2.04 GiB) is below today's measured p95 for a lead (3.2 GB).
- Only the newcomer is counted at that figure. A running session counts at what it actually uses (DEC-961).
- So the gate can admit one more lead than the LB's forecast would. The LB still decides admission (DEC-1052 O-A1).
- The fix is W2-20's own re-measure after the merge: `gov resources --sample` over a working day, then
  `--remeasure`. The reading already names the figure as due.
- This ACT writes the file `--init-config` gives, as DEC-1103 (1) decided. It does not edit values.

**Note 2 (a finding on W2-20, not on the file; for W2-20's round 2).** WSL's `nvidia-smi --query-compute-apps` reports
`used_memory` as `[N/A]`.
- So `gpu_room` counts no share as held. For a start of kind `other`, it holds back the whole embedder share, the
  whole reranker share and the headroom (9.66 GB). That is on top of the 6.4 GB the two loaded embedders already use.
- The result: a launch that declares `--gpu-need-mib 1024` (kind `other`) is refused with 9.5 GB free (rehearsed).
  The same need declared as kind `embedder` is admitted.
- Launches that declare no GPU need, which is every launch today, never read the GPU and are not affected.

## 3. The operator's steps (about a minute; a plain terminal, not in a slot)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
A=.gov-runtime/scratch/orchestrator/drafts/gate-config
bash $A/apply.sh check     # W2-20 at b0acd966b, config.py as built, the pin's python runs W2-20's code; init would write de4fb326288d…; state absent (exit 0)
bash $A/apply.sh apply     # runs W2-20's `gov resources --init-config`; the written sha256 checked = de4fb326288d…, recorded in $A/backup/; the gate admits a session (exit 0) and refuses a 20000 MiB GPU start (exit 3)
git commit --allow-empty -m "ACT-GATE-CONFIG-1: ~/.gov-os/machine/gate.json written by W2-20's gov resources --init-config (b0acd966b; sha256 de4fb326288d80d9d627ad910542ae5d86834c98a3d8895c0e16b9ece2fcd457), before W2-20 merges" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1103" --trailer "Role: owner"
```
- **What `apply` runs:**
  `cd ~/gov-os-worktrees/W2-20 && PYTHONPATH=$PWD/src <the pin's python> -m gov.cli.main resources --init-config`.
  The pin's python is the shebang of `~/.local/bin/gov`, `/home/usain/.local/share/gov-os/pin-bcea09060ebc/bin/python`.
  `apply` checks that this python imports W2-20's `config.py` and not the pin's.
- **If a file is already there:**
  - If it holds the expected bytes, `apply` says "already applied" and exits 0.
  - Otherwise it backs the file up to `$A/backup/gate.json.found` with its sha256 and stops. It never overwrites (P-3).
- **The commit** records the act. It touches no file: the gate file lives under HOME.

**Undo:** `bash $A/apply.sh undo`. It removes the file if it still hashes as written. If the file has changed since (a
`--remeasure`, say), undo moves it into `$A/backup/` instead. It also removes the side file `server-cpu.json` that
apply's own gate reading made. The rehearsal shows the machine folder back to its names before the apply.

**Then the CTO:** W2-20's round 2 verification on this machine, then its merge.

## 4. The rehearsal (`drafts/gate-config/rehearsal.log`; HOME = `~/gov-os-runs/GATE-CONFIG-rehearsal/home`)
One run, 2026-11-09 12:51:34–12:51:36, **0 failures**. The first run is kept as `rehearsal-run1.log`. Its one failure
was a rehearsal step that expected a 1 GiB GPU start of kind `other` to be admitted; that is note 2's finding.

| Step | Result |
|---|---|
| The real `~/.gov-os/machine` before and after | `cpu-stat.json` only; **no gate.json**; the same names after |
| **Before:** W2-20's launch admission (`_admit_start`, as `gov launch` runs it) with no file | **refused, exit 3**: "config: …gate.json is missing", plus memory, disk, inodes and slots all unconfigured |
| `apply.sh check`, then `apply` | state absent; written 2,633 bytes at mode 0600, sha256 = the bytes expected; `config.load()`: **no fault**, the three measured figures due for re-measure |
| Idempotent | a second `apply`: "already applied". A second `--init-config`: `RESOURCE_CONFIG_EXISTS`, exit 1. The file is unchanged by both |
| **Admits** | the launch admission for an engineer with no GPU need: **ADMITTED**. `gov resources --check --kind session` / `test` / `rebuild`: exit 0. A 1,024 MiB start of kind `embedder`: exit 0 |
| **Refuses over the limits** | a launch declaring 20,000 MiB of GPU (the card has 16,303): **refused, exit 3**, naming the GPU room. The machine read as 1 processor (`GOV_RESOURCES_NPROC=1`): **refused, exit 3**, "load 1.47 against the threshold 1" |
| Note 2's finding | a 1,024 MiB start of kind `other`: refused, 526 MB of room after 9.66 GB held back |
| `apply.sh undo` | the file removed (its hash matched), `server-cpu.json` removed; the launch admission **refused again**, exit 3, on the missing file |

## 5. The files (scratch)
| File | sha256 (first 12) | What |
|---|---|---|
| `drafts/gate-config/apply.sh` | `d8d02713b307` | check, apply and undo; W2-20's head, `config.py` hash and the expected bytes pinned |
| `drafts/gate-config/expected.py` | `a14691cd6a5c` | the bytes `init()` would write for a HOME and CPU set, from W2-20's `template()`; writes nothing |
| `drafts/gate-config/gate.json.expected` | `de4fb326288d` | the exact file for HOME=/home/usain, CPUs 0-19 |
| `drafts/gate-config/rehearse.sh`, `rehearsal.log` | `5299b7024fa5`, `0485e502d9e7` | the rehearsal and its record |

[DEC-1103 (1), DEC-1052 O-A1, DEC-947, DEC-950, DEC-898, DEC-979, DEC-1032, DEC-1001 (d), DEC-1088 (5)(b), P-3]
