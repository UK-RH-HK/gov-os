---
name: adopted-review-ticket-fields
description: "an auditor ticket in an adopted repo needs state_class, role, allowed_paths inside a path-map namespace (not governance/adoption/), kpis with verify, reads/needs/waits_on lists; test on a clone first"
metadata:
  node_type: memory
  type: project
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-15T19:03:00.358Z
---

In EXAMIN (W2-27, 2026-11-15), tested on a clone: for `gov brief independent-auditor <id>` to exit 0 and the auditor to be able to commit its verdict, the ticket needs:
- `state_class` (the shared record schema requires it);
- `role: independent-auditor`, and `allowed_paths` set to the report folder. The guard gives the auditor only its ticket's paths; without them it gets ignored scratch only;
- `kpis` where every success and failure line has `verify`;
- `reads`, `needs` and `waits_on` as lists (`[]` counts as a declared none). These are needed when the ticket was created on or after facts.yaml's `new_since`;
- a facts.yaml from `gov adopt --facts`, with `{UNSET_IDENTITY}` and `{UNSET_PYTEST_FOLDER}` filled.

The A5 verdict path must lie inside a path-map namespace, or A6 refuses UNKNOWN_ARTEFACT. It must also lie outside `governance/adoption/`, or the verdict is VERDICT_NOT_INDEPENDENT. The brief still leaves `{W2}`, `{PROFILE}` and an empty Objective.

**Why:** F-011. `tk` cannot write these fields, and the kit denies `Edit(.tickets/**)`.

**How to apply:** before giving the operator a ticket-writing command, dry-run it on a `git clone` in scratch with the GOV_ variables unset. Related: [[check-before-ready-line]].
