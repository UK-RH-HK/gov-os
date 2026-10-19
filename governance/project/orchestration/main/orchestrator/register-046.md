
## 46. Parallel tickets, ticket leads, and owner answers on W1-08 and W1-46 (register v0.46, appended by the W1 orchestrator on branch `w1/integrate`)

Owner decisions of 2026-10-04. DEC-235 to DEC-237 are standing rules carried by the orchestrator prompt v4
(`governance/project/prompts/w1-orchestrator.md`, commit `e4dc57ce`), sections 3, 4, 5 and 7 and brief A5. DEC-238
to DEC-242 answer the five open packages on W1-08 (`DAEO-uudf`) and W1-46 (`DAEO-jdqr`). DEC-243 accepts the digest.

### DEC-235 — Parallel tickets in Wave 1 (a light form of CAP-23)
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v4, section 3) · **Under:** CAP-23, DEC-076 · **Amends:** the Wave 3 placing of parallel work, for this light form only; DEC-183 (a worker starts in its ticket's worktree, not the repository root)
- **Decision:**
  - Up to 6 tickets are in flight at once, each in its own short-lived worktree
    (`~/gov-os-worktrees/<W1-id>`, branch `w1/<W1-id>`, cut from `w1/integrate`). A ticket starts only when its
    dependencies are closed and its `allowed_paths` overlap no ticket in flight; overlapping tickets wait.
  - Resource gate, checked before each start: at least 4 GiB of memory available (`free -g`) and a 1-minute load
    average below the number of CPU cores. Heavy tickets (retrieval, indexing, models) count double. WSL now has
    24 GB (the owner's change to `.wslconfig`).
  - The main orchestrator merges a ticket's branch into `w1/integrate` after green, in the main tree, and re-runs
    every acceptance suite and the builder tests after each merge. Only then is the ticket closed, its worktree
    removed and its branch deleted. No worktree is left behind.
  - The full claims and concurrency capability, with the claims role and `gov claim` (CAP-23.b), stays in Wave 3.
  - The Contract gets a Wave 1 covers item under CAP-23 for this light form. The validator needs a provider ticket
    and a KPI line for every Wave 1 covers item; the orchestrator puts it on W1-42 (`DAEO-gjjf`), whose exit report
    shows it. That choice of provider is the orchestrator's, not the owner's, and the owner may move it.

### DEC-236 — Two-level orchestration: the main orchestrator and a ticket lead per ticket
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v4, sections 3 to 5 and brief A5) · **Under:** MR-5, DEC-096, DEC-156
- **Decision:**
  - The main orchestrator runs the wave: it chooses and claims tickets, starts a ticket lead for each, merges and
    re-verifies, makes delegated decisions (DEC-220) and brings the owner the rest. It reads only a lead's final
    summary, never its workers' output.
  - A ticket lead runs the ticket loop for one ticket in that ticket's worktree, as `GOV_ROLE=orchestrator` with
    the ticket in `GOV_TICKET`. It starts the workers, holds that ticket's loop count and never discloses it.
  - A lead never edits `.tickets/`, the decision register or `bootstrap.md`, never merges into `w1/integrate` and
    never pushes. It returns DONE, PACKAGES, ESCALATION or LEAD_CHECKPOINT.
  - Tickets, claims, the register and `bootstrap.md` are edited only by the main orchestrator, in the main tree.

### DEC-237 — Context limits for the main orchestrator and the ticket leads
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v4, section 7 and brief A5) · **Amends:** DEC-208
- **Decision:**
  - The main orchestrator stops with `CONTEXT_CHECKPOINT` at about 300k tokens, after a merge or a close. Leads
    keep running in their worktrees.
  - Each ticket lead, at about 300k tokens, writes `.gov-runtime/scratch/lead/CHECKPOINT.md` in its worktree and
    returns `LEAD_CHECKPOINT`; a fresh lead in the same worktree resumes from it.

