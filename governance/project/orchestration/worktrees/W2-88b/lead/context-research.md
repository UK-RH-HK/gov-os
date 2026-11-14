{
  "ticket": "DAEO-aks1",
  "ticket_text": "---\nid: DAEO-aks1\nstatus: in_progress\ndeps: [DAEO-2bdu]\nlinks: [DAEO-2bdu]\ncreated: 2026-11-12T16:55:43Z\ntype: task\npriority: 2\nassignee: research\nexternal-ref: W2-88b\nparent: DAEO-2bdu\ntags: [wave-2, research, adoption, memory, proofs, standard]\nwbs_id: W2-88b\ntitle: 'W2-88b W2-88''s proofs on real repositories: two public GitHub repositories and the register''s test repositories, on copies only'\nclass: research\nstate_class: AUTHORITATIVE\nrole: research\nprofile: STANDARD\ndepends_on:\n- DAEO-2bdu  # W2-88: the tools (assessment, plan, A9 lite, the measure) these proofs run\nwaits_on:\n- ref: DAEO-2bdu\n  reason: the proofs run W2-88's landed tools\nallowed_paths:\n- experiments/W2-88/**  # the one folder a research worker writes (DEC-996 (3) C); the proof record is here\nest_loc: 0\nreads:\n- .tickets/DAEO-2bdu.md\n- docs/research/W2-88-memory-practice.md\n- src/gov/adopt/**\nneeds: []\nkpis:\n  success:\n  - 'The proofs, recorded in experiments/W2-88/any-repository.md, each with its commit, size, the assessment, the plan''s proposals (count and kinds), the per-store figures and the measure: Verify: experiments/W2-88/any-repository.md holds one section per proof, (b) and (c), and each names its commit, size, the assessment, the plan''s proposals (count and kinds), the per-store figures and the measure; a grep for any of those fields missing from a section finds none'\n  - '  (b) two real, messy, public GitHub repositories of different languages and sizes. Candidates for the test designer or the owner to confirm, each pinned to a commit: a large polyglot monorepo with generated code and large fixtures (for example grafana/grafana, Go and TypeScript, of the order of 10^4 files), and a mid-size repository of another language with vendored dependencies in its tree (for example redis/redis, C, with deps/). They are cloned by the lead or the CTO (network) under ~/gov-os-runs/W2-88/github/<name>/, with their licence recorded, never committed and never pushed anywhere. They report data under \"Memory works there\" and neither runs the full practice: the practice''s first full run (S12 to S14) is EXAMIN''s copy at W2-27, with no separate proof repository; what goes wrong there is fixed in the practice, and the repositories adopted after EXAMIN follow the practice as fixed. Verify: the proof record has a section for each of two public repositories of different languages, each pinned to a commit with its licence recorded and its data under \"Memory works there\"; the clones are under ~/gov-os-runs/W2-88/github/<name>/ and a search of this repository''s tracked files and history for the clones'' paths finds nothing; the record states that neither runs the full practice (S12 to S14) [DEC-954 Q9f, DEC-1099 (2)] [changed, DEC-1099 (2)]'\n  - '  (c) the test repositories the register names, each read through a clone under ~/gov-os-runs/W2-88/: ~/workspace (DEC-078, DEC-718: 77,346 nodes and 270,647 edges, 2.2 GB peak, the envelope''s top); the dev tiers ~/gov-os-workbench/synthetic/a-dev (ORION) and b-dev (ARGUS) (DEC-071, DEC-630); ARGUS''s stress tier (DEC-071: 5,355 files, 57,777 chunks) only if it lies outside the held-out qualification material; the assessment step only, never an adoption, on a clone of EXAMIN''s copy ~/gov-os-workbench/examin/ (DEC-723), to feed W2-27. Verify: the proof record has a section for each named test repository it used, each read through a clone under ~/gov-os-runs/W2-88/; the EXAMIN copy''s section holds the assessment record only and no adoption record; a grep of the record for ARGUS''s stress tier finds it only with its location outside the held-out qualification material stated [DEC-954 Q9f]'\n  - 'Scale: on each real proof repository ((b) and (c)) the stage records the query time of one plain question on each route, and the vector scan''s time against the retrieve budget. A figure over the budget or over DEC-078''s envelope is recorded with the measure, and returned as a proposal (a CIT-P or a ticket) for the owner, never a silent change of the store. Verify: on each proof repository the record holds the query time of one plain question on each route and the vector scan''s time against the retrieve budget; a planted figure over the budget is recorded with the measure and a proposal file (a CIT-P or a ticket) is written for the owner, and the store''s files are byte-identical before and after [DEC-954 Q9f, DEC-078, CAP-19]'\n  - 'Memory works there, measured: on each real proof repository ((b) and (c)) after A9, its questions are run end to end with the standard (S10, S15) and with W2-61''s measure, and right end to end, wrong claims and hit@5 are reported. W2-81''s per-repository sets apply to the synthetic repositories, and 10 questions written under the rubric by the independent writer and checker (S12) apply to each real repository; these figures are data, set no bar, and a shortfall is a named residual with its cause (DEC-954 Q9e). No proof repository here runs the full practice (S12 to S14): its first full run is EXAMIN''s copy at W2-27 (proof (d)), with no separate proof repository. Verify: on each proof repository after A9 the record holds the right-end-to-end, wrong-claim and hit@5 figures from the run with the standard (S10, S15) and W2-61''s measure; each real repository has its 10 questions with the writer''s and checker''s records; a planted low figure does not make the stage not ok (no bar) and appears as a named residual with its cause; the record names no proof repository as having run S12 to S14 [DEC-1099 (2), DEC-1098 (1), DEC-1097 (1)(d), DEC-833, DEC-860, CAP-10] [changed, DEC-1099 (2)]'\n  failure:\n  - 'A clone of a GitHub repository, or any of its files, in this repository or in a commit; a clone outside ~/gov-os-runs/W2-88/; a write in the workbench, EXAMIN''s real repository or the held-out qualification material. Verify: `git ls-files` and the branch''s history hold no path of a clone; each clone''s folder is under ~/gov-os-runs/W2-88/; the modification times of the workbench, EXAMIN''s real repository and the qualification material are unchanged after the run'\n  - 'Anything written in ~/workspace or in any of the owner''s own repositories: every proof works on copies only (clones under ~/gov-os-runs/W2-88/), never on the original Verify: the modification times and `git status` of ~/workspace and of each original the proofs read are unchanged after the run; every path the run wrote is under ~/gov-os-runs/W2-88/ or experiments/W2-88/ [DEC-1150 (1), DEC-723]'\nnon_goals:\n- the code (W2-88), the skill text (W2-88a), the synthetic repositories (W2-88's proof (a)), EXAMIN's copy (W2-27, proof (d))\ndone_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]\nsources: [DEC-1150, DEC-996, DEC-954, DEC-1099, DEC-078, DEC-718, DEC-723]\ntrack: A\n---\n# W2-88b W2-88's proofs on real repositories (a child of W2-88)\n\nFiled by the owner's decision (DEC-1150 (1), package 1 (a), 2026-11-12), under DEC-996 (1)'s split list: W2-88 mixed three roles (DEC-995). This child holds the research half: proofs (b) and (c) moved word for word, the proof record (its path moved to `experiments/W2-88/any-repository.md`, the one folder a research worker writes), and the scale and measure lines for the real repositories. The owner added: proof (c) works on copies only; nothing is written in ~/workspace or in any of the owner's own repositories. It starts after W2-88 lands; it is not on W2-27's dependency chain (W2-27 needs W2-88's tools). If the research wall refuses the clones' folder under ~/gov-os-runs/W2-88/, that comes back as a package.\n",
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
  "supplementary": [
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "#### W2-88 Memory for any repository: assess, plan the refactoring, build the full index and embeddings, set up the stores (FULL, engineer; DEC-954 Q9f; Wave 2's minimum; to file)\n- **Draft:** `.gov-runtime/scratch/orchestrator/drafts/tickets/W2-88.md`, with its KPIs, paths and proofs.\n- **Why:** \"if we build memory that only this repository can use, we have built nothing\" (the owner, DEC-954 Q9f). Today:\n  - adoption has no knowledge-fabric stage (CAP-44.f's A9 is Wave 3 in the Contract);\n  - `gov rebuild` on an unadopted clone builds no index and says ok (W2-26's finding 2);\n  - nothing assesses a large repository or plans what full indexing needs.\n- **Allowed paths:** new modules under `src/gov/adopt/` (the assessment, the refactoring plan, the A9 lite stage), the stage list in `src/gov/adopt/command.py`, `project.py` and `stages.py`, `src/gov/rebuild/command.py` (the result's `ok` only), `src/gov/store/layout.py` (new), the adopt skill's A9 step and its generated copies, `tests/unit/adopt/test_w2_88*`, `docs/research/W2-88-any-repository.md`, `docs/changes/W2-88-CIT-P.md`. Clones go under `~/gov-os-runs/W2-88/` and are never committed.\n- **KPIs, success:**\n",
      "tokens": 295
    },
    {
      "id": "7c99160bec6d01c496740381",
      "path": "governance/project/orchestration/packages/LIFT-1/GLOSSARY-1.md",
      "text": "### 5.3 W2-88's line (open, not started; marked DEC-1096; DEC-1088 (6))\nAdded to `kpis.success`, after the A9 line. `waits_on` gains `W2-143`, marked the same. W2-88's own rule holds: a KPI\nchange goes through its test designer.\n```\n- 'The glossary at Wave 0 (DEC-1096 (5)): A9 lite''s build writes the repository''s glossary and code map (W2-143''s stage of gov rebuild). On each proof repository the stage''s record holds the entries by kind, the code map by kind and language, the files not mapped with their reason, the size and the build time; five of the repository''s own ids or code names, chosen by the test designer, each come first in gov glossary; a build without a glossary names its reason in the stage''s record. Verify: the proofs'' records in docs/research/W2-88-any-repository.md and one planted repository [DEC-1096, DEC-1072 (2), DEC-954 Q9f] [added, DEC-1096]'\n```\n\n",
      "tokens": 222
    },
    {
      "id": "35aa33fcb914963afa8544d2",
      "path": "governance/project/orchestration/packages/ROLES-SPEC-1.md",
      "text": "### 6.4 New tickets\n\n| Proposed id | Title | Class \u00b7 profile | Est. | Order |\n|---|---|---|---|---|\n| W2-00a | S1 Memory stream: the Senior Engineer's coordination | coordination \u00b7 LITE | CTO, minutes | filed when the roles land, before ACT 2 |\n| W2-00b | Agents stream (S2+S3): the Senior Engineer's coordination | coordination \u00b7 LITE | same | same |\n| W2-00c | S4 Adoption stream: the Senior Engineer's coordination | coordination \u00b7 LITE | same | same |\n| W2-89 | The CTO's watchers: each Senior Engineer's state (`gov streams`) | implementation \u00b7 STANDARD | 9.2 h | before ACT 2 |\n\n(W2-88 is left for DEC-954 Q9f's any-repository memory ticket; renumber if the CTO used it otherwise.)\n\n**W2-00a/b/c KPIs (outline):** every session of that stream's SE runs with `GOV_TICKET` = this id; its\nhandoffs and state are under its stream folder; it closes after its stream's last ticket, before W2-00.\nPaths: `.gov-runtime/scratch/streams/<stream>/**`.\n\n**W2-89 KPIs (outline):**\n- `gov streams` (read-only) shows each stream: its SE's state and since when, whether its process is alive\n  (launch record), the leads running, released tickets not started, and the last return [DEC-954 Q13b];\n",
      "tokens": 297
    },
    {
      "id": "1635e0d13b9641267936680e",
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md",
      "text": "  - 'S14 The bar: on the verdict set, judged on the declared configuration only. The figure is right end to end: the answer correct and its citation right, graded by a named grader model, with a second grader''s agreement reported. It must be at least 85 % with wrong claims at most 5 %; the target is 95 %. On n judged questions that is at least ceil(0.85 n) right and at most floor(0.05 n) wrong claims. Reported beside it, never judged: hit@5, gold in the first bundle, the answer correct with the citation set aside, the stricter grade, one search against two (exact McNemar), the exact 95 % interval, and the reader model by name. Verify: the result record in docs/research/W2-88-any-repository.md (or the adopted repository''s copy of it) holds the verdict line and the side table [DEC-1097 (1)(d), DEC-1098 (1), DEC-957, CAP-10, DEC-1079] [added, DEC-1098 (1)]'\n",
      "tokens": 218
    },
    {
      "id": "5e238b4671bff36b1c7afc8a",
      "path": "tests/acceptance/W2-88/README.md",
      "text": "  full: an A9 that builds in another process makes the case say the plant did not take. No question is run through the reader here (the\n  standing residual says so).\n- **P-2 (S15, the result record).** `docs/research/W2-88-any-repository.md` is W2-88b's (DEC-1150 (1)); no file is stated here for the verdict line\n  and the side table. The cases judge `gov.memaudit.figures.verdict_lines`'s text. Option: W2-88b's record is judged in W2-88b's suite (recommended).\n- **P-3 (the code graph): a named residual (DEC-1157 (3)).** The cases never run the real tool (no `_CBM_SUITES` entry): the code graph's nodes and\n  edges are asserted present only (`stores.codegraph.nodes`/`edges` are numbers, `codegraph_bytes` is reported, none compared), and the planted\n  adoptions have code intelligence off. **Where it goes:** W2-27's first full run on EXAMIN's copy (the real tool there); no case here.\n- **P-4 (F2 and S3's lock): decided in run 3 (P-4 (a), DEC-1157 (3)).** S3's lock reads \"never two at once\": the case holds the wait (a second\n  rebuild is serialised, not refused; `gov.rebuild.watch.take` blocks). F2's \"a file in neither list\" is the unit seam `fabric.check_coverage(record,\n",
      "tokens": 297
    },
    {
      "id": "bc3daa9e8297e0b0442512a6",
      "path": "tests/acceptance/W2-88/README.md",
      "text": "| success-14 (S14, the verdict set; I4, I7) | `test_w2_88_practice.py::test_s14_guard_the_declaration_is_written_before_the_used_marker`, `test_w2_88_practice.py::test_s14_f6_guard_a_planted_used_marker_makes_the_runner_refuse`, `test_w2_88_practice.py::test_s14_f6_guard_a_measured_role_is_refused_a_read_of_the_set_and_the_orchestrator_is_not` | none red: all **GUARD (green)**, the core and the existing guard (ACT-GUARD-SETS-1) carry the line; they hold it for the adopted repository's use (S20 forbids a second copy) |\n| success-15 (S15, the bar; I4) | `test_w2_88_practice.py::test_s15_guard_the_declared_bar_is_ceil_085_n_right_and_floor_005_n_wrong`, `test_w2_88_practice.py::test_s15_the_figures_printer_states_the_verdict_and_the_side_table` | **GUARD (green):** `declare`'s bar is ceil(0.85 n) / floor(0.05 n) (n = 40, 37) and `figures.verdict_lines` states the verdict and the side table; the result record `docs/research/W2-88-any-repository.md` is W2-88b's (no case: package P-2) |\n",
      "tokens": 249
    },
    {
      "id": "WAVE-1-WBS",
      "path": "docs/plan/WAVE_1_WBS.md",
      "text": "- **Roles and adoption:** full independent adoption and audit roles (CAP-47) with the A7, A10 and A11 gates and the final adoption verdict (CAP-44, DEC-090), and the remaining Wave 3 roles.\n- **Isolation and benchmarks:** multi-project isolation checks, and per-repository retrieval benchmarks.\n- **Exit:** every CAP in Contract v4 has at least one passing mechanism test and a mapped qualification scenario. Independent audit. Then qualification (CAP-49) and Release 1.\n",
      "tokens": 118
    },
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "  - the secret generated at test time from parts, found in history, reported without its value, behind a human gate;\n  - controls that must not be flagged;\n  - a fail-closed judge: FOUND_AND_HANDLED, MISSED or MISHANDLED per problem, and READY only when all are handled, no control is flagged and both question figures (hit@5 against 85, the stacked share against 99 %) meet their floors;\n  - one killed mutant per planted problem;\n  - one command for the real run, writing nothing in this repository;\n  - the self-tests hermetic, under 120 s, never skipped;\n  - **new (DEC-953, DEC-954; the plan's \u00a76):** a ticket in each synthetic repository closes with `gov close` at exit 0 on a pinned release (W2-16's numbered, frozen release, Q8c). Its real run is the orchestrator's.\n- **Also (DEC-954 Q9f):** its five repositories are W2-88's first proof of memory for any repository. W2-88 reads the builders and the per-repository question sets; it never changes them.\n- **Its held-out companion (the card below) is not yet filed.** It needs a ticket before W2-81's real run counts its question figures.\n- **KPIs, failure:**\n  - a miss judged handled;\n",
      "tokens": 287
    },
    {
      "id": "b3c4d307981bc189e8bba86c",
      "path": "docs/probes/DAEO-l78m/PR-DAEO-l78m.md",
      "text": "- **Cause:** the judge compares each repository's values only with its working tree and `<run>/outputs/<repository>/`. A folder that does not exist yields nothing.\n- **Should have happened:** MISHANDLED for that secret, naming the output by its folder. That needs every file a session can write in the run folder (at least the whole `outputs/` tree and the run folder's own files, outside the repositories' `.git`) to be compared with every held value, as `outputs/<repository>/` is now.\n- **Not the already-classified row:** that row covers the runner's own HOME and temp folder. This is the adopting session's own logs and reports, the channel KPI S4 names (\"no \u2026 log, \u2026 report or output\").\n- Ordinary work: yes, because a session adopting five repositories naturally writes a cross-repository summary in `outputs/`, or its per-repository log as `outputs/<repository>.log`. The README places logs in `outputs/<repository>/`, and nothing checks that they are there.\n- Consequence: fails open\n\n",
      "tokens": 249
    },
    {
      "id": "51867921d5d5d2a42e6b633c",
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md",
      "text": "| `allowed_paths` | add a module for the set tools (`src/gov/adopt/memory_sets.py`: pre-flight, USED, resume, figures) and its tests; and `docs/research/W2-88-memory-practice.md` | the fresh-80 scripts live in the CTO's scratch today; an adopted repository needs them in the product. The record's \u00a76 needs the refresh in \u00a75 |\n| `est_loc` 500, est. 20\u201326 lead-hours | about 750 LOC, about 30\u201338 lead-hours (\u00a74) | |\n\n**\"Memory works there\", re-worded:**\n```yaml\n  - 'Memory works there, measured: on each proof repository after A9, its questions are run end to end with the standard (S10, S15) and with W2-61''s measure, and right end to end, wrong claims and hit@5 are reported. W2-81''s per-repository sets apply to the synthetic repositories, and 10 questions written under the rubric apply to each real repository; these figures are data, set no bar, and a shortfall is a named residual with its cause (DEC-954 Q9e). On one real proof repository, chosen by the owner, the full practice runs (S12 to S14): its tuning set, then its verdict set used once and judged against S14''s bar [DEC-1098 (1), DEC-1097 (1)(d), DEC-833, DEC-860, CAP-10] [re-worded, DEC-1098 (1)]'\n```\n\n",
      "tokens": 294
    },
    {
      "id": "5d6b023598c10395c6489d6b",
      "path": "tests/acceptance/W1-16/README.md",
      "text": "  mistake in the test code. The stand-in is not part of the suite and was not committed.\n\n| KPI line | Test file | Test functions | Red reason today |\n|---|---|---|---|\n| **Success 1.** The index lives in a per-repository home under `.gov-runtime/`; `list_projects` in one repository shows only its own project [CAP-12.b] | `test_w1_16_home.py` | `test_the_wrapper_offers_its_public_interface` \u00b7 `test_the_home_is_under_the_repositorys_gov_runtime` \u00b7 `test_two_repositories_have_two_homes` \u00b7 `test_list_projects_in_one_repository_shows_only_its_own_project` \u00b7 `test_a_repository_answers_only_from_its_own_code` \u00b7 `test_indexing_again_keeps_one_project` | The wrapper does not exist |\n",
      "tokens": 171
    },
    {
      "id": "bef2649b4b0699e0adebe753",
      "path": "tests/acceptance/W1-16/test_w1_16_home.py",
      "text": "\"\"\"KPI success 1 and failure 2: a per-repository home under ``.gov-runtime/`` [CAP-12.b].\n\nTwo repositories in temporary directories are indexed through the wrapper. Each\nhas its own home under its own ``.gov-runtime/``; ``list_projects`` asked in\none shows that repository's project and nothing else, by the wrapper and by the\ntool itself; and no index file exists anywhere else after the run, the tool's\ndefault home included. No test indexes this repository (DEC-322).\n\"\"\"\n\nfrom __future__ import annotations\n\nimport json\nimport subprocess\nimport sys\nfrom pathlib import Path\n\nimport pytest\n\nimport w1_16_support as support\n\nALPHA = {\n    \"app/alpha.py\": \"def alpha_only_helper(value):\\n    return value + 1\\n\\n\\n\"\n                    \"def alpha_entry(value):\\n    return alpha_only_helper(value)\\n\",\n    \"README.md\": \"# Alpha\\n\\nA small repository.\\n\",\n}\nBETA = {\n    \"lib/beta.py\": \"def beta_only_helper(value):\\n    return value * 2\\n\\n\\n\"\n                   \"def beta_entry(value):\\n    return beta_only_helper(value)\\n\",\n    \"README.md\": \"# Beta\\n\\nAnother small repository.\\n\",\n}\n\n",
      "tokens": 273
    },
    {
      "id": "DEC-076",
      "path": "docs/DECISION_REGISTER.md",
      "text": "### DEC-076 \u2014 Wave 1 adjustments from S0b2\n- **Status:** ACCEPTED (owner, via Q-answers) \u00b7 **Basis:** SUGGESTION\n- G-02 (post-command `git status` containment against `allowed_paths`) moves from W2 to **W1**: it is the non-enumerative enforcement of MR-3.\n- codebase-memory in W1 must prove (a) a per-repository home isolates `list_projects`, and (b) the pre-index secret filter or an ignore mechanism keeps secrets out of its index.\n- S0b2's glue list and the stack plan's components are merged into one numbered W1 task list in S1 (the two G-numberings collide).\n- Superpowers' subagent-driven-development is excluded; the Gov OS's own orchestration and independent test-design skills replace it.\n\n",
      "tokens": 175
    },
    {
      "id": "DAEO-057v",
      "path": ".tickets/DAEO-057v.md",
      "text": "---\nid: DAEO-057v\nstatus: open\ndeps: [DAEO-g0ip, DAEO-49o5]\nlinks: []\ncreated: 2026-10-16T16:35:11Z\ntype: task\npriority: 4\nassignee: engineer\nexternal-ref: W2-18\ntags: [wave-2, implementation, standard, wave-3, deferred]\nwbs_id: W2-18\ntitle: 'Pinned install: a product repository runs a fixed release, never the development copy'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-g0ip\n- DAEO-49o5\nallowed_paths:\n- src/gov/install/**\n- src/gov/doctor/install*\n- template/governance/kernel/hooks/**\n- tests/unit/install/**\nkpis:\n  success:\n  - 'gov install <version> installs the CLI and kernel of a hash-verified release into a per-repository tool environment pinned to the release''s wheel hash, never an editable install. Verify: in a planted repository, `gov install <version>` exits 0; the tool environment''s record holds the release''s wheel hash and the hash check passed; the installed package metadata shows no editable install; a planted release with a wrong wheel hash is refused and installs nothing [CAP-43]'\n",
      "tokens": 264
    },
    {
      "id": "DAEO-057v",
      "path": ".tickets/DAEO-057v.md",
      "text": "# W2-18 Pinned install: a product repository runs a fixed release, never the development copy\n\n**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** The rest of K7 (DEC-941 item 3); W2-81 and EXAMIN install W2-16's release (DEC-954 Q8c).\n\nCard: `docs/plan/WAVE_2_WBS.md` \u00a72 (W2-18), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).\n\n- **Allowed paths:** `src/gov/install/**` (new), `src/gov/doctor/install*`, `template/governance/kernel/hooks/**` (the import fallback only), `tests/unit/install/**`.\n- **KPIs, success:**\n  - `gov install <version>` installs the CLI and kernel of a hash-verified release into a per-repository tool environment pinned to the release's wheel hash, never an editable install [CAP-43].\n  - `gov doctor` in a product repository fails when its `gov` is an editable install, resolves to another repository's `src/`, or differs from `framework.lock` [CAP-43, W2-H021].\n  - The guard and kernel hooks a session runs are the pinned release's code, not the session tree's [W2-M123].\n",
      "tokens": 292
    }
  ],
  "supplementary_query": "W2-88b W2-88's proofs on real repositories: two public GitHub repositories and the register's test repositories, on copies only\nThe proofs, recorded in experiments/W2-88/any-repository.md, each with its commit, size, the assessment, the plan's proposals (count and kinds), the per-store figures and the measure: Verify: experiments/W2-88/any-repository.md holds one section per proof, (b) and (c), and each names its commit, size, the assessment, the plan's proposals (count and kinds), the per-store figures and the measure; a grep for any of those fields missing from a section finds none\n  (b) two real, messy, public GitHub repositories of different languages and sizes. Candidates for the test designer or the owner to confirm, each pinned to a commit: a large polyglot monorepo with generated code and large fixtures (for example grafana/grafana, Go and TypeScript, of the order of 10^4 files), and a mid-size repository of another language with vendored dependencies in its tree (for example redis/redis, C, with deps/). They are cloned by the lead or the CTO (network) under ~/gov-os-runs/W2-88/github/<name>/, with their licence recorded, never committed and never pushed anywhere. They report data under \"Memory works there\" and neither runs the full practice: the practice's first full run (S12 to S14) is EXAMIN's copy at W2-27, with no separate proof repository; what goes wrong there is fixed in the practice, and the repositories adopted after EXAMIN follow the practice as fixed. Verify: the proof record has a section for each of two public repositories of different languages, each pinned to a commit with its licence recorded and its data under \"Memory works there\"; the clones are under ~/gov-os-runs/W2-88/github/<name>/ and a search of this repository's tracked files and history for the clones' paths finds nothing; the record states that neither runs the full practice (S12 to S14) [DEC-954 Q9f, DEC-1099 (2)] [changed, DEC-1099 (2)]\n  (c) the test repositories the register names, each read through a clone under ~/gov-os-runs/W2-88/: ~/workspace (DEC-078, DEC-718: 77,346 nodes and 270,647 edges, 2.2 GB peak, the envelope's top); the dev tiers ~/gov-os-workbench/synthetic/a-dev (ORION) and b-dev (ARGUS) (DEC-071, DEC-630); ARGUS's stress tier (DEC-071: 5,355 files, 57,777 chunks) only if it lies outside the held-out qualification material; the assessment step only, never an adoption, on a clone of EXAMIN's copy ~/gov-os-workbench/examin/ (DEC-723), to feed W2-27. Verify: the proof record has a section for each named test repository it used, each read through a clone under ~/gov-os-runs/W2-88/; the EXAMIN copy's section holds the assessment record only and no adoption record; a grep of the record for ARGUS's stress tier finds it only with its location outside the held-out qualification material stated [DEC-954 Q9f]\nScale: on each real proof repository ((b) and (c)) the stage records the query time of one plain question on each route, and the vector scan's time against the retrieve budget. A figure over the budget or over DEC-078's envelope is recorded with the measure, and returned as a proposal (a CIT-P or a ticket) for the owner, never a silent change of the store. Verify: on each proof repository the record holds the query time of one plain question on each route and the vector scan's time against the retrieve budget; a planted figure over the budget is recorded with the measure and a proposal file (a CIT-P or a ticket) is written for the owner, and the store's files are byte-identical before and after [DEC-954 Q9f, DEC-078, CAP-19]\nMemory works there, measured: on each real proof repository ((b) and (c)) after A9, its questions are run end to end with the standard (S10, S15) and with W2-61's measure, and right end to end, wrong claims and hit@5 are reported. W2-81's per-repository sets apply to the synthetic repositories, and 10 questions written under the rubric by the independent writer and checker (S12) apply to each real repository; these figures are data, set no bar, and a shortfall is a named residual with its cause (DEC-954 Q9e). No proof repository here runs the full practice (S12 to S14): its first full run is EXAMIN's copy at W2-27 (proof (d)), with no separate proof repository. Verify: on each proof repository after A9 the record holds the right-end-to-end, wrong-claim and hit@5 figures from the run with the standard (S10, S15) and W2-61's measure; each real repository has its 10 questions with the writer's and checker's records; a planted low figure does not make the stage not ok (no bar) and appears as a named residual with its cause; the record names no proof repository as having run S12 to S14 [DEC-1099 (2), DEC-1098 (1), DEC-1097 (1)(d), DEC-833, DEC-860, CAP-10] [changed, DEC-1099 (2)]\nA clone of a GitHub repository, or any of its files, in this repository or in a commit; a clone outside ~/gov-os-runs/W2-88/; a write in the workbench, EXAMIN's real repository or the held-out qualification material. Verify: `git ls-files` and the branch's history hold no path of a clone; each clone's folder is under ~/gov-os-runs/W2-88/; the modification times of the workbench, EXAMIN's real repository and the qualification material are unchanged after the run\nAnything written in ~/workspace or in any of the owner's own repositories: every proof works on copies only (clones under ~/gov-os-runs/W2-88/), never on the original Verify: the modification times and `git status` of ~/workspace and of each original the proofs read are unchanged after the run; every path the run wrote is under ~/gov-os-runs/W2-88/ or experiments/W2-88/ [DEC-1150 (1), DEC-723]",
  "further_batch": [
    {
      "id": "DAEO-l78m",
      "path": ".tickets/DAEO-l78m.md"
    },
    {
      "id": "DAEO-lkeb",
      "path": ".tickets/DAEO-lkeb.md"
    },
    {
      "id": "DAEO-xw3k",
      "path": ".tickets/DAEO-xw3k.md"
    },
    {
      "id": "DEC-077",
      "path": "docs/DECISION_REGISTER.md"
    },
    {
      "id": "DEC-079",
      "path": "docs/DECISION_REGISTER.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        },
        {
          "id": "7c99160bec6d01c496740381",
          "path": "governance/project/orchestration/packages/LIFT-1/GLOSSARY-1.md"
        },
        {
          "id": "35aa33fcb914963afa8544d2",
          "path": "governance/project/orchestration/packages/ROLES-SPEC-1.md"
        },
        {
          "id": "1635e0d13b9641267936680e",
          "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md"
        },
        {
          "id": "5e238b4671bff36b1c7afc8a",
          "path": "tests/acceptance/W2-88/README.md"
        },
        {
          "id": "bc3daa9e8297e0b0442512a6",
          "path": "tests/acceptance/W2-88/README.md"
        },
        {
          "id": "WAVE-1-WBS",
          "path": "docs/plan/WAVE_1_WBS.md"
        },
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        },
        {
          "id": "b3c4d307981bc189e8bba86c",
          "path": "docs/probes/DAEO-l78m/PR-DAEO-l78m.md"
        },
        {
          "id": "51867921d5d5d2a42e6b633c",
          "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "5d6b023598c10395c6489d6b",
          "path": "tests/acceptance/W1-16/README.md"
        },
        {
          "id": "bef2649b4b0699e0adebe753",
          "path": "tests/acceptance/W1-16/test_w1_16_home.py"
        },
        {
          "id": "DEC-076",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "DAEO-057v",
          "path": ".tickets/DAEO-057v.md"
        },
        {
          "id": "DAEO-057v",
          "path": ".tickets/DAEO-057v.md"
        },
        {
          "id": "DAEO-l78m",
          "path": ".tickets/DAEO-l78m.md"
        },
        {
          "id": "DAEO-lkeb",
          "path": ".tickets/DAEO-lkeb.md"
        },
        {
          "id": "DAEO-xw3k",
          "path": ".tickets/DAEO-xw3k.md"
        },
        {
          "id": "DEC-077",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "DEC-079",
          "path": "docs/DECISION_REGISTER.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "DAEO-l78m",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-lkeb",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-xw3k",
      "reason": "budget exceeded"
    },
    {
      "id": "DEC-077",
      "reason": "budget exceeded"
    },
    {
      "id": "DEC-079",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 19755,
  "budget": {
    "limit": 20000,
    "used": 19755
  },
  "hash": "6542267aef03e21f2b322cd08e6af7d44e224d75a77f57d706bcdc607a9000b5"
}
