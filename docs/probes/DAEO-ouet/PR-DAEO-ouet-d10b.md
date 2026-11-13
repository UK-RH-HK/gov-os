---
type: probe
task: DAEO-ouet
reviewer_session: b523b83c-3e5a-47b3-867f-7763bc80fcb3
implementer_session: the D-10 red-fix list's test designer of f1bb1819f and the merge cade65dfe (the command lists record brief, links and plan; its session log went with its removed worktree)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 8b31965edae8a9f173fa5a365922eaae2c3d32a5
---

# Fresh probe of W2-96 (DAEO-ouet) at 8b31965edae8, round 2, after D-10's command-list merge (DEC-895)

- **Why fresh:** probe_impact.py named it stale again: the merge c3bf5a547 changed four judged files (W1-07's list, its README and recorded-commands case, W1-32's command set).
- **Brief:** .gov-runtime/scratch/orchestrator/briefs/D10-W2-96-probe-r2.md; a fresh, read-only independent reviewer, effort max; verdict.py READY; the orchestrator's judgement: pass.
- **The reviewer's record follows, as returned.**

**Verdict: pass for W2-96 at `8b31965edae8`.** `accept` is still recorded and offered. The declared `gov accept W2-96` still fails four lines with no failed case, exactly as this morning, and still passes 109 of 109 with both opt-ins. I wrote nothing in any tree. My full record follows.

---

# Probe record: W2-96 (DAEO-ouet), the second fresh full probe after D-10's command-list merge (DEC-895)

**Sandbox check (Step 0, `EMG-d4b-launched.md`): passed.**
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-W2-96','w').write('x')"` failed as required: `OSError: [Errno 30] Read-only file system`. No file was created.
- (b) `echo sandbox-trial | git hash-object -w --stdin` returned `1ae28402a109c3397a44b19239a00adfa9472eb0`, and `git update-index --refresh` exited 0.

**ps check:** I ran the brief's command as given, `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"`. It printed nothing.

- **task:** DAEO-ouet (W2-96). A fresh, read-only full probe of `gov accept` at integrate `8b31965edae8`. The merge `c3bf5a547` changed four of its judged files when D-10 recorded `brief`, `links` and `plan` beside `accept`. KPI id: `w2-96-full-probe`.
- **decisions:** DEC-970, DEC-753, DEC-959, DEC-1061, DEC-1109, DEC-895, DEC-953, DEC-1040, DEC-801, DEC-808, DEC-1010, DEC-1014.
  - None of them is superseded or PROPOSED. DEC-970, DEC-1061 and DEC-1065 are ACCEPTED. DEC-753 is DONE (it was ACCEPTED; DEC-1098 (3)).
- **status:** DONE. The verdict is **pass**. There are two findings. Both are out of scope and fail closed, so neither blocks.
- **work_completed:**
  - Read the ticket, this morning's probe, both D-10 reviews (commands, accept maps), `D10-REDS.md`, JUDGEMENT, EMG-common, INTENT-DEC-1052 and DEC-1065.
  - Read the revision's diff, `commands.py`, the runner's map reader and per-line rule, the CLI's command discovery, the opt-in lists, and W2-96's README map.
  - Computed W2-96's judged files the way `probe_impact.py` does, and checked which of them changed since `9ca161a6fe38`.
  - Ran the four runs listed under **tests**.
  - Compared the tree before and after, including ignored files.
- **files_changed:** none.
  - `git status --porcelain` is empty, and HEAD is still `8b31965edae8`.
  - `git status --porcelain --ignored` is identical before and after. No new ignored entries, and no bytecode was refreshed.
  - Outside the trees: Step 0's blob and index refresh, as the brief requires, and my scratch folder under the sandbox's TMPDIR, now removed.
  - **A false refusal worked round (DEC-1040 item 3):** the guard refused `rm` of the symlink in my scratch folder (F2). I removed the scratch folder whole with `rm -r` instead. That path is inside `/tmp`, and `rm -r` removes a link without following it. Afterwards I checked that `/home/usain/.local/lib/python3.12/site-packages/pytest` is still there.
- **evidence:**
  - Probed commit `8b31965edae8`, checked at the start and at the end. Session `b523b83c-3e5a-47b3-867f-7763bc80fcb3`. `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-ouet`.
  - `git log 9ca161a6fe38..8b31965edae8 -- tests/acceptance/W1-07 tests/acceptance/W1-32 tests/unit/accept src/gov/accept` shows 3 commits: `cade65dfe`, `f1bb1819f` and `b0384ac62`. The brief named only the first two (see discovery 1).
  - In all of `src/` since this morning, only `src/gov/check/commands.py` changed (+2 lines).
  - My scratch folder peaked at 20K and 6 inodes (`du -sh`, `du -s --inodes`). It is now removed.
