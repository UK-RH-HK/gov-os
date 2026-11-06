# W2-134 (DAEO-m4rq): the memory measure re-anchors line-cited gold in memory

Written by the independent test designer from the ticket's KPI lines S1 to S4 and its failure lines (DEC-1085 (2),
W2-61h S8, DEC-1084), before any implementation. No implementation was read. The guard refused a read of
`src/gov/retrieval/measure.py` (the ticket's own path), so the measure's interface was taken from the W2-61 and
W2-61h acceptance cases and from black-box runs of the integrated measure on planted data.

Everything is planted in `tmp_path` (`w2_134_support.py`):

- a measured root, a git repository with two commits;
- a sets root, a plain folder in no git work tree (as `~/gov-os-eval`), holding the path map and the set `planted`;
- a stand-in `gov` that returns chosen evidence and can keep its answers as a run's kept outputs.

There is no store, no model and no network, and nothing reads this repository's sets, `~/gov-os-eval` or
`~/gov-os-runs`. The 13 items take about 6 seconds.

## How to run

```bash
PYTHONPATH=<tree>/src python3 -m pytest tests/acceptance/W2-134 -p no:cacheprovider -o tmp_path_retention_policy=failed
```

## The planted commits

| File | Commit 1 | Commit 2 (moving) | Commit 2 (steady, S4) |
|---|---|---|---|
| `docs/moved.md` | cited block at 5-7 | 10 lines inserted above: block at 15-17; 5-7 hold inserted notes | lines appended at the end |
| `docs/contract/CONTRACT.md` | cited block at 5-6; `capabilities/CAP-7.md` (a family member) holds its text | 6 lines inserted above: block at 11-12 | lines appended at the end |
| `docs/steady.md` | cited block at 3-4 | unmoved, lines appended below | lines appended at the end |
| `docs/zqxw134hidden/gone.md` | cited block at 73-77 (90 lines) | the 5 lines deleted (85 lines; 73-77 hold other text) | lines appended at the end |

## The interface these cases assume

The command is unchanged:

```
python3 -m gov.retrieval.measure <set> --root <root> [--sets-root <dir>] --part visible|hidden|all --gov <gov> [--json] [--kept <dir>]
```

1. **The source's own commit.** For a source cited by `lines: [a, b]`, it is the source's `commit`, else the
   question's `commit`. The block is that commit's lines a..b of the source's path, read from the measured root's
   repository. Its lines at the measured root are where that block is found. A source that names no commit is scored
   on its stated lines, as today (S4's q06).
2. **The scoring uses the re-anchored lines.** This covers both W2-61's overlap rule and W2-61h S7's family text
   (the gold span's text is the text at the re-anchored lines). It holds for a live run and for `--kept`.
3. **How an unresolved source is named.**
   - It is named on a line holding the question's id and `entry <n>`, where `<n>` is the 1-based number of the
     entry in `sources`, for example `x01 ... entry 2`.
   - The line goes in the text run's standard output or in either run's standard error. With `--json`, standard
     output stays one JSON document.
   - The line, the record and the streams never hold the label's question or answer, the source's path, the block's
     text, or its line numbers.
   - A source that was found is never named this way.
4. **Nothing is written.** No file or folder under the sets root (or, in the in-tree form, under
   `fixtures/evaluation/` and `governance/project/`) is created, changed or removed.
5. **Unchanged output.** The per-question line, the total line and the record's figures (`hit_at_5`,
   `first_gold_rank`, `in_bundle`, `full_evidence`, `pieces_found`, `pieces_needed`, `family_hits`) keep today's
   form. With no block moved, they keep today's values.

## KPI lines to cases

| KPI | Case (full node id) | On this branch | What it checks |
|---|---|---|---|
| S1 | `test_w2_134_s1_moved_block.py::test_s1_a_moved_block_is_scored_on_its_new_lines` (`question-commit`, `source-commit`) | **red**: no hit (the old lines are used) | The block is cited at commit 1's 5-7 (the question's `commit`, or the source's). Measured on commit 2 with the evidence on 15-17 at rank 2, it is a hit at rank 2 with full evidence 1 of 1, and the line reads `hit@5 yes (first gold rank 2)` |
| S1, F2 | `test_w2_134_s1_moved_block.py::test_s1_the_old_lines_of_a_moved_block_no_longer_count` | **red**: today a hit | On commit 2, evidence on the old lines 5-7 (now inserted notes) is no hit. A commit is never scored against another commit's lines |
| S1 | `test_w2_134_s1_moved_block.py::test_s1_an_unmoved_block_keeps_its_lines` | green by design (a guard) | `docs/steady.md` changed below its block. Evidence on 3-4 is a hit; evidence on 5-6 is not |
| S1 (with S7) | `test_w2_134_s1_moved_block.py::test_s1_a_family_member_holding_a_moved_block_s_text_is_a_hit` | **red**: no family hit | The Contract's block moved from 5-6 to 11-12. The capability page holding its text is a family hit at rank 1, named in the line |
| S1 | `test_w2_134_s1_moved_block.py::test_s1_kept_outputs_are_re_scored_on_the_moved_lines` | **red**: no hit | A run on commit 2 keeps its outputs. `--kept`, with a retriever that answers nothing, re-anchors too: a hit at rank 2, and no `retrieve` is asked |
| S2, F2 | `test_w2_134_s2_sets_root.py::test_s2_two_measures_on_two_commits_score_each_against_its_own_lines` | **red**: on commit 2, `old` hits and `new` misses | Two questions cite 5-7 at commit 1: `old` has evidence on 5-7, `new` on 15-17. The measures run one after the other on commit 2, commit 1 and commit 2. Commit 2 gives old no, new yes; commit 1 gives old yes, new no. Each record names its own commit |
| S2, F1 | `test_w2_134_s2_sets_root.py::test_s2_every_file_under_the_sets_root_is_byte_for_byte_as_it_was` (`sets-root`, `in-tree`) | green by design (a guard) | Three labels: a moved visible block, and a hidden label with a moved block and a deleted one. Every path under the sets root is hashed with sha256. `--part all` runs, text and `--json`, on commit 2 and then commit 1. Afterwards there is no path added, removed or changed. In-tree: the label folder and the path map in the measured root |
| S3, F3 | `test_w2_134_s3_unresolved.py::test_s3_a_deleted_block_counts_as_not_found_and_is_named_by_id_and_entry_only` (`hidden`, `visible`) | **red**: today the deleted block counts as found | x01 is the steady block plus the deleted one: hit at rank 1, full evidence 1 of 2. x02 is the deleted one alone: no hit, 0 of 1. `x01 … entry 2` and `x02 … entry 1` are named, and x01's entry 1 is not. Neither stream nor the record holds `zqxw134hidden`, `gone.md`, or 73 or 77 standing alone (the planted folders' own path is removed before the scan) |
| S4 | `test_w2_134_s4_unchanged.py::test_s4_with_every_cited_block_unmoved_the_lines_and_totals_are_today_s` | green by design (a guard) | The steady commit 2 holds six questions: line-cited (question commit, source commit, no commit), a heading plus a whole file, a miss, and a family hit. The six per-question lines and the total line equal today's output word for word, and so do the figures and `family_hits` |
| S4 (S7) | `test_w2_134_s4_unchanged.py::test_s4_kept_outputs_re_score_as_the_run_with_families` | green by design (a guard) | The same run's kept outputs, re-scored with `--kept` and no retrieval, give today's lines, total and figures, with the family hit |

"Today's output" in S4 is the integrated measure's output on this branch (`w2/W2-61h-s7` with `w2/integrate`,
2026-11-06) for the same planted run. It was recorded from a black-box run and is held word for word in the test.

**Expected state on this branch:** 8 red and 5 green out of 13 items. Each red fails on its own figure as stated in
the table.

## Not covered by a test

- **A block found more than once at the measured root.** S1 says the block is "found once", and `repin_gold.py`
  treats more than one place as unresolved, but the ticket does not say which outcome applies.
- **A heading-cited source.** A heading found at the root governs, as today, and S4's q02 checks that this is
  unchanged. A heading not found that falls back to its lines is not re-anchored by any case.
- **An alternative's entry number (`k.j`)** in the naming.
