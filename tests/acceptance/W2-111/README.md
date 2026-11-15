# W2-111 (DAEO-qvff): the reopen's acceptance cases: the guard's 100 ms on Bash calls and with 150 or more trees

`Rewrite-Reason: DEC-1184 (3)` (new cases, the owner's reopen of W2-111 on 2026-11-14, Q-SCAN-2 (a); DEC-979, DEC-906,
DEC-968). Written by a fresh independent test designer from the reopen's KPI lines, before the change, without
reading the engineer's work (DEC-820, DEC-963). No earlier case is changed.

`Rewrite-Reason: DEC-1187` (new cases for S9 and S10, the owner's second reopen of 2026-11-15, P-W2-111-MARGIN (a);
the earlier cases unchanged; the figure table corrected as the r4c review found): see "S9 and S10 (DEC-1187)" below.

`Rewrite-Reason: DEC-1157 (12), P-W2-111-S9-DROP (a)` (brief td-5, 2026-11-15: S9 amended by the CTO; the live-hook
case's judgement loses the "at least 30 ms below the before figure" clause and records the drop instead; nothing else
changed): see "S9 and S10 on the live hook's patched copy" below.

`Rewrite-Reason: DEC-1156 (7), P-W2-111-R5-ROWS (a)` (brief td-7, 2026-11-15: rv-3's F2, the five timing files listed
`serial: latency` in `tests/acceptance/serial-only.txt`; and rv-3's F1 as a described behaviour, DEC-136, DEC-802, one
new case file; no earlier case changed): see "F1 (rv-3)" and "F2 (rv-3)" below.

**Which lines this folder judges.** `gov accept W2-111` runs this folder only. It judges the reopen's lines:
success-5 to success-10, failure-4 and failure-5. The earlier lines (success-1 to success-4, failure-1 to failure-3) are
judged on the 15 revised hook-latency cases in their own three files, `tests/acceptance/W1-02/test_w1_02_guard_hook.py`,
`tests/acceptance/W1-05/test_w1_05_live_hooks.py` and `tests/acceptance/W2-57/test_w2_57_designer_read_p95.py`
(DEC-892, the ticket's `acceptance_tests` comment), not here.

## The interface and the measure

Every case drives one public interface: **the product guard's PreToolUse hook**
(`template/governance/kernel/hooks/pretooluse.py`), installed in a planted project at `governance/kernel/hooks/` and run
the way W1-02's cases run it (`w1_02_support.run_hook`, imported, not copied): a process with the call on stdin, the
session's identity in `GOV_ROLE` and `GOV_TICKET`, a fresh environment with an empty temporary `HOME`, this worktree's
`src/` on `PYTHONPATH`, and **the session's own `PATH`, inherited** (as a real session's hook has it; never shortened).
Not the live hook (`.claude/hooks/pretooluse.py`): its figures are the live-hook ACT's.

The timing cases use W1-02's measure, unchanged (`test_w1_02_guard_hook.py::test_decision_p95_is_under_100_ms`,
DEC-979 item 1 D2, DEC-1163 (3)): per call, the CPU time (user and system) of the hook's process and every process it
waited for (`RUSAGE_CHILDREN` before and after the one call, `HookResult.cpu_seconds`), less the median CPU time of a
reference hook (a fresh interpreter that reads the event and answers) called just before each timed call in the same
round; 3 warm-up calls; rounds of 40 calls; the round's figure is the nearest-rank p95 of the 40 CPU times less the
median of the 40 reference CPU times; **the bound is 100 ms at p95**; a round that misses repeats, up to three rounds;
the case passes when a round is under the bound. Every timed call must also be decided as expected (allow), or the case
fails on the decision. Why the wall time under load is not the measure, and why a CPU time alone was not: W1-02's
README, section "W2-111", stands for these cases too. The reference hook's text is written in `w2_111_support.py`, the
same as W1-02's, rather than imported from that test file, so that these cases do not move if that file is revised.
Each timing case prints its figures (judged per round; raw CPU p95, reference median, wall p95 and the 1-minute load
per round; the PATH entry count; the tree count); `-s` or `-rA` shows them.

## The worlds

- **W1-02's fixture project** (`bash_world`): `w1_02_support.make_project` as it is, the engineer on its ticket
  `DAEO-zz90` (allowed `src/gov/guard/**`). No path map, no worktree.
- **The planted repository** (`trees_world`, built once per run, about 2 s): under pytest's temporary folder, a
  ten-file repository with the product hook, the kernel template's path map with one planted evaluation set
  (`w2-111-planted-set`: visible `eval/memory/visible/**`, hidden `eval/memory/hidden/**`, measures the role
  `engineer`), the engineer's ticket `DAEO-zz11` (`W2-911`, allowed `src/app/**`), and **150 worktrees registered**
  (`git worktree add --detach`, under `<home>/gov-os-worktrees/T001` to `T150`; 151 trees with the main tree). The hidden
  part is committed, so every tree holds it. An untracked link `peek` in the main tree points at the last-listed tree's
  hidden folder. The engineer's session runs in the main tree (one case runs a session in the last-listed tree). Nothing
  of the real project's evaluation sets is opened, listed or planted.
- **The planted 150 ms hook** (failure-5): the installed hook is replaced, for the case only, by a hook that busy-loops
  until its own `time.process_time()` reaches 0.150 s (CPU work, not a sleep) and then runs the product hook's copy
  beside it as `__main__`, so the decision is the product hook's and only the cost changes; the product hook is put back
  after the case.

## The map

