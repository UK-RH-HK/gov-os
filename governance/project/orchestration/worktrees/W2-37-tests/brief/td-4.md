Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-37-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

You are a fresh independent test designer (MR-3). Ticket: DAEO-6n5k (W2-37, "gov impact"), profile FULL, class C2. You work only in the worktree `/home/usain/gov-os-worktrees/W2-37-tests` on branch `w2/W2-37-tests`. The suite `tests/acceptance/W2-37/` exists and the implementation is committed. The owner decided F1 (a) (DEC-1163 (7)): G-24's "no record names the item" counts the store's stated links too. You add one batch of acceptance cases holding that behaviour, red against the current code, and the README updated to map them. You change no existing case's assertions.

## Standing rules
- First: `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-6n5k`); `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-37-tests`, `w2/W2-37-tests`); `git rev-parse HEAD` (expect prefix `0c266d752`). If anything differs, stop and say so.
- DEC-732: every test run uses this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37-tests/src` per command. Quote `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37-tests/src python3 -c "import gov; print(gov.__file__)"` in your return.
- **Every pytest runs through the heavy slot**, with a TMPDIR outside the repository and outside ~/gov-os-runs (your sandbox's own TMPDIR if `/tmp` is read-only):
  `env TMPDIR=/tmp/gov-os-w237-td4 PYTHONUSERBASE=/home/usain/.local PATH=/home/usain/.local/bin:/home/usain/.nvm/versions/node/v22.23.3/bin:/usr/local/bin:/usr/bin:/bin PYTHONPATH=/home/usain/gov-os-worktrees/W2-37-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-37 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfs`
  (make the TMPDIR first with `mkdir -p /tmp/gov-os-w237-td4`). A "all slots taken; waiting" line, or any memory/CPU/disk gate refusal, is a wait, not a refusal. Never `-x`.
- Run everything in the foreground. Return only after your commit exists. No checkout of another commit, reset, clean, stash, amend, rebase, merge, push or tag. Stage by exact path, never `git add -A`/`.`.
- Write files with the Write and Edit tools and literal absolute paths; anything longer than one line of shell goes in a script under `/home/usain/gov-os-worktrees/W2-37-tests/.gov-runtime/scratch/` (if that is refused, probe through the test file itself). No here-documents.
- Never run `gov rebuild`, `gov close`, `gov adopt`, `gov pause`, `gov retrieve` or `gov context`. Search with Read and Grep; search again once in different words if the first does not answer.
- Never read `.claude/settings*.json`, anything under `~/.claude/`, the held-out file under `governance/project/`, the evaluation sets' root, or any hidden or memory-verdict folder. No glob/search/listing over `governance/project/`.
- Cases that build a code index are marked `local_only` (as the suite does); prefer cases that need no code index (a record-graph item: its deletable reading does not need the code graph). Inside the sandbox the code graph's `/tmp/gov-cbm-<uid>` may be read-only: such cases error at setup; name them, the lead runs them outside.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so. Never work around a refusal.

## What you read
- The ticket's KPI line S2 (in the context below), especially its new Verify clause: "G-24's 'no record names the item' counts the store's stated links too (a ticket's sources and closes, the register's Under and Changes lines): a planted decision named only by a ticket's sources is not deletable".
- The suite and README `tests/acceptance/W2-37/` (fixtures, `w2_37_support.py`, readings R1 to R11; `test_w2_37_deletable.py` holds the existing G-24 cases). Build on its fixtures and helpers. Public interfaces only: the `gov impact` command line and its JSON output (`graphs`, `complete`, `gaps`, `change[].deletable`, `affected`, `radius`), `gov.store.load`, and the store's documented `stated_links` table (`src/gov/store/loader.py` module docstring: frontmatter id keys `CITE_KEYS` such as `sources`/`closes` as CITES, `task` as OF_TASK, and the register's statements: supersession/amendment as SUPERSEDES/AMENDS, `**Under:**` as UNDER). Never read `src/gov/impact/` to learn what a test should expect.

## The behaviour to hold (F1 (a), DEC-1163; a success and a failure each, no combinatorial expansion)
In a temporary repository with a current record graph (store loaded at HEAD, nothing uncommitted):
1. **Named only by a ticket's `sources:`** — a decision DEC-NNN that no edge names, cited only in a ticket record's frontmatter `sources:` list: `gov impact DEC-NNN` gives `change[0].deletable` false, and the radius is not R0. Red on today's code.
2. **Named only by a ticket's `closes:`** — same, cited only in `closes:`. Not deletable.
3. **Named only by a register Under line** — a decision named only through another register entry's `**Under:** DEC-NNN`: not deletable.
4. **Named only by a register supersession/amendment ("Changes") line** — a decision named only by another entry's supersedes/amends statement (use the form the loader reads as SUPERSEDES or AMENDS): not deletable.
5. **Success guard** — a decision that no edge and no stated link names, on a current record graph: still deletable (R0), as today.
Keep it to these; if one of 3/4 cannot be planted so that the store records it in `stated_links` and no edge, say why in the README and return, rather than forcing it.

## What you write
- Only inside `tests/acceptance/W2-37/`: one new file `test_w2_37_stated_links.py` (helpers in it, or added to the support module without changing existing helpers' behaviour), and a README section for this batch mapping each case to the Verify clause, its expected red reason, and which are `local_only`. Deterministic, no network, temporary repositories only.
- Red first: run the suite to its end. The new cases 1 to 4 fail for the stated reason; case 5 passes; every existing case keeps its result (the known reds: the two `test_w2_37_skill_routing.py::test_the_skill_runs_gov_impact_for_the_question` cases).

## Commit
    git commit -m "W2-37: acceptance tests for F1 (a), G-24 counts the store's stated links (red)" --trailer "Task: DAEO-6n5k" --trailer "Role: independent-test-designer" --trailer "Implements: CAP-33.b, DEC-167" --trailer "Rewrite-Reason: test design batch for the owner's F1 (a) (DEC-1163 (7)); no existing case changed" -- tests/acceptance/W2-37
Then show `git log -1 --format='%H%n%B'` and `git status --short`.

## Return (your last message; the twelve fields as labelled lines, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
In `tests:` give each new case with its result (red, green or error at setup) and reason, and the full suite's counts. Then `guard_refusals:` (none, or each refusal's command form and reason).

## The ticket's context (gov context, built by the lead outside the sandbox)
{
  "ticket": "DAEO-6n5k",
  "ticket_text": "---\nid: DAEO-6n5k\nstatus: in_progress\ndeps: [DAEO-g0ip, DAEO-ym8a]\nlinks: []\ncreated: 2026-10-16T16:35:11Z\ntype: task\npriority: 2\nassignee: engineer\nexternal-ref: W2-37\ntags: [wave-2, implementation, full]\nwbs_id: W2-37\ntitle: gov impact\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-g0ip\n- DAEO-ym8a\nallowed_paths:\n- src/gov/impact/**\n- src/gov/closure/**\n- tests/unit/impact/**\n- template/governance/kernel/skills/change/SKILL.md\n- template/.rulesync/skills/change/SKILL.md\nkpis:\n  success:\n  - '\"What''s the impact of X?\" in plain language runs gov impact [CAP-33.g, DEC-167]. Verify: a planted question \"what is the impact of DEC-NNN?\" given to the plain-language entry runs gov impact on DEC-NNN and prints its result [Verify clause added, DEC-1157 (12)]'\n  - 'It also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join). Verify: planted records with mapped ids and a deletable-class row: gov impact resolves the mapped ids (G-16) and joins the deletable class (G-24) in its result; G-24''s \"no record names the item\" counts the store''s stated links too (a ticket''s sources and closes, the register''s Under and Changes lines): a planted decision named only by a ticket''s sources is not deletable [Verify clause added, DEC-1157 (12); F1 (a), DEC-1163]'\n  failure: []\n  lifted:\n  - 'A decision change raises a CIT-P that lists the affected specifications, decisions, tickets, tests and code from both graphs, with a radius [CAP-33.b, W2-M285]. [lifted (was S1), DEC-1083: the query only, no CIT-P (INVESTIGATION-1 \u00a75, W-3)]'\n  - 'After apply or archive, the CIT-E record matches the proposal or lists the differences [W2-L319]. [lifted (was S2), DEC-1083: the query only, no CIT-P (INVESTIGATION-1 \u00a75, W-3)]'\nprofile: FULL\nsources:\n- CAP-33.b\n- CAP-33.g\n- DEC-167\n- DEC-1083\nest_loc: 280\nacceptance_tests:\n  path: tests/acceptance/W2-37/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: C\ncloses:\n- CAP-33.b\n- CAP-33.g\n- DEC-167\nlist_rows:\n- W2-L319\n- W2-M056\n- W2-M150\n- W2-M285\n- W2-M320\n---\n# W2-37 gov impact\n\nCard: `docs/plan/WAVE_2_WBS.md` \u00a72 (W2-37), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).\n\n- **Allowed paths:** `src/gov/impact/**` (new), `src/gov/closure/**` (read API only), `tests/unit/impact/**`.\n- **KPIs:**\n  - A decision change raises a CIT-P that lists the affected specifications, decisions, tickets, tests and code from both graphs, with a radius [CAP-33.b, W2-M285].\n  - After apply or archive, the CIT-E record matches the proposal or lists the differences [W2-L319].\n  - \"What's the impact of X?\" in plain language runs `gov impact` [CAP-33.g, DEC-167].\n  - It also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join).\n",
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
  "supplementary": [],
  "supplementary_query": "gov impact\n\"What's the impact of X?\" in plain language runs gov impact [CAP-33.g, DEC-167]. Verify: a planted question \"what is the impact of DEC-NNN?\" given to the plain-language entry runs gov impact on DEC-NNN and prints its result [Verify clause added, DEC-1157 (12)]\nIt also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join). Verify: planted records with mapped ids and a deletable-class row: gov impact resolves the mapped ids (G-16) and joins the deletable class (G-24) in its result; G-24's \"no record names the item\" counts the store's stated links too (a ticket's sources and closes, the register's Under and Changes lines): a planted decision named only by a ticket's sources is not deletable [Verify clause added, DEC-1157 (12); F1 (a), DEC-1163]",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 2576,
  "budget": {
    "limit": 6000,
    "used": 2576
  },
  "hash": "8c6f6c8cf05bd7885b75048244b526184db008d231a88367065ada360ccba9cb"
}
