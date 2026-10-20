
## 77. Delegated decisions on W1-16's second round (register v0.77, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on what the W1-16 (`DAEO-lkeb`) ticket lead returned with
its second run. Each is reversible, the recommendations agree and the confidence is medium. DEC-347 touches the
secret filter and only makes it refuse more (stricter-only).

### DEC-346 — W1-16 DP-5 and DP-6: the 16-character floor counts the rest alone, and the daemon directory is a residual with one test
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-16 packages DP-5 option (a) and DP-6 options (a) and (c); confidence medium · **Under:** DEC-325, DEC-338, DEC-339
- **Decision:**
  - A leading `_` or `-` of a token body (DEC-339) does not count toward the 16-character floor: the rest alone
    needs 16 characters, as built.
  - The files the tool's daemon leaves in the wrapper's per-repository directory under `/tmp` are a residual;
    the wrapper does not remove the directory, because that races a live daemon. One test shows that no planted
    secret stands in that directory after an index run.

### DEC-347 — The secret filter also scans with the project's rules alone, so gitleaks' built-in global allowlist cannot shelter a finding
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-04) · **Basis:** W1-16 package R-2, fix option 1, the engineer's and the lead's recommendation; confidence medium · **Under:** DEC-298, DEC-324, DEC-286
- **Context:** gitleaks' built-in defaults carry a global allowlist, and `[extend] useDefault = true` merges it over
  every rule, the project's included. DEC-298's stripping removes only the allowlists written in the project's
  file. So a canary or token that contains `abcdefghijklmnopqrstuvwxyz` in any case, contains `false`, begins with
  `true` or ends with `null`, or contains the default uuid stopword, passes the filter and reaches an indexer.
- **Decision:**
  - The pre-index filter and the path-name check run a second scan with the project's rules alone, without
    `extend`, and refuse a file that either scan flags. This closes the gap for the project's rules (the canary and
    token rules); the built-in rules stay sheltered by their own defaults, which is a residual.
  - W1-16 carries the change, tests first, before it closes: `src/gov/secrets/**` is in its paths. The doubled
    gitleaks runs are accepted; batching stays the residual of DEC-339.
  - A plain `gitleaks` run outside the filter (the pre-commit hook) keeps the built-in allowlist; whether the commit
    hook also needs the second scan is settled before W1-41, with the owner.

| Version | Date | Change |
|---|---|---|
| 0.77 | 2026-10-04 | Delegated under DEC-220: DEC-346 (W1-16 DP-5, DP-6: the floor counts the rest alone; the daemon directory is a residual with one test), DEC-347 (stricter-only: the secret filter also scans with the project's rules alone, so gitleaks' built-in global allowlist cannot shelter a canary or token). |
