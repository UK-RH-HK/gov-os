You are a fresh independent test designer (MR-3). Ticket: DAEO-6n5k (W2-37, "gov impact"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-37-tests` on branch `w2/W2-37-tests`. The suite `tests/acceptance/W2-37/` exists and the implementation is committed; the second independent review found behaviours the suite does not hold (owner's DEC-812: fixed in this resume, a test-design batch first, DEC-136). You add one batch of new acceptance cases holding each behaviour below, red against the current code where the code does not yet hold it, and the README updated to map them. You change no existing case's assertions.

## Standing rules
- First: `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-6n5k`); `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-37-tests`, `w2/W2-37-tests`); `git rev-parse HEAD` (expect prefix `64ccbd0cc`). If anything differs, stop and say so.
- DEC-732: every test run uses this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37-tests/src` per command. Quote `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37-tests/src python3 -c "import gov; print(gov.__file__)"` in your return.
- **Every pytest runs through the heavy slot**, with a TMPDIR outside the repository and outside ~/gov-os-runs:
  `env TMPDIR=/tmp/gov-os-w237-td PYTHONUSERBASE=/home/usain/.local PATH=/home/usain/.local/bin:/home/usain/.nvm/versions/node/v22.23.3/bin:/usr/local/bin:/usr/bin:/bin PYTHONPATH=/home/usain/gov-os-worktrees/W2-37-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-37 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfs`
  (make the TMPDIR first with `mkdir -p /tmp/gov-os-w237-td`). A "all slots taken; waiting" line is a wait, not a refusal. Never `-x`.
- Run everything in the foreground. Return only after your commit exists. No checkout of another commit, reset, clean, stash, amend, rebase, merge, push or tag. Stage by exact path, never `git add -A`/`.`.
- Write files with the Write and Edit tools and literal absolute paths; anything longer than one line of shell goes in a script under `/home/usain/gov-os-worktrees/W2-37-tests/.gov-runtime/scratch/`. No here-documents.
- Never run `gov rebuild`, `gov close`, `gov adopt`, `gov pause`, `gov retrieve` or `gov context`. Search with Read and Grep; search again once in different words if the first does not answer.
- Never read `.claude/settings*.json`, anything under `~/.claude/`, the held-out file under `governance/project/`, the evaluation sets' root, or any hidden or memory-verdict folder. No glob/search/listing over `governance/project/`.
- Cases that build a code index are marked `local_only` (as the suite does); inside the sandbox the code graph's `/tmp/gov-cbm-<uid>` may be read-only: then they error at setup; say which they are, the lead runs them outside.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so. Never work around a refusal.

## What you read
- The ticket's KPI lines (in the context below; note DEC-1083 lifted the CIT-P/CIT-E lines; the query remains, and DEC-812 still asks these fixes).
- The suite and README `tests/acceptance/W2-37/` (fixtures, `w2_37_support.py`, readings R1 to R11). Build on its fixtures and helpers. Public interfaces only: the `gov impact` command line and its JSON output (`graphs`, `complete`, `gaps`, `change`, `affected`, `radius`, `--out`, `--compare`, `matches`, `differences`), `gov.store.load`. Never read `src/gov/impact/` to learn what a test should expect.

## The behaviours to hold (DEC-812 (1) and (2); each a success and a failure, no combinatorial expansion)
1. **A (compare against the proposal as committed).** A CIT-P (listing DEC-002 among its affected decisions) was committed and the store loaded; a CIT-E without DEC-002 gives `matches: false`. Then DEC-002 is removed from the CIT-P file in the working tree, not committed: `--compare` must not report `matches: true` with no differences. Accept either: the comparison uses the proposal as the store/HEAD holds it (so DEC-002 is still a difference), or it refuses / reports not matching while the CIT-P file differs from HEAD, naming the file.
2. **B (a register's first uncommitted entry).** The decision register named by the repository's path map has no entries at HEAD; the store is loaded; a first entry (e.g. DEC-090 with `**Supersedes:** DEC-001`) is added to it and not committed. `graphs.record` must not read `ok`: it reads `stale` (naming the register's path). Include the variant where the register sits in a non-governance namespace of the path map, where the report must not read `complete: true` while missing DEC-090 (`local_only` if a current code graph is needed for `complete` to matter; keep a variant that holds `graphs.record` alone without the code tool). The already-right case (the register holds one entry at HEAD, a further uncommitted entry reads `stale`) stays as a success guard.
3. **C (an incomplete proposal's match carries its incompleteness).** A CIT-P written with `complete: false` (and gaps) and a CIT-E with the same lists: the compare result carries the proposal's `complete: false` and its gaps (it may still say `matches: true`).
4. **E (refusals name their real cause).** `--compare` naming a CIT-P file that does not exist is refused naming that the file is missing (not "lists nothing under affected"). `--out ""` and `--out <an existing folder>` are refused naming the real cause (an empty path; a folder), not "a file is there already". Each still exits 1 with no traceback and writes nothing.
5. **F4 (`--out`'s stem against existing ids).** `--out` whose file stem is an id that already exists in the store (e.g. `CITP-001.md` when CITP-001 is a stored record, written to a new path) is refused naming the clash, and writes nothing.

## What you write
- Only inside `tests/acceptance/W2-37/`: one new file `test_w2_37_resume_findings.py` (helpers in it or added to the support module without changing existing helpers' behaviour), and a README section for this batch mapping each behaviour to its tests, its expected red reason, and which are `local_only`. Deterministic, no network, temporary repositories only.
- Red first: run the suite to its end. The new cases fail for the stated reason where the code lacks the behaviour; every existing case keeps its result (the three known reds stay red: the depth source and the two skill-routing cases).

## Commit
    git commit -m "W2-37: acceptance tests for the second review's findings A, B, C, E and F4 (red)" --trailer "Task: DAEO-6n5k" --trailer "Role: independent-test-designer" --trailer "Implements: CAP-33.b, DEC-167" --trailer "Rewrite-Reason: test design batch for the second review's findings A, B, C, E and F4 (DEC-812, DEC-136); no existing case changed" -- tests/acceptance/W2-37
Then show `git log -1 --format='%H%n%B'` and `git status --short`.

## Return (your last message; the twelve fields as labelled lines, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
In `tests:` give each new case with its result (red, green or error at setup) and reason, and the full suite's counts. Then `guard_refusals:` (none, or each refusal's command form and reason).

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
      "id": "24332afb64239a878b3741a6",
      "path": "tests/acceptance/W2-37/README.md",
      "text": "  word `stale` where the graph is stale), or a refusal whose error names the graph (`record`/`store` or `code`). A\n  report that reads the changed state as it is now and lists the late item is accepted too: nothing is dropped.\n- **R5. G-16, the id mapping.** A record's typed edge whose target is no record but a symbol of the code index\n  joins the two graphs (DEC-391 leaves such an edge `UNRESOLVED`, and follows no record-to-symbol edge). From the\n  symbol, callers and callees are followed as `gov closure` follows them. Back the other way, a symbol's change\n  reaches the records that name it. A mention in prose is no edge (DEC-391: no text scan). Package P-3.\n- **R6. KPI 2.** The CIT-E names its CIT-P by id in `proposal` (as `docs/changes/S2-CIT-E.md` does); both carry the\n  five lists in `affected` in their frontmatter (the kernel schemas allow keys beyond the shared frontmatter). The\n  CIT-P is found through the record store. Package P-2.\n- **R7. KPI 3.** The question is one argument of `gov impact`; it gives the same assessment as the id it names.\n- **R8. G-24, the deletable-class join.** \"Deletable\" is the S0b2 query class (W2-L322) whose code half the code\n",
      "tokens": 295
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
      "id": "e37ef54c115a6f743f6a8ad1",
      "path": "tests/acceptance/W2-37/README.md",
      "text": "### KPI 4: the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join)\n\n| Test | Holds | Today |\n|---|---|---|\n| G-16: `test_w2_37_code_graph.py` (7, `local_only`), and `test_w2_37_incomplete.py::test_an_unreadable_code_graph_is_said_and_the_record_side_still_given` | Reading R5 (above) | error: not built |\n| G-24: `test_w2_37_deletable.py::test_a_decision_nothing_links_is_deletable_and_affects_nothing` | DEC-050: `deletable: true`, nothing affected | error: not built |\n| `\u2026::test_a_decision_others_depend_on_is_not_deletable` | DEC-001: `deletable: false` | error: not built |\n| `\u2026::test_the_radius_of_a_deletable_change_is_below_that_of_a_wide_one` | radius(DEC-050) < radius(DEC-001) | error: not built |\n| `\u2026::test_a_symbol_nothing_calls_and_no_record_names_is_deletable` (`local_only`) | w37_orphan (has a callee, no caller, a prose mention only): deletable | error: not built |\n| `\u2026::test_a_symbol_nothing_calls_but_a_record_names_is_not_deletable` (`local_only`) | The join: w37_named_only is dead code to the code graph, but DEC-051 names it: not deletable, DEC-051 listed | error: not built |\n",
      "tokens": 278
    },
    {
      "id": "7f47d77621ec26e0abde5d56",
      "path": "tests/acceptance/W2-37/test_w2_37_deletable.py",
      "text": "\"\"\"The S0b2 glue G-24: \"gov impact's radius needs the deletable-class join\" (WAVE_2_TRIAGE.md).\n\nReading R8 (package P-3): the \"deletable\" class is the query class of S0b2's dev queries (W2-L322, DEC-388) that\nasks whether something can be removed; the code index answers its code half (\"dead code\", W1-16). The join: an item\nis deletable only when **neither** graph has anything that depends on it: no symbol calls it and no record names\nit by an edge. What it depends on itself does not count. Each entry of ``result.change`` carries ``deletable``.\nThe radius of a change nothing depends on is lower than that of a change that reaches all five kinds.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport pytest\n\nimport w2_37_support as support\n\n\n",
      "tokens": 186
    },
    {
      "id": "cb87bc643995275340afd409",
      "path": "tests/acceptance/W2-37/README.md",
      "text": "## The interface the tests assume\n\nThe sources fix the command's name (`gov impact`, CAP-33.g, DEC-167), the five kinds, the two graphs, the radius\n(R0 to R3+, DEC-035) and the depth it implies (DEC-391). They do not fix the output's form. The tests take the\nfollowing, named once in `w2_37_support.py` (\"The interface the tests assume\") so that a package that renames a key\nchanges one line. **Package P-6** asks for it to be confirmed.\n\n```\ngov impact [--json] [--root <path>] [--out <path>] <change>...       an impact assessment, and the CIT-P\ngov impact [--json] [--root <path>] --compare <CIT-E path>           the CIT-E checked against its CIT-P\n```\n\nA `<change>` is a record id, a symbol name, or one plain-language question.\n\n`result` of an assessment:\n\n| Key | What the tests hold it to |\n|---|---|\n| `change` | The stated change: a list of maps, each with `id` and `graph`, `deletable` (G-24) and `governance` (W2-M150). The stated change itself is not listed in `affected` (reading R1). |\n| `radius` | `R0`, `R1`, `R2`, `R3` (or `R3+`). |\n| `depth` | A whole number: the depth the radius implies, equal to `gov closure --radius <n>`'s `depth`. |\n",
      "tokens": 290
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
    }
  ],
  "supplementary_query": "gov impact\n\"What's the impact of X?\" in plain language runs gov impact [CAP-33.g, DEC-167]. Verify: a planted question \"what is the impact of DEC-NNN?\" given to the plain-language entry runs gov impact on DEC-NNN and prints its result [Verify clause added, DEC-1157 (12)]\nIt also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join). Verify: planted records with mapped ids and a deletable-class row: gov impact resolves the mapped ids (G-16) and joins the deletable class (G-24) in its result [Verify clause added, DEC-1157 (12)]",
  "further_batch": [
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
      "id": "c090b872693eb944f96de9d0",
      "path": "tests/acceptance/W2-37/test_w2_37_skill_routing.py"
    },
    {
      "id": "fc7efea0497257413422c878",
      "path": "tests/acceptance/W2-37/test_w2_37_skill_routing.py"
    },
    {
      "id": "e8b46dfa0bb02545e2131e2c",
      "path": "governance/project/orchestration/reviews/D10-launch-gate-sweep-review.md"
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
          "id": "24332afb64239a878b3741a6",
          "path": "tests/acceptance/W2-37/README.md"
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
          "id": "e37ef54c115a6f743f6a8ad1",
          "path": "tests/acceptance/W2-37/README.md"
        },
        {
          "id": "7f47d77621ec26e0abde5d56",
          "path": "tests/acceptance/W2-37/test_w2_37_deletable.py"
        },
        {
          "id": "cb87bc643995275340afd409",
          "path": "tests/acceptance/W2-37/README.md"
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
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "ffbceea7504b6455eed11d27",
          "path": "src/gov/impact/__init__.py"
        },
        {
          "id": "S2-CIT-E",
          "path": "docs/changes/S2-CIT-E.md"
        },
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
          "id": "c090b872693eb944f96de9d0",
          "path": "tests/acceptance/W2-37/test_w2_37_skill_routing.py"
        },
        {
          "id": "fc7efea0497257413422c878",
          "path": "tests/acceptance/W2-37/test_w2_37_skill_routing.py"
        },
        {
          "id": "e8b46dfa0bb02545e2131e2c",
          "path": "governance/project/orchestration/reviews/D10-launch-gate-sweep-review.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "45eb795fdcef4188c9f73206",
      "reason": "budget exceeded"
    },
    {
      "id": "S2-CIT-P",
      "reason": "budget exceeded"
    },
    {
      "id": "WAVE-2-LIST",
      "reason": "budget exceeded"
    },
    {
      "id": "c090b872693eb944f96de9d0",
      "reason": "budget exceeded"
    },
    {
      "id": "c953468ede5f557b3f0946d5",
      "reason": "budget exceeded"
    },
    {
      "id": "cee7f3375bff0dfc03101acc",
      "reason": "budget exceeded"
    },
    {
      "id": "e8b46dfa0bb02545e2131e2c",
      "reason": "budget exceeded"
    },
    {
      "id": "fc7efea0497257413422c878",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from independent-test-designer (ticket DAEO-6n5k): 3 paths, 14 chunks; 2 by role_paths.independent-test-designer.reads_denied {ticket_impl} (src/gov/impact/**); 1 by role_paths.independent-test-designer.reads_denied {ticket_impl} (tests/unit/impact/**) (DEC-1065 (2))"
    }
  ],
  "tokens": 5777,
  "budget": {
    "limit": 6000,
    "used": 5777
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
  "hash": "6faf068a9f70f7a9ae6db95da059c246c2be814de1f5f6a0455a8f71850a14f1"
}
