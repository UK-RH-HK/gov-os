task: DAEO-neam (W2-45), review round 2 (the last, DEC-1010), STANDARD, class C2; head `b13789476a9c`
status: DONE
work_completed: I checked the sandbox and identity, then read the ticket, the fix-round diff (round 1's head `0653dc01086e` to this head), the whole ticket change, both W2-45 unit files and the new acceptance files. For F1 I built the planted 20,000-commit, one-merge-in-six history (with the ticket's own builder) and an adversarial merge history, and ran the decision checker three ways: as shipped, with merges read as before the fix, and with no skipping at all. For F2/F3 I sent SIGINT, gave a huge limit, sent SIGTERM and ran `gov check` under GNU `timeout`. I planted two mutations on a `git archive` copy under my temp folder. I audited commits and paths.
files_changed: none
evidence:
- **Sandbox check:** (a) the write failed with `OSError: [Errno 30] Read-only file system` and no file was created. (b) `printenv` gave `independent-auditor` and `DAEO-neam`. The head was `b13789476a9c` at the start and at the end, and `git status --porcelain` was empty at the end.
- **F1 fixed, timing:** the planted history has 20,000 commits, 3,300 merges and 200 decisions.
  - `python3 -m gov.check.authority` took 16.2 s wall (load about 8 on 20 CPUs).
  - Through `gov check --json`, core-authority showed `elapsed_s` 16.344 next to `time_limit_s` 60, and the top-level `time_limit_s` was 60.
  - The checker itself took 15.9 s as shipped and 151.9 s with merges read as before the fix. Findings were identical.
- **F1 at scale with planted agent work:** I added an agent's ACTIVE decision on a side branch forked 4,000 commits back, an owner's decision beside it, and an agent's rewrite of DEC-007 merged late. As shipped 15.9 s, merges read 143.2 s. Findings were identical: `ACTIVE_UNAPPROVED DEC-900` and nothing else.
- **F1, no finding lost on adversarial merges:** a 50-commit history with 15 merges covering:
  - merges bringing the file from one side (owner and agent);
  - evil merges by an engineer and by the owner;
  - two `-s ours` merges;
  - empty-diff merges;
  - a move, a delete and a re-add on a side branch;
  - a criss-cross with 2 merge bases;
  - an octopus with 3 branches;
  - two commits naming one parent twice (written with `hash-object --literally`);
  - a non-UTF-8 path.

  All three modes gave identical findings (DEC-103, 104, 106, 107, 108, 110, 111, 114, 115, 116, 120 `ACTIVE_UNAPPROVED`). The commits naming a parent twice are left out of the skip list (47 of 50 listed), so they are read in full. The empty-diff merge gets one header and is listed with no paths, which is right because its tree equals both parents. The git output shows one header per parent for a merge, and `--no-renames` lists a move as a delete plus an add. A merge with no header is not listed, so it is read in full (fails safe).
- **F1, reasoning:** a merge is skipped only when the file is in none of its per-parent diffs. That is the same as `_merged`'s first case ("the file every parent holds"). A mode-only change is listed, so it is read and gives the same answer. The `.md` filter matches every path the walk can visit. So no merge is skipped that the merge rule (DEC-398, DEC-418) would have read differently.
- **F2 fixed:** SIGINT to `gov check` while the planted check runs: exit -2, a clean KeyboardInterrupt traceback, and the check's shell and grandchild are gone within 5 s.
- **F3 fixed:** `timeout-seconds: 3000000` gives exit 1 with the `OverflowError` traceback (row W2-L167). The group was stopped before the shell wrote its pids, and nothing was left.
- **Can the stop on the exception path hide the original error or signal outside the group?** `_stop` catches the lookup and permission errors, and its second `communicate` resumes cleanly; the original exception reached the caller in both probes. It signals only `killpg(process.pid)`, the check's own session.
- **New finding (N1), SIGTERM:** SIGTERM to `gov check` (exit -15) left the shell and grandchild running 5 s later. So did `timeout -s TERM 10 gov check` (exit 124). I stopped both by pid afterwards; none of my probe processes were left.
- **Mutations on a `git archive` copy:**
  - `--diff-merges=first-parent` (merges diffed only against the first parent): `test_w2_45_checker_speed.py` still gives 32 passed, yet on the adversarial history it loses DEC-107's `ACTIVE_UNAPPROVED`.
  - Control `--diff-merges=off`: 5 failed. This confirms the copy was the code under test.
