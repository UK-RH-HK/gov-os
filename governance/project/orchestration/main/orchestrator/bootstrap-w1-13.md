
## W1-13 residuals (gov readiness, 2026-10-05)

Recorded at W1-13's close, from the ticket lead's summaries and the reviewer's pass. The reviewer's two HIGH findings
were fixed, tests first; the fix was not re-probed by a second reviewer. Each item names who should settle it where
that is known.

**What still lets work through** (DEC-348, DEC-350)

- Nothing stops a direct `openspec archive`, and the READY rule of W1-09 trusts a specification status set by hand:
  `gov readiness` only gives the verdict. W1-26 runs it as a check and fails a `CLOSED` record with a required row
  open; W1-35's change skill runs it before apply and archive.
- **Nothing writes the specification frontmatter yet.** Until W1-12's proposal template or W1-35 writes it, the bare
  `gov readiness` answers `READINESS_INVALID` in any project that holds a change written from today's template
  (every folder under `openspec/changes/` except `archive` counts as a change, even an empty one). W1-26 must know
  this before it wires the bare form as a check. `--specification` and `--ticket` judge the named one alone.
- `gap_ticket` is reported as written, even when it names no ticket or a closed one; that check is W1-26's.
- Content is not judged: a reason of `.` or evidence of `['TBD']` passes. An N/A reason made only of a zero-width
  space passes; empty, null, absent, spaces, tabs and a no-break space are rejected.

**`gov.readiness.close`** (DEC-349; no command or skill calls it yet)

- It accepts any file in `.tickets/` with `class: audit` and `audits: <id>` as the audit ticket: a closed one, one
  with another role, a hand-written one. A specification closed again after its audit ticket was closed gets no new
  one. For W1-26 or W1-35.
- A record with no plain `status:` line passes the read command; `close` then creates the audit ticket and fails
  with a raw error, leaving the record unclosed (a retry reuses the ticket). An interrupted `close` can leave an
  orphan ticket; a read-only `proposal.md` fails after the ticket exists; a relative root other than `.` fails.
- The specification id goes unchecked into the audit ticket's `allowed_paths` (`docs/audit/<id>/**`).
- "Fresh" and "authored none of the audited files" (MR-4) rest on the orchestrator's session rules.

**How records are read**

- Duplicated YAML keys are read last-wins (`profile: FULL` then `profile: LITE` is judged at LITE). Row identity is
  loose: `n: 3.0` counts as row 3, `n: true` as row 1, a row's `key` is never compared, and rows numbered outside 1
  to 26 are ignored silently.
- `--ticket` on a ticket with no `specification` key answers `SPECIFICATION_NOT_FOUND` (exit 1), although DEC-307
  says such a ticket is not held: a caller that gates on this code would block it.

**The taxonomy is held in code**

- The 26 row keys, the ten mandatory rows of DEC-085 and the capability-type table are constants in
  `src/gov/readiness/checker.py`, compared by a builder test with `docs/contract/readiness-dimensions.yaml`. A
  project schema whose rows or table differ makes every specification in that project `READINESS_INVALID`. So a
  governed taxonomy change (CAP-30.e) has to change the checker together with the schema and the Contract file.

**Records**

- 299 lines against 170 plus about 40 for `close`; 18 acceptance cases were added after implementation, from the
  reviewer's findings. Workers ran unsandboxed (interim, DEC-183).
