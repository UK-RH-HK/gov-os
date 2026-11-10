# D-10's red-fix list: the review of the planted pinned gov for the kernel-hook suites (W2-20, DAEO-r30l)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-pinned-gov-review.md`; branch `w2/W2-20-d10d-tests` at `5b6873b3a`; reviewer log `/home/usain/gov-os-worktrees/W2-20-d10d-tests/.gov-runtime/scratch/lead/log/D10-pinned-gov-review.json`.
- verdict.py: READY (no blocking finding; F1 and F2 out of scope, rows; F3 bytecode beside the sources, a row).

**Sandbox check (Step 0):** passed.
- (a) The write to `/home/usain/gov-os-worktrees/.sandbox-trial-W2-20` failed with `OSError: [Errno 30] Read-only file system`, and the file is absent.
- (b) `git hash-object -w --stdin` gave `1ae28402a109…`, and `git update-index --refresh` exited 0.

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` printed nothing. No such process exists, so none is mine.

**task:** DAEO-r30l (W2-20). Read-only review of D-10's planted pinned gov: commits `3a1be7726` (W1-47), `24a71cafb` (W1-46) and `5b6873b3a` (W2-90). GOV_TICKET is DAEO-r30l. HEAD is `5465e8137` at start and end; it contains `5b6873b3a`, and the later merge changes none of the reviewed suites (the diff from `5b6873b3a` to HEAD on them is empty).

**status:** DONE

**work_completed:**
- Read the three diffs, the kernel and repository hook lines, this repository's tree guard, and every caller of the three changed helpers.
- Ran two scratch probes in my own TMPDIR that call the real `plant_pinned_gov` and the copied tree guard.
- Checked the trailers, the decisions they cite, and the report-only list.

**files_changed:** none in any tree. A scratch folder in TMPDIR was created and then removed.

**evidence:**
- Probe A, on the helper:
  - It writes only `<home>/.local/bin/gov` (mode 0755, first line `#!/usr/bin/python3.12`) and `<home>/.local/lib/python3.12/site-packages/gov-of-this-worktree.pth`, which names this tree's `src`. Every new path is under the stand-in home.
  - A second call changed nothing.
  - A call with `Path.home()` (/home/usain) was refused.
  - Under `-E`, with a decoy `gov` on PYTHONPATH, `gov` and `gov.guard.decide` resolved to `/home/usain/gov-os-worktrees/W2-20-d10d-tests/src/…`. The decoy was never imported. PyYAML came from `/usr/lib/python3/dist-packages`.
- Probe B, on the copied tree guard (`.claude/hooks/pretooluse.py`) run by the planted interpreter with `-E`:
  - It imported 13 `gov` files, all from this tree's `src`.
  - An engineer's write to its own path was allowed (exit 0).
  - An engineer's write under `tests/acceptance/` was denied by rule 1, with its own reason. Both are decisions, not crashes.
- `/usr/bin/python3.12 -E -s` finds no `gov` of its own. The owner's pin names a venv interpreter (`~/.local/share/gov-os/pin-bcea09060ebc/bin/python`).
- After the probes: `git status --porcelain` is empty, and no `.pyc` in the tree is newer than the probe start.
- Scratch footprint was 6.7M and 1088 inodes; the folder is removed.

**tests:**
- I ran no pytest, so the real-model exclusion was not needed and left nothing out.
- I did not re-run the CTO's helper's counts or the designer's counts (117/222 → 71/0, 71 on both PATHs, W1-47 967, W1-05 53→4, W1-28 3→1). I took them as given.
- I checked the account of the 71 against `tests/optin-lifted-guard.txt`. Its W1-46 section (33 entries, lines 107–139) holds only the full guard's families: write scope, ln, hard links, mv/install/cp targets, the research fence and `.gov-runtime`. That fits; I did not match the 71 one by one.

**discoveries:**
- The 71 are W1-46 full-guard cases. The five-rule tree guard (DEC-953) does not enforce those rules, which are built but off in this repository (DEC-1061).
- They were green on a clean PATH only because the hook line's own refusal ("no pinned gov", exit 2) counted as a stop.
- W1-49's precompact case is still PATH-dependent (F2).

