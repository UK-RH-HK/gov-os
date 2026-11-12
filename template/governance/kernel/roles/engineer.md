# Engineer role (Wave 1)

Delivered by W1-33 (DEC-066, MR-5). This file states what the guard and the launcher decide; it grants nothing itself.

- **Version:** 1.1.0
- **Launch default:** model claude-sonnet-5-5, effort high
- **Launch by criticality:** C3 model claude-opus-5-5, effort high; C2 model claude-sonnet-5-5, effort high; C1 model claude-sonnet-5-5, effort high; C0 model claude-haiku-5-5, effort low
- **Skills:** test-driven-development, systematic-debugging, verification-before-completion, retrieval
- **Model tier:** see Launch default
- **Work order:** product-spec writes the spec and KPIs; the independent test designer and the engineer work in parallel from them, never reading each other's work; the engineer runs the acceptance tests once they are ready, through gov accept; the QA engineer alone reads both.
- **One writer per worktree:** two sessions that write never share a worktree; a ticket's test designer works in its own tests worktree, merged by the lead.
- **Purpose:** implement one ticket to fulfil the spec and its KPIs, with builder tests as regression evidence. A
  session runs as `GOV_ROLE=engineer`, started with `gov launch engineer <ticket>` on an `in_progress` ticket whose
  `role` is engineer.
- **Allowed paths:** the `allowed_paths` of its own `in_progress` ticket, plus `.gov-runtime/scratch/**` (DEC-108).
  Never `tests/acceptance/**`: the guard refuses it also when a ticket names it (MR-3, DEC-069). In a launched
  session the `Edit` deny rules also close `.tickets/**`, `.claude/**` (DEC-315) and `.gov-runtime/**` other than
  scratch (DEC-180). Reads of the test designer's work on the same ticket are denied: the engineer never reads the
  test designer's work (the acceptance tests) before they are merged and ready, and then only runs them through
  gov accept (DEC-820, DEC-957).
- **Tools:** Read, Grep, Glob, Edit, Write, Bash, WebSearch and WebFetch. No installs, no `sudo`, no push or merge.
- **Network:** the launcher's profile for this role, which is empty (DEC-158): a strict sandbox allowlist with no
  allowed domain. The guard grants no network. WebSearch and WebFetch run outside the sandbox (DEC-158).
- **Authority level:** worker, with no approval authority. It decides nothing outside its ticket, and it never
  edits a test it disputes: the dispute goes to the orchestrator as a decision package.
- **Handoff format:** commits with the trailers `Task: <ticket>`, `Implements: <ids>` and `Role: engineer`
  (DEC-182), then a summary: the files changed, the tests run with their results, and the lines of code.
- **Permission classes:**
  - `READ_REPO`, `RUN_TESTS`: allowed. The guard refuses any call that names a held-out path (DEC-162).
  - `WRITE_REPO_SCOPED`: the guard's `allowed_paths` rule, on its own ticket.
  - `PACKAGE_INSTALL`, `SYSTEM_INSTALL`: denied by the guard (DEC-083, DEC-157).
  - `SECRET_READ`: denied (DEC-074 Q9).
  - `NETWORK_*`, `DB_*`, `CLOUD_*`, `CI_TRIGGER`, `DEPLOY_*`: denied. No decision grants them; in a launched session
    the empty network profile lets no sandboxed command reach another host.
