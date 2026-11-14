You are a fresh engineer. Ticket: DAEO-6n5k (W2-37, "gov impact"), profile FULL, class C2. You work only in the worktree `/home/usain/gov-os-worktrees/W2-37` on branch `w2/W2-37`, and write only two files: `src/gov/check/commands.py` and `tests/conftest.py`. This is P-7 (a) of DEC-812 item 6: "W2-37's paths gain `src/gov/check/commands.py` (the `RECORDED_GOV_COMMANDS` line that records `impact` only)", and the CTO's conftest line under DEC-1156 (7): `_CBM_SUITES` gains `"W2-37"`, so W2-37's code-graph cases run with the code-index tool on PATH. `gov impact` is built (`src/gov/impact/command.py`).

## Standing rules
- First: `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-6n5k`); `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-37`, `w2/W2-37`); `git rev-parse HEAD` (expect prefix `f141d6366`); `git status --short` empty. If anything differs, stop and say so.
- Every pytest runs through the heavy slot, with a TMPDIR outside the repository and outside ~/gov-os-runs (your sandbox's own TMPDIR if `/tmp` is read-only), for example:
  `env TMPDIR=/tmp/gov-os-w237-eng6 PYTHONUSERBASE=/home/usain/.local PATH=/home/usain/.local/bin:/home/usain/.nvm/versions/node/v22.23.3/bin:/usr/local/bin:/usr/bin:/bin PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/check tests/unit/accept/test_w2_96_run2.py tests/unit/session_watch/test_route.py tests/acceptance/W1-26/test_w1_26_recorded_commands.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfs`
  (make the TMPDIR first). A slot wait or a memory/CPU/disk gate refusal is a wait. Never `-x`.
- Run everything in the foreground. Return only after your commit exists. No checkout, reset, clean, stash, amend, rebase, merge, push or tag. Stage by exact path.
- Write files with the Write and Edit tools and literal absolute paths; anything longer than one line of shell goes in a script under `/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/`. No here-documents.
- Never run `gov rebuild`, `gov close`, `gov adopt`, `gov pause`, `gov retrieve` or `gov context`. Search with Read and Grep; once more in different words if the first does not answer.
- Never read `.claude/settings*.json`, anything under `~/.claude/`, the held-out file under `governance/project/`, the evaluation sets' root, or any hidden or memory-verdict folder. No glob/search/listing over `governance/project/`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so. Never work around a refusal.

## What to change (nothing else)
1. `src/gov/check/commands.py`: one new line after the `wait` line (:20), in the same form: `RECORDED_GOV_COMMANDS = RECORDED_GOV_COMMANDS + ("impact",)` with a trailing comment naming W2-37 and DEC-812 item 6 (for example `# impact (W2-37, DEC-812 item 6, P-7 (a)): the change's impact query`). Keep the line within the file's existing width (about 120 columns); if the comment does not fit, put it on the line above, as the `brief`/`links`/`plan` line does. Do not change `VERSION` or any other line.
2. `tests/conftest.py`: the `_CBM_SUITES` frozenset (:324) gains `"W2-37"` (keep the existing members and their order; add it after `"W2-92"`). Nothing else in the file.

## Check
- `git diff --stat` shows 2 files, 2 insertions and 1 deletion in all (or 3 insertions if the comment is on its own line); `git diff` shows only these lines.
- Run the pytest example above: every case green except any you can show was red before your change (run it once on the clean tree first if you need the comparison). `tests/acceptance/W1-26/test_w1_26_recorded_commands.py` reads W1-07's lists, which a test designer is changing on another branch; on this branch it has no `impact` case yet: that is expected.
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -m gov.check.commands --help` or the module's own entry, if it has one, still runs (report what you ran).

## Commit (one commit, the two files only)
    git commit -m "W2-37: commands.py records impact (DEC-812 item 6, P-7 (a)); _CBM_SUITES gains W2-37 (DEC-1156 (7))" --trailer "Task: DAEO-6n5k" --trailer "Role: engineer" --trailer "Implements: CAP-33.g, DEC-167" -- src/gov/check/commands.py tests/conftest.py
Then show `git log -1 --format='%H%n%B'`, `git status --short`, and `git show HEAD` (the diff verbatim in your return).

## Return (your last message; the twelve fields as labelled lines, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
In `evidence:` the diff verbatim; in `tests:` the counts and any red with its failure line. Then `guard_refusals:` (none, or each refusal's command form and reason).

## The ticket's context (gov context, built by the lead outside the sandbox)
{
  "ticket": "DAEO-6n5k",
  "ticket_text": "---\nid: DAEO-6n5k\nstatus: in_progress\ndeps: [DAEO-g0ip, DAEO-ym8a]\nlinks: []\ncreated: 2026-10-16T16:35:11Z\ntype: task\npriority: 2\nassignee: engineer\nexternal-ref: W2-37\ntags: [wave-2, implementation, full]\nwbs_id: W2-37\ntitle: gov impact\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-g0ip\n- DAEO-ym8a\nallowed_paths:\n- src/gov/impact/**\n- src/gov/closure/**\n- tests/unit/impact/**\n- template/governance/kernel/skills/change/SKILL.md\n- template/.rulesync/skills/change/SKILL.md\n- src/gov/check/commands.py  # P-7 (a), DEC-812 item 6: the RECORDED_GOV_COMMANDS line records `impact` only\n- tests/acceptance/W1-07/w1_07_support.py  # P-7 (a): W1-07's lists gain `impact`, by a test designer with a Rewrite-Reason\n- tests/acceptance/W1-07/test_w1_07_recorded_commands.py  # the same (its count test renamed)\n- tests/acceptance/W1-07/README.md  # the same\n- tests/acceptance/W1-32/test_w1_32_command_set.py  # P-7 (a): W1-32's command-set assertion gains `impact`\n- tests/conftest.py  # _CBM_SUITES gains W2-37 (its code-graph cases run with the tool on PATH), CTO, DEC-1156 (7)\nkpis:\n  success:\n  - '\"What''s the impact of X?\" in plain language runs gov impact [CAP-33.g, DEC-167]. Verify: a planted question \"what is the impact of DEC-NNN?\" given to the plain-language entry runs gov impact on DEC-NNN and prints its result [Verify clause added, DEC-1157 (12)]'\n  - 'It also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join). Verify: planted records with mapped ids and a deletable-class row: gov impact resolves the mapped ids (G-16) and joins the deletable class (G-24) in its result; G-24''s \"no record names the item\" counts the store''s stated links too (a ticket''s sources and closes, the register''s Under and Changes lines): a planted decision named only by a ticket''s sources is not deletable [Verify clause added, DEC-1157 (12); F1 (a), DEC-1163]'\n  failure: []\n  lifted:\n  - 'A decision change raises a CIT-P that lists the affected specifications, decisions, tickets, tests and code from both graphs, with a radius [CAP-33.b, W2-M285]. [lifted (was S1), DEC-1083: the query only, no CIT-P (INVESTIGATION-1 \u00a75, W-3)]'\n  - 'After apply or archive, the CIT-E record matches the proposal or lists the differences [W2-L319]. [lifted (was S2), DEC-1083: the query only, no CIT-P (INVESTIGATION-1 \u00a75, W-3)]'\nprofile: FULL\nsources:\n- CAP-33.b\n- CAP-33.g\n- DEC-167\n- DEC-1083\nest_loc: 280\nacceptance_tests:\n  path: tests/acceptance/W2-37/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: C\ncloses:\n- CAP-33.b\n- CAP-33.g\n- DEC-167\nlist_rows:\n- W2-L319\n- W2-M056\n- W2-M150\n- W2-M285\n- W2-M320\n---\n# W2-37 gov impact\n\nCard: `docs/plan/WAVE_2_WBS.md` \u00a72 (W2-37), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).\n\n- **Allowed paths:** `src/gov/impact/**` (new), `src/gov/closure/**` (read API only), `tests/unit/impact/**`.\n- **KPIs:**\n  - A decision change raises a CIT-P that lists the affected specifications, decisions, tickets, tests and code from both graphs, with a radius [CAP-33.b, W2-M285].\n  - After apply or archive, the CIT-E record matches the proposal or lists the differences [W2-L319].\n  - \"What's the impact of X?\" in plain language runs `gov impact` [CAP-33.g, DEC-167].\n  - It also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join).\n",
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
  "tokens": 2725,
  "budget": {
    "limit": 6000,
    "used": 2725
  },
  "hash": "0155c32f6ba3a089b3521ea3a180594af6dfceb065d94093b5adf23948990a67"
}
