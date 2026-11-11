# W2-88-STANDARD-1: Gov OS's memory standard as W2-88's lines (DEC-1098 (1))

For the owner. Drafted 2026-11-09 by a product-spec agent for the CTO (session `ad44f5fe`). **A draft:** no ticket,
skill or tracked file is edited. W2-88 (`DAEO-2bdu`) is open, so its lines may change, each marked with the decision
that made it (DEC-1088 (6)). Its own rule holds: a KPI change goes through its test designer. No question, label or
answer from a hidden or spent set is quoted here.

## 1. The standard, in one paragraph
Gov OS's memory standard is the configuration that the fresh 80 judged once. It has four parts: the
**Qwen3-Reranker-0.6B**, served by the machine's one shared reranker service; **the pool on** (the `pool:` block in
`governance/project/retrieval.yaml`); **today's 6,000-token bundle**, with its items widened to their sections; and
**agents searching again once** when the first bundle does not answer. On the fresh 80, used once on 2026-11-08 at
window 4's commit `c00d525f`, an agent reading its bundles was **right end to end on 78 of 79 (98.7 %; exact 95 %
interval 93.1 to 100), with 0 wrong claims**. That beats K9's bar (at least 68 right, at most 3 wrong claims) and
reaches the 95 % target (FRESH-80-RESULT). On the 138 tuning questions the same configuration gave **128 of 138
(92.8 %)** (E2). hit@5 was 84.8 % on the 80 and 76.8 % on the 138, which is why the bar judges what agents answer and
reports rank beside it (DEC-1097 (1)(d)). Under DEC-1098 (1) every adopted repository builds this standard at its
Wave 0, as W2-88's practice record describes, and proves it there: first on its own tuning set, then on a fresh
verdict set measured once.

## 2. The proposed KPI lines (W2-88 `kpis.success` and `kpis.failure`)
W2-88's lines have no numbers today. In §3 they are named by their first words. The new lines are numbered from S10,
so they cannot be confused with the old "was S5". Each is marked `[added, DEC-1098 (1)]`.

