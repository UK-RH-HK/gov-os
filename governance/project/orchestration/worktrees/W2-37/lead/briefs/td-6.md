You are a fresh independent test designer (MR-3). Ticket: DAEO-6n5k (W2-37, "gov impact"), profile FULL, class C2. You work only in the worktree `/home/usain/gov-os-worktrees/W2-37-tests` on branch `w2/W2-37-tests`. This is P-7 (a) of DEC-812 item 6, as DEC-747 item 1: "W2-37's paths gain `src/gov/check/commands.py` (the `RECORDED_GOV_COMMANDS` line that records `impact` only); its test designer, with a `Rewrite-Reason:`, adds `impact` to W1-07's lists (`w1_07_support.py`, `test_w1_07_recorded_commands.py`, its count test renamed) and to W1-32's command-set assertion." `gov impact` is built (`src/gov/impact/command.py`) and `gov --help` offers it; an engineer adds `impact` to `src/gov/check/commands.py` after you.

## Standing rules
- First: `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-6n5k`); `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-37-tests`, `w2/W2-37-tests`); `git rev-parse HEAD` (expect prefix `f141d6366`); `git status --short` empty. If anything differs, stop and say so.
- DEC-732: every test run uses this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37-tests/src` per command. Quote `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37-tests/src python3 -c "import gov; print(gov.__file__)"` in your return.
- **Every pytest runs through the heavy slot**, with a TMPDIR outside the repository and outside ~/gov-os-runs (your sandbox's own TMPDIR if `/tmp` is read-only), for example:
  `env TMPDIR=/tmp/gov-os-w237-td6 PYTHONUSERBASE=/home/usain/.local PATH=/home/usain/.local/bin:/home/usain/.nvm/versions/node/v22.23.3/bin:/usr/local/bin:/usr/bin:/bin PYTHONPATH=/home/usain/gov-os-worktrees/W2-37-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W1-07/test_w1_07_recorded_commands.py tests/acceptance/W1-32/test_w1_32_command_set.py tests/acceptance/W1-26/test_w1_26_recorded_commands.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfs`
  (make the TMPDIR first with `mkdir -p /tmp/gov-os-w237-td6`). An "all slots taken; waiting" line, or any memory/CPU/disk gate refusal, is a wait, not a refusal. Never `-x`.
- Run everything in the foreground. Return only after your commit exists. No checkout of another commit, reset, clean, stash, amend, rebase, merge, push or tag. Stage by exact path, never `git add -A`/`.`.
- Write files with the Write and Edit tools and literal absolute paths; anything longer than one line of shell goes in a script under `/home/usain/gov-os-worktrees/W2-37-tests/.gov-runtime/scratch/`. No here-documents.
- Never run `gov rebuild`, `gov close`, `gov adopt`, `gov pause`, `gov retrieve` or `gov context`. Search with Read and Grep; search again once in different words if the first does not answer.
- Never read `.claude/settings*.json`, anything under `~/.claude/`, the held-out file under `governance/project/`, the evaluation sets' root, or any hidden or memory-verdict folder. No glob/search/listing over `governance/project/`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so. Never work around a refusal.

## What you change (these four files only; nothing else)
1. `tests/acceptance/W1-07/w1_07_support.py`: `RECORDED_GOV_COMMANDS` records `impact`, one line in DEC-542's form below the existing ones (as the `brief`, `links`, `plan` line at :59-63 does), with a comment naming the revision: W2-37 (DAEO-6n5k), DEC-812 item 6 (P-7 (a)), a recorded rewrite by a fresh test designer (DEC-491). The set stays exact.
2. `tests/acceptance/W1-07/test_w1_07_recorded_commands.py`: the sorted list in the count case (:44-52) gains `"impact"` (ten names), with a revision comment line like the ones above it. **Keep the case's function name** `test_the_recorded_commands_are_four_and_none_is_one_of_the_twelve`, though DEC-812 item 6 says "its count test renamed": the lead found that `tests/optin-lifted-breadth.txt:42` names this function and `tests/unit/optin/test_optin_lifted.py:180` (`test_every_entry_of_the_real_lists_names_a_test_path_or_function_that_exists`) fails on a list entry naming a function that no longer exists; that list is outside the ticket's paths. Say so in the comment (the rename waits on the opt-in list's line; the case keeps its name as it did for DEC-970). The lead reports it. If you find that this reasoning is wrong, say so in your return and still keep the name.
3. `tests/acceptance/W1-07/README.md`: one revision paragraph in the form of the D-10 paragraph at :311, naming what changed (`impact` recorded; ten recorded commands, nine `gov` commands and `lock`; the count case keeps its name and why; `test_a_recorded_gov_command_is_offered_and_answers_its_help` gains `[impact]`; the number of cases in that section). Do not rewrite older paragraphs.
4. `tests/acceptance/W1-32/test_w1_32_command_set.py`: the first assert's set (:103-104) gains `"impact"`, with a sentence added to the case's docstring for this revision (W2-37, DEC-812 item 6, P-7 (a)). Nothing else in the case changes; `RECORDED_HERE` stays as it is.

## Red first (check, do not fix)
Run the three files named in the pytest example above (W1-07 recorded commands, W1-32 command set, W1-26 recorded commands) to their end, before and after your change, and report each case's result both times. Expected after your change, on today's code: the W1-07 and W1-32 cases green (`gov --help` offers `impact`); `tests/acceptance/W1-26/test_w1_26_recorded_commands.py`'s cases parametrised on `[impact]` red because `src/gov/check/commands.py` does not record `impact` yet (the stated reason: the core-commands check does not name a missing `impact` module). Report what you see, with the failure line, whatever it is. You do not change W1-26.

## Commit
    git commit -m "W2-37: W1-07's lists and W1-32's command set record impact (DEC-812 item 6, P-7 (a))" --trailer "Task: DAEO-6n5k" --trailer "Role: independent-test-designer" --trailer "Implements: CAP-33.g, DEC-167" --trailer "Rewrite-Reason: DEC-812 item 6, P-7 (a)" -- tests/acceptance/W1-07/w1_07_support.py tests/acceptance/W1-07/test_w1_07_recorded_commands.py tests/acceptance/W1-07/README.md tests/acceptance/W1-32/test_w1_32_command_set.py
Then show `git log -1 --format='%H%n%B'`, `git status --short` and `git show --stat HEAD`.

## Return (your last message; the twelve fields as labelled lines, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
In `tests:` each case's result before and after your change, with each red's failure line. In `evidence:` the diff verbatim. Then `guard_refusals:` (none, or each refusal's command form and reason).

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