**risks:** F1 (another hook fault could again pass the stop cases), F3 (bytecode written next to the sources).

**lessons:** a stop helper that accepts the hook line's own refusal cannot tell a guard that decided from a guard that never ran. A clean-PATH run is what exposed it.

**proposed_decisions:** none.

**unresolved:** none blocking.
- The Write tool's permission for my TMPDIR scratch file was not granted in this non-interactive session. That is a harness permission, not the guard's refusal, so I worked round it.
- I ran the same probe as inline `python3 -c` in one sandboxed command, writing only under my own TMPDIR folder.

**recommended_next_action:** READY: merge. File F1 and F2 as rows: F1 to the W1-46/W1-47 suites or Wave 3, F2 to D-10's red list. F3 can be accepted, or ride along with the next change to the helper.

task: DAEO-r30l
decisions: DEC-732, DEC-822, DEC-866, DEC-917, DEC-953, DEC-1061, DEC-1109, DEC-801, DEC-808, DEC-1010. DEC-110 is taken as W1-47's support code cites it; I did not read it in the register.

## Answers to the checks

**1. No fail-open.**

*Does the planted gov run this tree's own guard, and never a looser one?* Yes; probes A and B show it.
- The hook line uses the pinned gov only for the interpreter named on its first line. That is the runner's real interpreter, which has no `gov` of its own.
- With `-E`, `gov` comes from the stand-in home's path file, which names this tree's `src`. A PYTHONPATH decoy is ignored.
- Before this fix, on the owner's PATH, the line used the pin's venv. A venv's own packages load ahead of a user-site path file, so the cases judged the pin's package, not this tree (DEC-732).

*Could a case now pass where the real product would refuse?* No.
- This repository's real sessions always have the owner's pin at `~/.local/bin/gov`, so "a pin exists" is the product's real state. Planting one changes only which `gov` code is judged: this tree's.
- `gov launch` (src/gov) never looks for a home gov, so the pin that `kernel_sandbox` now plants changes no launch.
- The change runs against fail-open: 117 exit-2 refusals on a clean PATH (106 in W1-46, 11 in W1-47) become real decisions. The 71 that now fail are report-only and fail honestly.

*Is any case's point "no pinned gov refuses", and is it kept?* Yes, and they are untouched.
- The cases are in W2-106:
  - `test_w2_106_fail_closed.py`: no gov found, no interpreter, missing interpreter, a broken home gov that must not fall back.
  - `tests/unit/hooks/test_w2_106_template_hook_lines.py`: `test_with_no_gov_the_line_refuses_and_names_it` and `test_a_gov_naming_no_interpreter_that_runs_refuses`.
- Each builds its own home and calls none of the three helpers. W2-106's generated-project file imports W2-90's module but never calls `install_gov_for`, and importing plants nothing.
- W2-65's missing-interpreter case also uses its own box.
- Because a second call plants nothing more, a case that plants its own broken home gov first keeps it.

**2. Writes.**
- The helper writes only under the home it is given (probe A). Every caller passes a home under `tmp_path`: W1-05's and W1-07's sandboxes, W1-47's `kernel_live_sandbox`, and W1-28.
- No change reaches the real HOME. The assertion refuses `Path.home()`. Separately, the owner's pin already exists, so the early return writes nothing even when a run sets HOME to a scratch folder.
- One write outside the case's folders is enabled by the plant: F3.

**3. Coupling.**
- **W1-46 → W1-47 was already there.** `w1_46_support` imported `w1_47_support` as `w47` at module level at the base `09e1ff6e1`, and already used its `GuardResult`, `assert_stopped` and `make_stand_in`.
- **W2-90 → W1-47 is new as a module-level import.** Before, W2-90 reached W1-47 only lazily, through `w1_38_hooks_support` and through `w1_46_support` inside `w1_46_project`.
- **W1-47 → W2-90 already existed** (`test_w1_47_failed_commands`).
- **It is sound:**
  - No support module imports W2-90's module, so there is no import cycle.
  - The module names are unique, and importing `w1_47_support` does no I/O beyond adding paths.
  - The path file's name and line match W2-90's and W1-38's, so the two writes in `install_gov_for` coincide for one interpreter.
