
## W1-08 residuals (record schemas, templates and the path map, 2026-10-04)

Recorded at W1-08's close, from the ticket lead's summaries. None is a defect; each names the ticket that should
settle it.

- **Capability values for this repository.** The entry shape is decided (DEC-251, DEC-265). The values in
  `governance/project/path-map.yaml` (code intelligence on for Python, research corpus off) are the implementer's.
- **Namespace field values are free text.** Sensitivity, retention, export policy, embedding policy, provenance and
  deletion/rebuild behaviour are non-empty strings; the words in this path map are the implementer's. W1-15 fixes
  closed lists when it first reads them.
- **`permitted_roles`** is read as "may access", and all six roles are listed on every namespace. Confirm before
  W1-15.
- **`fixtures/**`** is the only `product` namespace.
- **The ticket schema** requires only `kpis`, `role` and `allowed_paths` beyond the shared frontmatter; the other six
  ticket fields are typed but optional. Consider requiring them at W1-09.
- **`status` and `type`.** `status` is any non-empty string on every record; a lesson's lifecycle is the required
  `lifecycle` key, closed to the six states. `type` is pinned per record type except on tickets.
- **Id grammars.** `lesson_id` is decided (DEC-252). The other four grammars are the implementer's, and `supersedes`,
  `superseded_by` and `consumers` have no grammar.
- **Failure, research, decision package and checkpoint records** have no type-specific fields; the required fields of
  the older schemas under `schemas/records/` were not carried over.
- **Closed and open maps.** `policies`, `systems`, `capabilities` and its two entries refuse unknown keys; namespaces,
  the path map's top level and record frontmatter accept extras. No test covers the open ones.
- **The `systems` snapshot** (13 minimal, 9 absent, none implemented) needs updating as tickets land, W1-46 first
  (research).
- **New top-level folders.** The root namespace uses `*`, and `.github/` and `.rulesync/` are pre-listed. Any other
  new top-level folder fails "every tracked path in exactly one namespace" until a namespace is added.
- **The two committed ADRs** lack `state_class` and would not validate against the decision schema until they get it.
- **Untested points:** language names must be non-empty strings (slightly stricter than DEC-251 says); the disabled
  form of `code_intelligence` (DEC-265, for W1-27's test design); that a lesson record's `id` uses `lesson_id` and
  no other grammar.
- **The held-out path string** appeared twice in the product-spec worker's output, from printing a ticket's
  `allowed_paths` and from ADR-0002 §6. Seeing the path is an accepted residual (DEC-223).
