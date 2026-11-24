# Lead brief: every hidden question-set root refused by code to every session that is not the measure's own (DEC-1249 (2), I-28; fixes under W2-204 and W2-208)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-24. **Read `docs/emergency-2/briefs/LEAD-COMMON.md` first: every rule there applies**, in particular: never open a sets root yourself, and never glob `/home/usain/*`. Decide, never ask (I-10).

## Why
Read DEC-1249 in `docs/DECISION_REGISTER.md` and row I-28 of `docs/emergency-2/integration/FINDINGS.md`. A Gov OS lead's ordinary glob reached a file inside EXAMIN's hidden question-set root. The owner: "make it impossible by code: every sets root refused to every session that is not the measure's own, in Gov OS and through the kit." The threat model is honest mistakes (CLAUDE.md, the golden rule), not an adversary: the aim is that no ordinary search, glob or read can reach a set. The two roots today are EXAMIN's (under `/home/usain/`, named for EXAMIN's evaluation) and `/home/usain/gov-os-eval`; `gov memaudit` takes a root as `--sets-root <path>` and no registry names them. Gov OS's project settings carry interim deny lines for both (`.claude/settings.json`), which a Bash command naming EXAMIN's root already trips; they go when this lands.

**Never open either real root, and never name EXAMIN's root in a shell command (the interim deny refuses it).** Tests use planted roots in temporary folders only.

## What (KPI lines, written as `## Fix:` sections into `.tickets/DAEO-ma4q.md` (W2-204) and `.tickets/DAEO-kt8e.md` (W2-208); the CTO approves them by this brief)
- **ER-1 One registry.** The machine's sets roots are named in one registry under `~/.gov-os/` (machine state, in no repository): repository, root path. `gov memaudit` resolves a sets root only through it; a `--sets-root` that is not registered is refused with a code naming the path.
- **ER-2 Out of reach of an ordinary glob.** The default root for a repository's sets is a folder under `~/.gov-os/evaluation/<repository>/` (a dot folder: a `*` glob never matches it, and nothing under `/home/usain/*` or a repository names it). `gov memaudit` refuses to create or register a root outside that folder (a code and the reason). A move command (or a documented, tested `gov memaudit` step; choose) moves an existing root and updates the registry; it refuses while a measure is in progress. The CTO runs the moves, each with its repository CTO's yes.
- **ER-3 Refused to every session that is not the measure's own.** A PreToolUse hook in Gov OS and in the kit (installed by `gov adopt`, `gov adapters` and `gov update`) refuses any tool call (Read, Edit, Write, Grep, Glob, NotebookEdit, Bash) whose input names a registered root, the `~/.gov-os/evaluation` folder or the registry, unless the session's role is one of the measure's own (the writer, checker, reader, grader and driver roles `gov memaudit` sets when it launches them; read how it launches them, `indep_launch.py` and `memaudit/driver.py`, and use what it sets, or add one variable it sets). The refusal names the rule and DEC-1249. The kit keeps exactly its two deny lines (W2-208 K1): the refusal is the hook, not new deny lines.
- **ER-4 The measure still works.** The measure's own sessions read and write their roots as today; a planted fresh-80 run end to end (the existing W2-204 tests' rig) passes with the root in the default folder.
- **ER-5 Doctor.** `gov doctor` names a registered root outside the default folder, an unregistered folder under `~/.gov-os/evaluation/`, and a repository missing the hook (a failure for the hook, a notice for the rest).

Code area: a small module for the registry and the hook (choose its place under `src/gov/memaudit/` or `src/gov/`), the hook file and its hook line in Gov OS's `.claude/settings.json` and the kit (`template/.rulesync/hooks.jsonc` and its hook file), `gov memaudit`'s root resolution (one function; another lead, fix-memaudit-2, is editing `deliver.py`, the brief writer and `fresh.py`: keep your edits there to the resolution call), `src/gov/doctor/` (one part). The models-by-role and kit-head leads also edit the kit: touch only your hook's line and file there.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-eval-roots`, branch `e2/eval-roots` from `w2/integrate`.

## Green
LEAD-COMMON's flow: the test designer writes ER-1 to ER-5's acceptance tests (red on the base; planted roots and planted sessions only), including a planted non-measure session whose Read, Grep, Glob and Bash `cat` of a registered root are each refused, and a Python glob of `/home/usain/*`-style patterns that cannot reach the default folder; the engineer builds. Then exactly the impact-selected suites: `PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-ma4q=e2/eval-roots --onto w2/integrate --select`, and `gov accept`, both through the heavy slot (DEC-1244 X-1). W1-35 or `tests/unit/dispatch` errors when run together are I-22, not yours. Check the acceptance trailers (LEAD-COMMON).

## Return
Branch and head; ER-1 to ER-5 with tests and result; the exact steps the CTO runs to move the two real roots (commands, checks, rollback), which the CTO runs only with each repository CTO's yes; the selected suites' summary lines; reds not yours; your `gov retrieve` calls (count, queries) and the records you used; the C3-trial counts.

## Your memory bundle (DEC-1249 (1); role: lead, profile decisions, history and plans; uncut, as `gov retrieve` printed it)
Query: How are the hidden question sets of the memory measure protected (sets root, transcript scan, which sessions may read them, how gov memaudit launches its writers, checkers and reader)? Decisions, history and plans.

