# Lead brief: integration plan item 1-8, `gov impact` bounded (I-5; a fix under W2-37, DAEO-6n5k)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-26. **Read `docs/emergency-2/briefs/LEAD-COMMON.md`
first: every rule there applies.** Decide, never ask (I-10). Use `systematic-debugging`. Every `gov retrieve` you or a helper runs
takes `--root /home/usain/gov-os-worktrees/W2-00-store` (the main tree's own store is stale).

## Why
X-1 (DEC-1244): the landing's selection is made trustworthy first, in the order 1-0 (landed), 1-11, 1-8, then 1-9 (`gov impact` at the
landing). FINDINGS I-5: `gov impact` ran past 150 s on one decision id, the suspected cause being the code index daemon waited on for a
record-only id (`src/gov/impact/__init__.py:135-150`, `:283`). Read row 1-8 (and 1-9, which builds on it) of
`docs/emergency-2/integration/INTEGRATION-PLAN.md` and FINDINGS I-5.

## What (K-lines as a `## Fix:` section in `.tickets/DAEO-6n5k.md`; the CTO approves them by this brief)
- **IM-1** `_Code` (the code graph) is built lazily: a record-only id (a decision, a spec, a ticket) never starts, asks or waits on the
  code index. Verify: `gov impact DEC-1204` finishes in under 30 s with the code index stopped, prints the five groups
  (specifications, decisions, tickets, tests, code), the code group reported as not loaded, and `complete: false`.
- **IM-2** An id that does need code (a source path) still loads the graph; with the index stopped it says so by name and exits
  non-zero, never hangs. Verify: a planted source path with the index stopped ends within 30 s naming the index.
- Confirm I-5's cause first (file:line), with a timing before and after on this repository.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-1-8-impact`, branch `e2/1-8-impact` from `w2/integrate`. Code area: `src/gov/impact/`,
`tests/unit/impact/`, `tests/acceptance/W2-37/` (the independent test designer only), `.tickets/DAEO-6n5k.md`. Another lead works on
`src/gov/queue/` and the path map check meanwhile; `e2/bundle-a` and `e2/bundle-b` are held: do not edit their files.

## Green
IM-1 and IM-2 red on the base, green after; `gov accept W2-37` green; then exactly the impact-selected suites
(`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-6n5k=e2/1-8-impact --onto w2/integrate --select`) through the heavy
slot. Check the trailers (LEAD-COMMON).

