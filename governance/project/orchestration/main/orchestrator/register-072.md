
## 72. Delegated decisions on W1-46's packages DP-17 to DP-21 (register v0.72, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the five packages the W1-46 (`DAEO-jdqr`) ticket lead
returned with its second run. Each is P2 or P3 and reversible, the lead's and the orchestrator's recommendations
agree, and the confidence is medium or higher. DEC-334 touches the guard and only makes it refuse more (stricter-only,
orchestrator prompt v4.1, section 6).

### DEC-332 — W1-46 DP-17: `gov launch` ends with the session's exit code
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-17 option (a); confidence medium · **Under:** DEC-317
- **Decision:** `gov launch` ends with the exit code of the session it started, whatever it is, and prints no
  envelope then (`CHILD_EXIT_CODE`), as built. A caller that needs to tell a launcher refusal from a session's own
  code 1 to 4 reads the output: a refusal prints the envelope.

### DEC-333 — W1-46 DP-18: the experiments root is `experiments/` in Wave 1
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-18 option (a); confidence medium · **Under:** DEC-273
- **Decision:** The experiments root is the fixed name `experiments/` in Wave 1, as built. A project key that names
  another root waits for a project that needs one.

### DEC-334 — W1-46 DP-19 and DP-20: the guard refuses a hard link to a file the role may not write, and `mv --target-directory` and `install` into protected places
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-04) · **Basis:** W1-46 packages DP-19 option (a) and DP-20 option (a); confidence medium-high and medium · **Under:** DEC-311, MR-3
- **Decision:**
  - The guard refuses `ln` without `-s` (and `link`, `cp -l`) when the source is a file the role may not write:
    otherwise a later call writes through the hard link and changes an acceptance test.
  - The guard treats the destination of `mv --target-directory=<dir>` and of `install` as a write target, as it does
    for `mv -t` and `cp -t`.
  - W1-46 carries both, in one short round (tests first), before it closes.

### DEC-335 — W1-46 DP-21: the builder test of the symbolic link under the acceptance tests makes its link by a form the guard does not read
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-46 package DP-21 option (a); confidence high · **Under:** DEC-311, DEC-132
- **Decision:** `tests/unit/containment/test_probe_repairs.py::TestRepair3Symlinks` still tests containment (the
  link is found and removed after the call), so it stays. Since DEC-311 the guard refuses `ln -s` into the acceptance
  tests before the call, so the test now makes the link with an interpreter one-liner, which the guard does not
  read. The orchestrator makes the change in the main tree, in its own commit with W1-46's trailer.

| Version | Date | Change |
|---|---|---|
| 0.72 | 2026-10-04 | Delegated under DEC-220: DEC-332 (W1-46 DP-17: `gov launch` ends with the session's exit code), DEC-333 (DP-18: `experiments/` fixed in Wave 1), DEC-334 (DP-19, DP-20, stricter-only: hard links to files the role may not write, `mv --target-directory` and `install` are refused), DEC-335 (DP-21: the containment builder test makes its link by an interpreter one-liner). |
