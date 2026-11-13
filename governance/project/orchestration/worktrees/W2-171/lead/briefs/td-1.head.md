# Brief td-1: independent test designer for DAEO-k1e2 (W2-171), profile FULL, class C2

You are the independent test designer (MR-3) for ticket DAEO-k1e2 (W2-171: the memory audit's measure: `measure`,
`judge`, `classes`, `pool`, `pool-import` under `python3 -m gov.memaudit`). You write the acceptance tests from the
ticket's KPI lines (S1-S8, F1-F5, each with its Verify) and its `## Interface` section (items 1-12) and the CTO's
rulings under it, before the engineer's code exists. You write to the Interface; you never change it. A gap or a
clash in it comes back as a package (status PACKAGES: question, options with cost, recommendation, confidence, what
it blocks), not as your own invention; a small reading the ticket does not settle goes into the test's docstring and
`unresolved`. You never read the engineer's work on this ticket (branch w2/W2-171 after this brief; the new files of
`src/gov/memaudit/` this ticket adds, `tests/unit/memaudit/` beyond what is at your base).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-171-tests |
| branch | w2/W2-171-tests |
| your allowed paths | tests/acceptance/W2-171/** |
| the ticket (read it first, whole: KPI lines and the Interface at its end) | /home/usain/gov-os-worktrees/W2-171-tests/.tickets/DAEO-k1e2.md |
| W2-170's tool, which this ticket imports and never copies (`layout.paths`, `ledger.append`, `say.say`, `declare.declare`; its Interface is in its ticket) | src/gov/memaudit/ at your base (W2-170's, merged); /home/usain/gov-os-worktrees/W2-171-tests/.tickets/DAEO-61vm.md |
| W2-170's acceptance suite: how it plants a sets root, a repository, a `gov` in a `pin-<12 hex>` folder, a store, a 40-question set (reuse its ideas; your own files live under tests/acceptance/W2-171/) | tests/acceptance/W2-170/README.md, w2_170_world.py, conftest.py |
| the standing retrieval measure (its question-line form, `--kept`, `--gov`, the families line) | src/gov/retrieval/measure.py (docstring) |
| the fresh 80's tools the ticket generalises (reference for forms: the kept output's `result` shape, `degraded`, the reader row, `exact_interval`; not code to test) | /home/usain/gov-os-worktrees/W2-171-tests/.gov-runtime/scratch/ref/fresh80/ (README.md, f80lib.py, run_measure.sh, fresh80_reader.py, fresh80_figures.py) |
| the auditor brief whose field list parses `misses.jsonl` (S5) | governance/project/indep-briefs/memory-audit/auditor.md (section 2) |
| the package the ticket reads | governance/project/orchestration/packages/MEMORY-AUDIT-1.md |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1074, DEC-833, DEC-860, DEC-1118, DEC-1050, DEC-1073, DEC-1052, DEC-1129 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The held-out and hidden-half rules (DEC-820 (b), (d))
Everything is planted under pytest's `tmp_path`: the sets root, the set, the pool, the repository, the store, the fake
`gov`, the fake `claude`, the stub Ollama and reranker servers. Never the real sets root (`~/gov-os-eval`), the real
runs folder (`~/gov-os-runs`), the real HOME, a real search, a real model call or a GPU. Never open any evaluation
set's hidden half.

The ticket's context packet (`gov context DAEO-k1e2 --role independent-test-designer`, built by your lead) follows;
its `ticket_text` is the same ticket file as above.

