---
type: probe
task: DAEO-xafn
reviewer_session: not known
implementer_session: not recorded
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: 2ef060a65c77
---

# Probe record: W2-148 (DAEO-xafn) The operator agent: ACTs applied by class from a queue, in a walled session, FULL review of the merged code (DEC-1010, DEC-1131)

## The lead's judgement

- **Who probed.** A fresh read-only reviewer of W2-148's lead (log `~/gov-os-worktrees/W2-148/.gov-runtime/scratch/lead/log/W2-148-A3-probe.json`), FULL review of the merged code at `w2/integrate` `2ef060a65c77`, the second and last review round (DEC-1010, DEC-1131). Recorded by the CTO (session b2f0511f, 2026-11-11), who did not re-run it.
- **READY, by code.** The verdict block marks 38 lines pass and S15 fail; `verdict.ready` is False because of S15 (DEC-1131 (3): a failed line blocks READY). No finding is in scope, ordinary work yes and fails open or loses work.
- **S15 / FR-1.** The (a) after-check's guard replay and its control snapshot cover the repository's `.claude/settings*.json` and `.rulesync/permissions.jsonc`, not the home `~/.claude/settings*.json`, which the `settings` row of `class-rules.yaml` also names. Consequence: more refusals only, never an unreviewed loosening (ordinary work yes, consequence other). DEC-1010's two rounds are used, so it goes to the owner once, with the reviewer's three options (`governance/project/orchestration/packages/W2-148-S15.md`). The reviewer named its proposal "DEC-1137"; that id is W2-11's re-baseline, so the owner's answer takes the next free id.
- **Rows.** FR-2 (ordinary yes, other, unverified: to check in a live one-turn wall session) and FR-3 to FR-5 (ordinary no) are rows, not a round (DEC-801, DEC-808).
- **Judgement: fail on S15 alone, pending the owner's choice; no close until then.**

## The reviewer's record (as returned)

This FULL review of the merged operator agent passes 38 of the 39 KPI lines and fails one: S15.

- **What fails.** The code's own rule table lets an (a) ACT add deny rules to the home-level `~/.claude/settings.json`, through the `settings` row, which names both roots. But the (a) after-check's guard replay, and its control-file snapshot, cover only the repository's `.claude/settings*.json` and `.rulesync/permissions.jsonc`. A planted (a) ACT adding `Read(**)` to the home deny list was applied with no replay.
- **How serious.** The finding itself is ordinary work yes, consequence other: it means more refusals, never an unreviewed loosening. The line still fails because S15 states that a deny-list addition gets a replay, and DEC-1131 (3) makes a failed line block READY. If the CTO reads S15's "the settings" as the repository's files only, S15 passes and FR-1 is a row.
- **Every other line holds.** The gates fail closed (G1 to G9). The class only rises. The yes is read only from human transcript lines. The restore rule follows DEC-1106 (1). The commit freeze and its reference-transaction gate work, and so do the DEC-1131 round count and failed-line rule, the wall, the canary, and waits and stops by pid.
- **Tests and trial.** All 420 scoped tests pass. My re-run of the trial meets its pass mark.
- **Rows.** Four findings land as rows: FR-2 (ordinary yes, other, unverified) and FR-3 to FR-5 (ordinary no). Nothing goes to a new round except S15, which goes to the owner once, with options.

