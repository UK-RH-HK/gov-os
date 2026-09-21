# OWNER-CLARIFICATION-P2-0004 — Project-editable files may request authority, never manufacture it

| Field | Value |
|---|---|
| Record | Owner clarification (product owner, 2026-09-21), given when authorising repair iteration 2 |
| Id | **OC-P2-04** |
| Status | IN FORCE for Phase 2 and later phases until the owner changes it |
| Applies to | BC-P2-45 (overlay precedence coverage) and the related tool-install trust surface (BC-P2-53, BC-P2-41) |

## The clarification, in the owner's terms

- Project-editable files **may** request, configure or narrow authority, but they **must not manufacture or increase
  trusted authority**.
- Any state capable of granting privileged authority **must derive from authenticated/sealed Governance OS state, or pass
  through the governed transaction / change-control path**.
- Direct hand edits to project permissions, path-map, sensitivity or equivalent authority-affecting files **must not
  silently increase effective trusted authority**.

## What it settles

The synthesis verifier ruled BC-P2-45 an ordinary repair requirement rather than an owner decision, and recorded the
architectural question underneath it: the tool-install envelope's *authorised* side is computed from documents the project
itself can edit. This clarification answers that question and is the normative source the repair is measured against,
alongside Contract v3:134 ("security and authority floors cannot be weakened by lower-precedence policy"), :137 ("invalid
weakening attempts fail closed and are observable") and OD-P2-03 requirement 2 (the envelope is computed from trusted OS
state).

Concretely, for every project overlay document whose content can change an authority, permission, filesystem-scope or
sensitivity decision:

1. **Narrowing is allowed.** A project may restrict what it grants itself, and that takes effect.
2. **Widening is refused, left without effect, and reported.** A hand edit that would increase effective trusted authority
   must not change the decision, must appear in the refused list with its policy, key, value, kernel value and reason, and
   must surface on a governance-suite check.
3. **The only route to more authority is the governed one** — authenticated or sealed OS state, or an approved change
   transaction. A file the project can write is a request, never a grant.
4. **Silence is failure.** An increase that takes effect without being refused and reported is a defect even if some other
   control would later catch it.

## Scope note

This clarifies how existing accepted requirements apply; it does not add a new capability to the Phase-2 universe and does
not change the frozen gate contract or any acceptance criterion. A verifier may find the implementation of this
clarification insufficient; that is a finding against the implementation, not a reopening of the clarification.
