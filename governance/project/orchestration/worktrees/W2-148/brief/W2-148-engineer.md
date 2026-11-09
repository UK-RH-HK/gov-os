Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-148/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-148 — the engineer's brief: build the operator agent to the stated interface (DAEO-xafn)

You are the engineer for **W2-148** (`.tickets/DAEO-xafn.md`: read it in full, with its body's "Readings settled by the
CTO"): the operator agent, which applies ACTs by class from a queue in a walled headless session, only when every gate
passes (the owner's DEC-1104 (2), approving `governance/project/orchestration/packages/OPERATOR-AGENT-1.md` with all
seven answers as recommended). Read the package in full: its §1 to §6 are the specification, its §7 the plan. Its KPI
lines S1 to S24 and its fourteen failure lines are what you build to. Profile FULL: every gate fails closed.

The independent test designer has written `tests/acceptance/W2-148/` (157 cases, all red today: nothing is built). Its
README states the interface the cases call; the CTO hands you that section below, **from the start** (the spec, not
the tests), so you build to it without reading the cases.

**Your job:**
1. **Build the code in `governance/project/operator/`** to the interface below: `operator_run.py` (G1 to G9, the
   recompute, the apply, the checks, the commit, the after-checks, the undo, the log, the notices, the digest),
   `act_class.py` with `class-rules.yaml` (the package's §2 table, row by row), `operator_launch.py` (the journal, the
   queue, the wall, the canary, the session, waits and stops by pid and pgid only), `landing_check.py`, `verdict.py`
   (copied **byte for byte** from `.gov-runtime/scratch/ref/verdict.py` in your worktree, sha256
   `277c8ca9f06c90906397579f4d5bd144fb506a40b0836eb2a8f9c1443d909378`), the fixed `brief.md` and `reviewer-brief.md`,
   and the wall's settings and hook for this kind, built on `governance/project/indep-walls/`'s template (read it; reuse
   it; never change it). The install runs standalone: the standard library and PyYAML, no `gov` import.
2. **The two points the designer left open, settled by the CTO (2026-11-09) [DEC-1104 (2)]:**
   - **The commit freeze and the copy of the owner's yes lines** are configurable paths (settings keys of your naming,
     e.g. `freeze` and `approvals`) whose defaults lie inside the operator's own folder: the freeze
     `<operator root>/log/act-in-progress.txt`, the approvals `<operator root>/log/act-approvals.jsonl` (the interface's
     place for them). G9 still holds on the CTO's `<scratch>/log/act-in-progress.txt` as well as the agent's own.
   - **The guard replay's call log** is the `calls` setting; its default is a call log the operator writes itself
     during its dry run (G8: each guard event its dry run produces, as `{id, time, role, ticket, event}` JSON lines,
     in its own `log/`), read by the replay of S15.
   - The CTO settles the final values in ACT-OPERATOR-1; state your defaults in the evidence record.
