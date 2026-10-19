---
type: probe
task: DAEO-6n5k
reviewer_session: 895b39f4-5a54-448f-b934-fbbcfab8803d
implementer_session: b658f614-efea-46bf-aeca-1d047c7066b2
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: 2ff873b2c5fa5295f32cfe9299745c0c2b188e54
---

# Probe record (draft, failing): W2-37 `gov impact`, second and last review

This draft stays in the lead's scratch folder. A failing review's record is never committed, because the probe gate reads every committed record. Nothing is committed after the probed head either.

- **What was probed.** The head `2ff873b2` on `w2/W2-37`. The round's fix is `fd9c8f23` (engineer session `b658f614-efea-46bf-aeca-1d047c7066b2`), after the test batch `ac4983f8`.
- **The reviewer.** A fresh read-only reviewer: role `independent-auditor`, session `895b39f4-5a54-448f-b934-fbbcfab8803d` (read from its scratchpad path), 2026-10-19. The orchestrator commissioned and judged it.
- **How it ran.** It was launched sandboxed through `gov launch`, then resumed in the same session in the owner's launch form for the code-graph probes (P-W2-38).
- **No writes.** It wrote nothing in the repository: the tripwire shows no change in this worktree on either pass, and `git status --short` was clean at the end. Its temporary folder was `/tmp/claude-1000/w237-probe.pWGaQD`.
- **Threat model.** ADR-0001, as DEC-801 states it.
- **Tests the reviewer ran.**
  - Sandboxed: W2-37 plus `tests/unit/impact` gave 96 passed, 3 failed and 19 errors. The 3 failures are the expected P-1 ×2 and P-2 reds; the 19 errors are the read-only `/tmp/gov-cbm`, P-W2-38.
  - Outside the sandbox: the `local_only` cases gave 20 passed and 76 deselected.

## Findings

### A (MAJOR): `--compare` reads the CIT-P as edited in the working tree and never says it differs from the stored one
- **Setup.** CITP-001, which lists DEC-002, was committed and the store loaded. A CIT-E without DEC-002 correctly gave `matches: false`.
- **The fault.** With DEC-002 then taken out of the CIT-P in the working tree, uncommitted, the compare gave `matches: true` and `differences: []`. It gave no word of the drift, and the result carries no graph state.
- **The fix the review asks for.** F1's rule applies to `assess` but not to `compare`.
- Ordinary work: yes, because bringing the proposal up to date with what was done before writing the CIT-E is the drift KPI 2's check exists to catch.
- Consequence: fails open

### B (MINOR): the first entry of a decision register is not seen as uncommitted
- **Setup.** The register named by the path map has no entries at HEAD. A first entry, DEC-090 (`**Supersedes:** DEC-001`), is added and not committed.
- **The fault.** `graphs.record` reads `ok`.
- **When it fails open.** With the register in a non-governance namespace, which the code index does not copy, the report reads `complete: true` and is missing DEC-090.
- **When it fails closed.** In the usual governance layout the code graph reads `stale`, so the report is `complete: false`.
- **When it is already right.** Once the register holds an entry at HEAD, a further uncommitted entry reads `stale`.
- Ordinary work: yes (narrow), because each condition is ordinary but all four must hold together.
- Consequence: fails open

### C (MINOR): a match against an incomplete CIT-P doesn't carry the incompleteness
A CIT-P written with `complete: false` and a CIT-E with the same lists give `matches: true`. The result has no `complete` and no gaps.
- Ordinary work: yes, because this is the normal path whenever the code index is missing.
- Consequence: other (the match is true as stated, and the CIT-P file says `complete: false`)

### D (MINOR): items written as maps without an `id` all read as the item "None"
A CIT-P with `[{name: A}, {name: B}]` and a CIT-E with `[{name: C}]` give `matches: true`. With only one side written this way, the result fails closed.
- Ordinary work: no, because both records must be hand-written in a form `gov impact` never writes.
- Consequence: fails open (a Wave 3 row, DEC-801)

### E (MINOR): refusal messages misname the cause
- A CIT-P file missing from the working tree is refused with "lists nothing under `affected`".
- `--out ""` and `--out <folder>` are refused as "a file is there already".
- Ordinary work: yes, because a missing file or a wrong path is an everyday slip.
- Consequence: other (both fail closed)

## Re-probes of the first review's findings
All five are sound:
- **F1:** an added, staged or deleted record, or a store loaded on another branch, each read `stale` and name the path. With both graphs the report reads `complete: false`. The one remaining hole is B.
- **F2:** a string, map or integer kind is refused with `IMPACT_AFFECTED_MALFORMED`. Each of these is listed as a difference: ids differing in case, a leading space, a nested list, a missing kind, a null kind, an extra kind.
- **F3:** the CIT-P carries `complete: false`, `graphs` and `gaps`, and its body says the assessment is not complete.
- **F6:** a called and a dead `w37_shared` give not deletable, R1. Two dead definitions give deletable, R0.
- **F8:** a moved-in file dated 2001 reads `code: stale` and `complete: false`. A file holding a secret is not counted.

## Probed and found sound
- **No writes.** No `gov impact` run writes beyond `gov.codeintel`'s own daemon log and `.identity` file. Record-only runs, compares and refusals change nothing.
- **Refusals stay refusals.** No store (and none is created), an empty or garbage store, an unknown, empty, blank or missing change, and a malformed, compound or unquoted question all give exit 1 with no traceback. A refused `--out` writes nothing, and an existing file is not overwritten.
- **Questions.** Each form assesses the named id.
- **Baseline.** DEC-001 is R3 and `w37_apply` is R2, both `complete: true`.
- **Scope and trailers.** Every commit stays within its paths and carries its role. `bb630e54..ac4983f8` adds 364 lines and removes none. Nothing under `src/gov/closure/` changed.

## Judgement
**fail.** A and B are ordinary work and fail open. This was the second and last review (DEC-413), so there is no third round without the owner: the lead returns PACKAGES.
- **Recommended:** fold A and B into the held ticket's resume after W2-03 closes. That resume already needs a merge, a re-verify and a fresh probe.
- **Riding along in the resume (DEC-802):** C, E and F4.
- **Wave 3 rows (DEC-801):** D, F5 and F7.
