# W2-205 acceptance tests: the run-time tool, slice 3 (across sessions)

Ticket DAEO-rt3s (W2-205), profile FULL. Written by the independent test designer (MR-3) from the ticket's five success
lines, two failure lines and its `## Interface` section, before any implementation, on the base `167a2f1dc`. The code
read is the integrated public surface (`gov msg`, `gov dispatch`, `gov launch`, `gov checkpoint`, the kernel hook files,
slice 1's and slice 2's acceptance support), never this ticket's branch. Memory used: the ticket, the lead's brief
(`docs/emergency-2/briefs/LEAD-rt-slice3.md`) and audit 3's decisions (`docs/emergency-2/audits/03-run-time-tool.md`).

## How they run

    TMPDIR=$(mktemp -d) PYTHONPATH=<worktree>/src bash <heavy_slot.sh> \
      python3 -m pytest tests/acceptance/W2-205 -q -p no:cacheprovider -n auto

36 cases (30 functions). No model, no network, no real `claude`, never the real `~/.gov-os`: every `gov` child
(`python3 -m gov.cli.main`) and every hook runs with a `HOME` under `tmp_path`. All are acceptance tests; none is
`local_only`. No sleep is longer than 2 s and no wait longer than 15 s (the wait for a relaunch to reach the stand-in:
on the base it runs to its end, so the six relaunch cases take about 16 to 22 s each there, a few seconds once built).

## What is planted

- **`w2_205_support.Home`**: slice 1's fixture machine (`w2_121c_support.Box`, imported unchanged: a `HOME`, a stub
  folder first on `PATH`, the `nvidia-smi` stand-in, planted CPUs and meminfo) with a planted load (3.0), slice 2's
  shortened admission periods, the configuration file `gate.json`, and a `gov` stand-in on `PATH` that runs this
  worktree's `gov` (so a hook may call the command or import it). It writes messages (`plant_message`) and `end`
  events (`plant_end`) straight to the inbox file and the runtime log, in the forms slice 1 and the Interface give,
  and the relaunch key (`config`) to `~/.gov-os/runtime/config.json`.
- **The clock**: `GOV_RUNTIME_NOW` (ISO-8601, `+00:00`). The planted reports use a fixed time; where a pass sends a
  message itself (S1's first case), its clock is planted at the real time (a minute ago, then now), so the gap is about
  60 s whichever clock stamps the message.
- **A dead session**: a registry entry written as the launcher writes it (`pid`, `repository`, `ticket`, `role`,
  `started`, `notify`, `address` `<role>:<ticket>`, `boot`, `start_ticks`, and `session_id`) for a `sleep` process that
  ran and is gone.
- **`w2_205_support.Rig`** (the relaunch cases): slice 1's `LaunchKit` (W2-184's fixture project, W2-60a's recording
  stand-in CLI at `~/.local/bin/claude`, the open resource gate) and a `Home` on the same HOME whose passes carry the
  gate's readings, so the `gov launch` a pass starts is the real one and ends at the stand-in, which records its
  arguments. The session to resume is started by a real launch first (so its launch record exists; `gov launch` resumes
  only a session it started, by a UUID); further tickets get that record planted under a new session id. The
  checkpoint is an automatic record written by `gov.checkpoint.record.write`.
- **The hooks** are the kernel's files (`template/governance/kernel/hooks/stop.py`, `precompact.py`,
  `sessionstart.py`) run as child processes with the hook JSON on stdin, a small fixture git project (one ticket,
  one commit) as `CLAUDE_PROJECT_DIR`, `GOV_TICKET`, `GOV_ROLE` and, for `stop.py`, `GOV_MSG_ADDRESS`.

## KPI line to tests

KPI ids name the ticket's lines by position (success 1 to 5, failure 1 and 2), the RT id beside each as a note. Every
item is a test function (a parametrised one covers all its rows). "Red on the base": what fails on `167a2f1dc`.

