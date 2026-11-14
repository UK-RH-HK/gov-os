{
  "ticket": "DAEO-aks1",
  "ticket_text": "---\nid: DAEO-aks1\nstatus: in_progress\ndeps: [DAEO-2bdu]\nlinks: [DAEO-2bdu]\ncreated: 2026-11-12T16:55:43Z\ntype: task\npriority: 2\nassignee: research\nexternal-ref: W2-88b\nparent: DAEO-2bdu\ntags: [wave-2, research, adoption, memory, proofs, standard]\nwbs_id: W2-88b\ntitle: 'W2-88b W2-88''s proofs on real repositories: two public GitHub repositories and the register''s test repositories, on copies only'\nclass: research\nstate_class: AUTHORITATIVE\nrole: research\nprofile: STANDARD\ndepends_on:\n- DAEO-2bdu\nwaits_on:\n- ref: DAEO-2bdu\n  reason: the proofs run W2-88's landed tools\nallowed_paths:\n- experiments/W2-88/**\nest_loc: 0\nreads:\n- .tickets/DAEO-2bdu.md\n- docs/research/W2-88-memory-practice.md\n- src/gov/adopt/**\nneeds: []\nkpis:\n  success:\n  - 'The proofs, recorded in experiments/W2-88/any-repository.md, each with its commit, size, the assessment, the plan''s proposals (count and kinds), the per-store figures and the measure: Verify: experiments/W2-88/any-repository.md holds one section per proof, (b) and (c), and each names its commit, size, the assessment, the plan''s proposals (count and kinds), the per-store figures and the measure; a grep for any of those fields missing from a section finds none'\n  - '  (b) two real, messy, public GitHub repositories of different languages and sizes. Candidates for the test designer or the owner to confirm, each pinned to a commit: a large polyglot monorepo with generated code and large fixtures (for example grafana/grafana, Go and TypeScript, of the order of 10^4 files), and a mid-size repository of another language with vendored dependencies in its tree (for example redis/redis, C, with deps/). They are cloned by the lead or the CTO (network) under ~/gov-os-runs/W2-88/github/<name>/, with their licence recorded, never committed and never pushed anywhere. They report data under \"Memory works there\" and neither runs the full practice: the practice''s first full run (S12 to S14) is EXAMIN''s copy at W2-27, with no separate proof repository; what goes wrong there is fixed in the practice, and the repositories adopted after EXAMIN follow the practice as fixed. Verify: the proof record has a section for each of two public repositories of different languages, each pinned to a commit with its licence recorded and its data under \"Memory works there\"; the clones are under ~/gov-os-runs/W2-88/github/<name>/ and a search of this repository''s tracked files and history for the clones'' paths finds nothing; the record states that neither runs the full practice (S12 to S14) [DEC-954 Q9f, DEC-1099 (2)] [changed, DEC-1099 (2)]'\n  - '  (c) the test repositories the register names, each read through a clone under ~/gov-os-runs/W2-88/: ~/workspace (DEC-078, DEC-718: 77,346 nodes and 270,647 edges, 2.2 GB peak, the envelope''s top); the dev tiers ~/gov-os-workbench/synthetic/a-dev (ORION) and b-dev (ARGUS) (DEC-071, DEC-630); ARGUS''s stress tier (DEC-071: 5,355 files, 57,777 chunks) only if it lies outside the held-out qualification material; the assessment step only, never an adoption, on a clone of EXAMIN''s copy ~/gov-os-workbench/examin/ (DEC-723), to feed W2-27. Verify: the proof record has a section for each named test repository it used, each read through a clone under ~/gov-os-runs/W2-88/; the EXAMIN copy''s section holds the assessment record only and no adoption record; a grep of the record for ARGUS''s stress tier finds it only with its location outside the held-out qualification material stated [DEC-954 Q9f]'\n  - 'Scale: on each real proof repository ((b) and (c)) the stage records the query time of one plain question on each route, and the vector scan''s time against the retrieve budget. A figure over the budget or over DEC-078''s envelope is recorded with the measure, and returned as a proposal (a CIT-P or a ticket) for the owner, never a silent change of the store. Verify: on each proof repository the record holds the query time of one plain question on each route and the vector scan''s time against the retrieve budget; a planted figure over the budget is recorded with the measure and a proposal file (a CIT-P or a ticket) is written for the owner, and the store''s files are byte-identical before and after [DEC-954 Q9f, DEC-078, CAP-19]'\n  - 'Memory works there, measured: on each real proof repository ((b) and (c)) after A9, its questions are run end to end with the standard (S10, S15) and with W2-61''s measure, and right end to end, wrong claims and hit@5 are reported. W2-81''s per-repository sets apply to the synthetic repositories, and 10 questions written under the rubric by the independent writer and checker (S12) apply to each real repository; these figures are data, set no bar, and a shortfall is a named residual with its cause (DEC-954 Q9e). No proof repository here runs the full practice (S12 to S14): its first full run is EXAMIN''s copy at W2-27 (proof (d)), with no separate proof repository. Verify: on each proof repository after A9 the record holds the right-end-to-end, wrong-claim and hit@5 figures from the run with the standard (S10, S15) and W2-61''s measure; each real repository has its 10 questions with the writer''s and checker''s records; a planted low figure does not make the stage not ok (no bar) and appears as a named residual with its cause; the record names no proof repository as having run S12 to S14 [DEC-1099 (2), DEC-1098 (1), DEC-1097 (1)(d), DEC-833, DEC-860, CAP-10] [changed, DEC-1099 (2)]'\n  failure:\n  - 'A clone of a GitHub repository, or any of its files, in this repository or in a commit; a clone outside ~/gov-os-runs/W2-88/; a write in the workbench, EXAMIN''s real repository or the held-out qualification material. Verify: `git ls-files` and the branch''s history hold no path of a clone; each clone''s folder is under ~/gov-os-runs/W2-88/; the modification times of the workbench, EXAMIN''s real repository and the qualification material are unchanged after the run'\n  - 'Anything written in ~/workspace or in any of the owner''s own repositories: every proof works on copies only (clones under ~/gov-os-runs/W2-88/), never on the original Verify: the modification times and `git status` of ~/workspace and of each original the proofs read are unchanged after the run; every path the run wrote is under ~/gov-os-runs/W2-88/ or experiments/W2-88/ [DEC-1150 (1), DEC-723]'\nnon_goals:\n- the code (W2-88), the skill text (W2-88a), the synthetic repositories (W2-88's proof (a)), EXAMIN's copy (W2-27, proof (d))\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1150, DEC-996, DEC-954, DEC-1099, DEC-078, DEC-718, DEC-723]\ntrack: A\n---\n# W2-88b W2-88's proofs on real repositories (a child of W2-88)\n\nFiled by the owner's decision (DEC-1150 (1), package 1 (a), 2026-11-12), under DEC-996 (1)'s split list: W2-88 mixed three roles (DEC-995). This child holds the research half: proofs (b) and (c) moved word for word, the proof record (its path moved to `experiments/W2-88/any-repository.md`, the one folder a research worker writes), and the scale and measure lines for the real repositories. The owner added: proof (c) works on copies only; nothing is written in ~/workspace or in any of the owner's own repositories. It starts after W2-88 lands; it is not on W2-27's dependency chain (W2-27 needs W2-88's tools). If the research wall refuses the clones' folder under ~/gov-os-runs/W2-88/, that comes back as a package.\n\n**Notes moved from the front matter (2026-11-13, the CTO; the launcher reads list items raw):** `DAEO-2bdu` is W2-88: the tools (assessment, plan, A9 lite, the measure) these proofs run. `experiments/W2-88/**` is the one folder a research worker writes (DEC-996 (3) C); the proof record is here. **The copies' folder (P2 (a), the CTO under DEC-1156 (7)):** the clones go under `~/gov-os-runs/W2-88b/` (the folder the guard gives this ticket); where S2, S3, F1 and F2 name `~/gov-os-runs/W2-88/`, read `~/gov-os-runs/W2-88b/`, and the record states the path and the reason.\n",
  "authority": [
    {
      "id": "DEC-1150",
      "sha256": "426014d96506e8905b83ec14649c4df05847304c33793e338a7dcdc1d0063b29",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "426014d96506e8905b83ec14649c4df05847304c33793e338a7dcdc1d0063b29",
      "reason": "declared in sources",
      "tokens": 444
    },
    {
      "id": "DEC-996",
      "sha256": "388151798cf1224477e5ac5e4ef28b9fe9abb1575c37dacf1bb52dae20baec22",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "388151798cf1224477e5ac5e4ef28b9fe9abb1575c37dacf1bb52dae20baec22",
      "reason": "declared in sources",
      "tokens": 610
    },
    {
      "id": "DEC-954",
      "sha256": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
      "reason": "declared in sources",
      "tokens": 1881
    },
    {
      "id": "DEC-1099",
      "sha256": "b9c573f648306751605d024396c1389caa92b1c391b0323505292ca8c7a2cbfa",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b9c573f648306751605d024396c1389caa92b1c391b0323505292ca8c7a2cbfa",
      "reason": "declared in sources",
      "tokens": 693
    },
    {
      "id": "DEC-078",
      "sha256": "a4ff1f85485da1bf3e24937e66ac119487e56846e463a753100799ff4633a9e2",
      "authority": "decision",
      "lifecycle": "DONE",
      "constraint": "a4ff1f85485da1bf3e24937e66ac119487e56846e463a753100799ff4633a9e2",
      "reason": "declared in sources",
      "tokens": 250
    },
    {
      "id": "DEC-718",
      "sha256": "1934518e5b019b8a75d1943f41ee4552b3c806a8743b5417a822c4ef25febe48",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1934518e5b019b8a75d1943f41ee4552b3c806a8743b5417a822c4ef25febe48",
      "reason": "declared in sources",
      "tokens": 4248
    },
    {
      "id": "DEC-723",
      "sha256": "64490650b0f016881523f75f1f8f7914c8eca69fa6e0531e450409a535b30071",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "64490650b0f016881523f75f1f8f7914c8eca69fa6e0531e450409a535b30071",
      "reason": "declared in sources",
      "tokens": 315
    },
    {
      "id": "DAEO-2bdu",
      "sha256": "b3653385a5191d85946b54ad0df10498611ef55d7e1091c793bc0bed88273b5a",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "b3653385a5191d85946b54ad0df10498611ef55d7e1091c793bc0bed88273b5a",
      "reason": "declared in sources",
      "tokens": 5721
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1150",
      "sha256": "426014d96506e8905b83ec14649c4df05847304c33793e338a7dcdc1d0063b29",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "426014d96506e8905b83ec14649c4df05847304c33793e338a7dcdc1d0063b29",
      "reason": "declared in sources",
      "tokens": 444
    },
    {
      "id": "DEC-996",
      "sha256": "388151798cf1224477e5ac5e4ef28b9fe9abb1575c37dacf1bb52dae20baec22",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "388151798cf1224477e5ac5e4ef28b9fe9abb1575c37dacf1bb52dae20baec22",
      "reason": "declared in sources",
      "tokens": 610
    },
    {
      "id": "DEC-954",
      "sha256": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "44e6d9a16ad8b897f7935a33e86a52d379942c8b80615eacbcb2fb9215586cb4",
      "reason": "declared in sources",
      "tokens": 1881
    },
    {
      "id": "DEC-1099",
      "sha256": "b9c573f648306751605d024396c1389caa92b1c391b0323505292ca8c7a2cbfa",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b9c573f648306751605d024396c1389caa92b1c391b0323505292ca8c7a2cbfa",
      "reason": "declared in sources",
      "tokens": 693
    },
    {
      "id": "DEC-078",
      "sha256": "a4ff1f85485da1bf3e24937e66ac119487e56846e463a753100799ff4633a9e2",
      "authority": "decision",
      "lifecycle": "DONE",
      "constraint": "a4ff1f85485da1bf3e24937e66ac119487e56846e463a753100799ff4633a9e2",
      "reason": "declared in sources",
      "tokens": 250
    },
    {
      "id": "DEC-718",
      "sha256": "1934518e5b019b8a75d1943f41ee4552b3c806a8743b5417a822c4ef25febe48",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1934518e5b019b8a75d1943f41ee4552b3c806a8743b5417a822c4ef25febe48",
      "reason": "declared in sources",
      "tokens": 4248
    },
    {
      "id": "DEC-723",
      "sha256": "64490650b0f016881523f75f1f8f7914c8eca69fa6e0531e450409a535b30071",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "64490650b0f016881523f75f1f8f7914c8eca69fa6e0531e450409a535b30071",
      "reason": "declared in sources",
      "tokens": 315
    },
    {
      "id": "DAEO-2bdu",
      "sha256": "b3653385a5191d85946b54ad0df10498611ef55d7e1091c793bc0bed88273b5a",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "b3653385a5191d85946b54ad0df10498611ef55d7e1091c793bc0bed88273b5a",
      "reason": "declared in sources",
      "tokens": 5721
    }
  ],
  "supplementary": [],
  "supplementary_query": "W2-88b W2-88's proofs on real repositories: two public GitHub repositories and the register's test repositories, on copies only\nThe proofs, recorded in experiments/W2-88/any-repository.md, each with its commit, size, the assessment, the plan's proposals (count and kinds), the per-store figures and the measure: Verify: experiments/W2-88/any-repository.md holds one section per proof, (b) and (c), and each names its commit, size, the assessment, the plan's proposals (count and kinds), the per-store figures and the measure; a grep for any of those fields missing from a section finds none\n  (b) two real, messy, public GitHub repositories of different languages and sizes. Candidates for the test designer or the owner to confirm, each pinned to a commit: a large polyglot monorepo with generated code and large fixtures (for example grafana/grafana, Go and TypeScript, of the order of 10^4 files), and a mid-size repository of another language with vendored dependencies in its tree (for example redis/redis, C, with deps/). They are cloned by the lead or the CTO (network) under ~/gov-os-runs/W2-88/github/<name>/, with their licence recorded, never committed and never pushed anywhere. They report data under \"Memory works there\" and neither runs the full practice: the practice's first full run (S12 to S14) is EXAMIN's copy at W2-27, with no separate proof repository; what goes wrong there is fixed in the practice, and the repositories adopted after EXAMIN follow the practice as fixed. Verify: the proof record has a section for each of two public repositories of different languages, each pinned to a commit with its licence recorded and its data under \"Memory works there\"; the clones are under ~/gov-os-runs/W2-88/github/<name>/ and a search of this repository's tracked files and history for the clones' paths finds nothing; the record states that neither runs the full practice (S12 to S14) [DEC-954 Q9f, DEC-1099 (2)] [changed, DEC-1099 (2)]\n  (c) the test repositories the register names, each read through a clone under ~/gov-os-runs/W2-88/: ~/workspace (DEC-078, DEC-718: 77,346 nodes and 270,647 edges, 2.2 GB peak, the envelope's top); the dev tiers ~/gov-os-workbench/synthetic/a-dev (ORION) and b-dev (ARGUS) (DEC-071, DEC-630); ARGUS's stress tier (DEC-071: 5,355 files, 57,777 chunks) only if it lies outside the held-out qualification material; the assessment step only, never an adoption, on a clone of EXAMIN's copy ~/gov-os-workbench/examin/ (DEC-723), to feed W2-27. Verify: the proof record has a section for each named test repository it used, each read through a clone under ~/gov-os-runs/W2-88/; the EXAMIN copy's section holds the assessment record only and no adoption record; a grep of the record for ARGUS's stress tier finds it only with its location outside the held-out qualification material stated [DEC-954 Q9f]\nScale: on each real proof repository ((b) and (c)) the stage records the query time of one plain question on each route, and the vector scan's time against the retrieve budget. A figure over the budget or over DEC-078's envelope is recorded with the measure, and returned as a proposal (a CIT-P or a ticket) for the owner, never a silent change of the store. Verify: on each proof repository the record holds the query time of one plain question on each route and the vector scan's time against the retrieve budget; a planted figure over the budget is recorded with the measure and a proposal file (a CIT-P or a ticket) is written for the owner, and the store's files are byte-identical before and after [DEC-954 Q9f, DEC-078, CAP-19]\nMemory works there, measured: on each real proof repository ((b) and (c)) after A9, its questions are run end to end with the standard (S10, S15) and with W2-61's measure, and right end to end, wrong claims and hit@5 are reported. W2-81's per-repository sets apply to the synthetic repositories, and 10 questions written under the rubric by the independent writer and checker (S12) apply to each real repository; these figures are data, set no bar, and a shortfall is a named residual with its cause (DEC-954 Q9e). No proof repository here runs the full practice (S12 to S14): its first full run is EXAMIN's copy at W2-27 (proof (d)), with no separate proof repository. Verify: on each proof repository after A9 the record holds the right-end-to-end, wrong-claim and hit@5 figures from the run with the standard (S10, S15) and W2-61's measure; each real repository has its 10 questions with the writer's and checker's records; a planted low figure does not make the stage not ok (no bar) and appears as a named residual with its cause; the record names no proof repository as having run S12 to S14 [DEC-1099 (2), DEC-1098 (1), DEC-1097 (1)(d), DEC-833, DEC-860, CAP-10] [changed, DEC-1099 (2)]\nA clone of a GitHub repository, or any of its files, in this repository or in a commit; a clone outside ~/gov-os-runs/W2-88/; a write in the workbench, EXAMIN's real repository or the held-out qualification material. Verify: `git ls-files` and the branch's history hold no path of a clone; each clone's folder is under ~/gov-os-runs/W2-88/; the modification times of the workbench, EXAMIN's real repository and the qualification material are unchanged after the run\nAnything written in ~/workspace or in any of the owner's own repositories: every proof works on copies only (clones under ~/gov-os-runs/W2-88/), never on the original Verify: the modification times and `git status` of ~/workspace and of each original the proofs read are unchanged after the run; every path the run wrote is under ~/gov-os-runs/W2-88/ or experiments/W2-88/ [DEC-1150 (1), DEC-723]",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 16157,
  "budget": {
    "limit": 20000,
    "used": 16157
  },
  "hash": "774df4cc6377873ffc3590a95f4f0eb9a152096a702921107120281d46a0a588"
}
