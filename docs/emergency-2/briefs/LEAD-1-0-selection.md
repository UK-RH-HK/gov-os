# Lead brief: integration plan item 1-0, a trustworthy impact selection (fixes under W2-115b and W2-206; the owner's order of 25 Nov: it starts now, as its own lead)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-25. **Read `docs/emergency-2/briefs/LEAD-COMMON.md` first: every rule there applies** (read your bundle whole, never cut a `gov retrieve` result, list your retrieves, one trailer paragraph with no blank line before `Co-Authored-By`, never open a sets root). Decide, never ask (I-10). Use `systematic-debugging`.

## Why
The owner (DEC-1244 X-1; his order of 25 Nov): every landing runs the tests the product's impact selection picks, never a hand-picked set, and the full suite runs only for a release and weekly. Today the selection fails both ways:
- **Too broad:** every landing of 24 and 25 Nov selected 300 to 400 suites (`gov queue <ticket>=<branch> --onto w2/integrate --select`), about the whole suite: each landing took 50 to 90 minutes and loaded the machine. The CTO's reading, to verify first: the selection takes its changed files from the last green full-suite record (`base` in the output, the 0.1.5 record `0bd2945b0`) to the merged tree, so every branch carries two days of everyone's changes, not its own diff.
- **Too narrow where it matters:** reds it never picked, found only by the release suite: I-20 (`template/**` -> W2-16, W2-208, `tests/unit/update`), I-21 (`governance/project/release-authority.yaml` -> W2-209), I-29 (`governance/project/indep-walls/**` and the launcher's templates -> W2-178, W2-149; the rebuild's due rule -> W2-116). Read those rows of `docs/emergency-2/integration/FINDINGS.md`.
Read row 1-0 (and 1-8, 1-9, 1-11, which feed it) of `docs/emergency-2/integration/INTEGRATION-PLAN.md`.

