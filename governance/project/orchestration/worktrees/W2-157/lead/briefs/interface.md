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
