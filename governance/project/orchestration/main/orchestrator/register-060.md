
## 60. Delegated decisions on W1-15's test design packages (register v0.60, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the six packages the W1-15 (`DAEO-7nne`) ticket lead
returned from its test design. For each, the designer's, the lead's and the orchestrator's recommendations agree,
the confidence is medium or higher, and the choice is reversible until W1-16 or W1-17 builds on it. None changes
the guard or containment. The suite on the branch already follows them.

### DEC-285 — W1-15 DP-1: the filter's interface, and how a check command is run
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-1 option (a); confidence medium-high on the function, medium on the check convention · **Under:** CAP-03.a, CAP-03.e, CAP-38.b
- **Decision:**
  - The filter is the function `gov.secrets.indexable(root, paths)`: it takes the project root and a list of
    project-relative paths and returns, in order, the sub-list an indexer may read. It drops a file that holds a
    secret, a file whose namespace is not `memory_class: governance`, and anything unreadable. If it cannot decide,
    it raises or drops the path; it never lets the path through.
  - A family check's `command` is run by `sh -c` in the project root, and exit 0 means green. W1-26 may refine this
    when it builds `gov check`.

### DEC-286 — W1-15 DP-2: the seven dev canaries, and both spellings of the token canary
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-2 option (a); confidence medium on the count · **Under:** DEC-074 Q8
- **Decision:** The seven dev canaries are the seven planted values the test designer found in the dev tiers (three
  strings with the canary word and an example cloud key pair in `a-dev`; the token canary and a key-file canary in
  `b-dev`). The token canary is detected in both spellings, with underscores as the KPI writes it and hyphenated as
  `b-dev` holds it. The owner is asked to confirm the count against the S0b1 manifest; the list is one tuple in the
  suite's support module.

### DEC-287 — W1-15 DP-3: the filter runs the gitleaks binary
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-3 option (a); confidence medium-high · **Under:** CAP-03, DEC-195
- **Decision:** The filter runs gitleaks 8.30.1 (in the tool registry) with the rules of `.gitleaks.toml`, so there
  is one source of rules. The filter and check cases therefore need the binary where they run. Putting gitleaks on
  CI is an install for the owner, raised with W1-40; until then those cases run on this machine.

### DEC-288 — W1-15 DP-4: what each gitleaks file holds
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-4 option (a); confidence medium
- **Decision:** `template/.gitleaks.toml` holds the defaults plus the token and canary rules, with no path
  allowlist. The root `.gitleaks.toml` holds the same rules plus this repository's own allowlist. A product that
  adopts the template inherits no allowlist.

### DEC-289 — W1-15 DP-5: the two W1-08 residuals stay open
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-5 option (a); confidence high
- **Decision:** W1-15 reads only a namespace's `paths` and `memory_class`. The closed lists for the free-text
  namespace fields and the meaning of `permitted_roles` move to the first ticket that reads export or embedding
  policy (W1-17 or W1-24). `bootstrap.md` is corrected at W1-15's close.

### DEC-290 — W1-15 DP-6: allowlists, and secrets inside a store
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-6, the lead's three recommendations; confidence medium · **Under:** CAP-03.a, CAP-38.b
- **Decision:**
  - The root `.gitleaks.toml` allowlists, by path, the tracked documents that only name the canary identifier (the
    ticket file, plan documents, this suite's README), after the engineer runs gitleaks over the tree and reports
    which they are. The template gets no such entry.
  - The pre-index filter ignores path allowlists: a file with a fake secret in a governance namespace, such as a
    test fixture, never reaches an index.
  - The secrets-indexing check scans the content of the stores, SQLite rows included, because `gitleaks dir` skips
    binary files. The extra lines over the 70 LOC estimate are accepted.

| Version | Date | Change |
|---|---|---|
| 0.60 | 2026-10-04 | Delegated under DEC-220: DEC-285 (W1-15 DP-1: `gov.secrets.indexable(root, paths)`; a check command runs by `sh -c`, exit 0 is green), DEC-286 (DP-2: the seven canaries as found in the tiers, both spellings; the owner confirms the count), DEC-287 (DP-3: the filter runs gitleaks), DEC-288 (DP-4: the template has no allowlist), DEC-289 (DP-5: the two W1-08 residuals move to W1-17 or W1-24), DEC-290 (DP-6: a root-only allowlist for documents naming the canary; the filter ignores allowlists; the check scans store content). |
