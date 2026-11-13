# Brief rev-2: independent reviewer (STANDARD review) for DAEO-ozyt (W2-157), class C2, round 2 (the last)

You are a fresh, read-only independent reviewer (independent-auditor) of ticket DAEO-ozyt (W2-157: the GPU backstop in
the product, `gov resources --backstop <pgid>...`). Probe head `365a4acda69b` of branch `w2/W2-157` in
/home/usain/gov-os-worktrees/W2-157 against the ticket's KPI lines (S1-S5, F1-F4) and its Interface, by running it as
well as reading it, and judge each KPI line pass or fail. You write nothing in the repository: everything you plant
goes under your session's `$TMPDIR`. Your lead writes the probe record from your return.

## What to read
| what | path |
|---|---|
| the ticket (KPI lines with their Verify, the Interface line, non-goals, rabbit holes) | /home/usain/gov-os-worktrees/W2-157/.tickets/DAEO-ozyt.md |
| the lead's readings L1-L9 of what the ticket's Interface left open (the pair built and tested to these) | at the end of this brief (as the pair got them); docs/changes/W2-157-evidence.md restates them as applied |
| the change: `git -C /home/usain/gov-os-worktrees/W2-157 diff fbf97f2a06e8..365a4acda69b` (round 1's fix alone: `diff 1c2ad5b9c6ef..365a4acda69b`) | src/gov/resources/backstop.py (new), command.py, config.py; tests/unit/resources/test_w2_157_backstop.py; docs/changes/W2-157-evidence.md; tests/acceptance/W2-157/ (the independent test designer's) |
| W2-20's gate the change sits beside (its frozen `--init-config` key set must not change) | src/gov/resources/config.py at fbf97f2a06e8, tests/acceptance/W2-20/test_w2_20_config.py |
| the CTO's reference tool (the same triggers and pause; read only) | /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/gpu_backstop.sh |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1067, DEC-1068, DEC-1030, DEC-1073, DEC-1119, DEC-1109 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## Round 1 (head 1c2ad5b9c6ef) and what changed since
Round 1 failed S1 and S4 on one cause: FR-1/FR-2, a backstop running inside a group it names froze itself before it
paused the groups named after that one and before it wrote the TRIP line and the inbox item. The lead settled the fix as
L5b (at the end of this brief, after L1-L9): the own group is paused last, after every other group, the TRIP line and
the item. The test designer added 7 acceptance cases for it (tests/acceptance/W2-157/test_w2_157_own_group.py) and an
engineer fixed backstop.py (365a4acda69b), with FR-5's sentence in the evidence's operator step. Round 1's other
findings were judged out of scope and stay as residual rows; do not re-raise them unless the fix changed them:
FR-3 (a GPU that cannot be read: blind, no inbox item), FR-4 (only the first GPU line), FR-6 (a trickled /api/ps
answer blocks), FR-7 (a huge period crashes), FR-8 (a log replaced by a bigger file), FR-9 (an earlier model without
size_vram aborts that port's check), FR-10 (a pgid reused within one watch).

## What the lead already ran (do not re-run whole suites; DEC-959 item 1)
- `gov accept W2-157` at 365a4acda69b: 116 passed, 0 failed.
- The lead's scoped verify of 365a4acda69b runs alongside you (its result goes in the lead's record).

## How to probe (safety first: the backstop pauses real process groups)
Run `python3 -m gov.cli.main resources --backstop ... --root <planted project> --json` with this tree's `src/` on
`PYTHONPATH`, a planted `HOME` (its own `.gov-os/machine/gate.json`), a stand-in `nvidia-smi` first on `PATH`, stand-in
HTTP servers on free ports (never 11434 or 11435) and planted logs, all under `$TMPDIR`. Signal and pause only process
groups you start yourself (`setsid`/`start_new_session`); send each SIGCONT then SIGKILL when done. Never the real GPU,
the real HOME's gate.json, the real embedding servers or the reranker; nothing matched by name. Probe first L5b and round 1's FR-1/FR-2 scene (a job started with `&` in gov's own group, named first, and a second
group after it; the own group alone; the own group last; an ended group beside it), then whether the fix broke
anything of L1-L9. Look also for what the acceptance cases may not reach, for example: a named group that ends mid-watch, or a pgid later reused
by another group; a stand-in `nvidia-smi` that hangs or prints a second GPU line; an embedder log that is rotated,
written without a final newline, or holds a partial-offload line split across two polls; `/api/ps` answers that are
slow, huge or malformed; the limit or period given in odd but valid forms; anything written outside the log and the one
inbox item (S5); a fault that lets the watch end, or crash, without pausing when it should (fails open).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE or ESCALATION) / work_completed /
files_changed (none) / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then:
- `What was probed:` the setup and each probe, run or read.
- `Findings:` each as `FR-<n> (<severity>): <one line>` (numbered from FR-11; round 1 used FR-1 to FR-10), then what was done, what happened, what should have happened,
  known or new, and whether ordinary work reaches it.
