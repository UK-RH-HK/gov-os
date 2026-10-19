
## 66. Owner answers of 2026-10-04 on the parallel run's open packages (register v0.66, appended by the W1 orchestrator on branch `w1/integrate`)

The owner answered every package and question open at the stop of the parallel run: W1-49's lost-content finding,
W1-09 DP-4 and DP-6, W1-12 DP-5, W1-46 DP-10 to DP-12 and DP-14 to DP-16, W1-25 DP-1 and DP-3 with the watchdog
defaults, W1-50 DP-4 and DP-5, W1-10 DP-3, and four confirmations. DEC-306 to DEC-324 record them. DEC-325 is the
orchestrator's delegated decision that DEC-324 asks for. The orchestrator prompt is v4.1 (`3ccbf75c`): its section 6
now also delegates stricter-only decisions.

### DEC-306 — W1-49: the in-place-save race is a residual until W1-29 replaces the checkpoint file
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-49's second review, finding 1 · **Under:** DEC-264, DEC-250, CAP-37
- **Decision:**
  - If the session saves its checkpoint in place between the PreCompact hook's read and its write, the new text can
    be cut or overwritten. That is accepted as a residual in `bootstrap.md` until W1-29 replaces the checkpoint
    file. W1-49 is merged and closed as built.
  - When it is closed the orchestrator tells the owner, who updates section 7 of the orchestrator prompt (DEC-250).
  - The auto-compact setting takes effect in sessions started after the merge.

### DEC-307 — W1-09 DP-4: a ticket names its specification in a `specification` key
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-09 package DP-4 option (a), as built · **Under:** CAP-31, MR-2
- **Decision:** A ticket key `specification` holds a record id. The specification is closed when that record's
  status is `CLOSED`; any other status, or no such record, means not closed, and the ticket is not READY. A ticket
  without the key is not held. W1-12, W1-13 and W1-14 make a specification a record and write the key accordingly.

### DEC-308 — W1-09 DP-6: an open decision package names its waiting tickets in `constrains`
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-09 package DP-6 option (a), as built · **Under:** CAP-34.e
- **Decision:** A decision package names the tickets that wait on it in `constrains`, which is already a graph
  edge, and it is open while its status is `PROPOSED`. A ticket constrained by an open package is not READY. W1-34
  keeps the key and the status; W1-11 decides what a declined or stale package does.

### DEC-309 — W1-12 DP-5: the CIT-E rule is stated in the schema, and W1-26 checks the link
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-12 package DP-5 option (a), as built · **Under:** CAP-30.e
- **Decision:** W1-12's schema carries the source and the extension rule of `readiness-dimensions.yaml`, and its
  suite goes red when the YAML changes without the schema. The check that a change to the taxonomy or to the YAML
  has a linked CIT-E record goes to W1-26, as a new KPI line in its own commit (`Task: DAEO-fygv`), with W1-26 added
  as a provider of CAP-30.e. W1-12 is merged and closed as built.

### DEC-310 — G-07 and G-09 may be read from the S0b2 output, by exact file path
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the question DEC-304 left open · **Amends:** DEC-304 · **Under:** DEC-198, DEC-222
- **Decision:** A product-spec worker may read the text of G-07 and G-09 from the S0b2 output in
  `~/gov-os-workbench/s0b2/out/`, by exact file path only, and never anything under `s0b2/probe/`. Its draft settles
  what the kernel `templates/openspec/` folder holds, under the delegation rule.

### DEC-311 — W1-46 DP-14: literal deny rules for the names that exist at launch, and `ln` judged by the guard
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-14 option (b) · **Amends:** DEC-180 · **Under:** DEC-176, CAP-58
- **Decision:**
  - The launcher's settings carry a literal `Edit` deny rule for every name that exists under `.gov-runtime/`
    outside `scratch/` at launch, plus the freeze flag.
  - The guard treats the destination of `ln` as a write target.
  - A new name created under `.gov-runtime/` at the OS level after launch is a residual in `bootstrap.md`.
  - The two live `ln` tests are revised to target existing names: rewrites after implementation, reason "owner
    decision".
  - The engineer's wider guard change is accepted: `.gov-runtime/` outside `scratch/` is denied by the guard to
    every role, not only to the orchestrator.

