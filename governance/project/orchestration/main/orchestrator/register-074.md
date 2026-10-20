
## 74. Delegated decisions on W1-16's packages (register v0.74, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the packages the W1-16 (`DAEO-lkeb`) ticket lead
returned. Each is P2 or P3 and reversible, the lead's and the orchestrator's recommendations agree, and the
confidence is medium or higher. DP-1 (which question set decides the 60 % line) and the daemon's loopback UI go to
the owner.

### DEC-337 — W1-16 DP-2 and DP-3: the wrapper is a Python package, and "a rename" is a symbol rename
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-16 packages DP-2 option (A), confidence high, and DP-3 option (A), confidence medium · **Under:** CAP-12.a, CAP-12.b
- **Decision:**
  - The public interface is the package `gov.codeintel` (`index`, `home`, `projects`, `definitions`, `references`,
    `callers`, `impact`, `dead_code`), as built. It has no `gov` command; a later ticket that needs one adds a
    command module (DEC-317).
  - "Before and after a rename" is tested with a symbol rename. A file or folder move is a residual.

### DEC-338 — W1-16 DP-4: the tool's daemon files go to a short per-repository directory outside the repository
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-16 package DP-4 option (C); confidence medium · **Under:** CAP-12.a
- **Decision:**
  - The daemon's lock and socket files are not index files, so the failure line "an index file outside
    `.gov-runtime/`" does not cover them. They cannot live under `.gov-runtime/`: a socket path is limited to 108
    bytes.
  - The wrapper sets a short directory of its own for each repository, outside the repository, and never uses the
    tool's shared default. A test shows the shared default is not used.
  - Whether the daemon may serve its loopback UI at every call is the owner's to decide and is not settled here.

### DEC-339 — W1-16 R-1 and R-3: a token body that begins with `_` or `-` is flagged, and `gov.secrets` gets a public name check
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-16 packages R-1 and R-3; confidence medium · **Under:** DEC-324, DEC-325, DEC-298
- **Decision:**
  - R-1: the token rule also flags a body that begins with `_` or `-` when the rest meets DEC-325 (a digit, or
    mixed case; 16 characters). It only makes the rule flag more.
  - R-3: `gov.secrets` exposes a public function that says whether a path name holds a secret, and the wrapper
    stops importing private names. W1-17 and W1-19 use the same function. Batching the filter's gitleaks runs is a
    residual, to be measured on a large repository.
  - R-2 (a token holding the full alphabet run is never flagged when the gitleaks defaults are extended): W1-16's
    engineer traces the cause and reports it; a fix is a separate decision before W1-41.

| Version | Date | Change |
|---|---|---|
| 0.74 | 2026-10-04 | Delegated under DEC-220: DEC-337 (W1-16 DP-2, DP-3: a Python package; a rename is a symbol rename), DEC-338 (DP-4: daemon files in a short per-repository directory outside the repository), DEC-339 (R-1: a body beginning with `_` or `-` is flagged; R-3: a public name check in `gov.secrets`; R-2 is traced). DP-1 and the loopback UI go to the owner. |
