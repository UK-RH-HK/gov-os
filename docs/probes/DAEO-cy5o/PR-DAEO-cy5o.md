---
type: probe
task: DAEO-cy5o
reviewer_session: 666a6e88-5a6f-43a1-bbeb-20f8c77a4a11
implementer_session: 898cb9f9-4684-4006-8fa3-359d08239f96
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 6be837bbbe4158768ca88ae47972308386e008cf
---

# Probe record: DAEO-cy5o (W2-57), load out of the close: review 1 of the ticket's one declared round (DEC-916)

## The lead's note

- **Commissioned and judged** by the ticket lead (an orchestrator-role session in this ticket's worktree, DEC-137). The reviewer was a fresh `independent-auditor` session (`666a6e88-5a6f-43a1-bbeb-20f8c77a4a11`, 2026-10-27), started through `gov launch` under its OS sandbox with the reading tools alone (`Bash`, `Read`, `Grep`, `Glob`), at effort max. It wrote nothing: the lead's tripwire before and after its session shows no change in any tree.
- **What was probed:** the decided part of W2-57 at head `6be837bbbe41` (code head `0abd2dbd1796`): KPI 1 (the rulesync probe and its four effects) and KPI 2 (the doctor probes), by the engineer (`5ec92077f8fd`, `0abd2dbd1796`, session `898cb9f9-4684-4006-8fa3-359d08239f96`); the test designer's acceptance tests and revisions for KPI lines 1 to 7 (`f590aa5b2460`, `afe4b16b50f6`, `af09123932af`, `7161a1672604`, `68c2ab1f23f4`, `5b0d637e5dee`, `4fe257d59eb0`, `85087920aa72`, `9103c4c5cfbb`, `d835cf51bbea`, session `653d4474-228f-485a-9b72-d1e0b848d82e`). The route of `nightly:` entries out of the close's serial phase is not built: it needs `src/gov/close/command.py`, outside the ticket's paths (package P-W2-57-B1); its acceptance case stays red until then.
- **The lead's verification at `0abd2dbd1796`** (after a full rebuild, in the close's form): `gov check` exit 0 (15 GREEN, 2 YELLOW known before, no RED); the full parallel run 16,415 passed, 31 skipped, 10 failed (the pending route case; W2-66's known red, DEC-919; eight reds of the base that the orchestrator's own close of DAEO-uzme on `w2/integrate` refused on too: W1-01's `docs/source` deny cases ×4, W1-47's ×2, W1-06's registry entry, W1-49's precompact case without tk); the serial run 180 passed; W1-38's suite three times in the close's parallel form, 201 of 201 each time, 0 rulesync skips and 0 timeouts; `rulesync --version` sampled beside the parallel run at loads up to 68: at most 3.54 s, the whole check at most 7.33 s.
- **Verdict: pass.** The lead's judgement agrees with the reviewer's classification (DEC-809): no finding is "yes" with "fails open" or "loses work". F1 is no / fails open (a Wave 3 row, or a ride-along in the resume the ticket has anyway, DEC-802); F2 and F3 are yes / other; F4, O1 and O2 are yes / other.
- **Two notes on the reviewer's records findings.** F4: the edit of `tests/acceptance/W1-30/README.md` (only where it describes r11 and r13) was allowed in the lead's brief by the orchestrator's run brief for W2-57 (the README is also changed on `w2/W2-67`); it is recorded here as that allowance, not as a deviation. O1: `Implements: engineer` on the lead's checkpoint commit is the form the common lead brief prescribes for a lead's own commits (`Implements: {IMPL}`).

## The reviewer's record

Verdict: pass

**Head probed:** 6be837bbbe41 (code head 0abd2dbd1796), branch w2/W2-57.

**Step 0:** (a) the write outside the sandbox failed (read-only file system); (b) `git hash-object -w --stdin` wrote object 1ae28402a109 and `git update-index --refresh` exited 0.

**gov.__file__:** /home/usain/gov-os-worktrees/W2-57/src/gov/__init__.py

**Classification (DEC-809):** none of the 4 findings is both reachable in ordinary work and failing open or losing work. F1 fails open but not in ordinary work (row or ride-along). F2, F3 and F4 are ordinary work with consequence "other" (rows or ride-along). O1 and O2 are records observations, consequence "other".

### What I probed and found sound

**Part 1: the rulesync probe**
- **Late answers are waited for.** Each call's limit is now 25 s. A call answering after 15 s is waited for and the check compares as with a prompt answer. A real fault behind two late answers is still found by its own finding.
- **A generate that never answers** ends the check red, with "rulesync generate: no answer within 25 seconds" and no "absent" reading.
- **A slow rulesync cannot look absent.** The check reports rulesync absent only when `RULESYNC_BIN` names no file or the PATH holds none, and neither lookup runs the tool.
- **A check the runner cuts stays red.** I ran `gov check`'s own runner function with a declared limit of 3 s and a rulesync answering after 10 s. Result: RED, CHECK_FAILED "adapter-portability did not end within its time limit of 3 seconds". That text doesn't name rulesync, so W2-57's never-answering case would catch a check that didn't end by itself. Nothing in `src/` turns that red green or skipped, and `gov ci` refuses an absent tool.
- **The 9 revised W1-38 cases bite at the new limit.** With `--version` answering after 26 s (1 s past 25 s), all 9 failed.
- **W1-38's session fixture** skips only when `RULESYNC_BIN` names no file. A timeout, a start failure or a non-zero `--version` errors every dependent case.
- **`test_timeout_handling`** now execs its sleep, and passed with nothing left alive.
- **W1-33's helper** fails rather than skips on a timeout; the research case passed. W1-30's r15 probe also fails rather than skips, but see F2.
- **Builder unit case:** 94 passed.

