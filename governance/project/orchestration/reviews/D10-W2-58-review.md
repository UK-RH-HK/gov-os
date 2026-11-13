# D-10's red-fix list: the review of W2-58's live-session probe, round 1 (W2-141, DAEO-xwro)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-W2-58-review.md`; branch `w2/W2-58-d10-tests` at `9d99dbaca`; reviewer log `/home/usain/gov-os-worktrees/W2-58-d10-tests/.gov-runtime/scratch/lead/log/D10-W2-58-review.json`.
- verdict.py: READY. But the live run outside the sandbox failed at the CLI's permission layer; round 2: `briefs/D10-W2-58-probe-r2.md`.

The revision is sound and the verdict is **pass**. None of the four findings blocks, so `verdict.py` should compute READY. Nothing was written in any tree: `status --porcelain` is empty and HEAD is still `063660c57`.

**Sandbox check (Step 0):** passed.
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-xwro` failed with `OSError: [Errno 30] Read-only file system`.
- (b) `git hash-object -w --stdin` worked (`1ae28402a109…`) and `git update-index --refresh` exited 0.
- The session ran as `GOV_TICKET=DAEO-xwro`, `GOV_ROLE=independent-auditor`.

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing.

task: DAEO-xwro
decisions: DEC-820, DEC-826, DEC-953, DEC-954, DEC-110, DEC-580, DEC-1038, DEC-1040, DEC-1093, DEC-801, DEC-808, DEC-1010

- **task:** DAEO-xwro (W2-141), D-10's red-fix list: review of W2-58's live-probe revision `9ca161a6f..9d99dbaca`. The later merge `063660c57` changes nothing under W2-58.
- **status:** DONE
- **work_completed:**
  - Read the diff, the W2-58 support module, the kernel hook and both settings files, the launcher's guard-wiring check, the launch environment and the guard's read rules.
  - Reproduced discovery (2) with planted calls.
  - Answered checks 1–4 and classified four findings.
- **files_changed:** none.
- **evidence:**
  - File references are given per answer below.
  - Reproduction: 10 planted Bash calls through W2-58's own guard runner, in a fixture built in my TMPDIR, with this tree's `src`.
  - The folder used 1.1 MB and 261 inodes, and has been removed.
  - The tree's bytecode is dated 10:16 UTC, before my run, and `-B` stopped my run from writing any.
- **tests:** No pytest run; I did not repeat the designer's runs. The only run was the reproduction. No exclusion was needed because no suite ran, no session started and no model or embedder was used.
- **discoveries:**
  1. Discovery (2) also covers the heavy-slot gate (F3).
  2. The fixture's hook lacks the kernel's exit-code mapping (F1).
  3. Three commands failed once with a sandbox mount error (`bwrap: Can't get type of source …/.git/worktrees/W2-141-d10/commondir`, `…/.git/config.lock`). Each passed on retry. The sandbox mounts paths that other sessions create and remove.
  4. The Write tool needed a permission grant this session doesn't have (a harness prompt, not the guard). So I ran the reproduction as one `python3 -B -c` command in TMPDIR, not as a script file.
- **risks:**
  - The live run depends on Haiku copying a ~600-character line exactly. A miscopy gives a false red, not a false green.
  - The hook's Python gets only `PYTHONPATH` and `PYTHONDONTWRITEBYTECODE`. A runner whose packages come from `PYTHONUSERBASE` would see the hook refuse every call: a red, not a false green.
- **lessons:** Trace a probe's red from the hook's exit status before suspecting a guard rule. D10-REDS first suspected W2-141's S1/S2; the cause was the hook's environment.
- **proposed_decisions:** none.
- **unresolved:** the live run (the CTO's helper's, after this review).
- **recommended_next_action:** Run the live cases. Record F1–F4 as rows. For F2, add a correcting line to the D-10 record, since commits are not amended.

## Answers to the checks

**1. What each case measures is unchanged.** Yes.
- **Commands:** Every probe command is the same as in the script, with the same output file and the same `name=$?` line. `python3 -B` replaces the exported `PYTHONDONTWRITEBYTECODE=1`, which has the same effect for pytest and the import.
- **Assertions:** None changed: collect=0 with "2 tests collected" and both names; "1 failed, 1 passed" with the failing test's name and message; `value=2 added=True`; no ` D`/`D ` lines and refresh=0.
- **`results.txt`:** The test now creates it empty before the launch, so a session that never runs the line still fails with "did not run the probe to its end". `.gov-runtime/` is git-ignored in the fixture, so the scratch files cannot show in `git status`.
- **Prompt:** The one-try wording is kept, with "in a single Bash call, without changing a character" added.
- **Gained:** The guard now judges each command, not just `bash <script>`. The engineer's `python3 -B -m pytest <own folder>` passes as a test run because `-B` is an accepted interpreter flag (`src/gov/guard/reads.py:72,371-392`). So the live engineer case also covers the guard's half of "the engineer runs its tests".

