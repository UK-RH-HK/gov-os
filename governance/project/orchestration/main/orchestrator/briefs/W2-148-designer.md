# W2-148 — the independent test designer's brief (DAEO-xafn)

You are the independent test designer for **W2-148** (`.tickets/DAEO-xafn.md`): the operator agent, which applies
ACTs by class from a queue in a walled headless session, only when every gate passes (the owner's DEC-1104 (2),
approving `governance/project/orchestration/packages/OPERATOR-AGENT-1.md` with all seven answers as recommended). Read
the ticket in full first, including its body's "Readings settled by the CTO", then the package in full: its §1 to §6
are the specification. Its KPI lines S1 to S24 and its fourteen failure lines are what you test. Profile FULL:
thorough, every success and failure line with its edge cases, every gate refusing on its own.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-148-tests`, branch `w2/W2-148-tests`, made from `w2/integrate` today.
- You write only `tests/acceptance/W2-148/`: the cases, a `conftest.py` and support module(s) (the planted builders),
  and a `README.md` whose map the runner reads (header `| KPI line | Test (node id) | On integrate | Why |`, one id such
  as `S1` in each KPI cell, the test in backticks with its full node id, as `tests/acceptance/W2-133/README.md`).
- **State the interface in the README,** so the engineer builds to it: the code lives in `governance/project/operator/`
  (nothing there yet); give the command forms and module functions your cases call (`operator_run.py <step> <ACT>
  <manifest sha>`, `act_class.py`, `operator_launch.py`, the landing check's function), the arguments or settings that
  plant every location (operator root, repository, HOME, the CTO's scratch, the transcript folder, the clock: S24), the
  ACT bundle's layout and the manifest's fields (touched files with before/after sha256, commands, checks with their
  rehearsed exit codes and counts, the DEC id, the rehearsal log and review record with their hashes, the claimed
  class, the author), the queue line's form, the verdict block's extra fields (`manifest_sha256`, `class`), the log
  line's fields, the refusal reasons or exit codes, the commit trailers, and the notice channels' stub points. Keep it
  as small as the KPI lines need; name what you leave to the engineer.
- **Your record:** your whole return (the twelve fields below) is your session's **final message**, in full: the
  launcher keeps it in this worktree's `.gov-runtime/scratch/lead/log/W2-148-designer.json`, which is the record (your
  session cannot write that folder itself, and its own scratchpad is deleted when it ends).
- **You may read:** any code and record on `w2/integrate` in your worktree: the package, `ACT-INDEP-WALLS-1.md` and the
  other ACT files under `governance/project/orchestration/packages/` (the table's rows, and S23's list),
  `governance/project/indep-walls/` (the walls' template: `wall_hook.py`, `settings.json.tmpl`, `kinds.yaml`, which
  this ticket reuses), `governance/project/path-map.yaml`, `governance/project/test-map.yaml`, `tests/optin-*.txt`,
  `.claude/hooks/pretooluse.py`, `docs/DECISION_REGISTER.md` (the Status line's form for S2), and
  `governance/project/orchestration/tools/` for how the CTO's committed tools are tested. Two reference copies from the
  CTO's scratch are in your worktree: `.gov-runtime/scratch/ref/verdict.py` (the verdict block's form and `ready()`;
  the install pins a copy) and `.gov-runtime/scratch/ref/LAUNCH-SPEC.md` (the walls' launch script, its canary S9 and
  its clean-environment launch line S10, which S17 and S18 reuse).

## What the cases must show (from the ticket)
- **S1 to S5, S9, S11 to S13 (the gates):** each gate refusing on its own, with every other gate passing in the same
  planted bundle, and nothing applied (the planted live tree's hashes unchanged); G9's holds wait and then proceed.
- **S6 (the classifier):** one planted manifest per row of the package's §2 table, both sides of every "only added" or
  "only removed" row (a deny-list addition (a) against an allow-rule addition (b); a `couplings` addition (a) against a
  `record_only` addition (b); an opt-in line removed (a) against one added (b); a path-map refusal-list addition (a)
  against a removal (b)), each script hit, an unknown path (O), an unparsable list file (never (a)), a mixed manifest.
  Note: the CTO's own scratch tools and the blind writers/checkers rows are "none" (not the operator's): say how the
  interface answers them (refused as not an ACT, or (O)) and test that.
- **S7, S8 (votes and recompute):** every disagreement order; the recompute between G6 and the apply through a test
  hook the interface names.
- **S10 (the yes):** planted transcripts as JSON lines in the shapes below; only the human line after the review with
  the right ACT and sha8 counts; the verbatim copy in `log/act-approvals.jsonl`.
- **S12 (dry run):** the unlisted-file cases in the clone's tree and in the planted HOME, and a non-byte-for-byte undo.
- **S14, S15 (apply and after-check):** the commit's files and trailers in a planted repository; one (a) ACT per
  control family that also changes a control file (crontab through a stub on PATH), each undone with a P1; the guard
  replay through a planted call log and a planted path map.
- **S16 (landing check):** the planted range of the ticket's Verify.
- **S17 to S19 (launch, canary, the wall):** a stub `claude` on PATH recording argv, cwd and environment; malformed
  queue lines; one install file changed against `APPROVED`; the canary's refusal with settings made invalid; the wall
  hook driven per allowed form and per refused class, fail closed; a source scan for name-matched kills.
- **S20 to S22 (log, pushes, undo):** an injected clock for the 14-day and 7-day windows; stub channels; the planted
  unfinished journal.
- **S23 (the trial):** the engineer's measured record. Test that `docs/changes/W2-148-evidence.md` exists with a row
  per ACT file, the counts per class, the rises listed, the 8 replays and 7 faults with their outcomes, and the
  before/after hashes, and that no ACT is classed lower than your own reading of the table for the rows you can pin
  from the ACT files' titles and touched paths (pick a fixed subset; say which). Red until the engineer writes it.
- **S24:** a planted operator root holding stand-ins for the owner's files (`CLAUDE.md`, `.claude/settings.json`,
  `hooks/`, a dated `log/*.log`): unchanged after a full run; the session's cwd is the wall folder.
- Every case is red on integrate for the right reason (the code does not exist yet) unless it is a green guard; say
  which. Mark any case that needs a live `claude` session as live and keep it out of the default run.

**The transcript shapes (Claude Code 2.1.319, the ticket's reading; plant these, never read a real transcript):** one
JSON object per line. A typed owner turn, from the terminal or Remote Control: `{"type": "user", "origin": {"kind":
"human"}, "promptSource": "sdk", "isSidechain": false, "timestamp": "<ISO>", "sessionId": "<id>", "message": {"role":
"user", "content": "<text>"}}`, the content also possibly a list of `{"type": "text", "text": ...}` blocks. A subagent's
result: the same with `"origin": {"kind": "task-notification", ...}` and `"promptSource": "system"`. A tool result:
`"message": {"role": "user", "content": [{"type": "tool_result", ...}]}` with a `toolUseResult` key. System lines:
`"isMeta": true`, `"origin"` null. A subagent's own lines: `"isSidechain": true`. The session id is the one line of
`log/cto-session.txt` in the CTO's scratch; the transcript is `<transcripts folder>/<session id>.jsonl`.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)):** there is none yet; never open the engineer's
  worktree (base name `W2-148`, under the worktrees folder) or the branch `w2/W2-148` if either appears, and never read
  the engineer's files on this ticket. You work from the ticket's KPI lines, the package and today's integrate code.
- **The exclusion line (DEC-1093 (2)), for you:** keep every Grep, Glob and recursive Bash search inside your own
  worktree. If a search must start above it, it carries the exclusion by base name: `--exclude-dir=W2-148` for grep,
  `!**/W2-148/**` for Grep and Glob, `-path '*/W2-148' -prune` for find. If a search shows you a line of the
  implementation anyway, stop reading it and say so in your return.