| KPI id | tests | expected red reason |
|---|---|---|
| S1 (RT-2) | `test_w2_205_s1_ends.py::test_s1_a_lead_a_worker_and_a_job_each_give_one_end_event_and_a_gap_within_120_s` | no `end` event in the runtime log (0, not one) |
| S1 (RT-2) | `test_w2_205_s1_ends.py::test_s1_a_session_gov_launch_started_leaves_an_end_event_with_its_message_id` | no `end` event from the launcher |
| S1 (RT-2) | `test_w2_205_s1_ends.py::test_s1_a_planted_end_whose_message_is_200_s_late_exits_3_naming_it` | no `--ends` (exit 2, not 3) |
| S1 (RT-2) | `test_w2_205_s1_ends.py::test_s1_an_end_with_no_message_yet_is_a_gap_to_now_and_says_unsent` | no `--ends` (exit 2, not 0) |
| S2 (RT-2) | `test_w2_205_s2_stop_check.py::test_s2_an_unread_wake_blocks_once_with_its_text_and_the_same_input_again_passes` | no `gov msg stop-check` (exit 2) |
| S2 (RT-2) | `test_w2_205_s2_stop_check.py::test_s2_a_second_newer_wake_blocks_once_more` | no `gov msg stop-check` (exit 2) |
| S2 (RT-2) | `test_w2_205_s2_stop_check.py::test_s2_an_unread_notice_only_passes` | no `gov msg stop-check` (exit 2, not 0) |
| S2 (RT-2) | `test_w2_205_s2_stop_check.py::test_s2_nothing_unread_and_nothing_waited_on_passes_even_beside_a_launchable_ticket` | no `gov msg stop-check` (exit 2, not 0) |
| S2 (RT-2) | `test_w2_205_s2_stop_check.py::test_s2_no_gov_msg_address_passes` | no `gov msg stop-check` (exit 2, not 0) |
| S2 (RT-2) | `test_w2_205_s2_stop_check.py::test_s2_a_wake_already_read_does_not_block` | no `gov msg stop-check` (exit 2, not 0) |
| S2 (RT-2) | `test_w2_205_s2_stop_check.py::test_s2_the_stop_hook_prints_the_block_once_after_its_checkpoint_and_exits_0` | `stop.py` prints no block decision for an unread wake message |
| S3 (RT-5) | `test_w2_205_s3_relaunch.py::test_s3_the_launcher_records_the_session_id_in_the_registry_entry` | the registry entry has no `session_id` |
| S3 (RT-5) | `test_w2_205_s3_relaunch.py::test_s3_a_death_is_relaunched_once_with_resume_and_the_next_step_and_a_second_pass_adds_none` | the pass starts no launch (0, not one) |
| S3 (RT-5) | `test_w2_205_s3_relaunch.py::test_s3_a_second_death_of_the_ticket_in_the_boot_is_one_died_twice_message_and_no_launch` | the first death is not relaunched |
| S3 (RT-5) | `test_w2_205_s3_relaunch.py::test_s3_an_entry_with_no_session_id_is_one_cannot_resume_message_and_no_launch` | no wake message naming that it cannot resume |
| S3 (RT-5) | `test_w2_205_s3_relaunch.py::test_s3_only_a_death_without_a_return_is_relaunched` | no launch for the death without a return (the two returns' halves are already met on the base, so the case holds all three) |
| S3 (RT-5) | `test_w2_205_s3_relaunch.py::test_s3_the_key_absent_false_or_unreadable_gives_the_slice_1_message_only_and_true_relaunches` | with the key true the death is not relaunched (the off rows are already met on the base, so the case holds the on row too) |
| S4 (RT-5) | `test_w2_205_s4_hooks.py::test_s4_precompact_then_sessionstart_inject_the_recorded_next_step_first` | the injection begins `Checkpoint resume: ticket=...`, not `Resume at the recorded next step (...)` |
| S4 (RT-5) | `test_w2_205_s4_hooks.py::test_s4_with_no_checkpoint_nothing_of_the_kind_is_injected_and_with_one_it_begins_with_its_next_step` | with a checkpoint the injection does not begin with the resume part (the no-checkpoint half is already met) |
| S5 (RT-6) | `test_w2_205_s4_hooks.py::test_s5_the_precompact_and_sessionstart_outputs_name_gov_msg_read` | the PreCompact output does not name `gov msg read` |
| S5 (RT-6) | `test_w2_205_s5_messages.py::test_s5_messages_among_the_five_address_kinds_are_each_read_once_in_the_order_sent` | `gov msg send` refuses the kind `relay` (exit 2); the five addresses already send and read on the base |
| S5 (RT-6) | `test_w2_205_s5_messages.py::test_s5_five_notices_give_one_digest_line_and_no_wake` | no `gov msg digest` (exit 2) |
| S5 (RT-6) | `test_w2_205_s5_messages.py::test_s5_the_digest_is_one_line_a_day_for_notices_read_or_unread` | no `gov msg digest` (exit 2) |
| S5 (RT-6) | `test_w2_205_s5_messages.py::test_s5_a_relay_never_wakes` | `gov msg send` refuses the kind `relay` (exit 2) |
| S5 (RT-6) | `test_w2_205_s5_messages.py::test_s5_the_audit_exits_0_when_no_message_names_the_owner` | no `gov msg audit` (exit 2, not 0) |
| S5 (RT-6) | `test_w2_205_s5_messages.py::test_s5_the_audit_exits_3_naming_each_relay` | no `gov msg audit` (exit 2, not 3) |
| S5 (RT-6) | `test_w2_205_s5_messages.py::test_s5_the_audit_counts_the_last_n_days_only` | no `gov msg audit` (exit 2, not 0) |
| F1 | `test_w2_205_s3_relaunch.py::test_f1_a_pass_killed_after_the_launch_and_before_its_log_line_does_not_relaunch_again` | the pass does not relaunch the death at all |
| F1 | `test_w2_205_s3_relaunch.py::test_f1_a_session_that_dies_every_time_is_relaunched_once_and_its_checkpoint_is_not_rewritten` | the first death is not relaunched |
| F2 | `test_w2_205_f2_stall.py::test_f2_guard_a_silent_transcript_still_messages_once_and_pushes_once` | none: a regression guard, green on the base and to stay green |

Count per line: S1 4, S2 7, S3 6, S4 2 (6 cases), S5 8 (10 cases), F1 2, F2 1.

Red run on the base (through the heavy slot, `-n auto`): `35 failed, 1 passed in 59.21s`; every failure for the reason
above (the command, the kind, the event, the entry's key or the hook's part does not exist), no harness error. The one
pass is F2's guard.

**F2's other half is the lead's**: that `tests/acceptance/W2-121c` stays green and that the branch's diff touches
none of the cron line, the scratch dispatcher, `heavy_slot.sh` and the repository's own `.claude/settings.json` is
checked by the lead at the green step, not by a test here.

## The test designer's readings where the Interface is open

- **`gov dispatch waits --ends`** is read in its text form: each end's line matches `<id> <kind> <to> gap <n> s` (any
  spacing, `<n>` whole or decimal), an unsent end's line holds the word `unsent` after it, a finding is a line that
  begins `finding:` and holds the end's id. A gap of exactly 120 s is no finding. Of `--json` only this is asserted:
  one envelope, the same exit code, the ids somewhere in it.
