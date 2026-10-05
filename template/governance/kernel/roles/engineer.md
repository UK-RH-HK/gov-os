# Engineer role (Wave 1)

Delivered by W1-33 (DEC-066, MR-5). This file states what the guard and the launcher decide; it grants nothing itself.

- **Purpose:** implement one ticket until its acceptance tests pass, with builder tests as regression evidence. A
  session runs as `GOV_ROLE=engineer`, started with `gov launch engineer <ticket>` on an `in_progress` ticket whose
  `role` is engineer.
- **Allowed paths:** the `allowed_paths` of its own `in_progress` ticket, plus `.gov-runtime/scratch/**` (DEC-108).
  Never `tests/acceptance/**`: the guard refuses it also when a ticket names it (MR-3, DEC-069). In a launched
  session the `Edit` deny rules also close `.tickets/**`, `.claude/**` (DEC-315) and `.gov-runtime/**` other than
  scratch (DEC-180).
- **Tools:** Read, Grep, Glob, Edit, Write, Bash, WebSearch and WebFetch. No installs, no `sudo`, no push or merge.
- **Network:** the launcher's profile for this role, which is empty (DEC-158): a strict sandbox allowlist with no
  allowed domain. The guard grants no network. WebSearch and WebFetch run outside the sandbox (DEC-158).
- **Model tier:** standard; the orchestrator may name another model after `--` on the launch command.
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
