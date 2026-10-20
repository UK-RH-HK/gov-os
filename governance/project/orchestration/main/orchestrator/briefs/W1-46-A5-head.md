You are the ticket lead for ticket `DAEO-jdqr` (`W1-46`, "Worker session launcher (gov launch)"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-46` on branch `w1/W1-46`. You run the ticket loop for this one ticket.

## State of this ticket

- Acceptance tests exist from test design batch 1 (`e0f083eb`): 257 cases, 22 of them `local_only`; red was confirmed (32 failed, 120 errors, 105 passed). The suite's README holds the designer's readings and its seven packages. Nothing is implemented.
- All seven packages are now decided. Read them in the register: DEC-231 (command line `gov launch <role> <ticket> [-- <CLI arguments>]`), DEC-232 (two short real sessions, `local_only`, not opt-in), DEC-233 (a `sandbox` key in the repository's settings makes the launcher refuse), DEC-234 (the temp-directory assertion stays), DEC-240 (DP-4), DEC-241 (DP-5), DEC-242 (DP-7). Also DEC-205, DEC-215, DEC-216, DEC-218, DEC-219, DEC-223 and DEC-180.
- The ticket's `allowed_paths` now include `governance/project/research-allowlist.yaml` (DEC-241).

## What you do, in order

1. **Test design batch 2** (brief A1, a fresh designer, profile FULL, DEC-221). It revises the suite for the decisions, before implementation (so these are revisions before implementation, not rewrites after):
   - DEC-233 turns the "ignore or refuse" case into a refusal test.
   - DEC-240: a research install is inside its experiment folder when the session's working directory is the folder or below it, or the command first changes into it with `cd`. `uv --directory` and `uv --project` are not followed; no test for them (the reviewer probes them later).
   - DEC-241: `governance/project/research-allowlist.yaml` extends the kernel default; the starting hosts are listed in DEC-241 (the designer copies them from the register). A test shows the built settings carry them, and a `local_only` test shows the sandbox accepts these entries, the `readthedocs.io` subdomain form included: EXP-001 tested only an empty list. If the sandbox refuses an entry's form, that is a package, not a guess.
   - DEC-242: refusals for an unknown ticket, a ticket that isn't `in_progress`, a ticket of another role, and a research ticket whose `allowed_paths` isn't exactly one experiment folder; a missing `held-out.yaml` launches normally with no held-out rule. This replaces batch 1's reading wherever it said a missing file refuses; a missing key, an empty list or a broken file still refuses (DEC-218, DEC-223).
   - If `tests/acceptance/W1-07/test_w1_07_registry.py` has a `NOT_IMPLEMENTED` case for `launch`, it is revised with the reason "planned: command implemented" (DEC-190); `gov launch` is not one of the twelve reserved operations, so the designer checks first.
2. **Check red** yourself.
3. **Engineer** (brief A2, fresh). Allowed paths are in the ticket. The launcher reads `held_out_paths` from the held-out file in code; no person or agent reads, prints or types the value. Proportion rule DEC-135; no guard decision may fail open.
4. **Verify** every suite. The `local_only` cases start two real short sessions: run them in the background. The W1-04 suite must still pass (KPI).
5. **Reviewer** (brief A3). Give it these described behaviours to probe, besides its own: `uv --directory` and `uv --project` pointing outside the experiment folder (DEC-240); `ln` into `.gov-runtime/` outside `scratch/`; a here-string `sh <<< "…"` writing outside the repository; the holder exception following a symbolic link; `uv run -w<pkg>` joined; an `env` or `command` prefix before an install; a duplicate YAML key in the allowlist or the held-out file.
6. If the per-session temp directory cannot be set, return the shared `$TMPDIR` as a residual (DEC-234) and have the designer revise the test as a planned revision.

Note: `spike-sandbox/EVIDENCE.md`, which the ticket cites, is not in the repository; the sandbox configuration is in EXP-001's record and ADR-0002.

