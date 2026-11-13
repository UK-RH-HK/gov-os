You are a fresh engineer. Ticket: DAEO-6n5k (W2-37, "gov impact"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-37` on branch `w2/W2-37`, and write only inside the ticket's allowed paths: `src/gov/impact/**`, `src/gov/closure/**` (read API only: do not change its behaviour), `tests/unit/impact/**`. The implementation exists and passed two reviews' re-probes; the second review left findings the owner decided are fixed in this resume (DEC-812), plus the owner's closure-depth decision DEC-815. An independent test designer is writing acceptance cases for the same behaviours in parallel in another worktree; you never read or write `tests/acceptance/`.

## Standing rules
- First: `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-6n5k`); `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-37`, `w2/W2-37`); `git rev-parse HEAD` (expect prefix `64ccbd0cc`). If anything differs, stop and say so.
- DEC-732: every test run uses this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src` per command. Quote `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -c "import gov; print(gov.__file__)"` in your return.
- **Every pytest runs through the heavy slot**, with a TMPDIR outside the repository and outside ~/gov-os-runs:
  `env TMPDIR=/tmp/gov-os-w237-eng PYTHONUSERBASE=/home/usain/.local PATH=/home/usain/.local/bin:/home/usain/.nvm/versions/node/v22.23.3/bin:/usr/local/bin:/usr/bin:/bin PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-37 tests/unit/impact -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfs`
  (make the TMPDIR first with `mkdir -p /tmp/gov-os-w237-eng`). A "all slots taken; waiting" line is a wait, not a refusal. Never `-x`.
- Run everything in the foreground. Return only after your commit exists. No checkout of another commit, reset, clean, stash, amend, rebase, merge, push or tag. Stage by exact path, never `git add -A`/`.`. Untracked sandbox placeholder names (`.bashrc`, `.gitconfig`, `.mcp.json`, ...) are never touched.
- Write files with the Write and Edit tools and literal absolute paths; anything longer than one line of shell goes in a script under `/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/`. No here-documents.
- Never run `gov rebuild`, `gov close`, `gov adopt`, `gov pause`, `gov retrieve` or `gov context`. Search with Read and Grep; search again once in different words if the first does not answer. A code question uses the code graph's traversal, never a whole-graph query (DEC-859).
- Never read `.claude/settings*.json`, anything under `~/.claude/`, the held-out file under `governance/project/`, the evaluation sets' root, or any hidden or memory-verdict folder. No glob/search/listing over `governance/project/`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so. Never work around a refusal. Install nothing.

## What to make true (each with a unit test in `tests/unit/impact/`)
1. **A (compare against the proposal as committed).** `gov impact --compare` must never say `matches: true` (or list no differences) when the CIT-P file in the working tree differs from HEAD (edited, staged or uncommitted). Either compare against the proposal as HEAD / the store holds it, or refuse / report not matching while the file differs, naming the file. Example: CITP-001 listing DEC-002 committed and loaded; DEC-002 removed in the working tree, uncommitted; a CIT-E without DEC-002 must not give `matches: true`.
2. **B (a register's first uncommitted entry).** The decision register named by the path map, differing from HEAD (added, staged or uncommitted content), makes `graphs.record` `stale` (naming the path), **even when HEAD holds no entry of it** (today only a register already holding an entry at HEAD is seen; a first entry DEC-090 added uncommitted reads `ok`, and with the register in a non-governance namespace the report reads `complete: true` while missing DEC-090). The record graph not current means `complete: false` and never a `deletable` item (reading R8, G-24).
3. **C.** A compare result carries the proposal's own `complete` and its gaps (a CIT-P written with `complete: false` and a CIT-E with the same lists: the result says `complete: false` and lists the gaps, whatever `matches` says).
4. **E.** Refusals name their real cause: a `--compare` CIT-P file that does not exist is refused as missing (not "lists nothing under affected"); `--out ""` is refused as an empty path and `--out <existing folder>` as a folder (not "a file is there already"). Exit 1, no traceback, nothing written.
5. **F4.** `--out` whose file stem is an id already in the store (e.g. `CITP-001.md` written to a new path while CITP-001 is a stored record) is refused naming the clash; nothing written.
6. **P-2 (DEC-815, the owner's decision).** The result's `depth_source` names `DEC-815` (the owner set R0/R1 one hop, R2 three, R3 eight for Wave 2; `gov.closure.depth_of_radius` already holds 1, 3, 8). Change `DEPTH_SOURCE` and its comment in `src/gov/impact/readings.py`; the acceptance case `test_w2_37_rows.py::test_the_depth_of_a_radius_comes_from_an_owner_decision_or_a_measurement` turns green.

Keep the change small; no behaviour that is green today changes. At the end, the acceptance suite run above: every case that passed before still passes, the depth case is green; the two `test_w2_37_skill_routing.py` cases stay red (they need the change skill's files, outside your paths: name them, do not touch them). Cases that build a code index may error at setup inside the sandbox (`/tmp/gov-cbm-<uid>` read-only): name them, the lead runs them outside.

## Commit (one commit, your paths only)
    git commit -m "W2-37: gov impact, the second review's findings A, B, C, E, F4 and the depth source (DEC-812, DEC-815)" --trailer "Task: DAEO-6n5k" --trailer "Role: engineer" --trailer "Implements: CAP-33.b, CAP-33.g, DEC-167" -- src/gov/impact tests/unit/impact
Then show `git log -1 --format='%H%n%B'` and `git status --short`.

## Return (your last message; the twelve fields as labelled lines, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
In `tests:` give the suite's counts and each red with its reason. Then `guard_refusals:` (none, or each refusal's command form and reason).

## The ticket's context (gov context, built by the lead outside the sandbox)
{
  "ticket": "DAEO-6n5k",
  "ticket_text": "---\nid: DAEO-6n5k\nstatus: in_progress\ndeps: [DAEO-g0ip, DAEO-ym8a]\nlinks: []\ncreated: 2026-10-16T16:35:11Z\ntype: task\npriority: 2\nassignee: engineer\nexternal-ref: W2-37\ntags: [wave-2, implementation, full]\nwbs_id: W2-37\ntitle: gov impact\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-g0ip\n- DAEO-ym8a\nallowed_paths:\n- src/gov/impact/**\n- src/gov/closure/**\n- tests/unit/impact/**\nkpis:\n  success:\n  - '\"What''s the impact of X?\" in plain language runs gov impact [CAP-33.g, DEC-167]. Verify: a planted question \"what is the impact of DEC-NNN?\" given to the plain-language entry runs gov impact on DEC-NNN and prints its result [Verify clause added, DEC-1157 (12)]'\n  - 'It also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join). Verify: planted records with mapped ids and a deletable-class row: gov impact resolves the mapped ids (G-16) and joins the deletable class (G-24) in its result [Verify clause added, DEC-1157 (12)]'\n  failure: []\n  lifted:\n  - 'A decision change raises a CIT-P that lists the affected specifications, decisions, tickets, tests and code from both graphs, with a radius [CAP-33.b, W2-M285]. [lifted (was S1), DEC-1083: the query only, no CIT-P (INVESTIGATION-1 \u00a75, W-3)]'\n  - 'After apply or archive, the CIT-E record matches the proposal or lists the differences [W2-L319]. [lifted (was S2), DEC-1083: the query only, no CIT-P (INVESTIGATION-1 \u00a75, W-3)]'\nprofile: FULL\nsources:\n- CAP-33.b\n- CAP-33.g\n- DEC-167\n- DEC-1083\nest_loc: 280\nacceptance_tests:\n  path: tests/acceptance/W2-37/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: C\ncloses:\n- CAP-33.b\n- CAP-33.g\n- DEC-167\nlist_rows:\n- W2-L319\n- W2-M056\n- W2-M150\n- W2-M285\n- W2-M320\n---\n# W2-37 gov impact\n\nCard: `docs/plan/WAVE_2_WBS.md` \u00a72 (W2-37), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).\n\n- **Allowed paths:** `src/gov/impact/**` (new), `src/gov/closure/**` (read API only), `tests/unit/impact/**`.\n- **KPIs:**\n  - A decision change raises a CIT-P that lists the affected specifications, decisions, tickets, tests and code from both graphs, with a radius [CAP-33.b, W2-M285].\n  - After apply or archive, the CIT-E record matches the proposal or lists the differences [W2-L319].\n  - \"What's the impact of X?\" in plain language runs `gov impact` [CAP-33.g, DEC-167].\n  - It also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join).\n",
  "authority": [
    {
      "id": "DEC-167",
      "sha256": "86b5876d766942fe8f1d6fc0b1d33d0b66815229f814ab57afdac95f99cb204b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "86b5876d766942fe8f1d6fc0b1d33d0b66815229f814ab57afdac95f99cb204b",
      "reason": "declared in sources",
      "tokens": 251
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "CAP-33.b",
      "sha256": "376667746939cdc654cbbae6fdbc167c6782d9b357dcb7a7839aaf26b1d36afe",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "376667746939cdc654cbbae6fdbc167c6782d9b357dcb7a7839aaf26b1d36afe",
      "reason": "declared in sources",
      "tokens": 147
    },
    {
      "id": "CAP-33.g",
      "sha256": "86f2d129f3c90f9f39711617986cbbc25e17e2ad525e4b1d477657f18a7a8212",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "86f2d129f3c90f9f39711617986cbbc25e17e2ad525e4b1d477657f18a7a8212",
      "reason": "declared in sources",
      "tokens": 133
    },
    {
      "id": "DAEO-g0ip",
      "sha256": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "reason": "declared in sources",
      "tokens": 444
    },
    {
      "id": "DAEO-ym8a",
      "sha256": "0c0c7ec45cd88e1a0fa97dd448da208e9d77da5a5f5d8053a460185aa32e8cb5",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "0c0c7ec45cd88e1a0fa97dd448da208e9d77da5a5f5d8053a460185aa32e8cb5",
      "reason": "declared in sources",
      "tokens": 164
    }
  ],
  "mandatory": [
    {
      "id": "DEC-167",
      "sha256": "86b5876d766942fe8f1d6fc0b1d33d0b66815229f814ab57afdac95f99cb204b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "86b5876d766942fe8f1d6fc0b1d33d0b66815229f814ab57afdac95f99cb204b",
      "reason": "declared in sources",
      "tokens": 251
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "CAP-33.b",
      "sha256": "376667746939cdc654cbbae6fdbc167c6782d9b357dcb7a7839aaf26b1d36afe",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "376667746939cdc654cbbae6fdbc167c6782d9b357dcb7a7839aaf26b1d36afe",
      "reason": "declared in sources",
      "tokens": 147
    },
    {
      "id": "CAP-33.g",
      "sha256": "86f2d129f3c90f9f39711617986cbbc25e17e2ad525e4b1d477657f18a7a8212",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "86f2d129f3c90f9f39711617986cbbc25e17e2ad525e4b1d477657f18a7a8212",
      "reason": "declared in sources",
      "tokens": 133
    },
    {
      "id": "DAEO-g0ip",
      "sha256": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "reason": "declared in sources",
      "tokens": 444
    },
    {
      "id": "DAEO-ym8a",
      "sha256": "0c0c7ec45cd88e1a0fa97dd448da208e9d77da5a5f5d8053a460185aa32e8cb5",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "0c0c7ec45cd88e1a0fa97dd448da208e9d77da5a5f5d8053a460185aa32e8cb5",
      "reason": "declared in sources",
      "tokens": 164
    }
  ],
  "supplementary": [
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "- **DEC-815 (owner, 2026-10-19; P-W2-45 (a)):** the depths of R0/R1, R2 and R3 are 1, 3 and 8 hops; `depth_source` names DEC-815 (`readings.py`), set in the resume.\n- **KPIs:**\n  - A decision change raises a CIT-P that lists the affected specifications, decisions, tickets, tests and code from both graphs, with a radius [CAP-33.b, W2-M285].\n  - After apply or archive, the CIT-E record matches the proposal or lists the differences [W2-L319].\n  - \"What's the impact of X?\" in plain language runs `gov impact` [CAP-33.g, DEC-167].\n  - It also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join).\n- **DEC-859 (owner, 2026-10-20; standing), in the resume:** the paths gain `src/gov/codeintel/**` (the accepted plan's widening, \u00a74.4).\n  - Agents' questions use the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), with small, targeted answers; the wrapper never loads the whole graph to answer a question; the tool's error is passed through.\n  - Whole-graph jobs (a full impact map, an audit of every dependency) read the graph in pages, never one query over the tool's row cap.\n",
      "tokens": 281
    },
    {
      "id": "WAVE-1-WBS",
      "path": "docs/plan/WAVE_1_WBS.md",
      "text": "## 5. Source merge (DEC-076)\n\nEvery source item is carried by a W1 ticket:\n\n| Source | Carried by |\n|---|---|\n| S0b2 GLUE, W1 items | G-01 \u2192 W1-02 \u00b7 G-03 \u2192 W1-09 \u00b7 G-04 \u2192 W1-11 \u00b7 G-05 \u2192 W1-14 \u00b7 G-06 \u2192 W1-16 \u00b7 G-07, G-09 \u2192 W1-12 \u00b7 G-08 \u2192 W1-13 \u00b7 G-10 \u2192 W1-41 \u00b7 G-11, G-15 \u2192 W1-38 \u00b7 G-12, G-18 \u2192 W1-15 \u00b7 G-14 \u2192 W1-39 \u00b7 G-17 \u2192 W1-17 + W1-19 \u00b7 G-19 \u2192 W1-21 \u00b7 G-20, G-21 \u2192 W1-17 \u00b7 G-22 \u2192 W1-18 \u00b7 G-25 \u2192 W1-37 |\n| S0b2 GLUE, moved to W1 | G-02 \u2192 W1-03 (DEC-076) |\n| S0b2 GLUE, W2 (stay W2) | G-13 framing-tolerant MCP client \u00b7 G-16 id mapping \u00b7 G-23 incremental re-index hook \u00b7 G-24 deletable-class join |\n| DEC-080 (retrieval completeness) | paging/continuation, facets, dedup, authority filter, one rerank, evidence bundle \u2192 W1-21 \u00b7 `gov closure` \u2192 W1-20 \u00b7 validator, canaries \u2192 W1-22 \u00b7 hierarchical synthesis \u2192 W1-23 \u00b7 parallel facet subagents \u2192 W1-36 |\n",
      "tokens": 213
    },
    {
      "id": "WAVE-2-TRIAGE",
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "text": "## Rows on the Wave 1 WBS's Wave 2 outline but not on the list\n\n| Item | Title | Disposition | Reason |\n|---|---|---|---|\n| S0b2 G-13 | Framing-tolerant MCP client | W2-32 | The code-index client is a retrieval component. |\n| S0b2 G-16 | Id mapping between the graphs | W2-37 | gov impact joins the record and code graphs by id. |\n| S0b2 G-23 | Incremental re-index hook | W2-06 | Same as CAP-17.b (Wave 1 WBS \u00a76). |\n| S0b2 G-24 | Deletable-class join | W2-37 | gov impact's radius needs the deletable-class join. |\n\n",
      "tokens": 130
    },
    {
      "id": "5e5ac8e4e4bcd1e61383b6d2",
      "path": "tests/unit/impact/test_impact.py",
      "text": "\"\"\"Builder tests for ``gov impact`` (W2-37).\n\nRegression evidence only (DEC-136). They cover what the acceptance tests cannot run inside a worker's sandbox\n(P-W2-38): the code side, with the code index's functions replaced (the codebase-memory binary is not run), so the\nid mapping of G-16, the deletable-class join of G-24 and a stale code index are held here too; and the parsing of the\nstated change and the radius reading. Every store is built in a temporary repository; nothing is indexed.\n\"\"\"\nfrom __future__ import annotations\n\nimport subprocess\nimport sys\nfrom pathlib import Path\n\nimport pytest\n\nREPO = Path(__file__).resolve().parents[3]\nsys.path.insert(0, str(REPO / \"src\"))\n\nfrom gov import codeintel, impact, store  # noqa: E402\nfrom gov.cli.errors import GovError  # noqa: E402\nfrom gov.impact import readings  # noqa: E402\n\n# helper <- apply <- entry and the test; helper <- orphan; named_only alone\nCALLS = {\"apply\": [\"helper\"], \"entry\": [\"apply\"], \"test_apply\": [\"apply\"], \"orphan\": [\"helper\"], \"helper\": [],\n         \"named_only\": []}\nPATHS = {name: \"tests/test_flow.py\" if name.startswith(\"test_\") else \"app/flow.py\" for name in CALLS}\n",
      "tokens": 289
    },
    {
      "id": "3d34b5ddc78a2c586b751523",
      "path": "src/gov/impact/readings.py",
      "text": "\n\n# P-3, reading R8 (G-24, the deletable-class join): deletable only when neither graph has anything that depends on\n# the item: no record edge names it and, for a symbol, the code index answers it as dead code (W1-16). What the item\n# depends on itself does not count. A graph that is not read in full and current never makes an item deletable.\n",
      "tokens": 87
    },
    {
      "id": "CONTRACT-v4",
      "path": "docs/contract/CONTRACT_v4.md",
      "text": "### CAP-33 \u2014 Change-impact transactions (CIT-P simulation, CIT-E execution)\n\n- **Outcome:** An agent can simulate a change before making it (CIT-P) and record what it changed (CIT-E).\n- **Acceptance:** A decision change raises a CIT-P listing the affected specs, decisions, tickets, tests and code from both graphs, with a radius; after apply/archive the CIT-E record matches the proposal or lists the differences.\n- **Wave:** W2 (OpenSpec proposal and apply/archive in W1, where a plain-language impact question runs an OpenSpec proposal plus `gov closure` (DEC-167); computed impact W2)\n- **Provider:** OpenSpec 1.13.2, W1-35, W2: gov impact\n- **Disposition:** KEPT\n- **Sources:** Contract v3 Gate K1, K2, K3, K4; Framework v4.1.2 \u00a747-49; DEC-005 (proportionality profiles LITE/STANDARD/FULL); DEC-035 (radius-scaled budgets/facets); DEC-011; DEC-066; DEC-105; DEC-167\n- **Covers:**\n  - `CAP-33.a` [W1] CIT-P proposal and CIT-E apply/archive records \u2014 Contract v3 K1, K2; Framework v4.1.2 \u00a747 \u00b7 delivered by W1-35\n  - `CAP-33.b` [W2] Automatic impact simulation over record and code graphs; impact radius \u2192 profile \u2014 Contract v3 K3, K4; Framework v4.1.2 \u00a748, \u00a749\n",
      "tokens": 292
    },
    {
      "id": "CONTRACT-v4",
      "path": "docs/contract/CONTRACT_v4.md",
      "text": "  - `CAP-33.b` [W2] Automatic impact simulation over record and code graphs; impact radius \u2192 profile \u2014 Contract v3 K3, K4; Framework v4.1.2 \u00a748, \u00a749\n  - `CAP-33.c` [W3] Upstream change propagates staleness and generates revalidation tasks \u2014 Contract v3 W6\n  - `CAP-33.d` [W1] Changes to the Gov OS itself pass evidence \u2192 corroboration \u2192 proposal \u2192 independent review \u2192 owner approval \u2192 versioned promotion \u2014 Framework v4.1.2 \u00a75 \u00b7 delivered by W1-35\n  - `CAP-33.e` [W1] An experiment or finding that contradicts a closed specification opens a CIT-P whose impact assessment gives three costed options (apply now, defer, re-baseline); the owner chooses; CIT-E records what was done; every version of the specification is kept \u2014 DEC-105 \u00b7 delivered by W1-35\n  - `CAP-33.f` [W1] The question \"what is the impact of X?\", asked in plain language, triggers the impact assessment; in Wave 1 that is an OpenSpec proposal plus `gov closure` \u2014 DEC-167 \u00b7 delivered by W1-35\n  - `CAP-33.g` [W2] From Wave 2 the same plain-language question runs `gov impact` \u2014 DEC-167\n",
      "tokens": 264
    },
    {
      "id": "WAVE-1-WBS",
      "path": "docs/plan/WAVE_1_WBS.md",
      "text": "| Register decisions | DEC-074 Q9 deny rules \u2192 W1-01 \u00b7 DEC-083 install rule \u2192 W1-04 (interim rule W1-01), registry \u2192 W1-06 \u00b7 DEC-084 bootstrap \u2192 W1-01, W1-05 \u00b7 DEC-086 ccusage \u2192 W1-06, counter \u2192 W1-31 \u00b7 DEC-087 CI evidence record \u2192 W1-40 \u00b7 DEC-070 exit audit \u2192 W1-43 \u00b7 DEC-088 audit triggers \u2192 W1-13, W1-35, W1-36, W1-43 \u00b7 DEC-089 gap tickets \u2192 W1-13, W1-26, W1-35 \u00b7 DEC-090 A0\u2013A6, A8 \u2192 W1-41 \u00b7 DEC-091 parent-child \u2192 W1-17, W1-21 \u00b7 DEC-093 package cap \u2192 W1-34, W1-35 \u00b7 DEC-046 lessons \u2192 W1-44 \u00b7 DEC-102 experiments, DEC-103 order of specification work, DEC-105 three-option CIT-P, DEC-136 probe findings \u2192 W1-35 \u00b7 DEC-104 UX and visual testing \u2192 Wave 2 \u00b7 DEC-106 learning metrics \u2192 W1-31, W1-42 \u00b7 DEC-137 post-green probe \u2192 W1-30 \u00b7 DEC-119, DEC-154 role definitions \u2192 W1-05, then W1-33 \u00b7 DEC-150, DEC-156 orchestrator write scope \u2192 W1-45 \u00b7 DEC-152, DEC-153, DEC-158, DEC-159, DEC-161 launcher and sandbox \u2192 W1-46 \u00b7 DEC-153 escape hatch and failed commands, DEC-162 oracle hiding \u2192 W1-47 \u00b7 DEC-153 Claude Code pin \u2192 W1-48 \u00b7 DEC-160 untested sandbox cases \u2192 Wave 2 \u00b7 DEC-163 minimal research role \u2192 W1-46 \u00b7 DEC-164 no `excludedCommands` \u2192 W1-46; subagents in a sandboxed worker and `excludedCommands` \u2192 EXP-002, Wave 2 \u00b7 DEC-165 lite upstream lesson loop \u2192 Wave 3 \u00b7 DEC-166 `gov discover` \u2192 Wave 2 \u00b7 DEC-167 plain-language impact question \u2192 W1-35, then `gov impact` in Wave 2 \u00b7 DEC-168 lesson scope and severity in the schema \u2192 W1-08 (records: W1-44) \u00b7 DEC-141 sandbox prerequisites in the registry \u2192 W1-48 \u00b7 DEC-169 validator \u2192 `docs/plan/tools/validate_s1.py` \u00b7 DEC-170 sandbox token line \u2192 W1-31 \u00b7 DEC-171 orchestrator change as a record \u2192 W1-45 \u00b7 DEC-172 settings ask rules removed \u2192 W1-47 (install test with the committed settings: W1-46) \u00b7 DEC-173 Charter \u00a76 install sentence \u2192 no ticket \u00b7 DEC-174 four `uv` forms in the install rule \u2192 W1-47 |\n",
      "tokens": 463
    },
    {
      "id": "ffbceea7504b6455eed11d27",
      "path": "src/gov/impact/__init__.py",
      "text": "\"\"\"The impact of a stated change over the record graph and the code graph (W2-37; CAP-33.b, CAP-33.g, DEC-167).\n\n``assess(root, changes, config)`` takes record ids, symbol names or one plain-language question (\"What's the impact of\nX?\") and returns the impact assessment: the affected specifications, decisions, tickets, tests and code, each with\nthe graph it came from, the radius and the depth it implies (``gov.closure.depth_of_radius``), the gaps, and the\nchange-impact proposal (CIT-P) as frontmatter. The two graphs are joined by id (G-16): a record's edge to no record is\nlooked up as a symbol of the code index, and a symbol reaches the records whose edges name it. ``compare(root, rel)``\nchecks a change-execution record (CIT-E) against the CIT-P it names.\n\nIt only reads. It builds neither the store nor the code index, and a graph that is missing, stale or unreadable is\nsaid, and the report is then never complete. The readings still with the owner are in ``gov.impact.readings``.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport hashlib\nimport re\nimport sqlite3\nimport subprocess\nfrom collections import Counter\nfrom pathlib import Path\n\nfrom gov.cli.errors import GovError\n",
      "tokens": 297
    },
    {
      "id": "S2-CIT-E",
      "path": "docs/changes/S2-CIT-E.md",
      "text": "| DEC-165 | The lite upstream lesson loop, Wave 3; reverses DEC-053 Q7 for framework lessons only | Charter \u00a77 non-goal row; CAP-41 (wave note, provider, `CAP-41.e` reworded, `CAP-41.g`\u2026`CAP-41.j`); `CAP-45.b`; `CAP-58.g`; ADR-0002 \u00a76; WBS \u00a75 and \u00a77 |\n| DEC-166 | `gov discover`, Wave 2 | `CAP-32.d`; ADR-0002 \u00a71 L4 and \u00a76; WBS \u00a75 and \u00a76 |\n| DEC-167 | A plain-language impact question triggers the impact assessment | `CAP-33.f` (W1, W1-35), `CAP-33.g` (W2), CAP-33 wave note; W1-35; ADR-0002 \u00a76; WBS rules, \u00a75 and \u00a76 |\n| DEC-168 | Scope and severity are in W1-08's lesson schema in Wave 1; the loop stays Wave 3 | `CAP-41.f` (W1, W1-08), CAP-41 wave note; W1-08 (one KPI), W1-44 (failure KPI); ADR-0002 \u00a76; WBS \u00a75 and \u00a77 |\n| DEC-169 | The validator: fingerprint fallback for `PROMPT.md` only; `docs/SOURCES.md` excluded from the S2 scope check. Confirmed by the owner as the owner's decision | `validate_s1.py` |\n| DEC-170 | Sandbox instruction tokens are a separate line in W1-31, outside the governance share; whether they count toward the 15 % is decided at the Wave 1 exit, using measured figures | W1-31 (KPI, source); ADR-0002 \"Consequences\"; `bootstrap.md`; WBS \u00a71, \u00a73 |\n",
      "tokens": 295
    },
    {
      "id": "S2-CIT-P",
      "path": "docs/changes/S2-CIT-P.md",
      "text": "| DEC-165 | The lite upstream lesson loop (Wave 3) | Charter v5 \u00a77 non-goal row; CAP-41 (wave note, `CAP-41.e` reworded, `CAP-41.f`\u2026`CAP-41.j`), `CAP-45.b`, `CAP-58.g`; ADR-0002 \u00a76; WBS \u00a77. No Wave 1 ticket changes |\n| DEC-166 | `gov discover` (Wave 2) | `CAP-32.d`; ADR-0002 \u00a71 L4 and \u00a76; WBS \u00a76. No Wave 1 ticket changes |\n| DEC-167 | A plain-language impact question triggers the impact assessment | `CAP-33.f` (W1, W1-35), `CAP-33.g` (W2); one KPI on W1-35; WBS rules and \u00a76 |\n| DEC-168 | Scope and severity in the Wave 1 lesson schema | `CAP-41.f` moves to W1 on W1-08; one KPI on W1-08, the failure KPI of W1-44; WBS \u00a75 and \u00a77 |\n| DEC-169 | The validator's fingerprint fallback and S2 scope check (S2A-F-08) | `validate_s1.py` only |\n| DEC-170 | Sandbox instruction tokens are reported apart from the governance share (S2A-F-07) | One KPI on W1-31, with `CAP-40.d` (added in the round-2 repair); ADR-0002 \"Consequences\"; WBS \u00a71, \u00a73; `bootstrap.md` |\n| DEC-171 | An orchestrator change outside its ticket's paths is a record, not a containment finding (S2A-F-01) | `CAP-58.e`; W1-45 (KPI, source, body); ADR-0002 \u00a76; WBS rules; `bootstrap.md` |\n\n",
      "tokens": 288
    },
    {
      "id": "45eb795fdcef4188c9f73206",
      "path": "docs/contract/contract.yaml",
      "text": "      costed options (apply now, defer, re-baseline); the owner chooses; CIT-E records what was done; every version of the\n      specification is kept\n    source: DEC-105\n    wave: W1\n    provider:\n    - W1-35\n  - id: CAP-33.f\n    item: 'The question \"what is the impact of X?\", asked in plain language, triggers the impact assessment; in Wave 1 that is an OpenSpec proposal plus `gov closure`'\n    source: 'DEC-167'\n    wave: W1\n    provider:\n    - W1-35\n  - id: CAP-33.g\n    item: 'From Wave 2 the same plain-language question runs `gov impact`'\n    source: 'DEC-167'\n    wave: W2\n- id: CAP-34\n  title: Human decision gates and contradiction resolution\n  outcome: The owner receives every question that matters as a ranked decision package in the active chat, and independent\n    branches keep going.\n  acceptance: A high-impact contradiction produces a package in chat with all ten fields (MR-6's eight plus current state\n    and exact permitted next actions), ranked P1\u2013P3 and batched at most five at a time with P1 allowed to bypass; the dependent\n    ticket is blocked; an independent ticket still reaches close; the answer lands as a register entry in git.\n  wave: W1\n  provider:\n  - W1-34\n",
      "tokens": 300
    },
    {
      "id": "cee7f3375bff0dfc03101acc",
      "path": "docs/contract/contract.yaml",
      "text": "  title: Change-impact transactions (CIT-P simulation, CIT-E execution)\n  outcome: An agent can simulate a change before making it (CIT-P) and record what it changed (CIT-E).\n  acceptance: A decision change raises a CIT-P listing the affected specs, decisions, tickets, tests and code from both graphs,\n    with a radius; after apply/archive the CIT-E record matches the proposal or lists the differences.\n  wave: W2\n  wave_note: 'OpenSpec proposal and apply/archive in W1, where a plain-language impact question runs an OpenSpec proposal plus `gov closure` (DEC-167); computed impact W2'\n  provider:\n  - OpenSpec 1.13.2\n  - W1-35\n  - 'W2: gov impact'\n  sources:\n  - Contract v3 Gate K1, K2, K3, K4\n  - Framework v4.1.2 \u00a747-49\n  - DEC-005 (proportionality profiles LITE/STANDARD/FULL)\n  - DEC-035 (radius-scaled budgets/facets)\n  - DEC-011\n  - DEC-066\n  - DEC-105\n  - DEC-167\n  scenarios:\n    dev:\n    - MR-A-05\n    - CIT-A-01\n    - CIT-A-02\n    - MR-B-05\n    - CIT-B-01\n    qual:\n    - MR-A-Q05\n    - CHAOS-A-Q01\n    - CHAOS-A-Q02\n    - CHAOS-A-Q05\n    - CIT-A-Q01\n    - CIT-A-Q02\n    - CIT-A-Q03\n    - A-Q03\n    - AUDIT-A-Q26\n    - AUDIT-A-Q27\n    - AUDIT-A-Q39\n    - SOAK-X-Q01\n  disposition:\n",
      "tokens": 299
    }
  ],
  "supplementary_query": "gov impact\n\"What's the impact of X?\" in plain language runs gov impact [CAP-33.g, DEC-167]. Verify: a planted question \"what is the impact of DEC-NNN?\" given to the plain-language entry runs gov impact on DEC-NNN and prints its result [Verify clause added, DEC-1157 (12)]\nIt also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join). Verify: planted records with mapped ids and a deletable-class row: gov impact resolves the mapped ids (G-16) and joins the deletable class (G-24) in its result [Verify clause added, DEC-1157 (12)]",
  "further_batch": [
    {
      "id": "WAVE-2-LIST",
      "path": "docs/plan/WAVE_2_LIST.md"
    },
    {
      "id": "c953468ede5f557b3f0946d5",
      "path": "docs/plan/tools/validate_s1.py"
    },
    {
      "id": "e8b46dfa0bb02545e2131e2c",
      "path": "governance/project/orchestration/reviews/D10-launch-gate-sweep-review.md"
    },
    {
      "id": "bdcc3ff91bdb24e6967c1a55",
      "path": "docs/changes/W2-20-evidence.md"
    },
    {
      "id": "DAEO-r30l",
      "path": ".tickets/DAEO-r30l.md"
    },
    {
      "id": "a20425c204636d39eee4006d",
      "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md"
    },
    {
      "id": "13393f598e929ea5656c9dda",
      "path": "src/gov/launch/command.py"
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
          "id": "WAVE-1-WBS",
          "path": "docs/plan/WAVE_1_WBS.md"
        },
        {
          "id": "WAVE-2-TRIAGE",
          "path": "docs/plan/WAVE_2_TRIAGE.md"
        },
        {
          "id": "5e5ac8e4e4bcd1e61383b6d2",
          "path": "tests/unit/impact/test_impact.py"
        },
        {
          "id": "3d34b5ddc78a2c586b751523",
          "path": "src/gov/impact/readings.py"
        },
        {
          "id": "CONTRACT-v4",
          "path": "docs/contract/CONTRACT_v4.md"
        },
        {
          "id": "CONTRACT-v4",
          "path": "docs/contract/CONTRACT_v4.md"
        },
        {
          "id": "WAVE-1-WBS",
          "path": "docs/plan/WAVE_1_WBS.md"
        },
        {
          "id": "ffbceea7504b6455eed11d27",
          "path": "src/gov/impact/__init__.py"
        },
        {
          "id": "S2-CIT-E",
          "path": "docs/changes/S2-CIT-E.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "S2-CIT-P",
          "path": "docs/changes/S2-CIT-P.md"
        },
        {
          "id": "45eb795fdcef4188c9f73206",
          "path": "docs/contract/contract.yaml"
        },
        {
          "id": "cee7f3375bff0dfc03101acc",
          "path": "docs/contract/contract.yaml"
        },
        {
          "id": "WAVE-2-LIST",
          "path": "docs/plan/WAVE_2_LIST.md"
        },
        {
          "id": "c953468ede5f557b3f0946d5",
          "path": "docs/plan/tools/validate_s1.py"
        },
        {
          "id": "e8b46dfa0bb02545e2131e2c",
          "path": "governance/project/orchestration/reviews/D10-launch-gate-sweep-review.md"
        },
        {
          "id": "bdcc3ff91bdb24e6967c1a55",
          "path": "docs/changes/W2-20-evidence.md"
        },
        {
          "id": "DAEO-r30l",
          "path": ".tickets/DAEO-r30l.md"
        },
        {
          "id": "a20425c204636d39eee4006d",
          "path": "governance/project/orchestration/packages/LOAD-BALANCER-1.md"
        },
        {
          "id": "13393f598e929ea5656c9dda",
          "path": "src/gov/launch/command.py"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "13393f598e929ea5656c9dda",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-r30l",
      "reason": "budget exceeded"
    },
    {
      "id": "WAVE-2-LIST",
      "reason": "budget exceeded"
    },
    {
      "id": "a20425c204636d39eee4006d",
      "reason": "budget exceeded"
    },
    {
      "id": "bdcc3ff91bdb24e6967c1a55",
      "reason": "budget exceeded"
    },
    {
      "id": "c953468ede5f557b3f0946d5",
      "reason": "budget exceeded"
    },
    {
      "id": "e8b46dfa0bb02545e2131e2c",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from engineer (ticket DAEO-6n5k): 11 paths, 59 chunks; 11 by role_paths.engineer.reads_denied {ticket_tests} (tests/acceptance/W2-37/**) (DEC-1065 (2))"
    }
  ],
  "tokens": 5991,
  "budget": {
    "limit": 6000,
    "used": 5991
  },
  "left_out": {
    "count": 4,
    "superseded": [
      "DEC-038",
      "DEC-798",
      "DEC-875",
      "DEC-876"
    ],
    "done": []
  },
  "hash": "d85b1a15674a89ce1920d4c9720de247c2a587a30518292c5a4c2e030313e0a5"
}
