# W2-148 evidence: the operator agent (DAEO-xafn, DEC-1104 (2), OPERATOR-AGENT-1)

- **By:** the engineer, 2026-11-09, on `w2/W2-148`, in the launch sandbox. Nothing live was written; no real `claude`
  session was started (a stub on PATH in every test and in the trial).
- **What was built:** `governance/project/operator/`: `operator_run.py` (G1 to G9, the recompute, the apply, the
  checks, the commit, the after-checks, the undo, the journal, the log, the notices, the digest), `act_class.py` with
  `class-rules.yaml` (OPERATOR-AGENT-1 §2, row by row), `operator_launch.py` (the journal, the queue, the wall, the
  canary, the session; waits and stops by pid and pgid only), `landing_check.py`, `verdict.py` (byte for byte the CTO's
  reference, sha256 `277c8ca9f06c90906397579f4d5bd144fb506a40b0836eb2a8f9c1443d909378`), `opcommon.py` (the shared
  parts), `brief.md`, `reviewer-brief.md`, and the wall for this kind (`wall/settings.json.tmpl`,
  `wall/operator_wall_hook.py`), built on `governance/project/indep-walls/`'s template and hook (read and reused; not
  changed). Standalone: the standard library and PyYAML, no `gov` import.
- **Re-run the trial:** `python3 tests/unit/operator/test_w2_148_trial.py --part all --out <result.json>` (about two
  minutes; temporary folders only). The tables below are that run's result.

## One row per KPI line

| KPI | Where it is met | Evidence |
|---|---|---|
| S1 G1 frozen | `Run.g1`: the bundle copied to `acts/<id>-<sha12>/`, every file hashed against the manifest, a link or an unlisted file refused, the copy made read-only; every later step runs the copy | gov accept S1; unit `test_g1_*` |
| S2 G2 under a decision | `Run.g2`: every DEC id the manifest names has an ACCEPTED Status in the register (`decision_register` of the path map, else `docs/DECISION_REGISTER.md`) | gov accept S2; unit `test_g2_*` |
| S3 G3 rehearsed | `Run.g3`: the log hashed in `files` as `rehearsal.sha256`, its last non-empty line `failures: 0` | gov accept S3; unit `test_g3_*` |
| S4 G4 READY | `Run.g4`: the install's own `verdict.py` READY, every KPI `pass`, the block names this manifest sha and a class, the reviewer is not the author, the reviewer's brief as its APPROVED line, three blocks "to the owner" | gov accept S4; unit `test_g4_*` |
| S5 G5 hashes match | `Run.g4`/`Run.g5`: request, verdict and recomputed sha the same, else "changed after review" | gov accept S5; unit `test_g5_*`; fault "an edit after review" |
| S6 the classifier | `act_class.py` + `class-rules.yaml`: list-shaped files parsed before and after; script hits; unknown path (O); highest file; unparsable never (a) | gov accept S6; unit `test_list_shaped_rows`, `test_fixed_rows`, `test_script_hits_raise_the_class`; S23 (1) below |
| S7 three votes | `Run.g6`: the highest of code, claim and review; a disagreement logged (`disagreement: true`, `notice: disagreement`), pushed P1, in the digest | gov accept S7; unit `test_votes_rise_and_never_fall`; fault "a wrong class claim" |
| S8 recompute | `Run.recompute` right after G6 and again just before the apply: the frozen copy reclassified and rehashed; a different class refuses and pushes P1 | gov accept S8; unit `test_recompute_*` |
| S9 G6 for (a) and (O) | (a) proceeds with no yes; (O) "yours" | gov accept S9; replays W1-01-EXEMPT-1, D8 |
| S10 the owner's yes | `opcommon.find_owner_line`: a `type: user` line with `origin.kind: human`, not meta, not sidechain, no tool result, string or text blocks, after the review's time, in the transcript named by `log/cto-session.txt`; copied verbatim to the approvals file | gov accept S10; unit `test_g6_b_needs_the_owners_typed_yes`; faults "a missing yes", "a yes for an older sha" |
| S11 G7 live state | `Run.g7`: the live before-hashes, then the frozen `apply.sh check`; else "rebuild, rehearse, re-review" | gov accept S11; unit `test_g7_*` |
| S12 G8 dry run | `Run._g8`: a clone at the live head outside the live tree (system temp), a planted HOME and a crontab stub; check, apply, the changed set (tree, HOME, crontab) equal to the touched list, the checks, undo byte for byte | gov accept S12; unit `test_g8_*`; fault "an unlisted file touched" |
| S13 G9 holds | `Run.g9`: quiet hours, the nightly window, the close flag, the CTO's and the operator's `act-in-progress.txt`; it waits (a `G9 held` line) and proceeds | gov accept S13; unit `test_g9_*` |
| S14 apply and commit | `Run.apply`: the freeze, the journal, `apply.sh apply`, the after-hashes, the checks, the live unlisted-file check, the staged list, the commit with its trailers; the freeze removed | gov accept S14; unit `test_an_a_act_is_applied_*`, `test_a_staged_extra_file_is_refused` |
| S15 control files for (a) | `after_checks`: the controls' bytes before and after; the guard replayed on the last 48 hours of calls on a clone (old and new lists); any other difference undoes the ACT's own touched files at once and pushes P1; the control file itself is left exactly as it is, the lock held, the P1 naming it (DEC-1106 (1), round 3) | gov accept S15; unit `test_an_a_act_changing_a_control_file_live_is_undone_and_the_control_left`, `test_a_path_map_addition_*`, round 3's `test_a_*_during_the_checks_*` |
| S16 the landing check | `landing_check.py`: outside a ticket as the landing selection reads it; the rule table's control rows | gov accept S16; unit `test_the_landing_check_*` |
| S17 queue and launch | `operator_launch.py`: the oldest `.req`, a malformed one moved aside under its own name, the wall built under the root, a clean environment, pid and pgid recorded, waited and stopped by them; APPROVED checked on every run and launch | gov accept S17; unit `test_the_launcher_*`, `test_a_malformed_request_is_moved_aside`, `test_an_approved_mismatch_*`, `test_no_wait_or_stop_by_a_name_match` |
| S18 the canary | `operator_launch.canary`: a Read outside the wall must come back in `permission_denials`, else refused before the session | gov accept S18; unit `test_the_canary_refuses_*` |
| S19 what the session may run | `wall/operator_wall_hook.py` and `wall/settings.json.tmpl` | gov accept S19; unit `test_the_wall_hook_allows_only_the_operators_forms` |
| S20 the log | `opcommon.log_event`: one line per gate reached, every key | gov accept S20; unit (gate list asserted) |
| S21 pushes and digest | `opcommon.notify` (push command and pings log); the first 14 days of (a) pushes from the log's first applied (a); `digest` with `missing_notices` | gov accept S21; unit `test_pushes_for_a_stop_after_14_days`, `test_the_digest_*` |
| S22 undo | the owner's `undo` step (7 days, the transcript line, not after a later ACT on the same files); the automatic undo; a failing undo holds `log/operator.lock`; the journal undone at the next launch | gov accept S22; unit `test_the_owners_undo_*`, `test_a_failing_undo_*`, `test_a_journal_*`; faults "a red check", "a failing undo" |
| S23 the trial | this record | the tables below |
| S24 planted roots | `opcommon.load_settings`: every location a setting with today's default; the owner's operator files never read or changed | gov accept S24; unit `test_the_owners_operator_files_are_untouched` |

## The defaults chosen (the CTO settles the final values in ACT-OPERATOR-1)