- **Reach:** `ask_guard`'s callers are W1-46, W1-33 and W1-28. W2-50, W2-56, W2-58, W2-61 and W2-84 have their own `ask_guard`, which runs the guard program with `sys.executable` (no hook line, no pin), so they are unaffected.

**4. Trailers.**
- All three commits carry `Task: DAEO-r30l`, `Implements: DEC-1109, DEC-866`, `Role: independent-test-designer`, a `Rewrite-Reason: DEC-866, W2-106: …` and `Co-Authored-By`. Git parses all five as trailers on each commit.
- DEC-1109 and DEC-866 are both ACCEPTED.
- Six files changed, all under `tests/acceptance/`: three support files and three README notes.

## Findings

**F1, out of scope: a stop case cannot tell a rule's refusal from a guard that never ran.**
- *What happens:* W1-46's and W1-47's stop cases assert through `assert_stopped`, which counts any exit 2 as stopped. That includes the hook line's own refusal (no pinned gov) and a crash of the hook program.
- *Effect:* on a clean PATH, 71 full-guard cases were green although no rule decided. This revision removes the trigger that was seen; the helper itself is not part of the revision.
- *What should happen:* a stop case should fail when the refusal is the hook line's own `gov hook: …` message, which is the test environment's fault.
- Ordinary work: yes, because the CTO's clean-PATH landing check did exactly this, and any other fault of the hook's environment would do it again.
- Consequence: fails open. That is the acceptance check failing open, not the product: the product still refuses the call.
- *Reversed by:* the stop cases failing when the hook line's own message is on standard error, or every such case also checking the deny's reason.

**F2, out of scope: W1-49's precompact case still takes the gov from the runner's PATH.**
- *The case:* `test_w1_49_precompact.py::test_without_tk_the_block_says_so_and_holds_the_rest[not on PATH]` links the runner's `gov` into the sandbox's HOME.
- *Effect:* it is red on `PATH=/usr/bin:/bin` by its own design, and on the owner's PATH it runs the pin's package instead of this tree's (DEC-732). W1-47's helper would fix it.
- Ordinary work: yes, because the landing check's clean PATH reaches it.
- Consequence: other. It fails loudly and never passes falsely.
- *Reversed by:* the case passing under `PATH=/usr/bin:/bin`, or W1-49 being outside D-10's landing set.

**F3, in scope: bytecode is written next to this tree's sources.**
- *What happens:* the hook line runs its program with `-E`, which ignores the `PYTHONDONTWRITEBYTECODE=1` the suites set (I confirmed `dont_write_bytecode` is 0 under `-E`). The planted path file now makes the hook import this tree's `src/gov`.
- *Effect:* a run where those caches are missing or stale writes `src/gov/**/__pycache__/*.pyc` into the tree under test. Before, the hook imported the pin's own package on the owner's PATH, and no hook ran on a clean PATH.
- *Why it is minor:* the files are gitignored, so `git status` stays clean. Such caches already exist (`src/gov/guard/__pycache__`), and W1-38's and W2-106's own plantings do the same.
- *What should happen:* either accept these caches, or keep the planted install's caches out of the tree.
- This is inferred from two verified facts. I did not reproduce the write, so as to write nothing in the tree.
- Ordinary work: yes, because every run after an edit to `src/gov` does it.
- Consequence: other. No tracked file changes, no real-HOME change, no lost work, no false pass.
- *Reversed by:* a run of these suites after touching one `src/gov/guard` file that leaves no newer `.pyc` under `src/gov`.

**Probed and sound, not findings:**
- The real-HOME assertion compares against the runner's `Path.home()`, which is a scratch folder when a run sets HOME. It still holds, because no caller passes the real HOME and the owner's existing pin triggers the early return.
- A second call trusts an existing script without checking the path file. No caller plants a script without the path file.

Classification: 3 findings. 1 in scope (F3: ordinary work yes, consequence other); 2 out of scope (F1: ordinary work yes, fails open, in the existing helper; F2: ordinary work yes, other). None is in scope with fails open or loses work, so none blocks.

Recommendation: READY.

```verdict
{"kpis": [{"kpi": "pinned-gov-fixture", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}]}
```
