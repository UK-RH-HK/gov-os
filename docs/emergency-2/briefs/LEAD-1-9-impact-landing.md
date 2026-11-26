# Lead brief: integration plan item 1-9, the impact trace at the landing and a close record that holds what happened (T-11 (a); fixes under W2-206 DAEO-l2b2 and W2-115b DAEO-j9z6)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-26. **Read `docs/emergency-2/briefs/LEAD-COMMON.md`
first: every rule there applies.** Decide, never ask (I-10). Use `systematic-debugging`. Every `gov retrieve` you or a helper runs
takes `--root /home/usain/gov-os-worktrees/W2-00-store` (the main tree's own store is stale).

## Why
X-1 (DEC-1244): the selection's inputs are made trustworthy first, in the order 1-0, 1-11, 1-8, 1-9; 1-0, 1-11 (c) and 1-8 landed
tonight (`fbcf2c9c8`, `29b964b58`, `7cf01be4d`). T-11 (a), the owner (DEC-1242): "the impact trace runs at the landing (`gov impact
--changed` in the after-step, into the close record)". Read row 1-9 of `docs/emergency-2/integration/INTEGRATION-PLAN.md`, the 1-8
landing record `.gov-runtime/scratch/orchestrator/log/landings/1-8-impact-20261126.md` (a record-only id is bounded at 0.15 s and says
`complete: false`), FINDINGS I-42 (a code question still reads the whole graph: do not trigger it from the landing) and TOOL-MAP §4 fix 2
(`docs/emergency-2/integration/TOOL-MAP.md`).

## What (K-lines as `## Fix:` sections in `.tickets/DAEO-l2b2.md` and, for the close record's `evidence`, `.tickets/DAEO-j9z6.md`; the CTO approves them by this brief)
- **IT-1** The landing's after-step runs `gov impact --changed <range>` for each **record** file the landed range changes (decisions,
  specs, tickets, the register: the record kinds `gov impact` resolves without the code graph) and writes into the close record the
  affected tickets and tests each names, with `complete` as the trace says. Source files are not traced here (I-42). Verify: land a
  planted change to a decision and to a spec: the close record names the tickets and tests each affects, within the landing's time.
- **IT-2** `--select`'s answer carries the same trace for the candidate range (Gov OS lands by the plain path: the CTO reads it there).
- **IT-3** The close record requires `evidence` when the landing writes it, and the landing's notices (path, ticket, impact, path map)
  are copied into it instead of living only in `queue.json`. Verify: a close record with no `evidence` fails its schema; a planted
  landing's notices appear in its close record. Keep a fix landing's close record in the form W2-201 X6 pins (one fix entry and line).
