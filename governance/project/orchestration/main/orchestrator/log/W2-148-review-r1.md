The review is done. **W2-148 is not READY: two findings block** (in scope, ordinary work, fail open):

- **F1:** the classifier's script scan misses `sudo`, `git push`, `git tag`, installs, network calls and `rm ~` whenever they follow `then`, `do`, `else`, `{` or `!`.
- **F2:** the G8 dry run can apply an ACT to the live tree when `apply.sh` names the live repository by path, then refuses and leaves the change in place, with no undo.

Both have small fixes, so this is one fix round. The other 22 KPI lines pass. Twelve more findings are recorded as non-blocking rows. All the tests pass: unit 108/108 and acceptance 156 here plus 1 deselected, which the CTO's own run covered (157/157).

task: W2-148 (DAEO-xafn), independent review round 1 of the operator agent; branch `w2/W2-148` at head `45dd9e2dc` against `w2/integrate`; profile FULL.

status: DONE. The verdict is not READY: F1 (S6) and F2 (S12) are in scope, reachable in ordinary work, and fail open.

work_completed:
- **Sandbox check (Step 0), first:**
  - (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-W2-148','w').write('x')"` failed: `OSError: [Errno 30] Read-only file system`. Correct.
  - (b) `echo sandbox-trial | git hash-object -w --stdin` worked (gave `1ae28402a109…`), and `git update-index --refresh` worked (rc 0). Correct.
- **`ps` check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` printed nothing.
- **What I read:**
  - The ticket in full, including the CTO's settled readings.
  - OPERATOR-AGENT-1 §1 to §8 and JUDGEMENT.md.
  - Every file under `governance/project/operator/`.
  - The README interface, the evidence record and LAUNCH-SPEC §3 and S9/S10.
  - Around the code: `deadman.py`, `landing_select.sh`, `close_queue.sh`, `nightly.sh`, the path map and the prompt's freeze rule.
- **What I ran:**
  - A probe of the script scan.
  - The unit tests and the acceptance cases, read-only.

files_changed: none. `git status` shows untracked `.bashrc`, `.profile`, `.gitconfig`, `.idea`, `.vscode` and similar at the worktree root. These are the sandbox's own mount placeholders, not files I wrote. The status at the start was clean outside the sandbox.

evidence:
- Unit tests: `heavy_slot.sh python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" tests/unit/operator` gave **108 passed**.
- Acceptance: the same command on `tests/acceptance/W2-148` gave **156 passed, 1 deselected**.
- Both ran with `HOME=<empty scratch>`, `PYTHONUSERBASE=/home/usain/.local` (so pytest is found while HOME stays empty) and `PYTHONPATH=<worktree>/src`.
- Scan probe (`scratchpad/probe_scan.py`, run with `python3 -I`): `then sudo`, `do git push`, `{ git tag v1; }`, `then rm -rf ~/.cache/old`, `do curl https://…`, `then pip install`, `! git push` and `else git push` all gave **no hit**. `sudo …`, `&& pip install`, `case … ) git push` and `$(sudo …)` gave hits. A manifest with an empty touched list and commands only gave (a).
- My temp folders: `rv-home` 4.0K, scratchpad 8.0K, `du -s --inodes` of TMPDIR 2030.

tests: The exclusion left out one acceptance case, `test_w2_148_launch.py::test_s18_settings_that_did_not_load_fail_the_canary_and_no_real_session_starts`. It was caught only because "real" is in its name; the CTO's `gov accept` ran it (157/157). The unit run lost nothing to the exclusion.

discoveries:
- **The guard keeps no call log.** No guard-wide log of the last 48 hours of calls exists (searched twice: `.claude/hooks`, `src/gov/guard`, the whole repository; only test stubs have a `calls.jsonl`). The engineer's replay therefore reads only the operator's own dry-run commands (F3).
- **`--test` pushes are real but labelled as tests.** `deadman.py --test` sends a real push, but it reads "TEST DEADMAN | … | no action needed" and is cut at 190 characters (`deadman.py:100-104`, `:209-210`) (F4).
- **G9 can hold for a close.** `close_queue.sh` writes `CLOSE-RUNNING` at `:17` and removes it at `:36`, `:38`, `:116`, `:120` and `:132`.
- **Absolute paths are the norm in past ACTs.** 50 of the 57 ACT files name `/home/usain/…` paths. Several start with `cd /home/usain/Dynamic-Agentic-Engineering-OS`: ACT-D4-RESTORE-1:54, ACT-SELECT-HOOK-1:52, ACT-GATE-CONFIG-1:71.
- **The trial's settings rows did not test the settings comparison.** ACT-PERMISSIONS-1/2, QUIET-DENY-1, STOP-WAITER-1 and PUSH-INPUT-1 came out (b) through "cannot be parsed: never (a)", not through the settings row's deny-list comparison. Not lower, but that comparison was not exercised on real settings files.

risks: Until F1 and F2 are fixed, the code's vote can miss a `sudo`, push or tag hit, and a dry run can change live files. The other two votes (the CTO's claim and the reviewer's class) still stand between those gaps and the apply.

lessons: A shell scan built on tokens has to strip reserved words (`then`, `do`, `else`, `{`, `!`) the way it strips `env` and `nohup`. A dry run in a clone is only as isolated as the script's paths, so it needs a live-hash check afterwards.

proposed_decisions:
- **Under DEC-105 (three options, for the CTO/owner):**
  - **F7:** §1 lists `apply.sh apply|undo` and `git add`/`commit` as forms the session may run, yet also says the session can never go past a gate. Recommend removing those forms (apply now; cost: a few lines in the hook and settings).
  - **F3:** the replay's call source is not settled. Recommend the CTO names a source in ACT-OPERATOR-1, or the owner defers the replay (defer).

unresolved:
- None for this review.
- The live canary, the flags `--permission-prompts none`, `--disable-slash-commands` and `--tools`, and a full live run under the Bash tool's timeout (F6) are first exercised by ACT-OPERATOR-1's rehearsal.

recommended_next_action:
- **The engineer, round 2:**
  - Fix F1: in `act_class.strip_wrappers`, step over `if`, `then`, `else`, `elif`, `do`, `while`, `until`, `{`, `}`, `!`, and add the probe's cases as unit tests.
  - Fix F2:
    - At G1 or G8, refuse an `apply.sh`, command or check that names the live repository path or the real HOME literally.
    - After the dry run, re-hash the live touched files and the control files; on any change, refuse, restore from the frozen `before/` copies and push a P1.
    - Add the path rule to the reviewer brief's check 1.
  - Optionally ride along: F8, F9, F14.
- **The CTO:** run the trial outside the sandbox. It is safe: every location is planted (`test_w2_148_trial.py:262-265`), a crontab stub comes first on PATH (`:255-269`), GOV_* is stripped and push is a stub. Run it exactly as the record states. Settle F3, F4, F5 and F6 in ACT-OPERATOR-1.

**Verdict per line:**
- **Pass:** S1, S2, S3, S4, S5, S7, S8, S9, S10, S11, S13, S14, S15, S16, S17, S18, S19, S20, S21, S22, S23, S24.
- **Fail:** S6 (F1) and S12 (F2).

**The engineer's readings, judged:**
- **An empty touched list classifies as (a).** Partly fails open, so a row (F14). The dry run refuses any change in the clone, the planted HOME or the crontab stub. What still reaches the apply as (a) is a commands-only ACT whose effect leaves no file there: a local-server download such as `/api/pull`, a service step, or an absolute path (F2).
- **`push_cmd` defaults to `deadman.py --channel push --test`.** The notice does reach the owner, but labelled as a test and cut short (F4: in scope, other).
- **`close_flag` defaults to `<scratch>/CLOSE-RUNNING`.** `close_queue.sh` writes it, so G9 does hold for a close. The nightly hold is by window only; the `NIGHTLY-RUNNING` flag is not read (F12, row).
- **The launcher holds while G9 would hold:** correct (`operator_launch.py:255-257`).
- **Refusals from G7 on are pushed:** correct (`opcommon.AFTER_G7`; `operator_run.py:1410-1417`), except a bare exception (F10).
- **(b) apply notices always pushed:** fine; more notices, not fewer.
- **A transcript line without `origin.kind` is never a yes:** correct (`opcommon.py:343-345`).

**Findings**

- **F1 (S6), scope: in.** The script scan (`act_class.py:233-279`, `segments` and `strip_wrappers`) treats a shell reserved word as the command name. A `sudo`, `git push`, `git tag`, install, network call or `rm` outside the project after `then`, `do`, `else`, `elif`, `{` or `!` raises nothing. Confirmed by the probe.
  Ordinary work: yes, because one-line `for …; do …; done` and `if …; then …; fi` are an everyday shell form that past ACTs use (ACT-QUERY-CPUS-1:24, ACT-QUERY-GPU-2:43), and the code's vote exists to catch the CTO's misclassification.
  Consequence: fails open.

- **F2 (S12), scope: in.** G8 runs `apply.sh` with the clone as cwd and a planted HOME (`operator_run.py:491-507`), but nothing refuses or detects a script that reaches the live repository or the real HOME by absolute path. Such a script applies the ACT live during the "dry run". The changed-set check then refuses as "missing" (`:504-507`), and the live change stays with no undo, journal, commit or after-check. The P1 does not say live files changed.
  Ordinary work: yes, because 50 of the 57 past ACT files name `/home/usain/…` and several begin with `cd /home/usain/Dynamic-Agentic-Engineering-OS`, while neither brief tells the author or the reviewer that `apply.sh` must stay relative.
  Consequence: fails open.

- **F3 (S15), scope: in.** The guard replay reads `calls`, by default the operator's own dry-run commands (`opcommon.py:77`, `operator_run.py:530-536`). No guard-wide log of the last 48 hours of calls exists. A path-map or deny-list addition in (a) that refuses agents' ordinary calls is therefore never caught.
  Ordinary work: yes, because it applies to every path-map or deny-list (a) ACT.
  Consequence: other (agents get refused; nothing loosens).

- **F4 (S21), scope: in.** The default push goes through `deadman.py --test`. It reaches the phone as "TEST DEADMAN | {json…" cut at 190 characters, so only about 60 characters of the notice text survive. Each notice also writes a TEST note into `deadman.log`. A P1 "lock held" can read like a test.
  Ordinary work: yes, because it applies to every notice.
  Consequence: other.

- **F5 (S13, S14), scope: in.**
  - The operator writes its commit freeze at `<operator root>/log/act-in-progress.txt`, which no CTO rule or tool reads; the prompt's freeze is the scratch's `log/act-in-progress.txt` (`w2-orchestrator.md:174`). So the CTO's commits are not frozen during an apply.
  - G9 and the launcher hold on the scratch file, which the prompt tells the CTO to write at hand-over and keep until the ACT is done. Queueing with that habit holds the launch indefinitely.
  Ordinary work: yes, because it is the CTO's standing rule.
  Consequence: other (the launch stalls, or a commit races the apply and the staged-list check refuses and undoes).

- **F6 (S17, S19), scope: in.** The session runs `operator_run.py` through Claude Code's Bash tool. Its timeout is 2 minutes by default and 10 at most; neither the brief nor the wall settings raise it. G8's clone and checks, plus each push (up to 300 s), exceed it, so the program is stopped mid-gate or mid-apply. The journal then undoes at the next launch, or the model reruns the command. Not exercised live; confirm in the rehearsal. A setting sized to `session_timeout_s` (for example `BASH_DEFAULT_TIMEOUT_MS` / `BASH_MAX_TIMEOUT_MS` in the wall's `env`) or a timeout named in the brief would fix it.
  Ordinary work: yes, because it is likely on every real run.
  Consequence: other.

- **F7 (S19), scope: in.** The wall hook and settings allow the session itself to run `bash <frozen>/apply.sh apply|undo` and `git add`/`commit` (`operator_wall_hook.py:98-133`, `settings.json.tmpl:7-10`), as §1 lists them. A session that leaves its brief could apply a frozen ACT after the program refused, for example at G6 for a missing yes. Nothing in the program ever asks it to run them (the "unless the program's output asks" in `brief.md:23` never occurs).
  Ordinary work: no, because the brief forbids it twice.
  Consequence: fails open. A Wave 3 row, and a DEC-105 note.

- **F8 (S1, S22), scope: in.** G1 removes and replaces an existing `acts/<id>-<sha12>/` before G5 runs (`operator_run.py:211-213`). If the bundle is edited and the request re-queued with the old sha (§6 row 1, "a fix it forgot to re-review"), the frozen copy of an already applied ACT is overwritten. That ACT's undo then refuses with "the frozen copy changed".
  Ordinary work: yes, because §6 itself names the stale re-queue.
  Consequence: other (the agent's undo is lost; a hand revert remains).

- **F9 (S4), scope: in.** The reviewer-is-not-the-author check is skipped when the manifest has no `author` (`operator_run.py:331-333`); `validate_manifest` does not require the field.
  Ordinary work: no, because it needs both the field missing and the CTO reviewing its own ACT.
  Consequence: fails open.

- **F10 (S21), scope: in.** An exception after G7 is refused as gate "error" (`operator_run.py:1419-1422`). It is neither pushed nor counted as a missing notice in the digest.
  Ordinary work: no, because it needs an unexpected exception.
  Consequence: other.

- **F11 (S12, S15), scope: in.** `.git/config` and the rest of `.git/` outside `hooks/` lie outside G8's changed set, the live unlisted-file check and the control snapshot. An unlisted `git config core.hooksPath …` in an (a) ACT would get past the git-hooks control.
  Ordinary work: no, because both the CTO and the reviewer would have to miss an unlisted command.
  Consequence: fails open.

- **F12 (S13), scope: in.** The nightly hold is by window only (`03:50-08:00`); the `NIGHTLY-RUNNING` flag, which other tools read, is not consulted. A nightly that runs past 08:00 does not hold an ACT.
  Ordinary work: yes, because overruns happen.
  Consequence: other.

- **F13 (S10), scope: in.** `owner_text` does not exclude `isCompactSummary` lines. If a future format marked such a line human, a yes quoted in it would carry a fresh timestamp after the review.
  Ordinary work: no, because it depends on a format not seen today.
  Consequence: fails open.

- **F14 (S6), scope: in.** An empty touched list with commands classifies as (a) (`act_class.py:478`). A commands-only effect with no file trace, such as a model pull through the local server, reaches the apply as (a) rather than (b). Recommend: an empty touched list with any command is at least (b).
  Ordinary work: no, because every one of the 57 past ACTs lists its files.
  Consequence: fails open.

**S23, re-read on a sample.**
- No row is lower than a pinned table row.
- Unpinned rows cannot come out lower: they are (a) or "none".
- The six (a) rows are the servers' ACTs, (a) by Q3. Their only network calls are to 127.0.0.1 (checked against their ACT files).
- The listed rises are right, for example D4-RESTORE-1 (opt-in lines added: (b)) and QUERY-GPU-2 (`~/.local/bin/ollama`: install).
- F1 does not change the trial: the only past hits behind `do` are local `curl` calls.

**S16.** "Outside a ticket" matches `landing_select.sh:72-83` word for word: `Role: owner`, or no `Task: DAEO-*` other than `DAEO-sdxk`; a merge is judged by its own trailers.

```verdict
{"kpis": [
 {"kpi": "S1", "verdict": "pass", "findings": [{"id": "F8", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S2", "verdict": "pass", "findings": []},
 {"kpi": "S3", "verdict": "pass", "findings": []},
 {"kpi": "S4", "verdict": "pass", "findings": [{"id": "F9", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S5", "verdict": "pass", "findings": []},
 {"kpi": "S6", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F14", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S7", "verdict": "pass", "findings": []},
 {"kpi": "S8", "verdict": "pass", "findings": []},
 {"kpi": "S9", "verdict": "pass", "findings": []},
 {"kpi": "S10", "verdict": "pass", "findings": [{"id": "F13", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S11", "verdict": "pass", "findings": []},
 {"kpi": "S12", "verdict": "fail", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F11", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S13", "verdict": "pass", "findings": [{"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F12", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S14", "verdict": "pass", "findings": []},
 {"kpi": "S15", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S16", "verdict": "pass", "findings": []},
 {"kpi": "S17", "verdict": "pass", "findings": [{"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S18", "verdict": "pass", "findings": []},
 {"kpi": "S19", "verdict": "pass", "findings": [{"id": "F7", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S20", "verdict": "pass", "findings": []},
 {"kpi": "S21", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F10", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S22", "verdict": "pass", "findings": []},
 {"kpi": "S23", "verdict": "pass", "findings": []},
 {"kpi": "S24", "verdict": "pass", "findings": []}
]}
```