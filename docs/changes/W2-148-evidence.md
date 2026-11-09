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
| S15 control files for (a) | `after_checks`: the controls' bytes before and after; the guard replayed on the last 48 hours of calls on a clone (old and new lists); any other difference undoes at once (controls restored byte for byte) and pushes P1 | gov accept S15; unit `test_an_a_act_changing_a_control_file_live_is_undone`, `test_a_path_map_addition_*` |
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
| `push_cmd` | `python3 <repo>/governance/project/orchestration/tools/deadman.py --channel push --test` (the notice JSON appended) |
| `calls` | `<operator root>/log/calls.jsonl`: the call log the operator writes itself during its dry run (G8), one `{id, time, role: operator, ticket: <ACT>, event: {tool_name: Bash, tool_input: {command}, cwd: "."}}` line per command it runs there; the replay reads it |
| `close_flag` | `<scratch>/CLOSE-RUNNING` (close_queue.sh's lock) |
| `nightly_window` | `03:50-08:00` (the wake at 03:50, the nightly 04:00 to about 07:00, its check at 08:00) |
| `poll_s` | 60 |
| `freeze` | `<operator root>/log/act-in-progress.txt` (G9 also holds on `<scratch>/log/act-in-progress.txt`) |
| `approvals` | `<operator root>/log/act-approvals.jsonl` |
| others | `claude` (`claude`), `model` (`claude-sonnet-5-5`), `canary_model` (`claude-haiku-5-5`), `budget_usd` (1), `canary_budget_usd` (0.05), `session_timeout_s` (2700), `canary_timeout_s` (300), `check_timeout_s` (3600), `hold_max_s` (0: a hold waits as long as it lasts) |

The journal is `<operator root>/log/journal.json`; a failed undo holds `<operator root>/log/operator.lock`
(every run and launch refuses while it exists; the freeze stays too); the session's pid and pgid are in
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

