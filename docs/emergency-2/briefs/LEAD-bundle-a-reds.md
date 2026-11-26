# Lead brief: bundle-a-reds, batch A of the 0.1.8 bundle is red; find each red's cause, fix at the root, re-run the exact selection (fixes under W2-212 DAEO-d3sr and the owning tickets)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-26. **Read `docs/emergency-2/briefs/LEAD-COMMON.md`
first: every rule there applies.** Decide, never ask (I-10). Use `systematic-debugging`. The owner waits on this branch for
release 0.1.8 (EXAMIN's measure needs D3): work steadily, smallest correct fix.

## Why
Branch `e2/bundle-a` (worktree `/home/usain/gov-os-worktrees/E2-bundle-a`, head `2f0c5dcd9`) merges onto `w2/integrate` the five
held branches `e2/d1-verdict` (W2-210), `e2/escalation-slice` (W2-211), `e2/d3-stale-route` (W2-212, D3), `e2/usage-per-repo`
(W2-207 UR) and `e2/models-by-role` (W2-201/W2-208). Its exact impact selection (635 entries, `.gov-runtime/scratch/orchestrator/
log/landing-bundle-a/select.json`) ran on it: **143 failed, 175 errors, 13594 passed** (`.../landing-bundle-a/pytest.out`).
By folder: W2-210 103, W2-52 72, W2-88 53, W1-41 30, W2-23 21, W2-190 14, W2-128 7, W2-197 4, W2-192 3, tests/unit/dispatch 2,
W2-188 2, W1-35 2, W2-201 1, W2-184 1, W2-13 1, W1-19 1, W1-01 1.

**The CTO's diagnosis of the largest cause (verify it first):** about 300 of the reds are one refusal. D3 added at adoption stage A3
(`src/gov/adopt/stages.py`, the `STALE_CLASS` refusal, from `e2/d3-stale-route`) a rule: a namespace whose name or paths say
superseded, historical, legacy or archive must state `stale_class`. The planted adoptions of six suites state those classes already in
the form the map has always had (`"classes": {"harbour": "legacy", "archive": "historical"}`), and A3 now refuses them all
(`ADOPT_STALE_CLASS: the path map is not recorded: namespace harbour says legacy, archive ... and states no stale_class`). A real adopted
repository with a legacy namespace (EXAMIN, ASMO OS) would meet the same refusal on its next adoption or update.

## What
- **BA-1 (the root fix, under W2-212 DAEO-d3sr, a `Fix:` line):** D3 reads the class a map already states. A namespace classed
  `legacy`, `historical` or `superseded` by the map's existing classes counts as stating its stale class (archive is historical, as D3
  says), and D3 then applies its policy (not indexed, not embedded) or its notice, without refusing; A3 refuses only a namespace whose
  name or paths say stale and which no class of the map states. Write the failing case first (W2-212's folder is the test designer's:
  a planted map with `classes: {harbour: legacy}` and no `stale_class` passes A3 and keeps harbour out of the default bundle). Do not
  change the six suites' fixtures: they are the existing form, and the fix makes D3 accept it. If you find the classes mean something
  else than D3's stale classes, stop that line of work, say what they mean with file:line, and choose the narrowest correct rule.
