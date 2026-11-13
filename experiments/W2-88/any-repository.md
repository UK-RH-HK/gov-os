---
id: W2-88b-any-repository
title: "W2-88's proofs (b) and (c) on real repositories, on copies only (ticket DAEO-aks1, W2-88b)"
type: research-record
role: research
decisions: [DEC-1150, DEC-996, DEC-954, DEC-1099]
sources: [DEC-1150, DEC-996, DEC-954, DEC-1099, DEC-078, DEC-718, DEC-723, DEC-1156, DEC-1064, DEC-1065]
state: skeleton
---

# W2-88's proofs (b) and (c): the tools on real repositories, on copies only

**State: skeleton (batch 1).** Every line that reads `pending` is filled from the lead's results files in batch 2; no
figure here was measured yet, and none is estimated. A line that waits on the owner reads `pending: P3` (the operator's
clones of the workbench repositories) or `pending: P4` (the independent writer's and checker's 10 questions for each
real repository); neither is invented.

## What this is

Question: does W2-88's chain (the assessment MA and its plan, A0 to A6, A8, A9 lite) work on real, messy repositories,
and what does it cost there? The decision it feeds: the owner's reading of W2-88's tools before W2-27 runs them on
EXAMIN's copy (DEC-1150 (1), DEC-996 (1), DEC-954 Q9f). The figures are **data and set no bar** (DEC-954 Q9e); a
shortfall is a named residual with its cause.

**Where the copies are, and why `W2-88b`.** The ticket's text names `~/gov-os-runs/W2-88/`. The guard lets this ticket
write only its own runs folder, `~/gov-os-runs/W2-88b/` (`src/gov/guard/decide.py:166`, `src/gov/guard/runs.py:118`), so
the clones are under `~/gov-os-runs/W2-88b/` (a folder for each clone, never in this repository). This is decided: P2
(a), the CTO under DEC-1156 (7), written in the ticket's body; where S2, S3, F1 and F2 name `~/gov-os-runs/W2-88/`, read
`~/gov-os-runs/W2-88b/`. The record gives no clone's own path, so that a search of the tracked files and the history for
the clones' paths finds nothing.

**What runs where.** The proofs need the network (GitHub clones), the real embedder, the shared reranker and the code
graph, none of which run in the research sandbox (DEC-1064, DEC-1065 (1)). The script `experiments/W2-88/proof_bc.py`
is written and tested here with stand-ins; the lead runs it outside the sandbox, in the heavy slot, one repository to a
process. Its result is `<runs>/results/<name>.json` (counts, ids, digests and figures only), its assessment, plan and
scale files are under `<runs>/out/<name>/`.

**What stands in.** In the sandbox test only (a planted repository, not a proof repository): `--stand-in` (one hash
vector for each chunk), `PROOF_CODE_GRAPH=0`, and a rebuild lock in the sandbox's own temp folder. The real runs use
none of these; each result records `stand_in` and `code_graph_requested`. The A5 verdict of a full run is the proof's
own stand-in commit (`Role: independent-auditor`), not an independent audit: it lets A6 and A8 run on a path map with no
action.

