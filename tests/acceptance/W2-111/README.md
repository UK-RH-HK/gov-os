# W2-111 (DAEO-qvff): the reopen's acceptance cases: the guard's 100 ms on Bash calls and with 150 or more trees

`Rewrite-Reason: DEC-1184 (3)` (new cases, the owner's reopen of W2-111 on 2026-11-14, Q-SCAN-2 (a); DEC-979, DEC-906,
DEC-968). Written by a fresh independent test designer from the reopen's KPI lines, before the change, without
reading the engineer's work (DEC-820, DEC-963). No earlier case is changed.

**Which lines this folder judges.** `gov accept W2-111` runs this folder only. It judges the reopen's lines:
success-5 to success-8, failure-4 and failure-5. The earlier lines (success-1 to success-4, failure-1 to failure-3) are
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
| failure-5 | `test_w2_111_slow_hook.py::test_the_planted_150_ms_hook_fails_each_new_timing_case` | none: green before and after the change; red only if a new timing case passes the planted 150 ms hook. |

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
| about 20 | before | 20-24 | 118.0, 111.3, 117.6 (red) | 104.2, 106.8, 116.2 (red) | 165.7, 122.1, 64.6 | 55.1 | 30.3 | 63.9 | 180-271, each fails |
| 50 or more | before | 52-53 | 99.9 | 88.1 | 86.9 | 83.7 | 50.7 | 109.3, 97.3 | 201-298, each fails |
| about 20 | after | 20-23 | 85.0 | 93.7 | 93.8 | 91.8 | 58.6 | 106.5, 93.8 | 209-304, each fails |
| 37-49 | after | 37-49 | 86.9 | 89.4 | 83.0 | 93.2 | 51.5 | 89.8 | 202-246, each fails |
| 50 or more | after | 51-59 | 86.9 | 94.8 | 91.9 | 86.5 | 57.8 | 97.4 | 238-283 (4 of 6 run, then stopped), each fails |
| gov accept, PATH 5 entries | after | 25-40 | pass | pass | pass | one of the three 151-tree cases red | (same run) | (same run) | 6 of 6 fail |
| alone, PATH 5 entries | after | 25 | not run | not run | not run | 83.1 | 51.3 | 87.4 | not run |

The quiet run after the change is not yet taken: the machine stayed at load 23 or more from other work.

**What the figures show.**

- Before the change, the Bash cases' verdict changed with the load: red at load 20-24 (plain and pipe), green at load
  3 and 52 (plain at 99.9).
- After the change, every timing case passed in the lead's runs at every load (20-59). Under `gov accept` at load
  25-40, one 151-tree case went red; the same cases passed run alone at load 25. The margin under load is 3-15 ms, so
  the cases still judge near the bound: about 50 ms of each call is imports and YAML reads, outside this ticket's paths.
- The planted 150 ms hook failed every case at every load (180-304).
