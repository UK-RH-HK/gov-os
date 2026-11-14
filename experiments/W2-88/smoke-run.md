---
id: W2-88b-smoke-run
type: evidence
status: ACTIVE
state_class: EVIDENCE
task: DAEO-aks1
decisions_applied: [DEC-1176, DEC-1150, DEC-728]
---
# W2-88b: gov adopt's smoke run on copies of redis/redis and grafana/grafana

Record state: **final** (batch 2 of 2; written 2026-11-14 from the logs). Both copies have finished: redis (batch 1) and grafana (batch 2). grafana's A6, A8 and A9 rows and its end HEAD, pending in batch 1, are filled in from its logs.

## What this is

The smoke run tests only whether gov adopt works on repositories different from this one, small and large, and where it fails. **No questions, no measure, no validation.** It holds no question set and no quality figure, and draws no conclusion on memory's quality. A9's own `measure` block (no question set was given) and its `scale` block stay in A9's record in the copy and are not copied here.

Owner decision: DEC-1176 (the re-scoping to a smoke run), DEC-1150 (the copies live outside this repository), DEC-728. Ticket: DAEO-aks1 (W2-88b).

## Where

The copies are under `~/gov-os-runs/W2-88b/<name>/` (the folder the guard gives this ticket, P2 (a)): `/home/usain/gov-os-runs/W2-88b/redis/` and `/home/usain/gov-os-runs/W2-88b/grafana/`. They are never committed in this repository and never pushed. No workbench, no `~/workspace`, no EXAMIN repository was read or cloned for this record. The stage logs are in `~/gov-os-runs/W2-88b/<name>-logs/` (`stages.tsv`, one `<label>.log` and `<label>.log.time` per stage run, `setup.log`, the driver's lines), gov's outputs in `~/gov-os-runs/W2-88b/<name>-out/`.

How each stage was run. The lead ran every stage on the two copies outside the sandbox, through the driver `stages.sh` (kept in the lead's scratch, not committed). Each stage runs as `setsid /usr/bin/time -o <label>.log.time -f "maxrss_kb=%M elapsed_s=%e" bash heavy_slot.sh gov adopt --lite ...` with `PYTHONPATH=<this worktree>/src`, so every stage went through `heavy_slot.sh` (a slot's wait is a wait; only the log of grafana's first, stopped A6 run, `A6-stopped-1.log`, shows one, below) and under the driver's memory watchdog (MemAvailable under 1,572,864 kB kills the stage's process group and the log then has a `watchdog:` line; no log in either copy has one). The driver polls the stage every 5 s, so the start-to-end span of a short stage is 5 s or more even where `/usr/bin/time`'s elapsed figure is a fraction of a second; both are given. The `/usr/bin/time` peak is, in the logs' words, "the stage's process tree's largest process". Every stage ran with `--session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1`.

Before MA the lead committed the adopter's input in each copy (not a gov stage): `governance/project/path-map.yaml` (sha256 `5f72c86362eebb895fe9dcbbd733709ec565422eb4f5b946d760a4d5b7ca48cb`, as the auditors' verdicts record it), with one namespace `all` holding `'**'`, `embedding_policy: embedded`, and code intelligence on. The adopter's proposal for A3 (`--map`) is `artefacts: []` (no action). MA-at-A3 is MA run a second time at A2's head, because A3's `--assessment` must hold the assessment of HEAD's commit; it has its own row, between A2 and A3, as the input to A3 and not one of the ten stage rows; S2's MA row is the first MA run.

## redis/redis

- Clone path: `/home/usain/gov-os-runs/W2-88b/redis/`
- Origin URL: `https://github.com/redis/redis.git`
- Pinned commit: `ee8e7f70152404649ac947157fd662d11b4a00d5`
- Copy's HEAD at the end of the run: `e4d21da2cd7522ffcf2de4a2b9ccadd5c970fc47` (A8's commit, `gov adopt --lite A8: legacy import and retirement`; A9 failed and made no commit)
- Tracked files at the pin: 1961 (`git ls-tree -r --name-only <pin>`); MA counts 1962 at the path-map commit, which adds `governance/project/path-map.yaml`
- Licence: `LICENSE.txt`, sha256 `4a0e416b9537688f30dfe69ddaceb2ca64d96b7df02a0a6760d376890ddc4e40`. Its first lines name a tri-licensing model for Redis 8 and later: the Redis Source Available License v2 (RSALv2), the Server Side Public License v1 (SSPLv1) and the GNU Affero General Public License v3 (AGPLv3), at the contributor's choice; Redis Open Source 7.2 and prior remain under the BSD 3-clause licence (as the file says, referenced in `REDISCONTRIBUTIONS.txt`). Language: C, with vendored `deps/`.
- Path map commit: `db81b792f3e7db886d314618d7721845ba92e735`

Stage table (wrapper as above; exit codes are the logs' `exit_code:` lines):

| stage | exact command | exit code | start (UTC) | end (UTC) | wall-clock s (start to end) | elapsed s (`/usr/bin/time`) | peak RSS kB (`/usr/bin/time`); gov's own peak where it printed one | outcome |
|---|---|---|---|---|---|---|---|---|
| MA | `gov adopt --lite --stage MA --out /home/usain/gov-os-runs/W2-88b/redis-out/ma --root /home/usain/gov-os-runs/W2-88b/redis --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:28:20+00:00 | 2026-11-14T01:28:42+00:00 | 22 | 18.72 | 63916; gov printed peak_rss_bytes 36339712 | completed |
| A0 | `gov adopt --lite --stage A0 --root /home/usain/gov-os-runs/W2-88b/redis --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:28:42+00:00 | 2026-11-14T01:28:47+00:00 | 5 | 0.14 | 30024 | completed |
| A1 | `gov adopt --lite --stage A1 --root /home/usain/gov-os-runs/W2-88b/redis --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:28:47+00:00 | 2026-11-14T01:28:52+00:00 | 5 | 0.23 | 32564 | completed |
| A2 | `gov adopt --lite --stage A2 --root /home/usain/gov-os-runs/W2-88b/redis --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:28:52+00:00 | 2026-11-14T01:28:57+00:00 | 5 | 0.38 | 37620 | completed |
| MA-at-A3 (input to A3, not one of the ten rows) | `gov adopt --lite --stage MA --out /home/usain/gov-os-runs/W2-88b/redis-out/ma-at-a3 --root /home/usain/gov-os-runs/W2-88b/redis --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:28:57+00:00 | 2026-11-14T01:29:18+00:00 | 21 | 19.64 | 63660; gov printed peak_rss_bytes 35770368 | completed |
| A3 | `gov adopt --lite --stage A3 --map /home/usain/gov-os-runs/W2-88b/redis-out/proposal.yaml --assessment /home/usain/gov-os-runs/W2-88b/redis-out/ma-at-a3 --root /home/usain/gov-os-runs/W2-88b/redis --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:29:18+00:00 | 2026-11-14T01:29:23+00:00 | 5 | 0.53 | 38704 | completed |
| A4 | `gov adopt --lite --stage A4 --root /home/usain/gov-os-runs/W2-88b/redis --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:29:23+00:00 | 2026-11-14T01:29:28+00:00 | 5 | 0.72 | 39400 | completed |
| A5 | `gov adopt --lite --stage A5 --verdict docs/audit/A5-path-map-verdict.md --root /home/usain/gov-os-runs/W2-88b/redis --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:44:43+00:00 | 2026-11-14T01:44:48+00:00 | 5 | 0.71 | 39168 | completed; verdict file `docs/audit/A5-path-map-verdict.md`, its commit in the copy `934b70218e6b43aac99c0da90ce131331d017700` (Role: independent-auditor alone), auditor session `4156cef7-6882-4672-89fe-5875c13ed3e1` |
| A6 | `gov adopt --lite --stage A6 --root /home/usain/gov-os-runs/W2-88b/redis --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:44:48+00:00 | 2026-11-14T01:45:52+00:00 | 64 | 58.33 | 805872 | completed |
| A8 | `gov adopt --lite --stage A8 --root /home/usain/gov-os-runs/W2-88b/redis --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:45:52+00:00 | 2026-11-14T01:46:28+00:00 | 36 | 32.39 | 806628 | completed |
| A9 | `gov adopt --lite --stage A9 --out /home/usain/gov-os-runs/W2-88b/redis-out/a9 --root /home/usain/gov-os-runs/W2-88b/redis --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 1 | 2026-11-14T01:46:28+00:00 | 2026-11-14T01:47:16+00:00 | 48 | 43.89 | 806012 | failed (finding F-1) |

All ten stages were reached; A9, the last, failed (F-1). Nothing follows A9, so no row is "not reached".

## grafana/grafana

- Clone path: `/home/usain/gov-os-runs/W2-88b/grafana/`
- Origin URL: `https://github.com/grafana/grafana.git`
- Pinned commit: `a00ff430d41e74022eb54361c9741e224e150021`
- Copy's HEAD at the end of the run: `140042f023c543f2a2fb3c139b5f6dbb063198a2` (A8's commit, `gov adopt --lite A8: legacy import and retirement`; read with `git -C /home/usain/gov-os-runs/W2-88b/grafana rev-parse HEAD`; A9 failed and made no commit; the copy is clean)
- Tracked files at the pin: 24619 (`git ls-tree -r --name-only <pin>`); MA counts 24620 at the path-map commit. Go and TypeScript.
- Licence: `LICENSE`, sha256 `0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0`. Its first lines read "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3, 19 November 2007" (AGPL-3.0).
- Path map commit: `da759782f8fcbb6c034f80f35b5ab9f587c55714`

Stage table (wrapper as above; exit codes are the logs' `exit_code:` lines):

| stage | exact command | exit code | start (UTC) | end (UTC) | wall-clock s (start to end) | elapsed s (`/usr/bin/time`) | peak RSS kB (`/usr/bin/time`); gov's own peak where it printed one | outcome |
|---|---|---|---|---|---|---|---|---|
| MA | `gov adopt --lite --stage MA --out /home/usain/gov-os-runs/W2-88b/grafana-out/ma --root /home/usain/gov-os-runs/W2-88b/grafana --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:28:22+00:00 | 2026-11-14T01:30:59+00:00 | 157 | 157.16 | 210308; gov printed peak_rss_bytes 52256768 | completed |
| A0 | `gov adopt --lite --stage A0 --root /home/usain/gov-os-runs/W2-88b/grafana --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:30:59+00:00 | 2026-11-14T01:31:04+00:00 | 5 | 0.27 | 83060 | completed |
| A1 | `gov adopt --lite --stage A1 --root /home/usain/gov-os-runs/W2-88b/grafana --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:31:04+00:00 | 2026-11-14T01:31:09+00:00 | 5 | 1.84 | 82800 | completed |
| A2 | `gov adopt --lite --stage A2 --root /home/usain/gov-os-runs/W2-88b/grafana --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:31:09+00:00 | 2026-11-14T01:31:14+00:00 | 5 | 3.76 | 145156 | completed |
| MA-at-A3 (input to A3, not one of the ten rows) | `gov adopt --lite --stage MA --out /home/usain/gov-os-runs/W2-88b/grafana-out/ma-at-a3 --root /home/usain/gov-os-runs/W2-88b/grafana --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:31:14+00:00 | 2026-11-14T01:33:57+00:00 | 163 | 159.79 | 211424; gov printed peak_rss_bytes 51621888 | completed |
| A3 | `gov adopt --lite --stage A3 --map /home/usain/gov-os-runs/W2-88b/grafana-out/proposal.yaml --assessment /home/usain/gov-os-runs/W2-88b/grafana-out/ma-at-a3 --root /home/usain/gov-os-runs/W2-88b/grafana --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:33:57+00:00 | 2026-11-14T01:34:07+00:00 | 10 | 5.79 | 155568 | completed |
| A4 | `gov adopt --lite --stage A4 --root /home/usain/gov-os-runs/W2-88b/grafana --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:34:07+00:00 | 2026-11-14T01:34:18+00:00 | 11 | 8.53 | 165468 | completed |
| A5 | `gov adopt --lite --stage A5 --verdict docs/audit/A5-path-map-verdict.md --root /home/usain/gov-os-runs/W2-88b/grafana --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T01:47:29+00:00 | 2026-11-14T01:47:41+00:00 | 12 | 7.93 | 165460 | completed; verdict file `docs/audit/A5-path-map-verdict.md`, its commit in the copy `c5edaf78c2806279ed504f9b7de581793735d54b` (Role: independent-auditor alone), auditor session `fddde1db-ec8c-42b4-ad7a-481c33b8e9b9` |
| A6 | `gov adopt --lite --stage A6 --root /home/usain/gov-os-runs/W2-88b/grafana --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T04:00:21+00:00 | 2026-11-14T11:26:10+00:00 | 26749 | 26747.32 | 6617236 | completed (the run after the stopped first one, see the note below the table; O-4) |
| A8 | `gov adopt --lite --stage A8 --root /home/usain/gov-os-runs/W2-88b/grafana --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 0 | 2026-11-14T11:26:10+00:00 | 2026-11-14T11:30:12+00:00 | 242 | 237.50 | 6679012 | completed |
| A9 | `gov adopt --lite --stage A9 --out /home/usain/gov-os-runs/W2-88b/grafana-out/a9 --root /home/usain/gov-os-runs/W2-88b/grafana --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` | 1 | 2026-11-14T11:30:12+00:00 | 2026-11-14T11:30:25+00:00 | 13 | 5.86 | 165460 | failed (finding F-3) |

All ten stages were reached; A9, the last, failed (F-3). Nothing follows A9, so no row is "not reached". The wall-clock figures are the stage's start to end from `stages.tsv` (A6: 04:00:21 to 11:26:10 is 26,749 s; A8: 11:26:10 to 11:30:12 is 242 s; A9: 11:30:12 to 11:30:25 is 13 s); the elapsed and peak figures are `/usr/bin/time`'s, from each stage's `.log.time` file.

**A6's first run was stopped by the lead's own harness, not by gov.** The first post driver (`grafana-logs/post-driver.log`) ran A6 from 2026-11-14T01:47:41+00:00. About 2026-11-14T03:59Z the lead's tool harness stopped it: its 2-hour limit on a background command killed the driver `stages.sh` and the stage's process tree. gov gave no exit code and printed no refusal. Its log is kept as `grafana-logs/A6-stopped-1.log` (the lead appended a `--- stopped ---` part saying this, and that the rebuild's `record.json` was last written 2026-11-14T03:54:07Z with `stage_running` secrets and `stage_running_s` 7104.4); `stages.tsv` has no row for it, and it is not A6's row above. The copy afterwards: HEAD `c6c22a0bfa3ad3e055d4682fc3ace13726958f42` (A5's commit), clean. This is an interruption of the lead's tooling; it is not a gov failure and not a finding against gov. A6 was then re-run from the same HEAD by the driver's `a6-on` phase (`stages.sh grafana a6-on`, detached from the harness; the driver's lines in `grafana-logs/post2-driver.log`, pid `501155` in `post2.pid`, `post2.exit` holds 1 for A9's exit code), which ran A6, A8 and A9 in turn and stopped after A9 (rc 1).

MA's own `estimate` block for grafana (gov's figures, `grafana-out/ma/memory-assessment.json`; not mine): `peak_rss_bytes` 38,447,071,380 (about 38.4 GB) against `free_memory_bytes` 16,303,906,816 (about 16.3 GB, read at MA's run; the lead's brief said about 15 GB, the log's figure is quoted); `estimated_nodes` 1,351,658, `estimated_edges` 4,722,026, `chunks` 222,176, `disk_bytes` 4,207,145,416, `index_seconds` 9,958; `envelope.within`: false (DEC-078's envelope: 80,000 nodes, 270,000 edges, 2,200,000,000 bytes). MA estimated a peak above what the machine had free. The memory watchdog never fired on grafana (no `watchdog:` line in any of its logs). The `/usr/bin/time` peaks of the stages that ran are A6 6,617,236 kB and A8 6,679,012 kB (`stages.tsv`). The stage that would build the full memory store did not get that far: A9 stopped at its git step (F-3) before any rebuild, with a peak of 165,460 kB. So this run gives no answer on whether MA's estimate holds, and no conclusion is drawn from it.

For comparison, MA's `estimate` block for redis: `peak_rss_bytes` 2,289,896,370, `free_memory_bytes` 16,539,521,024, `estimated_nodes` 78,617, `estimated_edges` 274,649, `chunks` 24,369, `index_seconds` 1,037, `envelope.within`: false.

## Findings

Each is a finding for the owner, returned by the lead as a candidate row or package. None is fixed here (the smoke run fixes nothing).

### F-1: redis, stage A9, exit 1, `FABRIC_INCOMPLETE`

- Stage and command: A9, `gov adopt --lite --stage A9 --out /home/usain/gov-os-runs/W2-88b/redis-out/a9 --root /home/usain/gov-os-runs/W2-88b/redis --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` (no question set given).
- Exit code: 1. Refusal code gov printed: `FABRIC_INCOMPLETE`.
- Error text (gov's output, every line the log holds, `redis-logs/A9.log`):
  ```
  semantic: 1 file(s) hold a chunk over 10000 characters, embedded from its first 10000: deps/jemalloc/doc_internal/jemalloc.svg
  gov adopt: FABRIC_INCOMPLETE: a store the path map calls for was not built: codegraph (codegraph: RuntimeError: codebase-memory-mcp query_graph failed (exit code 0))
  ```
- Time run: 2026-11-14T01:46:28+00:00 to 2026-11-14T01:47:16+00:00 (48 s start to end; 43.89 s elapsed by `/usr/bin/time`); peak 806012 kB (`/usr/bin/time`).
- File or path the error names: none in the error line; the `semantic:` line before it (a warning, O-1) names `deps/jemalloc/doc_internal/jemalloc.svg`. The refusal is raised at `src/gov/adopt/fabric.py:705-708`.
- What the rebuild's own record shows (`redis/.gov-runtime/rebuild/record.json`, written 2026-11-14T01:46:58Z, read only): `timing` record_s 1.4, lexical_s 0.5, secrets_s 3.3, semantic_s 0.3, codeintel_s 22.3, compaction_s 1.3, total_s 27.2; `stages_done` lists record, lexical, semantic, codeintel and compaction; `stage_running` null; `watchdog_faults` empty; the record names no store as not built and holds no codegraph error text. `redis-out/a9/` is empty. The stages A6 and A8 on this copy reported the rebuild's `codeintel` store `recreated` (their logs) and exited 0.
- State left: A9 made no commit; the copy's HEAD is A8's commit `e4d21da2cd7522ffcf2de4a2b9ccadd5c970fc47`.
- The error text says "exit code 0" in a message about a failure; that is gov's own wording, quoted as printed.

### F-2: A5's verdict has no named path; the first one chosen was refused by the guard (run 3)

This is not a stage failure: no A5 stage ran in run 3 with a refused verdict.

- A first pair of fresh independent-auditor sessions (redis `4e66e97f-fbd1-46f5-a78c-7ee5fd58cd4c`, grafana `e9403ce5-c537-4022-bc48-47f4b71f78da`) both judged the path map a pass but could not write the verdict: the briefs placed it at `governance/reviews/A5-path-map-verdict.md` in the copy, and this repository's PreToolUse hook (`.claude/hooks/pretooluse.py`, rule 5, DEC-953 item 2, lines 1093-1102) refused the write: "a reviewer or auditor writes only its own review or audit record (docs/probes/, docs/audit/, docs/assessment/, .gov-runtime/scratch/orchestrator/reviews/), its own scratch, or /tmp".
- gov adopt fixes no verdict path: `--verdict <path>` takes any path (`src/gov/adopt/stages.py`, `_verdict` and `a5`, lines 432-461), and the adopt skill (`template/governance/kernel/skills/adopt/SKILL.md`) names the Independent Auditor's role for A5 (line 24) and a `--verdict <path>` for A7 and A10 (line 41) but no place where the auditor's verdict goes. Neither gov adopt nor the skill says where the verdict is written, and the first place chosen was refused by the guard.
- Run 4 placed it under `docs/audit/`, which the hook allows. The accepted verdicts: redis, commit `934b70218e6b43aac99c0da90ce131331d017700`, auditor session `4156cef7-6882-4672-89fe-5875c13ed3e1`, verdict pass, path map hash `6f9a287a72ac1062f1103651205e35d56ff74a810cdef715640a52e991f94d5a`; grafana, commit `c5edaf78c2806279ed504f9b7de581793735d54b`, auditor session `fddde1db-ec8c-42b4-ad7a-481c33b8e9b9`, verdict pass, path map hash `ee5bcc474a0929c4fc8c07ead1c5757c52e55e706409acb68998227b328c4e60`. Each is committed in its copy as `docs/audit/A5-path-map-verdict.md` with `Role: independent-auditor` alone (`git log -1 --format='%H %(trailers:key=Role,valueonly)'`), and each auditor session differs from the session every stage ran under.
- Finding for the owner: name the verdict's path (for A5, and for A7 and A10 alike) in the skill or in gov's output, in a place the guard lets an auditor write.

### F-3: grafana, stage A9, exit 1, `ADOPT_GIT_FAILED`: the adopted repository's own `.gitignore` ignores a path gov adopt writes and commits

- Stage and command: A9, `gov adopt --lite --stage A9 --out /home/usain/gov-os-runs/W2-88b/grafana-out/a9 --root /home/usain/gov-os-runs/W2-88b/grafana --session lead-ac1f3754-57cb-46aa-99c0-37884f8ab5a1` (no question set given).
- Exit code: 1. Refusal code gov printed: `ADOPT_GIT_FAILED`.
- Error text (gov's output, as `grafana-logs/A9.log` holds it, one line):
  ```
  gov adopt: ADOPT_GIT_FAILED: git --literal-pathspecs add -- .claude/skills/retrieval/SKILL.md .claude/skills/discovery/SKILL.md governance/kernel/templates/brief.md governance/kernel/templates/role-cto.md governance/project/retrieval.yaml failed in /home/usain/gov-os-runs/W2-88b/grafana: The following paths are ignored by one of your .gitignore files: .claude/skills/discovery .claude/skills/retrieval hint: Use -f if you really want to add them. hint: Turn this message off by running hint: "git config advice.addIgnoredFile false"
  ```
- Time run: 2026-11-14T11:30:12+00:00 to 2026-11-14T11:30:25+00:00 (13 s start to end; 5.86 s elapsed by `/usr/bin/time`); peak 165460 kB (`/usr/bin/time`).
- What A9 tried to add: five paths, in `git --literal-pathspecs add --`: `.claude/skills/retrieval/SKILL.md`, `.claude/skills/discovery/SKILL.md`, `governance/kernel/templates/brief.md`, `governance/kernel/templates/role-cto.md` and `governance/project/retrieval.yaml`.
- File or path the error names: `.claude/skills/discovery` and `.claude/skills/retrieval`, as "ignored by one of your .gitignore files". The error does not name the ignore file. Read-only checks on the copy: `git -C /home/usain/gov-os-runs/W2-88b/grafana check-ignore -v .claude/skills/retrieval/SKILL.md` prints `.gitignore:84:.claude/skills/*	.claude/skills/retrieval/SKILL.md`, and the same for `.claude/skills/discovery/SKILL.md`: the rule is grafana's own `.gitignore`, line 84, `.claude/skills/*` (line 84 read with `sed -n 84p`).
- State left: gov left nothing behind. None of the five files exists in the copy (`ls` on each: no such file); `git status --short --ignored -- .claude governance` prints nothing; `grafana-out/a9/` is empty; A9 made no commit; the copy's HEAD is A8's commit `140042f023c543f2a2fb3c139b5f6dbb063198a2`, clean.
- This is not redis's F-1: a different copy, a different refusal code and a different cause. redis's A9 reached the rebuild and refused with `FABRIC_INCOMPLETE`; grafana's A9 refused at its git step, before any rebuild. Neither is fixed here.
- Finding for the owner: gov adopt A9 writes and commits paths (`.claude/skills/...`) that an adopted repository's own `.gitignore` may ignore, and it stops with `ADOPT_GIT_FAILED` instead of handling the rule. Whether to adapt gov's A9 to such a rule, or to name the condition in the skill or the stage's preconditions, is the owner's decision.

### Observations that are not failures

- **O-1, redis, A6, A8 and A9: a chunk over its size limit.** gov printed on each: `semantic: 1 file(s) hold a chunk over 10000 characters, embedded from its first 10000: deps/jemalloc/doc_internal/jemalloc.svg`. A6's and A8's results carry the same as `semantic.cut` (limit 10000, count 1, that path). MA lists the same file under `minified` (`by: header`). The stage completed.
- **O-2, redis, A6: a warning from a parser.** The A6 log's first line is `<unknown>:97: SyntaxWarning: invalid escape sequence '\$'`; it names no file (`<unknown>`). The stage completed.
- **O-3, both copies: MA's estimate against the envelope.** `envelope.within` is false on both (DEC-078's envelope): redis's estimated peak 2,289,896,370 bytes against the envelope's 2,200,000,000; grafana's as above.
- **O-4, grafana, A6: long phases (no failure).** Two runs of A6 are involved (see the note under grafana's table). *First run (stopped by the lead's harness, `A6-stopped-1.log`):* the log holds, as gov's wrapper printed it, `heavy_slot: all 3 slots taken; waiting (2026-11-14 01:47:41)` (no line for the end of the wait), then gov's rebuild line `rebuild: slow: past 1800 s and still running; it goes on to the end; its record: .gov-runtime/rebuild/record.json`. Its appended part says `record.json` was last written 2026-11-14T03:54:07Z with `stage_running` secrets and `stage_running_s` 7104.4. *Second run (`A6.log`, exit 0):* 2026-11-14T04:00:21+00:00 to 2026-11-14T11:26:10+00:00, 26,749 s start to end and 26,747.32 s elapsed by `/usr/bin/time` (about 7 h 26 min); peak 6,617,236 kB. Its log has the same `rebuild: slow: past 1800 s and still running` line, no slot-wait line, and a result in which `lexical`, `semantic` and `codeintel` each have `status` `recreated`; the 47 files over the chunk limit (as O-1, the limit 10000) are listed under `semantic.cut`. A6's own log and its record in the copy (`governance/adoption/A6-controlled-migration.md`, committed 2026-11-14T11:26:07Z as `a0c8e7e048fe901161ae85b51286137401bcee65`) hold no per-phase times, and the rebuild's `record.json` was overwritten by A8's rebuild, so no phase time of A6 is quoted from a log. What the lead saw while the second run went on, from `record.json` at the time (lead's observation of record.json during the run): `record` 22.4 s; `lexical` 6676.5 s (the record's `secrets_s` showed the same 6676.5); `semantic` 5729.3 s; then a second long phase the record labelled `secrets`, with one `gitleaks stdin` process per file at about 2 a second, from about 07:50Z to about 11:25Z; then the stage ended. For comparison, redis's whole secrets stage took 3.3 s (`timing.secrets_s` in its `record.json`) over its roughly 1,970 tracked files (est.: 1,972 at the end of the run, `git ls-files`), and A8 on grafana took 237.50 s elapsed. The cause of the difference is not examined here. The duration is an observation, not a failure: A6 exited 0. The earlier batch-1 text of this observation, written while the first run was still going, gave an estimate of about 12,300 s for the secrets stage (est.: 24,621 files at 2 a second); the second run's own figures above replace it and are not a measure of memory.
- **O-5, both copies: the secrets lists of MA and of MA-at-A3.** MA names 1 entry on redis and 148 on grafana; the lists are identical between the two runs on each copy (compared by path and rule id).

## The assessment's secrets

MA's `secrets` field, by path and rule id only. No value and no line of any file is copied; the scan covered every tracked file (`secrets_scanned` true, `secrets_unscanned` empty on both).

### redis (1 entry)

| path | rule id |
|---|---|
| `deps/xxhash/xxhash.h` | generic-api-key |

### grafana (148 entries)

| path | rule id |
|---|---|
| `.citools/src/air/go.sum` | generic-api-key |
| `.citools/src/cue/go.sum` | generic-api-key |
| `apps/advisor/go.sum` | generic-api-key |
| `apps/advisor/pkg/app/checks/configchecks/security_config_step.go` | generic-api-key |
| `apps/alerting/alertenrichment/go.sum` | generic-api-key |
| `apps/alerting/alertrulequality/go.sum` | generic-api-key |
| `apps/alerting/notifications/go.sum` | generic-api-key |
| `apps/alerting/rules/go.sum` | generic-api-key |
| `apps/annotation/go.sum` | generic-api-key |
| `apps/collections/go.sum` | generic-api-key |
| `apps/correlations/go.sum` | generic-api-key |
| `apps/dashboard/go.sum` | generic-api-key |
| `apps/dashboard/pkg/migration/conversion/testdata/golden_checksums.json` | generic-api-key |
| `apps/dashboard/pkg/migration/testdata/golden_checksums.json` | generic-api-key |
| `apps/dashvalidator/go.sum` | generic-api-key |
| `apps/example/README.md` | curl-auth-user |
| `apps/example/go.sum` | generic-api-key |
| `apps/folder/go.sum` | generic-api-key |
| `apps/iam/go.sum` | generic-api-key |
| `apps/live/go.sum` | generic-api-key |
| `apps/logsdrilldown/go.sum` | generic-api-key |
| `apps/playlist/go.sum` | generic-api-key |
| `apps/plugins/go.sum` | generic-api-key |
| `apps/preferences/go.sum` | generic-api-key |
| `apps/provisioning/go.sum` | generic-api-key |
| `apps/provisioning/pkg/connection/github/connection_test.go` | private-key |
| `apps/quotas/go.sum` | generic-api-key |
| `apps/scope/go.sum` | generic-api-key |
| `apps/secret/go.sum` | generic-api-key |
| `apps/shorturl/go.sum` | generic-api-key |
| `conf/defaults.ini` | generic-api-key |
| `devenv/docker/blocks/auth/authentik/README.md` | generic-api-key |
| `devenv/docker/blocks/auth/authentik/cloak.sql` | private-key |
| `devenv/docker/blocks/auth/authentik/docker-compose.yaml` | generic-api-key |
| `devenv/docker/blocks/auth/authentik/key.pem` | private-key |
| `devenv/docker/blocks/auth/jwt_proxy/cloak.sql` | gov-token-lower |
| `devenv/docker/blocks/auth/jwt_proxy/docker-compose.yaml` | generic-api-key |
| `devenv/docker/blocks/auth/oauth/cloak.sql` | gov-token-lower |
| `devenv/docker/blocks/auth/oauth/readme.md` | generic-api-key |
| `devenv/secrets/secrets-config.yaml` | gov-token-digit |
| `docs/sources/administration/enterprise-licensing/_index.md` | jwt |
| `docs/sources/administration/enterprise-licensing/activate-aws-marketplace-license/activate-license-on-instance-outside-aws/index.md` | generic-api-key |
| `docs/sources/administration/roles-and-permissions/access-control/create-custom-roles/index.md` | curl-auth-header |
| `docs/sources/administration/roles-and-permissions/access-control/plan-rbac-rollout-strategy/index.md` | curl-auth-header |
| `docs/sources/administration/roles-and-permissions/access-control/plan-rbac-rollout-strategy/index.md` | grafana-service-account-token |
| `docs/sources/administration/roles-and-permissions/access-control/plugin-role-definitions/index.md` | curl-auth-header |
| `docs/sources/administration/service-accounts/_index.md` | curl-auth-header |
| `docs/sources/administration/service-accounts/_index.md` | grafana-service-account-token |
| `docs/sources/administration/service-accounts/migrate-api-keys.md` | curl-auth-header |
| `docs/sources/administration/service-accounts/migrate-api-keys.md` | grafana-api-key |
| `docs/sources/administration/service-accounts/migrate-api-keys.md` | grafana-service-account-token |
| `docs/sources/datasources/google-cloud-monitoring/configure/index.md` | private-key |
| `docs/sources/developer-resources/api-reference/cloud-api/_index.md` | generic-api-key |
| `docs/sources/developer-resources/api-reference/cloud-api/_index.md` | grafana-api-key |
| `docs/sources/developer-resources/api-reference/http-api/api-legacy/dashboard_public.md` | generic-api-key |
| `docs/sources/developer-resources/api-reference/http-api/api-legacy/data_source.md` | generic-api-key |
| `docs/sources/developer-resources/api-reference/http-api/api-legacy/licensing.md` | jwt |
| `docs/sources/developer-resources/api-reference/http-api/api-legacy/query_history.md` | generic-api-key |
| `docs/sources/developer-resources/api-reference/http-api/api-legacy/serviceaccount.md` | grafana-api-key |
| `docs/sources/developer-resources/api-reference/http-api/examples/create-api-tokens-for-org.md` | curl-auth-header |
| `docs/sources/developer-resources/api-reference/http-api/examples/create-api-tokens-for-org.md` | grafana-api-key |
| `docs/sources/setup-grafana/configure-access/configure-authentication/_index.md` | curl-auth-header |
| `docs/sources/setup-grafana/configure-access/configure-authentication/grafana-cloud/index.md` | generic-api-key |
| `docs/sources/setup-grafana/configure-docker.md` | generic-api-key |
| `docs/sources/setup-grafana/configure-security/configure-database-encryption/integrate-with-hashicorp-vault/index.md` | vault-service-token |
| `e2e-playwright/unauthenticated/login.spec.ts` | generic-api-key |
| `go.sum` | generic-api-key |
| `go.work.sum` | generic-api-key |
| `hack/go.sum` | generic-api-key |
| `packages/grafana-openapi/src/api/openapi3.json` | grafana-service-account-token |
| `pkg/api/dtos/apikey.go` | grafana-service-account-token |
| `pkg/api/http_server_test.go` | private-key |
| `pkg/api/pluginproxy/test-data/access-token-1.json` | jwt |
| `pkg/api/pluginproxy/test-data/access-token-2.json` | jwt |
| `pkg/api/pluginproxy/token_provider_test.go` | generic-api-key |
| `pkg/apimachinery/go.sum` | generic-api-key |
| `pkg/apimachinery/identity/requester_test.go` | private-key |
| `pkg/apiserver/go.sum` | generic-api-key |
| `pkg/codegen/go.sum` | generic-api-key |
| `pkg/components/satokengen/tokengen_test.go` | generic-api-key |
| `pkg/components/satokengen/tokengen_test.go` | grafana-service-account-token |
| `pkg/infra/features/go.sum` | generic-api-key |
| `pkg/infra/metrics/go.sum` | generic-api-key |
| `pkg/infra/tracing/go.sum` | generic-api-key |
| `pkg/legacyapi/go.sum` | generic-api-key |
| `pkg/login/social/connectors/generic_oauth_test.go` | jwt |
| `pkg/login/social/connectors/google_oauth_test.go` | private-key |
| `pkg/login/social/connectors/okta_oauth_test.go` | jwt |
| `pkg/operators/provisioning/README.md` | curl-auth-header |
| `pkg/plugins/codegen/go.sum` | generic-api-key |
| `pkg/plugins/go.sum` | generic-api-key |
| `pkg/plugins/manager/testdata/test-app-with-backend/go.sum` | generic-api-key |
| `pkg/registry/apis/folders/validate_test.go` | generic-api-key |
| `pkg/registry/apis/secret/encryption/manager/manager_test.go` | generic-api-key |
| `pkg/registry/apis/secret/secretkeeper/secretkeeper_test.go` | generic-api-key |
| `pkg/services/auth/idimpl/service_test.go` | private-key |
| `pkg/services/auth/jwt/rsa_keys_test.go` | private-key |
| `pkg/services/authn/clients/jwt_test.go` | jwt |
| `pkg/services/cloudmigration/api/curl_commands.txt` | generic-api-key |
| `pkg/services/datasources/service/datasource_test.go` | generic-api-key |
| `pkg/services/datasources/service/datasource_test.go` | private-key |
| `pkg/services/ldap/ldap_test.go` | generic-api-key |
| `pkg/services/ldap/ldap_test.go` | private-key |
| `pkg/services/ldap/service/ldap_test.go` | private-key |
| `pkg/services/ldap/testdata/parsable.pem` | private-key |
| `pkg/services/live/live_test.go` | private-key |
| `pkg/services/ngalert/api/test-data/receiver-exports/redacted/all-integrations.json` | private-key |
| `pkg/services/ngalert/api/test-data/receiver-exports/redacted/all-integrations.yaml` | private-key |
| `pkg/services/ngalert/api/test-data/receiver-exports/unredacted/all-integrations.hcl` | private-key |
| `pkg/services/ngalert/api/test-data/receiver-exports/unredacted/all-integrations.json` | private-key |
| `pkg/services/ngalert/api/test-data/receiver-exports/unredacted/all-integrations.yaml` | private-key |
| `pkg/services/ngalert/notifier/compat.go` | generic-api-key |
| `pkg/services/ngalert/notifier/receiver_svc_test.go` | generic-api-key |
| `pkg/services/oauthtoken/oauth_token_test.go` | jwt |
| `pkg/services/pluginsintegration/pluginroute/README.md` | curl-auth-user |
| `pkg/services/provisioning/datasources/testdata/all-properties/all-properties.yaml` | generic-api-key |
| `pkg/services/provisioning/datasources/testdata/all-properties/sample.yaml` | generic-api-key |
| `pkg/services/provisioning/datasources/testdata/version-0/version-0.yaml` | generic-api-key |
| `pkg/services/publicdashboards/internal/api/api_test.go` | generic-api-key |
| `pkg/services/queryhistory/queryhistory_details_test.go` | generic-api-key |
| `pkg/services/signingkeys/signingkeysimpl/service_test.go` | private-key |
| `pkg/services/ssosettings/strategies/saml_strategy_test.go` | generic-api-key |
| `pkg/services/store/kind/dashboard/testdata/repeated-datasource-variables.json` | generic-api-key |
| `pkg/services/supportbundles/supportbundlesimpl/service_bundle_test.go` | age-secret-key |
| `pkg/storage/legacysql/dualwrite/dualwriter_continue_token_test.go` | generic-api-key |
| `pkg/storage/unified/README.md` | curl-auth-user |
| `pkg/storage/unified/apistore/go.sum` | generic-api-key |
| `pkg/storage/unified/resource/kv/go.sum` | generic-api-key |
| `pkg/storage/unified/resourceclient/go.sum` | generic-api-key |
| `pkg/tests/api/alerting/api_notification_channel_test.go` | generic-api-key |
| `pkg/tests/apis/provisioning/common/testing.go` | private-key |
| `pkg/tests/apis/provisioning/repository/repository_test.go` | private-key |
| `pkg/util/sqlite/go.sum` | generic-api-key |
| `pkg/util/uri_sanitize_test.go` | aws-access-token |
| `public/api-enterprise-spec.json` | grafana-service-account-token |
| `public/api-merged.json` | grafana-service-account-token |
| `public/app/features/alerting/unified/components/import-to-gma/preview/redactPreviewSecrets.test.ts` | generic-api-key |
| `public/app/features/alerting/unified/components/import-to-gma/preview/redactPreviewSecrets.test.ts` | private-key |
| `public/app/features/alerting/unified/components/import-to-gma/preview/redactPreviewSecrets.test.ts` | slack-webhook-url |
| `public/app/features/logs/logsModel.test.ts` | generic-api-key |
| `public/app/features/manage-dashboards/components/PublicDashboardListTable/PublicDashboardListTable.test.tsx` | generic-api-key |
| `public/app/features/manage-dashboards/components/SnapshotListTable.test.tsx` | generic-api-key |
| `public/app/features/provisioning/Connection/ConnectionForm.test.tsx` | private-key |
| `public/app/features/provisioning/Wizard/fields.ts` | private-key |
| `public/app/features/scopes/dashboards/ScopesDashboardsService.test.ts` | generic-api-key |
| `public/app/plugins/panel/timeseries/plugins/annotations/getAnnotationTooltip.test.tsx` | generic-api-key |
| `public/openapi3.json` | grafana-service-account-token |
| `scripts/build/gpg-test-vars.sh` | private-key |

## Earlier attempts

Run 3 started two attempts that the lead stopped because they overlapped (their logs are in `~/gov-os-runs/W2-88b/aborted-1/` and `aborted-2/`). They are not this record's rows: the stage rows above are the logs of the run under `<name>-logs/`. (`aborted-2/redis-logs/A3.log` ends with exit 1 and gov's text `ADOPT_STAGE_MISSING: stage A3 stands on stage A0, which left no committed record`; that attempt was stopped, its cause is not examined here, and it is not a finding of this record.)

Run 4's first A6 on grafana (2026-11-14T01:47:41+00:00 to about 03:59Z) was stopped by the lead's own harness (its 2-hour limit on a background command), not by gov; its log is `grafana-logs/A6-stopped-1.log`, it has no row in `stages.tsv` and no exit code, and A6 was re-run from the same HEAD (`c6c22a0bfa3ad3e055d4682fc3ace13726958f42`) by the driver's `a6-on` phase. It is not a gov failure and not a finding.
