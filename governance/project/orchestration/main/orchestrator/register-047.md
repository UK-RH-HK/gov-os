
## 47. Delegated decisions on W1-37's test design packages (register v0.47, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the four packages the W1-37 (`DAEO-yvzh`) ticket lead
returned from its test designer. For each, the designer's, the lead's and the orchestrator's recommendations agree,
the confidence is medium or higher, and the choice is reversible before W1-38. One part of DP-2 is not decided here
and goes to the owner: whether a version recorded beside the vendored files satisfies CAP-24's "every skill file
carries a version in frontmatter" for vendored skills. It reads the Contract, so it is the owner's.

### DEC-244 — W1-37 DP-1: the three skills are copied from the vendor folder into the skills path
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-37 package DP-1 option (a); confidence medium · **Under:** DEC-074 Q5, DEC-194
- **Decision:** W1-37 copies the three skill folders (`SKILL.md` and its supporting files) from
  `template/governance/kernel/vendor/superpowers/skills/` into `template/governance/kernel/skills/superpowers/<skill>/`.
  The vendor folder stays unchanged and is the only source; the skills folder is the path W1-38 registers.

### DEC-245 — W1-37 DP-2, in part: "namespaced" means the folder
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-37 package DP-2 option (a); confidence medium · **Under:** DEC-074 Q5
- **Decision:**
  - The namespace is the folder `skills/superpowers/<skill>/`. The copied files stay byte-identical to the vendor
    copy, so the hash check is a plain byte comparison.
  - The source version, v6.4.2, is recorded beside the files, in the record of DEC-246.
  - **Not decided here, with the owner:** whether that record satisfies CAP-24's version in frontmatter for
    vendored skills. If the owner wants the version in each `SKILL.md`, the copies change and the hash rule with
    them, as a revision of this ticket's tests.

### DEC-246 — W1-37 DP-3: the source hash is recorded in a file beside the copied skills
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-37 package DP-3 option (b); confidence medium · **Under:** DEC-199
- **Decision:** A record file inside `template/governance/kernel/skills/superpowers/` carries the source version,
  the vendor folder's digest by the DEC-199 rule, and the digest of the copy by the same rule. A test recomputes
  both offline. The tool registry is not changed.

### DEC-247 — W1-37 DP-4: how the token sizes are measured against the I-09 figures
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-37 package DP-4 option (a); confidence high on the mapping and the formula, medium on "within" as a ceiling · **Under:** DEC-074 Q5
- **Decision:**
  - A skill's size is floor(characters ÷ 4) of its `SKILL.md` alone, measured on the copy under
    `skills/superpowers/`. Each is at or below its figure: test-driven-development 2,389, systematic-debugging
    2,360, verification-before-completion 899. No tolerance.
  - The figures 8,089 and 795 of DEC-074 belong to nothing this ticket vendors and are not asserted.
  - The measured sizes go in the record of DEC-246.

| Version | Date | Change |
|---|---|---|
| 0.47 | 2026-10-04 | Delegated under DEC-220: DEC-244 (W1-37 DP-1: copy from the vendor folder into `skills/superpowers/`), DEC-245 (W1-37 DP-2 in part: the namespace is the folder, files byte-identical; the CAP-24 version question goes to the owner), DEC-246 (W1-37 DP-3: a record file beside the copies, by the DEC-199 rule), DEC-247 (W1-37 DP-4: floor(characters ÷ 4) of `SKILL.md`, at or below the three figures). |
