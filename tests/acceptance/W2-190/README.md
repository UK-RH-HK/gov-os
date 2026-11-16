# W2-190 acceptance tests: A3 refusing DELETE_FROM_ACTIVE_TREE of a referenced or superseded file

Ticket `DAEO-6oj6` (W2-190), profile STANDARD, class C2. Written by an independent test designer (MR-3) before the
implementation, from the ticket's KPI lines (S1-S3, F1-F2) as described behaviour (DEC-136), without reading the
implementation (DEC-820, DEC-963). Sources: DEC-1197 (2)(ii), DEC-974, CAP-06.b, CAP-08, DAEO-2bdu, DAEO-l78m; the
trigger is W2-81's full run on release 0.1.0 (`governance/project/orchestration/packages/P-W2-81-VERDICT-1.md`, section 2).

## What the tests reach

Every case runs `gov adopt --lite --stage <S> --json --session <name>` as a child process, as an adopter runs it, on a
project planted in a temporary folder as its own git repository (never this repository or a worktree of it). The child
gets W2-23's environment (empty `HOME`, no `GOV_ROLE` or `GOV_TICKET`, no network, no model; the `src/` of the tree the
suite stands in first on `PYTHONPATH`). No code intelligence is needed: no case moves anything.

- **Support:** `w2_190_support.py` *reuses W2-23's support by import* (`w2_23_support`: the planted programme repository,
  the child's environment, `Adoption`, `entry`, `refusal`, `succeeded`, `git`, `at_head`, `commits_deleting`), and adds
  the W2-190 documents and readers: the refusal's `problems`, a problem's text, the committed A3 record's entries.
- **One planted project** (`documents()`), carried through A0, A1 and A2 once per session and **copied per case**
  (`conftest.py`), so each case runs only the stage it judges. The path map's namespace holds `docs/**` and `*.md`: no
  file is unknown (an unknown file may only be kept and would refuse for another reason), and the path map spells out
  no deletion target. `assert_planted` checks, when planting, that each target is named by exactly the files the case
  intends, so a planting fault is never read as the tool's.

| Document | Planted as | Used by |
|---|---|---|
| `docs/plans/0003-storage-migration.md` | plain Markdown, no front matter | S1, S3, F1 |
| `docs/plans/0007-storage-migration.md` | "This plan supersedes plan 0003 (`docs/plans/0003-storage-migration.md`)." | S1 (the referencing file) |
| `docs/specs/storage-overview.md` | names `docs/plans/0003-storage-migration.md` too | S1 (both referencing files named) |
| `docs/drop-1.txt` | W2-23's base file; no other file names it, no record | S1, S3 |
| `docs/records/old-rule.md` | front matter `id`, `type`, `status: SUPERSEDED` | S2 |
| `docs/records/lower-rule.md` | front matter `status: superseded` (lower case) | S2 |
| `docs/records/active-rule.md` + `active-rule-v2.md` | ACTIVE record; the successor's `supersedes: [<id>]` (the id, not the path) | S2 |
| `docs/records/active-held-rule.md` + `active-held-rule-v2.md` | ACTIVE record; its own `superseded_by: [<id>]` | S2 |
| `docs/self-naming.md` | its text names its own path | F2 |
| `docs/adoption-only.md` | named only by `governance/adoption/notes.md`, committed after A2 | F2 |
| `docs/mutual-a.md`, `docs/mutual-b.md` | each names the other; both deleted by one proposal | F2 |
| `x.md` and `docs/a/x.md` | `docs/a/readme-for-x.md` names only `docs/a/x.md` | F2 |

## How to run

```
env HOME=<an empty folder> PYTHONPATH=<worktree>/src TMPDIR=<a writable temporary folder> \
  python3 -m pytest tests/acceptance/W2-190 -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  -m "not local_only" -k "not real and not green_here and not time_limit"
```

About 5 s in all (A0-A2 run once; each case runs A3, and in F1 A4 and A6, on a copy). No case is `local_only`,
serial-only or marked skip or xfail.

## The interface the cases hold (the ticket's, as written)

- The command is `gov adopt --lite --stage A3 --map <proposal>`; A0, A1, A2 run first.
- A refused proposal: the envelope's error code is the refusal A3 already gives, `PROPOSAL_REFUSED` (on the wire every
  adopt refusal carries the prefix `ADOPT_`: `ADOPT_PROPOSAL_REFUSED`, as A3's other refusals do); the details'
  `problems` holds one problem per refused path, each with its `path`; **no A3 record** is written or committed.
