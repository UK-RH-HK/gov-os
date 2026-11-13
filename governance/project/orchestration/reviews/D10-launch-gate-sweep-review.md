# D-10's red-fix list: the review of the launcher suites planting an open gate (W2-20, DAEO-r30l)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-launch-gate-sweep-review.md`; branch `w2/W2-20-d10b-tests` at `440304dd9`; reviewer log `/home/usain/gov-os-worktrees/W2-20-d10b-tests/.gov-runtime/scratch/lead/log/D10-launch-gate-sweep-review.json`.
- verdict.py: READY (no blocking finding).

Sandbox check passed, and I recommend READY: no finding blocks. Nothing in the nine commits lowers an expectation, writes to the real HOME or adds a new cross-suite import. All nine carry the five trailers, Rewrite-Reason included.

**Sandbox check (Step 0, EMG-d4b-launched.md):**
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-r30l','w').write('x')"` failed with `OSError: [Errno 30] Read-only file system`, as required.
- (b) `echo sandbox-trial | git hash-object -w --stdin` gave `1ae28402a109c3397a44b19239a00adfa9472eb0` (exit 0), and `git update-index --refresh` exited 0.

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing (grep exit 1).

---

**task:** DAEO-r30l. Read-only independent review of the nine commits in `df7c67292..440304dd9`, D-10's red-fix list (launcher suites planting an open resource gate, W2-20 S19, DEC-1088 (5)(b)). KPI `launcher-open-gate`.

**status:** DONE

**work_completed:**
- Read EMG-d4b-launched.md, EMG-common.md and JUDGEMENT.md.
- Read all nine commits with `git show`.
- Read the product code they depend on: `src/gov/launch/launcher.py`, `src/gov/launch/gate.py`, `src/gov/launch/environ.py`, `src/gov/resources/gate.py`, `src/gov/resources/machine.py`, `src/gov/resources/slots.py`.
- Checked at `df7c67292` which suites already imported `w1_46_support`.
- Checked how W1-33's own fix on integrate (`cfe4ed605`, not in this branch) combines with this branch.
- Searched the named suites for cases about the gate, resources, the launch log, HOME snapshots and runs after a launch.
- Ran 426 cases through the heavy slot.

**files_changed:** none.
- The only writes were the two Step 0 commands (blob `1ae28402a109`, index refresh).
- My scratch folder under my own TMPDIR was removed after the run.
- The ignored `__pycache__` folders in the worktree are dated 01:12–01:32 UTC, before the commits (01:33:18). They come from the designer's runs, not mine: I ran with `PYTHONDONTWRITEBYTECODE=1`.

**evidence:**
- Command: `env HOME=<my TMPDIR>/r30l/home TMPDIR=<my TMPDIR>/r30l/tmp PYTHONUSERBASE=/home/usain/.local PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/usain/gov-os-worktrees/W2-20-d10b-tests/src bash …/heavy_slot.sh python3 -m pytest -p no:cacheprovider -o tmp_path_retention_policy=failed -q -n auto -m "not local_only" -k "not real and not green_here and not time_limit" --optin=lifted,breadth`.
- Files:
  - W2-58: `test_w2_58_engineer.py`, `_test_designer.py`, `_fails_closed.py`, `_evaluation_sets.py`, `_review.py`
  - W1-28: `test_w1_28_launch_temp_folder.py`
  - W1-46: `test_w1_46_launch_refusals.py`, `test_w1_46_role_settings.py`
- Result: **420 passed, 6 failed** in 37.8 s.
- Scratch before removal: 187M (`du -sh`), 30,379 inodes (`du -s --inodes`).

**tests:**
- All of the W2-58 launch files pass, matching the designer's 16 → 0 for those files.
- W1-28's temp-folder file passes, including the refused-launch cases and the CLI-that-cannot-start case.
- W1-46's launch-refusal file passes.
- The 6 reds are all one guard case, `test_w1_46_role_settings.py::test_a_file_tool_write_under_gov_runtime_is_refused_by_the_guard[Write|Edit × engineer|test-designer|research]`, with `decision=allow`.
  - It never launches: `ask_guard` uses `live_support.command_environment`, which this revision does not touch.
  - These are the "W1-46 guard cases" the designer named as another cause.
- The exclusion deselected nothing in these eight files (the summary shows no deselected count).
- The five live-session cases this revision edits were not run. They are `local_only` and need the real CLI login outside the sandbox. They are W1-46's `test_w1_46_live_sessions.py`, W1-50's `test_w1_50_freeze_launcher.py` and `test_w1_50_freeze_live_pause.py`, W2-54's `test_w2_54_sandboxed_worker.py` and W2-58's `test_w2_58_launched_sessions.py`.
- I did not re-run the designer's full before → after counts for every suite.

