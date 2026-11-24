# W2-207 acceptance tests: usage and context per repository (fix UR-1 to UR-4)

Ticket DAEO-rt4s, fix section "usage and context per repository". Written by the independent test designer from the
four KPI lines and the CTO's fixed interface (`gov usage daily | show`, the record `~/.gov-os/usage/<D>.json`, the price
table `governance/project/usage-prices.yaml`), before any implementation. No model, no network: every command runs as
`python3 -m gov.cli.main usage ... --root <tmp root>` with `HOME` under tmp_path; transcripts are planted in the real
format (never real ones). Rates in the planted price table make every expected cost exact by hand (m-a: 10/20/1/5, m-b:
2/4/0.5/1 USD per million tokens). All are acceptance tests.

## How they run

    TMPDIR=$(mktemp -d) PYTHONPATH=<worktree>/src bash <heavy_slot.sh> \
      python3 -m pytest tests/acceptance/W2-207 -q -p no:cacheprovider -n auto

## KPI line to tests

Red on the base: `gov usage` does not exist, so each `gov` child exits non-zero (usage error) and the record file is
absent.

| KPI id | tests | expected red reason |
|---|---|---|
| S1 (UR-1) | `test_w2_207_ur1_record.py::test_ur1_daily_writes_one_row_per_session_with_role_tokens_peak_and_cost` | no `usage` command: exit not 0, no record |
| S1 (UR-1) | `test_w2_207_ur1_record.py::test_ur1_the_record_is_machine_state_nothing_is_written_under_the_root_or_repositories` | no record under HOME/.gov-os/usage |
| S1 (UR-1) | `test_w2_207_ur1_record.py::test_ur1_rerunning_a_day_rewrites_the_same_rows` | no `usage` command |
| S1 (UR-1) | `test_w2_207_ur1_record.py::test_ur1_a_session_with_two_models_gives_two_rows` | no `usage` command |
| S1 (UR-1) | `test_w2_207_ur1_record.py::test_ur1_a_missing_price_table_exits_2_naming_it` | exit is the CLI's usage error, not 2 naming `usage-prices` |
| S1 (UR-1) | `test_w2_207_ur1_record.py::test_ur1_a_model_with_no_price_has_cost_null_and_is_named_unpriced` | no `usage` command |
| S2 (UR-2) | `test_w2_207_ur2_totals.py::test_ur2_every_total_equals_the_sum_of_its_rows` | no `usage` command, no record |
| S2 (UR-2) | `test_w2_207_ur2_totals.py::test_ur2_the_plan_reading_is_the_last_line_of_that_day` | no `usage` command, no record |
| S2 (UR-2) | `test_w2_207_ur2_totals.py::test_ur2_a_day_with_no_usage_line_reads_unread` | no `usage` command (both parameters) |
| S3 (UR-3) | `test_w2_207_ur3_show.py::test_ur3_show_a_day_prints_cost_share_top_three_roles_largest_session_and_plan_reading` | no `usage` command |
| S3 (UR-3) | `test_w2_207_ur3_show.py::test_ur3_show_n_days_prints_one_line_per_day_per_repository_and_writes_nothing` | no `usage` command |
| S4 (UR-4) | `test_w2_207_ur4_planted.py::test_ur4_day_one_rows_and_totals_by_hand` | no `usage` command; covers three repositories, helpers, resumed file, dedupe, bad lines |
| S4 (UR-4) | `test_w2_207_ur4_planted.py::test_ur4_the_session_spanning_midnight_has_only_its_own_day_in_each_record` | no `usage` command |
| S4 (UR-4) | `test_w2_207_ur4_planted.py::test_ur4_a_transcript_of_only_bad_lines_is_skipped_and_counted_never_fatal` | no `usage` command |

## Readings the tests fix where the interface is silent

- The "unpriced" naming is asserted as the word `unpriced` anywhere in stdout, stderr or the record text.
- Role names after `top roles:` are asserted as `<role> $N.NN`; the repository is matched by its folder name in `show`.
- `skipped_lines` is asserted exactly (3) only for the day whose files hold two non-JSON lines and one usage-less
  assistant line; transcript lines that are plain user lines are never planted.

## Fix UR-5 to UR-7 (prices, shipped table, temporary folders)

Red on the branch head: the table has one cache-creation price, no shipped copy, no `cache_creation_5m`/`_1h` row
fields, no `temporary` record key. Planted repositories of these cases carry a `.git` folder (`Env.git_repo`).

| KPI id | tests | expected red reason |
|---|---|---|
| UR-5 | `test_w2_207_ur5_prices.py::test_ur5_a_lead_session_costs_what_its_record_says_within_one_percent` | bare root: exit 2 (no table), or cost off by more than 1 % |
| UR-5 | `test_w2_207_ur5_prices.py::test_ur5_one_hour_writes_are_not_priced_as_five_minute_writes` | no bare-root table; no 5m/1h fields |
| UR-5 | `test_w2_207_ur5_prices.py::test_ur5_without_the_split_all_cache_creation_is_five_minute` | no bare-root table; no 5m/1h fields |
| UR-5 | `test_w2_207_ur5_prices.py::test_ur5_a_table_with_separate_write_prices_prices_each_kind` | `cache_write_5m/1h` keys unknown: cost wrong |
| UR-5 | `test_w2_207_ur5_prices.py::test_ur5_the_old_single_cache_creation_key_prices_both_write_kinds` | green on the base by design: a regression guard that the legacy key prices both kinds |
| UR-6 | `test_w2_207_ur6_table.py::test_ur6_a_bare_root_works_with_the_shipped_table_for_the_real_models` | exit 2: no price table under the bare root |
| UR-6 | `test_w2_207_ur6_table.py::test_ur6_the_shipped_file_holds_the_figures_and_equals_the_committed_table` | no `src/gov/_shipped/.../usage-prices.yaml` |
| UR-6 | `test_w2_207_ur6_table.py::test_ur6_a_repository_table_overrides_the_shipped_one` | `claude-opus-5-5` cost 1.0 with the root table: green on the base by design: a regression guard of the override order |
| UR-7 | `test_w2_207_ur7_temporary.py::test_ur7_temporary_transcripts_are_counted_on_one_line_of_the_record` | no `temporary` key; /tmp folders appear as repositories |
| UR-7 | `test_w2_207_ur7_temporary.py::test_ur7_a_git_repository_under_tmp_stays_a_repository_row` | no `temporary` key |
| UR-7 | `test_w2_207_ur7_temporary.py::test_ur7_show_prints_one_temporary_line_and_no_temporary_repository` | no `temporary` line; temporary names printed |