- The problem for a deleted path another tracked file names carries the code `DELETE_REFERENCED` and names each
  referencing file by its repository-relative path; for a superseded file, `DELETE_SUPERSEDED`.
- **Not stated, so not asserted:** which field of a problem holds the code (a case asserts that the problem whose `path`
  is the deleted path *contains* the code string and each referencing path, in any of its values); what code(s) a file
  that is both referenced and superseded gets (no case plants one: each fixture isolates one cause).

Beyond the lines and written as none: binary files skipped in the text search (a rabbit hole of the ticket; no case);
the reverse suffix direction (`docs/a/x.md` deleted while another file names only `x.md`); classing by content.

## The map

| KPI | Tests | Expected outcome on the code before the change |
|---|---|---|
| S1: DELETE of a file another tracked file names is refused `PROPOSAL_REFUSED`, the problem has `DELETE_REFERENCED` and names each referencing file, no A3 record | `test_w2_190_referenced.py::test_s1_deleting_a_file_another_file_names_is_refused_with_delete_referenced_and_the_referencer`, `test_w2_190_referenced.py::test_s1_every_referencing_file_is_named_and_the_whole_proposal_is_refused` | red: A3 accepts and records the delete (exit 0, `ok: true`), so there is no `PROPOSAL_REFUSED` |
| S2: the same refusal with `DELETE_SUPERSEDED` for a file classed superseded (a SUPERSEDES edge's target, or front matter `status` superseded in any case) | `test_w2_190_superseded.py::test_s2_deleting_a_file_classed_superseded_is_refused_with_delete_superseded[status-upper-case]`, `test_w2_190_superseded.py::test_s2_deleting_a_file_classed_superseded_is_refused_with_delete_superseded[status-lower-case]`, `test_w2_190_superseded.py::test_s2_deleting_a_file_classed_superseded_is_refused_with_delete_superseded[target-of-a-supersedes-edge]`, `test_w2_190_superseded.py::test_s2_deleting_a_file_classed_superseded_is_refused_with_delete_superseded[superseded-by-in-its-own-front-matter]` | red: A3 accepts and records the delete (no `PROPOSAL_REFUSED`) |
| S3: RETIRE or KEEP of the same file is accepted; DELETE of an unreferenced, unsuperseded file is accepted with its batch | `test_w2_190_referenced.py::test_s3_retiring_the_referenced_file_is_accepted_and_recorded`, `test_w2_190_referenced.py::test_s3_keeping_the_referenced_file_is_accepted_and_recorded`, `test_w2_190_referenced.py::test_s3_deleting_an_unreferenced_unsuperseded_file_is_accepted_with_its_batch` | guard: green today, required to stay green |
| F1: no delete of a referenced or superseded file is recorded at A3 or executed by an A6 batch | `test_w2_190_referenced.py::test_f1_after_the_refusal_a4_and_a6_refuse_for_want_of_the_a3_record_and_the_file_stays` | red at A3's acceptance (it records the delete, so the case's first step finds no refusal); after the change A4 and A6 each refuse `ADOPT_STAGE_MISSING` naming A3 (as measured on the code before the change with A3 not run), HEAD does not move, the file stays tracked at HEAD and in the working tree, no commit deletes it |
| F2: no over-refusal: a mention in the file itself, in `governance/adoption/`, in a file the same proposal deletes, or a path sharing only a suffix (`docs/a/x.md` against `x.md`) is no reference | `test_w2_190_scope.py::test_f2_a_mention_inside_the_file_itself_is_not_a_reference`, `test_w2_190_scope.py::test_f2_a_mention_inside_the_adoptions_own_folder_is_not_a_reference`, `test_w2_190_scope.py::test_f2_a_mention_in_a_file_the_same_proposal_also_deletes_is_not_a_reference`, `test_w2_190_scope.py::test_f2_a_path_that_only_shares_a_suffix_is_not_a_reference` | guard: green today, required to stay green |

**Counts on the code before the change: 14 cases, 7 red (S1 2, S2 4, F1 1) and 7 green guards (S3 3, F2 4).**

How the red and guard cases were checked: against a stand-in `a3` (a patched copy of `src/`, kept outside the tree and
not committed: the text search with a path-boundary match outside `governance/adoption/` and outside the proposal's own
deletes, plus the record graph's SUPERSEDES targets and front matter `status`), all 14 pass, so the cases can be
satisfied together. Four variants of the stand-in that over-refuse (a plain substring match; the adoption folder
counted; the proposal's own deletes counted; the file itself counted) each fail the F2 case of their line.
