
## 208. Owner answers of 2026-10-14: the empty semantic index, ORION's cycle and ARGUS as reported, the containment restores, two closes, the backup, the W1-42 merge (register v0.208, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-686 — The empty semantic index in the adopted a-dev clone: one read-only diagnostic, then one round with a probe
- **Status:** ACCEPTED (owner, 2026-10-14) · **Under:** DEC-380, DEC-388, DEC-584 · **Basis:** the W1-42 lead's exit report at `1708868a`: in the adopted a-dev clone both scenario retrievals return no evidence and the semantic canary misses; the semantic index stays empty after a full `gov rebuild`
- **Decision:** option (a).
  - One read-only diagnostic first, then one round on what it shows, with a probe.
  - Then the two scenario retrievals and the semantic canary are re-run, and the exit report is corrected.
  - **Checked first:** whether the clone's path map gives its namespaces a valid `embedding_policy`. Under DEC-380 and DEC-388 a namespace whose policy is missing or unknown is read as "not embedded", so a path map written by adoption without valid policies would leave the semantic index empty, with no error.

### DEC-687 — ORION's cycle is completed in a-dev: a trailers base at the real adoption boundary, a local bare remote, `gov ci` and the merge re-run; ARGUS stays as reported
- **Status:** ACCEPTED (owner, 2026-10-14) · **Under:** DEC-482, DEC-585, DEC-674, DEC-678
- **Decision:**
  - **a-dev:** the trailers base is set in a-dev's path map at a-dev's real adoption boundary, its A8 commit (`bb1852e`), the way DEC-482 set this repository's base at its adoption commit. The commits of runs 1 and 2 came before it. Not at `540004a`, and not at any commit chosen to pass over a finding.
  - The a-dev clone gets a local bare remote under the clone's own folder, so that `gov ci push` and the evidence note work as the local gate of DEC-585.
  - Then ORION's `gov ci` and the merge are re-run.
  - **b-dev stays as reported:** adopted to A2, ARGUS's close refused, no CI and no merge, named in the exit report with its reason. The owner weighs it at the exit decision.

### DEC-688 — The eleven containment restores of acceptance-test files during adoption on 2026-10-12 are traced
- **Status:** ACCEPTED (owner, 2026-10-14) · **Under:** MR-3, DEC-686
- **Decision:**
  - They are traced read-only, together with the diagnostic of DEC-686: which call changed each file, under which role, and why containment restored it.
  - Criterion 3 (MR-3) needs them explained, not only named.
  - If the trace finds a real MR-3 breach, it comes to the owner as a package.

### DEC-689 — DAEO-6mk8 is closed with the ticket tool
- **Status:** ACCEPTED (owner, 2026-10-14) · **Under:** DEC-646, DEC-647, DEC-672 · **Basis:** the one further `gov close DAEO-6mk8` at `44f5bded` returned exit 3 on one case of 12,305 (a live network connection of W1-46, for one host), which passed alone straight afterwards (17 passed)
- **Decision:** option (a). It is closed with `tk close`, named for the exit auditor.

### DEC-690 — DAEO-emkd is closed with the ticket tool
- **Status:** ACCEPTED (owner, 2026-10-14) · **Under:** DEC-651, DEC-683, DEC-685 · **Basis:** `gov close DAEO-emkd` at `2588fd12` returned exit 3 on 13 findings, all on commits of 2026-10-01 to 2026-10-11, from before this round; every test run of the close was green
- **Decision:** option (a). It is closed with `tk close`, named for the exit auditor.

### DEC-691 — The a-dev clone holding ORION-im02 and its merge is backed up; the copy goes into the exit report's evidence list
- **Status:** ACCEPTED (owner, 2026-10-14) · **Under:** DEC-673, DEC-681
- **Decision and record:** the a-dev clone, now holding ORION-im02 and its merge, is backed up through the operator to `~/gov-os-workbench/archive/w1-42-exit-clones/live-run4-a-dev-exit/`. It is added to the exit report's evidence list.
  - The owner's message left the heads of the copy as a placeholder ("operator's heads"). The live clone stood at `30996b6` on its feature branch and `2d3d098` on its main when the lead of run 4 returned; the orchestrator asks the owner for the operator's figures and records them when given.

### DEC-692 — `w1/W1-42` is not merged into the integration branch until its red cases are resolved
- **Status:** ACCEPTED (owner, 2026-10-14)
- **Decision:** `w1/W1-42` is not merged into `w1/integrate` until its red cases are resolved or the owner decides otherwise.

| Version | Date | Change |
|---|---|---|
| 0.208 | 2026-10-14 | Owner: DEC-686 (empty semantic index in adopted a-dev: diagnostic, then one round with a probe; embedding policies of the path map checked first), DEC-687 (a-dev: trailers base at `bb1852e`, a local bare remote, `gov ci` and merge re-run; b-dev as reported), DEC-688 (the eleven containment restores traced), DEC-689 (DAEO-6mk8 closed with the ticket tool), DEC-690 (DAEO-emkd closed with the ticket tool), DEC-691 (backup of the a-dev clone with ORION-im02), DEC-692 (`w1/W1-42` not merged until its red cases are resolved). Next free id: DEC-693. |