**2. The hook fix is right.**
- **(a) Is it what the real kernel does?** Only partly, and the difference is the right one for a test.
  - The kernel also names its interpreter explicitly: the pinned one from the first line of `~/.local/bin/gov`.
  - But it runs that interpreter with `-E`, so `gov` comes from the pinned install. It also refuses on a missing pin, an interpreter that won't run, or any exit other than 0 or 2 (`template/governance/kernel/settings.json:13`, `.claude/settings.json:9`).
  - The fixture names the test runner's interpreter and this tree's `src`. That is the right stand-in for code that isn't installed, but it has no exit-code mapping (F1).
- **(b) Could it make the fixture's guard weaker?** Not in ordinary work.
  - It is this tree's `gov` run by the same interpreter, with the same `PYTHONPATH`, that the non-live cases use to run the guard (`w2_58_support.py:195-197,465-467`).
  - Without `-E`, nothing else can redirect it: the launched session's environment is a fixed list with no `PYTHONPATH` (`src/gov/launch/environ.py:3-7,18`). This also confirms the designer's trace.
  - The launcher still sees the guard wired: it looks for `hooks/pretooluse.py` with a matcher covering Write, Edit and Bash, and the matcher here is `*` (`launcher.py:263-306`).
- **(c) Does a hook that can't import `gov` still fail closed?** Yes.
  - The failed import exits 2 (`pretooluse.py:253-258,97-106`), the outer process passes the 2 through (`:443-457`), and the harness blocks on exit 2.
  - That is D-10's red itself.

**3. Discovery (2).** It is a false refusal that fails closed. It comes from how the guard is built, not from any intent: see F3. Scope: out.

**4. Trailers and paths.** All five trailers are present: Task: DAEO-xwro; Implements: DEC-1109, DEC-820; Role: independent-test-designer; Rewrite-Reason; and Co-Authored-By: Claude Opus 5.5. The Rewrite-Reason states the wrong cause (F2). Only `tests/acceptance/W2-58/README.md` and `test_w2_58_launched_sessions.py` changed.

## Findings

**F1: When the fixture's hook can't start, crashes outside its own error handling, or is killed, the live session's calls run unguarded.**
- The harness treats any exit other than 0 or 2 as non-blocking. The real kernel's command turns every such exit into a refusal; the fixture's command doesn't.
- If it happened, the live cases would still measure the sandbox but not the guard.
- Ordinary work: no, because the command names the interpreter running the tests, the hook turns its own failures (a failed import included) into exit 2, and its 20 s deadline (DEC-580) refuses before the harness's limit.
- Consequence: fails open
- Scope: in. A Wave 3 row. If the file is touched again, end the command with the kernel's mapping: `; r=$?; case $r in 0|2) exit $r;; esac; exit 2`.
- Reversed by: evidence that the harness blocks a PreToolUse call on any non-zero exit, or a live run where the fixture's hook fails to start in ordinary conditions.

**F2: The commit's Rewrite-Reason gives a cause that didn't happen.**
- It says "the guard refuses an opaque script for a session refused a part of the project (DEC-953 item 2)".
- Today's guard allows `bash .gov-runtime/scratch/w2-58/probe.sh` for both roles. That is the designer's own trace, and the code agrees: the guard judges only the script's path (`reads.py:1189-1208`), and its run-time rule covers only xargs pipes, `while read` loops and substitutions (`reads.py:1704-1756`).
- DEC-953 item 2 (amended by DEC-954) only keeps the guard's command forms in use (`DECISION_REGISTER.md:11881`).
- The real cause is the hook's missing `PYTHONPATH` (W2-56 S5, DEC-826 Q5). The README and docstring state it correctly; the code comment hedges with "may refuse".
- Ordinary work: yes, because the next lead or designer tracing W2-58 by its trailers is told the guard has a rule it doesn't have. A guard rule was already wrongly suspected once, in D10-REDS.
- Consequence: other
- Scope: in. Non-blocking; fix with a correcting line in the D-10 record.
- Reversed by: a guard call that refuses the old `bash <probe.sh>` form for either role in the fixture.

