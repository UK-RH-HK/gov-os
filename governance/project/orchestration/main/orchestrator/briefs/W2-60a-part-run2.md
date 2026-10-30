You are the ticket lead for ticket `DAEO-cv58` (`W2-60a`, "The role, its skills and its model and effort loaded at launch; the launch record"), profile FULL, keystone 3, working only in the worktree `/home/usain/gov-os-worktrees/W2-60a` on branch `w2/W2-60a`.

**This is run 2: round 3, the last, under the owner's exception to DEC-413 (DEC-951, P-W2-60a-ROUND3 (a)).** `git rev-parse --short=12 HEAD` must show `323f04554607` (your run-1 checkpoint writes it `323f04550b7c`; the commit is `323f04554607`). `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- your run-1 checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md`;
- your run-1 return: the last JSON object's `result` in `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/W2-60a-A5-run1.json` (the packages, the residuals, the default line's form);
- the package `governance/project/orchestration/packages/P-W2-60a-ROUND3.md` (main tree);
- review 2's draft, `.gov-runtime/scratch/lead/probes/PR-DAEO-cv58-review2-DRAFT-fail.md` (F1);
- the ticket file: its paths now hold `tests/unit/launch/test_runs.py`, `test_w1_28.py`, `test_w1_32.py` and `tests/acceptance/serial-only.txt`;
- DEC-951, DEC-413, DEC-916, DEC-233, DEC-313 and DEC-786.

## Why you start now

- **Run 1 returned PACKAGES at 09:15.** Review 2, the last under DEC-413, failed on F1:
  - a launch from a linked worktree checks the worktree's own `.claude/settings.local.json`;
  - the CLI (2.1.292) loads that session's local settings from the **main checkout's** file;
  - eight keys planted there each launched a worktree worker unrefused: an added directory, a sandbox block, a bypass mode, `disableAllHooks`, an `agent` key and three compaction spellings;
  - the CLI's own `/add-dir` "remember" writes there in ordinary work. It fails open.
- **The owner's answer (DEC-951): (a), the last round, scoped strictly to the five items below.**
  - If review 3 finds another fail-open case, you return PACKAGES. There is no fourth round.
  - Delegated alongside, and in force:
    - P-W2-60a-6 (a) and P-TD-4 are items (iii) and (iv);
    - P-W2-60a-3 goes to W2-56's refusal list, not to this round;
    - P-TD-3 and P-W2-60a-1 are accepted;
    - P-RETRIEVE is P-R1 of the common brief;
    - P-W2-60a-4's (a) is taken in now as item (ii), where run 1 recommended (b).
- **The owner on proportion:** 2,980 lines of acceptance tests for 713 lines of code is out of proportion. This round's tests are the minimum that shows each item.
- **Where the branch stands:** 12 commits ahead of `w2/integrate` and 82 behind; merge base `a1629f1860ca`.
  - A dry merge (`git merge-tree --write-tree`) on `816f764f36b8` reports **no conflict**.
  - Since the base, integrate has changed nothing under `src/gov/launch/`, `tests/unit/launch/`, `tests/acceptance/W2-58/`, `tests/acceptance/W1-38/` or in `tests/acceptance/serial-only.txt`.

## The five items, and nothing else

- **(i) Local settings for a worktree launch.** For a launch from a linked worktree, the repository-settings check also reads the main checkout's `.claude/settings.local.json`.
  - It refuses on that file exactly what it refuses on the tree's own copy: review 2's eight keys and every other refusal of DEC-233, DEC-313 and the hooks check.
  - **Fail closed:** when the main checkout cannot be found, or its local file exists and cannot be read or parsed, the launch is refused with the cause. `record.py`'s main-checkout look-up already refuses a bare repository or an unreadable `.git`; reuse it, never a second look-up.
  - A main checkout with no local file adds no refusal. A launch from the main checkout is unchanged.
- **(ii) The adopted layout's role file.** The role file is read from `governance/kernel/roles/<role>.md` when the tree has no `template/` (an adopted repository, P-W2-60a-4).
  - Where `template/` exists, nothing changes. Where neither file exists, the launch is refused as now.
  - The recorded hash is the hash of the file read.
- **(iii) Fixture role files for W2-56's 26 unit cases:** `tests/unit/launch/test_runs.py` (6), `test_w1_28.py` (2) and `test_w1_32.py` (18).
  - Each bare tree gets a role file with the version and default lines, in the form run 1 gave W2-11, so the launch is no longer refused for want of one.
  - Nothing else in those cases changes.
- **(iv) The nightly-route line,** P-TD-4's text exactly: `tests/acceptance/W2-60a/test_w2_60a_live_sessions.py  # nightly: live-session: one real engineer session through gov launch shows its role text, its named skill and a start with no connector, user-level agent or skill, or memory`. It goes at the end of the list's live-session section.
- **(v) W2-58's live phantom-deletion pair** (`test_a_launched_session_shows_no_phantom_deletion`, engineer and test designer).
  - Run 1's revision `abfa9e5ba13c` writes the fixture's role file after the fixture's commit.
  - The role file goes in before that commit, so the tree is clean when the session starts.
  - Nothing else changes.