```yaml
  - 'S10 The standard pinned at Wave 0: A9 lite builds and serves the store with Gov OS''s memory standard: Qwen3-Reranker-0.6B through the machine''s one shared reranker service (no private reranker), the pool on (retrieval.yaml''s pool: block as Gov OS ships it), the 6,000-token bundle with its items widened to their sections, and the gov pin, the embedder, the reranker and the retrieval.yaml digest written in the A9 record. Any setting that differs from the standard is named in the record, and the stage is not ok unless the record cites the owner''s decision id for it. Verify: on a planted adoption the A9 record names the four settings and the pin; a planted retrieval.yaml with the pool off, a second reranker or another bundle budget is named, and the result is not ok without a decision id [DEC-1098 (1), DEC-1097 (1)(a), DEC-1097 (5), DEC-1046 (1)] [added, DEC-1098 (1)]'
  - 'S11 The store current after every merge: adoption installs the refresh that this repository runs (practice record §7): after each update of the repository''s integration branch the store is rebuilt by the pinned code, double-buffered, so a failed build leaves the last good store in service; a daily backstop runs; every bundle names the commit its store was built at. Verify: on a planted repository, a merge followed by a query returns the new commit within the time the proof measured for a seeded rebuild; a planted failing build keeps the old store and reports the failure [DEC-1098 (1), DEC-1072 (2)] [added, DEC-1098 (1)]'
  - 'S12 The repository''s own tuning set: about 80 questions, written blind under the rubric (docs/research/memory-measure-audit/RUBRIC.md, its version in force) by an independent writer, and cross-checked by an independent checker in at most two rounds. The checker lists every other place that states each answer. Both are sessions outside the retrieval work, opened by the owner''s operator. The writer never reads search results and never finds gold with the product''s search. The categories follow the fresh 80''s twelve (callers, code paraphrase, exact string, multi-file, decision, ticket, plan, contract or spec, kernel or template, history, failure memory, nonexistent id), mapped to the repository''s own domains. A category the repository has no domain for is dropped, and the drop is recorded. R5 applies: each domain at least 10 %, no subsystem over 25 %. There is at least one nonexistent-id question, scored apart. The set is split into two halves of 40: the first is used to choose fixes; the second is reported in counts only and never chooses. Source families (official copies) are declared in the path map. Verify: the set''s checks in the proof record (path missing 0, heading on no line 0, heading on more than one line 0, unresolved 0, quota PASS) [DEC-1098 (1), DEC-1070 (2)-(3), DEC-1074 (4), DEC-1069 (5), DEC-1076 (5), DEC-1078 (4), DEC-1071 (5), DEC-1010] [added, DEC-1098 (1)]'
  - 'S13 The fresh verdict set, used once: 80 questions, written by the same independent writer and checker under the same rubric, blind, before the first measure of the tuning set. None of its gold sources is a gold source of the tuning set. It is held outside every worktree in a folder of mode 700, declared in the path map''s evaluation_sets with every role but the orchestrator refused, and the guard refuses the measured roles a read of the set and of its run folder (as ACT-GUARD-SETS-1). It is used once, as FRESH-80-1 did. First a counts-only pre-flight: the set''s digest, how its anchors resolve at the measured commit, and whether each nonexistent id still exists nowhere. Then the checker''s staleness pass at that commit. Then a declaration, committed before any search, naming the configuration (S10), the commit, the denominator with nonexistent-id questions apart, the bar and how it rounds (S14), any data conditions as data only, and the fault rule (FRESH-80-1 §3.5). Then a control on the tuning set. A USED marker is written before the first search, and the runner refuses to start once it exists. The result record gives counts only. Verify: the declaration''s commit is earlier than the USED marker; a planted USED makes the runner refuse; a planted read of the set by a measured role is refused by the guard [DEC-1098 (1), DEC-1097 (1)(b), (1)(g), DEC-1097 (2), DEC-1092 (4), DEC-1078 (3), DEC-1074 (1)] [added, DEC-1098 (1)]'
  - 'S14 The bar: on the verdict set, judged on the declared configuration only. The figure is right end to end: the answer correct and its citation right, graded by a named grader model, with a second grader''s agreement reported. It must be at least 85 % with wrong claims at most 5 %; the target is 95 %. On n judged questions that is at least ceil(0.85 n) right and at most floor(0.05 n) wrong claims. Reported beside it, never judged: hit@5, gold in the first bundle, the answer correct with the citation set aside, the stricter grade, one search against two (exact McNemar), the exact 95 % interval, and the reader model by name. Verify: the result record in docs/research/W2-88-any-repository.md (or the adopted repository''s copy of it) holds the verdict line and the side table [DEC-1097 (1)(d), DEC-1098 (1), DEC-957, CAP-10, DEC-1079] [added, DEC-1098 (1)]'
  - 'S15 Search again once in the adopted repository: adoption copies, unchanged, the kernel''s retrieval skill with step 7 (W2-142 S1), the discovery skill''s line (W2-142 S2) and T-0''s and T-8''s "Search again once" line (W2-128''s line). Nothing is re-worded per repository. The verdict''s judged condition is up to two searches (A2). Verify: a string test on a planted adoption''s generated skill and T-0 for "search again once", "own, different words", "not found" and "two searches" [DEC-1098 (1), DEC-1094 (2), DEC-1092 (1)] [added, DEC-1098 (1)]'
  - 'S16 A miss is a result. A verdict below either limit stands as recorded. It is never run again, never re-scored to pass, and its labels are never changed after its figures exist. The spent set becomes a diagnostic set. An independent auditor classifies its misses by kind, counts only: never retrieved, ranked low, vocabulary, correct answer citing an unlisted place, other. The result goes to the repository''s owner with options: structural fixes judged on the tuning set and then a new fresh set used once, or the figure accepted as a named residual with its cause. The store stays in service. The four settings of S10 change only by Gov OS''s owner''s decision (a CIT-P), never at the adopted repository. Verify: the result record''s miss section on a planted miss (stand-in figures); the runner refuses a set marked USED [DEC-1098 (1), DEC-1074 (1)-(2), DEC-1071 (1), DEC-1083 (2), DEC-954 Q9e, DEC-1070 (14)] [added, DEC-1098 (1)]'
  - 'S17 The Wave 0 order in the adopt skill: A9''s step in template/governance/kernel/skills/adopt/SKILL.md states the practice in order and points to the practice record. The order: assess and plan; census the stated links and build the graph from them; build the store with the standard (S10) and its refresh (S11); have the verdict set and the tuning set written (S13, S12); measure the tuning set and fix only the structure, never a named question, until its halves agree within 5 points; declare and measure the verdict set once (S14); record every method and figure. Verify: a string test on the skill for the steps in that order, and the skills check [DEC-1098 (1), DEC-1072 (2), DEC-1071 (1)-(3), DEC-1074 (4), CAP-33] [added, DEC-1098 (1)]'
  failure:
  - 'A verdict set read by a measured role, measured twice, or used to choose anything; a declaration committed after the first search [added, DEC-1098 (1)]'
  - 'A store served with a setting other than the standard''s and no decision id in the A9 record [added, DEC-1098 (1)]'
  - 'A tuning or verdict question written with the product''s own search, or by a session in the retrieval work [added, DEC-1098 (1)]'
```

