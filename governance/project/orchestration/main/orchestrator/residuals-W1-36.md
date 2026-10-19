
## W1-36 residuals (the skills retrieval, audit, checkpoint and adopt, and their checks, 2026-10-07)

- **Built:** four skill files under `template/governance/kernel/skills/` (retrieval, audit, checkpoint, adopt),
  versioned and within the size limits; the declaration `skill-regression-b1` (W1-26's skill validator over
  the four folders); the declaration `audit-reproducibility` (W1-26's audit validator over `docs/audit/`,
  tier G1, hard block). The audit skill (v1.1.0) describes the report form of DEC-441.
- **"Not applicable until the first audit" (DEC-447):** the audit declaration carries
  `allows-not-applicable: "true"`. With no report under `docs/audit/` the family is YELLOW with that reason;
  with a valid report GREEN; with an invalid one RED, a hard block.
- **The suite tests the text of the skills and the checks on constructed reports, not sessions.** Measured only
  at the Wave 1 exit (W1-42, W1-43): retrieval runs its facets in disposable subagents and only the validated
  bundle returns ("intermediate retrieval batches appear in the main context" is a failure line); the audit
  reports the planted divergence on the MR-A-06 and MR-B-06 dev scenarios; the audit starts a fresh session
  whose only inputs are the context pack and the repository, and edits no audited file; contested and
  owner-level findings appear as decision packages; a wave-exit report has one row per LITE feature
  specification closed in the wave. Until then they are unmeasured, not met.
- **The vendored superpowers skills carry no `version`,** so the skill-regression declaration names the four
  folders instead of the whole skills folder, and those three skills are not validated. Open: add a version to
  the vendored copies (they are committed unchanged, DEC-194) or leave them outside the check.
- **Declared commands name paths under `template/…`,** which an installed project does not have: for the
  adoption tickets (W1-39, W1-41).
- **W1-26's suite was revised for this ticket:** five cases remove the kernel's own audit declaration from
  their temporary project, because a second check of the same family (over another folder) made their family
  status ambiguous; the fixture's skill copy was aligned to the integration branch's. No assertion was changed.
- **Records:** the merge-back `15ac9b54` was flagged by the containment check for the shared W1-26 support
  file (aligned to the integration branch's version before the merge, DEC-412).
- **Learning metrics:** two lead starts (the first declared its checks with commands that exited 0 whatever
  they found), then four short worker turns started by the orchestrator (alignment, DEC-447 cases, the field,
  the W1-26 life-cycle case); 84 cases; no reviewer round (STANDARD); about 165 lines of skill text and two
  declarations.
- **Regression at `087a166a`:** REGLINE
