You are the ticket lead for ticket `DAEO-r30l` (`W2-20`, "Machine-wide resource gate"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-20` on branch `w2/W2-20`.

**This is run 3: the merge-back and the re-scope (DEC-941 item 2, DEC-950 item 2).** `git rev-parse --short=12 HEAD` must show `1a54976c7a71`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- your run-2 checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md` ("What the resume lead does");
- the ticket file (`.tickets/DAEO-r30l.md`), with its KPIs as the orchestrator amended them for this run;
- DEC-950 (item 2), DEC-942 (items 1 to 3), DEC-947 (all five items), DEC-898 (item 1) and DEC-941 (items 2 and 6). DEC-742 and DEC-747 are the values this run replaces;
- `src/gov/resources/gate.py`, `command.py` and `src/gov/launch/gate.py` as built, and `tests/acceptance/W2-20/README.md`;
- the orchestrator's interim gate, which the product must do as product code (read them, copy nothing):
  - `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/gate_check.py`;
  - `gate-config.json` and `lead_mem.py` in the same folder.

## Why you start now

- **W2-20 is built work,** held since 2026-10-17 for the close order (DEC-737). It is one of the nine held tickets to be merged back (DEC-941 item 2), in priority 4 (DEC-946). W2-21, and with it K6, waits on it.
- **The rules changed after it was built, and the owner chose to re-scope it now (DEC-950 item 2, P-W2-20-SCOPE (a)).** The built gate has:
  - a fixed 4 GiB floor, with no verification reserve and no working size;
  - the 1-minute load only;
  - a ceiling of 8 weighted sessions;
  - no disk or inode reading, although that KPI has been on the ticket since `efa2e4b0` (DEC-898).

  The owner's rules are now DEC-942 (no fixed number of leads; the load gate) and DEC-947 (the memory reserve; a 3 GiB floor; re-measured weekly).
- **Until it lands,** the orchestrator runs the gate by hand (`tools/gate_check.py`).
- **Where the branch stands:**
  - 10 commits ahead of `w2/integrate` and 811 behind; merge base `5bc27b7ce022`;
  - `w2/W2-01` (`DAEO-g0ip`), the dependency, is closed.
  - **A dry merge (`git merge-tree --write-tree`) reports one conflict, in `tests/acceptance/W1-07/README.md`.** The two sides are adjacent lines:
    - `w2/integrate` adds W2-57's section "## Revision (W2-57, `Rewrite-Reason: W2-L409: the failure text is kept`)" just before the heading "## The four commands of DEC-542 …";
    - your branch rewrites that heading ("…, and W2-20's `resources` in their form: five recorded") and the table and count below it.
  - `tests/acceptance/W1-07/w1_07_support.py` and `tests/acceptance/W1-26/README.md` merge without a conflict.

## The decisions for this run

1. **Merge `w2/integrate` into `w2/W2-20`** (`git merge --no-ff w2/integrate`, with `Task: DAEO-r30l`, `Implements: DEC-950` and `Role: orchestrator` in the final trailer block). Never `-s ours`, never drop this ticket's side (DEC-750 item 3).
   - **The W1-07 README conflict is a test designer's to resolve (MR-3, DEC-906), never yours.**
     - Leave the merge in progress, and start a fresh independent test designer (`gov launch`, sandboxed, `--effort xhigh`; its brief must not set `TMPDIR`). Its only task is that one file:
       - both sides kept as written: W2-57's revision section, then your branch's heading, table and count;
       - no conflict marker left, nothing else changed;
       - the file staged.
     - Check `git diff --cached -- tests/acceptance/W1-07/README.md` yourself, then commit the merge with your trailers. Its message says the file was resolved by the test designer.
     - If the commit gate refuses that commit, the test designer commits the merge with its own `Role:` and the same `Task:` and `Implements:` trailers.
     - **If the resolution cannot be mechanical** (both sides kept as written, neither side's meaning changed): `git merge --abort`, and return PACKAGES naming it.
   - Any other conflict: `git merge --abort`, and return PACKAGES naming each file.
   - After the merge, `grep -c '^### DEC-950' docs/DECISION_REGISTER.md` must show 1. If not, stop and return PACKAGES: the trailer gate would refuse every `Implements: DEC-950`.
2. **Rebuild** from this worktree's code (check `gov.__file__` first): `flock /tmp/gov-os-rebuild.lock` around the rebuild command, never `--no-embeddings`. Name every entry or record the load lists as `invalid`; `invalid: []` is expected.
3. **Design first, short.** In your scratch, `.gov-runtime/scratch/lead/design.md`, at most a page, in behaviour. It goes into the test designer's and the engineer's briefs as text, never as names of code (DEC-462). It says:
   - **the one configuration file:** the machine-wide `~/.gov-os/machine/gate.json`, as built. It holds every value the gate uses:
     - the memory floor (3,145,728 kB);
     - one verification run's peak (7,404,492 kB);
     - the working size per session (2,140,236 kB);
     - the disk floor (100 GiB) and the inode floor (10,000,000);
     - the path the disk is read at;
     - the verification lock's path;
     - the GPU margin (10 %).

     Each value carries its date and its source. A value missing or malformed shuts the gate, naming it;
   - **the sessions' live memory:** each registered session's whole process tree, summed from its processes' resident memory at the time of the check. A session whose process runs inside another live session's tree is counted in that one and charged no working size of its own: a lead's tree holds its workers;
   - **the gate,** open only when every condition holds:
     - load: `min(load1, load15) < nproc`;
     - memory: `MemAvailable + the live sessions' memory ≥ floor + verification peak + working size × (running sessions + 1)`;
     - disk: free space and free inodes at or above their floors;
     - the GPU, for a start that declares a GPU need only;
     - **no ceiling** on sessions or leads, weighted or not;
   - **the re-measure** (DEC-947 item 3):
     - `gov resources` records a sample of each live session's tree, noting whether a verification run holds the configured lock;
     - from the samples, it writes the verification peak (the largest sample) and the working size (the largest sample outside verification) with the date into the file, showing old and new side by side;
     - the reading names a measured figure older than seven days as due;
   - **the GPU, minimal** (DEC-950 item 2: nothing in the Gov OS needs one today):
     - a start that declares a need in memory opens only when one GPU's free memory, read with `nvidia-smi`, is at least the need plus 10 %;
     - no `nvidia-smi` or no GPU shuts such a start, naming it;
     - a start with no declared need never reads the GPU;
   - **a source the tests can plant for every new reading,** as the built ones have: the 15-minute load from the same file, the process table, the disk's reading and `nvidia-smi` on `PATH`;
   - **what stays:**
     - the registry;
     - the stale-entry clearing;
     - `--register`, `--check` and the reading's named reasons;
     - the start check's refusal with exit 3;
     - "a session in another repository counts".

     `--heavy` stays accepted, but carries no weight in a ceiling.
4. **Tests first,** by a fresh independent test designer (`gov launch`, sandboxed, `--effort xhigh`; its brief must not set `TMPDIR`), in `tests/acceptance/W2-20/`, one case or more per amended KPI line:
   - **load:** a short peak (1-minute load over `nproc`, 15-minute load under) does not shut; both at or over shuts, naming both;
   - **memory:** the boundary of the reserve, each side, with 0, 1 and 3 running sessions:
     - the live memory added back;
     - a nested session counted once and charged no working size;
     - the verification peak charged once, not per session;
   - **no ceiling:** 20 light and heavy live sessions with memory, load and disk to spare: the gate opens;
   - **disk:** free space and free inodes, each below its floor, each shut and named; a gate that reads one but not the other fails a case;
   - **the configuration:**
     - every value read from the one file;
     - a missing or malformed value shuts, naming it;
     - a figure older than seven days named as due;
   - **the re-measure:** planted samples in, the two figures out with the date, and old and new side by side;
   - **the GPU:**
     - a declared need against a planted `nvidia-smi`, at the 10 % margin, each side;
     - none on `PATH` shuts, named;
     - a start with no declared need never runs it (a planted `nvidia-smi` that records its calls);
   - **fail closed:** each reading that cannot be taken shuts its condition, named;
   - **the existing cases that pin DEC-742's values** are revised, each with `Rewrite-Reason: DEC-950 item 2 (DEC-942 item 1, DEC-947)` and each named in the README:
     - the 4 GiB floor;
     - the 1-minute load alone;
     - heavy sessions counting double towards 8;
     - DEC-747's sessions boundary.

     No other expectation is lowered (DEC-906).

   Everything runs under a temporary `HOME` from planted sources: never the real `~/.gov-os/`, `/proc` or GPU. **Check red yourself:** every new case red on the merged head, none skipped, none erroring at collection.
5. **The engineer** (fresh, `gov launch`, sandboxed, `--effort high`) works only in `src/gov/resources/**`, `src/gov/launch/gate*` and `tests/unit/resources/**`.
   - **Not `src/gov/check/commands.py`:** its one line is in already, and W2-16 holds the file now. If a change there is needed, return PACKAGES.
   - The launcher's call of the gate is W2-21's, not this ticket's.
6. **Verification: in full,** in the close's form (LEAD-w2-common), plus `pytest --collect-only -q` over `tests` (DEC-868). The full run goes under `flock /tmp/gov-os-verify.lock`.
   - **Look hardest at:**
     - `tests/acceptance/W2-20/` and `tests/unit/resources/`;
     - `tests/acceptance/W1-07/`, `W1-26/` and `W1-32/`: the command list pins `resources`, and the merged README;
     - `tests/acceptance/W2-57/`.
   - **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists, you and your workers run no suite and no full run. Wait, and go on the moment it is gone.
   - **Closes:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, start no worker and no suite.
   - **The 01:00 cut-off (owner, DEC-939 item 6):** from about 01:00, start no full verification run that `nightly_estimate.py estimate` says cannot finish before 02:00.
   - **Known:**
     - W1-42's accepted reds;
     - the load-sensitive cases (W1-05's and W1-19's latency cases), re-run alone;
     - W2-54's green-here cases may time out under load (row W2-L429), so re-run them alone.
   - Any other red is named with its cause.
7. **Repair: at most one batch.**
   - A red in this ticket's code: a fresh engineer, in the ticket's allowed paths only.
   - A red in `tests/acceptance/**`: a fresh independent test designer (DEC-906), each change with a `Rewrite-Reason:` and no expectation lowered.
   - Then the red cases and their suites again; a second full run only if code changed.
8. **Reviews: none.** W2-20 is STANDARD and its ticket asks for none: no reviewer before the merge (DEC-498), and no probe record exists to go stale (DEC-895 does not apply).
9. **Checkpoint:** `gov checkpoint` at each round boundary and at the end (DEC-511), committed with this ticket's trailers.
10. **Your trailers** (LEAD-w2-common, DEC-927 item 2): run `trailer_gate.py` on your worktree before you return.
11. **Return** DONE (green; ready to merge into `w2/integrate`, then the close queue), or PACKAGES.
    - Carry run 2's residuals as they stand, and add any new one.
    - Name, for the orchestrator, the command that replaces `tools/gate_check.py` once this is merged and pinned, and the one that replaces `lead_mem.py --summary`.

**The park rule (DEC-941 item 2):** if the work grows beyond this one run, stop and return PACKAGES naming the cost. That covers:
- a second repair batch;
- a fix outside the ticket's paths;
- a red whose cause is another ticket's code;
- a design point the decisions above do not settle.

Name what is left, its size in lines and hours, and what waits on it (W2-21, and K6).

**Running beside you:**
- W2-16 holds `src/gov/check/commands.py`.
- W2-60a and W2-56 hold `src/gov/launch/launcher.py`, `role.py`, `record.py`, `sandbox.py` and `environ.py`. `src/gov/launch/gate*` is yours.
- W2-05 holds the git-environment lines across `src/gov/**/*.py`. Add no git call.
- W2-67 holds `tests/unit/close/**` and `tests/unit/guard/**`.
- W2-84 holds `src/gov/guard/reads.py`.
- W2-61 holds `src/gov/retrieval/measure.py`.
- W2-71 holds `src/gov/secrets/**`.
- W2-77 holds `src/gov/close/nightly.py`.

Do not touch them. If a fix needs a change there, return PACKAGES.

**Estimate:** about 200 code lines and 20 to 25 test cases, about 1.5 to 2 lead-days:
- the merge, the test designer's resolution and the rebuild, about 45 minutes;
- the design note and the tests, about 2 hours;
- the engineer, up to two 90-minute budgets;
- one full run, about 95 minutes;
- the return.

If your session nears its end first, write your checkpoint and return PACKAGES naming what is left; a fresh lead resumes from the checkpoint.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
