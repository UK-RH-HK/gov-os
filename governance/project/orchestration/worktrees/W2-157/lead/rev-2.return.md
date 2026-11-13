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