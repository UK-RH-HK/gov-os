
## 57. Delegated decisions on W1-10's test design packages (register v0.57, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on five of the six packages the W1-10 (`DAEO-4yyl`) ticket
lead returned. For each, the designer's, the lead's and the orchestrator's recommendations agree, the confidence is
medium or higher, and the choice is reversible: each is a rule inside `gov.store.load` or the suite, and no later
ticket has built on it yet. The suite and the implementation on the branch already follow them. DP-3 (who writes
`.gov-runtime/store.db` in a live session) is not decided here: it touches the guard, so it goes to the owner; it
changes nothing in this ticket.

### DEC-274 — W1-10 DP-1: what a record is, and what an invalid one does to a load
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-10 package DP-1 option (a); confidence medium · **Under:** DEC-239, CAP-13.a
- **Decision:**
  - A record is any tracked Markdown file whose frontmatter has an `id`. It needs `id`, `type` and `status`
    (DEC-239). An unreadable or incomplete one is listed in the load's `invalid` by path, and the load continues.
  - Known consequences, recorded as residuals for later tickets: the charter, the contract and the plan have `id`
    and `status` but no `type` and are reported invalid; the seven kernel templates load as records with
    placeholder ids; decisions are headings in the register, not files, so every `DEC-…` reference is dangling
    until decisions are records; two files with one id both load.

### DEC-275 — W1-10 DP-2: the store's public interface is a Python interface
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-10 package DP-2 option (a); confidence high · **Under:** DEC-190
- **Decision:** W1-10 delivers `gov.store.load` and `gov.store.digest`, and `gov.records.records`, `active`,
  `edges`, `dangling` and `commits`. `gov rebuild` stays reserved; the ticket that wires it to `load` (W1-27)
  revises its registry case with the reason "planned: command implemented".

### DEC-276 — W1-10 DP-4: the digest covers the store's logical content
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-10 package DP-4 option (a); confidence high · **Under:** CAP-13.a
- **Decision:** "The same digest twice" is over the store's logical content (records, edges, commits, trailers, in
  a fixed order), not over the bytes of `store.db`.

### DEC-277 — W1-10 DP-5: the source of each typed edge, and trailers
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-10 package DP-5 option (a); confidence medium, high for DEC-012's five keys · **Under:** DEC-012, DEC-182, CAP-09.a
- **Decision:**
  - A frontmatter key gives an edge of the same name in upper case, from the carrying record to each listed id:
    `evidence_for`, `constrains`, `implements`, `tests`, `generates`, `validates`, `supersedes`, `depends_on`.
    `superseded_by` gives the same SUPERSEDES edge once.
  - Trailers are not edges. They come from `commits()`, and a trailer id that names no record is in `dangling()`.
  - Before any real record uses the four keys DEC-012 does not name (`evidence_for`, `tests`, `generates`,
    `validates`), a product-spec worker checks them against the archived Framework §11.2 (DEC-222).
  - Known consequences, recorded as residuals: a ticket's `depends_on` holds WBS ids while its `id` is the tk id,
    so those edges are dangling in this repository; trailer values such as `decision-record` name no record and
    are dangling too.

### DEC-278 — W1-10 DP-6: both dev tiers, and the load call alone is timed
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-10 package DP-6 option (a); confidence medium-high
- **Decision:** "Full load of a dev tier < 5 s" is tested on both `a-dev` and `b-dev`, and the limit is on the
  `load` call alone.

| Version | Date | Change |
|---|---|---|
| 0.57 | 2026-10-04 | Delegated under DEC-220: DEC-274 (W1-10 DP-1: a record is a tracked Markdown file with an `id` in its frontmatter; invalid ones are listed and the load continues), DEC-275 (DP-2: a Python interface; `gov rebuild` stays reserved for W1-27), DEC-276 (DP-4: the digest covers logical content), DEC-277 (DP-5: frontmatter key to edge of the same name; trailers are not edges), DEC-278 (DP-6: both dev tiers, the load call alone). DP-3 goes to the owner. |
