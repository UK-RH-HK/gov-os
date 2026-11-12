---
type: probe
task: DAEO-ozyt
reviewer_session: 7087bb80-3399-4558-b2b8-329f6b0dd9d8
implementer_session: "eng-1-2 bada15f5-de56-4438-958f-cc3416e0acb3 (8939fcff5515, c5b0ee91dd12); eng-2 09b6ec9c-efe6-40f8-8c65-a2804b1bfb3e (1c2ad5b9c6ef); eng-3 71777e66-34d9-4fc1-9259-75f870e88b36 (365a4acda69b)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 365a4acda69b7bf1ce98009b3003719f16b0ecaa
---

# Probe record: W2-157 (DAEO-ozyt) the GPU backstop in the product, STANDARD review, rounds 1 and 2 of 2 (DEC-1010)

- **Round 1** (reviewer session 4ad4ff19-4cc0-4b86-b9d9-eec361b11b9d, independent-auditor, Opus high, read-only) probed
  head `1c2ad5b9c6ef`: **fail** (`verdict.ready`: S1 marked fail and FR-1 blocks, in scope, ordinary work, fails open;
  S4 marked fail). FR-1/FR-2: a backstop running inside a group it names froze itself before it paused the groups named
  after that one, and before it wrote the TRIP line and the inbox item.
- **The repair:** the lead settled the wanted behaviour as L5b (the backstop's own group, when named, is paused last,
  after every other named group, the TRIP line and the inbox item; a `note:` line in the item; resuming the own group
  lets the command end). The independent test designer added 7 acceptance cases for it (`ca7f8e689f2d`,
  `c4107a6d6cee`, merged at `97e44155c5e1`, 6 red on the built code); a fresh engineer fixed `backstop.py` and added
  FR-5's sentence to the evidence's operator step (`365a4acda69b`). Round 1's FR-3, FR-4 and FR-6 to FR-10 were judged
  out of scope and stay as residual rows.
- **Round 2** (reviewer session 7087bb80-3399-4558-b2b8-329f6b0dd9d8, independent-auditor, Opus high, read-only, a fresh
  session) probed head `365a4acda69b`: **pass**, `verdict.ready` True: every KPI line S1-S5 and F1-F4 pass; FR-1 and FR-2
  fixed; three new findings, none blocking: FR-11 (medium; in scope, not ordinary work, fails open: with the own group
  named, an inbox item that cannot be written at the trip crashes the command before the own group is paused), FR-12
  (low; in scope, ordinary work, other: with the own group named the watch never ends on its own), FR-13 (low; in
  scope, ordinary work, other: the root is not checked to be a project at the start). No third round (DEC-1010).
- **The lead's checks of the probed head:** `gov accept W2-157` 116 passed, 0 failed (every KPI line); the scoped verify
  (`lead_verify.sh`) 4167 tests, 7 failed, every one outside this ticket: the six W2-96 signal reds (shared base reds,
  ruling P-W2-121-5; W2-177 fixes them) and W2-02's `green_here` core-schema case on `.tickets/DAEO-1k7y.md` (W2-177's
  ticket file in the base; this branch changes no ticket file).
- **Residual rows the lead names:** FR-11 (a `try`/`finally` so the own group's SIGSTOP happens whatever the item write
  does), FR-12, FR-13; round 1's FR-3 (a GPU that cannot be read leaves the watch blind with no inbox item: an owner
  question), FR-4, FR-6 to FR-10.

The two reviewers' returns follow verbatim, round 1 first; the last verdict block (round 2's) decides.

## Round 1: the reviewer's return (head 1c2ad5b9c6ef)

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

## Round 2: the reviewer's return (head 365a4acda69b)

I ran the step 0 sandbox check, then the round-2 review of head `365a4acda69b`. The L5b fix works and all nine KPI lines pass. I found three new non-blocking findings, all for the record rather than another round. One of them fails open, but only when the project root can't be written.