| KPI | Test | Expected red reason before the change |
|---|---|---|
| success-5 | `test_w2_111_bash_p95.py::test_a_bash_call_with_a_role_set_is_decided_within_100_ms_at_p95` | the latency assertion (`p95 CPU time of the hook and its children per call, less the median CPU time of the reference hook ... the bound is 100 ms`): every round at or above 100 ms. See "Before the change": in this sandbox the red did not hold (`[plain]` red in run 1 only, by load; all green in run 2): an open question to the lead. |
| success-6 | `test_w2_111_many_trees_p95.py::test_a_call_with_150_worktrees_registered_is_decided_within_100_ms_at_p95` | the latency assertion, every round at or above 100 ms with 150 worktrees. See "Before the change": on the product hook these were green before the change (an open question to the lead). |
| success-7 | `test_w2_111_install_decisions.py::test_each_install_form_is_still_refused_with_a_role_set`, `test_w2_111_install_decisions.py::test_the_same_non_installs_are_still_allowed_with_a_role_set`, `test_w2_111_install_decisions.py::test_a_changed_PATH_is_read_again_within_one_session` | none: green before the change, by design; they pin today's answers. Red after it only if an install is allowed, a non-install refused, or a call answered by another call's PATH. |
| success-8, failure-4 | `test_w2_111_hidden_part_decisions.py::test_a_read_of_the_hidden_part_is_still_refused_with_150_worktrees`, `test_w2_111_hidden_part_decisions.py::test_a_read_outside_the_hidden_part_is_still_allowed_with_150_worktrees` | none: green before the change, by design (the fails-open check). Red after it only if a refusal turned into an allow, or an allow into a refusal. |
| failure-5 | `test_w2_111_slow_hook.py::test_the_planted_150_ms_hook_fails_each_new_timing_case`, `test_w2_111_live_hook_slow_hook.py::test_the_planted_150_ms_hook_fails_the_live_hook_case` | the first: none, green before and after the change; red only if a new timing case passes the planted 150 ms hook. The second (DEC-1187): red before the change because the after copy cannot be built: `the live hook's diff docs/changes/W2-111-live-hook/live-hook.diff is absent: S10's diff of .claude/hooks/ against the applied ACT-GUARD-FIX-6 bytes is not prepared`; after it, red only if the live-hook case's judgement passes the planted hook. |
| success-9 | `test_w2_111_yaml_count.py::test_a_call_refused_before_the_held_out_check_parses_no_yaml_file`, `test_w2_111_yaml_count.py::test_a_write_or_edit_of_any_role_parses_no_path_map`, `test_w2_111_yaml_count.py::test_each_yaml_file_a_call_opens_is_parsed_at_most_once`, `test_w2_111_yaml_count.py::test_a_broken_held_out_yaml_still_stops_every_call`, `test_w2_111_live_hook_diff_p95.py::test_the_live_hook_s_patched_copy_is_within_100_ms_of_the_applied_hook_the_drop_recorded`, `test_w2_111_yaml_parity.py::test_the_product_loader_answers_each_text_as_the_pure_safe_loader_does` | The count cases: **none, green before the change** (35 passed at `00c9327e0`): they pin behaviours 1, 2 and 3 and DEC-218; behaviour 3 was expected red and is not (see "Before the change, S9"). The live-hook case (S9 as amended, P-W2-111-S9-DROP (a): every mapped case within 100 ms at p95, quiet, paired; decisions unchanged; the drop recorded): `the live hook's diff docs/changes/W2-111-live-hook/live-hook.diff is absent: S10's diff of .claude/hooks/ against the applied ACT-GUARD-FIX-6 bytes is not prepared` (20 of 20). The product loader's parity (F1, rv-3): on the ticket branch before the fix, the class texts red, `<text> (<form>): gov.util.parts.load_yaml_unique read the text that the pure SafeLoader refuses`; on the tests branch green (its loader is the pure one): see "F1 (rv-3)". |
| success-10 | `test_w2_111_live_hook_diff_p95.py::test_the_live_hook_s_patched_copy_is_within_100_ms_of_the_applied_hook_the_drop_recorded` | the diff is absent (the same text, 20 of 20). |
| failure-4 | `test_w2_111_yaml_count.py::test_a_call_refused_before_the_held_out_check_parses_no_yaml_file`, `test_w2_111_yaml_count.py::test_a_write_or_edit_of_any_role_parses_no_path_map`, `test_w2_111_yaml_count.py::test_each_yaml_file_a_call_opens_is_parsed_at_most_once`, `test_w2_111_yaml_count.py::test_a_broken_held_out_yaml_still_stops_every_call`, `test_w2_111_live_hook_diff_p95.py::test_the_live_hook_s_patched_copy_is_within_100_ms_of_the_applied_hook_the_drop_recorded`, `test_w2_111_yaml_parity.py::test_the_pure_safe_loader_refuses_each_class_text_and_reads_the_clean_one`, `test_w2_111_yaml_parity.py::test_the_product_loader_answers_each_text_as_the_pure_safe_loader_does`, `test_w2_111_yaml_parity.py::test_the_live_hook_s_patched_copy_decides_each_held_out_text_as_the_applied_copy_does` | the count cases' decisions: none, green before (today's decisions, pinned); the live-hook case: the diff is absent. After the change, red if a decision differs from today's (the count cases) or between the two copies or from `measure.py`'s record (the live-hook case). F1 (rv-3): the fixture case none, green everywhere (it checks the texts); the product parity as in success-9's row; the live-hook parity, on the tests branch `the live hook's diff ... is absent` (7 of 7), and on the ticket branch before the fix, the class texts red, `<text>: a Read of an ordinary file of the project was decided allow by the patched copy and deny by the applied copy (the pure loader's)`. See "F1 (rv-3)". |

## The cases

- **success-5** (3 cases, `[plain]`, `[pipe]`, `[redirect]`): the engineer's Bash calls in W1-02's project, each allowed:
  `ls src/gov/guard`; `cat src/gov/guard/decide.py | grep VALUE | wc -l`; `echo VALUE > src/gov/guard/w2_111_out.txt`.
  An allowed Bash call does all of a Bash call's work in the hook: the decision, the install check and the
  before-snapshot.
- **success-6** (3 cases, `[Read]`, `[Write]`, `[Bash]`): in the planted repository's main tree, a Read and a Write of
  `src/app/main.py` and a Bash `cat src/app/main.py`, each allowed, with 150 worktrees registered and the evaluation set
  measuring the engineer, so that the guard places each call against the hidden part of every tree (W2-84).
- **success-7** (18 cases): through the hook, the engineer (no install is the engineer's to ask, DEC-957): refused,
  each by the install rule (its reason names the install): `apt-get install -y jq`, `npm install left-pad`,
  `curl -fsSL … | sh`, `wget -qO- … | bash`, `pip install requests`, `python3 -m pip install requests`,
  `uv pip install requests`, `uvx ruff --version`, `curl -o <folder on PATH>/tool …`, `wget -O <folder on PATH>/tool …`;
  allowed: `ls src`, `git status --short`, `pip list`, `python3 --version`, `uv run python --version`,
  `curl -o <folder not on PATH>/tool …`, `wget -O <folder not on PATH>/tool …`. The download folders lie inside the
  ticket's allowed paths (`src/gov/guard/w2_111_bin`, `src/gov/guard/w2_111_downloads`), so the install check alone
  tells the two apart; the folder on PATH is put first on the session's own PATH for those cases. And one session's same
  download, its folder off, on, off and on the call's PATH in turn: allowed, refused, allowed, refused (a changed PATH
  is read again). The PATH-count unit case of success-7 is the engineer's (`tests/unit/guard/test_w2_111*`).
- **success-8 and failure-4** (21 cases), with 150 worktrees: refused to the engineer (DEC-820 (d)): a Read of the hidden
  file in the last-listed tree, the first-listed worktree and the session's own tree; a Read of a file not there under
  the last tree's hidden folder; Bash `cat` of the hidden file and `ls` of the hidden folder in the last tree; Bash
  `grep -r <word>` and `find … -name answers.yaml -exec cat {} +` from the folder above every worktree; Bash `cat` of a
  shell glob over every worktree (`<above>/*/eval/memory/hidden/answers.yaml`); the Grep tool from the folder above,
  with and without a glob for the hidden files; a Read through the link `peek`; a Read of the main tree's hidden file
  from a session in the last-listed tree. Allowed: a Read of the visible file in the last tree and of a source file in
  the session's tree; Bash `cat` of `docs/notes.md` and `grep -r <word> docs` in the last tree; the Grep tool in the last
  tree's `docs`; a Read of the hidden file by a session no set measures; and a listing of names alone from the folder
  above (Bash `find <above>`, the Glob tool `**/hidden/*.yaml`), which opens no file and is allowed today (names may be
  seen, DEC-820), pinned so: a speed-up must not turn it into a refusal either.
- **failure-5** (6 cases): each of the six timing cases above measured with the planted 150 ms hook in its place; the
  case asserts the timing case would fail: all three rounds at or above 100 ms.

## Kinds, markers and the whole-folder run

The success-5, success-6 and failure-5 cases are **load-sensitive** (they assert a latency, by the hook's own CPU time
less a reference beside it, never the wall time); the success-7 and success-8 cases are acceptance cases. No case
carries a marker: none needs a real model, a dev tier or the network, so none is `local_only`; and no case name,
parameter id, file or folder name holds `real`, `green_here` or `time_limit`, so the whole-folder filter
(`-m "not local_only" -k "not real and not green_here and not time_limit"`) selects every case here, as it selects
W1-02's latency cases: the nightly runs them. No `skip`, `xfail` or `flaky` mark. Run times: see "Before the change".

## Before the change

Measured by the test designer on 2026-11-14, in its tests worktree at `d54654eab143` (the guard's code before the
change), in a launched session (`gov launch`, the OS sandbox), every run through the heavy slot. The session's own
PATH has **5 entries** (`~/.local/bin`, the node folder, `/usr/local/bin`, `/usr/bin`, `/bin`); a launched session's
PATH holds no Windows folder, while an interactive WSL shell of the owner appends the Windows PATH (`/mnt/c/...`,
`/etc/wsl.conf` does not turn that off). Machine: 20 logical CPUs. The load is the 1-minute load at each round's end;
the machine was shared with other sessions throughout (no quiet window was had). Cells in ms; a case that needed more
rounds shows each, separated by commas.

| case (parameter) | run | judged (p95 less reference) | raw CPU p95 | reference median | wall p95 | load | trees | verdict |
|---|---|---|---|---|---|---|---|---|
| Bash `[plain]` | 1 | 175.8, 150.1, 133.1 | 209.6, 183.1, 163.9 | 33.8, 33.0, 30.8 | 226.7, 190.9, 166.7 | 21.3, 24.9, 26.3 | 1 | red |
| Bash `[pipe]` | 1 | 117.6, 99.1 | 143.7, 124.6 | 26.1, 25.6 | 161.3, 135.1 | 26.3, 27.2 | 1 | green |
| Bash `[redirect]` | 1 | 92.3 | 114.9 | 22.7 | 111.4 | 26.3 | 1 | green |
| 150 trees `[Read]` | 1 | 82.3 | 102.8 | 20.5 | 99.7 | 24.7 | 151 | green |
| 150 trees `[Write]` | 1 | 41.3 | 61.8 | 20.5 | 60.4 | 24.7 | 151 | green |
| 150 trees `[Bash]` | 1 | 78.9 | 98.0 | 19.1 | 97.2 | 23.8 | 151 | green |
| Bash `[plain]` | 2 | 102.3, 67.0 | 123.9, 85.1 | 21.6, 18.1 | 118.8, 81.2 | 42.6, 43.2 | 1 | green |
| Bash `[pipe]` | 2 | 73.0 | 92.1 | 19.1 | 88.2 | 43.7 | 1 | green |
| Bash `[redirect]` | 2 | 72.6 | 91.3 | 18.7 | 87.7 | 42.6 | 1 | green |
| 150 trees `[Read]` | 2 | 67.8 | 86.2 | 18.4 | 83.4 | 40.9 | 151 | green |
| 150 trees `[Write]` | 2 | 42.9 | 60.8 | 17.8 | 59.3 | 41.7 | 151 | green |
| 150 trees `[Bash]` | 2 | 85.0 | 103.8 | 18.8 | 100.2 | 40.7 | 151 | green |
| planted 150 ms hook `[bash-plain]` | 2 | 227.2, 218.8, 222.9 | 245.5, 236.6, 240.8 | 18.3, 17.8, 17.9 | 237.2, 228.7, 233.8 | 38.4, 35.9, 32.5 | 1 | fails the bound (the planted case passes) |
| planted 150 ms hook `[bash-pipe]` | 2 | 215.0, 217.4, 212.8 | 232.7, 234.8, 229.3 | 17.6, 17.4, 16.6 | 225.6, 227.4, 222.3 | 30.5, 27.4, 25.7 | 1 | fails the bound |
| planted 150 ms hook `[bash-redirect]` | 2 | 213.8, 227.4, 227.1 | 231.6, 244.7, 244.7 | 17.8, 17.2, 17.6 | 223.9, 236.5, 236.7 | 23.3, 21.1, 19.0 | 1 | fails the bound |
| planted 150 ms hook `[trees-Read]` | 2 | 220.0, 220.2, 204.5 | 238.6, 237.1, 220.3 | 18.6, 16.8, 15.7 | 231.1, 230.4, 213.3 | 18.1, 17.2, 15.6 | 151 | fails the bound |
| planted 150 ms hook `[trees-Write]` | 2 | 182.4, 181.1, 182.7 | 197.9, 196.8, 198.3 | 15.5, 15.7, 15.5 | 191.8, 190.8, 192.1 | 14.0, 13.4, 12.1 | 151 | fails the bound |
| planted 150 ms hook `[trees-Bash]` | 2 | 221.7, 232.3, 232.6 | 238.1, 249.2, 249.4 | 16.5, 16.9, 16.9 | 230.3, 241.1, 241.1 | 11.0, 10.3, 9.4 | 151 | fails the bound |

Run 1 (2026-11-14 ~23:25, the timing files alone): 1 failed (`[plain]`, on the latency assertion), 5 passed. Run 2
(~23:50, the whole folder): **51 passed** in 204 s. The decision cases (success-7, success-8) were green in every run,
as designed. Run 3 (~23:58, the whole folder with the whole-folder filter `-m "not local_only" -k "not real and not
green_here and not time_limit"`: it selects all 51 cases): 51 passed in 215 s; judged figures at load 10 to 13: Bash
`[plain]` 117.5, 78.5; `[pipe]` 118.5, 103.8, 75.2; `[redirect]` 70.7; 150 trees `[Read]` 69.9, `[Write]` 38.9,
`[Bash]` 75.5. Per-test durations of run 2 (pytest's own): each planted-hook case 25 to 30 s (three rounds of 40 calls of
a 0.2 s hook; 172 s for the six); each timing case 3 to 9 s; each decision case under 0.4 s; building the planted
repository 1.5 s. The timing and planted-hook cases are past the 5 s default of their kind (load-sensitive): a timing
case takes one to three rounds of 40 calls, and a planted-hook case must take all three rounds to show the case fails;
that is W1-02's measure itself (its rounds and samples are not cut), so they are declared as the slower kind with that
reason.

**What this shows, and what it does not.** In this sandbox, before the change, the new timing cases were **not red for
the stated reason**:

- **success-5 (Bash).** Red once (`[plain]` in run 1, at load 21 to 26), green in run 2 at load 42 to 44. The red is
  the load's, not the install check's: with 5 PATH entries the install check costs about 0.2 ms in process (a scratch
  probe of the decision's steps, 2026-11-14: the imports about 28 ms, the decision 4 to 15 ms, the install check 0.2 ms,
  the before-snapshot 8 to 12 ms). The CTO's 52 ms for the install check was measured in a session whose PATH is not
  this one's (probably with the Windows folders appended); these cases inherit the PATH of whichever session runs them.
- **success-6 (150 trees).** Green in both runs. A scratch probe (one round each, load about 40) gave the product
  hook's Read 98 ms judged with no worktree and 111 ms with 150, and its Bash 184 ms and 113 ms (load noise larger than
  the trees' cost): the product hook's own cost of 150 trees is small. The CTO's 59 ms (listing 248 trees) and 47 ms
  (judging each tree) were measured on the live hook (`.claude/hooks/pretooluse.py`, its own tree code), whose figures
  are the live-hook ACT's, not these cases'.

Neither was forced red: no PATH was shortened or lengthened, no tree added past the line's 150, the bound not lowered.
The question goes to the lead (the test designer's return, `unresolved`). The lead adds the after figures and the
loaded runs' figures below.

## Measured figures before and after the change (the lead, 2026-11-15)

`Rewrite-Reason: DEC-1184 (3)` (figures added, no case changed).

**The method.** W1-02's measure, unchanged: the p95 of the hook's own CPU time, less the reference hook's median, in
ms; the bound is 100. The call's PATH was the CTO's interactive session's PATH: 46 entries, 27 of them under `/mnt/c`
(a launched session has 5). The load came from the lead's CPU burners; the load shown is `os.getloadavg()[0]` at each
round. "Before" is the guard's code at `15c380fdc64a`; "after" is the change (src at `689e9706b2d3`). The PATH matters
because the install check before the change resolved every PATH entry on each Bash call. On `/mnt/c` that is mostly a
9p wait, which wall time counts and CPU time largely does not.

Judged figure per round, in ms; "red" = all three rounds over 100. The gov accept row's red is load-sensitive: the
same cases pass run alone at load 25.

| run | code | load | Bash plain | Bash pipe | Bash redirect | 151 trees Read | 151 trees Write | 151 trees Bash | planted 150 ms hook (all six) |
|---|---|---|---|---|---|---|---|---|---|
| quiet | before | 3 | 58.8 | 56.0 | 58.7 | 53.3 | 30.7 | 63.6 | not run |
| about 20 | before | 23.2-26.3 for the Bash rounds; 20.8-23.4 for the tree cases; 7.4-18.5 for the planted cases (corrected, r4c review) | 118.0, 111.3, 117.6 (red) | 104.2, 106.8, 116.2 (red) | 165.7, 122.1, 64.6 | 55.1 | 30.3 | 63.9 | 180-271, each fails |
| 50 or more | before | 52-53 | 99.9 | 88.1 | 86.9 | 83.7 | 50.7 | 109.3, 97.3 | 201-298, each fails |
| about 20 | after | 20-23 | 85.0 | 93.7 | 93.8 | 91.8 | 58.6 | 106.5, 93.8 | 209-304, each fails |
| 37-49 | after | 37-49 | 86.9 | 89.4 | 83.0 | 93.2 | 51.5 | 89.8 | 202-246, each fails |
| 50 or more | after | 51-59 (the planted cases at 38-49, corrected, r4c review) | 86.9 | 94.8 | 91.9 | 86.5 | 57.8 | 97.4 | five figures printed, then stopped: four with a result, 238-283, each fails; the fifth (trees Write, 203.7-212.2) with no recorded result (corrected, r4c review) |
| gov accept, PATH 5 entries (the lead's note, not in the log) | after | 25-40 (the lead's note, not in the log) | pass | pass | pass | one of the three 151-tree cases red | (same run) | (same run) | 6 of 6 fail |
| alone, PATH 5 entries | after | 25 | not run | not run | not run | 83.1 | 51.3 | 87.4 | not run |

The r4b runs (corrected, r4c review; the earlier line "The quiet run after the change is not yet taken" is withdrawn):
after the change, quiet, the six timing cases ran at 27.0-50.5 ms, all passing; at load 60-64, at 46.4-86.5 ms, all
passing; the planted 150 ms hook at 178.1-253.3 ms, every case failing. The "gov accept" row's PATH entry count and load
are in neither `accept-1.json` nor `accept-1.err`: they are the lead's note, not the log's.

**What the figures show.**

- Before the change, the Bash cases' verdict changed with the load: red at load 23-26 (plain and pipe), green at load
  3 and 52 (plain at 99.9).
- After the change, every timing case passed in the lead's runs at every load measured (20-59 in r4, quiet and 60-64
  in r4b). Under `gov accept` (its load and PATH: the lead's note, not in the log) one 151-tree case went red; the same
  cases passed run alone at load 25. The margin under load is 3-15 ms, so the cases still judge near the bound: about
  50 ms of each call is imports and YAML reads, outside this ticket's paths (the reason for DEC-1187).
- The planted 150 ms hook failed every case at every load at which a result was recorded (178.1-304: r4 and r4b).

## S9 and S10 (DEC-1187): the YAML count, and the live hook's diff timed

`Rewrite-Reason: DEC-1187`. Written by a fresh independent test designer (brief td-4) from S9, S10, failure-4,
failure-5 and the CTO's interface for S9's count case (DEC-1157 (3), the ticket's paragraph at its end), before the
change and without reading the engineer's work (DEC-820): the diff file is used by the live-hook cases at run time, by
its path, and was never opened. No earlier case is changed.

### S9's count case (`test_w2_111_yaml_count.py`, 35 cases; support `w2_111_yaml_count.py`)

**What it measures.** The product guard's hook (`template/governance/kernel/hooks/pretooluse.py`) run as W1-02 runs it
(`w1_02_support.run_hook`), in W1-02's fixture project with the two governance YAML files the guard reads committed:
`governance/project/held-out.yaml` (one held-out path, outside the project, that no call names) and
`governance/project/path-map.yaml` (the kernel template's, with W2-111's planted evaluation set measuring the engineer
and a `role_paths:` section in this repository's own form, so both sections a real project has are there). The only
addition to W1-02's run is a probe folder first on the child's `PYTHONPATH`, whose `sitecustomize` (written by the
case into its temporary folder; it never imports or patches the guard's modules) reports, per call and across every
process of the call (the hook forks its decision):

- the YAML files opened under the project's `governance/`: an audit hook on the `open` event;
- every parse through yaml's public load API (`yaml.load`, `safe_load`, `full_load`, `unsafe_load`, their `_all` forms,
  `compose`, `compose_all`, `parse`, and a loader's `get_single_data` used directly), counted once at its outermost
  entry and put to its file: the stream's name, or, for text, the governance YAML file (or ticket file) whose bytes it
  is or holds (a parser may parse one section's lines alone).

A fixture first checks the probe is live: a direct `yaml.safe_load` of `held-out.yaml` in a child with the same
environment must be reported as one open and one parse of it.

**The cases.**

- **Behaviour 1** (`test_a_call_refused_before_the_held_out_check_parses_no_yaml_file`, 6): a Bash call with
  `dangerouslyDisableSandbox` set (no role, engineer, test designer, auditor) and a Read whose path holds a NUL byte (no
  role, engineer): each refused, as today (the first with its reason naming `dangerouslyDisableSandbox`); no YAML parse
  at all and no governance YAML file opened.
- **Behaviour 2** (`test_a_write_or_edit_of_any_role_parses_no_path_map`, 10): Write and Edit, by no role (`docs/`,
  refused), the engineer (`src/gov/guard/decide.py`, allowed; its ticket's acceptance file, refused), the test designer
  (the acceptance file, allowed) and the auditor (`src/gov/guard/decide.py`, refused), each decided as today; no parse
  of `path-map.yaml` (and, should it be opened, no parse the probe cannot place).
- **Behaviour 3** (`test_each_yaml_file_a_call_opens_is_parsed_at_most_once`, 14): Read, Write, Edit, Glob, Grep and
  Bash by the engineer and by no role, and Read and Bash by the test designer, each decided as today; no governance YAML
  file parsed more than once; and `held-out.yaml` opened on each.
- **DEC-218** (`test_a_broken_held_out_yaml_still_stops_every_call`, 5): with `held-out.yaml` broken, a Read (no role,
  engineer), a Write, a Glob and a Bash (engineer) are each refused.

**DEC-218, kept explicit.** `held-out.yaml` is read on every call past the guard's early refusals: a broken
`held-out.yaml` stops every call. Its one parse per call is therefore needed, never waste: behaviour 3 asserts it is
opened on each such call and parsed at most once; behaviour 1's calls, refused before the held-out check, read nothing;
and the DEC-218 case asserts the broken file still refuses.

**Before the change, S9** (2026-11-15, the test designer, at `00c9327e0`, in its launched session): **35 passed** in 3 s.
Behaviours 1 and 2 were expected green and are: they pin today's behaviour. **Behaviour 3 was expected red and is
not.** The probe shows, for a Read, Glob, Grep or Bash with a role set: `held-out.yaml` opened and parsed once,
`path-map.yaml` opened and parsed once (one section's lines, `evaluation_sets:`), and a third parse whose text is the
session's ticket's front matter (from `.tickets/<id>.md`, not a YAML file under `governance/`). With no role, the
third parse is absent. Writes and edits open and parse `held-out.yaml` alone. So the "3 yaml loads for those 2 files"
of the lead's measure at `0e2cdf33e` are 3 loads for 3 files: no governance YAML file is parsed twice. The same held
with 3 worktrees registered and with the `role_paths:` section present (a scratch probe, not a case). The case was not
forced red (no file planted to be parsed twice, no bound changed): the question goes to the lead
(`proposed_decisions` of the test designer's return).

### S9 and S10 on the live hook's patched copy: within 100 ms, the drop recorded (`test_w2_111_live_hook_diff_p95.py`, 20 cases; support `w2_111_live_hook.py`)

**What it measures.** The engineer's diff of `.claude/hooks/` (`docs/changes/W2-111-live-hook/live-hook.diff`, paths
`a/.claude/hooks/...`) is applied with `git apply` (in a fresh `git init` folder) to a clean copy of the tree's
`.claude/hooks/` (`__pycache__` left out); a second clean copy is the before copy, its `pretooluse.py` and
`bash_writes.py` checked against ACT-GUARD-FIX-6's sha256 prefixes (`9b4228ea095a`, `f03f9ac3e431`). A diff that is
absent, cannot be read by `git apply`, changes no file or a path outside `.claude/hooks/`, or does not apply fails every
case with that reason. Each copy is run as `.claude/settings.json`'s PreToolUse command runs the live hook: `sh` runs
the pinned interpreter with `-E` and the copy's `pretooluse.py`; the interpreter is the first line of
`$HOME/.local/bin/gov` (its `#!` taken off), else of the real home's (`pwd.getpwuid`: **the whole-folder run sets
`HOME` to an empty folder, so the real home is used for the interpreter only**; the hook's own `HOME` is the session's),
else of the `gov` on `PATH`. `CLAUDE_PROJECT_DIR` and the working folder are the repository root the tests run in (its
real config, tickets and registered worktrees), `GOV_GUARD_CALLS_DIR` and `TMPDIR` point into pytest's temporary
folder, as `measure.py` does; the payload is `measure.py`'s.

The 20 cases are `measure.py`'s (`~/gov-os-runs/W2-111/gf6-measure/measure.py`), in its order and with its inputs; the
scratch targets are under pytest's temporary folder. The first 15 are the mapped W1-05 (9), W1-02 (5) and W2-57 (1)
cases; the last 5 the Bash cases. The measure is W2-111's: per call, the CPU time of the hook's process and its
children (`RUSAGE_CHILDREN`) less the median CPU time of the reference hook timed beside it; nearest-rank p95 over 40
calls after 3 warm-up calls; a round that does not pass is repeated, up to 3 rounds. **Before and after are paired in
the same run**: each sample times a reference and the before copy, and a reference and the after copy, the order
alternating sample by sample. A case passes when, in one round, the after figure is **under 100 ms** (DEC-1187 (1)'s
own target, the same for the 15 mapped cases and the 5 Bash cases). Every call (warm-up included) must be decided
the same by both copies, and by the before copy as `measure.py` recorded on the live repository (allow, but deny for
the engineer's and the auditor's refused Writes) (failure-4). `git status --porcelain --untracked-files=all` of the
repository is the same after the case as before it: the case writes nothing there. **The drop is recorded, not
judged**: each case gives, per round, before, after and the drop (before less after), with the wall p95 of each and
the load, in its failure message and in a line printed on a pass (`-s` shows it; the line starts `PASS` or `FAIL`), so
S9's measured drop is visible in every run.

**Why so.** S9 is judged on the live hook, where the fixed cost lies (P-W2-111-S9-BASE (a)); pairing the two copies in
one run makes the drop a difference taken under the same load, never a figure from another day. CPU time less a
reference beside it, not the wall time under load: W1-02's README, section "W2-111".

**Why the 30 ms clause went** (P-W2-111-S9-DROP (a), the CTO under DEC-1157 (12), 2026-11-15; the ticket's S9 line).
The case used to require each of the 15 mapped cases to be at least 30 ms below its before figure as well. That figure
came from a measure taken at load 14-28; quiet, the applied ACT-GUARD-FIX-6 hook already runs 52-83 ms, under the
bound, and the rest of each call (the interpreter, the pinned gov's imports, compiling the script) lies outside
`.claude/hooks/`, where the diff cannot reach it. S9 is now judged by DEC-1187 (1)'s own target, S10's measure, with
the drop recorded. The bound (100 ms), the pairing, the 40 samples, 3 warm-ups, up to 3 rounds, the before copy's
hash check, the `git apply`, the decision equality, the porcelain check and the 20 parameter ids are unchanged. The test
function, whose name ended "and 30 ms below the applied hook", was renamed to
`test_the_live_hook_s_patched_copy_is_within_100_ms_of_the_applied_hook_the_drop_recorded` (td-6, the lead's decision
on P-W2-111-TD5-NAME (a)), so that its name says what it now checks: the old name named a clause the case no longer
judges. The 20 node ids are new in this run and never landed, so the rename removes no landed case (F1 guards only the
15 revised cases of W1-02, W1-05 and W2-57, untouched).

**Before the change:** all 20 red, each `the live hook's diff docs/changes/W2-111-live-hook/live-hook.diff is absent:
S10's diff of .claude/hooks/ against the applied ACT-GUARD-FIX-6 bytes is not prepared` (0.1 s).

**The harness checked without the diff** (a scratch run, not a case; 2026-11-15, the launched session, empty `HOME`,
load 4-12): with a stand-in diff that adds one comment line, the copies built, the pinned interpreter resolved from the
real home, every decision matched `measure.py`'s record in both copies, and `git status` was unchanged. At 40 samples
the drop between identical copies was -28.3 to +12.2 ms over 15 rounds (5 cases): the noise of a recorded drop at this
sample count (that run judged the 30 ms clause, since removed; not re-run for td-5).

### failure-5 for the live-hook case (`test_w2_111_live_hook_slow_hook.py`, 5 cases)

The planted hook (`w2_111_support.SLOW_HOOK`, as `test_w2_111_slow_hook.py` plants it: 150 ms of its own CPU time per
call, a busy loop, then the after copy's own hook as `__main__`, so the decision is unchanged) is put in place of a copy
of the after copy's `pretooluse.py`; the live-hook case's judgement, paired with the before copy, must fail: no round
passes, all three rounds run, every after figure at or above 100 ms. **Five of the 20 cases**, spread over the kinds
(`W1-05 Glob-no-role`, `W1-05 Write-engineer`, `W1-02 engineer Write acceptance (deny r1)`, `W2-57 test-designer Read
ordinary`, `Bash pipeline (engineer)`): each takes all three rounds of a 0.2 s hook. Before the change: all 5 red, the
diff absent (the same text). In the scratch runs with the stand-in diff (`W1-05 Glob-no-role`), the planted hook's
after figures were 207.2-254.0 ms in every round printed, three rounds each time: the judgement failed it.

### Kinds, markers and run time (DEC-1187's cases)

The count cases are acceptance cases (about 0.1 s each; 35 in 3 s). The live-hook and its planted cases are
**load-sensitive** (they assert a latency, by CPU time less a reference beside it). **No marker**: none needs a real
model, a dev tier or the network; no name, id or file holds `real`, `green_here` or `time_limit`, so the whole-folder
filter selects them all and `gov accept W2-111` runs them on this machine. They need what the live hook needs here: the
pinned gov (`~/.local/bin/gov` or `gov` on `PATH`) and the tree's `.claude/hooks/` at ACT-GUARD-FIX-6's bytes. Run time,
estimated from the scratch run (about 0.3 s per pair of calls; 0.45 s with the planted hook): each live-hook case 15 to
40 s (one to three rounds of 40 pairs), the 20 about 5 to 13 minutes; each planted case about 55 s, the 5 about 5
minutes. They are past the 5 s of their kind for the reason W1-02's measure is: 40 calls a round, three rounds when
needed, two copies paired; not cut. No `skip`, `xfail` or `flaky` mark.

**After ACT-GUARD-FIX-7 is applied** the tree's `.claude/hooks/` is no longer ACT-GUARD-FIX-6's bytes, and the 25
live-hook cases fail on the before copy's hash check by design (the diff is judged against FIX-6's bytes): their
retirement or re-pointing then is a follow-up row for the CTO (the test designer's return, `risks`).

## F1 (rv-3): the YAML loader answers as the pure SafeLoader does (`test_w2_111_yaml_parity.py`, 28 cases; support `w2_111_yaml_parity.py`)

`Rewrite-Reason: DEC-1156 (7), P-W2-111-R5-ROWS (a)`. Written by a fresh independent test designer (brief td-7) from
rv-3's F1 given as a described behaviour (DEC-136), without reading the engineer's work or the diff (DEC-820): the diff
is used by its path at run time, never opened.

**The behaviour.** The guard reads `held-out.yaml` (and the path map's blocks) with a loader that refuses a key written
twice. A text the pure-Python `yaml.SafeLoader` refuses must still be refused, and a text it reads must be read to the
same data, whatever faster parser is used. rv-3 found libyaml's parser more lenient on: a tab inside or after a plain
value and after `key:`, a `? ` inside a flow item, and a byte order mark after the start of the text. Before the fix such
a `held-out.yaml` was read: a held-out entry with a tab in it no longer stopped every call, as the pure loader's refusal
did (DEC-218): **fails open**.

**The texts** (each under `held_out_paths:`, `{p}` an absolute folder under pytest's temporary folder): a tab inside an
entry (`- {p}/held<TAB>mat`); a tab after an entry; a tab after `held_out_paths:`; `[{p}/held? mat]`; a BOM after a line
break (`<BOM>- {p}/held` on line 2); a key written twice (`held_out_paths:` twice, the duplicate rule itself); and one
clean control (`- {p}/held`). The pure loader refuses all but the clean one.

**The cases.**

- **The fixture** (`test_the_pure_safe_loader_refuses_each_class_text_and_reads_the_clean_one`, 7): the judging loader,
  `yaml.load(text, Loader=PureUnique)` (`PureUnique`: a `yaml.SafeLoader` subclass whose `construct_mapping` raises
  `ConstructorError(None, None, "a key is written twice", node.start_mark)` when the mapping's length differs from the
  node's), refuses each refused text and reads the clean one to its one entry. Green everywhere: it shows the texts are
  what they claim.
- **The product loader** (`test_the_product_loader_answers_each_text_as_the_pure_safe_loader_does`, 14: each text, given
  as `text` and as a `file` opened UTF-8 as the guard opens `held-out.yaml`): `gov.util.parts.load_yaml_unique` and
  `gov.guard.heldout.load_yaml_unique` each give the pure loader's answer: the same data, or an exception of the same type
  with the same text. (success-9: the parsed-once loader; failure-4.)
- **The live hook's copy** (`test_the_live_hook_s_patched_copy_decides_each_held_out_text_as_the_applied_copy_does`, 7):
  the before and after copies of `.claude/hooks/` (`w2_111_live_hook.make_copies`, as the live-hook case builds them),
  each run as `.claude/settings.json`'s command runs the hook (the pinned interpreter, `-E`), no role set, on a planted
  project: `CLAUDE_PROJECT_DIR` and the working folder a temporary git repository whose
  `governance/project/held-out.yaml` is the text's bytes exactly; the call log in the temporary folder. A Read of a
  planted file under the folder the entry names (as a lenient parser reads it: `held<TAB>mat`, `held? mat` or `held`)
  and a Read of an ordinary file of the project (`docs/guide.md`) are decided the same by both copies. The before copy
  reads `held-out.yaml` through the pinned gov's pure loader, so it must refuse both Reads for a refused text and refuse
  the planted file and allow the ordinary one for the clean text (asserted: the harness is sound). (failure-4.)

**Before the fix.** On this tests branch (`c034b6654ed0` plus these files) the product loader is the base's, the pure
SafeLoader, so the 7 fixture and 14 product cases **pass here** (0.2 s); the 7 live-hook cases fail, `the live hook's
diff docs/changes/W2-111-live-hook/live-hook.diff is absent`, as td-4's do. **The red before the fix shows only on the
ticket branch**, whose r5 src and diff hold the faster parser; the lead runs it there. Expected there: each class text's
product case `<text> (<form>): gov.util.parts.load_yaml_unique read the text that the pure SafeLoader refuses`, and each
class text's live-hook case `<text>: a Read of an ordinary file of the project was decided allow by the patched copy and
deny by the applied copy (the pure loader's)`. The clean control is green before and after.

**The harness checked without the engineer's work** (scratch runs, not cases; the launched session, empty `HOME`): with a
stand-in diff that changes nothing, the 7 live-hook cases passed (1.8 s); with a stand-in diff that puts libyaml's
`CSafeLoader` in the hook's held-out loader, the 5 class texts failed with the message above (the planted file still
refused, the ordinary file allowed: the fail-open), and the key written twice too (that stand-in has no duplicate check);
the clean control passed. With a stand-in product loader of libyaml plus the duplicate check, the 10 class-text product
cases failed (`read the text that the pure SafeLoader refuses`), and so did the key written twice given as text.

**Exception text, said plainly.** The answer compared is the exception's type and its whole text, as the brief states.
libyaml's error marks carry no snippet of the source line, the pure loader's do (for a text): so a refusal raised from
libyaml has another text than the pure loader's for the same text input, even where both refuse (the stand-in's
`key-written-twice-text`). Given a file, neither mark has a snippet. The guard's held-out reader replaces the parser's
text by fixed text, so the difference reaches a user only through a path map's error.

**Kinds.** Acceptance cases, about 0.2 s for the 21 in-process cases and 2 s for the 7 live-hook cases. Not timing
cases, so not in `serial-only.txt`. No marker; no name, id or file holds `real`, `green_here` or `time_limit`, so the
whole-folder filter selects all 28.

## F2 (rv-3): the five timing files kept serial

`Rewrite-Reason: DEC-1156 (7), P-W2-111-R5-ROWS (a)`. rv-3 found W2-111's timing cases red only inside lead_verify's
parallel phase (load 10 to 20), while alone and quiet they passed 25 of 25. They are now listed in
`tests/acceptance/serial-only.txt`, in its `# --- latency: kept serial, each alone` block, one entry per file, each
`serial: latency: <reason>`: `test_w2_111_bash_p95.py`, `test_w2_111_many_trees_p95.py`, `test_w2_111_slow_hook.py`,
`test_w2_111_live_hook_diff_p95.py` and `test_w2_111_live_hook_slow_hook.py`. The close leaves them out of its parallel
phase and runs each alone afterwards; the nightly runs them alone too. No case, bound or round was changed.
`gov_close_serial_only.entries` reads all five.
