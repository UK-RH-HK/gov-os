# ACT-GUARD-CALLLOG-1: the guard's call log (DEC-1106 (2), W2-148's F3)

- **For:** the owner, to decide §7, then the owner's operator (a guard change: P-ACT-SPLIT), as the message in §5.
- **By:** an agent for the CTO, 2026-11-09. Designed, built and rehearsed in a clone. **Nothing live is changed**
  until the operator runs §5.
- **Sources:** DEC-1106 (2), DEC-1104 (2), DEC-1103 (4), DEC-953 item 2, DEC-820, DEC-1082 (3); OPERATOR-AGENT-1 §1
  and §4 (S15, the after-check's replay); SANDBOX-GUARD-EXP-1 §2 (a), SANDBOX-GUARD-EXP-DECLARATION §3, §4, §7;
  `tools/guard_refusals.py` (the refusal ledger, DEC-958); ACT-INDEP-WALLS-1 (the model; its hook is the live one,
  `147706ae`).
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/guard-calllog/` (§4).

## 1. What lands
**Two changes** (`apply.sh`, §5):
1. **The guard** (`.claude/hooks/pretooluse.py`, `d5be03dbb48e` → `a7981319f877`): after each decision the hook
   appends one line to the call log. The rules and their order are unchanged. The only edits to existing lines are
   the rule id passed to each of the 14 `answer(...)` calls and one `record(...)` on the allow path and on the
   fail-closed path. About 150 lines added (`pretooluse.diff`, 314 lines).
2. **The log folder** `~/.gov-os/guard-calls/` (mode 0700), with `salt.key` (0400): 32 random bytes as 64 hex
   characters, the key of the keyed hash. `apply.sh` makes it before the hook changes, so the first line already
   carries a keyed hash. The salt is never printed.

## 2. The log
**Where: `~/.gov-os/guard-calls/<UTC day>.jsonl`.** Why there:
- `~/.gov-os/` is already the machine's own Gov OS state (`machine/gate.json`, the slots, the sessions). It is outside
  the repository, every worktree (`~/gov-os-worktrees`), the run clones (`~/gov-os-runs`) and the sets root. So no
  branch carries it, no `git status` shows it, and no guard walk passes over it (`tree_roots`, the hidden walk and its
  10,000-file cap).
- **Not** the operator agent's install: S15 hashes that as a control file after every (a) ACT, and the log changes
  on every call. **Not** `.gov-runtime/scratch/`: that is inside the main tree and is the CTO's writable scratch.
  **Not** `~/.claude/`: that is Claude Code's folder, and the tuner is refused it (rule 2c).
- `rm` of it is already refused to every session: it is outside the project and its scratch (the catastrophic rule).
  `salt.key` is refused to every role **by name** (rule 3, `*.key`). The live guard refused this agent's own Bash line
  that named it.

**What one line holds** (at most 1 KiB, one `write` to a file opened for appending, so concurrent sessions' lines
never interleave):

| Field | What it is |
|---|---|
| `v` | 1 (the line's format) |
| `time` | UTC, to the millisecond |
| `session` | Claude Code's session id |
| `role`, `ticket` | `GOV_ROLE`, `GOV_TICKET` as the session was launched |
| `agent` | the subagent type (`agent_type`), empty for the main session |
| `tool` | the tool name |
| `decision` | `allow`, `deny` or `ask` |
| `rule` | the rule that decided (below); `none` for an allow |
| `tree` | the **kind** of tree, never its path: `main`, `worktree`, `run`, `scratch` or `other` |
| `ms` | the time from the hook's start to its decision |
| `sha256` | sha256 of the normalised action |
| `keyed` | HMAC-SHA256 of the normalised action under `salt.key`; null when there is no valid salt |

- **The normalised action:** the canonical JSON of `{"tool": <name>, "input": <tool_input>}`: keys sorted, no spaces,
  UTF-8 (`action_bytes` in the hook). A reader recomputes it from a transcript's or stream's `tool_use` (name, input)
  with the same three lines of code. The rehearsal's live session matched every call this way (§6).
- **Never in the log:** the command, a path, a file's text, the folder, the reason text, or anything from the input
  but its hash. The name fields keep only `[A-Za-z0-9._:-]`, at most 64 characters. A `GOV_TICKET` or session id
  carrying anything else is cut down to that.
- **Rule ids:** `2-heldout`, `2-hidden`, `3-secret`, `2-listing`, `2-judge` (another read-judge reason), `2b-line`,
  `2b-write`, `2c`, `g14`, `rm`, `5`, `1`, `4-sudo`, `4-install`, `4-ask`, `deadline` (the 20-second refusal) and
  `error` (the fail-closed exit 2; its `sha256` is null when the input was not JSON).
- **Rotation and limits:** one file per UTC day (mode 0600). A day's file stops at **32 MiB**, about 90,000 calls
  against today's roughly 4,000 a day, and a `<day>.jsonl.capped` marker then says so. Files older than **92 days**
  are removed, by their names only, when a new day's file starts. About 1.5 MB a day.
- **A failure never changes the decision or blocks the call.** The decision is made first. The log then stops the
  20-second deadline and runs under its own 2-second one. Any error is caught and noted once on stderr
  (`guard (ACT-GUARD-CALLLOG-1): the call log was not written (...); the decision stands`), and the decision is
  answered as before. The day file is opened with `O_NOFOLLOW`. A folder that is a link, not a folder, or not this
  user's is not written.
- **`GOV_GUARD_CALLS_DIR`** (an absolute path; anything else is ignored) moves the log. It exists for the rehearsals
  and the suites, so their planted calls do not land in the live log (§7 item 5).
- **Telling live calls from planted ones:** Claude Code's session ids are UUIDs. The suites, checks and replays use
  fixed names (`guard4-check`, `live-hook`, `guard-fix-4`, `seal-replay`) and run in `run` or `scratch` trees. Readers
  keep lines whose `session` is a UUID and whose `tree` is `main` or `worktree`.

## 3. What each consumer gets, and whether hashes alone serve it
The log holds no action, so any consumer that must **re-judge** an action has to get the action itself from
elsewhere, today the transcripts under `~/.claude/projects`. Every guarded session keeps one: no launcher uses
`--no-session-persistence`. It then matches the action to the log by `(session, sha256)`. What the log adds to the
transcripts is:
- the **authoritative list** of calls the guard judged in a window;
- the **real role and ticket** of each session, where today's readers guess the role from the first user message's
  first 300 characters (G-14's rule, the experiment's §3 item 1);
- the **live decision and the rule** of each call, where today's readers parse the reason text.

**(a) W2-148's after-check replay (S15): not served by hashes alone. It needs the action itself.** The merged code
(`governance/project/operator/operator_run.py` `replay()`, `511a4a17`) reads one file, the `calls` setting, whose lines
are full events: `{id, time, role, ticket, event: {tool_name, tool_input, cwd}}`. It re-runs the guard on each event
before and after. Today `calls` defaults to the operator's own dry-run commands (`<operator root>/log/calls.jsonl`),
not the 48 hours of every session. Pointed at this log, it would refuse every path-map ACT, rightly: no line has an
`event`, so it reads "malformed line (fail closed)". The operator agent may read only the CTO session's own transcript
in `~/.claude/` (OPERATOR-AGENT-1 §1), so it cannot rebuild the events itself either. Three options, least revealing
first:
1. **Recommended: a corpus built by the CTO's tool, checked by the operator against the log.** Each request carries
   the window's corpus in W2-148's `calls` format, built by the existing reader (`replay_sets.py`'s rule: inputs only,
   never a tool result, the sets root rewritten or the call dropped and counted). It is passed as that run's `calls`
   file. Before re-judging, the operator agent checks it **both ways by `sha256`**:
   - every corpus line's `action_bytes(event.tool_name, event.tool_input)` hashes to a logged line of the same session,
     with the log's role and ticket, which win over the corpus's;
   - every logged live call of the window (a UUID session, `main` or `worktree`) has a corpus line, or is counted as
     dropped by rule.

   A dropped, altered or invented call fails the check, so the CTO cannot shape the replay. No new store of actions
   is kept; the corpus lives only for the check. The cost is about 30 lines in `replay()` plus the corpus builder, in
   W2-148's next pass (F21's round, DEC-1107, or a follow-up).
2. The operator agent reads the transcripts' tool inputs itself. This widens its `~/.claude/` access, and a
   transcript also holds every tool result.
3. The hook keeps the actions themselves (a `.secrets/` store, refused by name, 72 hours). That is a second copy of
   every action's text, Write and Edit contents included. **Not recommended.**

What the log alone gives the after-check: the window's calls by rule and role, the live baseline for each call, and the
completeness check in option 1.

**(b) The sandbox-and-guard experiment's scorer: served by hashes alone, from the next window.** Its fixed window
(2026-11-02 to 11-09) predates the log, so the declaration stands unchanged. For a fresh held-out window (needed after
a held-out failure, design §4) or a re-run, the extractor already holds the actions (transcripts). It joins them to
the log by `(session, sha256)` and takes the real role and ticket, and the live decision as "A as live in situ": a
check of the replay's fidelity (the replayed decision against the live one, per rule). The scorer still joins labels to
decisions by action id; the labels come from the action text, as designed. Shared reports quote `keyed`, never
`sha256` (§7 item 3). One addition is needed then: the log shows live decisions per session, so the tuner should
be refused it (§7 item 4).

**(c) The weekly false-refusal counts: counts by hashes alone; the verdict from the transcript, as today.** From the
log alone come:
- refusals per rule, per role and per week;
- the denominator (every call judged), which the ledger lacks today, so a refusal rate per rule;
- the same refused action retried (equal `keyed`), across days;
- after a guard change, the allow→refuse count per rule over a window: the before decisions in the log, the after
  decisions by the replay (a).

Whether a refusal is **false** needs the action. `guard_refusals.py` already harvests it from the transcripts. The join
by `(session, sha256)` gives it the rule id exactly, instead of parsing the reason.

## 4. The files (drafts, scratch; checked by hash before they apply)
| File (`drafts/guard-calllog/`) | sha256 (first 12) |
|---|---|
| `pretooluse.candidate.py`: the live hook `d5be03dbb48e` plus the call log | `a7981319f877` |
| `pretooluse.diff` (review diff) | `a868f5fbc53c` |
| `apply.sh`: `check`, `apply`, `undo` (backup with sha256s; the folder and salt; undo byte for byte) | `1e0d09b74cc9` |
| `calllog_check.py`: the checks of §6 (validate, planted, faults, prune, concurrent, latency, micro, replay, live) | `282f7eb974eb` |
| `rehearse.sh`, `rehearsal.log`, `REHEARSAL.md` | `82c7b2e7d3a9`, `3bcf2e2d7012`, `78618554f5ba` |

`apply.sh check` and `apply` stop unless the live hook still hashes `d5be03dbb48e` (checked on the main tree at
2026-11-09 17:09, head `b134a760b93c`: "check: ready to apply") and the candidate hashes as built. The log folder must be absent, or a
0700 folder with a valid salt from an earlier apply (kept, so keyed hashes stay comparable). `apply.sh` refuses a log
folder inside the tree, the worktrees, the run clones or the sets root. **If the hook moves before you apply, the CTO
rebuilds and re-runs the rehearsal first.**

## 5. The operator's steps: the message
> **ACT-GUARD-CALLLOG-1 (DEC-1106 (2)): the guard's call log.** In the main tree, about one minute:
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> G=.gov-runtime/scratch/orchestrator/drafts/guard-calllog
> bash $G/apply.sh check     # "check: ready to apply" (exit 0)
> bash $G/apply.sh apply     # backup; ~/.gov-os/guard-calls (0700) with its salt (0400); the hook; "state applied"
> git add .claude/hooks/pretooluse.py
> git diff --cached --name-status    # expect exactly: M .claude/hooks/pretooluse.py
> git commit -m "ACT-GUARD-CALLLOG-1: the guard appends each decision to ~/.gov-os/guard-calls (hashes of the action, the role, the ticket, the decision and its rule; never the contents)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1106" --trailer "Role: owner"
> ls -l ~/.gov-os/guard-calls      # within a minute: today's <YYYY-MM-DD>.jsonl, mode -rw-------
> ```
> **Undo:** `bash $G/apply.sh undo` restores the hook byte for byte. It leaves `~/.gov-os/guard-calls` as the record,
> unless it holds nothing but this apply's salt.

**Then the CTO**, the same day: merge `w2/integrate` into the live worktrees (each runs its own copy of the hook;
until then their calls are not logged). Confirm the first day's file validates
(`calllog_check.py validate ~/.gov-os/guard-calls`). Then file the follow-ups of §7 items 2, 4 and 5.

## 6. The rehearsal (DEC-1057): `REHEARSAL.md` and `rehearsal.log`
There was one clean run, 16:59–17:09 GMT, from a fresh `env -i` shell, with **0 failures**. It used a
`--no-hardlinks` clone at the main tree's head with a worktree and a planted sets root. Each step had its own log
folder in `/tmp`, and the live `~/.gov-os/guard-calls` was checked absent at every step.

| Step | Result |
|---|---|
| Suites before / after | `test_guard_fix_4` 467 passed; `test_g14` 151 passed, 1 skipped; W2-58 sets, launcher, live hook, reads 109 passed, 2 failed: **the same before and after**. The two W2-58 launch cases already fail at this head without the ACT |
| `guard4_check.py --settings <clone>` | 501 run, 0 failed, before and after; after: 501 valid lines |
| `apply.sh` | check ready; applied; a second apply refused; a log folder inside the tree refused |
| Replay, 48 hours, 8,142 unique calls | before → after **0 changed** (8,103 allow, 39 deny). After: **8,142 lines, one per call**. (sha256 recomputed, decision) pairs equal to the log's exactly |
| **Planted session**, 22 calls by the registered line | decisions as before 22/22. **22 lines and nothing else**: 8 allow, 13 refusals (one per rule id, `error` included), 1 ask. Each line's hashes match those recomputed; no input text in the log; the same action in another session carries the same hashes |
| **Faults**, 11 kinds × 22 calls | **0 of 242 decisions changed**: read-only folder or file, full disk (EFBIG), cap reached, folder a file, day file a link, folder a link, a hanging write, no salt, a relative setting, an unwritable default. One stderr note per unlogged call; nothing written through a link; a hang costs 2.0 s |
| Prune, concurrency | past 92 days removed by name only; 8 sessions at once: 200 whole lines |
| **Latency**, 120 calls each, alternated | median 71.0 → 73.0 ms (**+2.0 ms**); p95 128 → 123 ms (noise); the log itself **43 µs** per call |
| **Live session** (haiku, as an engineer) | 6 tool calls in Claude Code's stream, **6 lines, 6 of 6 matched by sha256** recomputed from the stream. Decisions as the results (3 allow; `4-sudo`, `3-secret`, `1`); 0 extra lines; 0 marker text; $0.006 |
| `apply.sh undo` | the hook byte for byte; `git status` clean |
| Live files (the hook and its two modules, the map, `held-out.yaml`, the settings, `~/.claude/settings.json`; `~/.gov-os/guard-calls`) | **unchanged** (absent) |

Run 1 (16:47) had the same counts. Its last check failed on its own test: it counted the main tree's HEAD, which other
sessions moved meanwhile (W2-148's merge, DEC-1107), and this untracked package. The check now compares the files'
hashes. Recorded in `REHEARSAL.md`.

## 7. For your decision
1. **Approve the location, the fields and the limits** (§2). Recommended: yes.
2. **W2-148's replay (§3 (a)): option 1.** The CTO's tool builds the 48-hour corpus (inputs only) in the `calls`
   format the merged `replay()` already reads, and the operator agent checks it against the log by `sha256` both ways
   before re-judging. It is a W2-148 code change (about 30 lines in `replay()`, plus the builder, and S15's wording),
   with a designer case: in F21's round (DEC-1107) or a follow-up before the first path-map ACT goes through the
   operator. Until then the after-check replays only the operator's own dry-run commands, as merged. Recommended:
   option 1. Options 2 and 3 reveal more. This ACT does not depend on the choice: the log is useful from day one for (c).
3. **Keep the plain `sha256` beside `keyed`?** Kept as asked. The operator agent's check of the corpus cannot use the
   salt (its wall refuses secrets), and a reader with the action needs no key. Its cost: anyone who can read the log
   (every session of this user; mode 0600 keeps out only other users) can confirm a guess of an **exact** action.
   Nothing is revealed that is not guessed whole. Guarded sessions' actions do not carry hidden-set text (they are
   refused it), so a guess confirms only that a call was made. Shared reports quote `keyed`. Recommended: keep.
4. **The tuner and a fresh experiment window:** add `~/.gov-os/guard-calls` to `session_hidden` for the engineer on
   W2-56. This is one path-map entry under rule 2c, no code, done when a fresh window is opened. Recommended: yes,
   then.
5. **The log's integrity and the seam:**
   - **Integrity.** The log is this user's file. The guard refuses `rm` of it, but a session's shell could still
     append to it or truncate it (the hook does not judge writes outside the trees). Option: the guard refuses
     resolved writes into `~/.gov-os/guard-calls` to every session, the same pattern as F5's freeze file (DEC-1106
     (3)), in that ACT. Recommended: yes, with F5.
   - **The seam.** `GOV_GUARD_CALLS_DIR` could move a launched session's log. The replay's join shows it, as calls
     with no line. The suites that run the live hook (`tests/unit/hooks/test_live_hook.py`, W1-46, W2-59, W2-116 and
     W2-141 support, `guard4_check.py`) do not set it today. After the ACT, their planted calls will land in the live
     log, under fixed session names that readers drop (§2). Follow-up: set it to a temporary folder in those suites
     (an engineer pass; W2-141's are acceptance tests, so that file is the test designer's). Recommended: keep the
     seam, file the follow-up.

**Residuals:**
1. The log records the **hook's** decision only. A call refused by Claude Code's own permission rules (the settings
   deny lists) is not the hook's decision; whether the hook ran first is Claude Code's. A hook killed at Claude Code's
   60-second timeout leaves no line; the guard's own deadline is 20 seconds, the log's 2 more.
2. Calls before the apply, and in a worktree before its merge, are not logged.
3. A session can still guess-confirm an exact action through `sha256` (item 3).

**What it costs:** about +2 ms on a 71 ms hook call (the log itself 43 µs). About 1.5 MB of disk a day, at most 32 MiB a day, 92 days
kept. No install, no GPU.

**Basis:** question 2 (a guard whose decisions are logged without their contents; an operator that can never be shown
a curated replay).
