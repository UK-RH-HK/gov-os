# W2-153 acceptance tests: the role template delivered at launch

Ticket DAEO-8s85 (W2-153, W2-128 TPL-4), profile STANDARD. Written by the independent test designer (MR-3) from
the ticket's five KPI lines, its two failure lines and its body's "Interface", before any implementation, reading
the ticket, `packages/LIFT-1/R3-TEMPLATES.md` §B ("Delivery") and §D TPL-4, `packages/ACT-CLAUDE-COPIES-1.md`, and
integrate's code (DEC-963). The ticket's implementation was never read.

## How they run

    PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-153 -q -p no:cacheprovider \
      -o tmp_path_retention_policy=failed

About 6 s, 66 cases (revision 4). No model, network, GPU or store, and no real Claude session. Needs `git`, `bash` and the
baseline commit in the repository's history.

- **`gov launch` (S1, F1, F2).** Each case runs `gov.launch.launcher.launch` (the launcher's public entry) in a child
  process (`w2_153_launch_harness.py`) with `HOME` set to a temporary folder. There `.local/bin/claude` is a stand-in
  that writes down its arguments, its working folder and its `TMPDIR`, then ends. It finds where to write in
  `claude.record` beside it, as the launcher passes the session a cleaned environment (W2-56 S5). The fixture repository has four
  `in_progress` tickets, the guard's settings and the eight `.claude/templates/` copies. The resource gate is planted
  open the way W2-136's launcher cases plant it (`gate.json` and the `GOV_RESOURCES_*` readings). The gate, the start
  lock, the registry and the session's temp folder all run as written, inside that home. One thing is replaced, the
  same way for both trees: the plan's check of a lead (`launcher.check_lead`) admits every ticket, because the
  fixture has no ready list and W2-153 is not about the plan.
- **The dispatcher's lead line (S2, F1, F2).** `launch_now.sh` names its paths absolutely, CLI included
  (`/home/usain/.local/bin/claude`), so a stand-in early on `PATH` alone would not catch the call. Each case runs a
  copy whose absolute paths (the orchestrator folder, the main repository, the worktrees folder, the CLI and
  `/home/usain`) are rewritten in one pass into a temporary folder. That folder holds a disk gate that passes, the
  brief, the log folder and the lead's tree. The stand-in is also first on `PATH` and at `$HOME/.local/bin/claude`.
  A copy with any `/home/usain` path left in it is not run.
- **The portability check (S3, S4).** A fixture project in this repository's layout, as the unit tests build theirs
  (`tests/unit/adapters/test_portability.py`; this folder is the only one the designer writes, so the "one case" is
  here). It has one kernel role (engineer), its template and the other seven, the one kernel skill it lists, the
  rulesync source composed as S3 states, the eight copies, and a stand-in rulesync that writes the generated files
  the project holds. The check runs as `python3 -m gov.adapters.portability` in that project.
- **Writer and sources on this repository (S3, S4).** The writer runs from the repository's root into a temporary
  folder. The twelve role sources (`.rulesync/subagents/` and `template/.rulesync/subagents/`) are read where they
  are.
- **F2's baseline** is integrate at `f73e72d4a43b`, the commit W2-153 is built on (`git merge-base w2/W2-153
  w2/integrate`, read 2026-11-10; DEC-1112 (3)). Its launcher is integrate's as of the W2-56 merge (`cf23e9f8dc1f`):
  S5's cleaned environment (`PATH`, `HOME`, `LC_ALL` in the worker's `--settings` env) and the sandbox entries for
  the session's runs folder and the reranker. Its `src/gov` is unpacked with `git archive` into a temporary folder
  once per session, and its `launch_now.sh` is read with `git cat-file`. Both are taken only after the blob ids are
  checked: `launcher.py` `91033723374d`, `launch_now.sh` `bd8f45b9d3dd`. A moved integrate therefore never changes
  what F2 compares against. **Moved in revision 3** (DEC-866 `Rewrite-Reason:`) from `1ef1a7a48c53` (launcher
  `5ecd20c0d252`, before W2-56), against which F2's five worker cases failed whatever W2-153 did. Nothing else in F2
  changed: the comparison still allows only the one appended flag. Integrate's later W2-56 follow-ups (`4bc040898467`,
  launcher `feec5c25458b`) are not in W2-153's base and so not in the baseline.

## The interface as read (the ticket's body)

- **Map:** engineer → `role-engineer`, independent-test-designer → `role-test-designer`, independent-auditor →
  `role-reviewer`, product-spec → `role-product-spec`, research → `role-research`, lead and orchestrator →
  `role-lead`.
- **Flag:** `--append-system-prompt-file <root>/.claude/templates/<stem>.md`, appended after the caller's arguments,
  with an absolute path, where `<root>` is the launch's repository root (its real path). A missing file refuses with
  `GovError` `LAUNCH_NO_TEMPLATE` naming that path, and no session starts.
- **Skills lists** (under `claudecode: skills:` in each source, DEC-1112 (3): rulesync 24.0.0 drops a top-level
  `skills` from the generated agent, so a list there would deliver nothing): engineer `[test-driven-development]`, independent-auditor `[audit]`, product-spec `[change]`,
  research `[discovery]`, orchestrator `[orchestration]`. The test designer gets `[test-design]` only once W2-128 has
  reconciled that skill with DEC-963, which the case reads as "the kernel skill names DEC-963". Until then the list
  leaves `test-design` out, so it is empty or absent. On integrate today the skill does not name DEC-963.
- **The composition (S3 amended, 2026-11-10, the CTO, DEC-1112 (3); revision 4).** Each `.rulesync/subagents/<role>.md`
  and its `template/.rulesync/` copy is the rulesync front matter (with `claudecode.skills`), then the role template's
  body, then one blank line, then the kernel role file's body (`template/governance/kernel/roles/<role>.md`
  verbatim, its front matter, if any, stripped). Each body is read by portability's `_split` rule (front matter
  stripped, the blank lines after it dropped). The templates end with one newline, so the blank line is one more
  `\n` (`w2_153_support.composed_body`). The agent's labelled fields are then exactly the role file's (W1-33, MR-5;
  W1-38), the templates carrying none. **Interface:** `gov.adapters.portability.compose(root, role) -> str`, the
  expected source's full text. The cases call it as `compose(Path(<project root>), "engineer")` in a child process
  on this tree's code.
- **Copies:** `brief`, `role-research`, `role-product-spec`, `role-test-designer`, `role-engineer`, `role-reviewer`,
  `role-lead`, `role-cto`, byte copies of `template/governance/kernel/templates/<stem>.md`. `ticket.md` and the
  kernel's other templates are not copied.

## Revision 4: S3 amended (2026-11-10, DEC-1112 (3), DEC-866 `Rewrite-Reason:`)

After ACT-CLAUDE-COPIES-2 the composed agents lacked the role file's fields, which W1-33 (MR-5) and W1-38 require.
The CTO amended S3 (the ticket's body, "S3 amended"): the role file's body follows the template's. This revision was
written on integrate `bbe222c59`, which holds W2-153's first composition (the template's body alone, the check
comparing against it).

- **Changed:** the sources case (renamed to `test_s3_each_role_source_is_its_front_matter_its_skills_its_template_s_body_and_its_role_file_s_body`)
  expects the template's body, one blank line and the role file's body; the rest of its assertions is unchanged. The
  portability bed's source (`w2_153_support.composed_source`, `ENGINEER_COMPOSED_BODY`) is composed the same way.
  That is fixture text only: no assertion of the bed's cases changes.
- **Added:** `test_s3_compose_returns_the_source_s_full_text_and_the_check_accepts_it` (2 cases),
  `test_s3_a_source_with_the_template_s_body_alone_is_a_finding` (1), and
  `test_s3_the_source_s_labelled_fields_are_its_role_file_s_and_the_template_contributes_none` (12). The last
  reproduces W1-33's `fields()` rule in `w2_153_support.fields` (no import of W1-33's support, which pulls in W1-46's).
- **Outside this folder (the same commit):** W1-38's `build_project_from_template` copies the kernel's `templates/`
  and writes the eight `.claude/templates/` copies (see W1-38's README, "The revision of W2-153"). W2-05's hooks-source
  cases move `templates` with the rest of the kernel. W2-57 uses W1-38's builder unchanged.
- **Self-check (a scratch copy of integrate's `src/gov`, never committed):** a reference `compose` and the check
  comparing against the amended composition passed all ten bed cases (the writer case left out). In memory, each
  source composed from this repository's front matter, template and role file passed both sources cases for the six
  roles.

## KPI lines, tests, and the outcome on `w2/integrate` (`f73e72d4a43b`)

**Revision 4, on integrate `bbe222c59` (W2-153's first composition merged):** 66 cases, 30 failed, 36 passed. The 30
reds: S3's sources case (12) and labelled-fields case (12), compose (2), the template's body alone (1), and the three
bed cases whose consistent source is now the amended composition (3). Every other case is green there, W2-153's first
build (S1, S2, S4 and the first S3) being merged. The table's "On integrate" column is revision 3's (`f73e72d4a43b`,
before that build), except for the rows marked "revision 4", and the paragraph that follows is revision 3's, kept for
its history.

Run in the launch sandbox on integrate's code (this branch, integrate merged, launcher `91033723374d`, revision 3,
2026-11-10): **51 cases, 38 failed, 13 passed** (about 5 s). F2's eleven cases are green here, the tree's launcher being
the baseline's. **On W2-153's branch F2 is expected green if the appended flag is the only change** to the built
arguments and the lead line; any other difference from `f73e72d4a43b` is red. Every red fails on
what its KPI line asks for, none on a premise. A reference build (below) passed the first 50; revision 2 (DEC-1112
(3)) moved the skills list under `claudecode` and added one case.

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_153_launch.py::test_s1_the_launch_passes_the_role_s_template_after_the_caller_s_arguments` | red (7 roles) | the built arguments carry no `--append-system-prompt-file` |
| S1 | `test_w2_153_launch.py::test_s1_with_no_caller_arguments_the_flag_is_still_passed_last` | red (engineer, lead) | no flag |
| F1 | `test_w2_153_launch.py::test_f1_a_missing_template_refuses_with_launch_no_template_naming_the_path_and_starts_no_session` | red (7 roles) | the launch starts the stand-in CLI without the role's copy |
| F1 | `test_w2_153_launch.py::test_f1_guard_a_copy_no_launch_uses_missing_refuses_nothing` | green (guard) | without `brief.md` and `role-cto.md` a worker and a lead still start; the refusal must be for the role's own copy only |
| F2 | `test_w2_153_launch.py::test_f2_the_built_arguments_are_integrate_s_but_for_the_one_flag` | green (guard, 7 roles) | this tree's launcher is integrate's; with the flag taken out the arguments must stay equal to integrate's |
| F2 | `test_w2_153_launch.py::test_f2_guard_integrate_s_launcher_starts_on_the_same_fixture_without_the_flag` | green (guard, engineer, lead) | the baseline runs on the fixture from integrate's unpacked `src` and carries no flag |
| S2 | `test_w2_153_dispatch.py::test_s2_the_lead_line_passes_the_flag_with_role_lead_md` | red | the lead line carries no flag |
| F1 | `test_w2_153_dispatch.py::test_f1_the_lead_line_refuses_when_role_lead_md_is_missing` | red | the lead line starts the stand-in (exit 0) without `role-lead.md` |
| F2 | `test_w2_153_dispatch.py::test_f2_the_lead_line_is_integrate_s_but_for_the_one_flag` | green (guard) | the script is integrate's; with the flag taken out its arguments and working folder must stay integrate's |
| F2 | `test_w2_153_dispatch.py::test_f2_guard_integrate_s_lead_line_starts_on_the_same_bed_without_the_flag` | green (guard) | the baseline runs on the bed, in the lead's tree, with the lead's settings and no flag |
| S3, S4 | `test_w2_153_portability.py::test_s3_s4_a_project_with_the_composed_source_and_the_eight_copies_is_reported_consistent` | red (revision 4: the reason) | `SOURCE_DIFFERS`: integrate (`bbe222c59`) compares the source with the template's body alone, not the template's body, a blank line and the role file's body (S3 amended) |
| S3 | `test_w2_153_portability.py::test_s3_a_source_that_keeps_the_kernel_role_file_s_body_is_a_finding` | red on `f73e72d4a43b`; green (guard) in revision 4 | the role file's body alone is a finding on `bbe222c59` too (it compares the template's body); it must stay one under the amended composition |
| S3 | `test_w2_153_portability.py::test_s3_a_source_with_the_template_s_body_alone_is_a_finding` | red (revision 4) | the template's body alone (W2-153's first composition, integrate's) is no finding on integrate; amended, it lacks the role file's fields |
| S3 | `test_w2_153_portability.py::test_s3_compose_returns_the_source_s_full_text_and_the_check_accepts_it` | red (revision 4; 2: `composed`, `template-body-alone`) | `ImportError`: integrate's `gov.adapters.portability` has no `compose` |
| S3 | `test_w2_153_portability.py::test_s3_the_skills_list_is_part_of_the_composition` | red | the composed source is a finding on integrate (its first half) |
| S3 | `test_w2_153_portability.py::test_s3_a_skills_list_at_the_top_level_is_a_finding` | red | the composed source (list under `claudecode`) is a finding on integrate (its first half); its second half makes the same list at the top level, with none under `claudecode`, a finding (DEC-1112 (3)) |
| S4 | `test_w2_153_portability.py::test_s4_a_changed_copy_and_a_missing_copy_are_findings` | red | integrate does not look at `.claude/templates/` |
| S4 | `test_w2_153_portability.py::test_s4_a_copy_differing_by_one_byte_is_a_finding` | red (2: trailing newline, line ending) | the same; the two cases make sure the copy is compared byte for byte |
| S4 | `test_w2_153_portability.py::test_s4_the_writer_writes_the_eight_copies_byte_for_byte` | red | integrate's `main()` takes no arguments: it runs the check and writes nothing |
| S3 | `test_w2_153_sources.py::test_s3_each_role_source_is_its_front_matter_its_skills_its_template_s_body_and_its_role_file_s_body` | red (6 roles × 2 trees; renamed in revision 4) | the sources hold the template's body alone (W2-153's first composition, on integrate), not the template's body, a blank line and the role file's body; the `claudecode.skills` list and the front matter checks are unchanged (a top-level `skills` refused; the front matter equal to integrate's but for `claudecode.skills`) |
| S3 | `test_w2_153_sources.py::test_s3_the_source_s_labelled_fields_are_its_role_file_s_and_the_template_contributes_none` | red (revision 4; 6 roles × 2 trees) | the sources carry none of the role file's labelled fields (W1-33's `fields()` rule): missing purpose, allowed paths, tools, network, model tier, authority level, handoff format and permission classes (research: seven, it has no permission classes field); each role template carries none, as the case requires |
| S3 | `test_w2_153_sources.py::test_s3_guard_the_check_finds_no_role_source_drift_in_this_repository` | green (guard) | the check, run from this repository's root without rulesync, names no `subagents` source; it must stay so once the sources and the check change together |
| S5 | untestable here | none | the CTO's evidence: see below |