## 3. What these replace or amend in W2-88, line by line
| W2-88's line today | Change | Why |
|---|---|---|
| "The assessment …" | unchanged | the standard starts after it |
| "The refactoring plan …" | unchanged | |
| "The full index and the embeddings (A9 lite …)" | unchanged; S10 adds the pinned settings and S11 the refresh | the build stays as written; the standard says what it serves |
| "The structure …" | unchanged | |
| "Scale …" | unchanged | its query times feed §4's estimate |
| **"Memory works there, measured …"** | **re-worded** (text below), `[re-worded, DEC-1098 (1)]` | its bar is hit@5 against CAP-10's 85 with full evidence at 99 %, on 10 questions per real repository, written by the test designer. DEC-1097 (1)(d) replaced hit@5 as the judged figure, and DEC-1098 (1) asks for a tuning set and a fresh verdict set |
| "The proofs …" (a) to (d) | (b) amended: one of the two GitHub repositories, or `~/workspace`, runs the full practice (Q2 in §6) | 160 questions on every proof repository is out of proportion (§4) |
| "A store of another layout version …" | unchanged | |
| the four failure lines and the moved line | unchanged; three failure lines added (§2) | |
| `acceptance_tests.author`: "The 10 questions per real repository … are this designer''s too" | **amended:** the test designer writes the planted cases (S10, S11, S13, S15 to S17); the question sets belong to the independent writer and checker (S12, S13) | DEC-1098 (1): an independent writer and checker, blind |
| the body: "The KPIs are unchanged until the owner amends them"; "The 10 questions … follow the rubric" | replaced by a pointer to this package and DEC-1098 (1) | |
| `waits_on` / `needs` | add W2-142 and W2-128 (S15), W2-116 (S11's refresh), the no-private-reranker ticket (DEC-1097 (8), not yet filed) (S10) | the lines copy or call their work |
| `allowed_paths` | add a module for the set tools (`src/gov/adopt/memory_sets.py`: pre-flight, USED, resume, figures) and its tests; and `docs/research/W2-88-memory-practice.md` | the fresh-80 scripts live in the CTO's scratch today; an adopted repository needs them in the product. The record's §6 needs the refresh in §5 |
| `est_loc` 500, est. 20–26 lead-hours | about 750 LOC, about 30–38 lead-hours (§4) | |

**"Memory works there", re-worded:**
```yaml
  - 'Memory works there, measured: on each proof repository after A9, its questions are run end to end with the standard (S10, S15) and with W2-61''s measure, and right end to end, wrong claims and hit@5 are reported. W2-81''s per-repository sets apply to the synthetic repositories, and 10 questions written under the rubric apply to each real repository; these figures are data, set no bar, and a shortfall is a named residual with its cause (DEC-954 Q9e). On one real proof repository, chosen by the owner, the full practice runs (S12 to S14): its tuning set, then its verdict set used once and judged against S14''s bar [DEC-1098 (1), DEC-1097 (1)(d), DEC-833, DEC-860, CAP-10] [re-worded, DEC-1098 (1)]'
```

## 4. What an adopted repository must provide, and what it costs
**It must provide:**
- the machine's shared services: the embedder and the one 0.6B reranker on the GPU. One GPU job at a time, the
  backstop at 15.5 GB, each request bounded by count × longest text (practice record §5.4);
- an integration branch whose updates trigger S11's refresh;
- a sets root outside every worktree (mode 700), with the path map's `evaluation_sets` lines and the guard rule. The
  guard rule is an operator ACT, as ACT-GUARD-SETS-1 was;
- two writer and checker sessions opened by the owner's operator, with their own folders and settings, as
  ACT-MSET-3 and ACT-MSET-4 set up;
- the owner's decisions: the declaration's configuration and bar (S10 and S14 make both defaults); permission for the
  readers and graders to read the verdict set (DEC-1097 (1)(e)); and whether the checker's staleness pass runs.

**The cost, scaled from this repository's runs** (2,521 files; 19,113 of 69,464 chunks embedded):
| step | this repository (measured) | a repository of about 10^4 files (est.) |
|---|---|---|
| full embed | 7 to 45 min (W2-88's ticket) | about 0.5 to 3 h of GPU, scaled by embedded chunks (est., low confidence: Scale measures it) |
| refresh after a merge | 40 s seeded (E0's clone); about 20 min warm (P1-PLAN) | minutes seeded; up to about 1 h cold (est.) |
| writing and cross-checking 80 questions | about half a day elapsed in two rounds (DEC-1076 at about 13:40 to DEC-1078 the same evening); session tokens not recorded | the same per set, ×2 for tuning and verdict; a code-heavy repository may need longer to find gold (est.) |
| one measure of 80 | 19 min of GPU, no tokens (E0) | about 20 to 40 min (est.; about 1.3 s a search here) |
| one end-to-end reader run of 80 (A1–A3, two graders) | $12.46 (the fresh 80); $0.157 a question (E2) | about the same: the bundle is a fixed 6,000 tokens, whatever the repository's size |
| tuning: say 2 to 4 reader runs on the tuning set | — | about $25 to $50 |
| the verdict's tools, once in the product | 2 to 3 h of agent work (FRESH-80-1 item 19) | none per repository once built |
| pre-flight, staleness pass, control, judged run | about 1 to 2 h of the operator; about 45 min live | the same |
| GPU memory | sampled peak 8,404 MiB during the measure (E0); padded reranker bound about 4.6 GB | the same: per search, not per repository |

**In all, per adopted repository (est.):** about 2 to 3 days elapsed, mostly writing the two sets and tuning; about $40 to $65
of reader and grader tokens, plus the writer's and checker's sessions; a few GPU hours; and about 3 to 4 hours of the
owner's operator. Data conditions such as the five bundles or other rerankers are not part of the standard; on the
fresh 80 they cost $96.59 more. **For W2-88 itself:** about +250 LOC (the set tools, S10's check, the skill step), so
about 750 LOC; plus one full practice run on one proof repository (about 2 days elapsed, about $60). Est. 30 to 38
lead-hours, against 20 to 26.

## 5. Risks, and what stays open
- **The glossary (DEC-1097 (6), (b)):** not in the standard. Its redesign is retested on the 138 after the 80. If the
  retest helps, W2-88's glossary line (GLOSSARY-1 §5.3) comes back as its own package. It is **not** added here.
- **G1's fewer scored pairs (DEC-1097 (10)):** brought as an option after the lift. If adopted, ranking changes, so
  the standard changes by that decision: the 138 are re-measured (DEC-1097 (4)), S10's settings follow it, and every
  verdict names its pin. An adopted repository judged on the old pin keeps its verdict. Its next verdict needs a new
  fresh set.
- **The nonexistent-id stop (product row):** the product reads only the id forms it knows (lexical `ids_in`). On the
  fresh 80, `UNRESOLVED_IDS` could not fire on that question's form (FRESH-80-RESULT), and an adopted repository will
  have more forms the product does not read (JIRA keys, RFC numbers). Until the row is fixed, S12 and S14 score that
  question on the reader's "not found", apart from the bar, and record the stop as "not applicable". The row needs a
  ticket: id forms read from the path map. That is not W2-88's work.
- **One repository's evidence:** the standard was proven on Gov OS's own repository, which is heavy on records. A
  code-heavy repository may score lower. That is why each adoption gives its own verdict.
- **The reader:** the figure is `claude-opus-5-5` reading at effort high with no tools. Real agents also grep and read,
  so S14 names the reader. Strict grading understates: on the 138, 7 of the 10 misses were correct answers citing an
  unlisted place. On the 80, the one miss was a "not found".
- **The practice record lags the standard:** §6 step 3 says "answer units", but C1 and C2 were measured and not kept
  (record §4). §6 step 4 names three sets, while DEC-1098 (1) names a tuning set and a verdict set. S12 keeps a second
  half that only reports. The record needs a refresh to S17's order; its path is not in W2-88's `allowed_paths` today
  (§3).
- **Who writes the sets:** for each repository the owner's operator opens two sessions. That is the largest human cost,
  and it is a single point of delay.
- **The refresh hook in another repository** may meet that repository's own hooks (W2-23's adapters). S11's planted
  case covers the double buffer, not every hook manager.

## 6. For the owner
1. **The eight lines S10 to S17 and the three failure lines, as written?** *Recommended: yes* (high confidence on S10,
   S13, S14: each restates what was decided and run; medium on S11 and S17, which depend on W2-116's and the skill's
   shape).
2. **Where the full practice proves itself in W2-88:** (a) one real proof repository (the owner chooses: `~/workspace`,
   or one of the two GitHub repositories), with the others reporting data; (b) every real proof repository (about ×3
   the cost); (c) none in W2-88, with EXAMIN at W2-27 as the first full run. *Recommended: (a)* (medium confidence).
   EXAMIN's adoption at W2-27 then runs the practice as its Wave 0, which is a W2-27 line outside this package.
3. **The tuning set's shape (S12):** (a) 80 in two halves, the second only reporting; (b) one set of 80 that chooses.
   *Recommended: (a)* (medium confidence): it is a cheap early sign before the single shot, and it never chooses.
4. **The writers:** sessions outside the system opened by the owner's operator (recommended), or the ticket's
   independent test designer as the ticket says today?
5. **W2-88's scope:** add the set tools and the practice record to its `allowed_paths` (recommended), or file a new
   ticket for the set tools?
6. **The nonexistent-id row (§5):** file it as its own ticket now? *Recommended: yes*, before the first adoption.

**Basis (DEC-1052's five tests):** (1) memory: every adopted repository is judged by what its agents answer, on a set
used once; (2) without S13 and S16 a verdict could fail open (a set read, run twice, or used to choose); (3) the costly
steps run once per repository at Wave 0, and the refresh runs only on a merge; (4) no new approval beyond the
declaration and the guard ACT; (5) the standard is already proven in use here, on the 138 and the fresh 80.

**Sources read:** `.tickets/DAEO-2bdu.md` (W2-88), `DAEO-qskx.md` (W2-142), `DAEO-t8mp.md` (W2-128's line);
`docs/research/W2-88-memory-practice.md`; LIFT-1's FRESH-80-RESULT, FRESH-80-1, E0-RESULT, E2-RESULT, E3-RESULT,
SEARCH-AGAIN-PRACTICE, G1-PROFILE, GLOSSARY-1 §5.3; ACT-MSET-3; DEC-1052, DEC-1067, DEC-1069 to DEC-1078, DEC-1083,
DEC-1088 (6), DEC-1092, DEC-1094 to DEC-1098.