- One fenced block opened by ```verdict holding JSON, one entry per KPI line S1-S5 and F1-F4:
  `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "FR-1", "scope": "in|out",
  "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}`. A KPI line is marked fail only
  when it does not hold; a finding goes under the line it bears on.
- `guard_refusals:` none, or each: time | form | the hook's reason | true or false-positive.

## The Interface (the ticket's Interface line, plus the lead's readings L1-L9 of what it leaves open)

The ticket's own line: `gov resources --backstop <pgid>...`; the limit `gpu_backstop_limit_mib`; the poll period
`gpu_backstop_every_s`; the inbox is the project's inbox folder (as W2-156's, which names W2-121's). The lead has fixed
the points below so the test designer and the engineer write to one interface; both conform to it and change none of
it. A clash with a KPI line comes back as a package (status PACKAGES), not as an invention.

- **L1 The command.** `gov resources --backstop <pgid> [<pgid> ...]` (`--root <project>` as every `gov` command), a new
  member of the existing mutually exclusive mode group in `src/gov/resources/command.py` (`nargs="+"`). Each value must
  be a decimal integer above 1; anything else (`abc`, `1`, `0`, `-5`) is argparse's usage error: exit 2, the value
  named on standard error, nothing read, written or signalled. No option or environment variable sets the limit,
  the period or the embedders: an option such as `--gpu-backstop-limit-mib 99999` is argparse's unrecognised-argument
  error (exit 2), and environment variables (`LIMIT`, `GPU_BACKSTOP_LIMIT_MIB`, `GOV_GPU_BACKSTOP_LIMIT_MIB`) are never
  read. The other mode options' rules are unchanged.