## What (K-lines written as `## Fix:` sections into `.tickets/DAEO-j9z6.md` (W2-115b) and `.tickets/DAEO-l2b2.md` (W2-206); the CTO approves them by this brief)
- **SEL-1 The branch's own change.** The selection reads the branch's own diff against the integration head (the merge base to the branch head), plus the base's known reds, never everything since the last green record. A planted branch that changes one file of one package selects that package's suites and the suites the test map couples to that file, and nothing else; report the count for each of the landings of 24-25 Nov (the landing records under `.gov-runtime/scratch/orchestrator/log/landings/`) before and after.
- **SEL-2 The missing edges.** The test map holds the edges of I-20, I-21 and I-29, each with a failing case first (the change to the file selects the suite that went red); and a kit-wide rule: a change under `template/**` selects the suites that render the kit.
- **SEL-3 Coverage named.** A changed file the selection places nowhere is listed (`unplaced`) and makes the landing refuse with its line to add (Q-1's spirit), except a record-only document, which passes with a notice (DEC-1239 (2)).
- **SEL-4 One run for many branches.** `--select` accepts several branches (or a batch branch) and gives one list for their merged tree, so held branches land in one run (the owner's order).
Not in this lead: 1-8, 1-9, 1-11's A3 part (later leads); the timing cases (D-03, a separate lead).

## Where
Worktree `/home/usain/gov-os-worktrees/E2-1-0-selection`, branch `e2/1-0-selection` from `w2/integrate`. Code area: `src/gov/queue/` (the selection), `governance/project/test-map.yaml`, `src/gov/close/` only where the selection lives. Nobody else edits these now.

## Green
SEL-1 to SEL-4 red on the base, green after; `tests/unit/queue`, W2-115, W2-206 green; then the selection for your own branch (it should now be small) run exactly, through the heavy slot; the count it gives is part of your return. Check the trailers (LEAD-COMMON).

## Return
Branch and head; the cause of the breadth confirmed (file:line); SEL-1 to SEL-4 with tests and result; the before and after counts per landing; the selected run's summary; your retrieves.

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
Query: How does gov queue --select compute its selection (the base record, changed files, the test map, couplings, unplaced) and why does it pick 300 to 400 suites; which edges are missing (I-20, I-21, I-29)? Code locations, conventions, earlier fixes and findings.

```
store: ea2016be9802 (/home/usain/gov-os-worktrees/W2-00-store-b)
{
  "store": {
    "commit": "ea2016be980276fb2e8970c333f36a244c254b21",
    "head": "ea2016be980276fb2e8970c333f36a244c254b21",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-b"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "1c869db104a470d770d34cea",
      "sha256": "a43529481802542feb45ba2bcfa51178b9c660a3f24b0bc0c0935e5837cd08a0",
      "path": "docs/emergency-2/briefs/LEAD-fix-select.md",
      "start_line": 1,
      "end_line": 24,
      "text": "# Lead brief: fix-select, `gov queue`'s selection: I-1 (a deleted test is not a selected target) and I-2 (a record-only document a branch writes is placed with a notice) (fixes under W2-115b, `DAEO-j9z6`)\n\nRead `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it (its test command, with node on PATH; the test\ndesigner's reading bounded). Name: `fix-select`; worktree `/home/usain/gov-os-worktrees/E2-fix-select`, branch\n`e2/fix-select` from `w2/integrate`. **Do not merge.** Every helper Sonnet; this lead runs medium (DEC-1236 (2)). It must\nbe green **within about 90 minutes**: I-1 rides release 0.1.5 before its version commit (DEC-1239 (1)); if I-2 would\ndelay that, finish I-1, commit, and say I-2 is left.\n\n**The findings** (`docs/emergency-2/integration/FINDINGS.md` I-1, I-2; DEC-1239):\n- **I-1:** `src/gov/close/select.py` `scoped()` adds every changed path since the last green record that is a test file\n  as `TEST_CHANGED` (about `:796-798`), including a test file the change **deleted**; `unresolved()` (`:315-332`) then finds\n  it gone and the selection refuses `SELECTION_REFUSED ... FILE_GONE` (`:841`). On 2026-11-22 every `gov queue` landing\n  after `e2/models-rubric` deleted `tests/acceptance/W2-201/test_w2_201_s9_substitution.py` refused this way. The fix: a\n  path the change deleted (absent from the tree at HEAD) is never selected as a target; it is listed (for example under\n  `deleted` in `--select`'s object) and its suite folder still runs if the folder remains. A target the test map names\n  (couplings, `every_close`, `record_reading`) that is gone still refuses as today (DEC-912 item 3).\n- **I-2:** a document the branch itself writes that no suite, coupling or ticket places refuses\n  (`SELECTION_REFUSED ... nothing maps to a suite`, the `UNPLACED` path in `scoped()`). The owner's decision: \"a record-only\n  document a branch writes is placed as a record with a notice at the landing, never refused.\" Define record-only by the\n  test map's own notion (a path under the record roots the map's `record_only` patterns cover, plus Markdown documents\n  outside `src/`, `tests/` and the kit's executable parts; say exactly which rule you choose and why); such a path goes to\n  `records` with a notice (`RECORD_PLACED <path>`) in `--select`'s object and the landing's record; code and tests the\n  branch writes that nothing places still refuse.\n\n",
      "chunk_id": "1c869db104a470d770d34cea",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-j9z6",
      "sha256": "c207059870254c37568c2ffb6fb5da2e76f3f0d2f8496293c23c1528c5650eee",
      "path": ".tickets/DAEO-j9z6.md",
      "start_line": 178,
      "end_line": 189,
      "text": "## Fix: gov queue's selection, I-1 and I-2 (2026-11-22; FINDINGS I-1, I-2; DEC-1239)\n\n- **I-1:** `select.scoped` with `change` given lists a path the change deleted (absent from HEAD) under `deleted`; it is never\n  selected as `TEST_CHANGED` nor counted unplaced; its suite folder still runs if it remains. A map-named target that is gone\n  (couplings, `every_close`, `record_reading`) still refuses `FILE_GONE` (DEC-912 item 3).\n- **I-2:** with `change` given, an unplaced `.md` outside `src/`, `tests/`, `template/`, `governance/kernel/`, `.claude/` and\n  `.rulesync/` is a record: listed under `records`, notice `RECORD_PLACED <path>` under `notices` in `--select`'s object, the\n  landing's answer and `queue.json` (top level and under `result`). Rule chosen: the map's `record_only` patterns already make\n  records; Markdown outside code, tests and the kit's executable/instruction parts is documentation the branch writes, never\n  something a suite could test. Code and tests nothing places still refuse. `gov close` (no `change`) unchanged.\n- **Tests:** `tests/acceptance/W2-115b/test_w2_115b_select_fixes.py` (9 cases, 8 red on the base), unit\n  `tests/unit/queue/test_queue_select_deleted_records.py`. Also fixed the ticket's YAML escaping of the new KPI lines.\n",
      "chunk_id": "6f7275f3710755a37a4a7920",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "4614b2f2bea1967a96f9c774",
      "sha256": "fc073347b75925d9fb3e679f1f0bec4f161a06048c50950852e9da59d9426c78",
      "path": "governance/project/orchestration/packages/L2-4-PROVING.md",
      "start_line": 6,
      "end_line": 29,
      "text": "## The cause (two defects, both found by running the landing, neither by a review)\n\n1. **Documents the branch never wrote refused the landing** (the CTO's find, `SELECTION_REFUSED: 6 changed path(s) nothing maps to\n   a suite`). `select.scoped` counts the change as everything since the newest green record, plus the ticket's own commits, plus\n   `change` (W2-115 S2, `0fb32b21f`; its test `test_s2_an_unmapped_path_merged_since_the_green_base_refuses` pins it for `gov close`).\n   `gov queue` runs it in the warm clone at the tested merge, so the range holds what the CTO committed on the base after the green\n   record, and a path of it that no suite places refused the landing as if the branch had written it. **The since-green range is the\n   intended model of `gov close` (W2-115) and stays; it leaked into the queue, whose KPI (W2-115b, success 1) is \"the branch's own\n   commits since the integration head as well as the ticket's\".** Owning ticket: **W2-115b (`DAEO-j9z6`)**: its allowed paths hold\n   `src/gov/queue/**` and `src/gov/close/select.py`, and its non-goals say `select.py` is open to it only for the keyword the queue\n   passes, behaviour without it unchanged. Not W2-202 or W2-206 (they build flags and base reds, not the change model). DEC-891's\n   places stay as they are: `record_only` is not widened (W2-66 refuses it).\n   **Fix:** with `change` given, a path counted only from the green range (neither the ticket's own commits nor `change` wrote it)\n   that nothing places is listed under `unplaced_base` (in `select.scoped`'s answer, `--select`'s object, a dry run's `select.json`)\n   and every suite it does reach stays selected; a path the landing wrote that nothing places is still refused, naming only itself;\n   without `change` nothing changes. Tests first (Opus designer): `tests/acceptance/W2-115b/test_w2_115b_unwritten_paths.py`\n   (success 10 to 13, failure 3), `tests/unit/queue/test_queue_select_unwritten.py`. Sonnet engineer: `ea637c1c0`, then `cb621b2da`.\n2. **The ticket `DAEO-gr7t` named the whole `tests/acceptance/` as its acceptance folder** and holds `src/gov/**`,\n   `tests/unit/**`: every change under those selected the whole tree and was refused `would run the whole of tests/acceptance/`.\n   Behind defect 1 it refused every such landing since 2026-11-18, and would have been the CTO's next refusal. No other ticket has the\n   shape. **Fix (a record fix under `DAEO-gr7t`, recorded in its file):** `acceptance_tests.path: tests/acceptance/E2-retire-guard/`\n   (holds no test, so the ticket holds no suite). Test first (Opus designer): `tests/unit/close/test_live_tickets_name_no_whole_suite.py`\n   reads the live tickets.\n\n",
      "chunk_id": "4614b2f2bea1967a96f9c774",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "e4cdf1c6c5973749006e6380",
      "sha256": "6ef16fcc8d3fa9972a02c21a1fb6746431e751de68a06790fb05481934ee3ea5",
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "start_line": 7,
      "end_line": 8,
      "text": "| I-1 | 2026-11-22 | `gov queue`'s selection takes a test file **deleted** since the last green record as a changed test (`TEST_CHANGED`), then refuses the landing because the head no longer holds it (`SELECTION_REFUSED ... FILE_GONE`); every queue landing refuses until a new green record exists | `src/gov/close/select.py:796-798` (`_is_test_file(p)` \u2192 `select(p, \"TEST_CHANGED\")` for a deleted path), `:841` (`unresolved`); logs `log/queue-rubric-20261122.out`, `log/queue-d7-20261122.out` | W2-115b `DAEO-j9z6` | fix (failing test first) | **fixed** in 0.1.5 (`8555186af`, lead `fix-select`, failing test first); verified in use: the next `gov queue --select` on `w2/integrate` passed |\n| I-2 | 2026-11-22 | A document a fix branch writes (a skill copy, an audit table, a brief) that no suite maps refuses the landing (`SELECTION_REFUSED ... nothing maps to a suite`) unless the ticket's `allowed_paths` hold it | `log/queue-rubric-20261122.out` first run; worked around by adding the paths to `DAEO-k1us`'s `allowed_paths` (`66c87e821`) | W2-115b | decided (DEC-1239 (2)): placed as a record with a notice at the landing, never refused | **fixed** in 0.1.5 (`8555186af`) |\n",
      "chunk_id": "e4cdf1c6c5973749006e6380",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "bd0a58b8efa19483d963abcc",
      "sha256": "d85f0b71ac290451e427612a525765e532cd4b61d476eac8e3a3003be49bef1a",
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "start_line": 54,
      "end_line": 55,
      "text": "| 25 | W6, W11 | the landing's selection: `src/gov/close/select.py` (`scoped`, `:742`), used by `queue/command.py:515-525` | P | auto at `gov queue` | P (only where `gov queue` is used) | changed paths \u2192 suites (`select.json`): path map, tickets' `allowed_paths`, test map, imports; widens to full on anything unplaced | not needed | traces code \u2192 tests only; no spec or decision enters; W2-66 (DAEO-c1uz); `FILE_GONE` selection bug, see row 62 |\n| 26 | W6 | `gov links` (`src/gov/links/check.py`) | P | auto inside `gov check --structural` at the queue's after-step (`check/structural.py:221`); typed otherwise | P | records \u2192 findings (`UNLINKED_ID`: a `[DEC-n]` in a KPI line not in the ticket's `sources`, `CLOSED_TICKET_EDITED`, \u2026) | `role-lead.md:79`, `role-cto.md:34` | no `KPI_DRIFT` (the ticket's `[Kn]` lines against its spec's K-lines); W2-129; integration |\n",
      "chunk_id": "bd0a58b8efa19483d963abcc",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-j9z6",
      "sha256": "a8350c6e6f775201390d4102638f11dbc392b4456ee4b6471682f8a9959d6220",
      "path": ".tickets/DAEO-j9z6.md",
      "start_line": 122,
      "end_line": 131,
      "text": "  base's own commits too, and a path of it that no suite places is refused as if the branch had written it. W2-115b's\n  success line 1 says the queue's change is \"the branch's own commits since the integration head as well as the\n  ticket's\"; its non-goals say `select.py` is open to it only for the keyword the queue passes and that the behaviour\n  without it is unchanged. The since-green range is `gov close`'s model (W2-115) and leaked into the queue; the base's\n  paths are neither this landing's change nor its to refuse (EMERGENCY-2 \u00a73.2: a block must be within the change's\n  scope). The range stays (it selects what the untested base paths reach); the refusal does not apply to it.\n  The test map's `record_only` cannot take the documents (W2-66: DEC-891's places and nothing else, no code path).\n- **The fix line:** with `change` given, a path counted from the green record that neither the ticket's own commits nor\n  `change` wrote, and that nothing places, is not refused: it is listed under `unplaced_base` in the selection (the\n  object `--select` prints too), and every suite it does reach (imports, couplings, overlaps) is still selected.\n",
      "chunk_id": "20ef5b976f59f3ec6163d06c",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "7c68bb7bded2903b29cc08f5",
      "sha256": "a805b46ad40cd024f39aac86d242f18105213904d15bd2386935b90c90477ae5",
      "path": "src/gov/close/select.py",
      "start_line": 848,
      "end_line": 860,
      "text": "    # I-2 (DEC-1239 (2)): with ``change`` given, a Markdown document outside the code, test and kernel places that\n    # nothing places is a record, placed with a notice; code and tests that nothing places still refuse\n    placed_records = [p for p in unplaced if change is not None and _is_record_document(p)]\n    unplaced = [p for p in unplaced if p not in placed_records]\n    if unplaced:\n        raise SelectionRefused(f\"{len(unplaced)} changed path(s) nothing maps to a suite (no coupling, no ticket \"\n                               f\"with a suite holds them, no test imports them): {', '.join(sorted(unplaced))}\")\n    governance = [p for p in paths if p.startswith(GOVERNANCE_OVERLAY) and not _any(p, test_map.get(\"record_only\"))]\n    if records and not code and governance and _bookkeeping(root, ticket, records):\n        # S2: governance files select nothing by themselves; the ticket's own bookkeeping beside them (its ticket\n        # file, its close record and checkpoint, the green records the change is counted from) is no record change\n        records = []\n    # the landing's own records: the green records and the base's other commits are counted, not listed\n",
      "chunk_id": "7c68bb7bded2903b29cc08f5",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "4c89fd5f52a86befb2abe01d",
      "sha256": "f0f0e972647f68b6f046cd82e50daa0a006fc33eaf96890cb53f4c98b89f96a9",
      "path": "docs/emergency-2/integration/ACCOUNT-2026-11-25.md",
      "start_line": 148,
      "end_line": 150,
      "text": "4. The re-pin itself is rehearsed on a planted home before every cut, beside the update rehearsal (part of the I-31 fix).\n5. Plan item 1-0 comes first in 0.1.9, with the missing selection edges named in I-20, I-21 and I-29, so landings run the tests that matter.\n6. Every brief carries its bundle uncut, every merge checks the trailers by code, and other CTOs send findings that need an answer by tmux to the Gov OS CTO, not only to their own logs.\n",
      "chunk_id": "4c89fd5f52a86befb2abe01d",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "2ef2bfff52af5a0d79bb08f1",
      "sha256": "f34047b24637ece15e9b1920a605d332c76b53ed383fc6ecfc9f837debeaa80f",
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "start_line": 26,
      "end_line": 26,
      "text": "| I-20 | 2026-11-24 | A selection bug (X-1): the CTO's chore `0bc85cd12` added `template/LICENSE`; the landing's selection placed it nowhere (`unplaced_base`), yet it turned `tests/acceptance/W2-16/test_w2_16_install.py::test_doctor_passes_on_a_project_installed_from_a_release[copied]` red (the kit's path map did not hold the new root file, so `gov doctor` failed `path_map` on a project copied from a release). Found by D1's selected run, which picked W2-16 for its own reasons | `.gov-runtime/scratch/orchestrator/log/landing-d1/pytest.out`; `0bc85cd12` | the selection's test map (W2-115b, plan 1-0) | fix: a test-map edge from `template/**` to the suites that render the kit (W2-16, W2-208, `tests/unit/update`), failing test first, in plan item 1-0; the file itself moved to `template/governance/kernel/LICENSE`, held by every map | moved, W2-16 re-run |\n",
      "chunk_id": "2ef2bfff52af5a0d79bb08f1",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-j9z6",
      "sha256": "af5913ba20f9aa3bb47816f077b2990cc7dca0d5a68c18bfd7d7dfa16f7381d4",
      "path": ".tickets/DAEO-j9z6.md",
      "start_line": 130,
      "end_line": 139,
      "text": "  `change` wrote, and that nothing places, is not refused: it is listed under `unplaced_base` in the selection (the\n  object `--select` prints too), and every suite it does reach (imports, couplings, overlaps) is still selected.\n  A path the landing's own change wrote and nothing places is refused as before. Without `change` (`gov close`)\n  nothing changes. Verify: a planted project with a green record and, after it, two commits on the base that no ticket\n  made (a document outside `record_only`, a shell script) beside a branch that changes mapped code: `gov queue <T>=<branch>\n  --select` prints the object and exits 0, the two paths under `unplaced_base`; a branch that itself writes an unplaced\n  path is refused `SELECTION_REFUSED` (exit 2) naming it and not the base's; a base-side path a test imports still\n  selects that test; `select.scoped(root, T)` without `change` still refuses the base-side path.\n- **Order:** this section (`Role: orchestrator`); the test designer (Opus, the C3 trial of DEC-1222 (2); `src/gov/close/**`\n  and `src/gov/queue/**` are C3), tests under `tests/acceptance/W2-115b/` and `tests/unit/queue/`, red on the base;\n",
      "chunk_id": "dd15261a7bc0874e9d85e947",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "dbb397ed429c2b9cfdf96160",
      "sha256": "8d0d495d6b60b834fef77a42b141052cf7df824b8ed408f01de879ad6db4a86f",
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "start_line": 1,
      "end_line": 7,
      "text": "# Integration findings (DEC-1238 (3)): bugs and friction found by running Gov OS's own work on its tools\n\nEach row: what happened, the evidence, the owning ticket, the kind (fix / spec question), its state. New rows at the end.\n\n| # | Date | Found | Evidence | Owner | Kind | State |\n|---|---|---|---|---|---|---|\n| I-1 | 2026-11-22 | `gov queue`'s selection takes a test file **deleted** since the last green record as a changed test (`TEST_CHANGED`), then refuses the landing because the head no longer holds it (`SELECTION_REFUSED ... FILE_GONE`); every queue landing refuses until a new green record exists | `src/gov/close/select.py:796-798` (`_is_test_file(p)` \u2192 `select(p, \"TEST_CHANGED\")` for a deleted path), `:841` (`unresolved`); logs `log/queue-rubric-20261122.out`, `log/queue-d7-20261122.out` | W2-115b `DAEO-j9z6` | fix (failing test first) | **fixed** in 0.1.5 (`8555186af`, lead `fix-select`, failing test first); verified in use: the next `gov queue --select` on `w2/integrate` passed |\n",
      "chunk_id": "dbb397ed429c2b9cfdf96160",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "20d5ac918cae206867c97ef3",
      "sha256": "aec24bd63844bf48dfecb6d8e5cb55ee6b4c356eacf05a798110dd02264c41ad",
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "start_line": 25,
      "end_line": 26,
      "text": "| I-19 | 2026-11-24 | `gov memaudit fresh` prints a bare `UsageError` with no reason on a stop | EXAMIN `REQUESTS.md` FINDINGS LOG EF-6 | `gov memaudit` (W2-204) | fix: name the stop and its cause | none needed |\n| I-20 | 2026-11-24 | A selection bug (X-1): the CTO's chore `0bc85cd12` added `template/LICENSE`; the landing's selection placed it nowhere (`unplaced_base`), yet it turned `tests/acceptance/W2-16/test_w2_16_install.py::test_doctor_passes_on_a_project_installed_from_a_release[copied]` red (the kit's path map did not hold the new root file, so `gov doctor` failed `path_map` on a project copied from a release). Found by D1's selected run, which picked W2-16 for its own reasons | `.gov-runtime/scratch/orchestrator/log/landing-d1/pytest.out`; `0bc85cd12` | the selection's test map (W2-115b, plan 1-0) | fix: a test-map edge from `template/**` to the suites that render the kit (W2-16, W2-208, `tests/unit/update`), failing test first, in plan item 1-0; the file itself moved to `template/governance/kernel/LICENSE`, held by every map | moved, W2-16 re-run |\n",
      "chunk_id": "20d5ac918cae206867c97ef3",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-j9z6",
      "sha256": "6c46978993e5633e9f0e74cf46507b57dbf27cfac04f703d6cf75a33ba044883",
      "path": ".tickets/DAEO-j9z6.md",
      "start_line": 114,
      "end_line": 123,
      "text": "## Fix: the queue's selection refuses only the landing's own unplaced paths (L2-4, DEC-1217 (1), DEC-1223 (9))\n- **The bug (found by the CTO, 2026-11-20):** `gov queue DAEO-sdhj=e2/w2-17-fixes --onto w2/integrate --select` was refused,\n  `SELECTION_REFUSED: 6 changed path(s) nothing maps to a suite`: `docs/emergency-2/briefs/*.md`, `proposals/*.md`,\n  `release-0.1.4/STEPS.md` and `repin.sh`, none written by the branch. They were committed on `w2/integrate` after the last\n  green record (`e74765954`). Every document the CTO commits after a green run therefore blocks every landing.\n- **The cause, from the code and the tickets:** `select.scoped` counts the change as \"everything since the newest green\n  record, with the ticket's own commits\" (W2-115 S2, `0fb32b21f`; `test_s2_an_unmapped_path_merged_since_the_green_base_refuses`\n  pins it for `gov close`). `gov queue` calls it in the warm clone at the tested merge, so the green range holds the\n  base's own commits too, and a path of it that no suite places is refused as if the branch had written it. W2-115b's\n  success line 1 says the queue's change is \"the branch's own commits since the integration head as well as the\n",
      "chunk_id": "7867aa07572fe4055d8c3154",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "4e36798cfa2caf8693170906",
      "sha256": "701c625b174bdb5a9bf1ee362feef845ad511e8a69a9787f78f90aa66bb68716",
      "path": "docs/releases/0.1.6/manifest.json",
      "start_line": 91,
      "end_line": 97,
      "text": "    \"- I-21 (W2-209 S3 red on the base since the authority file went on; a selection miss) and I-22 (W1-35's conftest shadowed in a one-process run) logged\",\n    \"- Merge e2/fix-update-wheel: I-17 fixed, gov update and gov install take a release's own wheel (the kept cut wheel when its hash matches, else a rebuild with or without the build info); the hash check unchanged\",\n    \"- P0-2: the pre-flight refuses STORE_BEHIND\",\n    \"- P0-1: the refresh retried and checked; status, retrieve and brief name a store behind HEAD\",\n    \"- Plan item 0-4 corrected: the kit's licence moves to template/governance/kernel/LICENSE, worded for Gov OS's rights only (a root LICENSE in a product claimed the product's licence and failed gov doctor's path_map in every adopted map, W2-16 [copied] red); I-20 logged (the selection placed template/LICENSE nowhere); the D1 landing brief\",\n    \"- Acceptance tests, red on the base: P0-1 (refresh retried and checked), P0-2 (preflight STORE_BEHIND), P0-3 (kit git hook)\",\n    \"- Fix I-17: gov update/install take a release's own wheel (the cut wheel kept in the share, else a rebuild with or without the pre-F3 build info); the hash check is unchanged\",\n",
      "chunk_id": "4e36798cfa2caf8693170906",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "DAEO-btcs",
      "sha256": "c03e81f3b4654ca5c485c1e45e1a1f47192e59e38d6a0553753b6f64449a3aa5",
      "path": ".tickets/DAEO-btcs.md",
      "start_line": 67,
      "end_line": 78,
      "text": "  ids\").\n- **Starts after the ACT's commit.** An ACT is not a ticket, so `gov plan` cannot hold this ticket on it: the CTO\n  launches it only once the operator has committed ACT-SELECT-FIXES-1 (the map's sha256 `80d47adb410d`). S6 is what\n  makes it tests first: every pinning case is shown red on the map of the ACT's parent.\n- **A new file, not W2-66b's:** `test_w2_66_live_test_map.py` (and its README) is held by W2-66b (`DAEO-zuiy`, in\n  progress), whose KPI keeps every other case of that file unchanged. A file of its own in the same suite folder is\n  selected with W2-66 and needs no change to W2-66b. Its `RECORD_READERS` and `COUPLINGS` fixtures are not touched.\n- **No product code:** nothing in `src/` or the schema changes; a coupling's suites already take node ids.\n- **F1 (a)** (the CTO's choice, 2026-11-09, ACT-SELECT-FIXES-1 \u00a75): the ACT also places in `record_only` the four\n  records the whole case found unplaced, and drops the breadth list's `rep:` line for it, so a selection runs all\n  seven rows. S4 pins that no opt-in list leaves a row out.\n- **Profile LITE:** test cases only, read-only on the live map; an independent test designer, then the CTO's scoped\n",
      "chunk_id": "09dc0fe81a9d21bdde3b6f3e",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "9dcad4b894b31a0f35dc97e9",
      "sha256": "56da9dff69e737f0c891332c04bec3c07178e7c822e84315f69c206de3b5e526",
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "start_line": 35,
      "end_line": 35,
      "text": "| I-29 | 2026-11-25 | A selection bug (X-1): the 0.1.6 release full suite on `7b5650f44` was red on 10 tests the landings' selections never ran: W2-178 (5) and W2-149 S8, the walls changed by FM-5's wall settings template (`indep_launch.py`'s templates map to no wall test); W2-116 S2 (the due rule P0-1 changed) and W2-208 P0-3 [trunk] and [main] (the kit hook, red outside its lead's rig). An 11th, W2-184 S4, is flaky (25 of 25 alone) | `docs/close/nightly/NR-20261125T003933Z-7b5650f44543.json` | the selection's test map (plan 1-0) | fix: the reds by two fix leads (fix-walls, fix-phase0-reds); the edges `governance/project/orchestration/tools/templates/**` -> W2-178, W2-149 and `src/gov/rebuild*` due rule -> W2-116 in plan item 1-0 | 0.1.6 held until green |\n",
      "chunk_id": "9dcad4b894b31a0f35dc97e9",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "f1cd1e58020b6502d968e8c5",
      "sha256": "87e302385fda1fdf40afd4a150cf3d37790b6b32319171b92bd78efe558aed8d",
      "path": "docs/emergency-2/briefs/RESEARCH-step1-tool-map.md",
      "start_line": 32,
      "end_line": 41,
      "text": "  but nothing calls it; `gov impact DEC-1204` ran over 106 s and hit a 150 s timeout (suspected: `_Code.__init__` at\n  `:135-150` waits on the code-index daemon even for a record-only id); nothing compares a ticket's `[Kn]` lines with\n  its spec's K-lines; no test-to-ticket trace; the landing's selection traces code to tests only. Smallest fixes\n  proposed: `_Code` lazy; `gov impact --changed <range>` as a trigger at the landing; a `KPI_DRIFT` finding in\n  `links/check.py`; the back-trace by inverting `accept.runner.parse_map`. Do not write to `/tmp` outside your own\n  scratch folder.\n- **Known since the audits (count them in):** Gov OS made its first `gov queue` landings today (`4f779086f` L2-4); the\n  queue then refused two landings on a target named only in a README map row's notes (`FILE_GONE`, a selection bug to\n  list in the map's gaps under W2-115b); `models-rubric` landed by hand merge (`f6e9e38af`).\n\n",
      "chunk_id": "f1cd1e58020b6502d968e8c5",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "523d339a8b68f603f789b44e",
      "sha256": "c11c718823ff05b715e1eb02b882e804c26ede02334f897c0097d1459bf470a9",
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "start_line": 45,
      "end_line": 59,
      "text": "## 1. Proposal (i): test-map couplings for the miss kinds seen\n\n**What changes.** These go in `governance/project/test-map.yaml`. The map is read by the product's selection,\n`src/gov/close/select.py:404-408`, so no code changes. Three new `couplings:` entries go after the last one (insert\nafter line 167, before `# Moved from the path map` at line 169). One target is added to the existing W1-28 entry\n(lines 162-164):\n\n```yaml\n  - paths: [\"tests/acceptance/**.py\"]                       # existing (line 162); suites gain the W1-50 case\n    suites: [\"tests/acceptance/W1-28/test_w1_28_fixture_copies.py\",\n             \"tests/acceptance/W1-50/test_w1_50_freeze_fixture_settings.py::test_the_two_whole_tree_fixtures_are_found\"]\n    why: \"file scan: W1-28's held-out copy check and W1-50's whole-tree fixture count read every Python source under tests/acceptance/ (I1 \u00a74.1, DEC-385, DEC-912 item 3; P-SELECT-FIXES-1 (i), K10)\"\n  - paths: [\".claude/settings.json\", \".rulesync/hooks.jsonc\", \".rulesync/permissions.jsonc\"]\n    suites: [\"tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py\",\n             \"tests/acceptance/W1-46/test_w1_46_research_installs.py\",\n",
      "chunk_id": "523d339a8b68f603f789b44e",
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
    "duplicates": 14,
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
      "chunk_id": "1c869db104a470d770d34cea",
      "parent_id": "a6a977061e1bd1a6a0d9fe48",
      "path": "docs/emergency-2/briefs/LEAD-fix-select.md",
      "start_line": 1,
      "end_line": 24
    },
    {
      "chunk_id": "6f7275f3710755a37a4a7920",
      "parent_id": "9ddaa6e21f69888f8673f72f",
      "path": ".tickets/DAEO-j9z6.md",
      "start_line": 178,
      "end_line": 189
    },
    {
      "chunk_id": "4614b2f2bea1967a96f9c774",
      "parent_id": "bb8fc7697a3f58b1074bb873",
      "path": "governance/project/orchestration/packages/L2-4-PROVING.md",
      "start_line": 6,
      "end_line": 29
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "path": "docs/releases/0.1.6/NOTE.md",
      "chunk_id": "4d71c4aed654a12b076fe703",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-usage-fix.md",
      "chunk_id": "2e1b73daeb138677d1580958",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/ACCOUNT-2026-11-25.md",
      "chunk_id": "63a68009136d9dfdcdf97525",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH.md",
      "chunk_id": "152e19b9419b6b7cbf542915",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "0c24fc724a00d577a7a00632",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/ACCOUNT-2026-11-25.md",
      "chunk_id": "a85eb6c77e5b71c155532e1f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-select.md",
      "chunk_id": "5d5237b986f5a8f550d3213f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "9c3b144655080ce359d3971a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/ACCOUNT-2026-11-25.md",
      "chunk_id": "fe4f3e7fa9433db38a9cf248",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "chunk_id": "f3ddbdc44944b7b8a07ab0a8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "30fbdf12a1136f2333798c40",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-select.md",
      "chunk_id": "15a534547060395e1ae2be37",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "7910d3644a6ad6ba14d6aca5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/manifest.json",
      "chunk_id": "8a60c6285c43568287970ab8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/manifest.json",
      "chunk_id": "69225e84725cebdeaf8fdb13",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "e2429f455da4a808eb0e40d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/NOTE.md",
      "chunk_id": "6a85841e4cd548e296e2b61a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/ACCOUNT-2026-11-25.md",
      "chunk_id": "f82c6c95e26f309358e09ef6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.6/NOTE.md",
      "chunk_id": "baab709dfa75efe08c08c6bb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "c6b9bd195bab5846f38e3b93",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "114454472cab2a2b6ee0dd24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "51c94448282583d1abd94596",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "d9b51e0d1005a0d899734f97",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "601d25e48ee6e48eb129be26",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "bbf6999bd0560b94178550e6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "f8e59ebf8df307115a47d156",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "885630cdacb19e23a5c2e718",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/test-map.yaml",
      "chunk_id": "b6d138927f99de27f64af452",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "87af7b7ee7ff77183f9d536e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "f59e88f720b5ee1aba5437c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "1879d875a44a02135a1da4b0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "d36c7e6c3033fa125021c973",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "1d4ca6b570cd8d2e84171d97",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "64a4fcacf5bd7337a95d5b8e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "99c850e7e5ed7eed01e32d7d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.csv",
      "chunk_id": "4668c25ae33b75bae31f00e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "5a2123c2fd7e3a5ec23f6dbd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "bdd30a8766cd4c15e3b96d3b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "9d94c9310596909f3fe4fa9a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "7d902df1d575f6682ab65f03",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "246301269d8e38952c4e0dc2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "11a46fe1caf95f21845aafd8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "c98ea5b49644c81cc3c3f9ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/01-landing-templates-briefs.md",
      "chunk_id": "dec619d5503e208f307cd3ce",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "22703223eb3e7b9382b7c76c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "d92ff4a73a753e47b5d69c81",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "636605eb68617e5eea5e0603",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-l2-4-queue.md",
      "chunk_id": "016527e84e52ab1456320ba8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "25a5df5b951c747b4c3684f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH.md",
      "chunk_id": "a92b54bc9afedcef46e9a218",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "c96a2d2e3357243e414ae26b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "b16700fd124eab81de1a188e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "e59765e4d0bdfc21a9b68b90",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "4726a9fe271c5d81c6122538",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "d7ecbedfb05da14a31f65536",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "6238122267400dd1c0460972",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "08c3a6ab1bb6dbed0868b515",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "45485f969662ed32b4363667",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "d31243234d1ce38230e850f1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R1-GOVCHECK.md",
      "chunk_id": "271dab6d987d0a9d88e4696b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "143ff4a3e591a6b046c96122",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "b038dc216e5088bab1047d6f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "18ab62a513892f4edc12ca1e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "342b564afdf6ebff8cd22b79",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "395f766bd23f48a657f9c450",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "8d4789f10211a38a5255e45e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/D6-PART2.md",
      "chunk_id": "5163bd0592a99a30fc398077",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "46ad0b64a2a490dd61b442e5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "75a191f2b78bb1e16d436a62",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "3459e54c5e11f661c4c92e4f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/MORNING-BRIEF-2026-11-19.md",
      "chunk_id": "7270a0ea2d2e3ef469cf4533",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "4e433d38c9370738dec705d0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-btcs.md",
      "chunk_id": "a8ffec9741ded34b9369beae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "c3ed2f075e63c31d29b55d72",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "f4f73d049143d6bee93b7c24",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "19ad1f4d4f51784760c0b872",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "c3da4bedb68631676364b0c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/test-map.yaml",
      "chunk_id": "69775b96277a856284975a21",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-66/README.md",
      "chunk_id": "8464bdb379cfdf1ad0014213",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "f7fb064a036be063fd816ac4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "ddef442bf0a638230d8a435a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "bb83644e0cd4366ecd463298",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "808e2b1b8bcabec54eb691de",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "b9ccc4dd20459739f9bdfff7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/LIFT-1/R1-GOVCHECK.md",
      "chunk_id": "041553c94cbc3d80f154341f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "d9fff3e35fdaa4673e82d71b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "3740d31a49f752bd1db16fd7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "e48bf87b739ca3ebce4b1487",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "ba35b5ec9f6d67dfaaffe139",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "4fad9125035369d26812cfd8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "6e9019ca52af518ef1092dcc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "34adc2836135f84328cac5a0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/close/select.py",
      "chunk_id": "f77b3fb6503652a85256264b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "089a71ead1ce41b370988f55",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-btcs.md",
      "chunk_id": "01b0e0d8d3eab6f43335e9c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "ea7a19b96ba508cec815c8c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH-RESULT.md",
      "chunk_id": "ad379569ddf6da946e741142",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "79b7aee9706b1ef29de0931e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "f39ccc24075214442bec46d2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "abc74248c32273f1c022bc7b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-FIXES-1.md",
      "chunk_id": "602043d58ffaf7c20bf6701f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-gate-null.md",
      "chunk_id": "5e17ee4e1d7bf08157ac77dd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.2/manifest.json",
      "chunk_id": "ffae2e205e3c8f0812dd59b7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "82497daab714537dccd10313",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "9f2130430da7c1f6691dea82",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-115b/README.md",
      "chunk_id": "2c87feabce04a5834d8a3153",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "9b0ebfe72ee53d6ed08dd309",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "6a9dee6e838a6b4ead5fa878",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/P-SELECT-GRAPH.md",
      "chunk_id": "29a4728ff5166eec795b9891",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "19f49b00a88a8f0fb42c62e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-j9z6.md",
      "chunk_id": "505aad0ca390dc8fc4608318",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-repin-registry.md",
      "chunk_id": "8bddcf02e1a8d3476fd221da",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/TEST-AUDIT-TI8-2026-11-19.md",
      "chunk_id": "23addef9b6f75f274071a2a6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-memaudit-3.md",
      "chunk_id": "63ba33081f31cfb82cce61bf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-btcs.md",
      "chunk_id": "21b4797b6431ae26f00ea21e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/gov-os-decisions.html",
      "chunk_id": "31e06433170c00c3848ec1c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "3b3f0d6d550d9628abcb700d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "6d6f0442e46fb07e775158ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.3/manifest.json",
      "chunk_id": "0e6df2c00852ec3e1916a723",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/SMART-WORK-1.md",
      "chunk_id": "340da290522b65abaa4f7d3e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep-schemas/indep-counts.schema.json",
      "chunk_id": "34515452398424ca068391bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-usage-per-repo.md",
      "chunk_id": "80ab77adc03f7f2266a40100",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/CHAIN-DISCOVERY.md",
      "chunk_id": "e027fcbcac84ca70154d534e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-92-evidence.md",
      "chunk_id": "58a38828470f0f1e867db807",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "4ca4b9395f95dd6f60b3ea7f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-115b/README.md",
      "chunk_id": "ad20842ee8650d4f52168233",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I4-records-plan-rest.md",
      "chunk_id": "c59be9ed56b42d719eb64b6a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "1f8919d3d28760ebfd378128",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "ea7ac3e7b6296c3a500885ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I2-close-checks-ratchet.md",
      "chunk_id": "2e5a66fe8ba9bddd3c65b05a",
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
      "used": 5799
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyIudGlja2V0cy9EQUVPLWJ0Y3MubWQiLDY3LDc4LCIwOWRjMGZlODFhOWQyMWJkZGUzYjZmM2UiXSxbIi50aWNrZXRzL0RBRU8tajl6Ni5tZCIsMTE0LDEyMywiNzg2N2FhMDc1NzJmZTQwNTVkOGMzMTU0Il0sWyIudGlja2V0cy9EQUVPLWo5ejYubWQiLDEyMiwxMzEsIjIwZWY1Yjk3NmY1OWYzZWM2MTYzZDA2YyJdLFsiLnRpY2tldHMvREFFTy1qOXo2Lm1kIiwxMzAsMTM5LCJkZDE1MjYxYTdiYzA4NzRlOWQ4NWU5NDciXSxbIi50aWNrZXRzL0RBRU8tajl6Ni5tZCIsMTg3LDE4OSwiNWY3NzVmZjJlZjYyZTNlYWI4MTI5YzA2Il0sWyJkb2NzL2VtZXJnZW5jeS0yL2JyaWVmcy9MRUFELWZpeC1zZWxlY3QubWQiLDEyLDIxLCJkZWEzOGRlNWNiM2NmZmRlODIyODE1ZmUiXSxbImRvY3MvZW1lcmdlbmN5LTIvYnJpZWZzL1JFU0VBUkNILXN0ZXAxLXRvb2wtbWFwLm1kIiwzMiw0MSwiZjFjZDFlNTgwMjBiNjUwMmQ5NjhlOGM1Il0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL0FDQ09VTlQtMjAyNi0xMS0yNS5tZCIsMTQ4LDE1MCwiNGM4OWZkNWY1MmE4NmJlZmIyYWJlMDFkIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL0ZJTkRJTkdTLm1kIiwxLDcsImRiYjM5N2VkNDI5YzJiOWNmZGY5NjE2MCJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9GSU5ESU5HUy5tZCIsNyw4LCJlNGNkZjFjNmM1OTczNzQ5MDA2ZTYzODAiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vRklORElOR1MubWQiLDI1LDI2LCIyMGQ1YWM5MThjYWUyMDY4NjdjOTdlZjMiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vRklORElOR1MubWQiLDI2LDI2LCIyZWYyYmZmZjUyYWY1YTBkNzliYjA4ZjEiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vRklORElOR1MubWQiLDM1LDM1LCI5ZGNhZDRiODk0YjMxYTBmMzVkYzk3ZTkiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vVE9PTC1NQVAubWQiLDU0LDU1LCJiZDBhNThiOGVmYTE5NDgzZDk2M2FiY2MiXSxbImRvY3MvcmVsZWFzZXMvMC4xLjYvbWFuaWZlc3QuanNvbiIsOTEsOTcsIjRlMzY3OThjZmEyY2FmODY5MzE3MDkwNiJdLFsiZ292ZXJuYW5jZS9wcm9qZWN0L29yY2hlc3RyYXRpb24vcGFja2FnZXMvUC1TRUxFQ1QtRklYRVMtMS5tZCIsNDUsNTksIjUyM2QzMzlhOGI2OGY2MDNmNzg5YjQ0ZSJdLFsic3JjL2dvdi9jbG9zZS9zZWxlY3QucHkiLDg0OCw4NjAsIjdjNjhiYjdiZGVkMjkwM2IyOWNjMDhmNSJdXSwiZiI6Ii9ob21lL3VzYWluL2dvdi1vcy13b3JrdHJlZXMvVzItMDAtc3RvcmUtYiIsImkiOltdLCJvIjoyMCwicCI6eyJiIjoic2VydmljZSIsImQiOiJjdWRhOjAiLCJoIjoiNjI0NTM2ZDFlNjc2OTM0NiIsIm8iOlszNCwwLDIyLDE3LDM2LDIsMTIsOCw3LDMsMSwyNywzMCw0LDE1LDIwLDEzLDksMzEsMTAsMTgsMTEsMTYsMjYsMzUsNSwxOSwzOCwxNCwyNSwzOSwyOSw2LDI4LDIxLDM3LDIzLDMyLDMzLDI0XX0sInEiOiJIb3cgZG9lcyBnb3YgcXVldWUgLS1zZWxlY3QgY29tcHV0ZSBpdHMgc2VsZWN0aW9uICh0aGUgYmFzZSByZWNvcmQsIGNoYW5nZWQgZmlsZXMsIHRoZSB0ZXN0IG1hcCwgY291cGxpbmdzLCB1bnBsYWNlZCkgYW5kIHdoeSBkb2VzIGl0IHBpY2sgMzAwIHRvIDQwMCBzdWl0ZXM7IHdoaWNoIGVkZ2VzIGFyZSBtaXNzaW5nIChJLTIwLCBJLTIxLCBJLTI5KT8gQ29kZSBsb2NhdGlvbnMsIGNvbnZlbnRpb25zLCBlYXJsaWVyIGZpeGVzIGFuZCBmaW5kaW5ncy4iLCJyIjowLCJzIjoiZWEyMDE2YmU5ODAyNzZmYjJlODk3MGMzMzNmMzZhMjQ0YzI1NGIyMSIsInQiOm51bGwsIngiOlsiOWRkYWE2ZTIxZjY5ODg4Zjg2NzNmNzJmIiwiYTZhOTc3MDYxZTFiZDFhNmEwZDlmZTQ4IiwiYmI4ZmM3Njk3YTNmNThiMTA3NGJiODczIl19",
  "routing": {
    "code": [],
    "named": [],
    "phrasings": [
      "How does gov queue --select compute its selection (the base record, changed files, the test map, couplings, unplaced) and why does it pick 300 to 400 suites; which edges are missing (I-20, I-21, I-29)? Code locations, conventions, earlier fixes and findings.",
      "gov queue --select compute selection base record changed files test map couplings unplaced pick 300 400 suites edges missing I-20 I-21 I-29 Code locations conventions earlier fixes findings."
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
        "chunk_id": "dea38de5cb3cffde822815fe",
        "path": "docs/emergency-2/briefs/LEAD-fix-select.md",
        "start_line": 12,
        "end_line": 21
      },
      {
        "chunk_id": "5f775ff2ef62e3eab8129c06",
        "path": ".tickets/DAEO-j9z6.md",
        "start_line": 187,
        "end_line": 189
      }
    ]
  }
}
```
