---
id: DAEO-aks1
status: open
deps: [DAEO-2bdu]
links: [DAEO-2bdu]
created: 2026-11-12T16:55:43Z
type: task
priority: 2
assignee: research
external-ref: W2-88b
parent: DAEO-2bdu
tags: [wave-2, research, adoption, memory, proofs, standard]
wbs_id: W2-88b
title: 'W2-88b W2-88''s proofs on real repositories: two public GitHub repositories and the register''s test repositories, on copies only'
class: research
state_class: AUTHORITATIVE
role: research
profile: STANDARD
depends_on:
- DAEO-2bdu  # W2-88: the tools (assessment, plan, A9 lite, the measure) these proofs run
waits_on:
- ref: DAEO-2bdu
  reason: the proofs run W2-88's landed tools
allowed_paths:
- experiments/W2-88/**  # the one folder a research worker writes (DEC-996 (3) C); the proof record is here
est_loc: 0
reads:
- .tickets/DAEO-2bdu.md
- docs/research/W2-88-memory-practice.md
- src/gov/adopt/**
needs: []
kpis:
  success:
  - 'The proofs, recorded in experiments/W2-88/any-repository.md, each with its commit, size, the assessment, the plan''s proposals (count and kinds), the per-store figures and the measure: Verify: experiments/W2-88/any-repository.md holds one section per proof, (b) and (c), and each names its commit, size, the assessment, the plan''s proposals (count and kinds), the per-store figures and the measure; a grep for any of those fields missing from a section finds none'
  - '  (b) two real, messy, public GitHub repositories of different languages and sizes. Candidates for the test designer or the owner to confirm, each pinned to a commit: a large polyglot monorepo with generated code and large fixtures (for example grafana/grafana, Go and TypeScript, of the order of 10^4 files), and a mid-size repository of another language with vendored dependencies in its tree (for example redis/redis, C, with deps/). They are cloned by the lead or the CTO (network) under ~/gov-os-runs/W2-88/github/<name>/, with their licence recorded, never committed and never pushed anywhere. They report data under "Memory works there" and neither runs the full practice: the practice''s first full run (S12 to S14) is EXAMIN''s copy at W2-27, with no separate proof repository; what goes wrong there is fixed in the practice, and the repositories adopted after EXAMIN follow the practice as fixed. Verify: the proof record has a section for each of two public repositories of different languages, each pinned to a commit with its licence recorded and its data under "Memory works there"; the clones are under ~/gov-os-runs/W2-88/github/<name>/ and a search of this repository''s tracked files and history for the clones'' paths finds nothing; the record states that neither runs the full practice (S12 to S14) [DEC-954 Q9f, DEC-1099 (2)] [changed, DEC-1099 (2)]'
  - '  (c) the test repositories the register names, each read through a clone under ~/gov-os-runs/W2-88/: ~/workspace (DEC-078, DEC-718: 77,346 nodes and 270,647 edges, 2.2 GB peak, the envelope''s top); the dev tiers ~/gov-os-workbench/synthetic/a-dev (ORION) and b-dev (ARGUS) (DEC-071, DEC-630); ARGUS''s stress tier (DEC-071: 5,355 files, 57,777 chunks) only if it lies outside the held-out qualification material; the assessment step only, never an adoption, on a clone of EXAMIN''s copy ~/gov-os-workbench/examin/ (DEC-723), to feed W2-27. Verify: the proof record has a section for each named test repository it used, each read through a clone under ~/gov-os-runs/W2-88/; the EXAMIN copy''s section holds the assessment record only and no adoption record; a grep of the record for ARGUS''s stress tier finds it only with its location outside the held-out qualification material stated [DEC-954 Q9f]'
  - 'Scale: on each real proof repository ((b) and (c)) the stage records the query time of one plain question on each route, and the vector scan''s time against the retrieve budget. A figure over the budget or over DEC-078''s envelope is recorded with the measure, and returned as a proposal (a CIT-P or a ticket) for the owner, never a silent change of the store. Verify: on each proof repository the record holds the query time of one plain question on each route and the vector scan''s time against the retrieve budget; a planted figure over the budget is recorded with the measure and a proposal file (a CIT-P or a ticket) is written for the owner, and the store''s files are byte-identical before and after [DEC-954 Q9f, DEC-078, CAP-19]'
  - 'Memory works there, measured: on each real proof repository ((b) and (c)) after A9, its questions are run end to end with the standard (S10, S15) and with W2-61''s measure, and right end to end, wrong claims and hit@5 are reported. W2-81''s per-repository sets apply to the synthetic repositories, and 10 questions written under the rubric by the independent writer and checker (S12) apply to each real repository; these figures are data, set no bar, and a shortfall is a named residual with its cause (DEC-954 Q9e). No proof repository here runs the full practice (S12 to S14): its first full run is EXAMIN''s copy at W2-27 (proof (d)), with no separate proof repository. Verify: on each proof repository after A9 the record holds the right-end-to-end, wrong-claim and hit@5 figures from the run with the standard (S10, S15) and W2-61''s measure; each real repository has its 10 questions with the writer''s and checker''s records; a planted low figure does not make the stage not ok (no bar) and appears as a named residual with its cause; the record names no proof repository as having run S12 to S14 [DEC-1099 (2), DEC-1098 (1), DEC-1097 (1)(d), DEC-833, DEC-860, CAP-10] [changed, DEC-1099 (2)]'
  failure:
  - 'A clone of a GitHub repository, or any of its files, in this repository or in a commit; a clone outside ~/gov-os-runs/W2-88/; a write in the workbench, EXAMIN''s real repository or the held-out qualification material. Verify: `git ls-files` and the branch''s history hold no path of a clone; each clone''s folder is under ~/gov-os-runs/W2-88/; the modification times of the workbench, EXAMIN''s real repository and the qualification material are unchanged after the run'
  - 'Anything written in ~/workspace or in any of the owner''s own repositories: every proof works on copies only (clones under ~/gov-os-runs/W2-88/), never on the original Verify: the modification times and `git status` of ~/workspace and of each original the proofs read are unchanged after the run; every path the run wrote is under ~/gov-os-runs/W2-88/ or experiments/W2-88/ [DEC-1150 (1), DEC-723]'
non_goals:
- the code (W2-88), the skill text (W2-88a), the synthetic repositories (W2-88's proof (a)), EXAMIN's copy (W2-27, proof (d))
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1150, DEC-996, DEC-954, DEC-1099, DEC-078, DEC-718, DEC-723]
track: A
---
# W2-88b W2-88's proofs on real repositories (a child of W2-88)

Filed by the owner's decision (DEC-1150 (1), package 1 (a), 2026-11-12), under DEC-996 (1)'s split list: W2-88 mixed three roles (DEC-995). This child holds the research half: proofs (b) and (c) moved word for word, the proof record (its path moved to `experiments/W2-88/any-repository.md`, the one folder a research worker writes), and the scale and measure lines for the real repositories. The owner added: proof (c) works on copies only; nothing is written in ~/workspace or in any of the owner's own repositories. It starts after W2-88 lands; it is not on W2-27's dependency chain (W2-27 needs W2-88's tools). If the research wall refuses the clones' folder under ~/gov-os-runs/W2-88/, that comes back as a package.
