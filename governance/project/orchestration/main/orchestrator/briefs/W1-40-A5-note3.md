
## Run 3: your packages are decided; continue from the branch

You are a fresh lead continuing run 2 (branch head `0ef8f1d7` plus the merge `7c49f0b2` of `w1/integrate`, which brings the register and the registry's new field; run 2's briefs, logs and checkpoint are under `.gov-runtime/scratch/lead/` in this worktree). Read DEC-494 and DEC-497 in `docs/DECISION_REGISTER.md` (the last two sections) and the gitleaks entry with its header comment in `governance/project/tool-registry.yaml` (`archive`, `archive_sha256`).

- **P-4 (DEC-494, the owner's).** The workflow gains two install steps of their own in the named place: gitleaks, downloaded from the registry's `archive` and verified against the registry's `archive_sha256` before it is unpacked (a mismatch fails the step), and the `gov` package installed from the checkout. Nothing else is installed: not pytest, not openspec, not rulesync, not lefthook. The version, address and checksum come from the registry: the step reads them from the file, or a case holds that the workflow's text and the registry agree. No test downloads anything; a case may verify a local file against a checksum.
- **A step whose tool is not on the runner (DEC-497).** It prints the word "unmeasured" with the tool's name and fails: never green, never skipped in silence. That is the tests step (pytest is absent on the runner) and, inside `gov ci job`, a check of `gov check` that reports its tool absent (openspec; rulesync for the adapter check): the job names it as unmeasured and exits non-zero. This replaces your P-9 recommendation. The later steps still run after a failed one, so one run reports every step (no `continue-on-error`). If telling "the tool is absent" from another warning is not possible inside this ticket's paths, return the exact place; do not guess from a message's wording without a case that holds it.
- **P-6:** `gov ci record` prints "no G3 check declared" and exits 0 for such a record; the record itself never says passed. A case holds both.
- **P-7, P-8:** left as built (residuals for the Wave 2 list).
- **P-10:** the checkout brings the parent commit (`fetch-depth: 2`), a case first. The runner's green on a missing parent is a residual, not yours to fix.
- **P-11:** `gov ci job` fails for an unknown check family as `gov check` does, a case first.
- **The `install -D` after the refused `mkdir`:** accepted (DEC-497); the guard's refusal to create the folder of an allowed file is a residual.
- **The adapter comparison** keeps its named place; no step is written for it.
- **An engineer commit exists:** every test designer commit that rewrites an existing case carries a `Rewrite-Reason:` trailer naming the cases and the decision.
- Your own merge commits carry `Task:`, `Role: orchestrator` and `Implements: CAP-39.a`.
- As before: nobody runs `lefthook install` or writes under `.git/hooks`; the root hook file and the root workflow file are produced from their templates by a Bash copy, never by Write or Edit.
- Order: a test designer brings the suite to these decisions, you check red, a fresh engineer, you verify every suite and the unit tests, you read the diff for places that end green without having run, and return DONE or PACKAGES, with the residual list complete (run 2's list plus the new ones).