## Return
Branch and head; I-5's cause (file:line) and the timings before and after; IM-1 and IM-2 with tests and result; the selected run's
summary; your retrieves (count, queries, records used).

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
store: c8ce78a15dfb (/home/usain/gov-os-worktrees/W2-00-store-b)
{
  "store": {
    "commit": "c8ce78a15dfb86d0d8a321c73351a8de03efc77e",
    "head": "c8ce78a15dfb86d0d8a321c73351a8de03efc77e",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-b"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "6e5c3df04ce47873c9b0d5ce",
      "sha256": "6791451198b21886fc6759ccec8e307554cb2a7daf14c200200350beae0fffd7",
      "path": "src/gov/impact/__init__.py",
      "start_line": 133,
      "end_line": 137,
      "text": "\n\nclass _Code:\n    \"\"\"The code graph of the code index, read once if it was built; ``usable`` when it was read, even stale.\"\"\"\n\n",
      "chunk_id": "6e5c3df04ce47873c9b0d5ce",
      "routes": [
        "lexical",
        "code"
      ],
      "batch": 1
    },
    {
      "id": "aebc349d7fdd426ceb0172b1",
      "sha256": "ef78c12e494d58b6fe9da0768bdb645d6e5ab551b7cf207ff04f69470d128caa",
      "path": "src/gov/impact/__init__.py",
      "start_line": 138,
      "end_line": 151,
      "text": "    def __init__(self, root: Path):\n        from gov import codeintel\n\n        self.root, self.dead, self.paths = root, Counter(), {}\n        staged = codeintel.home(root).parent / \"files\"\n        if not staged.is_dir():\n            self.state = \"missing: no code index was built here; gov impact never builds it\"\n            return\n        try:\n            self.dead = Counter(entry[\"name\"] for entry in codeintel.dead_code(root))\n        except (RuntimeError, OSError, LookupError, ValueError, TypeError) as error:\n            self.state = f\"unavailable: the code index cannot be read ({error})\"\n            return\n        self.state = _staleness(root, staged) or OK\n",
      "chunk_id": "aebc349d7fdd426ceb0172b1",
      "routes": [
        "code"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-6n5k",
      "sha256": "060145574a70f75b35fbf1433421f97000c967f70f7bc9f1da044e2a1b45af3b",
      "path": ".tickets/DAEO-6n5k.md",
      "start_line": 62,
      "end_line": 71,
      "text": "# W2-37 gov impact\n\nCard: `docs/plan/WAVE_2_WBS.md` \u00a72 (W2-37), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).\n\n- **Allowed paths:** `src/gov/impact/**` (new), `src/gov/closure/**` (read API only), `tests/unit/impact/**`.\n- **KPIs:**\n  - A decision change raises a CIT-P that lists the affected specifications, decisions, tickets, tests and code from both graphs, with a radius [CAP-33.b, W2-M285].\n  - After apply or archive, the CIT-E record matches the proposal or lists the differences [W2-L319].\n  - \"What's the impact of X?\" in plain language runs `gov impact` [CAP-33.g, DEC-167].\n  - It also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join).\n",
      "chunk_id": "9758bde9084cf6e8411e5837",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-6n5k",
      "sha256": "6206cf3d18a0427eec1092ce6e4c906e137adfe4e2360a7ee495ca1ae266ddc0",
      "path": ".tickets/DAEO-6n5k.md",
      "start_line": 1,
      "end_line": 61,
      "text": "---\nid: DAEO-6n5k\nstatus: closed\ndeps: [DAEO-g0ip, DAEO-ym8a]\nlinks: []\ncreated: 2026-10-16T16:35:11Z\ntype: task\npriority: 2\nassignee: engineer\nexternal-ref: W2-37\ntags: [wave-2, implementation, full]\nwbs_id: W2-37\ntitle: gov impact\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-g0ip\n- DAEO-ym8a\nallowed_paths:\n- src/gov/impact/**\n- src/gov/closure/**\n- tests/unit/impact/**\n- template/governance/kernel/skills/change/SKILL.md\n- template/.rulesync/skills/change/SKILL.md\n- src/gov/check/commands.py  # P-7 (a), DEC-812 item 6: the RECORDED_GOV_COMMANDS line records `impact` only\n- tests/acceptance/W1-07/w1_07_support.py  # P-7 (a): W1-07's lists gain `impact`, by a test designer with a Rewrite-Reason\n- tests/acceptance/W1-07/test_w1_07_recorded_commands.py  # the same (its count test renamed)\n- tests/acceptance/W1-07/README.md  # the same\n- tests/acceptance/W1-32/test_w1_32_command_set.py  # P-7 (a): W1-32's command-set assertion gains `impact`\n- tests/conftest.py  # _CBM_SUITES gains W2-37 (its code-graph cases run with the tool on PATH), CTO, DEC-1156 (7)\nkpis:\n  success:\n  - '\"What''s the impact of X?\" in plain language runs gov impact [CAP-33.g, DEC-167]. Verify: a planted question \"what is the impact of DEC-NNN?\" given to the plain-language entry runs gov impact on DEC-NNN and prints its result [Verify clause added, DEC-1157 (12)]'\n  - 'It also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join). Verify: planted records with mapped ids and a deletable-class row: gov impact resolves the mapped ids (G-16) and joins the deletable class (G-24) in its result; G-24''s \"no record names the item\" counts the store''s stated links too (a ticket''s sources and closes, the register''s Under and Changes lines): a planted decision named only by a ticket''s sources is not deletable [Verify clause added, DEC-1157 (12); F1 (a), DEC-1163]'\n  failure: []\n  lifted:\n  - 'A decision change raises a CIT-P that lists the affected specifications, decisions, tickets, tests and code from both graphs, with a radius [CAP-33.b, W2-M285]. [lifted (was S1), DEC-1083: the query only, no CIT-P (INVESTIGATION-1 \u00a75, W-3)]'\n  - 'After apply or archive, the CIT-E record matches the proposal or lists the differences [W2-L319]. [lifted (was S2), DEC-1083: the query only, no CIT-P (INVESTIGATION-1 \u00a75, W-3)]'\nprofile: FULL\nsources:\n- CAP-33.b\n- CAP-33.g\n- DEC-167\n- DEC-1083\nest_loc: 280\nacceptance_tests:\n  path: tests/acceptance/W2-37/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: C\ncloses:\n- CAP-33.b\n- CAP-33.g\n- DEC-167\nlist_rows:\n- W2-L319\n- W2-M056\n- W2-M150\n- W2-M285\n- W2-M320\n---\n",
      "chunk_id": "f8c807c9ab4e4bf4292bb412",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "f1cd1e58020b6502d968e8c5",
      "sha256": "86a1402b80c8e485d993583a886557ab31781bc7499ea26df028318f969b773c",
      "path": "docs/emergency-2/briefs/RESEARCH-step1-tool-map.md",
      "start_line": 23,
      "end_line": 41,
      "text": "## Restart notes (the CTO, 17:05): the first run wrote neither file\n- **Decide, never ask:** you are a `claude -p` session; a question in your final message is never answered. Where a\n  choice is yours, make it and say so in the file. Write `TOOL-MAP.md` first from what you can verify, then the\n  corrections; a section you could not verify says so with what is missing, rather than stopping.\n- **Helpers:** at most four, each with one narrow area (for example: `src/gov` commands and their callers; hooks,\n  settings, lefthook and cron; the scratch and orchestration tools; the kit), each returning rows as plain text (no\n  instructions to you, no code blocks of settings), never whole files. If a helper stops early, do that area yourself\n  by listing and grepping.\n- **Already found for W6 (keep, verify cheaply, do not re-time):** `gov impact` (`src/gov/impact/__init__.py:283`) exists\n  but nothing calls it; `gov impact DEC-1204` ran over 106 s and hit a 150 s timeout (suspected: `_Code.__init__` at\n  `:135-150` waits on the code-index daemon even for a record-only id); nothing compares a ticket's `[Kn]` lines with\n  its spec's K-lines; no test-to-ticket trace; the landing's selection traces code to tests only. Smallest fixes\n  proposed: `_Code` lazy; `gov impact --changed <range>` as a trigger at the landing; a `KPI_DRIFT` finding in\n  `links/check.py`; the back-trace by inverting `accept.runner.parse_map`. Do not write to `/tmp` outside your own\n  scratch folder.\n- **Known since the audits (count them in):** Gov OS made its first `gov queue` landings today (`4f779086f` L2-4); the\n  queue then refused two landings on a target named only in a README map row's notes (`FILE_GONE`, a selection bug to\n  list in the map's gaps under W2-115b); `models-rubric` landed by hand merge (`f6e9e38af`).\n\n",
      "chunk_id": "f1cd1e58020b6502d968e8c5",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "5a02365313eb162e4452c432",
      "sha256": "5f8593cbb99e184f63d672f98c82a8ef7eb2659795b419b5d0e4734ff4636c83",
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "start_line": 214,
      "end_line": 241,
      "text": "## 4. W6, the trace question, answered from the code\n\n**Answer: partly.** Code exists that traces a change in a decision or a spec to the specs, decisions, tickets, tests and code it affects, over the record graph and the code graph, but nothing calls it. What runs by code is the landing's selection from changed paths to tests, which traces code to tests only.\n\n**What exists for each link:**\n\n| Link | What exists (path:line) | Used by code today? |\n|---|---|---|\n| decision \u2192 spec | the record graph: `store/loader.py:49` `EDGE_TYPES` (CONSTRAINS, IMPLEMENTS, EVIDENCE_FOR, SUPERSEDES, \u2026) and the register's stated links (`:95-105`: UNDER, AMENDS, SUPERSEDES, CITES); `retrieval/graph_route.py`, `reverse_edges.py`; walked by `gov impact` (`impact/__init__.py:283` `assess`, `_walk`, `_grouped` into the five kinds specifications, decisions, tickets, tests, code, `readings.py:18`) and by `gov closure` | `gov impact` and `gov closure`: typed only; `retrieve` walks the graph only when the question names an id |\n| spec \u2192 ticket | a ticket's `sources`/`links` front matter, read as edges and stated links (`impact/__init__.py:79`); `gov links` finds a `[DEC-n]` in a KPI line that is not in `sources` (`links/check.py:556-575` `UNLINKED_ID`); `gov plan` orders tickets by dependency and writes (`plan/derive.py:205`), not by spec; `gov discover` makes tickets from a spec (`discover/tickets.py:107`) | `gov links` runs automatically only inside the queue's after-step (`queue/after.py`); the rest typed |\n| spec K-lines \u2194 ticket `[Kn]` lines | **nothing.** `check_spec.py` parses a spec's K-lines and is called only by `gov discover` and adoption's `fabric.py`; `gov brief`'s ready check reads the ticket's `kpis` alone (`brief/build.py:157-186`); `links/check.py:158` reads the ticket's KPI lines for bracketed ids only | no |\n| ticket \u2192 test | `tests/acceptance/<ID>/README.md` mapped to KPI lines by `accept/runner.py:139` `parse_map` (forward: line \u2192 tests); `gov impact` types a record as a test when a `TESTS` edge names it (`readings.py:24-27`) | `gov accept` at the land (`queue/acceptance.py`); no inverse (test \u2192 ticket \u2192 spec) |\n| code \u2192 test | the path map, each ticket's `allowed_paths`, the test map, imports; `close/select.py` (`scoped` `:742`; docstring `:1-14`); the code graph's callers and callees (`codeintel`, used by `gov impact` for a symbol) | `select.scoped` runs automatically at `gov queue` (`queue/command.py:515-525`) and, for hand commits on `w2/integrate`, through `landing_select.sh` (reference-transaction line 16) |\n\n**Modules, as the brief asked:** the graph is `src/gov/store/loader.py` plus `src/gov/retrieval/graph_route.py` and `reverse_edges.py` (there is no `src/gov/graph*`); `check/links` is `src/gov/links/check.py` (1,049 lines, integrity of ids and statuses, no spec-to-ticket comparison); `select` is `src/gov/close/select.py`, called by `queue/command.py`; `gov plan` is `src/gov/plan/` (dependencies and paths, not impact); `gov discover` is `src/gov/discover/` (spec \u2192 tickets, one direction, at creation).\n\n**Findings that are the CTO's own, checked cheaply:** `gov impact` has no caller in `src/`, `template/`, `.claude/`, `lefthook.yml`, `governance/`, or the scratch tools (the only text is `skills/change/SKILL.md:48-52`); `gov impact DEC-1204` over 106 s and a 150 s timeout is the CTO's measurement and `_Code.__init__` (`:135-150`) is the suspected cause (I read the code; the `codeintel.dead_code(root)` call at `:145` runs for every id, record or symbol, which fits a wait on the code index; I did not re-time).\n\n**The smallest code that would close the gap (four changes, each small):**\n1. **`_Code` lazy** (`impact/__init__.py:135-150`): build the code graph only when an id is not a record or a symbol is asked; a record-only id never touches the code index. A fix under W2-37 (DAEO-6n5k, closed); the failing test first: `gov impact DEC-1204` finishes in a bounded time without a code index. About 15 lines.\n2. **`gov impact --changed <range>` as the trigger at the landing:** for each record file in the range (a decision entry, a spec, a ticket) run `assess` and print the affected tickets and tests; the queue's after-step (`queue/after.py`) calls it and writes the list into the close record. About 40 lines; a fix under W2-115b/W2-37.\n3. **A `KPI_DRIFT` finding in `links/check.py`:** for each ticket with a `spec`/`sources` link to a specification, compare its `[Kn]` KPI lines with the spec's K-lines as `check_spec.py` parses them; report a missing or changed line. About 40 lines; also the brief's ready check (A-23b), a fix under W2-129 (links) and W2-152 (brief).\n4. **The back-trace:** invert `accept.runner.parse_map` over `tests/acceptance/*/README.md` into `{test: (ticket, KPI line)}`, and give `gov impact` a test \u2192 ticket edge, so a changed test names its ticket and spec. About 30 lines; a fix under W2-96 (accept).\n\nThese four make the trace one thing, used by planning (`gov plan`, `gov discover` can read the same affected list) and by the landing, as the draft's \"Must be\" says; they are a spec question for the owner only on one point, the trigger (SQ-11 in the corrections file).\n\n---\n\n",
      "chunk_id": "5a02365313eb162e4452c432",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "d4bf816a50116a6d8e7b240b",
      "sha256": "8a3f7d3b5a9409d49218596622713d37b3ffe88734c130258a6fe4811bc004bb",
      "path": "governance/project/orchestration/packages/P-W2-50.md",
      "start_line": 30,
      "end_line": 32,
      "text": "## 6. What it blocks, and what waiting costs\n- It gates W2-37 (the code graph's cap) and W2-15a's baseline (a fair measure), and it costs every rebuild about 15 minutes. The record grows with every checkpoint.\n- Nothing stops meanwhile: W2-62, W2-59 and W2-50's resume run.\n",
      "chunk_id": "d4bf816a50116a6d8e7b240b",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "4583e83f52865fa54eeeb473",
      "sha256": "ce99fe2c734ec6329976133219d7ada7bfcc21d6b1181aa23551af105550af22",
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "start_line": 70,
      "end_line": 71,
      "text": "| 1-8 | **`gov impact` bounded.** `_Code` is built lazily, so a record-only id never touches the code index. [I-5; T-11; X-1; TOOL-MAP \u00a74 fix 1; map row 22] | W2-37 (DAEO-6n5k; closed, a fix under it) | fix S | 1-0 | W6 | `gov impact DEC-1204` finishes in under 30 s with the code index stopped and prints the five groups (specifications, decisions, tickets, tests, code), the code graph reported as not loaded and the report `complete: false`. |\n| 1-9 | **The impact trace at the landing, and a close record that holds what happened.** The after-step runs `gov impact --changed <range>` for each record file in the range and writes the affected tickets and tests into the close record. The close record requires `evidence` when the landing writes it. The landing's notices (path, ticket, impact) are copied into it instead of dying in `queue.json`. [T-11 (a); X-1; TOOL-MAP \u00a74 fix 2; records fix 16, hand-off 21] | W2-206 (DAEO-l2b2); W2-115b | fix M | 1-8 | W6, W11 | Land a planted change to a decision and to a spec: the close record names the tickets and tests each affects, holds the run's notices and `evidence`. A close record with no `evidence` fails its schema. |\n",
      "chunk_id": "4583e83f52865fa54eeeb473",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "002970d9f4c147084934b0e8",
      "sha256": "314ccff0ea15691c9d7b71eb17f360d8f93d6354297d8ce2848aea76b7c518e5",
      "path": "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "start_line": 264,
      "end_line": 273,
      "text": "      \"text\": \"  but nothing calls it; `gov impact DEC-1204` ran over 106 s and hit a 150 s timeout (suspected: `_Code.__init__` at\\n  `:135-150` waits on the code-index daemon even for a record-only id); nothing compares a ticket's `[Kn]` lines with\\n  its spec's K-lines; no test-to-ticket trace; the landing's selection traces code to tests only. Smallest fixes\\n  proposed: `_Code` lazy; `gov impact --changed <range>` as a trigger at the landing; a `KPI_DRIFT` finding in\\n  `links/check.py`; the back-trace by inverting `accept.runner.parse_map`. Do not write to `/tmp` outside your own\\n  scratch folder.\\n- **Known since the audits (count them in):** Gov OS made its first `gov queue` landings today (`4f779086f` L2-4); the\\n  queue then refused two landings on a target named only in a README map row's notes (`FILE_GONE`, a selection bug to\\n  list in the map's gaps under W2-115b); `models-rubric` landed by hand merge (`f6e9e38af`).\\n\\n\",\n      \"chunk_id\": \"f1cd1e58020b6502d968e8c5\",\n      \"routes\": [\n        \"semantic\"\n      ],\n      \"batch\": 2\n    },\n    {\n      \"id\": \"523d339a8b68f603f789b44e\",\n      \"sha256\": \"c11c718823ff05b715e1eb02b882e804c26ede02334f897c0097d1459bf470a9\",\n",
      "chunk_id": "002970d9f4c147084934b0e8",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "24be65b1b79894583ed7222d",
      "sha256": "f12ab8495e55270338378faeae4852e60fefe8bf650e043247474152241f533d",
      "path": "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "start_line": 260,
      "end_line": 265,
      "text": "      \"sha256\": \"87e302385fda1fdf40afd4a150cf3d37790b6b32319171b92bd78efe558aed8d\",\n      \"path\": \"docs/emergency-2/briefs/RESEARCH-step1-tool-map.md\",\n      \"start_line\": 32,\n      \"end_line\": 41,\n      \"text\": \"  but nothing calls it; `gov impact DEC-1204` ran over 106 s and hit a 150 s timeout (suspected: `_Code.__init__` at\\n  `:135-150` waits on the code-index daemon even for a record-only id); nothing compares a ticket's `[Kn]` lines with\\n  its spec's K-lines; no test-to-ticket trace; the landing's selection traces code to tests only. Smallest fixes\\n  proposed: `_Code` lazy; `gov impact --changed <range>` as a trigger at the landing; a `KPI_DRIFT` finding in\\n  `links/check.py`; the back-trace by inverting `accept.runner.parse_map`. Do not write to `/tmp` outside your own\\n  scratch folder.\\n- **Known since the audits (count them in):** Gov OS made its first `gov queue` landings today (`4f779086f` L2-4); the\\n  queue then refused two landings on a target named only in a README map row's notes (`FILE_GONE`, a selection bug to\\n  list in the map's gaps under W2-115b); `models-rubric` landed by hand merge (`f6e9e38af`).\\n\\n\",\n      \"chunk_id\": \"f1cd1e58020b6502d968e8c5\",\n",
      "chunk_id": "24be65b1b79894583ed7222d",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "1a7cf701c8cac1689bf21860",
      "sha256": "d0076abbfbadda07947a844bb031e30cb8fba1e583f856af4201396b02f1f768",
      "path": "governance/project/orchestration/packages/P-W2-50.md",
      "start_line": 8,
      "end_line": 16,
      "text": "## 2. What happened (measured 2026-10-19, read-only, on the main tree's stores after the pin's rebuild)\n- **The rebuild took 1,258 s** (21:27:10 to 21:48:08): lexical 396 s (the rebuild's own timing), semantic about 55 s (to `store.db`'s last write at 21:34:40), and the code graph about 808 s. Wave 1's rebuilds took 145 to 204 s.\n- **The orchestration record is indexed, contrary to DEC-819 item 4.** `store.db` (239 MB) holds 7,606 files and 56,999 chunks. Of these, **5,686 files (75 %) and 21,898 chunks (38 %) come from `governance/project/orchestration/`**: `worktrees/` 3,637 files and 9,360 chunks; `main/` 2,046 files and 12,516 chunks. About 30 MB of the 54 MB of chunk text (`lexical_fts_content`) is theirs. They have **no vectors** (the semantic route skips them), but the lexical route and the code graph carry them.\n- By file kind they are mostly raw run output: 1,484 `.txt`, 1,146 `.exit`, 721 `.json`, 372 `.err`, 219 `.log`, 173 `.load`, 128 `.rc` and 92 `.done` files, beside the Markdown briefs and checkpoints.\n- **The code graph** (`code.db`, 200 MB): 58,350 of its 86,000 nodes (67 %) and 61,147 of its 182,113 edges come from the orchestration record. The total is over the code-graph tool's 100,000-row cap that the plan cites (lens G, W2-37).\n- **The secret scans:** each of those 5,686 files costs at least two gitleaks runs in the lexical gate and three or more in the code graph's, on every rebuild, in every tree. That is most of the rebuild's 21 minutes. One lead's rebuild drove the machine's load to 32 tonight.\n- `semantic_vector` (140 MB) is the store's largest table: 21,097 of its 31,782 vectors are acceptance tests' chunks. That is expected, and not part of this package.\n- The path map could not be read to show which namespace gives the record its memory class: the guard refuses commands that read it until W2-58 (refusal 4 of today, taken).\n\n",
      "chunk_id": "1a7cf701c8cac1689bf21860",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "4a69968e2ae56ea898711759",
      "sha256": "b986582cd66c72d78684b43d4ff902ac5fd1c581487d33bd41f2026a9ae2d23f",
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "start_line": 607,
      "end_line": 626,
      "text": "### R1. Answer code questions with the code-graph tool's own traversal (F1)\n\nClassification: F1 \u2014 ordinary work: yes; consequence: other.\n\n- **Make it an entry criterion of W2-37,** the ticket that switches on `gov impact` (DEC-803): the code graph answers on this repository before `gov impact` ships.\n- **Give the fix an owner,** by an owner decision. Either:\n  - add `src/gov/codeintel/__init__.py` (the query functions) to W2-37's paths; or\n  - widen W2-56's paths, since it already holds that file for the daemon's folder.\n- **The glue:**\n  - use `trace_path` for callers, callees and impact, at DEC-815's depths, which are inside the tool's limit of 15;\n  - use `search_graph` for definitions, and for dead code with `max_degree=0`;\n  - use per-kind `query_graph` only where a whole kind is needed;\n  - never page with SKIP inside the query;\n  - pass the tool's error text through.\n- **Tests first:** a graph above 100,000 edges is answered completely or refused by name.\n- **Research first, small:**\n  - `trace_path` latency in the wrapper's session mode (CLI mode took about 4 s per call);\n  - whether `detect_changes` gives W2-37's radius.\n- **Cost:** it removes our traversal (about 60 lines) and adds a few query calls.\n\n",
      "chunk_id": "4a69968e2ae56ea898711759",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-g23i",
      "sha256": "fe2a0b8202767afb2e9ce5a4dbd6d68ad70f41b0021893167d95b15f8caf4889",
      "path": ".tickets/DAEO-g23i.md",
      "start_line": 1,
      "end_line": 50,
      "text": "---\nid: DAEO-g23i\nstatus: closed\ndeps: [DAEO-g0ip, DAEO-6n5k, DAEO-s694, DAEO-xxgp]\nlinks: []\ncreated: 2026-10-16T16:35:11Z\ntype: task\npriority: 4\nassignee: engineer\nexternal-ref: W2-38\ntags: [wave-2, implementation, full, wave-3, deferred]\nwbs_id: W2-38\ntitle: Profile from impact; impact-selected tests at close\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-g0ip\n- DAEO-6n5k\n- DAEO-s694\n- DAEO-xxgp\nallowed_paths:\n- src/gov/impact/profile*\n- src/gov/close/select*\n- tests/unit/impact/**\n- tests/unit/close/test_select*\nkpis:\n  success:\n  - An R0 change runs only the LITE checks, and an R3 change raises the FULL gate and readiness rows, with the profile computed by gov impact [CAP-53.b].\n  - A close runs the tests gov impact names, on top of W2-66's path-scoped selection (W2-48's cache was withdrawn, DEC-880). The full suite runs only in the nightly [DEC-968, DEC-983, DEC-982] [W2-H043, W2-M240, W2-M241, W2-M163].\n  failure:\n  - A change whose impact misses a test that would fail is caught by the milestone run and recorded as a learning event.\nprofile: FULL\nsources:\n- CAP-53.b\n- DEC-983\nest_loc: 150\nacceptance_tests:\n  path: tests/acceptance/W2-38/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: C\ncloses:\n- CAP-53.b\n- W2-H043\nlist_rows:\n- W2-H043\n- W2-M163\n- W2-M240\n- W2-M241\n---\n",
      "chunk_id": "051285503cdd768c5b1c6af9",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "24a4f8a79ff37bf6d7bd8feb",
      "sha256": "aac699f72c64ed917344d527328c736f3bfca60591830a3139fc7dd50047620b",
      "path": "governance/project/orchestration/packages/PKG-W2-37-CITP-1.md",
      "start_line": 1,
      "end_line": 14,
      "text": "# PKG-W2-37-CITP-1: approve the change skill's impact-section bytes (W2-37, DAEO-6n5k; owner's item; short form)\n\n**The question.** You decided W2-37's P-1 on 11-13 (DEC-1163 (7)): the change skill gains an impact section, under a\nCIT-P for your approval of those kernel bytes. The bytes are written and the CIT-P passed its independent review. Do you\napprove them, and do you keep the version number?\n\n**What changes** (`template/governance/kernel/skills/change/SKILL.md` and `template/.rulesync/skills/change/SKILL.md`,\nbyte-equal):\n- \"What is the impact of X?\" now runs `gov impact \"What is the impact of DEC-NNN?\"` or `gov impact <id or symbol>\u2026`.\n  It reports both graphs, `complete` or the gaps, what is deletable, what is affected (by kind) and the radius.\n  `--out` writes the CIT-P and `--compare` checks a CIT-E.\n- `## Tools` names `gov impact` in place of `gov closure`.\n- sha256, before \u2192 after (both files): `2af36b72\u2026dc982` \u2192 `a25b02a7c5c8090c2251b945e48b60779ce7c2de7c254ae661a1cb0715932536`.\n- The full CIT-P, with the lines verbatim: `/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/changes/W2-37-CIT-P.md`.\n",
      "chunk_id": "24a4f8a79ff37bf6d7bd8feb",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "a7e5be86ecf30a2c608159b5",
      "sha256": "01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b",
      "path": "src/gov/impact/__init__.py",
      "start_line": 156,
      "end_line": 156,
      "text": "\n",
      "chunk_id": "a7e5be86ecf30a2c608159b5",
      "routes": [
        "code"
      ],
      "batch": 2
    },
    {
      "id": "bb23be8b49f9746aae6138d7",
      "sha256": "01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b",
      "path": "src/gov/impact/__init__.py",
      "start_line": 163,
      "end_line": 163,
      "text": "\n",
      "chunk_id": "bb23be8b49f9746aae6138d7",
      "routes": [
        "code"
      ],
      "batch": 2
    },
    {
      "id": "98b0544046eda3eee5bf0c41",
      "sha256": "01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b",
      "path": "src/gov/impact/__init__.py",
      "start_line": 168,
      "end_line": 168,
      "text": "\n",
      "chunk_id": "98b0544046eda3eee5bf0c41",
      "routes": [
        "code"
      ],
      "batch": 2
    },
    {
      "id": "CAP-33.b",
      "sha256": "dc818c7c15f3cad64ba80092f0111b725c3a7eac23a3a766ea18eaf6af5e202e",
      "path": "docs/contract/capabilities/CAP-33.b.md",
      "start_line": 11,
      "end_line": 16,
      "text": "# CAP-33.b: Automatic impact simulation over record and code graphs; impact radius \u2192 profile\n\nA covers item of CAP-33 (Change-impact transactions (CIT-P simulation, CIT-E execution)). Generated from `docs/contract/contract.yaml` (Contract v5, version 5.1), which is the authority (DEC-614).\n\n- **Item:** Automatic impact simulation over record and code graphs; impact radius \u2192 profile\n- **Wave:** W2\n",
      "chunk_id": "6c5407a67d4a198311517485",
      "routes": [
        "semantic",
        "closure"
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
    "duplicates": 36,
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
      "chunk_id": "f8c807c9ab4e4bf4292bb412",
      "parent_id": "aee996aed6de8fa7e313aaf3",
      "path": ".tickets/DAEO-6n5k.md",
      "start_line": 1,
      "end_line": 61
    },
    {
      "chunk_id": "f1cd1e58020b6502d968e8c5",
      "parent_id": "6127b7f79ebda11e6b20110e",
      "path": "docs/emergency-2/briefs/RESEARCH-step1-tool-map.md",
      "start_line": 23,
      "end_line": 41
    },
    {
      "chunk_id": "5a02365313eb162e4452c432",
      "parent_id": "66e0db3610eeb26118d4ea40",
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "start_line": 214,
      "end_line": 241
    },
    {
      "chunk_id": "1a7cf701c8cac1689bf21860",
      "parent_id": "dc7ceeb697e68958822522f3",
      "path": "governance/project/orchestration/packages/P-W2-50.md",
      "start_line": 8,
      "end_line": 16
    },
    {
      "chunk_id": "4a69968e2ae56ea898711759",
      "parent_id": "34d08bd8882fc5901b71655b",
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "start_line": 607,
      "end_line": 626
    },
    {
      "chunk_id": "051285503cdd768c5b1c6af9",
      "parent_id": "1619d50a2efca857ef5760c5",
      "path": ".tickets/DAEO-g23i.md",
      "start_line": 1,
      "end_line": 50
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "id": "DAEO-057v",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-0mab",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-0mtg",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-0pyc",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-0rfi",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-0uhh",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-0z8c",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-1ahb",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2azm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2bdu",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2d6f",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2ds6",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2gc7",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2keg",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-3r1j",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-49o5",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-4k3l",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-57hm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-5j8b",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-60rw",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-6ox0",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-6y0x",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-7r5e",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-7rr2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-7y6v",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-8lmb",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-9nys",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-a3m2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-a3u2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-arrl",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-b6hm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-b926",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-btt7",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-c1uz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-csj8",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-cuao",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-cv58",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-cy5o",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-drhj",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-e82f",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-e8f0",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ebmh",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ecac",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-egsy",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-fau3",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-g87r",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-gdzh",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-h2k3",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-h4rh",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ha8z",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-iw1f",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-j8gn",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-jip3",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-jsg1",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-juee",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-jzvg",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-k7hz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-kh9l",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-kia7",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-kiar",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-kl5e",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-kmcr",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-l78m",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-lrre",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-m1u3",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-n0wb",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-neam",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-nqa2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ouet",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-pl6k",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-qty6",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-r30l",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-r9ss",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-rd0g",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-rmbe",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-s694",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-s9qc",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-sdhj",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-siiz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-swdu",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-tgk2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-u4oz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-u5g6",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-uzme",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-w19l",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wbdh",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wi46",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wnnz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wq2b",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wudw",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-xm6l",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-xxgp",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-yadm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ye2a",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-zflj",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-zndm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-zoex",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-zpdj",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-zqvn",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "path": ".tickets/DAEO-g23i.md",
      "chunk_id": "84c12793a2223e5b1a66b130",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-37-DAEO-6n5k.md",
      "chunk_id": "193102199a80279283e7967b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PKG-W2-37-CITP-1.md",
      "chunk_id": "6367222beb4996abd0b8453e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-6n5k.md",
      "chunk_id": "0bcf90c138127aa845f4f7e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-33.b.md",
      "chunk_id": "e5f5a29f8c708d662e1beb29",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-33.g.md",
      "chunk_id": "6a52f1a963a0e59215f45514",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/impact/__init__.py",
      "chunk_id": "b35cd9d6e7a4ff9351a55a4d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/impact/__init__.py",
      "chunk_id": "2f0aff058564a49b86e66684",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "eb280331e342c54ea69fce4b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/impact/__init__.py",
      "chunk_id": "251caa6f55463987555d255b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-53.b.md",
      "chunk_id": "8ddc09551210679eef6586ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-33.g.md",
      "chunk_id": "69d1c2ff2116e7d81202cbb5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PKG-W2-37-CITP-1.md",
      "chunk_id": "aa90312f814bbead3369d50a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-37-DAEO-6n5k.md",
      "chunk_id": "d0a96602e5abc7079b6df8ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "968f97f5934de02194dc567c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "2e69abb8f8e8a3b0dbde00b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "4f1f018c6002953eb0834b57",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "2ad53b6c537a997032cdee50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "cc2c3b433b257cdf642c9141",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "9496ca58565b55cb3ecd40c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "640c79cf35257a4828735ccc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-53.b.md",
      "chunk_id": "270155eae5f4563cee454a65",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "161e6457f1af8dcea089911b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/impact/__init__.py",
      "chunk_id": "08314910362614869b360590",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "3cf93315691c9d4bdd0e7ea8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "a62953bc903517b189944ac8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/impact/__init__.py",
      "chunk_id": "fcb28fb9a4de3ff9f09e1719",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "14dffded78f1168fc40cf2c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "536e34ec3c6dd2a3796f1e28",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "836cbe1d01cd28e7af287e99",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "28713fa893abc9f3954927c5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "fe6ec5820f53c29e49a3741a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-88-evidence.md",
      "chunk_id": "bd83f047e2742f75c9d0c043",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "676a6f04c3c882eefafb6cb5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "1e43d2e7b111854c387e6a05",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "e4016c4d938613556bb51187",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "36eb55155ea3cd0646d10226",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "1186aff43aa549aa1ac00fa0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "faa1104e0599cfbc6a038695",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "52e6bece0a3935872e5e266f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/impact/__init__.py",
      "chunk_id": "3b8adcb99bce862717e04a2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-50.md",
      "chunk_id": "e9f7673881a9d078ad6b4ee8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/skills/change/SKILL.md",
      "chunk_id": "5a02435b41773c8594caf5ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "97745802a6aaf49a99113bdb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "c43417eb39d4d9c0c6e7c22e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "9b33afc6dcb66af8a214cec9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g23i.md",
      "chunk_id": "f9842e111eb3cbf629c2484e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "ad4c1919fecf45dc1c3a7bcb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "0a34f0041b83035599202044",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "a0268abc9d6a8fbf1b003904",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "aa36e922ba4ef7faf3aca187",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "df79183fa6e09012273d7021",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/impact/__init__.py",
      "chunk_id": "59280be0c8af4688caa572f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "3281f8977192a3dc30366fc9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-92-memory-measure.md",
      "chunk_id": "2e56d42e0df5a2f16ba02dd6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "f561dad9222054f51cbaa770",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "63625f307137dddf7cd89f44",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "ac1061c1d3fb854294d23a4e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "64736d65f8a266cda5466db1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "9c19f9afbe96b809806292df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "8b8b2e1fc9dc6e1b6b5f107e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "eeb667c5b61b8ccc685a694a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "5b4d50380a8b9f11b90b30df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "3a38041f429aff9b858da3fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "b52fc4e54d898ef3b9f842db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "dc70d069f76f85a133aae886",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "427d15dfa10d5d30db1b2628",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-timing-tests.md",
      "chunk_id": "cb45d8061e07894df5747b20",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "228fef247583a516d63c64d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "3e8804bf0498072f3c1e9c89",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "e1ca34beaf7f7ec329ce5fd6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "11328bf034adbfe1b99d7c24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ym8a.md",
      "chunk_id": "a7f78f1e75e8a1244ff09cf0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "56e214f62350662214256d4b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ym8a.md",
      "chunk_id": "99ebea01c7a7a7f75a58e853",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "cfe84d26af4a8583a0cdaf6a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "903fdc2247822d8efab46dc2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ym8a.md",
      "chunk_id": "36ebaa4ff84945453a078e26",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "5e04a78f570dedce507f7c2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-160-evidence.md",
      "chunk_id": "eb0b46e1af2f42743416e3fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ym8a.md",
      "chunk_id": "5ff96c84ce208743a864e487",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "20a518576e05f3601865920f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rt3s.md",
      "chunk_id": "160795d84828f0e98e018e95",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "e0f1b687d4f809383ee0e097",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "55e37800ffe75d34b0b7a027",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-92-evidence.md",
      "chunk_id": "5828c9d78a2e5d086739ca50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "1c764288b3bd91b2f5198161",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "91a3f25c77f54d50dd57d712",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/impact/readings.py",
      "chunk_id": "8506c8b3274e170fdf264cf0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "69e97a04757508c92c777846",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "703a1ad004f27928702e5d64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-92-evidence.md",
      "chunk_id": "58a38828470f0f1e867db807",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "c0fc3b5fc69fb2ade071ab18",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "91a8498a504784e58197a542",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "caa286c4f62b8b938f9195ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0mab.md",
      "chunk_id": "122f93dcf757d14a572bee93",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "80c1febb01606a546afd07ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "31edd7a429b6f6ba54b3a2db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0mab.md",
      "chunk_id": "f626cb5f1cd5f8dd954b06fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "2b7c151bdb0201d1f565eb8b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "bd2da4777914ff739964e2e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "2a982878a0f92017bc0b93bd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "3a54d57a8a235442a8251db9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "8ea5458744df78f6e935ae35",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-92-memory-measure.md",
      "chunk_id": "9f36de10fd29393211f0a500",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "78c5e0c802b1bf709e1591e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-55.md",
      "chunk_id": "81bca6e4d5fb9c8af197a764",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "4b04eb6ca19ef5d1ca84ac0e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "116a448339eecbe230314cfa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "21f386a47e16752b492bead6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wnnz.md",
      "chunk_id": "9bcac5a68058b34f3fdf7b26",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "3e387e4972b0a5041247c31a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "f81fa3aae4d9cb5e343ae20c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "8c026b1448173a70beb13fc4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-92-evidence.md",
      "chunk_id": "70abd170f136b6825cf7de30",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "8d6f0ce66e42946c24a139f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-92-memory-measure.md",
      "chunk_id": "ad707370dcc45a5c1e795480",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "e9c570f4994036dba5302e64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2bdu.md",
      "chunk_id": "20f3c186d3847602d7a6f35c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "240ffa504e145b0fe43f0d81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "4162a7464ea2ec066299fbac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-92-evidence.md",
      "chunk_id": "12503246081d6af95013c086",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "da9f60b08e962f904544b72a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-146-evidence.md",
      "chunk_id": "cc5f8a15e2bb2346ec52405e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "ef2a81532de69313f84f193d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-129-links.md",
      "chunk_id": "4713c1c80f4eac702a036c35",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "6ef5b71f01b88f2d496e9fb0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "9eebb1ac1fa79d8568eedbab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "9b587032604a1c1b8aaad977",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-92-memory-measure.md",
      "chunk_id": "9dd29f7e45cb437510e0f6e1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "9a29d629a3f05278dd003892",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "0d662e8ec0ba7fb40b01d1b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "7dd20a8bdf808cac87a8ae46",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "e131de308ccec4b111576374",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-92-memory-measure.md",
      "chunk_id": "662e110f6acc0ee86d3ca7c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "478fb3634fd075c1b0844c28",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "bf2abb005636a5afc686e93c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/A2.md",
      "chunk_id": "02af9a6681d3da0c59abb420",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "3a679135f17f19e7235c9b22",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-92-evidence.md",
      "chunk_id": "5427e9629f1b495a35a976ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "e3666c791f35caeafb47490c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "5999ada519ac9f8316ac8532",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "d91c1c5c80f5cc5578f2893f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-88-evidence.md",
      "chunk_id": "0235e638317b195660475aac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wnnz.md",
      "chunk_id": "9c9e67bdd3787712b25300d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "1c40078620d3ed163ee8ac85",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "970f254deb040eb4056d95eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-129-links.md",
      "chunk_id": "056dc0cfaa3d8e5ac1df6018",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "0644ba84674b46d1c572667f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "4e598dff34f6f08af4fbef42",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "b38020320cd9ed6fb291b43b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/A1.md",
      "chunk_id": "e9855ac0c4064b9d07c958d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "ce92fa5054da2b695b025540",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "f9669249a6f7bc7ce9d9f224",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.2/manifest.json",
      "chunk_id": "ffae2e205e3c8f0812dd59b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "62c8c8169a4121391a8ce097",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "6d43f3a0f2fd18550facebd4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "f2221cfbaa2d2f707e7e2805",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-52.md",
      "chunk_id": "b402ee740151197303f710f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "0e7d9ea0668827d95a3170d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.0/manifest.json",
      "chunk_id": "0ed8402b1884f9c7c146593e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "146bc2d02146d7ffd710d639",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-gdzh.md",
      "chunk_id": "766f139dc5eb0c4b7a42696d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "52a1f30e346bae0ddbaf3383",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "d5f00cfeff6855503cacebe0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "3944318d643206ea1ccd49db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "53f770fdc09a0bb99482c776",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-88-evidence.md",
      "chunk_id": "31b2a17633d06b03f285f183",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/TRAILERS-UNPARSED-20261113.md",
      "chunk_id": "1607c103aa9e0cda62f1ddc2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "9f62b5a851c007f36b5bbf6f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-W2-60a-P5.md",
      "chunk_id": "d9cff2796f786806986ba73e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "2fbadd9563c1bf874b8a71c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "7dcf28edb1116731337b22ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "f874a5b9dc408f20fc13aa41",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "fe5eeb31e23dd2727a76b9c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-149-evidence.md",
      "chunk_id": "bfd33d39b8c351e12cd0f69a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "6db91c613f6227838d5ab326",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-2026-10-31.md",
      "chunk_id": "71ab02757e0682cea32cfffb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "f7ed2c638336fc6368001745",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVENTORY-TESTS-CODE-1.md",
      "chunk_id": "e588352ab7c447520697618b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "1f570b1d277114df6a721648",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "e6cc350bd5020c12c0033dc1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "cdc8480fdbf0a645895e2e57",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-88-evidence.md",
      "chunk_id": "4dc87e2532a9a60d076fa87f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "56d3aa7ecc3c7ff0ef7b0e5f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "67f609552dcd508dee712091",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/impact/__init__.py",
      "chunk_id": "67280e0461ef27546c7ce6c5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "7c7d479f29a7cd36df15f7c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "9a2ce33faed425d95b598db7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1/ready-batches.md",
      "chunk_id": "5b4bb7aa6b522187a3b4bc0e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "90250801a413e823275eb76c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "617787c133f6f9e1639dd4c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "66459e3dcdc3ed542116a03c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "cbf021c2a637665352f54f40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/TRAILERS-UNPARSED-20261113.md",
      "chunk_id": "93109383b0831c68068504b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "5e9fce215267357bc3e4fdc7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "dccbb6789ce6700c17ee31c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "6faf5f211b57b2c471876f10",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "506f781d705a2380cbce0738",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "22bb800159ee63b7fcad2c5d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "09f71b676a6a3ad2fd16983d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "b0c5cc1e37c88eef2386d828",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "baf64c0a74bfadf000da2cec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "ebf46d7adc939c50fb2b1e6d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "960611f33bc3d89383afe5a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "c85e6091aa7ec5e8927a25aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "2c49a32d6e17aa32d949ce19",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "2b5b5b2c532c60f83cbc7c00",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "f4ad52dece5ecaca1e6c8872",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "eb8ca7c15cbce14cbad76863",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "06b87190422f89847af1f6ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "4b7b3e9d17c5058e89031dfe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/COMPANY-MAP-2026-10-29.md",
      "chunk_id": "771a2c99e2e0a47c704fedbc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-50.md",
      "chunk_id": "30da6df3e414cdc093d59a7e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-20261113.md",
      "chunk_id": "e0b1d4ce5249a7bf63c3b28e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "9a1d8c70070cfd7348f0cfe2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "7a4889ae1895a5404ca815ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k.md",
      "chunk_id": "d920209915000bb8aa9c8725",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/CHAIN-DISCOVERY.md",
      "chunk_id": "da410f7e7a1acb5624e5ca79",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "8c85a9ac5ab206002f63991b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-130-SITTING.md",
      "chunk_id": "695596bf83e66f470e8f9418",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "e59835d576923af1d6b47ee9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "8e8327fc9c4e4296d5880068",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "03ed61643ae60da274a9692d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "d675001a7f8337cad308223e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "52a08a3833e7c92825203a1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "c57ba47e3bcbd1c0d9b4dc81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "2a49bda9f2c6b3b0ecb5ef57",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "543d67de1e70a5103f69f3cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "e8c852d08362f8188bc50126",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "f6d635b3e2b3d8bc00d5f8c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "3dfad99bae979b0cc51a460b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "51fbcd303a3c3a42c0d48fd3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "ce6c2cf73fde0d65573b955b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-SPEC-MAP.md",
      "chunk_id": "5e58dbdb543aee56b67eed0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/CHAIN-DISCOVERY.md",
      "chunk_id": "1c5504cdae41388485f20ddc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "chunk_id": "f509ddfbf2561303c4c1f5cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "a2975d17c974965e0925c081",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "95b4edc64da11ec0e7fd1d18",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "435675f8eb05688cb9da66a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k.md",
      "chunk_id": "61de319df9360c1af4f006d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "43137ce20a0beb030ac83e59",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "6fa9107598421555f79b4894",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-130-SITTING.md",
      "chunk_id": "af683c31ca565e3afd4e9909",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "52596f32d8c4af948561d4af",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "936b8a1e3f2215951f4ef852",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "e52623aa205d6c7e9a1aa88c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "337d59737b8c6b10036589b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "3b3414ad3a9ee32628bb44ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "22773e524fb237a672953390",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-dec1163.md",
      "chunk_id": "652854f84eeac2c43029e367",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "00e7f6b620492514f89f7eae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "d0bd0ea3350dd47c6f1631f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "2013a7e19818c3fda5f5f00b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/main/orchestrator/CHECKPOINT.md",
      "chunk_id": "7bfd7ab9d92aeb9855a1e249",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "0dadc5c51a0f860a3b2ce8be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "ee074c3e7a9d30f53b226fda",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "dd3150545b3351f3b7198d62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "9bcfeb841268802953742b70",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REPLAN-W2.md",
      "chunk_id": "5a2691743df5c7e788e8fdcd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "2ac8a795639a9b42becebd7f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-20261113.md",
      "chunk_id": "76b9f5ee705b519e51b56d85",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "add825aeaf8227bf0cefa0b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "73a5381ef5b5791018a12a51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "36a86ac0b53a41bcdff13796",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "8dbcab662432497fab6d868d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "a63cf9e5f8d7549b619c14cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/impact/command.py",
      "chunk_id": "22a1b6be7b3b0b18d495c678",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/AR-2-git-sweep.md",
      "chunk_id": "a117200b975a867e3ce1847f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/check/commands.py",
      "chunk_id": "d1a83c355f85e45f9ca5db51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-6n5k/CP-DAEO-6n5k-0002.md",
      "chunk_id": "62db17c122ada87fe48a2678",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CAPACITY-1.md",
      "chunk_id": "1f8027e378efe3649cfabeff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-6n5k/CP-DAEO-6n5k-0004.md",
      "chunk_id": "25dc86324a81c5249a5cb7cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "77f6e0f8e4f8675dd1fd6ec9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-6n5k/CP-DAEO-6n5k-0007.md",
      "chunk_id": "9e95a987f8c5005498b7b75d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "77216c5a6327ca4b1aaf49b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-6n5k/CP-DAEO-6n5k-0010.md",
      "chunk_id": "ce0825b529048ed6981da548",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-57hm.md",
      "chunk_id": "c14ae83a59beeaa850f734f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "717d35471d57c15e6e60242c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-6n5k/CP-DAEO-6n5k-0002.md",
      "chunk_id": "6ec8df763edcc4e11541f165",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/AR-2-git-sweep.md",
      "chunk_id": "36afb6119db3d3496d7f3161",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-6n5k/CP-DAEO-6n5k-0004.md",
      "chunk_id": "7e3cfba0c565d1187fc9a79a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-6n5k/CP-DAEO-6n5k-0010.md",
      "chunk_id": "64a919d4d847e6e9ead32c65",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "f35b6ff165979596dcecdc7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "35615802ab81d99913d4dd1d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "7ffdddfa7dc4d91d3442cde0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "68d8e648711cac1e66dd8642",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1.md",
      "chunk_id": "a67fc278bd7011deb3dfdb2c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-6n5k/CP-DAEO-6n5k-0007.md",
      "chunk_id": "b1d0388f2802a12355687715",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "c594710d4bfd3118bd80f595",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "e9bdb62321f9047f4f63b69d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-SPEC-MAP.md",
      "chunk_id": "8f34a13b201bda68b1b7a739",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "7adc5c12d819525081ebc9c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "b28cca61f5576a910536c9a3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "c5a42636dbc3e91038b1538f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "c38925a2a721aba7f91bc62b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "73a646690a75c62399223655",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "976c1519a81f906aeb21839c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "cffe0c5f68a5afd8e4e457eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "b50716431610e582b4a5bb4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "be5c84830303cb1756a2fc9a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/AR-2-git-sweep.md",
      "chunk_id": "ddfcf50278251c58761e4ea7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ROLES-SPEC-1.md",
      "chunk_id": "0c11041b567c8dbccbdcef9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "43d4964eba3dd45e4039207e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "986068b520032dbe2add6029",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "d71d2644578c69ddd4a00ac7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "d430d79ebb083bea65751d52",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ouet.md",
      "chunk_id": "d204a9a56548402f3f018588",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "dd3c58ebeadc4264e3e61987",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/07-contract-rebaseline.md",
      "chunk_id": "972e0cde1b16f027145b6cfa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-GOV-FEATURES-1.md",
      "chunk_id": "292cbd21c18443019b24fc0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D0-CLEANUP-LIST.md",
      "chunk_id": "95cf81eeec34e0b336d5b9ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "81262ea8b613f51dffd85c67",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "f6deeb3c2e1a61d6a69bcd24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "99111fe4fbe69f711275a526",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "e4997d2367d766cf3bf8f439",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/ARCHIVE-SUPERSEDED.md",
      "chunk_id": "3a49ce22747075628e7391c5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "d8f0979ed4b5295ad5f714b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/REVIEW-BUNDLE-2026-10-22.md",
      "chunk_id": "4037f6fb3cf6b1adda90adf3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-55-review.md",
      "chunk_id": "f454c559f31db129ef6bca30",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-commands-review.md",
      "chunk_id": "b4d15fac657d6c58be6b50dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "9f99e5a62cfbdd0e34f29cac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "57dcec48e611c2a531cd066f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-20261114.md",
      "chunk_id": "aa855a5cf8563da3e4cd382d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "f2acc5f86e390c2dbdf6ad56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-55-review.md",
      "chunk_id": "2ab645eb67957364a7c3161c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-H064.md",
      "chunk_id": "5e71812753a2e27a0c282530",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "c2c03ceaff971049a7d2f3f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/w2_37_support.py",
      "chunk_id": "44800b0c0750711f002ff907",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "4dda84c0ac93f8e4d038a977",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "2abcfd983067ec0991c518ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-W2-DEC953.md",
      "chunk_id": "87cf181f22ae2e40b8f86548",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "0c14054ea0f5db3a9b740ff8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-commands-review.md",
      "chunk_id": "b793f5fc48e3cf41e3f52e51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-INVENTORY-2026-11-19.md",
      "chunk_id": "6202b6996bdae5b032ca6f3e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "69e01534f2820bc701109ebb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-55-review.md",
      "chunk_id": "43001e10821c3f2db4be6de3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PLAN-GROWTH-1.md",
      "chunk_id": "73c9964e4da48b329b378d07",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "92d61ca1b78f8685c70290c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "b4dd162745ad70f3d0ee3360",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-49-CIT-P.md",
      "chunk_id": "8a510de4e8c2b277d2379227",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/HOLDS-REVIEW-1.md",
      "chunk_id": "3bb9f17537099d343c5ced67",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "ff4992e60f517495e42e7db0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "4afd7e5a62bbf9cf3431afbc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-MEMORY-STAGE.md",
      "chunk_id": "98be6d0458403939c208f19b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "e39bc700a8b4913e08bf64f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-20261113.md",
      "chunk_id": "89a25f746ba68396ffacbf66",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-timing-tests.md",
      "chunk_id": "91fec92c0e56d05303ae57bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "cc012ddf342c1708856dba42",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/A2.md",
      "chunk_id": "7036faeaa60dbd7f2fe71bd6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "74c6cec02170610c49c45c26",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "d0b05f25252deea7d6bb2060",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "3082ddfeedadfa026639a739",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/impact/__init__.py",
      "chunk_id": "d010fa2efab3aceb3b0fc6a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/impact/__init__.py",
      "chunk_id": "6b945f9cd168d162bd41aaa2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/RESEARCH-step1-tool-map.md",
      "chunk_id": "516a5b2b50cdb537734340d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "18e41a9eb41d1dabfda6a38c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "60fcf4d4f0dddae34793ec16",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-50.md",
      "chunk_id": "f128f770ac8dc31dffad846a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-timing-tests.md",
      "chunk_id": "e45bedf2009a445abb3b3e46",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "a33ba1087f711ccd307c8c6a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "27206e5b98f4372ef6afe3c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "62b823599d3030d43b5e812e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "2b43f53b195eabfb4afbf6e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/c-tickets.md",
      "chunk_id": "17360fda4736cfd11a6d3482",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "300376a14a15c2c141ddda8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "400761adea76e1e17ace9c10",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "748966c56e2da52cf366ad18",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2d6f.md",
      "chunk_id": "8285d794cadd7aa7bc130d2a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2d6f.md",
      "chunk_id": "1d09fa99e0aec08125cc1e35",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/test_w1_07_recorded_commands.py",
      "chunk_id": "9907041dbd5bb7c5f2a07084",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/conftest.py",
      "chunk_id": "ba36706b77577a0def275423",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-p7a.md",
      "chunk_id": "2266c8cdf7695920c5a13c72",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/README.md",
      "chunk_id": "3a33e16dbaefc1c589e9fa1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/w2_37_support.py",
      "chunk_id": "c29629c1bb0e8625da99a018",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-version-1.1.0.md",
      "chunk_id": "25387f612b090516e23b6efc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/optin-weekly.txt",
      "chunk_id": "3e12da4b4ef94464e9732be3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/optin-weekly.txt",
      "chunk_id": "149f9233e1a689f044d6f51e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "af715113870bc26f299e3072",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/w2_37_support.py",
      "chunk_id": "a9d611bcfe0191bd8cc84065",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/w2_37_support.py",
      "chunk_id": "1b89536f18c54265e1e9beeb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "23829260ed117e4bc51a8bbf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k.md",
      "chunk_id": "94702754f25dc475d8c8cc04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "9611c2e735d12370dfd5a576",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/C-decisions-to-spec.md",
      "chunk_id": "c7b99e79edf60d4bb22d17dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "5f3a69b1ad677c98d920b151",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "b9909c40da7657e08faa31e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/test_w1_07_recorded_commands.py",
      "chunk_id": "80425c186512acf11ffa9a94",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-35/test_w1_35.py",
      "chunk_id": "c424846f3a452003885fae51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-dec1163.md",
      "chunk_id": "5d7f87dbe498eb25a0f63f01",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "13ee296dbb92b4c026b759aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "981936274341288ed89dffdf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "ab4bc044245cdb19df63d22c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "c2d76987189063c81824f878",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-32/test_w1_32_command_set.py",
      "chunk_id": "71fb391ecbcf66163b3d7922",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/w1_07_support.py",
      "chunk_id": "9278afc330891f9f0a8611dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "fedb0af1503ada3a665b80b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "2f56752968de2335ae439b61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "d531a7b1889dc14465b16aab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "34c04f92ab43f1d414cc98d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "9599d4bb62b388800e351539",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "a8fb664f5387e48dd3dbdd14",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "1c15360cf4d8a5a8122c30aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/F-models-context.md",
      "chunk_id": "65cfff053c9a2cca199b5e6f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/test_w1_07_recorded_commands.py",
      "chunk_id": "c7972993dab5f2b5293d6a9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "924620bc9323cd1c01c36f5e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "06cf344577895dcadd487593",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "888eb64cae0ea8a960e72b44",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-version-1.1.0.md",
      "chunk_id": "80dea5134d14296f3625d21c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "1846d097ede92653556a81db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "chunk_id": "97f76959d9da9870fd042099",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "f1483aa6311885b8e1215587",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "5df279fc263c8f9f6b8fe731",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "1cd0113771eb1b592e50b1d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "dbdc530f720529962df9475e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "f3eea672973554816b7a1ece",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-drhj/PR-DAEO-drhj-run4-narrow.md",
      "chunk_id": "63270e1676fd2aeb3abce5c4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-35/README.md",
      "chunk_id": "b9e883994b33a0ea0a82926f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "35f819097e0602334f8de233",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "dc75a6f92424cd135154ae26",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/F-models-context.md",
      "chunk_id": "6a7b528dcca4d8ba15ae8ca4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/impact/test_impact.py",
      "chunk_id": "61fd6a6fc1c3e251f21d9166",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "e5cad610f7c352cbce058c24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "02e1a6ae94cedc30da11cea8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-version-1.1.0.md",
      "chunk_id": "bced6904cfc22abc1e24886d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "3cd34942ac20aa8c750d763c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "49a281329d44ae6fc8a8387c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-p7a.md",
      "chunk_id": "95d546390f91f0759f2a212e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-p7a.md",
      "chunk_id": "9e69c8862da8d498b91933c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-p7a.md",
      "chunk_id": "07196dbd2c6f174b6e4413f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/conftest.py",
      "chunk_id": "48fbed48c4185afd9cccb2e1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "e1f7b3fc599a036c4a7203cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "3bf2a2a0d79ea6cd24939047",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "50f09692623041105fb43730",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P2-perticket.csv",
      "chunk_id": "ee3179c3e49ae7de16070cef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/C-decisions-to-spec.md",
      "chunk_id": "2c13460ff7c063a572cf6a51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "b947d7a8b4291086dc0ac520",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "e0df604e4a9b9f544292911e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "4ca4b9395f95dd6f60b3ea7f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/F-models-context.md",
      "chunk_id": "6f892ce9a47b6a1fde35529d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "0aceafe3ec2beba72ddac49e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "63349c107f71b8a69e18e444",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "283bbb816e32e2fcf224663c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P2-lifecycle.md",
      "chunk_id": "933c4254e0edbbf21d888039",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P2-lifecycle.md",
      "chunk_id": "3193dab8ee09389d7b290050",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "2c1038e86a44012886c30f8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/G-tools-glue.md",
      "chunk_id": "eefe17ef25bd52b57ec3e914",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "8497c64ad9f6faaeacca2e82",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "f30601e913f1228f4914399b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "92cd3fc49bbba096fd9a45ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "df35582a5609ea10aafd624c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "cdeb6fadce1cdd43a41a67bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "62f51b24cf62e48c4c039357",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "b3d0e2a431b9afb50531ebc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "77056325cdb67a2bb2281631",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "182e4ba52f1679e13fdf0612",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "afa6c4562994cda3e9e5db0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "6ede760db282fac57355e22d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "efd94f4ca26c0a7e27b44463",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "5f102f3caec62f97d6395ee6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "28918d26731e55a363bbf945",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "bd434a4e1dd5c33f66a53f8b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "801a23efb14454cc18431060",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "9f0e1e2dfa909bfe3ef67587",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "adfa0217d4109126a14918c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "3cd5b92a27e4f09eda96bf3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k.md",
      "chunk_id": "7776b29e805800e8620cdaff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "6d769fd96083b34b31ac8863",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "feac1c2b5df9e413e3b03647",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "b936c6afe50d3db52d25016d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "874695c039be093883dff2f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "4cb61819bd54f8c4d0e7f307",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "eea64b5611209b253764ee11",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "c0a01dbdbf1904f125df07fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k.md",
      "chunk_id": "e78ced1a0b1d33588dd8221c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "06a703ee49bd1b0664751668",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "b9fb9d82708d465571a48950",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "aade2b0992e8b0feb783ae7e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "06085d027bbcf469de27b4e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k.md",
      "chunk_id": "014dccb473abf9ebc5c3e365",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "9f021c2d654c00fcc6920b53",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "ab30b1a09e1479cdf85c9ed1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "66e51e63a9794d36933b508f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k.md",
      "chunk_id": "8d195a56ba5318b3eb4de9e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k.md",
      "chunk_id": "49cec3d759d839ed5f5eb659",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "9f5b9e7130b62186edd9b4fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/w2_37_support.py",
      "chunk_id": "d73f7725a4a218d9e997a50c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/test_w2_37_code_graph.py",
      "chunk_id": "16475f924072c5d634cd8c48",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/test_w2_37_proposal.py",
      "chunk_id": "2ccfc6323d4453e5f4a9edf8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/test_w2_37_resume_findings.py",
      "chunk_id": "fa8fb12dd637690a8ab2452a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/test_w2_37_resume_findings.py",
      "chunk_id": "c344e4832c7a9fe1f6727cdb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/test_w2_37_resume_findings.py",
      "chunk_id": "cce56b5fa7907a690f2ac8dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/w2_37_support.py",
      "chunk_id": "3387dd6b2fe544c56e104e34",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/test_w2_37_question.py",
      "chunk_id": "29b0fb6639b420d271ed8778",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/test_w2_37_review_findings.py",
      "chunk_id": "c6c35c6120fff8b8edbabc5a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/test_w2_37_review_findings.py",
      "chunk_id": "16a85a05c47b0102a6d78c3b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/test_w2_37_resume_findings.py",
      "chunk_id": "475e3c69772e707a8e969ebd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/test_w2_37_review_findings.py",
      "chunk_id": "e14d6c390bc7b6ff5be0b732",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/test_w2_37_command.py",
      "chunk_id": "94fb6bcaeeb39ad6279ee813",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "8ec12806d53e740cf6ba5d20",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "0445be3a3ece9be932e1ec2e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k.md",
      "chunk_id": "e35dfd4b6b3283deb63330c6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "c5189f6a8557de94693c3598",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k.md",
      "chunk_id": "008dee25285ed4a5cee37c2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "c0f65c0ccc6a36041529cec0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "db194f9fd49c49ffc7bc1a68",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "5cbaf0eed8771261cb7059c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "2a6cfca9c58277df036ba842",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "ef8f9976f5aebf3be5a2ddc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "776f60fa146de9e5ee25bf9d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "56850e0340cb230c0e7bb46a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "d9af17c8b9c15ce34ffbe4c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "b14689db02477d8c3b5834c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "fd66bc470f67cc522c00fdde",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "467afb9acd5b4997f39ec159",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "4b26083393c560ba57364a8a",
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
    "closure": {
      "available": true,
      "reason": null,
      "followed": {
        "records": [
          "CAP-33.b",
          "CAP-33.g",
          "DEC-167",
          "CAP-53.b",
          "DAEO-0mab",
          "DEC-953"
        ],
        "left": 0
      },
      "changed_by": {
        "DEC-953": [
          "DEC-968",
          "DEC-959"
        ]
      }
    },
    "code": {
      "available": true,
      "reason": null
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5824
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLTZuNWsubWQiLDEsMzMsIjM0MDdhYjZkMWM0Zjc5NzRlZTdjODc2OSJdLFsiLnRpY2tldHMvREFFTy02bjVrLm1kIiw2Miw3MSwiOTc1OGJkZTkwODRjZjZlODQxMWU1ODM3Il0sWyJkb2NzL2NvbnRyYWN0L2NhcGFiaWxpdGllcy9DQVAtMzMuYi5tZCIsMTEsMTYsIjZjNTQwN2E2N2Q0YTE5ODMxMTUxNzQ4NSJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9icmllZnMvTEVBRC0xLTAtc2VsZWN0aW9uLm1kIiwyNjAsMjY1LCIyNGJlNjViMWI3OTg5NDU4M2VkNzIyMmQiXSxbImRvY3MvZW1lcmdlbmN5LTIvYnJpZWZzL0xFQUQtMS0wLXNlbGVjdGlvbi5tZCIsMjY0LDI3MywiMDAyOTcwZDlmNGMxNDcwODQ5MzRiMGU4Il0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL0lOVEVHUkFUSU9OLVBMQU4ubWQiLDcwLDcxLCI0NTgzZTgzZjUyODY1ZmE1NGVlZWI0NzMiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vVE9PTC1NQVAubWQiLDIzMywyMzUsIjM3MzQxMzUyNzNjMjYzNjg5ZDUzMzJlNCJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vcGFja2FnZXMvUC1XMi01MC5tZCIsMzAsMzIsImQ0YmY4MTZhNTAxMTZhNmQ4ZTdiMjQwYiJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vcGFja2FnZXMvUEtHLVcyLTM3LUNJVFAtMS5tZCIsMSwxNCwiMjRhNGY4YTc5ZmYzN2JmNmQ3YmQ4ZmViIl0sWyJzcmMvZ292L2ltcGFjdC9fX2luaXRfXy5weSIsMTMzLDEzNywiNmU1YzNkZjA0Y2U0Nzg3M2M5YjBkNWNlIl0sWyJzcmMvZ292L2ltcGFjdC9fX2luaXRfXy5weSIsMTM4LDE1MSwiYWViYzM0OWQ3ZmRkNDI2Y2ViMDE3MmIxIl0sWyJzcmMvZ292L2ltcGFjdC9fX2luaXRfXy5weSIsMTU2LDE1NiwiYTdlNWJlODZlY2YzMGEyYzYwODE1OWI1Il0sWyJzcmMvZ292L2ltcGFjdC9fX2luaXRfXy5weSIsMTYzLDE2MywiYmIyM2JlOGI0OWY5NzQ2YWFlNjEzOGQ3Il0sWyJzcmMvZ292L2ltcGFjdC9fX2luaXRfXy5weSIsMTY4LDE2OCwiOThiMDU0NDA0NmVkYTNlZWU1YmYwYzQxIl1dLCJmIjoiL2hvbWUvdXNhaW4vZ292LW9zLXdvcmt0cmVlcy9XMi0wMC1zdG9yZS1iIiwiaSI6W10sIm8iOjIwLCJwIjp7ImIiOiJzZXJ2aWNlIiwiZCI6ImN1ZGE6MCIsImgiOiJlMmZhM2YyNTIxZTM3MTU4IiwibyI6WzE0LDksOCwxMSw2LDEzLDAsMiwxMiwxMCwyNiwyMywxLDIwLDIxLDIyLDI1LDI5LDQsMTcsNywzMywyNywzLDE1LDUsMzUsMTksMzYsMzgsMzksMzEsMTgsMTYsMjgsMzQsMjQsMzcsMzAsMzJdfSwicSI6ImdvdiBpbXBhY3QgcGVyZm9ybWFuY2U6IHRoZSBjb2RlIGdyYXBoIF9Db2RlIGxvYWRlZCBmb3IgcmVjb3JkLW9ubHkgaWRzLCB0aGUgY29kZSBpbmRleCBkYWVtb24gd2FpdCwgSS01IHBhc3QgMTUwIHNlY29uZHMsIGltcGFjdCB0ZXN0cyBXMi0zNyIsInIiOjAsInMiOiJjOGNlNzhhMTVkZmI4NmQwZDhhMzIxYzczMzUxYThkZTAzZWZjNzdlIiwidCI6bnVsbCwieCI6WyIxNjE5ZDUwYTJlZmNhODU3ZWY1NzYwYzUiLCIzNGQwOGJkODg4MmZjNTkwMWI3MTY1NWIiLCI2MTI3YjdmNzllYmRhMTFlNmIyMDExMGUiLCI2NmUwZGIzNjEwZWViMjYxMThkNGVhNDAiLCJhZWU5OTZhZWQ2ZGU4ZmE3ZTMxM2FhZjMiLCJkYzdjZWViNjk3ZTY4OTU4ODIyNTIyZjMiXX0=",
  "routing": {
    "code": [
      "6e5c3df04ce47873c9b0d5ce",
      "aebc349d7fdd426ceb0172b1"
    ],
    "named": [
      "9758bde9084cf6e8411e5837",
      "f8c807c9ab4e4bf4292bb412"
    ],
    "phrasings": [
      "gov impact performance: the code graph _Code loaded for record-only ids, the code index daemon wait, I-5 past 150 seconds, impact tests W2-37",
      "gov impact performance code graph _Code loaded record-only ids code index daemon wait I-5 past 150 seconds impact tests W2-37",
      "gov impact performance: the code graph _Code loaded for record-only ids, the code index daemon wait, I-5 past 150 seconds, impact tests W2-37 DAEO-6n5k"
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
        "chunk_id": "3734135273c263689d5332e4",
        "path": "docs/emergency-2/integration/TOOL-MAP.md",
        "start_line": 233,
        "end_line": 235
      },
      {
        "chunk_id": "3407ab6d1c4f7974ee7c8769",
        "path": ".tickets/DAEO-6n5k.md",
        "start_line": 1,
        "end_line": 33
      }
    ]
  }
}
