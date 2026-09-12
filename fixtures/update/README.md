# Fixture 4 — Framework update (stored synthetic 4.1.1 → current release; genuine 4.1.2 → 4.1.3 → 4.1.4 in repair2.rs)

The stored synthetic **previous release 4.1.1** under `previous-release/4.1.1/` (derived once from the 4.1.2 payload; documented differences
below), installs it into a fresh project, creates project state (overlay customisation, decisions, tasks), then upgrades
to the 4.1.2 release candidate with `gov update --check` / `--apply` and finally exercises `--rollback`.

Differences of the synthetic 4.1.1 kernel (see `tests/certification/update.rs::make_previous_release`):

- `KERNEL.yaml` version `4.1.1`, `supported_from_versions: []`, no `migrations/` payload.
- Policies `LEARNING_POLICY.yaml` and `ARCHIVE_POLICY.yaml` absent (4.1.1 shipped 11 policies + a `GATE_POLICY` name).
- Overlay template `PROJECT_POLICY.yaml` uses the old key `human_gates:` and `schema_version: 0.9.0`;
  `PROJECT_EXCEPTIONS.yaml` template absent.
- `project-policy.schema.json` accepts `human_gates`; `project-exceptions.schema.json` absent.

Proved: migration path `M-4.1.1-4.1.2` resolved; CIT-P impact printed; human gate required because the target is
uncertified; kernel replaced; migration operations applied (exceptions file added, `human_gates`→`gates`,
`gates.presentation_channel`, lock schema version); **project overlay values preserved** (name, alias, custom
policy override); **spec/ untouched** (tree hash equal); adapters regenerated; indexes rebuilt; doctor has no critical
finding; `gov update --rollback` restores the 4.1.1 kernel, overlay and lock byte-for-byte.
