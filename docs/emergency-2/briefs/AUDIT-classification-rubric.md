# Audit and design session: the classification rubric (DEC-1255 (3), the owner's order of 2026-11-26)

You are a design and audit session on Opus at high effort, the one exception of rule 7 (a wide audit the owner asks for), started
by the Gov OS CTO on 2026-11-26. You are read-only everywhere except your two output files. Decide, never ask: an open point becomes
a card for the owner, never a question to the CTO. Your helpers (if any) run Sonnet; give each the exact files to read.

## Rules that stay
- **Memory first:** `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"` before grepping for a concept; write
  a long result to a file and read it whole (never `head`, `tail` or a pipe); then search once more in your own words. Your return
  lists every retrieve (count, queries, records used).
- **Never open a hidden question-set root** (EXAMIN's and Gov OS's evaluation roots, or any folder named for evaluation sets), never
  list or glob inside one, and never glob `/home/usain/*` or another repository's root to find a file: use only the exact paths below
  (DEC-1249 (2), I-28). You study hidden evaluation sets as a kind, from Gov OS's records about them (DEC-1249, FINDINGS I-28, the
  `gov memaudit` code and docs), never from their contents. The same for secrets: from the rules and code that handle them, never by
  printing one.
- Never write outside your two output files; never commit to `w2/integrate`; never push. Work in a worktree:
  `git -C /home/usain/Dynamic-Agentic-Engineering-OS worktree add -b e2/rubric-audit /home/usain/gov-os-worktrees/E2-rubric-audit w2/integrate`,
  and commit your two files there with `Role: independent-auditor`, `Task: chore`, `Class: C`, one trailer paragraph.

## The owner's order (DEC-1255, `docs/DECISION_REGISTER.md`; read DEC-1255 and DEC-1254 whole)
A new feature (W2-213, `.tickets/DAEO-stdl.md`, read it): a standard repository layout and classification by rubric, so the path map
follows a standard instead of guessing staleness from words in paths (D3 did, I-40). **Before that ticket's spec, the classification
rubric is designed first:** review the real kinds of material we meet and every action they go through; for each kind and action
propose how material is classed, where it lives in the standard, how memory treats it, what moves and what never moves, and what needs
the owner's yes. It comes back to the owner as a rubric for his yes, in the form of his decisions pages, before the spec is written;
the rubric then joins the rubrics register (DEC-1252 RG-0 to RG-2).

**The kinds:** a developed product (EXAMIN), a light repository (ASMO OS), a fresh one, an imported tool or library, code reconstructed
with REA, data sets, vendored and generated files, archives, hidden evaluation sets, secrets. **The actions:** adoption, importing,
installing a tool, testing a tool before use, retiring. **Fixed by the owner:** the standard lives in the kit; code, tests, specs
(`docs/specs`), research (`docs/research`), governance, everything stale (one `archive/` folder) and everything brought in
(`imports/<name>/`) each have one place; an owned repository is restructured at A6 with the owner's yes; a new one starts in the
standard (`gov init`); an import is never restructured (whole in `imports/<name>/`, one class: use, absorb or study); Gov OS keeps its
classing for now. **How it runs** (the rubric must make this possible): the rubric becomes code (classes, rules, where each class
lives); agents class each file, folder and piece of material in a fixed output form (path, class, destination, reason) over disjoint
chunks, up to ten in parallel; code merges and checks (every tracked file classed exactly once, every class valid, every destination
where the standard puts it); the orchestrator reviews; the owner approves an owned repository's moves; code executes with rollback.

## Read (exact paths only)
- Gov OS: `docs/emergency-2/GOLDEN-WORKFLOW.md` (W1, W2, rules 4 and 6); `docs/emergency-2/EMERGENCY-2.md` §13 (the imports rows);
  DEC-1221, DEC-1222, DEC-1223 (8), DEC-1227 (D3), DEC-1228, DEC-1233 (6), DEC-1245, DEC-1248, DEC-1249, DEC-1252, DEC-1254, DEC-1255
  in the register; `governance/project/path-map.yaml` and its schema `template/governance/kernel/schemas/path-map.schema.json`; the
  kit's path map under `template/governance/`; `src/gov/adopt/` (stages A0 to A10, AS, and D3's `STALE_CLASS` as it is on branch
  `e2/bundle-a`: `git show e2/bundle-a:src/gov/adopt/stages.py`); `src/gov/retrieval/` (namespaces, policies; D3's `stale.py` on
  `e2/bundle-a`); the adopt skill `template/governance/kernel/skills/adopt/SKILL.md`; the guide `adopting-an-existing-repository.md` in
  the kit; FINDINGS I-16, I-24, I-25, I-28, I-36, I-40, I-43 (`docs/emergency-2/integration/FINDINGS.md`);
  `docs/emergency-2/integration/DIAGNOSIS-bundle-a-1.md` (on `e2/bundle-a`); `docs/emergency-2/integration/PRACTICE-FIRST-PLAN.md`
  (RG and DS rows); `docs/emergency-2/integration/TOOL-MAP.md` (imports rows).
- EXAMIN (a developed product), read-only: `/home/usain/gov-os-runs/W2-27/examin/governance/project/path-map.yaml`, its top-level
  folder listing (`ls` of that one folder), `docs/audits/wave0/` there (its assessment and the fresh 80 record
  `docs/audits/wave0/memory/FRESH80-2026-11-25.md`, which names the stale citations).
- ASMO OS (a light repository): `/home/usain/ASMO-OS-V1/governance/project/path-map.yaml` and its top-level listing.
- The solar app (a trial workflow, possibly an import): `/home/usain/workspace/ASMO`, its top-level listing only.
- For REA, Startup Launchpad and libraries: what Gov OS's records say (DEC-1221 to DEC-1228, `gov retrieve`), not a search of disk.