**Part 2: the doctor probes**
- **Timed probes are bounded.** Version probes now get 30 s, the venv freeze 40 s, and all timed probes of one run share a 90 s budget. Three hanging tools ended doctor at 90.1 s, inside W1-07's 180 s wait.
- **The budget is reset each run.** It is set at the start of each run and cleared afterwards, and no threaded caller exists.
- **The budget never makes a silent tool read as answering.** It can make a tool that answers read as not answering, but only once the budget is spent:
  - for registry tools that fails closed, unless the binary's hash matches its pin (a stronger check);
  - for Claude Code it reads as a pass (F1).
- **The exception wrapper never yields ok true.** On the Latin-1 rename, `gov doctor --json` gave exit 1, ok false, DOCTOR_PART_FAILED, naming the part (path_compliance), the exception type and its text.
- **No part raises a GovError on purpose**, so the wrapper hides no deliberate code: index freshness and canaries catch their own errors, and the lock comparison returns a verdict.
- **`gov status` still reads it as not read.** On the same repository it gave exit 0, with the doctor part "read: false" and the reason "GovError: gov doctor's path_compliance part raised UnicodeDecodeError: …". That is the same not-read shape as before, with a clearer reason.

**Part 3: the test designer's batch A**
- W2-57's 13 cases are green; the red-to-green ones were red at the old limits, so the change is real.
- W1-38's revisions only add assertions, and its waits rise to 60, 180 and 180 s. The one wait that loosened, `test_timeout_handling` (15 → 180 s), is covered under `gov check` by W2-57's never-answering case and the builder case.
- W1-07's revision re-raises every assertion failure with the command's trimmed output; no expectation changed.

