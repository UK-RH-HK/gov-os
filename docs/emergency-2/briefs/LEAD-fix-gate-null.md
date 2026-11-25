# Lead brief: the resource gate shuts on `cpu: reading null` when an embedding server's process tree changes (a fix under W2-20; root cause under Q-7; it gates the 0.1.7 patch release)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-25. **Read `docs/emergency-2/briefs/LEAD-COMMON.md` first: every rule there applies** (never cut a `gov retrieve` result, list your retrieves, one trailer paragraph with no blank line before `Co-Authored-By`). Decide, never ask (I-10). Use `systematic-debugging`. **This blocks the release: small and fast.**

## The failure (three release suites in a row; the owner's Q-7: the same failure three times, fix the root)
W2-184's S1 criticality cases (and before them W2-184 S4, W2-156 S6, W2-60a) run the real `gov launch`, which reads the real resource gate. They fail with `gov launch: LAUNCH_REFUSED: the resource gate is shut: cpu: reading null, limit 64 (an embedding server's CPU use over the last minute could not be sampled) (DEC-1088 (5))`. Records: `docs/close/nightly/NR-20261125T115821Z-4856c1fef6ee.json` and the two before it (FINDINGS I-30). In ordinary use the same refusal can hit any real launch.

## The CTO's reading of the cause (verify it, then fix the cause)
`src/gov/resources/machine.py` `_sample_servers` sums each embedding server's CPU over its process tree (`ollama serve` and its model runner child, `tree(table, pid)`). When the runner child exits (the model unloads after its keep-alive) or a new one starts, the tree's summed CPU **falls below** the kept samples of the same server pid. `_window_rate` keeps only samples with `cpu_seconds <= cpu` (line ~315), finds none, and returns `None`; `now` then holds `None` and the gate reads `cpu: reading null` and shuts. A fall in the tree's sum is a reset (a child gone), not an unreadable reading: treat it as a new process (the short fresh sample already used for a new pid, `pending`), or measure from the samples after the reset, so the gate gets a number. Never read a real failure (no listener, a process that cannot be read) as healthy: those stay as they are.

## What
- **G-NULL-1:** a planted process table in which the server's runner child exits between samples (the summed CPU falls) gives a number for the server's last-minute CPU, not `None`, and the gate stays open when the machine has room; a planted table where the server's process cannot be read still shuts the gate with its reason. Failing test first (the test designer, under `tests/acceptance/W2-20/` or `tests/unit/resources/`, as W2-20's acceptance folder holds its other cases); then the engineer's fix.
- Say whether the W2-184, W2-156 and W2-60a cases should also plant the machine reading (W2-207's MA-4 makes the reading injectable): if the product fix removes the null, leave the tests reading the real gate.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-fix-gate-null`, branch `e2/fix-gate-null` from `w2/integrate`. Code area: `src/gov/resources/machine.py` only (and its tests). The `## Fix:` section goes in `.tickets/DAEO-r30l.md` (W2-20), trailer `Fix: the resource gate shut on cpu: reading null when an embedding server's process tree changed` with `Task: DAEO-r30l`.