### DEC-312 — W1-46 DP-16: the owner committed `.claude/agents/research.md`
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-16 option (a) · **Under:** DEC-163, DEC-254, CAP-22.d
- **Decision:** The owner committed `.claude/agents/research.md` in the W1-46 worktree as `b311c4c`, with the
  trailers `Task: DAEO-jdqr` and `Role: owner`, while no session ran there. If the containment check flags that
  HEAD move at the next call in that worktree, it is a record of an owner action (DEC-254), not a defect.

### DEC-313 — W1-46 DP-10: `gov launch` refuses permission bypass and added directories
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-10 option (a) · **Under:** CAP-61, DEC-161
- **Decision:** `gov launch` refuses `--dangerously-skip-permissions`, `--permission-mode bypassPermissions` and
  `--add-dir`, in any position, and the matching settings keys (`permissions.defaultMode: bypassPermissions`,
  `permissions.additionalDirectories`). `--allow-dangerously-skip-permissions`, which the package also named, is
  refused with them: that only makes the launcher stricter.

### DEC-314 — W1-46 DP-11: no launch when the project's settings don't register the guard
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-11 option (a), as built · **Under:** CAP-61, CAP-58
- **Decision:** `gov launch` refuses when the project's settings do not register the guard. The launcher does not
  register the hooks itself. As built, the refusal covers a missing or unwired `.claude/settings.json`,
  `disableAllHooks`, `--bare`, and `--setting-sources` with any value.

### DEC-315 — W1-46 DP-12: `Edit` deny rules for acceptance tests, tickets and `.claude` in worker sessions
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-12 option (a) · **Under:** MR-3, CAP-58, CAP-61
- **Decision:** The settings the launcher builds carry `Edit` deny rules for `tests/acceptance/**` (every role but
  the independent test designer), `.tickets/**` and `.claude/**`. W1-46 gets a new KPI line for them, in its own
  commit (`Task: DAEO-jdqr`).

### DEC-316 — W1-46 DP-15: `cdn-lfs.huggingface.co` leaves the research allowlist
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-15 option (a) · **Amends:** DEC-241
- **Decision:** `cdn-lfs.huggingface.co`, which does not resolve, is dropped from the starting hosts. The owner
  extends the list later if research needs it.

### DEC-317 — W1-25 DP-1: one generic change in `src/gov/cli/main.py`, made in W1-46's round
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-25 package DP-1 option (b) · **Under:** CAP-27, CAP-28
- **Decision:** In W1-46's engineer round, one generic change is made in `src/gov/cli/main.py`: each command's
  handler, arguments, act paths and exit codes come from its own module, including command-defined exit codes
  beyond 0 and 1. W1-07's suite is re-run. `src/gov/cli/**` is already in W1-46's `allowed_paths`. Later command
  tickets no longer need `main.py`. W1-25's engineer starts once this change is merged.

### DEC-318 — W1-50 DP-4: a commit that names a closed ticket, or one never started
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-50 package DP-4 · **Under:** DEC-255, CAP-58.h
- **Decision:** A commit whose trailers name a closed ticket is judged by that ticket's role and `allowed_paths`
  only if it is an ancestor of the ticket's close commit; otherwise it is a finding. A commit that names a ticket
  that was never started is a finding.

### DEC-319 — W1-50 DP-5: in a worker's call, another role's trailer is a finding
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-50 package DP-5 option (b) · **Under:** DEC-255, MR-3, CAP-58.h
- **Decision:** In a worker's call, a commit whose `Role` trailer differs from the caller's role is a finding.
  Own-trailer judging applies only in an orchestrator session's own call. W1-50's implementation follows W1-46's
  merge, as planned (DEC-256).

