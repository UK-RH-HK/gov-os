# W2-192 acceptance tests: adoption stage AS, the spec audit

Ticket `DAEO-mpq2` (W2-192), profile FULL, class C2. Written by an independent test designer (MR-3) before the
implementation, from the ticket's KPI lines (S1-S3, F1) as described behaviour (DEC-136), reading only the code as it
stands at the ticket's base (DEC-820, DEC-963). Sources: DEC-1200 (4), DEC-1199, DEC-974, CAP-44,
`governance/project/orchestration/packages/P-ADOPT-SPEC-AUDIT-1.md` section 2 and step 3 of the EXAMIN Wave 0 brief.
(These are the acceptance cases; the ticket's `verify` column names the engineer's own unit tests under
`tests/unit/adopt/test_w2_192_*.py`, which are not here.)

## What the tests reach

Every case runs `gov adopt --lite --stage <S> --json --session <name>` as a child process, as an adopter runs it, on a
project planted in a temporary folder as its own git repository (never this repository or a worktree of it). The child
gets W2-23's environment (empty `HOME`, no `GOV_ROLE` or `GOV_TICKET`, no network, no model; the `src/` of the tree the
suite stands in first on `PYTHONPATH`). Git calls carry pinned author and committer variables and no global config. The
one read of `gov.adopt.command.STAGES` is made in a child process of the same environment.

- **Support:** `w2_192_support.py` *reuses W2-23's support by import* (`w2_23_support`: the child's environment,
  `Adoption`, `refusal`, `succeeded`, `git`, `at_head`, `frontmatter`, `commit_all`), and adds the W2-192 project and
  readers (the AS record's front matter, the byte snapshot of F1, the record rewrite of S3).
- **One planted project**, carried through A0, A1 and A2 once per session and **copied per case** (`conftest.py`); AS
  is run once on one copy (`audited`) and the cases that only read the record share it; a case that changes the
  project copies it first. The fixtures never assert an AS outcome (a failing fixture would show an error, not a red
  case): each case asserts it.
- **The cases read the committed record's front matter** (`yaml.safe_load` of the part between the first two `---`
  lines), never the body's wording.

| Planted file | What it is | Used by |
|---|---|---|
| `specs/alpha.md` | spec, `type: spec`, title "Alpha harbour ledger", wave 1, status accepted; names `` `src/alpha.py` `` (tracked, tested) | built |
| `specs/beta.md` | "Beta berth planner", wave 2, draft; names `` `src/beta.py` `` (tracked) and `` `src/beta_extra.py` `` (not tracked) | partly built |
| `specs/omega.md` | "Omega tide forecaster", wave 3, proposed; names `` `src/omega.py` `` (not tracked) | not built |
| `src/alpha.py`, `src/beta.py`, `src/gamma.py` | flat top-level modules, one commit of their own with the test; `gamma` is named by no spec | modules, code with no spec |
| `tests/test_alpha.py` | names `src/alpha.py` and imports `alpha` | built's test evidence |
| `.tickets/FIX-aa01.md`, `.tickets/FIX-bb02.md` | `status: closed` wave 1 (tag `wave-1`); `status: open` wave 2 (tag `wave-2`) | tickets |
| path map | namespaces `harbour` (W2-23's), `specs`, `tickets`, `code`, `tests`: every tracked file held, each with an exact `embedding_policy` (`embedded` or `not embedded`, three embed), so A3 has no other reason to refuse | all |

W2-23's loose `lib/` and `scripts/` code is left out of the planting, so the only `.py` files are the three modules
and the test (no assertion is made about any file outside the forms the brief states).

## How to run

```
env HOME=<an empty folder> PYTHONPATH=<worktree>/src TMPDIR=<a writable temporary folder> \
  python3 -m pytest tests/acceptance/W2-192 -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  -m "not local_only" -k "not real and not green_here and not time_limit"
```

About 1.5 s on the code before the change, about 3 s once AS exists (A0-A2 run once; AS once; each A3 case runs on a
copy). No case is `local_only`, serial-only, `skip`, `xfail` or `flaky`; no case name holds `real`, `green_here` or
`time_limit`.

## The interface the cases hold

Stated by the ticket: `gov adopt --lite --stage AS [--session <name>] [--json]` after A0, A1, A2 on a clean tree commits
`governance/adoption/AS-spec-audit.md`; `command.STAGES` holds `"AS"` with A2 before it and A3 after; A3 before AS is
recorded is refused and writes no A3 record.

Stated by the lead for want of it in the ticket (held exactly):

- A3 before AS: `ADOPT_STAGE_MISSING`, naming `AS` (message or details). After AS, A3 with `artefacts: []` succeeds.
- The record is `gov.adopt.project.record_text`'s form (`stage: AS`); its front matter keys: `specs` (`path`, `title`,
  `wave`, `status`, `built` = `built` / `partly built` / `not built`, `evidence` = lists `code`, `tests`, `commits`),
  `modules`, `tickets` (`id`, `wave`, `done`), `specs_without_code`, `code_without_spec`, `gaps` (`subject`,
  `question`, `answer`).
