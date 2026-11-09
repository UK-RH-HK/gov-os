---
id: DAEO-xafn
status: in_progress
deps: []
links: []
created: 2026-11-09T13:47:49Z
type: task
priority: 1
assignee: engineer
external-ref: W2-148
tags: [wave-2, implementation, operator, acts, full]
wbs_id: W2-148
title: 'The operator agent: ACTs applied by class from a queue, in a walled session (DEC-1104 (2))'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- governance/project/operator/**
- tests/unit/operator/test_w2_148*
- docs/changes/W2-148-evidence.md
kpis:
  success:
  - 'S1 G1 Frozen: the run copies the ACT bundle into `acts/<id>-<sha12>/` under the operator root, read-only, and refuses unless every file hashes as the manifest says; from then on it runs only its own copy, so an edit to the CTO''s scratch after the copy changes nothing. Verify: a planted bundle with one byte changed before the copy (refused, nothing applied); a planted bundle edited in the source folder after the copy (the run uses the frozen bytes; the frozen folder is not writable) [DEC-1104 (2); DEC-1103 (4)]'
  - 'S2 G2 Under a decision: the manifest names a DEC id that the register holds with Status ACCEPTED; a missing id, an id not in the register, or an entry not ACCEPTED refuses. Verify: a planted register with an ACCEPTED, a PROPOSED and an absent id [DEC-1104 (2); DEC-1103 (4)]'
  - 'S3 G3 Rehearsed (DEC-1057): the rehearsal log is in the bundle, hashed in the manifest, and ends with 0 failures; a missing log, a hash mismatch or a log ending with failures refuses. Verify: three planted bundles, one per case [DEC-1104 (2); DEC-1103 (4); DEC-1057]'
  - 'S4 G4 READY: the review record''s last verdict block names this manifest sha and a class, and the install''s own pinned copy of verdict.py computes READY; for an ACT any KPI marked fail also refuses (the moderator''s triage does not apply); the reviewer''s brief hashes as its line in APPROVED and the reviewer is not the ACT''s author; a third review round refuses with "to the owner". Verify: planted review records: READY; not READY; a malformed block (fail closed); a block naming another sha; a fail with no blocking finding; a changed reviewer brief; reviewer equal to author; three rounds [DEC-1104 (2); DEC-1103 (4); DEC-1010]'
  - 'S5 G5 Hashes match: the manifest sha in the queue request, in the verdict block and as recomputed from the frozen copy are the same; any one differing refuses with "changed after review". Verify: three planted mismatches, one per pair [DEC-1104 (2); DEC-1103 (4)]'
  - 'S6 The classifier on every table row: `act_class.py` with `class-rules.yaml` reads a manifest (every touched file with its before and after sha256, every command) and gives each row of OPERATOR-AGENT-1 §2''s table its class: list-shaped files are parsed before and after and are (a) only when the only differences are items added to a named refusal or coupling list or lines removed from an opt-in list; any other change to them is (b) or (O) as the row says; a script hit for sudo, push, tag, an install, a network call or rm outside the project raises the class; an unknown path is (O); the ACT''s class is the highest among its files; a file that cannot be parsed is never (a). Verify: one planted manifest per table row (both sides of every "only added"/"only removed" row), each script hit, an unknown path, a malformed list file, a mixed (a)+(b) manifest giving (b) [DEC-1104 (2); DEC-1103 (4)]'
  - 'S7 Three votes, and the class only rises: the class applied is the highest of the code''s vote, the class the ACT file claims and the reviewer''s `class` field; a disagreement is written to the log, shown in the digest and pushed as a P1; no vote can lower the code''s class. Verify: planted votes in every order of disagreement ((a)/(a)/(b), (b)/(a)/(a), (a)/(b)/(a), any with (O)): the highest applies each time, the disagreement logged [DEC-1104 (2); DEC-1103 (4)]'
  - 'S8 Recompute and refuse: immediately before the apply, the class is recomputed by `act_class.py` from the frozen copy of the patch, not from any claim; a result different from the class recorded at G6 refuses, logs and pushes a P1. Verify: a planted bundle whose frozen patch classifies higher than the class recorded at G6 (via a test hook between G6 and the apply): refused, nothing applied [DEC-1104 (2); DEC-1103 (4)]'
  - 'S9 G6 for (a): an ACT runs as (a) only when the class applied (S7) is (a); (O) always refuses with "yours"; (b) goes to the owner''s yes (S10). Verify: planted (a), (b) and (O) bundles: (a) proceeds with no yes; (O) refused at G6 with nothing applied [DEC-1104 (2); DEC-1103 (4)]'
  - 'S10 G6 for (b), the owner''s yes from the transcript: a (b) ACT runs only after a line `yes ACT-<id> <sha8>` (sha8 the manifest sha''s first 8 hex) typed by the owner after the review''s time, read from the CTO session''s own transcript (the session named in `log/cto-session.txt`): a `type: user` line marked human (`origin.kind: human`), its content a string or text blocks, not a tool result, not a task notification, not `isMeta`, not a sidechain; never from a record the CTO wrote. The yes is copied verbatim into `log/act-approvals.jsonl`. A yes for another ACT or sha, one older than the review, or the same text in a non-human line does not count. Verify: planted transcripts in the shapes Claude Code writes today (human turns from the terminal and from Remote Control, tool results, task notifications, meta lines, sidechain lines): only the human line after the review counts; each other case refused [DEC-1104 (2); DEC-1103 (4); DEC-1058]'
  - 'S11 G7 Live state as stated: the frozen `apply.sh check` passes against the live before-hashes; a moved live file refuses with "rebuild, rehearse, re-review". Verify: a planted live tree with one listed file changed [DEC-1104 (2); DEC-1103 (4)]'
  - 'S12 G8 Dry run, undo and the touched-file check: in the agent''s own clone at the live head with a planted HOME, it runs `check`, `apply`, the manifest''s checks, then `undo`; the run refuses unless the undo restores every file byte for byte and the set of files changed by the apply, in the clone''s tree and in the planted HOME together, equals the manifest''s touched list; an extra file, a missing file or an undo that is not byte for byte refuses. Verify: planted bundles whose apply touches one unlisted file in the tree, one unlisted file in the planted HOME, and whose undo leaves one byte different: each refused, the live tree untouched [DEC-1104 (2); DEC-1103 (4)]'
  - 'S13 G9 Holds: a run inside the quiet hours (02:00 to 07:30), during the nightly''s window, while a close queue runs or while `log/act-in-progress.txt` exists waits, and proceeds when the hold clears; it never refuses for a hold. Verify: an injected clock and planted hold files: each holds, then proceeds once cleared [DEC-1104 (2); DEC-1103 (4)]'
  - 'S14 The apply and its commit: the run writes `log/act-in-progress.txt` (the commit freeze), runs `apply.sh apply` and the manifest''s checks against the rehearsal''s stated exit codes and counts, refuses unless `git diff --cached --name-status` equals the list, commits only the listed files with the trailers `Role: operator`, `Act: ACT-<id>`, `Act-sha: <manifest sha>`, `Class: a|b`, `Review: <review record sha>` and, for (b), `Approved-by: owner (chat, <time>)`; never `Role: owner`, never a push, a tag, sudo or a history rewrite; the freeze file is removed at the end. Verify: a planted repository: the commit''s files and trailers; a staged extra file refused; a check whose count differs from the rehearsal''s red (S19) [DEC-1104 (2); DEC-1103 (4)]'
  - 'S15 The post-apply control-file check for (a): after an (a) ACT is applied, the hook folder, the settings, `.claude/**`, the git hooks, `crontab -l`, the pin, the sentinel''s and the dead-man''s code and the operator''s install must hash as before; the path map and the settings deny lists may differ only by the computed additions; for path-map or deny-list additions, a replay of the guard on the last 48 hours of calls changes no allowed call to refused apart from the cases the review listed; any other difference undoes the ACT at once and pushes a P1. Verify: a planted (a) ACT that also changes a control file (each control family once, crontab through a stub): undone byte for byte, P1 pushed; a planted path-map addition whose replay turns one unlisted allowed call to refused: undone, P1 [DEC-1104 (2); DEC-1103 (4)]'
  - 'S16 The landing check: a function in the install, given a range of first-parent commits, flags every commit outside a ticket (as the landing selection reads it: `Role: owner`, or no `Task: DAEO-<id>` other than the CTO''s) that touches a (b) or (O) control path of the rule table without `Role: owner`, or without `Role: operator` together with an `Act:` trailer, as one inbox P1 item each; a commit with the right trailers, or touching only (a) or ticket paths, is not flagged. Verify: a planted range: a CTO commit on the guard hook (flagged), the same with `Role: operator` but no `Act:` (flagged), an operator commit with both (not flagged), an owner commit (not flagged), a ticket commit (not flagged) [DEC-1104 (2); DEC-1103 (4)]'
  - 'S17 The queue and the cron launch: the CTO writes one request line (the ACT''s id and its manifest''s sha256) into `queue/`; that is the only input; `operator_launch.py`, run by the dispatcher''s cron line every 10 minutes outside the quiet hours, picks up the oldest request, runs the canary (S18), then starts the walled session (`claude -p --restricted` with the wall''s settings, from a wall folder built from `governance/project/indep-walls/`''s template inside the operator root, never the root itself, with a clean environment: no `GOV_*`, no `CLAUDE_PROJECT_DIR`), records its pid and pgid, and waits and stops only by them; a malformed request line is refused and moved aside; a launch by hand passes through the same gates. Every result prints the sha256 of `install/APPROVED`, and any install file not matching its APPROVED line refuses every run. Verify: a stub `claude` on PATH recording argv, cwd and environment; planted good and malformed queue lines; one install file changed by a byte (refused); a code search for name-matched kills (`pkill`, `killall`, `pgrep -f`): none [DEC-1104 (2); DEC-1103 (4); DEC-1073]'
  - 'S18 The canary: before each real session a one-turn session in the wall must come back with a Read outside the wall in its `permission_denials`; otherwise the launch refuses before the real session. Verify: a wall whose settings are made invalid on purpose (a stub `claude` modelling the ignored settings): refused, no real session started [DEC-1104 (2); DEC-1103 (4); DEC-1101]'
  - 'S19 What the session may run: the wall''s settings and its hook allow only `operator_run.py <step> <ACT> <manifest sha>`, the frozen `apply.sh check|apply|undo`, the manifest''s checks, and `git add`/`git commit` of the listed files; they refuse `sudo`, `git push`, `git tag`, history rewrites, deletions outside the project and its scratch, secrets, the held-out material, the sets root, `tests/acceptance/**`, `~/.claude/` beyond reading the CTO session''s transcript, and the operator''s own install, brief, rule table and APPROVED. Verify: the wall hook driven with one planted call per allowed form (allowed) and per refused class (refused), fail closed on malformed input [DEC-1104 (2); DEC-1103 (4)]'
  - 'S20 The log: `log/operator.jsonl` gets one line per gate per ACT (time, ACT, manifest sha, the three votes, the gate''s result, the commit, each check''s result, the undo state); only the agent writes it. Verify: a full planted run and a refused run: one line per gate reached, every field present [DEC-1104 (2); DEC-1103 (4)]'
  - 'S21 The pushes and the digest: through the dead-man''s switch''s channels, every (a) ACT applied is pushed for the first 14 days after the first live (a) run, then the digest only; any refusal after G7, any undo and any red check are pushed at once as a P1, always; the digest lists every ACT applied (class, the three votes, the touched files, the commit, the undo command) and compares the log with the notices sent. Verify: an injected clock (day 1, day 14, day 15) and stub channels: the pushes sent as stated; a P1 on day 30; a notice missing from the channels shown in the digest [DEC-1104 (2); DEC-1103 (4)]'
  - 'S22 Undo: an applied ACT''s undo stays ready for 7 days or until the next ACT on the same files; it runs automatically when a check fails; otherwise on the owner''s line `undo ACT-<id> <sha8>`, read from the transcript as the yes is (S10); it restores byte for byte; an apply that fails partway is undone from the backups with a P1; an undo that fails holds the lock, applies nothing else and pushes a P1; a session that dies mid-apply leaves a journal, and the next launch runs the undo first and pushes a P1. Verify: a red check (undone); an `undo` line in a planted transcript on day 3 (undone) and day 8 (refused); a failing undo (lock held, the next queued ACT not run); a planted unfinished journal (undone at the next launch) [DEC-1104 (2); DEC-1103 (4)]'
  - 'S23 The trial on past ACTs, measured: the classifier runs on every ACT file under `governance/project/orchestration/packages/` (the 54 counted at OPERATOR-AGENT-1''s commit `116c2b413` and every later one), each read from its own files and commits into a manifest; pass mark: no ACT classed lower than the table puts it, every rise listed with its reason, the counts per class recorded; 8 applied ACTs (SELECT-FIXES-1, SELECT-HOOK-1, GUARD-SETS-1, PERMISSIONS-2, NIGHTLY-STOP-1, OLLAMA-CAP-1, W1-01-EXEMPT-1, D8) are replayed end to end in clones at the commit before each was applied, with planted review records and yes lines, each giving its expected class and outcome ((O) refused); 7 planted faults (an edit after review, a wrong class claim, an unlisted file touched, a red check, a failing undo, a missing yes, a yes for an older sha) each refused; no live file changes (the live control files, `~/gov-os-operator/` and `~/.claude/` hashed before and after). Verify: the record `docs/changes/W2-148-evidence.md` with the per-ACT table, the counts, the rises, each replay''s and each fault''s outcome and the before/after hashes; re-run by the review [DEC-1104 (2); DEC-1103 (4)]'
  - 'S24 Planted roots, and the owner''s operator untouched: every location (the operator root, the repository, HOME, the CTO''s scratch, the clock) comes from an argument or a setting with today''s defaults, so every test runs on planted folders; the agent''s files live only in `install/`, `queue/`, `acts/`, its wall folder and its own named files under `log/`; the owner''s operator files already in `~/gov-os-operator/` (`CLAUDE.md`, `.claude/`, `hooks/`, the dated `log/*.log`) are never read as configuration and never changed. Verify: a planted operator root holding those files: a full run leaves their hashes unchanged and the session''s cwd is the wall folder [DEC-1104 (2); DEC-1103 (4)]'
  failure:
  - 'An ACT applied with any of G1 to G8 not passed, or a gate that errors, crashes or cannot read its input treated as a pass (every gate fails closed).'
  - 'An ACT applied whose bytes changed after its review, in the bundle or the request.'
  - 'An ACT applied at a class lower than any of the three votes; an unknown path, an unparsable list file or a script hit classed (a); a disagreement between votes not logged and pushed.'
  - 'A (b) ACT applied without a matching yes, or a yes accepted from a tool result, a task notification, a meta or sidechain line, a record the CTO wrote, another ACT or sha, or a time before the review.'
  - 'A file changed by the dry run or the apply, in the tree or the planted HOME, that is not on the touched list, not refused.'
  - 'A control file changed by an (a) ACT left in place, or left without a P1.'
  - 'A commit outside a ticket touching a (b) or (O) control path without the right trailers not flagged.'
  - 'A session started with the wall''s settings not loaded, from the operator root, with the owner''s or the CTO''s settings, hooks or CLAUDE.md, or with any GOV_* or CLAUDE_PROJECT_DIR in its environment.'
  - 'The agent pushing, tagging, running sudo, writing tests/acceptance/**, reading ~/.claude beyond the named transcript, or changing its own install, brief, rule table or APPROVED; an APPROVED mismatch that does not refuse the run.'
  - 'A refusal after G7, an undo or a red check not pushed; an applied ACT missing from the log or the digest.'
  - 'A failed apply not undone; another ACT applied while an undo has failed; an unfinished journal not undone at the next launch.'
  - 'Anything the CTO writes, other than a queue line, that makes the agent run; a queue line that bypasses a gate.'
  - 'A wait or a stop by a name match.'
  - 'The trial or any test changing a live file, ~/gov-os-operator/ or ~/.claude/.'
profile: FULL
sources:
- DEC-1104
- DEC-1103
- DEC-1101
- DEC-1058
- DEC-1057
- DEC-1010
- DEC-928
- DEC-1073
est_loc: 900
acceptance_tests:
  path: tests/acceptance/W2-148/
  author: 'independent-test-designer (MR-3), from these KPI lines and OPERATOR-AGENT-1, before the engineer: planted ACT bundles, registers, review records, transcripts, an operator root, a HOME and repositories in a temporary folder; stub claude, crontab and push channels; never the real ~/gov-os-operator, ~/.claude, ~/gov-os-eval or this repository''s live files'
track: B
list_rows: []
needs:
- governance/project/indep-walls/**
waits_on: []
---
# W2-148 The operator agent: ACTs applied by class from a queue, in a walled session

The owner's DEC-1104 (2): OPERATOR-AGENT-1 (`governance/project/orchestration/packages/OPERATOR-AGENT-1.md`) approved
with all seven answers as recommended; built after ACT-INDEP-WALLS-1 (applied, `147706ae`), tests first, one review, a
trial on past ACTs replayed. Read the package in full: its §1 to §6 are this ticket's specification, its §7 its plan.

- **What is built here:** the code, in `governance/project/operator/`: `operator_run.py` (the gates G1 to G9, the
  apply, the after-checks, the undo, the log, the notices), `act_class.py` with `class-rules.yaml` (the classifier and
  the package's §2 table), `operator_launch.py` (the queue, the canary, the walled session), the landing check's
  function, a pinned copy of `verdict.py`, the fixed brief (`brief.md`) and the fixed reviewer's brief, and the wall's
  settings and hook for this kind, built on `governance/project/indep-walls/`'s template (reused, not changed here).
  The engineer's unit tests in `tests/unit/operator/test_w2_148*`; the trial's record in
  `docs/changes/W2-148-evidence.md`.
- **What is not built here (ACT-OPERATOR-1, the CTO's, after the merge; (b) and (O), applied by the owner's operator by
  hand one last time):** the install copied into `~/gov-os-operator/install/` with `APPROVED`; the settings deny rule
  closing that folder to the CTO's writes except `queue/`; the dispatcher's cron line; the landing selection's trigger
  wired to S16's function; the two briefs approved by the owner. Nothing live changes under this ticket.
- **Class implementation, not ops (the CTO):** this ticket is code with tests, reviewed and merged as the CTO's other
  committed tools were (W2-97's merge queue); it changes no live configuration. The live install, cron line and deny
  rule are configuration and come by ACT-OPERATOR-1.
- **Profile FULL:** the agent applies changes to governance files and controls; a gate that fails open applies an
  unreviewed or misclassified change to the guard's surroundings. Hence tests first, every gate tested refusing on its
  own, one independent review (READY by `verdict.py`), and the trial before the first live run.
- **Readings settled by the CTO (2026-11-09) [DEC-1104 (2)]:**
  - **The yes's marks (S10):** in today's transcripts (Claude Code 2.1.319) a typed owner turn, from the terminal or
    from Remote Control (Android, claude.ai), is a `type: user` line with `origin: {kind: human}`; subagent results
    arrive as `origin.kind: task-notification`, tool output as `tool_result` blocks, and system lines carry `isMeta`.
    Only the first counts. If a future format drops the mark, no line counts (fail closed) and the package's Q2
    alternative is the fallback, the owner's to choose.
  - **The landing check's scope (S16):** "commits outside a ticket" as the landing selection already reads them
    (ACT-SELECT-HOOK-1 §1 step 3), so a ticket's merged work under its own review is not flagged; the check catches
    the CTO applying a control change itself.
  - **The folder (S24):** `~/gov-os-operator/` already holds the owner's hand operator (`CLAUDE.md`, `.claude/`,
    `hooks/`, dated logs). The agent's session runs from its own wall folder inside it, never from the root, so the
    owner's operator's settings and note never load into it.
  - **The 54:** the package counted 54 ACT files at `116c2b413`; ACT-GATE-CONFIG-1 and ACT-D4-RESTORE-1 have been
    added since. S23 classifies every ACT file present at the trial, and reports the 54 and the later ones apart.
- **Tests first:** an independent test designer writes `tests/acceptance/W2-148/` from these lines and the package,
  before the engineer starts, on planted folders only.
- **Est.:** about 900 lines with the engineer's tests; about 3 working days elapsed with its review and the trial
  (OPERATOR-AGENT-1 §7).

[DEC-1104 (2); DEC-1103 (4)]
