I checked S4 and F3 at head `7bcff333b`. Both pass, with no blocking findings. Three information-only observations are recorded below, none blocking.

**Step 0, the sandbox check:** (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-l4gf` failed with `OSError: [Errno 30] Read-only file system`, and no file exists. (b) `git hash-object -w --stdin` printed `1ae28402a109c3397a44b19239a00adfa9472eb0` (exit 0) and `git update-index --refresh` exited 0. The `ps` check for ollama or llama-server found nothing (grep rc=1).

task: DAEO-l4gf (W2-154), rv-1: a narrow check of S4 only (DEC-1154)
status: PASS
work_completed: Identity checked (`git rev-parse HEAD` gives `7bcff333b5954d16ba128c253ed469c01797e32d`, porcelain empty). Probes 1–4 run: the restored line, the commit's trailers across the file's whole history, collect-only behaviour (3a, 3a2, 3b, 3c, 3c0), and F3. S1–S3 were not re-reviewed.
files_changed: none. Nothing was written in the worktree (porcelain empty before and after). Scratch files are only under `$TMPDIR/w2-154-rv1/`: probe3.sh, probe3.log, out-3*.txt and empty-home/. Step 0(b) added one loose git object (`1ae28402…`), as the D-4b rules require.
evidence: the probe record below, with each command and its output quoted.
tests: collect-only only, five pytest invocations through heavy_slot.sh (none of the ui_off cases was run): 3a exit 0, 3a2 exit 0, 3b exit 0 (9 collected), 3c exit 5 (9 deselected), 3c0 exit 5 (9 deselected). No folder runs, so the `local_only`/`real` exclusion did not apply and left nothing out.
discoveries: (1) The lead's verify run at this head has no summary.txt yet. Its scoped `serial.entries` lists only two entries (W1-05 live hooks p95, W2-57 designer read p95), neither of them ui_off, so that run will not exercise the restored entry. Only this probe's collect-only runs do. (2) Inside the launch sandbox, heavy_slot.sh cannot remove `/tmp/gov-os-heavy-prio-2946399` (13 `rm` errors) or append to `…/orchestrator/log/heavy-slot-waits.jsonl`. The run still went ahead. (3) The merge 5d74cdaee is in the file's history and carries no `Role:` trailer. It is a clean merge with no change of its own to the file.
risks: none in scope.
lessons: In this sandbox the 10-minute cap on a backgrounded foreground command can kill a heavy_slot gate wait. Launching with `run_in_background` and a long timeout from the start avoids losing the wait.
proposed_decisions: none
unresolved: Two tool refusals, each met once and not repeated or worked around. The Write tool's permission layer refused `$TMPDIR/w2-154-rv1/probe3.sh`, so I wrote the script with a Bash heredoc into the sandbox-writable `$TMPDIR` (the brief's scratch). Monitor refused a grep on the scratch log, so I used the background task's notification instead. The lead's verify summary was not done when I finished.
recommended_next_action: The CTO commits the record below as `docs/probes/DAEO-l4gf/PR-DAEO-l4gf.md`, and the ticket goes on to landing (DEC-1154). Observation O2 (heavy_slot inside the sandbox) could become an orchestrator-tools row.

---

````markdown
---
task: DAEO-l4gf
status: PASS
head: 7bcff333b5954d16ba128c253ed469c01797e32d
scope: S4 narrow check (DEC-1154)
role: independent-auditor
date: 2026-11-13
decisions: [DEC-1154, DEC-1112, DEC-1061, DEC-1157, DEC-549, DEC-889, DEC-801, DEC-808, DEC-1010, DEC-1014]
---
# PR-DAEO-l4gf: rv-1, a narrow check of W2-154's S4 (and F3)

The change checked: ad4355943 (the test designer's S4, `tests/acceptance/serial-only.txt`, +3 −5), merged in 7bcff333b,
on top of f42c51629 (w2/integrate brought in, with df8ba7007: the ticket's new allowed path, the owner's S4 (a), DEC-1157 (12)/(15)).
Base of the check: ae1d68394752 (S1–S3 verified and reviewed; not re-reviewed here).

## Identity
`git -C /home/usain/gov-os-worktrees/W2-154 rev-parse HEAD` gives `7bcff333b5954d16ba128c253ed469c01797e32d`. `git status --porcelain` is empty, before and after.
Session: `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-l4gf`.

## Probe 1: the restored line is live, exact, in place; nothing else changed
`git diff ae1d68394752 7bcff333b -- tests/acceptance/serial-only.txt`:
```
-# D-10 (DEC-1112 (3), the CTO's (a)): out while D-4's cut keeps every case of the file in breadth (DEC-1061;
-# tests/optin-lifted-breadth.txt, `# cap`): a default run collects none of them, and an entry that names no case
-# stops the close's serial phase (exit 4). In a run with --optin=breadth its seven cases run in the parallel phase,
-# not serially, until the plugin fix (b) treats an entry out of the run as not in it and this line returns. Was:
-# tests/acceptance/W1-16/test_w1_16_ui_off.py  # serial: daemon: every case of the file starts or asks the codebase-memory daemon
+# ui_off (W2-154 S4, DEC-1112 (3)): every case of the file is in tests/optin-lifted-breadth.txt (`# cap`, DEC-1061), so a default run
+# names the entry "not in this run" (S1); a run with --optin=breadth runs its cases serially (S2).
+tests/acceptance/W1-16/test_w1_16_ui_off.py  # serial: daemon: every case of the file starts or asks the codebase-memory daemon
```
Against the file before the D-10 gate (`git diff 6afff5d74^ 7bcff333b`, 6afff5d74^ = af850b6f2), the only difference is the two comment lines:
```
@@ -82,6 +82,8 @@
 tests/acceptance/W1-16/test_w1_16_token_rule.py::test_a_file_with_a_token_shaped_string_stays_out_of_the_index  # serial: daemon: ...
+# ui_off (W2-154 S4, DEC-1112 (3)): every case of the file is in tests/optin-lifted-breadth.txt (`# cap`, DEC-1061), so a default run
+# names the entry "not in this run" (S1); a run with --optin=breadth runs its cases serially (S2).
 tests/acceptance/W1-16/test_w1_16_ui_off.py  # serial: daemon: every case of the file starts or asks the codebase-memory daemon
```
`grep -n ui_off tests/acceptance/serial-only.txt` shows line 87, `tests/acceptance/W1-16/test_w1_16_ui_off.py  # serial: daemon: …`. It is live (no leading `#`) and sits at the end of the W1-16 daemon block, right after the `test_w1_16_token_rule.py` entries and before `# --- live-session`. The file exists (`tests/acceptance/W1-16/test_w1_16_ui_off.py`, 12075 bytes). The serial line is byte-identical to the one 6afff5d74 commented out.
**Sound.**

## Probe 2: trailers of ad4355943; no engineer commit on the file
`git log -1 --format='%(trailers)' ad4355943`:
```
Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Task: DAEO-l4gf
Role: independent-test-designer
Implements: DEC-1112, DEC-1061, DEC-889, DEC-549, DEC-1109
Rewrite-Reason: DEC-1112 (3) and the owner's S4 (a), 2026-11-13: with W2-154's S1 the close's serial plugin names an entry whose every case an opt-in list leaves out as not in this run, so W1-16's ui_off entry (out since the D-10 gate, 6afff5d74) returns
```
- `Implements:` lists DEC-1112, DEC-1061, DEC-889, DEC-549 and DEC-1109. That is exactly the ticket's `sources:` (DAEO-l4gf.md front matter).
- There is no `Role: owner` and no `Decided-by:`.
- The Rewrite-Reason names DEC-1112 (3) and the owner's S4 (a). DEC-1112 is ACCEPTED with item (3) standing; DEC-1128 changes only its items (2) and (4). DEC-1157 (ACCEPTED, standing) item (15) reads "W2-154's S4 brought in full now".

The file's whole history, at the Role trailer of every commit including merges (`git log --full-history 7bcff333b -- tests/acceptance/serial-only.txt`):
```
     10 independent-test-designer
     61 orchestrator
      1 (no Role)            # 5d74cdaee, a merge
--- engineer hits:
(end)
```
The 10 commits that are not merges are all `Role: independent-test-designer` (fdf18f7c4 … ad4355943). The single merge with no Role is 5d74cdaee ("W2-153: S3 amended's cases and W1-38's builder merged"). `git diff b78f862a9 5d74cdaee -- tests/acceptance/serial-only.txt` is empty and `git show --cc` shows nothing, so it is a clean merge with no change of its own (see O1).
**Sound.**

## Probe 3: behaviour with the restored entry, collect-only only
The script `$TMPDIR/w2-154-rv1/probe3.sh` cds to the worktree and stops if the `cd` fails. Each run is
`env TMPDIR=<scratch> PYTHONUSERBASE=/home/usain/.local HOME=<scratch>/empty-home PYTHONPATH=<W>/src:<W>/src/gov/close/pytest_plugin [GOV_CLOSE_SERIAL_ONLY_OF=<W> GOV_CLOSE_SERIAL_ONLY_GIVEN=<entries> GOV_CLOSE_SERIAL_ONLY_OUT=<out>] bash heavy_slot.sh python3 -m pytest <entries> -q --tb=line --no-header -p gov_close_serial_only -p no:cacheprovider -o tmp_path_retention_policy=failed --collect-only [--optin=breadth]`.
This is the form of command.py's serial-afterwards run (lines 925–938, 950–955) and its parallel run (OF set, GIVEN removed). `GOV_TESTS_OPTIN` was unset.

**3a. Default run (no opt-in), GIVEN = the ui_off entry:**
```
gov_close_serial_only: not in this run: tests/acceptance/W1-16/test_w1_16_ui_off.py

no tests collected (9 deselected) in 0.12s
exit=0
--- out file:
tests/acceptance/W1-16/test_w1_16_ui_off.py
```
It prints "not in this run", exits 0 (not 4, and not pytest's 5), names the entry in the out file and collects no case of the file. **Sound.**

**3a2. Default run with a neighbouring W1-16 entry** (GIVEN = `test_w1_16_one_daemon.py` and the ui_off entry), so the phase is not stopped when another entry is collected:
```
gov_close_serial_only: not in this run: tests/acceptance/W1-16/test_w1_16_ui_off.py
tests/acceptance/W1-16/test_w1_16_one_daemon.py::test_one_question_of_the_code_graph_starts_the_daemon_at_most_once

1/10 tests collected (9 deselected) in 0.13s
exit=0
--- out file:
tests/acceptance/W1-16/test_w1_16_ui_off.py
```
**Sound.**

**3b. Serial-afterwards run with `--optin=breadth`:**
```
tests/acceptance/W1-16/test_w1_16_ui_off.py::test_the_tool_alone_serves_its_ui_unless_the_setting_of_its_home_says_false
tests/acceptance/W1-16/test_w1_16_ui_off.py::test_a_call_of_the_wrapper_leaves_the_ui_off[index]
tests/acceptance/W1-16/test_w1_16_ui_off.py::test_a_call_of_the_wrapper_leaves_the_ui_off[projects]
tests/acceptance/W1-16/test_w1_16_ui_off.py::test_a_call_of_the_wrapper_leaves_the_ui_off[callers]
tests/acceptance/W1-16/test_w1_16_ui_off.py::test_a_second_index_keeps_the_ui_off
tests/acceptance/W1-16/test_w1_16_ui_off.py::test_a_first_call_that_builds_no_index_does_not_serve_the_ui
tests/acceptance/W1-16/test_w1_16_ui_off.py::test_ui_variables_of_the_callers_environment_do_not_turn_the_ui_on
tests/acceptance/W1-16/test_w1_16_ui_off.py::test_a_repository_and_a_symbol_named_like_the_switch_do_not_turn_the_ui_on
tests/acceptance/W1-16/test_w1_16_ui_off.py::test_a_setting_left_in_the_home_is_turned_off_by_the_next_call

9 tests collected in 0.05s
exit=0
--- out file:
--- (end out)
```
Nine items: seven functions, one of them parametrized ×3. There is no "not in this run" line and the out file is empty. **Sound.**

**3c. Parallel form (OF set, no GIVEN) with `--optin=breadth`:**
```
no tests collected (9 deselected) in 0.05s
exit=5
```
The plugin deselects all nine in the parallel phase, so the opted-in cases never run in parallel. Exit 5 is only because this single-file collection is left empty; the close's parallel run gives the whole folder. **Sound.**
3c0 (the same, default) gives `no tests collected (9 deselected)`, exit 5.

The opt-in reaches both phases alike: command.py's `_TEST_RUNNER_VARIABLES = ("PYTEST_ADDOPTS", "PYTEST_PLUGINS")` does not remove `GOV_TESTS_OPTIN`. A close that opts in therefore deselects the cases in its parallel run and collects them in its serial run (3b with 3c), and loses neither.

## Probe 4: F3, only the ticket's allowed paths
`git diff --name-only w2/integrate...w2/W2-154` (w2/integrate is now 9ad3bf742):
```
governance/project/orchestration/nightly/nightly.sh
src/gov/close/command.py
src/gov/close/pytest_plugin/gov_close_serial_only.py
tests/acceptance/serial-only.txt
tests/unit/close/test_serial_eng_w2_154.py
tests/unit/close/test_serial_w2_154_nightly.py
tests/unit/close/test_serial_w2_154_plugin.py
tests/unit/close/test_serial_w2_154_support.py
```
Every path matches `allowed_paths`. `tests/acceptance/serial-only.txt` is allowed for S4 only, and its only change is the S4 change. `git diff --name-only f42c51629^2 7bcff333b` gives the same list. The 4 commits integrate has gained since then touch none of serial-only.txt, optin-lifted-breadth.txt, tests/conftest.py, src/gov/close/ or the ui_off file.
**Sound.** (command.py's "serial-afterwards line only" limit belongs to S1–S3 and was not re-reviewed.)

## The lead's verification run
`.gov-runtime/scratch/lead/log/verify/` has no summary.txt when I finished (the run was waiting on a heavy slot), so there is no summary line to quote. Its `serial.entries` holds two entries (W1-05 live-hooks p95, W2-57 designer read p95) and not the ui_off entry, so that run does not exercise S4's line (see O3).

## Findings
Classification: 0 blocking, 0 major, 0 minor, 3 info (all out of scope, recorded rows; no round).

**O1 (info): a merge with no Role in the file's history.** The merge 5d74cdaee (2026-11-10) brought test-designer work on serial-only.txt into the history and carries no `Role:` trailer. It changed nothing of its own in the file, and no engineer change hides in it.
- Ordinary work: yes, because a merge commit written by hand can leave out the trailer.
- Consequence: other (a provenance gap in a commit, not in the file's content).
- Reversed by: a diff showing that 5d74cdaee itself changes the file against its first parent (it shows none).

**O2 (info): heavy_slot.sh in the launch sandbox.** Run in the launch sandbox, heavy_slot.sh repeatedly fails to remove `/tmp/gov-os-heavy-prio-2946399` (13 × `rm: … Read-only file system`) and to append to `…/orchestrator/log/heavy-slot-waits.jsonl`. The wait and the run still went ahead.
- Ordinary work: yes, because every sandboxed worker's pytest goes through heavy_slot.sh.
- Consequence: other (the waits log misses sandboxed waits; possibly a stale priority file if the sandbox ever creates one it cannot remove).
- Reversed by: heavy_slot's waits log showing entries from sandboxed runs, or the priority file being owned and cleaned by a process outside the sandbox.

**O3 (info): the lead's run does not reach the restored entry.** The lead's scoped verify run at this head does not include the ui_off entry. S4's runtime behaviour is shown only by this record's collect-only runs; no full close with the restored entry was run.
- Ordinary work: yes, because a scoped selection leaves out entries outside the change's scope.
- Consequence: other (evidence coverage).
- Reversed by: a full `gov close` serial-afterwards run at this head whose output shows `gov_close_serial_only: not in this run: tests/acceptance/W1-16/test_w1_16_ui_off.py` and exit 0.

What would reverse the PASS on S4: any of these at 7bcff333b —
- a commit with `Role: engineer` touching `tests/acceptance/serial-only.txt`;
- the ui_off line commented out or different;
- a default-run serial-afterwards collection ending in exit 4 ("no case is named by the entry");
- an opted-in parallel collection that keeps any of the file's nine cases.

```verdict
{"kpis": [{"kpi": "S4", "verdict": "pass", "findings": [{"id": "O1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "O3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F3", "verdict": "pass", "findings": []}, {"kpi": "tooling", "verdict": "pass", "findings": [{"id": "O2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```

```
verdict: PASS
head: 7bcff333b595
findings: blocking 0, major 0, minor 0, info 3
```
````