**F3: An engineer that runs its own acceptance tests through a shell is refused, with a reason telling it to "run them with pytest", which it was doing.**
- Reproduced in the fixture for the engineer:
  - allowed: `python3 -m pytest tests/acceptance/W2-95/ …`, and the same behind `timeout 600`;
  - refused: `bash -c '<that pytest>'`, and `bash …/heavy_slot.sh python3 -m pytest tests/acceptance/W2-95/ …`;
  - allowed: `bash …/heavy_slot.sh python3 -m pytest …` when it names no folder.
- The test designer was allowed all five forms.
- The heavy-slot form is the gate every test run must go through (DEC-1038 (4)).
- Cause, for the guard's owner: the guard treats bash's arguments as files bash opens, and exempts a test run only when the command itself is pytest (`reads.py:55-60,371-392,421,1329-1331,1479-1487`). It does not look inside a `bash -c` string (`protected.py:107-121`).
- DEC-820 (c) lets the engineer run its tests and see results, so this is a false refusal. The plain call or `gov accept <W2>` works around it (DEC-1040 item 3).
- Ordinary work: yes, because the briefs send every test run through `bash heavy_slot.sh <command>`.
- Consequence: other (fails closed)
- Scope: out. It is the guard's behaviour, not this revision; the probe uses the plain form, which passes. A row for the guard's re-pin list or Wave 3. Any fix must keep `bash -c 'cat <own test file>'` refused.
- Reversed by: a decision that a pytest handed to a shell is meant to be refused (then only the refusal's wording is wrong), or a guard run that allows the heavy-slot form.

**F4: The Task trailer names W2-141's ticket, which doesn't mention W2-58's tests.**
- DAEO-xwro's `allowed_paths` and notes say nothing of them. It has a "D-6 part 2 placed here" note but no D-10 note.
- The placement is traced only in D10-REDS (`D10-REDS.md:139-143`).
- Ordinary work: yes, because a reader following W2-58's history by trailer lands on a ticket about search refusals with no line explaining why.
- Consequence: other
- Scope: out. The ticket's notes are the CTO's to write.
- Reversed by: a note in DAEO-xwro or W2-58's ticket, or a decision placing the fix there.

Classification: F1 in · ordinary work no · fails open; F2 in · ordinary work yes · other; F3 out · ordinary work yes · other; F4 out · ordinary work yes · other. None is in scope, reachable in ordinary work and failing open or losing work, so none blocks and no round is proposed.

```verdict
{"kpis": [{"kpi": "w2-58-live-probe", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```

## Round 2

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-W2-58-review-r2.md`; at `bc765c646`; reviewer log `/home/usain/gov-os-worktrees/W2-58-d10-tests/.gov-runtime/scratch/lead/log/D10-W2-58-review-r2.json`. verdict.py: READY.

# Review of W2-58's live-session probe, round 2 (D-10; W2-141, DAEO-xwro)

**Verdict: pass.** F1 and F2 from round 1 are closed. The new fail-closed wrapper never turns a real allow into a refusal. What each live case measures is the same as before D-10. The trailers and paths are correct. The only new finding, F1, is out of scope and does not block, so `verdict.py` should compute READY.

**Sandbox check (Step 0): passed.**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-141` failed with `OSError: [Errno 30] Read-only file system`, and the file does not exist.
- (b) `echo sandbox-trial | git hash-object -w --stdin` worked (`1ae28402a109…`, the same blob round 1 wrote) and `git update-index --refresh` exited 0.
- The session ran as `GOV_TICKET=DAEO-xwro`, `GOV_ROLE=independent-auditor`.

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing.

task: DAEO-xwro
decisions: DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-1073, DEC-820, DEC-826, DEC-877, DEC-580, DEC-1040, DEC-1080

- **task:** DAEO-xwro (W2-141), D-10's red-fix list. This is the round 2 review of W2-58's live-session probe at `bc765c646`, compared with `9ca161a6f`, the last commit before D-10.
- **status:** DONE
- **work_completed:**
  - Read the round 2 diff, the full diff against `9ca161a6f`, the fixture builder in `w2_58_support.py`, the guard's exit paths, the kernel's hook command, the launcher's check that the guard is wired, the decisions the trailer cites, the D-10 record and DAEO-xwro's ticket.
  - Ran one small reproduction of the wrapper, with a stand-in guard.
- **files_changed:** none. `git status --porcelain` is empty and HEAD is still `bc765c646`.
- **evidence:**
  - File references are given in the answers below.
  - The reproduction took the hook command the test module itself produces (`live_guard_command()`, imported read-only with `python3 -B`). It ran that command under `/bin/sh` (dash) and `/bin/bash`, against a stand-in guard placed in a fixture folder in my TMPDIR, 13 runs in all.
  - My scratch folder used 20 KB and 5 inodes, and has been removed.
- **tests:** no pytest run.
  - The live cases need the network and run outside the sandbox. The CTO's helper's run (12 passed) was not repeated.
  - No exclusion flags applied because no suite ran, so nothing was left out.
  - No model, embedder or session was started.
- **discoveries:**
  1. With the wrapper in place, a live pass now proves the guard actually ran. Under round 1's bare command, a hook that could not start would have let the probe through unguarded, so a pass could not tell a guarded run from an unguarded one. Now that hook refuses, so the 12 passed show the guard ran and allowed `bash .gov-runtime/scratch/w2-58/probe.sh` for both roles.
  2. The D-10 record still gives the disproven cause for W2-58's red (F1).
  3. Saving the reproduction script with the Write tool needed a harness permission grant this session doesn't have. That is a false refusal from the harness, not the guard; round 1 hit the same thing. I worked round it with one `python3 -B -c` command that wrote only inside my TMPDIR (DEC-1040 item 3).
- **risks:**
  - The live cases still depend on Haiku running one short call and a `cat`. A miscopy or a refusal from the model gives a red, never a false green.
  - The hook names the test runner's own interpreter. If that interpreter cannot be run from the CLI's process, every call is refused with a reason: a red, not a false green.
- **lessons:** A fail-closed hook wrapper is also what makes a live pass count as evidence that the guard ran.
- **proposed_decisions:** none.
- **unresolved:**
  - F1's correcting line in the D-10 record (the CTO's).
  - Round 1's F3 and F4 rows are unchanged. DAEO-xwro's ticket still has no W2-58 or D-10 note.