### DEC-238 — W1-08: the kernel minimum per policy, and the capability list
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the W1-08 package, option (a), as the product-spec worker drafted it · **Under:** DEC-224, DEC-230, CAP-06.e, CAP-54.b
- **Decision:**
  - Kernel minimum: `hard-block` for `security`, `authority`, `test`, `change`, `human_gate` and `tool`; `warning`
    for `memory`, `context` and `checkpoint`; `informational` for `model_routing`, `budget`, `learning` and
    `archive`.
  - `capabilities` is a closed list of two: `code_intelligence` (with `languages`) and `research_corpus`.

### DEC-239 — W1-08 DP-3: the identity field keys, and the KPI line's wording
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-08 package DP-3 option (a), as drafted · **Under:** CAP-50.a
- **Decision:**
  - Shared frontmatter: `id`, `type` and `status` required; `lifecycle`, `version`, `provenance`, `supersedes`,
    `superseded_by` and `consumers` optional. The canonical path and `content_hash` are derived by `gov`, not
    stored.
  - W1-08's KPI line is reworded from "are in the shared frontmatter" to "are in the shared frontmatter or derived
    by gov", in its own commit with the trailer `Task: DAEO-uudf`.

### DEC-240 — W1-46 DP-4: when a research install is inside its experiment folder
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-4 option (a) · **Under:** DEC-163, DEC-174, CAP-25.e
- **Decision:**
  - A research install is inside its experiment folder when the session's working directory is the folder or below
    it, or the command first changes into it with `cd`.
  - `uv --directory` and `uv --project` are not followed by the rule. The reviewer probes them, as a described
    behaviour (DEC-136).

### DEC-241 — W1-46 DP-5: the research allowlist file and its starting hosts
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-5 option (a) · **Under:** DEC-158, DEC-163, CAP-61.c
- **Decision:**
  - `governance/project/research-allowlist.yaml` extends the kernel default. The owner extends the list. That path
    is added to W1-46's `allowed_paths`, in its own commit with the trailer `Task: DAEO-jdqr`.
  - Starting hosts: `github.com`, `api.github.com`, `raw.githubusercontent.com`, `objects.githubusercontent.com`,
    `codeload.github.com`, `pypi.org`, `files.pythonhosted.org`, `registry.npmjs.org`, `huggingface.co`,
    `cdn-lfs.huggingface.co`, `arxiv.org`, `export.arxiv.org`, `docs.python.org`, `docs.rs`, `crates.io`,
    `static.crates.io`, `developer.mozilla.org`, and the subdomains of `readthedocs.io`.
  - The launcher's acceptance test must show that the sandbox accepts these entries; EXP-001 tested only an empty
    list.

### DEC-242 — W1-46 DP-7: when `gov launch` refuses, and a missing `held-out.yaml`
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-7 · **Under:** DEC-161, DEC-163, DEC-223
- **Decision:**
  - `gov launch` refuses to launch for an unknown ticket, a ticket that isn't `in_progress`, or a ticket of another
    role.
  - It refuses a research ticket whose `allowed_paths` isn't exactly one experiment folder.
  - It launches normally when `held-out.yaml` is missing: no held-out rule, consistent with the guard (DEC-223). A
    product repository without a qualification oracle must still be able to launch workers.

### DEC-243 — The digest of delegated decisions DEC-226 to DEC-234 is accepted
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the orchestrator's digests · **Under:** DEC-220
- **Decision:** DEC-226 to DEC-234 stand as recorded, including the orchestrator's ranking of W1-46's DP-1 and DP-2
  as P2.

| Version | Date | Change |
|---|---|---|
| 0.46 | 2026-10-04 | Orchestrator prompt v4 and owner answers: DEC-235 (parallel tickets in Wave 1, a light form of CAP-23: up to 6 in flight, one worktree each, a resource gate, merges by the main orchestrator with every suite re-run), DEC-236 (main orchestrator and ticket leads), DEC-237 (context limits, about 300k tokens for each), DEC-238 (W1-08: kernel minimums and the two capabilities), DEC-239 (W1-08 DP-3: identity keys; KPI line reworded), DEC-240 (W1-46 DP-4: inside the experiment folder), DEC-241 (W1-46 DP-5: `research-allowlist.yaml` and its starting hosts), DEC-242 (W1-46 DP-7: refusals; a missing `held-out.yaml` launches), DEC-243 (digest DEC-226…DEC-234 accepted). |
