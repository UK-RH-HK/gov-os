You are the ticket lead for ticket `DAEO-xxgp` (`W2-48`, "Test-result cache at close and in the leads' runs, glued to pytest-testmon, subprocesses seen, a nightly full run"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-48` on branch `w2/W2-48`. You run the ticket loop for this one ticket and return one summary. You are a headless session: nobody answers questions while you work, and only your final message is read.

**This is run 2, the resume after your run 1's PACKAGES.** `git log --oneline -1` must show `17ddaf09`, and `git status --short` must show nothing but sandbox placeholder files, if any (anything else: stop and return PACKAGES naming it). Read `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree.

## Your packages, decided (all in the register after step 1's merge)

- **DEC-875 (delegated):** P-W2-48-4 (a): your paths gain `src/gov/close/command.py`, for the `--no-cache` option and the call into the cache only (your ticket file on `w2/integrate`, `e6976ef3`). P-W2-48-6 (a): a fresh test designer revises the planted change of `test_a_declared_command_runs_again_only_when_a_file_of_its_input_globs_changes`, `Rewrite-Reason: DEC-875`. P-1, P-2, P-3 confirmed as your test designer wrote them. P-A: you measure the time saved this round.
- **DEC-876 (owner): P-W2-48-5 (b) with (c), on five conditions:**
  1. **Fail safe:** anything the cache still cannot see stays "always run". Each widening of (b), coverage passed into children started with their own environment, and `git` and similar programs keyed by their version, **is proven by a test in which a change reached only that way invalidates the cached result.**
  2. **(c) is done:** the path map now declares `test_inputs: ["fixtures/**", "template/**", "schemas/**"]` (`65039414`); the register and the ticket files are left out on purpose.
  3. **The backstop:** the nightly full uncached run (DEC-852 item 3); a test that fails there but passed through the cache is a P1 package.
  4. **A target, measured and reported:** at least **60 to 70 % of tests reused on a typical ticket's close,** and **a typical close under about 15 minutes.** Measure it as a close measures it: the whole regression, cached, after a change typical of a ticket (for example a change to one module under `src/gov/` and its tests), on a quiet machine, against the uncached run on the same head. **If the round falls short, do not start another open-ended round:** return a package with a fallback (for example, running only the suites the change's paths affect, with the nightly full run as backstop), its measured effect, and its risk.
  5. **Size:** you are at about 1,680 lines (source 1,117: `testcache/__init__.py` 440, the plugin 364, `commands.py` 165, `__main__.py` 81, `close/cache.py` 67; builder tests 364; the research record 199) against 220, for what is meant to be mostly glue around testmon. **Simplify where you can rather than add.** Your return says where the lines went, and what this round removed.

## This run's order

1. **Merge `w2/integrate` into this branch** (DEC-750's form: `--no-ff`, `Task: DAEO-xxgp`, `Role: orchestrator`, `Implements: DEC-726`; never `-s ours`; never drop a side). It brings W2-53's close (its close record; `core-schema` is RED on its `type: close` until W2-02 merges, a known red), W2-62 and W2-63, `test_inputs`, your widened paths, and DEC-861 to DEC-876.
2. **Tests:** a fresh independent test designer, launched sandboxed (`--effort xhigh`): P-W2-48-6's revision, and the proving cases of condition 1 (one per widening: a change reached only through a child started with its own environment; a change of the `git` version).
3. Check red yourself.
4. **One engineer round** (launched sandboxed, `--effort high`), carrying everything (DEC-802): the close's wiring in `command.py`; (b)'s two widenings; the cache-only reds of your run 1 (W1-07's copied-repository setup race; latency cases slowed by coverage: such cases run without the cache's measurement, or always run); the lead's run showing its failure output; `GOV_TESTCACHE_HOME` not inherited by the tests' own processes; and simplification.
5. **Verify in full** (the loop's step 4, with the pre-close collection, DEC-868), then **the timed pair** of condition 4, reported in `docs/research/W2-48-cache-choice.md`.
6. **FULL review** (brief A3 with `JUDGEMENT.md`, `--effort max`), with condition 1's fail-safe rule as its focus. Commit the probe record only if it passes.
7. Return DONE with the measured figures and the lines' account, or PACKAGES with condition 4's fallback.

---

