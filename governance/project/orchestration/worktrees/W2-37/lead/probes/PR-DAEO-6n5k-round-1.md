---
type: probe
task: DAEO-6n5k
reviewer_session: 606bdff7-6e36-41ce-a19e-9dd9357e8407
implementer_session: 95a6e9ea-8399-43d2-a23d-448732a6d6d7
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: fail
probed_commit: 6b5640b0b0662a4d81ff0415f454acd9731db7a0
---

# Probe record (draft, failing): W2-37 `gov impact`, first review

Kept as a draft under the lead's scratch folder: a failing review's record is never committed (the probe gate reads every committed record).

- **What was probed.** The head `6b5640b0` on `w2/W2-37` (engineer session `95a6e9ea-8399-43d2-a23d-448732a6d6d7`, commit `2234049f`). A fresh read-only reviewer (role `independent-auditor`, session `606bdff7-6e36-41ce-a19e-9dd9357e8407`, 2026-10-19), commissioned and judged by the orchestrator, launched sandboxed through `gov launch`, then resumed in the same session in the owner's launch form for the code-graph probes (P-W2-38). It wrote nothing in the repository (tripwire: no change in this worktree, either pass). Threat model: ADR-0001 as DEC-801 states it.
- **Tests seen by the reviewer.** Sandboxed: W2-37 + `tests/unit/impact` 79 passed, 3 failed (the P-1 ×2 and P-2 expected reds), 12 errors (P-W2-38). Outside: the 13 `local_only` cases, 13 passed.

## Findings

### F1 (MAJOR) — uncommitted or older-branch record state reads `ok` and `complete: true`
An uncommitted ticket implementing DEC-001 and an uncommitted removal of DEC-002's edge, with a current store and code index: `gov impact DEC-001` gave `graphs.record: ok`, `complete: true`, the new ticket neither listed nor a gap, DEC-002 still listed. A store loaded on a newer branch read `ok` on an older one (lists a ticket not in the tree, drops one that is). `gov closure` reports `uncommitted` files for the same tree.
- Ordinary work: yes, because changing a decision and asking its impact before committing is KPI 1's own flow, and switching branches after a load is routine.
- Consequence: fails open

### F2 (MAJOR) — a CIT-E kind written as a single value or a map is ignored, and the CIT-E matches
Proposal `code: []`, CIT-E `code: w37_orphan` (or `decisions: {DEC-099: done}`): `--compare` gave `matches: true, differences: []`.
- Ordinary work: yes, because `key: value` for `key: [value]` is a common YAML slip.
- Consequence: fails open

### F3 (MAJOR) — the CIT-P written by `--out` drops the report's incompleteness
With no code index, the printed report was `complete: false` with a `CODE_GRAPH_MISSING` gap; the file written had only `change`, `radius`, `depth` and `affected` (`code: []`), no `complete`, `graphs` or `gaps`.
- Ordinary work: yes, because any project without a current code index that uses `--out` hits it.
- Consequence: fails open (the lead's reading: the persisted impact report reads as complete when a graph was missing; the reviewer gave "other")

### F6 (MAJOR) — a live symbol sharing its bare name with a dead one is read deletable, radius R0
Two `w37_dup` definitions, one dead, one called: the live one's change gave `deletable: true`, radius R0 (control: R1). Nothing dropped from the lists; the radius (which sets the profile) is lowered.
- Ordinary work: yes, because the same function name in several modules is common.
- Consequence: fails open

### F8 (MAJOR) — a new code file with an older modification time leaves the code graph `ok`
A new caller of `w37_apply` moved into the tree with its date kept (`mv`, `cp -p`, unpacking): `graphs.code: ok`, `complete: true`, the caller not listed. An in-place edit with its date kept is caught (sound).
- Ordinary work: yes, because moving a file drafted elsewhere into the tree keeps its date.
- Consequence: fails open

### F4 (MINOR) — the `--out` file's stem becomes the CIT-P id with no clash check
`--out docs/impact/SPEC-300.md` writes a CIT-P with id SPEC-300; the store keeps the specification and silently leaves the CIT-P out.
- Ordinary work: yes, because naming the impact file after the changed item is natural.
- Consequence: other (fails closed)

### F5 (MINOR) — `--out` of a read command writes where the guard does not look
`--out` wrote through `../`, into `.git/`, through a dangling link; a plain out-of-scope path is not stopped by the guard (it polices no `gov` command's writes). It never overwrites.
- Ordinary work: no for the link, `..` and `.git/` (deliberate constructions); yes for a plain out-of-scope path.
- Consequence: other

### F7 (MINOR) — an error from the code index during the walk ends in a traceback
Simulated: `callers`/`callees` raising gives exit 1 with a traceback, no envelope; no complete-looking answer.
- Ordinary work: no, because the graph is read once and cached; a later failure needs an artificial fault.
- Consequence: other (fails closed)

## Probed and found sound
Read-only without `--out` (tree, store, HEAD, refs, stash, index unchanged); `--out` adds one file and refuses an existing one; refusals stay refusals (no store, damaged store, empty, blank or unknown change, malformed CIT-E, conflicting options); questions assess exactly the id asked or are refused; CIT-E case, kind, missing and extra list items are differences; impact's record items plus gaps equal `gov closure`'s set at the same depth (DEC-001, DEC-003, DEC-070); every commit within its paths with its role; no change under `src/gov/closure/`; acceptance tests unchanged since the test designer's commit.

## Judgement
fail: F1, F2, F3, F6 and F8 are ordinary work and fail open. They go to a test design batch (DEC-136), a fresh engineer and a second, last review (DEC-413). F4 rides along in the resume (DEC-802); F5 and F7 are Wave 3 hardening rows (DEC-801); F5's guard side is returned as a package (DEC-779).
