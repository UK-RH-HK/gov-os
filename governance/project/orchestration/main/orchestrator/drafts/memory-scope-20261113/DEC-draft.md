# DEC-1176 draft (for the owner's yes; DEC-1175 is reserved)

Drafted 2026-11-13 by a helper of the CTO (DAEO-sdxk). Nothing is recorded or committed. The ticket edit is
`W2-88b.patch` beside this file (`git apply --check` passes from the repository root, and the front matter parses).
The adopt skill's reconciliation (the weekly re-measure on the same hidden questions) is a separate package:
`MEMORY-AUDIT.md` beside this file. It is not part of this decision.

---

### DEC-1176 — Memory for any repository is built, measured and maintained per repository in its own Wave 0, not proven by measuring other repositories; W2-88b becomes a smoke run of gov adopt on grafana and redis (no questions, no measure, no validation)
- **Status:** ACCEPTED-on-yes (PROPOSED until the owner's yes in the chat; then recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-13)`; item (1) standing) · **Under:** DEC-954 Q9f, DEC-1150 (1), DEC-1099 (2), DEC-1098 (1), DEC-1072 (2), DEC-957 (memory's target 95 %), DEC-974, DEC-728 · **Changes:** DEC-954 Q9f (its proof list), DEC-1150 (1) (W2-88b's content and its copies line), DEC-1099 (2) (as it adopted W2-88-STANDARD-1 §3: the 10 questions per real repository)
- **Decision:**
  - (1) **Standing: memory is proven per repository.** Each adopted repository's memory is built in that repository's own Wave 0 (refactoring, indexing, embeddings, stores), measured there on its own hidden questions to at least 95 %, and kept there by weekly maintenance and re-measuring. Memory for any repository (DEC-954 Q9f) is not proven by measuring other repositories. How the weekly re-measure works (the same hidden questions, against today's fresh set measured once) is decided separately, on `MEMORY-AUDIT.md`. Until then DEC-1101 (1), DEC-1125 (2), DEC-1098 (1) and the adopt skill's step 6 stand as written.
  - (2) **W2-88b (DAEO-aks1) re-scoped to a smoke run.** gov adopt runs on copies of grafana/grafana (large) and redis/redis (smaller) under `~/gov-os-runs/W2-88b/`, with the memory tools it runs: the assessment (MA), the index, the embeddings and the stores (A9 lite, run with no `--questions`). Its only purpose is to test whether gov adopt works on repositories different from this one, small and large, and where it fails.
    - **The record:** `experiments/W2-88/smoke-run.md`. Per repository and per stage (MA, A0 to A6, A8, A9) it names whether the stage completed, or where and how it failed: the command, its exit code, the refusal code, the error and the time.
    - **A failure is a finding:** it is recorded and returned to the owner. It never stops the other repository and is never fixed in W2-88b.
    - **Out:** no questions, no measure, no validation of the result's quality. No workbench clones (ORION, ARGUS, ARGUS's stress tier, EXAMIN's copy). No question sets for grafana, redis or `~/workspace`, and `~/workspace` is not read at all.
    - **The ticket edit:** the five old success lines and the two old failure lines are removed. They are listed word for word in the ticket's body as "Removed by DEC-1176 (2)". In their place go five success lines (S1 to S5) and three failure lines, each with its `Verify:` clause (`W2-88b.patch`).
  - (3) **A5 on a copy (the one open point, for the owner's choice).** gov adopt's chain stops at A5 without an independent auditor's committed verdict on the path map (`src/gov/adopt/stages.py:432-461`: `NO_VERDICT`; the verdict's commit must carry `Role: independent-auditor` alone, from a session that ran no stage). Without it, A6, A8 and A9 (the memory build) are never reached.
    - **(a) Recommended:** a fresh independent-auditor session gives A5's verdict on each copy. It is the product's own gate and judges the path map only, never memory. Cost: two short auditor sessions (about $3 each, MEMORY-AUDIT-1 §7's auditor figure) and about 30 minutes. This is the patch's S4.
    - **(b)** No verdict. A5 is recorded as the failure `NO_VERDICT`, and the memory build runs outside gov adopt, by `gov rebuild` on each copy. Cost: A6 to A9 untested through gov adopt; S4 is removed and S2's chain ends at A5.
    - **(c)** A verdict written by the lead, labelled "smoke run, not a review". Not offered: it would forge the auditor trailer the gate checks.
  - (4) **What does not change:**
    - W2-88 (closed) keeps its record. Its proof (a) on W2-81's five synthetic repositories stands. Its "Memory works there" line's clause on real repositories is spent with W2-88b's lines.
    - DEC-1099 (2)(c) stands: EXAMIN's copy at W2-27 is the practice's first full run, measured on its own sets.
    - DEC-957's MEMORY-SPEC-MAP gap "the large-repository measure" stays closed by W2-88's Scale line on proof (a). The smoke run's stage times on grafana are data beside it, not a measure.
- **Changes, sentence by sentence:**

  | Decision | Old (quoted) | New |
  |---|---|---|
  | DEC-954 Q9f | "…and set up the database structure; proven on W2-81's synthetic repositories, two real messy public GitHub repositories of different languages and sizes, and any test repository path named earlier in the register; EXAMIN's copy is its live trial." | "…and set up the database structure; the tools proven on W2-81's synthetic repositories (W2-88's proof (a)) and smoke-run on copies of two real public repositories of different sizes, grafana and redis (W2-88b: whether gov adopt completes, and where and how it fails; no questions, no measure, no validation); each repository's memory built, measured on its own hidden questions to at least 95 % and maintained in its own Wave 0, never proven by measuring other repositories (DEC-1176); EXAMIN's copy is its live trial and the practice's first full run (DEC-1099 (2))." |
  | DEC-1150 (1) | "W2-88b (DAEO-aks1, research: proofs (b) and (c), their scale and measure lines, the proof record in `experiments/W2-88/`, the clone failure line)" | "W2-88b (DAEO-aks1, research: the smoke run of gov adopt on copies of grafana and redis, its record `experiments/W2-88/smoke-run.md`, the clone failure line; proof (c), the scale line and the measure line removed by DEC-1176 (2))" |
  | DEC-1150 (1) | "**Proof (c) works on copies only:** nothing is written in ~/workspace or in any of the owner's own repositories (a failure line of W2-88b)." | "**The smoke run works on copies only,** under `~/gov-os-runs/W2-88b/`. `~/workspace`, the workbench and the owner's own repositories are neither cloned, read nor written (a failure line of W2-88b; DEC-1176 (2))." |
  | DEC-1099 (2), as it adopted W2-88-STANDARD-1 §3 (the re-worded "Memory works there" line, carried into W2-88b) | "W2-81's per-repository sets apply to the synthetic repositories, and 10 questions written under the rubric apply to each real repository; these figures are data, set no bar…" | "W2-81's per-repository sets apply to the synthetic repositories; no question set is written for a real repository outside its own Wave 0 (DEC-1176 (1)); these figures are data, set no bar…" |
  | DEC-1099 (2), as it adopted W2-88-STANDARD-1 §3, row "The proofs … (a) to (d)" | "(b) amended: one of the two GitHub repositories, or `~/workspace`, runs the full practice" (already overtaken by answer (2)(c)) | removed: no proof repository other than an adopted repository's own Wave 0 runs any part of the practice's measure |

- **Basis:** the owner's messages of 2026-11-13 (chat):
  - "W2-88b: I change its scope. Memory is built per repository in its own Wave 0 (refactoring, indexing, embeddings, stores), measured on its own hidden questions to at least 95 %, and kept there by weekly maintenance and re-measuring. It is not proven for 'any repository' by measuring other repositories. So: no workbench clones (P3) and no question sets for grafana, redis or ~/workspace (P4). Keep only a smoke run of the tools on grafana and redis: they index, embed and build their stores without failing, with no questions and no measure. ... bring the ticket edit (W2-88b's KPI lines, and DEC-954 Q9f's 'any repository' evidence) as one decision for my yes."
  - The follow-up on the smoke run: "its only purpose is to test whether gov adopt works on repositories different from ours, small and large, and where it fails. No measuring and no validation."
- **Where it goes (DEC-851):**
  - this register: DEC-954's, DEC-1150's and DEC-1099's status lines gain "Changed by: DEC-1176";
  - W2-88b's ticket, by `W2-88b.patch`;
  - MEMORY-SPEC-MAP's test-data row "W2-88's two real GitHub repositories: visible only, 10 each" (`packages/MEMORY-SPEC-MAP.md:180`), marked removed by DEC-1176;
  - the WBS and the plan's W2-88b row (title, scope, estimate);
  - the decisions-in-force list, RESUME HERE and the next version row ("Next free id: DEC-1177").
  - No new ticket (DEC-974).