**S5 is not a test here.** It asks that W2-153 land at the `.claude/` copies ACT, so that the copies (S4's writer)
and the rulesync outputs (S3) are installed in the same ACT that makes S1 and S2 live, and no launch is refused for a
missing copy (CAP-33, DEC-315). The copies are written only by the ACT. This ticket commits no `.claude/` file, and
the ACT's record (`ACT-CLAUDE-COPIES-1` or its successor) is the owner's operator's, outside this ticket's paths. The
CTO verifies it from that record, as the ticket's Verify line says. Until the ACT runs, the portability check on this
repository reports the eight copies as missing. That is expected, and no case here asserts on the repository's own
`.claude/templates/`.

**A check of the tests themselves** (a throwaway shared clone at `1ef1a7a48c53`, removed afterwards, never
committed): a minimal reference build was written there. It had the map and the refusal in `launcher.py` (flag
appended after the caller's arguments), the composition, the copies' check and `--write-templates` in
`portability.py`, the dispatcher's file check with the flag placed *before* `-p` (so F2 does not depend on where the
flag goes), and the twelve sources composed. It passed all 50 cases. Two wrong builds each failed the cases meant
for them: an extra `--verbose` beside the flag failed F2 for all seven roles (and S1's caller-arguments check), and
the dispatcher without its file check failed its F1.

## Notes and limits (interface gaps; also the return's `discoveries`)

- **D-1. The templates' own `skills:` differ from the ticket's lists.** The kernel templates' front matter names
  research `[discovery, retrieval]`, product-spec `[discovery, change]`, engineer `[test-driven-development,
  systematic-debugging]` and lead `[orchestration, checkpoint]`. The ticket's Interface names one skill each. These
  tests follow the ticket.
- **D-2. "The kernel role file's front matter".** The kernel role files (`template/governance/kernel/roles/*.md`)
  have no front matter. The tests read S3 as the ACT note does: the source keeps its rulesync front matter (`name`,
  `targets`, `description`, `claudecode.tools`), checked equal to integrate's at the baseline commit, plus
  `claudecode.skills` (DEC-1112 (3); no top-level `skills`). The tools check against the role file's Tools field is
  left as it is. The portability bed's source plants its list under `claudecode` too.
- **D-3. `--write-templates <dir>`.** The ticket does not say whether `<dir>` is the copies' folder or a root under
  which `.claude/templates/` is made. The writer case accepts either (exactly the eight files, in one of the two). It
  runs from the repository's root, so it reads that root's kernel.
- **D-4. The dispatcher has no test hook,** and its CLI path is absolute. The cases rewrite the script's absolute
  paths. An implementation that finds its paths another way (from `$0`, or another environment variable) would
  reach paths the copy does not rewrite, and the case says so by failing.
- **D-5. S2's refusal** is checked as a non-zero exit with no session started. The KPI line asks for no message or
  code.
- **D-6. The `gov launch` command line** (`python3 -m gov.cli.main launch …`) is not run: it needs the project's
  configuration, and the KPI line names the launcher. The cases call `gov.launch.launcher.launch`, the function the
  command calls.
- **R-1. F2's and S3's baseline commit.** If W2-128's round 2a changes a role source's rulesync front matter
  (description or tools) before W2-153 lands, the sources case flags it as a front-matter change. The baseline
  commit (`w2_153_support.BASELINE_COMMIT` and its blob ids) then moves to a commit holding that change, a one-line
  edit by the test designer. Done once in revision 3 for W2-56's launcher (`1ef1a7a48c53` → `f73e72d4a43b`).

- **D-7. `compose`'s arguments (revision 4).** The ticket states `compose(root, role) -> str`. The cases pass `root`
  as a `pathlib.Path` and `role` as the kernel role file's stem (`engineer`), and require a `str`. They check the
  returned text's front matter as a mapping (the YAML's layout is not compared) and its body exactly. The front
  matter expected is the fixture source's own (`name`, `targets`, `description`, `claudecode.tools`) with
  `claudecode.skills`. The case's second form plants a stale source (the template's body alone) and requires the
  same text, because the copies ACT's builder writes `compose`'s text over the sources. A `compose` that reads the
  front matter from elsewhere than the source passes if the mapping is the same.
- **D-8. The template's contribution (revision 4).** "The template contributes none" is read as: W1-33's `fields()`
  finds no labelled field in the role template's text. On integrate all six templates hold none. A template that
  gains one fails the labelled-fields case on its premise line, naming the template, not the source.

## Files

- `w2_153_support.py`: the map, the skills lists, the eight stems, the baseline commit and blobs, the three beds
  (`LaunchBed`, `DispatchBed`, `PortabilityBed`, which also calls `compose`), S3 amended's `composed_body`, W1-33's
  `fields()` rule reproduced, the stand-in CLI and the helpers.
- `w2_153_launch_harness.py`: one `launch()` call in a child process, its outcome written as JSON.
- `conftest.py`: puts this folder on the import path, and unpacks integrate's `src/gov` once per session.
- `test_w2_153_launch.py` (S1, F1, F2), `test_w2_153_dispatch.py` (S2, F1, F2), `test_w2_153_portability.py` (S3,
  S4), `test_w2_153_sources.py` (S3).