- Spec, module and ticket forms, and the built / partly / not rules, as the brief states them.
- The lite checks are applied where `gov adopt` reads the AS record (A3 on it): an `ADOPT_` code that is none of
  `ADOPT_STAGE_MISSING`, `ADOPT_CHAIN_BROKEN`, `ADOPT_PROPOSAL_REFUSED`, `ADOPT_TREE_NOT_CLEAN`, naming the module, the
  spec or the gap's subject; no A3 record. **Its name is not pinned.**
- F1: AS changes no byte outside `governance/adoption/` (HEAD and the working tree); every gap's `answer` is empty
  after AS and stays empty after A3 reads the record.

**Not stated, so not asserted:** the record's body wording; the codes of AS's own refusals (the one case of AS before A2
asserts only a refusal with an `ADOPT_` code); the order of any list; whether AS stands in `gov.adopt.project.STAGES`
or is checked by A3 another way; the owner's route that writes an answer (no case writes one).

Two cases rest on a reading of the KPI line, not on a sentence of the lead's brief; both are named here so they can be
dropped without touching the others: (1) `test_s1_as_before_a2_is_refused_and_writes_no_record` (S1: AS "reads A1's
inventory and A2's classes", so with no A2 record it must refuse; the code is not pinned) and (2) the spec half of S3,
`test_s3_a_record_that_leaves_out_a_spec_is_refused_naming_it` (S3: "names every spec ... the inventory holds"; the brief's
S3 recipe names the module and the question only). Also read from the line, not stated: a commit hash of the built spec's
evidence is a prefix of at least 7 characters of the commit that touched `src/alpha.py`; every `code` and `tests` item
of evidence is a file tracked at HEAD (so the untracked `src/beta_extra.py` is no evidence).

## The map

| KPI | Tests | Expected outcome on the code before the change |
|---|---|---|
| S1: AS stands after A2 and before A3 in `command.STAGES` | `test_w2_192_stage.py::test_s1_the_command_lists_as_between_a2_and_a3` | red: `gov.adopt.command.STAGES` holds no `AS` |
| S1: `--stage AS` after A0-A2 commits `governance/adoption/AS-spec-audit.md` (stage AS, clean tree, nothing else at stake) | `test_w2_192_stage.py::test_s1_as_runs_after_a2_and_commits_its_record` | red: the argument parser refuses `AS` (invalid choice, exit 2), so the run does not succeed and no record exists |
| S1: A3 before AS is recorded is refused `ADOPT_STAGE_MISSING` naming AS, no A3 record, HEAD does not move | `test_w2_192_stage.py::test_s1_a3_before_as_is_refused_naming_as_and_writes_no_a3_record` | red: A3 after A2 succeeds today (exit 0, `ok: true`), so there is no refusal |
| S1: after AS, A3 with an all-KEEP proposal is accepted | `test_w2_192_stage.py::test_s1_a3_after_as_with_an_all_keep_proposal_is_accepted` | red: the AS run (its precondition) is refused by the argument parser |
| S1: AS reads A1's inventory and A2's classes: with A2 undone AS is refused and writes no record | `test_w2_192_stage.py::test_s1_as_before_a2_is_refused_and_writes_no_record` | red: the argument parser refuses `AS` and prints no envelope (exit 2) |
| S1 (guard): A3 with only A0 and A1 run is `ADOPT_STAGE_MISSING` naming A2 | `test_w2_192_stage.py::test_s1_guard_a3_without_a2_still_names_a2` | **guard: green today, required to stay green** (the chain's existing refusal) |
| S2: the specs found are exactly the three planted | `test_w2_192_record.py::test_s2_the_specs_found_are_exactly_the_planted_ones` | red: no AS run, so no record |
| S2: each spec's title, wave, status as it states them | `test_w2_192_record.py::test_s2_each_spec_carries_its_title_wave_and_status_as_it_states_them[alpha.md]`, `test_w2_192_record.py::test_s2_each_spec_carries_its_title_wave_and_status_as_it_states_them[beta.md]`, `test_w2_192_record.py::test_s2_each_spec_carries_its_title_wave_and_status_as_it_states_them[omega.md]` | red: no AS run, so no record |
| S2: each spec is built, partly built or not built | `test_w2_192_record.py::test_s2_each_spec_is_classed_built_partly_built_or_not_built[alpha.md-built]`, `test_w2_192_record.py::test_s2_each_spec_is_classed_built_partly_built_or_not_built[beta.md-partly-built]`, `test_w2_192_record.py::test_s2_each_spec_is_classed_built_partly_built_or_not_built[omega.md-not-built]` | red: no AS run, so no record |
| S2: evidence (code paths, tests, commits): the built spec's code, test and the commit that touched its code; the partly built spec's present code and not the absent; every item real | `test_w2_192_record.py::test_s2_the_built_spec_has_code_test_and_commit_evidence`, `test_w2_192_record.py::test_s2_the_partly_built_spec_names_the_code_it_has_and_not_the_code_it_lacks`, `test_w2_192_record.py::test_s2_every_item_of_evidence_is_backed_by_the_repository` | red: no AS run, so no record |
| S2: the tickets found, done or not, by wave | `test_w2_192_record.py::test_s2_the_tickets_found_are_listed_done_or_not_by_wave` | red: no AS run, so no record |
| S2: the top-level code modules | `test_w2_192_record.py::test_s2_the_top_level_code_modules_are_listed` | red: no AS run, so no record |
| S2: specs with no code, code with no spec | `test_w2_192_record.py::test_s2_specs_with_no_code_and_code_with_no_spec_are_listed` | red: no AS run, so no record |
| S2: each gap once, one question each, with a place (`answer`) for the answer; a built spec raises none | `test_w2_192_record.py::test_s2_each_gap_is_listed_once_as_one_question_with_a_place_for_the_answer`, `test_w2_192_record.py::test_s2_a_built_spec_and_a_specified_module_raise_no_gap` | red: no AS run, so no record |
| S3: a record that leaves out a top-level module is refused (not by the chain's or A3's existing codes), naming it, no A3 record | `test_w2_192_lite_checks.py::test_s3_a_record_that_leaves_out_a_module_is_refused_naming_it` | red: the AS run (its precondition) is refused by the argument parser |
| S3: a record that leaves out a spec is refused, naming it, no A3 record | `test_w2_192_lite_checks.py::test_s3_a_record_that_leaves_out_a_spec_is_refused_naming_it` | red: the AS run is refused by the argument parser |
| S3: a gap with an empty or no question is refused, naming its subject, no A3 record | `test_w2_192_lite_checks.py::test_s3_a_gap_with_no_question_is_refused_naming_its_subject[empty-string]`, `test_w2_192_lite_checks.py::test_s3_a_gap_with_no_question_is_refused_naming_its_subject[key-absent]` | red: the AS run is refused by the argument parser |
| S3 (control): the same edit and commit with no defect is accepted by A3 | `test_w2_192_lite_checks.py::test_s3_a_record_rewritten_without_a_defect_is_accepted` | red: the AS run is refused by the argument parser |
| F1: no byte outside `governance/adoption/` changes, at HEAD or in the working tree, tracked or not; AS's commits touch only that folder; the tree is clean | `test_w2_192_scope.py::test_f1_as_changes_no_byte_outside_the_adoption_folder` | red: the AS run is refused by the argument parser |
| F1: no spec and no code changes or is created | `test_w2_192_scope.py::test_f1_the_specs_and_the_code_are_byte_for_byte_as_planted` | red: the AS run is refused by the argument parser |
| F1: every gap's `answer` is empty after AS | `test_w2_192_scope.py::test_f1_every_gap_answer_is_empty_after_as` | red: no AS run, so no record |
| F1: A3 reading the record leaves it byte for byte and its answers empty | `test_w2_192_scope.py::test_f1_a3_reading_the_record_leaves_it_and_its_gap_answers_as_they_were` | red: the AS run is refused by the argument parser |

**Counts on the code before the change: 30 cases, 29 red (S1 5, S2 15, S3 5, F1 4) and 1 green guard (S1's
`test_s1_guard_a3_without_a2_still_names_a2`).** Every other case is red; there is no other guard.

There is no guard that "A3 after A2 alone is accepted" and stays so: after the change it is refused by design.

## How the red and guard cases were checked

Against a stand-in AS (a patched copy of `src/` and the tests, kept outside the tree and not committed: `AS` in
`command.STAGES` and `project.STAGES`, a stage function that builds the record by the brief's rules, and the lite checks
at A3's start), all 30 cases pass, so they can be satisfied together. Four mutants of the stand-in each fail the cases of
their line: no lite checks (the four S3 refusal cases fail), AS writing a file outside the folder (the F1 byte
comparison fails), AS closing its gaps with an answer (both F1 answer cases fail), AS calling every spec built (the S2
classification cases for beta and omega, the gaps case, and the cases that need a gap fail).
