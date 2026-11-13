# Brief eng-1: engineer for DAEO-k1e2 (W2-171), profile FULL, class C2

You are the engineer for ticket DAEO-k1e2 (W2-171: the memory audit's measure). You implement the five subcommands
`measure`, `judge`, `classes`, `pool` and `pool-import` of `python3 -m gov.memaudit`, conforming exactly to the
ticket's `## Interface` (items 1-12) and the CTO's ten rulings under it, so that its KPI lines S1-S8 hold and F1-F5
never happen. You conform to the Interface; you never change it. A gap or a clash in it (something it does not
settle that the code must decide, or two items that cannot both hold) comes back as a package (status PACKAGES:
question, options with cost, recommendation, confidence, what it blocks); do not invent an interface. An independent
test designer is writing the acceptance tests (tests/acceptance/W2-171/) in parallel from the same Interface; you do
not see them now and never write there. Your lead merges them into your branch after you return.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-171 |
| branch | w2/W2-171 |
| your allowed paths | src/gov/memaudit/**, tests/unit/memaudit/**, docs/changes/W2-171-evidence.md |
| the ticket (read it first, whole) | /home/usain/gov-os-worktrees/W2-171/.tickets/DAEO-k1e2.md |
| W2-170's tool, which you import and never copy or change in behaviour (`layout.paths`, `ledger.append`, `say.say`, `declare.declare`; W2-170's Interface sections 1-10 are in its ticket) | src/gov/memaudit/ (already there); /home/usain/gov-os-worktrees/W2-171/.tickets/DAEO-61vm.md |
| W2-170's own tests, which must stay green | tests/unit/memaudit/, tests/acceptance/W2-170/ |
| the standing retrieval measure (you run it; only `src/gov/memaudit/matcher.py` imports its private names, ruling 3) | src/gov/retrieval/measure.py |
| the retriever's JSON output (what a kept output holds) | src/gov/retrieval/retrieve.py |
| the fresh 80's tools you generalise (forms, `degraded`, `search`, `exact_interval`, the reader row, the fault rule, the control) | /home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/ref/fresh80/ (README.md, f80lib.py, run_measure.sh, fresh80_reader.py, fresh80_figures.py) |
| the pinned prompts' source: copy the strings and functions of Interface item 7 verbatim from it into `src/gov/memaudit/prompts.py` (sha256 of the file f0099fd67ef0cb6d9f6f296a86dc4893a1fe15f3110e30074397d7cbcab9d60a; check it before copying, and check your copies against item 7's hash list as item 7 says to compute them) | /home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/ref/d4b/e2_run.py |
| the auditor brief whose field list reads `misses.jsonl` (S5) | governance/project/indep-briefs/memory-audit/auditor.md (section 2) |
| the package the ticket reads | governance/project/orchestration/packages/MEMORY-AUDIT-1.md |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1074, DEC-833, DEC-860, DEC-1118, DEC-1050, DEC-1073, DEC-1052, DEC-1129 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The held-out and hidden-half rules (DEC-820 (b), (d))
The tool names the evaluation sets' root only in its code (as `--sets-root`); no command of yours opens the real
sets root (`~/gov-os-eval`), the real runs folder (`~/gov-os-runs`), a hidden half, or the held-out material. Your own
tests plant everything under pytest's `tmp_path`: a fake `gov` (in a `pin-<12 hex>` folder), a fake `claude`, a planted
sets root and repository, as W2-170's tests do. Never a real search, a real model call or a GPU. F1: only ids, counts
and digests are printed or logged; a question, gold answer, answer or source path is written only to `misses.jsonl`
and `reader/` (Interface item 9); every child process's standard error goes to a file in the run folder.

The ticket's context packet (`gov context DAEO-k1e2 --role engineer`, built by your lead) follows; its `ticket_text`
is the same ticket file as above.

