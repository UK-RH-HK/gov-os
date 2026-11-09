# W2-141 — the independent test designer's brief, D-6 part 2: S4, the suites' temporary call-log folder (DAEO-xwro)

You are the independent test designer for **W2-141** (`.tickets/DAEO-xwro.md`: read it, with its new line **S4**, its
new failure line, the new path `tests/conftest.py` and its "D-6 part 2 placed here" note). W2-141 is merged into
`w2/integrate`. Your earlier cases are in `tests/acceptance/W2-141/`. Read your README and `w2_141_hook_support.py`
first.

## Why
ACT-GUARD-CALLLOG-1 (DEC-1106 (2), applied `010e1f0c`) made the guard hook append one line per decision to
`~/.gov-os/guard-calls/<UTC day>.jsonl` (hashes only). It is keyed by `salt.key` in that folder. The hook reads
`GOV_GUARD_CALLS_DIR` (an absolute path) in place of that folder; see `.claude/hooks/pretooluse.py`, the constant
`CALLS_ENV`, which you may read.

The owner's DEC-1108 (5): "the suites that run the live hook pointed at a temporary folder as a follow-up". DEC-1109
(2) restarted it within D-6 part 2. Today every test that runs the hook with the real HOME appends to the real log.

## What S4 says, briefly
Every test that runs the guard hook (the live `.claude/hooks/pretooluse.py`, or the template's copy) runs it with
`GOV_GUARD_CALLS_DIR` set to a folder of its own under the test's temporary folder:
- set once for the whole suite in **`tests/conftest.py`**, as an autouse fixture beside `_own_vector_cache`, which
  sets `GOV_VECTOR_CACHE` the same way;
- carried by every suite that builds the hook's environment itself (an `env=` dict made from scratch, or with
  `GOV_*` stripped).

No test reads or writes `~/.gov-os/guard-calls`.

## What to do (tests only; there is no engineer for this line)
1. **`tests/conftest.py`:** one autouse fixture that `monkeypatch.setenv`s `GOV_GUARD_CALLS_DIR` to a per-test folder
   under `tmp_path_factory.getbasetemp()`. It is made only when used, like the vector cache. Change nothing else in
   the file.
2. **Find the suites that run the hook with an environment they build:**
   - a names-only search for `pretooluse.py`, `.claude/hooks` and `env=` under `tests/`, then read those places;
   - where a suite builds the environment from nothing, or drops `GOV_*`, make it carry `GOV_GUARD_CALLS_DIR` from
     `os.environ`;
   - inside `tests/acceptance/**`, a change to another ticket's folder carries `Rewrite-Reason: DEC-1108 (5)` in the
     commit body and a one-line note in that folder's README;
   - you may change `tests/unit/hooks/test_live_hook.py` (it is in W2-141's paths);
   - any **other** `tests/unit/**` file that needs the change: **do not edit it**. List it, with the line, as a
     discovery for the CTO.
3. **One case** in `tests/acceptance/W2-141/`, for example `test_w2_141_calls_dir.py`:
   - run the hook once with the conftest's environment, on a planted repository through your support module;
   - assert that one line landed in the temporary folder, and that the scratch HOME's `.gov-os/guard-calls` does not
     exist;
   - give it a guard that the fixture's variable is an absolute path under the base temp.
4. **Verify:** a scoped run with a **scratch HOME** of `tests/acceptance/W2-141/` and `tests/unit/hooks/` and of each
   suite you changed. It leaves no `<scratch HOME>/.gov-os/guard-calls` folder. List the before and after.

Map the case to **S4** and its failure line. Update your README with S4's line and a note for DEC-1108 (5) and
DEC-1109.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-141-d6-tests`, branch `w2/W2-141-d6-tests`, made from
  `w2/integrate`. You write `tests/conftest.py`, `tests/acceptance/**` (as above) and
  `tests/unit/hooks/test_live_hook.py`. Nothing else.
- **Your record:** your whole return is your session's **final message**, in full.

## Rules
- **Never read this ticket's implementation (G-14):** `src/gov/guard/reads.py`, `src/gov/guard/role_paths.py`,
  `.claude/hooks/role_reads.py` and `tests/unit/guard/test_w2_141*`. `pretooluse.py` is not W2-141's implementation:
  you may read it for `CALLS_ENV` and the log's form.
  - **The exclusion line (DEC-1093 (2)):**
    - recursive grep carries `--exclude=reads.py --exclude=role_paths.py --exclude=role_reads.py`;
    - Grep or Glob carries `!src/gov/guard/reads.py` and `!src/gov/guard/role_paths.py`.
- **Never run anything that writes the real `~/.gov-os/`, `~/.claude/`, the crontab or settings.** Every run uses a
  scratch HOME (link `.local/lib` to the user site so pytest is found).
- No GPU, model, network or installs.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Every run goes through the heavy slot that `EMG-common.md` names, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-141-d6-tests/src`. Never the full suite.
- **DEC-1080:** one simple command per Bash call, and no `cd … &&` chains.
- **Search again once (DEC-1092 (1)).**
- **Commit** on `w2/W2-141-d6-tests` with
  `--trailer "Task: DAEO-xwro" --trailer "Implements: DEC-1108, DEC-1109" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished. Waits and stops by pid only.

## Return
- The twelve labelled fields of `EMG-common.md` (the sandbox and `ps` checks first).
- The conftest change, quoted.
- Each suite changed, with its reason.
- The new case: node id, expectation, result.
- The scoped runs' counts, and the scratch HOME's before and after.
- The unit files you did not edit, as `discoveries`.
- The commit.