**Repositories.** Proof (b): grafana/grafana (Go and TypeScript, the large polyglot monorepo) and redis/redis (C, with
`deps/`, mid-size with vendored dependencies), each pinned to a commit with its licence recorded. Proof (c): `~/workspace`
(DEC-078, DEC-718: 77,346 nodes and 270,647 edges, 2.2 GB peak, the envelope's top), the dev tiers a-dev (ORION) and
b-dev (ARGUS), ARGUS's stress tier (only if its location lies outside the held-out qualification material), and, for the
assessment only, EXAMIN's copy.

**Command (one repository, run by the lead).**
`python3 experiments/W2-88/proof_bc.py --repo <name> --root <the clone> --runs ~/gov-os-runs/W2-88b [--assess-only]
[--questions <file>] [--budget-ms <N>] [--origin <url>] [--licence <SPDX>]`.

## Proof (b): two public GitHub repositories of different languages

Neither runs the full practice (S12 to S14); both report data under "Memory works there".

### grafana/grafana

- **commit:** pending (the clone's HEAD before any proof commit, full hash; the assessed commit; A9's commit).
- **licence:** pending (AGPL-3.0 expected: the licence file's path and sha256 in the clone, and the SPDX id as given).
- **size:** pending (files, bytes, commits; whether the clone is shallow).
- **assessment:** pending (binary, generated, minified, vendored, secrets by rule id, files no route can take with
  reasons; the estimate; the assessment's own peak RSS against the per-session figure).
- **plan's proposals (count and kinds):** pending.
- **per-store figures:** pending (judged, indexed, refused with reasons, chunks, vectors, nodes, edges, seconds; digests).
- **scale:** pending (one plain question's time on each route; the vector scan against the retrieve budget of 2,000 ms;
  the envelope figures found; whether `SCALE-PROPOSAL.md` was written).
- **measure:** pending (right end to end, wrong claims, hit@5, residuals).
- **questions:** pending: P4 (10, written under the rubric by the independent writer and checker opened by the owner's
  operator; their records).

### redis/redis

- **commit:** pending.
- **licence:** pending (BSD-3-Clause expected for the versions then in the tree: the file and its sha256 decide).
- **size:** pending.
- **assessment:** pending.
- **plan's proposals (count and kinds):** pending.
- **per-store figures:** pending.
- **scale:** pending.
- **measure:** pending.
- **questions:** pending: P4.

## Proof (c): the register's test repositories, each read through a clone

### ~/workspace

Read through a `git clone --no-hardlinks` made by the lead; the original is never written (F2).

- **commit:** pending.
- **size:** pending.
- **assessment:** pending.
- **plan's proposals (count and kinds):** pending.
- **per-store figures:** pending (DEC-078, DEC-718: 77,346 nodes, 270,647 edges, 2.2 GB peak to compare).
- **scale:** pending.
- **measure:** pending.

### a-dev (ORION)

- **commit:** pending: P3 (the operator's clone; agents never read the workbench, DEC-723).
- **size:** pending: P3.
- **assessment:** pending: P3.
- **plan's proposals (count and kinds):** pending: P3.
- **per-store figures:** pending: P3.
- **scale:** pending: P3.
- **measure:** pending: P3 (W2-81's per-repository sets apply to the synthetic repositories).

### b-dev (ARGUS)

- **commit:** pending: P3.
- **size:** pending: P3.
- **assessment:** pending: P3.
- **plan's proposals (count and kinds):** pending: P3.
- **per-store figures:** pending: P3.
- **scale:** pending: P3.
- **measure:** pending: P3.

### ARGUS's stress tier

Used only if its location lies outside the held-out qualification material, and the owner's operator confirms that:
pending: P3. Nothing of its contents is named here, and no agent reads it. If the operator says it lies inside, this
section is replaced by that one line and no figure is taken.

- **commit:** pending: P3.
- **size:** pending: P3 (DEC-071 states 5,355 files and 57,777 chunks to compare).
- **assessment:** pending: P3.
- **plan's proposals (count and kinds):** pending: P3.
- **per-store figures:** pending: P3.
- **scale:** pending: P3.
- **measure:** pending: P3.

### EXAMIN's copy (the assessment only)

This section holds the assessment only, to feed W2-27 (proof (d)); **no adoption ran** on it (`adoption: none` in its
result), no stage A0 to A9, no commit in the clone, and the clone is checked unchanged (HEAD and `git status`) at the end
of the run. The clone is the operator's (DEC-723); the lead gives its path to the script with `--assess-only`.

- **commit:** pending: P3 (the assessed commit).
- **size:** pending: P3.
- **assessment:** pending: P3.
- **plan's proposals (count and kinds):** pending: P3 (proposals as files for the owner; none applied).
- **per-store figures:** not applicable: the assessment only; no store was built.
- **scale:** not applicable: the assessment only; its estimate is under **assessment**.
- **measure:** not applicable: the assessment only; no question was run.

## No proof repository here runs the full practice (S12 to S14)

No repository above runs the full practice: S12 to S14 (the question set, its writer and checker, the baseline
audit) are not run on any of them. The practice's first full run is EXAMIN's copy at W2-27 (proof (d)), with no separate
proof repository (DEC-1099 (2)); what goes wrong there is fixed in the practice, and the repositories adopted after
EXAMIN follow the practice as fixed. The 10 questions of each real repository (P4) feed the measure only; a shortfall is
a named residual with its cause, never a bar.

## Copies only

What was written and where (F1, F2), to be completed from the lead's run:

- In this repository: `experiments/W2-88/proof_bc.py` and this record. No clone, no file of a clone and no result file.
- Under `~/gov-os-runs/W2-88b/`: the clones (a folder for each), `results/<name>.json`, `out/<name>/` (the assessment,
  the plan, the scale proposal if any, the audit records A9 writes), `out/<name>-alone/` (the assessment alone, for its
  peak RSS), `work/<name>/` (the empty proposal). In each clone of a full run: the proof's commits and `.gov-runtime/`
  (the clone is the copy). The clones are never committed or pushed.
- Outside both: the machine's rebuild lock (`/tmp`, one rebuild at a time, W2-76), and the shared reranker's own files.
- Not written: `~/workspace`, the workbench, EXAMIN's real repository and the held-out qualification material. The
  modification times and `git status` of each original are to be taken before and after the lead's run: pending.
- The store is never changed by a proposal (S4): the result holds the sha256 of every file of the clone's store taken
  right after A9 and again at the script's end: pending.
