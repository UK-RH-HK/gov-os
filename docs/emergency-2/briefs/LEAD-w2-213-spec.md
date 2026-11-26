# Lead brief: w2-213-spec, W2-213's specification in the owner's order, slice 1 ready to build (DEC-1255, DEC-1256; product-spec)

You are a spec lead (Sonnet, medium; the product-spec role and the `spec-writing` skill), started by the Gov OS CTO on 2026-11-26.
**Read `docs/emergency-2/briefs/LEAD-COMMON.md` first** (memory first with `--root /home/usain/gov-os-worktrees/W2-00-store`, never cut a
result, never open a sets root, never glob `/home/usain/*`). Decide, never ask (I-10): an open point is written in the spec's open
questions as a package for the owner, never asked of the CTO. You write the spec and the ticket's fields; no code, no tests.

## Read, whole
DEC-1255 and DEC-1256 in `docs/DECISION_REGISTER.md` (the owner's scope and order, his words); the accepted rubric
`docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md` and its page's cards (`docs/emergency-2/integration/RUBRIC-DECISIONS-2026-11-26.html`,
every recommended option accepted except C-03, which is (c): no two passes, ASMO OS restructures fully once); the sheet
`docs/emergency-2/integration/ANSWERS-B-2026-11-26-rubric.txt`; `.tickets/DAEO-stdl.md`; `docs/RUBRICS.md`; the golden workflow's W1, W7
and Q-2 to Q-5 (`docs/emergency-2/GOLDEN-WORKFLOW.md`); an existing spec in the nine-part form as the example (find one under
`docs/specs/` with `gov retrieve`); the path map schema `template/governance/kernel/schemas/path-map.schema.json`.