- **Search again once (DEC-1092 (1)):** if what you searched (Grep and Read; no `gov retrieve` in the sandbox,
  `EMG-d4b-launched.md`) does not answer, or you can tell your answer may be incomplete, search once more in your own,
  different words; then answer from both searches and the files you read, with path and lines, or say "not found".
  Two searches in all.
- **Planted folders only:** every case under a temporary folder (operator root, HOME, repository clones, transcripts,
  register, queue). Never touch or read the real `~/gov-os-operator/`, `~/.claude/`, crontab, the live hook, settings or
  git hooks; a case that would reach them fails closed. No real `claude` session outside a case marked live; no GPU,
  no model, no network, no installs.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run your cases through the heavy slot that `EMG-common.md` names (where the sandbox allows it), with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-148-tests/src`, and run
  `python3 -m gov.cli.main accept W2-148 --root /home/usain/gov-os-worktrees/W2-148-tests` to show the runner reads
  your map.
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains; one line
  before any command that will ask for permission.
- **Commit** on `w2/W2-148-tests`, only `tests/acceptance/W2-148/`, with
  `--trailer "Task: DAEO-xafn" --trailer "Implements: DEC-1104" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Before you end your session,** make sure every test run you started has finished: do not end with a background
  run still going; any wait or stop by pid, never a name match.
- Keep to the estimate: tests about half a day; FULL, so every line covered, but one case per edge, no combinatorial
  expansion (about 60 to 90 cases).

## Return
The twelve labelled fields of `EMG-common.md` (sandbox check and `ps` check first), with the case list (node id, KPI
line, red or green on integrate, and why), the interface the README states, the commit, `gov accept`'s counts,
`TESTS-READY` text, and anything untestable or ambiguous as `discoveries` or a decision package with your
recommendation and confidence.