| Setting | Default |
|---|---|
| `operator_root` | the install's parent (`~/gov-os-operator/` once installed) |
| `repo` | `/home/usain/Dynamic-Agentic-Engineering-OS` |
| `home` | the process's HOME |
| `scratch` | `<repo>/.gov-runtime/scratch/orchestrator` |
| `transcripts` | `<home>/.claude/projects/-home-usain-Dynamic-Agentic-Engineering-OS` |
| `clock` | none: the system clock |
| `pings_log` | `<home>/.config/gov-os-notify/pings.log` (the dead-man's log channel) |
| `push_cmd` | unset: a notice goes through the dead-man's three channels from the install's own code (the `pings_log` line, the Windows toast through `install/win_toast.ps1`, a headless `claude -p` asked to call PushNotification), one line of at most 190 characters (F4, F19); when set, `<push_cmd> <notice JSON>` replaces the toast and the push (the tests' stub) |
| `calls` | `<operator root>/log/calls.jsonl`: the call log the operator writes itself during its dry run (G8), one `{id, time, role: operator, ticket: <ACT>, event: {tool_name: Bash, tool_input: {command}, cwd: "."}}` line per command it runs there; the replay reads it |
| `close_flag` | `<scratch>/CLOSE-RUNNING` (close_queue.sh's lock) |
| `nightly_window` | `03:50-08:00` (the wake at 03:50, the nightly 04:00 to about 07:00, its check at 08:00) |
| `poll_s` | 60 |
| `freeze` | `<operator root>/install/act-in-progress.txt` (the commit freeze, DEC-1106 (3); never in either `log/`; not counted by the APPROVED check nor by the install's control-file hash; G9 also holds on the CTO's `<scratch>/log/act-in-progress.txt`) |
| `approvals` | `<operator root>/log/act-approvals.jsonl` |
| others | `claude` (`claude`), `model` (`claude-sonnet-5-5`), `canary_model` (`claude-haiku-5-5`), `budget_usd` (1), `canary_budget_usd` (0.05), `session_timeout_s` (2700), `canary_timeout_s` (300), `check_timeout_s` (3600), `hold_max_s` (0: a hold waits as long as it lasts) |

The journal is `<operator root>/log/journal.json`; a failed undo, or a live change left for the owner under the
restore rule (round 3), holds `<operator root>/log/operator.lock` (every run and launch refuses while it exists; the
run's own freeze is still removed at its end); the session's pid and pgid are in
`log/session.json`; a malformed request goes to `queue/rejected/<stamp>-<pid>/<its name>`, a taken one to
`queue/taken/…` and then `queue/done/…`. Without `--config`, the install reads `install/operator-settings.json` when
it exists (hashed in APPROVED like the code), else the defaults above.

## What the trial could not do in the sandbox (for the CTO's run outside it)

- **`crontab -l`** exits 1 in the sandbox (no crontab readable), so its row below hashes an empty output before and
  after; the live crontab's hash is the CTO's to take outside.
- **No real `claude`:** the canary and the session were run against a stub that models Claude Code's handling of
  `--settings` (by rule). The live canary (a real one-turn session in the wall) and the flags `--disable-slash-commands`,
  `--permission-prompts none` and `--tools` (taken from LAUNCH-SPEC S10) are first exercised by ACT-OPERATOR-1's rehearsal.
- **The real guard's replay:** the replays and the unit tests used a planted guard. The live guard
  (`.claude/hooks/pretooluse.py` importing `gov.guard`) is run by the replay with `PYTHONPATH=<repo>/src` on a clone;
  its behaviour on the real last 48 hours of calls is first seen live.
- **The real push:** a stub channel; the dead-man's `push` channel itself is not started in the sandbox.
- **The replays' checks** were light (`true`, YAML parses); a real ACT's checks (scoped pytest) run in the dry run's
  clone and live, as their manifests state.
- **`~/.claude/`** is hashed for its configuration only (settings, CLAUDE.md, hooks, agents, skills, commands, rules,
  output styles, workflows): its session folders are written by every running session, this one included, and its
  credentials are not read.


## S23 (1): the classifier on every ACT file

57 ACT files under `governance/project/orchestration/packages/` at the trial: the 54 counted at `116c2b413` and 3 later (ACT-D4-RESTORE-1, ACT-GATE-CONFIG-1, ACT-PATHMAP-NS-1). Pass mark: no ACT classed lower than the table puts it. **Lower: 0** (none).

| ACT file | Class | Table | At 116c2b413 | What decided it |
|---|---|---|---|---|
| ACT-1-GUARD.md | (b) | (b) (pinned) | yes | repo:.claude/settings.json (settings: a change the row does not allow as (a)); repo:.rulesync/hooks.jsonc (rulesync-other: the settings' and agents' source (.rulesync/**) |
| ACT-D4-RESTORE-1.md | (b) | (a) (not pinned) | later | repo:tests/optin-lifted-breadth.txt (optin: lines added or changed); repo:tests/optin-lifted-guard.txt (optin: lines added or changed); repo:tests/optin-lifted.txt (optin |
| ACT-D8.md | (O) | (O) (pinned) | yes | repo:.git/worktrees/W2-61h (unknown: src/**, tests, the register, tickets, or a path no rule names: not an ACT's business, or unclassifiable); repo:.git/refs/heads/w2/W2- |
| ACT-DEADMAN-1.md | (b) | (b) (pinned) | yes | crontab:crontab (crontab: crontab lines (NIGHTLY-1, NIGHTLY-STOP-1, SCHEDULE-STOP-2, DISPATCH-CRON-2, DISPATCHER-1, RUNS-SWEEP-1): run code on a schedule outside the guar |
| ACT-DISPATCH-CRON-2.md | (b) | (b) (pinned) | yes | crontab:crontab (crontab: crontab lines (NIGHTLY-1, NIGHTLY-STOP-1, SCHEDULE-STOP-2, DISPATCH-CRON-2, DISPATCHER-1, RUNS-SWEEP-1): run code on a schedule outside the guar |
| ACT-DISPATCHER-1.md | (b) | (b) (pinned) | yes | crontab:crontab (crontab: crontab lines (NIGHTLY-1, NIGHTLY-STOP-1, SCHEDULE-STOP-2, DISPATCH-CRON-2, DISPATCHER-1, RUNS-SWEEP-1): run code on a schedule outside the guar |
| ACT-G14.md | (O) | (b) (pinned) | yes | repo:.gov-runtime/scratch/orchestrator/tools/guard4_check.py (cto-scratch: the CTO's own scratch tools (record_checks.sh): none, never an ACT's business (N-2)) |
| ACT-G14b.md | (b) | (b) (pinned) | yes | repo:.claude/hooks/role_reads.py (guard-hook: guard hook code (1-GUARD, GUARD-FIX-1 to 4, G14, G14b, INDEP-WALLS-1's rule 2c): no rule can prove a code change only tighte |
| ACT-GATE-CONFIG-1.md | (b) | (b) (pinned) | later | home:.gov-os/machine/gate.json (machine-gate: machine gate files (DEC-1103 (1)'s gate.json): they decide what launches); home:.gov-os/machine/server-cpu.json (machine-gat |
| ACT-GUARD-FIX-1.md | (b) | (b) (pinned) | yes | repo:.claude/hooks/pretooluse.py (guard-hook: guard hook code (1-GUARD, GUARD-FIX-1 to 4, G14, G14b, INDEP-WALLS-1's rule 2c): no rule can prove a code change only tighte |
| ACT-GUARD-FIX-2.md | (b) | (b) (pinned) | yes | repo:.claude/hooks/pretooluse.py (guard-hook: guard hook code (1-GUARD, GUARD-FIX-1 to 4, G14, G14b, INDEP-WALLS-1's rule 2c): no rule can prove a code change only tighte |
| ACT-GUARD-FIX-3.md | (O) | (b) (pinned) | yes | repo:.gov-runtime/scratch/orchestrator/tools/test_guard_fix_3.py (cto-scratch: the CTO's own scratch tools (record_checks.sh): none, never an ACT's business (N-2)) |
| ACT-GUARD-FIX-4.md | (O) | (b) (pinned) | yes | repo:.gov-runtime/scratch/orchestrator/tools/guard4_check.py (cto-scratch: the CTO's own scratch tools (record_checks.sh): none, never an ACT's business (N-2)); home:.cla |
| ACT-GUARD-SETS-1.md | (O) | (b) (pinned) | yes | repo:tests/acceptance/W2-84/test_w2_84_code_under_test.py (unknown: src/**, tests, the register, tickets, or a path no rule names: not an ACT's business, or unclassifiabl |
| ACT-HLABEL-1.md | (O) | none (not pinned) | yes | home:gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/h02.yaml (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessio |
| ACT-HLABEL-2.md | (O) | none (not pinned) | yes | home:gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/h03.yaml (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessio |
| ACT-HLABEL-3.md | (O) | none (not pinned) | yes | home:gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/h26.yaml (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessio |
| ACT-HNEW-1.md | (O) | none (not pinned) | yes | home:gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/h25.yaml (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessio |
| ACT-INDEP-WALLS-1.md | (O) | (b) (pinned) | yes | repo:governance/project/indep-walls/CLAUDE.md.tmpl (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessions under DEC-1101 ( |
| ACT-MSET-1.md | (O) | none (not pinned) | yes | home:gov-os-eval/fixtures/evaluation/memory-verdict/hidden (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessions under DE |
| ACT-MSET-2.md | (O) | none (not pinned) | yes | home:gov-os-eval/fixtures/evaluation/memory-verdict/XCHECK.md (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessions under |
| ACT-MSET-3.md | (O) | none (not pinned) | yes | home:gov-os-writer/.claude/settings.json (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessions under DEC-1101 (N-2)); hom |
| ACT-MSET-4.md | (O) | none (not pinned) | yes | home:gov-os-eval/fixtures/evaluation/memory-verdict-2/XCHECK.md (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessions und |
| ACT-NIGHTLY-0400.md | (O) | (O) (pinned) | yes | script hit windows: powershell.exe -NoProfile -Command x |
| ACT-NIGHTLY-1.md | (O) | (b) (pinned) | yes | script hit windows: powershell.exe -NoProfile -Command x |
| ACT-NIGHTLY-STOP-1.md | (O) | (b) (pinned) | yes | home:crontab.pre-nightly-stop-<stamp>.txt (unknown: src/**, tests, the register, tickets, or a path no rule names: not an ACT's business, or unclassifiable) |
| ACT-OLLAMA-CAP-1.md | (a) | (a) (not pinned) | yes | home:.ollama/serve-11434.log (servers: the shared servers' committed configs and modules, with their restart (OLLAMA-CAP-1, QUERY-CPUS-1, QUERY-GPU-2, RERANK-GPU-SLOTS-1, |
| ACT-P-TRACE-IMPL-1.md | (O) | (O) (pinned) | yes | repo:governance/project/path-map.yaml (path-map: a change to accepted_history, read only from the owner's commits) |
| ACT-PATHMAP-NS-1.md | (b) | (b) (not pinned) | later | repo:governance/project/path-map.yaml (path-map: a change the row does not allow as (a)) |
| ACT-PERMISSIONS-1.md | (b) | (b) (pinned) | yes | repo:.claude/settings.local.json (settings: cannot be parsed (JSONDecodeError): never (a)); repo:.claude/settings.local.json.pre-act-permissions-1 (claude-rest: the rest  |
| ACT-PERMISSIONS-2.md | (b) | (b) (pinned) | yes | repo:.claude/settings.local.json (settings: cannot be parsed (JSONDecodeError): never (a)); repo:.claude/settings.local.json.pre-act-permissions-2 (claude-rest: the rest  |
| ACT-PUSH-INPUT-1.md | (b) | (b) (pinned) | yes | home:.claude/settings.json (settings: cannot be parsed (JSONDecodeError): never (a)) |
| ACT-QUERY-CPUS-1.md | (a) | (a) (not pinned) | yes | home:.ollama/serve-11435.log (servers: the shared servers' committed configs and modules, with their restart (OLLAMA-CAP-1, QUERY-CPUS-1, QUERY-GPU-2, RERANK-GPU-SLOTS-1, |
| ACT-QUERY-GPU-1.md | (a) | (a) (not pinned) | yes | home:.ollama/serve-11435.log (servers: the shared servers' committed configs and modules, with their restart (OLLAMA-CAP-1, QUERY-CPUS-1, QUERY-GPU-2, RERANK-GPU-SLOTS-1, |
| ACT-QUERY-GPU-2.md | (b) | (a) (not pinned) | yes | home:.local/bin/ollama (installs: installs and downloads without sudo (RERANK-TRIAL-1/2): new code on the machine (DEC-083, DEC-957)) |
| ACT-QUIET-DENY-1.md | (b) | (b) (pinned) | yes | repo:.claude/settings.local.json (settings: cannot be parsed (JSONDecodeError): never (a)) |
| ACT-REPIN-1.md | (O) | (O) (pinned) | yes | repo:governance/project/tool-registry.yaml (unknown: src/**, tests, the register, tickets, or a path no rule names: not an ACT's business, or unclassifiable); home:.local |
| ACT-REPIN-2.md | (O) | (O) (pinned) | yes | repo:governance/project/tool-registry.yaml (unknown: src/**, tests, the register, tickets, or a path no rule names: not an ACT's business, or unclassifiable); home:.local |
| ACT-REPIN-EMERGENCY-1.md | (O) | (O) (pinned) | yes | repo:governance/project/tool-registry.yaml (unknown: src/**, tests, the register, tickets, or a path no rule names: not an ACT's business, or unclassifiable); home:.local |
| ACT-REPIN-W2.md | (O) | (O) (pinned) | yes | repo:governance/project/tool-registry.yaml (unknown: src/**, tests, the register, tickets, or a path no rule names: not an ACT's business, or unclassifiable); home:.local |
| ACT-REPIN-W3.md | (O) | (O) (pinned) | yes | repo:governance/project/tool-registry.yaml (unknown: src/**, tests, the register, tickets, or a path no rule names: not an ACT's business, or unclassifiable); home:.local |
| ACT-REPIN-W4.md | (O) | (O) (pinned) | yes | repo:governance/project/tool-registry.yaml (unknown: src/**, tests, the register, tickets, or a path no rule names: not an ACT's business, or unclassifiable); home:.local |
| ACT-RERANK-CPU-1.md | (a) | (a) (not pinned) | yes | home:.local/share/gov-os/reranker-venv/lib/python3.12/site-packages/gov-reranker-cpu.pth (servers: the shared servers' committed configs and modules, with their restart ( |
| ACT-RERANK-GPU-SLOTS-1.md | (a) | (a) (not pinned) | yes | home:.local/share/gov-os/reranker-venv/lib/python3.12/site-packages/gov_reranker_gpu_slot.py (servers: the shared servers' committed configs and modules, with their resta |
| ACT-RERANK-TRIAL-1.md | (O) | (b) (pinned) | yes | repo:.gov-runtime/scratch/orchestrator/log/act-in-progress.txt (cto-scratch: the CTO's own scratch tools (record_checks.sh): none, never an ACT's business (N-2)); home:.c |
| ACT-RERANK-TRIAL-2.md | (O) | (b) (pinned) | yes | repo:.gov-runtime/scratch/orchestrator/log/act-in-progress.txt (cto-scratch: the CTO's own scratch tools (record_checks.sh): none, never an ACT's business (N-2)); home:.c |
| ACT-RERANK-WAIT-1.md | (a) | (a) (not pinned) | yes | home:.local/share/gov-os/reranker-venv/lib/python3.12/site-packages/gov_reranker_gpu_slot.py (servers: the shared servers' committed configs and modules, with their resta |
| ACT-RUNS-SWEEP-1.md | (b) | (b) (pinned) | yes | crontab:crontab (crontab: crontab lines (NIGHTLY-1, NIGHTLY-STOP-1, SCHEDULE-STOP-2, DISPATCH-CRON-2, DISPATCHER-1, RUNS-SWEEP-1): run code on a schedule outside the guar |
| ACT-SANDBOX-SEAL-1.md | (O) | (a) (not pinned) | yes | repo:governance/project/indep-walls/CLAUDE.md.tmpl (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessions under DEC-1101 ( |
| ACT-SCHEDULE-STOP-2.md | (O) | (b) (pinned) | yes | home:crontab.pre-schedule-stop-<stamp>.txt (unknown: src/**, tests, the register, tickets, or a path no rule names: not an ACT's business, or unclassifiable) |
| ACT-SELECT-FIXES-1.md | (O) | (b) (pinned) | yes | repo:.gov-runtime/scratch/orchestrator/tools/record_checks.sh (cto-scratch: the CTO's own scratch tools (record_checks.sh): none, never an ACT's business (N-2)) |
| ACT-SELECT-HOOK-1.md | (b) | (b) (pinned) | yes | repo:.git/hooks/reference-transaction (git-hooks: git hooks (SELECT-HOOK-1): they run code outside every session's guard) |
| ACT-SENTINEL-1.md | (b) | (b) (pinned) | yes | script hit session: ~/.local/bin/claude --remote-control CTO sentinel --model claude-haiku-5-5 --set |
| ACT-STOP-WAITER-1.md | (b) | (b) (pinned) | yes | repo:.claude/settings.local.json (settings: cannot be parsed (JSONDecodeError): never (a)) |
| ACT-W1-01-EXEMPT-1.md | (O) | (O) (pinned) | yes | repo:governance/project/path-map.yaml (path-map: a change to acceptance_exemptions, read only from the owner's commits) |
| ACT-W2-57-LS-1.md | (O) | (O) (pinned) | yes | repo:governance/project/path-map.yaml (path-map: a change to load_sensitive, read only from the owner's commits) |
| ACT-WSL-INTEROP-1.md | (O) | (O) (pinned) | yes | script hit windows: /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -Comman; script hit sudo: sudo sh -c echo ":WSLInterop:M::MZ::/init:PF" > /pr |

| Class | Count |
|---|---|
| (a) | 6 |
| (b) | 19 |
| (O) | 32 |
| all | 57 |

## Rises

Every ACT the code classes higher than the table's row (the class only rises; each is a refusal or a yes the table would not have asked for, never a lower class):

| ACT | Table | Code | Why the class rose |
|---|---|---|---|
| ACT-D4-RESTORE-1 | (a) | (b) | repo:tests/optin-lifted-breadth.txt (optin: lines added or changed); repo:tests/optin-lifted-guard.txt (optin: lines added or changed); repo:tests/optin-lifted.txt (optin: lines added or changed) |
| ACT-G14 | (b) | (O) | repo:.gov-runtime/scratch/orchestrator/tools/guard4_check.py (cto-scratch: the CTO's own scratch tools (record_checks.sh): none, never an ACT's business (N-2)) |
| ACT-GUARD-FIX-3 | (b) | (O) | repo:.gov-runtime/scratch/orchestrator/tools/test_guard_fix_3.py (cto-scratch: the CTO's own scratch tools (record_checks.sh): none, never an ACT's business (N-2)) |
| ACT-GUARD-FIX-4 | (b) | (O) | repo:.gov-runtime/scratch/orchestrator/tools/guard4_check.py (cto-scratch: the CTO's own scratch tools (record_checks.sh): none, never an ACT's business (N-2)); home:.claude/settings.json.pre-act-guar |
| ACT-GUARD-SETS-1 | (b) | (O) | repo:tests/acceptance/W2-84/test_w2_84_code_under_test.py (unknown: src/**, tests, the register, tickets, or a path no rule names: not an ACT's business, or unclassifiable); repo:tests/acceptance/W2-8 |
| ACT-HLABEL-1 | none | (O) | home:gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/h02.yaml (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessions under DEC-1101 (N-2)); home |
| ACT-HLABEL-2 | none | (O) | home:gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/h03.yaml (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessions under DEC-1101 (N-2)); home |
| ACT-HLABEL-3 | none | (O) | home:gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/h26.yaml (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessions under DEC-1101 (N-2)); home |
| ACT-HNEW-1 | none | (O) | home:gov-os-eval/fixtures/evaluation/memory-retrieval/hidden/h25.yaml (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessions under DEC-1101 (N-2)); home |
| ACT-INDEP-WALLS-1 | (b) | (O) | repo:governance/project/indep-walls/CLAUDE.md.tmpl (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessions under DEC-1101 (N-2)); repo:governance/project |
| ACT-MSET-1 | none | (O) | home:gov-os-eval/fixtures/evaluation/memory-verdict/hidden (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessions under DEC-1101 (N-2)) |
| ACT-MSET-2 | none | (O) | home:gov-os-eval/fixtures/evaluation/memory-verdict/XCHECK.md (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessions under DEC-1101 (N-2)); home:gov-os- |
| ACT-MSET-3 | none | (O) | home:gov-os-writer/.claude/settings.json (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessions under DEC-1101 (N-2)); home:gov-os-writer/.claude/settin |
| ACT-MSET-4 | none | (O) | home:gov-os-eval/fixtures/evaluation/memory-verdict-2/XCHECK.md (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessions under DEC-1101 (N-2)) |
| ACT-NIGHTLY-1 | (b) | (O) | script hit windows: powershell.exe -NoProfile -Command x |
| ACT-NIGHTLY-STOP-1 | (b) | (O) | home:crontab.pre-nightly-stop-<stamp>.txt (unknown: src/**, tests, the register, tickets, or a path no rule names: not an ACT's business, or unclassifiable) |
| ACT-QUERY-GPU-2 | (a) | (b) | home:.local/bin/ollama (installs: installs and downloads without sudo (RERANK-TRIAL-1/2): new code on the machine (DEC-083, DEC-957)) |
| ACT-RERANK-TRIAL-1 | (b) | (O) | repo:.gov-runtime/scratch/orchestrator/log/act-in-progress.txt (cto-scratch: the CTO's own scratch tools (record_checks.sh): none, never an ACT's business (N-2)); home:.cache/gov-os-trial (unknown: sr |
| ACT-RERANK-TRIAL-2 | (b) | (O) | repo:.gov-runtime/scratch/orchestrator/log/act-in-progress.txt (cto-scratch: the CTO's own scratch tools (record_checks.sh): none, never an ACT's business (N-2)); home:.cache/gov-os-trial/hf/hub/model |
| ACT-SANDBOX-SEAL-1 | (a) | (O) | repo:governance/project/indep-walls/CLAUDE.md.tmpl (walled-sessions: the blind writers and checkers (HLABEL-1 to 3, HNEW-1, MSET-1 to 4): walled sessions under DEC-1101 (N-2)); repo:governance/project |
| ACT-SCHEDULE-STOP-2 | (b) | (O) | home:crontab.pre-schedule-stop-<stamp>.txt (unknown: src/**, tests, the register, tickets, or a path no rule names: not an ACT's business, or unclassifiable) |
| ACT-SELECT-FIXES-1 | (b) | (O) | repo:.gov-runtime/scratch/orchestrator/tools/record_checks.sh (cto-scratch: the CTO's own scratch tools (record_checks.sh): none, never an ACT's business (N-2)) |

## S23 (2): 8 applied ACTs replayed end to end

Each in a clone of this repository at the commit before it was applied (its applying commit's parent, or, for an ACT with no repository commit, the commit that added its ACT file), with a planted operator root (the install and its APPROVED), HOME, scratch, transcript (the owner's yes for (b)), clock, crontab stub and push stub; its planted review record READY with the table's class.

| Replay | Class | Outcome | Gate | Votes (code, claim, review) | At | Built from |
|---|---|---|---|---|---|---|
| ACT-SELECT-FIXES-1 | (b) | applied | all passed | b, b, b | `8038e0ee648c^` | the applying commit 8038e0ee648c |
| ACT-SELECT-HOOK-1 | (b) | applied | all passed | b, b, b | `2e10e8aba81d` | a planted hook; the ACT's one line added (its command neutralised: the trial never starts the live selection) |
| ACT-GUARD-SETS-1 | (b) | applied | all passed | b, b, b | `15952bbfa576^` | the applying commit 15952bbfa576 (its hook, path map and opt-in list; see below) |
| ACT-PERMISSIONS-2 | (b) | applied | all passed | b, b, b | `ef08c01e37bc` | a planted settings.local.json; the ACT's change (additional directories and read deny rules) as its apply.py makes it |
| ACT-NIGHTLY-STOP-1 | (b) | applied | all passed | b, b, b | `27f44b5304dc` | the planted crontab (a stub: never the live one); its nightly line commented out |
| ACT-OLLAMA-CAP-1 | (a) | applied | all passed | a, a, a | `be668bc5cfb2` | the server's restart as its log in the planted HOME (the trial restarts no server) |
| ACT-W1-01-EXEMPT-1 | (O) | refused | G6 | O, O, O | `2acc8a314ec7^` | the applying commit 2acc8a314ec7 |
| ACT-D8 | (O) | refused | G6 | O, O, O | `2ae4e094162c` | its deletions as listed (placeholders), its commands from its text |

ACT-GUARD-SETS-1's whole applying commit (`15952bbfa576`) also changed test files (`tests/acceptance/W2-84/**`, `tests/unit/guard/test_w2_84_trees.py`): replayed whole, the code's vote is (O) and it is **refused at G6** ("yours"), a rise listed above. The row above replays its control files only (the guard hook, the path map and the opt-in list): (b), applied with the owner's yes. A future ACT of this kind splits its test changes into a ticket.


## S23 (3): 7 planted faults

| Fault | Outcome | Gate | Reason |
|---|---|---|---|
| an edit after review | refused | G4 | the verdict block names another manifest sha: changed after review |
| a wrong class claim | refused | G6 | class (b): no owner's line 'yes ACT-SELECT-FIXES-1 18209bf5' after the review in the CTO session's transcript |
| an unlisted file touched | refused | G8 | the dry run changed a file not on the touched list (unlisted): repo:docs/unlisted-by-the-trial.txt |
| a red check | undone | checks | a check is red after the apply (test ! -e .live-marker); undone |
| a failing undo | lock held | checks | a check is red after the apply (test ! -e .live-marker); undone; the undo failed (apply.sh undo exited 7): lock held |
| a missing yes | refused | G6 | class (b): no owner's line 'yes ACT-SELECT-FIXES-1 53906d8e' after the review in the CTO session's transcript |
| a yes for an older sha | refused | G6 | class (b): no owner's line 'yes ACT-SELECT-FIXES-1 53906d8e' after the review in the CTO session's transcript |

## S23 (4): no live file changed

Hashed before the trial and after it (names and hashes only: each row's sha256 is over the sorted `path<TAB>sha256` lines of its files; no content was printed or read into the record).

| Path | Files | Before | After |
|---|---|---|---|
| live repository: .claude/hooks/** | 6 | 8d775c6a79680b1086e66fda5b17a5b737997c4cbea8c2ee76b06e684a5dbb06 | 8d775c6a79680b1086e66fda5b17a5b737997c4cbea8c2ee76b06e684a5dbb06 |
| live repository: .claude/settings*.json | 2 | 1730c3f7c9ca19acabb591726c994d889e12b6852e9148d097572662721af9b9 | 1730c3f7c9ca19acabb591726c994d889e12b6852e9148d097572662721af9b9 |
| live repository: the rest of .claude/** (agents, skills, commands) | 41 | fd9570353a05e66acdda70661a8ff4332a186f082b593f310402c0a9947aa0d7 | fd9570353a05e66acdda70661a8ff4332a186f082b593f310402c0a9947aa0d7 |
| live repository: .git/hooks/** | 15 | a3037550074b3cf21383ac235cff33081e0ef1e4da1d09bbc8efe18c9d0d7c9c | a3037550074b3cf21383ac235cff33081e0ef1e4da1d09bbc8efe18c9d0d7c9c |
| live repository: path map, test map, opt-in lists | 6 | 53a48621ed3afbcc7bc224b23377940170369fdc42b3c9184654771a8fee8bec | 53a48621ed3afbcc7bc224b23377940170369fdc42b3c9184654771a8fee8bec |
| live repository: deadman.py, sentinel-brief.md | 2 | d467b8db04823b8cefb018b391b2122db6df960ff42db021b3a13bf0a887492f | d467b8db04823b8cefb018b391b2122db6df960ff42db021b3a13bf0a887492f |
| the pin ~/.local/bin/gov | 1 | 20205dbcd3d368875c5ffdb9543efad210f35cfa482f90316147c301b17f4b46 | 20205dbcd3d368875c5ffdb9543efad210f35cfa482f90316147c301b17f4b46 |
| ~/gov-os-operator/ (every file) | 41 | 4ffe90672c21702f037b221665518ee0aa44e63cc92c87d2b9e929f924de292b | 4ffe90672c21702f037b221665518ee0aa44e63cc92c87d2b9e929f924de292b |
| ~/.claude/ (its configuration: settings, CLAUDE.md, hooks, agents, skills, commands, rules) | 233 | aecb0752f552ee3736efc4d3eae78a452be2e76212f6d7a70ba28a46ecb6ba91 | aecb0752f552ee3736efc4d3eae78a452be2e76212f6d7a70ba28a46ecb6ba91 |
| crontab -l (its output; exit 1) | 1 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |

Equal: **True**.

## Round 2: the review's findings (2026-11-09)

The independent review's round 1 found the work not READY: F1 and F2 blocked (in scope, ordinary work, fail open).
Round 2 fixes both and the cheap rows; F3, F5 and F7 are left to the CTO and the owner, as the round-2 brief says.
Commits on `w2/W2-148`: `f680fc5ae` (F1, F14) and `43eb90435` (the rest); unit cases in
`tests/unit/operator/test_w2_148_parts.py` (F1, F14) and `tests/unit/operator/test_w2_148_round2.py` (the rest).

| Finding | The fix | Unit cases |
|---|---|---|
| F1 (S6, blocking) | `act_class.strip_wrappers` steps over the shell's reserved words and grouping marks (`if then else elif fi do done while until esac { } ( ) ! coproc`) as it steps over `env`; a `for`/`select` header is skipped up to its `do`, a `case` header and `function <name>` are skipped. So `then sudo …`, `do git push`, `{ git tag v1; }`, `then rm -rf ~/x`, `do curl https://…`, `then pip install …`, `! git push` and `else git push` give their hits, in `commands` and in `apply.sh` | `test_reserved_words_are_stepped_over` (19 forms, each in a command and in `apply.sh`: those eight, `elif`, `while`, `until`, a subshell, a multi-line `for`, a function body `f() { … }`, `function g { … }`, a heredoc-fed `bash`, a `case` arm; and two that stay (a): a local `curl` in a loop, reserved words as `echo`'s arguments) |
| F2 (S12, blocking): refuse before running | `operator_run.path_rule` at G1, on the frozen copy, before anything runs: `apply.sh`, each manifest command and each check is refused when it names the live repository's path (the `repo` setting, and its real path) or the real HOME (the `home` setting) literally, the repository as `~/<rel>`, `$HOME/<rel>`, `${HOME}/<rel>` (quoted or not), HOME as `~<user>`, or `cd`s/`pushd`es to HOME (a bare `cd`, `cd ~`, `cd $HOME`, `cd ${HOME}`). The reason names the rule: "the frozen script must work relative to its cwd and HOME". `$HOME/<file>` and `cd "$(dirname …)"` stay allowed (the dry run plants HOME). The settings' values are the live ones by default, so planted runs check against their planted roots | `test_the_path_rule_reads_every_form` (16 refused forms, 12 allowed), `test_g1_refuses_a_script_that_names_the_live_paths` (in `apply.sh`, a command, a check, a bare `cd`, the HOME path), `test_g1_refuses_the_repository_named_through_home` |
| F2: detect after the dry run | `Run.g8` reads the live touched files and the control files (§3's list: `.claude/**`, `.rulesync/**`, the git hooks, `.git/config` and core.hooksPath's folder, `crontab -l`, the pin, the dead-man's and the sentinel's code, the path map, the install) before the dry run and again after it, whatever its outcome. On any change it restores the touched files from the frozen `before/` copies and the control files from the bytes read before, re-reads them, and refuses at G8 with "LIVE FILES CHANGED during the dry run (…)"; the log line carries `live_changed` and `restored`; the refusal after G7 pushes the P1, whose text says live files changed; a restore that does not bring every file back holds the lock | `test_a_live_file_changed_by_the_dry_run_is_restored_and_refused` (a touched file, a control file, the pin created in HOME; each path built at run time so the G1 rule cannot see it) |
| F2: the briefs | `reviewer-brief.md`'s first check now holds the path rule (relative to the cwd and `$HOME`, the bundle through the script's own folder, no live path named, no `cd` to either). `brief.md` needs nothing for it: the session never writes a script | — |
| F14 | An empty touched list with any command (a manifest command, or an `apply.sh` line beyond `exit`, `set`, `echo`, `cd`, `test` …) adds the hit `commands-only`, class (b) in `class-rules.yaml` | `test_an_empty_touched_list_with_commands_is_at_least_b` |
| F8 | G1 never removes or replaces an existing `acts/<id>-<sha12>/`: a second request for the same sha reuses it only when its manifest hashes as the request and every file as the manifest says; otherwise "changed after review", the copy left as it is. Only `review.md` (not hashed by the manifest) is taken afresh from the bundle, so a later review round on the same manifest is read | `test_a_stale_requeue_never_replaces_an_applied_acts_frozen_copy` (re-queued after an edit: refused at G7, the frozen bytes unchanged, the owner's undo then works), `test_an_existing_frozen_copy_that_changed_is_refused_and_left_alone`, `test_a_later_review_round_on_the_same_manifest_is_read` |
| F9 | G4 refuses a manifest with no `author` | `test_g4_refuses_a_manifest_with_no_author` |
| F10 | An unexpected error at G7 or later (`Run.at`, the gate being run) is pushed as a P1 (kind `refused`) and its log line carries `notice: refused`, so the digest's `missing_notices` counts it when the push is missing; an error before G7 is logged only | `test_an_unexpected_error_after_g7_is_pushed_and_counted`, `test_an_error_before_g7_is_not_pushed` |
| F11 | `.git/config` and the files of the folder core.hooksPath names (when outside `.git/hooks`) join the control snapshot (S15 and the F2 re-hash); `.git/config` joins the dry run's changed set and the live unlisted-file check | `test_the_dry_run_counts_git_config_in_its_changed_set`, `test_a_live_git_config_change_is_undone`, `test_the_folder_core_hookspath_names_is_a_control` |
| F12 | G9 (and so the launcher) also holds while `NIGHTLY-RUNNING` exists: setting `nightly_flag`, default `<scratch>/NIGHTLY-RUNNING` (`nightly.sh` writes `$ORCH/NIGHTLY-RUNNING`, `ORCH` the CTO's scratch); a flag older than `nightly_flag_max_age_s` (6 hours, `nightly.sh`'s own stale mark) is a dead run's leftover and does not hold | `test_g9_holds_while_the_nightly_flag_is_fresh`, `test_a_dead_nightlys_old_flag_does_not_hold` |
| F13 | `owner_text` refuses a line with `isCompactSummary` (beside `isMeta`) | `test_a_compact_summary_is_never_the_owners_line` |
| F6 | The wall's settings `env` sets `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS` to `session_timeout_s` less a minute (2,640,000 ms by default); `request.txt` names it as `timeout_ms`, and `brief.md` tells the session to give its one Bash call that timeout, never in the background, never twice | `test_the_wall_sizes_the_bash_timeout_to_the_session` |
| F4 | Without `push_cmd` (today's default), a notice goes through the dead-man's three channels from the install's own code (the forms of `deadman.py`'s `send()` copied, nothing imported): the JSON line in `pings_log` (the log channel, as before), the Windows toast through the install's own `win_toast.ps1` (a copy), and a headless `claude -p` asked to call PushNotification with the line. The line (`notice_line`) is at most 190 characters: the priority and the ACT first, then the gate or the result, then the undo line; the middle is cut, never the head or the undo line; no "TEST" label, no `deadman.log` note. `push_cmd` still overrides it (the tests' stub) | `test_the_notice_line_fits_190_and_keeps_its_head_and_undo`, `test_the_default_notice_goes_through_the_three_channels` (stub `claude`, PowerShell and `wslpath`) |
| F3, F5, F7 | Not in this round (the CTO's or the owner's): the replay's call source, the freeze's place and the hand-over rule, the session's `apply.sh` and `git` forms | — |

### Round 2's runs

- **Unit tests:** 153 passed (`tests/unit/operator/`, 108 in round 1 plus 19 F1 forms, 1 F14 case and 25 in
  `test_w2_148_round2.py`), run with `-m "not local_only" -k "not real and not green_here and not time_limit"`
  (the exclusion left nothing out of this folder).
- **`gov accept W2-148`:** pass, 157 passed, 0 failed, 0 skipped, 0 unmapped; every one of the 38 lines pass
  (success-1 to 24, failure-1 to 14).
- **The trial re-run (S23):** the same results as round 1. 57 ACT files (54 counted at `116c2b413`, 3 later:
  ACT-D4-RESTORE-1, ACT-GATE-CONFIG-1, ACT-PATHMAP-NS-1), none lower than the table, counts (a) 6, (b) 19, (O) 32,
  the same 22 rises. The 8 replays (their `apply.sh` relative, so the path rule passes them): SELECT-FIXES-1,
  SELECT-HOOK-1, PERMISSIONS-2, NIGHTLY-STOP-1 applied as (b), OLLAMA-CAP-1 applied as (a), GUARD-SETS-1 whole refused
  at G6 as (O) and its control part applied as (b), W1-01-EXEMPT-1 and D8 refused at G6 as (O). The 7 faults: an edit
  after review refused (G4), a wrong class claim refused (G6), an unlisted file touched refused (G8), a red check undone,
  a failing undo lock held, a missing yes refused (G6), a yes for an older sha refused (G6). The live files, hashed
  before and after the run, equal:

| Path | Files | Before | After |
|---|---|---|---|
| live repository: .claude/hooks/** | 6 | 8d775c6a79680b1086e66fda5b17a5b737997c4cbea8c2ee76b06e684a5dbb06 | 8d775c6a79680b1086e66fda5b17a5b737997c4cbea8c2ee76b06e684a5dbb06 |
| live repository: .claude/settings*.json | 2 | 1730c3f7c9ca19acabb591726c994d889e12b6852e9148d097572662721af9b9 | 1730c3f7c9ca19acabb591726c994d889e12b6852e9148d097572662721af9b9 |
| live repository: the rest of .claude/** (agents, skills, commands) | 41 | fd9570353a05e66acdda70661a8ff4332a186f082b593f310402c0a9947aa0d7 | fd9570353a05e66acdda70661a8ff4332a186f082b593f310402c0a9947aa0d7 |
| live repository: .git/hooks/** | 15 | a3037550074b3cf21383ac235cff33081e0ef1e4da1d09bbc8efe18c9d0d7c9c | a3037550074b3cf21383ac235cff33081e0ef1e4da1d09bbc8efe18c9d0d7c9c |
| live repository: path map, test map, opt-in lists | 6 | de1deae14fc972c91fffb7be5c0db35c8b0a86918cb4c12ef00e785ed7cbf91a | de1deae14fc972c91fffb7be5c0db35c8b0a86918cb4c12ef00e785ed7cbf91a |
| live repository: deadman.py, sentinel-brief.md | 2 | d467b8db04823b8cefb018b391b2122db6df960ff42db021b3a13bf0a887492f | d467b8db04823b8cefb018b391b2122db6df960ff42db021b3a13bf0a887492f |
| the pin ~/.local/bin/gov | 1 | 20205dbcd3d368875c5ffdb9543efad210f35cfa482f90316147c301b17f4b46 | 20205dbcd3d368875c5ffdb9543efad210f35cfa482f90316147c301b17f4b46 |
| ~/gov-os-operator/ (every file) | 41 | 7b68bd2edda32656dbd12e809457d9652507e2f141391f4da59daea25b558ba7 | 7b68bd2edda32656dbd12e809457d9652507e2f141391f4da59daea25b558ba7 |
| ~/.claude/ (its configuration: settings, CLAUDE.md, hooks, agents, skills, commands, rules) | 233 | aecb0752f552ee3736efc4d3eae78a452be2e76212f6d7a70ba28a46ecb6ba91 | aecb0752f552ee3736efc4d3eae78a452be2e76212f6d7a70ba28a46ecb6ba91 |
| crontab -l (its output; exit 1) | 1 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |

Equal: **True**. Two rows differ from round 1's (the path map row and `~/gov-os-operator/`): the live files changed
between the two runs by others' work; within each run before and after are equal.

## Round 3 (DEC-1106): the owner's exception round, F15 and the freeze (2026-11-09)

Review round 2 found one blocking defect, F15: the live re-hash around G8 and the (a) after-check's undo restored every
live difference and deleted files created meanwhile, so a CTO commit or merge landing during the dry run or the apply
was reverted (a guard tightening silently stopped applying) and the P1 blamed the dry run. The owner's DEC-1106 decided
one exception round to DEC-1010: (1) the restore rule, (3) the commit freeze in the install folder. Code commit on
`w2/W2-148`: `1ac0c1716fe4`; unit cases in `tests/unit/operator/test_w2_148_round3.py` (22 new) and six round-1/2 cases
revised to the new rule.

| Point | The change | Unit cases |
|---|---|---|
| (1) after G8 (`Run.g8`, `Run.live_changed`) | The live touched files and the control files (the path map among them; files created or removed under `.claude/**` count) are re-hashed after the dry run against the hashes taken before it. A touched file whose live bytes are the frozen after-copy's (absent, for a deletion: `is_after`) is the dry run's own change and is restored to its bytes from before the dry run; anything else (a control file, a file created or removed, a touched file at third bytes) is left exactly as it is. Always refused at `G8`; the reason, and so the P1's `text`, holds "live files changed" and names every file (no truncation); with anything left, the lock is held (S22's form: the next run and the next launch refuse at `lock`). The result and the log line carry `live_changed`, `restored_files`, `left`, `lock` | `test_g8_the_dry_runs_own_change_is_restored_and_refused_without_the_lock`, `test_g8_a_concurrent_commit_to_the_path_map_is_left_with_the_lock` (the commit stays in HEAD, the tree clean, the next run and launch refused at the lock and change nothing), `test_g8_a_new_skill_file_committed_meanwhile_is_left`, `test_g8_a_touched_file_at_third_bytes_is_left`, `test_g8_both_at_once_its_own_restored_the_rest_left`; revised: `test_a_live_file_changed_by_the_dry_run_is_left_refused_and_locked` (3 forms) |
| (1) in every live undo (`undo_live`, used by the (a) after-check's undo, the apply's other failures, the owner's undo and the journal's) | The blind restorers `restore_controls` and `restore_tree` are gone. Each touched file is read: at its after-copy it is the ACT's own and is undone; at its before-copy nothing is done; at third bytes it is left. With no touched file at third bytes the frozen `apply.sh undo` runs as before; with one, `apply.sh` is not run (it would write over it) and each own file is put back from the frozen `before/` copy. Every other difference since the undo state was taken (the control files, S15's list, and the tree as git status reports it) is left as written and named (`foreign_differences`). The undo commit holds only the own files; a commit someone else made meanwhile stays in HEAD's history. With anything left: the lock held, the P1 naming each file (`left_text`), the result `undone` (or `refused` when the undo itself failed), never `applied`. `after_checks` now names every differing control file, not only the first | `test_a_concurrent_control_commit_during_the_checks_is_left_and_the_acts_own_file_undone` (the undo commit holds only `tests/optin-x.txt`; the other commit stays), `test_a_control_file_written_but_not_committed_during_the_checks_is_left`, `test_a_crontab_change_during_the_checks_is_left` (a stateful crontab stub), `test_the_acts_touched_file_at_third_bytes_in_the_undo_is_left_too`, `test_a_clean_a_act_with_no_concurrent_change_is_applied_without_the_lock`; revised: `test_an_a_act_changing_a_control_file_live_is_undone_and_the_control_left`, `test_a_live_git_config_change_is_left_and_locked`, `test_the_folder_core_hookspath_names_is_a_control` |
| (1) the hook points | `GOV_OPERATOR_TEST_HOOK` gains `in-G8` (after the dry run's steps and the clone's removal, before the live re-hash; the hashes from before are already taken) and `in-apply-checks` (for every class, after `apply.sh apply`, the checks and the run's own commit, before the after-check). The run waits for the hook, ignores its exit code, runs no git command while it runs (so holds no `.git/index.lock`) and gives it its own environment | `test_the_hook_is_waited_for_its_exit_code_ignored_and_no_git_lock_held`, `test_the_in_apply_checks_point_runs_for_a_b_act_too`, and every case above |
| (3) the commit freeze | `<operator root>/install/act-in-progress.txt` (the `freeze` setting's default). Claimed with `O_EXCL` after G9 passes (`claim_freeze`; a run that finds it taken meanwhile waits at G9 again: it never refuses for a hold), its text a token unique to the run, recorded in the journal; removed at the end of the run whatever the outcome, only while it still holds that token (`release_freeze`). Never in either `log/`. The APPROVED check and the install's control-file hash leave it out. A stale one holds G9 (a `G9 held` line, in the run and now also in the launcher's log) and is never removed by a run that did not write it; the owner's undo refuses (nothing written) while one is held; the journal's undo removes the dead run's freeze only when it still holds the token that run recorded | `test_the_freeze_defaults_to_the_install_folder`, `test_the_approved_check_and_the_control_hash_never_count_the_freeze`, `test_the_freeze_is_claimed_once_and_released_only_by_its_writer`, `test_the_freeze_exists_during_the_apply_in_install_never_in_a_log_and_is_gone_after` (seen from the hook: in `install/`, in neither log, no index lock, a `digest` passing the APPROVED check meanwhile), `test_a_stale_freeze_holds_g9_and_is_never_removed_by_the_run`, `test_a_stale_freeze_holds_until_it_is_gone_then_the_run_proceeds`, `test_the_launcher_holds_on_a_stale_freeze_with_a_g9_line`, `test_the_owners_undo_never_writes_over_a_stale_freeze`, `test_the_journals_undo_removes_only_the_freeze_its_run_wrote` (own token, someone else's) |
| F19 | The defaults table above: `push_cmd` unset means the three channels; `freeze` the install folder | — |
| Not in this round | F3 (the guard's call log: its own ACT, DEC-1106 (2)); F7 (kept, DEC-1106 (4)); F16 to F18 and F20 (their text was not in this round's brief) | — |

### Round 3's runs

- **Unit tests:** 175 passed (`tests/unit/operator/`: round 2's 153 plus 22 in `test_w2_148_round3.py`; 6 cases
  revised in place), run with `-m "not local_only" -k "not real and not green_here and not time_limit"` (the exclusion
  left nothing out of this folder).
- **`gov accept W2-148`:** pass, 166 passed, 0 failed, 0 skipped, 0 unmapped; every one of the 39 lines pass
  (success-1 to 24, failure-1 to 15; failure-15, DEC-1106's line, 7 passed).
- **The trial re-run (S23):** the same results as round 2. 57 ACT files (54 at `116c2b413`, 3 later), none lower than
  the table, counts (a) 6, (b) 19, (O) 32, the same 22 rises; the 8 replays as before (SELECT-FIXES-1, SELECT-HOOK-1,
  GUARD-SETS-1's control part, PERMISSIONS-2, NIGHTLY-STOP-1 applied as (b), OLLAMA-CAP-1 applied as (a), GUARD-SETS-1
  whole, W1-01-EXEMPT-1 and D8 refused at G6 as (O)); the 7 faults as before (an edit after review refused at G4, a
  wrong class claim refused at G6, an unlisted file touched refused at G8, a red check undone, a failing undo lock held,
  a missing yes and a yes for an older sha refused at G6). The live files, hashed before and after the run, equal:

| Path | Files | Before | After |
|---|---|---|---|
| live repository: .claude/hooks/** | 6 | 8d775c6a79680b1086e66fda5b17a5b737997c4cbea8c2ee76b06e684a5dbb06 | 8d775c6a79680b1086e66fda5b17a5b737997c4cbea8c2ee76b06e684a5dbb06 |
| live repository: .claude/settings*.json | 2 | 1730c3f7c9ca19acabb591726c994d889e12b6852e9148d097572662721af9b9 | 1730c3f7c9ca19acabb591726c994d889e12b6852e9148d097572662721af9b9 |
| live repository: the rest of .claude/** (agents, skills, commands) | 41 | fd9570353a05e66acdda70661a8ff4332a186f082b593f310402c0a9947aa0d7 | fd9570353a05e66acdda70661a8ff4332a186f082b593f310402c0a9947aa0d7 |
| live repository: .git/hooks/** | 15 | a3037550074b3cf21383ac235cff33081e0ef1e4da1d09bbc8efe18c9d0d7c9c | a3037550074b3cf21383ac235cff33081e0ef1e4da1d09bbc8efe18c9d0d7c9c |
| live repository: path map, test map, opt-in lists | 6 | de1deae14fc972c91fffb7be5c0db35c8b0a86918cb4c12ef00e785ed7cbf91a | de1deae14fc972c91fffb7be5c0db35c8b0a86918cb4c12ef00e785ed7cbf91a |
| live repository: deadman.py, sentinel-brief.md | 2 | d467b8db04823b8cefb018b391b2122db6df960ff42db021b3a13bf0a887492f | d467b8db04823b8cefb018b391b2122db6df960ff42db021b3a13bf0a887492f |
| the pin ~/.local/bin/gov | 1 | 20205dbcd3d368875c5ffdb9543efad210f35cfa482f90316147c301b17f4b46 | 20205dbcd3d368875c5ffdb9543efad210f35cfa482f90316147c301b17f4b46 |
| ~/gov-os-operator/ (every file) | 41 | 7b68bd2edda32656dbd12e809457d9652507e2f141391f4da59daea25b558ba7 | 7b68bd2edda32656dbd12e809457d9652507e2f141391f4da59daea25b558ba7 |
| ~/.claude/ (its configuration: settings, CLAUDE.md, hooks, agents, skills, commands, rules) | 233 | 83fd1a239de3116e38796b9e72d5ddb131df7dc7776632dc77d2b5f656bf1b20 | 83fd1a239de3116e38796b9e72d5ddb131df7dc7776632dc77d2b5f656bf1b20 |
| crontab -l (its output; exit 1) | 1 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |

Equal: **True**. The `~/.claude/` row differs from round 2's: that configuration changed between the two runs (not by
the trial); within this run before and after are equal.

### Round 3's notes for the narrow review

- **The rule reaches every live undo, not only the (a) after-check's.** The designer's revised S15 families include
  control files the live unlisted-file check catches first (the hook folder, `.git/config`), so the rule had to hold
  in the `unlisted` path too. A live unlisted file the apply wrote is now left as written (the lock held, the P1 naming
  it) instead of being restored; the touched files are still undone.
- **Ordinary work under the rule:** a control file Claude Code itself writes in the live tree during G8 (for example
  `.claude/settings.local.json` or `.claude/scheduled_tasks.lock`, both under `.claude/**`) is now a difference the
  agent leaves, so that run refuses at G8 and holds the lock until the owner clears it. That is DEC-1106's rule as
  written; whether such files leave the control list is a question for ACT-OPERATOR-1.
- **The journal's freeze:** the journal's undo after a dead session removes that session's freeze only when its text
  is still the token the journal recorded; a journal from before round 3 has no token, so its freeze stays and holds
  G9 until removed by hand.

## F21 (DEC-1107): the owner's undo and the recovery leaving another's file say "refused" (2026-11-09)

The narrow DEC-1106 review left F21: with files left, the owner's undo step returned `result: "undone"` with exit 0 and
the journal's recovery `undone` (exit 1). The owner's DEC-1107 fixed it in one tiny round. Code commit on
`w2/W2-148-f21`: `0e43fac2ebd7` (`operator_run.py`: `undo_step`, `recover`); unit cases in
`tests/unit/operator/test_w2_148_f21.py` (9 new).

| Point | The change | Unit cases |
|---|---|---|
| The owner's undo leaving a file (`undo_step`) | With `st.left` not empty after `undo_live` (the restore rule, unchanged): `result` `refused`, `gate` `undo`, exit 1; `undo: "done"`, `left`, `lock: true`; the lock written; the log line `refused` with `undo: "done"` and `left`; the P1 (kind `undo`) says "refused" and names each file. The ACT's own touched files at their after-copy are undone as before; the undo commit holds only them | `test_the_owners_undo_leaving_a_foreign_file_says_refused_and_exits_non_zero` (the frozen `apply.sh undo` writes an unlisted control file live; the next run refused at the lock) |
| The owner's undo with a touched file at third bytes | The up-front "moved since the apply" refusal no longer applies when some touched file is at third bytes: `undo_live` runs (no `apply.sh`; each own file at its after-copy put back from the frozen `before/` copy; the third-bytes file left as written), then the row above. With no file at third bytes, a touched file not at its after-copy (back at its before-copy) still refuses up front, nothing written | `test_the_owners_undo_with_a_touched_file_at_third_bytes_undoes_its_own_and_says_refused` (the undo commit holds only its own file), `test_the_owners_undo_with_a_touched_file_back_at_its_before_copy_refuses_up_front` |
| A second undo after the lock is cleared | "already undone" now also counts a later line for the same ACT and sha with `undo: "done"` (the refused-with-left line), so a cleared lock does not let the undo run twice | `test_the_owners_undo_after_the_lock_is_cleared_is_already_undone` |
| The recovery leaving a file (`recover`) | With `st.left`: `result` `refused`, `gate` `journal`, exit 1, `undo: "done"`, `left`, `lock: true`; the P1 (kind `recovered`) says "refused" and names each file. The launcher already passes a non-zero recovery's result through as its own, so no object on its stdout carries `undone` | `test_the_recovery_leaving_a_touched_file_at_third_bytes_says_refused_on_the_launchers_stdout`, `test_the_recovery_leaving_a_foreign_file_says_refused_through_the_recover_step` |
| Unchanged | With nothing left: the owner's undo `undone`, exit 0; the recovery `undone` (the launcher's `recovered.result`). An undo after the next ACT on the same files stays a plain refusal. The run path's undo (`UndoState.fail`) is not changed | `test_the_owners_undo_with_nothing_left_still_says_undone_with_exit_0`, `test_the_recovery_with_nothing_left_still_says_undone`, `test_the_owners_undo_after_the_next_act_on_the_same_files_stays_a_plain_refusal` |

### F21's runs

- **Unit tests:** 184 passed (`tests/unit/operator/`: round 3's 175 plus 9 in `test_w2_148_f21.py`), with
  `-m "not local_only" -k "not real and not green_here and not time_limit"` (the exclusion left nothing out).
- **`gov accept W2-148`:** pass, 169 passed, 0 failed, 0 skipped, 0 unmapped; all 39 lines pass (success-22 10,
  failure-15 9).
- **The trial (S23)** was not re-run: the change touches only the owner's undo and the recovery, which the trial does
  not reach.