- A trace that fails or times out never refuses the landing: it is written as `impact: unavailable (<reason>)`.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-1-9-impact-landing`, branch `e2/1-9-impact-landing` from `w2/integrate`. Code area:
`src/gov/queue/` (the after-step, the answer), `src/gov/close/` only where the close record and its schema live, the close record's
schema file, `tests/unit/queue/`, `tests/acceptance/W2-206/` and `tests/acceptance/W2-115b/` (the independent test designer only),
the two ticket files. Do not edit `src/gov/impact/` or `src/gov/codeintel/` (I-42 is a later fix); `e2/bundle-a` and `e2/bundle-b` are
held: do not edit their files.

## Green
IT-1 to IT-3 red on the base, green after; `gov accept W2-206` and `gov accept W2-115b` green; then exactly the impact-selected suites
(`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-l2b2=e2/1-9-impact-landing --onto w2/integrate --select`) through the
heavy slot. Check the trailers (LEAD-COMMON).

## Return
Branch and head; where the trace runs (file:line) and what it costs on this repository's last landing range; IT-1 to IT-3 with tests
and result; the selected run's summary; your retrieves (count, queries, records used).

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
store: 29b964b58caf (/home/usain/gov-os-worktrees/W2-00-store-b)
{
  "store": {
    "commit": "29b964b58caf19bf415eb5ca1eb4c5039439e28e",
    "head": "29b964b58caf19bf415eb5ca1eb4c5039439e28e",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-b"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "DAEO-k1us",
      "sha256": "15c52c45f898730e72fc820753e2902e2cee61d07dd4f3a9c85902e5c7adfd43",
      "path": ".tickets/DAEO-k1us.md",
      "start_line": 177,
      "end_line": 239,
      "text": "## Fix, part 2: a fix under a closed ticket lands, relaunches and has a run folder (DEC-1219 (5)), lines X6 to X8\n\nThe first part (X1 to X5) lets a fix start under a closed ticket, but the owner's model says a fix is recorded in its owning\nticket, open or closed (EMERGENCY-2 4.2), and three places still treat a closed ticket as the end: `gov queue` refuses it\n(`TICKET_CLOSED`), the relaunch of a dead session restarts it as a plain launch (which a closed ticket refuses), and a worker\non a closed ticket gets no run folder. The test designer and the engineer run Opus (`src/gov/queue/**` and\n`src/gov/launch/**` are C3; the prompts carry `Task: DAEO-k1us`). The README maps X6 to X8 as `S15` to `S17`, as it maps X1 to\nX5 as `S10` to `S14`. \"The relaunch\" is `gov.dispatch.relaunch` (the watch pass's relaunch of a dead registry entry); there is\nno `gov relaunch` command.\n\n**X6 A fix branch under a closed ticket lands through `gov queue`; a plain branch on a closed ticket is still refused.** The\nsignal is a commit trailer, because the launch record's `kind` is machine-local (`.gov-runtime/launches`) and a branch carries\nnothing of it. A branch is a **fix landing** when the ticket at the integration head is `closed` and at least one commit of\n`<since>..<tip>` has both a `Task: <the ticket>` trailer and a `Fix: <one line>` trailer (the line is the first such\ncommit's `Fix:` value, non-blank). Any other branch for a closed ticket is refused `TICKET_CLOSED` as today (a branch whose\ncommits carry `Task:` of the closed ticket and no `Fix:` is a plain branch; so is a `Fix:` trailer on commits of another\nticket's `Task:`). A fix landing runs as any candidate does (G-1, the path and ticket notices, the impact-selected tests, and\nthe ticket's acceptance folder through the runner of `gov accept`: the folder named by the ticket file at the integration\nhead or the tip), and a red it causes keeps it out of the batch as for any candidate. It lands with **no second close**:\n`tk close` and `CLOSE_RECORD_FAILED` on a closed ticket are not reached, the ticket file stays `closed`, and the landing's\nclose commit (subject `fix: <ticket> (gov queue landed at <tested12>)`, `Task: <ticket>`) appends to the ticket's close\nrecord `docs/close/<ticket>/CL-<ticket>.md` one entry of its front-matter key `fixes` (a list, created when the record has\nnone; each entry `{line, branch, tip, tested, landed}`: the `Fix:` line, the branch name, its tip, the tested commit, the\nUTC time) and one body line `- fix landed: <line> (<branch> @ <tip12>)`, keeping everything else of the record as it was;\nwhere the ticket has no close record, one is written with `fixes` only the way the landing writes a record, and nothing\nelse of a first close. The answer's `closes` entry for it adds `fix: true` and `fix_line`; `queue.json` says the same. The\ndry run's `closes` stays empty for an ordinary ticket (W2-206) and holds only the entry each fix would get, with `commit`\nand `close_record` null, `fix: true` and `fix_line` (a dry run changes nothing and appends nothing); a landed feature's\nentry is as today. A second fix on\nthe same ticket lands the same way and appends a second entry. A fix `Fix:` trailer on an `open` or `in_progress` ticket's\nbranch is an ordinary landing (the ticket closes as today; no `fixes` entry). Verify: planted branches through `gov queue`\nand its `--dry-run` on W2-115b's planted project with a closed ticket that has an acceptance folder: (a) a fix branch\n(`Task:` + `Fix:`) lands, the ticket stays closed, the close record gains `fixes` with the line and the body line, the\nexit code is 0, a second fix branch appends a second entry; (b) a branch whose commits carry the closed ticket's `Task:` and\nno `Fix:`, and a branch with `Fix:` under another ticket's `Task:`, are each refused `TICKET_CLOSED`, exit 1, nothing moved;\n(c) a fix branch whose change breaks the ticket's acceptance folder or a selected test is not landed; (d) the dry run of\n(a) answers the same, changes no ref or file and appends nothing; (e) a `Fix:` branch on an `in_progress` ticket closes it\nas today.\n\n**X7 The relaunch keeps the kind.** The launch's `kind` and `kind_line` are carried in the registry entry (`kind`,\n`kind_line`: for a worker from the plan, for a lead from `build_lead_settings`'s env values; a feature's entry holds\n`feature` and null, or neither key), and `relaunch.spawn` starts the same kind: a `fix` entry is\n`gov launch <role> <ticket> --fix \"<line>\" --root <repository> -- --resume <session id> \"<text>\"` and a `chore` entry is\n`gov launch <role> --chore \"<line>\" --root <repository> -- --resume ...` with no ticket (the chore's `ticket` in the entry is\nits `chore-<8 hex>` label, which is not a ticket and is not passed), for a worker and for a lead; a feature entry, or an\nentry from before this change with neither key, spawns exactly as today (no flag). The claim, the idempotence, `twice` and\n`unresumable` rules, the notify address and the checkpoint text are unchanged (a chore has no checkpoint: the\n`FALLBACK_STEP` text, which names no ticket file for it). Verify: planted dead registry entries (the form W2-205's\nrelaunch tests plant) of a worker fix, a worker chore, a lead fix, a lead chore and a feature: the command the pass spawns\n(the stand-in `gov` that records its argv) holds `--fix <line>` with the owning ticket, `--chore <line>` with no ticket id,\nthe same for the leads, and neither flag for the feature and the old-form entry; a relaunched fix launch (run on the stub\nCLI through `gov launch`) is not refused and its record holds `kind` `fix` and the same `kind_line`.\n\n**X8 A worker fix gets a run folder.** A worker launched with `--fix` on a closed (or open) ticket gets the run folder an\n`in_progress` ticket's worker gets: `runs.folder` takes the launch's kind and, for `fix`, does not judge the ticket's\nstatus (every other rule of it stays: the plain name, the root, the project not inside it, the name given once; a feature\nlaunch on a ticket that is not `in_progress` still gets none, and a chore none, X2); the launcher makes it with its marker\nwhen it is not there (reusing the ticket's earlier folder where one is marked as this repository's, never removing or\nrewriting what it holds) and hands it to the session as an `in_progress` worker's. Verify: a planted `--fix` launch of an\nengineer on a closed ticket (the stub CLI, a planted runs root): the folder exists under the root with its marker naming the\nrepository, the same launch repeated reuses it, and the session's env/settings carry it as an `in_progress` ticket's launch\ndoes; the same launch without `--fix` on the closed ticket is refused as today; `--chore` makes none.\n\n",
      "chunk_id": "fe27d1ee94717aa06609d84a",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-k1us",
      "sha256": "bf522d9577d002361a1cd9b24259e714689c7fbe5362699707a929e00c2e57ad",
      "path": ".tickets/DAEO-k1us.md",
      "start_line": 172,
      "end_line": 176,
      "text": "new feature`, `--fix` and `--chore` in the line that names `gov launch`, or in the skill's line); a copy equals what its\nkernel file generates; `gov accept W2-201` and the copy checks (W1-28, W1-33, W2-153 S3) stay green.\n\n**Landed:** merged into `w2/integrate` at `2031f758d` on 2026-11-19 (the CTO); on the merged tree W2-201, `tests/unit/launch`, `tests/unit/queue`, W2-202, W2-206, W2-195 and `tests/unit/optin`: 1,576 passed. Follow-up X6 to X8 (a fix under a closed ticket lands and relaunches): lead `rubric-tickets-2`.\n\n",
      "chunk_id": "f4223c1e31637caa8cfe33bc",
      "routes": [
        "lexical",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "dc88f72e52c20eec5862793c",
      "sha256": "4b70cf1dca000db0296ac0b29c73e8b43c2dba928f9d9fc2b1bfbb652ebd35f2",
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "start_line": 71,
      "end_line": 71,
      "text": "| 1-9 | **The impact trace at the landing, and a close record that holds what happened.** The after-step runs `gov impact --changed <range>` for each record file in the range and writes the affected tickets and tests into the close record. The close record requires `evidence` when the landing writes it. The landing's notices (path, ticket, impact) are copied into it instead of dying in `queue.json`. [T-11 (a); X-1; TOOL-MAP \u00a74 fix 2; records fix 16, hand-off 21] | W2-206 (DAEO-l2b2); W2-115b | fix M | 1-8 | W6, W11 | Land a planted change to a decision and to a spec: the close record names the tickets and tests each affects, holds the run's notices and `evidence`. A close record with no `evidence` fails its schema. |\n",
      "chunk_id": "dc88f72e52c20eec5862793c",
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
      "id": "e873da7ba988161c516a23b5",
      "sha256": "3656226d826dbcb793865a009aed4d8971b5bdb799a894747adbe60df52f24a9",
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "start_line": 151,
      "end_line": 151,
      "text": "      \"text\": \"| 1-8 | **`gov impact` bounded.** `_Code` is built lazily, so a record-only id never touches the code index. [I-5; T-11; X-1; TOOL-MAP \\u00a74 fix 1; map row 22] | W2-37 (DAEO-6n5k; closed, a fix under it) | fix S | 1-0 | W6 | `gov impact DEC-1204` finishes in under 30 s with the code index stopped and prints the five groups (specifications, decisions, tickets, tests, code), the code graph reported as not loaded and the report `complete: false`. |\\n| 1-9 | **The impact trace at the landing, and a close record that holds what happened.** The after-step runs `gov impact --changed <range>` for each record file in the range and writes the affected tickets and tests into the close record. The close record requires `evidence` when the landing writes it. The landing's notices (path, ticket, impact) are copied into it instead of dying in `queue.json`. [T-11 (a); X-1; TOOL-MAP \\u00a74 fix 2; records fix 16, hand-off 21] | W2-206 (DAEO-l2b2); W2-115b | fix M | 1-8 | W6, W11 | Land a planted change to a decision and to a spec: the close record names the tickets and tests each affects, holds the run's notices and `evidence`. A close record with no `evidence` fails its schema. |\\n\",\n",
      "chunk_id": "e873da7ba988161c516a23b5",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "3af9e4511d4fb18a0371d238",
      "sha256": "6c8f0bd24baa96d00e4f532cb7952371dbd89bb70156e04749cbe54196cff54f",
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "start_line": 119,
      "end_line": 120,
      "text": "| **The landing's own records** | code only: `queue.json` (`.gov-runtime/queue/<stamp>/`, `queue/command.py:76,474`); `select.json`, JUnit, `summary.txt`, `verify.exit` (`.gov-runtime/close/verify/<t>/`, `close/command.py:1724-1746`); nightly `docs/close/nightly/NR-*.json` (`close/nightly.py:483-485`) | `gov queue`, `gov close`, the nightly | never | the CTO; the next landing reads only the committed close record | W11 | `queue.json` is ignored runtime: a landing's notices (path, ticket, impact) are lost after the run \u2192 copy the notices into the close record (fix, W2-206, ~10 lines) |\n| **Fix section** | none (prose, `.tickets/DAEO-xm6l.md:84-96`; `ticket.md:65` says the opposite) | an agent, by hand (14 of 271 tickets) | `queue/checks.py:14-16` needs `Task:` + `Fix:` trailers (H\\*); `release/patch.py:150-173` reads `Fix:` | release notes, via the trailer only | W12 | the queue writes `fixes:` into the **close record** (`queue/fix.py:40-66`), not the ticket; its own commit has no `Fix:` trailer (`queue/command.py:412-413`) \u2192 A-15: the queue writes `## Fix:` from the trailer (fix, W2-115b, ~30 lines); `ticket.md:65` brought in line (chore) |\n",
      "chunk_id": "3af9e4511d4fb18a0371d238",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "e7b3f173236fcf0ccaf1cdfb",
      "sha256": "324632522451d3b539acf2e2f5cf44e18db1e73508cf1620248465d53516dab0",
      "path": "src/gov/queue/fix.py",
      "start_line": 1,
      "end_line": 19,
      "text": "\"\"\"A fix landed under a closed ticket, in the ticket's close record (W2-201 fix X6, DEC-1219 (5)).\n\nA fix is recorded in its owning ticket, open or closed (EMERGENCY-2 4.2): ``gov queue`` lands a closed ticket's fix\nwith no second close, and appends to ``docs/close/<ticket>/CL-<ticket>.md`` one entry of its front-matter list\n``fixes`` (``{line, branch, tip, tested, landed}``) and one body line ``- fix landed: <line> (<branch> @ <tip12>)``;\neverything else of the record stays as it was. A ticket with no close record gets one in the close record's form\nwith its identity and ``fixes`` only, nothing else of a first close.\n\"\"\"\n\nfrom __future__ import annotations\n\nfrom datetime import datetime, timezone\nfrom pathlib import Path\n\nfrom gov.cli.errors import GovError\n\nFIX_RECORD_FAILED = \"FIX_RECORD_FAILED\"\n\n\n",
      "chunk_id": "e7b3f173236fcf0ccaf1cdfb",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "244881e09b905dcd5661dd36",
      "sha256": "1421b760377add27b8ed3ca68f6d852a2573c577dae42eda168bab1d86a28ce6",
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "start_line": 118,
      "end_line": 118,
      "text": "| **Close record** | `schemas/close.schema.json` (requires only `task`); no template | `close/command.py:1441-1470`; the queue through `close._record_and_close` (`queue/command.py:422`), commit `--no-verify`, trailers `Task`, `Role` only (`:426-427`) | **after**: schema family | `close/select.py:136-139` (`evidence.scope == \"full\"`, `evidence.head`: the green record the next selection starts from); `close/nightly.py:150-154`; status and release do **not** read it (release reads trailers, `release/patch.py:236-248`) | W11, W6 | what a close must hold (evidence, selection, impact list of T-11, fixes) is in no schema; 19 records, 6 with no evidence, silently ignored by the selection \u2192 `close.schema.json` requires `evidence` when written by the queue (fix, W2-206, ~15 lines); T-11's impact list into it |\n",
      "chunk_id": "244881e09b905dcd5661dd36",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-l2b2",
      "sha256": "e1401e72bfe295f23a3614bdc7d01f4f8b558de608fee190475411aa790f4220",
      "path": ".tickets/DAEO-l2b2.md",
      "start_line": 1,
      "end_line": 34,
      "text": "---\nid: DAEO-l2b2\nstatus: closed\ndeps: [DAEO-l2bd]\nlinks: [DAEO-l2bd, DAEO-j9z6]\ncreated: 2026-11-19T03:00:00Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-206\ntags: [close, queue, landing, emergency-2]\nwbs_id: W2-206\ntitle: 'gov queue becomes the landing-and-close, part 2: --dry-run, --select, --full, the after-step (L2 \u00a73 A6, A8; DEC-1214 L2) and two fixes of W2-202'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\nprofile: FULL\ndepends_on: [DAEO-l2bd]\nwaits_on: []\nallowed_paths:\n- src/gov/queue/**\n- src/gov/close/batch.py\n- src/gov/close/nightly.py\n- src/gov/accept/runner.py\n- tests/unit/queue/**\n- tests/unit/close/**\n- tests/unit/accept/**\n- tests/acceptance/W2-206/**\n- tests/acceptance/W2-202/**\n- .tickets/DAEO-l2b2.md\n- .tickets/DAEO-l2bd.md\nest_loc: 330\nkpis:\n  success:\n",
      "chunk_id": "f5478013f6647e2a4bf4552b",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "CAP-63.b",
      "sha256": "cefd449f92aa11124121fde2a3828c5277982815ff36ff058bd5790165883654",
      "path": "docs/contract/capabilities/CAP-63.b.md",
      "start_line": 11,
      "end_line": 16,
      "text": "# CAP-63.b: The landing writes the ticket's close record and closes the ticket at the land; no separate close step carries weight of its own (DEC-1214 L2)\n\nA covers item of CAP-63 (The landing). Generated from `docs/contract/contract.yaml` (Contract v5, version 5.1), which is the authority (DEC-614).\n\n- **Item:** The landing writes the ticket's close record and closes the ticket at the land; no separate close step carries weight of its own (DEC-1214 L2)\n- **Wave:** W2\n",
      "chunk_id": "120b6cea3f290594c8d9f67a",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "CAP-63.b",
      "sha256": "aa74b03e8e7327000c3737ac02825a513002bd13fc6aa92c0d3e92c413bd27a5",
      "path": "docs/contract/capabilities/CAP-63.b.md",
      "start_line": 1,
      "end_line": 10,
      "text": "---\nid: CAP-63.b\ntype: capability\nstatus: ACCEPTED\nstate_class: DERIVED\ntitle: The landing writes the ticket's close record and closes the ticket at the land; no separate close step carries weight of its own (DEC-1214 L2)\ndepends_on:\n- CAP-63\n---\n\n",
      "chunk_id": "b6a059e93602b4ae556e14cb",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "4417a14220fd6a34f0d6b355",
      "sha256": "2d1134edc7690f1a0cb4c6237fb093c9c84d1b063d3ffd9af176818e5a9c1600",
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "start_line": 117,
      "end_line": 118,
      "text": "| **Handover** (lead `CHECKPOINT.md`, CTO morning handover) | prose (`role-lead.md:72-75`); none for the CTO | by hand | **never** | the next session, by reading | W15 | DEC-1242 T-13: the handover in the checkpoint form, read by the launcher (fix, W1-25 + W2-207, ~40 lines) |\n| **Close record** | `schemas/close.schema.json` (requires only `task`); no template | `close/command.py:1441-1470`; the queue through `close._record_and_close` (`queue/command.py:422`), commit `--no-verify`, trailers `Task`, `Role` only (`:426-427`) | **after**: schema family | `close/select.py:136-139` (`evidence.scope == \"full\"`, `evidence.head`: the green record the next selection starts from); `close/nightly.py:150-154`; status and release do **not** read it (release reads trailers, `release/patch.py:236-248`) | W11, W6 | what a close must hold (evidence, selection, impact list of T-11, fixes) is in no schema; 19 records, 6 with no evidence, silently ignored by the selection \u2192 `close.schema.json` requires `evidence` when written by the queue (fix, W2-206, ~15 lines); T-11's impact list into it |\n",
      "chunk_id": "4417a14220fd6a34f0d6b355",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "cbcba0cedb99e85575e5b7bf",
      "sha256": "e1a0c993b9878f8614634e0ac4414cc07fa4bfab15ce98b5e6a1784d0b50c129",
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "start_line": 318,
      "end_line": 323,
      "text": "| 16 | Close record requires `evidence` when the queue writes it; landing notices and T-11's impact list copied in | `close.schema.json`, `queue/command.py:422,474` | fix, W2-206 | ~25 |\n| 17 | The queue writes `## Fix:` in the ticket from the trailer; its commit carries `Fix:` | `queue/fix.py:40-66`, `queue/command.py:412-413` | fix, W2-115b (A-15) | ~30 |\n| 18 | `FIGURES.json` stamped from the declaration; a release gate reads the latest verdict | `memaudit/figures.py:118-136`, `release/gates.py` | fix, W2-204 + W2-209 (A-9, A-13) | ~40 |\n| 19 | Standalone scan writes `SCAN.json` | `memaudit/command.py:103-125` | fix, W2-198 | ~15 |\n| 20 | Handover in the checkpoint form, read by the launcher; one checkpoint schema | `checkpoint/record.py`, `launch/`, `schemas/records/checkpoint.schema.json` | fix, W1-25 + W2-207 (T-13); chore | ~40 |\n| 21 | Decision record level fields, `gov decisions answer`, the register entry validated | `decisions/`, `register-entry.schema.json` | **new feature, approved** (DEC-1236, DEC-1242 T-1, R-6) | per its spec |\n",
      "chunk_id": "cbcba0cedb99e85575e5b7bf",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-l2b2",
      "sha256": "f8d34d416a74883d5a13cf96105141587e8bdc9267a500eb39845d71ecea192e",
      "path": ".tickets/DAEO-l2b2.md",
      "start_line": 57,
      "end_line": 75,
      "text": "# W2-206 the landing becomes the close, part 2 (L2 \u00a73 A6, A8; two fixes of W2-202)\n\nA new KPI line on W2-115b/W2-202 (closed) is a new ticket (EMERGENCY-2 4.6). The lines are those of\n`docs/emergency-2/L2-COMMANDS.md` \u00a73 items A6 (`--dry-run`, `--select`, `--full`) and A8 (the after-step), decided by\nthe owner in DEC-1214 L2, with the owner's rule for the full run (DEC-1216 (5): every run inside the gate, fewer\nworkers rather than a peak) and the two fixes W2-202's record named (recorded in `.tickets/DAEO-l2bd.md`, the failing\ntest first). A2 waits for the M1 lead's close record; A7 waits for the owner's answer to L2-6; B waits for the owner's yes.\n\n**The logic of `close._verify_command` and `_select_command` moves** into `gov.queue` (the close's own commands stay\nuntil B1 retires them; `gov close --select`'s output is the reference for A6 S2).\n\n**The lead's rulings on the test designer's four open points (2026-11-19):** (1) a dry run refused as a whole writes\n`verify.exit` (exit 1) so `gov wait` returns; the tests assert only exit 1, `TICKET_UNKNOWN`, nothing moved. (2)\n`--select` equals `gov close --select` (each ticket's own acceptance folder is in the selection). (3) A `--full` run\nleaves the candidates' own acceptance folders out of its run (W2-202 A3 F1: no test runs twice in a landing). (4) A6 S4's\nsecond case plants no number in the path map.\n\n**Closed at the land, 2026-11-19 04:34 (the CTO; EMERGENCY-2 4.3 step 5):** merged as 8e27b6248 (branch `e2/l2-build-2` at 6192547a7). On the merged tree, through the slot with workers: `tests/unit/queue`, `close`, `accept`, `optin` and `tests/acceptance/W2-115`, `W2-115b`, `W2-193`, `W2-194`, `W2-202`, `W2-206`: 724 passed; `gov accept W2-206`: 45 passed, 0 failed. The CTO's rulings on the lead's lines: `--full`'s path-map worker number is also capped by one slot's size (with the A2 ticket); the lead brief's line telling the engineer to read the acceptance folder is corrected (the engineer role's text holds). Not built here: A2 (after W2-200), A7 (the owner's L2-6), the B items (the owner's yes).\n\n",
      "chunk_id": "1b244e67926b6859b278051b",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DEC-1206",
      "sha256": "cdafc5d8152a7ec18d9375db433569d74e39bcc4f15b6f3321908021d15173e6",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 1828,
      "end_line": 1829,
      "text": "- **Governing sources:** DEC-1186 (3) (Q1 (a), Q2 (a), Q3 (a)); DEC-1171 (3); DEC-1203 (3); package P-W2-15A-CLOSE (`drafts/w2-15a-close/PACKAGE.md`); ~/gov-os-operator/queue/jobs/results/JOB-20261116-02.result.md; `docs/research/EXP-003/w2-15a-baseline.md` section 11; `.tickets/DAEO-kq8b.md`.\n\n",
      "chunk_id": "a541af0bf00f9155a9c637fd",
      "routes": [
        "semantic"
      ],
      "batch": 2,
      "entry": "DEC-1206",
      "status": "ACCEPTED",
      "changed_by": [],
      "in_force": true
    },
    {
      "id": "DAEO-l2bd",
      "sha256": "fcd8d4dae7a6d0fbc5713b01226a967ba1293d781a5206135bed57d4f1fcfde5",
      "path": ".tickets/DAEO-l2bd.md",
      "start_line": 72,
      "end_line": 73,
      "text": "**Closed at the land, 2026-11-19 02:10 (the CTO; EMERGENCY-2 4.3 step 5):** merged as 2b54f3d1a (branch `e2/l2-build` at 04802659f). On the merged tree, through the slot with workers: `tests/unit/queue`, `close`, `adopt`, `optin` and `tests/acceptance/W2-115`, `W2-115b`, `W2-193`, `W2-194`, `W2-202`, `W2-174`: 1,099 passed; `gov accept W2-202`: 39 passed, 0 failed (14 of 14 lines). Acceptance commits by the independent test designer (38f3b5c4d, 3e7412ac6). The CTO's rulings on the lead's lines: A5 S2 stays as reworded (a repository with its own facts is left byte-identical); a fast-forwarded hand merge stays refused. Next in this stream: A2 after W2-200 (M1) lands, then A6 to A8.\n\n",
      "chunk_id": "609313ae2ba44a2133407c2b",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-l2bd",
      "sha256": "97935df4e9547ad7f4c25abbbfc11713b4d9c7da3109e35ab5e18a0ffad21051",
      "path": ".tickets/DAEO-l2bd.md",
      "start_line": 60,
      "end_line": 71,
      "text": "# W2-202 the landing becomes the close, part 1 (L2 \u00a73 A1, A3, A4, A5)\n\nA new KPI line on W2-115b (DAEO-j9z6), which is closed, is a new ticket (EMERGENCY-2 4.6). The lines are those of\n`docs/emergency-2/L2-COMMANDS.md` \u00a73 items A1, A3, A4 and A5, decided by the owner in DEC-1214 L2 and Q-CLOSE: the\nlanding and the close are one deterministic action; a red that is red at the base is recorded as a known base red and\ndoes not block. A2 (one close record, one writer) waits for `e2/m1-context`'s change to the close record; A6 to A8 and\nthe retirements (B) wait for the owner's yes.\n\nW2-115b's own cases that assert `BATCH_UNEXPLAINED` for a red that is red at the base (its \"red on the base too\" case)\nassert the behaviour A1 replaces: the independent test designer rewrites them in this ticket with the line naming\nDEC-1214 Q-CLOSE and `Rewrite-Reason:`.\n\n",
      "chunk_id": "993f3bc451d4e37e8a0016b5",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-g23i",
      "sha256": "29d8acfbad57a9064823e2f4d45c381e391b481af552a7ef538ebd4bfccfb6cc",
      "path": ".tickets/DAEO-g23i.md",
      "start_line": 1,
      "end_line": 39,
      "text": "---\nid: DAEO-g23i\nstatus: closed\ndeps: [DAEO-g0ip, DAEO-6n5k, DAEO-s694, DAEO-xxgp]\nlinks: []\ncreated: 2026-10-16T16:35:11Z\ntype: task\npriority: 4\nassignee: engineer\nexternal-ref: W2-38\ntags: [wave-2, implementation, full, wave-3, deferred]\nwbs_id: W2-38\ntitle: Profile from impact; impact-selected tests at close\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-g0ip\n- DAEO-6n5k\n- DAEO-s694\n- DAEO-xxgp\nallowed_paths:\n- src/gov/impact/profile*\n- src/gov/close/select*\n- tests/unit/impact/**\n- tests/unit/close/test_select*\nkpis:\n  success:\n  - An R0 change runs only the LITE checks, and an R3 change raises the FULL gate and readiness rows, with the profile computed by gov impact [CAP-53.b].\n  - A close runs the tests gov impact names, on top of W2-66's path-scoped selection (W2-48's cache was withdrawn, DEC-880). The full suite runs only in the nightly [DEC-968, DEC-983, DEC-982] [W2-H043, W2-M240, W2-M241, W2-M163].\n  failure:\n  - A change whose impact misses a test that would fail is caught by the milestone run and recorded as a learning event.\nprofile: FULL\nsources:\n- CAP-53.b\n- DEC-983\nest_loc: 150\nacceptance_tests:\n  path: tests/acceptance/W2-38/\n",
      "chunk_id": "051285503cdd768c5b1c6af9",
      "routes": [
        "lexical",
        "closure"
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
    "duplicates": 60,
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
      "chunk_id": "fe27d1ee94717aa06609d84a",
      "parent_id": "85d3dc3b82dfdee884963f90",
      "path": ".tickets/DAEO-k1us.md",
      "start_line": 177,
      "end_line": 239
    },
    {
      "chunk_id": "1b244e67926b6859b278051b",
      "parent_id": "8f648343876a800878346bb1",
      "path": ".tickets/DAEO-l2b2.md",
      "start_line": 57,
      "end_line": 75
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "id": "ADR-0001",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "ADR-0002",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-01",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-02",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-03",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-04",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-05",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-06",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-07",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-08",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-09",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-10",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-11",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-12",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-13",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-14",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-15",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-16",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-17",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-18",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-19",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-20",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-21",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-22",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-23",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-24",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-25",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-26",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-27",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-28",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-29",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-30",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-31",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-32",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-33",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-34",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-35",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-36",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-37",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-38",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-39",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-40",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-41",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-42",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-43",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-44",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-45",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-46",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-47",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-48",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-49",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-50",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-51",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-52",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-53",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-54",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-55",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-56",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-57",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-58",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-59",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-60",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-61",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-62",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-64",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-65",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-66",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-67",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-68",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CAP-69",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "CHARTER-v6",
      "reason": "DEPTH_LIMIT_REACHED"
    },
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
      "id": "MR-1",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "MR-2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "MR-3",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "MR-4",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "MR-5",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "MR-6",
      "reason": "DEPTH_LIMIT_REACHED"
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
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "cf32231794dfdce4f89fe622",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-6n5k.md",
      "chunk_id": "3407ab6d1c4f7974ee7c8769",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "cf36fd8a20264065f61cf9f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-6n5k.md",
      "chunk_id": "f8c807c9ab4e4bf4292bb412",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "cb3709e02088d257c3c4b145",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "80ac99264c7bdf78431d747b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "c9277fb22e2db73ee7126f35",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "d7f397ef0126f560c2c8bba6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "6e8a7acf8d7edcf5cc3002a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "4ee5989eb04026fe019a8718",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "99fc3ca4801d5fd9a97d7395",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "fb679667ef03ffe0bd5d1368",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "968f97f5934de02194dc567c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "f9a9d9f2ff8319936c523e26",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "161e6457f1af8dcea089911b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "2e69abb8f8e8a3b0dbde00b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-6n5k.md",
      "chunk_id": "0bcf90c138127aa845f4f7e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "a62953bc903517b189944ac8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "87dc28fc0fc8670c305896d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "676a6f04c3c882eefafb6cb5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "8c4150f5cf2805c8004d367c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "1c5f219c30f0e71cee6d876a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "36eb55155ea3cd0646d10226",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "79cfd96f78060e349a260390",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g0ip.md",
      "chunk_id": "52e6bece0a3935872e5e266f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-w2-56.md",
      "chunk_id": "8f1dce2021b64b8ed870613b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/L2-COMMANDS.md",
      "chunk_id": "a777a5dd65da8c18f29bd35d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g23i.md",
      "chunk_id": "f9842e111eb3cbf629c2484e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "a63a1a7dd79127fcbc302c65",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "044479861d4f27a4a4edf344",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g23i.md",
      "chunk_id": "84c12793a2223e5b1a66b130",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l2bd.md",
      "chunk_id": "2db295c212a84d9ea357b1b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "521dcb0e76b5625bf8a8b8a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "9b361d318c743291d24efe9e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "e437cf6624e13d68b86a4036",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "3cbe2590b5a158a48f5cb3c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "f4a430109051db6b53eb966a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-w2-56.md",
      "chunk_id": "faa5a5e7969bf3f79935914a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "aae03f191f7002b366959a71",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "6d963f380de407cf518b1d6b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-rubric-tickets-2.md",
      "chunk_id": "191ed87d47f567d291b4b0b8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "967e7ca3d1ab09ebb5d2db2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-w2-56.md",
      "chunk_id": "61a55859711f1f6d5209b6b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "a3aebf4ecfff2d243f65af72",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "3baeefa19294f892b84d4cc3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "9a5a8dd15abed08bb1e6edca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "7592a9bfae68a1b3bbc0d0c5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-rubric-tickets-2.md",
      "chunk_id": "8b67ecfc6ce82ffe37c654a3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "28210d02a01628dd67c1a63a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "48717aec810fb6cc6b4db856",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "1781167355421b9e6d8384bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "d5a68da576ce9c6a0e5a7a6c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-rubric-tickets.md",
      "chunk_id": "ae1b0b0ba9aac4d16dece4f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.3/manifest.json",
      "chunk_id": "f716dc0cd82881fedf11d039",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "eed9d83bac5eddccc3169fc8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "49ef56b6735dc84a54bbe770",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "fed0a0ddf24a0b0da77f31c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "b8a9f351f0462263761c9abe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ifgf.md",
      "chunk_id": "0129b090d5f79897b509df60",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "985085bc8baaaed9cd023315",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "1413f8ddadcbcf6293997f25",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "15c4f5f5760a3eda8fbcdb64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "29487dba7c0a1e70a9e83d90",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "df8c8f3cba1fcf2f2ba1d776",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "40ceb9a6cafc47527d25e931",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "b1b494d24b7e2577ec386042",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "2a5e32c2fbeea01dd2dada7a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "b4ed80a0391def49e878110f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-models-rubric.md",
      "chunk_id": "05fd3695cb05082116ffd4a4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "cdf3554f51d77545e6bf4cf4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "67d8a746db5efe954ec36110",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "afa16cae7d094ae1c6430bdb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-models-rubric.md",
      "chunk_id": "20b90ac07cdd6dd0178a0f78",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "f4ac9270b12814a76b5a2ded",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "71bc5df85723e1c43628bf07",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-63.md",
      "chunk_id": "da1a7d2e9829b9baab1e16b8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-63.a.md",
      "chunk_id": "a1775455d03b9554b25892f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-63.d.md",
      "chunk_id": "0ff619f6d6a8b472c525d6e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-rubric-tickets.md",
      "chunk_id": "ee13dcc74d067feeba7242b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "052bcf7656af6892323757e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "c3c7440a4b82b838bb386344",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d4fd33a9e9b468ef2ee82379",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "c4c58728a5fa509b07624479",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-models-rubric.md",
      "chunk_id": "bb84559c54abc23c3d4cb2c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-152-CIT-P.md",
      "chunk_id": "cb360c1f92bfb1d26a540bf7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-63.c.md",
      "chunk_id": "80a1fbd62576eac5a1fd8018",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "ee7fb2526dff2a4fa5f4c00b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "e577983f8a448f63ea83bb6a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-63.a.md",
      "chunk_id": "1a64f628dd956d9f12e7ea0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-63.d.md",
      "chunk_id": "ab81955f5a1f8972d2fa26d6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "f75f917df92290db36eaa213",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-v4is.md",
      "chunk_id": "89d249a57467f5033b065ac3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "7ba4e8f3ff2bc44fddd7ab57",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "3384d861b69cacef122a2793",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "465b5f077fdf9817c1d8a65a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "938488645025455b22b99fa7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-63.c.md",
      "chunk_id": "4240b3e9abe7352db7fe39e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "3c8ad782d1191ff2d9612bc4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "557579098e787ffd1e3b0fe4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "1d06ea0f3ff8e7f42febaf14",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-63.md",
      "chunk_id": "b26600f14bbb8689c40188f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e8950a8c24a066f172087c9f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "88a39c77f74494fd540b8f6f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "2ed0e3be72b0dcd2fcd4a050",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "ac5bb6d7a7d74a0dfd0f9f62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "1af4920a62ee8832ff0fec1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "dc8eb4b92314acd468b50f34",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-PAGE-2026-11-22.html",
      "chunk_id": "b9b5ea877145db216768688b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "799868b3cb7246a8caa7de66",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "c51b60c9db8a008898af42b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "572367370bde705554059e9e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "12826ea2472dd890a5c9c5a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "c7dad3d31491d2fd3f7926df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "00f1d983046608c27e1921c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "cc2ce371990c713fc091be7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "37fbfcfd886e1ec5544447d3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "45db20593f6c4dbe377189fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-7jln.md",
      "chunk_id": "3fc28d3e10e7e8edd889f30f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "8683672a8a91fcb6bd9d7010",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "aafaafcf62d465a98457ec41",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "0c1694b95081dfce7e8cdcf9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "112cee83e0b57b90b6910b56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e84a90604302364382fbeaca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "a37ba41791ec5f0cfc473c54",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "ef2e0404951b73fd2a51c303",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "cff8ace31ee7f2fb6f535abc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d8d5ffedbd8b1374012e28ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e465c3733b00bd9bcb27fbb0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/L2-COMMANDS.md",
      "chunk_id": "f7bcd5be3ed2f209d2ada073",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "c4ef622a07a4bde9ba7c3f9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "fc868cc581e21c25f063b5ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "292a2b4b0a09f2c4169d27d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "704a6255174946d81f4f713b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "a464d3463fc0a9e68f96225d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "30e43439d04f37e8a346cd6e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "48c294b1025b3a21b0070bdc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "62b21c46352c57d840bd3d1e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "00333f344f5b0626635aae04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-k1-usage.md",
      "chunk_id": "f6d3ff79e3e624a44dde0ed3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "244e0458684d53e83e24f8ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "05282765a9b193094606a827",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "95a4a0d46dab19bb25c81b7b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "ac63f1f2e4710a133eaa6c6f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-w2-56.md",
      "chunk_id": "98cf12c5353785a33c16a14f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "68653b12a98a1aedfd8402e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d50af533a7972b4a52032237",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "75fccf287b98364673a6a5ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "5c7ecebb4eaa755305efd0f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "b323d55bbdb8266776c540e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "1a7625c2bd3b95d798270288",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d6dc2d7e7c683f546651481e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "567283513d661a86474c4eab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "2d5625f554c70fecaf94fb61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "63b2634029fcd77a7d49099e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "9496ca58565b55cb3ecd40c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "aeb8b1da6b882f8650ed8631",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "cc2c3b433b257cdf642c9141",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "a8f6056984189b1783176382",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "06feffa7d351cc570ad5181d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "5ac2864a00b4d4b7d90bd60c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-k1-usage.md",
      "chunk_id": "ce41298a8c4f12aee4c5c835",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "ef33a78c043059570f7bb076",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "5999785546283b379b524e0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d7edb1d99f6a1db1e3cd1fca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "79be47e476f5439efd9a3d2a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-k1-usage.md",
      "chunk_id": "ef50cf77fb2c8561a8890af6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.2/manifest.json",
      "chunk_id": "32094476ea05903ba846b99d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "f3819855d03e830796078743",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "6264bbd3683d33384c9cbd12",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e8c9cbaa0b3adda63285750f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d404afff796890b4c7d3a902",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-l2-build.md",
      "chunk_id": "1f856f773eaf6c995feaf310",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "7e89d62af5aa45446cf548cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "7ba70758f3aeb51d8613ce61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "abc522db18f194c70d9580f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-close-e2.md",
      "chunk_id": "80fbe5e5c24e016cc7094a3e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "38947694e687ce4112e14411",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "89a85be4b1913d73816510fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "24988366b3dbe291e5f34567",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l2bd.md",
      "chunk_id": "cc7fbdfc98ab7d754c677a0f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "f2c1ff8c20b4b7783c2e1d8f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "cbaedf1d27319dd6d45fbf92",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e08978255fd372e98aaf2947",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.2/manifest.json",
      "chunk_id": "2b42e77433285521548f95b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "a3a41ea519fed7dfe74b0d3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-40/test_w1_40_templates.py",
      "chunk_id": "5ad230074c617ce6410248da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e3fb6de18670c9b05326e39c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "00f9324f833ed4efb89f0252",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "de4bc0b09a661b2f906dee1d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d886cdb7e7ff21531796cb7a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "2844fd711cced06235cc40b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "07ab7803ce8030b21cac145a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "2ac620d074aca7cca44b9c1a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "chunk_id": "51a7f3e64592c4484c0276d3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "17283cfd4aece642ca3a3636",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "189b0199f5250bf4eb886b8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "2ddf1149560c2c6e5f17516e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "7eaaa5e27988881aefb5bcf9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "4c7cc75476ed8d58f43e46df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-emq1.md",
      "chunk_id": "a4e1b211baabcb3822321e8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "144d062fa81a196e2fa656be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "f0207a25091522202b5dde66",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "33cafa168e646bbdcf575ae0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "280e3154834e763c2e6970c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "1b072994bacafd85d25ed39a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "80357a2b33baa49ccb15625a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "3b0c3fa1590547cd98a7552d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "1a18b1b2b52722d6aa52910e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "82b3846482465a650c71a3a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "925ad47c2b83055b4c27c3cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "bab98fb2c2a4dda7f3e6df6f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e9b77166731cecbfbab912d6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "02f38b7bb0a1220f26795588",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "6cadb25de1b6ccb4235e0028",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "fe23ca03dd166bb225c17c8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "782088b03f8e74e7bad85c3d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "ac46c2d64f37d54c2bda2873",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "5fe260bf6f8aa9bb6d6eb95b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "chunk_id": "3c9cdfee45d5c6e1d2a1a77c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "7b579ca089b6e88f27bd9afa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "1138223d03a41be5799db9a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "85858898e1a946c70c0582cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "2d61d91e80f3b1498d8687ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "6725bde267cc764c4a18ce2c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "8b4e70d33257f116e822a226",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "b68a45d04e8560a267dcd5cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "966a4844829247ab9ec22ed7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "477407060917e6877ad12c56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "530882ae4786686db887320d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "8a49b75c51db1e62693986e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "c25633899411dc7669a3a420",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "a8daa3a29edd146fe5a7bf28",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e565b65659ce0c453d2fcce1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d83cf4b9f9273a49c50d6e97",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d56d9ca4f3ad867f4a97dd69",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "edbf01106e20fbd27a106ed7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "9004873b51ef6e5ed892e67e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "30149e3aba7c9d7153f72086",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "1500d2f059fbd6152f219a4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "000f405c39e555c29469d9eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "8e3ea894c2f8f0cbafc5ce26",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d93ae005d79620ec8c7418aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "aaf2f0aa98f2a0a7759f012b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/wave-1/W1-43-wave-1-exit-audit.md",
      "chunk_id": "2f55d591881d217506bbd0f2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "9f1a0102828b04fb8f046a81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "aa2bae76945fe4dde186c666",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "cdf82f0bdc04dee85a2655f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "2eeeb2ab8ef79a684f3a39cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "9bdfa8f2fb2598724342b007",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "f4055011b096f38dec9984ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "ee0bac91f9c9b24e09bc68bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d922fb7824eb5e5166663467",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "0ff23b735a76cd2c165d7ae9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "bb6faefaeb2787304bd69672",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "756dac68dc16d694b64302e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P2-lifecycle.md",
      "chunk_id": "a402e2db1e6d6d3c09ce0041",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "da3295ab179ee59823a7d435",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "5975eb404c84e6a69a53f536",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-CLOSES-1.md",
      "chunk_id": "4e173d718b05c9c382a2662d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "1dc24e103d61a640020019b8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "2ff891398a24d9a50434d0b1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d9e5e5b5593e13bb5f9f7894",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "1e429d80eedad8cfb277de35",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "29e5ccc543414c7b47e22aa1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "aa9b5ad5ed882ef8c4940714",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/L2-COMMANDS.md",
      "chunk_id": "5b57c5d0d683eec9c2b60bc3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "942c1681cbe534aade130d29",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "08bd3a9e807219b021a37af6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "4b074bb6abf0b811d62a2b3b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/w2_201_support.py",
      "chunk_id": "3a22c07a5ebc44d8f3e4955f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "e36c7c00f708780c34b007cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "c242c40e6fe4d1774bba6603",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "2ba24528da4b2f9d4dd537f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "4a1220a390820a126fe56d51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "1690ac041c483a4234b44b5d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "399fbd5297f35babf523cb0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "4915d8c18ba141aa0a10cb1b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-58-C1.md",
      "chunk_id": "598b13948f482a8917c59b4c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "25d914640061a44c1e244984",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "defd21c545be9b6f4a1ff4f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "a48eba3be5f64a3e268961d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "7207c4115e67f9ca050fe2b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "8518ab4a97f720df5e9a8a40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "57da6482320850a3daa88ecd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "0ea1528fd43dad4904f7a676",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "ae67a907ee29c838b5dff0dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "fdac3bf6e15168eb34aba111",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "83cda8144f2db1f273396208",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-rd0g.md",
      "chunk_id": "5a55561ef9ade75019f51afe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "db31479fe2c4ca9441a5cb99",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "2edfe4b1c19242230de52a9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "289c7df017cbc1890183976b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "91351a3d91d35cb73cb651c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "ed8d028c992bfdf7d3abc4e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/w2_201_support.py",
      "chunk_id": "bceb6e4fa89db7f9ec6dd882",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "01bb18efb2054fd57f582599",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "86649a38f306566f0f5af185",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "355e28e6ed634e49b6a316a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "4bf9df88911094209aaf5aa1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "846a14a91854793c2dcf6e60",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "f561dad9222054f51cbaa770",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "8253b2771ed41a8b8fbdd5b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "8e4116d0aec0b4625a48e829",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "5a1aef6797cdf23ea0350eb8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "90c37c856daaf97e7ffa18fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "500e37c2df79780c085bf3f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "64736d65f8a266cda5466db1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "39de402f9125d9b9bc714885",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "581d6e7f2d45804ddadf1199",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/launch/test_w2_184_criticality.py",
      "chunk_id": "9ccdd405151443d3bd295dcc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "67eecf849b4d631beab86f2e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "4f0c20719fc0220d5d89c382",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "e82d4b99d368459d14127132",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "eeb667c5b61b8ccc685a694a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "435652af3c3c207a73b6e00d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d234cf0e099ecaa12e93d277",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "3c67d2c1e4c91124a4ec8a51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "d5d250c4f9d581bbf20c0df4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "9d05e716e979b2afe8368cb7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "7caadcf6ecf3fb3625afe61b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "3a38041f429aff9b858da3fc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "773d63e36354f6c8b7316c3b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "4d68bef02018f1e19c45e54e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "dc70d069f76f85a133aae886",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "18b671e35e95a2fed735e29f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-nn1s.md",
      "chunk_id": "228fef247583a516d63c64d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-33.b.md",
      "chunk_id": "e5f5a29f8c708d662e1beb29",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-33.b.md",
      "chunk_id": "6c5407a67d4a198311517485",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-33.g.md",
      "chunk_id": "69d1c2ff2116e7d81202cbb5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-33.g.md",
      "chunk_id": "6a52f1a963a0e59215f45514",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "ca5ba0459b460bfd3da8b828",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ym8a.md",
      "chunk_id": "a7f78f1e75e8a1244ff09cf0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "eb280331e342c54ea69fce4b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-35.a.md",
      "chunk_id": "4d67b14c8fe25331ea5455e1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-35.a.md",
      "chunk_id": "a16a2e96bfd227e59f4dcd91",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-35.b.md",
      "chunk_id": "740aeb2d2d7fb13dfc5b7409",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-35.b.md",
      "chunk_id": "7376b9621a486550e34dbeba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "9f782709afa5e4ec6c375522",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ym8a.md",
      "chunk_id": "99ebea01c7a7a7f75a58e853",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-35.c.md",
      "chunk_id": "7463e89e3b0e8c28407209a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-35.c.md",
      "chunk_id": "e5117b047d26aba7a1d88c3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "7b7102f6a1dfa315cbebb351",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ym8a.md",
      "chunk_id": "36ebaa4ff84945453a078e26",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "3b51f68c51bd761d3f1fd068",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "e8733ea5a63e52fcc0809dc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "140da85c6374fa7d7349cbe1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ym8a.md",
      "chunk_id": "5ff96c84ce208743a864e487",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "e808421b42f5514c2bed4ca7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "ce507b52a8298cc80acb73eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "5b8ca648163cd3622fb604be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "06ddc3d95952b1e74ed3e70c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-15A-CLOSE.md",
      "chunk_id": "e15cb376511884a82363eebc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_TRIAGE.md",
      "chunk_id": "e8d7e95c193ce9b453f1fedd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/L2-COMMANDS.md",
      "chunk_id": "57eee81fbab95fc71ec224c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/conftest.py",
      "chunk_id": "1372169b3b625d1eb2c33b1c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-CLOSES-1.md",
      "chunk_id": "0e08d53d9a5ebc9f9b7924ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "6ff141923bb27113a6402095",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-l2-build.md",
      "chunk_id": "716c0847d1f067de7c623316",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_fix_f13_model_written.py",
      "chunk_id": "eb80c9a9d41725de91eda852",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "5fc83d736a61455e42bd9908",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kt8e.md",
      "chunk_id": "0c45d3e7472978264e2c40af",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_s6_hook_fork.py",
      "chunk_id": "f937cde1c32000eadcc5f478",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fixes-015a.md",
      "chunk_id": "e267c3e4d0dded56bc382c6c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "8143e5e7288b87b78e5fa0ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-g87r.md",
      "chunk_id": "694a5d371cb3e9a4e943f25f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "be7e622d745766806ca65b29",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_s6_hook_fork.py",
      "chunk_id": "11a575e7edffc1c4f14e2a16",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-models-by-role.md",
      "chunk_id": "2b02b3c62bc19073a076d6a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.3/manifest.json",
      "chunk_id": "4fc028c581a73c1a6c66e0b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "e378bd1dc79e16987539f735",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "33234c240209dfe1ca23f7c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/w2_201_support.py",
      "chunk_id": "472aab17e23da45965152c7b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "fbc7bc834c1459e246679d97",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "8dbcab662432497fab6d868d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "95549eda076c75d669c84abd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "1d34f59d136fc065fcc063a4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "08822d7987887b662bc9bbdc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "22773e524fb237a672953390",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/tools/counts_notes_v5.md",
      "chunk_id": "81f8c3f1db653714aef20b72",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/CHAIN-DISCOVERY.md",
      "chunk_id": "e40be5d9d5d3d8258465fc20",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x3_lead.py",
      "chunk_id": "0502f7d564f6ddda32a8f100",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "7267abf577fc9e5ad96f01de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "74dc0c37f8cf2ff531b99ad6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "060013124d32ac5cb4bbd838",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "37be4c253429ee543f6c071c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/w2_201_support.py",
      "chunk_id": "322b5bb86612af39f8e69aed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/CHAIN-DISCOVERY.md",
      "chunk_id": "da410f7e7a1acb5624e5ca79",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST.md",
      "chunk_id": "fc3796401d074c271c20d3f7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "eda751f223389e11b74302aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "1a442217cbb1bc90dfa63683",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/w2_201_support.py",
      "chunk_id": "bb27670e919ac620df331d14",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "522350a9fbee7b95e1f10988",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "chunk_id": "d2586b8669063cfcbd34593b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "0d720352ab1ded5cfdc4e916",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "b433073f8275c72ac7662c74",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/SOURCE_MAP.csv",
      "chunk_id": "a3fb6866a64a6f0e85318f9b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "7bd968ad0c28f97e0789ef51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "fc06f44f4de6b21b3915d62e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/contract.yaml",
      "chunk_id": "d8b73da439269b431c5bcd0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/w2_201_support.py",
      "chunk_id": "7cce772114536eab9059e5ff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "chunk_id": "779c85ff6d94aa5dcccc5581",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "bdca6a8ecdc9976c772aeac0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "5e86ff0e76b2078aab678180",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "chunk_id": "3157922a2b948c9712d5cd04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "c6da1032993011b5af1860dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "435b46ba2897741f93176b20",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-55-review.md",
      "chunk_id": "f83907deb9908204f7d44bbb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "db25169d8c02b4ddd3c760b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/05-repository.md",
      "chunk_id": "b972bc4d8b0b47b9177a9386",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "9c38f40d8653b2b63fb2f0c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "ed995075aca783c31ffaa0f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".github/workflows/ci.yml",
      "chunk_id": "ffb4805e1aa91d6ca9ec77fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/w2_201_support.py",
      "chunk_id": "cb1ea470246516baacd8393b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "98b71825d36a379ffd140ac6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/queue/command.py",
      "chunk_id": "78349ee8d189132477fa9229",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-PAGE-2026-11-22.html",
      "chunk_id": "51e84e26148f02db22c71359",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "80736971f10fcfb5392ac630",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_fix_f14_lead_effort.py",
      "chunk_id": "f994c96396901997ba61ee81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "12099bccb8c380393cd0287f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "f7ed2c638336fc6368001745",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "6f4f149b971393a4ba1b882c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "2ea2881f687ec7dbaa9b12b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_s6_hook_fork.py",
      "chunk_id": "d966296b22309106c060d8df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "chunk_id": "9d59e1fa6f63e1b56395f350",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "51fbcd303a3c3a42c0d48fd3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "fc44a4edb9d27dd4ab60557b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "3b3f0d6d550d9628abcb700d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "7b1ee757d3830f345c0e00c6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_r4_memaudit_models.py",
      "chunk_id": "70f422800aab9f9e070fcd1d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "1fcc6139445418dccf47b940",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "14fccb5d17d5d5ddd50e53d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_s4_exceptions.py",
      "chunk_id": "c44c9572d74e67451278bc17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "5fd2858269dfaec85daedfc2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "2fa48d6bb7e011d5cc5200d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "ff038dd7bde06ccb9e92f835",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-184/README.md",
      "chunk_id": "4191f9a9d14f08dcabdd9f7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/CHAIN-DISCOVERY.md",
      "chunk_id": "bfb6869ae624791f7fa095f7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-rubric-tickets.md",
      "chunk_id": "f92697969f2a37096b04766d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST.md",
      "chunk_id": "794d8cebc3b95c89a826d165",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_f2_no_usage_brake.py",
      "chunk_id": "6dbdb05e67d694f8838cb5b2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "482a6e9f20a373d595506b4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "9eebb1ac1fa79d8568eedbab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x8_fix_run_folder.py",
      "chunk_id": "32ee116e3bc145474450d95e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/CHAIN-DISCOVERY.md",
      "chunk_id": "1c5504cdae41388485f20ddc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W2-55-review.md",
      "chunk_id": "359582e850269c7cf9d62927",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/CHAIN-DISCOVERY.md",
      "chunk_id": "af7b7eeb5133a3aa800e2c1b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "1814a8a2c8727ad84fe203ff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-l2-4-queue.md",
      "chunk_id": "492fc15e6798cbcb23d23fc1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/MORNING-BRIEF-2026-11-19.md",
      "chunk_id": "3ac0cf9f55988caa7d980931",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_s8_wake_hooks.py",
      "chunk_id": "2706808afcd91727178fc4f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/CHAIN-DISCOVERY.md",
      "chunk_id": "fe10647eea846d362892c440",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "chunk_id": "9b90fb34bb728045bf93b024",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-card-w2-128.md",
      "chunk_id": "494f435a9f23a0b641799d81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "662fe3de5275810234791d55",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_s5_hook_class.py",
      "chunk_id": "56aa481b4e854a581e3ae37a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/CHAIN-DISCOVERY.md",
      "chunk_id": "0eea0b402d345c85e7fb075e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/release-0.1.4/STEPS.md",
      "chunk_id": "7da9631c189e77b886ce89b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4-LIST-B.md",
      "chunk_id": "709627d9ab27629ecb86cfe9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fixes-015a.md",
      "chunk_id": "c30011eec4696cb75b161aaa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D3-WORKLIST.md",
      "chunk_id": "aa20351a554b1f369ab20f14",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/C3-TRIAL.md",
      "chunk_id": "8db6e8d7b34f357d8297f534",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-bundle-a-reds.md",
      "chunk_id": "8bcbe739828f7160b7bd835c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "81df90349063cf00f4413e94",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/w2_201_support.py",
      "chunk_id": "86d5cbc9270277d62ef24a3a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "chunk_id": "3146e26ced2a1ad7bdb5ae8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/model-exceptions.yaml",
      "chunk_id": "a4a9d0756f6c4861e4c920ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "c366d10eae340b4e13b00a98",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_s7_cache.py",
      "chunk_id": "cb2753d6668647cdb30725fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "aac0502c4fb51989f15916e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "fdb53da1d3c4dd40743ab13f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_r2_launch_model.py",
      "chunk_id": "dd392f91ab348a51463fdbc2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "3bf5f3cdeab6da2f5e034590",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "7a9f387ba1434e1c7732e70a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "433e85ec7eb8e7cb8382fe95",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/queue/command.py",
      "chunk_id": "d35abd919abe2afad8d38edc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "47c321674278f48da653e506",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_fix_f19_rubric_model.py",
      "chunk_id": "dda1d180c7fc9a873601787b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fixes-015a.md",
      "chunk_id": "23989e8db5cfbe8baf8e2e18",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/command.py",
      "chunk_id": "764d953087096e7741b1295d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_s2_criticality.py",
      "chunk_id": "fe3e6589f4d58b1b4248cfbf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "d7d314a3d0f18b0833273f33",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "2426ccf3eb8c090b06b55635",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-33/README.md",
      "chunk_id": "876da67700e1ffcdda2b37ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/MORNING-BRIEF-2026-11-19.md",
      "chunk_id": "34ecb9aba0cbe28f35e04f68",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/queue/command.py",
      "chunk_id": "365b9ce0d1caa1ccd25d5ea2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "cecbdcef92eea4e916075682",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-dc-forbidden.md",
      "chunk_id": "f828c563a0450d3e6dfb514b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "61ce8a1aaf39807bf0d01ae3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "caa4e1f4b147f8bc1d296c56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/C3-TRIAL.md",
      "chunk_id": "cfae7701e6ffdeabf3c0aea5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_f1_hook_unreadable.py",
      "chunk_id": "86b3673b9daf12df41683b8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "0814a7f0aa932259581eaa67",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fixes-015a.md",
      "chunk_id": "6c808d2ccbf579deaf2c33c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/C3-TRIAL.md",
      "chunk_id": "1ea7631ca1dd419a9d2fbdc7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_f3_line_checks.py",
      "chunk_id": "e6a7b24645532365aaec58bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/queue/command.py",
      "chunk_id": "43853d0e5d0a48cd01c98d1c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x5_words.py",
      "chunk_id": "3764d9b7ed5a99eb9b94ec42",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "chunk_id": "f509ddfbf2561303c4c1f5cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/command.py",
      "chunk_id": "5429d75a61250a8385cb7453",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "18a509958a09f17bc274d500",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "7f424e9e445090fd2b9449d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "1feb3b106b1dfaf50ce4db02",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_s1_role_files.py",
      "chunk_id": "02f65afac3bd4d656535d5a4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/path-map.yaml",
      "chunk_id": "7f0e6643344b760094f3f87e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/command.py",
      "chunk_id": "8a64e5d6e03eed67883e6ca4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/queue/command.py",
      "chunk_id": "17a5e751306b1992d1da3d46",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "bae3d29a95a61c1aa3fdf081",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_r3_limiters.py",
      "chunk_id": "c18f7465dc82667fc6f5e41b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/path-map.yaml",
      "chunk_id": "897dc0483aace040218df878",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "6c6371b0a5990f4d9ee66c2c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "dd23c1ada235e22bfa86d844",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/C3-TRIAL.md",
      "chunk_id": "768b5a9e43877f59ccbb81b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x1_fix.py",
      "chunk_id": "eff26f58c55fa3751a72b721",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/queue/command.py",
      "chunk_id": "6f66f5364ec62c525c8eefdb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/queue/command.py",
      "chunk_id": "a90a6053cfcedf7a205d2fde",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".claude/hooks/agent_model.py",
      "chunk_id": "1864ba01399a11b24d1126ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "905b0e6a7081202acba3501d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "edcc475a25219e6ca102dc39",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "3467133da936abb1058f8779",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "bccd9ab5607d13e5d929f8c4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_fix_f1_connectors.py",
      "chunk_id": "5c412a6cdbfbfe27a380bfba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "e9bdb62321f9047f4f63b69d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-models-by-role.md",
      "chunk_id": "6e48d9709caa00cba11b0799",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "7110130d4101d05f462365bd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "58c68bc5cebeb63cb0f6d5bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/model_exceptions.py",
      "chunk_id": "494ae6442eda81f3590edc71",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_r1_role_files.py",
      "chunk_id": "8ab00d1eb1a9a7c60f09eab7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/C3-TRIAL.md",
      "chunk_id": "05d2672d34a8e57e5e4d6c77",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-6n5k/CP-DAEO-6n5k-0002.md",
      "chunk_id": "62db17c122ada87fe48a2678",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/command.py",
      "chunk_id": "4e03847e24e54f282b44a395",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5rgj.md",
      "chunk_id": "2c735b8cbcdbc9e7c441d473",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "262e15401f4cb1a4d84b04d8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5rgj.md",
      "chunk_id": "47075a8d88ef2ed0705034d3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/command.py",
      "chunk_id": "aa4515f5d8d47adb02b9d92c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-6f0s.md",
      "chunk_id": "47561065d3adccc0df0def29",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_r2_launch_model.py",
      "chunk_id": "489b1a3477df90732e20ece9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-6n5k/CP-DAEO-6n5k-0004.md",
      "chunk_id": "25dc86324a81c5249a5cb7cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-6f0s.md",
      "chunk_id": "f9e80b4f881c36dd5d82710f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/criticality.yaml",
      "chunk_id": "386a1f861f9185513ef1e0fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-lrre.md",
      "chunk_id": "1e6dbf6506193b3d1d8a0570",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "cb704885dad149f800cee1bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-lrre.md",
      "chunk_id": "9618ec4486f21036f2f7c0bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "a40f05aa8a4c35229f10fde6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-6n5k/CP-DAEO-6n5k-0007.md",
      "chunk_id": "9e95a987f8c5005498b7b75d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x3_lead.py",
      "chunk_id": "7b299e8635b9ee7651961a8f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/queue/checks.py",
      "chunk_id": "ab6490b5e0c3962e7777fc3a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "8e12f3e75ee0036ec69a10f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-6n5k/CP-DAEO-6n5k-0010.md",
      "chunk_id": "ce0825b529048ed6981da548",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "6066d3a24069ffec66c4dffd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l2b2.md",
      "chunk_id": "6b18528a4f4de43ada08c3f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x7_relaunch_kind.py",
      "chunk_id": "c1a2c10c083d97ef9f021c24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-6n5k/CP-DAEO-6n5k-0002.md",
      "chunk_id": "6ec8df763edcc4e11541f165",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/L2-4-PROVING.md",
      "chunk_id": "1a1cfc0620a94178c7d2aaee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/queue/checks.py",
      "chunk_id": "6cc0d3cde5140d022e327664",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-6n5k/CP-DAEO-6n5k-0004.md",
      "chunk_id": "7e3cfba0c565d1187fc9a79a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "7955bd57e436df8a68344ab5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/w2_201_x6_support.py",
      "chunk_id": "da15b16669707542b61fffbf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "a20dd2ff55f40bb07fc853e0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/command.py",
      "chunk_id": "b2bbe7d46917196de213934e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-6n5k/CP-DAEO-6n5k-0010.md",
      "chunk_id": "64a919d4d847e6e9ead32c65",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "cad61cb6b9d16d961e0946d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/MORNING-BRIEF-2026-11-19.md",
      "chunk_id": "3052fbd6b5aa88fbfa3e6fee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_r3_limiters.py",
      "chunk_id": "27a2d357d6c88281067f0956",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "65221085dd3a6c1c81cdfc08",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/checkpoints/DAEO-6n5k/CP-DAEO-6n5k-0007.md",
      "chunk_id": "b1d0388f2802a12355687715",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "b3cd5f2152aa207648be10af",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "6882632f252facf2d50e8287",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/util/runs.py",
      "chunk_id": "ff722406236f02d851d92eef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/w2_201_x4_support.py",
      "chunk_id": "4dd2122d29e2717628fc891e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/MORNING-BRIEF-2026-11-19.md",
      "chunk_id": "8145830386869c31b1e7f5bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-sdhj.md",
      "chunk_id": "975f8e076948ebe4c3587bd0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "b1a86e53d72d9703240bf955",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/C3-TRIAL.md",
      "chunk_id": "e47f1d558e017d411f127b64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/w2_201_x_support.py",
      "chunk_id": "9d7eebaa24427efdec098988",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "3738b74c6abdcfe7f98dab44",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "chunk_id": "801772bc3bbc6d4909c158ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "chunk_id": "fc45a289acc9a72f01e1d344",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "156ae8c14a3224f7ff7e1ec5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x2_chore.py",
      "chunk_id": "9c99bcc0e64edcee65cda838",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-g5-land.md",
      "chunk_id": "2afb08b6008057b3c19eae8f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "8fd7b798ec71bf5504440417",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-select.md",
      "chunk_id": "dea38de5cb3cffde822815fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-release-rule.md",
      "chunk_id": "c876f8b8a18c16ca370071a3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "fdef38795ee27ffa6cd93ccf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "chunk_id": "2a8c88f84d4c1fc44d42674f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/integration-plan-decisions-2026-11-24.html",
      "chunk_id": "349efb59d4ea3c438739eac0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "d0b05f25252deea7d6bb2060",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-37-DAEO-6n5k.md",
      "chunk_id": "d0a96602e5abc7079b6df8ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "3082ddfeedadfa026639a739",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "679be9dfbe0e86a861b56e71",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_s3_launch_rubric.py",
      "chunk_id": "0ff89a8441482dbda1a6988f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "2466721086a917621ba5ce9a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x4_new_ticket_notice.py",
      "chunk_id": "03dcc557f3f21e387f46085d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-rubric-tickets-2.md",
      "chunk_id": "500d6d8bcdbbfc44872c5bd7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "2bc9869012827892e2e85cee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "chunk_id": "1e6ef8505c84dc3601f4bbb0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x6_fix_landing.py",
      "chunk_id": "3ea72ceca32b3b61633bf50d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "e5e9fead486f21e45b2a79dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "c63138045a22e937795e2845",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOLDEN-WORKFLOW-CORRECTIONS.md",
      "chunk_id": "945def6c89f746161aedf94f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/w2_201_x7_support.py",
      "chunk_id": "a518a88943ff46695c4a38b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "bf2abb005636a5afc686e93c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "e3666c791f35caeafb47490c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-rubric-tickets.md",
      "chunk_id": "d4534faf28d4f6a1e3639946",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "970f254deb040eb4056d95eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "4e598dff34f6f08af4fbef42",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-40/w1_40_support.py",
      "chunk_id": "68dd2667e81f4e1a3d22679b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-l2-build-2.md",
      "chunk_id": "a18ee23464ae99fcdc332fce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l2b2.md",
      "chunk_id": "76d0788545dec856607a9414",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "80c1febb01606a546afd07ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-e82f/CL-DAEO-e82f.md",
      "chunk_id": "3a54d57a8a235442a8251db9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "78c5e0c802b1bf709e1591e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "116a448339eecbe230314cfa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-11-pathmap.md",
      "chunk_id": "0456241109d06747360b85f8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "96c077711ca32401aa1d647a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-11-pathmap.md",
      "chunk_id": "b9d3b18ce1ddf16c6d07c262",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-37-DAEO-6n5k.md",
      "chunk_id": "193102199a80279283e7967b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "f80028e60a40195f13d65e51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "92ce00f0dfe49fb389f30c56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "40386b6be037a75748bacbc2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "d2786b41a2699d6279d8db52",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "23f6c218a0f998530bacba90",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "e3f53bc1def6a49e26f5c2cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "dcc0fb4d6b69be1bf6d31c1c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "6fc7d056468a995abaac5947",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "0f686c03ea3bb2d789205648",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "a8119ad2383251af7bb47dc9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "c8b95196222a5dbbd95d8273",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "3704eb0f9c1f23ce3a8cf1b8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "46a91ce1bdf78fe77aaae0c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "97333c70de90c2fd7a3f6998",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "09d246fafeda04884f0fde67",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "b3c6e2ad680de8abfc25b097",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "64f54d985a4deae59ed6f254",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "e2347437d771b6be62beda8f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "7cdc8e79099cfb7e5031748c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-184/test_w2_184_r1_rows.py",
      "chunk_id": "9efc3a0906b401a36a72e2db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PKG-W2-37-CITP-1.md",
      "chunk_id": "24a4f8a79ff37bf6d7bd8feb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "5d72ea05897a2ceed6306309",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "eb9fe5c62e03a48894700f00",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "3cd964d58d4e96a123bc9189",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/queue/command.py",
      "chunk_id": "52025b597da5bde2918af903",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "75f8cc029d0ecf5c8798c6fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/GOLDEN-WORKFLOW.md",
      "chunk_id": "ce5bfd72775a0cbfaaa646c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "24dc7270cb5862326e2b534d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l2b2.md",
      "chunk_id": "27e2bfe47a64ccbdc0ee4da3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "3df631a54cb299b968a1ffd5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "2e0818d9298a2ecae04c2f15",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "ffae3c82fed2eb1d0ed16b7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l2b2.md",
      "chunk_id": "9eab4b9ce4372bf58541cc25",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "fab0e4d1f4dc2c162e90827b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "fdb9b68cbbd07862f5710e60",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "7786152eaa963df57e43f235",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-11-pathmap.md",
      "chunk_id": "e60022d5936d2dfe3db9cf79",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-11-pathmap.md",
      "chunk_id": "5a8a8bb127f4039b8437595c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-11-pathmap.md",
      "chunk_id": "b0f4f2d4c215c118f081c45c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-11-pathmap.md",
      "chunk_id": "ac3adf21202db6f1d2f0a5e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "a65a0f90bbcf78242a88b0e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "d9ff0de1a6d00ee7952ab992",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "dacf4ba75c8fb07222e55450",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "e59835d576923af1d6b47ee9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "93741b6f8506f97a8f6fa7a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/TRAILERS-UNPARSED-20261113.md",
      "chunk_id": "1607c103aa9e0cda62f1ddc2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-g5-land.md",
      "chunk_id": "9150127e8f5cd941d9230ef0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "158e1e89ccb0f787fb3170a4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-11-pathmap.md",
      "chunk_id": "5a70e6fb7e4aeba4c1ff9b70",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "7a4889ae1895a5404ca815ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/TRAILERS-UNPARSED-20261113.md",
      "chunk_id": "93109383b0831c68068504b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "8c85a9ac5ab206002f63991b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "9c20fef8d5f050b5784e4cbb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/G5-APPROVAL.md",
      "chunk_id": "ce029903a6f27f90280c6a06",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-card-w2-128.md",
      "chunk_id": "5085cb9117f5be5dd67036dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-11-pathmap.md",
      "chunk_id": "a9e994c76b56f8f562600c66",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "67c548718f87327ed3b860dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-card-w2-128.md",
      "chunk_id": "be236ccb5bedf67295ac9edd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/G5-APPROVAL.md",
      "chunk_id": "aefaf00c8f1d528405868664",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "43f87272b31a91307f4b5cc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-kq8b.md",
      "chunk_id": "90482921a96607b452b679e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-release-rule.md",
      "chunk_id": "5c18cd4be2c7760216e0846b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/G5-APPROVAL.md",
      "chunk_id": "7d661056c14d0159f8d720fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "0f92902227542c0a7295c918",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-11-pathmap.md",
      "chunk_id": "634512437303c357643b6ee9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/G5-APPROVAL.md",
      "chunk_id": "4fded7078e8379d5e9d11a89",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1/ready-batches.md",
      "chunk_id": "5b4bb7aa6b522187a3b4bc0e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "0a3559b04fe2b81d835382d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-timing-tests.md",
      "chunk_id": "e45bedf2009a445abb3b3e46",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "1075243cae156378f37ac532",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-184/README.md",
      "chunk_id": "b908ba00f0bcca2375e59300",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "c7d97fe40a468ea4194e7d58",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-a2h5.md",
      "chunk_id": "5696c5533d46760c67c81f99",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-bundle-a-reds.md",
      "chunk_id": "b8edf88f9e60ba2c7fea45bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "ee7e33633a0c9e82364fa3de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "43d1a93351e58e6ec1e00e09",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-d7-adopt-lands.md",
      "chunk_id": "2b69cadd21f3888473c6ca4c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "a621370dbcd008c53db43e75",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.4/manifest.json",
      "chunk_id": "ea49efa18122fb437b6026a2",
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
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "a33ba1087f711ccd307c8c6a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "dd3150545b3351f3b7198d62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "60fcf4d4f0dddae34793ec16",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "2ac8a795639a9b42becebd7f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/COMPANY-MAP-2026-10-29.md",
      "chunk_id": "771a2c99e2e0a47c704fedbc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-bundle-a-reds.md",
      "chunk_id": "d072eb0ec549f66c0331050f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "5a02365313eb162e4452c432",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "add825aeaf8227bf0cefa0b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-zflj/CL-DAEO-zflj.md",
      "chunk_id": "27206e5b98f4372ef6afe3c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "chunk_id": "ba8b13f8e4c6985caf40525b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-kl5e/CL-DAEO-kl5e.md",
      "chunk_id": "62b823599d3030d43b5e812e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "a63cf9e5f8d7549b619c14cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-release-rule.md",
      "chunk_id": "6b3cc7dced1f8c0b109b6184",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-release-rule.md",
      "chunk_id": "223d15ecfdfab2fd5f603ea9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/DAEO-0rfi/CL-DAEO-0rfi.md",
      "chunk_id": "2b43f53b195eabfb4afbf6e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "3734135273c263689d5332e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "77f6e0f8e4f8675dd1fd6ec9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-release-patch.md",
      "chunk_id": "753dea6d9d52d1f1bcbf3c30",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "77216c5a6327ca4b1aaf49b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "35615802ab81d99913d4dd1d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1.md",
      "chunk_id": "a67fc278bd7011deb3dfdb2c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/c-tickets.md",
      "chunk_id": "17360fda4736cfd11a6d3482",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/D.md",
      "chunk_id": "73a646690a75c62399223655",
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
      "path": "docs/emergency-2/audits/E2-AUDIT-2-CONTRACT-IN-CODE.md",
      "chunk_id": "767dbddbfaace0a8fe4abb5a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PKG-W2-37-CITP-1.md",
      "chunk_id": "aa90312f814bbead3369d50a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/PKG-W2-37-CITP-1.md",
      "chunk_id": "6367222beb4996abd0b8453e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "6de2e4018694f9a19f8ab6d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "ebcf5c63fecceba4ea6a4909",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "0a93495c432299ea7e24a407",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-models-rubric.md",
      "chunk_id": "fc424c02846a7c2251723923",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "0fe457381932ae20c8b881a4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-184/test_w2_184_r1_rows.py",
      "chunk_id": "6c172a5b3a17abcf797e6d50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-1-8-impact.md",
      "chunk_id": "3df76c49eeaa3e964113c921",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/queue/test_queue_new_tickets.py",
      "chunk_id": "3d4561b79cb19297f4f86fa0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P3-lifts.md",
      "chunk_id": "10f4cf863a9de860f20a7cbe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P3-lifts.md",
      "chunk_id": "1a3430790b16196dfa2dfa96",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-40/test_w1_40_templates.py",
      "chunk_id": "0fe72d9d7507ac4cc7f87076",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-184/README.md",
      "chunk_id": "2115f0f8b32b235e2cbc9214",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/dispatch/test_w2_201_x7_spawn_kind.py",
      "chunk_id": "9f5b990311f850cb99ccf2a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/launch/test_w2_201_launch.py",
      "chunk_id": "ec5beac805c68014d41567da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/hooks/test_w2_201_agent_model.py",
      "chunk_id": "b82bebc7143b2988654b3d29",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/launch/test_w2_201_x7_kind_key.py",
      "chunk_id": "e9d5d50defe75b229babda07",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/launch/test_w2_201_kind.py",
      "chunk_id": "6f5cf17091216e9c5c7b7313",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P3-lifts.md",
      "chunk_id": "52987521dbbe2592ee441b7e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-33/w2_33_support.py",
      "chunk_id": "7e611aed3637bb2b1a9308fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/launch/test_w2_201_x8_runs.py",
      "chunk_id": "f1c3e7cede0424690a26eebb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/hooks/test_w2_201_agent_model_worktree.py",
      "chunk_id": "e05122b17cc36342557486e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-33/README.md",
      "chunk_id": "30dd32f4b435a97f40ad9a51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-184/README.md",
      "chunk_id": "66f27d24d5fff85b503746ff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-33/w2_33_support.py",
      "chunk_id": "503e73eb7a4b3f8a97ab9603",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-22/test_w2_22_fix_connectors_drift.py",
      "chunk_id": "c979fb9048a168c4727b0588",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/queue/test_queue_w2_201_fix_landing.py",
      "chunk_id": "1f34cf431b49830886bf3501",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/launch/test_w2_184_criticality.py",
      "chunk_id": "da9508cad4286e4a4b5c2e6d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-33/test_w2_33_planted.py",
      "chunk_id": "90200b00758dc57a42e655e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-136/test_w2_136_plan_output.py",
      "chunk_id": "1f71e5130a39dd0db5e45797",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_s5_hook_class.py",
      "chunk_id": "a0950d427ab348103b02704f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-184/test_w2_184_r1_rows.py",
      "chunk_id": "bc76677c20e3ab94c64c5245",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k.md",
      "chunk_id": "d920209915000bb8aa9c8725",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k.md",
      "chunk_id": "94702754f25dc475d8c8cc04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-33/README.md",
      "chunk_id": "1cf651f3965990ac20d7fc91",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "027f54d91f08cc2e636f4bc6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "63d34472617fdec9540074bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "0e5df154dd67f3ad7458824d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "ebfa5baff64640dfe7aa22b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-dec1163.md",
      "chunk_id": "5d7f87dbe498eb25a0f63f01",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "2e0f8c36053297bb49ec8964",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x6_fix_landing.py",
      "chunk_id": "e8e98e8daca40151b6d55876",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x6_fix_landing.py",
      "chunk_id": "221f7c4aa6bc41bb04fb448b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-version-1.1.0.md",
      "chunk_id": "bced6904cfc22abc1e24886d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "e662e6f6df93632db9e91526",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "abc1f7f5c0740a00efe9a150",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "0d712d21788ef5fb8996f198",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x6_fix_landing.py",
      "chunk_id": "c2b678d4af66fb54d75c66df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "647929cd48038ccc5d56e3be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "5636fd7809429c4cbb536096",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "fe26020d9f8f4f7d0d9d782c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "a30af1e261559ffd0286dd00",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x6_fix_landing.py",
      "chunk_id": "8a0563179db0986843c905f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x6_fix_landing.py",
      "chunk_id": "5a38b7fe95115ca77652303c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "0d92859933a2e5829277ab09",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "5222d5dbd5abf052c54abe45",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x6_fix_landing.py",
      "chunk_id": "8b8e0fabac8a8c91b6d7372e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "f0835b34c8c00316950863a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-p7a.md",
      "chunk_id": "95d546390f91f0759f2a212e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x6_fix_landing.py",
      "chunk_id": "eecdebed2daff1f2394044a3",
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
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-version-1.1.0.md",
      "chunk_id": "80dea5134d14296f3625d21c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-6n5k/PR-DAEO-6n5k-narrow-dec1163.md",
      "chunk_id": "652854f84eeac2c43029e367",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/README.md",
      "chunk_id": "91a8498a504784e58197a542",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x6_fix_landing.py",
      "chunk_id": "b2585dd7ef5dbdbe4e57685e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x6_fix_landing.py",
      "chunk_id": "08e696f975a3c683f563c046",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-115b/README.md",
      "chunk_id": "601bda9ed338b4b2e937d880",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/w2_201_x6_support.py",
      "chunk_id": "62558a48585b2a4fb1fa0531",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x6_fix_landing.py",
      "chunk_id": "75ffd42abfec83ac50dc7628",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x6_fix_landing.py",
      "chunk_id": "fa59571083bf81f0b539699d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/test_w2_201_x6_fix_landing.py",
      "chunk_id": "f2a3b40417d4252b83892f41",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-158/README.md",
      "chunk_id": "10e874c111714d7650a67f7b",
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
      "path": "tests/acceptance/W1-07/test_w1_07_recorded_commands.py",
      "chunk_id": "9907041dbd5bb7c5f2a07084",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/README.md",
      "chunk_id": "3a33e16dbaefc1c589e9fa1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-37/w2_37_support.py",
      "chunk_id": "44800b0c0750711f002ff907",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-07/test_w1_07_recorded_commands.py",
      "chunk_id": "c7972993dab5f2b5293d6a9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I3-retrieval-context-resume.md",
      "chunk_id": "748966c56e2da52cf366ad18",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I-SYNTHESIS.md",
      "chunk_id": "dc75a6f92424cd135154ae26",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P2-perticket.csv",
      "chunk_id": "ee3179c3e49ae7de16070cef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "fbb85536b2a7d4dcafa1a2dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "3c90a013942a52a0684ccca8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "4e242dffc43010ad5dcf21bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "88bc5979254dfdd8e15086d6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "ac6a6a0a1b486900f5b72297",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "42cf5a123a2271f0564bedd9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-201/README.md",
      "chunk_id": "2f41b18dd6de81b5d649b715",
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
          "CAP-35.a",
          "CAP-35.b",
          "CAP-35.c",
          "DAEO-5rgj",
          "DAEO-6f0s",
          "DAEO-lrre",
          "DEC-1120",
          "DEC-1212",
          "DEC-1214"
        ],
        "left": 46
      },
      "changed_by": {
        "DEC-1120": [
          "DEC-1214",
          "DEC-1212"
        ],
        "DEC-1212": [
          "DEC-1215",
          "DEC-1214"
        ],
        "DEC-1214": [
          "DEC-1236",
          "DEC-1225",
          "DEC-1222",
          "DEC-1219",
          "DEC-1215"
        ]
      }
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5973
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLTZuNWsubWQiLDYyLDcxLCI5NzU4YmRlOTA4NGNmNmU4NDExZTU4MzciXSxbIi50aWNrZXRzL0RBRU8tZzIzaS5tZCIsMSwzOSwiMDUxMjg1NTAzY2RkNzY4YzViMWM2YWY5Il0sWyIudGlja2V0cy9EQUVPLWsxdXMubWQiLDE3MiwxNzYsImY0MjIzYzFlMzE2MzdjYWE4Y2ZlMzNiYyJdLFsiLnRpY2tldHMvREFFTy1rMXVzLm1kIiwxNzcsMTg4LCIyOWRkMTBkNTkwM2YwZWZiZjdmNGUyZTQiXSxbIi50aWNrZXRzL0RBRU8tbDJiMi5tZCIsMSwzNCwiZjU0NzgwMTNmNjY0N2UyYTRiZjQ1NTJiIl0sWyIudGlja2V0cy9EQUVPLWwyYmQubWQiLDYwLDcxLCI5OTNmM2JjNDUxZDRlMzdlOGEwMDE2YjUiXSxbIi50aWNrZXRzL0RBRU8tbDJiZC5tZCIsNzIsNzMsIjYwOTMxM2FlMmJhNDRhMjEzMzQwN2MyYiJdLFsiZG9jcy9ERUNJU0lPTl9SRUdJU1RFUi5tZCIsMTgyOCwxODI5LCJhNTQxYWYwYmYwMGY5MTU1YTljNjM3ZmQiXSxbImRvY3MvY29udHJhY3QvY2FwYWJpbGl0aWVzL0NBUC02My5iLm1kIiwxLDEwLCJiNmEwNTllOTM2MDJiNGFlNTU2ZTE0Y2IiXSxbImRvY3MvY29udHJhY3QvY2FwYWJpbGl0aWVzL0NBUC02My5iLm1kIiwxMSwxNiwiMTIwYjZjZWEzZjI5MDU5NGM4ZDlmNjdhIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2JyaWVmcy9MRUFELTEtOC1pbXBhY3QubWQiLDE1MSwxNTEsImU4NzNkYTdiYTk4ODE2MWM1MTZhMjNiNSJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9JTlRFR1JBVElPTi1QTEFOLm1kIiw3MCw3MSwiNDU4M2U4M2Y1Mjg2NWZhNTRlZWViNDczIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL0lOVEVHUkFUSU9OLVBMQU4ubWQiLDcxLDcxLCJkYzg4ZjcyZTUyYzIwZWVjNTg2Mjc5M2MiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vUkVDT1JEUy1NQVAubWQiLDExNywxMTgsIjQ0MTdhMTQyMjBmZDZhMzRmMGQ2YjM1NSJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9SRUNPUkRTLU1BUC5tZCIsMTE4LDExOCwiMjQ0ODgxZTA5YjkwNWRjZDU2NjFkZDM2Il0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL1JFQ09SRFMtTUFQLm1kIiwxMTksMTIwLCIzYWY5ZTQ1MTFkNGZiMThhMDM3MWQyMzgiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vUkVDT1JEUy1NQVAubWQiLDMxOCwzMjMsImNiY2JhMGNlZGI5OWU4NTU3NWU1YjdiZiJdLFsic3JjL2dvdi9xdWV1ZS9maXgucHkiLDEsMTksImU3YjNmMTczMjM2ZmNmMGNjYWYxY2RmYiJdXSwiZiI6Ii9ob21lL3VzYWluL2dvdi1vcy13b3JrdHJlZXMvVzItMDAtc3RvcmUtYiIsImkiOltdLCJvIjoyMCwicCI6eyJiIjoic2VydmljZSIsImQiOiJjdWRhOjAiLCJoIjoiOGEwNDJlNWFmMTIzNDk3ZCIsIm8iOlsxNSwxMSwxMiwyMCwzNiwyLDI2LDcsNiwxMyw4LDE2LDMyLDQsMzksMzAsMzQsMjUsMjEsMjQsMjcsMzMsOSwxOSwzNywyMiwxOCwwLDUsMTQsMjksMSwzLDEwLDI4LDE3LDM1LDMxLDIzLDM4XX0sInEiOiJ0aGUgbGFuZGluZydzIGFmdGVyLXN0ZXAgYW5kIGNsb3NlIHJlY29yZDogZ292IGltcGFjdCAtLWNoYW5nZWQgaW50byB0aGUgY2xvc2UgcmVjb3JkLCBldmlkZW5jZSBmaWVsZCwgbm90aWNlcyBjb3BpZWQgZnJvbSBxdWV1ZS5qc29uLCBULTExLCBXMi0yMDEgWDYgZml4IGNsb3NlIHJlY29yZCBmb3JtIiwiciI6MCwicyI6IjI5Yjk2NGI1OGNhZjE5YmY0MTVlYjVjYTFlYjRjNTAzOTQzOWUyOGUiLCJ0IjpudWxsLCJ4IjpbIjg1ZDNkYzNiODJkZmRlZTg4NDk2M2Y5MCIsIjhmNjQ4MzQzODc2YTgwMDg3ODM0NmJiMSJdfQ==",
  "routing": {
    "code": [],
    "named": [
      "fe27d1ee94717aa06609d84a",
      "f4223c1e31637caa8cfe33bc"
    ],
    "phrasings": [
      "the landing's after-step and close record: gov impact --changed into the close record, evidence field, notices copied from queue.json, T-11, W2-201 X6 fix close record form",
      "landing s after-step close record gov impact --changed close record evidence field notices copied queue.json T-11 W2-201 X6 fix close record form",
      "the landing's after-step and close record: gov impact --changed into the close record, evidence field, notices copied from queue.json, T-11, W2-201 X6 fix close record form CAP-63 DAEO-6n5k DAEO-k1us"
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
        "chunk_id": "29dd10d5903f0efbf7f4e2e4",
        "path": ".tickets/DAEO-k1us.md",
        "start_line": 177,
        "end_line": 188
      }
    ]
  }
}