```
task: W2-148 (DAEO-xafn), FULL read-only review of the merged operator agent at w2/integrate 2ef060a65c77, judged on S1–S24 and F1–F15 (DEC-1131)
status: DONE; 38 lines pass, S15 fails (FR-1: in scope, ordinary work yes, other); no finding is in scope, ordinary work yes and fails open or loses work
work_completed: read the ticket whole, the judged code whole (operator_run.py, opcommon.py, act_class.py, class-rules.yaml, operator_launch.py, freeze_gate.py, landing_check.py, verdict.py, brief.md, wall/), OPERATOR-AGENT-1 §1–§6 and the evidence record; ran the scoped tests (420); re-ran the trial's classify, replays and faults on planted folders; 3 planted probe runs through operator_run.py; a code search
files_changed: none
evidence: Step 0: the write outside the tree failed (read-only file system); git hash-object gave 1ae28402a109 and update-index --refresh exited 0; ps showed no ollama or llama-server of mine. Head 2ef060a65c77 (two CTO record commits past 7b5c3cb94fd9; no judged file moved). TMPDIR peaked at 129M and 8,755 inodes, then removed (36K at end). Main tree and worktree clean at end. Read refusals 0.
tests: tests/acceptance/W2-148 and tests/unit/operator through the heavy gate with GOV_TESTS_OPTIN=lifted,breadth and the exclusion: 419 passed, 1 deselected (the S18 canary case, "real" in its name, a stub claude), which run alone passed: 420 of 420
discoveries: FR-1 (S15 fail); FR-2 to FR-5 rows; the record's per-ACT table counts 57 files, and the head has 81, all at or above the table
risks: FR-1: an (a) tightening of the user-level deny list applies with no replay; FR-2 needs the live canary or rehearsal to settle
lessons: a rule row naming both the repository and HOME needs every after-check that relies on its class to cover both roots
proposed_decisions: DEC-1137 (proposed): S15/FR-1: (1) cover the home settings in the replay and snapshot; (2) home settings a fixed (b); (3) re-baseline S15 to the repository's settings; recommended (2)
unresolved: the owner's choice on DEC-1137; FR-2's real behaviour
recommended_next_action: compute READY (False: S15); send DEC-1137's options to the owner once; file FR-2 to FR-5 as rows
```

---

task: DAEO-xafn
decisions: DEC-801, DEC-808, DEC-1010, DEC-1131, DEC-1104, DEC-1103, DEC-1106, DEC-1107, DEC-1108, DEC-1101, DEC-1058, DEC-1057, DEC-1073, DEC-1064, DEC-1065
probed_commit: 2ef060a65c77

**Scope.** `governance/project/operator/**`, `tests/unit/operator/test_w2_148*` (plus `test_act_operator_1.py` and `test_dec1131_rounds.py`), `docs/changes/W2-148-evidence.md`, and how the 39 KPI lines hold through them. Read as context, out of scope: `tests/acceptance/W2-148/**`, OPERATOR-AGENT-1 and `governance/project/indep-walls/`.

