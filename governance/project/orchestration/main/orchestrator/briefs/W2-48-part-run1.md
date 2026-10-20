You are the ticket lead for ticket `DAEO-xxgp` (`W2-48`, "Test-result cache at close and in the leads' runs, glued to pytest-testmon, subprocesses seen, a nightly full run"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-48` on branch `w2/W2-48`, cut from the integration branch `w2/integrate` at `{BASE}`. You run the ticket loop for this one ticket and return one summary. You are a headless session: nobody answers questions while you work, and only your final message is read.

**This is run 1.** `git log --oneline -1` must show `{BASE}`, and `git status --short` must show nothing (anything else: stop and return PACKAGES naming it). Your ticket file `.tickets/DAEO-xxgp.md` holds the KPIs; read it first. Every decision this brief cites is in your worktree's register.

## Why you start now, ahead of everything else in keystone 2 (DEC-869)

Every `gov close` runs the full regression: W2-53's closes of 2026-10-20 took 76 minutes each (14,600 tests, `-n auto`, then a serial batch of 263). The owner put this ticket in the very next free slot after W2-53's close, ahead of every other keystone-2 ticket, because it shortens every close after it.

## The decisions for this run (all in your register)

- **DEC-726, restated by DEC-843:** reuse by behaviour (each planted change re-runs every dependent test; a change outside every input reuses; every reuse recorded with the run it came from; a failed result never reused); glued to pytest-testmon and coverage, with `--testmon-env` a hash of the declared data globs and the test command.
- **DEC-852's three conditions:** (1) the code a test runs in a separate process (`python3 -m gov …`) is seen, through subprocess coverage configured and tested, or any test that starts a process always re-runs; proven by a change reached only through a subprocess; (2) the same cache serves the leads' suite runs in their worktrees, with the same rules and `--no-cache`; a lead's own entries stay in its worktree and are never read by a close; (3) one command runs the nightly full uncached regression on `w2/integrate`'s head and names every test that fails there but whose latest cached result was a pass or a reuse.
- **DEC-868:** the pre-close gate (collection in one process, `gov check` after the rebuild, a fresh checkpoint) is W2-07's to build into `gov close`; your cache must not change what the gate's collection sees.
- **DEC-083 and Q-13, the install:** pytest-testmon and coverage are not installed (`/usr/bin/python3` has pytest 9.0.3 and pytest-xdist 3.8.0 under `~/.local`, installed with `pip install --user --break-system-packages`). The owner installs them; the orchestrator brings the package. **Until the owner's install is on this machine, run the tests-first step and the choice research only**; the engineer starts after it. Check with `/usr/bin/python3 -c "import testmon, coverage; print(testmon.__file__, coverage.__version__)"`.
- **DEC-838, DEC-839:** the full window; `--effort xhigh` for the FULL test designer (a measured trial), `high` for the engineer, `max` for the reviewer.

## Facts for the design

- `gov close` builds its run in `src/gov/close/command.py:798-860`: `PYTHONPATH=<root>/src`, the caller's test-runner variables stripped, `python3 -m pytest <tests> -q -p no:cacheprovider --tb=line --no-header -n <workers>`, then the serial-only cases (`serial_only.PLUGIN`) in a second run, and the results plugin (`results.PLUGIN`). The cache call goes in `src/gov/close/cache*` only.
- **Many tests start `gov` in a subprocess** (`python3 -m gov.cli.main …`, `gov check`'s declared checks): coverage's own subprocess measurement (`[run] patch = subprocess` in coverage 7.10+, or a `.pth` start-up) is the route; prove it with a planted change to a module only a subprocess imports.
- **xdist:** testmon and `-n` must be shown to work together, or the close's parallel run keeps `-n` and the cache selects before it.
- `-p no:cacheprovider` is in every close run: keep testmon's data in `.testmondata` (or its configured path) written only by main-tree closes, from a clean tree at a recorded commit.
- The record of the choice is `docs/research/W2-48-cache-choice.md`: the planted change set (an imported module, a fixture or `conftest.py`, a configuration file, a data file, a module reached only through a subprocess, a file outside every input) and the time saved on this repository's regression.

## This run's order

1. **Tests first:** a fresh independent test designer, launched sandboxed (`--effort xhigh`), on every KPI line, FULL proportion (planted changes in a temporary repository built by the test, never this tree's `.testmondata`).
2. Check red yourself.
3. **The install gate:** if testmon and coverage are not importable yet, write your checkpoint and wait (re-check every 10 minutes with the line above, for up to four hours), then go on; if they never appear, return PACKAGES naming it.
4. **Implement:** a fresh engineer, launched sandboxed (`--effort high`), inside the allowed paths only.
5. **Verify** as the loop says, plus one full uncached regression and one cached re-run on the same head, both timed.
6. **FULL review:** a fresh read-only reviewer (`--effort max`, A3 with `JUDGEMENT.md`). Commit the probe record only if it passes.
7. Return.

---