**Part 4: the test designer's batch B**
- **The list's form.** All 63 entries carry `<route>: <kind>: <reason>`. r11 and the list cases: 52 passed, and they aren't vacuous (W1-16 collects 161 marked cases).
- **W1-16's split is right.** The 19 functions moved to the parallel phase take only gitleaks, sandbox, tier and config fixtures and call W1-15's pre-index filter; none takes the codebase-memory fixture. The two unmarked cases that take the module fixture are static reads. No daemon case runs in parallel.
- **No live or real-model file is left in the parallel phase.**
- **Listing W2-58, W2-62, W2-54 and W1-21's family check now is safe in the meantime.** They move from the parallel phase into the single serial run, with the same environment and scope filter. The same cases run, alone instead of under load. The lead's serial run passed all 180, and the parallel skip count stayed at 31, so the interim skip guard reads the same.
- **r11 against its old version:** every old assertion is kept or made stricter. A new check requires each entry to name a collected case. The only removals are the decided ones: the read-merge case out, and W1-16's split.
- **r13:** the limit goes 5 → 30 s and the sleep 14 → 45 s, with the assertions unchanged. It passed alone in 48 s with nothing alive.
- **W1-46:** the `example.com` case is stricter (it now needs the proxy's CONNECT 403); the host cases' assertion is unchanged.
- **W1-50:** the two freeze cases drop every CLAUDE* variable, as DEC-784 requires.
- **Designer-read p95:** wall-time p95 under 100 ms, its world built under tmp_path.

**Scope**
- The engineer's commits touch only `src/gov/adapters/portability.py`, `src/gov/doctor/command.py`, `tests/unit/adapters/test_portability.py` and `docs/changes/W2-57-CIT-E.md`, all in `allowed_paths`. No acceptance test is touched.
- The test designer stayed within the named files except F4.

### Findings

**F1: doctor's shared probe budget can make claude_code pass without reading the version.** Severity: medium-low.
- **What was done:** I built a committed repository whose tool registry pins three tools by the sha256 of their binaries, each of whose `--version` never answers. A `claude` first on the PATH answers "2.0.0" at once, below doctor's minimum of 2.1.285. I ran `gov doctor --json` with this worktree's `src/`.
- **What happened:**
  - The three probes were each cut at 30 s and used up the 90 s budget. The tools part passed by hash.
  - The Claude Code probe got no time. The claude_code part reported "pass", with no CLI version and no issues.
  - Doctor exited 0 with ok true and healthy true, in 90.1 s.
  - The same repository with tools that answer at once: exit 3, DOCTOR_UNHEALTHY, claude_code "fail" ("CLI version 2.0.0 below minimum 2.1.285").
  - Before this change every probe had its own limit (Claude Code's was 3 s), so its version was always asked.
- **What should have happened:** a Claude Code version that was not read should not read as a pass. It should be unmeasured or a failure, or Claude Code's probe should not draw on a budget the tools part can spend.
- **Root cause:** the claude_code part already read "no version" as a pass, before this change, when it had 3 s. The new 30 s limit narrows that path; the shared budget opens a new way into it.

Ordinary work: no, because the timed probes of one run must add up to 90 s before the claude_code part. That means about 20 version probes averaging more than 4.5 s each, or three tools that hang, against at most 1.77 s per probe measured at a load of 48.
Consequence: fails open

**F2: W1-30's r15 rulesync policy-pair case accepts a rulesync timeout as its "red after the fault".** Severity: low.
- **What was done:** I put a stand-in rulesync first on the PATH: the installed one for its first two calls, then a `--version` that never answers. I ran `test_w1_30_r15_policy_pairs.py::test_a_registry_that_pins_another_rulesync_than_the_installed_one_turns_the_portability_check_red` with a plugin recording each `gov check` result.
- **What happened:** the case passed in 27 s. The run before the fault was GREEN. The run after it was RED only with "rulesync --version: no answer within 25 seconds; the generated files were not compared". The version was never compared, yet the case's "red or yellow after" assertion accepted it.
- **What should have happened:** like W1-38's 9 revised cases, the after-run's red should be held to its reason (the version finding naming 23.0.0), so a timeout fails the case.
- **Why it doesn't fail open:** W1-38's own version cases still catch a broken comparison. One requires both version numbers in the output. The other uses its own prompt stand-in, which a timeout cannot reach.
- **Scope:** the file is outside the test designer's named files (only W1-30's r11 and r13 are named).

Ordinary work: yes, because a rulesync call passing its limit under a close's load is the event this ticket addresses (two closes at 10 s), and the case then passes on that run without its comparison.
Consequence: other

**F3: W1-02's 5-second bound, now on CPU time, lets an idle wait of 5 to 18 s through.** Severity: low.
- **What was done:** I measured a hook-like child that waits 8 s without working, using W1-02's own CPU-time measure, result type and in-time assertion.
- **What happened:** wall time 8.00 s, CPU time 0.003 s. The assertion passed. Under the old 5 s wall bound (process limit 8 s) the same wait failed.
- **What still holds:**
  - A hang past 18 s still fails, below the guard's own 20 s deadline.
  - Each case still asserts the decision.
  - The serial p95 cases hold ordinary paths at 100 ms.
- **What should have happened:** this is within KPI 6's "a limit a loaded machine meets" for CPU-bound work, which is what those 168 inputs stress. But no case now holds an input-specific idle wait (a lock wait, a sleep in a retry) under 18 s for those inputs.

Ordinary work: yes, because an engineer can add an idle wait on a guard path in ordinary work.
Consequence: other

**F4: a test designer write outside the named files.** Severity: low (info).
- **What happened:** commit 4fe257d59eb0 changed `tests/acceptance/W1-30/README.md`. The ticket body names only W1-30's r11 and r13 files. It is prose only; no case or expectation changed.
- **What should have happened:** the README should be named in the ticket body, or the edit recorded as a deviation.

Ordinary work: yes, because a README beside a revised case is an ordinary companion edit.
Consequence: other

**O1: `Implements: engineer` on the lead's checkpoint commit.** Severity: info.
- **What happened:** commit 6be837bbbe41 carries `Implements: engineer`, a role name where a decision id is expected. Product traceability resolves `Implements:` items against record ids once a ticket is closed. I did not verify whether "engineer" resolves. W2-65's checkpoints carry the same trailer.
- **What should have happened:** a decision id, as the other leads' checkpoints carry.

Ordinary work: yes, because it is a trailer the lead writes on every checkpoint.
Consequence: other (at worst a red traceability family later, which fails closed)

**O2: W2-57's README overstates the interim savings.** Severity: info.
- **What happened:** the README states "about 303 s less in each close's serial phase" and "no paid session in a close". Both hold only once the route is built (P-W2-57-B1). Until then the newly listed live sessions run in the serial phase, so it gets longer.
- **What should have happened:** the README should say these savings start when the route lands.

Ordinary work: yes, because a reader plans close times from it.
Consequence: other

### Scratch, refusals, retrieval
- **Scratch:** 8 inodes / 24 KB before; 4,804 inodes / 27 MB at peak and at the end.
- **Refusals met: 2.**
  1. A Bash search of `docs/DECISION_REGISTER.md` with a long alternation was refused as more than the guard reads in bounded time (DEC-562). I searched the named file with the Grep tool instead.
  2. A Bash heredoc write to variable paths in my temp folder was refused ("/<guard-unresolvable>"). I wrote the same probe files with the Write tool at literal paths inside my temp folder.
  Neither call was refused twice.
- **`gov retrieve`:** used twice, for who may add list entries (DEC-862) and the routed cases. It returned FACET_UNAVAILABLE: lexical and semantic stores both "stale", because the head adds the lead's checkpoint after the rebuild and I may not rebuild. I read the named register sections instead.
- **Code-graph tool:** not used; I read the named files and scanned W1-16's test files' fixtures with a small parse.
