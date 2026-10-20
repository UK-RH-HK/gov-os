
## W1-12 residuals (readiness schema and proposal templates, 2026-10-04)

Recorded at W1-12's close, from the ticket lead's summaries and a product-spec worker's reading of G-07 and G-09
(DEC-310). None is a defect of the ticket; each names who should settle it.

- **The CIT-E rule is stated only** (DEC-309). The schema carries the source and the extension rule of
  `readiness-dimensions.yaml`, and W1-12's suite goes red when the YAML changes without the schema. The check that a
  change to the taxonomy or to the YAML has a linked CIT-E record is a KPI line of W1-26.
- **The kernel `templates/openspec/` folder holds nothing** (DEC-304, DEC-326). G-07 and G-09 name no path there, and
  OpenSpec reads templates only from the schema's own `templates/` folder. The path left the ticket's `allowed_paths`.
- **Names.** G-07 calls the artefact `feature-readiness`; as built, the schema is `feature-readiness` and the
  artefact is `readiness`, file `readiness.yaml` (DEC-305). G-08, W1-13's source, says the checker reads
  `feature-readiness.md`: DEC-305 supersedes that file name. For W1-13's test design brief.
- **The record lacks profile and capability types.** `readiness.yaml` has no `profile` or declared capability-type
  field, and `cell_states` holds only the state names and `requires: [reason]` on N/A. The readiness YAML's
  `meaning`, `satisfies`, `mandatory`, `rules` and `profiles` are not copied. W1-13 needs them or must read the
  contract YAML.
- **Artifact order.** `readiness` requires `specs`, while `tasks` and `apply` keep their upstream requirements, so
  OpenSpec does not force the record before tasks.
- **`validate --strict` parses only the spec deltas and `.openspec.yaml`**; the proposal, design, tasks and readiness
  files cannot fail it. The stock `spec.md` template fails `--strict`, so the fork replaces it with plain "replace
  this" sentences, one SHALL requirement and one scenario. The other three templates are byte-identical to upstream;
  about 317 lines are upstream `spec-driven` text.
- **Free fields.** `evidence` and `gap_ticket` carry no id pattern, so nothing duplicates the shared id grammars
  (DEC-227). Validation falls to W1-13.
- **Untested:** a `config.yaml` naming an unknown schema makes `openspec new change` exit 1 with "Unknown schema".
