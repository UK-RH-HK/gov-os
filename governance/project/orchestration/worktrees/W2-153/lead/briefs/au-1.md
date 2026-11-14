# W2-153 — narrow independent check of the routed line's new cases, the independent auditor's brief (DAEO-8s85)

You are a fresh, read-only independent auditor working under **W2-153** (`.tickets/DAEO-8s85.md`, read-only at
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-8s85.md`). This is a **narrow** check (DEC-1154 form):
only the new cases for the ticket's sixth success line, routed from W2-33 (DEC-1156 (3)). S1 to S5 and both failure
lines were reviewed and merged earlier; they are out of scope.

**The line (success 6, `S6`):** the generated role copies carry each kernel role file's `Launch default`,
`Launch by criticality` and `Skills` lines unchanged, and a hand edit to a generated role copy is named as drifted by
the generation check. Verify: after the copies ACT, each generated role copy holds those lines byte-equal to its
kernel role file; a planted hand edit in one copy is named as drifted [DEC-315, DEC-957, DEC-1156 (3)].
W2-33's ticket (`.tickets/DAEO-lrre.md`, its F1 and the "Clauses judged elsewhere" paragraph) states where the
clause came from: F1's "one edited by hand in the generated folder (the generation check names it as drifted)".

## Head to probe
`0ffe7196e1e2cfc64f9e5da8fef0a438c2e6a80d` on `w2/W2-153`, in `/home/usain/gov-os-worktrees/W2-153` (read it; write
nothing there). Since the branch's last integrate merge (`9afc9e44d`) its only changes are
`tests/acceptance/W2-153/test_w2_153_routed.py` (new) and `tests/acceptance/W2-153/README.md` (the "Routed line"
section, mapped to `S6`). The code under check is integrate's `src/gov/adapters/portability.py` (the generation
check) and the committed copies (`.claude/agents/*.md`, `.rulesync/subagents/*.md`,
`template/.rulesync/subagents/*.md`) against `template/governance/kernel/roles/*.md`.

## What the lead saw (verify, do not take on trust)
- `gov accept W2-153` on this head: pass; `success-6` 71 passed, 0 failed, 18 skipped (the 18: six role files carry no
  `Launch by criticality` line, times three folders); nothing unmapped.
- The test designer reported planted breaks: a `Launch default` line changed in `template/.rulesync/subagents/engineer.md`
  failed exactly that case; the check's generated-file comparison disabled failed the three `generated-agent` drift
  cases; its source comparison disabled failed the three `composed-source` drift cases.
- The designer's discovery: the check compares `.rulesync/subagents/` with `compose()` and `.claude/agents/` with
  rulesync's output, but does not compare `template/.rulesync/subagents/`; a hand edit there is not named. Triage it
  against the line's scope (in or out, ordinary work, consequence) in your verdict.

## Questions
1. Do the cases verify both clauses of S6 as written (byte-equal lines in every generated role copy; a planted hand
   edit in a generated copy named as drifted by the generation check)? Any silent narrowing (a skip, a filter, a
   parametrize that drops a role or folder)?
2. Can each case fail? Plant your own break where you can, only in copies under your own `$TMPDIR` (e.g. `git
   worktree`-free: `git archive 0ffe7196e1e2 | tar -x -C <your $TMPDIR>/tree`), never in the repository's files.
3. Is the README's map right for `gov accept` (`src/gov/accept/runner.py`, `parse_map`)?

## Rules
- Read-only: you have Bash, Read, Grep, Glob only. `git status --short` in `/home/usain/gov-os-worktrees/W2-153` must be
  empty before and after. Write only under your sandbox's `$TMPDIR`.
- Pytest, if you run it, in this form with a copy's own `src` or the tree's:
  `env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=<tree>/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <tree>/tests/acceptance/W2-153/test_w2_153_routed.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=short`
  in the foreground (the slot may queue; wait in the same call, Bash timeout 600000 ms). Never run anything in the
  background or end your session while a command runs. If pytest writes `.pytest_cache` or `__pycache__` into the
  tree, use `-p no:cacheprovider` and `PYTHONDONTWRITEBYTECODE=1`.
- No GPU, model, network or installs. Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. One simple command per Bash call. Refused twice for the same call:
  stop and say so; never work around a refusal.

## Return (your final message, in full)
The twelve labelled fields of `EMG-common.md` (task, status, work_completed, files_changed, evidence, tests,
discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action; sandbox and `ps` checks
first), then a judgement line (`judgement: pass` or `judgement: fail`), your findings (each: id, what you did, what
happened, scope in/out, ordinary work yes/no, consequence), and the fenced `verdict` block JUDGEMENT.md below
defines, with one entry for `success-6`, exactly in that form:

```verdict
{"kpis": [{"kpi": "success-6", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```

## JUDGEMENT.md (word for word, `governance/project/briefs/JUDGEMENT.md` at this head)

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

## The ticket's context packet (gov context DAEO-8s85 --role independent-auditor; the store's copy, the ticket file wins)
```json
{
  "ticket": "DAEO-8s85",
  "ticket_text": "---\nid: DAEO-8s85\nstatus: in_progress\ndeps: []\nlinks: [DAEO-t8mp]\ncreated: 2026-11-09T20:40:06Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-153\ntags: [wave-2, templates, launch, adapters, standard]\nwbs_id: W2-153\ntitle: 'The role template delivered at launch: gov launch and the dispatcher pass it as the appended system prompt, refusing without it; the subagent bodies and the template copies generated and checked byte for byte (W2-128 TPL-4; the CTO''s split, DEC-1112 (3))'\nclass: tool\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- docs/probes/DAEO-8s85/**  # the probe record (the routed line's narrow check)\n- src/gov/launch/launcher.py\n- src/gov/adapters/portability.py\n- tests/unit/launch/test_w2_153*\n- tests/unit/adapters/test_w2_153*\n- tests/unit/launch/test_runs.py\n- tests/unit/launch/test_w1_28.py\n- tests/unit/launch/test_w1_32.py\n- tests/unit/launch/test_w2_136_plan_check.py\n- tests/unit/resources/test_w2_20_unit_launch.py  # renamed from test_w2_20_launch.py by `ae489a979` (D-10 collection fix) [changed, path moved]\n- tests/unit/resources/test_w2_20_round3.py\n- tests/unit/launch/test_w2_56.py\n- tests/unit/launch/test_w2_56_r5_lead_store.py\n- governance/project/orchestration/tools/dispatch/launch_now.sh\n- .rulesync/subagents/*.md\n- template/.rulesync/subagents/*.md\n- docs/changes/W2-153-evidence.md\nkpis:\n  success:\n  - 'S1 gov launch <role> <ticket> passes --append-system-prompt-file <root>/.claude/templates/<stem>.md (the role''s template, map below) for every worker role and for a lead, and refuses to start (GovError LAUNCH_NO_TEMPLATE naming the path) when that file is missing. Verify: a launcher unit test on the built argv per role, and the refusal case [DEC-1050] (W2-128 TPL-4 S1)'\n  - 'S2 The dispatcher''s lead launch form (governance/project/orchestration/tools/dispatch/launch_now.sh) passes the same flag with role-lead.md, and refuses when the file is missing. Verify: a test on the built command [DEC-1050] (TPL-4 S2)'\n  - 'S3 Each .rulesync/subagents/<role>.md (and template/.rulesync/subagents/) is its kernel role file''s front matter plus a skills: list (the role''s one or two kernel skills) with the body of its kernel role template; gov.adapters.portability compares the source with that composition (in place of the role file''s whole text) and reports them consistent. Verify: the existing portability tests extended by one case [DEC-1050] (TPL-4 S3)'\n  - 'S4 .claude/templates/<stem>.md are generated byte copies of template/governance/kernel/templates/<stem>.md for brief, role-research, role-product-spec, role-test-designer, role-engineer, role-reviewer, role-lead and role-cto; gov.adapters.portability reports a missing or differing copy as a finding, and python3 -m gov.adapters.portability --write-templates <dir> writes the copies (the ACT''s step). Verify: a test with one copy changed and one missing, and the writer on a temporary folder [DEC-1050] (TPL-4 S4)'\n  - 'S5 It lands at the .claude/ copies ACT: the copies are installed (S4''s writer, and rulesync for S3) in the same ACT that makes S1 and S2 live, so no launch is refused for a missing copy. Verify: the ACT''s record [DEC-1050, CAP-33]'\n  - 'Routed from W2-33 (its S7 copies and F1 drift, DEC-1156 (3)): the generated role copies carry each kernel role file''s `Launch default`, `Launch by criticality` and `Skills` lines unchanged, and a hand edit to a generated role copy is named as drifted by the generation check. Verify: after the copies ACT, each generated role copy holds those lines byte-equal to its kernel role file; a planted hand edit in one copy is named as drifted [DEC-315, DEC-957, DEC-1156 (3)]'\n  failure:\n  - 'A launched session starts without its role template (TPL-4 F1). Verify: S1''s and S2''s refusal cases [marked, DEC-1112 (3): a verify on each line, DEC-1083]'\n  - 'A lead or worker launch changes in any other way than the one added flag. Verify: the built argv otherwise byte-equal to integrate''s on the same fixture [marked, DEC-1112 (3)]'\nprofile: STANDARD\nsources:\n- DEC-1050\n- DEC-1052\n- DEC-1083\n- DEC-1112\n- DEC-1109\n- CAP-33\nest_loc: 250\nacceptance_tests:\n  path: tests/acceptance/W2-153/\n  author: independent-test-designer (MR-3), from these KPI lines and W2-128's interface\ntrack: A\nlist_rows: []\n---\n# W2-153 The role template delivered at launch (W2-128's code half, part 2)\n\n**Why.** R3-1 to R3-3: role files never reached launched sessions. W2-128 (`DAEO-t8mp`) wrote the templates; the CTO\nsplit its code half into W2-152 (`gov brief`) and this ticket (a delegated P2 under DEC-1112 (3);\n`packages/LIFT-1/D5-STATUS.md`). W2-128's S9 is built here; W2-128 closes after both.\n\n**Interface (D5 row 9, stated before the pair starts).**\n- **The role \u2192 template map** (one constant in `launcher.py`, reused by the portability check): engineer\n  `role-engineer`, independent-test-designer `role-test-designer`, independent-auditor `role-reviewer`, product-spec\n  `role-product-spec`, research `role-research`, lead and orchestrator `role-lead`.\n- **The flag** is appended to the CLI arguments the launcher builds (after the caller's), as\n  `--append-system-prompt-file <absolute path>`; `<root>` is the launch's repository root (the worker's worktree).\n- **The skills lists:** engineer `[test-driven-development]`, independent-test-designer `[test-design]`,\n  independent-auditor `[audit]`, product-spec `[change]`, research `[discovery]`, orchestrator `[orchestration]`; the\n  test designer's `test-design` only once W2-128 has reconciled that skill with DEC-963 (review F7): until then it is\n  left out and the case says so.\n- **The copies** are written only by the ACT (DEC-315): this ticket commits no `.claude/` file.\n\n- **Decided after the build (2026-11-10, the CTO, DEC-1112 (3)):**\n  - The source's skills list sits under `claudecode: skills:`, because rulesync 24.0.0 passes `skills` to the\n    generated agent only there. A top-level `skills:` is dropped, so the agents would preload nothing.\n  - The existing launcher unit tests whose fixtures start a session (`test_runs.py`, `test_w1_28.py`, `test_w1_32.py`,\n    `test_w2_136_plan_check.py`) write the role's `.claude/templates/<stem>.md` in their fixture. W2-136's case that\n    the caller's arguments end the argv now allows the one appended flag. Paths added. Refusing only when the folder\n    exists was not taken: it would fail open against F1.\n\n- **The review's R1 (2026-11-09, the CTO, DEC-1112 (3)):**\n  - The CTO scanned the suites the review named, on a clean `w2/W2-153` checkout against its merge base: 58 cases\n    newly red.\n    - Unit, the engineer's (paths added): `tests/unit/resources/test_w2_20_unit_launch.py` (29; named `test_w2_20_launch.py` then) and `test_w2_20_round3.py`\n      (7).\n    - Acceptance support files, a test designer's under DEC-866 (`Rewrite-Reason:`), in the same commit:\n      - W2-20: `test_w2_20_launch.py` (13), `test_w2_20_plan_source.py` (2), `test_w2_20_stale_samples.py` (1);\n      - W2-136: `test_w2_136_launch_check.py` (3);\n      - W1-46: `test_w1_46_held_out.py` (2), `test_w1_46_experiment_folder.py` (1).\n  - 141 cases in W1-28, W1-32, W1-46, W2-58, W1-50 and W2-54 are red on the base too. Their fixtures' machine gate\n    file is missing (W2-20's gate), so the launch stops before the template check. Their launch fixtures plant the\n    copy too, so W2-153 does not turn them red again once the gate files are fixed.\n  - Each fixture plants `.claude/templates/<stem>.md` for the role it launches (any byte content).\n  - After W2-56 merged into integrate, and with it into this branch (`a67fd010`, one conflict resolved by the CTO),\n    two more groups (rescanned 2026-11-10, DEC-1112 (3)):\n    - W2-56's acceptance folder: 136 of 256 newly red; it goes to the test designer.\n    - `tests/unit/launch/test_w2_56.py` (3): the engineer's; path added.\n    - W2-153's own launch cases read the stub's record path from an environment variable (`W2_153_RECORD`), which\n      W2-56's cleaned environment (its S5) now removes. The designer moves that harness to a path W2-56 keeps.\n    - After integrate `e242a66b` merged (W2-56's follow-ups R3/R5): `tests/unit/launch/test_w2_56_r5_lead_store.py`\n      (12), its lead fixtures without the copy; the engineer's, path added (DEC-1112 (3)).\n\n- **S3 amended (2026-11-10, the CTO, DEC-1112 (3)):** after ACT-CLAUDE-COPIES-2, the D-10 helper found the composed\n  agents lack the role file's fields (purpose, allowed paths, tools, network, model tier, authority level, handoff\n  format, permission classes), which W1-33 (MR-5, DEC-066) and W1-38 require: 27 cases.\n  - **Decided:** each composed `.rulesync/subagents/<role>.md` (and the template's copy) is\n    - its rulesync front matter (with `claudecode.skills`),\n    - then the role template's body,\n    - then one blank line,\n    - then the kernel role file's body (`template/governance/kernel/roles/<role>.md` verbatim, its front matter, if\n      any, stripped).\n  - The role templates carry no labelled field, so the agent's labelled fields are exactly the role file's. The\n    approved 1.0.0 templates do not change.\n  - **Interface:** `gov.adapters.portability` exposes `compose(root, role) -> str`, the expected source's full text.\n    Its check compares against that, and the copies ACT's builder writes it, so the two cannot drift.\n  - **W1-38's project builder** (`tests/acceptance/W1-38/w1_38_support.py::build_project_from_template`) also copies\n    the kernel's `templates/` into the generated project, as it copies `roles/` and `skills/`. That is a test\n    designer's revision under DEC-866.\n  - Paths: the test designer revises W1-38's support and W2-153's S3 cases; the engineer changes the portability\n    check and the twelve sources.\n\n**Not here:** the templates' text (W2-128); `gov brief` (W2-152).\n",
  "authority": [
    {
      "id": "DEC-1050",
      "sha256": "030c1c5a56d759a3b5e9567d1e8e9ec223f1ee733b958a466aefa0fdbdb4d9bf",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "030c1c5a56d759a3b5e9567d1e8e9ec223f1ee733b958a466aefa0fdbdb4d9bf",
      "reason": "declared in sources",
      "tokens": 948
    },
    {
      "id": "DEC-1052",
      "sha256": "b06a8c0bb8a126b90670963ca424b09adcf354c8d7237f73b6f46b22826c7095",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b06a8c0bb8a126b90670963ca424b09adcf354c8d7237f73b6f46b22826c7095",
      "reason": "declared in sources",
      "tokens": 1862
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
      "id": "DEC-1112",
      "sha256": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "reason": "declared in sources",
      "tokens": 498
    },
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
      "id": "CAP-33",
      "sha256": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "reason": "declared in sources",
      "tokens": 215
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1050",
      "sha256": "030c1c5a56d759a3b5e9567d1e8e9ec223f1ee733b958a466aefa0fdbdb4d9bf",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "030c1c5a56d759a3b5e9567d1e8e9ec223f1ee733b958a466aefa0fdbdb4d9bf",
      "reason": "declared in sources",
      "tokens": 948
    },
    {
      "id": "DEC-1052",
      "sha256": "b06a8c0bb8a126b90670963ca424b09adcf354c8d7237f73b6f46b22826c7095",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "b06a8c0bb8a126b90670963ca424b09adcf354c8d7237f73b6f46b22826c7095",
      "reason": "declared in sources",
      "tokens": 1862
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
      "id": "DEC-1112",
      "sha256": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "reason": "declared in sources",
      "tokens": 498
    },
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
      "id": "CAP-33",
      "sha256": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "authority": "capability",
      "lifecycle": "ACCEPTED",
      "constraint": "6a23ae252b2d47f166ff958018bec2c7bbc7f5b8ef69d500fab0d85651539cf1",
      "reason": "declared in sources",
      "tokens": 215
    }
  ],
  "supplementary": [
    {
      "id": "5d0a8132a6a210348d4b08a5",
      "path": "tests/acceptance/W2-153/README.md",
      "text": "## The interface as read (the ticket's body)\n\n- **Map:** engineer \u2192 `role-engineer`, independent-test-designer \u2192 `role-test-designer`, independent-auditor \u2192\n  `role-reviewer`, product-spec \u2192 `role-product-spec`, research \u2192 `role-research`, lead and orchestrator \u2192\n  `role-lead`.\n- **Flag:** `--append-system-prompt-file <root>/.claude/templates/<stem>.md`, appended after the caller's arguments,\n  with an absolute path, where `<root>` is the launch's repository root (its real path). A missing file refuses with\n  `GovError` `LAUNCH_NO_TEMPLATE` naming that path, and no session starts.\n- **Skills lists** (under `claudecode: skills:` in each source, DEC-1112 (3): rulesync 24.0.0 drops a top-level\n  `skills` from the generated agent, so a list there would deliver nothing): engineer `[test-driven-development]`, independent-auditor `[audit]`, product-spec `[change]`,\n  research `[discovery]`, orchestrator `[orchestration]`. The test designer gets `[test-design]` only once W2-128 has\n  reconciled that skill with DEC-963, which the case reads as \"the kernel skill names DEC-963\". Until then the list\n",
      "tokens": 277
    },
    {
      "id": "3ee03b36210074cebfb05c3a",
      "path": "tests/acceptance/W2-50/w2_50_support.py",
      "text": "\n\n# --------------------------------------------------------------------------\n# The fixture project, from scratch\n# --------------------------------------------------------------------------\n\nGUARD_COMMAND = f'python3 \"$CLAUDE_PROJECT_DIR\"/{GUARD_REL}'\nPROJECT_FILES = {\n    \"README.md\": \"# W2-50 fixture project\\n\",\n    \".gitignore\": \".gov-runtime/\\n__pycache__/\\n\",\n    \"src/app/main.py\": \"VALUE = 1\\n\",\n    \"src/other/main.py\": \"VALUE = 1\\n\",\n    \"docs/notes.md\": \"notes\\n\",\n    \"docs/spec/feature.md\": \"spec\\n\",\n    \"docs/audit/earlier.md\": \"audit\\n\",\n    \"experiments/spikes/exp-901/README.md\": \"# Experiment 901\\n\",\n}\n# W2-153 (DEC-1050, DEC-1116): ``gov launch`` refuses a session without ``.claude/templates/<stem>.md`` for its role\n# (LAUNCH_NO_TEMPLATE), so the fixture project holds the eight copies, byte for byte the kernel's own\n# ``template/governance/kernel/templates/<stem>.md`` (what the ACT installs, W2-153 S4). The cases that launch a\n# session test what they tested before; none accepts the refusal.\nTEMPLATE_STEMS = (\"brief\", \"role-research\", \"role-product-spec\", \"role-test-designer\", \"role-engineer\",\n                  \"role-reviewer\", \"role-lead\", \"role-cto\")\n",
      "tokens": 297
    },
    {
      "id": "659b90c7925c0415f76a4cba",
      "path": "governance/project/orchestration/reviews/w2-153-w1-46.md",
      "text": "    - True, which is acceptable as explained under F3: any stem (another role's or an unknown name); a relative path with something before `.claude/templates/`; anything inserted before the caller's arguments.\n  - **Rebuilt launches:** all four rows (`accept-edits`, `accept-edits-joined`, `engineer`, `research`) start with exit 0 and exactly one session. Each argv ends with the caller's arguments, then `--append-system-prompt-file <repo>/.claude/templates/role-engineer.md` (`role-research.md` for research). The old assertion is False on all four; the new one is True on all four.\n  - **Launcher:** `src/gov/launch/launcher.py:450` (lead) and `:483` (worker) both build `[*cli_args, *template]`. `template_args` (`:332-339`) always returns the pair or raises `LAUNCH_NO_TEMPLATE`. No launch path skips the pair.\n  - **Scratch:** the probe folder (49 MB) and the retained pytest folders (496 MB) are deleted. The scratch HOME holds 1 inode.\n- **tests:**\n",
      "tokens": 240
    },
    {
      "id": "0c1c783b25b6d20df763f111",
      "path": "tests/acceptance/W2-153/w2_153_support.py",
      "text": "What is never touched: no real Claude session starts. ``gov launch`` runs with ``HOME`` set to a temporary folder whose\n``.local/bin/claude`` is a stand-in that records its arguments and ends; the machine-wide folder, the gate's readings\nand the registry all live in that home. The dispatcher's script runs as a copy whose absolute paths are rewritten into\na temporary folder (its CLI, the orchestrator folder and the worktrees folder), so it can reach no real path.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport datetime\nimport io\nimport json\nimport os\nimport re\nimport subprocess\nimport sys\nimport tarfile\nfrom pathlib import Path\n\nimport yaml\n\nHERE = Path(__file__).resolve().parent\nREPO = HERE.parents[2]\nSRC = REPO / \"src\"\nHARNESS = HERE / \"w2_153_launch_harness.py\"\n\nCOMMAND_TIMEOUT_S = 120.0  # a wait under parallel load, not a time the ticket promises\nSAFE_PATH = \"/usr/local/bin:/usr/bin:/bin\"\nGIB = 1024 ** 3\n\nFLAG = \"--append-system-prompt-file\"\nREFUSAL = \"LAUNCH_NO_TEMPLATE\"\n\n# The ticket's Interface (D5 row 9): the role -> template map, one constant in launcher.py.\nROLE_TEMPLATE = {\n    \"engineer\": \"role-engineer\",\n    \"independent-test-designer\": \"role-test-designer\",\n",
      "tokens": 298
    },
    {
      "id": "f9c97a91aaa7ecafc5f0a4da",
      "path": "tests/acceptance/W2-153/w2_153_support.py",
      "text": "\"\"\"Support code for the W2-153 acceptance tests (standard library and PyYAML only).\n\nW2-153 delivers the role template at launch (W2-128 TPL-4): ``gov launch`` and the dispatcher's lead line pass\n``--append-system-prompt-file <root>/.claude/templates/<stem>.md`` and refuse without the file; the rulesync role\nsources are composed (S3 amended, DEC-1112 (3): the rulesync front matter with ``claudecode.skills``, the kernel role\ntemplate's body, one blank line, the kernel role file's body; ``gov.adapters.portability.compose(root, role)``); the\n``.claude/templates/`` copies are checked byte for byte and written by ``python3 -m gov.adapters.portability\n--write-templates <dir>``.\n\nHow the code under test is chosen (DEC-732): every command runs with ``PYTHONPATH`` set to the ``src/`` folder of the\nworking tree this file is in. The baseline for the failure line F2 is integrate's code at ``BASELINE_COMMIT``, read\nfrom git (``git archive`` / ``git cat-file``) into a temporary folder after checking its blob ids.\n\nWhat is never touched: no real Claude session starts. ``gov launch`` runs with ``HOME`` set to a temporary folder whose\n",
      "tokens": 284
    },
    {
      "id": "7d88bda43a96dd3f80716a83",
      "path": "tests/acceptance/W2-153/README.md",
      "text": "and the rulesync outputs (S3) are installed in the same ACT that makes S1 and S2 live, and no launch is refused for a\nmissing copy (CAP-33, DEC-315). The copies are written only by the ACT. This ticket commits no `.claude/` file, and\nthe ACT's record (`ACT-CLAUDE-COPIES-1` or its successor) is the owner's operator's, outside this ticket's paths. The\nCTO verifies it from that record, as the ticket's Verify line says. Until the ACT runs, the portability check on this\nrepository reports the eight copies as missing. That is expected, and no case here asserts on the repository's own\n`.claude/templates/`.\n\n**A check of the tests themselves** (a throwaway shared clone at `1ef1a7a48c53`, removed afterwards, never\ncommitted): a minimal reference build was written there. It had the map and the refusal in `launcher.py` (flag\nappended after the caller's arguments), the composition, the copies' check and `--write-templates` in\n`portability.py`, the dispatcher's file check with the flag placed *before* `-p` (so F2 does not depend on where the\nflag goes), and the twelve sources composed. It passed all 50 cases. Two wrong builds each failed the cases meant\n",
      "tokens": 290
    }
  ],
  "supplementary_query": "The role template delivered at launch: gov launch and the dispatcher pass it as the appended system prompt, refusing without it; the subagent bodies and the template copies generated and checked byte for byte (W2-128 TPL-4; the CTO's split, DEC-1112 (3))\nS1 gov launch <role> <ticket> passes --append-system-prompt-file <root>/.claude/templates/<stem>.md (the role's template, map below) for every worker role and for a lead, and refuses to start (GovError LAUNCH_NO_TEMPLATE naming the path) when that file is missing. Verify: a launcher unit test on the built argv per role, and the refusal case [DEC-1050] (W2-128 TPL-4 S1)\nS2 The dispatcher's lead launch form (governance/project/orchestration/tools/dispatch/launch_now.sh) passes the same flag with role-lead.md, and refuses when the file is missing. Verify: a test on the built command [DEC-1050] (TPL-4 S2)\nS3 Each .rulesync/subagents/<role>.md (and template/.rulesync/subagents/) is its kernel role file's front matter plus a skills: list (the role's one or two kernel skills) with the body of its kernel role template; gov.adapters.portability compares the source with that composition (in place of the role file's whole text) and reports them consistent. Verify: the existing portability tests extended by one case [DEC-1050] (TPL-4 S3)\nS4 .claude/templates/<stem>.md are generated byte copies of template/governance/kernel/templates/<stem>.md for brief, role-research, role-product-spec, role-test-designer, role-engineer, role-reviewer, role-lead and role-cto; gov.adapters.portability reports a missing or differing copy as a finding, and python3 -m gov.adapters.portability --write-templates <dir> writes the copies (the ACT's step). Verify: a test with one copy changed and one missing, and the writer on a temporary folder [DEC-1050] (TPL-4 S4)\nS5 It lands at the .claude/ copies ACT: the copies are installed (S4's writer, and rulesync for S3) in the same ACT that makes S1 and S2 live, so no launch is refused for a missing copy. Verify: the ACT's record [DEC-1050, CAP-33]\nRouted from W2-33 (its S7 copies and F1 drift, DEC-1156 (3)): the generated role copies carry each kernel role file's `Launch default`, `Launch by criticality` and `Skills` lines unchanged, and a hand edit to a generated role copy is named as drifted by the generation check. Verify: after the copies ACT, each generated role copy holds those lines byte-equal to its kernel role file; a planted hand edit in one copy is named as drifted [DEC-315, DEC-957, DEC-1156 (3)]\nA launched session starts without its role template (TPL-4 F1). Verify: S1's and S2's refusal cases [marked, DEC-1112 (3): a verify on each line, DEC-1083]\nA lead or worker launch changes in any other way than the one added flag. Verify: the built argv otherwise byte-equal to integrate's on the same fixture [marked, DEC-1112 (3)]",
  "further_batch": [
    {
      "id": "1d6c25e28722740af62784e5",
      "path": "src/gov/launch/launcher.py"
    },
    {
      "id": "933230beb4da0505bcb0235c",
      "path": "docs/changes/W2-153-evidence.md"
    },
    {
      "id": "d06c0e178030a1fd89273720",
      "path": "tests/acceptance/W2-153/README.md"
    },
    {
      "id": "e342d37f409280abeee31b37",
      "path": "docs/changes/W2-153-evidence.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "5d0a8132a6a210348d4b08a5",
          "path": "tests/acceptance/W2-153/README.md"
        },
        {
          "id": "3ee03b36210074cebfb05c3a",
          "path": "tests/acceptance/W2-50/w2_50_support.py"
        },
        {
          "id": "659b90c7925c0415f76a4cba",
          "path": "governance/project/orchestration/reviews/w2-153-w1-46.md"
        },
        {
          "id": "0c1c783b25b6d20df763f111",
          "path": "tests/acceptance/W2-153/w2_153_support.py"
        },
        {
          "id": "f9c97a91aaa7ecafc5f0a4da",
          "path": "tests/acceptance/W2-153/w2_153_support.py"
        },
        {
          "id": "7d88bda43a96dd3f80716a83",
          "path": "tests/acceptance/W2-153/README.md"
        },
        {
          "id": "1d6c25e28722740af62784e5",
          "path": "src/gov/launch/launcher.py"
        },
        {
          "id": "933230beb4da0505bcb0235c",
          "path": "docs/changes/W2-153-evidence.md"
        },
        {
          "id": "d06c0e178030a1fd89273720",
          "path": "tests/acceptance/W2-153/README.md"
        },
        {
          "id": "e342d37f409280abeee31b37",
          "path": "docs/changes/W2-153-evidence.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "1d6c25e28722740af62784e5",
      "reason": "budget exceeded"
    },
    {
      "id": "933230beb4da0505bcb0235c",
      "reason": "budget exceeded"
    },
    {
      "id": "d06c0e178030a1fd89273720",
      "reason": "budget exceeded"
    },
    {
      "id": "e342d37f409280abeee31b37",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 8849,
  "budget": {
    "limit": 9000,
    "used": 8849
  },
  "left_out": {
    "count": 3,
    "superseded": [
      "DEC-043",
      "DEC-875",
      "DEC-876"
    ],
    "done": []
  },
  "hash": "57bcb5b6b98f9f5bb9c0e2afd0c598e80329469fec0d61bb4721b49d2eac4a46"
}
```