**Method.** Everything ran on a clone of `w2/integrate` at `2ef060a65c77`, with HOME an empty folder under TMPDIR. Every run used planted operator roots, repositories, HOME, transcripts and clocks, and stubs for `claude`, `crontab` and the push channels. No real model, no network, and no read of `~/gov-os-operator` or `~/.claude`.
- **Tests:** 420 scoped tests through `heavy_slot.sh`. The exclusion deselected 1 (S18's canary case), which I ran alone.
- **Trial re-run** (S23), through the unit trial module's own functions, without its live-hash `main()`:
  - classification of all 81 ACT files at head;
  - the 8 replays (9 runs: GUARD-SETS-1 whole and its control part);
  - the 7 planted faults.
- **Own probes:** 3 planted runs through `operator_run.py` with the unit kit:
  - a (b) ACT, then an (a) ACT, each whose `apply.sh` also edits an unlisted git-ignored `.claude/settings.local.json` only when it exists;
  - an (a) ACT adding `Read(**)` to the deny list of the home `.claude/settings.json`.
- **Code reading:** every gate and helper named below, and a search of the scoped code for name-matched kills (none).

**Probed and found sound.**
1. **S1 (G1).** `operator_run.py:261-313`:
   - the bundle is checked for links and special files, copied to a temporary folder, and every file hashed against the manifest;
   - an unlisted or missing file refuses, and so does a manifest that names another ACT (`check_act`, `:88-96`);
   - the copy is renamed into place and made read-only (`opcommon.py:664-674`).
   A second request for the same sha reuses the copy only if it still hashes as its manifest says (`:324-377`).
2. **S2 (G2).** `:380-411`: every heading of each named DEC must show Status ACCEPTED. A missing id, an id not in the register, an unreadable register or any other status refuses.
3. **S3 (G3).** `:429-449`: the log must be hashed in `files`, be present, match its hash and end with `failures: 0`. A missing log, a hash mismatch or a log ending with failures each refuses.
4. **S4 (G4).** `:452-535` with the pinned `verdict.py`:
   - a malformed block fails closed, and a KPI line marked fail blocks on its own (DEC-1131 (3));
   - for an ACT, a KPI line not marked pass refuses;
   - the block must name this manifest sha and a class;
   - the reviewer must be named and must not be the author (casefolded);
   - the reviewer's brief must hash as its APPROVED line;
   - three verdict blocks across the ACT id's builds refuse "to the owner"; a block carried forward counts once (`act_rounds`).
5. **S5 (G5).** `:538-543`: the request's, the verdict's and the recomputed sha must all be equal, else "changed after review".
6. **S6.** `act_class.py:470-530` and `class-rules.yaml`:
   - each file takes the first matching row, and an unknown path is (O);
   - a list file is parsed before and after (it cannot be (a) if absent, unparsable, or not held as hashed);
   - script hits raise the class;
   - the ACT takes the highest class, and an unreadable bundle is (O).
   The trial re-run found no ACT file classed lower than the table.
7. **S7.** `:546-560`: the highest of the three votes applies, and an unknown or missing vote counts as (O) (`opcommon.py:702-704`). A disagreement is logged at G6, pushed as a P1 and listed in the digest.
8. **S8.** `recompute`, `:578-600`, runs after G6 and again immediately before the apply (`:920`). A different class, or a changed frozen copy, refuses after G7 with a P1.
9. **S9.** (O) refuses with "yours" (`:561-562`); (a) goes on with no yes; (b) needs the yes.
10. **S10.** `opcommon.py:456-532`:
    - only a `type: user` line with `origin.kind: human` counts, never `isMeta`, a sidechain, a compact summary, a `toolUseResult` or a `tool_result` block;
    - the content must be a string or text blocks, and the yes must be a line of its own;
    - its time must be after the review;
    - it is read from the transcript of the session named in `log/cto-session.txt`;
    - the raw line is copied into `log/act-approvals.jsonl` (`operator_run.py:571-573`).
11. **S11 (G7).** `:603-613`: every touched file's live hash, then the frozen `apply.sh check`. Either refuses with "rebuild, rehearse, re-review".
12. **S12 (G8).** `:677-774`, in a clone at the live head with a planted HOME and crontab stub:
    - the changed set covers the tree including ignored files, the git hooks, `.git/config`, the HOME and the crontab;
    - an extra file, a missing file, a wrong after-state, a red check, an undo that is not byte for byte, or the undo changing an unlisted file each refuses;
    - the live files are re-hashed after the dry run (`:623-637`).
13. **S13 (G9).** `opcommon.py:164-194` and `operator_run.py:786-801`, `:915-927`: it holds for the quiet hours, the nightly's window and flag, the close flag, the CTO's freeze and the install freeze. It waits, and refuses only past `hold_max_s` (0 means never). After a hold it re-runs the recompute and G7.
14. **S14.** `:804-907`:
    - the freeze is claimed with O_EXCL and released only by its token (`opcommon.py:197-233`);
    - a journal is written; then `apply.sh apply`, the after-hashes, the unlisted-file check and the checks against exit and count;
    - the staged list must equal the touched list; the commit carries the stated trailers and never `Role: owner`.
    - `freeze_gate.py:92-142`: on the live branch only, a change to the ACT's paths or to the control paths is refused unless every added commit carries this ACT's `Act` and `Act-sha`; an unreadable freeze or manifest freezes every path; a rewind or creation is refused. The 14 unit cases cover it.
15. **S15, except FR-1.** `:1165-1193`:
    - the control snapshot before against after (repository `.claude/**`, `.rulesync/**`, `.git/hooks`, `.git/config`, the hooksPath folder, the dead-man's and sentinel's files, the path map, the pin, the crontab, the install);
    - the replay of repository deny lists and the path map, after checking the call set both ways against the guard's call log (`:1214-1303`), with the known rows F30 to F33;
    - any other difference undoes the ACT's own files under DEC-1106 (1).
16. **S16.** `landing_check.py:58-89`: commits outside a ticket on `control: true` paths are flagged unless they carry `Role: owner`, or `Role: operator` with `Act:`.
17. **S17.** `operator_launch.py:218-299`:
    - the APPROVED check (`opcommon.py:260-307`) runs first, then the lock, the journal recovery, and the oldest request;
    - a malformed request is moved aside;
    - holds are checked, the wall is built under the root (never the root itself), the canary runs;
    - the session starts with a clean environment in its own group, with pid and pgid recorded, waited on by pid and stopped by pgid;
    - every result carries the APPROVED sha;
    - there are no name-matched kills.
18. **S18.** `:150-177`, `:204-215`, `:275-283`: with no denied Read outside the wall, the launch refuses before the real session, with a P1.
19. **S19.** `wall/operator_wall_hook.py:60-215`: exactly the stated forms; fails closed (exit 2) on a malformed event or wall. The settings template has the stated allow and deny lists.
20. **S20.** `opcommon.py:367-377` and `Run.line`: one line per gate reached, with every field.
21. **S21.** `opcommon.py:387-452`, `:677-699` and `operator_run.py:1788-1837`:
    - (a) pushes stop after day 14; (b) is always pushed;
    - every P1 kind is pushed;
    - the digest lists every applied ACT, and the log against the notices shows `missing_notices`.
22. **S22 and F11.** `:1471-1784`:
    - the undo for 7 days, unless a later ACT changed the same files;
    - the owner's undo line, read as the yes is;
    - an undo on a red check or a failed apply;
    - a failed undo holds the lock, and nothing else runs;
    - the launcher recovers the journal first.
23. **S23.** The re-run's outcomes match the record: 0 lower, 22 rises, SELECT-FIXES-1, SELECT-HOOK-1, GUARD-SETS-1 (control part), PERMISSIONS-2 and NIGHTLY-STOP-1 applied as (b), OLLAMA-CAP-1 as (a), W1-01-EXEMPT-1, D8 and GUARD-SETS-1 (whole) refused at G6 as (O), and the 7 faults each refused, undone or with the lock held.
24. **S24.** Every location is a setting with today's default (`opcommon.py:47-119`). The session's cwd is `<root>/wall` (`operator_launch.py:105-147`).
25. **F15.** `live_changed` (`:639-675`), `undo_live` (`:1518-1577`) and `foreign_differences` (`:1580-1593`): only a touched file at its after-copy is written back; anything else is left, the lock held, and a P1 names it.

**Findings**

- **FR-1 (S15).** The `settings` row of `class-rules.yaml` makes deny additions to the home `.claude/settings*.json` class (a). The (a) after-check's replay only takes repository touched files: `lists = [t for t in run.repo_touched() …]` (`operator_run.py:1183`). The control snapshot holds only the pin from HOME (`CONTROL_HOME_FILES`, `:50`). A planted (a) ACT adding `Read(**)` to the home deny list was applied, votes a/a/a, with no replay on its log line. S15 states "for path-map or deny-list additions, a replay … changes no allowed call to refused".
  - scope: in
  - Ordinary work: yes, because a deny rule added to the user settings is the textbook (a) ACT, and past ACTs edited `~/.claude/settings.json` (PUSH-INPUT-1, GUARD-FIX-4).
  - Consequence: other (a tightening applied without its replay: calls agents rely on may be refused; nothing is loosened and nothing is lost)
  - Reversed by: the CTO's reading that S15's "the settings" means the repository's `.claude/settings*.json` only, as the evidence record's §3 list reads it. S15 then passes and FR-1 is a row.
- **FR-2 (S24, F8).** The walled session starts from `<operator root>/wall`, a child of `~/gov-os-operator/`, which holds the owner's hand operator's `CLAUDE.md`. Claude Code documents that it loads CLAUDE.md files from parent folders. Whether `--restricted` stops this could not be checked here (no real `claude`).
  - scope: in
  - Ordinary work: yes, because it would happen on every launch if the parent note loads.
  - Consequence: other (instructions only: every action still passes the wall hook and the gates in code)
  - Reversed by: a live one-turn wall session (ACT-OPERATOR-1's canary or rehearsal) showing the parent CLAUDE.md is not loaded.
- **FR-3 (F5, S12/S14).** The dry-run clone holds no git-ignored live file that is not listed. The live apply's unlisted-file check skips ignored files (`tree_state(…, ignored=False)`, `:825`). So an `apply.sh` that edits an unlisted ignored file only when it exists does nothing in the dry run and edits it live. My planted (b) ACT was applied with `.claude/settings.local.json` changed and no refusal. The (a) version was caught by the after-check: undone, lock held, P1.
  - scope: in
  - Ordinary work: no, because it needs three misses at once: the author leaves the file off the list, the script tolerates the file's absence (the past ACTs that edit `settings.local.json` read it, and would fail in the clone), and the reviewer and the owner both miss the line in `apply.sh`.
  - Consequence: fails open
  - Reversed by: ACT scripts in the ordinary path that edit ignored files tolerantly, or the dry run copying the live ignored control files into its clone.
- **FR-4 (F11).** `operator_run.py run` checks the lock but not the journal (`:1891`). Run by hand while a dead run's journal exists, it overwrites that journal (`:814`), so the dead apply is never undone.
  - scope: in
  - Ordinary work: no, because the launcher always recovers first, and the wall lets the session run only the request's ACT.
  - Consequence: fails open
  - Reversed by: a path in ordinary work that runs `operator_run.py run` without the launcher.
- **FR-5 (S6).** The script scan reads `apply.sh`, `commands` and the checks only (`act_class.py:498-512`). A helper file in the bundle (an `apply.py`, as PERMISSIONS-2 had) is not scanned. An `rm` target that starts with a variable (`"$PWD/../x"`) is left to the dry run, which cannot see it.
  - scope: in
  - Ordinary work: no, because an (a) ACT with a network, sudo or push step hidden in a helper, or deleting through `$PWD/..`, is not an ordinary shape, and the reviewer's class vote reads the bundle.
  - Consequence: fails open
  - Reversed by: an ordinary (a) ACT whose effects live in an unscanned helper.

**Classification:** 0 yes/fails open or loses work; 2 yes/other (FR-1, FR-2); 3 rows marked no (FR-3, FR-4, FR-5); 1 KPI line marked fail (S15), which blocks READY under DEC-1131 (3).

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "S6", "verdict": "pass", "findings": [{"id": "FR-5", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "S7", "verdict": "pass", "findings": []}, {"kpi": "S8", "verdict": "pass", "findings": []}, {"kpi": "S9", "verdict": "pass", "findings": []}, {"kpi": "S10", "verdict": "pass", "findings": []}, {"kpi": "S11", "verdict": "pass", "findings": []}, {"kpi": "S12", "verdict": "pass", "findings": []}, {"kpi": "S13", "verdict": "pass", "findings": []}, {"kpi": "S14", "verdict": "pass", "findings": []}, {"kpi": "S15", "verdict": "fail", "findings": [{"id": "FR-1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S16", "verdict": "pass", "findings": []}, {"kpi": "S17", "verdict": "pass", "findings": []}, {"kpi": "S18", "verdict": "pass", "findings": []}, {"kpi": "S19", "verdict": "pass", "findings": []}, {"kpi": "S20", "verdict": "pass", "findings": []}, {"kpi": "S21", "verdict": "pass", "findings": []}, {"kpi": "S22", "verdict": "pass", "findings": []}, {"kpi": "S23", "verdict": "pass", "findings": []}, {"kpi": "S24", "verdict": "pass", "findings": [{"id": "FR-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": []}, {"kpi": "F4", "verdict": "pass", "findings": []}, {"kpi": "F5", "verdict": "pass", "findings": [{"id": "FR-3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "F6", "verdict": "pass", "findings": []}, {"kpi": "F7", "verdict": "pass", "findings": []}, {"kpi": "F8", "verdict": "pass", "findings": []}, {"kpi": "F9", "verdict": "pass", "findings": []}, {"kpi": "F10", "verdict": "pass", "findings": []}, {"kpi": "F11", "verdict": "pass", "findings": [{"id": "FR-4", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "F12", "verdict": "pass", "findings": []}, {"kpi": "F13", "verdict": "pass", "findings": []}, {"kpi": "F14", "verdict": "pass", "findings": []}, {"kpi": "F15", "verdict": "pass", "findings": []}]}
```