- **tests:** every run went through `heavy_slot.sh`. Each used a scratch HOME whose `.local/lib` linked to the user site: gov strips `PYTHON*` from its child, so `PYTHONUSERBASE` alone never reaches it. Each also used my own TMPDIR and `PYTHONDONTWRITEBYTECODE=1`. The pytest runs used `-p no:cacheprovider -o tmp_path_retention_policy=failed`.
  1. **W1-07's recorded-commands file and W1-32's command set**, with `--optin lifted,breadth` and the exclusion flags `-m "not local_only" -k "not real and not green_here and not time_limit"`:
     - **13 collected, 13 passed in 9.04 s.**
     - `[accept]`, `[brief]`, `[links]` and `[plan]` all passed.
  2. **`tests/unit/accept`**, with the same flags, serial: **98 passed in 80.61 s**, the same as this morning.
  3. **`gov accept W2-96`, the declared way** (`PYTHONPATH=src <pin>/bin/python -m gov.cli.main accept W2-96`):
     - **exit 3, `outcome: fail`**, `error_kind` null.
     - 74 passed, 0 failed, 0 skipped; 15 of them unmapped.
     - Passed per line: success 1–5 were 11/15/16/9/18 and failure 1–4 were 12/16/9/16.
     - success-2, success-5, failure-1 and failure-4 answer `fail` with no failed case.
  4. **The same command with `GOV_TESTS_OPTIN=lifted,breadth`**, as a confirmation:
     - **exit 0, `outcome: pass`**, 109 passed, 0 failed, 0 skipped.
     - Passed per line: success 1–5 were 14/22/23/11/36 and failure 1–4 were 18/23/11/31; 23 were unmapped.
  - Runs 3 and 4 match this morning's probe figure for figure.
  - The exclusion flags left nothing out of runs 1 and 2. They cannot be passed through `gov accept`. W2-96's acceptance folder has no `local_only` marker and no test name with those words, so they would leave nothing out there either.
- **discoveries:**
  1. **`b0384ac62` (Task DAEO-f58b)** changes W1-32's failed-removal cases: its README, `added_cases`, `launch` and `launch_support` files.
     - None of these is a W2-96 judged file.
     - W1-32's command-set case imports `w1_32_support`, not the launch support that commit changed.
     - Across W2-96's judged files, only these changed since this morning: the command lists (`commands.py`, three W1-07 files, W1-32's command set), W2-96's own W1-27 and W1-46 map fix (`48c2cd33b`, reviewed READY), and this morning's probe record.
     - Nothing changed in `src/gov/accept`, `tests/unit/accept` or `tests/acceptance/W2-96`.
  2. **The review record the brief names is not in the probed tree.** `governance/project/orchestration/reviews/D10-commands-review.md` does not exist at `8b31965edae8` in this worktree. I read it from the main tree's working copy, which is on `w2/integrate` at the same head. It says READY:
     - F1: the citation for `brief` is wrong; in scope, consequence other.
     - F2: the default run never compares the code's list with the tests' list; out of scope, consequence other.
  3. **The maps review's F1 still holds at this head.** The reader drops the KPI lines after a comma, which fails open; it is out of scope. `runner.py` is unchanged, and the item is filed as "a row for W2-96" (`D10-REDS.md:245-246`). W2-96's own report is not affected: it names all nine lines.
  4. **This morning's F3 (bytecode written in `src/`) neither reproduced nor was reversed.** This reused worktree already held the 10:33:22 `__pycache__` folders, and valid bytecode is not rewritten.
  5. **A run without the opt-ins skips all 10 of W1-07's recorded-commands cases** (`optin-lifted-breadth.txt:42-44`). In that run, `accept`'s recording is checked only by W1-32's pin, which reads W1-07's list, and by the unit case r13. This is the commands review's F2.
