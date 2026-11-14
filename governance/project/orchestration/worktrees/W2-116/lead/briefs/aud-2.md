# Brief: independent auditor, W2-116 (DAEO-f58b) pass 2c: a narrow independent check of a test revision

You are a fresh independent auditor, read-only. You write nothing in any repository folder; work only under your
session's own `TMPDIR`. Your last message is the probe record, whole; the lead commits it under
`docs/probes/DAEO-f58b/`.

## What to check, and only this
The independent test designer's change of pass 2c on `w2/W2-116`, in /home/usain/gov-os-worktrees/W2-116, head
**037cf8a4fff0cada2b64fb8b7751b7c6d5dcd4ed** (the merge of w2/W2-116-tests). The change is
`git diff 9e9428942df546bb9d19f2b271b63b4fd0644bf4 6666cec2cbc9` (9e9428942 is the merge of w2/integrate pass 2c
started from), seven commits, one per file:
- 8893ad5b0 `tests/acceptance/W2-131/test_w2_131_unchanged.py`
- d92b61bf5 `tests/acceptance/W2-133/test_w2_133_unchanged.py`
- 67aa2d12b `tests/acceptance/W2-135/test_w2_135_unchanged.py`
- 3ad7ce713 `tests/unit/retrieval/test_w2_131_register_ids.py`
- 56930ce1a `tests/unit/retrieval/test_w2_133_gap_label.py`
- cd2324e06 `tests/unit/retrieval/test_w2_135_item_cap.py`
- 6666cec2c `tests/unit/status/test_status.py`

**Why the change exists (the order the lead was given, DEC-1156 (7)):** two decided behaviours of W2-116 turn 17
cases of other tickets red; the CTO routes them as revisions of decided behaviour, to a test designer, with
`Rewrite-Reason: DEC-1156 (7), R2-F3's token key / S2's status part (W2-116 pass 2c)`, one commit per file, no case
losing its point:
1. **R2-F3's `f` token key** (the CTO's Q3 (a) under DEC-1157 (12)): a continuation token now carries `f`, the store
   folder (half) it was made on, beside W2-138's `s` (the store's commit) (`src/gov/retrieval/retrieve.py` ~195-225).
   In the six token files, "the helper that drops the `s` key before comparing continuation tokens from two folders
   drops `f` as well. Nothing else changes."
2. **S2's `integration_store` status part** (in the ticket): `gov status` gains a part `integration_store` after
   `reranker` (`src/gov/status/command.py` 195-209); unconfigured, it is `{"read": false, ...}` and `not_read` names
   it. In `tests/unit/status/test_status.py`: "the exact `PARTS` tuple gains `integration_store` in the position the
   code gives it, and `not_read` stays asserted as the code's behaviour now is. The case still pins the whole tuple."

**Judge, for each of the seven files:**
- Does each case keep its point (what it guards for its own ticket: W2-131 register ids, W2-133 gap labels, W2-135
  item cap / cut lines, W2-138's `s` premise where it is read, the status case's "every not-read place named")?
  Would it still fail on the plausible wrong change it was written against? Is any assertion loosened (a subset, an
  `in`, a filter, a dropped key beyond `f`)?
- Did nothing but `f` and `integration_store` change (comments and docstrings naming them aside)?
- Is dropping `f` limited to comparisons of tokens from two folders (before/after stores), so that no case that should
  see `f` loses it?