task: DAEO-ozyt (W2-157), independent review round 2 (STANDARD, class C2), head 365a4acda69b
status: DONE
work_completed: **Sandbox check, reported first:** (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-W2-157','w')..."` failed with `OSError: [Errno 30] Read-only file system`, and no file exists. (b) `git hash-object -w --stdin` printed 1ae28402a109… and `git update-index --refresh` worked. GOV_TICKET=DAEO-ozyt. **ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing. **Identity:** `git rev-parse HEAD` = 365a4acda69b7bf1ce98009b3003719f16b0ecaa, and `git status --porcelain` was empty at the start and at the end. I read the ticket, L1–L9 and L5b, `backstop.py`, the `command.py`/`config.py` diff, the evidence file, the own-group acceptance file header and the reference `gpu_backstop.sh`. I ran nine probe scenes (P1–P9) through the real CLI and the module, all under `$TMPDIR`.
files_changed: none
evidence: Probe scripts and outputs are under `$TMPDIR/probe/` (scripts/p1.py–p9.py, drv.py). The key outputs are quoted under "What was probed".
tests: I re-ran no suite (the lead ran `gov accept W2-157`: 116 passed). Grepping the W2-157 unit and acceptance tests for chmod / PermissionError / read-only / OSError finds no case that reaches FR-11.
discoveries: Each Bash call here runs in its own PID namespace: processes planted in one call die when the call ends, so each scene was driven from a single Python script. An unreaped zombie keeps its group "live" to `killpg(g, 0)`. That is the kernel's behaviour, the same as the reference script's `kill -0`, and not a finding.
risks: FR-11. When the own group is named and the inbox item cannot be written at the trip, gov crashes before pausing its own group, so the job in that group keeps using the GPU, while the TRIP line already says that group is paused.
lessons: Reordering a safety action to come after a write (L5b) makes that write a new failure point for the action. The own-group SIGSTOP needs to happen whatever the write does.
proposed_decisions: none
unresolved: Whether a backstop is ever run against a root it cannot write (for example from inside the launch sandbox against the main tree, as W2-137 S5's "GPU backstop armed" step might). If so, FR-11 becomes ordinary work.
recommended_next_action: Record FR-11, FR-12 and FR-13 as residual rows with FR-3 to FR-10. No round 3 is needed (DEC-1010). FR-11 is cheap to fix as an accepted residual: send the own group's SIGSTOP even when the item or log write fails. Hand it as a case to the independent suite (DEC-136).

**What was probed:**
- **Setup:** `python3 -m gov.cli.main resources --backstop … --root $TMPDIR/probe/proj --json`, with this tree's `src/` on PYTHONPATH and no bytecode writes. HOME was planted with its own `gate.json` holding the three keys (period 0.5 s, sometimes an embedder on a free port). A stand-in `nvidia-smi` printed scripted readings. Every group I signalled was one I started (`start_new_session`) and got SIGCONT then SIGKILL in teardown. No real GPU, server, gate.json or port 11434/11435 was touched.
- **P1, round 1's FR-1/FR-2 scene:** `bash -c 'sleep 300 & python3 -m gov … --backstop $$ <B> <C>'`, own group first, readings 15,800 then 15,900. The second group (B) was stopped (T). The TRIP line `… reading 15900/16376 MiB; paused groups 6 7 8` and the item (paused 6 7 8, a resume and a stop line for each, the note line) both existed while gov, the shell and the job were all T. After `kill -CONT -- -8` the run ended with rc=0 and the envelope showed `tripped: true, paused [6,7,8]`. The start line ended `; own group 8 named: paused last`. **Sound.**
- **P2, own group named alone, its `&` job ending after 1 s, gov exec'd:** after 6 s gov was still polling, with only gov and the dead job left in the group. When I then fed a 15,900 reading, it tripped, stopped itself and wrote an item for a job that ended long before. This is FR-12.
- **P3, inbox folder not writable at the trip:**
  - Own group first plus B: B was stopped and the TRIP line said `paused groups 7 8`. Then a PermissionError traceback and rc=1, with no envelope. The own group's `sleep 300` stayed **S (running)**. This is FR-11.
  - Same without the own group: the group was stopped and the TRIP line written, then a traceback and rc=1 with no item. The pause held.
- **P4, no `--root`, current folder a read-only folder that is not a project:** the start was accepted and the watch ran. Only at the trip (third reading) did it crash, after pausing the group. This feeds FR-11 and FR-13.
- **P6, a hanging `nvidia-smi`:** both an exec'd `sleep 100` and a shell whose child holds the pipe were cut after about 20 s and logged as `no GPU reading: … timed out after 20 seconds`, and the watch went on. Bounded; a variant of the known FR-3. **Sound.**
- **P7, embedder log with no server at the port:**
  - A line written before the start never counted.
  - `offloaded 10/` and `33 layers to GPU\n` written across two polls tripped once, naming the whole matched text.
  - A line with no final newline was held, and tripped only once its newline was written.
  - `33/33` never tripped.
  
  **Sound.**
- **P8, `/api/ps` variants (direct call):**
  - A second model partly off the GPU trips.
  - `size_vram` 0 trips (FR-5's case; the doc sentence covers it).
  - `models` given as a dict, an HTTP 500 and a 5 s answer (cut at 3.0 s) do not trip.
  - A `size_vram` given as a string is skipped and a later model is still checked.
  - A 200,000-model answer takes 0.1 s.
  - A first model without `size_vram`, or a partial model without a name, aborts the port's check (the known FR-9; the nameless model is a variant needing a malformed server).
- **P9, filesystem spy over a CLI run, with the planted tree and the worktree snapshotted:**
  - With no trip, only `gpu-backstop.log` and its folder's mtime changed (S5).
  - With a trip, the log, the `.gov-runtime/dispatch/inbox` chain and one item changed.
  - The worktree stayed clean.
- **Read, not re-run:** `config.py` only adds functions; VALUES, OPTIONAL and template() are untouched, so W2-20's frozen key set stands. `_group` refuses non-ASCII digits, signs and spaces. Duplicate groups are dropped (`dict.fromkeys`).

**Findings:**

**FR-11 (medium): with the own group named, a failed inbox write leaves the own group's job running.**
- **What was done:** a backstop sharing its group with a `&` job, plus a second group, with the inbox folder not writable when it trips.
- **What happened:** the second group was paused and the TRIP line said both groups were paused. Then writing the item raised PermissionError and gov exited 1 with a traceback and no envelope. Its own group was never paused, so the job in it ran on.
- **What should have happened:** the own group is paused whatever the item write does, the failure is reported, and the log does not name a group as paused that was not.
- **New:** L5b's reordering created this; before the fix, the own group was paused in the loop, before the item. No test reaches it.
- **Ordinary work: no**, because it needs a project root the backstop cannot write at the trip (a read-only tree, or a current folder outside any project). Nothing at the start checks the root, so this only shows at the trip.
- **Consequence: fails open.**
- **Reverses it:** a workflow where a session arms the backstop against a root it cannot write (for example, the launch sandbox against the main tree) makes it ordinary and blocking.
- **Decisions:** DEC-1067, DEC-1068 (4), DEC-801, DEC-1010.

**FR-12 (low): with the own group named, the watch never ends on its own.**
- **What was done:** `job & gov … --backstop $$`, with the job ending normally.
- **What happened:** gov keeps its own group live, so it never logs `end: every watched group has ended`. It polls indefinitely. A later, unrelated trip pauses gov itself (and the launching shell, when gov isn't exec'd) and writes an item about a job that is already gone. A script waiting on gov hangs.
- **What should have happened:** S4's "when every named group has ended on its own, the watch logs it and ends" should apply to a job sharing gov's group. Alternatively, L5b should state that it does not.
- **New:** the reference `gpu_backstop.sh` behaves the same way, so this is not a regression against it.
- **Ordinary work: yes**, because the shared-group launch is the FR-1 pattern and jobs normally end.
- **Consequence: other** (a hang and a spurious pause or item; nothing is killed).
- **Reverses it:** an owner reading that, with the own group named, ending is by trip or by the owner only.
- **Decisions:** DEC-1073 (4), DEC-1010.

**FR-13 (low): the root is not checked to be a project.**
- **What was done:** `gov resources --backstop <g>` with no `--root`, run from a folder that is not a project.
- **What happened:** the start was accepted. At the trip it tried to create `.gov-runtime/dispatch/inbox` in that folder: it crashed when the folder was read-only (P4), and would otherwise put the item where nobody reads it.
- **What should have happened:** the item goes to the project's inbox. A root that cannot hold it should be refused at the start, as L2 refuses a bad configuration.
- **New.**
- **Ordinary work: yes**, because running from the wrong folder or mistyping `--root` is an honest slip.
- **Consequence: other** (the pause holds; the notification is lost or crashes).
- **Reverses it:** evidence that every `gov` command accepts any current folder as root by design, with the backstop following that.
- **Decisions:** DEC-1068 (4), DEC-1010.

Round 1's FR-1 and FR-2 are fixed (P1). FR-3 to FR-10 are unchanged by the fix and not re-raised.

Classification: 3 findings, none blocking. FR-11 is in scope, not ordinary work, fails open. FR-12 and FR-13 are in scope, ordinary work, consequence other. No round 3 is proposed.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "FR-11", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": [{"id": "FR-12", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "FR-13", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": []}, {"kpi": "F4", "verdict": "pass", "findings": []}]}
```

guard_refusals: none
