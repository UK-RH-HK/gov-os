# Brief rev-2: independent auditor (STANDARD review, round 2, the last: DEC-1010) for DAEO-neam (W2-45), class C2

You are the independent auditor for ticket DAEO-neam (W2-45): `gov check` runner semantics and scale. Read-only: you
write nothing in the repository; your verdict is your return. Probe head `b13789476a9c` of branch `w2/W2-45` (check it
is unchanged when you start and when you finish: `git -C /home/usain/gov-os-worktrees/W2-45 rev-parse HEAD`). You are
a fresh session. Round 1 (another auditor) ran at `0653dc01086e` and returned FAIL. This is round 2, the last: there
is no third round, so judge what is in front of you, the whole ticket change, and the round-1 fixes first.

## Step 0, before any work: the sandbox check (report it first in `evidence`)
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-neam','w').write('x')"` must FAIL.
- (b) `printenv GOV_ROLE GOV_TICKET` must print `independent-auditor`, `DAEO-neam`.
If (a) wrote the file or (b) differs, stop and return ESCALATION with what you saw. Delete nothing.

## Round 1's findings and what the CTO decided (P-W2-45-3 (a))
- **F1 (major, S1):** on a planted 200-decision, 20,000-commit history with merges, the decision checker took 132.8 s
  (3,300 merges, one in six) / 285.9 s (6,600 merges) against the 60 s budget: only one-parent commits were passed over,
  every merge was read for every decision. Decided: fix in this round.
- **F2 (minor, S5):** an interrupted runner (Ctrl-C, any exception other than the timeout) left the check's process
  group running (it runs in its own session). **F3 (minor, S5, row W2-L167):** a limit above about 2,147,483 s gave an
  `OverflowError` traceback and left the group running. Decided: stop the group on any exception; the traceback itself
  stays the row W2-L167.
- **F4 to F6 (minor) are recorded rows, not findings of this round:** F4 "unmeasured" as a string value / nested deeper /
  on stderr only is GREEN (outside accepted Interface item 4); F5 test gaps ("unmeasured" inside another word, `_stop`'s
  escaped-descendant branch); F6 `CHECK_TOOL_ABSENT` names the literal first word (`cd`), built-ins state
  `time_limit_s` 60 with no limit applied. Do not re-raise them; say only if the fix round made one worse.