## What you write
1. **`docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md`**, the rubric: the classes (each with its definition, how to tell it, where
   it lives in the standard, its memory policy: indexed and embedded, keyword only, or kept out; whether it moves, and who approves);
   the standard layout (the folders and the path map's namespaces it fixes); a table kind by action (what happens, what moves, what
   never moves, what needs the owner's yes); the fixed output form an agent writes per item and the checks code runs on the merged
   answers; what stays judgement and why; the conflicts with standing decisions or the plan, cited; what happens to D3's word-guessing
   once the standard exists. Every rule with its basis (a decision or an incident, DEC-1233 (6)).
2. **`docs/emergency-2/integration/RUBRIC-DECISIONS-2026-11-26.html`**, the owner's decisions page: copy
   `docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-26.html` and change only the `<title>` text if needed, the header line, the
   lead paragraph, `const BATCH="B-2026-11-26-rubric"` and the `SECTIONS` array. Each card is
   `{"id","from","title","found":[...],"opts":[[key,label,cost,recommended(1 or absent)],...],"reason","sources","stops"}`, one card per
   choice the owner must make (the classes and their memory policies, the layout, what needs his yes, each conflict), 2 to 4 options with
   costs, one recommended, plain words, his phone's width. The page's script must still parse (`node -e` on its script).

## Return (under 400 words)
Branch and head; the number of classes and cards; the three choices you think matter most; the conflicts found; your retrieves (count,
queries, records used).

## Your memory bundle (DEC-1249 (1); profile: decisions, history and plans; uncut)
store: cbb322668017 (/home/usain/gov-os-worktrees/W2-00-store-b)
{
  "store": {
    "commit": "cbb322668017ed3ab7da111fc0cd8e2106b60905",
    "head": "cbb322668017ed3ab7da111fc0cd8e2106b60905",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-b"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "DEC-1255",
      "sha256": "797209f2cdc1068dad4a16fe742639fbc273f61c580f620e3409e47e1f83693a",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2330,
      "end_line": 2330,
      "text": "  - (2) \"A new feature ticket, approved now: a standard repository layout and classification by rubric, so the path map follows a standard instead of guessing staleness from words in paths. Guessing needs a new exception every time; a standard does not.\" The standard, in the kit: where code, tests, specs (`docs/specs`), research (`docs/research`), governance, everything stale (one `archive/` folder) and everything a repository brings in (`imports/<name>/`) live, with the path map's namespaces and classes fixed by it. A repository we own and develop (EXAMIN, ASMO OS) is restructured to the standard at adoption's A6, with the owner's yes on the moves; its path map then follows the standard. A new repository starts in the standard: `gov init` (I-25). An imported tool or code (REA, Startup Launchpad, a library) is never restructured: it sits whole in `imports/<name>/` with one class (use, absorb or study). Gov OS itself keeps its classing until restructuring it pays, since its tests pin its paths. How it works: the rubric becomes code (its classes, its rules and where each class lives); the judgement is an agent's, classing each file, folder and piece of material in a fixed output form (path, class, destination, reason); the repository is split into disjoint chunks by path, so up to ten agents (within the machine's gate) class it in parallel; code merges and checks their answers (every tracked file classed exactly once, every class valid, every destination where the standard puts that class; a gap, a double or a conflict goes back to its agent); the orchestrator reviews the merged classification and the restructuring plan (each move, each namespace, what memory will hold) and brings the owner the moves of a repository we own for his yes; code executes the approved plan (the moves, the path map regenerated from the standard, memory rebuilt, the impact-selected tests run, a rollback if anything breaks). The same flow serves every stage: adoption, an import, installing a tool, testing a tool before use, retiring. \"File it under the right owner and give me its place in the releases; it does not hold 0.1.8.\"\n",
      "chunk_id": "b47fb03c8382d9ed9bd14230",
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
      "id": "DEC-1255",
      "sha256": "b1233ab264431d75751ba4b1a52218cf6dbe9eb7de57077c39faeabe54fa6f93",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2331,
      "end_line": 2331,
      "text": "  - (3) \"Before that ticket's spec: the classification rubric, designed first. Launch a design and audit session for it, on the model the rubric sets for an audit I ask for.\" It reviews the real kinds (a developed product such as EXAMIN, a light repository such as ASMO OS, a fresh one, an imported tool or library, code reconstructed with REA, data sets, vendored and generated files, archives, hidden evaluation sets, secrets) and every action (adoption, importing, installing a tool, testing a tool before use, retiring); for each kind and action it proposes how material is classed, where it lives in the standard, how memory treats it, what moves and what never moves, and what needs the owner's yes; it comes back as a rubric for his yes in the form of his decisions pages, before the ticket's spec is written; the rubric then joins the rubrics register.\n",
      "chunk_id": "ae3785d2df7bb36b13ea4a8d",
      "routes": [
        "lexical"
      ],
      "batch": 1,
      "entry": "DEC-1255",
      "status": "ACCEPTED",
      "changed_by": [],
      "in_force": true
    },
    {
      "id": "DAEO-d3sr",
      "sha256": "ee04e7a62dd8fe82da9bf6c65026cab7ac236d4be19ec527bb9a79f5506a9071",
      "path": ".tickets/DAEO-d3sr.md",
      "start_line": 1,
      "end_line": 54,
      "text": "---\nid: DAEO-d3sr\nstatus: in_progress\ndeps: []\nlinks: [DAEO-l78m, DAEO-d3d4]\ncreated: 2026-11-24T09:00:00Z\ntype: task\nkind: feature\npriority: 1\nassignee: engineer\nexternal-ref: W2-212\ntags: [adoption, retrieval, stale-route, emergency-2, release-0.1.6]\nwbs_id: W2-212\ntitle: \"The route that keeps stale, superseded and legacy documents out of default memory (D3): a declared class on a path-map namespace, the default bundle without it, found on purpose by path or flag, set by adoption, named by doctor\"\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\nprofile: STANDARD\ndepends_on: []\nwaits_on: []\ncloses: []\nallowed_paths:\n- src/gov/retrieval/**\n- src/gov/adopt/**\n- src/gov/doctor/**\n- src/gov/config/**\n- src/gov/check/pathmap.py\n- src/gov/cli/**\n- template/governance/kernel/schemas/path-map.schema.json\n- template/governance/kernel/skills/adopt/**\n- template/.rulesync/skills/adopt/**\n- tests/unit/retrieval/**\n- tests/unit/adopt/**\n- tests/unit/doctor/**\n- tests/acceptance/W2-212/**\nest_loc: 450\nspecification: docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md\nkpis:\n  success:\n  - 'SR-1 Out of the default bundle. In an adopted repository, a document in a namespace the path map marks superseded, historical or legacy (a declared class on the namespace, the optional field `stale_class`, never a guess from its name) is absent from `gov retrieve`''s default bundle, lexical and semantic alike, and a current document on the same topic is present. Verify: the python-app stand-in''s `docs/design/lending.md` absent for the lending question, `lending-v2.md` present.'\n  - 'SR-2 Still findable on purpose. Such a document is still found when asked for by path or by `gov retrieve --include-stale`, and the bundle says it is stale (`stale: true` and its `stale_class`) when it shows it. Verify: the same repository, the lending question with `--include-stale` and a question naming `docs/design/lending.md`: the bundle lists it under `stale`, marked.'\n  - 'SR-3 Adoption sets it. The adopt skill and the A3 form give such namespaces `stale_class` with `lexical_policy: not indexed` and `embedding_policy: not embedded`, and say so; A3 refuses a namespace whose name or paths say superseded, historical, legacy or archive and that lacks the class (`ADOPT_STALE_CLASS`), and gives a notice where only its description fields say so. Verify: a path map with `docs/legacy/**` unclassed is refused naming the namespace; the same with the class and policies is recorded.'\n  - 'SR-4 Every adopted repository gets it. `gov update` carries the route (the schema and the skill are kernel files it copies); in an adopted repository whose path map has such namespaces without the class, `gov doctor` names each with the line to add, as a notice that never fails the run. Verify: a planted unclassed `legacy` namespace: doctor exits 0 and names it with the three lines.'\n  failure:\n  - 'F1 The class cannot fail open. A namespace with `stale_class` and a policy that keeps its files in the index or the vectors is CONFIG_INVALID naming the namespace, and a class value other than superseded, historical or legacy is too; a stale-class file already in the index (built before the class) is still left out of the default bundle.'\nnon_goals:\n- 'The imports feature, a content-reading A2, and the refresh of the index after a path-map change (the Phase 0 lead''s)'\n- 'Editing Gov OS''s or EXAMIN''s live path map'\nsources: [DEC-1227, DEC-1228, docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md, DAEO-l78m]\nacceptance_tests:\n  path: tests/acceptance/W2-212/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: A\n---\n",
      "chunk_id": "9a366b23e8d5a0674bae78d3",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-stdl",
      "sha256": "5ca57ec49de3c4391740dced26fce929301d0f693918cddc3d665e943b826d05",
      "path": ".tickets/DAEO-stdl.md",
      "start_line": 42,
      "end_line": 55,
      "text": "## The owner's scope (DEC-1255 (2), his words in short)\n- **The standard, in the kit:** where code, tests, specs (`docs/specs`), research (`docs/research`), governance, everything stale (one\n  `archive/` folder) and everything a repository brings in (`imports/<name>/`) live; the path map's namespaces and classes fixed by it.\n- **Owned repositories** (EXAMIN, ASMO OS) are restructured to the standard at adoption's A6, with the owner's yes on the moves; their\n  path map then follows the standard. **A new repository** starts in it: `gov init` (I-25). **An import** (REA, Startup Launchpad, a\n  library) is never restructured: whole in `imports/<name>/`, one class (use, absorb or study). **Gov OS** keeps its classing for now.\n- **How:** the rubric becomes code (classes, rules, where each class lives); agents class each file, folder and piece of material in a\n  fixed form (path, class, destination, reason), over disjoint chunks by path, up to ten in parallel within the machine's gate; code\n  merges and checks (every tracked file classed exactly once, every class valid, every destination where the standard puts it; a gap, a\n  double or a conflict back to its agent); the orchestrator reviews the merged classification and the restructuring plan and brings the\n  owner an owned repository's moves; code executes the approved plan (moves, path map regenerated from the standard, memory rebuilt, the\n  impact-selected tests, rollback on any break). The same flow for adoption, an import, installing a tool, testing a tool before use,\n  and retiring.\n\n",
      "chunk_id": "ccde3c0c8852e50ff7a0d19a",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "bfb6c50387e3a793a5fbe481",
      "sha256": "9db7140dc18f4162e21cd52723dce773f97f4fb4d9c045a2e5a3635ee16d0814",
      "path": "docs/emergency-2/briefs/LEAD-bundle-a-reds.md",
      "start_line": 17,
      "end_line": 21,
      "text": "superseded, historical, legacy or archive must state `stale_class`. The planted adoptions of six suites state those classes already in\nthe form the map has always had (`\"classes\": {\"harbour\": \"legacy\", \"archive\": \"historical\"}`), and A3 now refuses them all\n(`ADOPT_STALE_CLASS: the path map is not recorded: namespace harbour says legacy, archive ... and states no stale_class`). A real adopted\nrepository with a legacy namespace (EXAMIN, ASMO OS) would meet the same refusal on its next adoption or update.\n\n",
      "chunk_id": "bfb6c50387e3a793a5fbe481",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-d3sr",
      "sha256": "aa13470a22d81b58c914652d2dbd9f31d4b5fe853dedae7c34f2b92794360dcb",
      "path": ".tickets/DAEO-d3sr.md",
      "start_line": 59,
      "end_line": 62,
      "text": "## Design (the lead's choices)\n- Namespace field `stale_class: superseded | historical | legacy` (optional). It requires `lexical_policy: not indexed` and `embedding_policy: not embedded`.\n- Retrieval drops chunks of stale-class paths from every route unless `include_stale`; `--include-stale` and a path named in the question add a `stale` list to the bundle, read from the files, each entry `stale: true`.\n- A3 refuses a name or path match without the class; a description-field match is a notice. `gov doctor` notices the same for an adopted repository.\n",
      "chunk_id": "2c54993dca65ccad085759dc",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "bede30dacba43ffb04353cf8",
      "sha256": "49d80c339fe0c4d2445193a13d32a60a80af3b70efe4728130d6ebd23f066b2d",
      "path": "docs/emergency-2/briefs/LEAD-bundle-a-reds.md",
      "start_line": 22,
      "end_line": 30,
      "text": "## What\n- **BA-1 (the root fix, under W2-212 DAEO-d3sr, a `Fix:` line):** D3 reads the class a map already states. A namespace classed\n  `legacy`, `historical` or `superseded` by the map's existing classes counts as stating its stale class (archive is historical, as D3\n  says), and D3 then applies its policy (not indexed, not embedded) or its notice, without refusing; A3 refuses only a namespace whose\n  name or paths say stale and which no class of the map states. Write the failing case first (W2-212's folder is the test designer's:\n  a planted map with `classes: {harbour: legacy}` and no `stale_class` passes A3 and keeps harbour out of the default bundle). Do not\n  change the six suites' fixtures: they are the existing form, and the fix makes D3 accept it. If you find the classes mean something\n  else than D3's stale classes, stop that line of work, say what they mean with file:line, and choose the narrowest correct rule.\n- **BA-2 Classify every other red** by running its node ids on `w2/integrate` (the base; a worktree at its head) through the heavy slot:\n",
      "chunk_id": "bede30dacba43ffb04353cf8",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "09de4e55eda7d5204f77d832",
      "sha256": "067f4807a73a9daef71adfd83583fe31d552d1bd41a33f167312515e1f5a1e04",
      "path": "docs/contract/contract.yaml",
      "start_line": 459,
      "end_line": 487,
      "text": "    item: Sensitivity class per path/dataset/namespace before read, index or export; secret-class paths excluded from every\n      index by default-deny; one full gitleaks scan runs once before a repository goes public or is shared with a third party, and no scan runs while it is private\n    source: Contract v3 A3; Framework v4.1.2 \u00a716, \u00a772; EMERGENCY-2 \u00a72.11 (DEC-1211); DEC-1182\n    wave: W1\n    provider:\n    - W1-15\n    - W1-08\n  - id: CAP-03.b\n    item: Development/governance memory separated from customer/runtime product data\n    source: Framework v4.1.2 \u00a716\n    wave: W1\n    provider:\n    - W1-15\n    - W1-08\n  - id: CAP-03.c\n    item: Each namespace declares sensitivity class, permitted roles, retention, export policy, embedding policy, provenance\n      and deletion/rebuild behaviour (path-map namespace fields)\n    source: Framework v4.1.2 \u00a716\n    wave: W1\n    provider:\n    - W1-08\n  - id: CAP-03.d\n    item: Whole-repository corpus minus secrets\n    source: OWNER-CLARIFICATION-BR-0002\n    wave: W1\n    provider:\n    - W1-17\n  - id: CAP-03.e\n    item: Secret exclusion by sensitivity class holds on every retrieval route, including the code route\n",
      "chunk_id": "09de4e55eda7d5204f77d832",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "d99703d9117d6e42b367a2f3",
      "sha256": "9d2bea7d09e88872f936c8ad5aa74099d44befb8f3d32cddf312d1fc2a9cca72",
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "start_line": 58,
      "end_line": 59,
      "text": "| **use** | a dependency the repository runs on and does not own | text (library code, its docs): namespace `imports-use`: memory class governance, keyword index on, embedding off, sensitivity internal at least, tier `reference`. Non-text (datasets, models, binaries, lock files): namespace `imports-use-opaque`: keyword index off, embedding off (product class for customer or runtime data) | text found by keyword only, in the last tier, labelled as an import, so agents can find how to work with it; never embedded, never a record of the graph; non-text reached only through its register line | origin, kind, pin, licence note, who classed it and when |\n| **absorb** | something to assess; the useful parts are taken into the repository's own code or spec | until parts are taken: as use. The taken parts are the repository's own files, in its own namespaces | the taken parts indexed as own with their origin noted; the rest as use | state `to-assess` or `taken`; for taken parts: own paths, origin, version, licence; what is left out |\n",
      "chunk_id": "d99703d9117d6e42b367a2f3",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "d4743752af1c4fea7fee98e3",
      "sha256": "598e6bca7d654ca6f25a89498be6a4738a993cafdaf4b06401990fdd7fb619fd",
      "path": "governance/project/orchestration/packages/MEMORY-SPEC-MAP.md",
      "start_line": 57,
      "end_line": 57,
      "text": "| 9 | **The tools that build indexes and embeddings in an adopted repository** (CAP-44, CAP-20) | `gov rebuild` builds every store where a path map and `.gitleaks.toml` exist. **On an unadopted clone it builds nothing and reports `\"ok\": true`** (W2-26's finding 2). Adoption (A0\u2013A6, A8; W1-39, W1-41): A3 refuses a namespace with a bad embedding policy, and A4 indexes the code graph for importers. **There is no knowledge-fabric stage:** CAP-44.f's A9 (\"new knowledge fabric\") is Wave 3 in the Contract. Nothing assesses a large repository, and nothing plans what full indexing needs | **W2-88 (draft, new, Q9f).** Also W2-52 (held): lite A7 and A10 records (A10 is the independent memory verification); W2-23 (open): adoption safety; W2-81 (claimed): the synthetic repositories, their question sets and the judge; W2-27: the live trial on EXAMIN's copy | **Only by W2-88**, which is new. Before it, **no** |\n",
      "chunk_id": "d4743752af1c4fea7fee98e3",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "c97642dee2be75c6198d9604",
      "sha256": "a4efea04fa7c034d1b33b7cf88535966ad50ecb43eb26ac46ceed9cb43384d90",
      "path": "docs/emergency-2/briefs/LEAD-bundle-a-reds.md",
      "start_line": 189,
      "end_line": 189,
      "text": "      \"text\": \"- **SR-2 Still findable on purpose.** Such a document is still found when asked for by path or by an explicit flag (choose the flag; for example `gov retrieve --include-stale`), and the bundle says it is stale when it shows it.\\n- **SR-3 Adoption sets it.** The adopt skill and the A3 form give such namespaces the declared class with `lexical_policy: not indexed` and `embedding_policy: not embedded`, and say so; A3 refuses a namespace named or described as superseded, historical, legacy or archive that lacks the class (a notice naming it is enough where the name alone is ambiguous: choose and say which).\\n- **SR-4 Every adopted repository gets it.** `gov update` carries the route; in an adopted repository whose path map already has such namespaces without the class, `gov doctor` names each one with the line to add (a notice, never a failure), so EXAMIN and ASMO OS can mark theirs. Gov OS's own path map: say which of its namespaces would take the class (do not edit Gov OS's live map; the CTO does).\\n\\nKernel text you may change (the CTO approves it by naming it here): the adopt skill under `template/governance/kernel/skills/adopt/` and the A3 form's text.\\n\\n\",\n",
      "chunk_id": "c97642dee2be75c6198d9604",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DEC-1228",
      "sha256": "d3fa148b4ae6b0652ee6ac405f6e10813119cae35afb7a5582e2efd0066728ef",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2045,
      "end_line": 2045,
      "text": "- **Decision:** (1) The imports feature is its own ticket, after 0.1.4 and EXAMIN's fresh 80 (IM-1 (b)), with D3's route (DEC-1227). (2) \"MCP tools are a kind of import: registered in the tool registry, their version pinned, installed with your approval, and given only to the roles and sessions that need them. The first is REA (github.com/morluto/rea), for study work.\" (3) \"REA and the code it reconstructs, my rule: such code is imported as study, with its origin recorded (the app, its version, the date, REA). It may be studied and used in research, experiments and development. Before any of it is used in a product being developed, it is classed absorb, and the absorb assessment states whether we hold a commercial licence from the supplier; without one, it stays out of anything commercialised.\" (4) \"The first product to study with REA: Startup Launchpad (https://startuplaunchpad.app/startup-launchpad), a service that scans the repository and live site of AI-built apps for security issues, explains them in plain English and writes fix prompts. REA sees its website and its browser code; its scanning engines run on its servers, so their behaviour is studied from its output: run it on a synthetic test repository with planted issues, never on our own code. The study starts now, in its own folder outside the products: you approve and record REA's install under the install rule, and the study's records move into the imports register when the feature lands.\"\n",
      "chunk_id": "598b9ad4ce77917a0af91943",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2,
      "entry": "DEC-1228",
      "status": "ACCEPTED",
      "changed_by": [
        "DEC-1248",
        "DEC-1232"
      ],
      "in_force": true
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
      "id": "9eb2c4899a5fe0a2a7979323",
      "sha256": "0e41f4dfc982e5c3d1d005d0686bff6ec20e2e6248343bbaefd1c97f398a1805",
      "path": "docs/emergency-2/briefs/STUDY-startup-launchpad.md",
      "start_line": 36,
      "end_line": 39,
      "text": "   (which it should catch, by its claims); what is worth absorbing for Gov OS (for example a security stage for adopted\n   repositories, plain-English findings, fix prompts) classed as the imports spec does (use / absorb / study), each\n   absorb candidate with \"commercial licence: none held\" unless found otherwise; open questions for the owner.\n\n",
      "chunk_id": "9eb2c4899a5fe0a2a7979323",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
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
      "batch": 2
    },
    {
      "id": "b1ae63a4757ac1e710e294d7",
      "sha256": "38fed9d831d6c977c6bac59b0304b2c7aa44d3a2ecc655d66bdd620abb36e126",
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "start_line": 120,
      "end_line": 120,
      "text": "| W2 | **Build memory** | The repository's records, code and documents are indexed: words, meaning and the record graph; stale and legacy material kept out of default memory | Store build and rebuild; the graph's links from front matter; namespaces and their index policy | None | Built; the route that keeps stale and legacy documents out comes in 0.1.6. A path classed in two namespaces (W2-81's A4) is a fix under W1-41 (DEC-1238 (1c)) | As today, plus the route |\n",
      "chunk_id": "b1ae63a4757ac1e710e294d7",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "6cd0a6d6c33cefa19534c560",
      "sha256": "9fdb0d256f87c4e4648226cbe573bd798eda38743ed67b2b818970e027bd01c9",
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "start_line": 15,
      "end_line": 17,
      "text": "- **Adoption sees no import as an import.** A1 lists every tracked file. A2 classes a file by the path map's namespace only and reads no content. A3 takes the adopter's proposal; the tool proposes none. The memory assessment (stage MA) flags vendored files by a folder-name list or a header phrase, and proposes a folder for vendored code that has none; it gives no class, no version, no origin and no licence.\n- **A submodule leaves no trace.** Its entry is a commit, not a file; the assessment and the delete check skip it as \"no file of this repository\". No record, index or answer mentions it.\n- **The record graph ignores the path map.** It reads every Markdown file of the commit that has an `id`, `type` and `status`. I checked on a scratch repository: a copied folder holding a decision `DEC-010` with `superseded_by: DEC-011` gave a second record `DEC-010` and a SUPERSEDES edge into the repository's own `DEC-010`. A copied kit's or a studied project's decision files can therefore demote the repository's own decisions, whatever the namespace says. The code graph also reads every tracked file, not the path map.\n",
      "chunk_id": "6cd0a6d6c33cefa19534c560",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "3e4e9b9cde883b4517bd3cfc",
      "sha256": "14cb9630efeaf51d45cd54c2e01187aeabef99d50131ca65be8cf4b9d353febb",
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "start_line": 17,
      "end_line": 18,
      "text": "- **The record graph ignores the path map.** It reads every Markdown file of the commit that has an `id`, `type` and `status`. I checked on a scratch repository: a copied folder holding a decision `DEC-010` with `superseded_by: DEC-011` gave a second record `DEC-010` and a SUPERSEDES edge into the repository's own `DEC-010`. A copied kit's or a studied project's decision files can therefore demote the repository's own decisions, whatever the namespace says. The code graph also reads every tracked file, not the path map.\n- **The path map already has what \"place in memory\" needs, as configuration:** a namespace's `embedding_policy` (embedded or not), its `lexical_policy` (indexed or not), its sensitivity, and the `retrieval_authority` block (ordered tiers by path or record, each step lifting or lowering a hit). Gov OS's own path map uses it by hand (`kernel-vendored`: vendored, not embedded, pinned in the tool registry). `memory_class` has only two values (governance, product), so a \"research namespace\" is a naming and policy choice, not a class. The path map's `research_corpus` switch is validated and read by nothing else.\n",
      "chunk_id": "3e4e9b9cde883b4517bd3cfc",
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
    "duplicates": 33,
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
      "chunk_id": "9a366b23e8d5a0674bae78d3",
      "parent_id": "55bab9d170ca47e5b9743c8c",
      "path": ".tickets/DAEO-d3sr.md",
      "start_line": 1,
      "end_line": 54
    },
    {
      "chunk_id": "ccde3c0c8852e50ff7a0d19a",
      "parent_id": "726b033b2e820a48ce892f78",
      "path": ".tickets/DAEO-stdl.md",
      "start_line": 42,
      "end_line": 55
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
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "51e9db91eb825349851483e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/COMPETITIVE-ANALYSIS.md",
      "chunk_id": "fb5a6746efd7045a065866fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "f41392d732ce3b15b18dcf74",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "bf90d134baa5e218fe3fa24e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-03.a.md",
      "chunk_id": "980abf64a2bb727064caf6c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "474b1641de3828ba8421c479",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-3-MCP-TOOLS.md",
      "chunk_id": "cb7727ed0d47a8c1e85adf97",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "3f47abdef4b93961787ded3a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "e778deca60d009b9b72e3d24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "9e849377bba6abc40131ce9b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-03.a.md",
      "chunk_id": "424dd41fe031a8b82712eece",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/stages.py",
      "chunk_id": "3db945088a6c78562b38a66e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/secrets/__init__.py",
      "chunk_id": "26bbc19b6e30ed3f34a062e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-58-CIT-E.md",
      "chunk_id": "7535908f4a2440747b622ae6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-42.md",
      "chunk_id": "f72bd5bb13e626802c464cf5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "575bcb12c36720380212dbe0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/STUDY-startup-launchpad.md",
      "chunk_id": "559b74e0071809d76d90de88",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-44.f.md",
      "chunk_id": "263b7c5e20a061ccf7d68c5d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "e1a69211380827d837dbd2ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "cb3c9544d48c7070cabf9ccf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-12.b.md",
      "chunk_id": "1326e595594d055f9fdcfdd0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/secrets/__init__.py",
      "chunk_id": "16ab68a4cf84634025e9c369",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/secrets/__init__.py",
      "chunk_id": "450cb179b868b42f858ad3c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/stages.py",
      "chunk_id": "10e543849f4e69479bb21616",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/discover/draft.py",
      "chunk_id": "99d47590a2b081d26b24bda4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "ff61af2f8c9fabff17ff44aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "b438b45f4bb2dd0948f1282f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/lite_gates.py",
      "chunk_id": "5305158a9c1a86cd2d1be3b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.md",
      "chunk_id": "f17af825cc490dec236791c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/secrets/__init__.py",
      "chunk_id": "3a324e486f03a7f12d90ceae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-44.f.md",
      "chunk_id": "1d2436ea6bbeeccfd11e6c78",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/learning.py",
      "chunk_id": "55e0f18eac299f84b21d77ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "b7763a3232a979a4d54eacfc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/gate.py",
      "chunk_id": "fa6311c51007d370d6a2ca3d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/learning.py",
      "chunk_id": "9f159a2d8e35e4c2f5f85b39",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-42.c.md",
      "chunk_id": "d1dcc48e59896f405bafeef4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "e1a67a6ca79f058d900f19dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-03.c.md",
      "chunk_id": "7579c88c560e1973866b7943",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "4d68aa2ffb4555970d4ff8e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "88556a078a33b2c582cac82b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "d4370aa077d1fedb7c337aa3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/STUDY-startup-launchpad.md",
      "chunk_id": "a8478946dfe09edc88781c19",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/fabric.py",
      "chunk_id": "eb7326e795d5d18feb6d8ad1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-48.b.md",
      "chunk_id": "4d8c389cc2d12cc9801146c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-42.c.md",
      "chunk_id": "f332089b972af8857bb9826f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "05d7e07435c9102b984c7ce4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/gate.py",
      "chunk_id": "fdbbceaa87d98f6932e8dfbb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "chunk_id": "1fe2501a7c99e8ae6bfbc19e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-12.b.md",
      "chunk_id": "cce9894064809a0660b6aee2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/adopter-brief-rerun.md",
      "chunk_id": "0357168bdcbd97f5b208e29f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/plan/derive.py",
      "chunk_id": "e95ac36effae7e96fc694cbb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "6f25fea6c1c67cc2945cbe80",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.md",
      "chunk_id": "0a155a951b64728f7ddd2713",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/discover/draft.py",
      "chunk_id": "28d8d3ba779be230a39d14d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-44.h.md",
      "chunk_id": "7794df99b3112e12c2bcfa42",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "c456977cbc79e93f2c51e497",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/GLOSSARY-1.md",
      "chunk_id": "06c78e53bcc7cf0b9c349e18",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/fabric.py",
      "chunk_id": "c73127f83657e35ce3027270",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/fabric.py",
      "chunk_id": "fa38a72476b21b785a72eea6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r3gx.md",
      "chunk_id": "af6a5ffff7db5632f2db5ad1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/stages.py",
      "chunk_id": "f089e569f4f27da2b6f06ddd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "a236647fed60fac900928d17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/report.json",
      "chunk_id": "912fa400d2ecc8cf026b4ad8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "55d73c65864bf72120d55141",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/gate.py",
      "chunk_id": "9f32f2af06cfaaf2964538a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "f3362c8d0f216a62944f0db9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "ab395a1af19931083ff89906",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-bundle-a-reds.md",
      "chunk_id": "1926c8de0bcdee3bae32e8c4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "a6319e47b1c101163f2195cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "0a5f2b0c7d67dab65765615e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/discover/command.py",
      "chunk_id": "a4945274ee3a662ae32d03da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "9d8ec5f60d4af837e77f6a0d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "39d58bfe7c68555ecb03a5f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/05-repository.md",
      "chunk_id": "f3273cbf109b8c82a5715122",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "ed0dcef6a842c281422419e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-doubtful-settled.md",
      "chunk_id": "2288cae72c544c0f658a1e8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/slots.py",
      "chunk_id": "02c74a14b219b5ef218bc29d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "f03f7c15b13962b00ab75c8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/plan_check.py",
      "chunk_id": "acf0a271caf057eccbe5314c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "29426fff56a18df71a3c3e5e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "dd3185f8e5a639763b34da89",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/measure.py",
      "chunk_id": "4d2fb6da9bedbb893fb3095d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/measure.py",
      "chunk_id": "cd67a86cbfcb1d5af929137d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "5cf09fc94e8bdfc056c44a75",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-26.html",
      "chunk_id": "03e8c53af0059f893eec8656",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/decisions/backfill.py",
      "chunk_id": "223fae5d10acb6156b618376",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/gate.py",
      "chunk_id": "1dac557de5b482ca63a1b846",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "6a0bfd5baa162d6d048b56e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/slots.py",
      "chunk_id": "5d900d22f24ff753e11cc2fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "96d42720527130a92d4cabfb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "39e24a2851d345352a2f4e06",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-88-evidence.md",
      "chunk_id": "075769ffec5e7f2cd4ea774b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/secrets/__init__.py",
      "chunk_id": "9f9c90f3e32f9d5d44798b60",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "b85df37c3955982f950a20cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2bdu.md",
      "chunk_id": "268996c9fe4366d896d4d589",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/secrets/__init__.py",
      "chunk_id": "8232e3f01f2714335dd0b079",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/machine.py",
      "chunk_id": "4f891faa1665d782501864a4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/plan/tickets.py",
      "chunk_id": "5d12df073e68618347c2e729",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "ef89c80fe218b716458d4fe4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "1416679f9d2d5fb9ccd63c9a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "9c2e160da4e91ba16c5dbe68",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "e7e6c982188ef86a43f92cb6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/learning.py",
      "chunk_id": "cd296517ae3f324d0561c554",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "cb39fabcee0f7d23df5e54c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cdoi.md",
      "chunk_id": "f7ff994640c049ae1589fec8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/discover/command.py",
      "chunk_id": "5533f400fdfbbaf7130f030c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "56d8471d36d3a557c3fbbecf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "3ffe2b35333b186f0384eb44",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "69d91cbcccebbd4073062bd3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "139104139d1878bf9c86c669",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/config.py",
      "chunk_id": "43c9ac4708e9b62a8c0d0968",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/util/gitenv.py",
      "chunk_id": "9efe181062db56229ff6e5f2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/plan_check.py",
      "chunk_id": "553f970e235a93a05a97ec1a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cdoi.md",
      "chunk_id": "286673dd057276f6f11f4ef1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/discover/command.py",
      "chunk_id": "acf6d3fa28c3922ac09aa044",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.md",
      "chunk_id": "6af9ccd4db181826de4a6aac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/machine.py",
      "chunk_id": "7cb4dff20328a1f6bc274250",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "2a94f18c101cf16b883c48ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/gate.py",
      "chunk_id": "0b3d36114c0c9b94b8ea988b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/path-map.yaml",
      "chunk_id": "4f09faf7a4dc8f9903dc27d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/resources/slots.py",
      "chunk_id": "1d9eb3082eb12ac6943cd018",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "d4bb01d3a85a02887158ae9d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "1893f2a625ba528586f2c403",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md",
      "chunk_id": "8020c93065f20c339a5911f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5j8b.md",
      "chunk_id": "38cfc4ceeb86c249a6c41191",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r3gx.md",
      "chunk_id": "4640ecc660432769acc96bdc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/README.md",
      "chunk_id": "866b52f2bbc49ed364436b17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/fabric.py",
      "chunk_id": "d4524df13557a0ca1f21acbf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/05-repository.md",
      "chunk_id": "0261d733fb706e0b5a0e477d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-bundle-a-reds.md",
      "chunk_id": "6b0e4aa7d09fd6099b7256c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/IMPORTS-ADOPTION-SPEC.md",
      "chunk_id": "75462c3e3f43764e399ab6f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-register-exit.md",
      "chunk_id": "c8d529bdaf798d1adf67ba68",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "20d83527e47c5047f48545df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/path-map.yaml",
      "chunk_id": "c7854a7cc4e1a9fc743524e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "21dee69b4e66539445db2771",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "7efe5045ab828858001a6525",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/README.md",
      "chunk_id": "c3d9ec62fda2374ce7e431f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/w2_204_support.py",
      "chunk_id": "a864f9d42d9668e719e9dadf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/README.md",
      "chunk_id": "bd9e3bf4724c71241159c7f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/w2_81_judge.py",
      "chunk_id": "9ea18371ca89c1ed5c493081",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/w2_81_judge.py",
      "chunk_id": "be3c684b896f6eba30fd89fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/README.md",
      "chunk_id": "7ae8b1d61d9df85ed4e05192",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/README.md",
      "chunk_id": "252761b26f8fb60eac376379",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/w2_81_judge.py",
      "chunk_id": "c8f6a715df4ade7bcd25005f",
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
      "used": 5947
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLWQzc3IubWQiLDQyLDQ0LCJjZTI2YzY3NGI2MDZkMWJlZjkxYWVmYjciXSxbIi50aWNrZXRzL0RBRU8tZDNzci5tZCIsNDMsNTQsImIwNDFmZWZiOTFmMmU4YTVkZTAwMDcwNCJdLFsiLnRpY2tldHMvREFFTy1kM3NyLm1kIiw1OSw2MiwiMmM1NDk5M2RjYTY1Y2NhZDA4NTc1OWRjIl0sWyJkb2NzL0RFQ0lTSU9OX1JFR0lTVEVSLm1kIiwyMDQ1LDIwNDUsIjU5OGI5YWQ0Y2U3NzkxN2EwYWY5MTk0MyJdLFsiZG9jcy9ERUNJU0lPTl9SRUdJU1RFUi5tZCIsMjMzMCwyMzMwLCJiNDdmYjAzYzgzODJkOWVkOWJkMTQyMzAiXSxbImRvY3MvREVDSVNJT05fUkVHSVNURVIubWQiLDIzMzEsMjMzMSwiYWUzNzg1ZDJkZjdiYjM2YjEzZWE0YThkIl0sWyJkb2NzL2NvbnRyYWN0L2NvbnRyYWN0LnlhbWwiLDQ1OSw0ODcsIjA5ZGU0ZTU1ZWRhN2Q1MjA0Zjc3ZDgzMiJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9HT0xERU4tV09SS0ZMT1cubWQiLDEyMCwxMjAsImIxYWU2M2E0NzU3YWMxZTcxMGUyOTRkNyJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9icmllZnMvTEVBRC1idW5kbGUtYS1yZWRzLm1kIiwxNywyMSwiYmZiNmM1MDM4N2UzYTc5M2E1ZmJlNDgxIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2JyaWVmcy9MRUFELWJ1bmRsZS1hLXJlZHMubWQiLDIyLDMwLCJiZWRlMzBkYWNiYTQzZmZiMDQzNTNjZjgiXSxbImRvY3MvZW1lcmdlbmN5LTIvYnJpZWZzL0xFQUQtYnVuZGxlLWEtcmVkcy5tZCIsMTg5LDE4OSwiYzk3NjQyZGVlMmJlNzVjNjE5OGQ5NjA0Il0sWyJkb2NzL2VtZXJnZW5jeS0yL2JyaWVmcy9MRUFELWQzLXN0YWxlLXJvdXRlLm1kIiwxMSwxNiwiMzdiMDA2NTI4MjY0ODRmZDQ1YmYyM2E3Il0sWyJkb2NzL2VtZXJnZW5jeS0yL2JyaWVmcy9TVFVEWS1zdGFydHVwLWxhdW5jaHBhZC5tZCIsMzYsMzksIjllYjJjNDg5OWE1ZmUwYTJhNzk3OTMyMyJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9wcm9wb3NhbHMvSU1QT1JUUy1BRE9QVElPTi1TUEVDLm1kIiwxNSwxNywiNmNkMGE2ZDZjMzNjZWZhMTk1MzRjNTYwIl0sWyJkb2NzL2VtZXJnZW5jeS0yL3Byb3Bvc2Fscy9JTVBPUlRTLUFET1BUSU9OLVNQRUMubWQiLDE3LDE4LCIzZTRlOWI5Y2RlODgzYjQ1MTdiZDNjZmMiXSxbImRvY3MvZW1lcmdlbmN5LTIvcHJvcG9zYWxzL0lNUE9SVFMtQURPUFRJT04tU1BFQy5tZCIsNTgsNTksImQ5OTcwM2Q5MTE3ZDZlNDJiMzY3YTJmMyJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vcGFja2FnZXMvTUVNT1JZLVNQRUMtTUFQLm1kIiw1Nyw1NywiZDQ3NDM3NTJhZjFjNGZlYTdmZWU5OGUzIl1dLCJmIjoiL2hvbWUvdXNhaW4vZ292LW9zLXdvcmt0cmVlcy9XMi0wMC1zdG9yZS1iIiwiaSI6W10sIm8iOjIwLCJwIjp7ImIiOiJzZXJ2aWNlIiwiZCI6ImN1ZGE6MCIsImgiOiI2ODYzY2MxZDYwYzVkMTkyIiwibyI6WzIsMzMsNywxMiwyMSwyNSwyNiw4LDQsMzAsMywxNywwLDE4LDMxLDEwLDYsMjQsMjcsMjksOSwxNCwxNSwxLDE2LDExLDUsMTksMjAsMTMsMjIsMzUsMzYsMzIsMjgsMzQsMjMsMzksMzcsMzhdfSwicSI6ImNsYXNzaWZ5aW5nIHJlcG9zaXRvcnkgbWF0ZXJpYWw6IG5hbWVzcGFjZXMgYW5kIGNsYXNzZXMgaW4gdGhlIHBhdGggbWFwLCBzdGFsZSBsZWdhY3kgYXJjaGl2ZSwgaW1wb3J0cyBjbGFzc2VkIHVzZSBhYnNvcmIgc3R1ZHksIFJFQSByZWNvbnN0cnVjdGVkIGNvZGUgbGljZW5jZSwgaGlkZGVuIGV2YWx1YXRpb24gc2V0cyBvdXRzaWRlIHRoZSBpbmRleCwgc2VjcmV0cywgYWRvcHRpb24gQTMgQTYgbW92ZXMsIG1lbW9yeSBwb2xpY2llcyBpbmRleGVkIGVtYmVkZGVkIiwiciI6MCwicyI6ImNiYjMyMjY2ODAxN2VkM2FiN2RhMTExZmMwY2Q4ZTIxMDZiNjA5MDUiLCJ0IjpudWxsLCJ4IjpbIjU1YmFiOWQxNzBjYTQ3ZTViOTc0M2M4YyIsIjcyNmIwMzNiMmU4MjBhNDhjZTg5MmY3OCIsImQ0MGMxMWE0NzlkNjU0M2E2ZThhMWVlZCJdfQ==",
  "routing": {
    "code": [],
    "named": [],
    "phrasings": [
      "classifying repository material: namespaces and classes in the path map, stale legacy archive, imports classed use absorb study, REA reconstructed code licence, hidden evaluation sets outside the index, secrets, adoption A3 A6 moves, memory policies indexed embedded",
      "classifying repository material namespaces classes path map stale legacy archive imports classed use absorb study REA reconstructed code licence hidden evaluation sets outside index secrets adoption A3 A6 moves memory policies indexed embedded"
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
        "chunk_id": "ce26c674b606d1bef91aefb7",
        "path": ".tickets/DAEO-d3sr.md",
        "start_line": 42,
        "end_line": 44
      },
      {
        "chunk_id": "b041fefb91f2e8a5de000704",
        "path": ".tickets/DAEO-d3sr.md",
        "start_line": 43,
        "end_line": 54
      }
    ]
  }
}