- **Paths and roles:** the three-dot diff against w2/integrate stays inside allowed_paths plus tests/acceptance/W2-45/.
  - Engineer commits touch only src/ and tests/unit/check/.
  - Test-designer commits touch only tests/acceptance/ and the three widened files, each revision with its `Rewrite-Reason`.
  - Every commit carries `Task: DAEO-neam` and `Implements: DEC-729`; none carries `Role: owner` or `Decided-by:`.
  - The `commands.py` lines between the two heads come from the w2/integrate merge (W2-159), not from this ticket.
  - The W1-40 revision changes only the docstring (lines 46-47) and the assertion at line 49.
tests: I re-ran nothing the lead ran. Through heavy_slot I ran only `test_w2_45_checker_speed.py` against the two mutated copies (32 passed; 5 failed, 27 passed).
discoveries:
- `src/gov/check/authority.py` (outside the paths, unchanged since D-6) drops every `ACTIVE_UNAPPROVED` from the decision checker.
- It also drops any `GovError` the checker raises (`DECISIONS_GIT_FAILED`, `DECISIONS_OBJECT_UNREADABLE`) without a finding, so core-authority shows GREEN. On my planted history, core-authority was GREEN while the checker reported DEC-900.
- So a lost `ACTIVE_UNAPPROVED` could never show through `gov check`. The S1 merge guard case rightly calls the checker directly. Proposed as a row for the owner of authority.py.
risks:
- N1: since round 1's head the check runs in its own session, so stopping `gov check`'s process group no longer reaches it. On the base it ran in that group. This affects GNU `timeout`, a terminal hangup, and `gov.resources.slots._stop_group`, which stops a slot by its group with SIGTERM then SIGKILL; the check escapes such a stop.
- The S1 timings depend on machine load (16 s here at load 8; eng-3 measured 19-24 s at load 10-20).
lessons: I could only show a test gap on the merge skip by mutating the fix plausibly (first parent only) and checking it against the existing scenarios. A mutation that skips every merge is caught; the narrower one is not.
proposed_decisions: none. N1 is the owner's call: a row (consistent with F2 being rated minor), or a fix of about 10 lines (a SIGTERM/SIGHUP handler in `run_checks` that raises, so the existing exception path stops the group).
unresolved:
- The one-merge-in-three history (6,600 merges) was not measured. My probe builder script could not be written, see guard_refusals.
- S2-S4 and Interface item 8 were not re-run: the fix round does not touch them, round 1 found them met, and the lead's 38 acceptance tests pass. Nothing in the fix round makes F4-F6 worse.
recommended_next_action: I recommend landing on this verdict. Record N1 and N2 as rows, and add the authority.py discovery as a row for its owner.

Classification: 2 findings, both minor. N1 (S5): ordinary work yes, consequence other. N2 (S1): ordinary work no (test gap), consequence other. No finding is blocking or major, so the verdict is PASS.

- **N1.** Ordinary work: yes, because a `timeout` wrapper, a terminal hangup or a slot stop sends SIGTERM to `gov check`. Consequence: other. The check runs on as an orphan with no limit, but no result is reported, so nothing is reported green. Evidence that would reverse it: an owner ruling that a runner stopped from outside counts as "a check left running past its limit" would make it major; the fix is about 10 lines.
- **N2.** Ordinary work: no, because it is a test gap; the shipped code is correct. Consequence: other. Evidence that would reverse it: a test that fails under the first-parent mutation, such as an `-s ours` merge or a conflict resolved to main's side.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "N2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": [{"id": "N1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```

```
verdict: PASS
head: b13789476a9c
findings: 2
- N1 | minor | S5 | src/gov/check/runner.py:109-125 | gov check stopped by SIGTERM keeps no hold on its check: `timeout -s TERM 10 gov check` on a planted check `sleep 120 & …; wait` (or SIGTERM to gov check) ends gov check (124 / -15) and the check's shell and grandchild are still running 5 s later; they should be stopped as on SIGINT. The check's own session (Interface item 7) also takes it out of a group stop (timeout, terminal hangup, slots._stop_group) that reached it on the base. Sibling of F2; not made by the fix round.
- N2 | minor | S1 | tests/unit/check/test_w2_45_checker_speed.py:189 (SCENARIOS) | no case of a merge that leaves the decision's file as its first parent has it and differs from another parent (an -s ours merge, a conflict resolved to main's side): the mutation --diff-merges=first-parent passes all 32 unit cases (and the acceptance guards, which bring files from the side), yet loses ACTIVE_UNAPPROVED DEC-107 on such a merge. The shipped code (separate) is correct.
```
guard_refusals:
- 21:04 | Write tool to `/tmp/gov-launch-nh5aclf0/claude-1000/W2-45-rev2/probe/build.py`, the probe history builder | "requested permissions to write … you haven't granted it yet" | true. A permission prompt in a non-interactive session, not a hook. Not retried and not routed around; I used one-line probes with the ticket's own builder and git commands instead.