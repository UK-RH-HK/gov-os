---
name: ticket-fields-no-inline-comments
description: "never put a `# comment` on a ticket's role:/class:/status: line — the launcher reads those lines raw and refuses the launch"
metadata:
  node_type: memory
  type: feedback
  originSessionId: f3886235-4854-4c91-9cf3-1a1dd009cb50
  modified: 2026-11-13T21:58:16.371Z
---

In `.tickets/DAEO-*.md` front matter, scalar fields the launcher reads (`role:`, `class:`, `status:`) carry no inline `# comment`. A research ticket's single `allowed_paths` item (its experiment folder, DEC-242) and its `waits_on`/`deps` items carry none either: the launcher's `_load_ticket` keeps the comment in the value (W2-88b LAUNCH_BLOCKED, 11-13). Engineer tickets' commented path items have launched fine (W2-60a's P-8), but new entries are safest bare, with the reason in the ticket body.

**Why:** on 2026-11-13 I changed W2-94's role with `role: engineer  # was …`; YAML parses it, but `src/gov/launch/launcher.py` read the line raw and refused the engineer (LAUNCH_BLOCKED), costing a lead run.

**How to apply:** after editing a ticket's scalar field, `grep -n "^role:\|^class:\|^status:" <ticket>` must show bare values. Related: [[trailers-one-block]].

**Again on 11-16 00:5x (W2-174):** my DEC-1188 apply script wrote `profile: FULL  # [changed …]`, and land.py's pre-check then printed the profile as empty. Every apply script that changes a bare field (status, profile, role, class) writes the value alone and puts the reason in the body.

**Also (11-16):** a list item holding ": " (e.g. a non_goals line "no X: because Y") parses as a mapping and fails the ticket schema, turning W1-08/W2-02/W2-54's core-schema cases red for every close and land (W2-189's ticket, fixed 7dcd9a408). Quote such items, and after any ticket edit validate every ticket against template/governance/kernel/schemas/ticket.schema.json before committing.
