# W2-183 (DAEO-href) acceptance tests: gov close's context packet at a project setting; the supplementary cap

Sources: DEC-1165, DEC-1027, DEC-860, CAP-15.d. Profile STANDARD, class C2. Written by the independent test designer
from the ticket's KPI lines and the interface the CTO stated at claim; the base is `d36c268c1` (before any W2-183 code).

## What the cases drive (public forms only)

- `gov context <ticket> --json --root <stand-in> [--budget N]` (`python3 -m gov.cli.main context`), its envelope.
- `gov.close.command._build_context(root, ticket)`, the close's context step, in a child process on a real stand-in
  (nothing of `gov.context` is mocked): the packet, or a `_Finding` (code, message, `details["context_error"]`).
- `gov.context.close_budget(root)` and `gov.context.SUPPLEMENTARY_CAP`, imported inside the case that uses them (a tree
  without them reds that case and no other).
- The setting is `budgets.close_context_tokens` in the stand-in's `governance/project/facts.yaml`, written by the case
  (`Project.setting`) and restored afterwards.

Every stand-in is a temporary git repository under `tmp_path_factory` (never this repository's store or
`.gov-runtime/`), built once per module: **small** (a 131-token ticket and one charter record, no index), **big** (the
ticket's own text about 6,300 tokens and one mandatory source about 4,000: 10,403 tokens in all, no index) and **ledger**
(a small ticket and 80 matching pages of about 300 tokens each, lexically indexed: about 24,000 tokens of supplementary
evidence). No vector, no embedder (the address is a dead port), `HOME` empty, offline. The ledger's index needs
`gitleaks` on `PATH` (as W2-04's does); a machine without it fails those cases with that message.
A child process gets the `PYTHONPATH` the run was given first and this tree's `src/` after it.

## The map: case, KPI line, expected on the base (`d36c268c1`)

Run on the base: **28 red, 21 green** (49 cases, about 30 s).

### S1: the close builds the packet at the project's setting; with none, the default

| KPI id | tests | expected on the base |
|---|---|---|
| S1 | `test_w2_183_s1_close_setting.py::test_the_close_builds_the_packet_at_the_setting_65536` | red: the close ignores the setting and refuses `CONTEXT_OVER_CEILING` at 6,000 |
| S1 | `test_w2_183_s1_close_setting.py::test_with_no_setting_the_close_refuses_at_the_default[no key]` | green (guards today's refusal) |
| S1 | `test_w2_183_s1_close_setting.py::test_with_no_setting_the_close_refuses_at_the_default[no budgets]` | green |
| S1 | `test_w2_183_s1_close_setting.py::test_with_no_setting_the_close_refuses_at_the_default[no file]` | green |
| S1 | `test_w2_183_s1_close_setting.py::test_a_setting_of_8000_refuses_the_ten_thousand_token_ticket` | green (the refusal is the default's) |
| S1 | `test_w2_183_s1_close_setting.py::test_the_refusal_at_8000_is_made_at_the_setting_not_at_the_default` | red: the refusal's `limit` is 6000, not 8000 |
| S1 | `test_w2_183_s1_close_setting.py::test_the_setting_is_the_ceiling_to_the_token` | red: a setting equal to the mandatory part (10,403) still refuses |
| S1 | `test_w2_183_s1_close_setting.py::test_gov_context_with_no_budget_still_refuses_at_6000_whatever_the_setting` | green (the default of `gov context` is unchanged) |
| S1 | `test_w2_183_s1_close_setting.py::test_gov_context_with_a_budget_of_65536_gives_the_whole_mandatory_part` | green |
| S1 | `test_w2_183_s1_close_setting.py::test_close_budget_reads_the_setting` | red: `close_budget` does not exist (`ImportError` named in the failure) |
| S1 | `test_w2_183_s1_close_setting.py::test_close_budget_is_the_default_with_no_setting[no key]` | red: `close_budget` does not exist |
| S1 | `test_w2_183_s1_close_setting.py::test_close_budget_is_the_default_with_no_setting[no budgets]` | red: same |
| S1 | `test_w2_183_s1_close_setting.py::test_close_budget_is_the_default_with_no_setting[no file]` | red: same |
| S1 | `test_w2_183_s1_close_setting.py::test_with_no_setting_the_close_packet_is_what_it_was` | green |

### S2: the supplementary block holds at most 6,000 tokens whatever `--budget` is passed; the close's packet likewise

| KPI id | tests | expected on the base |
|---|---|---|
| S2 | `test_w2_183_s2_supplementary_cap.py::test_the_stand_in_holds_far_more_evidence_than_the_cap` | green (the fixture holds about 24,000 tokens of pages) |
| S2 | `test_w2_183_s2_supplementary_cap.py::test_the_cap_is_6000` | red: `gov.context.SUPPLEMENTARY_CAP` does not exist |
| S2 | `test_w2_183_s2_supplementary_cap.py::test_a_big_budget_gives_at_most_6000_tokens_of_supplementary[60000]` | red: 22,778 tokens (81 items) |
| S2 | `test_w2_183_s2_supplementary_cap.py::test_a_big_budget_gives_at_most_6000_tokens_of_supplementary[20000]` | red: 19,670 tokens (70 items) |
| S2 | `test_w2_183_s2_supplementary_cap.py::test_a_big_budget_gives_at_most_6000_tokens_of_supplementary[12000]` | red: 11,802 tokens (42 items) |
| S2 | `test_w2_183_s2_supplementary_cap.py::test_the_block_is_the_same_whatever_budget_is_passed_past_the_cap` | red: a room of 18,000 gives 64 items, a room of 6,000 gives 21 |
| S2 | `test_w2_183_s2_supplementary_cap.py::test_a_room_under_the_cap_gets_at_most_that_room[3000]` | green (guards the room under the cap) |
| S2 | `test_w2_183_s2_supplementary_cap.py::test_a_room_under_the_cap_gets_at_most_that_room[1000]` | green |
| S2 | `test_w2_183_s2_supplementary_cap.py::test_a_room_under_the_cap_gets_at_most_that_room[5000]` | green |
| S2 | `test_w2_183_s2_supplementary_cap.py::test_the_close_packet_at_the_setting_65536_holds_at_most_6000_supplementary` | red: the close's packet is built at 6,000, not at the setting |
| S2 | `test_w2_183_s2_supplementary_cap.py::test_the_close_packet_is_gov_contexts_packet_at_the_same_budget` | red: the close's packet is not `gov context --budget 65536`'s (same hash, same items) |

### S3: the mandatory part is never shortened; a budget with under 6,000 of room is unchanged

The hashes are pinned from the base `d36c268c1` (see the file's comment); they guard what must not change.

| KPI id | tests | expected on the base |
|---|---|---|
| S3 | `test_w2_183_s3_unchanged.py::test_a_small_tickets_packet_at_the_default_budget_is_what_it_was` | green (hash `fb62b2a3…e721`, 131 tokens) |
| S3 | `test_w2_183_s3_unchanged.py::test_the_ledgers_packet_at_the_default_budget_is_what_it_was` | green (hash `0a79ea57…2b15`, pages 00 to 19, 5,620 tokens of evidence) |
| S3 | `test_w2_183_s3_unchanged.py::test_a_budget_that_leaves_6000_or_less_of_room_is_unchanged[3134]` | green (hash `0e0b95be…35cf7`, 10 items) |
| S3 | `test_w2_183_s3_unchanged.py::test_a_budget_that_leaves_6000_or_less_of_room_is_unchanged[6134]` | green (hash `7ac26340…87aa6`, 21 items) |
| S3 | `test_w2_183_s3_unchanged.py::test_the_close_with_no_setting_gives_the_small_packet_it_gave` | green |
| S3 | `test_w2_183_s3_unchanged.py::test_the_small_packet_at_the_setting_has_the_same_mandatory_items` | green (the setting is ignored today; the packet is the default's) |
| S3 | `test_w2_183_s3_unchanged.py::test_a_mandatory_part_over_its_ceiling_is_still_refused_named` | green |
| S3 | `test_w2_183_s3_unchanged.py::test_a_mandatory_part_over_a_big_budget_is_still_refused_named` | green |
| S3 | `test_w2_183_s3_unchanged.py::test_the_mandatory_part_is_served_whole_when_the_budget_holds_it` | green |
| S3 | `test_w2_183_s3_unchanged.py::test_the_mandatory_part_is_not_shortened_by_a_big_budget_with_evidence_to_spare` | green |
| S3 | `test_w2_183_s3_unchanged.py::test_the_close_packet_of_the_big_ticket_is_whole_at_the_setting` | red: the close refuses the big ticket (the setting is not read) |

### F1: a setting that is not a positive whole number refuses by name

Values: `0`, `-5`, `"many"`, and the edges `true` and `2.5`.

| KPI id | tests | expected on the base |
|---|---|---|
| F1 | `test_w2_183_f1_invalid_setting.py::test_an_invalid_setting_refuses_the_closes_context_step_by_name[zero]` | red: the step returns a packet at the default |
| F1 | `test_w2_183_f1_invalid_setting.py::test_an_invalid_setting_refuses_the_closes_context_step_by_name[negative]` | red: same |
| F1 | `test_w2_183_f1_invalid_setting.py::test_an_invalid_setting_refuses_the_closes_context_step_by_name[string]` | red: same |
| F1 | `test_w2_183_f1_invalid_setting.py::test_an_invalid_setting_refuses_the_closes_context_step_by_name[bool]` | red: same |
| F1 | `test_w2_183_f1_invalid_setting.py::test_an_invalid_setting_refuses_the_closes_context_step_by_name[float]` | red: same |
| F1 | `test_w2_183_f1_invalid_setting.py::test_close_budget_refuses_an_invalid_setting_naming_the_key_and_the_value[zero]` | red: `close_budget` does not exist |
| F1 | `test_w2_183_f1_invalid_setting.py::test_close_budget_refuses_an_invalid_setting_naming_the_key_and_the_value[negative]` | red: same |
| F1 | `test_w2_183_f1_invalid_setting.py::test_close_budget_refuses_an_invalid_setting_naming_the_key_and_the_value[string]` | red: same |
| F1 | `test_w2_183_f1_invalid_setting.py::test_close_budget_refuses_an_invalid_setting_naming_the_key_and_the_value[bool]` | red: same |
| F1 | `test_w2_183_f1_invalid_setting.py::test_close_budget_refuses_an_invalid_setting_naming_the_key_and_the_value[float]` | red: same |
| F1 | `test_w2_183_f1_invalid_setting.py::test_a_setting_of_1_is_valid_and_refuses_as_an_ordinary_ceiling` | red: the setting is not read, a packet is returned |
| F1 | `test_w2_183_f1_invalid_setting.py::test_an_invalid_setting_is_refused_whatever_the_ticket` | red: the big ticket is refused for its size (`CONTEXT_OVER_CEILING`), not for its setting |
| F1 | `test_w2_183_f1_invalid_setting.py::test_a_valid_setting_after_an_invalid_one_works` | red: the invalid setting is not refused |

## Left out of the folder

The run excludes `local_only`, `real`, `green_here` and `time_limit` cases; this folder has none. A setting written as a
string of digits (`"65536"`) is not tested: the interface says "a value that is not a whole number" refuses and does not
say whether a quoted number counts (a question for the CTO, in the return's `proposed_decisions`).
