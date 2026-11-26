# Lead brief: card-w2-128, the CTO's role card meets the template contract (seven W2-128 `role-cto` base reds) and states the release rule now built; a fix under W2-128 (DAEO-t8mp)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-26. **Read `docs/emergency-2/briefs/LEAD-COMMON.md`
first: every rule there applies.** Decide, never ask (I-10). Use `systematic-debugging`.

## Why
The CTO's role card `template/governance/kernel/templates/role-cto.md` was rewritten to 2.0.0 for Emergency 2 (`7fc18d489`, the owner's
yes in DEC-1253). Since then seven W2-128 cases are red on `w2/integrate`, in every landing whose selection holds W2-128:
- `test_w2_128_templates.py::test_s2_prose_is_within_r3_budget[role-cto]`: prose 7745 characters against R3 §C's 6000 (`governance/project/facts.yaml:175`).
- `test_w2_128_links.py::test_s14_template_carries_its_link_lines[role-cto]`: lacks LINK-INTEGRITY §5's link words.
- `test_w2_128_rows.py` rows 3, 4 and 9 `[role-cto]`: no line carrying D5 rows 4 and 9; row 3's line ends with no bracketed decision id.
- `test_w2_128_templates.py::test_f1_every_gov_command_and_script_a_template_names_is_in_facts`: `facts.yaml`'s commands lack
  `gov launch`, `gov msg`, `gov queue`, `gov release`, `cto_watch.sh`, `start_cto.sh`, `start_lead.sh` (and a parse of `gov gov`).
- `test_w2_128_templates.py::test_s20_t8_names_search_again_once_on_its_start_line`.
This is the same shape as FINDINGS I-35 (the orchestrator role file).

