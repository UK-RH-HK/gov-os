
## W1-09 residuals (ticket vendoring, claims and the READY rule, 2026-10-04)

Recorded at W1-09's close, from the ticket lead's summary and the reviewer's findings, three of which were fixed.
None is a defect of the ticket; each names who should settle it.

- **Stale store.** The READY rule reads records from the store as last loaded. A specification reopened, a package
  added or an input superseded after the load leaves tickets READY until the next `gov.store.load`. The store has no
  freshness mark. For W1-13 and W1-26, which call the rule.
- **Packages that do not load block nothing** (with DEC-308): broken frontmatter, no `status`, a status in another
  case, a ticket named by its WBS id. For W1-34 and W1-11.
- **Specification gate edges** (with DEC-307): an empty `specification:` key reads as absent; duplicate record ids
  give an order-dependent answer; a `CLOSED` specification superseded by a draft still counts; any record type
  counts. For W1-13.
- **Holder comparison is on the stripped text.** `" a "` is released by `"a"` and not by itself; an empty lock is
  released by anyone passing `""`.
- **A ticket that is `in_progress` without a lock can be claimed.** DEC-292 left the link between `claim` and
  `in_progress` open. `claim` also accepts `status: Closed` (capitalised) and a ticket with no status.
- **`create` trusts the script's last output line** and does not check the script's sha256 before running it. Not
  reachable with the pinned script. Which copy of `tk` `create` runs in this repository is open under DEC-295: it
  always runs `<root>/governance/kernel/bin/tk`.
- **Acceptance folder cases left open under DEC-293 and DEC-300:** a path naming another ticket's folder, and an
  empty folder, both still count.
- **Raw exceptions instead of `GovError`:** ids `.`, `..` or with a NUL in `holder` and `release`; a lock that is a
  directory; a claims folder that is a file; a release on an unreadable claims folder; `create` when the script is
  missing or fails; a holder that cannot be encoded leaves a stuck empty lock. All fail closed.
- **`blocked` can give an empty reason list** for an unreadable ticket, an unreadable store or an unknown status; a
  reason code for "cannot be read" needs a decision.
- **Only `deps` is read, not `depends_on`.** A record with status `SUPERSEDED` or `REJECTED` but no edge is a good
  input.
- **Minor lock and ticket edges.** A dangling-link lock cannot be released through the interface; with two `status`
  keys the last wins; a lock is keyed by file name, not by the frontmatter id. A claims folder that is a symbolic
  link is recorded under DEC-297.
- **The release `flock` is advisory and POSIX-only.** A lock removed by hand is outside it. The double hold the
  reviewer saw was not reproduced (about 1,800 rounds by the designer, 480 by the lead); the fix rests on the lead's
  reading of the diff.