```
store: 83bc050aa88b (/home/usain/gov-os-worktrees/W2-00-store-a)
{
  "store": {
    "commit": "83bc050aa88bb2e6f50e7cc2978ce8403016f364",
    "head": "83bc050aa88bb2e6f50e7cc2978ce8403016f364",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-a"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "ADR-0002",
      "sha256": "6cc269551156c91c631bfaed84ed132c4d7c5991b07690effe826b6ab2d303bd",
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "start_line": 262,
      "end_line": 302,
      "text": "### 5. Repository layouts\n\n**Product repository after adoption** (architecture v0.3 \u00a72.2, with `.tickets/` in place of `backlog/`):\n\n```text\n<product>/\n\u251c\u2500\u2500 AGENTS.md  CLAUDE.md  .claude/            generated by rulesync (rulesync owns .claude/, DEC-074 Q7)\n\u251c\u2500\u2500 .rulesync/                                kernel part + overlay part\n\u251c\u2500\u2500 governance/kernel/ (Copier-owned) \u00b7 governance/project/ (overlay) \u00b7 governance/framework.lock\n\u251c\u2500\u2500 openspec/ specs/ \u00b7 changes/ \u00b7 schemas/feature-readiness (26 rows, docs/contract/readiness-dimensions.yaml)\n\u251c\u2500\u2500 spec/ decisions/ \u00b7 lessons/ \u00b7 failures/ \u00b7 research/ \u00b7 gates/ \u00b7 checkpoints/\n\u251c\u2500\u2500 .tickets/                                 ticket tasks (+ .tickets/.claims/)\n\u251c\u2500\u2500 tests/acceptance/<ticket-id>/             Independent Test Designer only\n\u251c\u2500\u2500 lefthook.yml  .github/workflows/gov.yml  .gitleaks.toml\n\u2514\u2500\u2500 .gov-runtime/                             gitignored, derived\n```\n\n**The Gov OS repository** (this repository; the Wave 1 tickets' `allowed_paths` use these paths):\n\n```text\ncopier.yml                      template configuration (_subdirectory: template)\ntemplate/                       everything copied into a product: governance/kernel/{hooks,schemas,skills,roles,templates,bin},\n                                .rulesync/, openspec/schemas/, lefthook.yml.jinja, .github/workflows/gov.yml, .gitleaks.toml\nsrc/gov/                        the gov CLI (subpackages per command area)\ntests/unit/                     builder tests (regression evidence only)\ntests/acceptance/<ticket-id>/   written only by the Independent Test Designer (MR-3)\ngovernance/project/             the Gov OS's own overlay: path-map, roster, profiles, tool-registry,\n                                retrieval.yaml and rebuild.yaml (memory's query and store settings)\n.tickets/                       the WBS\ndocs/                           charter, contract, ADRs, spec, plan, register, lessons\nfixtures/evaluation/            memory's visible tuning set; never indexed (DEC-1066 (3))\ncli/govbridge/                  carried code; ported into src/gov/ by the tickets that reuse it, then removed\n```\n\nThe hidden sets of memory's measure live outside every worktree and are never indexed (DEC-1052 G-3, DEC-1055 (4),\nDEC-1066 (3)). With no guard, a set is protected by the transcript scan: it reads every transcript written between the\nset's writing and the end of its measure for the set's path and question ids, and a hit voids the measure; the memory\nreader runs with only the memory tool, and the gold sits outside the index and the clone (EMERGENCY-2 \u00a72.7, A-12;\nCAP-66; DEC-1214 E3). The guard rule that refused the hidden sets, DEC-1082 (3), DEC-1084 (1) and ACT-GUARD-SETS-1,\nis retired (DEC-1211).\n\n",
      "chunk_id": "1fe2501a7c99e8ae6bfbc19e",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "6c83b2c610915e3e5015f13b",
      "sha256": "f1ad4794f38a440983281b655278253677e1caeeed289466de2c3cefe11a3981",
      "path": "docs/emergency-2/briefs/LEAD-memaudit-adopted.md",
      "start_line": 21,
      "end_line": 32,
      "text": "  the owner's E3 in DEC-1214 (an adopted repository's CTO launches an independent question writer, a fresh session that\n  never sees the store's build, and runs the measure itself; the transcript scan voids a measure if the hidden half is\n  read; the sets live outside the clone and are never indexed); EMERGENCY-2 \u00a72.7, \u00a75.3.\n- The first run's findings F-1 and F-2: `.gov-runtime/scratch/orchestrator/drafts/fresh-80/P-FRESH-80-1.md` \u00a76 and\n  `JOB-20261116-17.md` beside it (the cycle the design means: writer round 1, preflight 1 recorded not stopping, checker,\n  writer round 2 and checker round 2 when asked, `void`, the final preflight, `measure`, `judge`).\n- W2-187's and W2-188's tickets (`.tickets/DAEO-0cd2.md`, `.tickets/DAEO-zlog.md`).\n\n**The CTO's decisions (do not reopen them):**\n1. **Per-repository configuration.** The domain table, the subsystem table, the question categories with their quotas,\n   and the control set with its baseline move out of the code into `governance/project/memory-audit.yaml` (a schema\n   under `template/governance/kernel/schemas/`). Gov OS's own file holds today's constants unchanged, so Gov OS's\n",
      "chunk_id": "6c83b2c610915e3e5015f13b",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "893ce0465aa42fb9ac0f5ee9",
      "sha256": "7b8fb6161ee628d2428d6d1b66dcfd1dcac5da58618de6572d7c90deb5e387d9",
      "path": "docs/changes/W2-204-evidence.md",
      "start_line": 203,
      "end_line": 226,
      "text": "## 4. What W2-188's adopt skill step 6 and the practice record should now say (for the CTO; not edited here)\n\n- **Before step 6's measure, a new sentence:** the repository states its own measure tables in\n  `governance/project/memory-audit.yaml` (the schema is `template/governance/kernel/schemas/memory-audit.schema.json`):\n  its governing domains by path, its subsystems by path or by a record key, its categories with quotas that sum to the\n  half size and include `nonexistent-id`, the paths no question may cite, and its control set (`none`, or a set\n  with `baseline: first` at a first measure). `gov memaudit check` must print `CONFIG ok`. Without the file every\n  step refuses (`MA-CONFIG-MISSING`); Gov OS's tables are never used for another repository.\n- **The steps are `gov memaudit <step>`** (`preflight`, `void`, `declare`, `measure`, `judge`, `figures`,\n  `brief`, `deliver`, `check`, `fresh`, `scan`), not `python3 -m gov.memaudit` (which still works).\n- **A fresh pair of halves is one command run until it ends:** `gov memaudit fresh --sets-root R --repo D --commit C\n  --tag YYYYMMDD`, on a snapshot it clones and builds; the repository's own store is not the one measured.\n- **The writer and the checker are the adopter's CTO's own fresh sessions**, each given the folder `gov memaudit\n  brief` writes and nothing else; their output enters the sets root only through `gov memaudit deliver`. The walls\n  launcher (`indep_launch.py`) and the approved briefs under `governance/project/indep-briefs/` are Gov OS's own\n  and are not part of what an adopter runs. \"Behind the walls\" in step 6 holds for Gov OS; for an adopter it reads\n  \"by independent fresh sessions, closed by the transcript scan\".\n- **The CTO never reads the sets root;** the transcript scan at the end of `fresh` (or `gov memaudit scan`) is the\n  check, and a finding voids the measure.\n- **The practice record** (`docs/research/W2-88-memory-practice.md`) should name the file as the place of a\n  repository's domains, categories and control, and say that the control's baseline of a repository without an earlier\n  figure is its first measure's own figure (`baseline: first`), not Gov OS's 34.\n- **The standing set's declaration** (`standing declare`) checks each question's category against the repository's\n  file too.\n",
      "chunk_id": "893ce0465aa42fb9ac0f5ee9",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DEC-1101",
      "sha256": "ffb20eb370b72c83b9e4b5c2706e70f7f1e9518ad848a72fde2dafb9c14432bd",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 1570,
      "end_line": 1573,
      "text": "### DEC-1101 \u2014 Memory quality audited periodically with fresh questions, for Gov OS and every adopted repository; the \"not found\" and \"may be incomplete\" answers counted weekly; independent writers, checkers and labellers launched automatically in walled folders, with fixed briefs the owner approves once\n- **Status:** ACCEPTED (owner, 2026-11-09, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-09)`); items (1) and (2) standing, active from now; **item (1)'s cadence changed by DEC-1125 (2): weekly while development is active, monthly once stable** \u00b7 **Under:** DEC-1098 (1), (4), DEC-1099 (1) Q5, (2), DEC-1100, DEC-1078, DEC-1070 (14), DEC-820, DEC-1052 \u00b7 **Source:** the owner's message (chat, 2026-11-09); its item 1 repeats DEC-1100 (recorded `1d49ca86`) \u00b7 **Changed by:** DEC-1179 (7) \u00b7 **Class:** kept (items changed: 85 % bar superseded \u00a75.3; hit@k reporting superseded \u00a75.2)\n- **Decision:**\n  - (1) **Standing: memory quality is audited periodically with new questions,** for Gov OS and for every adopted\n",
      "chunk_id": "692c0a5c94ec7440d9023a9e",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1,
      "entry": "DEC-1101",
      "status": "ACCEPTED",
      "changed_by": [],
      "in_force": true
    },
    {
      "id": "DEC-1101",
      "sha256": "239404d3bd9ecb4ff4d4ae9e89c30b6dbcbc266d6a2fd55672e77a2ebed7e4b6",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 1572,
      "end_line": 1582,
      "text": "- **Decision:**\n  - (1) **Standing: memory quality is audited periodically with new questions,** for Gov OS and for every adopted\n    repository (through W2-88). Each audit: an independent writer writes a fresh set, weighted toward what was added or\n    changed since the last audit plus a sample of older areas, cross-checked in at most two rounds; measured once\n    (retrieval figures, and agents right end to end with search again once) against the bar (85 %, target 95 %); an\n    independent auditor classifies the misses by kind; structural fixes only, brought to the owner and judged on the\n    earlier sets; the spent set joins a growing pool of earlier questions, re-run at every audit as a regression check;\n    the next audit's fresh set is the verdict on the fixes. Every two weeks while development is active, monthly once\n    stable. **Beside it:** agents' \"not found\" and \"may be incomplete\" answers counted from their returns and shown\n    weekly in the digest; a structural-pass notice of an unindexed path resolved within a day.\n  - (2) **Standing: automated independent sessions, a priority now.** Every question writer, checker and labeller is\n",
      "chunk_id": "6034e75bf22958f870786704",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1,
      "entry": "DEC-1101",
      "status": "ACCEPTED",
      "changed_by": [],
      "in_force": true
    },
    {
      "id": "DAEO-ma4q",
      "sha256": "42928df6d8de004e326e1c4ba2493b10a0bc2c48cc8dadaa315f3b5afeb70ba0",
      "path": ".tickets/DAEO-ma4q.md",
      "start_line": 75,
      "end_line": 88,
      "text": "## The CTO's decisions (not to be reopened)\n\n1. The domain table, subsystem table, categories with quotas and the control set with its baseline move into\n   `governance/project/memory-audit.yaml` (schema `template/governance/kernel/schemas/memory-audit.schema.json`). Gov OS's\n   file holds today's constants. No silent default. A subsystem by path or by record key.\n2. The steps an adopter runs are on the CLI under `gov memaudit` and one command runs a whole fresh 80 on a pinned snapshot\n   it builds. `python3 -m gov.memaudit` keeps working.\n3. The writer and checker are independent fresh sessions the adopter's CTO launches; the walls launcher stays Gov OS's.\n   The product gives the filled briefs and takes the delivered halves from the sets root.\n4. F-1 and F-2 are fixed here (the driver follows the cycle; the writer's result counts areas in the configuration's domain list).\n5. The reader's and graders' prompts, schemas, models are not touched.\n6. No real session, no measure, no rebuild of a shared store, nothing under `~/gov-os-eval`; the CTO runs the first real\n   fresh 80 after the land.\n\n",
      "chunk_id": "a6712fb2309e3e434974cdf8",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "39ede6ea7d60251f4bf53a8f",
      "sha256": "fb0a6ed283978088a87c711956f031dd7ce858c3dcad5ca1f85883142699e120",
      "path": "docs/contract/contract.yaml",
      "start_line": 3839,
      "end_line": 3871,
      "text": "  disposition:\n    class: KEPT\n  covers:\n  - id: CAP-65.a\n    item: Every brief carries the ticket's retrieval bundle, uncut (CAP-15)\n    source: EMERGENCY-2 \u00a75.4, \u00a75.6, \u00a75.7 (DEC-1211)\n    wave: W2\n    provider:\n    - W2-197\n  - id: CAP-65.b\n    item: Every template and every skill says memory first; the brief template no longer says \"No `gov retrieve` in the sandbox\"\n    source: EMERGENCY-2 \u00a75.4, \u00a75.6, \u00a75.7 (DEC-1211)\n    wave: W2\n    provider:\n    - W2-197\n  - id: CAP-65.c\n    item: 'A memory-use log records each retrieve: who asked, when, the question and what came back'\n    source: EMERGENCY-2 \u00a75.4, \u00a75.6, \u00a75.7 (DEC-1211)\n    wave: W2\n    provider:\n    - W2-197\n- id: CAP-66\n  title: The hidden-set scan\n  outcome: A hidden question set that an agent has read is detected, and its measure is void.\n  acceptance: The transcripts written between a set's writing and the end of its measure contain neither its path nor its\n    question ids, or the measure is void; the memory reader runs with only the memory tool and the gold sits outside the index.\n  wave: W2\n  provider:\n  - 'W2: the transcript scan (A-12)'\n  sources:\n  - EMERGENCY-2 \u00a72.7, A-12 (DEC-1211)\n  - DEC-1214 E3\n  scenarios:\n",
      "chunk_id": "39ede6ea7d60251f4bf53a8f",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "fae9ada4a8dfbcc50f095b6c",
      "sha256": "5700f2f7a5d4dbbd51ddc92d00d2d774ebbb647dd2f060e943aed6129e83bc05",
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/checker.md",
      "start_line": 50,
      "end_line": 54,
      "text": "| The evaluation's own documents: `fixtures/evaluation/**`, the memory-measure audit folder, `docs/audit/memory-*`, the W2-61 baseline, the memory practice record | they hold earlier questions | your tree leaves them out (the walls' `tree-exclude.txt`) |\n| Records of the standing measure that name questions it missed: `docs/research/W2-86-memory-measure.md`, `W2-87-memory-measure.md`, `W2-92-memory-measure.md`, `docs/research/D4B-memory-survey.md` and `D4B-memory-survey-package-draft.md` | they name tuning questions and misses | **this brief only**: your tree holds them; leave them unread, and never list one as an `also` place |\n| Anything about this audit: `governance/project/orchestration/packages/MEMORY-AUDIT-1*`, `governance/project/indep-walls/**`, any other brief | the audit stays blind to itself | **this brief only** for the first two; your tree leaves the briefs out |\n| Contents under a protected class: secrets and keys, the held-out material, any acceptance test, any hidden half | the guard protects them | you may see names only |\n\n",
      "chunk_id": "fae9ada4a8dfbcc50f095b6c",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "c323838b02ce5e15083e5b17",
      "sha256": "f9839103922fd4e7329ca1e77d9d335bee714f81d887d93ff8f013e6c3dad7fb",
      "path": "docs/changes/W2-204-evidence.md",
      "start_line": 179,
      "end_line": 193,
      "text": "6. gov memaudit fresh --sets-root $R --repo $D --commit $C --tag $T --runs-dir $RUNS \\\n       --allow-session <each writer's and checker's session id> [--projects ~/.claude/projects]\n       STEP <A> void ok ; STEP <A> preflight-final ok ; STEP <A> measure ok ; STEP <A> judge ok   (each half)\n       SCAN <V> clean ; SCAN <H> clean          # the transcript scan, from each half's first brief to now\n       FRESH VERDICT hidden right <r> of <n> (<p> %): passes|misses\n       FRESH BESIDE visible right <r> of <n>    # exit 0\n\n7. gov memaudit figures --sets-root $R --audit $H      # one JSON line of counts, for the record\n```\n\n- **What the CTO's fresh sessions do:** steps 2, 4 and 5's writer and checker, each a new session with only its\n  folder (`brief.md`, `seed.txt`, `input/`) and a clean checkout at `$C`. Everything else is a command.\n- `fresh` is run again after every delivery; it resumes at the step that waited and never repeats a recorded one.\n  `WAITING` is exit 5, `STOPPED <A> <step> [<code>]` exit 2 (to the owner: a half void at `void`, a final\n  pre-flight refused, a measure or judge stop), `MEASURE VOID <A>` exit 2 with no verdict line (a transcript in the\n",
      "chunk_id": "c323838b02ce5e15083e5b17",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "6de80af8cf179106042c865b",
      "sha256": "5700f2f7a5d4dbbd51ddc92d00d2d774ebbb647dd2f060e943aed6129e83bc05",
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/checker.md",
      "start_line": 50,
      "end_line": 54,
      "text": "| The evaluation's own documents: `fixtures/evaluation/**`, the memory-measure audit folder, `docs/audit/memory-*`, the W2-61 baseline, the memory practice record | they hold earlier questions | your tree leaves them out (the walls' `tree-exclude.txt`) |\n| Records of the standing measure that name questions it missed: `docs/research/W2-86-memory-measure.md`, `W2-87-memory-measure.md`, `W2-92-memory-measure.md`, `docs/research/D4B-memory-survey.md` and `D4B-memory-survey-package-draft.md` | they name tuning questions and misses | **this brief only**: your tree holds them; leave them unread, and never list one as an `also` place |\n| Anything about this audit: `governance/project/orchestration/packages/MEMORY-AUDIT-1*`, `governance/project/indep-walls/**`, any other brief | the audit stays blind to itself | **this brief only** for the first two; your tree leaves the briefs out |\n| Contents under a protected class: secrets and keys, the held-out material, any acceptance test, any hidden half | the guard protects them | you may see names only |\n\n",
      "chunk_id": "6de80af8cf179106042c865b",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DEC-1101",
      "sha256": "06d7ec7fc1d07d9a4a24e19ec3c3fe7097c699a0afb54c4b6b492d65397e99bf",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 1581,
      "end_line": 1590,
      "text": "    weekly in the digest; a structural-pass notice of an unindexed path resolved within a day.\n  - (2) **Standing: automated independent sessions, a priority now.** Every question writer, checker and labeller is\n    launched automatically, without the owner opening sessions: headless sessions in their own walled folders. From now\n    for the periodic audits, the sandbox experiment's labellers (DEC-1099 (1) Q5) and the sets W2-88 needs for\n    EXAMIN's copy. Independence: a fixed brief per job that the owner approves once, hashed, which the CTO may not\n    change without the owner's approval; the writer chooses its content by rule (what changed since the last audit,\n    from git, plus a random sample of older areas from a seed recorded before writing), not by the CTO; memory's own\n    search, run outputs, the CTO's scratch and the other sessions' folders denied to them by their settings, the guard,\n    and the sandbox once proven; only counts reach the CTO.\n  - (3) **The order:** first what must land in the path map, the guard and the folders' settings, as one ACT for the\n",
      "chunk_id": "47e0e1e6e321112130b6207c",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2,
      "entry": "DEC-1101",
      "status": "ACCEPTED",
      "changed_by": [],
      "in_force": true
    },
    {
      "id": "9425c7b642f3198921d2b6a8",
      "sha256": "abde86593af6dab72d70ffc5ae4bae0fd92d75288206cc9d9f090ecbb7e2dd5f",
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/checker.md",
      "start_line": 43,
      "end_line": 50,
      "text": "## 4. What you must never read\nYour tree may hold some of these. You leave them unread, and the last column says what stops you.\n\n| What | Why | What enforces it |\n|---|---|---|\n| Memory's own search and anything it produced: `gov retrieve`, `gov context`, a bundle, a ranked list, a measure record, a store, any run folder, the CTO's scratch | you judge the question, not its score | no shell; the wall's settings deny them; the wall hook refuses every path outside your folder and tree; none is in your tree |\n| Any earlier question set, notes or figures; the writer's walled folder | independence from the writer | they live in the sets root, behind the wall hook |\n| The evaluation's own documents: `fixtures/evaluation/**`, the memory-measure audit folder, `docs/audit/memory-*`, the W2-61 baseline, the memory practice record | they hold earlier questions | your tree leaves them out (the walls' `tree-exclude.txt`) |\n",
      "chunk_id": "9425c7b642f3198921d2b6a8",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "d6f80dbfba802882e9e2784b",
      "sha256": "e412a46411b925fdaf6ec417850b7df6eca87e918b6854f0986c3b2c789f7e05",
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/auditor.md",
      "start_line": 54,
      "end_line": 58,
      "text": "| The evaluation's own documents: `fixtures/evaluation/**`, the memory-measure audit folder, `docs/audit/memory-*`, the W2-61 baseline, the memory practice record | they hold earlier questions | your tree leaves them out (the walls' `tree-exclude.txt`) |\n| Records of the standing measure that name questions it missed: `docs/research/W2-86-memory-measure.md`, `W2-87-memory-measure.md`, `W2-92-memory-measure.md`, `docs/research/D4B-memory-survey.md` and `D4B-memory-survey-package-draft.md` | they name tuning questions and misses | **this brief only**: your tree holds them |\n| Anything about this audit: `governance/project/orchestration/packages/MEMORY-AUDIT-1*`, `governance/project/indep-walls/**`, any other brief | the audit stays blind to itself | **this brief only** for the first two; your tree leaves the briefs out |\n| Contents under a protected class: secrets and keys, the held-out material, any acceptance test, any hidden half | the guard protects them | you may see names only |\n\n",
      "chunk_id": "d6f80dbfba802882e9e2784b",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "e12bd64afd6ea9759abc54d3",
      "sha256": "abde86593af6dab72d70ffc5ae4bae0fd92d75288206cc9d9f090ecbb7e2dd5f",
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/checker.md",
      "start_line": 43,
      "end_line": 50,
      "text": "## 4. What you must never read\nYour tree may hold some of these. You leave them unread, and the last column says what stops you.\n\n| What | Why | What enforces it |\n|---|---|---|\n| Memory's own search and anything it produced: `gov retrieve`, `gov context`, a bundle, a ranked list, a measure record, a store, any run folder, the CTO's scratch | you judge the question, not its score | no shell; the wall's settings deny them; the wall hook refuses every path outside your folder and tree; none is in your tree |\n| Any earlier question set, notes or figures; the writer's walled folder | independence from the writer | they live in the sets root, behind the wall hook |\n| The evaluation's own documents: `fixtures/evaluation/**`, the memory-measure audit folder, `docs/audit/memory-*`, the W2-61 baseline, the memory practice record | they hold earlier questions | your tree leaves them out (the walls' `tree-exclude.txt`) |\n",
      "chunk_id": "e12bd64afd6ea9759abc54d3",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "d1634e013f1867dfc6b1a53c",
      "sha256": "5700f2f7a5d4dbbd51ddc92d00d2d774ebbb647dd2f060e943aed6129e83bc05",
      "path": "governance/project/indep-briefs/memory-audit/checker.md",
      "start_line": 50,
      "end_line": 54,
      "text": "| The evaluation's own documents: `fixtures/evaluation/**`, the memory-measure audit folder, `docs/audit/memory-*`, the W2-61 baseline, the memory practice record | they hold earlier questions | your tree leaves them out (the walls' `tree-exclude.txt`) |\n| Records of the standing measure that name questions it missed: `docs/research/W2-86-memory-measure.md`, `W2-87-memory-measure.md`, `W2-92-memory-measure.md`, `docs/research/D4B-memory-survey.md` and `D4B-memory-survey-package-draft.md` | they name tuning questions and misses | **this brief only**: your tree holds them; leave them unread, and never list one as an `also` place |\n| Anything about this audit: `governance/project/orchestration/packages/MEMORY-AUDIT-1*`, `governance/project/indep-walls/**`, any other brief | the audit stays blind to itself | **this brief only** for the first two; your tree leaves the briefs out |\n| Contents under a protected class: secrets and keys, the held-out material, any acceptance test, any hidden half | the guard protects them | you may see names only |\n\n",
      "chunk_id": "d1634e013f1867dfc6b1a53c",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "eb0cdcaa370761b15fb013c9",
      "sha256": "0b23d5922af1409fb2a32f1abdd67867b4a18f12db73f801980ae5dcff0bdd4b",
      "path": "docs/plan/wave-2/w2-81-proving-run/record.md",
      "start_line": 54,
      "end_line": 57,
      "text": "- **Targets and command:** `gov memaudit scan --set ~/gov-os-eval/fixtures/evaluation/adoption-proving-ground/hidden --since 2026-11-20T14:20:00Z --id <repository>-h01 ... <repository>-h30 (180 ids: the ids the hidden half's form gives, `<repository>-h<nn>`, none read from it) --projects <the scratch root>` printed `no transcript in the window names the set: 29 transcripts read, 180 ids`.\n- **Also grepped in the same 29 transcripts:** `gov-os-eval`, `adoption-proving-ground`, `W2-81-manifests`, `report.json`, `/hidden`, `e2e/`: 0 files each; `Dynamic-Agentic-Engineering-OS`: 1 file (the kit's `.copier-answers.yml` text, `_src_path`); no transcript names another repository's path.\n- **Not scanned, by construction:** the reader and grader sessions (121 questions, 242 sessions) run `claude -p --safe-mode --tools \"\" --no-session-persistence` (`gov.memaudit.claude.argv_of`): no tools, so none could read a file, and none writes a transcript.\n- **The tool's own defect (EXAMIN's F-033, reported to the CTO by the EXAMIN session):** without `--id`, `gov memaudit scan` takes the set's file stems as ids, here the six repository names, and would match every transcript; I passed explicit ids.\n",
      "chunk_id": "eb0cdcaa370761b15fb013c9",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "31ff0aac37b589b698b992d3",
      "sha256": "abde86593af6dab72d70ffc5ae4bae0fd92d75288206cc9d9f090ecbb7e2dd5f",
      "path": "governance/project/indep-briefs/memory-audit/checker.md",
      "start_line": 43,
      "end_line": 50,
      "text": "## 4. What you must never read\nYour tree may hold some of these. You leave them unread, and the last column says what stops you.\n\n| What | Why | What enforces it |\n|---|---|---|\n| Memory's own search and anything it produced: `gov retrieve`, `gov context`, a bundle, a ranked list, a measure record, a store, any run folder, the CTO's scratch | you judge the question, not its score | no shell; the wall's settings deny them; the wall hook refuses every path outside your folder and tree; none is in your tree |\n| Any earlier question set, notes or figures; the writer's walled folder | independence from the writer | they live in the sets root, behind the wall hook |\n| The evaluation's own documents: `fixtures/evaluation/**`, the memory-measure audit folder, `docs/audit/memory-*`, the W2-61 baseline, the memory practice record | they hold earlier questions | your tree leaves them out (the walls' `tree-exclude.txt`) |\n",
      "chunk_id": "31ff0aac37b589b698b992d3",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "74dafdbd8cd244ef9013fed8",
      "sha256": "e412a46411b925fdaf6ec417850b7df6eca87e918b6854f0986c3b2c789f7e05",
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/auditor.md",
      "start_line": 54,
      "end_line": 58,
      "text": "| The evaluation's own documents: `fixtures/evaluation/**`, the memory-measure audit folder, `docs/audit/memory-*`, the W2-61 baseline, the memory practice record | they hold earlier questions | your tree leaves them out (the walls' `tree-exclude.txt`) |\n| Records of the standing measure that name questions it missed: `docs/research/W2-86-memory-measure.md`, `W2-87-memory-measure.md`, `W2-92-memory-measure.md`, `docs/research/D4B-memory-survey.md` and `D4B-memory-survey-package-draft.md` | they name tuning questions and misses | **this brief only**: your tree holds them |\n| Anything about this audit: `governance/project/orchestration/packages/MEMORY-AUDIT-1*`, `governance/project/indep-walls/**`, any other brief | the audit stays blind to itself | **this brief only** for the first two; your tree leaves the briefs out |\n| Contents under a protected class: secrets and keys, the held-out material, any acceptance test, any hidden half | the guard protects them | you may see names only |\n\n",
      "chunk_id": "74dafdbd8cd244ef9013fed8",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "CAP-66",
      "sha256": "975e302800bdc944e21247d288109f10d770cb11f7467c7517cdaeea6b7a6ddd",
      "path": "docs/contract/capabilities/CAP-66.md",
      "start_line": 11,
      "end_line": 19,
      "text": "# CAP-66: The hidden-set scan\n\nGenerated from `docs/contract/contract.yaml` (Contract v5, version 5.1), which is the authority; this record exists so that the id resolves (DEC-614).\n\n- **Outcome:** A hidden question set that an agent has read is detected, and its measure is void.\n- **Acceptance:** The transcripts written between a set's writing and the end of its measure contain neither its path nor its question ids, or the measure is void; the memory reader runs with only the memory tool and the gold sits outside the index.\n- **Wave:** W2\n- **Disposition:** KEPT\n- **Covers:** CAP-66.a, CAP-66.b\n",
      "chunk_id": "011ab7f45980359a697f7cc9",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "f8b0997c719cbf085d895676",
      "sha256": "263051b119b8d0f70d20a1bfbf81600c1195fd7a119fe9755d890eb3db25bded",
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "start_line": 56,
      "end_line": 63,
      "text": "| The evaluation's own documents: `fixtures/evaluation/**`, the memory-measure audit folder, `docs/audit/memory-*`, the W2-61 baseline, the memory practice record | they hold earlier questions | your tree leaves them out (the walls' `tree-exclude.txt`) |\n| Records of the standing measure that name questions it missed: `docs/research/W2-86-memory-measure.md`, `W2-87-memory-measure.md`, `W2-92-memory-measure.md`, `docs/research/D4B-memory-survey.md` and `D4B-memory-survey-package-draft.md` | they name tuning questions and misses | **this brief only**: your tree holds them |\n| Anything about this audit: `governance/project/orchestration/packages/MEMORY-AUDIT-1*`, `governance/project/indep-walls/**`, any other brief | the audit stays blind to itself | **this brief only** for the first two; your tree leaves the briefs out |\n| Contents under a protected class: secrets and keys, the held-out material, any acceptance test, any hidden half | the guard protects them | you may see names only |\n\nIf a file you opened turns out to be one of these, stop reading it and do not use what you saw. Name its path class\n(never its content) in `out/conflicts.md`, even if you go on and finish the set.\n\n",
      "chunk_id": "f8b0997c719cbf085d895676",
      "routes": [
        "lexical",
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
    "duplicates": 31,
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
      "chunk_id": "1fe2501a7c99e8ae6bfbc19e",
      "parent_id": "fad0aeeee295c54ab4867588",
      "path": "docs/adr/ADR-0002-architecture-and-stack.md",
      "start_line": 262,
      "end_line": 302
    },
    {
      "chunk_id": "893ce0465aa42fb9ac0f5ee9",
      "parent_id": "87a4fcfc64231d52f53ae38b",
      "path": "docs/changes/W2-204-evidence.md",
      "start_line": 203,
      "end_line": 226
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "path": "governance/project/indep-briefs/memory-audit/auditor.md",
      "chunk_id": "7a1236c6e2d00b3783b59d48",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/CONTRACT_v5.md",
      "chunk_id": "3c67d2c1e4c91124a4ec8a51",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/record.md",
      "chunk_id": "06c6f77c6f7d7c27721a25e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/record.md",
      "chunk_id": "ca45571f9b459a32a11a1e74",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-204-evidence.md",
      "chunk_id": "fedc64cf47718cde60dc1c64",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-204-evidence.md",
      "chunk_id": "e93dffb98960557a77308669",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "6be3be29a9ecd9e29c1e21ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/writer.md",
      "chunk_id": "ccae5193ee7e40cb9aaccbac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-scan-fix.md",
      "chunk_id": "3cf8a339e928d020576e1f62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "ea978fd467814dd8100690d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "1b323c1698e0110486ff2a0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "d08c398bb7765becfc9e9732",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-scan-fix.md",
      "chunk_id": "4c5bfa04b29459ab69940661",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/command.py",
      "chunk_id": "bbebb9fa433f9c0e4f31f588",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-66.a.md",
      "chunk_id": "1c880e00d338928ecc2402cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-scan-fix.md",
      "chunk_id": "a8ed7053285fb56f10ed8499",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-scan-fix.md",
      "chunk_id": "d44d1bab62efbda3e851c232",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "1c55e21464e473dd8cab9200",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-49.a.md",
      "chunk_id": "833e15ba0699648d6e353fa7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-49.a.md",
      "chunk_id": "7f1661d3fc4759db876cb06f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "e6e9b3ba007f957716b7290a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/command.py",
      "chunk_id": "b2fb303e366282e551c658cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-61vm.md",
      "chunk_id": "151ebd62d6f7fcaa33b5745d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "d67a30cf3894497455c42e6e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-66.a.md",
      "chunk_id": "e374095a067d941bf0bbff54",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-o5wi.md",
      "chunk_id": "4e31d9db50eb67f251475a62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "32c5cd5d94e9175c86040ec7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/path-map.yaml",
      "chunk_id": "b7f4c3c64f97e8e35d24b66d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/auditor.md",
      "chunk_id": "43448fd2d961a56327e5f033",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-49.c.md",
      "chunk_id": "3e210a0f4fc200897b68df1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/auditor.md",
      "chunk_id": "e4fd780f5a8146f7ca89c8ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "b0eedfaacdfbdac6307c5404",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-scan-fix.md",
      "chunk_id": "d7d055e9ca74df932ce59da8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/auditor.md",
      "chunk_id": "463d508d0ceb02cef876cadc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "e7f451aa849ad99c1d27e2af",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1.md",
      "chunk_id": "c4fa50a2149024fd7df77892",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "f0dda0eaf6543b22139c5d2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "0eb66a520e0eaf57562291f7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-61vm.md",
      "chunk_id": "32c22a9ef3b73352d30b107c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md",
      "chunk_id": "1e1448fdf8984f2453ec0436",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/command.py",
      "chunk_id": "e7b88dec8be03b7695093108",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "89148e05b97f18d532f1688d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "bc41d6c9e3d7f040fffdc90d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-adopted.md",
      "chunk_id": "f3ef3503397017b85e73305b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/briefs/checker.py",
      "chunk_id": "8e4155b0adef43f64a72ff5b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-W2-H063-1.md",
      "chunk_id": "2f705a58e05d82f41e7c4a42",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/briefs/writer.py",
      "chunk_id": "1aeb4f5332e9660856eeb763",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/writer.md",
      "chunk_id": "762536e5374e9e7df3929090",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "325a78af15812cb1e07d21c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/OWNER-DECISIONS-2026-11-18.md",
      "chunk_id": "bcbf9860a224c627a6b3818d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p8tv.md",
      "chunk_id": "5d24590ddb3765070c6f39c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-SPEC-MAP.md",
      "chunk_id": "3dfad75b7f3d0ec44f3c098e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md",
      "chunk_id": "ea69ee9294fc2aca5e30b9e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-61vm.md",
      "chunk_id": "86b6a25e22a78880aa04bb44",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/briefs/writer.py",
      "chunk_id": "f22fb4f88d109cb0c9994c47",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-o5wi.md",
      "chunk_id": "0294d71446004a8097dbcc16",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-204-evidence.md",
      "chunk_id": "1db6a1c38f72df639d934806",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/writer.md",
      "chunk_id": "1ebf002fd8274c3b8804d59f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/checker.md",
      "chunk_id": "fcd496c8fa8feb8f835db86f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-P1.md",
      "chunk_id": "71a49051cceed94bf44ca0a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/checker.md",
      "chunk_id": "1fbd5c5022b2c25c8ecad1bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "5f9f8e91e11d3c417fc92b71",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-FRESH-80-1.md",
      "chunk_id": "d805baee7476460d86a328e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-61vm.md",
      "chunk_id": "6f5d324ce849f2016ebf676e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-adopted.md",
      "chunk_id": "0751767c169390217e45b94b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1.md",
      "chunk_id": "63331df7e366791e6f1edd30",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/auditor.md",
      "chunk_id": "03d2796b4a550e4c6db43f72",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-adopted.md",
      "chunk_id": "cdad874a35b990fa808c1201",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/adopt/memory_sets.py",
      "chunk_id": "6fe497d78a3f0893eb3efeff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "3b2d49091b0c5466575ab2a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-87-memory-measure.md",
      "chunk_id": "2f3ae08ce336462fc1b4a8b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p8tv.md",
      "chunk_id": "205606124c3cdab94beb1c39",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-61vm.md",
      "chunk_id": "864baff15d69abe4bca5fe1c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/deliver.py",
      "chunk_id": "779f24863468368d10096c1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-AUDIT.md",
      "chunk_id": "c798d24de1c44d47b323a180",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/fresh.py",
      "chunk_id": "e67be68dd5539fd068038e66",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-88-memory-practice.md",
      "chunk_id": "4fdf2b7c98a446f80f7d49db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-o5wi.md",
      "chunk_id": "d01a632d4a9dce02a3f504ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/path-map.yaml",
      "chunk_id": "d21fcca1bc98d1740dd6d8ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "281c009d5a2a8e46828c4c82",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/path-map.yaml",
      "chunk_id": "da2d14aae1dbc596561761f7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-adopted.md",
      "chunk_id": "7d172f182c22517ca7981749",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/auditor.md",
      "chunk_id": "29fef277e1faaf6fc3e3c29d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "86ad7690c8e4e28b9765fff0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/auditor.md",
      "chunk_id": "0126b83bdde39d8d033cf1f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1e2.md",
      "chunk_id": "116171c148f07a5e1c595053",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/writer.md",
      "chunk_id": "991c891114493f708c46f63d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/memory-measure-new-visible.md",
      "chunk_id": "90c504de7dcc403f7ec7fe81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/README.md",
      "chunk_id": "50f5c2d438b5be8a7d7a00e0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/README.md",
      "chunk_id": "0160d3f9f229fca50484cef2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/memory-recall-diagnosis-hidden.md",
      "chunk_id": "c4823518d4712ca7fec8d08c",
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
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5996
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLW1hNHEubWQiLDc1LDg4LCJhNjcxMmZiMjMwOWUzZTQzNDk3NGNkZjgiXSxbImRvY3MvREVDSVNJT05fUkVHSVNURVIubWQiLDE1NzAsMTU3MywiNjkyYzBhNWM5NGVjNzQ0MGQ5MDIzYTllIl0sWyJkb2NzL0RFQ0lTSU9OX1JFR0lTVEVSLm1kIiwxNTcyLDE1ODIsIjYwMzRlNzViZjIyOTU4Zjg3MDc4NjcwNCJdLFsiZG9jcy9ERUNJU0lPTl9SRUdJU1RFUi5tZCIsMTU4MSwxNTkwLCI0N2UwZTFlNmUzMjExMTIxMzBiNjIwN2MiXSxbImRvY3MvY2hhbmdlcy9XMi0yMDQtZXZpZGVuY2UubWQiLDE3OSwxOTMsImMzMjM4MzhiMDJjZTVlMTUwODNlNWIxNyJdLFsiZG9jcy9jb250cmFjdC9jYXBhYmlsaXRpZXMvQ0FQLTY2Lm1kIiwxMSwxOSwiMDExYWI3ZjQ1OTgwMzU5YTY5N2Y3Y2M5Il0sWyJkb2NzL2NvbnRyYWN0L2NvbnRyYWN0LnlhbWwiLDM4MzksMzg3MSwiMzllZGU2ZWE3ZDYwMjUxZjRiZjUzYThmIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2JyaWVmcy9MRUFELW1lbWF1ZGl0LWFkb3B0ZWQubWQiLDIxLDMyLCI2YzgzYjJjNjEwOTE1ZTNlNTAxNWYxM2IiXSxbImRvY3MvcGxhbi93YXZlLTIvdzItODEtcHJvdmluZy1ydW4vcmVjb3JkLm1kIiw1NCw1NywiZWIwY2RjYWEzNzA3NjFiMTVmYjAxM2M5Il0sWyJnb3Zlcm5hbmNlL3Byb2plY3QvaW5kZXAtYnJpZWZzL21lbW9yeS1hdWRpdC9jaGVja2VyLm1kIiw0Myw1MCwiMzFmZjBhYWMzN2I1ODliNjk4Yjk5MmQzIl0sWyJnb3Zlcm5hbmNlL3Byb2plY3QvaW5kZXAtYnJpZWZzL21lbW9yeS1hdWRpdC9jaGVja2VyLm1kIiw1MCw1NCwiZDE2MzRlMDEzZjE4NjdkZmM2YjFhNTNjIl0sWyJnb3Zlcm5hbmNlL3Byb2plY3Qvb3JjaGVzdHJhdGlvbi9wYWNrYWdlcy9NRU1PUlktQVVESVQtMS9icmllZnMvYXVkaXRvci5tZCIsNTQsNTgsIjc0ZGFmZGJkOGNkMjQ0ZWY5MDEzZmVkOCJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vcGFja2FnZXMvTUVNT1JZLUFVRElULTEvYnJpZWZzL2NoZWNrZXIubWQiLDQzLDUwLCI5NDI1YzdiNjQyZjMxOTg5MjFkMmI2YTgiXSxbImdvdmVybmFuY2UvcHJvamVjdC9vcmNoZXN0cmF0aW9uL3BhY2thZ2VzL01FTU9SWS1BVURJVC0xL2JyaWVmcy9jaGVja2VyLm1kIiw1MCw1NCwiNmRlODBhZjhjZjE3OTEwNjA0MmM4NjViIl0sWyJzcmMvZ292L19zaGlwcGVkL2dvdmVybmFuY2UvcHJvamVjdC9vcmNoZXN0cmF0aW9uL3BhY2thZ2VzL01FTU9SWS1BVURJVC0xL2JyaWVmcy9hdWRpdG9yLm1kIiw1NCw1OCwiZDZmODBkYmZiYTgwMjg4MmU5ZTI3ODRiIl0sWyJzcmMvZ292L19zaGlwcGVkL2dvdmVybmFuY2UvcHJvamVjdC9vcmNoZXN0cmF0aW9uL3BhY2thZ2VzL01FTU9SWS1BVURJVC0xL2JyaWVmcy9jaGVja2VyLm1kIiw0Myw1MCwiZTEyYmQ2NGFmZDZlYTk3NTlhYmM1NGQzIl0sWyJzcmMvZ292L19zaGlwcGVkL2dvdmVybmFuY2UvcHJvamVjdC9vcmNoZXN0cmF0aW9uL3BhY2thZ2VzL01FTU9SWS1BVURJVC0xL2JyaWVmcy9jaGVja2VyLm1kIiw1MCw1NCwiZmFlOWFkYTRhOGRmYmNjNTBmMDk1YjZjIl0sWyJzcmMvZ292L19zaGlwcGVkL2dvdmVybmFuY2UvcHJvamVjdC9vcmNoZXN0cmF0aW9uL3BhY2thZ2VzL01FTU9SWS1BVURJVC0xL2JyaWVmcy93cml0ZXIubWQiLDU2LDYzLCJmOGIwOTk3YzcxOWNiZjA4NWQ4OTU2NzYiXV0sImYiOiIvaG9tZS91c2Fpbi9nb3Ytb3Mtd29ya3RyZWVzL1cyLTAwLXN0b3JlLWEiLCJpIjpbXSwibyI6MjAsInAiOnsiYiI6InNlcnZpY2UiLCJkIjoiY3VkYTowIiwiaCI6ImU1YjIwMmYwZmMwYmE2MzEiLCJvIjpbMSwxMCwyNSwyNiw1LDMxLDI5LDgsMTYsMTUsNiwyNCwzNSwyMywxMSwzLDIyLDM4LDcsMTgsMzksMCwxOSwzMCwyMCwxNCwxNywyMSwyLDksMjgsMTMsMTIsMzcsMzMsNCwzNCwyNywzMiwzNl19LCJxIjoiSG93IGFyZSB0aGUgaGlkZGVuIHF1ZXN0aW9uIHNldHMgb2YgdGhlIG1lbW9yeSBtZWFzdXJlIHByb3RlY3RlZCAoc2V0cyByb290LCB0cmFuc2NyaXB0IHNjYW4sIHdoaWNoIHNlc3Npb25zIG1heSByZWFkIHRoZW0sIGhvdyBnb3YgbWVtYXVkaXQgbGF1bmNoZXMgaXRzIHdyaXRlcnMsIGNoZWNrZXJzIGFuZCByZWFkZXIpPyBEZWNpc2lvbnMsIGhpc3RvcnkgYW5kIHBsYW5zLiIsInIiOjAsInMiOiI4M2JjMDUwYWE4OGJiMmU2ZjUwZTdjYzI5NzhjZTg0MDMwMTZmMzY0IiwidCI6bnVsbCwieCI6WyI4N2E0ZmNmYzY0MjMxZDUyZjUzYWUzOGIiLCJmYWQwYWVlZWUyOTVjNTRhYjQ4Njc1ODgiXX0=",
  "routing": {
    "code": [],
    "named": [],
    "phrasings": [
      "How are the hidden question sets of the memory measure protected (sets root, transcript scan, which sessions may read them, how gov memaudit launches its writers, checkers and reader)? Decisions, history and plans.",
      "hidden question sets memory measure protected sets root transcript scan sessions read gov memaudit launches writers checkers reader Decisions history plans."
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
```