**Out of this round:** option (b)'s `--setting-sources project`; the main checkout's `env` block (`GOV_DEV_TIERS`, W2-56's); P-W2-60a-3's arguments; and reviews 1 and 2's residuals, which stay residuals.

## This run's order

1. **Merge `w2/integrate` into `w2/W2-60a`** (`git merge --no-ff w2/integrate`, with `Task: DAEO-cv58`, `Implements: DEC-951, DEC-941` and `Role: orchestrator` in the final trailer block).
   - The merge must be clean. Any conflict: `git merge --abort`, and return PACKAGES.
   - `grep -c '^### DEC-951' docs/DECISION_REGISTER.md` must then show 1. If not, stop and return PACKAGES.
2. **Rebuild** under the rebuild lock, from this worktree's code.
3. **One test batch: a fresh independent test designer** (the pinned bare `gov launch`, as in run 1; sandboxed; `--effort xhigh`; its brief must not set `TMPDIR`). The five items go to it as behaviours, at the minimum that shows each:
   - **(i):** one case in `tests/acceptance/W2-60a/`, with the eight keys as parameters planted in the main checkout's file, plus one case for an unreadable main-checkout file;
   - **(ii):** one case for an adopted tree with no `template/`. W1-38's 5 cases stay as they are;
   - **(iii), (iv), (v):** as stated above;
   - **`Rewrite-Reason:`** each change to an existing file carries `Rewrite-Reason: DEC-951 (P-W2-60a-ROUND3)`, and P-W2-60a-6 for (iii), `abfa9e5ba13c` for (v);
   - **its limit:** about 150 lines in all;
   - **DEC-820 (c):** it never reads `launcher.py`, `role.py`, `record.py` or the CIT-E (this branch changed them). Give it what it needs of them as text: the default and version lines' form, and the main-checkout look-up's refusals.
   
   **Then check red yourself:**
   - (i)'s and (ii)'s new cases fail for their README reasons;
   - the 26 unit cases pass;
   - W1-30's `test_w1_30_r11_declared_here.py` and W2-57's `test_w2_57_serial_list.py` are green with the new line;
   - W2-58's pair passes, run alone in your own session. It is live; a sandboxed worker cannot run it.
4. **One engineer** (fresh, the pinned bare `gov launch`, sandboxed, `--effort high`) for **(i) and (ii) only**:
   - in `launcher.py` (the check) and `role.py` (the path), reusing `record.py`'s look-up;
   - builder tests in `tests/unit/launch/test_role*` and `test_launch_record*`;
   - a few lines in the CIT-E's sections on the two;
   - about 20 lines of code.
5. **A full run in the close's form** at the final head, with collect-only (DEC-868), `gov check` and `keyword_warn.py`.
   - Use run 1's holder job (`.gov-runtime/scratch/lead/probe/hold_lock.sh`, `run_verify2.py`), so the wait for the gates and the lock does not count against the two-hour limit.
   - **Known:**
     - class (i): the real role files have no default line until W2-11 (W1-28, W1-32, W1-33, W1-46, W1-50 and the serial live cases);
     - W1-38's 5 cases: name the cause each now shows. With (ii) they may fail as class (i) instead of for a missing role file;
     - the W2-56 environment case;
     - W2-66's case under DEC-919: this branch adds a conftest and changes the serial-only list.
   - The 26 unit cases and W2-58's pair must be green. Any other red is named with its cause.
6. **`gov checkpoint`** (DEC-511), committed **before** review 3, so the head it probes is the last commit but its record (run 1's deviation).
7. **Review 3:** a fresh FULL reviewer (brief A3 with `governance/project/briefs/JUDGEMENT.md` word for word, `--effort max`, read-only, launched sandboxed through the pinned launcher) on that head, given the CIT-E, review 2's draft and the five items.
   - **The probe asks above all whether any route reaches a worker's local settings unchecked:**
     - a worktree launch, and the main checkout's file;
     - a launch from the main checkout;
     - a `.git` file that points elsewhere;
     - a main-checkout file that is a link, unreadable, not JSON, or names a key in another spelling;
     - the tree's own file;
     - settings or setting sources given after `--`.
   - **It also asks:**
     - whether the adopted layout lets a launch take role text from anywhere but the file it records;
     - whether any refusal the launcher makes today no longer refuses;
     - whether (iii) or (v) lowers an expectation.
   - **If it passes:** commit the probe record under `docs/probes/DAEO-cv58/`, with the full commit id as `probed_commit`.
   - **If it fails** on a finding an honest agent can hit in ordinary work that fails open or loses work: return **PACKAGES**, the finding in DEC-818's six parts. No fourth round, and no fix in this run. The draft stays under `.gov-runtime/scratch/lead/probes/`.
   - Any other finding is a residual.
8. **Return** DONE or PACKAGES. Run `trailer_gate.py` first.
   - DONE means the probe passed, and the branch is ready to merge once W2-11's default lines are in.
   - W2-56 merges this branch back first (DEC-786).

**Running beside you:**
- W2-05 holds `src/gov/**/*.py` for git-environment lines: leave those lines as they are.
- W2-85 adds two `nightly: real-model` lines to the same list, in another section; the second ticket to merge merges the first back.
- W2-84 holds `src/gov/guard/reads.py`.
- W2-56 holds `sandbox.py`, `environ.py`, `src/gov/codeintel/**` and the rest of `tests/unit/launch/**`; W2-20 holds `src/gov/launch/gate*`.

Touch none of them. Any change you need there is PACKAGES.

**Estimate:** about 4 to 5 hours:
- about 20 lines of code and about 150 lines of tests;
- the test batch and your red check, about 1.5 hours;
- the engineer, about 1 hour;
- one full run, 50 to 95 minutes;
- review 3, about 2 hours.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