## Green
G-NULL-1 red on the base, green after; `tests/unit/resources`, W2-20 and W2-184 green (W2-184 run twice, `-n auto`); then exactly the impact-selected suites (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-r30l=e2/fix-gate-null --onto w2/integrate --select`), through the heavy slot. Check the trailers.

## Return
Branch and head; the cause confirmed (file:line, and the planted case that reproduces it); the fix in three lines; the tests before and after; the selected suites' summary; your retrieves.

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
Query: How does the resource gate sample the embedding servers' CPU (machine.py _sample_servers, _window_rate, tree, kept samples, cpu reading null) and which tests run gov launch against the real gate? Code locations, conventions, earlier fixes and findings.

```
store: 4856c1fef6ee (/home/usain/gov-os-worktrees/W2-00-store-a)
{
  "store": {
    "commit": "4856c1fef6eed957d6efeec87f87b6a4a689f375",
    "head": "4856c1fef6eed957d6efeec87f87b6a4a689f375",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-a"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "7e9a45bf72d25f2dd35e87fe",
      "sha256": "1f53d3f1fa11ab783ba13ba8bf4ec2990cfb23cd60bb612095fc08655addddf3",
      "path": "src/gov/resources/machine.py",
      "start_line": 329,
      "end_line": 371,
      "text": "def _sample_servers(folder: Path, values: dict):\n    \"\"\"The servers' own sampling: ``((p95, why), (now, why))``.\"\"\"\n    ports = _server_ports(values)\n    if ports is None:\n        why = \"the embedding servers' section cannot be read, so their CPU cannot be measured\"\n        return (None, why), (None, why)\n    path, samples = folder / SERVER_HISTORY, _read_samples(folder / SERVER_HISTORY)\n    try:\n        (folder / OLD_SERVER_HISTORY).unlink(missing_ok=True)  # round 3's history is never read\n    except OSError:\n        pass\n\n    def cpu_now():\n        table = processes()\n        pids = {name: listener(port, table) for name, port in ports.items()}\n        return {name: (pid, round(sum(table[p][\"ticks\"] for p in tree(table, pid)) / TICKS, 3)\n                       if pid in table else None) for name, pid in pids.items()}, time.time()\n\n    def kept(name, pid, at) -> list[dict]:\n        \"\"\"The server's kept samples: of its current pid, earlier than ``at`` and at most ``KEEP_S`` old.\"\"\"\n        return [s for s in samples if s[\"server\"] == name and s[\"pid\"] == pid and 0 < at - s[\"time\"] <= KEEP_S]\n\n    first, at = cpu_now()\n    pending = [n for n, (pid, cpu) in first.items() if pid is not None and cpu is not None and not kept(n, pid, at)]\n    if pending:  # no kept sample of this server's process (new, or every one expired): a short fresh one first\n        time.sleep(SHORT_S)\n        second, later = cpu_now()\n        samples += [{\"time\": at, \"server\": n, \"pid\": first[n][0], \"cpu_seconds\": first[n][1]} for n in pending]\n        first, at = second, later\n    out, now = {}, {}\n    for name, (pid, cpu) in first.items():\n        mine = [s for s in samples if s[\"server\"] == name and 0 <= at - s[\"time\"] <= SERVER_KEEP_S]\n        if cpu is not None:\n            mine.append({\"time\": at, \"server\": name, \"pid\": pid, \"cpu_seconds\": cpu})\n        rates = _rates(mine)[-SERVER_SAMPLES:] + ([0.0] if pid is None else [])\n        out[name] = round(_p95(rates), 2) if rates else None\n        now[name] = 0.0 if pid is None else (None if cpu is None else _window_rate(kept(name, pid, at), at, cpu))\n        samples = [s for s in samples if s[\"server\"] != name] + mine[-SERVER_LINES:]\n    _write_samples(path, sorted(samples, key=lambda s: s[\"time\"]))\n    p95 = (None, \"an embedding server's CPU could not be sampled\") if None in out.values() else (out, None)\n    current = (None, \"an embedding server's CPU use over the last minute could not be sampled\") \\\n        if None in now.values() else (now, None)\n    return p95, current\n",
      "chunk_id": "7e9a45bf72d25f2dd35e87fe",
      "routes": [
        "lexical",
        "semantic",
        "code"
      ],
      "batch": 1
    },
    {
      "id": "c6818a0afbc0249d8fd5de54",
      "sha256": "d337c27afc7bda74a40aaeccb8dde95f54c614810ee8d231ee01f040bcf03c32",
      "path": "src/gov/resources/machine.py",
      "start_line": 255,
      "end_line": 276,
      "text": "def servers_cpu(folder: Path, values: dict):\n    \"\"\"``((p95, why), (now, why))``, each ``{\"shared\": cores, \"query\": cores}`` or None (round 7, review F2).\n\n    - p95: ``GOV_RESOURCES_EMBEDDING_CPU`` where set, else the p95 of each server's rates between its consecutive\n      samples of one process over the last week (one sample of each server's process tree per reading, in\n      ``embedding-cpu.jsonl``: ``{\"time\", \"server\", \"pid\", \"cpu_seconds\"}``).\n    - now: ``GOV_RESOURCES_EMBEDDING_CPU_NOW`` where set, else each server's CPU use over the busy cores' last minute\n      from its kept samples, those of its current pid at most ``KEEP_S`` old (the same window rule: the newest kept\n      sample at least a minute old, else the oldest). It is the servers' part of the busy cores.\n\n    A listening server with no kept sample (a new process, or every sample expired) is sampled afresh first, a quarter\n    of a second apart, so stale samples never shut the gate (review R2-F1, DEC-1105). A server that is not listening\n    uses no CPU now.\"\"\"\n    planted = {}\n    for key, name in ((\"p95\", \"GOV_RESOURCES_EMBEDDING_CPU\"), (\"now\", \"GOV_RESOURCES_EMBEDDING_CPU_NOW\")):\n        if os.environ.get(name) is not None:\n            planted[key] = _planted_servers(name)\n    if len(planted) < 2:\n        sampled = _sample_servers(folder, values)\n        planted.setdefault(\"p95\", sampled[0])\n        planted.setdefault(\"now\", sampled[1])\n    return planted[\"p95\"], planted[\"now\"]\n",
      "chunk_id": "c6818a0afbc0249d8fd5de54",
      "routes": [
        "lexical",
        "semantic",
        "code"
      ],
      "batch": 2
    },
    {
      "id": "7963c5035e08a67cf87b323a",
      "sha256": "e174ffe00d96e095d632f58120dc259e67e81f6f403e373c5dd21360ae072061",
      "path": "docs/changes/W2-20-evidence.md",
      "start_line": 16,
      "end_line": 35,
      "text": "## Round 4: DEC-1105's exception round, R2-F1 only\n\nThe configuration format is unchanged (frozen from `28fbcfebf`); `src/gov/resources/config.py` and `gate.json` are\nuntouched. Only the servers' CPU samples changed: they are a cache, moved to the designer's round-8 interface.\n\n| Finding | Ruling | What changed | Unit evidence (`tests/unit/resources/test_w2_20_round3.py`) |\n|---|---|---|---|\n| **R2-F1**: the first reading after ten quiet minutes shut the gate on cpu (a server with only expired samples was not resampled, so `embedding_cpu_now` read `null`) | fix (DEC-1105) | `machine._sample_servers`: the samples live in `~/.gov-os/machine/embedding-cpu.jsonl`, one line per server per sample, `{\"time\", \"server\", \"pid\", \"cpu_seconds\"}`. A server's **kept** samples are those of its current pid at most `KEEP_S` (600 s) old. A listening, readable server with none kept (a new process, or every sample expired) is sampled afresh first (a sample, a quarter of a second, the reading), and both samples are written; so stale samples never shut the gate. `now` is the window rate over the kept samples (unchanged rule). The p95 keeps round 7's span: the rates between a server's consecutive samples of one process over the last week (at most 500). An unreadable server still reads `null` and shuts on `cpu` (F5). Round 3's `server-cpu.json` is never read and is removed at the next reading. | `test_r2_f1_a_history_older_than_the_keep_window_is_sampled_afresh_and_the_gate_opens` (both servers' histories three hours old: `now` and p95 0.0, the gate open, a fresh pending sample and the reading's own written for each), `test_r2_f1_a_history_inside_the_keep_window_is_read_without_a_fresh_sample` (300 s: no pending sample), `test_r2_f1_expired_lines_of_another_pid_never_count`, `test_r2_f1_an_unreadable_server_with_an_expired_history_still_shuts_on_cpu`, `test_f2_a_kept_history_written_before_round_4_still_reads` (2: rounds 2 and 3's file dropped) |\n\n**The interface's one disagreement, named:** the round-8 README computes the p95 from the kept (600 s) samples; S12\nand round 7 keep it over a week. As the brief rules, the p95 keeps round 7's week; the expiry rule applies to the\ncurrent use (and to when a server is sampled afresh).\n\n**Round 4's runs (inside the sandbox; `HOME` an empty scratch folder with only the user site's `lib` linked in):**\n\n- `gov accept W2-20`: **170 passed, 0 failed, 1 skipped (171)**; every line passes but S16, whose one case skips (the\n  CTO's run outside the sandbox).\n- Unit tests, `tests/unit/resources tests/unit/launch` with `-m \"not local_only\" -k \"not real and not green_here and\n  not time_limit\"`: **287 passed, 86 deselected**.\n\n",
      "chunk_id": "7963c5035e08a67cf87b323a",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "9ad8246261ab925a31ebf248",
      "sha256": "0ee3813037c84d3aff1f66fb924ce4a8469da8668ca721982ec90a4cce91abfb",
      "path": "docs/changes/W2-20-evidence.md",
      "start_line": 44,
      "end_line": 44,
      "text": "| **F2**: the cpu rule counted the servers twice | fix (round 7's interface) | `cpu`: `busy_cores_1m + max(0, p95(shared) - now(shared)) + max(0, p95(query) - now(query)) < nproc`. New reading `embedding_cpu_now` (`machine.servers_cpu`): `GOV_RESOURCES_EMBEDDING_CPU_NOW`, else each server's process-tree CPU over the busy cores' last minute (kept `[t, pid, ticks]` samples in `server-cpu.json`'s `window`, the same window rule as the busy cores; a server's new process, or a history from round 2 with no window, gets a short window at once). Unreadable: `null`, shut on `cpu` with `reading` `null`. | `test_f2_only_the_part_of_each_servers_p95_above_its_current_use_is_added` (4: the store rebuild opens at 12.5; the same p95 idle now shuts at 20.0; busier now than its p95 adds nothing, 20.0 shuts; 3.9 of 4 opens), `test_f2_busy_cores_alone_shut_only_at_nproc`, `test_f2_an_unreadable_current_use_shuts_on_cpu_with_a_null_reading` (4), `test_f2_the_own_current_use_is_the_servers_cpu_over_the_last_minute`, `test_f2_a_kept_history_written_before_round_3_still_reads` |\n",
      "chunk_id": "9ad8246261ab925a31ebf248",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "df0353f7d752b7aaa544ad72",
      "sha256": "4d8009610c3191795fddceed60bbc4b39ee79e2a1f52a63d9d37edb9240dc75b",
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "start_line": 36,
      "end_line": 36,
      "text": "| I-30 | 2026-11-25 | Load flakes in W2-184 and the resource gate: the 0.1.6 release suite on b8a04194a was red on exactly two W2-184 S1 criticality cases (`test_s1_a_profile_rule_matches_the_ticket_s_profile[STANDARD-notes/x/**-C0]` and `[LITE-...]`); W2-184 alone passed 505 of 505; the same family flaked all night under load (W2-184 S4, S1; W2-156 S6, W2-60a, the gate's `cpu: reading null`). A green release needed a second full run (90 min) | `docs/close/nightly/NR-20261125T052127Z-b8a04194a337.json` | the tests that start `gov launch` under the resource gate (W2-184, W2-156, W2-60a) and `gov resources`' reading | fix: the cases plant the machine reading (the injectable reading of W2-207 MA-4) instead of reading the loaded machine; failing test first | the release suite re-run |\n",
      "chunk_id": "df0353f7d752b7aaa544ad72",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "cdc69bb8ecff0cf443f4c39a",
      "sha256": "9583cbefc94d2c687c952b980191e8e6f90f0389ee2c806e7a4589f856165ba0",
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "start_line": 52,
      "end_line": 56,
      "text": "| Operator agent (cron `operator_launch.py`, every 10 min) | **no** | `operator_launch.py:43-45` runs `claude -p --restricted` itself | one session at a time, from its queue |\n| Independent sessions (`tools/indep_launch.py`) | **no** | `indep_launch.py:1343, :1381` run `claude` under `timeout` | evaluation runs, own launcher |\n| Editor: VS Code server, its extensions, language servers, Codex, ripgrep | **no** | none | about 6.0 GB resident now, the largest single consumer (the CTO's own `claude` is inside this figure, 0.5 GB) |\n| Embedding servers and reranker | **read, not started or capped by the gate** | `resources/machine.py` readings; CPUs set by their own ACTs | llama servers 1.6 GB, reranker 1.6 GB |\n| Test runs (`heavy_slot.sh`, `verify_lock.sh`, `gov accept`, pytest) | **partly: by another limiter** | `heavy_slot.sh:166-168` takes `/tmp/gov-os-heavy-slot-N.lock` (3 slots, 6 workers, `taskset`) | the gate has its own slots (`~/.gov-os/machine/slots/`, `gov resources --slot`, `slots.py:311`). Nothing uses them. The gate counts these runs only through free memory and load |\n",
      "chunk_id": "cdc69bb8ecff0cf443f4c39a",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "b1014c65a3a0d993d651ce8d",
      "sha256": "7eaffebbf85ebc9b08aa4de341f0e5da4521d695a948392916bb88c6e84235be",
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "start_line": 91,
      "end_line": 105,
      "text": "## 4. The sample day and `--remeasure` (DEC-1105)\n\n**DEC-1105 (owner, 11-09), the sentence:** \"Then the CTO merges W2-20, runs `gov resources --sample` over a working day and\nthen `--remeasure`.\" (S16 per CPU and R2-F1 were the exception round before it; both done, merged 11-09.)\n\n**What it is, exactly.**\n\n- `gov resources --sample` (`resources/measure.py:60`) is one reading, a fraction of a second. It lists every session in\n  the registry (`~/.gov-os/machine/sessions/`), measures each one's process-tree memory, notes whether\n  `/tmp/gov-os-verify.lock` is held, adds each holder of one of the gate's own slots, and appends **one JSON line** to\n  `~/.gov-os/machine/samples.jsonl`. Nothing else is written.\n- \"A working day\" is not defined in the decision. The CTO's tool `tools/resources_sample_day.sh` (D30 in\n  EMERGENCY-TOOLS-1, \"not yet (after the re-pin)\") reads it as 96 samples, one every 300 s: **8 hours**. The CTO runs it, in\n  the background; the line goes to `log/resources-sample-day.log`; samples go to `samples.jsonl`. Today that file has two\n  lines (11-09 16:23 and 16:24), both with an empty list (the merge-time tests, no session was registered).\n",
      "chunk_id": "b1014c65a3a0d993d651ce8d",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-r30l",
      "sha256": "384c748bdbe8be0d83c7b2364ed4693d1fd703939a3d7d3ccd104ae227bc0b00",
      "path": ".tickets/DAEO-r30l.md",
      "start_line": 32,
      "end_line": 41,
      "text": "- src/gov/launch/command.py  # gov launch's --gate-override and --gpu-need-mib options (P-1) [added, DEC-1088 (5)(b); DEC-1097 (8)]\n- tests/unit/launch/test_runs.py  # an open gate planted in its launch fixtures only (S19) [added, DEC-1088 (5)(b); DEC-1097 (8)]\n- tests/unit/launch/test_w1_28.py  # an open gate planted in its launch fixtures only (S19) [added, DEC-1088 (5)(b); DEC-1097 (8)]\n- tests/unit/launch/test_w1_32.py  # an open gate planted in its launch fixtures only (S19) [added, DEC-1088 (5)(b); DEC-1097 (8)]\n- tests/unit/launch/test_w2_136_plan_check.py  # an open gate planted in its launch fixtures only (S19) [added, DEC-1088 (5)(b); DEC-1097 (8)]\n- tests/unit/rebuild/test_w2_76_watch.py  # its machine-wide rebuild-lock default, now each tree its own (S7, DEC-1001 (d)) [added, DEC-1097 (8)]\n- tests/unit/rebuild/test_w2_76_lock_override.py  # the same [added, DEC-1097 (8)]\nkpis:\n  success:\n  - gov resources reads free memory, load, and every live Gov OS session on the machine from a machine-wide registry under ~/.gov-os/machine/, whichever repository started it.\n",
      "chunk_id": "4e8bcd655c11c29bb2c07076",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-r30l",
      "sha256": "67677faf2d4e65dfb6a6b42ed831ddf25bd481ea65d3ff3e48a3634210b82717",
      "path": ".tickets/DAEO-r30l.md",
      "start_line": 125,
      "end_line": 131,
      "text": "  - `gov resources` reads free memory, load, and every live Gov OS session on the machine from a machine-wide registry under `~/.gov-os/machine/`, whichever repository started it.\n  - The gate opens or shuts with a named reason.\n  - A stale entry (dead PID) is cleared [W2-M244, W2-M188, W2-M262].\n- **KPIs, failure:** a session in another repository counts against the gate; a start while the gate is shut is refused with the reading.\n- **DEC-747 (delegated, 2026-10-17):** `src/gov/check/commands.py` is in the paths for the one line that records `resources` (P-A). \"At most 8 sessions\" holds after the start: the start check adds the new session's weight (P-B). DEC-742's load value stands (P-C). P-B's \"at most 8\" superseded by DEC-942 item 1.\n\n**Entry criterion from W2-136's review (F2; DEC-803, the CTO, 2026-11-07):** before leads are routed through `gov launch`, the plan check reads the **current** tickets and the **approved** ready list (the main tree's, or a named path the dispatcher keeps), never a lead worktree's own copies, which can be stale (fails open otherwise); and an override is written to a launch log, not only to stderr (W2-136 F4). [DEC-1088]\n",
      "chunk_id": "4a14253941a52dc1ca820eaf",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "10402015239ea38d94df25fa",
      "sha256": "df4edbc782327ed3fee475628635a8459726808bef0ed08a0431221211a9878c",
      "path": "governance/project/orchestration/packages/AUDIT-GOV-FEATURES-1.md",
      "start_line": 478,
      "end_line": 504,
      "text": "### 4.9 The resource gate (`gate_check.py`, `disk_gate.sh`, `gate-config.json`, scratch budgets; DEC-898, DEC-942, DEC-947)\n\n- **Protects:**\n  - memory exhaustion and thrash: five leads started at once drove the load to 155 (owner, 10-29, `lead_chain2.sh` line 27);\n  - disk or inode exhaustion: an auditor hit ENOSPC at 98 % inodes (DEC-898).\n\n  **Needed now?** The disk gate and the budgets, yes. The memory arithmetic, only in a simpler form.\n- **Cost:**\n  - **Lead launches held by the gate: 12.2 h** in the 20 h from 10-29 16:30 to 10-30 13:00 (`log/chain-*.log`):\n    - load and memory together, 8.4 h;\n    - **memory alone, 3.2 h**, often with the CPU idle. On 10-30 at 12:52 the load was 2.1, against a need of 19.1 GB and 18.0 to 18.9 GB held;\n    - load alone, 0.5 h.\n  - **W2-57's brief gap:** the load gate held its starts from 19:30 to 22:20, 150 min.\n  - **Scratch budgets** stopped two leads' full runs (DEC-904). That led to the retention trial (DEC-905).\n  - **W2-20's built gate contradicts DEC-942 and DEC-947** (P-W2-20-SCOPE, DEC-950).\n  - **Owner decisions** with this as main reason, **9:** DEC-742, 776, 847, 898, 902, 904, 905, 942, 947.\n- **Caught:**\n  - **Real:** the disk inventory found a launcher regression that left 4.1 million inodes and 36 GiB behind (row W2-M405, DEC-902).\n  - **Real:** the budget's pressure cut a full run's footprint from 5,306,782 to 165,707 files (DEC-905).\n  - **None:** no OOM kill has been recorded since the watch began on 10-29 at 20:47 (`log/oom-watch.txt`).\n- **Standard practice:** a fixed cap on concurrent leads, measured once and re-measured weekly. A memory limit per session (cgroups), and alerting on disk and inodes. pytest's retention policy (in use).\n- **Recommendation:**\n  - **Keep** the disk gate and the scratch budgets.\n  - **Replace** the per-minute memory arithmetic with a fixed lead cap.\n  - Risk: an OOM kill under an unusual mix of work. Medium-low.\n  - Confidence: medium.\n\n",
      "chunk_id": "10402015239ea38d94df25fa",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "c8cccb0e22d571366270deed",
      "sha256": "96c5d5a0833c57d3fd5d70c3f119ba48bab278f88f2a775904576b059de640af",
      "path": "src/gov/resources/machine.py",
      "start_line": 313,
      "end_line": 320,
      "text": "def _window_rate(kept: list[dict], at: float, cpu: float) -> float | None:\n    \"\"\"A server's cores over the last minute from its kept samples (its current pid, at most ``KEEP_S`` old).\"\"\"\n    same = [s for s in kept if s[\"cpu_seconds\"] <= cpu and at > s[\"time\"]]\n    older = [s for s in same if at - s[\"time\"] >= WINDOW_S]\n    base = max(older, key=lambda s: s[\"time\"]) if older else (min(same, key=lambda s: s[\"time\"]) if same else None)\n    if base is None:\n        return None\n    return round(max(0.0, (cpu - base[\"cpu_seconds\"]) / (at - base[\"time\"])), 2)\n",
      "chunk_id": "c8cccb0e22d571366270deed",
      "routes": [
        "lexical",
        "code"
      ],
      "batch": 2
    },
    {
      "id": "00951cea6ec54784218f3848",
      "sha256": "a96f34e383543df119e62b685d3d8d8ade79e5d12b201069ab127bf2eb851b44",
      "path": "src/gov/resources/machine.py",
      "start_line": 14,
      "end_line": 38,
      "text": "  (``GOV_RESOURCES_DISK``, JSON ``{\"free_bytes\", \"free_inodes\"}``, else ``statvfs`` of HOME's disk); the processes\n  ``/proc/<pid>`` (``GOV_RESOURCES_PROC``); the GPU ``nvidia-smi`` on ``PATH``.\n- The own busy-cores sampling: two readings of the CPU counters; the earlier one is the newest sample at least a\n  minute old in ``~/.gov-os/machine/cpu-stat.json`` (each reading adds one), else the oldest at least a quarter of a\n  second old, else a reading a quarter of a second before.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport datetime\nimport json\nimport math\nimport os\nimport shutil\nimport subprocess\nimport tempfile\nimport time\nfrom pathlib import Path\n\nPAGE = os.sysconf(\"SC_PAGE_SIZE\") if hasattr(os, \"sysconf\") else 4096\nTICKS = os.sysconf(\"SC_CLK_TCK\") if hasattr(os, \"sysconf\") else 100\nCPU_HISTORY = \"cpu-stat.json\"\nSERVER_HISTORY = \"embedding-cpu.jsonl\"  # the servers' CPU samples, one JSON line per server per sample (review R2-F1)\nOLD_SERVER_HISTORY = \"server-cpu.json\"  # round 3's history: dropped at the next reading, never read\nSERVER_LINES = 600  # the lines kept of each server\n",
      "chunk_id": "00951cea6ec54784218f3848",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "0e7d0db240bf21751163325c",
      "sha256": "0321265bf20445582d24a8eb93f970ef485d9d76a5ef653d6da6506b2ed9d128",
      "path": "src/gov/resources/machine.py",
      "start_line": 1,
      "end_line": 15,
      "text": "\"\"\"The gate's readings of the machine (W2-20 S1, S2, S4, S5, S12, S13).\n\nEach reader returns ``(value, why)``: the value, or None with why it cannot be read. A reading that cannot be taken\nis never a default: the gate shuts on it, naming it (F5).\n\nSources, each replaceable for a planted machine:\n\n- memory ``/proc/meminfo`` (``GOV_RESOURCES_MEMINFO``: ``MemAvailable:`` in kB); load ``/proc/loadavg``\n  (``GOV_RESOURCES_LOADAVG``: fields 1 and 3); the processor count (``GOV_RESOURCES_NPROC``, else the machine's);\n  busy cores over the last minute (``GOV_RESOURCES_BUSY_CORES``, one number, else the gate's own sampling of\n  ``/proc/stat``, ``GOV_RESOURCES_STAT``); the embedding servers' CPU p95 (``GOV_RESOURCES_EMBEDDING_CPU``, JSON\n  ``{\"shared\": cores, \"query\": cores}``, else the gate's own sampling of the two servers) and their use over the\n  same last minute (``GOV_RESOURCES_EMBEDDING_CPU_NOW``, the same form; round 7, review F2); the shared disk\n  (``GOV_RESOURCES_DISK``, JSON ``{\"free_bytes\", \"free_inodes\"}``, else ``statvfs`` of HOME's disk); the processes\n  ``/proc/<pid>`` (``GOV_RESOURCES_PROC``); the GPU ``nvidia-smi`` on ``PATH``.\n",
      "chunk_id": "0e7d0db240bf21751163325c",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "bf186ed3abd2ff32a353d867",
      "sha256": "0bd2d9dc6b7f19e70c142bae7d8aa4d648a80a3a07872aa6fda9da328972489c",
      "path": "src/gov/resources/machine.py",
      "start_line": 283,
      "end_line": 300,
      "text": "def _read_samples(path: Path) -> list[dict]:\n    \"\"\"The servers' kept samples, oldest first; a line that is not ``{\"time\", \"server\", \"pid\", \"cpu_seconds\"}`` is\n    skipped (a sample only lengthens the window).\"\"\"\n    try:\n        text = path.read_text(encoding=\"utf-8\")\n    except (OSError, UnicodeDecodeError):\n        return []\n    out = []\n    for line in text.splitlines():\n        try:\n            item = json.loads(line)\n        except ValueError:\n            continue\n        if isinstance(item, dict) and item.get(\"server\") in (\"shared\", \"query\") and _number(item.get(\"time\")) \\\n                and isinstance(item.get(\"pid\"), int) and not isinstance(item[\"pid\"], bool) \\\n                and _number(item.get(\"cpu_seconds\")) and item[\"cpu_seconds\"] >= 0:\n            out.append({key: item[key] for key in (\"time\", \"server\", \"pid\", \"cpu_seconds\")})\n    return sorted(out, key=lambda s: s[\"time\"])\n",
      "chunk_id": "bf186ed3abd2ff32a353d867",
      "routes": [
        "code"
      ],
      "batch": 2
    },
    {
      "id": "d76ce7093778cb73ecad45e9",
      "sha256": "ec9155687622310df606d2283ce49bca01cafeae86b799907285e9fa21a6fd02",
      "path": "docs/changes/W2-20-evidence.md",
      "start_line": 52,
      "end_line": 66,
      "text": "| F10 | row, not this round | unchanged: the re-measure takes the largest kept sample; nothing samples on a schedule | \u2014 |\n\nThe four launch fixtures that plant an open gate (`test_runs.py`, `test_w1_28.py`, `test_w1_32.py`,\n`test_w2_136_plan_check.py`) and the resources fixture (`conftest.py`) now plant `GOV_RESOURCES_EMBEDDING_CPU_NOW` idle,\nas the designer's support does, so no unit case reads the real servers.\n\n**Round 3's runs (inside the sandbox, on `b6c6dad61` plus a style-only edit of `machine.py`; an empty `HOME` with only\nthe user site's `lib` linked in, since `gov accept` drops `PYTHON*` variables):**\n\n- `gov accept W2-20`: **168 passed, 0 failed, 1 skipped (169)**; every line passes but S16, whose one case skips (the\n  CTO's run outside the sandbox, `GOV_W2_20_MEASURE=1`). Round 7's new cases (the cpu rule, the frozen configuration\n  format) are green.\n- `gov accept W2-136`: **76 passed, 0 failed**.\n- Unit tests, `tests/unit/resources tests/unit/launch tests/unit/rebuild tests/unit/secrets_check` with `-m \"not\n  local_only\" -k \"not real and not green_here and not time_limit\"`: **375 passed** (202 opt-in rows deselected by\n",
      "chunk_id": "d76ce7093778cb73ecad45e9",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "6925cff86fc65e8eb4ef5608",
      "sha256": "e838a581dcd6fc7ca1abebdfd9f17419a788e9b2f7ae5183af4110b12497bcc6",
      "path": "src/gov/resources/machine.py",
      "start_line": 208,
      "end_line": 211,
      "text": "\n\n# --- the embedding servers' CPU p95 ---------------------------------------------------------------------------------\n\n",
      "chunk_id": "6925cff86fc65e8eb4ef5608",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "f8bbfd3c6b1f2971308ce8b2",
      "sha256": "9d7d6a58fdcb7613843ff9684756a2cbbf82cb0ef8944248bee415bd7285e6bd",
      "path": "src/gov/resources/machine.py",
      "start_line": 323,
      "end_line": 326,
      "text": "def _rates(samples: list[dict]) -> list[float]:\n    \"\"\"The rates between one server's consecutive samples of one process (oldest first).\"\"\"\n    return [(b[\"cpu_seconds\"] - a[\"cpu_seconds\"]) / (b[\"time\"] - a[\"time\"]) for a, b in zip(samples, samples[1:])\n            if a[\"pid\"] == b[\"pid\"] and b[\"time\"] > a[\"time\"] and b[\"cpu_seconds\"] >= a[\"cpu_seconds\"]]\n",
      "chunk_id": "f8bbfd3c6b1f2971308ce8b2",
      "routes": [
        "code"
      ],
      "batch": 2
    }
  ],
  "batches": [
    {
      "size": 10
    },
    {
      "size": 10
    }
  ],
  "merge": {
    "candidates": 20,
    "duplicates": 11,
    "dropped": [],
    "reranked": true
  },
  "rerank": {
    "by": "service",
    "device": "cuda:0",
    "reason": null
  },
  "expansions": [
    {
      "chunk_id": "7e9a45bf72d25f2dd35e87fe",
      "parent_id": "805586d1d649a866646f8f8a",
      "path": "src/gov/resources/machine.py",
      "start_line": 329,
      "end_line": 371
    },
    {
      "chunk_id": "c6818a0afbc0249d8fd5de54",
      "parent_id": "dc4d12a0e804a7abd380e743",
      "path": "src/gov/resources/machine.py",
      "start_line": 255,
      "end_line": 276
    },
    {
      "chunk_id": "7963c5035e08a67cf87b323a",
      "parent_id": "beee5aa4918720b7c0bd4b1d",
      "path": "docs/changes/W2-20-evidence.md",
      "start_line": 16,
      "end_line": 35
    },
    {
      "chunk_id": "10402015239ea38d94df25fa",
      "parent_id": "cb7e909ae6c8776b385b3879",
      "path": "governance/project/orchestration/packages/AUDIT-GOV-FEATURES-1.md",
      "start_line": 478,
      "end_line": 504
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "0fb77d30531b0150b3878cb9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "6f3c5439b4cfead0002b59aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/machine.py",
      "chunk_id": "504fe3d1f41ef106f89a20c6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/machine.py",
      "chunk_id": "c15fa49d77ad2e63ba791c6e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/machine.py",
      "chunk_id": "2a7926950b2272d898566c7b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "3cbfc1c6f0b4c7bffeaaf878",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "df8a3c6b85f42b8d5f24c125",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "82497daab714537dccd10313",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "1bf642f128c3a3738d7c2db2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "e3f050f7c7f6d3f33560cf2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "213f0c02b7aaa40127bbd43f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "63ba33081f31cfb82cce61bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "1f4fb10e2c09ba11e7666302",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "4e433d38c9370738dec705d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "91c433d34ab0f87811570d31",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "19f49b00a88a8f0fb42c62e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "9b0ebfe72ee53d6ed08dd309",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "6a9dee6e838a6b4ead5fa878",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "79b7aee9706b1ef29de0931e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "abc74248c32273f1c022bc7b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "b50a38f5aa04f8e33876061c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "1879d875a44a02135a1da4b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "5fbd2cd6062591b55ef8d6b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "6e2fd0c390e6a85d8ba60762",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "70eb80cab27469a298a9e078",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "992583b096faa736061be020",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "9f78a531a985c7c40ff3b892",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "8a85a05ab1db5296c4742994",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "c941ec1c25ffb656afea885c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "2cd7f700bf1a6234637b4cda",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "ccd2f7a9ecfe2fee02880502",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "4364c134b7f98007ccbc3386",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qzrq.md",
      "chunk_id": "cdab34041e630577c7616648",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "46fceeb40f98e5bccf1f6794",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/gate.py",
      "chunk_id": "6d270a9e0ca5a14ef4efd358",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "22703223eb3e7b9382b7c76c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "c9aa0d79c273843802efbc24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "cc22f8ec310fe1d07afc7ff9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "326fd3bb4e29cc2cc8bf155e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "8a6e46f4154e615748350033",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/gate.py",
      "chunk_id": "0e7fb4dfb8b4f43dbf47ca0d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "b19275fc1197d0c0783bd0c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/gate.py",
      "chunk_id": "8cf05a5241583fa58a07a718",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "fd2bb734568e19eda709960a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "67bc2bd6acb48777e26e0412",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "4d2d97f055b7b79b0349af8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "d716ca1263cfc5b275f158c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "fa33b9709e40bdc766fabd24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "829e18dbed19559dd991e947",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "cf99cd773ecf6cf6e1ed0830",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/gate.py",
      "chunk_id": "ba3696eb734da6412ac59fdd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "42e80ceb79a3cd97e7e8ea17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "e3041d9aa07ce40f496415cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/__init__.py",
      "chunk_id": "83a0de7a3d44e5c207b86b18",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "fbb87d3428c4a8f1a58ac847",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "811879e131ea11204daf866a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "51cdf04f086bd965e6557aad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "4512cf1352b45b0d0d7360bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "a20425c204636d39eee4006d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "163301d7882f68794ce6adce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "96a258d998cbcecc889b1ac4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "480cd7c247896c096c5c2505",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "ebfa652825450cbc39df982e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "c64723aa865f59358d475c04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "12ae53c0f0df4b639a6ef1f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "63a51e9f7ae879d8602d707f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/command.py",
      "chunk_id": "7ddb588616bf3bc91ca74bc0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "9137858e4a6751c80914ac61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1/resources_sample_day_v2.sh",
      "chunk_id": "94ba7597246222d8bc04695a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "e753b8925f988bef182f0415",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/gate.py",
      "chunk_id": "9b9966fd03f612c9eee92296",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "b6974b8d38e8c248902d40bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/03-run-time-tool.md",
      "chunk_id": "bde530902ed7b51539770ef5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "6f7ee57752d2d10479d97ac7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "645727983f72f21b14160b74",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "abfb4e8951aebeeef0852243",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-157-evidence.md",
      "chunk_id": "20eff8c8ff34c1423c97ec59",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "24d7f93984de9b88d50dd193",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-123-evidence.md",
      "chunk_id": "865fdc51b597061315421ff2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "a1c9ca78d1c305865623ce7e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "69c2768a6f0927a3e8dba390",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "e854d0972b13f6cc03767a1e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "0668c5aadeeab0fd0baad35a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "7591c66df3fa654bde5cc8ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "48ca053bb7794ab0838a14ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "81c73ec6956191c300e304cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "ff0dba24a0dd8134ba1ac438",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "f470bbf48eb9fc8f5ae2ed22",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "f57558a8221a57b1560a4a50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r30l.md",
      "chunk_id": "150d61513b1cb0dc93b901e0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "3ac9b63444a1aae7ee9c0286",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/gate.py",
      "chunk_id": "b888d3ca453af6084056dd1a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "60f6798d6fca501b58ac067e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/C.md",
      "chunk_id": "288fdc3bcd9d7ac420b9cc2c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/gate.py",
      "chunk_id": "2f05b7ecf6ec03538ab95692",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/gate.py",
      "chunk_id": "63d55ff57b6793641f00af62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/gate.py",
      "chunk_id": "8046d99b85f618ca6de37c0d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/gate.py",
      "chunk_id": "bb2f4aea9b45bb4904b36620",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "bb44a5b0a5bb338b68e0d461",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/gate.py",
      "chunk_id": "e80ce8dce3ef545aac468ced",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "c583704a2427a44095534f08",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-20-evidence.md",
      "chunk_id": "bdcc3ff91bdb24e6967c1a55",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wnnz.md",
      "chunk_id": "95203c37505af1e3c4cbe0f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/machine.py",
      "chunk_id": "e45534534689a41f38ca32c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md",
      "chunk_id": "ff1f559ab60fd2b85bbaea13",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "chunk_id": "a126fd950a097eee22c23b2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "183b1d186fb05909dbd0f730",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "ea4e2fd80be55d763e007bc0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "70d21656b4e04d06a1c27a40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/test_w2_20_stale_samples.py",
      "chunk_id": "cde11c1b0cf14066ada93559",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "252ff6ba81959c017d451ed9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/E-roles-context.md",
      "chunk_id": "944f846c9f76901e3363c487",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "3c6ba15cf80c5af7de5f0e57",
      "reason": "NOT_GATHERED"
    }
  ],
  "facets": {
    "lexical": {
      "available": true,
      "reason": null
    },
    "semantic": {
      "available": true,
      "reason": null
    },
    "code": {
      "available": true,
      "reason": null
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5649
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLXIzMGwubWQiLDMyLDQxLCI0ZThiY2Q2NTVjMTFjMjliYjJjMDcwNzYiXSxbIi50aWNrZXRzL0RBRU8tcjMwbC5tZCIsMTI1LDEzMSwiNGExNDI1Mzk0MWE1MmRjMWNhODIwZWFmIl0sWyJkb2NzL2NoYW5nZXMvVzItMjAtZXZpZGVuY2UubWQiLDQ0LDQ0LCI5YWQ4MjQ2MjYxYWI5MjVhMzFlYmYyNDgiXSxbImRvY3MvY2hhbmdlcy9XMi0yMC1ldmlkZW5jZS5tZCIsNTIsNjYsImQ3NmNlNzA5Mzc3OGNiNzNlY2FkNDVlOSJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9GSU5ESU5HUy5tZCIsMzYsMzYsImRmMDM1M2Y3ZDc1MmI3YWFhNTQ0YWQ3MiJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vcGFja2FnZXMvTE9BRC1CQUxBTkNFUi0xLm1kIiw1Miw1NiwiY2RjNjliYjhlY2ZmMGNmNDQzZjRjMzlhIl0sWyJnb3Zlcm5hbmNlL3Byb2plY3Qvb3JjaGVzdHJhdGlvbi9wYWNrYWdlcy9MT0FELUJBTEFOQ0VSLTEubWQiLDkxLDEwNSwiYjEwMTRjNjVhM2EwZDk5M2Q2NTFjZThkIl0sWyJzcmMvZ292L3Jlc291cmNlcy9tYWNoaW5lLnB5IiwxLDE1LCIwZTdkMGRiMjQwYmYyMTc1MTE2MzMyNWMiXSxbInNyYy9nb3YvcmVzb3VyY2VzL21hY2hpbmUucHkiLDE0LDM4LCIwMDk1MWNlYTZlYzU0Nzg0MjE4ZjM4NDgiXSxbInNyYy9nb3YvcmVzb3VyY2VzL21hY2hpbmUucHkiLDIwOCwyMTEsIjY5MjVjZmY4NmZjNjVlOGViNGVmNTYwOCJdLFsic3JjL2dvdi9yZXNvdXJjZXMvbWFjaGluZS5weSIsMjY4LDI3NiwiYTEzMGZhN2I3ODUxZTQ4NDkxODQwZDRjIl0sWyJzcmMvZ292L3Jlc291cmNlcy9tYWNoaW5lLnB5IiwyODMsMzAwLCJiZjE4NmVkM2FiZDJmZjMyYTM1M2Q4NjciXSxbInNyYy9nb3YvcmVzb3VyY2VzL21hY2hpbmUucHkiLDMxMywzMjAsImM4Y2NjYjBlMjJkNTcxMzY2MjcwZGVlZCJdLFsic3JjL2dvdi9yZXNvdXJjZXMvbWFjaGluZS5weSIsMzIzLDMyNiwiZjhiYmZkM2M2YjFmMjk3MTMwOGNlOGIyIl0sWyJzcmMvZ292L3Jlc291cmNlcy9tYWNoaW5lLnB5IiwzNDksMzY2LCJlZTM5YTk2ZGIzMWEyYjg3NjYwNDY2NzgiXSxbInNyYy9nb3YvcmVzb3VyY2VzL21hY2hpbmUucHkiLDM2NSwzNzEsImI3NWZiMTU0NTQ2MzM1MDMzZDc5YTZmYiJdXSwiZiI6Ii9ob21lL3VzYWluL2dvdi1vcy13b3JrdHJlZXMvVzItMDAtc3RvcmUtYSIsImkiOltdLCJvIjoyMCwicCI6eyJiIjoic2VydmljZSIsImQiOiJjdWRhOjAiLCJoIjoiMDM0NDg1YzcxMzIwNzJjMSIsIm8iOlszLDAsMiw3LDM4LDI0LDExLDEwLDMzLDM2LDQsMSw1LDgsMTUsNiwxOSw5LDE4LDE2LDI3LDEzLDIyLDI4LDI1LDIxLDMxLDIzLDM1LDM0LDM3LDMyLDM5LDE0LDEyLDMwLDI2LDI5LDE3LDIwXX0sInEiOiJIb3cgZG9lcyB0aGUgcmVzb3VyY2UgZ2F0ZSBzYW1wbGUgdGhlIGVtYmVkZGluZyBzZXJ2ZXJzJyBDUFUgKG1hY2hpbmUucHkgX3NhbXBsZV9zZXJ2ZXJzLCBfd2luZG93X3JhdGUsIHRyZWUsIGtlcHQgc2FtcGxlcywgY3B1IHJlYWRpbmcgbnVsbCkgYW5kIHdoaWNoIHRlc3RzIHJ1biBnb3YgbGF1bmNoIGFnYWluc3QgdGhlIHJlYWwgZ2F0ZT8gQ29kZSBsb2NhdGlvbnMsIGNvbnZlbnRpb25zLCBlYXJsaWVyIGZpeGVzIGFuZCBmaW5kaW5ncy4iLCJyIjowLCJzIjoiNDg1NmMxZmVmNmVlZDk1N2Q2ZWZlZWM4N2Y4N2I2YTRhNjg5ZjM3NSIsInQiOm51bGwsIngiOlsiODA1NTg2ZDFkNjQ5YTg2NjY0NmY4ZjhhIiwiYmVlZTVhYTQ5MTg3MjBiN2MwYmQ0YjFkIiwiY2I3ZTkwOWFlNmM4Nzc2YjM4NWIzODc5IiwiZGM0ZDEyYTBlODA0YTdhYmQzODBlNzQzIl19",
  "routing": {
    "code": [
      "7e9a45bf72d25f2dd35e87fe",
      "c6818a0afbc0249d8fd5de54"
    ],
    "named": [],
    "phrasings": [
      "How does the resource gate sample the embedding servers' CPU (machine.py _sample_servers, _window_rate, tree, kept samples, cpu reading null) and which tests run gov launch against the real gate? Code locations, conventions, earlier fixes and findings.",
      "resource gate sample embedding servers CPU machine.py _sample_servers _window_rate tree kept samples cpu reading null tests run gov launch against real gate Code locations conventions earlier fixes findings."
    ]
  },
  "pool": {
    "settings": {
      "meaning_uncut": true,
      "route_depth": 60,
      "rerank_depth": 40,
      "per_file_first10": 2,
      "drop_nested": true
    },
    "reranked": 40,
    "order": "first",
    "nested": [
      {
        "chunk_id": "b75fb154546335033d79a6fb",
        "path": "src/gov/resources/machine.py",
        "start_line": 365,
        "end_line": 371
      },
      {
        "chunk_id": "ee39a96db31a2b8766046678",
        "path": "src/gov/resources/machine.py",
        "start_line": 349,
        "end_line": 366
      },
      {
        "chunk_id": "a130fa7b7851e48491840d4c",
        "path": "src/gov/resources/machine.py",
        "start_line": 268,
        "end_line": 276
      }
    ]
  }
}
```