- **BA-2 Classify every other red** by running its node ids on `w2/integrate` (the base; a worktree at its head) through the heavy slot:
  red on the base (not batch A's: list it, don't fix it); red only on `e2/bundle-a` (find the culprit branch and the cause, fix it at the
  root under its owning ticket, failing test first; a test under `tests/acceptance/` is the test designer's); passes alone but failed in
  the run (I-30/I-32/I-22 kind: list it, never re-run it a second time). Known to the CTO: the W2-128 `role-cto` cases follow the CTO's
  rewrite of `template/governance/kernel/templates/role-cto.md` (2.0.0, DEC-1253), on `w2/integrate` already: list them as base reds
  for the CTO; W1-35's two import errors are I-22.
- **BA-3 The diagnosis record (T-12, plan 1-6's form):** `docs/probes/bundle-a/1.md`, one line per red id the run printed:
  `<node id>  cause: <base | culprit <branch>: <cause> | flaky | env>`, grouped where one cause covers many.

## Where
Work on branch `e2/bundle-a` in its worktree (the CTO's batch branch; commit the fixes there, each with its owning ticket's `Task:`,
`Fix:` and `Role:`). Code area: the files each cause needs. Others work meanwhile in `src/gov/release/` (release-rule lead),
the timing tests (`tests/acceptance/serial-only.txt`, W2-112, W2-13, W1-19: timing-tests lead), and `e2/bundle-b` (W2-207 runtime,
eval-roots, kit-head; its lead branched from `2f0c5dcd9`): do not edit those. Never merge into `w2/integrate`.

## Green
BA-1 red then green; `gov accept W2-212` and `gov accept W2-210` green; then the **exact** batch A selection again, recomputed on your
head (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-d3d4=e2/d1-verdict DAEO-esl1=e2/escalation-slice
DAEO-d3sr=e2/d3-stale-route DAEO-rt4s=e2/usage-per-repo DAEO-k1us=e2/models-by-role --onto w2/integrate --select` gives the list for
the branches; since your fixes are on `e2/bundle-a`, select instead with `--select` for `DAEO-d3sr=e2/bundle-a` against `w2/integrate`
if that covers more, and say which you used), run exactly through the heavy slot. Every remaining red must be on the base or listed as
flaky in BA-3. Check the trailers (LEAD-COMMON).

## Return
Head of `e2/bundle-a`; BA-1's cause confirmed (file:line) and the fix; each other cause and its fix or class; the re-run's summary and
its list's count; `docs/probes/bundle-a/1.md`; your retrieves (count, queries, records used).

## Your memory bundle (DEC-1249 (1); profile: similar past failures and their root causes, for a red; uncut)
store: c1e81afd3e75 (/home/usain/Dynamic-Agentic-Engineering-OS), store behind HEAD, head ea858330f5f6, 44 stale path(s)
{
  "store": {
    "commit": "c1e81afd3e7560e7a8f769bb51de083b07d72158",
    "head": "ea858330f5f602aa0f4134244622d502ffdd82c9",
    "stale": [
      ".claude/agents/orchestrator.md",
      ".claude/templates/role-cto.md",
      ".rulesync/subagents/orchestrator.md",
      ".tickets/DAEO-d3sr.md",
      ".tickets/DAEO-esl1.md",
      ".tickets/DAEO-j9z6.md",
      ".tickets/DAEO-l2b2.md",
      ".tickets/DAEO-ma4q.md",
      "docs/DECISION_REGISTER.md",
      "docs/checkpoints/DAEO-sdxk/CP-DAEO-sdxk-3337.md",
      "docs/emergency-2/CTO-HANDOVER.md",
      "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "docs/emergency-2/briefs/LEAD-bundle-b.md",
      "docs/emergency-2/briefs/LEAD-memaudit-launch.md",
      "docs/emergency-2/briefs/LEAD-release-rule.md",
      "docs/emergency-2/briefs/LEAD-timing-tests.md",
      "docs/emergency-2/briefs/PRODUCT-CTO-HANDOVER-METHOD.md",
      "docs/emergency-2/integration/FINDINGS.md",
      "governance/project/orchestration/tools/start_cto.sh",
      "governance/project/test-map.yaml",
      "src/gov/_shipped/template/governance/kernel/templates/role-cto.md",
      "src/gov/close/select.py",
      "src/gov/memaudit/brief.py",
      "src/gov/memaudit/say.py",
      "src/gov/memaudit/writercheck.py",
      "src/gov/queue/command.py",
      "src/gov/queue/dry.py",
      "template/.rulesync/subagents/orchestrator.md",
      "template/governance/kernel/roles/orchestrator.md",
      "template/governance/kernel/templates/role-cto.md",
      "tests/acceptance/W2-115b/README.md",
      "tests/acceptance/W2-115b/test_w2_115b_sel.py",
      "tests/acceptance/W2-115b/test_w2_115b_unwritten_paths.py",
      "tests/acceptance/W2-115b/w2_115b_sel_support.py",
      "tests/acceptance/W2-204/README.md",
      "tests/acceptance/W2-204/test_w2_204_fm5_launch.py",
      "tests/acceptance/W2-204/test_w2_204_ml_launch.py",
      "tests/acceptance/W2-204/test_w2_204_s9_s10_brief_deliver.py",
      "tests/acceptance/W2-206/README.md",
      "tests/acceptance/W2-206/test_w2_206_sel4.py",
      "tests/unit/memaudit/test_launch_lines.py",
      "tests/unit/queue/test_queue_select_sel.py",
      "tests/unit/queue/test_queue_select_unwritten.py",
      "tests/unit/queue/test_queue_w2_206_flags.py"
    ],
    "root": "/home/usain/Dynamic-Agentic-Engineering-OS"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "3841688c37e6ce43d3debf6f",
      "sha256": "3dfaac07da2a4f43045296f0e3f3a834f337193f1a100da6c153fc36c7bb1614",
      "path": "docs/plan/wave-2/w2-81-proving-run/adopter-brief-0.1.4.md",
      "start_line": 82,
      "end_line": 130,
      "text": "## 5. The order\n\nFollow the adopt skill (`.claude/skills/adopt/`) for each stage's form; this list fixes the order and the forms earlier\nruns showed are needed.\n1. **A1 and A2**, each committed.\n2. **MA**, the assessment, right before A3: `gov adopt --lite --stage MA --out <outputs>/ma-a3`. Report its proposals\n   (proposals only; nothing is moved).\n3. **A3, the path map.** `governance/project/path-map.yaml` puts every tracked path in exactly one namespace and is\n   committed before A3 runs. **The memory rule:** your repository's own code, tests, documents and records are development\n   memory, `memory_class: governance`; `product` is only for product data that must stay out of memory (binaries, media,\n   generated data). Superseded and legacy documents stay governance, classed by their own namespaces. Before A3, count\n   your tracked text files outside every governance namespace (`git ls-files` and a read-only `python3 -c` over the path\n   map) and justify each in the A3 record. A3's `--map` proposal (in your outputs folder, never committed by hand) is a\n   top-level `artefacts` list, one entry per artefact: `{path, action, target, batch, kind, justification}`, `batch` a\n   positive integer, `kind` given for a RETIRE. Run A3 with `--session <your session id>`.\n4. **A4**, the batched plan.\n5. **A5**, the independent review of the path map: `tk start <the A5 review ticket>` and commit; `gov brief\n   independent-auditor <id>`, filling any `{...}` slot left and an empty \"Objective:\" from the ticket's KPI lines by hand\n   (record that as a finding); launch it; wait for it; then\n   `gov adopt --lite --stage A5 --verdict governance/project/audits/adoption-A5/verdict.md --json`. The auditor's session is\n   not yours: its `auditor_session` must differ from A3's `--session`.\n6. **A6**, the controlled migration of the reviewed plan; then **A7** (lite), a fresh auditor's verdict on the A7 review\n   ticket, given the same way, its front matter naming `stage: A7`, and its `checked` list one entry per record read, each\n   as `record: <path>` and `sha256: <its sha256 at HEAD>` (`--verdict governance/project/audits/adoption-A7/verdict.md`).\n7. **A8**, the legacy import and retirement; then **A9 lite** (the index and the embeddings) in the background with\n   `--out <outputs>/a9` and no `--questions`; then **A10** (lite), a fresh auditor's verdict on the A10 review ticket, the\n   same way (`stage: A10`, the same `checked` form). After A9, check your store: among your own tracked text files, list\n   any with `indexed = 0` in `lexical_file` (read-only `sqlite3`), and report each you did not intend.\n8. **The LITE ticket cycle.** The adoption ticket (profile LITE) lands by `gov queue`, which is run after you stop, not by\n   you: it merges the ticket's work branch, runs the ticket's acceptance folder and the selected tests, and closes the\n   ticket at the land (`governance/project/queue.yaml` names the integration branch and the work-branch form, the ticket's\n   id). Your part:\n   - an independent test designer writes the ticket's acceptance cases from its KPI lines under its\n     `acceptance_tests.path`: make its tests worktree (`gov launch independent-test-designer <the adoption ticket>\n     --tests-worktree`), `cd` there, and launch it from there (`gov launch` starts a worker in the folder it is run from),\n     with `gov brief independent-test-designer <the adoption ticket>`;\n   - the work branch `gov queue` reads is the form in `queue.yaml`: when the test designer's branch has another name,\n     point a branch of that name at its commits (`git branch <name> <its branch>`) and say so in the report;\n   - `gov accept <the adoption ticket>` (with `--root` the tests worktree when the tests are only there) and record its\n     answer; do not run `gov queue`, `gov close` or `gov queue --dry-run`.\n   Record each step; a refusal is a finding.\n9. **The lite verdict**, if the product gives a stage or command for it (the adopt skill says); otherwise report that none\n   exists.\n10. **A final `gov rebuild`**, so the store's commit equals HEAD after your last commit (check with `gov retrieve` on a\n    neutral word: it must not stop with `FACET_UNAVAILABLE`). Your last commit is before it; the tree is then clean.\n11. **Stop.** Write `<outputs>/reports/99-handoff.md`: each stage's exit code and commit, the findings, the store's commit\n    and HEAD, the work branch's name and tip, and `git status --porcelain` (it must be empty). Write \"ADOPTION STOPPED\" as\n    its last line. Do nothing more. If a finding stops you before step 10, do steps 10 and 11 as far as they can be done.\n\n",
      "chunk_id": "3841688c37e6ce43d3debf6f",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "EXP-W2-81-proving-run-0.1.4",
      "sha256": "b4e7157334ed5ff7542eab009bcc1ae5a13526f4a383c22dcbec75e60e63b6aa",
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "start_line": 251,
      "end_line": 253,
      "text": "4. **New (path map).** \"A3 refuses a path map in which a tracked path matches two namespaces, naming the path and both.\" Verify: the rust adopter's map (`audits/**` in two namespaces) is refused at A3.\n5. **New feature (verdict).** \"`gov adopt --lite --stage VERDICT` gives ADOPTED_HEALTHY, ADOPTED_WITH_ACCEPTED_EXCEPTIONS or NOT_ADOPTED_HEALTHY from the lite conditions of CAP-44.h, names itself lite and the conditions it does not check, and gives ADOPTED_WITH_ACCEPTED_EXCEPTIONS only for an exception named in an owner decision.\" Verify: a stand-in adoption with A7 unmet gives NOT_ADOPTED_HEALTHY; the same with an owner decision naming A7 gives the accepted-exceptions verdict.\n6. **New feature (stale route).** \"In an adopted repository a document in a namespace marked superseded, historical or legacy is absent from the default bundle, and a current document on the same topic is present.\" Verify: the python-app stand-in's `docs/design/lending.md` is absent from `gov retrieve`'s bundle for the lending question and `lending-v2.md` is present.\n",
      "chunk_id": "4c3aa5e0dcbbdb86507b20cf",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "1893f2a625ba528586f2c403",
      "sha256": "5bc1b721192e254e9ce10a69e233c132b0f9cd0f981868b6e8dcd198484537ab",
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "start_line": 138,
      "end_line": 140,
      "text": "| Memory-use log | code only (`memory_use/__init__.py:5-9`) | `memory_use/__init__.py:72-94` (from `retrieve/command.py:144`, `brief/command.py:61`) | never | `gov memory-use` | W15 | \u2014 |\n| **Adoption stage records** A0-A4, A6, A8, A9 | code only (`adopt/project.py:193-196`: `stands_on` = previous record's sha256) | `Run.finish`, one commit each (`adopt/stages.py:50-57`), `governance/adoption/<stage>-<title>.md` | **before next stage** H: `project.chain` (`project.py:175-190`: `STAGE_MISSING`, `CHAIN_BROKEN`) | A3 needs A1 (`stages.py:479`); A6 needs A0 and A4 (`:684-706`) | W1 | A2 classifies with doctor's grammar \u2192 \u00a73.4 |\n| **A3 target path map** | the proposal's `artefacts` (`stages.py:214-230`) | the caller's proposal, recorded by A3 | **before** H: proposal refusals (`stages.py:474-505`); A5/A6/A7 hold the hash (`lite_gates.py:157-171`) | A4 plan (`stages.py` `_plan`), A5 review | W1 | does not refuse a path in two namespaces (A4, DEC-1238 (1c)) \u2192 \u00a73.5 item 2 |\n",
      "chunk_id": "1893f2a625ba528586f2c403",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "ADOPT-A3",
      "sha256": "cde0052be72ceba7d7906f73d26af89fde6709381d956753cc89afe809fadcc8",
      "path": "governance/adoption/A3-target-path-map.md",
      "start_line": 3786,
      "end_line": 3788,
      "text": "# ADOPT-A3: target path map\n\nWritten by `gov adopt --lite --stage A3`.\n",
      "chunk_id": "f1722dec0e254a36ad0f1cd0",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-6oj6",
      "sha256": "e906acca0361a37b538ff484ef6b5c1ceeacd31ccaf1a1995732075e80e3e627",
      "path": ".tickets/DAEO-6oj6.md",
      "start_line": 32,
      "end_line": 34,
      "text": "  - line: \"S1 `gov adopt --lite --stage A3 --map <proposal>` refuses the proposal as a whole (`PROPOSAL_REFUSED`, as its other refusals) when an artefact's action is DELETE_FROM_ACTIVE_TREE and its repository-relative path appears in the text of another tracked file; the problem for that path carries the code `DELETE_REFERENCED` and names each referencing file; no A3 record is written [DEC-1197 (2)(ii)]\"\n    verify: \"tests/unit/adopt/test_w2_190_referenced.py: a fixture repository with docs/plans/0003-storage-migration.md and docs/plans/0007-storage-migration.md whose text says it supersedes plan 0003 (`docs/plans/0003-storage-migration.md`); a proposal deleting 0003 is refused with DELETE_REFERENCED naming 0007, and governance/adoption/ holds no A3 record\"\n  - line: \"S2 The same refusal, with the code `DELETE_SUPERSEDED`, for a file classed superseded: the target of a SUPERSEDES edge in the repository's record graph, or a file whose front matter status is superseded (any case) [DEC-1197 (2)(ii), CAP-08]\"\n",
      "chunk_id": "e915faacdc7d35c3853bdbe9",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "37b00652826484fd45bf23a7",
      "sha256": "015fc0625f691a2d02449db1021fa074fb6f46de55be65e12ddd442c99329eaf",
      "path": "docs/emergency-2/briefs/LEAD-d3-stale-route.md",
      "start_line": 11,
      "end_line": 16,
      "text": "- **SR-2 Still findable on purpose.** Such a document is still found when asked for by path or by an explicit flag (choose the flag; for example `gov retrieve --include-stale`), and the bundle says it is stale when it shows it.\n- **SR-3 Adoption sets it.** The adopt skill and the A3 form give such namespaces the declared class with `lexical_policy: not indexed` and `embedding_policy: not embedded`, and say so; A3 refuses a namespace named or described as superseded, historical, legacy or archive that lacks the class (a notice naming it is enough where the name alone is ambiguous: choose and say which).\n- **SR-4 Every adopted repository gets it.** `gov update` carries the route; in an adopted repository whose path map already has such namespaces without the class, `gov doctor` names each one with the line to add (a notice, never a failure), so EXAMIN and ASMO OS can mark theirs. Gov OS's own path map: say which of its namespaces would take the class (do not edit Gov OS's live map; the CTO does).\n\nKernel text you may change (the CTO approves it by naming it here): the adopt skill under `template/governance/kernel/skills/adopt/` and the A3 form's text.\n\n",
      "chunk_id": "37b00652826484fd45bf23a7",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "ba5be38512445a0ef082e9be",
      "sha256": "b0d4530ac2f91eab2a5a32cb4d2fc435976b9896d0fec736f6fd6d1ac99784db",
      "path": "governance/project/orchestration/packages/P-W2-81-VERDICT-1.md",
      "start_line": 39,
      "end_line": 54,
      "text": "  - If it is them, the cause is real and shared. The adopter chose deletion by its own judgement, and the product\n    accepted a delete of a superseded document that its successor still references.\n  - **Fix in the product:** A3 refuses DELETE_FROM_ACTIVE_TREE of a file that another tracked file references, or of\n    one classed superseded.\n- **legacy-docs: two controls FLAGGED.** A control is flagged when any of these holds (`w2_81_judge.py:716-744`):\n  - it is classed in a flagging class;\n  - it maps to no namespace;\n  - it is left out of the lexical index;\n  - it was changed in place, retired, or taken as a legacy document;\n  - a finding names it.\n\n  legacy-docs kept superseded and obsolete documents out of the embeddings through its path map, and its store is\n  stale. One of these likely touched the controls. Your operator can confirm by printing each flagged control's\n  evidence `said` lines; controls are not hidden variants, but check that first.\n  - **Fix:** the adopter's path map, or the product's classing, depending on that evidence.\n- **python-app-clean: stacked_share 85, below 99.** A retrieval figure, measured on the one current store. Its\n",
      "chunk_id": "ba5be38512445a0ef082e9be",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "0357168bdcbd97f5b208e29f",
      "sha256": "7e562edc42bf4458b4b86099ceda8f69f75806de00a8b683d8c4d0d7e1afb42a",
      "path": "docs/plan/wave-2/w2-81-proving-run/adopter-brief-rerun.md",
      "start_line": 128,
      "end_line": 138,
      "text": "   committing it) and not something to leave for A3.\n4. **The memory rule, before A3:** your repository's own code, tests, documents and records are development memory,\n   `memory_class: governance`; `product` is only for product data that must stay out of memory: binaries, media, and data\n   files that are generated or bulk (a text file is `product` only if you can say what generated it or why it is bulk\n   data; a hand-written table, a checklist or a note is a document, `governance`). Count your tracked text files outside\n   every governance namespace (`git ls-files` and a read-only `python3 -c` over the path map) and justify each in the A3\n   record.\n   [[PLACEHOLDER D3 (waits for the owner's decision on the stale-document route, and for it to be built): the sentence\n   for superseded, historical and legacy namespaces: whether the adopter gives them `lexical_policy: not indexed` and\n   `embedding_policy: not embedded` as the explicit treatment under test, or leaves them as the 0.1.4 run did (namespaces\n   of their own, `not embedded`, still found by the keyword route). Not written by the lead; the CTO fills it in.]]\n",
      "chunk_id": "0357168bdcbd97f5b208e29f",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "a7e7fe0494ade6a40d200df2",
      "sha256": "c3edf5593889e36eb371dd109331d8ab3a1046735a1db4ed80b040efd79f02fb",
      "path": "docs/plan/wave-2/w2-81-proving-run/adopter-brief-rerun.md",
      "start_line": 106,
      "end_line": 120,
      "text": "## 5. The order (changed)\n\nFollow the adopt skill (`.claude/skills/adopt/`) for each stage's form; this list fixes the order and the forms earlier\nruns showed are needed. **The order is A1, the path map, A2, AS, MA, A3.** Run each stage once, with the form below; a\nstage's second run leaves a second commit and is a finding, not a retry.\n\n1. **A1**, committed (the product commits it).\n2. **The path map**, before A2 (the 0.1.4 run wrote it after A2 in three repositories: A2 then classed 125 to 128 paths\n   `namespace: null`, six controls were flagged and two large files missed on that alone).\n   `governance/project/path-map.yaml` puts **every tracked path in exactly one namespace** and is committed before A2\n   runs.\n   - Check it yourself with a read-only `python3 -c` over `git ls-files` and the path map's globs: each tracked path\n     matches **one** namespace's `paths`, not none and not two (the product's classifier takes the first match and says\n     nothing of a second, so an overlap passes silently and fails later).\n   - The adoption's own records are the usual overlap: `governance/adoption/**` and\n",
      "chunk_id": "a7e7fe0494ade6a40d200df2",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-6oj6",
      "sha256": "49c9f34022d2b76688ba0f980fc411e89a5ac713566d5ef9c94d0d75c9ea9ef9",
      "path": ".tickets/DAEO-6oj6.md",
      "start_line": 1,
      "end_line": 32,
      "text": "---\nid: DAEO-6oj6\nwbs_id: W2-190\nexternal-ref: W2-190\ntitle: \"A3 refuses DELETE_FROM_ACTIVE_TREE of a file another tracked file references, or one classed superseded\"\ntype: task\nclass: implementation\nrole: engineer\nprofile: STANDARD\nstatus: closed\nstate_class: AUTHORITATIVE\npriority: 1\ncreated: 2026-11-16T05:39:29Z\ndeps: [DAEO-2bdu]\nlinks: []\ntags: [wave-2, adoption]\nallowed_paths:\n- src/gov/adopt/stages.py\n- tests/unit/adopt/test_w2_190*\nreads:\n- src/gov/adopt/**\n- src/gov/records/**\n- governance/project/orchestration/packages/P-W2-81-VERDICT-1.md\nneeds:\n- src/gov/adopt/stages.py\nwaits_on:\n- ref: DAEO-2bdu\n  reason: W2-88 holds src/gov/adopt/stages.py's A3 as merged; closed\nest_loc: 80\nkpis:\n  success:\n  - line: \"S1 `gov adopt --lite --stage A3 --map <proposal>` refuses the proposal as a whole (`PROPOSAL_REFUSED`, as its other refusals) when an artefact's action is DELETE_FROM_ACTIVE_TREE and its repository-relative path appears in the text of another tracked file; the problem for that path carries the code `DELETE_REFERENCED` and names each referencing file; no A3 record is written [DEC-1197 (2)(ii)]\"\n",
      "chunk_id": "cc474cdc44c31fadfb2c0f01",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "8aa3354b7a47a66f9a556c4b",
      "sha256": "595903b61cea94a77739a76c92dd726ce10f77ba07a08b8ba39be089f4d474cb",
      "path": "docs/plan/wave-1-exit/evidence/a-dev-history.txt",
      "start_line": 67,
      "end_line": 75,
      "text": "6de2223 | 2026-10-12T11:02:48+01:00 | Ticket ORION-ad02 started: adoption stage A5 | Task: ORION-ad02 | Role: orchestrator | Implements: \n8ce28d8 | 2026-10-12T11:02:19+01:00 | gov adopt --lite A4: batched plan | Task:  | Role:  | Implements: \n844b879 | 2026-10-12T11:02:15+01:00 | gov adopt --lite A3: target path map | Task:  | Role:  | Implements: \n62ad4d2 | 2026-10-12T11:02:14+01:00 | gov adopt --lite A2: classification | Task:  | Role:  | Implements: \nc7be732 | 2026-10-12T11:02:14+01:00 | gov adopt --lite A1: inventory | Task:  | Role:  | Implements: \n9b08f6f | 2026-10-12T10:59:07+01:00 | Adoption repair: record types and state classes, namespace fields | Task: ORION-ad01 | Role: product-spec | Implements: CAP-03, CAP-06, CAP-44\nc604650 | 2026-10-12T10:55:35+01:00 | Ticket ORION-ad01: second round, the legacy records without a type and the namespace fields | Task: ORION-ad01 | Role: orchestrator | Implements: \n92ca47e | 2026-10-12T10:53:39+01:00 | gov adopt --lite A2: classification | Task:  | Role:  | Implements: \nc5f3d80 | 2026-10-12T10:53:39+01:00 | gov adopt --lite A1: inventory | Task:  | Role:  | Implements: \n",
      "chunk_id": "8aa3354b7a47a66f9a556c4b",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "0c4bc78483ac88001375a51a",
      "sha256": "1976532b4d0f00e9913133ad4af062079935a271ee725a741cbcfd7b8239ec28",
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "start_line": 140,
      "end_line": 143,
      "text": "| **A3 target path map** | the proposal's `artefacts` (`stages.py:214-230`) | the caller's proposal, recorded by A3 | **before** H: proposal refusals (`stages.py:474-505`); A5/A6/A7 hold the hash (`lite_gates.py:157-171`) | A4 plan (`stages.py` `_plan`), A5 review | W1 | does not refuse a path in two namespaces (A4, DEC-1238 (1c)) \u2192 \u00a73.5 item 2 |\n| **Auditor's verdict files** (A5, A7, A10) | free front matter; `adoption-verdict.schema.json` registered (`check/schema.py:53`) but **no code writes that type** | an auditor, by hand (`--verdict <path>`, `adopt/command.py:34`) | **before** H: `stages.py:541-565`, `lite_gates.py:62-105` (`NO_VERDICT`, `VERDICT_NOT_PASS`, `VERDICT_OTHER_RECORD`, `VERDICT_NOT_INDEPENDENT`) | A5, A7, A10 | W1 | A5 uses another key set than A7/A10 (B16) \u2192 one schema, gates validate against it (fix, W1-41, ~20 lines) |\n| AS spec audit record | as stage records | `adopt/spec_audit.py:276` | **before A3** H: `spec_audit.gate` (`:310-314`) | A3 | W1 | \u2014 |\n| **Adoption verdict** (CAP-44.h) | on `e2/d1-verdict` only (`3acad31a9`, `3f2050653`), not merged | \u2014 | \u2014 | \u2014 | W1 | the merge (W2-210, 0.1.6 per DEC-1231) |\n",
      "chunk_id": "0c4bc78483ac88001375a51a",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-mpq2",
      "sha256": "353b319cda5d4e5f0ddb329f4559f7c5f7ab58957fbbf600781219c8fa37ce41",
      "path": ".tickets/DAEO-mpq2.md",
      "start_line": 35,
      "end_line": 50,
      "text": "- .claude/skills/adopt/SKILL.md\nreads:\n- template/governance/kernel/skills/adopt/SKILL.md\n- src/gov/adopt/**\n- docs/contract/CONTRACT_v4.md\n- governance/project/orchestration/packages/P-ADOPT-SPEC-AUDIT-1.md\nneeds:\n- src/gov/adopt/command.py\n- src/gov/adopt/stages.py\nwaits_on: []\nest_loc: 400\nkpis:\n  success:\n  - line: \"S1 gov adopt offers stage AS (the spec audit) after A2 and before A3: `gov adopt --lite --stage AS` reads A1's inventory and A2's classes and writes governance/adoption/AS-spec-audit.md; A3 refuses to run before AS is recorded [DEC-1200, P-ADOPT-SPEC-AUDIT-1]\"\n    verify: \"tests/unit/adopt/test_w2_192_stage.py: a fixture repository through A1 and A2; AS writes its record; A3 before AS is refused with a named code; command.STAGES lists AS between A2 and A3\"\n  - line: \"S2 The AS record lists every spec found (path, title, its stated wave or status), each built, partly built or not built with evidence (code paths, tests, commits), the tickets found done or not by wave, specs with no code, code with no spec (top-level code modules no spec names), and each gap as one question to the owner with a place for the answer [DEC-1200]\"\n",
      "chunk_id": "85790741a703e48472f6296a",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "0689ffc6439e6cafc2d8138d",
      "sha256": "ba56f714bab19bf2b01e3f9d52894ad6997f1b24703db7acb01e9a3f0287900b",
      "path": "docs/emergency-2/briefs/LEAD-d3-stale-route.md",
      "start_line": 15,
      "end_line": 18,
      "text": "Kernel text you may change (the CTO approves it by naming it here): the adopt skill under `template/governance/kernel/skills/adopt/` and the A3 form's text.\n\nCode area: `src/gov/retrieval/` (the namespace filter), `src/gov/adopt/` (A3 form and its check), `src/gov/doctor/` (the notice part only), the path-map schema under `template/governance/kernel/schemas/` (a property added to an existing schema). Stay out of `src/gov/rebuild*` beyond reading the policy (the Phase 0 lead changes the refresh), and out of `src/gov/memaudit/`, `src/gov/dispatch/`, `src/gov/resources/`, `src/gov/launch/`, `src/gov/decisions/`, `src/gov/usage/` (other leads).\n\n",
      "chunk_id": "0689ffc6439e6cafc2d8138d",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "EXP-W2-81-proving-run-0.1.4",
      "sha256": "505ec5556252ecbb83b3991c9f5c42216ba0395788eeff1fbbd2c0a3e3d3d8e1",
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "start_line": 73,
      "end_line": 80,
      "text": "### Class 4 evidence: A2 before the path map (R9, R10)\n\n- The brief's order is A1, A2 (each committed), then MA, then \"A3, the path map ... committed before A3 runs\" (`adopter-brief-0.1.4.md` \u00a75 steps 1-3). The kit's default path map holds only the kit's own trees, so A2 records `namespace: null` for every other tracked path.\n- Per repository, the A2 record's null count: python-app 0 of 409, typescript-monorepo 0 of 410, python-app-clean 0 of 403; **rust-workspace 128 of 410, legacy-docs 128 of 410, secret-history 125 of 407**. The first three adopters re-ran A2 after writing the path map (git order: A2, path map, A2 again); the last three did not (A2, path map, A3).\n- The six flagged controls are exactly the controls in those three repositories (\"is mapped to no namespace the path map holds\", `report.json` `controls[].evidence`), and the two MISSED large files are in one of them. With the path map in force the files classify correctly: legacy-docs' `historic/export_ledger.py` is `code`, `docs/specs/draft-rostering-record-format.md` is `specs`, both embedded.\n- Also left behind in those repositories: 125 to 128 PROPOSED `DP-ADOPT-*` decision packages asking \"what is this file\" for files the later path map holds (rust F-008).\n- What it changed: 8 of the 63 reasons. Nothing else.\n\n",
      "chunk_id": "13239ea66726264903950442",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "EXP-W2-81-proving-run-0.1.4",
      "sha256": "512e4a61aea14946407d3da72014070267e015a98d42325c7e0501c6eede06c0",
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "start_line": 128,
      "end_line": 129,
      "text": "| AS not in the order (\u00a75 step 1-3: A1, A2, MA, A3) | carried from the 0.1.1 brief; A3 refuses `ADOPT_STAGE_MISSING \"run AS first\"` (rust F-003); the adopters ran AS as the refusal and the adopt skill say | **Nothing judged.** AS is not read by the judge (T2) and handles no planted kind. Cost: one finding and a minute per repository |\n| A3 `artefacts` form (\u00a75 step 3: a batch for every entry, `kind` for a RETIRE) | 0.1.4 takes KEEP with no batch or target, and RETIRE without target for the kinds rule-file, memory-store, chat-database only (rust F-005) | **Nothing judged, one thing for memory.** All six A3 records are all-KEEP (409, 410, 410, 410, 407, 403 entries; 0 A6 batches; 0 A8 retirements), the safe handling for every kind (never moved, never deleted), so no planted problem went MISHANDLED. A correct form could not have retired a superseded plain document anyway: RETIRE is limited to three kinds, and A3 refuses to delete a referenced or superseded file (W2-190). The product has **no route** for taking a superseded document out of default memory except the path map's `lexical_policy` |\n",
      "chunk_id": "15883dee8ccea94eefff0c5a",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "4ab186a94ea8fd18bfbd4a53",
      "sha256": "e6aa0bb07df90c302944a9551d8b4ffd7cc2274381bf43b233c90d9de36d6a33",
      "path": "docs/contract/contract.yaml",
      "start_line": 2822,
      "end_line": 2835,
      "text": "      Auditor session and recorded as its own stage; A7 checks the A6 migration against the A3 path map and the A4 plan reviewed\n      at A5; A10 checks the A8 legacy memory extraction and retirement, the derived state rebuilt from git and the canary\n      of each index (CAP-55); the fresh auditor runs at A5, AS, A7 and A10 (DEC-1214 G6)'\n    source: Adoption Protocol v3.0 \u00a712, \u00a715; Distribution Protocol v1.2 \u00a710; DEC-722; DEC-1214 G6\n    wave: W2\n  - id: CAP-44.g\n    item: Remediation, finding states, human gates during adoption\n    source: Adoption Protocol v3.0 \u00a717\u2013\u00a719; EMERGENCY-2 \u00a78.4 (DEC-1211)\n    wave: W3\n  - id: CAP-44.h\n    item: 'Adoption verdict, lite: ADOPTED_HEALTHY / ADOPTED_WITH_ACCEPTED_EXCEPTIONS / NOT_ADOPTED_HEALTHY from a fresh Independent\n      Auditor against the lite conditions: A0\u2013A6 and A8 with their stage records and the A5 review, the native layout kept,\n      the lite A7 and A10 gates passed, the pinned, hash-verified release (gov doctor MATCH), gov doctor green (exit 0), gov\n      check with no RED family, and one ticket closed by gov close at exit 0 with the repository''s own test command; of the\n",
      "chunk_id": "4ab186a94ea8fd18bfbd4a53",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "1688e6cdb96989111cb1e5c5",
      "sha256": "f77beabc10b02c5ffc27c32246a362d739c05f67cf389b406ed725a3d0b4fe32",
      "path": "docs/emergency-2/briefs/LEAD-d3-stale-route.md",
      "start_line": 25,
      "end_line": 26,
      "text": "## Return\nBranch and head; SR-1 to SR-4 with tests and result; the selected suites' summary lines; the namespaces of Gov OS's and EXAMIN's path maps (read only) that would take the class; reds not yours; the C3-trial counts.\n",
      "chunk_id": "1688e6cdb96989111cb1e5c5",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "EXP-W2-81-proving-run-0.1.4",
      "sha256": "8c6e0df026b3d0fac6631130790649b2fbceeae437c10eddcfa73c14077d192e",
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "start_line": 60,
      "end_line": 61,
      "text": "| R2b | 6 | **4** (set-up) | With the real `HOME` the landing is still red in all six, on the ticket's own line F1: `outputs/*/dry-realhome/summary.txt` (python-app 16 passed 1 failed; legacy 15/1; secret 3/1; ts 2/1; clean 2/1; rust 2/4) and `accept.out` (`failure-1` failed, `success-1`, `success-2` passed). F1 is not a product KPI: the lead's own set-up wrote it (`tools/setup_0.1.4.py:125`: \"every commit touching governance/adoption/ carries Role: orchestrator\"). The product's stage commits are subject-only by design (`src/gov/adopt/project.py:128-146`, `commit()`; `governance/project/bootstrap.md` \u00a7\"The adoption's commits\": \"carry no trailers\"). Contract v5 does not require trailers on them (CAP-58.h: a commit with no `Role`/`Task` trailer is judged against the caller; CAP-63.a's trailer check did not fail them in the dry run). The same line sank release 0.1.1. | the run's set-up (lead); an owner option below |\n| R3 | 13 | **3** | `A2-content-class`: A2 classes by path-map namespace only (`src/gov/adopt/stages.py:181-188`, `a2()`). See the not-built table. | CAP-44.b / CAP-01.c, both W1; no W2 line |\n",
      "chunk_id": "a621370dbcd008c53db43e75",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "EXP-W2-81-proving-run-0.1.4",
      "sha256": "3fc74bd635459eeb3b0398644db45e59194b7864ecda06e95c5fc6c878e4b9ef",
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "start_line": 122,
      "end_line": 128,
      "text": "## Class 4: the adoption run's own gaps\n\nThe adopter brief (`adopter-brief-0.1.4.md`) left out stage AS and used an A3 form 0.1.4 refuses; three adopters ended with `artefacts: []`.\n\n| Gap | Source | What it changed in the planted problems |\n|---|---|---|\n| AS not in the order (\u00a75 step 1-3: A1, A2, MA, A3) | carried from the 0.1.1 brief; A3 refuses `ADOPT_STAGE_MISSING \"run AS first\"` (rust F-003); the adopters ran AS as the refusal and the adopt skill say | **Nothing judged.** AS is not read by the judge (T2) and handles no planted kind. Cost: one finding and a minute per repository |\n",
      "chunk_id": "ad6844f89ae4ee935058b236",
      "routes": [
        "semantic"
      ],
      "batch": 2
    }
  ],
  "batches": [
    {
      "size": 10
    },
    {
      "size": 10
    }
  ],
  "merge": {
    "candidates": 20,
    "duplicates": 13,
    "dropped": [],
    "reranked": true
  },
  "rerank": {
    "by": "service",
    "device": "cuda:0",
    "reason": null
  },
  "expansions": [
    {
      "chunk_id": "3841688c37e6ce43d3debf6f",
      "parent_id": "3e354da31fff79f37b68fb51",
      "path": "docs/plan/wave-2/w2-81-proving-run/adopter-brief-0.1.4.md",
      "start_line": 82,
      "end_line": 130
    },
    {
      "chunk_id": "13239ea66726264903950442",
      "parent_id": "d40c11a479d6543a6e8a1eed",
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "start_line": 73,
      "end_line": 80
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "path": ".tickets/DAEO-6oj6.md",
      "chunk_id": "a3f3ab3964187777d28daf16",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-d3-stale-route.md",
      "chunk_id": "4333cbf65c220627e8f5c8e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A3-target-path-map.md",
      "chunk_id": "7b15c7f5e3ad2043ac9ec541",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "039bc5163540c789d83cc017",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "5a678b760bb7f94a1513a9d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/skilleval/harness.py",
      "chunk_id": "61105b0e5989831ce1910943",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/spec_audit.py",
      "chunk_id": "c6a5bfc668d548e44950ffcc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/stages.py",
      "chunk_id": "b5ff169afa371fe604490cd2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/spec_audit.py",
      "chunk_id": "49f84b8ffa0292618418981b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-44.h.md",
      "chunk_id": "ae56a0205fc2ffeceba8cb2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-44.h.md",
      "chunk_id": "4bd9732574d171a31db6b61d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/spec_audit.py",
      "chunk_id": "82f4a21a2724a00cf000de98",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/discover/command.py",
      "chunk_id": "85782cbf44a1557a459f9872",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/skilleval/harness.py",
      "chunk_id": "d99a467de0185413cc2e8f60",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/discover/check.py",
      "chunk_id": "a8cf17cd48a463a5b77d0174",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/command.py",
      "chunk_id": "157908b69a01f6e4e9141c52",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-44.h.md",
      "chunk_id": "7794df99b3112e12c2bcfa42",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/ratchet.py",
      "chunk_id": "6898008ba0a81c4f5fb865fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/dispatch/relaunch.py",
      "chunk_id": "875ed7974cb7452c14ec8653",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/dispatch/relaunch.py",
      "chunk_id": "9385bb81169a0a6ca23f853f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-44.h.md",
      "chunk_id": "80a00dd31497a53193f60dc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A2-classification.md",
      "chunk_id": "66d24e6645bc44325b258e15",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/spec_audit.py",
      "chunk_id": "a1b48d89073eeb07242b1cd3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-44.h.md",
      "chunk_id": "72e197ea65aa38ba955db9b8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "139104139d1878bf9c86c669",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/spec_audit.py",
      "chunk_id": "c1a2d8ee45138def53c403b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/report.json",
      "chunk_id": "1b8d54fb2836bae395c5fa30",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/spec_audit.py",
      "chunk_id": "ce5ca9a5ccf964af8af2cdb5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/ratchet.py",
      "chunk_id": "ac024fb98b60a46624bd8a50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/EXIT-REPORT.md",
      "chunk_id": "02cb2bed84ab8a4dd3a4c240",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/command.py",
      "chunk_id": "eb55a1c16bed5e7d45d328d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/matcher.py",
      "chunk_id": "8dd5a2cd304188d7948fa27f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/report.json",
      "chunk_id": "912fa400d2ecc8cf026b4ad8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "61478f65372f9b895e0b7ff2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/matcher.py",
      "chunk_id": "7a491287b2e34e4eab9dbe0c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-d3-stale-route.md",
      "chunk_id": "2bce8d330ddd1134f7bba542",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/ratchet.py",
      "chunk_id": "18a85dd32193f5d18f9aaa93",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-d7-adopt-lands.md",
      "chunk_id": "ea61903026d7099c2587f3f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/command.py",
      "chunk_id": "ad781ffc977f710c76fab754",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "ff61af2f8c9fabff17ff44aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/command.py",
      "chunk_id": "7e590ed2d039dbda6aa6c0e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/spec_audit.py",
      "chunk_id": "6a185454bf8508364b25c323",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/dispatch/relaunch.py",
      "chunk_id": "b337a594c5e01f4c83098868",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-47.d.md",
      "chunk_id": "92604f540405f45e855209e0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/a-dev-history.txt",
      "chunk_id": "4b827c19a97114820b73f705",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/spec_audit.py",
      "chunk_id": "7bd6efb45e2945b9f00a9dd3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "58eed578d68bbc4db1a7752d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/msg/command.py",
      "chunk_id": "bf3533b35a962faa633fd9c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-47.d.md",
      "chunk_id": "8db5708e75a928101d2532ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-d7-adopt-lands.md",
      "chunk_id": "b64f14b64a436afc17fad36f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/skilleval/harness.py",
      "chunk_id": "8017aae0edc35f9a946eb552",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/README.md",
      "chunk_id": "c3d9ec62fda2374ce7e431f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/report.json",
      "chunk_id": "1bd6f8df1f7f683b8629df0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/util/runs.py",
      "chunk_id": "ff722406236f02d851d92eef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-192-CIT-P.md",
      "chunk_id": "c1069bef15b88660b6996bdb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/rebuild/watch.py",
      "chunk_id": "1bf6ca69965f6b3990724936",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/spec_audit.py",
      "chunk_id": "aad0e62198ae6c5112419b65",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/README.md",
      "chunk_id": "52aa5d104b5bee98f8c5f12b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/record.md",
      "chunk_id": "8e561b9e0af8c6e4b499230c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/measure.py",
      "chunk_id": "4d2fb6da9bedbb893fb3095d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "1990af697c1147526155bc0d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "8403395e0be99dc1c5d9ad4e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/dispatch/relaunch.py",
      "chunk_id": "3a5071639cd83706600f756f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/adoption/adoption-path-map-verdict.md",
      "chunk_id": "103c2f55b4ce384cb4b8a14d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/spec_audit.py",
      "chunk_id": "0159df0637976b2b885676be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-d7-adopt-lands.md",
      "chunk_id": "894e6fa884a8b53ee1d8d9fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/command.py",
      "chunk_id": "667bd7be9e20cf58e1866c10",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/w2_81_judge.py",
      "chunk_id": "c8f6a715df4ade7bcd25005f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-192-CIT-P.md",
      "chunk_id": "0d7a5d2420fce4f96ada4dd4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/judge.py",
      "chunk_id": "b4a97d4f1551e14fd9409e40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "51e9db91eb825349851483e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "d493921e95bb3fabfaea0cab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/judge.py",
      "chunk_id": "16de2933f6bbe3da2b963274",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/adopt-a-dev-A8.json",
      "chunk_id": "7196dc6d812d4f9d9e418087",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/matcher.py",
      "chunk_id": "371d108c2718a1d0cda29dce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A2-classification.md",
      "chunk_id": "d1e631bb44bbc57fbc82c6b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/command.py",
      "chunk_id": "94c612c92cd885aa2c0d0c16",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/README.md",
      "chunk_id": "2744b5ddfcfb144f2a58db1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/a-dev-history.txt",
      "chunk_id": "9124b7f63f3b587c1dd79b8f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "ab395a1af19931083ff89906",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-6oj6.md",
      "chunk_id": "ea02663ef10367c35ea8ed4f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/judge.py",
      "chunk_id": "2471b4f2beac2ad024ef2547",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/stages.py",
      "chunk_id": "453b6004eaab6a1d9671d92a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/measure.py",
      "chunk_id": "cd67a86cbfcb1d5af929137d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A2-classification.md",
      "chunk_id": "30e32ba9f15a5ae622fcc898",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/command.py",
      "chunk_id": "abb61b9b1342401fba902793",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/README.md",
      "chunk_id": "252761b26f8fb60eac376379",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/report.json",
      "chunk_id": "350d6c945b797627c733b995",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/spec_audit.py",
      "chunk_id": "569649dd2b319387331b09ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-81-VERDICT-1.md",
      "chunk_id": "fc459d652927b1a2df049f7b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/command.py",
      "chunk_id": "dbe12465ae1c4271188ef9be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/README.md",
      "chunk_id": "349c80f46de7315eeecafb9f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-d7-adopt-lands.md",
      "chunk_id": "2b69cadd21f3888473c6ca4c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/spec_audit.py",
      "chunk_id": "01b7366b247de8991599dbf6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-d3-stale-route.md",
      "chunk_id": "f9be0c32aa6468d3a57653da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l78m.md",
      "chunk_id": "5ded2bfb0c9ebd4f099945cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "b438b45f4bb2dd0948f1282f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/report.json",
      "chunk_id": "d8e80516f8e46bbbf8bf37ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "6a0bfd5baa162d6d048b56e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/judge.py",
      "chunk_id": "cf81848d87d1245407996efd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "5035ffde31898b76d7736daf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/command.py",
      "chunk_id": "6aa9afc8232327d742178df7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/README.md",
      "chunk_id": "881cc1c5444cfaa28f7a9355",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/adopt-a-dev-A6.json",
      "chunk_id": "f0599d6f5ab41596a31e6886",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "39d58bfe7c68555ecb03a5f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/adopter-brief-rerun.md",
      "chunk_id": "ebd4c5f150e26cd6875aa9d6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/skilleval/harness.py",
      "chunk_id": "8a91c36bc0be4900624b5ca9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/README.md",
      "chunk_id": "c8d7c74410cd44509c7b4e8b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "b7763a3232a979a4d54eacfc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/judge.py",
      "chunk_id": "3ec932527e8ca3f6d041f32b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-mpq2.md",
      "chunk_id": "5bbde5280b456d4ba5579e44",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/command.py",
      "chunk_id": "166206a8f7e5a0b37d65b9ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "e34e139bc3639ea95c8dd938",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/project.py",
      "chunk_id": "151d98c5c58770c9535c693c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "c48fb00f4219bad12b91327a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/secrets/__init__.py",
      "chunk_id": "7c639a351bb48eabc526a32e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/README.md",
      "chunk_id": "866b52f2bbc49ed364436b17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/report.md",
      "chunk_id": "a30d992648de37a666c86c5e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/stages.py",
      "chunk_id": "c568eba8ad45f1decbe68521",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/dispatch/inbox.py",
      "chunk_id": "237730da258cae45ca30ce0e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-d3d4.md",
      "chunk_id": "6f30df76c900196743b1707b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/dispatch/inbox.py",
      "chunk_id": "1ca1fff6a60064919b0997aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-d7-adopt-lands.md",
      "chunk_id": "28cb67acaff9e3c3a7777168",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/command.py",
      "chunk_id": "78776818661b15bee5c7622c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/matcher.py",
      "chunk_id": "6b5e4d9583f82138c37338ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l78m.md",
      "chunk_id": "48d63d0ad4785fcb8e36a4a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/discover/check.py",
      "chunk_id": "885d5b5dd7a972cc389af3ff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "283ba10ee40f9a5f8aabcba3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/judge.py",
      "chunk_id": "38288318c2e8e68997116fad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/adoption/adoption-path-map-verdict.md",
      "chunk_id": "53f226e22e629498e51b8dfc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/util/runs.py",
      "chunk_id": "3e9ce08fd02b29d1b712a9a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/secrets/__init__.py",
      "chunk_id": "2b608d70ece6d1c858483c96",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/a-dev-history.txt",
      "chunk_id": "5bf7c7e8257b2630f112d41b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/spec_audit.py",
      "chunk_id": "fcb6637fdf39aee174c3b2e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-mpq2.md",
      "chunk_id": "4d8f433ccacd5273d807944f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "f3362c8d0f216a62944f0db9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "cf20e662ce174998d256f454",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "cb39fabcee0f7d23df5e54c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/README.md",
      "chunk_id": "c32e9e646dc7178ff19af99e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "c7ed4c48ed86f6e91e5bbbb6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "e7e6c982188ef86a43f92cb6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "68d8e648711cac1e66dd8642",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/command.py",
      "chunk_id": "7c8448f83135b31096b7a318",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "f5f5db6ded06a2f52d452314",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/prompts.py",
      "chunk_id": "5e0777822257f801898374c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/record.md",
      "chunk_id": "4e87ae593baeb0b2642b57fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "a6319e47b1c101163f2195cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/brief/build.py",
      "chunk_id": "1154bc12e71d94daa2e9e459",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "adf0c642a6584d8abd1db11b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "ed0dcef6a842c281422419e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/discover/check.py",
      "chunk_id": "68b3d9c7a331be9b2d6af8e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "162b4ad4faa1c918d1d9e53b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "55d73c65864bf72120d55141",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A8-legacy-import-and-retirement.md",
      "chunk_id": "1ffa3be6d445fb7b1f3efec8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/util/runs_root.py",
      "chunk_id": "470b264b95018ff8ebbe9f84",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-192/README.md",
      "chunk_id": "2cfa2af2208ddccfe80b33cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kmcr.md",
      "chunk_id": "1672dad07780c74b8e1e97cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/prompts.py",
      "chunk_id": "cb0c44413a2a333d0d8ad4c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/stages.py",
      "chunk_id": "e203d131bbb272d192f02577",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/command.py",
      "chunk_id": "a45292ed4e531576e9114ddd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/README.md",
      "chunk_id": "81d71da8e16d8d8f50015b5f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "05d7e07435c9102b984c7ce4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/EXIT-REPORT.md",
      "chunk_id": "1973a3bee1fb3b68f2d9dbd6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/command.py",
      "chunk_id": "b2447408faa8b2c32cb38906",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/discover/check.py",
      "chunk_id": "8b7b82bf219ea3c3b0e3c7ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-190/README.md",
      "chunk_id": "a6276d63da0e04cb37d20767",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/state.py",
      "chunk_id": "323d80069bc6157dd3643dba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/command.py",
      "chunk_id": "d0c53eb20b620b7a7c4f608a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/README.md",
      "chunk_id": "658af8f7015bc4481edaa7ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "5cf09fc94e8bdfc056c44a75",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "69d91cbcccebbd4073062bd3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "43c9ac4708e9b62a8c0d0968",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/spec_audit.py",
      "chunk_id": "94b3a53da381b96bab929c06",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/skilleval/harness.py",
      "chunk_id": "4b52b31d215f0a8d3324f32b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/w2_81_judge.py",
      "chunk_id": "9ea18371ca89c1ed5c493081",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/secrets/__init__.py",
      "chunk_id": "27202a479a57c54a5a770b92",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "4d68aa2ffb4555970d4ff8e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/secrets/__init__.py",
      "chunk_id": "d04742b17ad3736c973c3cb5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/adopt/test_adopt.py",
      "chunk_id": "2d5fac48033ad313566b7e89",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "3ffe2b35333b186f0384eb44",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "96d42720527130a92d4cabfb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/adopt/test_adopt.py",
      "chunk_id": "03a6b1e6fabc437da02a18c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "ef89c80fe218b716458d4fe4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/skilleval/harness.py",
      "chunk_id": "929ba9ccd40467e6293042d3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/project.py",
      "chunk_id": "1d57be57d602cad1c9dc7ef9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "0a5f2b0c7d67dab65765615e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/adopt/test_w2_190_delete_checks.py",
      "chunk_id": "68290971c6ce7e1deff9243c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/w2_81_judge.py",
      "chunk_id": "c8eeeae9dfdc3a57bb8d63c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/README.md",
      "chunk_id": "d1ce7bf04c3df4808db9e6e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/README.md",
      "chunk_id": "810775ad4f449cf452728c78",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/README.md",
      "chunk_id": "eb14643c94504ff8f218d600",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/adopt/test_w2_190_delete_checks.py",
      "chunk_id": "287bfc85d6b941121b12a9fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/README.md",
      "chunk_id": "9c2d5f46311c177c7450c566",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-192/README.md",
      "chunk_id": "8de705d7ec3ce2c807aca902",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-190/README.md",
      "chunk_id": "82eca7366eceeaf3dc26e844",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/adopt/test_adopt.py",
      "chunk_id": "73789030b59ec1bb2f9201b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/test_w1_41_embedding_policy.py",
      "chunk_id": "6502fd56557cd6a5d79d5096",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-192/README.md",
      "chunk_id": "aea2d72d47bd9b4b8ecd697d",
      "reason": "NOT_GATHERED"
    }
  ],
  "facets": {
    "lexical": {
      "available": true,
      "reason": null
    },
    "semantic": {
      "available": true,
      "reason": null
    },
    "code": {
      "available": true,
      "reason": null
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5773
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLTZvajYubWQiLDEsMzIsImNjNDc0Y2RjNDRjMzFmYWRmYjJjMGYwMSJdLFsiLnRpY2tldHMvREFFTy02b2o2Lm1kIiwzMiwzNCwiZTkxNWZhYWNkYzdkMzVjMzg1M2JkYmU5Il0sWyIudGlja2V0cy9EQUVPLW1wcTIubWQiLDM1LDUwLCI4NTc5MDc0MWE3MDNlNDg0NzJmNjI5NmEiXSxbImRvY3MvY29udHJhY3QvY29udHJhY3QueWFtbCIsMjgyMiwyODM1LCI0YWIxODZhOTRlYThmZDE4YmZiZDRhNTMiXSxbImRvY3MvZW1lcmdlbmN5LTIvVzItODEtUFJPVklORy1SVU4tMC4xLjQtQU5BTFlTSVMubWQiLDYwLDYxLCJhNjIxMzcwZGJjZDAwOGM1M2RiNDNlNzUiXSxbImRvY3MvZW1lcmdlbmN5LTIvVzItODEtUFJPVklORy1SVU4tMC4xLjQtQU5BTFlTSVMubWQiLDEyMiwxMjgsImFkNjg0NGY4OWFlNGVlOTM1MDU4YjIzNiJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9XMi04MS1QUk9WSU5HLVJVTi0wLjEuNC1BTkFMWVNJUy5tZCIsMTI4LDEyOSwiMTU4ODNkZWU4Y2NlYTk0ZWVmZmYwYzVhIl0sWyJkb2NzL2VtZXJnZW5jeS0yL1cyLTgxLVBST1ZJTkctUlVOLTAuMS40LUFOQUxZU0lTLm1kIiwyNTEsMjUzLCI0YzNhYTVlMGRjYmJkYjg2NTA3YjIwY2YiXSxbImRvY3MvZW1lcmdlbmN5LTIvYnJpZWZzL0xFQUQtZDMtc3RhbGUtcm91dGUubWQiLDExLDE2LCIzN2IwMDY1MjgyNjQ4NGZkNDViZjIzYTciXSxbImRvY3MvZW1lcmdlbmN5LTIvYnJpZWZzL0xFQUQtZDMtc3RhbGUtcm91dGUubWQiLDE1LDE4LCIwNjg5ZmZjNjQzOWU2Y2FmYzJkODEzOGQiXSxbImRvY3MvZW1lcmdlbmN5LTIvYnJpZWZzL0xFQUQtZDMtc3RhbGUtcm91dGUubWQiLDI1LDI2LCIxNjg4ZTZjZGI5Njk4OTExMWNiMWU1YzUiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vUkVDT1JEUy1NQVAubWQiLDEzOCwxNDAsIjE4OTNmMmE2MjViYTUyODU4NmYyYzQwMyJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9SRUNPUkRTLU1BUC5tZCIsMTQwLDE0MywiMGM0YmM3ODQ4M2FjODgwMDEzNzVhNTFhIl0sWyJkb2NzL3BsYW4vd2F2ZS0xLWV4aXQvZXZpZGVuY2UvYS1kZXYtaGlzdG9yeS50eHQiLDY3LDc1LCI4YWEzMzU0YjdhNDdhNjZmOWE1NTZjNGIiXSxbImRvY3MvcGxhbi93YXZlLTIvdzItODEtcHJvdmluZy1ydW4vYWRvcHRlci1icmllZi1yZXJ1bi5tZCIsMTA2LDEyMCwiYTdlN2ZlMDQ5NGFkZTZhNDBkMjAwZGYyIl0sWyJkb2NzL3BsYW4vd2F2ZS0yL3cyLTgxLXByb3ZpbmctcnVuL2Fkb3B0ZXItYnJpZWYtcmVydW4ubWQiLDEyOCwxMzgsIjAzNTcxNjhiZGNiZDk3ZjViMjA4ZTI5ZiJdLFsiZ292ZXJuYW5jZS9hZG9wdGlvbi9BMy10YXJnZXQtcGF0aC1tYXAubWQiLDM3ODYsMzc4OCwiZjE3MjJkZWMwZTI1NGEzNmFkMGYxY2QwIl0sWyJnb3Zlcm5hbmNlL3Byb2plY3Qvb3JjaGVzdHJhdGlvbi9wYWNrYWdlcy9QLVcyLTgxLVZFUkRJQ1QtMS5tZCIsMzksNTQsImJhNWJlMzg1MTI0NDVhMGVmMDgyZTliZSJdXSwiZiI6Ii9ob21lL3VzYWluL0R5bmFtaWMtQWdlbnRpYy1FbmdpbmVlcmluZy1PUyIsImkiOltdLCJvIjoyMCwicCI6eyJiIjoic2VydmljZSIsImQiOiJjdWRhOjAiLCJoIjoiMTQ2YmVmMTBjODhiMTUxNyIsIm8iOls5LDAsMTAsNywyLDEsMTEsMzQsNSwyOSwyMiwxNSwzOCw0LDMsMTYsMzMsNiwyNywxMiw4LDI0LDI1LDE4LDIwLDEzLDE3LDI4LDE0LDM3LDM2LDMwLDM5LDMxLDIzLDI2LDMyLDIxLDE5LDM1XX0sInEiOiJhZG9wdGlvbiBzdGFnZSBBMyByZWZ1c2FscyBhbmQgdGhlIHBhdGggbWFwIG5hbWVzcGFjZSBjbGFzc2VzIGxlZ2FjeSBoaXN0b3JpY2FsIHN1cGVyc2VkZWQsIEQzIHN0YWxlX2NsYXNzLCBlYXJsaWVyIGxhbmRpbmdzIHJlZCBhY3Jvc3Mgc3VpdGVzIGZyb20gb25lIGFkb3B0IGNoYW5nZSBhbmQgdGhlaXIgcm9vdCBjYXVzZXMiLCJyIjowLCJzIjoiYzFlODFhZmQzZTc1NjBlN2E4Zjc2OWJiNTFkZTA4M2IwN2Q3MjE1OCIsInQiOm51bGwsIngiOlsiM2UzNTRkYTMxZmZmNzlmMzdiNjhmYjUxIiwiZDQwYzExYTQ3OWQ2NTQzYTZlOGExZWVkIl19",
  "routing": {
    "code": [],
    "named": [],
    "phrasings": [
      "adoption stage A3 refusals and the path map namespace classes legacy historical superseded, D3 stale_class, earlier landings red across suites from one adopt change and their root causes",
      "adoption stage A3 refusals path map namespace classes legacy historical superseded D3 stale_class earlier landings red across suites one adopt change root causes"
    ]
  },
  "pool": {
    "settings": {
      "meaning_uncut": true,
      "route_depth": 60,
      "rerank_depth": 40,
      "per_file_first10": 2,
      "drop_nested": true
    },
    "reranked": 40,
    "order": "first",
    "nested": []
  }
}
