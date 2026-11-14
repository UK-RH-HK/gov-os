Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

You are a fresh engineer, making an owner-approved version change in a kernel skill (the launcher runs this ticket's workers as engineer; the work is a product-spec kind of change). Ticket: DAEO-6n5k (W2-37, "gov impact"), profile FULL, class C2. You work only in the worktree `/home/usain/gov-os-worktrees/W2-37` on branch `w2/W2-37`, and write only these two files: `template/governance/kernel/skills/change/SKILL.md` and `template/.rulesync/skills/change/SKILL.md`. Never touch `.rulesync/skills/change/SKILL.md` or `.claude/skills/change/SKILL.md` (the CTO's copies ACT makes those).

The owner approved the change skill's impact-section bytes at 13:50 UTC 2026-11-13: "yes W2-37 CIT-P a25b02a7, version 1.1.0". The approved body is the one at commit 68d9a917b (sha256 `a25b02a7c5c8090c2251b945e48b60779ce7c2de7c254ae661a1cb0715932536` for each file); the owner set the version to 1.1.0. The CIT-P names two version lines in each file: `version: "1.0.0"` (line 4) and `metadata.version: "1.0.0"` (line 6, indented `  version: "1.0.0"`).

## Standing rules
- First: `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-6n5k`); `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-37`, `w2/W2-37`); `git rev-parse HEAD` and `git status --short` (expect a clean tree at e8c414b0d). If anything differs, stop and say so.
- `sha256sum` both files before you edit; both must be `a25b02a7c5c8090c2251b945e48b60779ce7c2de7c254ae661a1cb0715932536` today. If not, stop and say so.
- Every pytest runs through the heavy slot, with a TMPDIR outside the repository and outside ~/gov-os-runs (your sandbox's own TMPDIR if `/tmp` is read-only):
  `env TMPDIR=/tmp/gov-os-w237-ps5 PYTHONUSERBASE=/home/usain/.local PATH=/home/usain/.local/bin:/home/usain/.nvm/versions/node/v22.23.3/bin:/usr/local/bin:/usr/bin:/bin PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-37/test_w2_37_skill_routing.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfs`
  (make the TMPDIR first). A slot wait or gate refusal is a wait. Never `-x`.
- Run everything in the foreground. Return only after your commit exists. No checkout, reset, clean, stash, amend, rebase, merge, push or tag. Stage by exact path.
- Write files with the Write and Edit tools and literal absolute paths; anything longer than one line of shell goes in a script under `/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/`. No here-documents.
- Never run `gov rebuild`, `gov close`, `gov adopt`, `gov pause`, `gov retrieve` or `gov context`. Search with Read and Grep; once more in different words if the first does not answer.
- Never read `.claude/settings*.json`, anything under `~/.claude/`, the held-out file under `governance/project/`, the evaluation sets' root, or any hidden or memory-verdict folder. No glob/search/listing over `governance/project/`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so. Never work around a refusal.

## What to change
- In each of the two files, line 4 `version: "1.0.0"` becomes `version: "1.1.0"`, and line 6 `  version: "1.0.0"` becomes `  version: "1.1.0"` (keep the quotes and the two-space indent).
- Nothing else: no other byte in either file changes (the body is owner-approved as it stands). The two files stay byte-equal (`cmp`).

## Check
- `git diff --stat` shows 2 files, 2 insertions and 2 deletions each; `git diff` shows only the four version lines.
- `cmp` the two files; `sha256sum` both after.
- The acceptance file above: `[template]` cases green; `[claude-copy]` stays red (the CTO's copy, made after this: expected).

## Commit (one commit, the two files only)
    git commit -m "W2-37: the change skill's version 1.1.0, as the owner approved the CIT-P (a25b02a7, 2026-11-13)" --trailer "Task: DAEO-6n5k" --trailer "Role: engineer" --trailer "Implements: CAP-33.g, DEC-167" -- template/governance/kernel/skills/change/SKILL.md template/.rulesync/skills/change/SKILL.md
Then show `git log -1 --format='%H%n%B'`, `git status --short`, and `git show HEAD` (the diff verbatim in your return).

## Return (your last message; the twelve fields as labelled lines, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
In `evidence:` the sha256 before and after of both files, the `cmp` result and the diff verbatim. Then `guard_refusals:` (none, or each refusal's command form and reason).

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
