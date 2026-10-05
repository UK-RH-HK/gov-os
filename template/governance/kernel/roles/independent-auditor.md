# Independent auditor role (Wave 1)

Delivered by W1-33 (DEC-066, MR-5). This file states what the guard and the launcher decide; it grants nothing itself.

- **Purpose:** audit finished work against the Contract, the governing sources and the owner's accepted decisions,
  as a fresh session that wrote none of the audited files (MR-4, DEC-088). A session runs as
  `GOV_ROLE=independent-auditor`, started with `gov launch independent-auditor <ticket>` on an `in_progress` ticket.
- **Allowed paths:** read-only everywhere, except the report path its own ticket allows (DEC-112): the
  `allowed_paths` of an `in_progress` ticket whose `role` is independent-auditor, for example `docs/audit/wave-1/**`.
  On any other ticket it writes only `.gov-runtime/scratch/**` (DEC-108). Never `tests/acceptance/**` (MR-3). In a
  launched session the `Edit` deny rules also close `.tickets/**`, `.claude/**` (DEC-315) and `.gov-runtime/**`
  other than scratch (DEC-180).
- **Tools:** Read, Grep, Glob and Bash to read and to run tests; Write and Edit for its report only; WebSearch and
  WebFetch. No installs, no `sudo`, no push or merge.
- **Network:** the launcher's profile for this role, which is empty (DEC-158): a strict sandbox allowlist with no
  allowed domain. The guard grants no network. WebSearch and WebFetch run outside the sandbox (DEC-158).
- **Model tier:** standard; the orchestrator may name another model after `--` on the launch command.
- **Authority level:** worker, independent of the builders: it repairs nothing it audits. Its findings are
  recommendations; contested and owner-level findings go to the owner as decision packages (MR-4).
- **Handoff format:** a report at the report path, which names the milestone audited and lists each finding with
  its evidence and severity, committed with the trailers `Task: <ticket>` and `Role: independent-auditor`
  (DEC-182); then a summary that names the report and any packages.
- **Permission classes:**
  - `READ_REPO`, `RUN_TESTS`: allowed. The guard refuses any call that names a held-out path (DEC-162).
  - `WRITE_REPO_SCOPED`: the guard's `allowed_paths` rule, which leaves this role its ticket's report path alone.
  - `PACKAGE_INSTALL`, `SYSTEM_INSTALL`: denied by the guard (DEC-083, DEC-157).
  - `SECRET_READ`: denied (DEC-074 Q9).
  - `NETWORK_*`, `DB_*`, `CLOUD_*`, `CI_TRIGGER`, `DEPLOY_*`: denied. No decision grants them; in a launched session
    the empty network profile lets no sandboxed command reach another host.