**discoveries:**
1. For a worker, `gov launch` runs the gate (`_admit_start`, `launcher.py:445`) after every other refusal check (`launcher.py:425-442`): role, CLI arguments, ticket, repository settings, CLI presence, built settings, sandbox faults. For a lead it runs after the plan check and settings (`launcher.py:411-419`). So no refusal case can pass because the gate is open. A refusal check that broke would now start a session, and `assert_refused` would catch it; with the gate shut, the gate's own `LAUNCH_REFUSED` hid that.
   - One case passed only because the gate was shut: W1-28's `test_a_cli_that_cannot_be_started_leaves_no_temp_folder`. No temp folder is made before the gate, so it passed without testing anything. It now reaches `_run` and passes for its own reason.
2. The cleaned session environment (W2-56 S5, `src/gov/launch/environ.py:18`) passes only PATH, HOME, LANG, LC_ALL, USER and LOGNAME. So the planted `GOV_RESOURCES_*` never reach a launched session, stand-in or live. W2-54's in-sandbox `gov retrieve` builds its own environment anyway.
3. Outside `gov.resources`, only `gov/launch/gate.py` and `gov/launch/launcher.py` read the gate or its readings. `gov close` checks the disk with `statvfs`, not with the planted readings.
4. `GOV_RESOURCES_EMBEDDING_CPU_NOW` is not planted (W2-136's form doesn't plant it either). Every planted launch therefore samples the real embedding servers' processes in /proc, with a pause of up to 0.25 s, and writes the sample history into the case's HOME. It cannot shut the gate, because the planted p95 is 0.
5. W1-33's integrate fix plants into its own `elsewhere/gate-readings` folder and calls `run_gov` itself. After the merge, W1-46's `open_gate_environment` adds nothing there, and the two touch no common file.

**risks:**
- Six copies of the planted configuration exist: W2-136, W1-33, W1-46, W2-50, W2-58 and W2-116. A new required key in W2-20's `gate.json` turns all six red at once. That fails closed, not open, and it is the price of adding no new coupling.
- The live-session edits rest on reading alone until the CTO runs them outside the sandbox.

**lessons:** Before judging whether an opened gate weakens refusal cases, check where the product runs it. Here it runs last, so opening it makes those cases stronger.

**proposed_decisions:** none.

**unresolved:**
- The five live-session cases need a run outside the sandbox.
- W2-116's six launch cases stay red for another cause: W2-56 S5's cleaned environment drops `W2_116_SESSION_LOG`. The designer has reported it.

**recommended_next_action:** Mark READY and merge. Run the five live-session cases outside the sandbox between measures. F1's recorded override is optional, at the next edit.

---

### Answers to the checks

**1. No expectation lowered.**
- *Refusal, gate, resource condition or launch-log cases:* none passes because the gate is open.
  - All the named refusals happen before the gate (discovery 1). No suite among the nine reads `~/.gov-os/machine/launch.log` or tests the gate or a resource condition.
  - No assertion changed in any of the nine commits. The only changes are planting calls, environment plumbing, W1-38's runner copy (identical to W1-07's `run_gov_with_code`, plus the gate variables), and docstrings/README notes.
- *Planted only where a launch must start?* No. W1-46's, W2-50's and W2-58's `launch()` plant for every launch, refusal cases included. That is safe and in fact stronger, for the reasons in discovery 1.
- *Planted readings leaking into a case that reads the real machine on purpose?*
  - None today: the readings never reach a session (discovery 2), and only the launcher and `gov resources` read them.
  - W2-50, W2-58 and W2-116 build a new dictionary for the launch only.
  - W1-46's `gov_environment` keeps carrying the readings for later runs in the same test. No case today runs a command that reads the machine after a launch (F2).
- *HOME snapshots:* the two HOME snapshots in these suites (W1-28 freeze, W1-32 status) wrap `gov pause` and `gov status`, not launches. W1-32's leftover listing reads only `sandbox.tmpdir`.

**2. Nothing written to the real HOME.**
- All five live-session sites build a scratch sandbox with `make_sandbox(<tmp>)`, so `gate.json` lands in `<tmp>/…/home/.gov-os/machine/` and the readings in `<tmp>/…/elsewhere/open-gate/`.
  - The sites: W1-46 `_start` (`:117`), W1-50 freeze_launcher (`:245`), W1-50 live_pause (`:240`), W2-54 (`:198`), W2-58 `_start` (`:154`).
