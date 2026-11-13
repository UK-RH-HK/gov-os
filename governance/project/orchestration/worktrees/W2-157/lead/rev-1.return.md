task: DAEO-ozyt (W2-157), independent review (STANDARD), round 1, head `1c2ad5b9c6ef`

Sandbox check (step 0): passed. (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-157` failed with `OSError: [Errno 30] Read-only file system`, and no file was made. (b) `git hash-object -w --stdin` returned `1ae28402a109…` with exit 0, and `git update-index --refresh` exited 0. `GOV_TICKET=DAEO-ozyt`. Identity: `git rev-parse HEAD` = `1c2ad5b9c6ef8528850fb4dde8894aa6bb5fcb10`.
ps check: `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` matched only my own shell's command line. No ollama or llama-server process of mine runs.

status: DONE
work_completed: I read the ticket, the diff from fbf97f2a06e8 to 1c2ad5b9c6ef (backstop.py, command.py, config.py, the evidence doc, and the designer's acceptance folder and harness), W2-20's config at the base, the CTO's `gpu_backstop.sh`, the wrapper that starts the query embedder, W2-121's ticket for the inbox location, and DEC-1067, DEC-1068, DEC-1030, DEC-1073, DEC-1119 and DEC-1109 by id. I ran 21 behaviour probes of `gov resources --backstop` from this tree's `src/`. Everything ran under `$TMPDIR`: a planted HOME and project, stand-in `nvidia-smi` scripts, stand-in HTTP servers on free ports, planted logs, and process groups I started myself (each sent SIGCONT then SIGKILL afterwards).
files_changed: none. `git status --porcelain` is empty. Step 0's required `hash-object -w` left one loose object in `.git`.
evidence: the probe scripts are in `$TMPDIR/rv/` (p1 to p5), using a copy of the designer's harness with its `src` path re-pointed. Outputs are quoted under "What was probed".
tests: I re-ran no suite (DEC-959 item 1). I ran only the five probe scripts.
discoveries: each Bash call runs in its own PID namespace, so the planted groups had pids 5 to 73. The query embedder on port 11435 runs on the CPU when `~/.ollama/query-server-device` is not `gpu`. Today it reads `gpu`.
risks: FR-1 and FR-2 (one cause). Arming the backstop from inside the job's own process group, which is the usual result of forgetting `setsid`, gives one of two outcomes. A group named after its own is never paused (fails open). Or the job is paused and nobody is told.
lessons: the acceptance harness always starts the watch in a group of its own, so no case can reach the self-group path.
proposed_decisions: none
unresolved: FR-3 (a backstop that cannot read the GPU stays armed but blind and tells no one) is a design question on the reading L3, for the owner. It is not a defect of the build.
recommended_next_action: hold one more engineer round, for FR-1/FR-2 only. Classification: 1 blocking cause (FR-1, with FR-2 as its other consequence: in scope, reachable in ordinary work, fails open); 8 recorded rows (FR-3 to FR-10), none blocking. In that round the backstop should refuse to start when its own process group is among those named, naming it. The alternative is to pause every other named group first, write the TRIP line and the inbox item, and pause its own group last. The engineer adds a unit test and the test designer adds an acceptance case. The other rows are filed as recorded rows; FR-5's operator note can go into the evidence doc in the same round.
decisions: DEC-1067, DEC-1068, DEC-1030, DEC-1073, DEC-801, DEC-1010

**What was probed:**
- **Setup.** `python3 -m gov.cli.main resources --backstop … --root <planted project> --json`, with `PYTHONPATH` set to this tree's `src`, `PYTHONDONTWRITEBYTECODE=1`, a planted HOME holding a whole `gate.json` with a 0.1 s period, and a stand-in `nvidia-smi` first on `PATH`.
- **p1: the watch inside a group it names** (run):
  - (a) A bash in its own session starts the job in the background, then runs gov with `--backstop $$`. Readings 15,800 then 15,900. After 4 s the group is stopped (`T`), the backstop with it. The log holds only the start line. No TRIP line, no inbox item, no envelope.
  - (b) The same, with `--backstop $$ <second job's group>`. The second named group is still running (`S`) and received no signal. No TRIP line, no inbox item.
- **p2: nvidia-smi faults** (run):
  - It hangs 60 s on the first call, then reads 15,900. Logged `no GPU reading: … timed out after 20 seconds`, then it trips on the next poll and the job stops: sound.
  - Two lines, the second 23,000 MiB: no trip, since only the first line is read (L3).
  - `[N/A], [N/A]`, or an NVML error line before a valid line: `no GPU reading`, no trip, the watch goes on (L3). One log line per poll.
- **p3: embedder log and `/api/ps`** (run):
  - A partial-offload line split across two writes 0.5 s apart trips once it is whole: sound.
  - A line with no final newline never trips. The engineer's reading R4 chose this; the servers write whole lines.
  - A log truncated smaller trips on the new line: sound.
  - A log replaced, between polls, by a file bigger than the start offset: its first line is skipped and there is no trip (FR-8).
  - `33/33` gives no trip: sound.
  - `size_vram` 0 trips: sound.
  - `models: null` gives no trip: sound.
  - A first model without `size_vram` hides a later partial model (FR-9). A partial model without `name` gives no trip (FR-9).
- **p4: odd values** (run):
  - A period of 1e10 s or 1e300 s: after the start line, `OverflowError: timestamp out of range`, exit 1, no pause (FR-7).
  - `--backstop 0<g> <g>` is accepted as one group: paused once, named once in the item: sound.
- **p5: a `/api/ps` server that trickles one byte a second** (run): after 15 s, one `nvidia-smi` call, the job running, the watch stuck. The 15,900 reading never comes (FR-6).
- **Read:**
  - The acceptance tests are unchanged since the merge commit `15db0ce13`.
  - The branch's diff against the merge base `fbf97f2a06e8` touches only the allowed paths and the designer's `tests/acceptance/W2-157/` (F4).
  - `config.py`'s diff has no deleted lines, so W2-20's `VALUES`, `OPTIONAL` and `template()` are untouched.
  - `ACT_PATHS` is a declaration only; nothing outside `main.py`'s shape check uses it.
  - `<root>/.gov-runtime/dispatch/inbox/` is W2-121's state folder (DAEO-cb2b, Interface).
  - The trip pauses first, then writes the log line and the item.
  - The configuration refuses a float limit, a NaN or infinite period, a relative log path and a port outside 1-65535.

**Findings:**

- **FR-1 (medium, blocking): a backstop running inside a group it names pauses itself before the groups named after that one.**
  - Done: the job was started without `setsid` from the shell that also ran gov, so both share one group, and that group was named first, before a second job's group.
  - Happened: SIGSTOP to its own group froze the backstop, and the second named group kept running on the GPU.
  - Should have happened: every live named group paused (S1), or a refusal at start naming the group.
  - New (the reference script has the same order). Not reached by any acceptance case.
  - Ordinary work: yes. A background job in a non-interactive shell (an agent's Bash call, a measure script arming its own group) shares the shell's group unless `setsid` is used.
  - Consequence: fails open.
  - Reversal: a run showing gov refuses its own group or pauses it last, or proof that every arming path starts gov in a group of its own.

- **FR-2 (medium, same cause as FR-1): in the same setup with one group named, the job is paused but the TRIP line and the inbox item are never written.**
  - Done: p1(a).
  - Happened: everything froze silently, and the command never ends. The log line and item appear only if someone resumes the group, and nobody is told to.
  - Should have happened: S4's one inbox item and the TRIP line.
  - New. Ordinary work: yes, because of the same honest mistake.
  - Consequence: other (the wake-up is lost; the GPU is safe).
  - Reversal: as for FR-1.

- **FR-3 (low, recorded, out): a GPU that cannot be read leaves the backstop blind with no inbox item.**
  - Done: every reading fails (NVML error, `[N/A]`).
  - Happened: one `no GPU reading` log line per poll, forever, and no trip or wake-up.
  - Should have happened: what L3 states (no trip). An inbox item after some consecutive failures is a question for the owner.
  - Known by design (L3, and the reference script does the same).
  - Ordinary work: yes (NVML failures on WSL after a driver change).
  - Consequence: fails open, outside the KPI lines.
  - Reversal: an owner ruling that blind is acceptable.

- **FR-4 (low, out): only the first GPU line is read; a second card over the limit is never seen.**
  - L3 as written; new as a row.
  - Ordinary work: no (one GPU on this machine). Consequence: other.
  - Reversal: a second GPU in scope.

- **FR-5 (low, out): with the query server's device set to `cpu` (a supported fallback), the built-in embedder list makes every poll trip.**
  - Port 11435 reports `size_vram` 0 below `size` and its log shows `offloaded 0/N`.
  - Happened (by reading; the code path for `size_vram` 0 was run in p3): an immediate, needless pause.
  - Should have happened: the operator's step in the evidence doc should say to leave 11435 out when it runs on the CPU.
  - New. Ordinary work: yes, only while the fallback is on (it reads `gpu` today).
  - Consequence: other (a needless pause; nothing lost).
  - Reversal: a rule that the query server is always on the GPU.

- **FR-6 (low, Wave 3, out): a `/api/ps` answer trickled byte by byte blocks the watch indefinitely.**
  - The 3 s timeout applies to each socket read, not to the whole answer, so no later reading is taken.
  - Ordinary work: no (ollama answers at once or not at all). Consequence: fails open.
  - Reversal: a total deadline per answer.

- **FR-7 (low, out): a period valid under L2 but too large for the platform (about 1e10 s and up) crashes with a traceback after the start line.**
  - Exit 1, and the job is never watched.
  - Ordinary work: no. Consequence: fails open.
  - Reversal: an upper bound on the period checked at start.

- **FR-8 (low, out): an embedder log replaced by rename with a file bigger than the start offset has its beginning skipped.**
  - A partial-offload line there is missed.
  - Ordinary work: no. The servers append with `>>` (`ollama_query_cpu_wrapper.sh`). Consequence: fails open.
  - Reversal: logs rotated by rename on this machine.

- **FR-9 (low, out): an earlier `/api/ps` model lacking `size_vram` or `name` aborts the check for that port.**
  - A later partial model gives no trip.
  - Ordinary work: no. Ollama always sends both fields. Consequence: fails open.
  - Reversal: an ollama answer that omits `size_vram`.

- **FR-10 (info, out): a named group that ends (at start or mid-watch) stays in the pause list.**
  - If its id is later reused by a new group, a trip pauses that stranger.
  - Read, not run.
  - Ordinary work: no (it needs the pid numbers to wrap during one watch). Consequence: other.
  - Reversal: a reuse inside one watch on this machine.

- **Probed and found sound:** argument forms; the 20 s bound on a hung `nvidia-smi`, then a trip; a partial-offload line split across polls; truncation; N = M; `size_vram` 0; `models: null`; groups deduplicated; the pause before the log and item; configuration refusals; diff scope; acceptance tests untouched; W2-20's key set untouched; the inbox location.

```verdict
{"kpis": [
 {"kpi": "S1", "verdict": "fail", "findings": [{"id": "FR-1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "FR-3", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "FR-4", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "FR-6", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}, {"id": "FR-7", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S2", "verdict": "pass", "findings": []},
 {"kpi": "S3", "verdict": "pass", "findings": [{"id": "FR-5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "FR-8", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}, {"id": "FR-9", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S4", "verdict": "fail", "findings": [{"id": "FR-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "FR-10", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S5", "verdict": "pass", "findings": []},
 {"kpi": "F1", "verdict": "pass", "findings": []},
 {"kpi": "F2", "verdict": "pass", "findings": []},
 {"kpi": "F3", "verdict": "pass", "findings": []},
 {"kpi": "F4", "verdict": "pass", "findings": []}
]}
```

guard_refusals: 2026-11-12 about 06:27 | a Bash heredoc writing a probe script to `$TMPDIR/rv/p1.py` whose text held the call `m.env()` | "the call reads a secret or a key (.env, *.env, …), which is refused to every role (DEC-820 (a)) (DEC-953 item 2)" | false positive (no file was read; the `.env` was a method name).