- **recommended_next_action:** Merge per the computed verdict. Add F1's line to `D10-REDS.md`. Carry round 1's F3 and F4 as rows.

## Answers to the checks

**1. F1 and F2 are closed, and the wrapper cannot turn a real allow into a refusal in ordinary work.**

- **F1 is closed.** The fixture's command now ends with the kernel's own mapping, `r=$?; case $r in 0|2) exit $r;; esac; …; exit 2` (`template/governance/kernel/settings.json:13`). Before it, an `[ -x <interpreter> ]` check refuses with a reason. The reproduction gave the same results under dash and bash:

| What the stand-in guard did | What the hook returned |
|---|---|
| allowed (exit 0, no output) | exit 0; the 92 bytes of input reached the guard; `PYTHONPATH` was this tree's `src` |
| printed a deny decision as JSON, exit 0 | exit 0, with the JSON passed through unchanged |
| refused (exit 2 with a reason) | exit 2, keeping the guard's own reason |
| exit 1 | exit 2, "ended with exit 1 (it could not run or crashed); refused" |
| killed with SIGKILL | exit 2, "ended with exit 137 …; refused" |
| interpreter missing | exit 2, "no interpreter at …; refused" |
| hook file missing | Python's own exit 2 ("can't open file"), passed through as a refusal |

- **A real allow cannot become a refusal.**
  - The guard allows with exit 0, and the wrapper passes that through, along with any deny or ask decision it prints.
  - By construction the guard ends only with 0 or 2:
    - a failure inside it goes to `_fail`, which exits 2 (`pretooluse.py:97-106`);
    - its outer process turns any other status from the decision process into an error, then into `_fail` (`:443-447`, `:460-468`);
    - when the 20 s deadline (`DEADLINE_S = 20.0`, DEC-580) runs out, it prints a deny decision and exits 0, or exits 2 if even that fails (`:418-429`).
  - So the wrapper's extra refusals happen only when the interpreter cannot run (then no guard could run either) or when the exit is one a working guard never produces.
  - The `[ -x ]` check does not consume the guard's input. The live pass shows it passes in practice.
- **No false green.** The wrapper only adds refusals. The interpreter and `PYTHONPATH` are the same as round 1's, which round 1 reviewed.
- **The launcher still sees the guard wired.** Its check looks for `hooks/pretooluse.py` in the command, and the matcher is `*` (`launcher.py:259-273`). The fixture's settings carry nothing its other checks refuse (`:282-306`).
- **F2 is closed on the branch.**
  - The new Rewrite-Reason cites DEC-826 Q5 (the cleaned environment of a governed session) and DEC-877 item 4 (the launcher drops `PYTHONPATH`). Both say what the trailer claims and both are still in force: DEC-826 is ACCEPTED, and DEC-953 item 2 changes only the guard's rules, not Q5; DEC-877 is DONE.
  - None of the old cause remains: a search of W2-58's folder for `opaque|DEC-953|can place|hides its commands|script file|may refuse` finds nothing.
  - `9d99dbaca`'s trailer cannot be amended. The record it was meant to be corrected in still lacks the correcting line (F1, scope out).

