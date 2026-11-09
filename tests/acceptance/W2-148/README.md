# W2-148 acceptance tests: the operator agent applies ACTs by class from a queue, in a walled session

Ticket DAEO-xafn (W2-148), profile FULL, the owner's DEC-1104 (2) approving OPERATOR-AGENT-1 with Q1 to Q7 as
recommended. Written by the independent test designer (MR-3) from the ticket's KPI lines S1 to S24, its fourteen
failure lines, the package's §1 to §6 and the CTO's readings in the ticket's body, before any implementation, reading
only `w2/integrate` (`5f015c990` on `w2/W2-148-tests`). Nothing of the engineer's work was read (there is none yet).

## How they run

    PYTHONPATH=<worktree>/src TMPDIR=<scratch> python3 -m pytest tests/acceptance/W2-148 -q \
      -p no:cacheprovider -o tmp_path_retention_policy=failed

Every case builds its own planted world under `tmp_path` (`w2_148_support.World`): no real `~/gov-os-operator`,
`~/.claude`, crontab, git hook, push channel, `claude`, network, GPU or model. Each subprocess gets the world's `HOME`
and a `PATH` that starts with the world's stubs (`claude`, `crontab`, `sudo`, `pkill`, `killall`), plus
`PYTHONUSERBASE` (the real user site, for PyYAML) and `PYTHONDONTWRITEBYTECODE=1`. Nothing needs a live session; the
`live` marker is registered and no case carries it. About 150 cases, most of them a full planted run of a few seconds.

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

## KPI lines, tests, and the outcome on `w2/integrate`