**Probe, do not only read:** run the seven files, before (at 9e9428942, from a `git worktree add --detach` under your
`TMPDIR`, or `git show <rev>:<path>` into your `TMPDIR`) and after (at the head), and say which cases were red before
and green after. If you can, try a plausible wrong change against a revised case (e.g. in a copy under your `TMPDIR`,
drop a register id's fix or a not-read place) and see that the case still fails.

How to run pytest (every run):
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/empty-home PYTHONPATH=<the checkout's>/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
`/tmp` is read-only in the sandbox: keep the sandbox's own `TMPDIR` (outside the repository). A resource gate's
refusal is a wait (DEC-1146); the `heavy-slot-waits.jsonl: Read-only file system` line is harmless. Never open the
evaluation sets' root or any hidden or memory-verdict folder. No `gov retrieve` or `gov context` in the sandbox: search
with Read and Grep, and once more in other words if the first does not answer (DEC-1065). Refused twice for the same
call by the guard, the sandbox or a hook: stop and say so; never work around it (DEC-1142 (9)).

Out of scope (rows if you see them, never failing findings): W2-116's own implementation and its acceptance suite
(reviewed in pass 2b, PASS); F-1 (a store named stale after an unchanged scheduled refresh, already a row); other
tickets' cases not in the seven files.

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.

## The ticket's context (gov context DAEO-f58b --role independent-auditor)
{
  "ticket": "DAEO-f58b",
  "ticket_text": "---\nid: DAEO-f58b\nstatus: in_progress\ndeps: [DAEO-lrre]\nlinks: []\ncreated: 2026-10-31T23:52:57Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-116\ntags: [wave-2, implementation, memory, standard, smart-work]\nwbs_id: W2-116\ntitle: 'The designers'' store in the product: a double-buffered store of the integration branch, refreshed after the nightly and once more a day, that a test designer''s retrieval reads (SMART-WORK-1)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-lrre\nallowed_paths:\n- src/gov/status/**  # S2: the store's head and age in gov status (CTO, DEC-1157 (12))\n- docs/probes/DAEO-f58b/**  # the probe record\n- src/gov/rebuild/integration.py\n- src/gov/rebuild/command.py\n- src/gov/launch/store.py\n- src/gov/launch/launcher.py\n- src/gov/retrieve/command.py\n- docs/changes/W2-116-evidence.md\n- tests/unit/rebuild/test_w2_116*\n- tests/unit/launch/test_w2_116*\n- governance/project/rebuild.yaml  # S2, P-W2-116-S2-INTERFACE Q2 (b) (CTO, DEC-1157 (12)): this repository's integration_refresh line lands with the code that reads it\n- src/gov/retrieval/retrieve.py  # R2-F3, Q3 (a) (CTO): the continuation token carries the half it was made on (about 20 lines)\n- tests/unit/status/test_w2_116*\n- tests/unit/retrieval/test_w2_116*\n- tests/acceptance/W2-131/test_w2_131_unchanged.py  # R2-F3's `f` token key (Q3 (a)): the helper drops `f` beside `s` when it compares tokens from two folders; a test designer, Rewrite-Reason (CTO, DEC-1156 (7))\n- tests/acceptance/W2-133/test_w2_133_unchanged.py  # the same\n- tests/acceptance/W2-135/test_w2_135_unchanged.py  # the same\n- tests/unit/retrieval/test_w2_131_register_ids.py  # the same\n- tests/unit/retrieval/test_w2_133_gap_label.py  # the same\n- tests/unit/retrieval/test_w2_135_item_cap.py  # the same\n- tests/unit/status/test_status.py  # S2's new `integration_store` part in gov status's PARTS (the same route)\nkpis:\n  success:\n  - '`gov rebuild --integration <branch>` keeps a store of that branch''s head in two detached worktrees outside the project, building into the one not in use and switching a link to it only when the build succeeded; a search during a build is answered from the ready one [DEC-963, DEC-983, DEC-982] Verify: the success-1 cases in tests/acceptance/W2-116/test_w2_116_double_buffer.py (the build in a detached worktree behind the link, the two halves alternating, a search during a build and a killed build answered from the ready half) pass [Verify clause added, DEC-1157 (12)]'\n  - 'It is refreshed after the nightly''s verdict and at a set second time each day (both in the project''s configuration), and its status (head, age) is in `gov status` [DEC-966 item 3, DEC-983, DEC-982] Verify: pass 2''s cases: a planted configuration''s two refresh times are read and the refresh runs after the nightly''s verdict and at the second time; `gov status` names the integration store''s head and age, and a stale store is named; a missing or invalid time refuses by name [Verify clause added, DEC-1157 (12)]'\n  - '`gov launch independent-test-designer` points the session''s retrieval at it; a designer''s retrieval never reads a ticket worktree''s store [DEC-963, DEC-983, DEC-982] Verify: the success-3 cases in tests/acceptance/W2-116/test_w2_116_launch.py pass: each launched worker role''s plain search reads the integration store from a worktree with none, and the session keeps its role and ticket [Verify clause added, DEC-1157 (12)]'\n  - 'The store is also refreshed after every landing on the integration branch, and it is the warm base `gov rebuild --seed` (W2-122) reads; a seed taken from a store behind the integration head is named, and only what changed since is re-embedded [DEC-1014 items 4 and 6, SMART-WORK-5 D, DEC-1015 item 3] (folds W2-06 S1, S2) Verify: the success-4 cases in tests/acceptance/W2-116/test_w2_116_refresh.py pass: after a merge the refresh brings the store to the new head re-embedding only what changed, an unchanged head does nothing, `gov rebuild --seed` reads it and a seed behind the head is named [Verify clause added, DEC-1157 (12)]'\n  - 'A re-index never empties the semantic index; a model-less re-index reports the semantic facet unavailable instead [DEC-719]. [moved from W2-06 S5, DEC-1083] Verify: the success-5 cases in tests/acceptance/W2-116/test_w2_116_reindex.py pass: a model-less re-index of the integration store keeps its index and says the semantic facet is unavailable [Verify clause added, DEC-1157 (12)]'\n  - '`gov launch` points every worker session''s retrieval at the integration store (the `GOV_STORE` of a launched session), not only a designer''s; a designer''s retrieval never reads a ticket worktree''s store. Verify: a launcher unit test per worker role: the session environment names the integration store; a designer''s never names a worktree''s store [DEC-1087 (3), DEC-963] [added, the CTO''s note of 2026-11-06 in the body (S3 widened), DEC-1087 (3)]'\n  failure:\n  - 'A designer''s retrieval answered from a ticket worktree''s store. Verify: tests/acceptance/W2-116/test_w2_116_launch.py::test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store passes [Verify clause added, DEC-1157 (12)]'\n  - 'The link switched to a store whose build failed, or a search answered from a half-built store. Verify: the failure-2 cases in test_w2_116_double_buffer.py and test_w2_116_reindex.py pass: a search during a build and through the link while the other half rebuilds is answered from the ready half, never stale; a build killed half way leaves the link [Verify clause added, DEC-1157 (12)]'\n  - 'A re-index that fails leaves the previous index and reports the failure; it never leaves no index [W2-M088]. [moved from W2-06 F1, DEC-1083] Verify: the failure-3 cases in test_w2_116_double_buffer.py and test_w2_116_reindex.py pass: a killed build or a failed re-index leaves the previous index and reports the failure [Verify clause added, DEC-1157 (12)]'\nprofile: STANDARD\nsources:\n- DEC-1109\n- DEC-1112\n- DEC-983\n- DEC-982\n- DEC-963\n- DEC-966\n- DEC-1014\n- DEC-1015\n- DEC-1083\n- DEC-1087\n- DEC-719\n- DAEO-kia7\nest_loc: 150\nacceptance_tests:\n  path: tests/acceptance/W2-116/\n  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-963); a planted branch, a build killed half-way, a search during a build\ntrack: B\nlist_rows:\n- W2-M088\n---\n# W2-116 The designers' store in the product\n\nThe owner's SMART-WORK-1 decision 2 (DEC-983): the designers' store (DEC-963, DEC-966 item 3) becomes the product's, not only the CTO's `refresh_integration_store.sh` and `store_refresh_daily.sh`.\n\n- **Why:** a test designer retrieves only from the integration branch's store, so its retrieval never serves a ticket's implementation. W2-33's role files and W2-83b's playbooks will tell an adopted product's designers so; nothing in the product builds that store.\n- **This repository's own configuration:** the place (`~/gov-os-worktrees/W2-00-store`) and the two times a day; the CTO's scripts are retired once this lands.\n- **Order:** after W2-60b (the launcher's files) and W2-33 (the rule it serves); before EXAMIN's copy (W2-27).\n\n**DEC-1087 (3) placed here (CTO, 2026-11-06, delegated P3 on the scope):** the owner orders the refresh after every\nmerge into integrate built, tested and reviewed before re-pin window 4, so the window puts it live. The worktrees get\nthe integration store's path, so workers can search.\n- **S2's interface (pass 2b; P-W2-116-S2-INTERFACE Q1 (a), the CTO, DEC-1157 (12), 2026-11-13).** A product tick that\n  watches a configured verdict file; the nightly does not change.\n  - **Config** in `rebuild.yaml`: `integration_refresh: {branch, after_nightly: {verdict: <glob>, latest: \"HH:MM\"},\n    second: \"HH:MM\"}`.\n  - **Command:** `gov rebuild --integration <branch> --when-due`. It refreshes when a verdict file is newer than the\n    last scheduled refresh, when `latest` passes without one, or once `second` passes; otherwise it builds nothing and\n    says `not_due`.\n  - **Record:** each scheduled refresh writes `<link>.refresh.json`. Tests plant the clock with `GOV_NOW`.\n  - **Error:** a missing or invalid time refuses `REBUILD_CONFIG_INVALID`, naming the key.\n  - **`gov status`** gains an `integration_store` part: head, branch head, built time, age, `stale` and the stale\n    reason. **Stale:** the store's head is behind the branch, or it was built before the last time a refresh fell due.\n  - **This repository's values** (Q2 (b), in this ticket's paths): `branch: w2/integrate`, verdict glob\n    `.gov-runtime/scratch/orchestrator/log/nightly/*/run.txt`, `latest: \"10:00\"`, `second: \"18:00\"`.\n  - **Cron:** a line every 5 minutes, in window 4's ACT next to the hook (not this ticket).\n  - **R2-F3 (Q3 (a)):** the continuation token carries a mark of the half it was made on, checked when it is used\n    (`src/gov/retrieval/retrieve.py`).\n- **This pass builds S1, S3 (widened, below), S4 and S5, and the three failure lines.** S2's two daily times and\n  `gov status` stay for the next pass. Until then the CTO's `store_refresh_daily.sh` runs as the backstop (DEC-1087\n  (3)).\n- **S3 widened:** `gov launch` points every worker session's retrieval at the integration store, not only a\n  designer's. A designer's retrieval still never reads a ticket worktree's store. A worktree has no store of its own\n  today, so a worker's search answers `STORE_MISSING` (checked 2026-11-06).\n- **S4's trigger:** \"after every landing\" covers every merge into the integration branch, by the merge queue or by\n  hand. The product offers the refresh as a command run after the merge (`gov rebuild --integration <branch>`, idempotent\n  at an unchanged head). The hook that calls it after a hand merge is installed by the owner's operator in re-pin window\n  4's ACT (hooks are the operator's). The design is the engineer's, stated in its evidence record.\n- **The deps W2-60b (the session record) and W2-33 (the roles) are not needed** for this pass: it touches neither the\n  session record nor the role files. They stay in `deps:` for S2 and the role rule's text.\n- **The rebuild uses the code it runs under.** The store at window 4's head is built by window 4's code, so the pinned\n  code and the store always match. The engineer states how the double buffer keeps the ready half answering while the\n  other builds (F2).\n\n**TESTS-READY and the designer's points settled (CTO, 2026-11-06, delegated P3):**\n- **The tests:** `tests/acceptance/W2-116/` on `w2/W2-116-tests`.\n- **The interface they assume:**\n  - `gov rebuild --integration <branch>`, its link at the path `rebuild.yaml`'s `integration_store` names (W2-122's\n    key);\n  - a seed from a store behind the head names the base's head commit (12 hex digits or more) and says `behind`.\n- **`allowed_paths` widened:** S3 needs a plain `gov retrieve` in a launched session to answer from the integration\n  store. So the launcher's session env (`src/gov/launch/launcher.py`) and the place `gov retrieve` picks its root\n  (`src/gov/retrieve/command.py`) are added, with the evidence record. Use an environment variable the launch sets and\n  `gov retrieve` reads when no `--root` is given.\n- **The refresh after a merge seeds from the ready half,** so it re-embeds only what changed (the designer's N-1).\n- **A build whose semantic store is not recreated counts as failed** (N-2), as the CTO's script counts it.\n- **Untested (N-4):** a search through the link writes its question-vector cache into the ready half. The engineer\n  states whether a sandboxed session may write there, or where the cache goes instead.\n\n**Pass 1 merged (CTO, 2026-11-06, `75acb0ff`; review READY in round 2, `reviews/w2-116.md`).** For the next pass (S2),\nriding along (DEC-802):\n- **R2-F1:** `gov retrieve --root <link>` still resolves the link once per facet. Resolve the root once in\n  `_store_root` in both branches. The plain form with `GOV_STORE` is fixed.\n- **R2-F3:** a continuation token carries no mark of the half it was made on. Page 2, asked after a switch, pages the\n  other half. The parallel-agents test after window 4 measures it (DEC-1087 (10)).\n- **F7:** the merge queue's promotion builds with the clone's code. Retire it, or make it build with the pinned gov,\n  once the hook is live.\n- **Window 4's ACT** installs the hook with `flock -o` (R2-F2), `env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP -u\n  GOV_REBUILD_LOCK` (F5), and the separate `W2-00-store.refresh.lock` taken before the heavy slot (F6).\n- **F3,** a stale `index.lock` after a refresh killed during its checkout, is a row (not ordinary work).\n\n[DEC-1087]\n- **W2-60b dropped from deps (CTO, 2026-11-13 16:00, a plan-order P2, DEC-957):** S2 needs no W2-60b code (the session record, the role set, KNOWN_ROLES); with DEC-1167 (3) moving W2-60b after the copy starts, the dependency made a cycle W2-27 -> W2-116 -> W2-60b -> after W2-27's start. W2-33's rule text is delivered (closed). `src/gov/status/**` added for S2's `gov status` line.\n",
  "authority": [
    {
      "id": "DEC-1109",
      "sha256": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "reason": "declared in sources",
      "tokens": 468
    },
    {
      "id": "DEC-1112",
      "sha256": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "reason": "declared in sources",
      "tokens": 498
    },
    {
      "id": "DEC-983",
      "sha256": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "reason": "declared in sources",
      "tokens": 674
    },
    {
      "id": "DEC-982",
      "sha256": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "reason": "declared in sources",
      "tokens": 766
    },
    {
      "id": "DEC-963",
      "sha256": "4a1905d866aafee5adc282ec609265f7df15540c75f06c3e5bbd528b3810cb7e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4a1905d866aafee5adc282ec609265f7df15540c75f06c3e5bbd528b3810cb7e",
      "reason": "declared in sources",
      "tokens": 821
    },
    {
      "id": "DEC-966",
      "sha256": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "reason": "declared in sources",
      "tokens": 607
    },
    {
      "id": "DEC-1014",
      "sha256": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "reason": "declared in sources",
      "tokens": 624
    },
    {
      "id": "DEC-1015",
      "sha256": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "reason": "declared in sources",
      "tokens": 689
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
      "id": "DEC-1087",
      "sha256": "2f6dbbf2fe7939aeef5a29de2e41d93144997ccd061d4af5bf04f5609d1d3298",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "2f6dbbf2fe7939aeef5a29de2e41d93144997ccd061d4af5bf04f5609d1d3298",
      "reason": "declared in sources",
      "tokens": 1467
    },
    {
      "id": "DEC-719",
      "sha256": "76e88cd4b06f7b5b75d21579f94f0243235def45e6714247a7b7f1a784751add",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "76e88cd4b06f7b5b75d21579f94f0243235def45e6714247a7b7f1a784751add",
      "reason": "declared in sources",
      "tokens": 655
    },
    {
      "id": "DAEO-kia7",
      "sha256": "ef3935e07048d805e4639d9c068b19d614c7387feaf8f2e4450c23883fba8725",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "ef3935e07048d805e4639d9c068b19d614c7387feaf8f2e4450c23883fba8725",
      "reason": "declared in sources",
      "tokens": 896
    },
    {
      "id": "DAEO-lrre",
      "sha256": "8e205955baf4b3da66dda2983331718d5bd8db493aaaacf4043285375419db03",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "8e205955baf4b3da66dda2983331718d5bd8db493aaaacf4043285375419db03",
      "reason": "declared in sources",
      "tokens": 1622
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1109",
      "sha256": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "reason": "declared in sources",
      "tokens": 468
    },
    {
      "id": "DEC-1112",
      "sha256": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "reason": "declared in sources",
      "tokens": 498
    },
    {
      "id": "DEC-983",
      "sha256": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "reason": "declared in sources",
      "tokens": 674
    },
    {
      "id": "DEC-982",
      "sha256": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "reason": "declared in sources",
      "tokens": 766
    },
    {
      "id": "DEC-963",
      "sha256": "4a1905d866aafee5adc282ec609265f7df15540c75f06c3e5bbd528b3810cb7e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4a1905d866aafee5adc282ec609265f7df15540c75f06c3e5bbd528b3810cb7e",
      "reason": "declared in sources",
      "tokens": 821
    },
    {
      "id": "DEC-966",
      "sha256": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "reason": "declared in sources",
      "tokens": 607
    },
    {
      "id": "DEC-1014",
      "sha256": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "reason": "declared in sources",
      "tokens": 624
    },
    {
      "id": "DEC-1015",
      "sha256": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "reason": "declared in sources",
      "tokens": 689
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
      "id": "DEC-1087",
      "sha256": "2f6dbbf2fe7939aeef5a29de2e41d93144997ccd061d4af5bf04f5609d1d3298",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "2f6dbbf2fe7939aeef5a29de2e41d93144997ccd061d4af5bf04f5609d1d3298",
      "reason": "declared in sources",
      "tokens": 1467
    },
    {
      "id": "DEC-719",
      "sha256": "76e88cd4b06f7b5b75d21579f94f0243235def45e6714247a7b7f1a784751add",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "76e88cd4b06f7b5b75d21579f94f0243235def45e6714247a7b7f1a784751add",
      "reason": "declared in sources",
      "tokens": 655
    },
    {
      "id": "DAEO-kia7",
      "sha256": "ef3935e07048d805e4639d9c068b19d614c7387feaf8f2e4450c23883fba8725",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "ef3935e07048d805e4639d9c068b19d614c7387feaf8f2e4450c23883fba8725",
      "reason": "declared in sources",
      "tokens": 896
    },
    {
      "id": "DAEO-lrre",
      "sha256": "8e205955baf4b3da66dda2983331718d5bd8db493aaaacf4043285375419db03",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "8e205955baf4b3da66dda2983331718d5bd8db493aaaacf4043285375419db03",
      "reason": "declared in sources",
      "tokens": 1622
    }
  ],
  "supplementary": [
    {
      "id": "b2001311b9974c3d2a1050d8",
      "path": "tests/acceptance/W2-116/README.md",
      "text": "## Files\n\n- `w2_116_support.py`: the planted project and its landings, the two stand-in endpoints, the commands, the link,\n  the hand-built store, the searches and the stand-in CLI for `gov launch`.\n- `conftest.py`: the case's box, the two endpoints, the environment, the project.\n- `test_w2_116_double_buffer.py` (S1, F2, F3, freshness), `test_w2_116_launch.py` (S3, F1),\n  `test_w2_116_refresh.py` (S4), `test_w2_116_reindex.py` (S5, F2, F3).\n\n**D-10's red fix (2026-11-10, W2-20 `DAEO-r30l`, DEC-1088 (5)(b), DEC-1109):** `w2_116_support.launch_and_search` plants an open gate (`plant_open_gate`, W2-136's form) in the box's HOME and adds its readings to the launch's environment. Its six launch cases stay red after it, for another reason reported to the CTO: the session's cleaned environment (W2-56 S5) no longer carries `W2_116_SESSION_LOG` to the stand-in CLI. The gate is W2-20's, not under test here; no expectation changes. W2-20 S19 runs the resource gate on every `gov launch`; with no `gate.json` in the case's HOME it shuts, and with the machine's own it shuts under load.\n\n",
      "tokens": 273
    },
    {
      "id": "c4742aaedd9968b77ca848d6",
      "path": "tests/acceptance/W2-116/README.md",
      "text": "| success-5 | `test_w2_116_reindex.py::test_s5_failure2_failure3_a_model_less_re_index_of_the_integration_store_keeps_its_index_and_says_so` | red | no `--integration` |\n| success-5 | `test_w2_116_reindex.py::test_s5_guard_a_model_less_re_index_of_a_tree_keeps_its_vectors_and_reports_the_facet_unavailable` | green (guard) | a plain model-less rebuild keeps every vector and reports `semantic: not_recreated` with `EMBEDDER_UNAVAILABLE` |\n| failure-1 | `test_w2_116_launch.py::test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store` | red | as in success-3 |\n| failure-2 | `test_w2_116_double_buffer.py::test_s1_failure2_a_search_during_a_build_is_answered_from_the_ready_half` | red | no `--integration` |\n| failure-2 | `test_w2_116_double_buffer.py::test_s1_failure2_freshness_a_search_through_the_link_while_the_other_half_rebuilds_is_never_stale` | red | no `--integration` |\n| failure-2 | `test_w2_116_double_buffer.py::test_s1_failure2_failure3_a_build_killed_half_way_leaves_the_link_and_the_ready_store_answers` | red | no `--integration` |\n",
      "tokens": 267
    },
    {
      "id": "38ead3446751d41d75eb35be",
      "path": "tests/acceptance/W2-116/README.md",
      "text": "| success-3 | `test_w2_116_launch.py::test_s3_every_worker_session_searches_the_integration_store_from_a_worktree_with_none[independent-test-designer]` | red | as above |\n| success-3 | `test_w2_116_launch.py::test_s3_every_worker_session_searches_the_integration_store_from_a_worktree_with_none[product-spec]` | red | as above |\n| success-3 | `test_w2_116_launch.py::test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store` | red | the designer's search in a ticket worktree with its own store gives the engineer's new note (`docs/engineer-new.md`) |\n| success-3 | `test_w2_116_launch.py::test_s3_guard_the_launched_session_keeps_its_role_and_ticket` | green (guard) | the session's `env` keeps `GOV_ROLE` and `GOV_TICKET` and starts in the worktree |\n| success-4 | `test_w2_116_refresh.py::test_s4_after_a_merge_the_refresh_brings_the_store_to_the_new_head` | red | no `--integration` |\n| success-4 | `test_w2_116_refresh.py::test_s4_at_an_unchanged_head_the_refresh_does_nothing` | red | no `--integration` |\n| success-4 | `test_w2_116_refresh.py::test_s4_the_refresh_after_a_merge_re_embeds_only_what_the_merge_changed` | red | no `--integration` |\n",
      "tokens": 292
    },
    {
      "id": "f070cd6977599617110c4fa5",
      "path": "governance/project/orchestration/reviews/w2-27-citp.md",
      "text": "### F9: the effect on the memory store and the measure is not stated\n\nUnder V (i), the apply rewrites 278 files under `docs/contract/`. It inserts about 10 lines into `contract.yaml` (the\n4.3 entry, and CAP-45's wave note and sources) and one row into `CONTRACT_v4.md`, so every later line number moves. The\nnote does not mention the store's refresh and re-embedding of these files, or the measure's re-anchoring of labels on\nthe Contract's files (DEC-1084). It also does not place the apply relative to the experiment windows (E1 to E5, the\nfresh 80 on a fixed pin). The measure runs on pinned clones, so this is probably harmless. One line in \u00a74 settles it.\nI opened no evaluation set.\n\n- Ordinary work: yes, because the apply lands on integrate while the experiments run.\n- Consequence: other.\n\n",
      "tokens": 200
    },
    {
      "id": "eb5469bb5affbdeb0f86fd71",
      "path": "tests/acceptance/W2-116/README.md",
      "text": "| success-4 | `test_w2_116_refresh.py::test_s4_the_refresh_after_a_merge_re_embeds_only_what_the_merge_changed` | red | no `--integration` |\n| success-4 | `test_w2_116_refresh.py::test_s4_the_integration_store_is_the_warm_base_gov_rebuild_seed_reads` | red | no `--integration` |\n| success-4 | `test_w2_116_refresh.py::test_s4_a_seed_from_a_store_behind_the_integration_head_is_named` | red | the seed from the hand-built store at H1, into a tree at H2, is `seeded` with `base`, `reason`, `copied`: no head, no `behind` |\n| success-4 | `test_w2_116_refresh.py::test_s4_guard_a_seed_from_a_store_behind_the_head_re_embeds_only_what_changed` | green (guard) | W2-122's seed: only `changed.md` and `merged.md` are embedded |\n| success-4 | `test_w2_116_refresh.py::test_s4_guard_a_seed_from_a_store_at_the_head_does_not_say_behind` | green (guard) | the seed says no `behind` today; it must not start to at the head |\n| success-5 | `test_w2_116_reindex.py::test_s5_failure2_failure3_a_model_less_re_index_of_the_integration_store_keeps_its_index_and_says_so` | red | no `--integration` |\n",
      "tokens": 271
    },
    {
      "id": "967690db82b58c1822e82f92",
      "path": "governance/project/orchestration/packages/LIFT-1/PAT-1-RESULT.md",
      "text": "## 5. Search during a refresh, and the continuation (W2-116's R2-F1 and R2-F3)\n- **The probe:** a search every 1.5 s for 4 minutes, alternating the two forms a worker uses (`--root <link>`, and `GOV_STORE=<link>` from inside a worktree with no store). A record commit landed during it.\n  - 147 searches: 0 errors, 0 fallbacks, 0 with a facet missing.\n  - The answers changed from the old half to the new half **exactly once**, in both forms: 92 old, then 55 new, with no flip-back.\n  - One search spanned the switch and answered from one half. No answer had the new record through only one facet, so R2-F1 (the link resolved once per facet) never showed.\n- **R2-F3, page 2 after a switch:** it is **refused**, with `CONTINUATION_INVALID` (\"the continuation's candidate pool is not this question's: the store or the pool settings changed since the earlier call\"). It never pages the other half silently. The worker asks page 1 again. Agent B saw the same.\n  - The refusal does not name the store the token came from (B's note).\n\n",
      "tokens": 257
    },
    {
      "id": "5ca66f1ed8fa195afcc4a98e",
      "path": "tests/acceptance/W2-116/README.md",
      "text": "- *the warm base:* a ticket worktree at the store's head, `gov rebuild --seed` with no folder: `seeded`, `base` the\n  link's half, nothing embedded.\n- *model-less re-index:* the H2 refresh with no model does not report success with a recreated semantic store,\n  names `semantic`, leaves the link, the ready half's head and its vectors, and the ready store answers; with the\n  model back the next refresh switches.\n\n**A check of the tests themselves** (a scratch copy of `src`, never committed): a sketch of about 60 lines\n(`--integration` alternating two halves `<link>-a` / `<link>-b`, each built by a child `gov rebuild --seed <ready\nhalf>`, the link replaced only when that child is ok with its semantic store recreated; the launcher putting\n`integration_store` in the session's env and `gov retrieve` reading it when no `--root` is given; the seed adding\nthe base's `head` and a `behind` sentence) passes all 20. A mutant of it that builds into the half in use and\nswitches on a failed build fails five: the alternation, the search during a build (`semantic: stale`), the\nfreshness case, the killed build (the ready half moved) and the model-less re-index.\n\n",
      "tokens": 291
    },
    {
      "id": "2f064a16769ab14f8513d391",
      "path": "tests/acceptance/W2-116/README.md",
      "text": "**D-10's red fix, the cleaned session environment (2026-11-10, W2-116 `DAEO-f58b`, DEC-1112 (3); Rewrite-Reason DEC-826 Q5, DEC-877 item 4):** W2-56 S5 gives a launched session a cleaned environment, so no parent variable reaches the stand-in CLI: not `W2_116_SESSION_LOG` (its `KeyError`), nor the question, the stand-in endpoints or `PYTHONPATH`. The stand-in now has its log, its question and the case's environment written into it when the case plants it (`install_cli`); its search runs with the case's environment beneath the session's own environment and the settings' `env` block, so whatever the launch gives the session wins, as before W2-56 (the case's environment names no store). The fixture project also plants the eight `.claude/templates/<stem>.md` copies (W2-153, DEC-1050; W1-46's and W2-56's form): without them `gov launch` refused every case with `LAUNCH_NO_TEMPLATE` before the session ran. No assertion changes. On integrate `9ca161a6f` the six launch cases (`test_w2_116_launch.py::test_s3_every_worker_session_searches_the_integration_store_from_a_worktree_with_none[engineer]`, `[independent-auditor]`, `[independent-test-designer]`, `[product-spec]`, `test_w2_116_launch.py::test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store`, `test_w2_116_launch.py::test_s3_guard_the_launched_session_keeps_its_role_and_ticket`) pass.\n",
      "tokens": 343
    }
  ],
  "supplementary_query": "The designers' store in the product: a double-buffered store of the integration branch, refreshed after the nightly and once more a day, that a test designer's retrieval reads (SMART-WORK-1)\n`gov rebuild --integration <branch>` keeps a store of that branch's head in two detached worktrees outside the project, building into the one not in use and switching a link to it only when the build succeeded; a search during a build is answered from the ready one [DEC-963, DEC-983, DEC-982] Verify: the success-1 cases in tests/acceptance/W2-116/test_w2_116_double_buffer.py (the build in a detached worktree behind the link, the two halves alternating, a search during a build and a killed build answered from the ready half) pass [Verify clause added, DEC-1157 (12)]\nIt is refreshed after the nightly's verdict and at a set second time each day (both in the project's configuration), and its status (head, age) is in `gov status` [DEC-966 item 3, DEC-983, DEC-982] Verify: pass 2's cases: a planted configuration's two refresh times are read and the refresh runs after the nightly's verdict and at the second time; `gov status` names the integration store's head and age, and a stale store is named; a missing or invalid time refuses by name [Verify clause added, DEC-1157 (12)]\n`gov launch independent-test-designer` points the session's retrieval at it; a designer's retrieval never reads a ticket worktree's store [DEC-963, DEC-983, DEC-982] Verify: the success-3 cases in tests/acceptance/W2-116/test_w2_116_launch.py pass: each launched worker role's plain search reads the integration store from a worktree with none, and the session keeps its role and ticket [Verify clause added, DEC-1157 (12)]\nThe store is also refreshed after every landing on the integration branch, and it is the warm base `gov rebuild --seed` (W2-122) reads; a seed taken from a store behind the integration head is named, and only what changed since is re-embedded [DEC-1014 items 4 and 6, SMART-WORK-5 D, DEC-1015 item 3] (folds W2-06 S1, S2) Verify: the success-4 cases in tests/acceptance/W2-116/test_w2_116_refresh.py pass: after a merge the refresh brings the store to the new head re-embedding only what changed, an unchanged head does nothing, `gov rebuild --seed` reads it and a seed behind the head is named [Verify clause added, DEC-1157 (12)]\nA re-index never empties the semantic index; a model-less re-index reports the semantic facet unavailable instead [DEC-719]. [moved from W2-06 S5, DEC-1083] Verify: the success-5 cases in tests/acceptance/W2-116/test_w2_116_reindex.py pass: a model-less re-index of the integration store keeps its index and says the semantic facet is unavailable [Verify clause added, DEC-1157 (12)]\n`gov launch` points every worker session's retrieval at the integration store (the `GOV_STORE` of a launched session), not only a designer's; a designer's retrieval never reads a ticket worktree's store. Verify: a launcher unit test per worker role: the session environment names the integration store; a designer's never names a worktree's store [DEC-1087 (3), DEC-963] [added, the CTO's note of 2026-11-06 in the body (S3 widened), DEC-1087 (3)]\nA designer's retrieval answered from a ticket worktree's store. Verify: tests/acceptance/W2-116/test_w2_116_launch.py::test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store passes [Verify clause added, DEC-1157 (12)]\nThe link switched to a store whose build failed, or a search answered from a half-built store. Verify: the failure-2 cases in test_w2_116_double_buffer.py and test_w2_116_reindex.py pass: a search during a build and through the link while the other half rebuilds is answered from the ready half, never stale; a build killed half way leaves the link [Verify clause added, DEC-1157 (12)]\nA re-index that fails leaves the previous index and reports the failure; it never leaves no index [W2-M088]. [moved from W2-06 F1, DEC-1083] Verify: the failure-3 cases in test_w2_116_double_buffer.py and test_w2_116_reindex.py pass: a killed build or a failed re-index leaves the previous index and reports the failure [Verify clause added, DEC-1157 (12)]",
  "further_batch": [
    {
      "id": "16479187a2415c661bb3bd65",
      "path": "tests/acceptance/W2-116/README.md"
    },
    {
      "id": "2782822da2c42b30ceb9a361",
      "path": "tests/acceptance/W2-116/README.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "b2001311b9974c3d2a1050d8",
          "path": "tests/acceptance/W2-116/README.md"
        },
        {
          "id": "c4742aaedd9968b77ca848d6",
          "path": "tests/acceptance/W2-116/README.md"
        },
        {
          "id": "38ead3446751d41d75eb35be",
          "path": "tests/acceptance/W2-116/README.md"
        },
        {
          "id": "f070cd6977599617110c4fa5",
          "path": "governance/project/orchestration/reviews/w2-27-citp.md"
        },
        {
          "id": "eb5469bb5affbdeb0f86fd71",
          "path": "tests/acceptance/W2-116/README.md"
        },
        {
          "id": "967690db82b58c1822e82f92",
          "path": "governance/project/orchestration/packages/LIFT-1/PAT-1-RESULT.md"
        },
        {
          "id": "5ca66f1ed8fa195afcc4a98e",
          "path": "tests/acceptance/W2-116/README.md"
        },
        {
          "id": "2f064a16769ab14f8513d391",
          "path": "tests/acceptance/W2-116/README.md"
        },
        {
          "id": "16479187a2415c661bb3bd65",
          "path": "tests/acceptance/W2-116/README.md"
        },
        {
          "id": "2782822da2c42b30ceb9a361",
          "path": "tests/acceptance/W2-116/README.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "16479187a2415c661bb3bd65",
      "reason": "budget exceeded"
    },
    {
      "id": "2782822da2c42b30ceb9a361",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 15949,
  "budget": {
    "limit": 16000,
    "used": 15949
  },
  "hash": "0ca323bf20637e4ccc2bac366a4f0fb9bb77c220a623e89d9b2c155a52c6965d"
}

## Your last message: the probe record, whole
```
---
type: probe
task: DAEO-f58b
reviewer_session: <your session id, or how you know it>
implementer_session: d49a06de-2ce9-46c3-b967-87829495f150 (independent-test-designer, td-4: pass 2c's seven-file revision)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
probed_commit: 037cf8a4fff0cada2b64fb8b7751b7c6d5dcd4ed
scope: narrow independent check of pass 2c (the test designer's seven-file revision, DEC-1156 (7))
---
# Probe record: W2-116 pass 2c (DAEO-f58b), narrow check
- What was probed (setup, commands, counts before and after)
- For each of the seven files: kept its point (yes/no, why); changed only `f` / `integration_store` (yes/no)
- Each finding: id, what, where (file:line), how found, then the two lines
  `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`
- Rows (out of scope, or "no" on the first question)
- Verdict: pass or fail, with the one line why
```
and, at its end, the verdict block, one entry per line judged (R2-F3's token key revision and S2's status part
revision):
````
```verdict
{"kpis": [{"kpi": "R2-F3", "verdict": "pass|fail", "findings": []}, {"kpi": "S2", "verdict": "pass|fail", "findings": [{"id": "F-1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```
````