## What (K-lines as a `## Fix:` section in `.tickets/DAEO-t8mp.md`; the CTO approves them, and the card's change, by this brief, EMERGENCY-2 §3.5)
- **CW-1 The card meets every requirement that still holds under Emergency 2 and the golden workflow v2.** Change the card (the
  engineer helper; this brief names the file, so the kernel change is approved): keep every rule it states (each bullet's meaning),
  cut wording to the prose budget, carry the link lines, put "search again once" on the line the test reads, cite the decision on each
  row line. Add the commands it names to `facts.yaml`'s commands map where they are real (`gov gov` is a parse fault: find it).
- **CW-2 Stale pins re-baselined, never the card bent to a retired rule.** A W2-128 case that pins a rule Emergency 2 retired (for
  example a row that requires every worker brief to be built by `gov brief`, or a pair under its ticket's own id, if D5's row says so)
  is the independent test designer's to change, citing the decision that retired it (EMERGENCY-2 section, DEC id) in a `Rewrite-Reason`
  trailer; the engineer never edits `tests/acceptance/`. Say in your return, per case, whether the card or the test moved and why.
- **CW-3 The release line, word for word** (replace the card's `- **Releases:**` bullet):
  `- **Releases:** you cut a release by code (`gov release <v> --patch`, the authority file on) once its release suite on the exact commit is green on an idle machine: a patch (fixes and chores), or an approved release, whose every feature ticket names the owner's accepted decision (`approved_by:` in its front matter, or `Approved-by:` on the commit) [DEC-1235 (2), I-34]; anything else is bigger and the owner's by hand. Every commit of yours that touches `template/` or `src/gov` carries `Class: C`, or `Approved-by:` when it needs his approval, all trailers in one paragraph. Pushes to GitHub and `sudo` are the owner's.`
  (Shorten its wording only if the budget needs it; its four facts stay.)
- The card's copies follow it: `.claude/templates/role-cto.md` and `src/gov/_shipped/template/governance/kernel/templates/role-cto.md`
  (find how the earlier card commit `7fc18d489` refreshed them and do the same; never `gov adapters generate` on this tree, I-16).
  Raise the card's `version:` to 2.0.1.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-card-w2-128`, branch `e2/card-w2-128` from `w2/integrate`. Code area: the card and its two
copies, `governance/project/facts.yaml` (the commands map only), `tests/acceptance/W2-128/` (the test designer only),
`.tickets/DAEO-t8mp.md`. Others work meanwhile on `e2/bundle-a` and `e2/bundle-b`: do not edit their files. Never merge into `w2/integrate`.

## Green
The seven cases green; `gov accept W2-128` green; W1-33 and W2-201 (they pin role files, I-35) still green; then exactly the
impact-selected suites (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-t8mp=e2/card-w2-128 --onto w2/integrate
--select`) through the heavy slot. Check the trailers (LEAD-COMMON).

## Return
Branch and head; per case, what moved (card or test) and why; the card's prose count; the selected run's summary; your retrieves
(count, queries, records used).

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
store: c1e81afd3e75 (/home/usain/Dynamic-Agentic-Engineering-OS), store behind HEAD, head c5de6a691cde, 78 stale path(s)
{
  "store": {
    "commit": "c1e81afd3e7560e7a8f769bb51de083b07d72158",
    "head": "c5de6a691cdecfb5ea9388208208718b98e41350",
    "stale": [
      ".claude/agents/orchestrator.md",
      ".claude/templates/role-cto.md",
      ".rulesync/subagents/orchestrator.md",
      ".tickets/DAEO-a2h5.md",
      ".tickets/DAEO-clon.md",
      ".tickets/DAEO-d3sr.md",
      ".tickets/DAEO-esl1.md",
      ".tickets/DAEO-j9z6.md",
      ".tickets/DAEO-l2b2.md",
      ".tickets/DAEO-ma4q.md",
      ".tickets/DAEO-t6hf.md",
      ".tickets/DAEO-zqvn.md",
      "docs/DECISION_REGISTER.md",
      "docs/checkpoints/DAEO-sdxk/CP-DAEO-sdxk-3337.md",
      "docs/emergency-2/CTO-HANDOVER.md",
      "docs/emergency-2/briefs/LEAD-1-0-selection.md",
      "docs/emergency-2/briefs/LEAD-bundle-a-reds.md",
      "docs/emergency-2/briefs/LEAD-bundle-b.md",
      "docs/emergency-2/briefs/LEAD-memaudit-launch.md",
      "docs/emergency-2/briefs/LEAD-release-rule.md",
      "docs/emergency-2/briefs/LEAD-timing-tests.md",
      "docs/emergency-2/briefs/PRODUCT-CTO-HANDOVER-METHOD.md",
      "docs/emergency-2/integration/FINDINGS.md",
      "docs/emergency-2/proposals/RELEASE-ON-BEHALF.md",
      "docs/plan/wave-2/w2-209-rehearsal/rehearse.py",
      "governance/project/orchestration/tools/start_cto.sh",
      "governance/project/test-map.yaml",
      "src/gov/_shipped/template/governance/kernel/templates/role-cto.md",
      "src/gov/close/select.py",
      "src/gov/memaudit/brief.py",
      "src/gov/memaudit/say.py",
      "src/gov/memaudit/writercheck.py",
      "src/gov/queue/command.py",
      "src/gov/queue/dry.py",
      "src/gov/release/__init__.py",
      "src/gov/release/command.py",
      "src/gov/release/cut.py",
      "src/gov/release/gates.py",
      "src/gov/release/patch.py",
      "src/gov/release/repin.py",
      "template/.rulesync/subagents/orchestrator.md",
      "template/governance/kernel/roles/orchestrator.md",
      "template/governance/kernel/templates/role-cto.md",
      "tests/acceptance/W1-19/README.md",
      "tests/acceptance/W1-19/test_w1_19_judged_time.py",
      "tests/acceptance/W1-19/test_w1_19_real_models.py",
      "tests/acceptance/W1-19/w1_19_support.py",
      "tests/acceptance/W2-112/README.md",
      "tests/acceptance/W2-112/test_w2_112_clock.py",
      "tests/acceptance/W2-112/test_w2_112_serial_list.py",
      "tests/acceptance/W2-112/w2_112_session.py",
      "tests/acceptance/W2-112/w2_112_support.py",
      "tests/acceptance/W2-115b/README.md",
      "tests/acceptance/W2-115b/test_w2_115b_sel.py",
      "tests/acceptance/W2-115b/test_w2_115b_unwritten_paths.py",
      "tests/acceptance/W2-115b/w2_115b_sel_support.py",
      "tests/acceptance/W2-13/README.md",
      "tests/acceptance/W2-13/test_w2_13_judged_time.py",
      "tests/acceptance/W2-13/test_w2_13_latency.py",
      "tests/acceptance/W2-13/w2_13_support.py",
      "tests/acceptance/W2-204/README.md",
      "tests/acceptance/W2-204/test_w2_204_fm5_launch.py",
      "tests/acceptance/W2-204/test_w2_204_ml_launch.py",
      "tests/acceptance/W2-204/test_w2_204_s9_s10_brief_deliver.py",
      "tests/acceptance/W2-206/README.md",
      "tests/acceptance/W2-206/test_w2_206_sel4.py",
      "tests/acceptance/W2-209/README.md",
      "tests/acceptance/W2-209/test_w2_209_approved.py",
      "tests/acceptance/W2-209/test_w2_209_class_q.py",
      "tests/acceptance/W2-209/test_w2_209_cut.py",
      "tests/acceptance/W2-209/test_w2_209_pending.py",
      "tests/acceptance/W2-209/w2_209_support.py",
      "tests/acceptance/serial-only.txt",
      "tests/unit/memaudit/test_launch_lines.py",
      "tests/unit/queue/test_queue_select_sel.py",
      "tests/unit/queue/test_queue_select_unwritten.py",
      "tests/unit/queue/test_queue_w2_206_flags.py",
      "tests/unit/release/test_approvals_units.py"
    ],
    "root": "/home/usain/Dynamic-Agentic-Engineering-OS"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "DAEO-t8mp",
      "sha256": "6606d1ba9c0bbb033415d2b9f2b91080550cde20b038d08b1e7ff2df33244c82",
      "path": ".tickets/DAEO-t8mp.md",
      "start_line": 104,
      "end_line": 123,
      "text": "# W2-128 The templates (P1-7, R3-TEMPLATES \u00a7D)\n\nFiled 2026-11-06 by the CTO on the owner's approval (DEC-1081 (2), DEC-974). The work package is R3's eight\npackages TPL-1 to TPL-8 (`governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md` \u00a7D, the templates in its\nAppendix), shaped by R2's evidence (P1-PLAN P1-7), plus LINK-INTEGRITY.md \u00a76.1's three lines for this ticket.\n\n- **Why:** bad briefs lose work (7,669 brief-gap minutes stated in 83 returns); four layers of brief text contradict\n  one another, and role files never reach launched sessions (R3-1 to R3-3).\n- **Order (R3 \u00a7D):** TPL-3b's scripts are done (CTO's tools, 2026-11-06); then TPL-2 and TPL-1 in parallel, then\n  TPL-3, then TPL-4; TPL-5 beside TPL-3; TPL-6 after TPL-4 and the owner's row decisions; TPL-7 beside TPL-3; TPL-8\n  last. The guard's G-1/G-2 fixes land before the templates drop the \"the guard refuses here-documents\" lines.\n- **Roles:** product-spec writes the templates, the schemas and the kernel texts; an independent test designer writes\n  the tests from these KPI lines first; one independent review. TPL-2's facts and TPL-6's project prompt are the\n  CTO's lane. **The code parts, TPL-3's `gov brief` in the product and TPL-4's launcher flag, are an engineer's**,\n  and `gov launch` starts an engineer only on an engineer's ticket: when they are reached, the CTO brings the owner a\n  split (one engineer's ticket for them), so the paths here hold no `src/` path.\n- **Unchanged:** W2-11 and W2-11b land as built and W2-128's lines replace theirs; W2-33's role files get the lines\n  through these templates (TPL-4).\n- **Estimate:** about 4 to 5 working days in all, parts in parallel (R3 \u00a7D, est.).\n\n",
      "chunk_id": "dfef0059bbd6a036a299fdc9",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-t8mp",
      "sha256": "28de0d4a19c762b467be3ed9f22ed9f10a457d4628f1d3c09728e78b0447c002",
      "path": ".tickets/DAEO-t8mp.md",
      "start_line": 50,
      "end_line": 54,
      "text": "  - 'Links recorded at the source (DEC-1073 (5)(c)): each role template (T-2 to T-8), the ticket template (T-1) and the record templates (decision-record, lesson, research, checkpoint, failure) carry LINK-INTEGRITY.md \u00a75''s lines for the records that role writes. Verify: a string test per template, and gov links on a planted record filled from each template''s example gives no finding [DEC-1073, DEC-866, DEC-182, DEC-927]'\n  - 'The facts file''s commands hold links (gov links --since {BASE}) with its check form; the lead template''s return quotes its first line [DEC-1073, DEC-927]'\n  - 'The lesson, failure and research schemas allow sources (ids), and research decisions, both optional; every existing record stays valid [DEC-1073]'\n  - 'The kernel part goes through one CIT-P under CAP-33 (evidence R2 and R3, an independent review, the owner''s approval, a versioned promotion), recorded in docs/changes/W2-128-CIT-P.md; the .claude/ copies are installed by the owner''s operator as an ACT [CAP-33, DEC-1050, DEC-1081]'\n  - 'The reviewer states, per finding, what evidence would reverse it [DEC-1014, SMART-WORK-4 line 4] [moved from W2-11b S2, DEC-1083]'\n",
      "chunk_id": "d52b7c12bbfdbc2d786e3397",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "e283092f5b877c48d85f5a64",
      "sha256": "bbcf68a45340909917ccf411e039ed62482f986baa725e81e6147f9b9bdb8a02",
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "start_line": 440,
      "end_line": 451,
      "text": "**W2-128** (P1-7's proposed templates ticket, not yet filed)\n- **Why:** (c) belongs in D-5's templates, as the owner suggests.\n- **When it is filed, add:**\n  - `'Links recorded at the source (DEC-1073 (5)(c)): each role template (T-2 to T-8), the ticket template (T-1) and the record templates (decision-record, lesson, research, checkpoint, failure) carry LINK-INTEGRITY.md \u00a75''s lines for the records that role writes; verify: a string test per template, and gov links on a planted record filled from each template''s example gives no finding [DEC-1073, DEC-866, DEC-182, DEC-927]'`\n  - `'The facts file''s commands hold links (gov links --since {BASE}) with its check form; the lead template''s return quotes its first line [DEC-1073, DEC-927]'`\n  - `'The lesson, failure and research schemas allow sources (ids), and research decisions, both optional; every existing record stays valid [DEC-1073]'`\n- **M3 (the follow rate)** covers the links lines.\n\n**Unchanged, and why:**\n- W2-115 (the smart close): no link check in the close. The structural pass runs after the landing.\n- W2-45: a `warning` declaration is already YELLOW at most.\n- W2-44: trailer identity is a separate concern.\n",
      "chunk_id": "e283092f5b877c48d85f5a64",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "W2-128-CIT-P",
      "sha256": "575726ec97f5a309e3171a09e80f8aed5df10b3fd6fb37f8822bfa201bfb9075",
      "path": "docs/changes/W2-128-CIT-P.md",
      "start_line": 46,
      "end_line": 51,
      "text": "| `template/governance/kernel/templates/role-research.md`, `role-product-spec.md`, `role-test-designer.md`, `role-engineer.md`, `role-reviewer.md`, `role-lead.md`, `role-cto.md` | New: T-2 to T-8, from R3's Appendix, each within R3 \u00a7C's budget, with the link lines of LINK-INTEGRITY \u00a75 and D5 rows 1 to 4 and 7 to 9; T-6 holds `JUDGEMENT.md`'s content as its Judgement section and the reversal line (DEC-1014) |\n| `template/governance/kernel/templates/keys.yaml` | New: the key list the generator reads |\n| `template/governance/kernel/templates/checkpoint.md`, `decision-record.md`, `decision-package.md`, `failure.md`, `lesson.md`, `research.md` | The link lines (fields and a comment); `research.md` gains \"Decision it feeds\" and \"Stop rule\" (R3-12) |\n| `template/governance/kernel/templates/brief-engineer.md`, `brief-test-designer.md`, `brief-reviewer.md`, `brief-product-spec.md`, `brief-lead.md` | Each a one-line pointer to its replacement |\n| `template/governance/kernel/roles/engineer.md` (and its `.rulesync/` sources) | Line 5: \"to fulfil the spec and its KPIs\" (DEC-957) |\n| `template/governance/kernel/schemas/facts.schema.json` | New: the facts file's schema |\n",
      "chunk_id": "5a26f0d3966a2702eeb59ff7",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "WAVE-2-WBS",
      "sha256": "1df326a6baa4ff7d361c2a51ed0f30e458a239cce4a651cfe76adb8c8a4b20b5",
      "path": "docs/plan/WAVE_2_WBS.md",
      "start_line": 1792,
      "end_line": 1794,
      "text": "#### W2-128 The templates: one per role, the ticket and the brief envelope, filled from the ticket and one facts file, delivered at launch, their use measured (P1-7, R3 TPL-1 to TPL-8, DEC-1050 TEMPLATES) (STANDARD, product-spec)\n- **Ticket file:** `DAEO-t8mp` (in_progress); its KPIs, paths and sources are there.\n\n",
      "chunk_id": "28b6c2bc1f2d07f52d78ea9f",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-wahn",
      "sha256": "2cf26059c2e68e977fe85ceaefcf3cc4bfcd4d4700404f55ae6f9af77df2161d",
      "path": ".tickets/DAEO-wahn.md",
      "start_line": 59,
      "end_line": 62,
      "text": "  - line: \"Each changed role template's `version` goes from 1.0.0 to 1.0.1 (DEC-1121's step for a template delta); no other front matter key changes, and the prose of each stays within its budget in `governance/project/facts.yaml` (3500 characters, role-lead 8000, role-cto 6000) with every placeholder a key of `keys.yaml` [DEC-1050, DEC-1116, DEC-1121]\"\n    verify: \"tests/acceptance/W2-175/: the front matter of each changed file parses with `version: 1.0.1` and the other keys equal the base's; tests/acceptance/W2-128/test_w2_128_templates.py::test_s2_prose_is_within_r3_budget and ::test_s5_every_key_placeholder_is_in_keys_yaml pass for all seven\"\n  - line: \"The cases of W2-128, W2-152 and W2-153 that read the role templates still pass with the new text (the gov brief golden files, the template tests, the launch delivery) [DEC-1050, DEC-1116]\"\n    verify: \"`PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-128 tests/acceptance/W2-152 tests/acceptance/W2-153 -q -p no:cacheprovider` exits 0 in the ticket's worktree, run through the heavy-job gate\"\n",
      "chunk_id": "63a432a2da45dee960b63f6e",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "7469cbdf69f9e4d2c524897d",
      "sha256": "2f22bac5049dec629abc5fd6b115ce6ace79975f308228d3d5f30457039e24cb",
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "start_line": 30,
      "end_line": 36,
      "text": "## D5-ROWS\n\n| rows | state | where it lands |\n|---|---|---|\n| 1-9 (the CTO's lines from 2026-11-03) | **READY on `w2/W2-128`**; added to W2-128 as one KPI line (string test per row; marked DEC-1109 (2)) | T-4 (1, 7), T-5 (2), T-7 and T-8 (3, 4, 8, 9), T-0 (5, 6) |\n| 10-17 (LINK-INTEGRITY \u00a75, the lines per recording role) | **entered** in `D5-ROWS.md` today (the CTO's step); **READY on `w2/W2-128`** under W2-128's link-lines KPI line | T-0 to T-8, T-1, the record templates; the skills' halves (orchestration, test-design, audit) in TPL-6 S3's CIT-P |\n\n",
      "chunk_id": "7469cbdf69f9e4d2c524897d",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-8s85",
      "sha256": "9f027e5caba37b3539614caba9c6def4b5228947bb8e24654e82c2fb53a6336a",
      "path": ".tickets/DAEO-8s85.md",
      "start_line": 69,
      "end_line": 82,
      "text": "# W2-153 The role template delivered at launch (W2-128's code half, part 2)\n\n**Why.** R3-1 to R3-3: role files never reached launched sessions. W2-128 (`DAEO-t8mp`) wrote the templates; the CTO\nsplit its code half into W2-152 (`gov brief`) and this ticket (a delegated P2 under DEC-1112 (3);\n`packages/LIFT-1/D5-STATUS.md`). W2-128's S9 is built here; W2-128 closes after both.\n\n**Interface (D5 row 9, stated before the pair starts).**\n- **The role \u2192 template map** (one constant in `launcher.py`, reused by the portability check): engineer\n  `role-engineer`, independent-test-designer `role-test-designer`, independent-auditor `role-reviewer`, product-spec\n  `role-product-spec`, research `role-research`, lead and orchestrator `role-lead`.\n- **The flag** is appended to the CLI arguments the launcher builds (after the caller's), as\n  `--append-system-prompt-file <absolute path>`; `<root>` is the launch's repository root (the worker's worktree).\n- **The skills lists:** engineer `[test-driven-development]`, independent-test-designer `[test-design]`,\n  independent-auditor `[audit]`, product-spec `[change]`, research `[discovery]`, orchestrator `[orchestration]`; the\n",
      "chunk_id": "ae6dc8a609990ca13074a560",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "2e35f466c5968b7ffcc31dce",
      "sha256": "77eda67853ff15eb9fd4c06ff4328d062a16c55f1366d616cdadf214701b456b",
      "path": "governance/project/orchestration/packages/LIFT-1/D5-ROWS.md",
      "start_line": 18,
      "end_line": 23,
      "text": "Rows 10 to 17 are LINK-INTEGRITY.md \u00a75's lines per recording role (DEC-1073 (5)(c), adopted by DEC-1074 (7)); the\nfull lines are in \u00a75, and W2-128's link-lines KPI line verifies them. Entered by the CTO, 2026-11-09 (DEC-1109 (2)).\n\n| # | template | the line | why (today's evidence) |\n|---|---|---|---|\n| 10 | every role (T-0, the commit form) | `git commit \u2026 --trailer \"Task: {ID}\" --trailer \"Role: {ROLE}\" --trailer \"Implements: {IMPL}\"`: `Task:` the `DAEO-\u2026` id, never a W2 id; `{IMPL}` only ACCEPTED ids from `sources:`; an id not in `sources:` goes in `discoveries`; a PROPOSED decision named \"proposed\", never as the rule | drift comes from links nobody is required to record (LINK-INTEGRITY \u00a72; DEC-182, DEC-927, DEC-1073) |\n",
      "chunk_id": "2e35f466c5968b7ffcc31dce",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-o5x1",
      "sha256": "f093873e318d5d80a14bf039ad3d5bfe10cfdc5e791b07a9e921a71843fdfe8c",
      "path": ".tickets/DAEO-o5x1.md",
      "start_line": 56,
      "end_line": 92,
      "text": "# W2-152 gov brief (W2-128's code half, part 1)\n\n**Why.** W2-128 (`DAEO-t8mp`) holds the templates; its code half could not be built on a product-spec ticket. The CTO\nsplit it into two engineer tickets (a delegated P2 under DEC-1112 (3); `governance/project/orchestration/packages/LIFT-1/D5-STATUS.md`):\nthis one (`gov brief`, the ready check) and W2-153 (delivery at launch). W2-128's S7, S6's S3, S10's S3 and S19's\nrefusals are built here; W2-128 closes after both.\n\n**Interface (D5 row 9, stated before the pair starts).**\n- **Command:** `src/gov/brief/command.py` (the CLI finds it as `gov brief`): `gov brief <role> <ticket> [--run <kind>] [--part <file>] [--repair <file>] [--root <repo>] [--json]`.\n  `<role>`: `engineer`, `independent-test-designer`, `independent-auditor`, `product-spec`, `research`, `lead`;\n  `<ticket>`: a tk id (`DAEO-\u2026`) or a W2 id, resolved in `<root>/.tickets/`.\n- **Inputs, read only:** the ticket's front matter and body; `<root>/governance/project/facts.yaml`; the kernel\n  templates at `<root>/template/governance/kernel/templates/` (else `<root>/governance/kernel/templates/`), with\n  `keys.yaml`. The role \u2192 template map: engineer `role-engineer`, independent-test-designer `role-test-designer`,\n  independent-auditor `role-reviewer`, product-spec `role-product-spec`, research `role-research`, lead `role-lead`.\n- **Placeholders** as W2-128's interface states (`{KEY}`, `{KEY: description}`, `{CMD:name}`, `{STEP:name}`);\n  `{WRITE_TREE}` is `{TESTS_TREE}` for a test designer and `{TREE}` otherwise; `{STEP:name}` is the step's `line:`\n  when `on: true`, and the whole line holding it is dropped when off.\n- **A KPI line has a verify** when it is `{line, verify}` with a non-empty `verify`, or a string holding `Verify:`\n  followed by text (so today's tickets need no rewrite).\n- **Output:** without `--json`, stdout is the brief text alone; warnings and the size line on stderr, each\n  `gov brief: <CODE> <detail>`. With `--json`, the API-0002 envelope with `result.brief`, `result.warnings`,\n  `result.size`, `result.budget`. A refusal is `GovError(\"BRIEF_NOT_READY\", \u2026)` with `details.findings` a list of\n  `{code, detail}`; nothing on stdout.\n- **facts.yaml** gains `ready: {new_since: <ISO date>}`; nothing else in it changes here.\n\n- **Clarified after the test design (2026-11-09, the designer's discoveries 1-3 and 7; DEC-1112 (3)):**\n  - a placeholder whose key is in `keys.yaml` but has no value from the ticket, the facts or the flags is a form key\n    the session fills itself (`{SUBJECT}`, `{COMMIT_PATHS}`, `{QUESTION}`, `{FOLDER}`, `{EXIT_FILE}` \u2026) and is left\n    as written; `PLACEHOLDER_LEFT` names a key not in `keys.yaml`, or a `CMD:`/`STEP:` name not in facts.yaml;\n  - a lead's run block is appended after the filled T-0 body as one contiguous block;\n  - T-0's front matter may be printed filled or left out (the cases ignore a leading front-matter block);\n  - `ready.new_since` is a quoted string (`\"2026-11-10\"`), and the schema requires the date form (`format: date` or a\n    pattern), so `\"soon\"` is refused.\n\n**Not here:** the launcher flag and the generated copies (W2-153); the templates' text (W2-128).\n\n",
      "chunk_id": "c9e1da1d19aa9547a1a2f767",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 1
    },
    {
      "id": "a29738413e3618fe525dab1a",
      "sha256": "edac49d324da15dd9a7e17fbd668e4606c82d50bf1407138880e94994e2f5fb7",
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "start_line": 44,
      "end_line": 66,
      "text": "## W2-128's KPI lines (21 success, 7 failure)\n\n| line | state |\n|---|---|\n| TPL-1 S1, S2, S3, S4, S5 | round 1 |\n| TPL-2 S1-S4 | round 1 (S1, S2, S4); S3 round 2 |\n| TPL-3 S1-S4, S6, S7 | round 2 (the split) |\n| TPL-3 S5 | scripts done; the facts line round 1 |\n| TPL-4 S1-S4 | round 2 (the split); the ACT for the owner |\n| TPL-5 S1-S3 | round 1 (schema, T-1); the ready check round 2 |\n| TPL-6 S1-S4 | after TPL-4; Appendix A for the owner |\n| TPL-7 S1-S3 | not started (the CTO's tools, after round 1) |\n| TPL-8 S1-S3 | last |\n| the link lines (DEC-1073 (5)(c)) | round 1 (the string tests; the planted-record `gov links` case where `gov links` runs in the sandbox) |\n| the facts' `links` command | round 1 |\n| the three schemas' `sources` / `decisions` | round 1 |\n| the CIT-P record and the `.claude/` ACT | the record's draft round 1; the review, the owner's approval and the ACT after round 2 |\n| the reviewer's reversal line (DEC-1014) | round 1 (T-6) |\n| the dependency fields (DEC-1088 (3)) | the template round 1; the ready check's refusals round 2 |\n| search again once (DEC-1092 (1), DEC-1094 (4)) | round 1 (T-0 and T-8). W2-142, the kernel skills' half, is merged (`984a3ba9`, review READY) and lands at the lift's re-pin ACT |\n| D5-ROWS 1-9 (added today) | round 1 |\n| the seven failure lines | with their success lines' rounds |\n\n",
      "chunk_id": "a29738413e3618fe525dab1a",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "WAVE-2-WBS",
      "sha256": "ba2ce5e512901e4e5290475240be77addb7d7ca8171096730fd8953dcef82d39",
      "path": "docs/plan/WAVE_2_WBS.md",
      "start_line": 1858,
      "end_line": 1860,
      "text": "#### W2-153 The role template delivered at launch: gov launch and the dispatcher pass it as the appended system prompt, refusing without it; the subagent bodies and the template copies generated and checked byte for byte (W2-128 TPL-4; the CTO's split, DEC-1112 (3)) (STANDARD, engineer)\n- **Ticket file:** `DAEO-8s85` (in_progress); its KPIs, paths and sources are there.\n\n",
      "chunk_id": "04aef43580b6c6ad305ad52d",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DEC1131-ONE-BAR-CIT-P",
      "sha256": "91c973b92569656632fb431da36873c01f2fcc4fc726d29b223e032fd168e535",
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "start_line": 397,
      "end_line": 420,
      "text": "### 5.3 The independent review (CAP-33 step 4)\n\nOne fresh read-only reviewer who did not write this record, under the rule itself: at most two rounds, each finding\nnaming the section of this record, the Contract item or the decision it fails, or a row. The CTO briefs it with\n`role-reviewer.md` and this record's path only. **Its checks:**\n\n1. **Verbatim \"before\" text:** every quoted \"before\" in section 2 is in the file at that line (Grep).\n2. **Nothing left behind:** after the edits, no kernel or project text states \"three iterations\" or \"three consecutive\"\n   for a role's rounds (only for the loop with no KPI line), nor \"per declared round\", nor the three-part test as the\n   only block, nor `role-reviewer.md` line 24's old words. (Grep over `template/`, `governance/project/`, `.claude/`.)\n3. **Text R is one text:** the four copies (JUDGEMENT.md, the lead brief, the auditor brief, prompt section 14) are\n   identical but for the stated \"KPI line\" reading in the auditor brief (diff).\n4. **Contradictions closed:** DEC1010-REVIEW's two (`role-reviewer.md` 24 against DEC-096; `role-lead.md` 42 against 48)\n   are gone, and no new one is made (the mechanical loop at three against the roles' two is stated in each place).\n5. **Budgets and form:** each role template's prose within the `facts.yaml` budget (`prose_size`); each added rule line ends with an\n   ACCEPTED decision id; `python3 -m gov.check.schema` still validates every record with the optional `id`; the new\n   `{LEDGER}` key is in `keys.yaml` and `facts.yaml`.\n6. **Tests that read the text:** W1-35's orchestration clauses and W2-128's template cases hold (a scoped run by the\n   product-spec ticket, never the full suite, DEC-968).\n7. **Recount** of W2-20 from `git log` and its review records (section 1.4's limit), and of one ticket the table says\n   kept to two (W2-141).\n8. **D-1 to D-9** (section 1.5): does each stay inside DEC-1131's words? The reviewer names any it reads as wider.\n9. **Ledger seed:** each row matches DEC1010-REVIEW 3.1 and 3.2.\n\n",
      "chunk_id": "e561c056f4a243166449ef17",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2,
      "status": "PROPOSED",
      "in_force": false,
      "not_in_force": "PROPOSED"
    },
    {
      "id": "DAEO-t8mp",
      "sha256": "fd1a67361d3be5d7b68a04b81729f53d1a7e8419aff606252488d5b6c46144f4",
      "path": ".tickets/DAEO-t8mp.md",
      "start_line": 27,
      "end_line": 39,
      "text": "- template/governance/kernel/skills/orchestration/SKILL.md\n- .rulesync/subagents/*.md\n- template/.rulesync/subagents/*.md\n- template/.rulesync/skills/*/SKILL.md\n- governance/project/facts.yaml\n- governance/project/orchestration/brief-gaps.md\n- tests/unit/templates/test_w2_128*\n- docs/changes/W2-128-CIT-P.md\nkpis:\n  success:\n  - 'TPL-1 S1 template/governance/kernel/templates/ holds T-0 to T-8 as in R3-TEMPLATES.md''s Appendix, each with name, version and role front matter. Verify: a unit test lists the nine files and parses their front matter [DEC-1050]'\n  - 'TPL-1 S2 The prose of each template (fenced tables of paths and commands excluded) is within R3 \u00a7C''s budget. Verify: the test measures the characters [DEC-1050]'\n  - 'TPL-1 S3 No template restates a rule that DEC-957, DEC-959, DEC-963, DEC-1010 or DEC-1050 superseded: the engineer template holds no instruction to read tests/acceptance/; the test designer''s permits reading code on w2/integrate; the reviewer''s carries the verdict block in DEC-1010''s form. Verify: string tests on those three facts [DEC-957, DEC-959, DEC-963, DEC-1010, DEC-1050] (folds W2-11b S1, F1)'\n",
      "chunk_id": "e83c91ae4c3ae76f3a876eae",
      "routes": [
        "lexical",
        "semantic",
        "closure"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-wahn",
      "sha256": "4c527e56598aea9d992b3b1f87a2134a37d5032751daa127da1ae3792c393c6e",
      "path": ".tickets/DAEO-wahn.md",
      "start_line": 28,
      "end_line": 46,
      "text": "# .claude/templates/role-*.md out of the paths: byte copies of the kernel templates, written only by the copies ACT after the owner's approval (DEC-315, as in W2-128)\nreads:\n- template/governance/kernel/templates/**\n- governance/project/facts.yaml\n- docs/changes/W2-128-CIT-P.md\n- governance/project/orchestration/packages/LIFT-1/TEMPLATES-APPROVAL-1.md\n- governance/project/orchestration/packages/P1-W2-11-BRIEFS.md\n- tests/acceptance/W2-128/test_w2_128_templates.py\nneeds:\n- template/governance/kernel/templates/role-engineer.md     # W2-128's text as approved (DEC-1116), version 1.0.0\n- template/governance/kernel/templates/role-test-designer.md\n- template/governance/kernel/templates/role-product-spec.md\n- template/governance/kernel/templates/role-research.md\n- template/governance/kernel/templates/role-reviewer.md\n- template/governance/kernel/templates/role-lead.md\n- template/governance/kernel/templates/role-cto.md\n- template/governance/kernel/templates/brief.md             # its return section holds the stop sentence the role templates repeat word for word\nwaits_on:\n- ref: DAEO-t8mp\n",
      "chunk_id": "ff4d48a7d7689893f5709b84",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "5e76fcf0db4a86c050406707",
      "sha256": "0458a0a2db3f9c1c6057eb11cd47e42e74b47abfe6694bb055d4cc4296e5ce3e",
      "path": "governance/project/orchestration/packages/LIFT-1/SEVEN-ANSWERS.md",
      "start_line": 126,
      "end_line": 162,
      "text": "## 3. The links\n**W2-92 built** (merged `3679ca0b`, 11-05 16:55; **not in the live pin**; it rides window 4):\n\n| kind | count | what an agent sees |\n|---|---|---|\n| UNDER | 2,481 | |\n| CITES | 1,679 | |\n| AMENDS | 388 | |\n| OF_TASK | 381 | |\n| SUPERSEDES | 7 | |\n| **statements** | **3,171** | the census's, one for one |\n| one bounded hop | at most 12 records of 2 chunks each, after the closure's chunks | CITES, UNDER and OF_TASK followed out; AMENDS and SUPERSEDES followed in |\n| status in the bundle (S9) | every register item | its entry, status, changers, in force or not |\n| drift (S10) | 190 decisions current though stated changed (83 with no hint in their own entry) | before the links 0 reached a changer; after, 190 of 190 |\n\nIts measured effect on retrieval: 106 against 105 on the 138 (DEC-1071's measure). The links help an agent see\nstatus and changers, not hit@5.\n\n**Still open:**\n\n| item | what | state | date | needed before the experiments? |\n|---|---|---|---|---|\n| W2-129 (`DAEO-q7lk`) | `gov links`: a record's links listed | open, tests first | filed 11-06 | no |\n| W2-130 (`DAEO-q8cl`) | marks for the drift found | open | filed 11-06 | no: it would change register text mid-experiment (a confound) |\n| the 150-id sitting | 110 spent and 40 PROPOSED decisions, each given a status by you (DEC-1074 (7) O2 (A)) | waiting on you | 11-05 | no; but until then a spent rule shows as in force, and a reader may cite it |\n| W2-128's link lines | the templates name the links | in W2-128 (open); its tests need W2-129, but `depends_on` is empty | 11-06 | no |\n| commit trailers, free-text citations, capability links | not built; no ticket | LINK-INTEGRITY \u00a77 places them after | 11-05 | no |\n\n**Recommendation:**\n- Run nothing of these before the experiments.\n- Run them in LINK-INTEGRITY \u00a77's order right after: W2-129, then W2-130 with your 150-id sitting.\n- Add W2-129 to W2-128's `depends_on` (a record fix).\n- **One design point:** the experiments must run on window 4's product commit, not the prototype clone (`e884675b`),\n  so that bundles carry S9's status as the product shows it (\u00a77).\n\n**Impact:** no delay before the experiments; about 1 day for W2-129 and W2-130 after them.\n\n",
      "chunk_id": "5e76fcf0db4a86c050406707",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "a8b466eea2056931e493c44d",
      "sha256": "cda9992053c85f55d1b021b1c654eb0ee540263a6e7f8a1d6752f732a6f8d668",
      "path": "docs/changes/W2-153-evidence.md",
      "start_line": 11,
      "end_line": 11,
      "text": "| S3 | The six `.rulesync/subagents/<role>.md` and `template/.rulesync/subagents/<role>.md`: their rulesync front matter as on integrate, plus `skills:` (the ticket's lists, D-1), then the body of the kernel role template (D-2). `portability._kernel_findings` compares a role that has a template with that composition (body of the template, the `skills:` list) in place of the role file's text; the role file's Tools field is still compared with `claudecode.tools`. The test designer's list is `[test-design]`: W2-128's round 2a reconciled that skill with DEC-963, so the \"until W2-128\" exception and its comments are gone (switch-over round) | `test_w2_153_portability.py` S3 cases; `test_this_repositorys_sources_are_the_composition`; the existing `test_portability.py` unchanged and green |\n",
      "chunk_id": "a8b466eea2056931e493c44d",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "W2-128-CIT-P",
      "sha256": "2cdd6262a031a6831aef2881f64d765717abc61209e4b07726681ea7a98efdb0",
      "path": "docs/changes/W2-128-CIT-P.md",
      "start_line": 16,
      "end_line": 23,
      "text": "# W2-128: change-impact proposal (CIT-P) on the kernel templates, schemas and the engineer role line\n\nThis change gives the kernel one template per role, a ticket template and a brief envelope, filled from the ticket and\none project facts file (`governance/project/facts.yaml`). It touches kernel files (templates, schemas, a role line), so\nit goes through CIT-P under CAP-33. The owner approved the scope when the ticket was filed (DEC-1081 (2), DEC-1050\nTEMPLATES); the interface was stated before the pair started (DEC-1109 (2)). This record is round 1's draft: the text\nhalf. Round 2 (the code half: `gov brief`, the ready check's refusals, the launcher flag) adds its own lines here.\n\n",
      "chunk_id": "126760f729c16b2ed6867747",
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
    "duplicates": 90,
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
      "chunk_id": "dfef0059bbd6a036a299fdc9",
      "parent_id": "eb3e1d135fa2a061cc6c95d4",
      "path": ".tickets/DAEO-t8mp.md",
      "start_line": 104,
      "end_line": 123
    },
    {
      "chunk_id": "c9e1da1d19aa9547a1a2f767",
      "parent_id": "31c330819ec7462047c12f02",
      "path": ".tickets/DAEO-o5x1.md",
      "start_line": 56,
      "end_line": 92
    },
    {
      "chunk_id": "a29738413e3618fe525dab1a",
      "parent_id": "0aaecf7ab056841ef166cce6",
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "start_line": 44,
      "end_line": 66
    },
    {
      "chunk_id": "e561c056f4a243166449ef17",
      "parent_id": "9d52a858b102585789bfb68f",
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "start_line": 397,
      "end_line": 420
    },
    {
      "chunk_id": "5e76fcf0db4a86c050406707",
      "parent_id": "2a5a984862cd43aef16e6de9",
      "path": "governance/project/orchestration/packages/LIFT-1/SEVEN-ANSWERS.md",
      "start_line": 126,
      "end_line": 162
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "id": "DAEO-03ub",
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
      "id": "DAEO-0z8c",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2bdu",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2ds6",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-2tfd",
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
      "id": "DAEO-57hm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-a3u2",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-blwa",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-cb2b",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-clon",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-csj8",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-cv58",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-emq1",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-f58b",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-g0ip",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-h2k3",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ha8z",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-jpr0",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-jsg1",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-k4wm",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-k7hz",
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
      "id": "DAEO-mb2t",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-n0wb",
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
      "id": "DAEO-ozyt",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-pg6i",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-qzrq",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-r30l",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-r8vq",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-siiz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ts4y",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-u4oz",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-wahn",
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
      "id": "DAEO-xxxx",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-ym8a",
      "reason": "DEPTH_LIMIT_REACHED"
    },
    {
      "id": "DAEO-zmo4",
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
      "path": ".tickets/DAEO-wahn.md",
      "chunk_id": "a76d86ecbf8cc4760c5ec5ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "aa8a990e1aa0e13623b1b065",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "36a558cf0d3c74c1370c9045",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "d70a321ddc2feb3671dc9ded",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "6e39385961326d5e06e579cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "a0d49d11e8911ce8e826c6d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wahn.md",
      "chunk_id": "861b0b0bda4ccc6c4a5e021b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-o5x1.md",
      "chunk_id": "5cf8077e5d26179003e75535",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "b5517ea41db1b5a6f50f1704",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "e491b24bda071985a2779364",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-o5x1.md",
      "chunk_id": "56829f6a3b013574e64044f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wahn.md",
      "chunk_id": "7631a05c6fe76ab4fb9f105a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-o5x1.md",
      "chunk_id": "b0ef865074d5cd7062a55fb4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "4475632159a1162afd0f1e48",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "ccafa88126de69fc327b2162",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "e2122cab5dd38d31144a83f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "6fc922d8e481ac42a4c8c73d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-o5x1.md",
      "chunk_id": "f4cf1a0fc93c3cd361fa2086",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "8595319e5507595c48040dee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-o5x1.md",
      "chunk_id": "be438f5c8ca17555d87b8ffb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-175-CIT-P.md",
      "chunk_id": "e5f56c3e6c8c791510a2572e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-o5x1.md",
      "chunk_id": "6f8b03cdf599e184bf9cbd65",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-175-CIT-P.md",
      "chunk_id": "c861a29434186e72a2d57735",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r2a.md",
      "chunk_id": "4b9a8276caa00405ea0e23c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "8493c0b5816404c9645b69d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-o5x1.md",
      "chunk_id": "ed113d4693b194474f8781f2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/W2-128-tpl101-review-r2.md",
      "chunk_id": "43b0fa2949eef599a65400ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "chunk_id": "f4ea2537fdf0fa2ba97f18a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-128-CIT-P.md",
      "chunk_id": "b340a3c050414c13e23328e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r1.md",
      "chunk_id": "23328a380f0cf52ed718f745",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "4e74bacf8d165f938e3aca31",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-128-DAEO-t8mp.md",
      "chunk_id": "d2737274c770e78d09a8ea81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "2eb0a3428adaf7588ae1595f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r2b.md",
      "chunk_id": "4244dbbb269fa0e17b2c8d2c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "a93a23e8bdb9ac964c4ef9a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "1d7df1c1d7a77f9f3f3849ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-128-CIT-P.md",
      "chunk_id": "07d153778e4fb7a2fcb15e15",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "2a78d50794d00188401e7d4f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wahn.md",
      "chunk_id": "fac09cd64202123c2d1cc7ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "f22a6e42a695152a99f6bcef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r2b.md",
      "chunk_id": "80bccdbefecf513ce71b4c81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r2a.md",
      "chunk_id": "108880130183469a90b4776f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "a9a3cdd6423d625d2a03ad2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "37b0b788b7071778264b2d4f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r2a.md",
      "chunk_id": "d371dc58d6155fc3f34dde43",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "1daaaf1826319b4cb70bd628",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "120965e2e3871cf02d462c83",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r1.md",
      "chunk_id": "a874e9253244038f5dd37413",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r1.md",
      "chunk_id": "1737fd2f24ce21f5b00e1af7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-3d3o.md",
      "chunk_id": "78f82b7703c142a8f7f3c008",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "f5c44f4f1dd2c2be22eb79d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY-tickets/W2-129-gov-links.md",
      "chunk_id": "7d3ae39a1cec6e2bc466d7ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r2b.md",
      "chunk_id": "1da7d61b9c0de9ccaa6eb70f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "5729cc375cf70a6c97a9fbb8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-33-CIT-P.md",
      "chunk_id": "5f9081463e8e5bc4db4262ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "fbc194ca64b184b36edb9ba7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "c1fb187684d26b80c226a47a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-8s85.md",
      "chunk_id": "0d413716649d8e75bfc5aadf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wahn.md",
      "chunk_id": "5582aa3bf9412c3148712274",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r2b.md",
      "chunk_id": "6079e94829c8d545fb2ba3bd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r2a.md",
      "chunk_id": "f01f72334ffa0378f1138628",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "f59cf177e3f27866b03038fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-175-CIT-P.md",
      "chunk_id": "7a8ee9a3bd3dbbae051189df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "6a0db77ff478efaf83c5f1e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r1.md",
      "chunk_id": "8433aa4a3ba09a2ddee12312",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-q7lk.md",
      "chunk_id": "0aacd67a080e05ccfb4bd6f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "f2ff83b9c1de2b1952e36003",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-ROWS.md",
      "chunk_id": "9af108faff5946d2242d91b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/W2-128-tpl101-review.md",
      "chunk_id": "78903159b0bc520a80b3bbef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "4d3f30eb4feaa8ac2b1b16e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "d482bcef7ec947444da468a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "e0a1a03ed4820bf89a1cf4d4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-3d3o.md",
      "chunk_id": "35c2d61ec1f845bb9b261bb9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "148ed5d13f7e5929447b2773",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/W2-128-tpl101-review.md",
      "chunk_id": "48c81d141708c18aaa5d87b5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "a7786cfd2570f2545901340d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "1829ddfce73ead216e350916",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/W2-128-tpl101-review-r2.md",
      "chunk_id": "0aea075b573059a71017be8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "6d963f380de407cf518b1d6b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "ee2efb3e8fab831035253eda",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md",
      "chunk_id": "4bc7305094587be38c333f92",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "5d8e6b700d825ec0a44625c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/links/check.py",
      "chunk_id": "cca4ef41e7b3f0a1322a8dec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "c11feda957501de1f672da40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "chunk_id": "4e661ab96eb4c2dbea8c42f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "8271d4ae5a36e8233c0750b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "359e095bf5ec883a4d7beb61",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/W2-128-tpl101-review.md",
      "chunk_id": "80c50efbd00734d0403fe814",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "7a7db801570b4e1a1563c739",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/W2-128-tpl101-review-r2.md",
      "chunk_id": "11772455461348a0568684ff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/c2-ticket-lines.md",
      "chunk_id": "283987ac5a648de65170d827",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "eb15072ac692f119b49a0adf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-33.md",
      "chunk_id": "bd67db30fe765d46b4037c11",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/contract/capabilities/CAP-33.md",
      "chunk_id": "91144f8645da5ea2a37f6b06",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md",
      "chunk_id": "14c3f2a9f199e5d95ab1017e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "eb88d84ad3e86acb0052f491",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "ba6ec487494f7e5749ebef00",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-08-review.md",
      "chunk_id": "4ebf518000c0f3e278df9785",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ROLES-SPEC-1.md",
      "chunk_id": "88178b0cdd63fa13bb279a6f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "ed9a22ecab26ac4f70f75b0d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-h4rh.md",
      "chunk_id": "914182188f3cdc66859e4e5f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/W2-128-tpl101-review.md",
      "chunk_id": "2d50c3c17de18a2f143f2f62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "9074eb8acd2837126be23480",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/W2-128-tpl101-review-r2.md",
      "chunk_id": "caa9d4c6797aac175734a045",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "67b8971a3b20d68be7d1513b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "fb0e2cf9927169ab33ccca68",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_REVISED_PLAN.md",
      "chunk_id": "7277b1d2f94940baa45a422a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "a5d83426dd652c3679e7a664",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ROLES-SPEC-1.md",
      "chunk_id": "5ba64a5a5b8e9590241bf502",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/schemas/facts.schema.json",
      "chunk_id": "2b31f7c9a5d8472795bb539a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "adb41eca1a8cc8785073fd8b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "11dc06ef4912850cd31986b1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/GLOSSARY-1.md",
      "chunk_id": "3e253287b968a230c28476bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "5dbcf855bb7e0b5096331dd2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "7800ab50c8116ba63b3d54db",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "87a344a83782102c45f627dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "905b0e6a7081202acba3501d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-o5x1.md",
      "chunk_id": "93110d2f7ebf4c69739c0e5b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-08-review.md",
      "chunk_id": "b36e0d54561644520027b0f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "2873cd4cf35563c5e9d9e770",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-ROWS.md",
      "chunk_id": "6cd7401e825c53feef9a4d94",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "79b22c6bfa2883ad81ce0ca6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/TPL6-APPENDIX-A.md",
      "chunk_id": "14fe2d96ea566e48c00280a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "bcc1cb1d3a9752c7987c13b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-o5x1.md",
      "chunk_id": "b65eb3195c1e050011d7866e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "4edf5a743afd2af4b27e4509",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-08-review.md",
      "chunk_id": "31f2007dbb64a469e8eac491",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/bootstrap.md",
      "chunk_id": "ab6544ec6cc23037e6569231",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "ab7209b865d3c39058f862f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "4f6fa09bd11301c5d4f6da5f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/W2-128-tpl101-review-r2.md",
      "chunk_id": "0d2dcf8e9951adce56fb83ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "299f42e0298327e5d4e39222",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/README.md",
      "chunk_id": "ba779da8358352ecd4255c78",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "b9ea28a84a44b1978953f97b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "ff44ebfd2a5230ae1b356cbb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "76ebd5be21b2d624bbf06f84",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ROLES-SPEC-1.md",
      "chunk_id": "0c11041b567c8dbccbdcef9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "79e1c8d61af65cefbe738950",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "48b2ba27deb685d8a995fee0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-153-evidence.md",
      "chunk_id": "933230beb4da0505bcb0235c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k1us.md",
      "chunk_id": "00f1d983046608c27e1921c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "f8a83cb6323f0d3727931989",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "51638cf1edb271ef32bc5618",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "080c9b36f777219b92038a5d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "8cad10c2b04d837bc0dc8202",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "f3fa66c3fcf384e5a93752ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wahn.md",
      "chunk_id": "589811cb2b8a04be5d11ce9b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-11-CITP-REVIEW-r2.md",
      "chunk_id": "8eda7cbb459275b95855ce01",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "f4cf20fe17b7294f0c4d37a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-t8mp.md",
      "chunk_id": "61df2e6c8011508a560f8cf0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/TEMPLATES-APPROVAL-1.md",
      "chunk_id": "7e3005f674781c1b2b2d07a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "d78b127b86654acdaba6c4a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-153-evidence.md",
      "chunk_id": "39484eab08d63b7a8f27fe52",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md",
      "chunk_id": "43f3726226453ee73d84122f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "647fecb1ec4110b99eb98900",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1/ready-batches.md",
      "chunk_id": "5e8e06212362d7fd54026df4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p3ln.md",
      "chunk_id": "0d2d584b9a88336af4cb0f8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k7hz.md",
      "chunk_id": "cc450f095b58f506cd05c5f7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-153-evidence.md",
      "chunk_id": "13fd51092aaac48f7f80905a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_LIST.md",
      "chunk_id": "9d4441fdc25d5ef6a4d53fe9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/TPL6-APPENDIX-A.md",
      "chunk_id": "7ce502dc9475da42140f35bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/tools/validate_s1.py",
      "chunk_id": "9a28280e0687a41067bc0c00",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEARCH-AGAIN-PRACTICE.md",
      "chunk_id": "5b4432630f3d2ce7e16f973e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-129-links.md",
      "chunk_id": "056dc0cfaa3d8e5ac1df6018",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/README.md",
      "chunk_id": "5b62ec65d87462598e78e7f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wahn.md",
      "chunk_id": "3cbedea7cd99b5d90a40b521",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/role.py",
      "chunk_id": "256730fd2600d7cc6ead0f89",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-3d3o.md",
      "chunk_id": "a4aa5a9042396c2ed702746f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEARCH-AGAIN-PRACTICE.md",
      "chunk_id": "c9e711930841e7212e23bc93",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/role.py",
      "chunk_id": "eb89507e15df115bfabf1832",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/README.md",
      "chunk_id": "ccaca798285c27544ad0c4d9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wahn.md",
      "chunk_id": "e613e606322e0596365a8aee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-W2-11-BRIEFS.md",
      "chunk_id": "657cafe27cc83fec8ebb90de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "2d5f20d48bfce51f659cc4bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "2ccf1c0fc38ff91f49a422a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/README.md",
      "chunk_id": "69bf348959785259e88ba015",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "40df0b3f819474f59851d20f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/report.json",
      "chunk_id": "eba33b7ff14185d9ad767652",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/README.md",
      "chunk_id": "5bc9f95ffcf3be964b83b919",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEARCH-AGAIN-PRACTICE.md",
      "chunk_id": "698015cb12ece3020eba541d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "6055053cf89a89b98f22a7c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "cb5f83924c7534bd08449ca8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "1837c499c9ddbe51cbd5e230",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "d0695c13a65afdeb573a2243",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-9bc0.md",
      "chunk_id": "e2e333920a569ba33ace377e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/README.md",
      "chunk_id": "3b0aacf939e8ffa7aff73db1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-9bc0.md",
      "chunk_id": "c82eb1b63829894bf9309a8b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "273a808851632c08fe5bc2f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "e2652a7e28bd99281c31f77c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/GLOSSARY-1.md",
      "chunk_id": "b7fb5de95bf04373c40945dc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/conftest.py",
      "chunk_id": "57e0e9e4a45a1ad977af06a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-11-CITP-REVIEW-r2.md",
      "chunk_id": "030ee56c48b5f9c9f4153c50",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "c2e0639c144d7d8cea2ed6ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-11-CITP-REVIEW-r2.md",
      "chunk_id": "1517bf7270400d40d00e29a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_round2a.py",
      "chunk_id": "1e758253f9d48cea250deb16",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "03cb5d03d2170e4e2c92ed09",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "ee81e6c9d5bbacfae0ce55e1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/CIT-P-ONE-BAR-review.md",
      "chunk_id": "e162521e020b8d55f8b633b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "15551f5db586d09af7adb56e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "578baf761e0ba5b66babc48e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "78600d065e0a2bc344e860b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/CIT-P-ONE-BAR-review.md",
      "chunk_id": "f5430e5522458eca4554d980",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "c8789e5dfce80b026cf961bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2bdu.md",
      "chunk_id": "febb32f104afd003862bc208",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "04c65adf1b4e853ff2f77100",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "0f4fc62f4f75ed7989e6c607",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "3d3300af206ed21a5040bc45",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "965fdb8b2c6c0081ca63d3b1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "94c427855805e43e617f0ddc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "809524e894bdb9c6e97d12c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "16b2aacfbf3ce9325c23fc70",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "7438868158449e45ef0b5672",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "20b71b8677044f313a931a9d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEARCH-AGAIN-PRACTICE.md",
      "chunk_id": "de3cc6090cc24eb9ddc1292e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-11-CITP-REVIEW-r2.md",
      "chunk_id": "ae863ea79338806cc576fcd0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md",
      "chunk_id": "405e278f0f9d6b144250a674",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "734be742a42259e6bb77df4c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_facts.py",
      "chunk_id": "d809bc2e11600aaef5d8a80d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "afb0f602cf1906b22fb842a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "20f896c2d0622d90c0b925f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_schemas.py",
      "chunk_id": "56048820a50eff3c4d7cd711",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "536da2de51cb6aaeb61e0c5a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-4k3l.md",
      "chunk_id": "31100cbf43b267986ea39ac1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "7e82b361c5bb7c981e666c59",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_templates.py",
      "chunk_id": "7c76269e1b8f4bb88cbb4fc2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/02-memory-in-use.md",
      "chunk_id": "5eb7fb07b8fd5c4b41b69b75",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "fe5eb5ec116bbd7997487266",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wahn.md",
      "chunk_id": "a10a739e112712283e27d8e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "e1568fa09ccd8e186aed8a4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wahn.md",
      "chunk_id": "68ae77cfb00520ee82559fca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/02-memory-in-use.md",
      "chunk_id": "b291217cb923d5a12ee4b6a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5y8d.md",
      "chunk_id": "61f4c16f1c2fdf799ae956cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "2c002cae8afd3ad9ea5360df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "a28577dce8c783d6f0d8b2de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "b5be65bb0006459e22450459",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "4fb5dc319b97437f9002469f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "50317150bb78fac105d05e09",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "2a2c51f1ca49572437f65ecf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "989a1c674ca564968d98f01b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "02a02fc864d3291e457a004f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "41eaa7f99bd33ac2197a5ecb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md",
      "chunk_id": "7f4f2abaf223cc285c9d0c2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-35/README.md",
      "chunk_id": "dce5a9c8245dab266720573f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "3de79151e8803358a92db3cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "67ae12780b035284bc72c928",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "36c7b8413307b564f770be0e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-lxzn.md",
      "chunk_id": "3ad7019383690dd38bb61cb7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-4k3l.md",
      "chunk_id": "247d06b35771138a694ec586",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "4781c4b0f7d3fc67d35122fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "c7ab02b8c7a4f9cd38703130",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "33d395066a682ba04c2402e1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "a2f41de16a005a1df0db7855",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "6ef3bd6e41f2cee446246f6b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "24a0770b31a1632518b7ba78",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/w2_128_support.py",
      "chunk_id": "f9497d17c8f104a8cf2eb642",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/DEPENDENCY-MAP-1.md",
      "chunk_id": "0be598f744a6d9f19f051eb1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEVEN-ANSWERS.md",
      "chunk_id": "effaf320678ce6cae956adeb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "c6fb7154f141f70684737571",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-152-r1.md",
      "chunk_id": "efebf30a464f531a2148efba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/w2_128_support.py",
      "chunk_id": "839e7ee8ab8a1bc7347f932b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/E-roles-context.md",
      "chunk_id": "e9ef587bab66125a65b7b1c2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-9bc0.md",
      "chunk_id": "024aca3738abebb57c09104d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "4d1dd546c3a86a7db25d6b84",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEARCH-AGAIN-PRACTICE.md",
      "chunk_id": "34f8d21f921037b2570f2998",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "21de3ff850e491c66454e7b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "29b53dee038ea6ecd922a242",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "chunk_id": "89587bdc0742795ebab4e7f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-183-DAEO-href.md",
      "chunk_id": "7fe30717669a0eb18758b260",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "dd86a4b134a8edad43c48715",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-183-DAEO-href.md",
      "chunk_id": "9b6bca9cad90f68ed37b9519",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-152-CIT-P.md",
      "chunk_id": "34a5435902dd11a375a53a8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "710c86cba3c76d7b45c16281",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5y8d.md",
      "chunk_id": "2466d8f133673ce146251c98",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_round2a.py",
      "chunk_id": "0e3cfd55bc8edeb52e9e001f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-88a-DAEO-pg6i.md",
      "chunk_id": "8fe665132f0d17d8e6e32a00",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "71fa0400cf0487c8fedc9e11",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5y8d.md",
      "chunk_id": "fbbaba9a16c898b9c9681def",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "9cef25c1df273f34627c885d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/E-roles-context.md",
      "chunk_id": "87269f7d8d1732637470b2a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k7hz.md",
      "chunk_id": "bf963307679ecac9fbe58a10",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "c835bee3dff9ef21fc4b6864",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "bf9f3edfa15f1fa2f45d0220",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "aece8e50a9f7029b10048d88",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "6f62a973f949c0cb1228f69b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "d6e62b974b2bad8b73641581",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-3d3o.md",
      "chunk_id": "53850543959695cf7550f4dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-4k3l.md",
      "chunk_id": "2666f5d68d5b2fe7424ee536",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/DEPENDENCY-MAP-1.md",
      "chunk_id": "402fff7dffcad8a090e797c5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "699b1f90f828c5c3edc4f23e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "033da61a0a990c58dd3accc8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-W1-08-review.md",
      "chunk_id": "5c1ca13b8455eeb1d76a134f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2bdu.md",
      "chunk_id": "09141bea59d9b3c346c0f744",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/DEPENDENCY-MAP-1.md",
      "chunk_id": "19578ed33ee2afdb414ed287",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-152-evidence.md",
      "chunk_id": "38c2ecdb2da3c7959d72818c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "307a009b4e4a744d0050bfb7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "69f94ccf1d869b2af74d7e9d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/TRAILERS-UNPARSED-20261113.md",
      "chunk_id": "93109383b0831c68068504b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/DEPENDENCY-MAP-1.md",
      "chunk_id": "d4bc79bf3d9ed47eddfbd033",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "chunk_id": "cf6b07c9b98032401f6afda2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "c366d10eae340b4e13b00a98",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md",
      "chunk_id": "662828ad064f7f3cd8588358",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "5c2de9bf0dc9218d5c6a03cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEARCH-AGAIN-PRACTICE.md",
      "chunk_id": "187c4042e6d5068cf6323c56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "f37e4fd638b682ccb2480a7b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/CIT-P-ONE-BAR-review.md",
      "chunk_id": "d2bd48082f7741ebd952ddbd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "chunk_id": "a79c679caeb5c47b95ad36b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/E-roles-context.md",
      "chunk_id": "9f5b088ace965e764b6e253b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEARCH-AGAIN-PRACTICE.md",
      "chunk_id": "12bfd2ca93cc88c2d5ef4653",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "99805db740f805e72354f343",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "2abcfd983067ec0991c518ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-136.md",
      "chunk_id": "1d211aa7855d815d0f6c874a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-4k3l.md",
      "chunk_id": "efbad0ccd5bec4b8b60740f7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "e4cbd1efc46a8ea88849208e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "6aba156e090acf12aabf14c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/READY-AFTER-LIFT-1.md",
      "chunk_id": "37263c94904f597080c6d41f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES-AUDIT.md",
      "chunk_id": "af81994e20b44f38bd07aafd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES-AUDIT.md",
      "chunk_id": "8774b6681fbd232e38cb78a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2bdu.md",
      "chunk_id": "ebd25842b92efda317b7a2e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_rows.py",
      "chunk_id": "934f9694863a7d32c39ffb28",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-4k3l.md",
      "chunk_id": "2391e81216acced9fd387eb1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-2.md",
      "chunk_id": "2d697d1689bfa28b7d04e878",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2bdu.md",
      "chunk_id": "46e10070a91daecc4933c6c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "de7a15cbef252122029a5a17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2bdu.md",
      "chunk_id": "cbdb0f86dc14338929533ad8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "6eec151d6f074f7d8e414f5e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.md",
      "chunk_id": "ecb935acc66bec4468ff45fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "a71973ff578f06807b16230c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "f6f3dc0d26910ccdb0421dcc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "69141b994b7da55bc7518043",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/WAVE_2_WBS.md",
      "chunk_id": "61358264019ca23502c12c7d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "4784da605749592dcd087ff3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "33a59e604e8056a2c056a655",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "1b4ccc161225f7ebf71f66f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "9eecb12b7dd3f6f25f2680cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "268b27edbc2097e467ef63e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADOPT-VERIFY-1/APPROACH.md",
      "chunk_id": "3573578b6ac2ec90e7dc71b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-136-evidence.md",
      "chunk_id": "c68ea54a69eb530d64464812",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l4gf.md",
      "chunk_id": "dfd974a2797b3e51a87b81c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "2ac2d0ca6b06584accedd090",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md",
      "chunk_id": "9ac2533181a8f681e4edb1b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md",
      "chunk_id": "2b50c057bcb277f5fe5e4b1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-11-CITP-REVIEW-r2.md",
      "chunk_id": "332560f50524ff7f2ce38ed6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "306b12ef288065781b2f48d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "1583a1800a2d45925ad1d1aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-11-CIT-P.md",
      "chunk_id": "aa9bfd1b659a1ace2877380e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wahn.md",
      "chunk_id": "f73b8ddd8a786a5612e0bc1d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qskx.md",
      "chunk_id": "69e7ba0772205d9495e323e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "c8f91ce428148e964f30a439",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "f7725f907af1791b7b763e5f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES-AUDIT.md",
      "chunk_id": "23482d2188bc2ef54e0145cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/close/nightly/NR-20261119T163111Z-11532ee3821f.json",
      "chunk_id": "97679a202594d7e96db13f60",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "77747518fa65a415cf93e7e0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "chunk_id": "e66d1b95499bcd365895a0ff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-4k3l.md",
      "chunk_id": "da1ddac4908eff53e031446b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/L2-4-PROVING.md",
      "chunk_id": "69e4abef34d2bebcb0bad45b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-136-evidence.md",
      "chunk_id": "cfdfa3b76565ea3b66037a10",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-152-CIT-P.md",
      "chunk_id": "646f79fbb28b975dc2947f9c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEVEN-ANSWERS.md",
      "chunk_id": "a4f6f62cbbc5335428adebb8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/c-tickets.md",
      "chunk_id": "69967852052b45599e11b489",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "feca69bff6ee6d594874c60e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADOPT-VERIFY-1/TICKET-DRAFT.md",
      "chunk_id": "a118360b65cb3fbdb732458a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/launcher.py",
      "chunk_id": "d067b3f0d525bbc2fedbcd0e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEARCH-AGAIN-PRACTICE.md",
      "chunk_id": "5e8d092bd3e449b784c2053f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/CIT-P-ONE-BAR-review.md",
      "chunk_id": "3125686142f735e28336d723",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-152-evidence.md",
      "chunk_id": "00086dd78662d82db0ddc2ad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "d4eb2cb8ff25659febe6667d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "f694b74ba4eb7e5d4d8cafe5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "347299835b9b09b3ad6e753e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "57da6482320850a3daa88ecd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_round2a.py",
      "chunk_id": "3c6c045a866f861a7fab2bd2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "331b72a11642e3a5c5f04374",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "33d751e3d781e9c1458c84b8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-130-SITTING.md",
      "chunk_id": "eafdc78b20476aebb857aef1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/brief/build.py",
      "chunk_id": "d3b62cdcb8e2850de42fe7b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-4k3l.md",
      "chunk_id": "fc6fc75ed71940308cee5e0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/02-memory-in-use.md",
      "chunk_id": "781b94b191ad55ff48124111",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "185c99ccdd3c74b593b48d5f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_round2b.py",
      "chunk_id": "bfd5b55b448d097b62cfaeb2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "95959cdfb6ed49ec88f5f663",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "0dadc5c51a0f860a3b2ce8be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "2bae9f637c1adfb18d137e80",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "d6fd9b7695012b462e0095e3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-152-r1.md",
      "chunk_id": "ab2552fc20b4b6facec315d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "a9af683b4e79476ef0ff8314",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-152-r1.md",
      "chunk_id": "2b23137712ba780ebc4bf78d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_links.py",
      "chunk_id": "f54f92beac650ae55e0d0d17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "c285677fd5aa72da0cdd8584",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md",
      "chunk_id": "e3333b29a64c224f4219b33c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "09b188ffd56e25e678841653",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-2bdu.md",
      "chunk_id": "20f3c186d3847602d7a6f35c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/closes/W2-136-DAEO-p3ln.md",
      "chunk_id": "8958cbe36b7465aab186c4f7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "c86bc6c3b97d22ef973dfce3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "chunk_id": "cbe4a6c85949e23ba027895d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-153-s3-amended.md",
      "chunk_id": "42c6cea57f1c1d6a97a21d9f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "be7e622d745766806ca65b29",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "3a69991905d7255e7cee2c96",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "09530acf505aa658fad835f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-validator-review.md",
      "chunk_id": "31f719837cc8842ad36c569f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-153-r1.md",
      "chunk_id": "82cd5161f717fb2c59dd97d1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-152-r1.md",
      "chunk_id": "191702fb8ce3a7b61519c0f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/DEPENDENCY-MAP-1.md",
      "chunk_id": "8254ed026bc83ca143a0cf2e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "3438f4bd6b4650515a1fc178",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/04-classification.csv",
      "chunk_id": "7be0d8e7cf799c262c013aa3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "c4339bcfef9ba441463f4628",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-153-s3-amended.md",
      "chunk_id": "80b007bc642f096b21dd2939",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-4k3l.md",
      "chunk_id": "91a0669442267db06fe93346",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md",
      "chunk_id": "bd79e0502c9553d76e5aa81e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/L2-4-PROVING.md",
      "chunk_id": "1a1cfc0620a94178c7d2aaee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-153-r1.md",
      "chunk_id": "a7ce2970237ce281c9bd94a2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "71a853e31d6d276aad8385d8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_round2a.py",
      "chunk_id": "dffc904aed553b0398eda9bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "ed6f11b53f0961640fc1e97b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/CIT-P-ONE-BAR-review.md",
      "chunk_id": "dea81a1f4c5e224567d321ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-152-r1.md",
      "chunk_id": "b1dc78ca202d108c36f44be6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/02-memory-in-use.md",
      "chunk_id": "9d0018b04a89ad1bd4e57883",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "351491221b79917ad20fc08c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "0debddbcbccc2e536931ecde",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "22b780b1274fb883ac885f82",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "6f399091a2ae524a972ee95d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "8b51e971a543f9cd223496a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "chunk_id": "9e507d8a2bfddddebabc15cf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-fd0p.md",
      "chunk_id": "becd71986547db39dba8c05f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "b16797806da16dbb819dcdd9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-33-CIT-P.md",
      "chunk_id": "8ba675d6d03f9483c10eb987",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-130-SITTING.md",
      "chunk_id": "b91098af8925cc06a43136a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/02-memory-in-use.md",
      "chunk_id": "1888acf1a4602b4cf1254bcb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-commands-review.md",
      "chunk_id": "fd16dfd526e61034e29877ba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-152-r1.md",
      "chunk_id": "285b4c463b8fa72534bcd882",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "3b4c685a87361685b42ef043",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "e9587c7fe28d0fa3d80fca99",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-152-r1.md",
      "chunk_id": "8d4c617684685bf87dd424e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "c9dffe008fd39069b873ad15",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-153-s3-amended.md",
      "chunk_id": "6e100101c48933f5fa1596b8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-152/test_w2_152_facts.py",
      "chunk_id": "ec141891e3e5b6012498ad0c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/briefs/LEAD-w2-common.md",
      "chunk_id": "1a377a9482b10cdd4e3fd2c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D4B-MORNING-2026-11-05.md",
      "chunk_id": "37f45d92e7a3c09ceca128c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "2ace7ec468940311791213a3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-11-CITP-REVIEW-r2.md",
      "chunk_id": "94ee029a459c5a5357543f35",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-152-CIT-P.md",
      "chunk_id": "35bf40f6b55bfc7145e715ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "chunk_id": "678fe589c14a099d18abb5d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-88-STANDARD-1.md",
      "chunk_id": "cc4d3221e49fb0b9404ba7eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_round2a.py",
      "chunk_id": "7d3cbbd784c7320489f3053b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/CIT-P-ONE-BAR-review.md",
      "chunk_id": "cbf39f8db3b3102ba2548c04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "f9398265a3b840d5d1d8a254",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "db50a50671b6f0f6e6d26d8a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-11-CIT-P.md",
      "chunk_id": "9aa1d72414ec88eb307112c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/GLOSSARY-1.md",
      "chunk_id": "e1dd51a01ca02d07d4054ea1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEVEN-ANSWERS.md",
      "chunk_id": "cb46854abc803fc793e58750",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/CIT-P-ONE-BAR-draft.md",
      "chunk_id": "4a0a4c0dbaf5ceeedff618ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/02-memory-in-use.md",
      "chunk_id": "9b92871c008888e19c1d8ee3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_rows.py",
      "chunk_id": "9d54fa4ae46f8118582ebf4a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEARCH-AGAIN-PRACTICE.md",
      "chunk_id": "d6f1d87ba1f463eb05f16031",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-152-r1.md",
      "chunk_id": "573710660f2e2c29ef2f683f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-11-CITP-REVIEW-r2.md",
      "chunk_id": "b94b6a0501822c1fdfbcb967",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "8645b5d259aec8315fc7aa69",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "c3aaa61f7776e4ce714a2119",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "435a351fc26e53a491555bae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "97dff7f44dfdfd1077d29ebf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "e59835d576923af1d6b47ee9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/d-tools.md",
      "chunk_id": "66a158e51c931c4efc288f80",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "61480c198d32d454fa2313ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P1-MORNING-20261114.md",
      "chunk_id": "aa855a5cf8563da3e4cd382d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/CIT-P-ONE-BAR-review.md",
      "chunk_id": "8f1781346bbd381856c85325",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k7hz.md",
      "chunk_id": "5c9eae93a091512e9b8575ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/FRESH-80-READINESS.md",
      "chunk_id": "4065429968c2fdbc156e36e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_round2a.py",
      "chunk_id": "a7e72afc26aef6d3337799c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-2.md",
      "chunk_id": "41dbbe2cacaeebe0c5d278fe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "3b913fbe12826897c6e77821",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "f2acc5f86e390c2dbdf6ad56",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "a4a85495db96ee2c9abafdd3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEARCH-AGAIN-PRACTICE.md",
      "chunk_id": "d1af9189da6c375d1642d984",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "63beefca0c40488610c0c4ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/GLOSSARY-1.md",
      "chunk_id": "bc1d330dcb05cb60153af901",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEARCH-AGAIN-PRACTICE.md",
      "chunk_id": "d4c5371de3b93b83f2f0025b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "57791832555d5ffb41dd5214",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/USAGE-1.md",
      "chunk_id": "705d78bda628075498fc3229",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/D10-commands-review.md",
      "chunk_id": "f894aad1cdfb118a3f0ffd6e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/DEPENDENCY-MAP-1.md",
      "chunk_id": "4a094dbdb588e1869a769f3a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "03ad569aad0a2ce8dbc2fbcf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "af718116b13b091b265e61b4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/GLOSSARY-1.md",
      "chunk_id": "17ae6cfd4c0f5e3415e912bd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/SEVEN-ANSWERS.md",
      "chunk_id": "4895735cd7c55380639475e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/a-decisions.md",
      "chunk_id": "13f93de08f8e1df9e757756a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-4k3l.md",
      "chunk_id": "5214075dd10ecfd9ad4bffc8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-3.md",
      "chunk_id": "c82a2a323a2d1bc758a33acd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-11-CIT-P.md",
      "chunk_id": "070de8f1e3f3ad3cc2e72ccd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "3928702bc45cbfa748d42cad",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DEC1010-REVIEW.md",
      "chunk_id": "25be2b656f9b9b6cfb6ffd92",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "0c5ba439077fa4e596e3b6d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "2d0ab2246ff6e8c6dd9d3e6c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D10-REDS.md",
      "chunk_id": "14f786fb5cce0472157f0ce1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-l4gf.md",
      "chunk_id": "e2d4bf5639f283b04bdf5eff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "5dc126a6243f6affe9023774",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/RUBRIC-2-APPLY.md",
      "chunk_id": "b58caed2c7d97e64dff43f11",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-3.md",
      "chunk_id": "e05b7982ab5f770bb3b996c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-175/conftest.py",
      "chunk_id": "5b6628a87ac42e97d7396413",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-1.md",
      "chunk_id": "0d47a99f549d4258317985c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "ee26b1a27057cd19a91b424f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-LB-PRODUCT-1.md",
      "chunk_id": "ca4ba938cf10a9cd07b1de66",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "11b688c21b3cff5c55e3dd49",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "1c647bdb9b860f90cce187c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-2.md",
      "chunk_id": "5ce68b1bb6c0aed589951653",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "91a63096a56cfaca1985424c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/FORECAST-W2-2.md",
      "chunk_id": "f46bd6a8d8ef81e53ff68083",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D9-FATES.md",
      "chunk_id": "79fcea01f024316a38d199cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r3gx.md",
      "chunk_id": "57f159839006b595f4707085",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "9f06d4f04a4dace86f51f68a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-k7hz.md",
      "chunk_id": "afc74d87d47317da6e18e8b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/INTEGRATION-PLAN.md",
      "chunk_id": "431a1a1bcd469abbf1e405d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/DECIDED-NOT-DONE.md",
      "chunk_id": "f14f1bde602ec9f82e9bb1b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "74c6cec02170610c49c45c26",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/P1-PLAN.md",
      "chunk_id": "3e56c1bced3cef1bc9cc7b7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-128-CIT-P.md",
      "chunk_id": "3ace6144de4bcda6f464959e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md",
      "chunk_id": "a83580edf0069786cfbcda90",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-175/README.md",
      "chunk_id": "782a80a2131e80b6f8e0d8f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-128-CIT-P.md",
      "chunk_id": "64228b2d62004d2657df8499",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r1.md",
      "chunk_id": "56dc685432649f02b294fcfa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md",
      "chunk_id": "668a967bd5999e329d0ad8f4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "7ee9de6e85d56b666516de14",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-128-CIT-P.md",
      "chunk_id": "9606922b885fe21a987cd367",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-ROWS.md",
      "chunk_id": "156244d43abb451a0884bcaa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-ROWS.md",
      "chunk_id": "b9d751958e7462d6233d7d13",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/facts.yaml",
      "chunk_id": "cb6cee0bf853931faa26dda1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md",
      "chunk_id": "ab407ef61eb0292ea28cfc91",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md",
      "chunk_id": "202f767572da6298a78170fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "11fa1d75310ccc1f9faf1c16",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-152-CIT-P.md",
      "chunk_id": "22a1db2c102c3a80ec2338a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "f1179231dc38ebffd54a1d4c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-zmo4.md",
      "chunk_id": "f17f83b5e874206c650bf4d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md",
      "chunk_id": "eef12a7b17d6079f84650fcc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "47a0a1cdbf2708c6e9a549ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md",
      "chunk_id": "6e89a67955608addebfab380",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-153-r1.md",
      "chunk_id": "ffbeae6a9887c20b6c41b889",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D5-STATUS.md",
      "chunk_id": "73dac67ded5e1086f612bdb3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-128-CIT-P.md",
      "chunk_id": "8bacdd4d6ca20d0cc9c382d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md",
      "chunk_id": "eca1c68909705da8c3124a40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_round2a.py",
      "chunk_id": "5f8346ba81a7aeab43ad3632",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md",
      "chunk_id": "dea7b49a974d2c3a2d1726a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-128-CIT-P.md",
      "chunk_id": "92f326a4990ebcb8534466b3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/01-landing-templates-briefs.md",
      "chunk_id": "6df6b4e987d6fe42f213d662",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/schemas/facts.schema.json",
      "chunk_id": "4040773c477be81ab05b64e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-wahn.md",
      "chunk_id": "3e34ec96cdbaa24f96a27fa7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/CIT-P-ONE-BAR-review.md",
      "chunk_id": "b008ead04493e2d30ce5ac7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "23f093577f366d325d29f467",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/c-tickets.md",
      "chunk_id": "5eb76b85e2d55f48eb7136cc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-qskx.md",
      "chunk_id": "e25373f4bc0fb643f6400501",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-fd0p.md",
      "chunk_id": "a4fe2eaf16eea2fefe9aafbc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "ec2aa1b9a346b1e4b218fb63",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/ADOPT-VERIFY-1/TICKET-DRAFT.md",
      "chunk_id": "07a7e8c886fa2e03e6bf65eb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/c-tickets.md",
      "chunk_id": "17360fda4736cfd11a6d3482",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-130-link-cleanup.md",
      "chunk_id": "f6dbad1a03d3cefba96c6248",
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
      "path": "governance/project/orchestration/reviews/w2-128-r1.md",
      "chunk_id": "16cb97391b7942034b02dfcd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r1.md",
      "chunk_id": "29dc54134fde00539a5ef0a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r1.md",
      "chunk_id": "4ee8c1e7b73e4fa30e90a791",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r2a.md",
      "chunk_id": "6129bac21ce5eb5b4a7a4e85",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r1.md",
      "chunk_id": "a393e3176f96103038c2bdc7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r1.md",
      "chunk_id": "c299378ccc2eec710ec04817",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r2a.md",
      "chunk_id": "592f14030fdce7bd2edd5f5d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r1.md",
      "chunk_id": "39b0ec71c75799ba842da767",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/W2-128-tpl101-review.md",
      "chunk_id": "3692df880fad7fe697a6e7d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r1.md",
      "chunk_id": "7a2063c808e7449812406dff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/W2-128-tpl101-review.md",
      "chunk_id": "15c82a32278173f9f10ad52d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r2a.md",
      "chunk_id": "8aa9da3e42ac135a8fce13d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/reviews/w2-128-r2b.md",
      "chunk_id": "cca02d53aaeb18b6f4cf43e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-175/README.md",
      "chunk_id": "5ee83048f1310a18f898783d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-q8cl/PR-DAEO-q8cl-pin2.md",
      "chunk_id": "dbf5dd923773dcf9f2e94f6e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-197/README.md",
      "chunk_id": "3f1ca3d5f2b2a8a2b0f85083",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/adapters/test_w2_153_portability.py",
      "chunk_id": "e0fa7f539a82e70897d5c347",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-88/test_w2_88_s16_search_again.py",
      "chunk_id": "0403176f04f1b638c724c54a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-153/test_w2_153_sources.py",
      "chunk_id": "8e6f702cf8647dc73879da76",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-175/w2_175_support.py",
      "chunk_id": "af53826e27c627387db63f0a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-197/README.md",
      "chunk_id": "e61449a1b41b2392334187fa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-152/README.md",
      "chunk_id": "1ae0efd3be75a670bfc96496",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-08/w1_08_support.py",
      "chunk_id": "2294ce6a9c8dfa48cad2dfe7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-153/w2_153_support.py",
      "chunk_id": "6b5fdc624bb1791385c740fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-35/README.md",
      "chunk_id": "45466ca2f81c61fa5e628fba",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-175/README.md",
      "chunk_id": "c2b3cf17197bd0fe3b003d9b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-152/w2_152_support.py",
      "chunk_id": "154ca20303f083521f88157b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-152/test_w2_152_facts.py",
      "chunk_id": "dc4e3e2323c1cda7f9e523e7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-35/w1_35_orchestration_support.py",
      "chunk_id": "4a28a0db8f2d05ffd3a68293",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-175/w2_175_support.py",
      "chunk_id": "086bd680fd28b0c694dd7eb3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-35/README.md",
      "chunk_id": "020eb72be502bb04e7bcb6f9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-152/README.md",
      "chunk_id": "06752a9a030870d36b51a01a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-175/README.md",
      "chunk_id": "fee120528dbf5d32d85fd659",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-175/README.md",
      "chunk_id": "c814349f91264b6671621f15",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-175/README.md",
      "chunk_id": "04914b705addea3925af1a71",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-175/README.md",
      "chunk_id": "fceee3b6e508b077664a5828",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_links.py",
      "chunk_id": "f92d107592e39bbb2412b8f6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-175/README.md",
      "chunk_id": "ad6bfce3e3e823b4edde9179",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-153/README.md",
      "chunk_id": "413711fcc03173fa4462e9e1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-153/test_w2_153_sources.py",
      "chunk_id": "88aba467ce0ac613d75c2832",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-35/test_w1_35_orchestration.py",
      "chunk_id": "d2671a2878007c794a716637",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/README.md",
      "chunk_id": "28713c7320854f8bc473a723",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/README.md",
      "chunk_id": "c6f2ca37278c5dde77c35cb8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/README.md",
      "chunk_id": "1d2780ef150d56d988294574",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-35/w1_35_orchestration_support.py",
      "chunk_id": "684fc5bb165b444901facd1d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-175/test_w2_175_templates.py",
      "chunk_id": "a398fe4b6200a897535a29f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-200/README.md",
      "chunk_id": "d860745237d63439547bf497",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-lrre/PR-DAEO-lrre.md",
      "chunk_id": "a2a18bcdd5400c7294f93d43",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-152/README.md",
      "chunk_id": "1f22cb3b3c720a63dccd5c4b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-152/README.md",
      "chunk_id": "ad59d8e9253b6a53231746f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-152/README.md",
      "chunk_id": "affae3cb7f1d7c9f72df316a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-175/README.md",
      "chunk_id": "884791df1c45fd614de712b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-35/test_w1_35_orchestration.py",
      "chunk_id": "3ee0fc26a3d4a8ae459f3cc8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-35/README.md",
      "chunk_id": "e39fea9ee2298824a67e3435",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-88/README.md",
      "chunk_id": "97b221b398315019ea75fd6e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-88/README.md",
      "chunk_id": "942fa2bcec113c17eb11314b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-href/PR-DAEO-href.md",
      "chunk_id": "cba9883b3f4ec19b186c23b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-35/w1_35_orchestration_support.py",
      "chunk_id": "6b7f2bf97adbfeec2ccbe6c8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-136/w2_136_support.py",
      "chunk_id": "274e62af1eb363a9a6fad5fd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-35/w1_35_orchestration_support.py",
      "chunk_id": "4463ff3be175f05d528dc422",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-o5x1/PR-DAEO-o5x1.md",
      "chunk_id": "a15956490e2bd30f87941876",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-35/test_w1_35_orchestration.py",
      "chunk_id": "19e175c72be1075faf56a5bd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-153/README.md",
      "chunk_id": "c451be719b3376060035f0fb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-153/w2_153_support.py",
      "chunk_id": "1e70a78cdbd4b2f6cfe55b24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-200/README.md",
      "chunk_id": "839a934890fbabdcc4dc74de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-175/w2_175_support.py",
      "chunk_id": "72402c22f0fb60cee1df7411",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-wahn/PR-DAEO-wahn.md",
      "chunk_id": "732652eb93d818d789b5e930",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-175/w2_175_support.py",
      "chunk_id": "26cc427721780caf679cee9e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-136/README.md",
      "chunk_id": "1003b7d72068d6731506969d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P2-perticket.csv",
      "chunk_id": "98a0070331c4064f7ecaf7c6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-153/test_w2_153_sources.py",
      "chunk_id": "de27932861a251526443edaa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-153/README.md",
      "chunk_id": "ab9720c102238a6dc7632382",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-175/README.md",
      "chunk_id": "aff5b9e00683294aace0b0f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-88/test_w2_88_s16_search_again.py",
      "chunk_id": "46e989d061de0ef1fed6314f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-11/README.md",
      "chunk_id": "aebf172cfb73a15449b72b3f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-197/README.md",
      "chunk_id": "0d0f240dd249a33092c212a3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-88/test_w2_88_s16_search_again.py",
      "chunk_id": "9bc2082aee03cc4478a8a732",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-o5x1/PR-DAEO-o5x1.md",
      "chunk_id": "c5abdfef3816ced3b4c40792",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-153/README.md",
      "chunk_id": "be7c51e6c6d8fae78d28dfdf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-href/PR-DAEO-href.md",
      "chunk_id": "d5e42b335c5e9213feafb435",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-o5x1/PR-DAEO-o5x1.md",
      "chunk_id": "3edf12b39899b7002fd3123b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-href/PR-DAEO-href.md",
      "chunk_id": "41d5788253974ddc90403345",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-o5x1/PR-DAEO-o5x1.md",
      "chunk_id": "c188ac688a33bbcbbd7fa1b9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-153/README.md",
      "chunk_id": "57df1de7c5ac3299148427a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-11/README.md",
      "chunk_id": "d3b6eefcb1d5de11b5a6ad77",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-136/README.md",
      "chunk_id": "977282a3f2e85fa8f1b5253c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_links.py",
      "chunk_id": "330b362522ebc5f19aff538c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_templates.py",
      "chunk_id": "14be6cb9281a82525a1cf543",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/w2_128_support.py",
      "chunk_id": "91be02fa41e7b2ee1dca20f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/README.md",
      "chunk_id": "22c6c1b438ce922d5e161b43",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/README.md",
      "chunk_id": "411a3c88ee6817445801cb18",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/README.md",
      "chunk_id": "6503ea3629fbf4f81301ed17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_templates.py",
      "chunk_id": "0355db01a08cb95615e988b1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/test_w2_128_facts.py",
      "chunk_id": "a50df03dc9f888186c745301",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-08/w1_08_support.py",
      "chunk_id": "7544eddbf0c0970d7069bcff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/README.md",
      "chunk_id": "2b95c25e349df4605ad0eef0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/README.md",
      "chunk_id": "7720511d7d9e43274f541c41",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/README.md",
      "chunk_id": "605504ef54e55966b02c4bdd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-128/w2_128_support.py",
      "chunk_id": "040b9466eaf4f3a8c78fda49",
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
          "CAP-33",
          "DAEO-9bc0",
          "DEC-182",
          "DEC-866",
          "DEC-943",
          "DEC-959",
          "DEC-963",
          "DEC-1052",
          "DEC-1088",
          "DEC-1092",
          "DEC-968",
          "DEC-1217"
        ],
        "left": 6
      },
      "changed_by": {
        "DEC-943": [
          "DEC-1052"
        ],
        "DEC-959": [
          "DEC-968"
        ],
        "DEC-1052": [
          "DEC-1217",
          "DEC-1157"
        ],
        "DEC-1088": [
          "DEC-1157"
        ],
        "DEC-1217": [
          "DEC-1241"
        ]
      }
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5970
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLThzODUubWQiLDY5LDgyLCJhZTZkYzhhNjA5OTkwY2ExMzA3NGE1NjAiXSxbIi50aWNrZXRzL0RBRU8tbzV4MS5tZCIsNjcsNzcsIjI0MGMyNzc0Mzc0YmFlNDMwYWJjODI5MCJdLFsiLnRpY2tldHMvREFFTy10OG1wLm1kIiwyNywzOSwiZTgzYzkxYWU0YzNhZTc2ZjNhODc2ZWFlIl0sWyIudGlja2V0cy9EQUVPLXQ4bXAubWQiLDUwLDU0LCJkNTJiN2MxMmJiZmRiYzJkNzg2ZTMzOTciXSxbIi50aWNrZXRzL0RBRU8tdDhtcC5tZCIsMTE1LDEyMywiMjhhMzZjNmRkMDJkYjI3OWU3MzdmNTdmIl0sWyIudGlja2V0cy9EQUVPLXdhaG4ubWQiLDI4LDQ2LCJmZjRkNDhhN2Q3Njg5ODkzZjU3MDliODQiXSxbIi50aWNrZXRzL0RBRU8td2Fobi5tZCIsNTksNjIsIjYzYTQzMmEyZGE0NWRlZTk2MGI2M2Y2ZSJdLFsiZG9jcy9jaGFuZ2VzL1cyLTEyOC1DSVQtUC5tZCIsMTYsMjMsIjEyNjc2MGY3MjljMTZiMmVkNjg2Nzc0NyJdLFsiZG9jcy9jaGFuZ2VzL1cyLTEyOC1DSVQtUC5tZCIsNDYsNTEsIjVhMjZmMGQzOTY2YTI3MDJlZWI1OWZmNyJdLFsiZG9jcy9jaGFuZ2VzL1cyLTE1My1ldmlkZW5jZS5tZCIsMTEsMTEsImE4YjQ2NmVlYTIwNTY5MzFlNDkzYzQ0ZCJdLFsiZG9jcy9wbGFuL1dBVkVfMl9XQlMubWQiLDE3OTIsMTc5NCwiMjhiNmMyYmMxZjJkMDdmNTJkNzhlYTlmIl0sWyJkb2NzL3BsYW4vV0FWRV8yX1dCUy5tZCIsMTg1OCwxODYwLCIwNGFlZjQzNTgwYjZjNmFkMzA1YWQ1MmQiXSxbImdvdmVybmFuY2UvcHJvamVjdC9vcmNoZXN0cmF0aW9uL3BhY2thZ2VzL0xJRlQtMS9ENS1ST1dTLm1kIiwxOCwyMywiMmUzNWY0NjZjNTk2OGI3ZmZjYzMxZGNlIl0sWyJnb3Zlcm5hbmNlL3Byb2plY3Qvb3JjaGVzdHJhdGlvbi9wYWNrYWdlcy9MSUZULTEvRDUtU1RBVFVTLm1kIiwzMCwzNiwiNzQ2OWNiZGY2OWY5ZTRkMmM1MjQ4OTdkIl0sWyJnb3Zlcm5hbmNlL3Byb2plY3Qvb3JjaGVzdHJhdGlvbi9wYWNrYWdlcy9MSUZULTEvTElOSy1JTlRFR1JJVFkubWQiLDQ0MCw0NTEsImUyODMwOTJmNWI4NzdjNDhkODVmNWE2NCJdXSwiZiI6Ii9ob21lL3VzYWluL0R5bmFtaWMtQWdlbnRpYy1FbmdpbmVlcmluZy1PUyIsImkiOltdLCJvIjoyMCwicCI6eyJiIjoic2VydmljZSIsImQiOiJjdWRhOjAiLCJoIjoiODg4YWM3MzMzY2MzZDQxZCIsIm8iOlszOCwzMiw2LDEsNSwxNSwwLDI5LDMsMzMsNCwyNCwzNiwyMCwxMSwyOCwzNSwyNywzMSw5LDEzLDIsMjYsOCwxNywyMSwxOCwxNCwyMiwxNiwyNSwzNywzOSwxMiw3LDIzLDEwLDM0LDE5LDMwXX0sInEiOiJXMi0xMjggcm9sZSB0ZW1wbGF0ZSBjb250cmFjdDogUjMgcHJvc2UgYnVkZ2V0LCBMSU5LLUlOVEVHUklUWSBsaW5rIGxpbmVzLCBENSByb3dzLCBmYWN0cy55YW1sIGNvbW1hbmRzIG1hcCwgSS0zNSByb2xlIGZpbGVzIHBpbm5lZCBieSB0ZXN0cywgaG93IHRoZSByb2xlIGNhcmQgY29waWVzIGFyZSByZWZyZXNoZWQiLCJyIjowLCJzIjoiYzFlODFhZmQzZTc1NjBlN2E4Zjc2OWJiNTFkZTA4M2IwN2Q3MjE1OCIsInQiOm51bGwsIngiOlsiMGFhZWNmN2FiMDU2ODQxZWYxNjZjY2U2IiwiMmE1YTk4NDg2MmNkNDNhZWYxNmU2ZGU5IiwiMzFjMzMwODE5ZWM3NDYyMDQ3YzEyZjAyIiwiOWQ1MmE4NThiMTAyNTg1Nzg5YmZiNjhmIiwiZWIzZTFkMTM1ZmEyYTA2MWNjNmM5NWQ0Il19",
  "routing": {
    "code": [],
    "named": [
      "dfef0059bbd6a036a299fdc9",
      "d52b7c12bbfdbc2d786e3397"
    ],
    "phrasings": [
      "W2-128 role template contract: R3 prose budget, LINK-INTEGRITY link lines, D5 rows, facts.yaml commands map, I-35 role files pinned by tests, how the role card copies are refreshed",
      "W2-128 role template contract R3 prose budget LINK-INTEGRITY link lines D5 rows facts.yaml commands map I-35 role files pinned tests role card copies refreshed",
      "W2-128 role template contract: R3 prose budget, LINK-INTEGRITY link lines, D5 rows, facts.yaml commands map, I-35 role files pinned by tests, how the role card copies are refreshed DAEO-t8mp"
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
        "chunk_id": "28a36c6dd02db279e737f57f",
        "path": ".tickets/DAEO-t8mp.md",
        "start_line": 115,
        "end_line": 123
      },
      {
        "chunk_id": "240c2774374bae430abc8290",
        "path": ".tickets/DAEO-o5x1.md",
        "start_line": 67,
        "end_line": 77
      }
    ]
  }
}