**2. What each live case measures is unchanged from before D-10.** Yes.
- `_HEAD`, `_TAIL`, `ENGINEER_PROBE` and `TEST_DESIGNER_PROBE` show no diff against `9ca161a6f`.
- `PROMPT` has the same value: `PROBE_CALL` and `OUT` expand back to the old literal text.
- The five live tests and their assertions show no diff.
- `_start` writes `probe.sh` as before and no longer creates `results.txt` in advance, which is again the behaviour before D-10. A session that never runs the probe still fails with "did not run the probe to its end".
- The launch arguments are unchanged. The one difference, a missing space in `PROMPT,"--permission-mode"`, has no effect.
- The only net change is the fixture's committed hook command. `make_project` applies `extra` after the default settings, so the live command replaces the default (`w2_58_support.py:339-341`).
- The old default hook was a bare `python3 …/pretooluse.py` (`:230`, `:305-308`). It could not import `gov` under `gov launch`, so at `9ca161a6f` the live cases could never pass.
- Round 1's gain, where the guard judged each command of the probe, is gone again, as it was before D-10. The live cases measure the launcher's OS-level sandbox (KPI success 2), as designed.
- The non-live cases still use the default settings.
- The README's new claims hold:
  - W1-46, W1-50 and W2-54 do run `bash {SCRATCH}/probe.sh` (`test_w1_46_live_sessions.py:182`, `test_w1_50_freeze_launcher.py:213`, `test_w1_50_freeze_live_pause.py:97`, `test_w2_54_sandboxed_worker.py:154`).
  - The fixture's settings carry no permission rules.
  - The "permission layer" cause rests on the session's own words, as quoted in the probe brief. I found no committed log, but the claim fits the round 2 pass.

**3. Trailers and paths.** Correct.
- Git parses all five trailers in `bc765c646`, exactly as the probe brief prescribed: Task: DAEO-xwro; Implements: DEC-1109, DEC-820; Role: independent-test-designer; the corrected Rewrite-Reason; Co-Authored-By: Claude Opus 5.5.
- `bc765c646` and `9d99dbaca` each change only `tests/acceptance/W2-58/README.md` and `test_w2_58_launched_sessions.py`. The merge `063660c57` changes nothing under W2-58.
- The W1-46 and governance files in the diff against `9ca161a6f` came from `w2/integrate` through that merge.

**Probed and found sound, with no finding:**
- The command's escaping inside the JSON and its plain POSIX syntax, which dash accepts.
- The hook's input and `PYTHONPATH` reaching the guard.
- The README's map of test names, which is unchanged.
- One remaining gap, which this revision does not change and does not reach in ordinary work: a hook that outlives the CLI's own hook timeout is ended by the CLI, not by the wrapper. The kernel has the same gap, and the guard's 20 s deadline ends first.

## Findings

**F1: The D-10 record still gives the disproven cause for W2-58's red, and nowhere corrects round 1's wrong Rewrite-Reason.**
- **What was done:** `9d99dbaca`'s trailer named a guard rule against opaque scripts as the cause. Commits are not amended, so round 1's review recommended a correcting line in the D-10 record.
- **What happened:** `governance/project/orchestration/packages/LIFT-1/D10-REDS.md:139-143` still lists W2-58 as "to trace" and blames "Likely W2-141's S1/S2". Apart from round 1's review itself, which does record F2, no record in `governance/project/orchestration` names `9d99dbaca`.
- **What should have happened:** the record names the cause found (`gov launch` passes no `PYTHONPATH`, W2-56 S5, DEC-826 Q5), notes that the old trailer is wrong, and points to `bc765c646`.
- The branch itself is right: `bc765c646`'s trailer and every text in W2-58's folder give the correct cause.
- Ordinary work: yes, because a lead or designer tracing W2-58 through the D-10 record or `git log` meets the guard-rule cause first, and a guard rule was already wrongly suspected once.
- Consequence: other
- Scope: out. It concerns the CTO's record, not this revision. A row.
- Reversed by: a line in `D10-REDS.md`, or another D-10 record, that names the cause found and corrects `9d99dbaca`'s trailer; or a rule that such corrections land only in the close record.

No superseded or PROPOSED rule is in use: DEC-820, DEC-826 and DEC-1109 are ACCEPTED, and DEC-877 is DONE.

Classification: F1 out · ordinary work yes · other. No finding is in scope, reachable in ordinary work and failing open or losing work, so none blocks. This was round 2 of 2, and no further round is proposed.

```verdict
{"kpis": [{"kpi": "w2-58-live-probe", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
