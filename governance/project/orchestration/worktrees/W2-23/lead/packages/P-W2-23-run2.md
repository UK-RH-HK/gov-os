---
task: DAEO-kmcr
decisions_applied: [DEC-954, DEC-1052, DEC-1112]
---
# W2-23 run 2 (build): packages after verification, before the FULL review

Head w2/W2-23 01a1770ce53c. W2-23's own acceptance: 22 of 22 pass (S1-S7, F1; `gov accept` outside the sandbox).
lead_verify (scoped selection, 4012 tests): 13 red. 4 already fail at the base; 5 are W2-96 signal cases that depend
on the environment; 4 come from W2-23 (P-W2-23-5, P-W2-23-6). No FULL review launched: it waits for these answers, so
that it reviews the final head (one round, DEC-1010).

## P-W2-23-4: the auto-compact entry of Interface item 5 against DEC-838 (class: CTO's Interface edit; owner decision in play; C3)
Item 5 asks for "an `env` block carrying the auto-compact entry (W2-M229)". W2-M229 rests on DEC-636, which DEC-838
superseded. DEC-838 is ACCEPTED and standing: "Every session uses its model's full window"; "No launch sets a compaction
threshold". As built, `src/gov/adapters/merge.py:30` reads `AUTO_COMPACT = {"CLAUDE_CODE_AUTO_COMPACT_WINDOW": "300000"}`,
so every adopted project would compact at 300k. The test designer (T1) and the engineer each raised this on their own.
- (a) Keep it as built. Cost: none now; every adopted project runs against DEC-838 item 1.
- (b) No threshold: `AUTO_COMPACT = {}`. The `env` block is still merged, and the programme's own entries are kept first. Item 5's
  words are edited. Cost: a one-line engineer change, two unit assertions, and one acceptance assertion revised by the
  test designer under a Rewrite-Reason (`test_s2_settings_keep_the_programmes_keys_and_entries_in_order_with_generated_ones_after`,
  last assertion). **Recommended.**
- (c) Take the value from a project setting. Cost: about 20 lines, and a new interface.
Recommendation: (b). Confidence: high (DEC-838 is the owner's standing rule; the Interface is a delegated line).
Blocks: S2's final form, and so the review.

## P-W2-23-5: W1-41's failed-batch case still expects the old shared rollback ref (class: CTO's ticket edit; C3)
`tests/acceptance/W1-41/test_w1_41_migration.py::test_a_failed_batch_rolls_back_to_its_point_and_the_batches_before_it_stay`
(lines ~98-101) takes the rollback point A4 planned (`refs/gov/adoption/rollback/batch-2`) and requires it to resolve.
Interface item 2 makes the refs per run (`refs/gov/adoption/rollback/<run-id>/batch-<n>`, W2-M219 "rollback refs are
unique"), so it no longer resolves. It passes at the base and is red at the head.
- (a) Give W2-23's test designer a named revision batch for that one W1-41 case: it reads the point from the A6
  record's per-run refs, with a Rewrite-Reason. This needs `tests/acceptance/W1-41/test_w1_41_migration.py` (that one
  case) added to W2-23's paths. Cost: one test-designer batch, about 2 USD. **Recommended.**
- (b) The code also updates the A4-named ref as an alias of the latest run's point. Cost: about 5 lines; it brings back a reused
  ref name (the problem W2-M219 removes).
Recommendation: (a). Confidence: medium-high. Blocks: a green verify.

## P-W2-23-6: `fixtures/adopt/**` is in no namespace of this repository's path map (class: CTO; control path or move; C2)
The ticket names `fixtures/adopt/**` as new, but `governance/project/path-map.yaml` (outside W2-23's paths) has no
namespace for it. As a result `tests/acceptance/W1-08/test_w1_08_path_map.py::test_every_tracked_path_matches_exactly_one_namespace`
and `tests/unit/retrieval/test_w2_91_full_embeddings.py::test_every_tracked_path_is_in_one_namespace` fail on 5 paths.
Both pass at the base.
- (a) The CTO adds `"fixtures/adopt/**"` to the `fixtures` namespace's paths in `governance/project/path-map.yaml`
  (beside `fixtures/brownfield/**`, line ~247), by the path's own route (ACT if it is a control path). Cost: one line.
  **Recommended** (the card itself names the folder).
- (b) The next engineer batch moves the fixture under `tests/unit/adapters/fixtures/programme/` (inside the paths).
  Cost: a few lines, folded into P-W2-23-4's batch; the card's `fixtures/adopt/` stays empty.
Recommendation: (a). Confidence: medium. Blocks: a green verify.

## Reds not W2-23's (for the CTO to confirm; none is on a known-red list I hold)
- At the base 219307d1d, the same 4 fail (`log/base-reds.txt`): W1-26 `test_this_repository_s_probe_records_are_well_formed`,
  `test_no_finding_of_the_check_on_this_repository_names_a_probe_record`; W1-08
  `test_the_probe_schema_accepts_this_repository_s_probe_records`; W2-02 `test_core_schema_is_green_on_this_repository`.
  All four come from `docs/probes/DAEO-xafn/PR-DAEO-xafn.md` (main's a37ef2c10).
- W2-96 signal cases in `tests/unit/accept/` (review3 r14, review4 r16, run2 r9/r12; 5 red in the detached verify). Run
  alone once in the lead's shell: 19 red, `error_kind: crash` (`log/w2-96-alone.txt`), so they depend on the
  environment. Neither the tests nor `src/gov/accept` reference adopt or adapters.

## Next run (after the answers)
One engineer batch (P-W2-23-4 (b), and P-W2-23-6 (b) if chosen) and one test-designer batch (the S2 assertion, and
W1-41 if P-W2-23-5 (a)), run in parallel. Then merge, accept, rebuild, verify, and the FULL review (independent-auditor,
Opus, high, about 4 USD). Then the probe record at docs/probes/DAEO-kmcr/PR-DAEO-kmcr.md. Merge w2/integrate back first
(the tree's ticket copy predates 865ea01e9; `gov links` flags DEC-1052 as UNLINKED until then).