3. **The trial (S23):** run the classifier on every ACT file under `governance/project/orchestration/packages/`, the
   8 replays (in clones at the commit before each was applied, with planted review records and yes lines) and the 7
   planted faults, all in temporary folders; hash the live control files, `~/gov-os-operator/` and `~/.claude/`
   before and after (names and hashes only; read no file's content there); write `docs/changes/W2-148-evidence.md` in
   the tables the interface names, with your defaults and anything the trial could not do in your sandbox named for
   the CTO's run outside it.
4. Your own unit tests in `tests/unit/operator/test_w2_148*`.

**Nothing live:** you never write `~/gov-os-operator/`, `~/.claude/`, the crontab, the live hook, settings or git
hooks, and never start a real `claude` session (a stub on PATH in your tests). The agent is installed only by the
owner's operator through ACT-OPERATOR-1, after the merge.

## Where you work
- `/home/usain/gov-os-worktrees/W2-148`, branch `w2/W2-148` (from `w2/integrate`, with `w2/W2-148-tests` merged in).
  Your paths are the ticket's `allowed_paths`: `governance/project/operator/**`, `tests/unit/operator/test_w2_148*`,
  `docs/changes/W2-148-evidence.md`.
- **You never read `tests/acceptance/W2-148/`** (G-14; DEC-820 (c)): only `gov accept`'s results. **The exclusion line
  (DEC-1093 (2)), by base name:** every recursive grep carries `--exclude-dir=W2-148`; every Grep or Glob call that
  could reach the folder carries `!tests/acceptance/W2-148/**`; find carries `-path '*/W2-148' -prune`. Start your
  searches from relative paths inside your worktree (`.`, `governance/`, `src/`), never from its absolute path (grep's
  `--exclude-dir` would skip the worktree itself, which is also named `W2-148`). If a search shows you a line of the
  cases anyway, stop reading it and say so in your return.
- You may read any code and record in your worktree: the package, the ACT files, `governance/project/indep-walls/`,
  the path map, the test map, `tests/optin-*.txt`, `.claude/hooks/pretooluse.py`, the register, and
  `.gov-runtime/scratch/ref/LAUNCH-SPEC.md` (the walls' launch script: its canary S9 and its launch line S10, which
  S17 and S18 reuse).

## Verify
- Through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
  with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-148/src`: your unit tests; then
  `python3 -m gov.cli.main accept W2-148 --root /home/usain/gov-os-worktrees/W2-148` (counts per line, results only).
  Name every red with its cause; a case that cannot pass in your sandbox (say why) is run by the CTO outside it.
- **Commit as you go**, each part as it passes, so a session that ends early leaves its work committed.

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No GPU, no model, no network, no installs, no service.
- DEC-1080: Read and Grep tools; one simple command per Bash call; no `cd … &&` chains. Search again once
  (DEC-1092 (1)) if needed.
- Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- Waits and stops by pid or pgid only, never a name match (L-0075), in your code and your session.
- **Commit** on `w2/W2-148` with
  `--trailer "Task: DAEO-xafn" --trailer "Implements: DEC-1104" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it in this worktree's
`.gov-runtime/scratch/lead/log/W2-148-engineer.json`; it is the record): the twelve labelled fields of `EMG-common.md`
(sandbox and `ps` checks first), what you built, `gov accept W2-148`'s counts per line, the unit counts, the trial's
results (counts per class, rises, replays, faults, before/after hashes), the defaults you chose for the open points,
every red named, and any place where the interface and a KPI line disagree (the KPI line wins: say so, with the
case's failure message).

---

# The interface the acceptance cases assume (the designer's README, as written)

## The interface the tests call (the engineer builds to it)

The code lives in `governance/project/operator/`. The tests copy that folder (less `__pycache__`) into
`<operator root>/install/`, write `install/APPROVED`, and run the copies, as the cron will run the live install.
The install runs standalone: the standard library and PyYAML, no `gov` import, no `PYTHONPATH`.

**Files the tests name** (the rest is the engineer's): `operator_run.py`, `operator_launch.py`, `act_class.py`,
`class-rules.yaml`, `landing_check.py`, `verdict.py` (byte for byte the CTO's reference, sha256
`277c8ca9…d909378`), `brief.md`, `reviewer-brief.md`.

**`install/APPROVED`:** one line per install file, `<sha256>  <path relative to install/>` (sha256sum's form), every
file under `install/` but `APPROVED` itself and `__pycache__/`. Any file not matching its line refuses every run and
every launch. Every result prints `approved_sha256` (the sha256 of `install/APPROVED`).

**Settings (S24):** both scripts take `--config <file.json>` before the step; a key left out takes today's default.
Keys: `operator_root` (default: the install's parent), `repo`, `home` (the live HOME, for home-rooted touched files and
the control files under it), `scratch` (the CTO's scratch: bundles at `<scratch>/acts/<ACT>/`, the session id in
`<scratch>/log/cto-session.txt`, the CTO's hold `<scratch>/log/act-in-progress.txt`), `transcripts` (the folder holding
`<session id>.jsonl`), `clock` (a file holding one ISO-8601 time with its offset, read each time the code needs the
time; default the system clock; the quiet hours and the nightly window compare against that time's own wall clock),
`pings_log`, `push_cmd`, `calls` (the guard's call log for the replay), `close_flag` (exists while a close queue
runs), `nightly_window` (`HH:MM-HH:MM`), `poll_s` (a hold's poll interval, seconds).

**Commands:**
- `python3 install/operator_run.py --config C run <ACT> <manifest sha>`: G1 to G9, the recompute, the apply, the
  checks, the commit, the after-checks. `... undo <ACT> <manifest sha>`: the owner's undo (S22).
  `... digest [--since <ISO>]`: the digest (S21; default the last 24 hours by the clock).
- `python3 install/operator_launch.py --config C`: the journal first, then the oldest request, the canary, the session.
- `python3 act_class.py <bundle dir>`: reads `<bundle dir>/manifest.json` and the bundle's files, with
  `class-rules.yaml` beside it; prints `{"class": "a"|"b"|"O", ...}`.
- `python3 landing_check.py --repo <repo> <rev range>`: prints a JSON list, one item per flagged first-parent commit:
  `{"commit": "<40 hex>", "priority": "P1", ...}`.
- Each of the first two prints its result as the **last line of stdout, one JSON object**: `result` (`applied`,
  `refused`, `undone`, `launched`, ...), `gate` (`G1`…`G9`, `recompute`, ...) and `reason` on a refusal,
  `approved_sha256`, and for the launcher `request: {act, sha256}` and `session: {pid, pgid, exit}`. Exit 0 when
  applied, undone (the undo step) or launched; non-zero on a refusal. Fixed phrases in `reason`: `changed after
  review` (any sha mismatch, S5), `to the owner` (a third review round), `yours` (class O), `rebuild, rehearse,
  re-review` (G7).
- **Test hook:** `GOV_OPERATOR_TEST_HOOK=<executable>` is run as `<exe> <point> <frozen folder>` at the points
  `after-G1` (the copy made and hashed) and `after-G6` (G6 passed; the recompute comes next and classifies the frozen
  bytes as they are then). The walled session's clean environment never carries it.

**The ACT bundle** (`<scratch>/acts/<ACT>/`): `manifest.json`; `apply.sh`; `rehearsal.log`; `before/<root>/<path>` and
`after/<root>/<path>` for each touched file that exists before or after; `review.md`, the review record (not listed in
the manifest, since it names the manifest's sha; its sha256 is the `Review:` trailer). The manifest sha is the sha256
of `manifest.json`'s bytes. `<root>` is `repo` (relative to the repository), `home` (relative to HOME) or `crontab`
(path `crontab`: the output of `crontab -l`). Manifest fields:
`act`, `dec`, `author`, `claimed_class` (`a|b|O`), `touched` (`[{root, path, before, after}]`, sha256 or null),
`files` (`{bundle-relative path: sha256}` for every bundle file but `manifest.json` and `review.md`), `rehearsal`
(`{log, sha256}`; the log's last non-empty line is `failures: <n>`, and G3 wants 0), `checks`
(`[{cmd, exit, count}]`: run with cwd the repository; red unless the exit code is `exit` and, when `count` is not null,
the last non-empty stdout line is that integer), `commands` (other shell lines; the classifier scans them, `apply.sh`
and the checks for script hits).

**`apply.sh check|apply|undo`** is run as `bash <frozen folder>/apply.sh <step>` with cwd the repository (the live one,
or the dry run's clone) and HOME the live or the planted HOME; it reads its bundle from its own folder. The planted
scripts do some things only in the live repository (it holds an untracked, excluded `.live-marker` a clone never has):
that is how a case makes the live apply differ from the dry run.

**The verdict block** (verdict.py's fenced form, the last block decides; one block per round): `kpis` as verdict.py,
plus `manifest_sha256`, `class`, `reviewer` (never the manifest's `author`), `reviewer_brief_sha256` (must equal
`reviewer-brief.md`'s line in APPROVED), `time` (ISO; the yes must come after it), and optionally `replay_refused`
(the call ids the review expects the replay to turn to refused). Three blocks: refused, "to the owner".

**The queue:** one request per file `<operator root>/queue/*.req`, one line `ACT-<id> <64 lowercase hex>\n`; the
oldest by mtime first. A malformed file is refused, no session starts, and it is moved aside (anywhere under the
operator root but the queue's top level).

**The wall:** `<operator root>/wall/`, built by the launcher (the session's cwd, never the root); its
`.claude/settings.json` holds a non-empty `permissions.deny` and a `PreToolUse` hook. The session and its canary are
started as `claude -p --restricted --settings <wall>/.claude/settings.json --no-session-persistence
--strict-mcp-config --max-budget-usd <n> ...` with no `GOV_*` and no `CLAUDE_PROJECT_DIR`. The stub reads `--settings`
like Claude Code: a file it cannot parse is ignored, and then the canary's Read comes back allowed. S19 drives the hook
command the launcher wrote into the wall's settings, as Claude Code would (`bash -c <command>`, the event on stdin, cwd
the wall, `CLAUDE_PROJECT_DIR` the wall); a refusal is exit 2 or a `permissionDecision: deny`; any other non-zero exit
fails the test (Claude Code would let the call through). Allowed forms tested: `python3 <install>/operator_run.py run
<ACT> <sha>` (no option), `bash <frozen>/apply.sh check|apply|undo`, a manifest check's exact `cmd`, `git -C <repo> add
<listed path>`, a Read of `<transcripts>/<session id>.jsonl`.

**The log** `<operator root>/log/operator.jsonl`: one JSON line per gate reached per ACT with the keys `time`, `act`,
`manifest_sha256`, `votes` (`{code, claim, review}`; null before G6), `gate`, `result` (`pass`, `refused`, `held`,
...), `commit`, `checks`, `undo`. A hold writes a `G9` line with result `held`. The yes is copied verbatim into
`<operator root>/log/act-approvals.jsonl`. The commit freeze `log/act-in-progress.txt` may be written in the operator
root's log or the scratch's (N-4); it must exist during the apply and be gone after.

**Notices:** each one is sent as `<push_cmd> <notice JSON>` and appended to `pings_log` as one JSON line. Notice keys:
`time`, `act`, `priority` (`P1` or another word), `kind` (the tests read `applied` and `disagreement`), `text`. The
digest (JSON) holds `approved_sha256`, `applied` (`[{act, class, votes, touched, commit, undo}]`, `undo` the line
`undo ACT-<id> <sha8>`), `disagreements`, and `missing_notices` (log events with no line in `pings_log`).

**Commits:** only the listed repository files; trailers `Role: operator`, `Act: <ACT>`, `Act-sha: <manifest sha>`,
`Class: a|b`, `Review: <sha256 of review.md>`, and for (b) `Approved-by: owner (chat, <time>)`; never `Role: owner`,
never a push or a tag (the bare remote and the tag list are checked).

**The replay (S15):** `calls` holds JSON lines `{id, time, role, ticket, event: {tool_name, tool_input, cwd}}`, the
event's paths relative to the repository. The planted guard `.claude/hooks/pretooluse.py` reads
`<CLAUDE_PROJECT_DIR or cwd>/governance/project/path-map.yaml` and the event on stdin and denies a Read under a
`sets_root_hidden` glob. Calls older than 48 hours by the clock are not replayed.

**The control files (S15), as planted:** the hook folder `.claude/hooks/**`, `.claude/settings*.json`, the rest of
`.claude/**`, `<repo>/.git/hooks/**`, `crontab -l`, the pin `<home>/.local/bin/gov`, the dead-man's and the
sentinel's code `governance/project/orchestration/tools/deadman.py` and `sentinel-brief.md`, and the install. After
an (a) ACT changed one of them, the ACT is undone and the control file is restored byte for byte too.

**The evidence record (S23)** `docs/changes/W2-148-evidence.md`, Markdown tables: one with `ACT file` and `Class`
columns (a row per ACT file, the class `(a)`, `(b)` or `(O)`); one with `Class` and `Count`; a heading naming the
`Rises`; one with `Replay`, `Class`, `Outcome` (outcome `applied` or `refused`); one with `Fault` and `Outcome`
(outcome `refused`, `undone` or `lock held`; the fault cells naming `after review`, `class`, `unlisted`, `red`,
`undo`, `missing`, `older`); one with `Path`, `Before`, `After` (sha256s, equal; rows for `gov-os-operator` and
`.claude`).

**Left to the engineer:** the journal's form and place; the clone's place (outside the live tree, cleaned up); the
wall hook's file and arguments; the default paths; how the launcher hands the request to the session; the brief's
text; how the guard replay gets a tree for the old and the new map; how the lock is held after a failing undo; the
names of other steps.

## The designer's notes on the interface (as written)

- **N-1. Readings of the interface.** Where the KPI lines leave a form open (the config file, the result line, the
  bundle's layout, the log's keys, the notice's keys, the test hook), the tests fix the smallest form above; a change
  to it is a test designer's revision, not the engineer's choice.
- **N-2. The two "none" rows.** The CTO's own scratch tools and the blind writers' walls are not the operator's; the
  classifier answers (O) (a path no rule names, for these), so a manifest naming them is refused at G6 as "yours".
- **N-3. G4 against G5.** A verdict block naming another sha fails G4 ("names this manifest sha") and G5; the tests
  accept either gate, and S5's cases want `changed after review` in the reason whichever gate refuses.
- **N-4. Where the freeze and the approvals go.** DEC-1028 (6)'s `log/act-in-progress.txt` and DEC-1058's
  `log/act-approvals.jsonl` live in the CTO's scratch today; S24 puts the agent's files under its own `log/`. The tests
  read the yes copy under the operator root, accept the freeze in either log, and hold G9 on the scratch's file (the
  CTO's hand ACTs and FRESH-80's hold write it there). Wiring the freeze to the CTO's checkpoint tool is ACT-OPERATOR-1's.
- **N-5. The landing check's "control path".** A CTO commit on its records (`CHECKPOINT.md`) is not flagged: the (O)
  catch-all for a path no rule names is not a control path; only the named (b) and (O) rows' paths are.
- **N-6. S23's pinned subset.** Every ACT the §2 table names in its example column, at its row's class: (b) for
  1-GUARD, GUARD-FIX-1 to 4, G14, G14b, INDEP-WALLS-1, GUARD-SETS-1, PERMISSIONS-1/2, QUIET-DENY-1, STOP-WAITER-1,
  PUSH-INPUT-1, SELECT-HOOK-1, SELECT-FIXES-1, GATE-CONFIG-1, NIGHTLY-1, NIGHTLY-STOP-1, SCHEDULE-STOP-2,
  DISPATCH-CRON-2, DISPATCHER-1, RUNS-SWEEP-1, DEADMAN-1, SENTINEL-1, RERANK-TRIAL-1/2; (O) for W1-01-EXEMPT-1,
  W2-57-LS-1, P-TRACE-IMPL-1, REPIN-1, REPIN-2, REPIN-EMERGENCY-1, REPIN-W2 to W4, WSL-INTEROP-1, NIGHTLY-0400, D8. The
  servers' and SANDBOX-SEAL-1's (a) and the walled sessions' rows are not pinned (any class passes "not lower").
- **N-7. The server row.** The committed module `governance/project/orchestration/tools/gov_reranker_gpu_slot.py`
  (RERANK-GPU-SLOTS-1, RERANK-WAIT-1) stands for "the shared servers' committed configs and modules": (a) by Q3.
- **N-8. A failing undo** is the frozen `apply.sh undo` exiting non-zero (before it restores anything).