- The real HOME reaches the session only through the passed environment (`inherited(os.environ)`). So the launcher reads the machine's own `gate.json`, and the planted copy in the scratch HOME goes unused, which is harmless.
- During a live launch, the launcher itself writes the real HOME's `launch.lock`, its registry entry and its CPU sample history. That is W2-20's behaviour for every real launch, not the tests'.
- The live handling is otherwise safe; F1 is a recorded row.

**3. No new cross-suite coupling.**
- At `df7c67292`, W1-28 (`w1_28_launch_support.py:40`), W1-38 (`:38`), W1-50 (`w1_50_freeze_support.py:45`) and W2-54 (`:49`) already imported `w1_46_support`. W1-32 already reached it through W1-28 (`w46 = w28.w46`).
- W2-50, W2-58 and W2-116 got their own copies, with no new import.
- W1-38 now uses W1-07's support module directly instead of its `run_gov_with_code`: same module, same coupling.
- Other importers are unaffected: W2-90 uses only constants, and W1-33 is covered in discovery 5.

**4. Trailers and paths.**
- All nine commits carry `Task: DAEO-r30l`, `Implements: DEC-1109, DEC-1088`, `Role: independent-test-designer`, the Rewrite-Reason (`DEC-1088 (5)(b): …`) and `Co-Authored-By`.
- 23 files changed, all under `tests/acceptance/{W1-28,W1-32,W1-38,W1-46,W1-50,W2-50,W2-54,W2-58,W2-116}/`. There are no merge commits in the range.

### Findings

**F1 — The live sessions pass the gate on planted readings, and nothing records it** (`W1-46/test_w1_46_live_sessions.py:132`, `W1-50/test_w1_50_freeze_launcher.py:257`, `W1-50/test_w1_50_freeze_live_pause.py:263`, `W2-54/test_w2_54_sandboxed_worker.py:77`, `W2-58/test_w2_58_launched_sessions.py:161`). Scope: in.
- These real sessions on this machine are now admitted whatever the machine's load. No line goes to `~/.gov-os/machine/launch.log`; DEC-899's recorded path is `--gate-override DEC-NNN` (`launcher.py:378-385`).
- They are still entered in the real registry, so other launches count them. Before S19 these cases launched with no gate at all.
- Option at the next edit: pass a recorded `--gate-override` in the five live launches, or state in the READMEs that the `local_only` cases run only between measures.
- Ordinary work: yes, because the CTO runs the `local_only` cases on this machine, and nothing in them now looks at the machine's load first.
- Consequence: other. The sessions are light (haiku, one or two Bash calls), run one after another and are registered. Tonight's refusal was 13.87 GB available against a 14.18 GB limit, which leaves a wide margin. There is no plausible path to lost work.

**F2 — W1-46's `gov_environment` carries the planted readings into every later `gov` run of the same test** (`W1-46/w1_46_support.py:405`, `:340-347`). Scope: in.
- After a `launch()` has planted, every later `gov` run in that test gets the readings, not only launches.
- A future case that launches and then runs `gov resources --check` to read the real machine would silently read the planted numbers.
- Ordinary work: no, because no case in W1-46, W1-28, W1-32 or W1-50 runs a command that reads the machine after a launch, and the gate's own cases live in W2-20's suite.
- Consequence: other. It would make such a future test inaccurate; no control fails open.

**F3 — W2-50's, W2-58's and W2-116's helpers overwrite `gate.json` without checking whether one is there** (`W2-50/w2_50_support.py:601-603`, `W2-58/w2_58_support.py:717-719`, `W2-116/w2_116_support.py:757-759`; also W1-46's unused `home=` parameter, `w1_46_support.py:350, 370-371`). Scope: in.
- W1-46's helper writes only when the file is missing.
- If any of these helpers were handed a sandbox whose HOME is the real one, they would replace the machine's own `gate.json` with the planted floors (a 3 GiB memory floor). W1-46's `home=` parameter would create one in a real HOME that lacks one. Either way the real gate would admit every launch on the machine.
- Ordinary work: no, because every sandbox in these suites comes from `make_sandbox(<tmp>)`, whose HOME is always `<tmp>/home`, no caller passes `home=`, and the live cases pass the real HOME only through the environment. It is a row for the Wave 3 hardening pass.
- Consequence: fails open (only in that unreachable case).

```verdict
{"kpis": [{"kpi": "launcher-open-gate", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}]}
```
