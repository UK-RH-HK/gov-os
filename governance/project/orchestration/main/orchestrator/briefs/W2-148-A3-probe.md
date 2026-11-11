# W2-148 (DAEO-xafn): FULL review of the operator agent's merged code (independent auditor)

You are a fresh **independent auditor** (Opus 5.5, effort high, class C3; RUBRIC-2, DEC-1120: reviewers run on Opus at
high, the old max is replaced), launched by the CTO (orchestrator DAEO-sdxk, session b40cba91, 2026-11-11) under ticket
`DAEO-xafn` (W2-148) from the worktree `/home/usain/gov-os-worktrees/W2-148` (the ticket's own worktree, on branch `w2/W2-148`). Your job is one **FULL, read-only review of the
ticket's merged code at the head of `w2/integrate`**, judged on the ticket's KPI lines alone (DEC-1131), producing a probe
record text that the CTO commits as `docs/probes/DAEO-xafn/PR-DAEO-xafn.md`. You cannot write it: you return it as text.
The record is the evidence the ticket's formal close needs (BATCH-PREP section 2: the ticket is merged but has no `docs/probes/DAEO-xafn/`; the CTO found that the scratch reviews are not a valid probe of the final code (below), so this is the fresh FULL review its close needs). Nothing here is a round of changes: you find, you
do not fix.

## Step 0 and the common rules

- **Step 0, the sandbox check, reported first in your return** (the launcher's `EMG-d4b-launched.md`, copied beside this
  brief): (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-xafn','w').write('x')"` must fail; (b)
  `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b)
  failed, stop and return. Then `ps -eo pid,args` on its own (no pipe): report that no ollama or llama-server process is
  yours.
- Read first, whole: `EMG-common.md` and `EMG-d4b-launched.md` beside this brief. The CTO's lift files (`LIFT-common.md`,
  `NIGHT-common.md`) are not copied for you; their rules that apply are restated in this brief, with these changes to the old
  text: the lift's closes are done; the main tree (`/home/usain/Dynamic-Agentic-Engineering-OS`) must stay clean (you never
  write there); the next free decision id is DEC-1137 (yours to propose, never to write); your temporary folder is the
  sandbox's own `TMPDIR` (never a new `/tmp/gov-os-emg-*` folder).
- **You are read-only.** Your tools are Bash, Read, Grep and Glob; you have no Write or Edit. Write only under your own
  `TMPDIR` (a probe script goes there as an inline `python3 -I -c '...'`, or a file made one simple command at a time). Never
  `git add`, `commit`, `stash`, `checkout`, `reset`, `merge`, `push` in any repository you did not clone yourself, and never
  commit anything at all: the record is returned as text and the CTO commits it. A reviewer commit anywhere in the ticket's range
  would make the probe record invalid (DEC-137). If the Write tool is refused when you try it, do not make the file another
  way; say so in your return.
- **The guard's rules hold.** No installs. No reads of secrets or of held-out material; never open `~/gov-os-eval`,
  `~/gov-os-runs`, `~/gov-os-wall-trees`, `~/gov-os-operator`, any folder named `hidden`, `memory-verdict` or
  `memory-verdict-2`, or the real `~/.claude`. A refusal is taken, never routed round (a false refusal is worked round by an
  equivalent form, named in your return). **Refused twice for the same call: stop and say so; no third try.**
- **No real model, embedder, reranker or GPU job, and no network (DEC-1064, DEC-1065).** Never run `gov retrieve` or
  `gov context`; read code with Grep and Read. Every test of yours uses stand-ins.
- **Waits and stops by pid only** (`tools/proc.sh`: `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh`),
  never the Monitor tool, never a process-name match (`pgrep -f`, `pkill`, `killall`). Run a long command in the background and
  wait on its pid.
- **Under `.gov-runtime/` and in everything you return, write commit hashes as 12 digits** (row W2-L423's rule), and write none
  of the keywords `tools/keyword_warn.py` looks for (they are written in parts in that file; never copy them out).
- **Scratch budget: 30 GB and 2,000,000 files and folders** outside the tracked tree. Report `du -sh` and `du -s --inodes` of
  your `TMPDIR` in `evidence`, and remove your clone and probe folders when done.
- **Context:** past about 200k tokens, hand over: write what you have and what remains, status PARTIAL.

## The head you review: a clone of `w2/integrate`

Your own worktree is **hundreds of commits behind** `w2/integrate` and is not what is merged. Do not judge its files. Make a
clone at the start and read and run everything from it:

```
git clone -q --no-hardlinks --single-branch -b w2/integrate file:///home/usain/Dynamic-Agentic-Engineering-OS $TMPDIR/clone
git -C $TMPDIR/clone rev-parse --short=12 HEAD
```

The head was `7b5c3cb94fd9` when this brief was written. **Review the clone's head at your start** and name its 12 digits as
the record's `probed_commit`; if it is not `7b5c3cb94fd9`, run `git -C $TMPDIR/clone diff --stat 7b5c3cb94fd9 HEAD -- governance/project/operator tests/unit/operator tests/acceptance/W2-148 docs/changes/W2-148-evidence.md`
and say what moved. Run code with `PYTHONPATH=$TMPDIR/clone/src`, and with `HOME` set to an empty folder under `TMPDIR` (add
`PYTHONUSERBASE=/home/usain/.local` if the empty HOME hides pytest or another module).

## The frame: the ticket's KPI lines (judge only these, DEC-1131)

Ticket `DAEO-xafn` (`.tickets/DAEO-xafn.md` in the clone: read it whole, including its notes). Its KPI lines are below, in the
ticket's own words, with the id each takes in your verdict block. **Judge each line by what it says and by its `Verify:`
text where it has one. A thing the ticket does not state is not a finding; a thing a line does state that is not met is.**
A failed line is `"verdict": "fail"` (a failed line blocks READY, DEC-1131 (3)).

- **S1**: S1 G1 Frozen: the run copies the ACT bundle into `acts/<id>-<sha12>/` under the operator root, read-only, and refuses unless every file hashes as the manifest says; from then on it runs only its own copy, so an edit to the CTO's scratch after the copy changes nothing. Verify: a planted bundle with one byte changed before the copy (refused, nothing applied); a planted bundle edited in the source folder after the copy (the run uses the frozen bytes; the frozen folder is not writable) [DEC-1104 (2); DEC-1103 (4)]
- **S2**: S2 G2 Under a decision: the manifest names a DEC id that the register holds with Status ACCEPTED; a missing id, an id not in the register, or an entry not ACCEPTED refuses. Verify: a planted register with an ACCEPTED, a PROPOSED and an absent id [DEC-1104 (2); DEC-1103 (4)]
- **S3**: S3 G3 Rehearsed (DEC-1057): the rehearsal log is in the bundle, hashed in the manifest, and ends with 0 failures; a missing log, a hash mismatch or a log ending with failures refuses. Verify: three planted bundles, one per case [DEC-1104 (2); DEC-1103 (4); DEC-1057]
- **S4**: S4 G4 READY: the review record's last verdict block names this manifest sha and a class, and the install's own pinned copy of verdict.py computes READY; for an ACT any KPI marked fail also refuses (the moderator's triage does not apply); the reviewer's brief hashes as its line in APPROVED and the reviewer is not the ACT's author; a third review round refuses with "to the owner". Verify: planted review records: READY; not READY; a malformed block (fail closed); a block naming another sha; a fail with no blocking finding; a changed reviewer brief; reviewer equal to author; three rounds [DEC-1104 (2); DEC-1103 (4); DEC-1010]
- **S5**: S5 G5 Hashes match: the manifest sha in the queue request, in the verdict block and as recomputed from the frozen copy are the same; any one differing refuses with "changed after review". Verify: three planted mismatches, one per pair [DEC-1104 (2); DEC-1103 (4)]
- **S6**: S6 The classifier on every table row: `act_class.py` with `class-rules.yaml` reads a manifest (every touched file with its before and after sha256, every command) and gives each row of OPERATOR-AGENT-1 §2's table its class: list-shaped files are parsed before and after and are (a) only when the only differences are items added to a named refusal or coupling list or lines removed from an opt-in list; any other change to them is (b) or (O) as the row says; a script hit for sudo, push, tag, an install, a network call or rm outside the project raises the class; an unknown path is (O); the ACT's class is the highest among its files; a file that cannot be parsed is never (a). Verify: one planted manifest per table row (both sides of every "only added"/"only removed" row), each script hit, an unknown path, a malformed list file, a mixed (a)+(b) manifest giving (b) [DEC-1104 (2); DEC-1103 (4)]
- **S7**: S7 Three votes, and the class only rises: the class applied is the highest of the code's vote, the class the ACT file claims and the reviewer's `class` field; a disagreement is written to the log, shown in the digest and pushed as a P1; no vote can lower the code's class. Verify: planted votes in every order of disagreement ((a)/(a)/(b), (b)/(a)/(a), (a)/(b)/(a), any with (O)): the highest applies each time, the disagreement logged [DEC-1104 (2); DEC-1103 (4)]
- **S8**: S8 Recompute and refuse: immediately before the apply, the class is recomputed by `act_class.py` from the frozen copy of the patch, not from any claim; a result different from the class recorded at G6 refuses, logs and pushes a P1. Verify: a planted bundle whose frozen patch classifies higher than the class recorded at G6 (via a test hook between G6 and the apply): refused, nothing applied [DEC-1104 (2); DEC-1103 (4)]
- **S9**: S9 G6 for (a): an ACT runs as (a) only when the class applied (S7) is (a); (O) always refuses with "yours"; (b) goes to the owner's yes (S10). Verify: planted (a), (b) and (O) bundles: (a) proceeds with no yes; (O) refused at G6 with nothing applied [DEC-1104 (2); DEC-1103 (4)]
- **S10**: S10 G6 for (b), the owner's yes from the transcript: a (b) ACT runs only after a line `yes ACT-<id> <sha8>` (sha8 the manifest sha's first 8 hex) typed by the owner after the review's time, read from the CTO session's own transcript (the session named in `log/cto-session.txt`): a `type: user` line marked human (`origin.kind: human`), its content a string or text blocks, not a tool result, not a task notification, not `isMeta`, not a sidechain; never from a record the CTO wrote. The yes is copied verbatim into `log/act-approvals.jsonl`. A yes for another ACT or sha, one older than the review, or the same text in a non-human line does not count. Verify: planted transcripts in the shapes Claude Code writes today (human turns from the terminal and from Remote Control, tool results, task notifications, meta lines, sidechain lines): only the human line after the review counts; each other case refused [DEC-1104 (2); DEC-1103 (4); DEC-1058]
- **S11**: S11 G7 Live state as stated: the frozen `apply.sh check` passes against the live before-hashes; a moved live file refuses with "rebuild, rehearse, re-review". Verify: a planted live tree with one listed file changed [DEC-1104 (2); DEC-1103 (4)]
- **S12**: S12 G8 Dry run, undo and the touched-file check: in the agent's own clone at the live head with a planted HOME, it runs `check`, `apply`, the manifest's checks, then `undo`; the run refuses unless the undo restores every file byte for byte and the set of files changed by the apply, in the clone's tree and in the planted HOME together, equals the manifest's touched list; an extra file, a missing file or an undo that is not byte for byte refuses. Verify: planted bundles whose apply touches one unlisted file in the tree, one unlisted file in the planted HOME, and whose undo leaves one byte different: each refused, the live tree untouched [DEC-1104 (2); DEC-1103 (4)]
- **S13**: S13 G9 Holds: a run inside the quiet hours (02:00 to 07:30), during the nightly's window, while a close queue runs or while `log/act-in-progress.txt` exists waits, and proceeds when the hold clears; it never refuses for a hold. Verify: an injected clock and planted hold files: each holds, then proceeds once cleared [DEC-1104 (2); DEC-1103 (4)]
- **S14**: S14 The apply and its commit: the run writes `log/act-in-progress.txt` (the commit freeze), runs `apply.sh apply` and the manifest's checks against the rehearsal's stated exit codes and counts, refuses unless `git diff --cached --name-status` equals the list, commits only the listed files with the trailers `Role: operator`, `Act: ACT-<id>`, `Act-sha: <manifest sha>`, `Class: a|b`, `Review: <review record sha>` and, for (b), `Approved-by: owner (chat, <time>)`; never `Role: owner`, never a push, a tag, sudo or a history rewrite; the freeze file is removed at the end. Verify: a planted repository: the commit's files and trailers; a staged extra file refused; a check whose count differs from the rehearsal's red (S19) [DEC-1104 (2); DEC-1103 (4)]
- **S15**: S15 The post-apply control-file check for (a): after an (a) ACT is applied, the hook folder, the settings, `.claude/**`, the git hooks, `crontab -l`, the pin, the sentinel's and the dead-man's code and the operator's install must hash as before; the path map and the settings deny lists may differ only by the computed additions; for path-map or deny-list additions, a replay of the guard on the last 48 hours of calls changes no allowed call to refused apart from the cases the review listed; any other difference undoes the ACT at once and pushes a P1. Verify: a planted (a) ACT that also changes a control file (each control family once, crontab through a stub): undone byte for byte, P1 pushed; a planted path-map addition whose replay turns one unlisted allowed call to refused: undone, P1; the replay re-judges the call set only after checking it against the guard's call log by sha256 both ways (DEC-1108 (2), the note below): a set call with no log line, a logged live call missing from the set, a short or stale window or a capped log each refused and named [DEC-1104 (2); DEC-1103 (4); DEC-1108 (2)]
- **S16**: S16 The landing check: a function in the install, given a range of first-parent commits, flags every commit outside a ticket (as the landing selection reads it: `Role: owner`, or no `Task: DAEO-<id>` other than the CTO's) that touches a (b) or (O) control path of the rule table without `Role: owner`, or without `Role: operator` together with an `Act:` trailer, as one inbox P1 item each; a commit with the right trailers, or touching only (a) or ticket paths, is not flagged. Verify: a planted range: a CTO commit on the guard hook (flagged), the same with `Role: operator` but no `Act:` (flagged), an operator commit with both (not flagged), an owner commit (not flagged), a ticket commit (not flagged) [DEC-1104 (2); DEC-1103 (4)]
- **S17**: S17 The queue and the cron launch: the CTO writes one request line (the ACT's id and its manifest's sha256) into `queue/`; that is the only input; `operator_launch.py`, run by the dispatcher's cron line every 10 minutes outside the quiet hours, picks up the oldest request, runs the canary (S18), then starts the walled session (`claude -p --restricted` with the wall's settings, from a wall folder built from `governance/project/indep-walls/`'s template inside the operator root, never the root itself, with a clean environment: no `GOV_*`, no `CLAUDE_PROJECT_DIR`), records its pid and pgid, and waits and stops only by them; a malformed request line is refused and moved aside; a launch by hand passes through the same gates. Every result prints the sha256 of `install/APPROVED`, and any install file not matching its APPROVED line refuses every run. Verify: a stub `claude` on PATH recording argv, cwd and environment; planted good and malformed queue lines; one install file changed by a byte (refused); a code search for name-matched kills (`pkill`, `killall`, `pgrep -f`): none [DEC-1104 (2); DEC-1103 (4); DEC-1073]
- **S18**: S18 The canary: before each real session a one-turn session in the wall must come back with a Read outside the wall in its `permission_denials`; otherwise the launch refuses before the real session. Verify: a wall whose settings are made invalid on purpose (a stub `claude` modelling the ignored settings): refused, no real session started [DEC-1104 (2); DEC-1103 (4); DEC-1101]
- **S19**: S19 What the session may run: the wall's settings and its hook allow only `operator_run.py <step> <ACT> <manifest sha>`, the frozen `apply.sh check|apply|undo`, the manifest's checks, and `git add`/`git commit` of the listed files; they refuse `sudo`, `git push`, `git tag`, history rewrites, deletions outside the project and its scratch, secrets, the held-out material, the sets root, `tests/acceptance/**`, `~/.claude/` beyond reading the CTO session's transcript, and the operator's own install, brief, rule table and APPROVED. Verify: the wall hook driven with one planted call per allowed form (allowed) and per refused class (refused), fail closed on malformed input [DEC-1104 (2); DEC-1103 (4)]
- **S20**: S20 The log: `log/operator.jsonl` gets one line per gate per ACT (time, ACT, manifest sha, the three votes, the gate's result, the commit, each check's result, the undo state); only the agent writes it. Verify: a full planted run and a refused run: one line per gate reached, every field present [DEC-1104 (2); DEC-1103 (4)]
- **S21**: S21 The pushes and the digest: through the dead-man's switch's channels, every (a) ACT applied is pushed for the first 14 days after the first live (a) run, then the digest only; any refusal after G7, any undo and any red check are pushed at once as a P1, always; the digest lists every ACT applied (class, the three votes, the touched files, the commit, the undo command) and compares the log with the notices sent. Verify: an injected clock (day 1, day 14, day 15) and stub channels: the pushes sent as stated; a P1 on day 30; a notice missing from the channels shown in the digest [DEC-1104 (2); DEC-1103 (4)]
- **S22**: S22 Undo: an applied ACT's undo stays ready for 7 days or until the next ACT on the same files; it runs automatically when a check fails; otherwise on the owner's line `undo ACT-<id> <sha8>`, read from the transcript as the yes is (S10); it restores byte for byte; an apply that fails partway is undone from the backups with a P1; an undo that fails holds the lock, applies nothing else and pushes a P1; a session that dies mid-apply leaves a journal, and the next launch runs the undo first and pushes a P1. Verify: a red check (undone); an `undo` line in a planted transcript on day 3 (undone) and day 8 (refused); a failing undo (lock held, the next queued ACT not run); a planted unfinished journal (undone at the next launch) [DEC-1104 (2); DEC-1103 (4)]
- **S23**: S23 The trial on past ACTs, measured: the classifier runs on every ACT file under `governance/project/orchestration/packages/` (the 54 counted at OPERATOR-AGENT-1's commit `116c2b413b28` and every later one), each read from its own files and commits into a manifest; pass mark: no ACT classed lower than the table puts it, every rise listed with its reason, the counts per class recorded; 8 applied ACTs (SELECT-FIXES-1, SELECT-HOOK-1, GUARD-SETS-1, PERMISSIONS-2, NIGHTLY-STOP-1, OLLAMA-CAP-1, W1-01-EXEMPT-1, D8) are replayed end to end in clones at the commit before each was applied, with planted review records and yes lines, each giving its expected class and outcome ((O) refused); 7 planted faults (an edit after review, a wrong class claim, an unlisted file touched, a red check, a failing undo, a missing yes, a yes for an older sha) each refused; no live file changes (the live control files, `~/gov-os-operator/` and `~/.claude/` hashed before and after). Verify: the record `docs/changes/W2-148-evidence.md` with the per-ACT table, the counts, the rises, each replay's and each fault's outcome and the before/after hashes; re-run by the review [DEC-1104 (2); DEC-1103 (4)]
- **S24**: S24 Planted roots, and the owner's operator untouched: every location (the operator root, the repository, HOME, the CTO's scratch, the clock) comes from an argument or a setting with today's defaults, so every test runs on planted folders; the agent's files live only in `install/`, `queue/`, `acts/`, its wall folder and its own named files under `log/`; the owner's operator files already in `~/gov-os-operator/` (`CLAUDE.md`, `.claude/`, `hooks/`, the dated `log/*.log`) are never read as configuration and never changed. Verify: a planted operator root holding those files: a full run leaves their hashes unchanged and the session's cwd is the wall folder [DEC-1104 (2); DEC-1103 (4)]
- **F1**: An ACT applied with any of G1 to G8 not passed, or a gate that errors, crashes or cannot read its input treated as a pass (every gate fails closed).
- **F2**: An ACT applied whose bytes changed after its review, in the bundle or the request.
- **F3**: An ACT applied at a class lower than any of the three votes; an unknown path, an unparsable list file or a script hit classed (a); a disagreement between votes not logged and pushed.
- **F4**: A (b) ACT applied without a matching yes, or a yes accepted from a tool result, a task notification, a meta or sidechain line, a record the CTO wrote, another ACT or sha, or a time before the review.
- **F5**: A file changed by the dry run or the apply, in the tree or the planted HOME, that is not on the touched list, not refused.
- **F6**: A control file changed by an (a) ACT left in place, or left without a P1.
- **F7**: A commit outside a ticket touching a (b) or (O) control path without the right trailers not flagged.
- **F8**: A session started with the wall's settings not loaded, from the operator root, with the owner's or the CTO's settings, hooks or CLAUDE.md, or with any GOV_* or CLAUDE_PROJECT_DIR in its environment.
- **F9**: The agent pushing, tagging, running sudo, writing tests/acceptance/**, reading ~/.claude beyond the named transcript, or changing its own install, brief, rule table or APPROVED; an APPROVED mismatch that does not refuse the run.
- **F10**: A refusal after G7, an undo or a red check not pushed; an applied ACT missing from the log or the digest.
- **F11**: A failed apply not undone; another ACT applied while an undo has failed; an unfinished journal not undone at the next launch.
- **F12**: Anything the CTO writes, other than a queue line, that makes the agent run; a queue line that bypasses a gate.
- **F13**: A wait or a stop by a name match.
- **F14**: The trial or any test changing a live file, ~/gov-os-operator/ or ~/.claude/.
- **F15**: Any live change made by the operator that is not its own dry-run or apply change: a file someone else changed during the dry run or the apply restored, deleted or overwritten, instead of left as written with a refusal, the lock held and a P1 naming the file (DEC-1106 (1)).

**The verdict block carries one entry for each of these 39 ids, in this order:** S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13, S14, S15, S16, S17, S18, S19, S20, S21, S22, S23, S24, F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, F13, F14, F15. (`F1` and on are the ticket's failure lines, in the order above.)

**Scope (the ticket's `allowed_paths`; "in scope" means a finding about these files or about how the KPI lines hold through them):**

- `governance/project/operator/**`
- `tests/unit/operator/test_w2_148*`
- `docs/changes/W2-148-evidence.md`

Code outside these paths is reachable context (read it to judge a line), but a defect that lives only there is `scope: out`.

## What has changed, and what has been reviewed before (facts; judge the code, not this history)

- **No earlier review is a basis for the probe record** (the CTO's check, 2026-11-11). Five reviews exist as scratch, none committed
  and none of the final code: round 1 (head `45dd9e2dcfb9`, not READY: S6 and S12), round 2 (`85a5cf655830`, not READY: one finding in
  round 2's own fix), a narrow round 3 (`1af33c535d60`, DEC-1106 (1) and (3): S12 to S15, S22, F15), a narrow review of DEC-1107
  (`0fe71aa8bb00`: S22, F15) and a narrow review of the replay check (`24abf75a1b93`, DEC-1108 (2): S15). DEC-1010's two rounds were
  used and the owner gave two exception rounds (DEC-1106, DEC-1107). So **a blocking finding in this review goes to the owner once,
  with options**; say plainly whether anything blocks.
- **The judged files have changed since the last of those reviews.**
  `git -C $TMPDIR/clone diff --stat 24abf75a1b93 HEAD -- governance/project/operator tests/unit/operator tests/acceptance/W2-148 docs/changes/W2-148-evidence.md`
  shows eight files: ACT-OPERATOR-1 (`2a64626532cb`, 2026-11-09: the new `freeze_gate.py`, the reference-transaction check of the commit
  freeze, 174 lines; 8 lines in `operator_run.py`; a new unit test file); a D-10 rename of the unit trial file (`a38809a3364a`); and
  ACT-OPERATOR-ROUNDS-1 (`6fbe73b1adde`, 2026-11-11, by the owner's operator, DEC-1131 (3): `verdict.py` and `operator_run.py`: a KPI
  line marked fail blocks READY, and the two-round cap counts per ACT id across its builds; plus a new unit test file). Read
  those changes with the rest. The reference-transaction hook that calls `freeze_gate.py` is installed in the main repository's
  git hooks by that ACT, and the guard's rule closing the install folder is in `.claude/hooks/pretooluse.py` and the path map: control
  paths outside the ticket's paths, reachable context, `scope: out` if one of them is the only place a defect lives.
- **Readings settled by the CTO (ticket, "Readings settled" and the notes):** the yes's marks (S10) are `type: user` with
  `origin.kind: human`, and if a format drops the mark no line counts (fail closed); the landing check's scope (S16) is the commits outside
  a ticket as the landing selection reads them; the agent's session runs from its own wall folder inside `~/gov-os-operator/`, never
  the root; DEC-1106 (1) and (3) override S15's "undoes the ACT" for files that are not the ACT's own, and the commit freeze is
  `install/act-in-progress.txt`; DEC-1108 (2) makes S15's replay check the CTO's call set against the guard's call log by sha256 both ways.
- **Known rows, carried (name one by its id if you meet it independently; a row, not a new round, unless you show a worse
  consequence than its record says):** F3 (the replay's call source: its own ACT), F5, F7 (kept as the package says), F16, F21 to F28 (the owner-undo and recovery paths when files are left; the pushed line's 190-character cut; a freeze
  left by a crash between the claim and the journal; Claude Code's own writes under `.claude/**` during the dry run; the ignored exit
  of `git reset` in `undo_live`), and F30 to F33 (the replay check: a set line with a non-object `event` and a `dropped` mark; a log
  line without `sha256` raising `KeyError`; session ids matched in lower case only; the replay judging each call without its `agent_type`).


## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.

## What to do

1. Read the ticket, then the code in scope at the clone's head, then the tests that map to each KPI line (the acceptance
   folder's README maps lines to cases; do not take the map as proof: read what the case asserts).
2. Judge **every KPI line** pass or fail from the code and your own probes (planted folders and stand-ins under `TMPDIR`; never
   a live root). Look hardest where a failure would fail open or lose work: every gate failing closed (G1 to G9: S1 to S5, S8, S11 to S13); the classifier on every table row and the class that only rises (S6, S7, S9); the owner's yes read from the transcript and nothing else (S10); the apply, the touched-file check, the control-file after-check and the undo, under DEC-1106's rule (only the ACT's own change is restored; another's live change is left as written, the lock held, a P1 naming the file; S12, S14, S15, S22); the commit freeze and the reference-transaction check in `freeze_gate.py` (S14); the DEC-1131 round count and the failed-line rule (S4); waits and stops by pid, the canary and the wall (S17 to S19); the trial's honesty (S23); the planted roots and the owner's operator untouched (S24)
3. Run the **scoped** tests only, through the heavy-job gate, with this exclusion on every run of a whole folder
   (`-m "not local_only" -k "not real and not green_here and not time_limit"`) and say what it left out:
   `tests/acceptance/W2-148/` and `tests/unit/operator/` (the ticket's `test_w2_148*` files, plus `test_act_operator_1.py` and `test_dec1131_rounds.py`, which landed after the earlier reviews), with `GOV_TESTS_OPTIN=lifted,breadth`. The unit trial file `tests/unit/operator/test_w2_148_unit_trial.py` may be run: it works on planted folders; check that it does before you run it. **Every probe uses planted operator roots, HOME, repositories and transcripts under your `TMPDIR` and stubs for `claude`, `crontab` and the push channels; never `~/gov-os-operator`, `~/.claude` or the live control files** (a failure line of this ticket)
   Command form: `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env PYTHONPATH=$TMPDIR/clone/src HOME=<empty folder> PYTHONUSERBASE=/home/usain/.local TMPDIR=$TMPDIR python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`
   (add `GOV_TESTS_OPTIN=lifted,breadth` for the opt-in cases). Never the full suite (DEC-968). The CTO's own results, which you
   do not re-run: BATCH-PREP: `gov accept W2-148` 166 of 166, then 169 of 169 after the replay check; the trial's counts are in `docs/changes/W2-148-evidence.md`. If the gate or the sandbox will not run a case, say which and why; never run it outside the gate.
4. Classify each finding: id `FR-1`, `FR-2`, ... (a FULL review's own ids, so none collides with an earlier round's), its KPI line,
   `scope: in|out`, the two lines below, `Reversed by:` (what evidence would make it not a finding), and how you showed it
   (the call, the file and lines).
5. Compose the record (below) and return.

## The verdict block and the probe record form

The verdict is one fenced `verdict` block in the record, one entry for **every** KPI line above (`pass` or `fail`, with its
findings, possibly none), in exactly this form (the close computes READY from it by code; you never declare READY):

```verdict
{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "FR-1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```

The record's form is the existing probe record `docs/probes/DAEO-u4oz/PR-DAEO-u4oz.md` (read it in your clone: it is the model,
written 2026-11-11). The CTO writes its "The lead's judgement" section; **you write the rest**, between `PROBE_MD_BEGIN` and
`PROBE_MD_END`, in this order:

1. The YAML front matter, exactly these keys: `type: probe`, `task: DAEO-xafn`, `reviewer_session: not known` (the CTO fills it
   from the launch log), `implementer_session: not recorded` (the CTO fills it), `reviewer_wrote_nothing: true`,
   `commissioned_by: orchestrator`, `judged_by: orchestrator`, `judgement: pass` (only if no finding is in scope, ordinary work
   yes and fails open or loses work, and no line is marked fail; else `fail`), `probed_commit: <12 digits>` (the CTO expands it
   to the full id: the close gate needs the full id, and `.gov-runtime/` takes 12 digits).
2. `# Probe record: W2-148 (DAEO-xafn) <title>, FULL review of the merged code (DEC-1010, DEC-1131)`.
3. `## The reviewer's record (as returned)`: a short plain-language summary (does every line pass; what blocks, if anything; what
   lands as rows), then the twelve fields in a fenced block, as in the model.
4. A line `task: DAEO-xafn`, a line `decisions:` (the decisions you relied on, each as DEC-n), a line `probed_commit: <12 digits>`.
5. `**Scope.**`, `**Method.**` (the probes, with counts), `**Probed and found sound.**` (numbered, by KPI line, with file and
   lines), and `**Findings**`: each with its KPI line, `scope`, `Ordinary work: yes|no, because ...`,
   `Consequence: fails open|loses work|other`, `Reversed by:`.
6. `**Classification:**` on one line (how many yes/fails open or loses work, yes/other, and rows marked no), then the `verdict` block.

## Return

As your final message: **the twelve labelled lines first**, each label at the start of its own line (`task`, `status`,
`work_completed`, `files_changed`, `evidence`, `tests`, `discoveries`, `risks`, `lessons`, `proposed_decisions`, `unresolved`,
`recommended_next_action`), with step 0 and the `ps` check first in `evidence`, the clone's head in `evidence`, the tests and
what the exclusion left out in `tests`, `files_changed: none`; status DONE, PARTIAL or PACKAGES. Then a line `PROBE_MD_BEGIN`,
the record text of the form above, and a line `PROBE_MD_END`. Estimate: 75 to 100 minutes, about $9.