### DEC-320 — W1-25 DP-3: only orchestrator-role sessions run `gov checkpoint`
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-25 package DP-3 · **Under:** CAP-37.a, CAP-20.a, DEC-176
- **Decision:** There is no guard or containment exception. Only orchestrator-role sessions, the main orchestrator
  and the ticket leads, run `gov checkpoint`, and they may already write `docs/checkpoints/<ticket>/`. Workers don't
  checkpoint; their state is their commits.

### DEC-321 — W1-25: the watchdog's defaults
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the defaults DEC-281 left open · **Extends:** DEC-281 · **Under:** CAP-37.c
- **Decision:** By default a checkpoint is stale after 4 hours, or after 20 commits on the branch since the
  checkpoint.

### DEC-322 — W1-10 DP-3: only orchestrator-role sessions write the live store
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-10 package DP-3 option (a) · **Under:** DEC-176, DEC-311, CAP-58
- **Decision:** Only orchestrator-role sessions write the live `.gov-runtime/store.db`. Tests and workers build
  their own stores in temporary directories. Revisit when `gov rebuild` is wired (W1-27).

### DEC-323 — Confirmed: the seven canaries, the root allowlist, the compaction warning and DEC-299
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER · **Confirms:** DEC-286, DEC-290, DEC-283, DEC-299
- **Decision:** The owner confirms the seven dev canaries (DEC-286), the root allowlist of DEC-290, and DEC-283's
  warning after every compaction, which W1-29 may refine. That a project can remove or rewrite a template rule
  (DEC-299) stays a residual.

### DEC-324 — W1-15: the token rule's over-blocking is fixed before adoption
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the W1-15 residual "the rules over-block" · **Under:** CAP-03.a
- **Decision:** The token rule's over-blocking is fixed before W1-41 (adoption), by requiring a digit or mixed
  case in the token body. The orchestrator decides the form under delegation and adds the KPI line to the ticket it
  chooses.

### DEC-325 — The token rule fix: its form, and W1-16 carries it
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** DEC-324; the W1-15 reviewer's suggested repair; confidence medium · **Under:** DEC-287, DEC-298, CAP-03.a
- **Decision:**
  - The `gov-token` rule flags a prefixed string (`sk`, `pk`, `rk`, `tok`, then `_` or `-`) only when the body
    after the prefix holds at least one digit, or both an upper-case and a lower-case letter. The length floor of
    16 characters stays.
  - The requirement is part of the rule itself, in both `template/.gitleaks.toml` and the root `.gitleaks.toml`,
    and never an allowlist: the pre-index filter ignores allowlists (DEC-298). gitleaks' expression language has no
    look-ahead, so the engineer chooses how the rule expresses it.
  - The canary rule is unchanged, and the seven dev canaries are still detected.
  - W1-16 (`DAEO-lkeb`) carries the fix: it depends on W1-15, starts next, and already has a secret-exclusion KPI.
    It gets a KPI line and W1-15's rule paths, in a commit with `Task: DAEO-lkeb`. W1-15's acceptance tests that
    assert the old rule are revised by W1-16's test designer, as rewrites after implementation, reason "owner
    decision".

| Version | Date | Change |
|---|---|---|
| 0.66 | 2026-10-04 | Owner answers: DEC-306 (W1-49: the in-place-save race is a residual until W1-29), DEC-307 and DEC-308 (W1-09 DP-4 and DP-6, as built), DEC-309 (W1-12 DP-5 as built; W1-26 checks the CIT-E link), DEC-310 (G-07 and G-09 read by exact path), DEC-311 to DEC-316 (W1-46 DP-14, DP-16, DP-10, DP-11, DP-12, DP-15), DEC-317 (W1-25 DP-1: one generic change in `main.py`, in W1-46's round), DEC-318 and DEC-319 (W1-50 DP-4, DP-5), DEC-320 and DEC-321 (W1-25 DP-3 and the watchdog's defaults), DEC-322 (W1-10 DP-3), DEC-323 (confirmations), DEC-324 (the token rule is fixed before W1-41). Delegated under DEC-220: DEC-325 (the fix's form; W1-16 carries it). |
