# Independent assessment of the Gov OS, October 2026: lens H, Test strategy (audit, research, design)

You are an independent auditor (`GOV_ROLE=independent-auditor`). The Wave 2 orchestrator started you on the owner's order of 2026-10-21.
- Seven auditors each assessed one lens (A to G), and a further session wrote the synthesis of A to E. Their reports are in `docs/assessment/2026-10/`. You are a further, separate auditor on one lens, lens H.
- You wrote none of the work you assess, and nobody expects a particular result from you. Report what you find, with its evidence.
- Read everything your lens needs.

## The purpose of the Gov OS (the owner's words)

The Governance OS exists for four things:
- the project's memory lives in the repository instead of in agents' memory;
- agents are safe and governed;
- the owner stays in control;
- the owner's products, EXAMIN, UPIM and ASMO, are built faster and more safely.

## The state when this brief was written (2026-10-21, 09:xx BST)

- **Repository:** `/home/usain/Dynamic-Agentic-Engineering-OS`, branch `w2/integrate`, head `21302ae9`.
- **Wave 2 is running.**
  - One ticket lead works now: W2-58, in `/home/usain/gov-os-worktrees/W2-58/`.
  - A queue of six closes (`gov close` of W2-02, W2-54, W2-62, W2-63, W2-50 and W2-58) runs after W2-58 merges, one at a time, in a quiet window. While a close runs, the file `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists.
  - Other ticket branches have worktrees under `/home/usain/gov-os-worktrees/<W2 id>/`; `git worktree list` gives their heads.
- **The `gov` on PATH** (`/home/usain/.local/bin/gov`) is the pinned judge: a wheel built from `fecb870c`, installed in `~/.local/share/gov-os/pin-fecb870c/`. It is not this repository's editable `src/`. Say which code each command you run used.
- **The test cache was withdrawn** (DEC-880, the owner, 2026-10-21; package P-W2-48-8 (b) with (d)). W2-48 glued a test-result cache to pytest-testmon and coverage. It reused 11.5 % of the tests and saved 3 % of a close: 79 minutes against 81 uncached. The cause: this repository's tests mostly run `gov` as a separate process, which testmon cannot see. Its four review findings F1 to F4 were fail-opens.
  - Branch `w2/W2-48` is kept as the record, unmerged: its code, its tests, and `docs/research/W2-48-cache-choice.md` (read with `git show w2/W2-48:<path>`).
  - Its lead's records are copied to `governance/project/orchestration/worktrees/W2-48/lead/`; `packages-run2.md` holds the measured causes and the timed pair.
- **New ticket W2-66** (`.tickets/DAEO-c1uz.md`; its card is in `docs/plan/WAVE_2_WBS.md` §2) is the lite form of W2-38, brought back from Wave 3: path-scoped regression at close, with the owner's four conditions and a 15-minute target.
  - **Its test designer starts only after your report,** so that its card can take your findings.
  - Your design is therefore expected to be concrete enough for a test designer to write its acceptance tests from.

## Your lens: H. Test strategy

The owner's text, word for word:

> Lens H has three parts: AUDIT what the Gov OS does today, RESEARCH how industry solves it and which free tools we can glue, then DESIGN what the Gov OS should do, for itself and for the repositories it governs. Use the layered model as the reference: L1 immediate (seconds), L2 affected components (minutes), L3 merge (5 to 30 minutes), L4 nightly full run, L5 release qualification.
>
> PART A, AUDIT: the state of testing in the Gov OS today, with evidence.
> A1. The test estate, measured: the number of tests by kind (unit, per-ticket acceptance, live or harness, dev-tier, load-sensitive); the share that run gov as a separate process; each suite's runtime; the top 20 slowest tests; tests that never failed in Wave 1 or Wave 2; duplicate tests; test-suite size against code (about 8 test lines per code line in Wave 2).
> A2. Testing in practice, by role and step: what a test designer writes and how (red first, proportionality, the README), what a worker runs while it works, what a lead runs before it returns, what a close runs, what the pre-close gate runs, what the gates W2-24 and W2-46 will run. Where the same tests run twice or more, and what that costs.
> A3. Decided against built: every decision on testing and verification (among them DEC-726, DEC-757, DEC-760, DEC-766, DEC-780, DEC-852, DEC-868, DEC-869, DEC-871, P-W2-48-8) and whether it is built, partly built, or only decided. Is the nightly full run running? Are the hooks and CI on? What do the ratchet lists (accepted_reds, load_sensitive) hold, and is each entry still justified, with a fix ticket?
> A4. Reliability: every refused close of Wave 1 and Wave 2 with its cause, classed (the ticket's code, the environment, load, the process, the orchestrator's own slip); flaky tests and how they are handled today; how a failure is localised today, and how long that takes.
> A5. Evidence today: what a close record says about which tests ran, were skipped or were reused, on which commit, and whether any record could be read as full validation when it wasn't.
> A6. Test quality: a sample mutation test on two or three modules (in your clone) to show whether the tests catch planted faults.
>
> PART B, RESEARCH: industry practice and free tools.
> B1. From official and primary sources (engineering publications of large software organisations, the documentation of build and test tools, peer-reviewed work on test selection): how teams with thousands of tests choose what to run at each layer; test impact analysis and dependency-aware selection; risk-based widening; caching, parallelism and sharding; flaky-test management; failure localisation (minimal reproduction, git bisect); and how they record what a run did and did not validate. Cite each source.
> B2. Free tools to glue: for each need, the mature, maintained, free tools for Python (and the equivalents for Rust and TypeScript, for UPIM and ASMO later), for example import-graph or dependency-graph test selection, changed-file test pickers, duration-based sharding, flaky detection and timeouts, mutation testing, and the affected-targets approach of large build systems as a reference. For the best two or three candidates, trial them on your clone: does each work on a repository whose tests mostly run gov as a separate process (where testmon failed, W2-48)? Measure selection accuracy (does a planted change select the tests that catch it) and time saved. Name each tool's licence, maintenance state and fit.
>
> PART C, GAP ANALYSIS AND DESIGN.
> C1. A gap table: for each industry practice of Part B, what the Gov OS does today (Part A), what is missing, its cost today in time or risk, and the proposed fix (glue a named tool, or build), with the ticket that should carry it.
> C2. The target strategy for the Gov OS itself, per layer: its trigger; how tests are selected (a path-to-suite map; dependency-aware selection through the code graph's own traversal, DEC-859, or a glued tool); risk rules that widen to the full suite for the shared core; parallelism and sharding; what W2-48's failure teaches about caching here; flaky tests (a quarantine with a fix deadline, never permanent); failure localisation; the integrated commit tested again after merges; and removing duplicated runs.
> C3. Evidence: every close record states its validation scope (scoped, integration or full), which tests ran, which were skipped and why, and on which commit; no agent or record claims full validation when only a selection ran. Say where this lives (the close record type, W2-02; the close, W2-07).
> C4. As part of the Gov OS product: how this becomes a kernel capability that gov close, the leads and the workers use, and that an adopted repository receives with the kernel (a "test orchestration and evidence" capability: change impact, risk-based selection, execution, failure diagnosis, the evidence record).
> C5. Adopted repositories, starting with EXAMIN (pytest; a product suite run with -m "not live"; a governance suite under xdist; Postgres): how the Gov OS learns their test commands (W2-19); their layers and selection; live and database-dependent tests; their nightly run and CI; what gov close requires there; a time budget per close; and what changes for Rust (UPIM) and TypeScript (ASMO).
> C6. Map everything to the plan (W2-07, W2-19, the new path-scoped ticket, W2-37, W2-38's Wave 3 part, W2-43, W2-45, W2-57, the nightly run) and the Contract (CAP-53.b, CAP-39.c and any other), and end with owner packages in the six-part format: what to glue, what to build, what to remove, in which ticket, in what order, with estimates.

The new path-scoped ticket the owner names is W2-66 (`DAEO-c1uz`); its owner conditions are DEC-880 item 2.

