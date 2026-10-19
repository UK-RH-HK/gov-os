You are the ticket lead for ticket `DAEO-xog0` (`W1-33`, "Wave 1 role definitions"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W1-33` on branch `w1/W1-33`. You run the ticket loop for this one ticket. Its implementer is a product-spec worker (brief A4, ticket mode). STANDARD has no reviewer step.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on.

## State of this ticket

- No acceptance tests yet; nothing implemented. `allowed_paths`: `template/governance/kernel/roles/**`, `governance/project/roster.yaml`, `.claude/agents/**`.
- Its dependency W1-05 is closed, and so is W1-46, which placed the minimal research role: `template/governance/kernel/roles/research*`, `.claude/agents/research.md` and its entry in `governance/project/roster.yaml`. **W1-33 does not redefine the research role** (KPI line 5, DEC-163): those files stay byte-identical, and the roster entry stays as it is.
- Read the Contract's CAP-22, CAP-47 and CAP-58 with their covers items (CAP-22.a, CAP-58.b), MR-3, MR-4 and MR-5, and in `docs/DECISION_REGISTER.md`: DEC-066, DEC-083, DEC-119, DEC-154, DEC-156, DEC-158, DEC-163, DEC-182 (trailers), DEC-312 (how the research role file was placed), DEC-315. Read "W1-05 residuals" and "W1-46 residuals" in `governance/project/bootstrap.md`, and what W1-46's launcher reads from a role definition and the roster (`src/gov/launch/`): the launcher's network profile is what the role definition names (KPI line 3).
- "Framework §32 permission classes" (KPI line 3) is in the archived sources. If the Contract and the register do not give the class names, the test designer returns that as a package saying which archived section would settle it; a product-spec gap worker may then read it under DEC-222.
- **A known obstacle: `.claude/agents/`.** In W1-46 no headless session could write `.claude/agents/research.md`: the harness refused the Write tool and `cp` for two engineers and the lead, and the owner placed the file (DEC-312). Expect the same here. The implementer tries once, with the Write tool. If it is refused, it does not look for another way: it writes the definitions it would have placed, with their exact final content, under `.gov-runtime/scratch/W1-33/agents/` in this worktree, and you return a package asking the owner to copy them, naming each file. The tests for the `.claude/agents/` files stay red until then; everything else is finished first.
- Never Read, print or diff `.claude/settings.json`; never read `governance/project/held-out.yaml`.

## What you do, in order

1. `git merge w1/integrate` if it is not already up to date.
2. **Test design** (brief A1, a fresh designer, profile STANDARD). Points it settles from the sources, or returns as packages, never as guesses:
   - where a "generated definition" comes from and what generates it (the kernel role files are the source and the `.claude/agents/` files are generated from them, or both are written by hand), and how the test shows the two agree;
   - the six required fields and their key names, in the form W1-46's launcher and the guard already read (the research role file shows the form in use);
   - how "only the orchestrator may install" and "the auditor is read-only" are expressed in a definition, and what test shows them without starting a session;
   - which roster the "five roles" are checked against, given that the roster now holds a sixth, research.
3. **Check red** yourself.
4. **Product-spec worker** (brief A4, ticket mode, fresh). Estimate 300 lines.
5. **Verify** every suite under `tests/acceptance/`, `tests/unit` and the validator, with the prefix `PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH`. W1-05's and W1-46's suites read the role files and the roster and must stay green; if one of their cases pins the minimal definitions this ticket replaces, that is a planned revision by the test designer, not an edit by the implementer. Red by design, to report apart: W1-50 (26 failed, 17 passed). The two 100 ms latency cases (`test_a_call_waits_under_100_ms_p95_for_the_hook` in W1-05 and `test_decision_p95_is_under_100_ms` in W1-02) are sensitive to machine load: if one fails, re-run its file alone before you treat it as red.
6. Return DONE, or PACKAGES, with the summary, the residuals for `bootstrap.md` and the learning metrics.

