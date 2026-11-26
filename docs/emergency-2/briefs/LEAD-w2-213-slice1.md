# Lead brief: w2-213-slice1, W2-213's first slice: the standard frozen in the kit and the layout checker (SL-1 to SL-14; DEC-1255, DEC-1256)

You are a ticket lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-26. **Read `docs/emergency-2/briefs/LEAD-COMMON.md`
first: every rule there applies.** Decide, never ask (I-10). Use `systematic-debugging`. Every `gov retrieve` you or a helper runs
takes `--root /home/usain/gov-os-worktrees/W2-00-store`. **Never open a hidden question-set root or a secret-named file**, and never
glob `/home/usain/*` (SL-6 is about exactly this): every test plants its own repository and its own stand-in hidden and secret paths.

## Why
The owner (DEC-1256): EXAMIN and ASMO OS restructure once, to the final standard, and nothing moves before W2-213's first slice reaches
them: the standard frozen in the kit and the checker, "runnable on a plan before any move". Both product CTOs have their chunking ready
and wait on this. Read DEC-1255 and DEC-1256 (`docs/DECISION_REGISTER.md`), the spec `docs/specs/W2-213-standard-layout.md` whole (slice 1
is SL-1 to SL-14), the accepted rubric `docs/emergency-2/proposals/CLASSIFICATION-RUBRIC.md` (with its erratum on ASMO OS's folders), and
`.tickets/DAEO-stdl.md` (its K-lines and allowed paths are the spec's, word for word).

## What
SL-1 to SL-14 as the spec and ticket state them. The CTO settled two of the spec's open questions: SL-14 (the check after the hand moves)
stays in slice 1 (the owner's step 3), and the standard lives at `template/governance/kernel/standard.yaml`. The other open questions:
build to the defaults the spec's K-lines already follow. The new `layout` command goes into `src/gov/check/commands.py` and W1-32's pinned
command set (the latter the test designer's). Flow: LEAD-COMMON's (the independent test designer first, red on the base, its README map
in the form `gov accept` reads, each case carrying its K-line id; then the engineer until `gov accept W2-213` is green).

**The hand route** (the owner: shipped "by the next release or by hand if that is sooner"; a new schema keeps it off a patch release): in
your return, the exact command a product CTO runs from Gov OS's source tree to check its plan without a release (for example
`PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src python3 -m gov.cli.main layout check <plan> --root <their repository>`),
proven by running it on a planted repository outside Gov OS.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-w2-213-slice1`, branch `e2/w2-213-slice1` from `w2/integrate`. Code area: the ticket's
`allowed_paths` only. `e2/bundle-a` and `e2/bundle-b` are held (they change the kit and `src/gov/adopt/`): do not edit their files. Never
merge into `w2/integrate`.

## Green
SL-1 to SL-14 red on the base, green after; `gov accept W2-213` green; W1-32 green; the hand-route proof; then exactly the
impact-selected suites (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-stdl=e2/w2-213-slice1 --onto w2/integrate
--select`) through the heavy slot. Check the trailers (LEAD-COMMON).

## Return
Branch and head; SL-1 to SL-14 with tests and result; the hand-route command and its proof; the selected run's summary; your retrieves
(count, queries, records used).

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
store: ea6829737f13 (/home/usain/gov-os-worktrees/W2-00-store-b)
{
  "store": {
    "commit": "ea6829737f138929d1fc01adb6a1c275729dbffd",
    "head": "ea6829737f138929d1fc01adb6a1c275729dbffd",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-b"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "DAEO-sdhj",
      "sha256": "ac1d87f94b3de32820accb7582164169e6e41bbff148b9f0a4ecef61551e3949",
      "path": ".tickets/DAEO-sdhj.md",
      "start_line": 82,
      "end_line": 84,
      "text": "## Fix: two deny lines only; gov update takes the legacy lines out; the held-out Read deny step retires (DEC-1217 (6), DEC-1219 (4))\n- **The bug:** `gov update` 0.1.3 put back the deny and allow lines Emergency 2 removed (`Edit(.tickets/**)`, `Bash(gov launch:*)`, one `Read` deny per held-out path), found in EXAMIN's report 28 (2026-11-18).\n- **The fix (built on branch `e2/kit-e2` under the W2-208 ticket `DAEO-kt8e`, before the owner's ruling that it is a fix here reached its lead; merged into `w2/integrate` at `fc8a52fb9` on 2026-11-19):** the kit's permission source and kernel settings hold the two deny lines (`git push`, `sudo`) and no allow line (K1, `c81e9b796`); `gov update` takes the legacy lines out of a project's settings through its journal and keeps a line the owner added by hand (K2, F2, `f8b4a677f`); the held-out `Read` deny step retires (`write_read_rules` gone; K3, F1, `62658001c`). Its tests are `tests/acceptance/W2-208/` (K1 to K3, F1, F2; designer commit `d513e8559`), read by `gov accept W2-208`.\n",
      "chunk_id": "013aea19af229d7674a7dd90",
      "routes": [
        "semantic",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "3443a0b46d0002af94eaee2d",
      "sha256": "dba492ca046d67ea9784e77462268827403039e4d436c5eb1eb252adbd52aa67",
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "start_line": 578,
      "end_line": 630,
      "text": "  ],\n  \"exit_code\": 0,\n  \"where\": \"a-dev exit clone, 2026-10-13\",\n  \"answer\": {\n   \"ok\": true,\n   \"command\": \"readiness\",\n   \"result\": {\n    \"specification\": \"ORION-SPEC-DIMADD\",\n    \"profile\": \"STANDARD\",\n    \"closed\": true,\n    \"open\": []\n   },\n   \"session\": \"\"\n  }\n },\n \"doctor\": {\n  \"argv\": [\n   \"gov\",\n   \"doctor\",\n   \"--json\"\n  ],\n  \"exit_code\": 3,\n  \"where\": \"this worktree, 2026-10-13\",\n  \"answer\": {\n   \"ok\": false,\n   \"command\": \"doctor\",\n   \"result\": {},\n   \"session\": \"\",\n   \"error\": {\n    \"code\": \"DOCTOR_UNHEALTHY\",\n    \"message\": \"one or more health checks failed or reported drift: tools; path_compliance; index_freshness; claude_code\",\n    \"details\": {\n     \"healthy\": false,\n     \"tools\": {\n      \"status\": \"fail\",\n      \"tools\": [\n       {\n        \"name\": \"node\",\n        \"pinned_version\": \"v22.23.3\",\n        \"found_version\": \"v22.23.3\",\n        \"sha256_match\": true,\n        \"ok\": true,\n        \"location\": \"/home/usain/.nvm/versions/node/v22.23.3/bin\"\n       },\n       {\n        \"name\": \"uv\",\n        \"pinned_version\": \"0.12.21\",\n        \"found_version\": \"0.12.21\",\n        \"sha256_match\": true,\n        \"ok\": true\n       },\n       {\n        \"name\": \"rulesync\",\n",
      "chunk_id": "3443a0b46d0002af94eaee2d",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "e79e4f98b1f0cb117262e73f",
      "sha256": "acab8404baf8ed52c978acc006d1d89ad58e45358bbddb9cd8fdda20e56fa63a",
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "start_line": 378,
      "end_line": 421,
      "text": "       \"inputs_hash\": \"82e70bc5be909a78\"\n      }\n     },\n     {\n      \"id\": \"core-mutation\",\n      \"family\": \"mutation scope\",\n      \"severity\": \"hard-block\",\n      \"status\": \"GREEN\",\n      \"findings\": [],\n      \"provenance\": {\n       \"commit\": \"93bcb247990552c07dfbe9a20c685830b47e46d2\",\n       \"check_version\": \"1.0.0\",\n       \"inputs_hash\": \"7e274d2dc1b115ae\"\n      }\n     },\n     {\n      \"id\": \"core-pathmap\",\n      \"family\": \"path-map compliance\",\n      \"severity\": \"hard-block\",\n      \"status\": \"GREEN\",\n      \"findings\": [],\n      \"provenance\": {\n       \"commit\": \"93bcb247990552c07dfbe9a20c685830b47e46d2\",\n       \"check_version\": \"1.0.0\",\n       \"inputs_hash\": \"6218844a8a69ddb3\"\n      }\n     },\n     {\n      \"id\": \"core-schema\",\n      \"family\": \"schema/invariants\",\n      \"severity\": \"hard-block\",\n      \"status\": \"GREEN\",\n      \"findings\": [],\n      \"provenance\": {\n       \"commit\": \"93bcb247990552c07dfbe9a20c685830b47e46d2\",\n       \"check_version\": \"1.0.0\",\n       \"inputs_hash\": \"eb2f12189b39dad2\"\n      }\n     },\n     {\n      \"id\": \"fresh-agent-reconstruction\",\n      \"family\": \"fresh-agent-reconstruction\",\n      \"severity\": \"hard-block\",\n      \"status\": \"GREEN\",\n",
      "chunk_id": "e79e4f98b1f0cb117262e73f",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "b0fbe01f0db242812e202aa0",
      "sha256": "dffe53b2c3e3f1b5ecbfd9136839fea9e95bd08174413772539863bb8cee1a7e",
      "path": "governance/project/bootstrap.md",
      "start_line": 2072,
      "end_line": 2086,
      "text": "## W1-32: `gov status` and the launcher's two residuals (DEC-392, DEC-449, DEC-526; 2026-10-08)\n\nMerged from `w1/W1-32` at `ff85c968` (81 cases; 266 source lines added against an estimate of 80: about\n190 in `src/gov/status/command.py`, about 75 in the launcher). `gov status --json` always answers\n`ok: true` with exit 0 (W1-07 holds it to exit 0 without a store) and gives `tickets` (ready, blocked with\nreasons, claimed with holder), `decision_packages`, `readiness`, `governance_share`, `pause`, `doctor` and\n`not_read`; whatever could not be read is `{read: false, reason}` and is listed under `not_read`. The\nlauncher ends its session on SIGINT, SIGTERM and SIGHUP (asked first, killed on a second signal or 5 s\nlater), removes the session's folder and ends with 130; a failed removal keeps the session's exit code.\nMerged as built under DEC-526 while package P-19 is with the owner; the ticket is not closed.\n\nNot covered or not built, by name:\n\n- **The natural-language half of CAP-28.a.** No skill, role file or instruction line routes a status\n  question to `gov status --json`; the file would lie in `.claude/**`, `CLAUDE.md`, `AGENTS.md` or the\n",
      "chunk_id": "b0fbe01f0db242812e202aa0",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "EXP-W2-81-proving-run-0.1.4",
      "sha256": "4ad5e8e7954af8dcc22cb47c57c74486197ca4622dfc6ff42a648b14f3b5d08a",
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "start_line": 244,
      "end_line": 251,
      "text": "## Draft KPI lines\n\nEach for the ticket that takes it, with its verify.\n\n1. **W2-22 (fix).** \"`gov doctor` exits 0 and names the drift when the Claude Code CLI and the extension differ by a patch version and neither is below 2.1.285; it exits 3 when either is below the minimum, when the difference exceeds the owner's gap, or when the CLI at the recorded version has another sha256.\" Verify: a scratch repository with stand-in `claude` and `extensions.json`: 2.1.329 against 2.1.328 gives exit 0 with `drift` named; 2.1.280 gives exit 3; a planted sha mismatch gives exit 3.\n2. **W2-52 / W1-41 (fix).** \"A verdict that the A5 or A7 gate accepts is a record the store reads.\" Verify: a verdict front matter exactly as the adopt skill gives it passes `gov adopt --lite --stage A5` and `gov rebuild` reports no invalid record.\n3. **W2-88 (fix).** \"`FABRIC_INCOMPLETE` names each file that is in neither list.\" Verify: a planted tracked path matching two namespaces gives a refusal that names it.\n4. **New (path map).** \"A3 refuses a path map in which a tracked path matches two namespaces, naming the path and both.\" Verify: the rust adopter's map (`audits/**` in two namespaces) is refused at A3.\n",
      "chunk_id": "399e6c298e01ef127e8d7bf8",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-5y8d",
      "sha256": "59d2b47a3792be0689f8dc4c3cc8801c87432ad301970bc9e25dd2dc1dac7256",
      "path": ".tickets/DAEO-5y8d.md",
      "start_line": 28,
      "end_line": 43,
      "text": "- tests/acceptance/W2-128/test_w2_128_rows.py  # row 8: the 'until W2-56' line deleted (DEC-1163 (1)), widened by the CTO (DEC-1157 (12))\n- tests/acceptance/W2-128/README.md\n- docs/probes/DAEO-5y8d/**  # the probe record\n- tests/acceptance/W2-182/**  # the revision's own folder: its README maps the revised case ids so gov accept W2-182 runs them (DEC-892; the W2-90 form); CTO, DEC-1157 (12)\nreads:\n- .gov-runtime/scratch/orchestrator/drafts/nightly-20261113-analysis.md\n- src/gov/check/commands.py\n- src/gov/rebuild/**\n- src/gov/session_watch/items.py\n- .rulesync/hooks.jsonc\n- template/governance/kernel/hooks/**\nneeds: []\nwaits_on: []\nkpis:\n  success:\n  - 'B: W1-32''s recorded command list holds the four approved commands gov --help shows (dispatch W2-121, adapters W2-23, session-watch W2-159, wait W2-160), and nothing else changes in it [DEC-1163 (6), DEC-1156 (7)] Verify: tests/acceptance/W1-32/test_w1_32_command_set.py passes on w2/integrate; a planted unrecorded command name added to gov --help in a stand-in makes it fail'\n",
      "chunk_id": "2466d8f133673ce146251c98",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "fa68f2ff9059451d2e4ae774",
      "sha256": "4d11e27c26ad2eefd3ff81fc1e0a72181f4f46296d5394496816ffd999de8988",
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "start_line": 151,
      "end_line": 153,
      "text": "- **Overlap in the plan.** W2-156, W2-159 and W2-160 each add one line to `src/gov/check/commands.py`, a file five other open tickets already hold (the tickets audit \u00a74.6). `gov plan` serialises them (M: batches 19-21). If that is too slow, a registry that does not need an edit per command is a separate ticket.\n- **Not done:** no ticket other than my five touched; no KPI line added to an existing ticket; the structural gap of \u00a74.3 (committed tools calling scratch paths) is covered by W2-20 (the `--slot` command exists) and W2-115 (the selection), not by a ticket of its own; the two installed-state gaps (\u00a74.1 `settings.local.json`, \u00a74.2 the reranker module) are owner ACTs and stay in \u00a74 of the inventory.\n- **Scratch:** `.gov-runtime/scratch/audit-d/` holds a shared clone (no objects copied) and one links output; the CTO may remove it.\n",
      "chunk_id": "fa68f2ff9059451d2e4ae774",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "dcedc7640b0e16d4b0b14d6e",
      "sha256": "073b59a484dfcc2ea8fce2e6f86537b61d73925370606d4c682dfc89bc42af52",
      "path": "docs/changes/W2-158-evidence.md",
      "start_line": 19,
      "end_line": 20,
      "text": "| S2 the lines and the last line | `test_output_order_and_last_line`; `test_s2_not_applicable_finding_and_plain_exit`; `test_s2_at_most_three_findings_and_each_shortened`; the timed-out line in the S1 test; `test_skills_family_is_every_declaration_of_the_skill_regression_family`; `test_a_file_that_cannot_be_read_makes_only_its_own_family_a_notice`; `test_a_command_that_cannot_be_started_is_a_notice` |\n| S3 exit 0 whatever is found, 2 only when it cannot run, nothing decides on it | `test_s3_a_failing_check_gives_exit_0_and_a_notice_through_the_command_line` (through `gov.cli.main.main`: no envelope); `test_s3_json_flag_changes_nothing`; `test_s3_exit_2_when_the_pass_cannot_run` (no folder, not git, a subfolder of a work tree, no HEAD); `test_l1_a_bad_timeout_is_argparses_usage_error`; `test_l1_other_usage_errors_exit_2_with_nothing_on_stdout`; `test_s3_no_close_launch_or_queue_code_calls_it` |\n",
      "chunk_id": "dcedc7640b0e16d4b0b14d6e",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "0d184a39c5c0ff6530f70733",
      "sha256": "f634a29979c11a10966296396ebf8e3e6c47a5f38b1361e8429bf61ad70eb759",
      "path": "docs/changes/W2-136-evidence.md",
      "start_line": 45,
      "end_line": 50,
      "text": "## The KPI lines and how each is met\n\n| KPI | How it is met | Unit tests (`tests/unit/plan/`, `tests/unit/launch/test_w2_136_plan_check.py`) | `gov accept` |\n|---|---|---|---|\n| S1: the lines, `--json`, exit 0/1/2 | `render.lines`, `command.run` | `test_the_first_line_the_batches_and_the_waits`, `test_only_open_and_in_progress_tickets_are_planned`, `test_json_gives_the_same_plan_in_the_shared_envelope`, `test_no_ticket_store_cannot_run`, `test_a_ticket_that_cannot_be_read_stops_the_plan`, `test_tickets_names_the_planned_tickets_and_an_unknown_one_cannot_run` | 6/6 |\n| S2: `NEEDS_WHAT_WRITES` naming the path, `WRITES_OVERLAP`, `DEPENDS_ON`, `WAITS_ON`, `READS_WIDE` orders nothing, the rest in one batch | `derive.hard_waits`, `_reads_wide`, `make_plan` | `test_a_needed_path_an_unfinished_ticket_writes_...`, `test_a_needed_path_a_closed_ticket_wrote_orders_nothing`, `test_depends_on_and_an_unfinished_waits_on_make_it_wait`, `test_reads_orders_nothing_and_warns_...`, `test_a_waits_on_decision_not_accepted_holds_...`, `test_a_waits_on_record_path_that_exists_is_met` | 7/7 |\n",
      "chunk_id": "0d184a39c5c0ff6530f70733",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "d7602c9537680d1daa8f5e5d",
      "sha256": "1ae1ac0664c9349101690abf9dd60f961223c4f0810b47469111632a206be59b",
      "path": "docs/plan/wave-1-exit/evidence/gov-check.json",
      "start_line": 1,
      "end_line": 1,
      "text": "{\"ok\": true, \"command\": \"check\", \"result\": {\"families\": {\"schema/invariants\": {\"status\": \"GREEN\", \"family\": \"schema/invariants\", \"check_count\": 1}, \"graph integrity\": {\"status\": \"GREEN\", \"family\": \"graph integrity\", \"check_count\": 1}, \"index freshness\": {\"status\": \"GREEN\", \"family\": \"index freshness\", \"check_count\": 1}, \"retrieval regression\": {\"status\": \"GREEN\", \"family\": \"retrieval regression\", \"check_count\": 1}, \"authority/role limits\": {\"status\": \"YELLOW\", \"family\": \"authority/role limits\", \"check_count\": 2}, \"mutation scope\": {\"status\": \"GREEN\", \"family\": \"mutation scope\", \"check_count\": 1}, \"path-map compliance\": {\"status\": \"GREEN\", \"family\": \"path-map compliance\", \"check_count\": 1}, \"context reproducibility\": {\"status\": \"GREEN\", \"family\": \"context reproducibility\", \"check_count\": 1}, \"concurrency/claims\": {\"status\": \"GREEN\", \"family\": \"concurrency/claims\", \"check_count\": 1}, \"adapter/model portability\": {\"status\": \"GREEN\", \"family\": \"adapter/model portability\", \"check_count\": 1}, \"skill regression\": {\"status\": \"GREEN\", \"family\": \"skill regression\", \"check_count\": 4}, \"command-contract consistency\": {\"status\": \"GREEN\", \"family\": \"command-contract consistency\", \"check_count\": 1}, \"secrets indexing\": {\"status\": \"GREEN\", \"family\": \"secrets indexing\", \"check_count\": 1}, \"recovery/rebuild\": {\"status\": \"GREEN\", \"family\": \"recovery/rebuild\", \"check_count\": 1}, \"fresh-agent reconstruction\": {\"status\": \"GREEN\", \"family\": \"fresh-agent reconstruction\", \"check_count\": 1}, \"product traceability\": {\"status\": \"YELLOW\", \"family\": \"product traceability\", \"check_count\": 3}, \"audit reproducibility\": {\"status\": \"YELLOW\", \"family\": \"audit reproducibility\", \"reason\": \"not applicable until the first audit\", \"check_count\": 1}}, \"checks\": [{\"id\": \"adapter-portability\", \"family\": \"adapter/model portability\", \"severity\": \"hard-block\", \"status\": \"GREEN\", \"findings\": [], \"provenance\": {\"commit\": \"93bcb247990552c07dfbe9a20c685830b47e46d2\", \"check_version\": \"1.0.0\", \"inputs_hash\": \"cdcccf9c54a38457\"}}, {\"id\": \"audit-reproducibility\", \"family\": \"audit reproducibility\", \"severity\": \"hard-block\", \"status\": \"YELLOW\", \"reason\": \"not applicable until the first audit\", \"findings\": [], \"provenance\": {\"commit\": \"93bcb247990552c07dfbe9a20c685830b47e46d2\", \"check_version\": \"1.0.0\", \"inputs_hash\": \"769c77f8649ab973\"}}, {\"id\": \"context-reproducibility\", \"family\": \"context-reproducibility\", \"severity\": \"hard-block\", \"status\": \"GREEN\", \"findings\": [], \"provenance\": {\"commit\": \"93bcb247990552c07dfbe9a20c685830b47e46d2\", \"check_version\": \"1.0.0\", \"inputs_hash\": \"041214055628a392\"}}, {\"id\": \"core-authority\", \"family\": \"authority/role limits\", \"severity\": \"hard-block\", \"status\": \"GREEN\", \"findings\": [], \"provenance\": {\"commit\": \"93bcb247990552c07dfbe9a20c685830b47e46d2\", \"check_version\": \"1.0.0\", \"inputs_hash\": \"b27c6f3685d74751\"}}, {\"id\": \"core-claims\", \"family\": \"concurrency/claims\", \"severity\": \"hard-block\", \"status\": \"GREEN\", \"findings\": [], \"provenance\": {\"commit\": \"93bcb247990552c07dfbe9a20c685830b47e46d2\", \"check_version\": \"1.0.0\", \"inputs_hash\": \"fbd59ee7d4fc2f14\"}}, {\"id\": \"core-commands\", \"family\": \"command-contract consistency\", \"severity\": \"warning\", \"status\": \"GREEN\", \"findings\": [], \"provenance\": {\"commit\": \"93bcb247990552c07dfbe9a20c685830b47e46d2\", \"check_version\": \"1.0.0\", \"inputs_hash\": \"d22af35b7a3e3b8d\"}}, {\"id\": \"core-decision-citations\", \"family\": \"authority/role limits\", \"severity\": \"warning\", \"status\": \"YELLOW\", \"findings\": [{\"code\": \"DECISION_UNRECORDED\", \"commit\": \"abcb3095d267d88c93d19115e9c06ba0fd9fad6f\", \"decision\": \"DEC-594\", \"message\": \"commit abcb3095d267 cites DEC-594, which its tree does not record\"}, {\"code\": \"DECISION_UNRECORDED\", \"commit\": \"a1c03c5b76cfdb31f7c5076fcc71a758cc8d4083\", \"decision\": \"DEC-480\", \"message\": \"commit a1c03c5b76cf cites DEC-480, which its tree does not record\"}, {\"code\": \"DECISION_UNRECORDED\", \"commit\": \"be2e8c142ec2cc2b0eccaa6a8335b799ed493895\", \"decision\": \"DEC-480\", \"message\": \"commit be2e8c142ec2 cites DEC-\n",
      "cut": {
        "chars": 10397,
        "sent": 4001,
        "lines": [
          1
        ]
      },
      "chunk_id": "d7602c9537680d1daa8f5e5d",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "ADOPT-A3",
      "sha256": "e009a708a32379886656428aa3539f8525b603a0132919e12997fd299763c1a7",
      "path": "governance/adoption/A3-target-path-map.md",
      "start_line": 3134,
      "end_line": 3167,
      "text": "- path: tests/acceptance/W1-32/test_w1_32_added_cases.py\n  action: KEEP\n- path: tests/acceptance/W1-32/test_w1_32_command_set.py\n  action: KEEP\n- path: tests/acceptance/W1-32/test_w1_32_launch.py\n  action: KEEP\n- path: tests/acceptance/W1-32/test_w1_32_status_not_read.py\n  action: KEEP\n- path: tests/acceptance/W1-32/test_w1_32_status_parts.py\n  action: KEEP\n- path: tests/acceptance/W1-32/test_w1_32_status_pause.py\n  action: KEEP\n- path: tests/acceptance/W1-32/test_w1_32_status_read_only.py\n  action: KEEP\n- path: tests/acceptance/W1-32/w1_32_launch_support.py\n  action: KEEP\n- path: tests/acceptance/W1-32/w1_32_support.py\n  action: KEEP\n- path: tests/acceptance/W1-33/README.md\n  action: KEEP\n- path: tests/acceptance/W1-33/conftest.py\n  action: KEEP\n- path: tests/acceptance/W1-33/test_w1_33_agent_definitions.py\n  action: KEEP\n- path: tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py\n  action: KEEP\n- path: tests/acceptance/W1-33/test_w1_33_kernel_role_files.py\n  action: KEEP\n- path: tests/acceptance/W1-33/test_w1_33_roster.py\n  action: KEEP\n- path: tests/acceptance/W1-33/w1_33_support.py\n  action: KEEP\n- path: tests/acceptance/W1-34/README.md\n  action: KEEP\n",
      "chunk_id": "aea3a7a2b7c45f855fdc192a",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "0d58b62d7c3869d3224529c0",
      "sha256": "007c14b6b04ffa5989190f17ed0b63c2a67d312fde5ca980f7e5b69c8e9bb8c6",
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "start_line": 105,
      "end_line": 151,
      "text": "  \"where\": \"this worktree at 93bcb247, the start of the exit run, 2026-10-12 (gov-check.json)\",\n  \"answer\": {\n   \"ok\": true,\n   \"command\": \"check\",\n   \"result\": {\n    \"families\": {\n     \"schema/invariants\": {\n      \"status\": \"GREEN\",\n      \"family\": \"schema/invariants\",\n      \"check_count\": 1\n     },\n     \"graph integrity\": {\n      \"status\": \"GREEN\",\n      \"family\": \"graph integrity\",\n      \"check_count\": 1\n     },\n     \"index freshness\": {\n      \"status\": \"GREEN\",\n      \"family\": \"index freshness\",\n      \"check_count\": 1\n     },\n     \"retrieval regression\": {\n      \"status\": \"GREEN\",\n      \"family\": \"retrieval regression\",\n      \"check_count\": 1\n     },\n     \"authority/role limits\": {\n      \"status\": \"YELLOW\",\n      \"family\": \"authority/role limits\",\n      \"check_count\": 2\n     },\n     \"mutation scope\": {\n      \"status\": \"GREEN\",\n      \"family\": \"mutation scope\",\n      \"check_count\": 1\n     },\n     \"path-map compliance\": {\n      \"status\": \"GREEN\",\n      \"family\": \"path-map compliance\",\n      \"check_count\": 1\n     },\n     \"context reproducibility\": {\n      \"status\": \"GREEN\",\n      \"family\": \"context reproducibility\",\n      \"check_count\": 1\n     },\n     \"concurrency/claims\": {\n",
      "chunk_id": "0d58b62d7c3869d3224529c0",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "30da559cd92a01aec4e2daea",
      "sha256": "3f10af6085f5e4e6d8d95eaeb2f7521da98f1c7d2ab96f3ea46b758a929659e7",
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "start_line": 71,
      "end_line": 110,
      "text": "     \"mirror\": false\n    },\n    \"doctor\": {\n     \"healthy\": false,\n     \"parts\": {\n      \"tools\": \"fail\",\n      \"hooks\": \"pass\",\n      \"path_map\": \"pass\",\n      \"path_compliance\": \"fail\",\n      \"index_freshness\": \"fail\",\n      \"canaries\": \"unmeasured\",\n      \"framework_lock\": \"unmeasured\",\n      \"isolation\": \"pass\",\n      \"claude_code\": \"drift\",\n      \"held_out\": \"pass\",\n      \"adoption_level\": \"pass\"\n     }\n    },\n    \"not_read\": [\n     \"tickets.ready: the record store (.gov-runtime/store.db) is older than HEAD (e08d042df41a): what was committed since its last load is not in it\",\n     \"tickets.blocked: the record store (.gov-runtime/store.db) is older than HEAD (e08d042df41a): what was committed since its last load is not in it\",\n     \"decision_packages: the record store (.gov-runtime/store.db) is older than HEAD (e08d042df41a): what was committed since its last load is not in it\"\n    ]\n   },\n   \"session\": \"\"\n  }\n },\n \"check\": {\n  \"argv\": [\n   \"gov\",\n   \"check\",\n   \"--json\"\n  ],\n  \"exit_code\": 0,\n  \"where\": \"this worktree at 93bcb247, the start of the exit run, 2026-10-12 (gov-check.json)\",\n  \"answer\": {\n   \"ok\": true,\n   \"command\": \"check\",\n   \"result\": {\n    \"families\": {\n",
      "chunk_id": "30da559cd92a01aec4e2daea",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "b2c48bceaf33d334f97da689",
      "sha256": "cf08ee1cf63ac40299c368bec0426aac009f131973dee7fe3e0f355bfc5526dc",
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "start_line": 1447,
      "end_line": 1491,
      "text": "   \"command\": \"retrieve\",\n   \"result\": {\n    \"stopping_reason\": \"FACET_UNAVAILABLE\",\n    \"evidence\": [\n     {\n      \"id\": \"ADR-011\",\n      \"sha256\": \"b4ade811ca0bff05c398d01c751ca1453d526270505f5d3f9d727b1c1c91e8ba\",\n      \"path\": \"decisions/adr-011.md\",\n      \"start_line\": 15,\n      \"end_line\": 27,\n      \"chunk_id\": \"7815fe0fc7bcc120256fec36\",\n      \"routes\": [\n       \"closure\"\n      ],\n      \"batch\": 1,\n      \"text_removed_chars\": 574\n     },\n     {\n      \"id\": \"ORION-im02\",\n      \"sha256\": \"c236ef32b75445a176bca1e3384afa5eb60c73826d1586204f971e2575739caa\",\n      \"path\": \".tickets/ORION-im02.md\",\n      \"start_line\": 45,\n      \"end_line\": 51,\n      \"chunk_id\": \"9c3bf05584f576ad968b0a2f\",\n      \"routes\": [\n       \"closure\"\n      ],\n      \"batch\": 1,\n      \"text_removed_chars\": 947\n     },\n     {\n      \"id\": \"ADR-011\",\n      \"sha256\": \"4e64a343c087f81f5dd2429b21c1a533fccfa8827f2d89e18103a5f919dcf61f\",\n      \"path\": \"decisions/adr-011.md\",\n      \"start_line\": 28,\n      \"end_line\": 38,\n      \"chunk_id\": \"7ccedb68cf4f4478b6c412cf\",\n      \"routes\": [\n       \"closure\"\n      ],\n      \"batch\": 1,\n      \"text_removed_chars\": 605\n     },\n     {\n      \"id\": \"ORION-im02\",\n",
      "chunk_id": "b2c48bceaf33d334f97da689",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "9d47aab84188bf520196755c",
      "sha256": "bf8a4cc76bb2ef62131f521977afae5a1b7f5e31fa2ffa8ccabb5f17b9d159d1",
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "start_line": 901,
      "end_line": 963,
      "text": "      \"systems_identified\": 15,\n      \"systems_total\": 22\n     }\n    }\n   }\n  }\n },\n \"rebuild\": {\n  \"argv\": [\n   \"gov\",\n   \"rebuild\",\n   \"--json\"\n  ],\n  \"exit_code\": 0,\n  \"where\": \"a-dev exit clone, 2026-10-13\",\n  \"answer\": {\n   \"ok\": true,\n   \"command\": \"rebuild\",\n   \"result\": {\n    \"digest\": \"b50ca2570d646e9a25a05b253c511203770468a8e65aa364dd5192557f978569\",\n    \"store\": {\n     \"digest\": \"b50ca2570d646e9a25a05b253c511203770468a8e65aa364dd5192557f978569\",\n     \"invalid\": []\n    },\n    \"stores\": {\n     \"lexical\": {\n      \"status\": \"recreated\"\n     },\n     \"semantic\": {\n      \"status\": \"recreated\"\n     },\n     \"codeintel\": {\n      \"status\": \"recreated\"\n     }\n    },\n    \"timing\": {\n     \"lexical_s\": 0.0\n    }\n   },\n   \"session\": \"\"\n  }\n },\n \"context\": {\n  \"argv\": [\n   \"gov\",\n   \"context\",\n   \"DAEO-gjjf\",\n   \"--dry-run\",\n   \"--json\"\n  ],\n  \"exit_code\": 0,\n  \"where\": \"this worktree, 2026-10-13\",\n  \"answer\": {\n   \"ok\": true,\n   \"command\": \"context\",\n   \"result\": {\n    \"ticket\": \"DAEO-gjjf\",\n    \"authority\": [\n     {\n      \"id\": \"DEC-080\",\n      \"sha256\": \"8448f4fcfe2db6df29722c5c87c79b68ad2bfb1fdcdf8782f321082e92c67bd0\",\n      \"authority\": \"decision\",\n      \"lifecycle\": \"ACCEPTED\",\n",
      "chunk_id": "9d47aab84188bf520196755c",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "ADOPT-A1",
      "sha256": "900bb9747494ea9cad4be32fd04fc53dac6a470ff24c649b6882d5dd8cb01651",
      "path": "governance/adoption/A1-inventory.md",
      "start_line": 2788,
      "end_line": 2810,
      "text": "  blob: 11850c8b7d294a5e827a46516c68dcc38a63457d\n- path: tests/acceptance/W1-32/test_w1_32_command_set.py\n  blob: 1d2eb98d825f8a3b448fcc93589ab70203e88ce1\n- path: tests/acceptance/W1-32/test_w1_32_launch.py\n  blob: 506e4b18776555263c0292472098f8bb54d8ae86\n- path: tests/acceptance/W1-32/test_w1_32_status_not_read.py\n  blob: 5ae5f86099753fb6e15ec53fc59aef10c74cbdc4\n- path: tests/acceptance/W1-32/test_w1_32_status_parts.py\n  blob: 022e3a23277d81f5d70246a9ac5a757dbb4e9cbb\n- path: tests/acceptance/W1-32/test_w1_32_status_pause.py\n  blob: 4bcf94eebfb0bce5f59b5f5b776069de48a74376\n- path: tests/acceptance/W1-32/test_w1_32_status_read_only.py\n  blob: 1b50c0fe4ab434715953f00ebe693fedc85c2ccc\n- path: tests/acceptance/W1-32/w1_32_launch_support.py\n  blob: 34febfffb5de07bd14974bcb7870f6e14e8dff72\n- path: tests/acceptance/W1-32/w1_32_support.py\n  blob: b55d46f4b8aaf8b634fa8c2418349018ec22c6fe\n- path: tests/acceptance/W1-33/README.md\n  blob: 24de2b6e470015b77fba20ccb765a6577c5d786f\n- path: tests/acceptance/W1-33/conftest.py\n  blob: 5884859d441929ad22b5e04bcb2fb9d1ca4e1036\n- path: tests/acceptance/W1-33/test_w1_33_agent_definitions.py\n  blob: 1873a4a4023d31443b3bb8764d8e258c5f788f13\n",
      "chunk_id": "5e05b7b98b6b116234bb3cc4",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-5y8d",
      "sha256": "41fb6e0e8479863eb65c68171b239897faf4d1e26a71c420e56dfff64aa77b79",
      "path": ".tickets/DAEO-5y8d.md",
      "start_line": 43,
      "end_line": 44,
      "text": "  - 'B: W1-32''s recorded command list holds the four approved commands gov --help shows (dispatch W2-121, adapters W2-23, session-watch W2-159, wait W2-160), and nothing else changes in it [DEC-1163 (6), DEC-1156 (7)] Verify: tests/acceptance/W1-32/test_w1_32_command_set.py passes on w2/integrate; a planted unrecorded command name added to gov --help in a stand-in makes it fail'\n  - 'C: W1-18''s and W2-123''s cases expect REBUILD_FAILED where a rebuild''s asked-for semantic store is not recreated (W2-124, DEC-1150 (3)), each keeping its point (the keyword answer and no start for W1-18; the last failed try''s record for W2-123) [DEC-1163 (6), DEC-1150 (3)] Verify: both cases pass on w2/integrate; each still fails on a planted break of what it guards (W1-18: a retrieval that starts the server; W2-123: a retry record that is not written)'\n",
      "chunk_id": "1e2ebf4eb4c94306bffb1bf4",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "ADOPT-A2",
      "sha256": "5b7df84849d25f53833791379c5267498007907a779a312e950200187ace1ef5",
      "path": "governance/adoption/A2-classification.md",
      "start_line": 2784,
      "end_line": 2813,
      "text": "- path: tests/acceptance/W1-32/test_w1_32_added_cases.py\n  namespace: root-files\n- path: tests/acceptance/W1-32/test_w1_32_command_set.py\n  namespace: root-files\n- path: tests/acceptance/W1-32/test_w1_32_launch.py\n  namespace: root-files\n- path: tests/acceptance/W1-32/test_w1_32_status_not_read.py\n  namespace: root-files\n- path: tests/acceptance/W1-32/test_w1_32_status_parts.py\n  namespace: root-files\n- path: tests/acceptance/W1-32/test_w1_32_status_pause.py\n  namespace: root-files\n- path: tests/acceptance/W1-32/test_w1_32_status_read_only.py\n  namespace: root-files\n- path: tests/acceptance/W1-32/w1_32_launch_support.py\n  namespace: root-files\n- path: tests/acceptance/W1-32/w1_32_support.py\n  namespace: root-files\n- path: tests/acceptance/W1-33/README.md\n  namespace: root-files\n- path: tests/acceptance/W1-33/conftest.py\n  namespace: root-files\n- path: tests/acceptance/W1-33/test_w1_33_agent_definitions.py\n  namespace: root-files\n- path: tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py\n  namespace: root-files\n- path: tests/acceptance/W1-33/test_w1_33_kernel_role_files.py\n  namespace: root-files\n- path: tests/acceptance/W1-33/test_w1_33_roster.py\n  namespace: root-files\n",
      "chunk_id": "9ff2887d4b4a78c2518fc1ce",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "2dec6a2d42ace4d5a471afeb",
      "sha256": "783639a08be8023b2d2b59b175e16249343f1bb80bea76f65237c4f2065bcd1b",
      "path": "docs/emergency-2/audits/08-register.csv",
      "start_line": 181,
      "end_line": 185,
      "text": "DEC-184,2026-10-03,DP-5: the W1-07 drafts written under the wrong identity are discarded,tickets,history,,,One-off discard of W1-07 drafts,docs/DECISION_REGISTER.md:1719,theme\r\nDEC-185,2026-10-03,KD-1: every `gov` command loads the `governance/project/` files it knows; an inv,records,kept,,,\"Every gov command loads governance/project files, invalid file gives CONFIG_INVALID; path map still how roles stay apart\",docs/DECISION_REGISTER.md:1724,theme\r\nDEC-186,2026-10-03,KD-2: check declarations are YAML in the kernel template; `gov check --list --j\u2026,other,kept,,,\"check declarations as kernel YAML files, still how checks are declared (template/governance/kernel/checks/)\",docs/DECISION_REGISTER.md:1732,theme\r\nDEC-187,2026-10-03,KD-3: no public surface for the read/act class at W1-07,tickets,history,,,W1-07 KD-3 no public surface for read/act class,docs/DECISION_REGISTER.md:1741,theme\r\nDEC-188,2026-10-03,The plan validator accepts the owner's close of W1-45,tickets,history,,,One-off validator change to accept the W1-45 close,docs/DECISION_REGISTER.md:1746,theme\r\n",
      "chunk_id": "2dec6a2d42ace4d5a471afeb",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "164bd13e85c17ba0290cc87b",
      "sha256": "bb8fa9dd9fc0db33ca4890042a4580a6ebe60a884b61a48ad82dfceba572f817",
      "path": "docs/emergency-2/audits/04-classification.csv",
      "start_line": 1410,
      "end_line": 1413,
      "text": "d942524f3,direct commit,DAEO-drhj,,orchestrator,W2-104 (DAEO-drhj): allowed paths take src/gov/check/commands.py for the skilleval line (DEC-1020),chore,4.6r,records only,,,,0,0,1,,,,,,,direct commit (2026-11-02),direct commit,no,\r\n235c4d5d1,direct commit,decision-record,,orchestrator,DEC-1020 (delegated): W2-104's command-list line (P-W2-104-CMDLIST (a)) and the PATH residual (P-W2-104-CLAUDEPATH (c)),chore,4.6r,records only,,,,0,0,1,,,,,,,direct commit (2026-11-02),direct commit,no,\r\nf9d0685f1,direct commit,decision-record,,orchestrator,\"DEC-1019 (delegated): W2-92's P-W2-92-5 (a), no record-file evidence when the record graph cannot be read; W1-21's guard case stays\",chore,4.6r,records only,,,,0,0,1,,,,,,,direct commit (2026-11-01),direct commit,no,\r\n9a74ef2a9,direct commit,DAEO-cb2b,,orchestrator,\"W2-121: the nightly landing hold as a KPI line (DEC-1018 item 1, DEC-1003)\",chore,4.6r,records only,,,,0,0,1,,,,,,,direct commit (2026-11-01),direct commit,no,\r\n",
      "chunk_id": "164bd13e85c17ba0290cc87b",
      "routes": [
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
    "duplicates": 10,
    "dropped": [],
    "reranked": true
  },
  "rerank": {
    "by": "service",
    "device": "cuda:0",
    "reason": null
  },
  "expansions": [],
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
      "id": "DAEO-0pyc",
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
      "id": "DAEO-2keg",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-60rw",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-6n5k",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-6ox0",
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
      "id": "DAEO-a3m2",
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
      "id": "DAEO-csj8",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-cuao",
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
      "id": "DAEO-g23i",
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
      "id": "DAEO-j8gn",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-jip3",
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
      "id": "DAEO-kia7",
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
      "id": "DAEO-lrre",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-neam",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-nn1s",
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
      "id": "DAEO-rpfv",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-s694",
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
      "id": "DAEO-u4oz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-u5g6",
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
      "id": "DAEO-ym8a",
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
      "id": "DAEO-zqvn",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "path": ".tickets/DAEO-49o5.md",
      "chunk_id": "ee0fa7abc9a24be4a3593c07",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-49o5.md",
      "chunk_id": "411fad9acacee52dbff7817d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "9f581f5c6a55b9ef4658e846",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-56-effects-review.md",
      "chunk_id": "cf350552bbcf8db2f9178687",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "d90b2a65cec57f406c8a71ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-56-effects-review.md",
      "chunk_id": "2445fa43ae292cfee876c4dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "975f8e076948ebe4c3587bd0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8goq.md",
      "chunk_id": "4ac3fb866f3b88e84d30fcfe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-49o5.md",
      "chunk_id": "6d3510272710313e33965dd0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "f7364d93dbbd6840d2fdf7c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8goq.md",
      "chunk_id": "7c71290f2112167b9f7b96cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "5696c5533d46760c67c81f99",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "e87149310c6a899cfc04dad6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "8199c65d6e1e6896aab7a379",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-49o5.md",
      "chunk_id": "5cce15743faf0877077a33ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-49o5.md",
      "chunk_id": "5bec9d5056548dee69c240d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8goq.md",
      "chunk_id": "5e6cdd1fde982ffb1fd06e97",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-49o5.md",
      "chunk_id": "90092e47293f0650c598f675",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "9835bf6251dc7ffe9df1fb38",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "1c1fcb094361a1134370ce2c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-56-effects-review.md",
      "chunk_id": "0ae001484935ffb11962d10f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "chunk_id": "047f90971815d6e3923b6c43",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "bc67d9ae0775f012a8dd9f7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-56-effects-review.md",
      "chunk_id": "b2dbe152e2c844ce9fd82794",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.3/manifest.json",
      "chunk_id": "ac075435a53aa45f61740d51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "91bd94c96ac67fbd551a6c4d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-56-effects-review.md",
      "chunk_id": "f6aed3bf6584946cf9ee7a64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p8tv.md",
      "chunk_id": "5f7f4802982c7280aab6fcdf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "288f24051e410d80d783e62c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-56-effects-review.md",
      "chunk_id": "5c7bbbfe35974164ca83a6ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "chunk_id": "12c81631bd9624f03d9bdc52",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "8ebd1c0a61e940a50ac45412",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/links/check.py",
      "chunk_id": "555a36d19b826ecf87e56011",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "6e5730e0366b77047f896531",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-56-effects-review.md",
      "chunk_id": "df9353ee4d89d663fbd2dd8b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "chunk_id": "1ce64261a4bf508238e46bbc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "3237a1178b719a2500148fa0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A1-inventory.md",
      "chunk_id": "91bad9047cbe457b9621679c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "chunk_id": "0f2c81af63a88cb8604a6cc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "6d007b61198f56ae2eba1f50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "fe8f0dc2b51db474e345b957",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "e8ef90fbfa4b36cd05fa11d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-66-scoped-close.md",
      "chunk_id": "60773914b805ef1fa101274f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/EXIT-REPORT.md",
      "chunk_id": "58af5b9bc01b7484d72f4f4b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "65b641e4253e64e3a1f16022",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "a2f9b439b6524be6257be487",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "8db321b6ffb92a71148f1766",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-32/README.md",
      "chunk_id": "cd6fa2871f2c15e603614550",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-drvn.md",
      "chunk_id": "2b2d8c1af417cb101d8a8359",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "a4487c1a0eb1892134d7eb65",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "33cafa168e646bbdcf575ae0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-check-b-dev.json",
      "chunk_id": "59944c5ffc83c4e2799a7c7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "2f2894abe4b80b7ceff1a323",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/optin-lifted-breadth.txt",
      "chunk_id": "fc6b2e230398234e7185a336",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-56-effects-review.md",
      "chunk_id": "462a71769a4fad3ff8a3f162",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "05ac76a01d53e8bf1383330d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "2624d1356456ceea76948c06",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/optin-lifted-breadth.txt",
      "chunk_id": "8c4886736674e8cb65220dc1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "652011cbbc20d81301d62637",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "f0207a25091522202b5dde66",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A2-classification.md",
      "chunk_id": "57beca83d8af5782cd4d5df4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "f05f6065787e32e7b277ed63",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-doctor-a-dev-before-the-embedding-policies.json",
      "chunk_id": "381c7464f01589c9fbade661",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "90f992bbd7f280cf9a13c583",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "c931112d3bf1a1400de4b9ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/adoption/A3-target-path-map.md",
      "chunk_id": "57677bf2a1e81740b1e157cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "chunk_id": "800c7ab616944f704c27af5e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "90e73ff2283b8e7cf69d49b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-32/conftest.py",
      "chunk_id": "05f56e85d70b507c5db2a228",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/CHAIN-DISCOVERY.md",
      "chunk_id": "45dc70cd1891cb9bb06fb1ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "44d7f073bd9306083a4ea92a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-56-effects-review.md",
      "chunk_id": "1e6be0b90c6d67f37e8bf4bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0qs5.md",
      "chunk_id": "30414ece72a1c81b2bd9d004",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "3c273c74b21add6a7a90370f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "61480c198d32d454fa2313ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "7461edec838746b178a81d6a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/status/__init__.py",
      "chunk_id": "19bd4db6fa3de4fa20fd9339",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "b3eb3568eb6e924dc6169728",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "66f44b22151a74ab1f15ef7d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "d658908c3f30d41081a8d8d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "34a760899b222ca5badd44ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-59-CIT-P.md",
      "chunk_id": "ce941edddb672be16fefb114",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "b5efba9b4794140568e9fede",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/optin-lifted-breadth.txt",
      "chunk_id": "943185a069433189dd7abd43",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-45.a.md",
      "chunk_id": "1cf25a77bd66c47342756a15",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "62be3409c0b8edff89856dee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-45.a.md",
      "chunk_id": "2b1267c4180a6728ac7c6543",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-02.c.md",
      "chunk_id": "e3a2226614b4e97e94055785",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-66-scoped-close.md",
      "chunk_id": "382e48ea0397250c4977cc21",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "chunk_id": "538cd971d77a0ad192574e44",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "e645a7f0016d64e119d0ec4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-02.c.md",
      "chunk_id": "a7869efeebcb0c078a6384ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-43.md",
      "chunk_id": "bf01deaf748b88f164835c70",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-43.md",
      "chunk_id": "0ca1516d96c74aee2507717c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "1ef6e133676bbafed5129a7a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-43.b.md",
      "chunk_id": "50f65616da68125631acb1ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-43.b.md",
      "chunk_id": "762df4427e42067ab45664c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "195eb498cf3ededbeb627358",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "11850de1a16db1bbee60ffff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "0577e968b4ddf949bd39f4a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "c66ce9250e6633609a327842",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "437f4667fdf17f5cd07c45f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "347299835b9b09b3ad6e753e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "b8b1a392b1d7de85513b2b2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "4479de3cd55c71960a8803e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "ac2bfd0d161acd1e2cd03d39",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "a3416abcf8e2c2a668a691df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/L2-COMMANDS.md",
      "chunk_id": "699f729f4c913b4bfc00dd31",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "4f1f018c6002953eb0834b57",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "9033c95cf495cc77eb821155",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "ccd8b1f73ef858134fa7f7f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "536ec010d76415d5536eb8b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "cb1ac9960a9c4f1a9406603c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-156-evidence.md",
      "chunk_id": "8f581c572c4ebae606efdf0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "968f97f5934de02194dc567c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "950aae0823fe7fe1cf2041c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "bf8086b7c9163fbdae26024b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "a87d5b4df10894cd7c3865ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-8goq/CP-DAEO-8goq-0002.md",
      "chunk_id": "02216b4f0c42c3ff96c67096",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "f728fb5a189b757ffacdb46e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "2e69abb8f8e8a3b0dbde00b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "befabf34fb8e831519b7320e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "7fc2685c81e19287feff83df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "f9f9b61d0e5ba66abc53ad14",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5y8d.md",
      "chunk_id": "fbbaba9a16c898b9c9681def",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "2ad53b6c537a997032cdee50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "75ca27447a384be2c06f50a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "161e6457f1af8dcea089911b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-commands-review.md",
      "chunk_id": "3e9245b2d9bfc2663b2c72e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-doctor.json",
      "chunk_id": "03aa90e7693529d4f6f5f455",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "a62953bc903517b189944ac8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-8goq/CP-DAEO-8goq-0005.md",
      "chunk_id": "516004cd3a09ab07bc5e3a81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "676a6f04c3c882eefafb6cb5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "f5faa1644e7593ab3a414a2d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "36eb55155ea3cd0646d10226",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "e535d964a9a32d34e6466805",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-xw3k.md",
      "chunk_id": "c5640934c61df795658a3f8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "52e6bece0a3935872e5e266f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-60a-CIT-E.md",
      "chunk_id": "2c32528840abe492c385f661",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "132fdec0f6b9f205f96988b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "9f114478cdc4d1bd4dd0b761",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kh9l.md",
      "chunk_id": "f458dbfc8703af01721053d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "3ccadf132750eaf9484ba5e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-49o5/CP-DAEO-49o5-0005.md",
      "chunk_id": "bcf101e69f8850d1d274a0c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "chunk_id": "3808d3726a2da5b447fee2ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "1839297b3ec6268cd3209902",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-commands-review.md",
      "chunk_id": "112ccb10a118b4fcc380fe31",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "chunk_id": "b010207a8b3d6fe1360d7156",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "fb359088cbfa1ecd91f14f95",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "4e9673a9db944a42e9927e73",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-check-a-dev-run7.json",
      "chunk_id": "1a546ff62af1e7c9e26d4b69",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "fc8c92043a2e0d063730df43",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-49o5/CP-DAEO-49o5-0010.md",
      "chunk_id": "5b37fe2868dde2f0985a0431",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "66e882040ca5f7b2fe80aa2c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "a61921b975b89379c4d26ed3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "chunk_id": "c92ab7c0d8e68621b433e711",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "e3cca766891e0c75bb8ca524",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adapters/portability.py",
      "chunk_id": "027fe1c7fb8f0dcf0f99ce48",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "1d51cd9d8049175a9abae2b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/path-map.yaml",
      "chunk_id": "dfe7342d41d61691fffb1dd9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "chunk_id": "cb97f67af9e82cd72761b886",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "8a6f2ce74369169bbb03e5ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "c9d0462662e234ad37781521",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.3/manifest.json",
      "chunk_id": "53a23519fdcea17a23405b7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "dadb663c5fb4ff3a8e9915cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "24154858809b4a20eb2b628a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "7627761395e44046a981467a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "d0b59ce7818d5f9e786d07a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "14f786fb5cce0472157f0ce1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "473427264d88d0ad442a5f90",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "b3d552ae689b7985d611f22c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-w19l.md",
      "chunk_id": "bfb18506e01826885363d2e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "1ed49a2bb6e827021893c1f2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-66-scoped-close.md",
      "chunk_id": "3bbe5a615ac7529a6cf87659",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-check-a-dev-run7-ci-head.json",
      "chunk_id": "5da8264d699489ff24c4f89d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "32e2b7ce05a3e86122d2212c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "67292306db11eae7c1c77842",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "144c635b6c3d448ddbe4d268",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-slot-path.md",
      "chunk_id": "18d83fa979498a03f82e1cd0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "chunk_id": "a7c246d63b900602c98ff772",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "0ebed2b21e7aa5a3446694eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "bc26e56f4556c534bf4eee0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "0c45d3e7472978264e2c40af",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/wave-1/W1-43-wave-1-exit-audit.md",
      "chunk_id": "66349faaf13003b1c10bae3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-doctor-run1.json",
      "chunk_id": "919b9fba44875960a463f23e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "b8622c99eea1f0d9eeecae8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "chunk_id": "31279137d61ed83728e0f35f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "b7cd38127192212b01d11819",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "2389a07214e3705f5992e785",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-32/w1_32_support.py",
      "chunk_id": "e72984b8b7a98cae5ff84789",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-GUARD-PARSER-W2.md",
      "chunk_id": "011cd1442ab0b06d9761093f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "73cac540990444cb479643be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "65397ee71cfcb1b630319a76",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-66-scoped-close.md",
      "chunk_id": "80de422edf7f3613f7c7d291",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-check-a-dev-run8.json",
      "chunk_id": "0c042641dede8f0ea4b5d224",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "0c2d3bea847aba40be3d4127",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/facts.py",
      "chunk_id": "9be456a5e7215fae49b210c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "79a3b3630be3d83065db679a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-xm6l.md",
      "chunk_id": "fa198678bdd095559dced835",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "9e75ebe87831dee3725120cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "b0ba6ad4d023cf1df9d7c3ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "9007be42b55e9c1c87829bcc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/wave-1/W1-43-wave-1-exit-audit.md",
      "chunk_id": "04700986f489fbd4010a35cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0cd2.md",
      "chunk_id": "3b14385ddeb3d4261a102a7d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "75912f657554f6ccbbcd6dc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/queue/coverage.py",
      "chunk_id": "350a7ad5fbfdc2925d15a2b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "00c0f6e9432037c075b2caab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-6n5k.md",
      "chunk_id": "8f75dc8029070c936895ec7f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-drvn.md",
      "chunk_id": "c3966e333d4c90dae48355aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "17b3e20e8a3f79a9abb62207",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "183a5fdaf009d9a596c0ef42",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "059a2e925cff87ae9113a4f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "86ea8a181a25a7895649e41a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5rgj.md",
      "chunk_id": "ac39d4208c72b732f6d73a50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "5667f9c5581e05b13cdb52ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "19d2aedb81bc8e0748f94400",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-32/test_w1_32_command_set.py",
      "chunk_id": "748dd550830e512eb399677f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.2/manifest.json",
      "chunk_id": "ffae2e205e3c8f0812dd59b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "1f0365fbdaf6fe263cab52d6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-184-CIT-E.md",
      "chunk_id": "567bd4a1809d261d8a00c52a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "d796afda5c3a0444f1166df1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-170-evidence.md",
      "chunk_id": "7a6390337a15d0c7b07f3c72",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "72eb71313070586fa223d0a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "5e474e6a411666aaa0544d60",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.0/manifest.json",
      "chunk_id": "82855b0e56ad6ec31fe7afa9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-32/w1_32_launch_support.py",
      "chunk_id": "518830b2e4ea92cd04774a45",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-8goq/CP-DAEO-8goq-0002.md",
      "chunk_id": "2dd3561954623ff8836cec5a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/RESEARCH-AGENT-FAILURES-1.md",
      "chunk_id": "770b6f31212320f5009f4eed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "65c283bcd2b3019e32b836f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-158-evidence.md",
      "chunk_id": "2e12aa1882de37a438b8ce58",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "ace58381a586b5bdffce5be8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "ea7df1c34d72ee2a9deae729",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "5c0a6413644ea3c15f0e3b77",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "a38b59da867ec95e73ab5242",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "2ef1a41b32fea1df71180dd0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-61vm.md",
      "chunk_id": "864baff15d69abe4bca5fe1c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "0666e62db410e736fc7cdb2d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "a91c9153d02ad9ff90ce2bdb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "95d54152233c480b4e89101b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "85e91bed92043d13312f4b7e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-11-pathmap.md",
      "chunk_id": "be93da4896edfbf083c16b8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "5837412cd26aa8ee9c189e9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "67f2d64a7bd761b1e680809b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/evidence/gov-commands.json",
      "chunk_id": "a52b4a2e8b0091cb20ecdb99",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "57d19219d2986abddf9ac9f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "b536ebe1ff7bc08564639538",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-152-CIT-P.md",
      "chunk_id": "22a1db2c102c3a80ec2338a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "21c3b617cf9381b643b36313",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "9c2c3fc00b7568288392c7ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "4ca98f1c0530b270b0cc4beb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "e8545b24e888085bf271bf5d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "c3145847746103f504a2fc86",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "bb0cad643373c29e65688775",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "3a53e071eff3b892a02d9b11",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "fa97e98094e26778b8861281",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "702622ead12f4fea80275cc9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "7df4df5f546c93e35534d549",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "9b0916c16871115cf16ff614",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "d2562007137c872aa9f6454a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "d7824e1d7e7c00703c9d198c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "60ff2a8be43717951494f5b8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "b34679b5674daf681fa26bf6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "3c8ce200d91a3e56ccd7d750",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "79cf260285f37c9eb7b652a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "50c846d8a96b49522f1f29b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "6e6676efccb4c4639665f076",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "6662eedf85207980230c1eec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "143b7500da6e0d40e558338a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "abfd4c6ca636688a622b93ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "8d1e017f911a05cfa62516c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "5ee22a9a467c10c7b15005e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "af522fcf963881694ce6d6ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/skills/devops/check_domain_skill.py",
      "chunk_id": "4d16e2d4a7dcf771b7ac36a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/skills/frontend/check_domain_skill.py",
      "chunk_id": "ccc0db4416906e78a2850225",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/skills/ui-ux/check_domain_skill.py",
      "chunk_id": "76d86d12140cf941663b651d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "7772c21dff1ac3602de40943",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "ffe751874aa93d3faef431c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "1c9e24dd5b6a9f4f18167d76",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/skills/api/check_domain_skill.py",
      "chunk_id": "d65db6ece977e6d481cd1af1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/skills/backend/check_domain_skill.py",
      "chunk_id": "46957c6b45783a92a56aeff8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/skills/data/check_domain_skill.py",
      "chunk_id": "950ba636ece7fd6011b1f34d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/skills/security/check_domain_skill.py",
      "chunk_id": "43795fefff93829984be5817",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/skills/security/SKILL.md",
      "chunk_id": "43fa9abe94dbce226e4d20ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "c086caa6dd4fa4047fc08e61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "79e0e63f59a1b215fe5f667b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "0bca1fcbdfcda5d0adf39795",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "ba96eb45523a033b7eced881",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kh9l/CL-DAEO-kh9l.md",
      "chunk_id": "ffbd73e67bed31e737ab58bd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "de7af025d57431dd3ecc1fb7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "12c0f1daa84f061a92bab412",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "6d66f464d4a467e487692d15",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "feb04d55f0ff5f680fc5522a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-p7a.md",
      "chunk_id": "2266c8cdf7695920c5a13c72",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "f61409142d7e00d1c645b94f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "9f26818e10c88028714d0805",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "c62caf528fe3aadeca1e6ed3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "5a6fc7e476ba623f5acacc05",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "010a0bef89c2c9305cf627d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "7bf26c1ee400a546ef45a501",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "6ce6662a29207593989e347b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "8a42cc23cfb8af0f733d228b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "171509479756cf5b8091805e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "e7a7ca42df1731e372e507df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-8goq/CP-DAEO-8goq-0005.md",
      "chunk_id": "aecfb4a2e845aff2dc3343b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "7407eb41de730632114780a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "2f6659734836b5fab230b1a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-drhj/PR-DAEO-drhj-run4-narrow.md",
      "chunk_id": "07abeb4916e6b69fc9758190",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "6ec225d9c5bb042f88691202",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "7a282842a7545eefed1f1852",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "cce2b0adbd580215380ebadf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-ouet/CP-DAEO-ouet-0009.md",
      "chunk_id": "90588c4e67258db43b2720a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/A-purpose-roadmap.md",
      "chunk_id": "865a209db2427bfd742f84a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "4e1ff7c72ce9a608c47cdcbb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "b99bbecb2e20f28a46a504a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "cea4cc9459921f403b35cb82",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "bbb671f54a02f5ad86501a3b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "0b5097a5c814f405270ded89",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "47bff630af6f83e1e91e9afd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "bfde643f0b9c5c5834a5a37e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "661166f1fe71d89468f21db7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "cc18fefb25afebd72fddf6c6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "f75887209b46a09c768936ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "1d1a8b62c0c1e6bb910ddab4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "d4f7a369cfa72f5eb3ee412c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "5cf38dc389e1966fd3951000",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "71f1ee8d776b270376257fc0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "e41da8706544182f300a5987",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "61b7640b2b8399a982bdb451",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-juee/CL-DAEO-juee.md",
      "chunk_id": "f302a5a9870d2203c967aa43",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kh9l/CL-DAEO-kh9l.md",
      "chunk_id": "9fb6df6c189167bf7d469421",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "97332d011e049f5a0cb9e5fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "5999204e9937def737a7ba58",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "28b4996f8308f10d2b799e68",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "177d029c67fb863b9fb6b682",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "913514685c79dc5978c373b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "c10bca4854a0fe2113aaff6e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-ouet/PR-DAEO-ouet-d10b.md",
      "chunk_id": "2f39347954220a066898bf93",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "6e651cb177ae0700686edda8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "c50ac5aaf20a67192a0d9a46",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "3ccb314dd03a49a4e66106ad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "18752e989fbccfe2c07456a4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "0af6bf2f678f4233cdf8ea78",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "77d9e93bf8d712d6dde2ec00",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "de7a59af60df859a62bb6279",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "dd6ec52ce8362ebfd581efa3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "baa2d4470eef9b8cc376ed5b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "01dfd765ac76b1616719f321",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "facf28b813f15e63e6f7e031",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "864d69b56d6a0306a2fac943",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-96/README.md",
      "chunk_id": "2d763919aac818aa0dc4c2fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-49o5/CP-DAEO-49o5-0005.md",
      "chunk_id": "d5af663f77ea42f995e69ae1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "55df166922fedc74a4ff261a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "7eebc35aa8305070555e9100",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "207ad4598975fb649029a14c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "6f32308f273c1e3eab1ed052",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "c14958d9f4d9e4639b4b0d54",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "25f0be9b9d1a8d8be78dbcc2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "d7aa7d0a40ecceb7d5ce5c04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "beb8f32fb67a42fea0e1b546",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "b5cc1cad71d7f23d153b8fbe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "c920ae33893f9a8b5778b7d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-09/README.md",
      "chunk_id": "50ea9a69c3f742253353f7d8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-153-r1.md",
      "chunk_id": "698921bde1f53a0a8aa246a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ouet.md",
      "chunk_id": "d204a9a56548402f3f018588",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-60a-CIT-E.md",
      "chunk_id": "0622c1a4e67990ce4ffd22c4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/context/contract-current.md",
      "chunk_id": "ac0bb52fc8db187eb66d9f3c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "3c7415ec617a0675f98f61cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-commands-review.md",
      "chunk_id": "d0097faee524e813cf99c113",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-49o5/CP-DAEO-49o5-0010.md",
      "chunk_id": "924bdc23ce66069771583fa2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-launch-gate-sweep-review.md",
      "chunk_id": "9fa8c016f588b8e63f62269f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-drhj/PR-DAEO-drhj-run4-narrow.md",
      "chunk_id": "63270e1676fd2aeb3abce5c4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "b38b55b42bc2efafcf2a1b3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-66-scoped-close.md",
      "chunk_id": "03a4b36d659c1fde8839868f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-launch-gate-sweep-review.md",
      "chunk_id": "030a5bcfdf29313cfbc95c09",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "f14f1bde602ec9f82e9bb1b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_1_WBS.md",
      "chunk_id": "944d1809b0b04262ec9bac5c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "29bb6685b9bbb4c62602f371",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-156-evidence.md",
      "chunk_id": "aea5ff124716b62c66ba4a9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PKG-W2-37-CITP-1.md",
      "chunk_id": "6367222beb4996abd0b8453e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-ouet/CP-DAEO-ouet-0009.md",
      "chunk_id": "9f61b37049a7286c160db7f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-drhj.md",
      "chunk_id": "76c35f9bc20ee483d51733ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/context/contract-current.md",
      "chunk_id": "6f0cb2d06af095471214e50e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-slot-path.md",
      "chunk_id": "a12dffbcc128a36274d0a594",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-slot-path.md",
      "chunk_id": "291ac8e9d8a5501bb1de01b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "fd6e2dad87dec53f00bb5235",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l4gf.md",
      "chunk_id": "dfd974a2797b3e51a87b81c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-slot-path.md",
      "chunk_id": "eb954311e86897aa8f8e17b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-slot-path.md",
      "chunk_id": "c9853d51b2ef01c42f141656",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-slot-path.md",
      "chunk_id": "cbf394858a8bcfd940ffd118",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-slot-path.md",
      "chunk_id": "0bb261ba02fe872cd8d44a57",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_1_WBS.md",
      "chunk_id": "f5953997fa1383905f73db57",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "e2347437d771b6be62beda8f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/D10-RECORD-REDS.md",
      "chunk_id": "4aad1b134ce30d016cfb3e29",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "4d12db0dc524892e5a31f9bd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-9-impact-landing.md",
      "chunk_id": "1b405b38e407383bbf946b3c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-slot-path.md",
      "chunk_id": "78baf48e80f552a1404debf8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-slot-path.md",
      "chunk_id": "ce33c555aaf057ba91a2248e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/w1_07_support.py",
      "chunk_id": "9278afc330891f9f0a8611dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/path-map.yaml",
      "chunk_id": "54adbae06c985ea26f1d93ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-cv58.md",
      "chunk_id": "e0492c8d720246f2fff7642b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-slot-path.md",
      "chunk_id": "e98389edf23bbeaef2b62c98",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-96-R4.md",
      "chunk_id": "6171448ad03046a6dd801022",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_1_WBS.md",
      "chunk_id": "2797d8b26f36a04c1d1ce5f7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-2azm/CL-DAEO-2azm.md",
      "chunk_id": "6a202c38ae86220fc08f4d41",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "fa8b59a34adb83556e7fbc58",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kh9l/CL-DAEO-kh9l.md",
      "chunk_id": "8a72daced52bfc87a26074da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-qty6/CL-DAEO-qty6.md",
      "chunk_id": "f19a02bacd1d0d133d0d36db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/wave-1/W1-43-wave-1-exit-audit.md",
      "chunk_id": "f70465b8d3f18bedb2692cf6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-50-CIT-E.md",
      "chunk_id": "bf7b5592e30f39c30a217b55",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-pl6k/CL-DAEO-pl6k.md",
      "chunk_id": "698bb3fd16619eeaa5a34fdf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "38cdb842e8eaa91c1a467058",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-r9ss/CL-DAEO-r9ss.md",
      "chunk_id": "f1d5e7970ea5fa88dcb9692f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-rmbe/CL-DAEO-rmbe.md",
      "chunk_id": "00a6420e3e6e94b2a530dbe9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-ye2a/CL-DAEO-ye2a.md",
      "chunk_id": "fdd4b62da006fabe1e29b33b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-60a/README.md",
      "chunk_id": "b703cf2abe93983e315c89ad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-commands-review.md",
      "chunk_id": "9de2f3ac18fe8d6083071983",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-drhj.md",
      "chunk_id": "9542abb9bad5f42b6b670c95",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/wave-1/W1-43-wave-1-exit-audit.md",
      "chunk_id": "f85ecdc5c77b44d0a02e072d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/status/command.py",
      "chunk_id": "6276173f701719ba5917bad4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-58-CIT-E.md",
      "chunk_id": "2fb6766929e581a7e93f1901",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-58-CIT-E.md",
      "chunk_id": "58cacd8c30444ebe98f92dd4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "a293a195a613b03f0fdc6a86",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "7954498198426eabed62db3a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "096a9bb3d7d558eb2afd9f6c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "d8a5817663256238583af376",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "88a87c15ca0c9e72f04408a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "758f93ef5e22a1a2ea5b1749",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "db862311ff30321774ac1765",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "482f1e07dc7f9f68c1fec901",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "ac206a40cdf26f492f182d43",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kh9l/CL-DAEO-kh9l.md",
      "chunk_id": "c16b736e6be96148ce2c3950",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kh9l/CL-DAEO-kh9l.md",
      "chunk_id": "8302f19b9a53c54e5c58ed8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "c11fe314e0cc8ccdad49f1da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "4f3497a0dac6eeef308e58df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "8044fe25a5ac493947b60aa1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-60a-CIT-E.md",
      "chunk_id": "b146b85ea76212cd77829a9a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-50-CIT-E.md",
      "chunk_id": "4deeeebeb51e8c09a53c5acf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "7d3f8220f402269c399d2808",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "bf36d16aac0282c497694ed3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "ec8f8c8bf3598f2815c5caa0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "ce1b4f8341a354e0217b7d8f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "a4bca7ba170976c073af5b37",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "e8a274492e9f3a817fb585ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "8167ce22a4a25aceaf369e12",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-16/README.md",
      "chunk_id": "acd45731e8eebf17da773c22",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "0e24401fa07469139b0c644a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "c78b167fdf93031f2135b8fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "0ebe720558dc8047907fb22b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "067166abcf086c8659af32cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "a4e1dcea7e8a7e088a98a1f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "96373d6129e161a8fea53596",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "84a4672f7ebb341a2cd2bfcd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "c312d4e614de3fc9cd4982b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "0ef32c080b34b09e8022455e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "ec677e2f1519f90fd7138cbd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "b5c996b447209b379bb03bce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/launch/test_w1_28.py",
      "chunk_id": "1871126b024064f8949ef111",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.3/manifest.json",
      "chunk_id": "0e6df2c00852ec3e1916a723",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/EXIT-REPORT.md",
      "chunk_id": "7ca536784992cf522230d89f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-03-DAEO-ym8a.md",
      "chunk_id": "fb997486caa64ea4e0f420d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-26-DAEO-2ds6.md",
      "chunk_id": "88cfb9b161b75115f2c635db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-51-DAEO-egsy.md",
      "chunk_id": "a0296250898177e620e14a8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-57-DAEO-cy5o.md",
      "chunk_id": "b8f2a4aaa83ba5cf53ee0fd5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-61-DAEO-iw1f.md",
      "chunk_id": "2632862b781f34c8955dcc1c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-64-DAEO-0uhh.md",
      "chunk_id": "ca3dfaa867867a0c57f8c453",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-77-DAEO-b6hm.md",
      "chunk_id": "6b14a88c0d031e25e1efc232",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-85-DAEO-gdzh.md",
      "chunk_id": "53b1a0758b058f9095983ad4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-87-DAEO-s9qc.md",
      "chunk_id": "d567bfbf2742cf39bdc953d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-90-DAEO-8lmb.md",
      "chunk_id": "ecb05fddabfbff941b40eca3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-153-r1.md",
      "chunk_id": "9a27e738033747caa88b98b1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "c40913bf22c3d6bde2b6edfe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_1_WBS.md",
      "chunk_id": "ca4841d03f228d75b2c1a8d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-50-CIT-E.md",
      "chunk_id": "2d5a52cf104c11b4693627b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "27daeb870c59c044d3e58432",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "71d98d6f5d4f9428affcb4fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-153-r1.md",
      "chunk_id": "59b1f6e56c88534005b6c0ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "9d0de9a5def363382f6e9256",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "93f1d695429de1401950dbe7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-juee/CL-DAEO-juee.md",
      "chunk_id": "c889fdb3e3c6bcb54b8dc79a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "14dffded78f1168fc40cf2c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-5j8b/CL-DAEO-5j8b.md",
      "chunk_id": "8020526908a0c230dda85752",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kh9l/CL-DAEO-kh9l.md",
      "chunk_id": "e44ccdb306c418bb418118b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "81886223e6223d982d6fbe22",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "6027ea697420581564f7817a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "6b2b294bbeb3b794d1894c31",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "06e07abca9303d2f0b7bb07a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "9cebc76b6da09b30965c056d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "abeeb428b439df596825a3fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "cf24baf87e0c7d1971476ef5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "5c5023d8967d03557037ea46",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "18497ac48d93ce4503afe5c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "39e6004bffd0827fec7145f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "28a1294a70b4feed1a8245e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "8042a44917868ca189b70c4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-50-CIT-E.md",
      "chunk_id": "3effb2ab6fd3c045668a8201",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-reds-records.md",
      "chunk_id": "b6fcd36c9f23c4ff6be4c85f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-1-exit/EXIT-REPORT.md",
      "chunk_id": "bae8edb91973c8516179f89d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "f0920a9f0fa646e9be88c3d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-60a-CIT-E.md",
      "chunk_id": "915b45676b295c502757d6d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "996d39d549dc5929fd4470c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-reds-followup.md",
      "chunk_id": "a67b480dfa3c238a5b1dd9bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-66-scoped-close.md",
      "chunk_id": "7852a5a51fd0c021acaa2379",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5y8d.md",
      "chunk_id": "72ce2e6d5d4d048f057955a8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-66-scoped-close.md",
      "chunk_id": "7e0ea9594795cd0a927845a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "8177929a574d7a58bc4c3565",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-launch-gate-sweep-review.md",
      "chunk_id": "c0b660884544ad9f7ab77063",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_1_WBS.md",
      "chunk_id": "7161a5d44743c0f737abea0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "120965e2e3871cf02d462c83",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.3/manifest.json",
      "chunk_id": "3313027705393f55a279d9b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_1_WBS.md",
      "chunk_id": "b8a93c9605b22854358d8057",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "d0ae279d7349b394b77aa9c4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-66-scoped-close.md",
      "chunk_id": "518515fffd96acb445790f53",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "7ccdcedb298c07920a728343",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "chunk_id": "c39e527751c7ac7b1a49e12b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "ed92385b90ee895c54fe893a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "c3aaa61f7776e4ce714a2119",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "d4de99afd882597566165b9d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "95ffb6f15b7c95f8f8b15cf1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_1_WBS.md",
      "chunk_id": "8ebe3c6d57925c68ef7f7bbb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-commands-review.md",
      "chunk_id": "f894aad1cdfb118a3f0ffd6e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "9969d3a9975c4f91181c0781",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "158e1e89ccb0f787fb3170a4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-launch-gate-sweep-review.md",
      "chunk_id": "fdd1072c7bfbde9b1de1a55a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-2026-10-31.md",
      "chunk_id": "bb5a41cb8f32cc9595cf5ad5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-184-CIT-E.md",
      "chunk_id": "a87fdc345961d19164c9e22c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-20261113.md",
      "chunk_id": "0f4e49f1dc27d6869de56c37",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l4gf.md",
      "chunk_id": "e2d4bf5639f283b04bdf5eff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-66-scoped-close.md",
      "chunk_id": "c63971519857229616c8ba36",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "836cd36f536ed00ab97490e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-66-scoped-close.md",
      "chunk_id": "8477dad08b5f5e794066d5cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVENTORY-TESTS-CODE-1.md",
      "chunk_id": "a085c742bd371e498790d424",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-37-DAEO-6n5k.md",
      "chunk_id": "193102199a80279283e7967b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "chunk_id": "3edc2cd3b464a8a18c489b2b",
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
      "path": "src/gov/doctor/command.py",
      "chunk_id": "2f9baa4cc0f34800a44fd1d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-136-evidence.md",
      "chunk_id": "9cb290d4a830617fc33598c5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-136-evidence.md",
      "chunk_id": "256432851bfab62142dfcdc7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "1de9105a0509c8afe4b700d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "a102d361c16ce783db519e96",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/OWNER-GLOSSARY.md",
      "chunk_id": "31c0788cc50d9ab7ede0dc5a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "5d2ff612d7e4731cf67bcafc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/f-checks.md",
      "chunk_id": "899fdbed78a3e0295f95f2dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "b601c260b505af0056b6bc8f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "97dff7f44dfdfd1077d29ebf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-commands-review.md",
      "chunk_id": "e491d6a3c9ead4f76feddf61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/EMERGENCY-PLAN-2026-11-02.md",
      "chunk_id": "cca778d371a830a73629fd0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/wait/command.py",
      "chunk_id": "73b559ec63e088b76f07a0de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/plan/command.py",
      "chunk_id": "87c32013300e642fd021b7ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "1f440a127739ded75be735dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "a71973ff578f06807b16230c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/brief/command.py",
      "chunk_id": "45509c373aa8d8ef76d44d95",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/update/core.py",
      "chunk_id": "734c9d2e9c447289942d53f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-11-pathmap.md",
      "chunk_id": "92bf1c54389463cb49001967",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-11-pathmap.md",
      "chunk_id": "57e567ce7e73cc14b6c0fb67",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-61vm.md",
      "chunk_id": "22baffa9005040664a6b1175",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/update/command.py",
      "chunk_id": "e8c7bd963e6b79932920b6d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-61vm.md",
      "chunk_id": "9336c606e6bce3219279858c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/update/command.py",
      "chunk_id": "76582795d2039d4ac8b1d35f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "chunk_id": "735895d419c731f227e13591",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "chunk_id": "061d4f32b80dfc6f21475e56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-kit-e2.md",
      "chunk_id": "aa7a46a8853de2aaf7451b76",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-11-pathmap.md",
      "chunk_id": "d418793adb283c5f91b5f574",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-3-MCP-TOOLS.md",
      "chunk_id": "8c5890a652aa2136e083229d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/L2-COMMANDS.md",
      "chunk_id": "a913fa6e6f7ca9fdb1e3e008",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "bbcf90e05f24dbd6119df859",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "37ad87978b8d9bd7427857c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wahn.md",
      "chunk_id": "678c895b23a2a79709524469",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/adoption/adoption-path-map-verdict.md",
      "chunk_id": "48bdf577ce5b7e0d256d8ffc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-p7a.md",
      "chunk_id": "9e69c8862da8d498b91933c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-drhj/PR-DAEO-drhj-run4-narrow.md",
      "chunk_id": "5f85ddc8aa87c4f46c5cec29",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-drhj/PR-DAEO-drhj-run3-narrow.md",
      "chunk_id": "b7bac73c51b806ec16b2981c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-30/README.md",
      "chunk_id": "374409cb89a9eb0c2455e341",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-28/README.md",
      "chunk_id": "b542494e7546a1462ae23ffb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-drhj/PR-DAEO-drhj-run3-narrow.md",
      "chunk_id": "a62d07d950c2753504d416e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/C-decisions-to-spec.md",
      "chunk_id": "3a7a55a19b095d28d4e3a72d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "f56bcff3506ba858b6c74088",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-49o5/PR-DAEO-49o5-last-round.md",
      "chunk_id": "68364b71b98147569b8939bd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-30/README.md",
      "chunk_id": "077a56b89fd3b5b72ce434ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/README.md",
      "chunk_id": "2f73100377dc7cafd007095a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-drhj/PR-DAEO-drhj-run4-narrow.md",
      "chunk_id": "3b360025f03b2bde084a7550",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-16/README.md",
      "chunk_id": "9f8909d2fce3652798ceaa61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-f58b/PR-DAEO-f58b-pass2c-narrow.md",
      "chunk_id": "41f6110451a4d179a161d423",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/launch/test_w1_28.py",
      "chunk_id": "88f26b3b40fd2a208a8afea1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-35/w1_35_orchestration_support.py",
      "chunk_id": "30c6ddb45a6f1e5f31ae4457",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "8be641c8a2a7dd553031c63d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-drhj/PR-DAEO-drhj-run3-narrow.md",
      "chunk_id": "91c55ba211844fd28be3d53c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-184/test_w2_184_s1_no_criticality_file.py",
      "chunk_id": "f1c9cb5711dd48d7fbd19457",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/README.md",
      "chunk_id": "367a1b19cca268efadd06981",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-121c/test_w2_121c_rt8_launch_line.py",
      "chunk_id": "421bf7c8fca23f9888f20497",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/wave-1/W1-43-wave-1-exit-audit.md",
      "chunk_id": "4f4be21efc1ee3587c17170e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-46/w1_46_support.py",
      "chunk_id": "742fd0ea8b842ca4dcfcf580",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/w1_07_support.py",
      "chunk_id": "ba0394c2af18bb3eae4312ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-5y8d/PR-DAEO-5y8d.md",
      "chunk_id": "6b04d7b4c1576b8f453b6c45",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-104/README.md",
      "chunk_id": "6abe90063ee40843a03c782d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-09/README.md",
      "chunk_id": "911fce61bd6fcd3db5cf29d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "f6939f951a96e5896b48a0c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/status/test_status.py",
      "chunk_id": "ff762b72acb6a96772eb8035",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-09/README.md",
      "chunk_id": "7ce82b25199bbe89e97a1648",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-ouet/PR-DAEO-ouet-d10b.md",
      "chunk_id": "af3a38c1c4e6236c69788824",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/launch/test_w1_32.py",
      "chunk_id": "b4d3a5e73200cb0f6487bcc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-p7a.md",
      "chunk_id": "07196dbd2c6f174b6e4413f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-49o5/PR-DAEO-49o5-last-round.md",
      "chunk_id": "00e3ab8d39adb1fbf44dfe66",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/README.md",
      "chunk_id": "3a33e16dbaefc1c589e9fa1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "07049630516f34b4cbb783b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-p7a.md",
      "chunk_id": "a0b69d95c365a94978a399fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "12890b5493c678be7c1353a4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "76b790fcfa4948233a0f8479",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "a688e8db429a4296ef42c428",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/test_w1_07_recorded_commands.py",
      "chunk_id": "b6179510004203f0845e99a3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "3106715cb19effd7455e444b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-09/test_w1_09_unloaded_package.py",
      "chunk_id": "c7ceb9b207730574e2749825",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "543192e01eb87fd6f699f86f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "3a94a78ebbac252876281ceb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-49o5/PR-DAEO-49o5-last-round.md",
      "chunk_id": "df4be2a30b4b8bbfe6d4542c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-ouet/PR-DAEO-ouet-d10b.md",
      "chunk_id": "0fa4cbb15f4ba73bfb4fd935",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "3449ddc6c95ca125ecf9e748",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "584cc5fe1f7b8bb5e380a658",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-09/README.md",
      "chunk_id": "88234e12de8740e77f0d1d1a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-96/README.md",
      "chunk_id": "523fae30032ceed913f29551",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-ouet/PR-DAEO-ouet-d10b.md",
      "chunk_id": "66ef0a8401a2f507951d0aac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-ouet/PR-DAEO-ouet-d10b.md",
      "chunk_id": "fa0382889717cf4f692387ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/README.md",
      "chunk_id": "4ab489f0f6bc92fc223879e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/README.md",
      "chunk_id": "525aa4af81e3fd82182dd884",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "a4d903d2a33a842e0bb51b55",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "4fea349351ccb710667b8524",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-drhj/PR-DAEO-drhj-run3-narrow.md",
      "chunk_id": "6c22801dc0f4e7379037f753",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "5e2c57bc130964840e2ee311",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "aa80dffce3ccbf13d9d02a96",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "12264868883ce72ffed51f4f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-ouet/PR-DAEO-ouet-d10b.md",
      "chunk_id": "a7cfee654d1fb729adbf0876",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-20/README.md",
      "chunk_id": "414877716416ae7a3303438b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-drhj/PR-DAEO-drhj-run4-narrow.md",
      "chunk_id": "8886507bdbd9ba3a87cc475c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/C-decisions-to-spec.md",
      "chunk_id": "66be0e732ede153a2a9d7133",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-ouet/PR-DAEO-ouet-d10b.md",
      "chunk_id": "aef879a2202ee5fce7454ddc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "a69986d4155c0389d495b8e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-ouet/PR-DAEO-ouet-d10b.md",
      "chunk_id": "ff60e5fc967276263f697fff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "b263e578d44af0ac40cfc155",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-17/README.md",
      "chunk_id": "7345fd175c47a95f2dc96124",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-187/README.md",
      "chunk_id": "6d379f0a4c65c090f2589c64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-32/README.md",
      "chunk_id": "60b5e3ffbc5335f387e22a50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-39/README.md",
      "chunk_id": "b7f857c9ff7d4fcc7dfafd35",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-38/README.md",
      "chunk_id": "87b7c851ab4c21396a33f8ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-187/README.md",
      "chunk_id": "48644c134bcd52638f689d10",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-16/README.md",
      "chunk_id": "2f615bffb3320bde9b4a2d57",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-187/README.md",
      "chunk_id": "f82e739654ca896d812171af",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/memory-measure-new-visible.md",
      "chunk_id": "4a0784334048e5b1bf024cef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-17/test_w2_17_fix_hook_once.py",
      "chunk_id": "c488275df55ee165a80c2a0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-206/README.md",
      "chunk_id": "fd99a51438536826d4c22b56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-197/README.md",
      "chunk_id": "0d0f240dd249a33092c212a3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-120/README.md",
      "chunk_id": "a3c6b78bb10b65acb687553b",
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
          "CAP-45.a",
          "CAP-02.c",
          "CAP-43",
          "CAP-43.b",
          "DEC-772",
          "DEC-1220",
          "DEC-1222",
          "DEC-1223",
          "DEC-1224",
          "DEC-1235",
          "DEC-1251",
          "DEC-1204"
        ],
        "left": 1
      },
      "changed_by": {
        "DEC-772": [
          "DEC-1223"
        ],
        "DEC-1204": [
          "DEC-1241"
        ],
        "DEC-1222": [
          "DEC-1225",
          "DEC-1223"
        ],
        "DEC-1223": [
          "DEC-1235",
          "DEC-1224"
        ]
      }
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 7819
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLTV5OGQubWQiLDI4LDQzLCIyNDY2ZDhmMTMzNjczY2UxNDYyNTFjOTgiXSxbIi50aWNrZXRzL0RBRU8tNXk4ZC5tZCIsNDMsNDQsIjFlMmViZjRlYjRjOTQzMDZiZmZiMWJmNCJdLFsiLnRpY2tldHMvREFFTy1zZGhqLm1kIiw4Miw4NCwiMDEzYWVhMTlhZjIyOWQ3Njc0YTdkZDkwIl0sWyJkb2NzL2NoYW5nZXMvVzItMTM2LWV2aWRlbmNlLm1kIiw0NSw1MCwiMGQxODRhMzljNWMwZmY2NTMwZjcwNzMzIl0sWyJkb2NzL2NoYW5nZXMvVzItMTU4LWV2aWRlbmNlLm1kIiwxOSwyMCwiZGNlZGM3NjQwYjBlMTZkNGIwYjE0ZDZlIl0sWyJkb2NzL2VtZXJnZW5jeS0yL1cyLTgxLVBST1ZJTkctUlVOLTAuMS40LUFOQUxZU0lTLm1kIiwyNDQsMjUxLCIzOTllNmMyOThlMDFlZjEyN2U4ZDdiZjgiXSxbImRvY3MvZW1lcmdlbmN5LTIvYXVkaXRzLzA0LWNsYXNzaWZpY2F0aW9uLmNzdiIsMTQxMCwxNDEzLCIxNjRiZDEzZTg1YzE3YmEwMjkwY2M4N2IiXSxbImRvY3MvZW1lcmdlbmN5LTIvYXVkaXRzLzA4LXJlZ2lzdGVyLmNzdiIsMTgxLDE4NSwiMmRlYzZhMmQ0MmFjZTRkNWE0NzFhZmViIl0sWyJkb2NzL3BsYW4vd2F2ZS0xLWV4aXQvZXZpZGVuY2UvZ292LWNoZWNrLmpzb24iLDEsMSwiZDc2MDJjOTUzNzY4MGQxZGFhOGY1ZTVkIl0sWyJkb2NzL3BsYW4vd2F2ZS0xLWV4aXQvZXZpZGVuY2UvZ292LWNvbW1hbmRzLmpzb24iLDcxLDExMCwiMzBkYTU1OWNkOTJhMDFhZWM0ZTJkYWVhIl0sWyJkb2NzL3BsYW4vd2F2ZS0xLWV4aXQvZXZpZGVuY2UvZ292LWNvbW1hbmRzLmpzb24iLDEwNSwxNTEsIjBkNThiNjJkN2MzODY5ZDMyMjQ1MjljMCJdLFsiZG9jcy9wbGFuL3dhdmUtMS1leGl0L2V2aWRlbmNlL2dvdi1jb21tYW5kcy5qc29uIiwzNzgsNDIxLCJlNzllNGY5OGIxZjBjYjExNzI2MmU3M2YiXSxbImRvY3MvcGxhbi93YXZlLTEtZXhpdC9ldmlkZW5jZS9nb3YtY29tbWFuZHMuanNvbiIsNTc4LDYzMCwiMzQ0M2EwYjQ2ZDAwMDJhZjk0ZWFlZTJkIl0sWyJkb2NzL3BsYW4vd2F2ZS0xLWV4aXQvZXZpZGVuY2UvZ292LWNvbW1hbmRzLmpzb24iLDkwMSw5NjMsIjlkNDdhYWI4NDE4OGJmNTIwMTk2NzU1YyJdLFsiZG9jcy9wbGFuL3dhdmUtMS1leGl0L2V2aWRlbmNlL2dvdi1jb21tYW5kcy5qc29uIiwxNDQ3LDE0OTEsImIyYzQ4YmNlYWYzM2QzMzRmOTdkYTY4OSJdLFsiZ292ZXJuYW5jZS9hZG9wdGlvbi9BMS1pbnZlbnRvcnkubWQiLDI3ODgsMjgxMCwiNWUwNWI3Yjk4YjZiMTE2MjM0YmIzY2M0Il0sWyJnb3Zlcm5hbmNlL2Fkb3B0aW9uL0EyLWNsYXNzaWZpY2F0aW9uLm1kIiwyNzg0LDI4MTMsIjlmZjI4ODdkNGI0YTc4YzI1MThmYzFjZSJdLFsiZ292ZXJuYW5jZS9hZG9wdGlvbi9BMy10YXJnZXQtcGF0aC1tYXAubWQiLDMxMzQsMzE2NywiYWVhM2E3YTJiN2M0NWY4NTVmZGMxOTJhIl0sWyJnb3Zlcm5hbmNlL3Byb2plY3QvYm9vdHN0cmFwLm1kIiwyMDcyLDIwODYsImIwZmJlMDFmMGRiMjQyODEyZTIwMmFhMCJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vcGFja2FnZXMvQVVESVQtTklHSFQtMS9kLXRvb2xzLm1kIiwxNTEsMTUzLCJmYTY4ZjJmZjkwNTk0NTFkMmU0YWU3NzQiXV0sImYiOiIvaG9tZS91c2Fpbi9nb3Ytb3Mtd29ya3RyZWVzL1cyLTAwLXN0b3JlLWIiLCJpIjpbXSwibyI6MjAsInAiOnsiYiI6InNlcnZpY2UiLCJkIjoiY3VkYTowIiwiaCI6IjdmNmViZmRhZDkxMDA3ZTAiLCJvIjpbMzgsMTIsMjEsMTQsMCw0LDM1LDMyLDIyLDMxLDI5LDI1LDE3LDEwLDI0LDEsMjgsOCwxOSwyLDExLDYsMjcsMzcsMzksMzQsMyw3LDE1LDI2LDE2LDIwLDM2LDMwLDE4LDksNSwxMywyMywzM119LCJxIjoiYSBuZXcgZ292IGNvbW1hbmQgcmVhZGluZyBhIEpTT04gTGluZXMgcGxhbiBmaWxlIGFuZCBwcmludGluZyBmaW5kaW5ncyB3aXRoIGxpbmUgbnVtYmVyczsga2VybmVsIGZpbGVzIGNhcnJpZWQgYnkgZ292IHVwZGF0ZSB3aXRoIGRyaWZ0IGRldGVjdGlvbjsgcGF0aCBtYXAgY29tcGlsZSBjaGVjazsgY29tbWFuZHMucHkgYW5kIFcxLTMyIHBpbm5lZCBjb21tYW5kIHNldDsgZXZhbHVhdGlvbi1zZXQgYW5kIHNlY3JldCBwYXRoIHJlZnVzYWxzIiwiciI6MCwicyI6ImVhNjgyOTczN2YxMzg5MjlkMWZjMDFhZGI2YTFjMjc1NzI5ZGJmZmQiLCJ0IjpudWxsLCJ4IjpbXX0=",
  "routing": {
    "code": [],
    "named": [
      "013aea19af229d7674a7dd90"
    ],
    "phrasings": [
      "a new gov command reading a JSON Lines plan file and printing findings with line numbers; kernel files carried by gov update with drift detection; path map compile check; commands.py and W1-32 pinned command set; evaluation-set and secret path refusals",
      "new gov command reading JSON Lines plan file printing findings line numbers kernel files carried gov update drift detection path map compile check commands.py W1-32 pinned command set evaluation-set secret path refusals",
      "a new gov command reading a JSON Lines plan file and printing findings with line numbers; kernel files carried by gov update with drift detection; path map compile check; commands.py and W1-32 pinned command set; evaluation-set and secret path refusals DAEO-sdhj"
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
    "nested": []
  }
}