- **L2 The configuration.** Three new dated, sourced values in the gate's one file `$HOME/.gov-os/machine/gate.json`,
  each in the file's usual form `{"value": ..., "date": "YYYY-MM-DD", "source": "<non-empty>"}`:
  - `gpu_backstop_limit_mib`: an integer of at least 1 (this machine's: 15872, DEC-1067 (GPU safety), DEC-1068 (4));
  - `gpu_backstop_every_s`: a number above 0 (this machine's: 5);
  - `gpu_backstop_embedders`: a list (possibly empty) of `{"port": <integer 1-65535>, "log": "<absolute path>"}`, the
    embedding servers to watch and each one's log (this machine's: port 11434 with `$HOME/.ollama/serve-11434.log`,
    port 11435 with `$HOME/.ollama/serve-11435.log`). This is the ticket's "the ports from the gate's configuration".
  Only `--backstop` reads and checks them: they are not in `config.VALUES` or `config.OPTIONAL`, so a file without them
  (or with a malformed one) still opens the gate exactly as before, and `gov resources --init-config` writes exactly
  W2-20's frozen key set, unchanged (tests/acceptance/W2-20/test_w2_20_config.py freezes it). `config.py` holds this
  machine's three entries as a constant (the built-in value, 15872 MiB) for the evidence's operator step; it is never
  a fallback. Under `--backstop`, the file missing, not JSON, or any of the three keys missing or malformed (not the
  form above, no date, no source) refuses to start: `GovError("RESOURCE_CONFIG_INVALID", ...)`, exit 1, the message
  (and `details.faults`) naming each faulty key (or `gate.json`); nothing written, nothing signalled.
- **L3 The GPU reading.** Once per poll, exactly `nvidia-smi --query-gpu=memory.used,memory.total
  --format=csv,noheader,nounits`, `nvidia-smi` found on `PATH`; the first line is `<used>, <total>` in MiB. A trip on
  the limit when used > limit (15,872 does not trip at a limit of 15,872; 15,873 does). A trip on a spill when used >=
  total - 64 (total - 63 and total - 64 trip; total - 65 does not). A reading that cannot be had (no `nvidia-smi`, a
  non-zero exit, an answer not of that form) is logged and is no trip; the watch goes on.
- **L4 The embedders.** Once per poll, for each configured embedder: `GET http://127.0.0.1:<port>/api/ps` (no proxy, a
  timeout of about 3 s), answer `{"models": [{"name", "size", "size_vram", ...}, ...]}`; any model with `size_vram` <
  `size` trips, the reason naming the port, the model and `size_vram/size`. No answer or a malformed one is no trip.
  Each embedder's log: its size in bytes when the watch starts is its start offset (a log missing then: offset 0); each
  poll reads only what was appended since; a line containing `offloaded <N>/<M> layers to GPU` with N < M trips, the
  reason naming the log's path and the matched text; N = M never trips; nothing before the start offset ever counts.
- **L5 The groups and the trip.** At start each named group is checked with signal 0 to the group (`os.killpg(g, 0)`);
  an ended one is skipped and named (in the start log line and in the result's `skipped`). Each poll begins by checking
  the groups the same way; when none is live, the log gets `end: every watched group has ended (<groups>)` and the
  watch ends: exit 0, `tripped: false` (also at once when none is live at start). Each poll checks in this order: the
  limit, the spill, each embedder's `/api/ps`, each embedder's log; the first reason found trips. A trip sends SIGSTOP to
  each live named group with `os.killpg(g, signal.SIGSTOP)`, and to nothing else: never a pid, never a name or pattern,
  never a group not named. Then one TRIP log line, one inbox item, and the watch ends: exit 0, `tripped: true`.
- **L6 Its log.** `$HOME/.gov-os/machine/gpu-backstop.log` (`config.machine_dir()`), appended, one line per event, each
  beginning `YYYY-MM-DD HH:MM:SS`: `start: limit <L> MiB; every <s> s; groups <g ...>; skipped (ended) <g ...|none>;
  embedders <port ...|none>`; `TRIP: <reason>; reading <used>/<total> MiB; paused groups <g ...>` (the reading is the
  poll's GPU reading, `none` when it could not be had); `end: every watched group has ended (<g ...>)`; a GPU reading
  that cannot be had: `no GPU reading: <why>`.
- **L7 The inbox item.** `<root>/.gov-runtime/dispatch/inbox/` (W2-121's state folder; `<root>` is `gov`'s `--root`, the
  project), created if absent; one file `gpu-backstop-<YYYYmmdd-HHMMSS>.txt`, written whole (a dot-named temporary file
  in the same folder, then renamed). Its first three lines: `log: gpu-backstop.log`, `W2: none`, `status: GPU backstop
  tripped: <reason>`; then `paused: <g ...>`, `skipped (already ended): <g ...|none>`, one line `resume: kill -CONT --
  -<g>` per paused group, and one line `stop: kill -TERM -- -<g> && kill -CONT -- -<g>` per paused group.
- **L8 The result.** The command's envelope `result` (`--json`):
  `{"tripped": bool, "reason": str|null, "reading": {"used_mib": int, "total_mib": int}|null, "paused": [int],
  "skipped": [int], "log": "<path>", "inbox_item": "<path>"|null}`. The Python seam (for unit tests):
  `gov.resources.backstop.watch(groups: list[int], root: Path, env: dict | None = None) -> dict` returning that result.
- **L9 Nothing else.** It reads only `nvidia-smi`'s answer, the `/api/ps` answers and the embedder logs; it writes only
  its log and, on a trip, the one inbox item (and the inbox folder if absent); it never writes `gate.json`, never starts,
  stops, restarts or signals a server, and signals nothing but the named groups.

## L5b (the lead's reading, added after review round 1's FR-1 and FR-2): the backstop's own group is paused last

When the process group of the `gov` process itself (`os.getpgrp()`) is among the named groups (for example a job
started with `&` from the same non-interactive shell that runs `gov resources --backstop`, so both share one group):

1. at start, the start log line (L6) carries `; own group <g> named: paused last` at its end;
2. on a trip, every other live named group is paused first (SIGSTOP, in the order named); then the TRIP log line (L6) and
   the one inbox item (L7) are written, the item's `paused:` line listing every paused group the own group included,
   with its `resume:` and `stop:` lines, and one more line `note: the backstop's own group <g> is paused last; resuming
   it resumes the backstop, which then ends`; then, last of all, SIGSTOP to the own group (which stops `gov` too);
3. so while everything is stopped, every named group is stopped and the TRIP line and the item exist; after
   `kill -CONT -- -<g>` the command ends: exit 0, `tripped: true`, `paused` holding every paused group (the own one
   included), as L8.

When the own group is not named, nothing changes. Nothing else is signalled; no group is refused for being the own one.