## What to read
| what | path / command |
|---|---|
| ticket (KPI lines S1-S5 are the spec; `## Interface` items 1-8, accepted as P-W2-45-1; the widenings; run 3's packages) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-neam.md (its text is also in the context packet below) |
| the fix round (round 1's head to this head) | `git -C /home/usain/gov-os-worktrees/W2-45 diff 0653dc01086e HEAD -- src/ tests/` (the merge of w2/integrate in between brings other tickets' files: restrict to the ticket's paths) |
| the whole ticket change | `git -C /home/usain/gov-os-worktrees/W2-45 diff w2/integrate...HEAD` (only the ticket's paths plus tests/acceptance/W2-45/ and the W1-40 file) |
| the fix commits | eng-3: `fbb137dd3` (F1, checker.py: `_changes` with `--diff-merges=separate`, `_approved` passes over merges that leave the file as every parent has it), `a95790aa9` (F2/F3, runner.py `except BaseException: _stop(process); raise`); td-4: `100015249` (acceptance: S1 on a merge history, S5 group stopped on interrupt and huge limit), `11f2e8165` (W1-40 revision, DEC-1153 (1)); lead's merge `b13789476` |
| acceptance tests (independent test designer) | tests/acceptance/W2-45/ (README.md first) |
| unit tests (engineer) | tests/unit/check/test_w2_45_checker_speed.py, tests/unit/check/test_w2_45_runner_semantics.py |
| sources (read by id in docs/DECISION_REGISTER.md; grep only by id) | DEC-729; also DEC-595 (TIMEOUT_S 60), DEC-398 and DEC-418 (the merge rule the checker follows), DEC-1010 (review rounds) |

Search with Read, Grep and Glob; if a first search does not answer, search once more in different words, then answer
from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context`.

## What to probe (at least these; find more)
1. **F1 fixed, and no finding lost.** The decision checker on a planted 200-decision, 20,000-commit history with one
   merge in six (and, if time allows, one in three) runs well inside 60 s (time `python3 -m gov.check.authority` in it,
   or core-authority's `elapsed_s` through `gov check --json`). Findings identical to the checker with the pass turned
   off on adversarial merge histories: a merge bringing the file from one side; a merge changing the file itself
   (evil merge); `-s ours` merges; octopus merges; a merge whose diff against every parent is empty; a commit naming a
   parent twice; moves and deletes on a side branch; several merge bases; a merge `read_merge` cannot read; a non-UTF-8
   path. Can a merge be passed over that the merge rule (DEC-398, DEC-418) would have read differently? Is the
   "path in none of its diffs" reasoning right when git prints no header for an empty diff, or with `--no-renames`?
2. **F2/F3 fixed.** Interrupt `gov check` (SIGINT) mid-check: no process of the check's group survives; a huge
   `timeout-seconds`: no survivor (the traceback is the row W2-L167). Can `_stop` on the exception path itself raise
   and hide the original exception, or signal anything outside the check's group?
3. **S1-S5 still hold** against Interface items 1-8 (round 1 found them met apart from F1-F6); item 8 unchanged.
4. **The new tests:** would they catch a wrong fix (reasoned, or a planted mutation on a `git archive` copy under your
   TMPDIR, never in the tree)? Is the merge-history S1 case honest about its shape (merge count, revisions on side
   branches)? Are the S5 group cases free of leaks and flakiness (pid reuse, zombies counted as alive)?
5. Paths and roles: `git diff --name-only w2/integrate...HEAD` within allowed_paths plus tests/acceptance/W2-45/;
   engineer commits touch only src/ and tests/unit/check/; test-designer commits only tests/acceptance/ and the
   revised W1-40 file, with `Rewrite-Reason` on the revision; each commit's `Task: DAEO-neam` and `Implements: DEC-729`.

Runs: planted folders only (pytest's tmp_path or your TMPDIR), never ~/gov-os-runs, ~/.claude or the real store. Your
read-only probes are allowed at any hour (DEC-1144 (7)). Every pytest goes through the heavy-slot gate, one file per run,
with a TMPDIR outside the repository and outside ~/gov-os-runs: your sandbox's own temp folder (`printenv TMPDIR`, then
write it literally): `mkdir -p <TMPDIR>/W2-45-rev2/home` once, then
`TMPDIR=<TMPDIR>/W2-45-rev2 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=<TMPDIR>/W2-45-rev2/home PYTHONUSERBASE=/home/usain/.local GOV_TESTS_OPTIN=lifted,breadth PYTHONPATH=/home/usain/gov-os-worktrees/W2-45/src python3 -m pytest <file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -p no:xdist`
A heavy-slot, memory or CPU gate refusal is a wait: run it again later. In-process probes with `python3 -I` against
the read-only tree are fine. No here-document, no backticks, no `bash -c`; a script longer than a line goes under your
TMPDIR. **Refused twice for the same call: stop and say so**; never reach the same effect by another form (DEC-1142 (9)).

The lead's runs at `b13789476a9c` (claims to check, not to trust):
- `gov accept W2-45`: pass, 38 passed, 0 failed.
- lead_verify (scoped selection): GREEN, 5044 tests, 0 failed, 6 skipped.
- tests/acceptance/W2-45 + W1-40 + the two W2-45 unit files + tests/unit/ci/test_ci_command.py: 196 passed.
- eng-3's timings of `python3 -m gov.check.authority` on its own planted 3,300-merge history: 178.4 s before, 19.3 to
  23.8 s after (load 10 to 20); linear 20,000 commits 9.3 s before, 10.2 s after. 600 random merge histories: 0
  mismatches against the checker with the pass stubbed off.

Known (do not count them as findings):
- `tests/acceptance/W1-21/test_w1_21_merge.py::test_several_batches_are_reranked_in_one_pass_over_the_merged_set` and
  `::test_a_rerank_over_more_than_thirty_candidates`: red at this head and at the base `0098b58d5` alike (retrieval's
  rerank cap; no retrieval file is in the change).
- F4 to F6 above (rows). The `src/gov/ci/command.py` `TOOL_ABSENT` discovery from round 1 (outside the paths; a row).

## Severity
Blocking: an honest operator running `gov check` can hit it and it fails open (a check reported GREEN that has a
finding, is unmeasured, or whose tool is absent; a hard-block key accepted on a warning-only cover; a check left running
past its limit or a process outside its group signalled; a decision-checker finding lost by the speed work). Major: a
KPI line or Interface item not met but failing closed. Minor: everything else (a test gap, wording, an edge that fails
closed). The verdict is FAIL if any finding is blocking or major; else PASS. For each blocking or major finding say what
would reverse it (a fix and its size, or an owner ruling).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE or ESCALATION) / work_completed /
files_changed (none) / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then a fenced verdict block:
```
verdict: PASS | FAIL
head: <hash12>
findings: <n>
- <id> | <severity: blocking, major, minor> | <KPI line> | <file:line> | <what is wrong, the planted input and the wrong output>
```
Then `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).

The ticket's context packet (`gov context DAEO-neam --role independent-auditor`, built by your lead) follows.

{
  "ticket": "DAEO-neam",
  "ticket_text": "---\nid: DAEO-neam\nstatus: in_progress\ndeps: [DAEO-g0ip]\nlinks: []\ncreated: 2026-10-16T16:35:12Z\ntype: task\npriority: 4\nassignee: engineer\nexternal-ref: W2-45\ntags: [wave-2, implementation, standard]\nwbs_id: W2-45\ntitle: gov check runner semantics and scale\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-g0ip\nallowed_paths:\n- src/gov/check/runner.py\n- src/gov/check/commands.py\n- src/gov/decisions/checker.py\n- tests/unit/check/**\n- tests/acceptance/W2-95/test_w2_95_adopted_and_gov_check.py  # one test-designer revision: _others() leaves out elapsed_s (Rewrite-Reason: P-W2-45-1 item 2; DEC-1148 (4))\n- tests/unit/ci/test_ci_command.py  # one revision: line 80 == \"RED\" and line 73's comment (Rewrite-Reason: P-W2-45-1 item 5; DEC-1148 (4))\n- docs/probes/DAEO-neam/**  # the probe record (P-W2-45-5 (a), the CTO, 2026-11-12)\n- tests/acceptance/W1-40/test_w1_40_ci_unmeasured.py  # one test-designer revision: line 49 and its docstring, Rewrite-Reason P-W2-45-1 item 5 (DEC-1153 (1))\nkpis:\n  success:\n  - 'The decision checker runs within the gov check budget on a 200-decision, 20k-commit repository Verify: a planted repository of 200 decisions and 20,000 commits: `gov check` runs the decision checker and its recorded time is within the gov check budget (the budget''s value printed beside it) [W2-H018].'\n  - 'A check that exits 0 with findings, or with \"unmeasured\" in its result, is not green Verify: planted checks, one exiting 0 with a finding and one exiting 0 with \"unmeasured\" in its result: both are reported not green; a planted clean check exiting 0 is green [W2-M129, W2-M212].'\n  - 'An absent tool of a hard-block check is red, not yellow Verify: a planted hard-block check whose tool is absent from the path: its result is red, never yellow [W2-M130, W2-M265].'\n  - 'A hard-block key is covered only by a check of hard-block tier Verify: a planted check map that covers a hard-block key only by a check of a lower tier is refused naming the key; the same key covered by a hard-block-tier check is accepted [W2-M211, W2-M259].'\n  - 'The time limit is stated and tested Verify: the limit''s value is printed in the runner''s result, and a planted check that runs past it is stopped and reported as timed out, by a unit test [W2-M151].'\n  failure: []\nprofile: STANDARD\nsources:\n- DEC-729\nest_loc: 160\nacceptance_tests:\n  path: tests/acceptance/W2-45/\n  author: independent-test-designer (MR-3); written before implementation\ntrack: C\ncloses:\n- W2-H018\nlist_rows:\n- W2-H018\n- W2-L096\n- W2-L098\n- W2-L104\n- W2-L118\n- W2-L167\n- W2-L168\n- W2-L169\n- W2-L171\n- W2-L223\n- W2-M063\n- W2-M128\n- W2-M129\n- W2-M130\n- W2-M131\n- W2-M132\n- W2-M144\n- W2-M146\n- W2-M151\n- W2-M170\n- W2-M211\n- W2-M212\n- W2-M259\n- W2-M265\n- W2-M268\n- W2-M315\n---\n# W2-45 gov check runner semantics and scale\n\n**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** K8 (DEC-941); W2-26 found no trigger (indexing about 30 % of the envelope).\n\nCard: `docs/plan/WAVE_2_WBS.md` \u00a72 (W2-45), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).\n\n- **Allowed paths:** `src/gov/check/runner.py`, `src/gov/check/commands.py`, `src/gov/decisions/checker.py` (speed only), `tests/unit/check/**`.\n- **KPIs:**\n  - The decision checker runs within the `gov check` budget on a 200-decision, 20k-commit repository [W2-H018].\n  - A check that exits 0 with findings, or with \"unmeasured\" in its result, is not green [W2-M129, W2-M212].\n  - An absent tool of a hard-block check is red, not yellow [W2-M130, W2-M265].\n  - A hard-block key is covered only by a check of hard-block tier [W2-M211, W2-M259].\n  - The time limit is stated and tested [W2-M151].\n\n## Interface (DEC-1052; P-W2-45-1 accepted as a whole, item 5 as written: an absent tool of a hard-block check is RED, openspec included; the CTO, 2026-11-12 12:58)\n\nProposal (all in src/gov/check/runner.py unless named):\n\n1. **Tier = the declaration's `severity`.** \"Hard-block tier\" means `severity: hard-block`. `tier:` (G0-G5) is not read.\n2. **Time fields (S1, S5).** Every check result gains `elapsed_s` (wall seconds, float) and `time_limit_s` (the limit\n   applied: its `timeout-seconds`, else `TIMEOUT_S`). The runner's result gains top-level `time_limit_s` (= `TIMEOUT_S`,\n   60, DEC-595). Built-in checks carry both too.\n3. **S1, the budget.** The `gov check` budget of the decision checker is the time limit of the check that runs it,\n   core-authority: 60 s (TIMEOUT_S; its declaration states none). Verified by a planted repository of 200 decision\n   records and 20,000 commits (built with `git fast-import`) holding the core-authority declaration: `gov check --json`\n   exits, and core-authority's entry has `elapsed_s` < `time_limit_s`, both printed. Speed work only in\n   `src/gov/decisions/checker.py`.\n4. **S2, not green.** A check is GREEN only when it exits 0 with no finding. Exit 0 also yields findings when: the\n   success form `{\"ok\": true, \"result\": R}` has a non-empty `R.findings`; or any JSON mapping in the output (top level\n   or R) has `\"unmeasured\": true` -> finding `CHECK_UNMEASURED` with its `reason`; or non-JSON output contains the word\n   \"unmeasured\" -> `CHECK_UNMEASURED`. Status from findings as now: RED if hard-block, YELLOW if warning.\n5. **S3, absent tool.** Exit code 127, or OSError on start -> finding `CHECK_TOOL_ABSENT` naming the command's first\n   word; RED when hard-block (never YELLOW), YELLOW when warning. The built-in `openspec-validate` (hard-block) follows\n   the same rule: `OPENSPEC_ABSENT` becomes RED. (Cost: a machine without openspec gets a red `gov check`; openspec\n   and gitleaks are installed here. Alternative (b): leave openspec YELLOW, named as a residual against S3.)\n6. **S4, tier coverage.** A path-map policy key of strength hard-block whose covering declarations (`enforces`) are all\n   of severity warning -> a `policy-<key>` result, severity hard-block, RED, finding `POLICY_TIER_TOO_LOW` with\n   `policy`, `checks` (the covering ids) and a message naming the key. \"Refused\" = that RED result and `gov check`'s\n   non-zero exit (unchanged). One hard-block declaration covering it -> no policy result (accepted). An uncovered key\n   keeps `POLICY_NOT_COVERED`.\n7. **S5, time limit.** A check past its limit is stopped with its whole process group (`start_new_session=True`,\n   `killpg` on timeout, so a grandchild holding the pipe cannot keep the runner waiting) -> finding `CHECK_TIMED_OUT`\n   (was `CHECK_FAILED`) carrying `time_limit_s`; status by severity. Unit test in `tests/unit/check/` (engineer): a\n   planted check `sleep 30` with `timeout-seconds: 1` -> `CHECK_TIMED_OUT`, `time_limit_s` 1 printed, ends in < 10 s.\n8. **Unchanged:** family roll-up, `gov check`'s exit code rule, the not-applicable (exit 2) path, `commands.py`\n   (W2-159's line kept; touched only if a module list needs it).\n\n## Widened by the owner (DEC-1148 (4), P1-J (a), 2026-11-12)\n\nTwo older tests assert what the accepted Interface changed: R1 (W2-95's `_others()`, `elapsed_s` is a wall time) by the test designer; R2 (`test_ci_command.py:80`, OPENSPEC_ABSENT is RED) by the engineer or designer. One revision each, each with its Rewrite-Reason; nothing else in either file changes.\n\n## Run 3's packages (2026-11-12)\n\n- **P-W2-45-3 (a)** (the CTO, delegated P2): a fix round inside the paths: a test-design batch (a history with one merge in six, an interrupt case), one engineer (`checker.py` passes over merges whose parents hold the decision's file unchanged; `runner.py` stops the group on any exception: F2, F3), then review round 2, the last (DEC-1010). F4 to F6 are rows.\n- **P-W2-45-5 (a)** (the CTO): the probe folder added.\n- **P-W2-45-4** (the W1-40 case, a widening): with the owner.\n\n## P-W2-45-4 decided (the owner, DEC-1153 (1), 2026-11-12)\n\n(a): `tests/acceptance/W1-40/test_w1_40_ci_unmeasured.py` added for one test-designer revision: line 49 expects a non-zero exit and RED, its docstring (lines 46-47) says so, `Rewrite-Reason: P-W2-45-1 item 5`; nothing else in the file changes. It rides run 4's batch with P-W2-45-3 (a).\n",
  "authority": [
    {
      "id": "DEC-729",
      "sha256": "b80ca7150e12e284beaf21a790ac312a9b77b18274523b12ff328e0c04e1cebb",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b80ca7150e12e284beaf21a790ac312a9b77b18274523b12ff328e0c04e1cebb",
      "reason": "declared in sources",
      "tokens": 358
    },
    {
      "id": "DAEO-g0ip",
      "sha256": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "reason": "declared in sources",
      "tokens": 444
    }
  ],
  "mandatory": [
    {
      "id": "DEC-729",
      "sha256": "b80ca7150e12e284beaf21a790ac312a9b77b18274523b12ff328e0c04e1cebb",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b80ca7150e12e284beaf21a790ac312a9b77b18274523b12ff328e0c04e1cebb",
      "reason": "declared in sources",
      "tokens": 358
    },
    {
      "id": "DAEO-g0ip",
      "sha256": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "2c22d5a59d1808d3845f8b8acf122da18a2a75971bd062d588936eb621c08d4a",
      "reason": "declared in sources",
      "tokens": 444
    }
  ],
  "supplementary": [
    {
      "id": "WAVE-2-TRIAGE",
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "text": "| W2-M257 | human_gate gap: a gate never written as a decision package | medium | W2-12 | Named in W2-12's KPIs (owner approval facts and gov approve). |\n| W2-M258 | How the system knows a register entry is the owner's (owner-signed decisions) | medium | W2-12 | Named in W2-12's KPIs (owner approval facts and gov approve). |\n| W2-M259 | A hard-block policy key is covered by any declaring check | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |\n| W2-M260 | Type with absent schema file not reported unmeasured | medium | W2-02 | Named in W2-02's KPIs (record types). |\n| W2-M261 | rulesync writes no env block; adopted projects elsewhere lack auto-compact window | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |\n| W2-M262 | Close's test-runner cases and secrets scan fail under concurrent machine load | medium | W2-20 | Named in W2-20's KPIs (machine-wide resource gate). |\n| W2-M263 | product-traceability-trailers red 'nothing is judged' right after adoption | medium | W2-07 | Re-triaged from W2-01 (DEC-738 item 4): RED stays when nothing comes after the base (DEC-479; W1-30's test); W2-07 owns the close's telemetry and reporting. |\n",
      "tokens": 294
    },
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "#### W2-45 `gov check` runner semantics and scale (STANDARD, engineer)\n- **Wave 3 (DEC-953, DEC-954).** K8 (DEC-941). W2-26 found no trigger: EXAMIN's indexing is about 30 % of the envelope. If W2-88's assessment of a large repository finds one, it is a package.\n- **Allowed paths:** `src/gov/check/runner.py`, `src/gov/check/commands.py`, `src/gov/decisions/checker.py` (speed only), `tests/unit/check/**`.\n- **KPIs:**\n  - The decision checker runs within the `gov check` budget on a 200-decision, 20k-commit repository [W2-H018].\n  - A check that exits 0 with findings, or with \"unmeasured\" in its result, is not green [W2-M129, W2-M212].\n  - An absent tool of a hard-block check is red, not yellow [W2-M130, W2-M265].\n  - **`openspec-validate` measures something or says it does not apply:** real openspec content that it validates, or an owner decision that declares it not applicable here, stated by the check; never silently yellow [W2-H061, DEC-781].\n  - A hard-block key is covered only by a check of hard-block tier [W2-M211, W2-M259].\n  - The time limit is stated and tested [W2-M151].\n\n",
      "tokens": 275
    },
    {
      "id": "WAVE-2-TRIAGE",
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "text": "| W2-M263 | product-traceability-trailers red 'nothing is judged' right after adoption | medium | W2-07 | Re-triaged from W2-01 (DEC-738 item 4): RED stays when nothing comes after the base (DEC-479; W1-30's test); W2-07 owns the close's telemetry and reporting. |\n| W2-M264 | gov doctor reports version drift without failing on it | medium | W2-22 | Named in W2-22's KPIs (gov doctor green). |\n| W2-M265 | Runner reports an absent tool of a hard-block check as red? | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |\n| W2-M266 | Moving the citations base takes earlier commits out of judgement unreported | medium | W2-01 | Named in W2-01's KPIs (gov close and traceability). |\n| W2-M267 | Any Markdown file with decision id in frontmatter counts as its record | medium | W2-03 | Named in W2-03's KPIs (decisions as records). |\n| W2-M268 | Project states on purpose that it declares no G3 check | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |\n| W2-M269 | Fetch and merge evidence notes before writing, for multiple clones | medium | W2-43 | Named in W2-43's KPIs (CI and secret floor). |\n",
      "tokens": 282
    },
    {
      "id": "WAVE-2-TRIAGE",
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "text": "| W2-M140 | Several tools pass doctor by version only, not by hash | medium | W2-22 | Named in W2-22's KPIs (gov doctor green). |\n| W2-M141 | core-graph red: depends_on names W1 ids, not record ids | medium | W2-03 | Fits W2-03's paths and KPIs (decisions as records); its builder takes it. |\n| W2-M142 | retrieval-regression and context-reproducibility unmeasured here | medium | W2-08 | Named in W2-08's KPIs (hooks back on). |\n| W2-M143 | secrets-indexing exceeds the runner's 60-second limit on this tree | medium | W2-06 | Named in W2-06's KPIs (fast pre-commit tier and re-index). |\n| W2-M144 | Five policy keys have no associated check | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |\n| W2-M145 | Decision-citations check accepts any frontmatter id or register heading as a record | medium | W2-03 | Named in W2-03's KPIs (decisions as records). |\n| W2-M146 | Decision-citations check says clean without reporting its measurement scope | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |\n| W2-M147 | product-traceability-trailers red with 735 findings | medium | W2-01 | Named in W2-01's KPIs (gov close and traceability). |\n",
      "tokens": 293
    },
    {
      "id": "WAVE-2-TRIAGE",
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "text": "| W2-M208 | Close stated-result check satisfied by a printed line; stand-in check root and src only | medium | W2-41 | Fits W2-41's paths and KPIs (close and escalation integrity); its builder takes it. |\n| W2-M209 | Reopened FULL ticket with an earlier probe record always refuses at probe gate | medium | W2-01 | Named in W2-01's KPIs (gov close and traceability). |\n| W2-M210 | Commit hook waits for the whole secrets scan (137-369 s); result caching | medium | W2-06 | Named in W2-06's KPIs (fast pre-commit tier and re-index). |\n| W2-M211 | Hard-block key covered by any declaring check, whatever its severity or tier | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |\n| W2-M212 | Success form with findings or 'unmeasured' inside its result is green | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |\n| W2-M213 | fresh-agent-reconstruction green with no checkpoint or an unfindable one | medium | W2-39 | Fits W2-39's paths and KPIs (model-switch continuity and checkpoints); its builder takes it. |\n",
      "tokens": 261
    },
    {
      "id": "WAVE-2-TRIAGE",
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "text": "| W2-L102 | Rebuild takes about 157 s on a 955-file project | low | W2-15a | Fits W2-15a's paths and KPIs (EXP-003 baseline); its builder takes it. |\n| W2-L103 | Rebuild exits 0 when optional indexes are not recreated | low | W2-06 | Fits W2-06's paths and KPIs (fast pre-commit tier and re-index); its builder takes it. |\n| W2-L104 | Recovery check unmeasured on a project never loaded | low | W2-45 | Fits W2-45's paths and KPIs (check runner semantics); its builder takes it. |\n| W2-L105 | Launches leave temporary gov-launch folders in /tmp | low | W2-21 | Named in W2-21's KPIs (stable launch). |\n| W2-L106 | Yellow families at baseline | low | W2-08 | Named in W2-08's KPIs (hooks back on). |\n| W2-L107 | --disposition finding records no class or context on the repair ticket | low | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |\n| W2-L108 | Close command inserts fields into the ticket tool's frontmatter itself | low | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |\n| W2-L109 | One edit gives many adapter findings | low | W2-05 | Fits W2-05's paths and KPIs (git environment sweep); its builder takes it. |\n",
      "tokens": 296
    },
    {
      "id": "WAVE-2-TRIAGE",
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "text": "| W2-H013 | Unseen link paths: existing hard links, replaced acceptance-test symlink, cp -s | high | W2-42 | Named in W2-42's KPIs (guard holes). |\n| W2-H014 | Removed text, including later secrets, persists in SQLite free pages | high | W2-43 | Named in W2-43's KPIs (CI and secret floor). |\n| W2-H015 | Direct openspec archive and hand-set spec status bypass readiness | high | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |\n| W2-H016 | Worker bulk-copied tree including held-out.yaml into scratchpad | high | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |\n| W2-H017 | DEC-385 fixture exclusion covers one exact path only | high | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |\n| W2-H018 | Decision checker too slow at scale for every gov check | high | W2-45 | Named in W2-45's KPIs (check runner semantics). |\n| W2-H019 | Containment rests on self-declared commit trailers | high | W2-44 | Named in W2-44's KPIs (trailers bound to launch identity). |\n| W2-H020 | gov check red on this repository: the baseline of 13 hard-block reds | high | W2-08 | Named in W2-08's KPIs (hooks back on). |\n",
      "tokens": 297
    },
    {
      "id": "3e8804bf0498072f3c1e9c89",
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "text": "| `gov impact` (code graph traversal) as a later input to selection and to the profile | **W2-37** (in progress) \u2192 **W2-38** (Wave 3) | CAP-33.b, CAP-53.b | W2-37 in progress |\n| Profile from impact; impact-selected tests at close (the full W2-38) | **W2-38**, Wave 3 (DEC-841) | CAP-53.b, CAP-39.c | Wave 3; its KPI line still builds \"on top of W2-48's cache\" (stale, finding 5) |\n| CI on the hosted runner: pinned pytest/xdist, the `not local_only` regression as an L4 complement, a green job | **W2-43** | CAP-39.a (CI) | open, needs Q-8 (owner approval of runner tools) |\n| `gov check` semantics: an unmeasured or absent-tool check is not green; time limits stated | **W2-45** | CAP-38.b, CAP-39.d | open |\n| Load out of the close: timing kinds as an isolated suite or the close's own resource gate; W1-46's live cases robust | **W2-57** (card only, no ticket file) | CAP-39.a | not created |\n| The close record type with a required `validation` block | **W2-64** (W2-02's widening) or W2-02's resume | CAP-38.d (suite currency), CAP-22-type records | W2-02 merged; its close was refused on 2026-10-21 at 15:36 for two reds outside the ticket; W2-64 planned |\n",
      "tokens": 291
    },
    {
      "id": "f4cdc04d27f307a7624b0c71",
      "path": "docs/assessment/2026-10/D-tool-staging.md",
      "text": "| `gov launch` | **Aid**, becoming the gate for how workers start. | The trial of DEC-789 became the standing rule of DEC-799 (WBS:59). Leads still start in the owner's launch form until W2-21 closes (DEC-715; WBS:59). Leads launch workers from the worktree, with that worktree's code: `cd <this worktree> && PYTHONPATH=src python3 -m gov.cli.main launch \u2026` (`briefs/LEAD-common.md:19`). So a worker's sandbox is built by the worktree's own launcher code. | W2-21 (`gov launch lead`), W2-56. |\n| `gov check` | **Gate** inside `gov close`; an **aid** on its own. | 18 declared checks (run 6). A red hard-block check refuses a close (register:8414). The checkpoint records \"`gov check` at `6f7d4f9e`: no red\" (`CHECKPOINT.md`, State). Its help text still says \"running them is not built yet\" (`src/gov/cli/main.py:95`; F9). Its runner semantics are open work (W2-45). | W2-45. The help text corrected (R5). |\n",
      "tokens": 227
    },
    {
      "id": "3b725e6e496b8215b606a134",
      "path": "docs/assessment/2026-10/SYNTHESIS.md",
      "text": "| `gov launch` | **Aid**, becoming the gate for how workers start (DEC-799) | It starts every worker whose suites do not need the code graph | It refuses leads and the orchestrator by design [E F6]; research cannot be launched [E F6]; it loads no role text [E F2]; it passes on the parent's whole environment [E F13]; it does not refuse every flag that drops the guard [E F19]; a worktree's own launcher code builds the sandbox [D \u00a72.2] | W2-21, W2-56 [E R1, R2, R3, R6] |\n| `gov check` | **Gate** inside `gov close`; **aid** on its own | 18 declared checks; a red hard-block check refuses a close | Its help text still says running the checks is \"not built yet\" [D \u00a72.1, F9] | W2-45 (runner semantics); the help text corrected [D R5] |\n| Retrieval (`gov retrieve`, the code graph) | **Aid** | It feeds `gov context`; a stale store refuses a close | Any edit to a tracked file switches the index off [B F2]; the code-graph query exceeds its 100,000-row cap [B F3]; register chunks carry the wrong id [B F4]; tests fill the semantic index and the kernel template is not in it [B F6]; the hit@5 figures disagree (Appendix A) | The proofs of section 6; W2-06, W2-13, W2-15a/b, W2-32 [D \u00a72.1; B] |\n",
      "tokens": 299
    },
    {
      "id": "26989fbdbd2df9a95c3ced46",
      "path": "tests/acceptance/W1-26/test_w1_26_command.py",
      "text": "\"\"\"KPI S1 (partial), S2, S5 (partial): the ``gov check`` command line.\n\nTests the API-0002 envelope, exit codes, per-family RED/YELLOW/GREEN status,\nand the hard-block vs warning severity semantics.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport pytest\n\nimport w1_26_support as support\n\ncli_support = support.cli_support\n\n\n# --------------------------------------------------------------------------\n# The command is built and returns the envelope\n# --------------------------------------------------------------------------\n\n",
      "tokens": 132
    },
    {
      "id": "809e132767ebae6f2abe9635",
      "path": "tests/acceptance/W1-26/README.md",
      "text": "| CAP-30.b (readiness gaps generate linked tickets) | `test_w1_26_gap_tickets.py` |\n| CAP-30.e (capability taxonomy extended only through a governed change) | `test_w1_26_taxonomy.py` |\n| CAP-38.b (17 families named, registered checks run, absent reported) | `test_w1_26_registry.py` |\n| CAP-01.c (authority semantics preserved across stages) | `test_w1_26_authority.py` |\n| CAP-24.c (skill changes follow versioned promotion) | `test_w1_26_skill.py` |\n| CAP-58.a (checks derived, not enumerated) | `test_w1_26_derived.py` |\n\n",
      "tokens": 132
    }
  ],
  "supplementary_query": "gov check runner semantics and scale\nThe decision checker runs within the gov check budget on a 200-decision, 20k-commit repository Verify: a planted repository of 200 decisions and 20,000 commits: `gov check` runs the decision checker and its recorded time is within the gov check budget (the budget's value printed beside it) [W2-H018].\nA check that exits 0 with findings, or with \"unmeasured\" in its result, is not green Verify: planted checks, one exiting 0 with a finding and one exiting 0 with \"unmeasured\" in its result: both are reported not green; a planted clean check exiting 0 is green [W2-M129, W2-M212].\nAn absent tool of a hard-block check is red, not yellow Verify: a planted hard-block check whose tool is absent from the path: its result is red, never yellow [W2-M130, W2-M265].\nA hard-block key is covered only by a check of hard-block tier Verify: a planted check map that covers a hard-block key only by a check of a lower tier is refused naming the key; the same key covered by a hard-block-tier check is accepted [W2-M211, W2-M259].\nThe time limit is stated and tested Verify: the limit's value is printed in the runner's result, and a planted check that runs past it is stopped and reported as timed out, by a unit test [W2-M151].",
  "further_batch": [
    {
      "id": "WAVE-2-TRIAGE",
      "path": "docs/plan/WAVE_2_TRIAGE.md"
    },
    {
      "id": "d8f3825817fae1bbee0f7231",
      "path": "tests/acceptance/W2-45/README.md"
    },
    {
      "id": "d650c2988957e8e1d3e41bfa",
      "path": "tests/acceptance/W2-45/w2_45_support.py"
    },
    {
      "id": "WAVE-2-TRIAGE",
      "path": "docs/plan/WAVE_2_TRIAGE.md"
    },
    {
      "id": "6aa9824792a77992bf58a237",
      "path": "docs/probes/DAEO-kl5e/PR-DAEO-kl5e-run-9.md"
    },
    {
      "id": "56023d5e6e574da21c7ed47a",
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md"
    },
    {
      "id": "CONTRACT-v4",
      "path": "docs/contract/CONTRACT_v4.md"
    },
    {
      "id": "CAP-01.c",
      "path": "docs/contract/capabilities/CAP-01.c.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "WAVE-2-TRIAGE",
          "path": "docs/plan/WAVE_2_TRIAGE.md"
        },
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        },
        {
          "id": "WAVE-2-TRIAGE",
          "path": "docs/plan/WAVE_2_TRIAGE.md"
        },
        {
          "id": "WAVE-2-TRIAGE",
          "path": "docs/plan/WAVE_2_TRIAGE.md"
        },
        {
          "id": "WAVE-2-TRIAGE",
          "path": "docs/plan/WAVE_2_TRIAGE.md"
        },
        {
          "id": "WAVE-2-TRIAGE",
          "path": "docs/plan/WAVE_2_TRIAGE.md"
        },
        {
          "id": "WAVE-2-TRIAGE",
          "path": "docs/plan/WAVE_2_TRIAGE.md"
        },
        {
          "id": "3e8804bf0498072f3c1e9c89",
          "path": "docs/assessment/2026-10/H-test-strategy.md"
        },
        {
          "id": "f4cdc04d27f307a7624b0c71",
          "path": "docs/assessment/2026-10/D-tool-staging.md"
        },
        {
          "id": "3b725e6e496b8215b606a134",
          "path": "docs/assessment/2026-10/SYNTHESIS.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "26989fbdbd2df9a95c3ced46",
          "path": "tests/acceptance/W1-26/test_w1_26_command.py"
        },
        {
          "id": "809e132767ebae6f2abe9635",
          "path": "tests/acceptance/W1-26/README.md"
        },
        {
          "id": "WAVE-2-TRIAGE",
          "path": "docs/plan/WAVE_2_TRIAGE.md"
        },
        {
          "id": "d8f3825817fae1bbee0f7231",
          "path": "tests/acceptance/W2-45/README.md"
        },
        {
          "id": "d650c2988957e8e1d3e41bfa",
          "path": "tests/acceptance/W2-45/w2_45_support.py"
        },
        {
          "id": "WAVE-2-TRIAGE",
          "path": "docs/plan/WAVE_2_TRIAGE.md"
        },
        {
          "id": "6aa9824792a77992bf58a237",
          "path": "docs/probes/DAEO-kl5e/PR-DAEO-kl5e-run-9.md"
        },
        {
          "id": "56023d5e6e574da21c7ed47a",
          "path": "governance/project/orchestration/packages/FORECAST-W2-1.md"
        },
        {
          "id": "CONTRACT-v4",
          "path": "docs/contract/CONTRACT_v4.md"
        },
        {
          "id": "CAP-01.c",
          "path": "docs/contract/capabilities/CAP-01.c.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "56023d5e6e574da21c7ed47a",
      "reason": "budget exceeded"
    },
    {
      "id": "6aa9824792a77992bf58a237",
      "reason": "budget exceeded"
    },
    {
      "id": "CAP-01.c",
      "reason": "budget exceeded"
    },
    {
      "id": "CONTRACT-v4",
      "reason": "budget exceeded"
    },
    {
      "id": "WAVE-2-TRIAGE",
      "reason": "budget exceeded"
    },
    {
      "id": "WAVE-2-TRIAGE",
      "reason": "budget exceeded"
    },
    {
      "id": "d650c2988957e8e1d3e41bfa",
      "reason": "budget exceeded"
    },
    {
      "id": "d8f3825817fae1bbee0f7231",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 5936,
  "budget": {
    "limit": 6000,
    "used": 5936
  },
  "left_out": {
    "count": 14,
    "superseded": [
      "DEC-002",
      "DEC-013",
      "DEC-038",
      "DEC-043",
      "DEC-045",
      "DEC-047",
      "DEC-048",
      "DEC-049",
      "DEC-636",
      "DEC-798",
      "DEC-869",
      "DEC-875",
      "DEC-876",
      "DEC-960"
    ],
    "done": []
  },
  "hash": "c576cd6e02b8bb354c62c91b88bd9517ff7737863a2904bf37ba13119e970b0b"
}