- **`ended_at` of an end the pass detects** is the previous pass's planted time, exactly, and the event carries
  `estimated: true`; a job's and a launcher's `ended_at` are within 30 s of the real clock.
- **A lead** is a registry entry whose role is `orchestrator` (its `end` event's kind `lead`), notified to `cto`.
- **`gov msg stop-check`'s reason** holds the newly blocking message's text; whether it also repeats an earlier,
  already seen message is not asserted. The check does not move the read mark (the three unread notices are still
  unread after it: the mark is `gov msg read`'s). `stop_hook_active` true is not tested.
- **`stop.py`** is run with `GOV_TICKET` set (without it today's hook returns at once; whether the check then runs is
  left open). The checkpoint is asserted as a record under the ticket's checkpoint folders.
- **A launchable ticket** beside the session (an `in_progress` ticket in the project the check runs in) is no reason
  to block.
- **The relaunch's arguments** are read at the stand-in CLI: `--resume <session id>` and, after that pair, an argument
  holding the checkpoint's `next_action` (the launcher appends its own `--append-system-prompt-file <path>` after the
  passed arguments, so "last argument" is the last one `gov launch` was given, not the CLI's last). The stand-in's
  working directory is the entry's repository.
- **"A second pass adds none"**: the dead entry is put back in the registry before the next pass (the launch's own
  gate clears stale entries), and the pass must add no launch, no `relaunched` event and **no `died twice` message**:
  the death's own claim does not make it a second death.
- **A second death** is a new registry entry (another dead pid, the same ticket and boot, a session id). The
  `died twice` message's id is `died-twice:<ticket>:<boot>`, its text or data holds `died twice` and the ticket; three
  more deaths still leave one message.
- **`cannot resume`**: exactly one wake message in the launcher's inbox whose text or data holds `cannot resume`
  (and the ticket); its id is not pinned, and slice 1's end message may stand beside it or be it.
- **A return**: a wake message with the entry's end id sent `--from` the entry's `address` saying exit code 0, or the
  entry's `exit_file` (a key of the entry naming a file) holding `0`. An exit file holding another code is not tested.
- **The key**: no `config.json`, `{"relaunch": false}`, a file that is not JSON and `{}` are all off: no launch, no
  claim file, no `relaunched` event, and exactly one end message with the entry's id (slice 1's). Whether a relaunch
  that is on also keeps slice 1's end message is not asserted.
- **F1's killed pass** is planted as what such a kill leaves: the launch done (the stand-in ran, the claim file
  `~/.gov-os/runtime/relaunch/relaunch:<ticket>:<boot>:<pid>:<start_ticks>` there), `state.json` and `log.jsonl` put
  back to what they were before the pass (the launched session's own launcher lines kept), the dead entry still in the
  registry. "The checkpoint is not rewritten": the ticket's checkpoint files are byte for byte the same, none added.
- **The two hooks in order**: the PreCompact hook writes its own automatic record (today with the next step
  `Resume after compaction`), which is then the latest; the injected first part is compared with what
  `gov checkpoint --resume --ticket <ticket>` gives after it (its `next_action` and `path`), so the case holds whatever
  the PreCompact record's next step is. The planted next step itself is asserted in the second S4 case (SessionStart
  alone). The `(checkpoint <path>)` may be the relative path or an absolute one ending in it.