Every case is **red on integrate for the right reason**: `governance/project/operator/` does not exist (the world's
build and the classifier fail on `require_operator`), and S23's record does not exist. No case is a green guard on
integrate; the cases marked "guard" are green once the code is built and fail an implementation that refuses too much.

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_148_gates.py::test_s1_g1_a_byte_changed_before_the_copy_refuses` | red | no code; G1 refuses a bundle file whose bytes differ from the manifest |
| S1 | `test_w2_148_gates.py::test_s1_g1_the_run_uses_its_frozen_copy_not_the_source_edited_after_it` | red | no code; the hook edits the source after G1; the frozen bytes run; `acts/*<sha12>*` read-only |
| S2 | `test_w2_148_gates.py::test_s2_g2_refuses_a_decision_not_accepted_in_the_register` | red | no code; PROPOSED, absent and missing DEC ids, each refused at G2 |
| S3 | `test_w2_148_gates.py::test_s3_g3_refuses_a_rehearsal_log_missing_mismatched_or_failing` | red | no code; three bundles, one per case, refused at G3 |
| S4 | `test_w2_148_gates.py::test_s4_g4_refuses_a_review_that_is_not_ready_for_an_act` | red | no code; not READY, malformed, no block, a fail with no blocking finding, a changed brief, reviewer = author, three rounds ("to the owner") |
| S4 | `test_w2_148_gates.py::test_s4_g4_a_block_naming_another_manifest_sha_refuses` | red | no code; refused at G4 or G5 (N-3) |
| S4 | `test_w2_148_gates.py::test_s4_guard_a_ready_review_of_two_rounds_passes` | red | no code; guard: two READY rounds apply |
| S4 | `test_w2_148_gates.py::test_s4_the_install_pins_verdict_py_byte_for_byte` | red | no `governance/project/operator/verdict.py` |
| S5 | `test_w2_148_gates.py::test_s5_g5_any_sha_differing_refuses_changed_after_review` | red | no code; request, verdict and recomputed sha, one pair differing each time |
| S6 | `test_w2_148_classify.py::test_s6_the_classifier_gives_each_table_row_its_class` | red | no `act_class.py`; 35 planted manifests: every row and its other side, each script hit, unknown path, unparsable lists, mixed |
| S7 | `test_w2_148_votes_yes.py::test_s7_code_a_claim_a_review_b_applies_as_b` | red | no code; (a)/(a)/(b) with a yes: `Class: b`, votes logged, a P1 `disagreement` |
| S7 | `test_w2_148_votes_yes.py::test_s7_a_b_vote_is_never_lowered_without_a_yes_it_is_refused` | red | no code; (b)/(a)/(a) and (a)/(b)/(a): refused at G6 with no yes, logged, P1 |
| S7 | `test_w2_148_votes_yes.py::test_s7_a_review_vote_of_o_refuses_as_yours` | red | no code; (a)/(a)/(O): "yours", logged, P1 |
| S8 | `test_w2_148_votes_yes.py::test_s8_a_frozen_patch_classifying_higher_after_g6_is_refused` | red | no code; the hook adds an allow rule to the frozen patch after G6: refused at `recompute`, P1 |
| S9 | `test_w2_148_gates.py::test_s9_g6_an_a_act_proceeds_with_no_yes` | red | no code; (a) applies with an empty transcript, no disagreement |
| S9 | `test_w2_148_gates.py::test_s9_g6_an_o_act_is_refused_as_yours` | red | no code; (O) refused at G6, "yours" |
| S10 | `test_w2_148_votes_yes.py::test_s10_a_human_yes_after_the_review_applies_and_is_copied_verbatim` | red | no code; terminal string and Remote Control text blocks: applied, `Approved-by`, `log/act-approvals.jsonl` |
| S10 | `test_w2_148_votes_yes.py::test_s10_a_yes_that_does_not_count_is_refused` | red | no code; none, other ACT, other sha, before the review, tool result, task notification, meta, sidechain, assistant, no origin mark |
| S10 | `test_w2_148_votes_yes.py::test_s10_a_yes_in_a_record_the_cto_wrote_or_another_session_does_not_count` | red | no code; the yes only in the scratch's records and another session's transcript |
| S11 | `test_w2_148_gates.py::test_s11_g7_a_moved_live_file_refuses_rebuild_rehearse_re_review` | red | no code; a listed live file moved: G7 |
| S12 | `test_w2_148_gates.py::test_s12_g8_the_dry_run_refuses` | red | no code; unlisted file in the tree, in the planted HOME, a non-byte-for-byte undo, a listed file not changed |
| S13 | `test_w2_148_gates.py::test_s13_g9_a_hold_waits_then_proceeds_once_cleared` | red | no code; quiet hours (02:00, cleared at 07:30), the nightly window, a close queue, the CTO's `act-in-progress.txt` |
| S14 | `test_w2_148_apply.py::test_s14_the_commit_holds_only_the_listed_files_and_the_fixed_trailers` | red | no code; files, trailers, the freeze during the apply, no push, tag or sudo |
| S14 | `test_w2_148_apply.py::test_s14_an_extra_staged_file_refuses_and_undoes` | red | no code; `git diff --cached` differs: no commit, undone, P1 |
| S14 | `test_w2_148_apply.py::test_s14_a_check_whose_count_differs_from_the_rehearsal_is_red_and_undone` | red | no code; count 3 against 2: undone, P1 |
| S15 | `test_w2_148_apply.py::test_s15_an_a_act_that_also_changes_a_control_file_is_undone_with_a_p1` | red | no code; eight families (hooks, settings, `.claude/**`, git hooks, crontab by a stub, the pin, the dead-man's code, the install) |
| S15 | `test_w2_148_apply.py::test_s15_guard_a_path_map_addition_whose_replay_refuses_only_listed_calls_stays` | red | no code; guard: a listed newly refused call and an older one leave it applied |
| S15 | `test_w2_148_apply.py::test_s15_a_path_map_addition_whose_replay_refuses_an_unlisted_call_is_undone` | red | no code; one unlisted call within 48 hours turned to refused: undone, P1 |
| S16 | `test_w2_148_apply.py::test_s16_the_landing_check_flags_control_commits_outside_a_ticket_without_the_trailers` | red | no `landing_check.py`; flags the CTO's and the operator-without-`Act:` commits only |
| S17 | `test_w2_148_launch.py::test_s17_the_launcher_starts_the_walled_session_for_the_oldest_request_clean_and_by_pid` | red | no code; oldest request, canary then session, flags, cwd the wall, clean environment, pgid recorded |
| S17 | `test_w2_148_launch.py::test_s17_a_malformed_request_line_is_refused_and_moved_aside` | red | no code; five malformed lines |
| S17 | `test_w2_148_launch.py::test_s17_an_install_file_changed_by_a_byte_refuses_the_launch` | red | no code; APPROVED mismatch: no session |
| S17 | `test_w2_148_launch.py::test_s17_an_install_file_changed_by_a_byte_refuses_a_run_by_hand` | red | no code; the same gates by hand |
| S17 | `test_w2_148_launch.py::test_s17_no_name_matched_kill_in_the_operator_code` | red | no code to search; then none of `pkill`, `killall`, `pgrep -f` in `.py`/`.sh` code lines |
| S18 | `test_w2_148_launch.py::test_s18_settings_that_did_not_load_fail_the_canary_and_no_real_session_starts` | red | no code; a stub modelling ignored settings: refused after one call |
| S19 | `test_w2_148_launch.py::test_s19_the_wall_hook_allows_each_allowed_form` | red | no code; seven allowed forms |
| S19 | `test_w2_148_launch.py::test_s19_the_wall_hook_refuses_each_refused_class` | red | no code; nineteen refused classes |
| S19 | `test_w2_148_launch.py::test_s19_the_wall_hook_fails_closed_on_malformed_input` | red | no code; not JSON, no tool input |
| S20 | `test_w2_148_notices_undo.py::test_s20_a_full_run_logs_one_line_per_gate_with_every_field` | red | no code; G1 to G9 pass lines, every field, the commit |
| S20 | `test_w2_148_notices_undo.py::test_s20_a_refused_run_logs_each_gate_reached_and_no_further` | red | no code; refused at G3: G1 to G3 only |
| S21 | `test_w2_148_notices_undo.py::test_s21_an_a_act_is_pushed_for_the_first_14_days_then_the_digest_only` | red | no code; day 1 and day 14 pushed, day 15 not |
| S21 | `test_w2_148_notices_undo.py::test_s21_a_refusal_after_g7_on_day_30_is_pushed_as_a_p1` | red | no code; a G8 refusal on day 30 |
| S21 | `test_w2_148_notices_undo.py::test_s21_the_digest_lists_every_applied_act_and_a_notice_missing_from_the_channels` | red | no code; the digest's rows and the missing day-1 notice |
| S22 | `test_w2_148_notices_undo.py::test_s22_a_red_check_undoes_at_once_with_a_p1` | red | no code |
| S22 | `test_w2_148_notices_undo.py::test_s22_the_owner_s_undo_line_on_day_3_undoes_and_none_refuses` | red | no code; no line: refused; a human line on day 3: undone, P1 |
| S22 | `test_w2_148_notices_undo.py::test_s22_the_owner_s_undo_line_on_day_8_is_refused` | red | no code |
| S22 | `test_w2_148_notices_undo.py::test_s22_an_undo_after_the_next_act_on_the_same_files_is_refused` | red | no code |
| S22 | `test_w2_148_notices_undo.py::test_s22_a_failing_undo_holds_the_lock_and_the_next_queued_act_is_not_run` | red | no code; P1; the launcher starts no real session |
| S22 | `test_w2_148_notices_undo.py::test_s22_an_apply_failing_partway_is_undone_from_the_backups_with_a_p1` | red | no code |
| S22 | `test_w2_148_notices_undo.py::test_s22_an_unfinished_journal_is_undone_at_the_next_launch_with_a_p1` | red | no code; the run stopped by its pgid mid-apply; the next launch (empty queue) undoes |
| S23 | `test_w2_148_trial.py::test_s23_the_record_has_a_row_per_act_file_with_its_class` | red | no record; the 54 at `116c2b413` and the two later |
| S23 | `test_w2_148_trial.py::test_s23_the_counts_per_class_match_the_rows` | red | no record |
| S23 | `test_w2_148_trial.py::test_s23_no_pinned_act_is_classed_lower_than_the_table` | red | no record; the pinned subset (N-6) |
| S23 | `test_w2_148_trial.py::test_s23_the_rises_are_listed` | red | no record |
| S23 | `test_w2_148_trial.py::test_s23_eight_replays_give_their_expected_class_and_outcome` | red | no record |
| S23 | `test_w2_148_trial.py::test_s23_seven_planted_faults_are_each_refused` | red | no record |
| S23 | `test_w2_148_trial.py::test_s23_no_live_file_changed_before_and_after_hashes` | red | no record |
| S24 | `test_w2_148_launch.py::test_s24_a_full_run_and_launch_leave_the_owner_s_operator_files_unchanged` | red | no code; owner's `CLAUDE.md`, `.claude/`, `hooks/`, `log/*.log` unchanged; top level only the agent's folders; cwd the wall |

The failure lines, by the cases that would catch each:

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| F1 | `test_w2_148_gates.py::test_s4_g4_refuses_a_review_that_is_not_ready_for_an_act` | red | a malformed block or no block refused (fail closed); every gate's own case in this file |
| F1 | `test_w2_148_gates.py::test_s12_g8_the_dry_run_refuses` | red | a gate that errors is never a pass |
| F2 | `test_w2_148_gates.py::test_s5_g5_any_sha_differing_refuses_changed_after_review` | red | bytes or request changed after review |
| F2 | `test_w2_148_gates.py::test_s1_g1_a_byte_changed_before_the_copy_refuses` | red | as above, in the bundle |
| F3 | `test_w2_148_classify.py::test_s6_the_classifier_gives_each_table_row_its_class` | red | unknown path, unparsable list, script hit never (a) |
| F3 | `test_w2_148_votes_yes.py::test_s7_a_b_vote_is_never_lowered_without_a_yes_it_is_refused` | red | no class lower than a vote; the disagreement logged and pushed |
| F4 | `test_w2_148_votes_yes.py::test_s10_a_yes_that_does_not_count_is_refused` | red | each wrong source, ACT, sha or time |
| F4 | `test_w2_148_votes_yes.py::test_s10_a_yes_in_a_record_the_cto_wrote_or_another_session_does_not_count` | red | a record the CTO wrote |
| F5 | `test_w2_148_gates.py::test_s12_g8_the_dry_run_refuses` | red | an unlisted file in the tree or the planted HOME |
| F6 | `test_w2_148_apply.py::test_s15_an_a_act_that_also_changes_a_control_file_is_undone_with_a_p1` | red | undone, P1 |
| F7 | `test_w2_148_apply.py::test_s16_the_landing_check_flags_control_commits_outside_a_ticket_without_the_trailers` | red | flagged |
| F8 | `test_w2_148_launch.py::test_s17_the_launcher_starts_the_walled_session_for_the_oldest_request_clean_and_by_pid` | red | the wall's settings, cwd, clean environment |
| F8 | `test_w2_148_launch.py::test_s18_settings_that_did_not_load_fail_the_canary_and_no_real_session_starts` | red | settings not loaded |
| F8 | `test_w2_148_launch.py::test_s24_a_full_run_and_launch_leave_the_owner_s_operator_files_unchanged` | red | never the root or the owner's settings |
| F9 | `test_w2_148_launch.py::test_s19_the_wall_hook_refuses_each_refused_class` | red | push, tag, sudo, tests/acceptance, ~/.claude, its own files |
| F9 | `test_w2_148_launch.py::test_s17_an_install_file_changed_by_a_byte_refuses_a_run_by_hand` | red | APPROVED mismatch refuses |
| F10 | `test_w2_148_notices_undo.py::test_s21_a_refusal_after_g7_on_day_30_is_pushed_as_a_p1` | red | pushed |
| F10 | `test_w2_148_notices_undo.py::test_s21_the_digest_lists_every_applied_act_and_a_notice_missing_from_the_channels` | red | in the digest |
| F10 | `test_w2_148_notices_undo.py::test_s20_a_full_run_logs_one_line_per_gate_with_every_field` | red | in the log |
| F11 | `test_w2_148_notices_undo.py::test_s22_an_apply_failing_partway_is_undone_from_the_backups_with_a_p1` | red | undone |
| F11 | `test_w2_148_notices_undo.py::test_s22_a_failing_undo_holds_the_lock_and_the_next_queued_act_is_not_run` | red | nothing else applied |
| F11 | `test_w2_148_notices_undo.py::test_s22_an_unfinished_journal_is_undone_at_the_next_launch_with_a_p1` | red | undone at the next launch |
| F12 | `test_w2_148_votes_yes.py::test_s10_a_yes_in_a_record_the_cto_wrote_or_another_session_does_not_count` | red | a CTO record makes nothing run |
| F12 | `test_w2_148_launch.py::test_s17_a_malformed_request_line_is_refused_and_moved_aside` | red | a queue line that is not the form starts nothing |
| F13 | `test_w2_148_launch.py::test_s17_no_name_matched_kill_in_the_operator_code` | red | no name match |
| F14 | `test_w2_148_trial.py::test_s23_no_live_file_changed_before_and_after_hashes` | red | the trial's hashes |
| F14 | `test_w2_148_launch.py::test_s24_a_full_run_and_launch_leave_the_owner_s_operator_files_unchanged` | red | planted roots only |

## Notes and limits

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

## Files

- `w2_148_support.py`: the planted world, the bundles and their `apply.sh`, the review records, the transcript
  shapes, the stubs, the snapshot, the evidence record's table reader.
- `conftest.py`: the `world` fixture; the `live` marker.
- `test_w2_148_gates.py` (S1-S5, S9, S11-S13), `test_w2_148_classify.py` (S6), `test_w2_148_votes_yes.py` (S7, S8,
  S10), `test_w2_148_apply.py` (S14-S16), `test_w2_148_launch.py` (S17-S19, S24), `test_w2_148_notices_undo.py`
  (S20-S22), `test_w2_148_trial.py` (S23).