## What: `docs/specs/W2-213-standard-layout.md`, the nine-part form, in the owner's order (DEC-1256 (1) to (5))
- **Slice 1, now, fully specified and ready to build:** (a) the standard frozen in the kit, `standard.yaml` (its path in the kit
  beside the other kernel files: the folders, the classes, the memory rules, exactly as R-01 to R-07 accept them, one entry per class with
  its destination and its memory policy) with its schema; (b) the checker: a command (name it; under `gov`, e.g. `gov layout check
  <plan>`) that reads a plan of nine-field lines (R-09's fields, exactly) and runs the seven code checks of R-09 on it before any move,
  printing each finding with its line and exit 0 only when clean; how a plan is written (the file form) and where it lives. Every K-line
  starts with a stable id (`SL-1`...), observable, with a failure line and a verify that names what the step must produce (the plan's
  rule 5). Test data: synthetic plans and a planted repository (declare it in the test-data table, the DS rows' form).
- **Slices 2 to 4** (the product CTOs' classing, the owner's yes, the moves by hand with rollback; ASMO OS's A6 is its restructure;
  EXAMIN measures again only after it, `forbidden-reach` first) are the products' work by the rubric, not this ticket's code: state them as
  the flow slice 1 must serve, with what each needs from slice 1.
- **Slice 5:** the rest of W2-213 (the generator of the path map from the standard, the moves and the reference rewrites by code, the same
  flow for an import, a tool's install, testing a tool before use, retiring), K-lines drafted, marked to be finalised when slice 1 lands;
  EXAMIN and ASMO OS its proving cases, found clean.
- The spec's open questions: anything the rubric leaves open for slice 1, as packages (question, options with costs, recommendation).

## The ticket
In `.tickets/DAEO-stdl.md` replace the placeholder SL-0 and its path: `kpis` become slice 1's K-lines, each a word-for-word copy of the
spec's line with code named only in its `verify` (Q-4, Q-5), and their failure lines; `allowed_paths` become slice 1's paths (the kit
file, its schema, the checker's source under `src/gov/`, `tests/unit/<its folder>/`, `tests/acceptance/W2-213/`, the path map's lines if a
new folder needs one); keep `kind: feature`, `approved_by`, `specification`. Check that the ticket still passes the ticket schema
(`tests/acceptance/W1-08/test_w1_08_ticket.py::test_the_committed_tickets_validate_against_the_ticket_schema`, through the heavy slot) and
that every new path is held by the path map exactly once.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-w2-213-spec`, branch `e2/w2-213-spec` from `w2/integrate`; commit with `Role: product-spec`,
`Task: DAEO-stdl`, `Class: F`, one trailer paragraph.

## Return
Branch and head; slice 1's K-line ids with one line each; the checker's command and the plan's file form; the open questions; your
retrieves (count, queries, records used).

## Your memory bundle (DEC-1249 (1); profile: decisions, history and plans; uncut)
store: 691bb72d6f41 (/home/usain/gov-os-worktrees/W2-00-store-b)
{
  "store": {
    "commit": "691bb72d6f41e56eeb5eb4b6bb7ee00b792216da",
    "head": "691bb72d6f41e56eeb5eb4b6bb7ee00b792216da",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-b"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "714348c71cc35f63d995d1fc",
      "sha256": "a2a283506ad79130205907806e731cd30ed5c62c81e27219a4534af55c91e281",
      "path": "src/gov/discover/draft.py",
      "start_line": 113,
      "end_line": 129,
      "text": "def spec(words: str, profile: str, types: list[str], ask_profile: bool, sources: list[str], memory: str,\n         names: dict[int, str] | None = None) -> str:\n    \"\"\"The draft ``spec.md``: the nine parts, then ``## Verify`` and ``## Sources read``.\"\"\"\n    out = []\n    for part in PARTS:\n        if part == \"Problem\":\n            body = words\n        elif part == \"Open questions\":\n            body = (\"<!-- Each question is a package: its options with their cost, and a recommendation. -->\\n\"\n                    + questions(profile, types, ask_profile, names or {}))\n        else:\n            guide, slot = GUIDE[part]\n            body = f\"<!-- {guide} -->\\n{slot}\"\n        out.append(f\"## {part}\\n{body}\\n\")\n    out.append(f\"## Verify\\n<!-- {VERIFY_GUIDE} -->\\n- K1: <how K1 is checked, and its result>\\n\")\n    out.append(\"## Sources read\\n\" + \"\\n\".join([*(sources or [\"- none\"]), memory]) + \"\\n\")\n    return \"\\n\".join(out)\n",
      "chunk_id": "714348c71cc35f63d995d1fc",
      "routes": [
        "code"
      ],
      "batch": 1
    },
    {
      "id": "060407cf79d5343db158b801",
      "sha256": "835e31acca5e0ee5fb4589c415e792e718e4c8fd95b64c1dd8f75fa6a0f98896",
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "start_line": 338,
      "end_line": 342,
      "text": "## Change log\n\n| Version | Date | Change |\n|---|---|---|\n| 0.1 | 2026-11-26 | First proposal (DEC-1255 (3)), for the owner's yes on `B-2026-11-26-rubric` |\n",
      "chunk_id": "060407cf79d5343db158b801",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "bcbcff6f6620dacee0226a82",
      "sha256": "c649cca5a361ae19e0a69ae46e85ca0d041f7116be55fb7ed6cca857a710617e",
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "start_line": 58,
      "end_line": 68,
      "text": "## 1. The classes\n\nEighteen classes, a closed list held by code (card R-01). \"Memory\" uses three policies: **embedded** (keyword index and\nvectors), **keyword** (keyword index only, `embedding_policy: not embedded`), **out** (`lexical_policy: not indexed`,\n`embedding_policy: not embedded`, or `memory_class: product`, which the indexer never reads). \"Tier\" is the\n`retrieval_authority` tier: governing, middle, reports, reference (last). \"Moves\" covers an owned repository's\nrestructuring at A6. Every move needs the owner's yes on that repository's plan (DEC-1255 (2); card R-11). The table says\nwhen a class never moves at all.\n\n| # | Class | Definition | How to tell it (signs) | Place in the standard | Memory, tier | Moves? | Basis |\n|---|---|---|---|---|---|---|---|\n",
      "chunk_id": "bcbcff6f6620dacee0226a82",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DEC-1255",
      "sha256": "b1233ab264431d75751ba4b1a52218cf6dbe9eb7de57077c39faeabe54fa6f93",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2331,
      "end_line": 2331,
      "text": "  - (3) \"Before that ticket's spec: the classification rubric, designed first. Launch a design and audit session for it, on the model the rubric sets for an audit I ask for.\" It reviews the real kinds (a developed product such as EXAMIN, a light repository such as ASMO OS, a fresh one, an imported tool or library, code reconstructed with REA, data sets, vendored and generated files, archives, hidden evaluation sets, secrets) and every action (adoption, importing, installing a tool, testing a tool before use, retiring); for each kind and action it proposes how material is classed, where it lives in the standard, how memory treats it, what moves and what never moves, and what needs the owner's yes; it comes back as a rubric for his yes in the form of his decisions pages, before the ticket's spec is written; the rubric then joins the rubrics register.\n",
      "chunk_id": "ae3785d2df7bb36b13ea4a8d",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1,
      "entry": "DEC-1255",
      "status": "ACCEPTED",
      "changed_by": [],
      "in_force": true
    },
    {
      "id": "DAEO-stdl",
      "sha256": "98cd4e228024fc78e3299771e1db58c6f7d13d373036a376dfc7d26c9a6fd7e5",
      "path": ".tickets/DAEO-stdl.md",
      "start_line": 1,
      "end_line": 38,
      "text": "---\nid: DAEO-stdl\nstatus: open\ndeps: []\nlinks: []\ncreated: 2026-11-26T11:30:00Z\ntype: task\npriority: 2\nassignee: engineer\nexternal-ref: W2-213\ntags: [layout, classification, rubric, path-map, adoption, imports, kit]\nwbs_id: W2-213\ntitle: \"A standard repository layout and classification by rubric: the path map follows a standard, never words in paths; agents class in parallel in a fixed form, code merges and checks, the owner approves an owned repository's moves, code executes and rolls back\"\nclass: implementation\nkind: feature\napproved_by: DEC-1255\nstate_class: AUTHORITATIVE\nrole: engineer\nprofile: FULL\ndepends_on: []\nwaits_on: [the classification rubric's yes (DEC-1255 (3)), then this ticket's specification]\nspecification: docs/specs/W2-213-standard-layout.md\nallowed_paths:\n- docs/specs/W2-213-standard-layout.md\nkpis:\n  success:\n  - 'SL-0 The specification first: after the owner''s yes on the classification rubric (DEC-1255 (3), page B-2026-11-26-rubric), `docs/specs/W2-213-standard-layout.md` is written in the nine-part form from the accepted rubric, its K-lines and allowed paths replace this line and the path above, and the ticket is then ready. Fails if: a build starts before the spec, or the spec contradicts an accepted card. Verify: the spec file exists, cites the rubric''s accepted decision id, and this ticket''s `kpis` and `allowed_paths` name its K-lines and paths'\n  failure:\n  - 'F-SL0 Work other than the spec starts on this ticket before the rubric''s yes. Verify: no commit with `Task: DAEO-stdl` touches a path outside the spec file until the spec lands'\nnon_goals:\n- Restructuring Gov OS itself (it keeps its classing until restructuring pays; its tests pin its paths)\n- Restructuring an imported tool or code (it sits whole in imports/<name>/ with one class)\nsources: [DEC-1255, DEC-1254, DEC-1222, DEC-1228, DEC-1252]\nacceptance_tests:\n  path: tests/acceptance/W2-213/\n  author: independent-test-designer (MR-3); written before implementation, from the specification\ntrack: F\n---\n",
      "chunk_id": "f529c1208bf2180f9cf50826",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "b4399186680efb2d8abe5b11",
      "sha256": "052e869b64f09b8098714d92ab692c48b7a4eaeb1df6d08113cbd33cad68602e",
      "path": "docs/emergency-2/integration/RUBRIC-DECISIONS-2026-11-26.html",
      "start_line": 96,
      "end_line": 126,
      "text": "    <li>At the end, tap \"Copy the answer sheet\" and paste it to your advisor, then to the CTO.</li>\n  </ul>\n</section>\n\n<div id=\"sections\"></div>\n\n<h2>Your answer sheet</h2>\n<div class=\"sheet\">\n  <div class=\"btns\">\n    <button id=\"take-cto\">Take every recommendation</button>\n    <button class=\"ghost\" id=\"clear\">Clear my answers</button>\n  </div>\n  <p class=\"hint\">Taking the recommendations keeps any notes you've written. A note is sent as one line, 400 characters at most.</p>\n  <textarea id=\"answers\" readonly aria-label=\"Answer sheet\"></textarea>\n  <div class=\"btns\"><button id=\"copy\">Copy the answer sheet</button></div>\n  <p class=\"hint\" id=\"copied\" aria-live=\"polite\"></p>\n</div>\n</main>\n\n<script>\nconst BATCH=\"B-2026-11-26-rubric\";\nconst SECTIONS = [\n {\n  \"title\": \"1. The classes and what memory holds\",\n  \"intro\": \"Eighteen classes, each with one place and one memory rule. These three cards fix the list, the memory rules, and the hardest line to draw: a dated record or a stale one.\",\n  \"qs\": [\n   {\n    \"id\": \"R-01\",\n    \"from\": \"Rubric \u00a71 \u00b7 DEC-1255 (2), (3)\",\n    \"title\": \"Class every file into one of eighteen fixed classes?\",\n    \"found\": [\n",
      "chunk_id": "b4399186680efb2d8abe5b11",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "4563f624acbc126b72ae3194",
      "sha256": "f0b497b9d681596c713e058978fd20c4562bb2269c79c448bf064dc6a34dc518",
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "start_line": 91,
      "end_line": 91,
      "text": "      \"text\": \"  - (2) \\\"A new feature ticket, approved now: a standard repository layout and classification by rubric, so the path map follows a standard instead of guessing staleness from words in paths. Guessing needs a new exception every time; a standard does not.\\\" The standard, in the kit: where code, tests, specs (`docs/specs`), research (`docs/research`), governance, everything stale (one `archive/` folder) and everything a repository brings in (`imports/<name>/`) live, with the path map's namespaces and classes fixed by it. A repository we own and develop (EXAMIN, ASMO OS) is restructured to the standard at adoption's A6, with the owner's yes on the moves; its path map then follows the standard. A new repository starts in the standard: `gov init` (I-25). An imported tool or code (REA, Startup Launchpad, a library) is never restructured: it sits whole in `imports/<name>/` with one class (use, absorb or study). Gov OS itself keeps its classing until restructuring it pays, since its tests pin its paths. How it works: the rubric becomes code (its classes, its rules and where each class lives); the judgement is an agent's, classing each file, folder and piece of material in a fixed output form (path, class, destination, reason); the repository is split into disjoint chunks by path, so up to ten agents (within the machine's gate) class it in parallel; code merges and checks their answers (every tracked file classed exactly once, every class valid, every destination where the standard puts that class; a gap, a double or a conflict goes back to its agent); the orchestrator reviews the merged classification and the restructuring plan (each move, each namespace, what memory will hold) and brings the owner the moves of a repository we own for his yes; code executes the approved plan (the moves, the path map regenerated from the standard, memory rebuilt, the impact-selected tests run, a rollback if anything breaks). The same flow serves every stage: adoption, an import, installing a tool, testing a tool before use, retiring. \\\"File it under the right owner and give me its place in the releases; it does not hold 0.1.8.\\\"\\n\",\n",
      "chunk_id": "4563f624acbc126b72ae3194",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DEC-1052",
      "sha256": "7fae51254511b89674d46eb6610d8bd8448fb2a2401f98fc01c2861a1ac51cff",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 1410,
      "end_line": 1410,
      "text": "- **The rows** (`packages/INVESTIGATION-1-COMBINED.md`): **approved:** T-2, T-3 (first), T-6 to T-11, T-13; Q-2 to Q-14; G-4 to G-9, G-13; M-2, M-3, M-5, M-6; R-6, R-7, R-9, R-10, R-12, R-13; O-5, O-8, O-9, O-11, O-12, O-13; K-1 to K-4; W-1 to W-10. **R-1 to R-5, O-1, O-2, O-4:** no cuts; the templates replace them. **O-3 refused:** a fresh CTO session every day; orchestrators keep long contexts. **O-6:** ACTs are for machine changes (installs, services, crontab) and only where they help; restarts of the repository's own servers from committed configs are approved by class; no ACTs for records. **G-12 refused:** review effort stays as it is. **G-3:** the hidden half of the memory measure moves outside every worktree, so no guard rule is needed for it. **G-14:** role separation is enforced deterministically from the path map: each role's reads and writes are its paths; the engineer never reads the acceptance tests; the test designer never reads the engineer's new code (it may read the integrated code, DEC-963); simple path checks, no shell guessing; repeated QA findings mean the spec is missing something and go back to product-spec. **M-1:** W2-04 accepted as built; no more runs on it. **M-4:** memory embeds the WBS, the specs and KPIs, the tickets, the code and the decisions; tests and the close, checkpoint and probe records are not embedded (they stay in keyword search, and tickets link to their tests); W2-61's measure before and after. **E1 and R1-21:** yes, inside the refactoring, E1 before the guard ACT. **Option A:** the product switches are re-scoped tickets after the resume.\n",
      "chunk_id": "0b34e63db75aacef7703b858",
      "routes": [
        "lexical"
      ],
      "batch": 1,
      "entry": "DEC-1052",
      "status": "ACCEPTED",
      "changed_by": [
        "DEC-1254",
        "DEC-1217",
        "DEC-1157"
      ],
      "in_force": true
    },
    {
      "id": "deed8786c22b0900296a8b8a",
      "sha256": "66ab022fe82c4356a9ea063b352e375418df8c89b6f99a6a3a1d791b2b56147a",
      "path": "governance/project/orchestration/packages/LIFT-1/D3-WORKLIST.md",
      "start_line": 27,
      "end_line": 29,
      "text": "| 10 | R-6, R-8, R-12, O-11 | register amendments: DEC-511 lifted; delegated choices as ticket or close-record lines; DEC-896 item 2 and DEC-927 item 2 lifted; DEC-1012 and DEC-1003 scoped | `docs/DECISION_REGISTER.md` (one entry) | DONE: DEC-1057's \"Changes\" line |\n| 11 | R-9, R-11, R-12, O-6, O-11 | the prompt: one DECISIONS-IN-FORCE list (\u00a70 points to it), pings only when work waits on the owner, the two-commit rule, ACTs only for machine changes with restarts by class, DEC-1012/DEC-1003 scoped | `governance/project/prompts/w2-orchestrator.md` | DONE (DEC-1057, the owner's eight answers and the rehearsal rule; DEC-1058's who-runs-it) |\n| 12 | R-9, O-6 | DECISIONS-IN-FORCE cut to one list of about 8 KB, LIFTED-BY-DEC953 folded in; the class list of approved restarts (the owner's) | `governance/project/orchestration/DECISIONS-IN-FORCE.md` | DONE (DEC-1057; `RESTART-CLASSES.md`; `LIFTED-BY-DEC953.md` deleted, its references pointed to the list) |\n",
      "chunk_id": "deed8786c22b0900296a8b8a",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "c388f0cc96b9f159d257c0eb",
      "sha256": "a5efe9ffb4e77d1b234f262106f7885212314b2a0a1120e5863abe56ec046228",
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "start_line": 98,
      "end_line": 114,
      "text": "## 2. The standard layout\n\nThe standard lives in the kit (`template/governance/standard.yaml`, a new kernel file `gov update` carries). The path map's\nnamespaces are generated from it: one namespace per class (two for `import-study`: under and over the ceiling; three for\n`archive`: one per `stale_class`) plus one per import. A3 then judges a generated map, not a proposal (card R-04).\n\n```\n<root>/\n  CLAUDE.md  AGENTS.md  README.md       governance (rule files) / docs     tool-fixed, never move\n  .claude/  .github/  .gitignore ...    config                             tool-fixed, never move\n  .rulesync/  .tickets/                 governance                         tool-fixed, never move\n  pyproject.toml  package.json  *.lock  config                             tool-fixed, never move\n  src/   (or the manifest's native root) code                              native layout kept (CAP-44.j)\n  tests/                                tests  (tests/acceptance/<ticket>/)\n  openspec/                             spec   (tool-fixed)\n  docs/                                 docs   (incl. DECISION_REGISTER.md)\n  docs/specs/                           spec\n",
      "chunk_id": "c388f0cc96b9f159d257c0eb",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "58bc8d1800b9af7ec2d6fc3d",
      "sha256": "9fc7041f68d8f0b92d30a1327e09d189253f95fa45e44e26cb60e5ca1a9bdc5a",
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "start_line": 113,
      "end_line": 130,
      "text": "  docs/                                 docs   (incl. DECISION_REGISTER.md)\n  docs/specs/                           spec\n  docs/research/<study>/                research\n  docs/records/<kind>/                  record (Gov OS's tools' own record paths stay)\n  data/                                 data   (own synthetic or test data; real data never tracked)\n  governance/kernel/                    kit    (gov update only)\n  governance/project/                   governance (path map, registers: imports.yaml, tool-registry.yaml)\n  governance/adoption/                  record (adoption's stage records, tool-written)\n  imports/<name>/                       import-use | import-absorb | import-study (one class per import, whole)\n  archive/superseded/<original path>    archive, stale_class superseded\n  archive/historical/<original path>    archive, stale_class historical\n  archive/legacy/<original path>        archive, stale_class legacy\n  (outside every repository)            hidden-set: the registered sets root\n  (ignored, untracked)                  secret, generated: listed by root, never read\n```\n\n**Rules of the layout.**\n\n",
      "chunk_id": "58bc8d1800b9af7ec2d6fc3d",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "0fb882a68f3f11c7192d1c4b",
      "sha256": "75c849bdee04a1339622198a430a4d8218db9e59beb8819445da3ad42f26ccaa",
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "start_line": 325,
      "end_line": 337,
      "text": "## 9. Where it goes next\n\n1. The owner answers `B-2026-11-26-rubric`.\n2. The CTO records the answers (a decision), adds the rubric's row to `docs/RUBRICS.md`, which does not exist yet (RG-0;\n   its first row is this rubric, enforcement `code` once W2-213 lands, `instruction` until then), and its kit copy (RG-2).\n3. A product-spec session writes W2-213's spec from \u00a71 to \u00a78 as answered, with KPI lines for: the standard file and\n   `gov init`; the generated path map; the classing form and the seven checks; the chunking within the gate; L4's reference\n   rewrite; M3 in the record graph; M5; the plan, the yes, the execution and rollback; the D3 retirement in \u00a78. The test\n   data: a synthetic owned repository with planted material of all ten kinds, including an untracked folder, a referenced\n   document, a vendored library, a fake secret and a registered hidden-set path that must never be opened.\n\n---\n\n",
      "chunk_id": "0fb882a68f3f11c7192d1c4b",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "922fd69880e201ba6eccc515",
      "sha256": "0625ded496e32e4ef2cef219dda174e764f68c53e8ea4c8ac3327d49b3d59ddd",
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "start_line": 217,
      "end_line": 228,
      "text": "**The checks code runs on the merged answers.** A failure goes back to its chunk's agent, with the lines named, at most\ntwice (GOLDEN-WORKFLOW rule 3). A third failure goes to the CTO.\n\n1. **Exactly once.** Every item of \"what is classed\" is covered by exactly one line, after folder lines are expanded.\n   A gap or a double fails, naming the path.\n2. **Valid.** `class` is in the closed list; the required fields for that class are present and nothing else; `stale_class`\n   is one of three values; `sign` and `kind` are from their lists; `reason` is not empty and is not a copy of another\n   line's reason across more than ten paths (a filled-in template).\n3. **Where the standard puts it.** `destination` equals L1's function for the class, the path and the import name. A class\n   that does not move has its own path as its destination. A move out of a tool-fixed path or a native layout fails.\n4. **Coherent.** One import, one class: every line under `imports/<name>` and every line naming that import carry the same\n   import class (L5). No two items share one destination (A3's \"target is taken\"). No destination is an existing path. A\n",
      "chunk_id": "922fd69880e201ba6eccc515",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "c59ee72ed77543ad4afa97a3",
      "sha256": "54e3fda12a04d52078b1592eb79afe070cbe9c4f70314a055954a0606207b7e3",
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "start_line": 251,
      "end_line": 251,
      "text": "| **Developed product** (EXAMIN) | Classed whole (\u00a74). Specs, research, records, current docs, archive material, imports and own data move to their places at A6. Code and tests stay in their native layout (L3); the kit, config and governance stay (L2). The path map is regenerated and memory rebuilt. Already adopted, so this is a re-run of A1 to A7 with the generated map. **Owner:** the plan's moves | A new import lands whole in `imports/<name>/` with its register line (origin, kind, class, pin, licence, who, when). **CTO** for use and study, confirmed at the next A5 or by the register commit. Absorb's taken parts land through a ticket, with `commercial_licence` stated | A registry line in `governance/project/tool-registry.yaml` (MCP tools with `kind: mcp` and their roles); installed in a pinned prefix outside the tree; nothing in the tree but the line. **CTO** (G7); **owner** if paid or it needs a secret | In a run folder outside the product. The trial's own records come back as `research` (`docs/research/<trial>/`); nothing of the tool enters the tree until it passes and is installed. **CTO** | Superseded or retired material moves to `archive/<stale_class>/` as a chore (git keeps everything). Retiring the whole product: a tag, the tree read-only, nothing moves. **Owner** for the whole product (irreversible outside a worktree, rule 8) |\n",
      "chunk_id": "c59ee72ed77543ad4afa97a3",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "023b89fdaacd8254da3bb021",
      "sha256": "38abfe78546fbad2e080b15b16c36af880acfa6963bcd124b48f7b982fb09cb9",
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "start_line": 67,
      "end_line": 70,
      "text": "| # | Class | Definition | How to tell it (signs) | Place in the standard | Memory, tier | Moves? | Basis |\n|---|---|---|---|---|---|---|---|\n| 1 | `code` | The repository's own source that is built or run | Under a manifest's package root (`pyproject.toml`, `package.json`, `Cargo.toml`, ...); imported by other code; a language the code graph reads | `src/`, or **the native package root its manifest names**, which the path map records as the code place | embedded, middle; code graph | **No** at A6 when it sits in a native layout; a code move is a ticket of its own | CAP-44.j; `stages.py` `_native`, `CONTENT_CHANGED`; card R-05 |\n| 2 | `tests` | Tests of the repository's own code | Under `tests/`; test-runner names (`test_*.py`, `*.spec.ts`); `tests/acceptance/<ticket>/` by the test designer | `tests/` (acceptance under `tests/acceptance/<ticket>/`) | keyword, reports | As code: no, where the runner's configuration names it | DEC-1052 M-4 (Gov OS `tests`); MR-3 |\n",
      "chunk_id": "023b89fdaacd8254da3bb021",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "3e0e725c078aca6124115559",
      "sha256": "1313883f264ab1b6913940f2c32336d6f6d170c4d64618b60a4bfdae9d73e5f1",
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "start_line": 252,
      "end_line": 253,
      "text": "| **Light repository** (ASMO OS) | As the product. Also: the four untracked, unignored folders (`ASMO-Web`, `GitHub-Harness`, `Infrastructure`, `UPIM-SPEC`) are classed before the plan: add as own code, place as an import, or ignore. The legacy framework (`framework.json`, `governance/framework/**`, `scripts`, `memory`, `hooks`, `tools`) and `spec/1-NOW` position files go to `archive/legacy/`. **Owner:** the plan; timing in card C-03 | As the product. The solar app (DEC-1246 (1)), studied from ASMO OS, is a **declared** study import (a register line naming its folder, nothing copied): it lives inside another repository, carries `Cesium/` and an ignored `.env`. **CTO** | As the product | As the product | As the product |\n| **Fresh repository** | `gov init` lays out the standard and generates the path map from it (I-25). Nothing to class until material arrives; each new file goes to its class's place, and the landing's path-map check (G-8) names a file outside it | As the product | As the product | As the product | As the product |\n",
      "chunk_id": "3e0e725c078aca6124115559",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "25d3e22cc0a2f8f9686d99a9",
      "sha256": "ecd60562bcbac051a06c2444974b1ca37c2e9ec164ac56fec904ad53116335db",
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "start_line": 138,
      "end_line": 149,
      "text": "  The standard lists them; the list grows only by the owner's yes on the rubric. *Basis:* A6 moves nothing it cannot prove\n  safe (`stages.py`); I-16, I-24 (the rule files' generated block is matched by its place).\n- **L3. Code and its tests keep their native layout** (card R-05). The path map records the manifest's package root as the\n  code place. A code move is a ticket of its own, through the flow and its tests, never an A6 batch. *Basis:* CAP-44.j;\n  finding 4 above.\n- **L4. A move another file names is rewritten or held.** Before A6, code lists every tracked file that names a path to\n  move (W2-190 S1's reference search, used for moves as well as deletes). A Markdown link or a path in a document's text or\n  front matter is rewritten by code in the same batch, and each rewrite is listed in the plan the owner approves. A code or\n  configuration file that names the path holds the move: the item stays and the plan names it. *Basis:* W2-190 S1\n  (`DELETE_REFERENCED`); finding 4 above; card R-05.\n- **L5. An import is never restructured.** Its tree moves whole and nothing inside it is renamed, split or edited. One\n  import has one class. *Basis:* DEC-1255 (2); CAP-44.j.\n",
      "chunk_id": "25d3e22cc0a2f8f9686d99a9",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "5c24f8fccfc27372979bccff",
      "sha256": "4a410ae82ec90bb71b1f5f4fb3256e357215c8959a6fc7d89ab93f45709aecf8",
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "start_line": 270,
      "end_line": 291,
      "text": "## 6. What stays judgement, and why\n\nThese stay with the classing agent, inside the fixed form that code checks (GOLDEN-WORKFLOW rule 4, \u00a72):\n\n- **Own or brought in.** The signs can conflict, for example a vendored-looking folder that many of the repository's own\n  later commits edited. Only reading its history and content decides. An unsure item is `ask` (R-10).\n- **Current, record or archive.** Whether a document is still true is a matter of meaning: a plan done, a register replaced,\n  a report that is history and not a rule. Front matter (`status`, `superseded_by`) decides it by code where it exists.\n  Elsewhere the agent decides and names its sign. This is where most errors will sit, so the orchestrator samples it first\n  (card R-03).\n- **Use, absorb or study.** This is the import's purpose, which the repository's intent decides (DEC-1222 IM-2: unsure means\n  held as study).\n- **Where an import begins and ends** (its name and root), and **whether data is synthetic or real** (its provenance; real\n  data is the owner's).\n- **The reason text.** Code checks that it is present, varied and names a sign; it cannot check that it is true. The\n  orchestrator's review and A5's fresh auditor read it.\n\nEverything else is code: the class list, the places, the destinations, the policies, the map, the checks, the plan, the\nmoves, the rebuild and the rollback.\n\n---\n\n",
      "chunk_id": "5c24f8fccfc27372979bccff",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "b26b048566594f06fb7756f7",
      "sha256": "0a5bdda66c5ef23e8e89f2cc0dedc0b646de8c189b54fe75fd417d845a79ab1b",
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "start_line": 125,
      "end_line": 139,
      "text": "  (outside every repository)            hidden-set: the registered sets root\n  (ignored, untracked)                  secret, generated: listed by root, never read\n```\n\n**Rules of the layout.**\n\n- **L1. One place per class, computed.** The destination is a function of the class and the path: `archive/<stale_class>/`\n  plus the original path; `imports/<name>/` plus the path inside the import's root; `docs/specs/`, `docs/research/<study>/`,\n  `docs/records/<kind>/` plus the file name; the path itself for a class that does not move. Code computes it, and the\n  agent's `destination` must equal it (\u00a74 check 3). *Basis:* DEC-1255 (2) (\"every destination where the standard puts that\n  class\"); GOLDEN-WORKFLOW rule 4.\n- **L2. Tool-fixed paths never move.** A file a tool reads at a fixed path (the manifests, CI, agent settings, the kit,\n  the rule files, `openspec/`, `.tickets/`, and the records Gov OS's own commands write) keeps its place whatever its class.\n  The standard lists them; the list grows only by the owner's yes on the rubric. *Basis:* A6 moves nothing it cannot prove\n  safe (`stages.py`); I-16, I-24 (the rule files' generated block is matched by its place).\n",
      "chunk_id": "b26b048566594f06fb7756f7",
      "routes": [
        "lexical",
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
    "duplicates": 32,
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
      "chunk_id": "f529c1208bf2180f9cf50826",
      "parent_id": "a1b6936297518362ad488061",
      "path": ".tickets/DAEO-stdl.md",
      "start_line": 1,
      "end_line": 38
    },
    {
      "chunk_id": "5c24f8fccfc27372979bccff",
      "parent_id": "a6e70c56e9b41f6ded6e7988",
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "start_line": 270,
      "end_line": 291
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "1166c69100bff2ba2642ff81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "5f3bc57e9e6662eddbb42df6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "f2c11b8c40e4a03a94d0ec17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "cec73a266dfd0dfa94def380",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "42c0322522ad8d364d3d6995",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "39ff60849e8671bacda93a69",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "08e40156088240128a1f55a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "aed58ea2c07b653aaea07cbf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "2d7ec72c411897d7b0a7a7bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "71454cae1e47d9dabf793a5d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-stdl.md",
      "chunk_id": "e01abdf9910da9ce04ee95c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "1635b0acf2d76d495f245a6c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "e62e5302ed114bf53bee9e1d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "dc1658986f8576d3024fb445",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "c70f68bf55de84317faf3abf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "29fc2c9313baf23b79c270a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "94e0a4136d9ccab12140ed34",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/refactor_plan.py",
      "chunk_id": "027be47a19d308bfe5d6e34e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/dispatch/dispatcher.py",
      "chunk_id": "89508664ac85093c3eeeb51b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "905b0e6a7081202acba3501d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "197a3a1c98a29936d51a7f0e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/refactor_plan.py",
      "chunk_id": "728f67432979787d0ad9787c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "f0905e0085a2fca055f1a431",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "d427299229d5b8c4913201f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D3-WORKLIST.md",
      "chunk_id": "4914efb49423553a47bf06e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/stages.py",
      "chunk_id": "708bcc92c05577221b900fc7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "5f9b640622817e8cc335dcf3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "f345d7c9a2cbfbdbbf952283",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/refactor_plan.py",
      "chunk_id": "81038ed6716086b75d6749fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "49fc05b1026d3659e7c9dc3e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/decisions/backfill.py",
      "chunk_id": "84f2903f69946e3722b9112a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "c26e2e0ef3d08d685bd93b65",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "feff196a185fd30e3ed13a02",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/brief/build.py",
      "chunk_id": "e4de0b66ce224dabebdaeb33",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "443a2080405d3f091b87c36b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "9c64db95f00d13bae4b18737",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/update/core.py",
      "chunk_id": "71b408dc6ef6088603e3930d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "6c6103e3e9679c4c6cc194a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/stages.py",
      "chunk_id": "c73a2c9b0200e8299e09bd4d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/facts.yaml",
      "chunk_id": "7e0152c8172da0b6a421232d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/refactor_plan.py",
      "chunk_id": "0c0ae8ca78a693c7d3be6629",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "992ea54cf414f088eb350398",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "b7ce740c2b076b6a4413baf1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/role.py",
      "chunk_id": "eb89507e15df115bfabf1832",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "248cda39bd7114c49564c18c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "chunk_id": "c6d7ef05cd7dea9a268d9eb2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "46f39173b9a837617554dd0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RUBRIC-DECISIONS-2026-11-26.html",
      "chunk_id": "9667d613186c75bb2b75b422",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/decisions/backfill.py",
      "chunk_id": "fd06dcb48fd2a955635fb316",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "86913d2f4599a689ea32a9bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/facts.yaml",
      "chunk_id": "c5f5caeeea4e106a2b28a465",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "ef10992578269b9f0e148928",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/decisions/backfill.py",
      "chunk_id": "366f78a72eb3a181d3d0e413",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "73911c27611a79ace5eabdc7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "b47fb03c8382d9ed9bd14230",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RUBRIC-DECISIONS-2026-11-26.html",
      "chunk_id": "e8c2158298640e9771479e1d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "0d1203484ef58f04f89b38ff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "54a3addc03ed98d69363153a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "734e3a8e27dd1507cb25e1c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/decisions/backfill.py",
      "chunk_id": "7a88b73256679d179666ac7d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md",
      "chunk_id": "b4238c46c958a88187f73410",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "9b0e2b5354bcf4fb2714dcf6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/discover/draft.py",
      "chunk_id": "0013410752495e3fde3712e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/refactor_plan.py",
      "chunk_id": "028ae11b3c7b866b0f1bd068",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-31/w1_31_support.py",
      "chunk_id": "a98f908c9eb0ac60188ceaa7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SWITCHED-OFF-1.md",
      "chunk_id": "0293e2d300ae89c5c89ab16e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/brief/build.py",
      "chunk_id": "ed5e976646d025fa02e6dec4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SWITCHED-OFF-1.md",
      "chunk_id": "fa2e7e74af3913a818c143eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/decisions/backfill.py",
      "chunk_id": "bb3dacc1017a9313616157a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "b9a2eeb493637cf27a91cf0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-40/README.md",
      "chunk_id": "58154a7f74896bd92eecd4dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "3903555444a97e6458ea5f04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/update/core.py",
      "chunk_id": "b4257992a5e57c7c00536444",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "c65c872434bbf793186150b8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/a-decisions.md",
      "chunk_id": "668e2014830b97333c15b0d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/refactor_plan.py",
      "chunk_id": "1cd6d08174e6989cb7c088d8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "107c99cddca41b3c1f05c2ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "7a9f387ba1434e1c7732e70a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/decisions.py",
      "chunk_id": "74017d694f6c13834ffe3355",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "61ce8a1aaf39807bf0d01ae3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/decisions/backfill.py",
      "chunk_id": "b6ad00644dca14e0bf8dc33c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/config.py",
      "chunk_id": "f7405126b57dd169659dc8f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-31/w1_31_support.py",
      "chunk_id": "2e487ee773cee16308226ef4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-q8cl.md",
      "chunk_id": "39f4339a28d9aa33872cb435",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "chunk_id": "5e00953f2dcd0f91d70c6a89",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "d0b05f25252deea7d6bb2060",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "chunk_id": "499bed7c3dafe0dadf98039e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "3082ddfeedadfa026639a739",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/check/authority.py",
      "chunk_id": "d7e0d721cf639c40d436c804",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/util/register.py",
      "chunk_id": "6a25563edf054fee7063d09a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-31/w1_31_support.py",
      "chunk_id": "2249a4f903176b7391c49a6e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/brief/build.py",
      "chunk_id": "54ed953cc1120ded70f848e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "8e913d39993a0dbcd6f369f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/check/authority.py",
      "chunk_id": "d32ed2e2c6efcf215105f4db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/util/role_paths.py",
      "chunk_id": "24b63a10c5202dd36fe4e841",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "f4ed4eab9d8523c9907963d8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "262f5f0a66bb122d54d36437",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "9b6c66317d3331389e1348f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-q8cl/PR-DAEO-q8cl-pin3.md",
      "chunk_id": "8be821140b0b85147ae7a037",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/refactor_plan.py",
      "chunk_id": "8b1fbc23a608b7281d177b77",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "b3cd5f2152aa207648be10af",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "50d66d63abf946db57c418a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/decisions/backfill.py",
      "chunk_id": "6d5430b9fb8b6ea87b705efa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/decisions/propagation.py",
      "chunk_id": "1889a7ef5d10cfea8c8b32e0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RUBRIC-DECISIONS-2026-11-26.html",
      "chunk_id": "bb8c44eed14cae736b62d5c4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/RESEARCH-step2-decisions-rubrics.md",
      "chunk_id": "3a754c7181c96150a6db7412",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/command.py",
      "chunk_id": "657b9c472db2cc88e64cd683",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "chunk_id": "e56d51b85f36f179ed0a573c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/refactor_plan.py",
      "chunk_id": "784dbcfe12c53c54a7c74e4b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "b0010c1e3aeccf906025e505",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "chunk_id": "7233a04719178c8c5ca63f64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/slots.py",
      "chunk_id": "02c74a14b219b5ef218bc29d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "b4d77af4474ae2551087064b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/command.py",
      "chunk_id": "62de7891028aa5a41693fd12",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "93cb823999aa6dc40c620540",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "3f424ee074998880ab5c1bd1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "2e6f3b32d7e068318de2396e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/discover/command.py",
      "chunk_id": "a4945274ee3a662ae32d03da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "5ba0f9985afb1c21574e8a84",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "a1e8d30c08ec62e7f9ed5198",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P3-lifts.md",
      "chunk_id": "08ba9e7aa3445c02fd4524e1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/refactor_plan.py",
      "chunk_id": "7088ce936778d810a314957b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/discover/draft.py",
      "chunk_id": "99d47590a2b081d26b24bda4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "c54151add37adc8999937f3a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "5d4d69c8525f4ac0ed0b3b51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "chunk_id": "192706cdb6961f4c0cfb2d27",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-stdl.md",
      "chunk_id": "8fc173cbab6ff9d920e0940f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/measure.py",
      "chunk_id": "4d2fb6da9bedbb893fb3095d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "f7070495845e627f0354dd65",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md",
      "chunk_id": "977cd4f38bf2bc33c257e40f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/util/register.py",
      "chunk_id": "06caeb80d7ea300b65cbb5cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "db024aa90081b097af3005af",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/gate.py",
      "chunk_id": "fa6311c51007d370d6a2ca3d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-40/README.md",
      "chunk_id": "a7d811afb0d3903b139ee785",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/W2-32-S11-WORDING.md",
      "chunk_id": "6a3525f4f920287b1f44f83a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "26661c8f467bf852f5e7dead",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "a29b9e00704af4118d32a816",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/discover/command.py",
      "chunk_id": "5533f400fdfbbaf7130f030c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "fdfdd00a98c2580a742563e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "6508affb5abc205fe2fe8092",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-stdl.md",
      "chunk_id": "1416c9dda9dba73d2ade490b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "5ef0240ac244e5ecff7f9bf6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/gate.py",
      "chunk_id": "fdbbceaa87d98f6932e8dfbb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-RESULT.md",
      "chunk_id": "93e0ef990b2e8661cb2c1dc1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "d7d314a3d0f18b0833273f33",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "053658c9410edf4b61bb7d0c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/discover/draft.py",
      "chunk_id": "67a486902650258900e4233d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "cb8c3d1cf6daa201441a5d7d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RUBRIC-DECISIONS-2026-11-26.html",
      "chunk_id": "aaac68dea6f3543005e74ad2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/decisions/backfill.py",
      "chunk_id": "d06bbbb03b2f24c2c723e7d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "143fb26cb10717366e98447d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-classification-rubric.md",
      "chunk_id": "51fc973ac35a9761643a7ad3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "eaebd9168f2ca80fdbcb4eaa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "ad66a715641a177f79c3fc58",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "e048329d07f57fe7077956ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "bc798cb2e9139758e349cbed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/refactor_plan.py",
      "chunk_id": "cebd35ad352eca9a833925ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/measure.py",
      "chunk_id": "cd67a86cbfcb1d5af929137d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "1ad392d53dbf1d32ebce12f7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/dispatch/dispatcher.py",
      "chunk_id": "3290b69b93b4c21a43ff744e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/brief/build.py",
      "chunk_id": "5609d872e68230f09fb82d5d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "e066f7e66c573901c42f48a4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/check/graph.py",
      "chunk_id": "b60b8b1ad949064aad513589",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "aca2b0831e5357292b7ce042",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/gate.py",
      "chunk_id": "9f32f2af06cfaaf2964538a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "c566e40df1d5f56a8f2fc827",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/update/core.py",
      "chunk_id": "af11a70456747b3ea79c4bf4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "2466938a722a33b519a5d889",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/check/authority.py",
      "chunk_id": "4b1cdafcf5d93147340d30ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "chunk_id": "684a12aefedf1d6fa7c93130",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "b87e719b6de9db4de5e3182d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/refactor_plan.py",
      "chunk_id": "82218a5727936d91c87408fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "b438b45f4bb2dd0948f1282f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "83edefdb93ba505d49ca11a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "a6319e47b1c101163f2195cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "cb39fabcee0f7d23df5e54c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/machine.py",
      "chunk_id": "4f891faa1665d782501864a4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "c0121afe482ecc20bf4a2e01",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/command.py",
      "chunk_id": "8a64e5d6e03eed67883e6ca4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "82d49248e0f54a6b7f743769",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "f008f568b6ab9e3414df4907",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "f72385a432c1a694ef0a8717",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "ab395a1af19931083ff89906",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "514b7d4fe6f442aeca713d62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/brief/build.py",
      "chunk_id": "3f5b2292343bf1ffcdbf735e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "d54b949b0dae118baed5c24a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "9bed8f6cf39399be28a0ffd9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "b161d20f3704b6809021b554",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "d27eb20754a9d0a5110c4dca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/util/role_paths.py",
      "chunk_id": "6a3c0c235a56dcdb1c9dc20b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md",
      "chunk_id": "a2c917956c9ef4501d0eec96",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/discover/command.py",
      "chunk_id": "acf6d3fa28c3922ac09aa044",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "ffe4d86090b899ade806b887",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "db3f7383f3bd271b3416fff5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "8c16659766f4aafa261b0c83",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/gate.py",
      "chunk_id": "1dac557de5b482ca63a1b846",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/brief.py",
      "chunk_id": "92173070f2e7bc0d4de45362",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "9098a5e2d4a540821a329be4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/slots.py",
      "chunk_id": "5d900d22f24ff753e11cc2fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/command.py",
      "chunk_id": "a57a333b3a2c22805601fd7e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "80039b8def432779a95f6003",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/backup/bundle.py",
      "chunk_id": "f2e9b20748afba8f22268462",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/discover/draft.py",
      "chunk_id": "28d8d3ba779be230a39d14d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "4d73d192eb82c1c1ffb6b72d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/update/core.py",
      "chunk_id": "28ccc6bf9313de29fe44eaf4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "b0cd1eac3a5454014dc41ed6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "96d42720527130a92d4cabfb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "55d73c65864bf72120d55141",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "fd37d944c9dcf1b0c691a02d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/util/register.py",
      "chunk_id": "dfc95ef2ce9139445aee135c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/update/core.py",
      "chunk_id": "8a776a09ead8e8ef9c34d13f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "57ba150ef74e7990e5cbbf13",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "04477b3a1b8ae3f2fba77098",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "a0913f1c818f3dc8e41bed98",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/decisions/propagation.py",
      "chunk_id": "68f4adaf759f41543054da19",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "aad4bd94290bf9c6994a2312",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "e7e6c982188ef86a43f92cb6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "0a5f2b0c7d67dab65765615e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/check/claims.py",
      "chunk_id": "bcb7fd0ad3eae3fc531002e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/util/frontmatter.py",
      "chunk_id": "f0714f8e0ec8e1a3b000b790",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/command.py",
      "chunk_id": "0596173241f562e9f8c05eb1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "39d58bfe7c68555ecb03a5f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "adfabb4be886adc0708c3409",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "58e3548f6225f81bf0b4268e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "18fe4add9fd6a788e66cf69f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/check/graph.py",
      "chunk_id": "5603a2d42ecfc40bb2ef3ef8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "4d68aa2ffb4555970d4ff8e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/slots.py",
      "chunk_id": "1d9eb3082eb12ac6943cd018",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "261dca71bdd50061a87b803c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/gate.py",
      "chunk_id": "0b3d36114c0c9b94b8ea988b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "7a1726546227c8567cfd2596",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/update/core.py",
      "chunk_id": "da976b8dbd01693fa4df272b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/update/core.py",
      "chunk_id": "59bac7f2e30628ea80d78856",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/update/core.py",
      "chunk_id": "4321c98cac5e3da0fd1d065c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/backup/bundle.py",
      "chunk_id": "7f16a699419437c9e1cd857c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "025e379b4ecec4c417d9a6b1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "f3362c8d0f216a62944f0db9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/backup/bundle.py",
      "chunk_id": "247c69249b70a47694ac7479",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "708e23331859bba5b3450d24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "69d91cbcccebbd4073062bd3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "ef89c80fe218b716458d4fe4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/backup/bundle.py",
      "chunk_id": "cec914791829d14be9ae32de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "8c8fb26764bba922120c64a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "5cf09fc94e8bdfc056c44a75",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/check/claims.py",
      "chunk_id": "e2e3fb86083ce39caddc1b24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "de89becfc89d9b15379e3f34",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "ee4723c30fad9d5d5640dfe2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "3ffe2b35333b186f0384eb44",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "43c9ac4708e9b62a8c0d0968",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "37c0c30c950306d031d7a304",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "ed0dcef6a842c281422419e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/backup/bundle.py",
      "chunk_id": "8004c6e4c2586a1d00704bf8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/check/graph.py",
      "chunk_id": "c94205c2483ae5bc80edf31c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/update/core.py",
      "chunk_id": "fdc133d175aaa6ddfbff2e24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/machine.py",
      "chunk_id": "7cb4dff20328a1f6bc274250",
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
      "used": 5829
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLXN0ZGwubWQiLDIyLDM1LCIxNDBhMjk2OGZkOWE2MTgyNDdmM2Q3NTQiXSxbImRvY3MvREVDSVNJT05fUkVHSVNURVIubWQiLDE0MTAsMTQxMCwiMGIzNGU2M2RiNzVhYWNlZjc3MDNiODU4Il0sWyJkb2NzL0RFQ0lTSU9OX1JFR0lTVEVSLm1kIiwyMzMxLDIzMzEsImFlMzc4NWQyZGY3YmIzNmIxM2VhNGE4ZCJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9icmllZnMvQVVESVQtY2xhc3NpZmljYXRpb24tcnVicmljLm1kIiw5MSw5MSwiNDU2M2Y2MjRhY2JjMTI2YjcyYWUzMTk0Il0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL1JVQlJJQy1ERUNJU0lPTlMtMjAyNi0xMS0yNi5odG1sIiw5NiwxMjYsImI0Mzk5MTg2NjgwZWZiMmQ4YWJlNWIxMSJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9wcm9wb3NhbHMvQ0xBU1NJRklDQVRJT04tUlVCUklDLm1kIiw1OCw2OCwiYmNiY2ZmNmY2NjIwZGFjZWUwMjI2YTgyIl0sWyJkb2NzL2VtZXJnZW5jeS0yL3Byb3Bvc2Fscy9DTEFTU0lGSUNBVElPTi1SVUJSSUMubWQiLDY3LDcwLCIwMjNiODlmZGFhY2Q4MjU0ZGEzYmIwMjEiXSxbImRvY3MvZW1lcmdlbmN5LTIvcHJvcG9zYWxzL0NMQVNTSUZJQ0FUSU9OLVJVQlJJQy5tZCIsOTgsMTE0LCJjMzg4ZjBjYzk2YjlmMTU5ZDI1N2MwZWIiXSxbImRvY3MvZW1lcmdlbmN5LTIvcHJvcG9zYWxzL0NMQVNTSUZJQ0FUSU9OLVJVQlJJQy5tZCIsMTEzLDEzMCwiNThiYzhkMTgwMGI5YWY3ZWMyZDZmYzNkIl0sWyJkb2NzL2VtZXJnZW5jeS0yL3Byb3Bvc2Fscy9DTEFTU0lGSUNBVElPTi1SVUJSSUMubWQiLDEyNSwxMzksImIyNmIwNDg1NjY1OTRmMDZmYjc3NTZmNyJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9wcm9wb3NhbHMvQ0xBU1NJRklDQVRJT04tUlVCUklDLm1kIiwxMzgsMTQ5LCIyNWQzZTIyY2MwYTJmOGY5Njg2ZDk5YTkiXSxbImRvY3MvZW1lcmdlbmN5LTIvcHJvcG9zYWxzL0NMQVNTSUZJQ0FUSU9OLVJVQlJJQy5tZCIsMjE3LDIyOCwiOTIyZmQ2OTg4MGUyMDFiYTZlY2NjNTE1Il0sWyJkb2NzL2VtZXJnZW5jeS0yL3Byb3Bvc2Fscy9DTEFTU0lGSUNBVElPTi1SVUJSSUMubWQiLDI1MSwyNTEsImM1OWVlNzJlZDc3NTQzYWQ0YWZhOTdhMyJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9wcm9wb3NhbHMvQ0xBU1NJRklDQVRJT04tUlVCUklDLm1kIiwyNTIsMjUzLCIzZTBlNzI1YzA3OGFjYTYxMjQxMTU1NTkiXSxbImRvY3MvZW1lcmdlbmN5LTIvcHJvcG9zYWxzL0NMQVNTSUZJQ0FUSU9OLVJVQlJJQy5tZCIsMzI1LDMzNywiMGZiODgyYTY4ZjNmMTFjNzE5MmQxYzRiIl0sWyJkb2NzL2VtZXJnZW5jeS0yL3Byb3Bvc2Fscy9DTEFTU0lGSUNBVElPTi1SVUJSSUMubWQiLDMzOCwzNDIsIjA2MDQwN2NmNzlkNTM0M2RiMTU4YjgwMSJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vcGFja2FnZXMvTElGVC0xL0QzLVdPUktMSVNULm1kIiwyNywyOSwiZGVlZDg3ODZjMjJiMDkwMDI5NmE4YjhhIl0sWyJzcmMvZ292L2Rpc2NvdmVyL2RyYWZ0LnB5IiwxMTMsMTI5LCI3MTQzNDhjNzFjYzM1ZjYzZDk5NWQxZmMiXV0sImYiOiIvaG9tZS91c2Fpbi9nb3Ytb3Mtd29ya3RyZWVzL1cyLTAwLXN0b3JlLWIiLCJpIjpbXSwibyI6MjAsInAiOnsiYiI6InNlcnZpY2UiLCJkIjoiY3VkYTowIiwiaCI6ImQ1ZTM0NzQ4MzY3OWZhZjgiLCJvIjpbMjcsMCwxMSwyNiwxMCwxOSw2LDM5LDI5LDM3LDcsMTgsMSwzLDE0LDIyLDI0LDE2LDksMjAsMiw0LDMzLDgsMzIsMTIsMjUsMTMsMTUsMjMsMzUsMjEsMTcsNSwyOCwzNCwzMSwzNiwzOCwzMF19LCJxIjoidGhlIGNsYXNzaWZpY2F0aW9uIHJ1YnJpYyBSLTAxIHRvIFItMTI6IGNsYXNzZXMsIHN0YW5kYXJkIGxheW91dCwgbWVtb3J5IHBlciBjbGFzcywgdGhlIG5pbmUtZmllbGQgcGxhbiBsaW5lIGFuZCBzZXZlbiBjb2RlIGNoZWNrczsgbmluZS1wYXJ0IHNwZWMgZm9ybSB3aXRoIHN0YWJsZSBLLWxpbmUgaWRzOyBwYXRoIG1hcCBzY2hlbWEiLCJyIjowLCJzIjoiNjkxYmI3MmQ2ZjQxZTU2ZWViNWViNGI2YmI3ZWUwMGI3OTIyMTZkYSIsInQiOm51bGwsIngiOlsiYTFiNjkzNjI5NzUxODM2MmFkNDg4MDYxIiwiYTZlNzBjNTZlOWI0MWY2ZGVkNmU3OTg4Il19",
  "routing": {
    "code": [
      "714348c71cc35f63d995d1fc"
    ],
    "named": [],
    "phrasings": [
      "the classification rubric R-01 to R-12: classes, standard layout, memory per class, the nine-field plan line and seven code checks; nine-part spec form with stable K-line ids; path map schema",
      "classification rubric R-01 R-12 classes standard layout memory per class nine-field plan line seven code checks nine-part spec form stable K-line ids path map schema"
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
    "nested": [
      {
        "chunk_id": "140a2968fd9a618247f3d754",
        "path": ".tickets/DAEO-stdl.md",
        "start_line": 22,
        "end_line": 35
      }
    ]
  }
}