- **"Ahead of every other part"** is asserted for the roles engineer, independent-test-designer and orchestrator (the
  orchestrator's own parts come after it). Source `startup`, or no `GOV_TICKET`: no such part.
- **The inbox line** `Read your inbox: gov msg read` is a whole line of the SessionStart injection; of the PreCompact
  output only `gov msg read` is asserted.
- **`gov msg digest`** prints exactly the lines `<day> <n> notices`, one a day in day order, the day being the
  message's `at` date; nothing else on stdout. `--day <d>` prints that day's line alone. A day with no notice is not
  tested.
- **`gov msg audit`**: the relay's line holds its id, its `from` and its `to`; a message among the roles is not
  listed. The owner's messages are planted straight in the inbox files (the audit reads the files). `--days <n>` is
  read as: only messages whose `at` is within the last n days count (30 days old: `--days 7` exits 0, `--days 60`
  exits 3).

## For the lead (found while writing)

- The Interface gives `precompact.py`'s output the inbox line and S5 names the PreCompact injection, but
  `template/governance/kernel/hooks/precompact.py` is not in the ticket's `allowed_paths` (only `stop.py` and
  `sessionstart.py`): `test_s5_the_precompact_and_sessionstart_outputs_name_gov_msg_read` cannot go green without it.
- After a real compaction the latest record is the PreCompact hook's own, whose next step is the fixed text
  `Resume after compaction`: the resumed session is told that, not the step recorded before. The ticket says "as it
  does now", so no test asks for more.