- **risks:**
  - Until F1 is settled, a close or a lead's check that runs `gov accept W2-96` the declared way gets exit 3. W2-96 closes at the lift (P1-13), so the CTO's choice (`D10-REDS.md:243-244`) is needed before then, or the close runs with both opt-ins.
  - The comma-drop row (fails open, in W2-96's code) is still open. W2-96's close is the natural place to decide it.
- **lessons:**
  - Take the `--ignored` baseline before running anything. In a reused probe worktree it already holds the previous probe's bytecode, so a bytecode check needs a tree without it.
  - When scratch holds a symlink, remove the scratch folder whole. The guard appears to resolve the link before judging an `rm` of it.
- **proposed_decisions:** none.
- **unresolved:** F1's fix, which is the CTO's choice (`D10-REDS.md:243-244`).
- **recommended_next_action:**
  - Take the probe as pass; READY is computed from the block below.
  - F1 stays the filed row, to be settled before W2-96's close.
  - F2 is a row for the guard's owner.
  - No round.

## Answers to the checks

**1. Does `accept` stay recorded and offered, and does W2-96's command-list KPI hold? Yes.**
- **The code's list:** `commands.py:14` (`accept` first) is unchanged. D-10's line (`:15-16`) appends the three new names after it. `GOV_COMMANDS` (`:20`) still includes `accept`, so `core-commands` still requires `src/gov/accept/command.py`, which exists.
- **The tests' list:** `w1_07_support.py:52` is unchanged. D-10 appends one line below it.
- **The pins:** W1-07 `test_w1_07_recorded_commands.py:50` and W1-32 `test_w1_32_command_set.py:84` both name `accept`. Both sets stay exact: adding or dropping a name fails both.
- **Offered:** the CLI offers every `src/gov/*/command.py` (`main.py:109-114`). The `[accept]` case passed: `gov --help` lists it, and `gov accept --help` exits 0.
- **The unit case:** `test_w2_96_r13_accept_is_a_recorded_command` (`test_w2_96_run2.py:383-386`) passed.
- **DEC-970's split by line holds:** W2-96's one line is untouched. The new line is W2-20's (Task DAEO-r30l), and W2-20 holds the rest of the file under DEC-970.

**2. Counts:** the four runs are in **tests** above.
- **Does this morning's finding still hold? Yes, unchanged.** The four failing lines are exactly the lines on README rows 71 and 72.
- Those rows name `test_r15_eight_thousand_empty_sibling_folders_are_removed_within_the_bound` and `test_r16_a_sigterm_to_gov_alone_while_a_nested_run_sleeps_leaves_no_process_and_nothing_later`. D-4's cut still lists them at `optin-lifted-breadth.txt:1164` and `:1167`.
- The runner fails a line whose named test matches no collected case (`runner.py:435-438`).
- No case failed in any run. With both opt-ins those two cases run and pass, and every line passes.

**3. Judgement: pass** for W2-96 at `8b31965edae8`.
- gov's code and W2-96's tests are byte-identical to this morning's passing probe.
- The revision only appends three names beside `accept` and keeps every set exact.
- The only finding against the default run (F1) fails closed and comes from D-4's cut, not from this revision.

**Probed and found sound:**
- `accept` is recorded and offered in all five places above.
- Only `commands.py` changed in `src/` since the passing probe.
- The declared run and the opted-in run match this morning's results figure for figure.
- The four failing lines fail only on the two uncollected cases, which pass when collected.
- The tree was left as I found it, ignored files included.

## Findings

Classification: 0 in scope; F1 is out of scope, ordinary work yes, consequence other; F2 is out of scope, ordinary work yes, consequence other. No round is proposed.

**F1. The declared `gov accept W2-96` still reports a failing run although every case it runs passes.**
- **What was done:** I ran `PYTHONPATH=src <pin>/bin/python -m gov.cli.main accept W2-96` at `8b31965edae8`.
- **What happened:**
  - It gave exit 3, `outcome: fail`, with 74 passed and 0 failed.
  - success-2, success-5, failure-1 and failure-4 failed with no failed case, because each names a case D-4's cut leaves out of the default run.
  - With both opt-ins, the same command passes 109 of 109.
- **What should have happened:** a run where every case passes should pass. Either the named cases run by default, or the map names cases that do.
- **Cause:** D-4's cut (DEC-1061), not this revision and not `src/gov/accept`. It is already filed at `D10-REDS.md:240-244` as the CTO's choice.
- **What would reverse it:** a declared run at `8b31965edae8` that exits 0 with every line passing, or the two functions being collected without the opt-in.
- Ordinary work: yes, because any engineer, lead or close that runs the declared command at integrate meets it, with no construction needed.
- Consequence: other (it fails closed: a false failure, with no failing case hidden).
- Scope: out.

**F2 (row, the guard, not W2-96). The guard refused removing a symlink inside my own scratch folder.**
- **What was done:** after the runs, I ran `rm` on the link `<sandbox TMPDIR>/w296p2/home/.local/lib`, which points to `/home/usain/.local/lib`. A scratch HOME needs that link to run `gov accept`, because gov strips `PYTHON*` from its child.
- **What happened:**
  - The guard refused it: "a reviewer or auditor writes only its own review or audit record …, its own scratch, or /tmp (DEC-953 item 2)".
  - The path is under `/tmp`. The likely cause is that the guard resolves the link to its target, which is outside `/tmp`.
  - `rm` on a link removes only the link.
- **What should have happened:** it should have been allowed, as removing the folder that holds it was.
- **What would reverse it:** the guard's code showing that it does not resolve the last path component for `rm`, which would mean the refusal had another cause; or the same `rm` being allowed on a re-run.
- Ordinary work: yes, because a reviewer who runs `gov accept` with an empty HOME, as the briefs ask, needs such a link and is told to clean its scratch.
- Consequence: other (it fails closed: a harmless clean-up was refused, and nothing was lost).
- Scope: out.

```verdict
{"kpis": [{"kpi": "w2-96-full-probe", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
